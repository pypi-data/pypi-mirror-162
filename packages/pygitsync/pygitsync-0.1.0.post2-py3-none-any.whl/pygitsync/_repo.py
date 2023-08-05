"""Manage git repository fetching."""

import logging
import pathlib
import re
import typing

import git

# NOTE: mypy complaining about missing type hints
import parver  # type: ignore

from ._configuration import GitRefType, RepoConfiguration
from ._url import extract_git_project

log = logging.getLogger(__name__)


class InvalidBranchError(Exception):
    """Problem occurred processing branch."""


def _get_remote(repo: git.Repo) -> git.Remote:
    remotes = repo.remotes
    if len(remotes) != 1:
        log.error(f"not just one remote, {str(remotes)}")
        raise RuntimeError("Something is wrong as there is not just one remote")

    origin = remotes[0]

    return origin


def _evaluate_branch(name_pattern: str, repo: git.Repo) -> None:
    try:
        # name "pattern" must be an exact match to a single branch.
        if name_pattern != repo.active_branch.name:
            log.debug(
                "active branch failed to match name pattern, "
                f"{repo.active_branch.name}, {name_pattern}"
            )
            repo.heads[name_pattern].checkout()

        origin = _get_remote(repo)
        origin.pull()
    except Exception as e:
        log.debug(f"exception evaluating branch, {str(e)}")
        raise InvalidBranchError(f"Invalid branch name, {name_pattern}") from e


def _evaluate_tag(name_pattern: str, repo: git.Repo) -> None:
    origin = _get_remote(repo)
    origin.fetch()

    pattern_matched_tags = [
        x for x in repo.tags if re.match(name_pattern, x.name)
    ]
    selected_tag: git.Reference
    if len(pattern_matched_tags) == 1:
        selected_tag = pattern_matched_tags[0]
        log.debug(
            f"single tag found matching pattern, {selected_tag.name} (tag), "
            f"{name_pattern} (pattern)"
        )
    elif len(pattern_matched_tags) != 0:
        log.debug(
            f"multiple tags found matching pattern, {name_pattern} (pattern), "
            f"{str([x.name for x in pattern_matched_tags])}"
        )
        sorted_tags = sorted(
            pattern_matched_tags,
            key=lambda x: parver.Version.parse(x.name),
            reverse=True,
        )
        selected_tag = sorted_tags[0]
        log.debug(f"selected tag from multiple, {selected_tag.name}")
    else:
        log.warning(f"No tags found matching pattern, {name_pattern}")
        return

    repo.head.reference = selected_tag  # type: ignore
    repo.head.reset(index=True, working_tree=True)


GIT_REF_METHOD: typing.Dict[
    GitRefType, typing.Callable[[str, git.Repo], None]
] = {
    GitRefType.branch: _evaluate_branch,
    GitRefType.tag: _evaluate_tag,
}


async def _fetch_repo(
    configuration: RepoConfiguration, working_dir: pathlib.Path
) -> None:
    log.debug(f"updating repo, {configuration.url}")
    project_name = extract_git_project(configuration.url)
    project_path = working_dir / project_name
    if not project_path.is_dir():
        log.debug(f"project directory does not exist, {project_path}.")
        log.debug(f"cloning the repo from configuration, {configuration.url}")
        this_repo = git.Repo.clone_from(
            url=configuration.url, to_path=project_path
        )
        log.info(
            f"Default active branch from fresh clone is, "
            f"{this_repo.active_branch.name}"
        )
    else:
        log.debug(f"existing project directory found, {project_path}")
        this_repo = git.Repo.init(project_path)

    GIT_REF_METHOD[configuration.pattern_type](configuration.pattern, this_repo)
