import asyncio
import json
import logging
import socket
import time
from collections import defaultdict
from typing import DefaultDict, NoReturn, Optional

import nats.errors
import requests
from nats.aio.client import Client as NATSClient
from nats.aio.msg import Msg
from pydantic import BaseSettings, Field

from powerflex_monitoring.format_exception import format_exception
from powerflex_monitoring.monitoring import MonitoringServer

logger = logging.getLogger(__name__)
HOSTNAME_TEMPLATE_VAR = "{hostname}"


class NatsHealthCheckerConfig(BaseSettings):
    NATS_SERVICE_HEALTH_CHECK_ADDRESS: str = Field(
        description="NATS service health check HTTP address."
    )
    NATS_SERVICE_HEALTH_CHECK_TIMEOUT: float = Field(
        description="How long to wait for the NATS health endpoint to respond to this service",
        default=5,
    )

    NATS_HEALTH_CHECK_SUBJECT_TEMPLATE: str = Field(
        description="NATS subject on which this service will subscribe to and periodically send requests. "
        f"The string {HOSTNAME_TEMPLATE_VAR} is replaced with the service's hostname. "
        "The hostname is used in this NATS subject to ensure it is unique across all containers. "
        "In docker-compose and kubernetes, the hostname is typically container-specific. ",
        default=f"nats_health_check.echo.{HOSTNAME_TEMPLATE_VAR}",
    )

    NATS_HEALTH_CHECK_UNHEALTHY_TIMEOUT_SEC: float = Field(
        description="Mark the service as unhealthy after determining that NATS is unhealthy for this period of time. "
        "Recommend making it less than NATS_HEALTH_CHECK_REQUEST_PERIOD_SEC.",
        default=60 * 4,
    )

    NATS_HEALTH_CHECK_REQUEST_TIMEOUT_SEC: float = Field(
        description="Timeout for the requests we periodically send to test the NATS connection.",
        default=5,
    )

    NATS_HEALTH_CHECK_REQUEST_PERIOD_SEC: float = Field(
        description="How often to periodically send a NATS request to test the NATS connection.",
        default=15,
    )


