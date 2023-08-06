import abc
import json
from typing import TypedDict


# Necessary because mypy does not accept "TypedDict" as a type
# error: Variable "typing.TypedDict" is not valid as a type
class AnyTypedDict(TypedDict):
    pass


class ServerBase:
    @property
    @abc.abstractmethod
    def status(self) -> int:
        pass  # pragma: no cover

    @property
    @abc.abstractmethod
    def response(self) -> AnyTypedDict:
        pass  # pragma: no cover

    # The type of this is too long and something like
    # Callable[[Union[HTTPScope, WebSocketScope, LifespanScope], Callable[[], Awaitable[Union[HTTPRequestEvent, HTTPDisconnectEvent, WebSocketConnectEvent, WebSocketReceiveEvent, WebSocketDisconnectEvent, LifespanStartupEvent, LifespanShutdownEvent]]], Callable[[Union[HTTPResponseStartEvent, HTTPResponseBodyEvent, HTTPServerPushEvent, HTTPDisconnectEvent, WebSocketAcceptEvent, WebSocketSendEvent, WebSocketResponseStartEvent, WebSocketResponseBodyEvent, WebSocketCloseEvent, LifespanStartupCompleteEvent, LifespanStartupFailedEvent, LifespanShutdownCompleteEvent, LifespanShutdownFailedEvent]], Awaitable[None]]], Awaitable[None]]]
    # See it with:
    # from asgiref.typing import ASGIApplication as ASGIApplication
    async def asgi_app(self, scope, receive, send) -> None:  # type: ignore
        """ASGI app which returns this class' status code and a JSON response.

        Based on the Prometheus server from the client library.
        """
        assert scope.get("type") == "http"

        status = self.status
        header = ("Content-Type", "application/json")
        output = json.dumps(self.response)

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
