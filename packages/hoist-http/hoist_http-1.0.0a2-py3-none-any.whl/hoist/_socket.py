import json
import logging
from typing import Any, List, NoReturn, Optional

from starlette.datastructures import Address
from starlette.websockets import WebSocket

from ._errors import *
from ._logging import hlog, log
from ._operations import verify_schema
from ._typing import Payload, Schema
from .exceptions import ClientError, CloseSocket

__all__ = (
    "make_client_msg",
    "make_client",
    "Socket",
)


def make_client_msg(addr: Optional[Address], to: bool = False) -> str:
    """Create a client message."""
    target: str = "from" if not to else "to"
    return f" {target} [bold cyan]{addr.host}:{addr.port}[/]" if addr else ""


def make_client(addr: Optional[Address]) -> str:
    """Make a client string."""
    return f"[bold cyan]{addr.host}:{addr.port}[/]" if addr else "client"


class Socket:
    """Class for handling a WebSocket."""

    def __init__(
        self,
        ws: WebSocket,
    ):
        self._ws = ws
        self._logged: bool = False

    async def connect(self) -> None:
        """Establish the WebSocket connection."""
        ws = self._ws
        await ws.accept()

        log(
            "connect",
            f"connecting{make_client_msg(ws.client, to=True)}",
        )

    @property
    def ws(self) -> WebSocket:
        """Raw WebSocket object."""
        return self._ws

    @property
    def logged(self) -> bool:
        """The authentication status of the current connection."""
        return self._logged

    @logged.setter
    def logged(self, value: bool) -> None:
        self._logged = value

    async def _send(
        self,
        *,
        success: bool = True,
        payload: Optional[Payload] = None,
        code: int = 0,
        error: Optional[str] = None,
        message: Optional[str] = None,
        desc: Optional[str] = None,
    ) -> None:
        """Send a message to the client."""
        content = {
            "success": success,
            "data": payload,
            "error": error,
            "code": code,
            "message": message,
            "desc": desc,
        }
        hlog("send", content, level=logging.DEBUG)
        await self.ws.send_json(content)

    async def error(
        self,
        code: int,
        *,
        description: Optional[str] = None,
        payload: Optional[Payload] = None,
    ) -> NoReturn:
        """Send an error to the client."""
        err = ERRORS[code]
        error = err[0]
        message = err[1]

        await self._send(
            code=code,
            desc=description,
            error=error,
            message=message,
            payload=payload,
        )
        raise ClientError(code=code, error=error, message=message)

    async def success(
        self,
        payload: Optional[Payload] = None,
        *,
        message: Optional[str] = None,
    ) -> None:
        """Send a success to the client."""
        await self._send(
            code=0,
            message=message,
            payload=payload,
        )

    async def recv(self, schema: Schema) -> List[Any]:
        """Receive a message from the client."""
        try:
            load: dict = json.loads(await self.ws.receive_text())
        except json.JSONDecodeError:
            await self.error(INVALID_JSON)

        hlog("receive", load, level=logging.DEBUG)

        if load.get("end"):
            raise CloseSocket

        try:
            verify_schema(schema, load)
        except Exception:
            await self.error(INVALID_CONTENT)

        return [load[i] for i in schema]

    async def recv_only(self, schema: Schema) -> Any:
        """Receive a single key from the client."""
        return (await self.recv(schema))[0]

    async def close(self, code: int) -> None:
        """Gracefully close the connection."""
        await self.ws.close(code)
        log(
            "disconnect",
            f"no longer receiving{make_client_msg(self.ws.client)}",
        )

    @property
    def address(self) -> Optional[Address]:
        """Address object of the connection."""
        return self.ws.client
