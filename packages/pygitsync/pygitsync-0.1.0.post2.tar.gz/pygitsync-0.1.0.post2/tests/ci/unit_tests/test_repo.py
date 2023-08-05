import logging

import pytest

import pygitsync._repo
from pygitsync._repo import (
    GitRefType,
    InvalidBranchError,
    RepoConfiguration,
    _evaluate_branch,
    _evaluate_tag,
    _fetch_repo,
)

from .repo_support import (
    DefaultBranchHead,
    FreshClone,
    MockRepo,
    NonDefaultBranchHead,
    RepoSupport,
    TaggedRepo,
)


@pytest.fixture()
def mock_configuration(mocker):
    rc = RepoConfiguration(
        pattern_type=GitRefType.branch,
        pattern="some_branch",
        url="user@some.where:this/project",
    )
    return rc


@pytest.fixture()
def mock_get_remote(mocker):
    return mocker.patch(
        "pygitsync._repo._get_remote", return_value=mocker.MagicMock()
    )


@pytest.fixture()
def mock_repo(mocker):
    def _apply(
        repo_url: str, repo_support: RepoSupport, initial_branch: str
    ) -> MockRepo:
        return MockRepo(repo_url, repo_support, initial_branch)

    return _apply


class TestEvaluateBranch:
    def test_default_branch(
        self, mock_configuration, mock_get_remote, mock_repo
    ):
        this_pattern = r"main"
        with mock_repo(
            mock_configuration.url,
            DefaultBranchHead(),
            initial_branch=this_pattern,
        ).instance() as repo_instance:
            this_repo = repo_instance.repo

            _evaluate_branch(this_pattern, this_repo)

            assert this_repo
            assert not this_repo.head.is_detached
            assert this_repo.head.reference == this_repo.heads.main
            # ensure files are checked out in filesystem
            assert (repo_instance.repo_dir / "c2").is_file()

    def test_nondefault_branch(
        self, mock_configuration, mock_get_remote, mock_repo
    ):
        this_pattern = r"feature"
        with mock_repo(
            mock_configuration.url,
            NonDefaultBranchHead(),
            initial_branch="main",
        ).instance() as repo_instance:
            this_repo = repo_instance.repo

            _evaluate_branch(this_pattern, this_repo)

            assert this_repo
            assert not this_repo.head.is_detached
            assert this_repo.head.reference == this_repo.heads.feature
            # ensure files are checked out in filesystem
            assert (repo_instance.repo_dir / "fc1").is_file()

    def test_branch_checkout(
        self, mock_configuration, mock_get_remote, mock_repo
    ):
        """Mismatched branch checks out necessary branch."""
        this_pattern = r"feature"
        with mock_repo(
            mock_configuration.url,
            NonDefaultBranchHead(),
            initial_branch="main",
        ).instance() as repo_instance:
            this_repo = repo_instance.repo
            this_repo.head.reference = this_repo.heads.main
            this_repo.head.reset(index=True, working_tree=True)

            assert (repo_instance.repo_dir / "dc2").is_file()

            _evaluate_branch(this_pattern, this_repo)

            assert this_repo
            assert not this_repo.head.is_detached
            assert this_repo.head.reference == this_repo.heads.feature
            # ensure files are checked out in filesystem
            assert (repo_instance.repo_dir / "fc1").is_file()

    def test_nonexistent_branch_raises(
        self, mock_configuration, mock_get_remote, mock_repo
    ):
        with mock_repo(
            mock_configuration.url,
            NonDefaultBranchHead(),
            initial_branch="master",
        ).instance() as repo_instance:
            with pytest.raises(
                InvalidBranchError, match=r"^Invalid branch name"
            ):
                this_repo = repo_instance.repo

                _evaluate_branch("main", this_repo)


