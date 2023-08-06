from typing import Any, Dict, Optional, Type

from ._typing import Payload, SchemaNeededType

__all__ = (
    "ServerResponseError",
    "ServerLoginError",
    "ClientError",
    "InvalidVersionError",
    "SchemaValidationError",
    "NotConnectedError",
    "InvalidOperationError",
    "AlreadyConnectedError",
    "InvalidActionError",
    "ServerConnectError",
    "BadContentError",
    "ConnectionFailedError",
    "ServerNotStartedError",
    "AlreadyInUseError",
)


class _ResponseError(Exception):
    def __init__(
        self,
        *args,
        code: int,
        error: str,
        message: str,
        payload: Optional[Payload] = None,
        **kwargs,
    ) -> None:
        self._code: int = code
        self._error: str = error
        self._message: str = message
        self._payload = payload
        super().__init__(*args, **kwargs)

    @property
    def code(self) -> int:
        """Error code."""
        return self._code

    @property
    def error(self) -> str:
        """Error name."""
        return self._error

    @property
    def message(self) -> str:
        """Error message."""
        return self._message

    @property
    def payload(self) -> Optional[Dict[str, Any]]:
        """Error payload."""
        return self._payload


class ServerResponseError(_ResponseError):
    """Generic bad server response."""


class ServerLoginError(Exception):
    """Failed to log in to the target server."""


class ClientError(_ResponseError):
    """The client caused an error on the server."""


class InvalidVersionError(Exception):
    """Version is not high enough."""


class SchemaValidationError(Exception):
    """Schema validation failed."""

    def __init__(
        self,
        *args,
        current: Optional[Type[Any]],
        needed: SchemaNeededType,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._current = current
        self._needed = needed

    @property
    def needed(self) -> SchemaNeededType:
        """Type(s) needed to be valid."""
        return self._needed

    @property
    def current(self) -> Optional[Type[Any]]:
        """Current type."""
        return self._current


class CloseSocket(Exception):
    """Close the socket."""


class NotConnectedError(Exception):
    """Socket is not connected to the server."""


class InvalidOperationError(Exception):
    """Operation was not found."""


class AlreadyConnectedError(Exception):
    """Attempted to connect to the WebSocket twice."""


class InvalidActionError(Exception):
    """Invalid action was sent to the server."""


class ServerConnectError(Exception):
    """Failed to connect to a server."""


class BadContentError(Exception):
    """Invalid JSON content was sent to the server."""


class ConnectionFailedError(Exception):
    """Failed to connect to the target server.."""


class ServerNotStartedError(Exception):
    """Server is not started."""


class AlreadyInUseError(Exception):
    """Port is already in use."""
