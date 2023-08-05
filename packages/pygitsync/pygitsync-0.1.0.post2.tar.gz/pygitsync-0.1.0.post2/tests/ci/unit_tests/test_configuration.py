import pathlib
import tempfile

import pytest

from pygitsync._configuration import (
    GitRefType,
    RepoConfiguration,
    _load_configuration,
)


@pytest.fixture()
def generate_config_file():
    def _apply(content: str, file_path: pathlib.Path) -> None:
        with file_path.open(mode="w") as f:
            f.write(content)

    return _apply


class TestLoadConfiguration:
    MOCK_INTERVAL = 4.56

    @pytest.mark.asyncio
    async def test_clean(self, generate_config_file):
        expected = {
            "daemon": True,
            "exception": 6.28,
            "sleep": 3.14,
            "pattern": "master",
            "pattern_type": GitRefType.branch,
            "url": "https://some.where/git/repo.git",
        }
        ingress_content = f"""---
application:
  exception_sleep_seconds: {expected["exception"]}
  is_daemon: {"true" if expected["daemon"] else "false"}
  sleep_interval_seconds: {expected["sleep"]}

repo:
  pattern_type: {expected["pattern_type"].name}
  pattern: {expected["pattern"]}
  url: {expected["url"]}
"""

        with tempfile.TemporaryDirectory() as d:
            working_dir = pathlib.Path(d)
            expected_path = working_dir / "some_config.yaml"

            generate_config_file(ingress_content, expected_path)

            result = await _load_configuration(
                expected_path,
                expected["daemon"],
                None,
            )

            assert (
                result.application.exception_sleep_seconds
                == expected["exception"]
            )
            assert result.application.is_daemon == expected["daemon"]
            assert (
                result.application.sleep_interval_seconds == expected["sleep"]
            )
            assert result.repo.pattern == expected["pattern"]
            assert result.repo.pattern_type == expected["pattern_type"]
            assert result.repo.url == expected["url"]

    @pytest.mark.asyncio
    async def test_sleep_cli(self, generate_config_file):
        """Sleep duration function argument takes precedence over yaml."""
        expected = {
            "daemon": True,
            "exception": 6.28,
            "sleep": 3.14,
            "pattern": "master",
            "pattern_type": GitRefType.branch,
            "url": "https://some.where/git/repo.git",
        }
        ingress_content = f"""---
application:
  exception_sleep_seconds: {expected["exception"]}
  is_daemon: {"true" if expected["daemon"] else "false"}
  sleep_interval_seconds: {self.MOCK_INTERVAL}

repo:
  pattern_type: {expected["pattern_type"].name}
  pattern: {expected["pattern"]}
  url: {expected["url"]}
"""

        with tempfile.TemporaryDirectory() as d:
            working_dir = pathlib.Path(d)
            expected_path = working_dir / "some_config.yaml"

            generate_config_file(ingress_content, expected_path)

            result = await _load_configuration(
                expected_path,
                expected["daemon"],
                expected["sleep"],
            )

            assert (
                result.application.exception_sleep_seconds
                == expected["exception"]
            )
            assert result.application.is_daemon == expected["daemon"]
            assert (
                result.application.sleep_interval_seconds == expected["sleep"]
            )
            assert result.repo.pattern == expected["pattern"]
            assert result.repo.pattern_type == expected["pattern_type"]
            assert result.repo.url == expected["url"]
