import logging
from typing import (
    TYPE_CHECKING, Any, List, Optional, Tuple, TypeVar, Union, get_type_hints
)

from typing_extensions import Final

from ._logging import hlog
from ._operations import verify_schema
from ._typing import (
    DataclassLike, Listener, ListenerData, Messagable, MessageListeners,
    Payload, Schema
)

if TYPE_CHECKING:
    from .message import Message

__all__ = (
    "MessageListener",
    "create_message",
)

T = TypeVar("T", bound=DataclassLike)

NEW_MESSAGE: Final[str] = "newmsg"
LISTENER_OPEN: Final[str] = "open"
LISTENER_CLOSE: Final[str] = "done"
SINGLE_NEW_MESSAGE: Final[str] = "s_newmsg"


async def create_message(conn: Messagable, data: Payload) -> "Message":
    """Generate a message object from a payload."""
    from .message import Message

    reply = data.get("replying")

    return Message(
        conn,
        data["message"],
        data["id"],
        data=data["data"],
        replying=await create_message(conn, reply) if reply else None,
    )


async def _process_listeners(
    listeners: Optional[List[ListenerData]],
    msg: str,
    id: int,
    payload: Payload,
    conn: Messagable,
    *,
    replying: Optional["Message"] = None,
) -> None:
    from .message import Message

    hlog(
        "listeners",
        f"processing: {listeners}",
        level=logging.DEBUG,
    )

    for i in listeners or ():
        func = i[0]
        param = i[1]
        is_schema: bool = isinstance(param, dict)

        schema: Any = param if is_schema else get_type_hints(param)
        verify_schema(schema, payload)

        await func(
            Message(
                conn,
                msg,
                id,
                data=payload,
                replying=replying,
            ),
            payload if is_schema else param(**payload),  # type: ignore
        )


class MessageListener:
    """Base class for handling message listening."""

    def __init__(
        self,
        extra_listeners: Optional[MessageListeners] = None,
    ):
        self._message_listeners: MessageListeners = {
            **(extra_listeners or {}),
        }
        self._current_id = 0

    @property
    def message_listeners(self) -> MessageListeners:
        """Listener function for messages."""
        return self._message_listeners

    async def _call_listeners(
        self,
        ws: Messagable,
        message: str,
        payload: Payload,
        replying: Optional["Message"],
    ) -> None:
        self._current_id += 1
        ml = self.message_listeners
        listeners = ml.get(message)
        data = (message, self._current_id, payload, ws)
        await _process_listeners(listeners, *data, replying=replying)

        glbl = ml.get(None)
        await _process_listeners(glbl, *data, replying=replying)

    def receive(
        self,
        message: Optional[Union[str, Tuple[str, ...]]] = None,
        parameter: Optional[Union[Schema, T]] = None,
    ):
        """Add a listener for message receiving."""

        def decorator(func: Listener):
            listeners = self.message_listeners

            param = parameter

            if not param:
                hints = get_type_hints(func)
                if hints:
                    param = hints[tuple(hints.keys())[1]]

            value = (func, (param or {}))

            if message in listeners:
                listeners[message].append(value)
            else:
                listeners[message] = [value]

        return decorator

    @property
    def current_id(self) -> int:
        """Current message ID."""
        return self._current_id
