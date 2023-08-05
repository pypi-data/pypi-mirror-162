"""Sync version in pyproject.toml with __version__."""
import re
from pathlib import Path

import logzero
import tomlkit
from logzero import logger

from sync_version.loglevel import loglevel

logzero.loglevel(loglevel(20))
logger.debug("debug on")


def convert(text: str) -> str:
    """Convert version in pyproject.toml to version used in __version__.py.

    s.split("-")[0] + "".join([] if "-" not in s else [s.split("-")[-1][0] + s.split("-")[-1][-1]])

    >>> convert("0.1.0")
    '0.1.0'
    >>> convert("0.1.0-alpha0")
    '0.1.0a0'
    """
    _ = text.split("-")
    return _[0] + "".join([] if "-" not in text else [_[-1][0] + _[-1][-1]])


def fetch_info():
    """Fetch name and version from pyproject.toml."""
    try:
        with open("pyproject.toml", encoding="utf8") as fha:
            jdata = tomlkit.load(fha)
    except Exception as exc:
        logger.exception(exc)
        raise

    try:
        name = jdata.get("tool").get("poetry").get("name")  # type: ignore
    except Exception:
        name = ""

    try:
        version = jdata.get("tool").get("poetry").get("version")  # type: ignore
    except Exception:
        version = ""

    return name, convert(version)


def sync_version(debug: bool = False, dry_run: bool = False):
    """Sync version in pyproject.toml with __version__.

    Args"
        debug: if True set loglevel to 10.

    Typical rundowns:

    poetry version prerelease
    sync-version

    poetry version patch
    sync-version
    """
    try:
        name, version = fetch_info()
    except Exception as exc:
        logger.exception(exc)
        raise

    init_py = Path(name.replace("-", "_")) / "__init__.py"
    if not init_py.is_file():
        logger.warning("File [%s] does not exist or is not a file.", init_py)
        raise SystemExit(1)

    try:
        text = init_py.read_text(encoding="utf8")
    except Exception as exc:
        logger.exception(exc)
        raise

    logger.debug("version: %s", version)

    try:
        text1 = re.sub(
            r"""(__version__\s*=\s*["'])([\w_.-]+)""", rf"\g<1>{version}", text, count=1
        )
    except Exception as exc:
        logger.exception(exc)
        raise

    assert version in text1, "Something is not right...check it out."

    # write back to __init__.py
    if text1.strip() != text.strip():
        logger.info(" %s written to __init__.py.", version)
        if not dry_run:
            try:
                init_py.write_text(text1, encoding="utf8")
            except Exception as exc:
                logger.exception(exc)
                raise
        else:
            logger.info("Dry-run: nothing changed")
    else:
        logger.info("__init__.py remains unchanged.")

    if debug:
        logger.debug("__init__.py: \n%s", text1)
    else:
        logger.info(
            "__init__.py.splitlines()[:4]: \n%s", "\n".join(text1.splitlines()[:4])
        )


if __name__ == "__main__":
    sync_version()
