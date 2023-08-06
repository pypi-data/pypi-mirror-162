import inspect
import logging
import os
from typing import Any, Dict

from rich.logging import RichHandler
from typing_extensions import Final

__all__ = (
    "log",
    "hlog",
)

_FORMAT: Final[str] = "%(message)s"
_COLORS: Final[Dict[int, str]] = {
    logging.DEBUG: "bold blue",
    logging.INFO: "bold green",
    logging.WARNING: "bold dim yellow",
    logging.ERROR: "bold red",
    logging.CRITICAL: "bold dim red",
}


def setup_logging() -> None:
    """Set up logging."""
    logging.basicConfig(
        level="INFO",
        format=_FORMAT,
        datefmt="[%X]",
        handlers=[
            RichHandler(
                show_level=False,
                show_path=False,
                show_time=False,
            )
        ],
    )


setup_logging()
logger = logging.getLogger("hoist")


def log(
    key: str,
    value: Any,
    *,
    level: int = logging.INFO,
    highlight: bool = False,
) -> None:
    """Log a rich message."""
    trace = os.getenv("HOIST_TRACE")
    frame = inspect.currentframe()
    assert frame
    back = frame.f_back
    assert back

    caller = back.f_code.co_name

    if caller == "hlog":
        nback = back.f_back
        assert nback
        caller = nback.f_code.co_name

    k = key if trace != "only" else caller
    prefix = f"([bold green]{caller}[/]) " if trace == "all" else ""

    logger.log(
        level,
        f"{prefix}[{_COLORS[level]}]{k}:[/] {value}",
        extra={
            "markup": True,
            **(
                {
                    "highlighter": None,
                }
                if not highlight
                else {}
            ),
        },
    )


def hlog(
    key: str,
    value: Any,
    *,
    level: int = logging.INFO,
) -> None:
    """Log a highligted rich message."""
    log(
        key,
        value,
        level=level,
        highlight=True,
    )
