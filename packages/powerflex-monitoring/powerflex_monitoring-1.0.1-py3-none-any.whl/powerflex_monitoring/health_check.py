import logging
from typing import TypedDict

from powerflex_monitoring.server_base import ServerBase

logger = logging.getLogger(__name__)


class HealthCheckResponse(TypedDict):
    healthy: bool
    cause: str


class HealthCheck(ServerBase):
    def __init__(self) -> None:
        self._is_healthy = True
        self._cause = "Initial state"

    @property
    def status(self) -> int:
        return 200 if self._is_healthy else 503

    @property
    def response(self) -> HealthCheckResponse:
        return {"healthy": self._is_healthy, "cause": self._cause}

    def make_unhealthy(self, cause: str = "Unknown") -> None:
        logger.error(
            "Service has been marked as unhealthy. Cause: %s", cause, stack_info=True
        )
        self._is_healthy = False
        self._cause = cause
