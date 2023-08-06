import logging

import uvicorn  # type: ignore
from starlette.routing import Mount, Router

from powerflex_monitoring.health_check import HealthCheck
from powerflex_monitoring.prometheus_metrics import make_metrics_app
from powerflex_monitoring.ready_check import ReadyCheck

logger = logging.getLogger(__name__)


class MonitoringServer:
    def __init__(self, port: int):
        self.port = port
        self.health_check = HealthCheck()
        self.ready_check = ReadyCheck()
        # The prometheus client library does not have type hints
        self.metrics_app = make_metrics_app()  # type: ignore

        health_check_name = "health"
        ready_check_name = "ready"
        metrics_name = "metrics"
        route_names = [health_check_name, ready_check_name, metrics_name]

        self.app = Router(
            routes=[
                Mount(
                    "/monitoring",
                    routes=[
                        Mount(
                            "/health",
                            app=self.health_check.asgi_app,
                            name=health_check_name,
                        ),
                        Mount(
                            "/ready",
                            app=self.ready_check.asgi_app,
                            name=ready_check_name,
                        ),
                        Mount(
                            "/metrics",
                            app=self.metrics_app,
                            name=metrics_name,
                        ),
                    ],
                )
            ]
        )

        for name in route_names:
            logging.info(
                "Added route at port %s: %s",
                self.port,
                self.app.url_path_for(name, path="/"),
            )

    def start(self) -> None:
        logger.info("🚀 Starting monitoring server at port %s", self.port)
        uvicorn.run(
            # For some reason, the types that come with starlette don't line up
            # with the type hints for uvicorn.
            self.app,  # type: ignore
            host="0.0.0.0",
            port=self.port,
            log_level="warning",
        )
