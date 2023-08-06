import logging
from typing import TypedDict

from powerflex_monitoring.server_base import ServerBase

logger = logging.getLogger(__name__)


class ReadyCheckResponse(TypedDict):
    ready: bool
    cause: str


class ReadyCheck(ServerBase):
    def __init__(
        self,
        initial_state: bool = False,
        initial_cause: str = "Service is initializing",
    ) -> None:
        self._is_ready = initial_state
        self._cause = initial_cause

    @property
    def status(self) -> int:
        return 200 if self._is_ready else 503

    @property
    def response(self) -> ReadyCheckResponse:
        return {"ready": self._is_ready, "cause": self._cause}

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    def set_ready(self, ready: bool, cause: str = "Unknown") -> None:
        if ready != self._is_ready:
            logger.info(
                "Service has been marked as %s. Cause: %s",
                "ready" if ready else "not ready",
                cause,
                stack_info=True,
            )
        self._is_ready = ready
        self._cause = cause
