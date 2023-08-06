import abc
import json
from typing import TypedDict

from starlette.types import Receive, Scope, Send


# Necessary because mypy does not accept "TypedDict" as a type
# error: Variable "typing.TypedDict" is not valid as a type
class AnyTypedDict(TypedDict):
    pass


class ServerBase:
    @property
    @abc.abstractmethod
    def _status(self) -> int:
        pass  # pragma: no cover

    @property
    @abc.abstractmethod
    def _response(self) -> AnyTypedDict:
        pass  # pragma: no cover

    async def asgi_app(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI app which returns this class' status code and a JSON response.

        Based on the Prometheus server from the client library.
        """
        assert scope.get("type") == "http"

        status = self._status
        header = ("Content-Type", "application/json")
        output = json.dumps(self._response)

        payload = await receive()
        if payload.get("type") == "http.request":
            await send(
                {
                    "type": "http.response.start",
                    "status": status,
                    "headers": [tuple(x.encode("utf8") for x in header)],
                }
            )
            await send({"type": "http.response.body", "body": output.encode("utf8")})
