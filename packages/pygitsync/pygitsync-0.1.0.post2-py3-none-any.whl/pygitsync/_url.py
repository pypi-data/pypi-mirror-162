import logging
import pathlib
import re
from urllib.parse import unquote, urlparse

log = logging.getLogger(__name__)

SCP_STYLE_REGEX = r"^(\w+@)?[\w.]+:[\w/]+"
URL_PREFIX_REGEX = r"^(file)|(ftp(s)?)|(git)|(http(s)?)|(ssh)://"


def _extract_from_url(url: str) -> str:
    return (
        pathlib.PurePosixPath(unquote(urlparse(url).path))
        .parts[-1]
        .replace(".git", "")
    )


def _extract_from_raw_path(path: str) -> str:
    return pathlib.PurePosixPath(path).parts[-1].replace(".git", "")


def _extract_from_scp_syntax(url: str) -> str:
    tokens = url.split(":")

    return (
        pathlib.PurePosixPath(unquote(tokens[1])).parts[-1].replace(".git", "")
    )


def extract_git_project(url: str) -> str:
    """Extract git project name from a git repo URL.

    Args:
        url: Git repo URL to parse

    Returns:
        Git project name
    """
    if re.match(URL_PREFIX_REGEX, url.lower()):
        log.debug(f"extracting git project name from URL, {url}")
        value = _extract_from_url(url)
    elif re.match(SCP_STYLE_REGEX, url.lower()):
        log.debug(
            f"extracting git project name from SCP-style path-spec, {url}"
        )
        value = _extract_from_scp_syntax(url)
    else:
        log.debug(f"extracting git project name from raw posix path, {url}")
        value = _extract_from_raw_path(url)

    return value