class TestEvaluateTag:
    def test_no_tags_found(
        self, caplog, mock_configuration, mock_get_remote, mock_repo
    ):
        """No tags matching pattern silently exits with a warning."""
        this_pattern = r"^4\.6"
        with caplog.at_level(logging.WARNING):
            with mock_repo(
                mock_configuration.url,
                TaggedRepo(["3.1.4", "v3.2", "v3.1.5"]),
                initial_branch="main",
            ).instance() as repo_instance:
                _evaluate_tag(this_pattern, repo_instance.repo)

            captured_text = caplog.text
            assert "No tags found matching pattern" in captured_text

    def test_no_tags_in_repo(
        self, caplog, mock_configuration, mock_get_remote, mock_repo
    ):
        """No tags in repo silently exits with a warning."""
        this_pattern = r"^(v)?\d+\.\d+\.\d+"
        with caplog.at_level(logging.WARNING):
            with mock_repo(
                mock_configuration.url,
                DefaultBranchHead(),
                initial_branch="main",
            ).instance() as repo_instance:
                _evaluate_tag(this_pattern, repo_instance.repo)

            captured_text = caplog.text
            assert "No tags found matching pattern" in captured_text

    def test_single_tag(self, mock_configuration, mock_get_remote, mock_repo):
        this_pattern = r"^(v)?\d+\.\d+\.\d+"
        with mock_repo(
            mock_configuration.url, TaggedRepo(["3.1.4"]), initial_branch="main"
        ).instance() as repo_instance:
            this_repo = repo_instance.repo

            _evaluate_tag(this_pattern, this_repo)

            assert this_repo
            assert not this_repo.head.is_detached
            assert this_repo.head.reference == this_repo.tags[0]
            assert this_repo.tags[0].name == "3.1.4"
            # check for the file in the commit that the tag is on
            assert (repo_instance.repo_dir / "c0").is_file()

    def test_tags_release_order(
        self, mock_configuration, mock_get_remote, mock_repo
    ):
        """Semantic release reasoning defines the "latest" tag found, not tag date."""
        this_pattern = r"^(v)?\d+(\.\d+)*"
        with mock_repo(
            mock_configuration.url,
            TaggedRepo(["3.1.4", "v3.2", "v3.1.5"]),
            initial_branch="main",
        ).instance() as repo_instance:
            this_repo = repo_instance.repo

            _evaluate_tag(this_pattern, this_repo)

            assert this_repo
            assert not this_repo.head.is_detached
            assert this_repo.head.commit == this_repo.commit("v3.2")
            assert this_repo.head.reference.name == "v3.2"
            # check for the file in the commit that the tag is on
            assert (repo_instance.repo_dir / "c1").is_file()


class TestFetchRepo:
    @pytest.mark.asyncio
    async def test_new_repo_created(
        self, caplog, mock_configuration, mock_get_remote, mock_repo, mocker
    ):
        """A repo that has not been cloned before is cloned/created."""
        mock_configuration.pattern = r"main"
        mock_configuration.pattern_type = GitRefType.branch
        with mock_repo(
            mock_configuration.url, DefaultBranchHead(), initial_branch="main"
        ).instance() as remote_instance:
            with mock_repo(
                str(remote_instance.repo_dir),
                FreshClone(mocker, remote_instance),
                initial_branch="main",
            ).instance() as repo_instance:
                assert not repo_instance.repo_dir.exists()

                await _fetch_repo(mock_configuration, repo_instance.working_dir)

                assert repo_instance.repo_dir.is_dir()

    @pytest.mark.asyncio
    async def test_branch_head_rule(
        self, caplog, mock_configuration, mock_get_remote, mock_repo, mocker
    ):
        b = mocker.MagicMock()
        t = mocker.MagicMock()
        pygitsync._repo.GIT_REF_METHOD = {
            GitRefType.branch: b,
            GitRefType.tag: t,
        }
        mock_configuration.pattern = "main"
        mock_configuration.pattern_type = GitRefType.branch
        with mock_repo(
            mock_configuration.url, DefaultBranchHead(), initial_branch="main"
        ).instance() as repo_instance:
            await _fetch_repo(mock_configuration, repo_instance.working_dir)

        t.assert_not_called()
        b.assert_called_once_with(mock_configuration.pattern, mocker.ANY)

    @pytest.mark.asyncio
    async def test_tag_pattern_rule(
        self, caplog, mock_configuration, mock_get_remote, mock_repo, mocker
    ):
        b = mocker.MagicMock()
        t = mocker.MagicMock()
        pygitsync._repo.GIT_REF_METHOD = {
            GitRefType.branch: b,
            GitRefType.tag: t,
        }
        mock_configuration.pattern = r"^(v|V)?\d+\.\d+\.\d+"
        mock_configuration.pattern_type = GitRefType.tag
        with mock_repo(
            mock_configuration.url,
            TaggedRepo(["3.1.2", "v3.4"]),
            initial_branch="main",
        ).instance() as repo_instance:
            await _fetch_repo(mock_configuration, repo_instance.working_dir)

        b.assert_not_called()
        t.assert_called_once_with(mock_configuration.pattern, mocker.ANY)
