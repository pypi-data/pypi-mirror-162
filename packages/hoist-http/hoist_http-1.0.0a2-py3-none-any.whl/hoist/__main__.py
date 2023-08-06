from typing import Optional

import click
from rich import print

from .server import Server
from .version import __version__


@click.command()
@click.option(
    "--token",
    "-t",
    type=str,
    help="Login token to use for the server.",
    default=None,
)
@click.option(
    "--host",
    "-h",
    type=str,
    help="Where to host the server.",
    default="0.0.0.0",
)
@click.option(
    "--port",
    "-p",
    type=int,
    help="What port to put the server on.",
    default=5000,
)
@click.option(
    "--log-level",
    "-l",
    type=int,
    help="Log level to use.",
    default=20,
)
@click.option(
    "--minimum-version",
    "-m",
    type=str,
    help="Minimum version to connect to the server with.",
    default=__version__,
)
@click.option(
    "--default-len",
    "-d",
    type=int,
    help="Default length of randomly generated key.",
    default=25,
)
@click.option(
    "--version",
    "-v",
    help="Display version and exit.",
    is_flag=True,
)
def main(
    token: Optional[str],
    host: str,
    port: int,
    log_level: int,
    minimum_version: Optional[str],
    default_len: int,
    version: bool,
) -> None:
    """Start a new Hoist server."""
    if version:
        return print(f"[bold cyan]Hoist {__version__}[/]")

    server = Server(
        token=token,
        log_level=log_level,
        minimum_version=minimum_version,
        default_token_len=default_len,
    )
    server.start(host=host, port=port)


if __name__ == "__main__":
    main()
