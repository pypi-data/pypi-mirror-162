import abc
import contextlib
import pathlib
import tempfile
import typing

import git

import pygitsync._repo
from pygitsync._url import extract_git_project


class RepoSupport(metaclass=abc.ABCMeta):
    repo: typing.Optional[git.Repo]

    def __init__(self):
        self.repo = None

    def _commit_file(self, file_path: pathlib.Path) -> None:
        assert self.repo

        filename = str(file_path)
        open(filename, "wb").close()
        self.repo.index.add([filename])
        self.repo.index.commit(filename)

    def _initialize_repo(
        self, repo_dir: pathlib.Path, initial_branch: str
    ) -> None:
        repo_dir.parent.mkdir(exist_ok=True, parents=True)
        self.repo = git.Repo.init(initial_branch=initial_branch, path=repo_dir)

    @abc.abstractmethod
    def __call__(self, repo_dir: pathlib.Path, initial_branch: str) -> None:
        return


class FreshClone(RepoSupport):
    def __init__(self, this_mocker, repo_instance) -> None:
        super().__init__()

        self.mocker = this_mocker
        self.repo_instance = repo_instance

        self._to_path = None
        self._git_clone = None

    def _file_clone(self, *args, **kwargs) -> git.Repo:
        return self._git_clone(
            f"file://{self.repo_instance.repo_dir.resolve()}", self._to_path
        )

    def __call__(self, repo_dir: pathlib.Path, initial_branch: str) -> None:
        # DO NOT initialise a git repo
        assert not self.repo
        assert not repo_dir.exists()

        self._to_path = repo_dir
        # preserve the original clone function so it can be used later
        self._git_clone = git.Repo.clone_from
        self.mocker.patch.object(
            pygitsync._repo.git.Repo, "clone_from", self._file_clone
        )


class DefaultBranchHead(RepoSupport):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, repo_dir: pathlib.Path, initial_branch: str) -> None:
        super()._initialize_repo(repo_dir, initial_branch)

        wtd = pathlib.Path(self.repo.working_tree_dir)
        self._commit_file(wtd / "c1")
        self._commit_file(wtd / "c2")


class TaggedRepo(RepoSupport):
    def __init__(self, tag_sequence: typing.List[str]) -> None:
        super().__init__()

        self.tag_sequence = tag_sequence

    def __call__(self, repo_dir: pathlib.Path, initial_branch: str) -> None:
        super()._initialize_repo(repo_dir, initial_branch)

        for x in range(len(self.tag_sequence)):
            self._commit_file(
                pathlib.Path(self.repo.working_tree_dir) / f"c{x}"
            )
            self.repo.create_tag(
                self.tag_sequence[x], message="tag at tag sequence {x}"
            )


class NonDefaultBranchHead(RepoSupport):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, repo_dir: pathlib.Path, initial_branch: str) -> None:
        super()._initialize_repo(repo_dir, initial_branch)

        wtd = pathlib.Path(self.repo.working_tree_dir)
        self._commit_file(wtd / "dc1")
        self._commit_file(wtd / "dc2")

        nb = self.repo.create_head("feature")
        self.repo.head.reference = nb
        self.repo.head.reset(index=True, working_tree=True)

        assert self.repo.active_branch.name == "feature"

        self._commit_file(wtd / "fc1")


T = typing.TypeVar("T", bound="MockRepo")


class MockRepo:
    """Manage test context of mock repo."""

    def __init__(
        self, repo_url: str, repo_support: RepoSupport, initial_branch: str
    ) -> None:
        self.initial_branch = initial_branch
        self.repo_url = repo_url
        self.repo_support = repo_support

        self.repo_dir = None
        self.working_dir = None

    @property
    def repo(self) -> typing.Optional[git.Repo]:
        return self.repo_support.repo

    @contextlib.contextmanager
    def instance(self) -> typing.Generator[T, None, None]:
        with tempfile.TemporaryDirectory() as d:
            self.working_dir = pathlib.Path(d)
            self.repo_dir = self.working_dir / extract_git_project(
                self.repo_url
            )

            # call the support for repo initialization
            self.repo_support(self.repo_dir, self.initial_branch)

            yield self
