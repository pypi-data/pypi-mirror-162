from typing import Optional

from ._messages import MessageListener
from ._typing import Messagable, Payload


class Message(MessageListener):
    """Object handling a messagable target."""

    def __init__(
        self,
        conn: Messagable,
        msg: str,
        id: int,
        *,
        data: Optional[Payload] = None,
        replying: Optional["Message"] = None,
    ) -> None:
        self._conn = conn
        self._msg = msg
        self._id = id
        self._data = data or {}
        self._replying = replying
        super().__init__()

    @property
    def content(self) -> str:
        """Message content."""
        return self._msg

    @property
    def data(self) -> Payload:
        """Raw message payload."""
        return self._data

    @property
    def replying(self) -> Optional["Message"]:
        """Message that the current message is replying to."""
        return self._replying

    @property
    def id(self) -> int:
        """Message ID."""
        return self._id

    async def reply(
        self,
        msg: str,
        data: Optional[Payload] = None,
    ) -> "Message":
        """Send a message to the target."""
        return await self._conn.message(msg, data or {}, replying=self)

    def to_dict(self) -> dict:
        """Convert the message to a dictionary."""
        reply = self.replying

        return {
            "replying": reply.to_dict() if reply else None,
            "id": self.id,
            "data": self.data,
            "message": self.content,
        }

    def __repr__(self) -> str:
        values = [f"{k}={repr(v)}" for k, v in self.to_dict().items()]
        return f"Message({', '.join(values)})"