class NatsHealthChecker:
    def __init__(self, nats_conn: NATSClient, monitoring_server: MonitoringServer):
        self.config = NatsHealthCheckerConfig(
            # type:ignore
        )

        logger.info(
            "Configuration for NATS health check", extra={"config": self.config.dict()}
        )

        self.nats_health_check_subject = (
            self.config.NATS_HEALTH_CHECK_SUBJECT_TEMPLATE.replace(
                HOSTNAME_TEMPLATE_VAR,
                socket.gethostname(),
            )
        )
        self.nats_conn = nats_conn
        self.monitoring_server = monitoring_server
        self.nats_request_timeout = 10
        self.time_since_nats_unhealthy: DefaultDict[str, Optional[float]] = defaultdict(
            lambda: None
        )

    async def _async_setup(self) -> None:
        logger.info(
            "NATS health checker subscribing to NATS subject %s to run periodic NATS health check.",
            self.nats_health_check_subject,
        )
        await self.nats_conn.subscribe(
            self.nats_health_check_subject, cb=self._echo_requests
        )

    def on_unhealthy(self, health_check_name: str, cause: str) -> None:
        """Check if a NATS health check has been unhealthy for too long.

        If so, then mark the service as unhealthy.
        """
        self.on_nats_health_status(
            healthy=False, health_check_name=health_check_name, cause=cause
        )

        time_since = self.time_since_nats_unhealthy[health_check_name]
        unhealthy_for_too_long = (
            time_since is not None
            and time.time() - time_since
            >= self.config.NATS_HEALTH_CHECK_UNHEALTHY_TIMEOUT_SEC
        )
        if unhealthy_for_too_long:
            self.monitoring_server.health_check.make_unhealthy(cause)

    def on_nats_health_status(
        self, healthy: bool, health_check_name: str, cause: str = "NATS is healthy"
    ) -> None:
        """Call this whenever a result for a NATS health check is found."""
        if healthy is True:
            logger.debug(
                "NATS health check %s indicates NATS is healthy", health_check_name
            )
            self.time_since_nats_unhealthy[health_check_name] = None

        if healthy is False:
            self.monitoring_server.ready_check.set_ready(False, cause=cause)

            if self.time_since_nats_unhealthy[health_check_name] is None:
                logger.info(
                    "NATS health check %s indicates NATS is currently unhealthy",
                    health_check_name,
                    extra={"cause": cause},
                )
                self.time_since_nats_unhealthy[health_check_name] = time.time()

        all_health_checks_pass = all(
            check_failure_time is None
            for check_failure_time in self.time_since_nats_unhealthy.values()
        )
        if not self.monitoring_server.ready_check.is_ready and all_health_checks_pass:
            self.monitoring_server.ready_check.set_ready(
                True, cause="NATS is healthy again"
            )

    async def _echo_requests(self, nats_msg: Msg) -> None:
        if nats_msg.reply:
            await self.nats_conn.publish(nats_msg.reply, nats_msg.data)

    async def check_echo_nats_request(self) -> None:
        """Make a NATS request to a service-unique subject to check NATS health."""
        health_check_name = self.check_echo_nats_request.__name__
        timeout = self.config.NATS_HEALTH_CHECK_REQUEST_TIMEOUT_SEC
        test_payload = {"timestamp": time.time()}
        try:
            response = await self.nats_conn.request(
                self.nats_health_check_subject,
                json.dumps(test_payload).encode(),
                timeout=timeout,
            )
        except (nats.errors.Error, nats.errors.TimeoutError) as exc:
            self.on_unhealthy(
                health_check_name=health_check_name,
                cause=f"NATS request to test subject failed after timeout={timeout}. Exception: "
                + format_exception(exc),
            )
            return
        test_response = json.loads(response.data)
        if test_payload != test_response:
            self.on_unhealthy(
                health_check_name=health_check_name,
                cause="NATS request to test subject returned incorrect data. "
                f"Expected {test_payload}. "
                f"Received {test_response}.",
            )
        else:
            self.on_nats_health_status(
                healthy=True, health_check_name=health_check_name
            )

    async def check_nats_service_health(self) -> None:
        """Check the NATS service's health endpoint to determine if it is healthy."""
        health_check_name = self.check_nats_service_health.__name__
        address = self.config.NATS_SERVICE_HEALTH_CHECK_ADDRESS
        # TODO
        # We will have to switch to aiohttp when  PR #58 is merged
        # https://github.com/edf-re/powerflex_edge_storage_interface/pull/58
        try:
            response = requests.get(
                address, timeout=self.config.NATS_SERVICE_HEALTH_CHECK_TIMEOUT
            )
        except requests.exceptions.ConnectionError as exc:
            self.on_unhealthy(
                health_check_name=health_check_name,
                cause=f"Could not connect to NATS service health check address={address}. Exception: "
                + format_exception(exc),
            )
            return

        status = response.status_code

        if status != 200:
            self.on_unhealthy(
                health_check_name=health_check_name,
                cause=f"NATS service health check returned non-200 status code {status}, address={address}",
            )
        else:
            self.on_nats_health_status(
                healthy=True, health_check_name=health_check_name
            )

    async def periodically_check_nats_health(self) -> NoReturn:
        """Periodically check the NATS health by running the following checks.

        1. Check if a test subject only used by this service responds to a NATS request
        2. Check if the NATS service's health check is bad

        If any health check keeps failing for longer than
        NATS_HEALTH_CHECK_UNHEALTHY_TIMEOUT_SEC,
        then mark the service as unhealth.

        If any health check fails at all, mark the service as not ready.

        Mark the service as ready if all health checks pass.
        """
        await self._async_setup()

        while True:
            await asyncio.gather(
                self.check_echo_nats_request(), self.check_nats_service_health()
            )
            await asyncio.sleep(self.config.NATS_HEALTH_CHECK_REQUEST_PERIOD_SEC)
