from typing import (
    TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Optional, Tuple, Type,
    TypeVar, Union
)

from typing_extensions import Protocol

if TYPE_CHECKING:
    from versions import Version
    from yarl import URL

    from .message import Message
    from .server import Server

_T = TypeVar("_T")


class DataclassLike(Protocol):
    """Protocol representing a dataclass-like object."""

    __annotations__: Dict[str, Any]

    def __init__(self, *args, **kwargs) -> None:
        ...


_A = TypeVar("_A", bound=Type[DataclassLike])

Payload = Dict[str, Any]
Operator = Callable[[_T], Awaitable[Any]]
SchemaNeededType = Union[Type[Any], Tuple[Optional[Type[Any]], ...]]
Schema = Dict[str, SchemaNeededType]
Operations = Dict[str, Operator]
UrlLike = Union[str, "URL"]
LoginFunc = Callable[["Server", str], Awaitable[bool]]
ResponseErrors = Dict[int, Tuple[str, str]]
Listener = Callable[["Message", _T], Awaitable[None]]
ListenerData = Tuple[Listener[_A], Union[_A, Schema]]
MessageListeners = Dict[
    Optional[Union[Tuple[str, ...], str]],
    List[ListenerData[_A]],
]
VersionLike = Union[str, "Version"]


class Messagable(Protocol):
    """Protocol representing a messagable target."""

    async def message(
        self,
        msg: str,
        data: Optional[Payload] = None,
        replying: Optional["Message"] = None,
    ) -> "Message":
        """Send a message."""
        ...


TransportMessageListener = Callable[
    [Messagable, str, Payload, Optional["Message"]],
    Awaitable[None],
]
