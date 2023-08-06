import asyncio
import inspect
import logging
import os
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Awaitable, Callable, Coroutine, Optional, Union

from rich.console import Console

from ._typing import UrlLike
from .client import Connection
from .server import Server

print_exc = Console().print_exception

__all__ = (
    "main",
    "connect",
    "start",
    "connect_to",
    "debug",
    "serve",
)


def main(func: Callable[[], Coroutine[Any, Any, Any]]) -> None:
    """Run a main async function."""
    frame = inspect.currentframe()
    assert frame
    assert frame.f_back

    if frame.f_back.f_globals["__name__"] == "__main__":
        try:
            asyncio.run(func())
        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                return

            print_exc()


@asynccontextmanager
async def connect(
    token: str,
    url: UrlLike = "http://localhost:5000",
    **kwargs: Any,
):
    """Connect to a Hoist server."""
    try:
        conn = Connection(url, token, **kwargs)
        await conn.connect()
        yield conn
    finally:
        await conn.close()


@contextmanager
def serve(
    token: Optional[str] = None,
    server: Optional[Server] = None,
    *,
    host: str = "0.0.0.0",
    port: int = 5000,
    **kwargs,
):
    """Serve a Hoist server."""
    try:

        srvr = server or Server(token, **kwargs)
        srvr.start(host=host, port=port)
        yield srvr
    finally:
        srvr.close()


def connect_to(
    url: UrlLike,
    token: str,
    **kwargs: Any,
):
    """Call a function with the connection."""

    def inner(func: Callable[[Connection], Awaitable[Any]]):
        async def _wrapper():
            conn = Connection(url, token, **kwargs)

            try:
                await conn.connect()
                await func(conn)
            except BaseException as e:
                if isinstance(e, KeyboardInterrupt):
                    return

                print_exc()
            finally:
                if not conn.closed:
                    await conn.close()

        coro = _wrapper()

        try:
            asyncio.run(coro)
        except RuntimeError:
            asyncio.get_event_loop().create_task(coro)

    return inner


def start(
    token: Optional[str] = None,
    server: Optional[Server] = None,
    *,
    host: str = "0.0.0.0",
    port: int = 5000,
    **kwargs,
) -> Server:
    """Start a Hoist server."""
    srvr = server or Server(token, **kwargs)
    srvr.start(host=host, port=port)
    return srvr


def debug(
    *,
    trace: Union[bool, str] = False,
    enable_uvicorn: bool = False,
) -> None:
    """Enable debug logging."""
    logging.getLogger("hoist").setLevel(logging.DEBUG)
    os.environ["HOIST_TRACE"] = (
        trace if not isinstance(trace, bool) else "all" if trace else ""
    )

    if enable_uvicorn:
        logging.getLogger("uvicorn.error").disabled = False
        logging.getLogger("uvicorn.access").disabled = False
