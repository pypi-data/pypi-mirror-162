import logging
from typing import TYPE_CHECKING, List, NamedTuple, Optional, overload

from aiohttp import ClientWebSocketResponse
from typing_extensions import Literal

from ._errors import INVALID_CONTENT
from ._logging import hlog, log
from ._messages import (
    LISTENER_CLOSE, LISTENER_OPEN, NEW_MESSAGE, SINGLE_NEW_MESSAGE,
    create_message
)
from ._typing import Payload, TransportMessageListener
from .exceptions import (
    BadContentError, InvalidVersionError, ServerLoginError, ServerResponseError
)
from .version import __version__

if TYPE_CHECKING:
    from .client import Connection

__all__ = ("ServerSocket",)


class _Response(NamedTuple):
    success: bool
    data: Optional[Payload]
    error: Optional[str]
    message: Optional[str]
    desc: Optional[str]
    code: int


class ServerSocket:
    """Class for handling a WebSocket connection to a server."""

    def __init__(
        self,
        client: "Connection",
        ws: ClientWebSocketResponse,
        token: str,
    ) -> None:
        self._ws = ws
        self._token = token
        self._logged: bool = False
        self._closed: bool = False
        self._message_listener: Optional[TransportMessageListener] = None
        self._client = client

    async def _rc(self) -> _Response:
        """Receive and parse a server response."""
        json = await self._ws.receive_json()
        hlog(
            "receive",
            json,
            level=logging.DEBUG,
        )
        return _Response(**json)

    async def _recv(self) -> _Response:
        """High level function to properly accept data from the server."""
        res = await self._rc()
        messages: List[Payload] = []

        code = res.code
        error = res.error
        message = res.message
        data = res.data

        if res.code != 0:
            assert error
            assert message

            if res.code == INVALID_CONTENT:
                assert data
                needed_raw = data["needed"]
                needed = (
                    ", ".join(needed_raw)
                    if isinstance(needed_raw, list)
                    else needed_raw  # fmt: off
                )

                raise BadContentError(
                    f'sent type {data["current"]} when server expected {needed}',  # noqa
                )

            raise ServerResponseError(
                f"code {code} [{error}]: {message}",
                code=res.code,
                error=error,
                message=message,
                payload=data,
            )

        if res.message == SINGLE_NEW_MESSAGE:
            assert data
            messages.append(data)
            res = await self._recv()

        if res.message == LISTENER_OPEN:
            log(
                "listener",
                "now receiving",
                level=logging.DEBUG,
            )

            while True:
                new_res_json = await self._ws.receive_json()
                new_res = _Response(**new_res_json)
                hlog(
                    "listener receive",
                    new_res_json,
                    level=logging.DEBUG,
                )

                if new_res.message == LISTENER_CLOSE:
                    break

                elif new_res.message in {NEW_MESSAGE, SINGLE_NEW_MESSAGE}:
                    data = new_res.data
                    assert data
                    messages.append(data)

            log(
                "listener",
                "done receiving",
                level=logging.DEBUG,
            )

        listener = self._message_listener
        assert listener

        for i in messages:
            client = self._client
            reply = i["replying"]

            await listener(
                client,
                i["message"],
                i["data"],
                await create_message(client, reply) if reply else None,
            )

        return res

    async def login(self, listener: TransportMessageListener) -> None:
        """Send login message to the server."""
        self._message_listener = listener

        try:
            await self.send(
                {
                    "token": self._token,
                    "version": __version__,
                },
                reply=True,
            )
        except ServerResponseError as e:
            if e.code == 4:
                assert e.payload
                raise InvalidVersionError(
                    f"server needs version {e.payload['needed']}, but you have {__version__}",  # noqa
                )
            if e.code == 3:
                raise ServerLoginError("login token is not valid") from e

            raise e  # we shouldnt ever get here

        self._logged = True

    @property
    def logged(self) -> bool:
        """Whether the socket has authenticated with the server."""
        return self._logged

    async def close(self) -> None:
        """Close the socket."""
        log("close", "closing socket", level=logging.DEBUG)

        if not self._closed:
            await self.send({"end": True})
        else:
            log(
                "close",
                "attempted to double close connection",
                level=logging.WARNING,
            )

        self._closed = True

    @overload
    async def send(  # type: ignore
        self,
        payload: Payload,
        *,
        reply: Literal[False] = False,
    ) -> Literal[None]:
        """Send a message to the server."""
        ...

    @overload
    async def send(
        self,
        payload: Payload,
        *,
        reply: Literal[True] = True,
    ) -> _Response:
        """Send a message to the server."""
        ...

    async def send(
        self,
        payload: Payload,
        *,
        reply: bool = False,
    ) -> Optional[_Response]:
        """Send a message to the server."""
        await self._ws.send_json(payload)
        hlog("send", payload, level=logging.DEBUG)

        if reply:
            return await self._recv()

        return None
