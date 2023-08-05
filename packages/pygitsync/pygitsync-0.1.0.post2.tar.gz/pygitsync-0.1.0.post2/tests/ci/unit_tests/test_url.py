import pytest

from pygitsync._url import extract_git_project


class TestExtractGitProject:
    def test_http_clean(self):
        result = extract_git_project(
            "http://some.where/this/is/the/http_project"
        )

        assert result == "http_project"

    def test_http_git_suffix_stripped(self):
        result = extract_git_project(
            "http://some.where/this/is/the/http_project.git"
        )

        assert result == "http_project"

    def test_ssh_clean(self):
        result = extract_git_project("git@some.where:this/is/the/ssh_project")

        assert result == "ssh_project"

    def test_ssh_git_suffix_stripped(self):
        result = extract_git_project(
            "git@some.where:this/is/the/ssh_project.git"
        )

        assert result == "ssh_project"

    def test_raw_path_clean(self):
        result = extract_git_project("this/is/the/local_project")

        assert result == "local_project"

    def test_raw_path_suffix_stripped(self):
        result = extract_git_project("this/is/the/local_project.git")

        assert result == "local_project"
