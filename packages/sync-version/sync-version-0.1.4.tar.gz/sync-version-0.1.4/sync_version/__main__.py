"""Prep __main__ entry."""
from typing import Optional

import logzero
import typer
from logzero import logger

from sync_version import __version__, sync_version
from sync_version.loglevel import loglevel

logzero.loglevel(loglevel())

app = typer.Typer(
    name="sync-version",
    add_completion=False,
    help="pip install robot",
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{app.info.name} v.{__version__}")
        raise typer.Exit()


@app.command()
def main(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-y",
        is_flag=True,
        help="Dry-run: wont write to __init__py.",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        is_flag=True,
        help="Turn on debug mode. Note that debug can also be turned on by 'set LOGLEVEL=debug' or 'export LOGLEVEL=debug'.",
    ),
    version: Optional[bool] = typer.Option(  # pylint: disable=(unused-argument
        None,
        "--version",
        "-v",
        "-V",
        help="Show version info and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
):
    """Sync __version__ in __init__py with version in pyproject.toml.

    e.g.

    poetry version prerelease
    # in the directory where pyproject.toml is located
    sync-version  # or ython -m sync_version

    poetry version patch
    sync-version  # or ython -m sync_version

    """
    if debug:
        logger.info("debug is on")
        # logzero.loglevel(loglevel(10, force=True))
        # logzero.loglevel(loglevel(20, force=True))
        logzero.loglevel(loglevel(10))

    logger.debug("debug")

    try:
        sync_version(dry_run=dry_run, debug=debug)
    except Exception as exc:
        logger.error(exc)
        typer.Exit(1)


if __name__ == "__main__":
    # set LOGLEVEL=10 or debug or DEBUG to turn on debug
    logger.debug(" debug on (main)")
    app()
