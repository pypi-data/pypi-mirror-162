"""Manage configuration parameters."""

import enum
import pathlib
import typing

import aiofiles
import pydantic
import ruamel.yaml

DEFAULT_CONFIGURATION_FILE = pathlib.Path(".pygitsync.yaml")
DEFAULT_SLEEP_INTERVAL_SECONDS = 120.0
EXCEPTION_SLEEP_DURATION_SECONDS = 15.0


class GitRefType(str, enum.Enum):
    """Type of git reference to sync against."""

    branch = "branch"
    tag = "tag"


class ApplicationConfiguration(pydantic.BaseModel):
    """General application configuration."""

    exception_sleep_seconds: float = EXCEPTION_SLEEP_DURATION_SECONDS
    is_daemon: bool = False
    sleep_interval_seconds: float = DEFAULT_SLEEP_INTERVAL_SECONDS


class RepoConfiguration(pydantic.BaseModel):
    """Configuration of git repository for synchronization."""

    pattern_type: GitRefType
    pattern: str
    url: str

    class Config:
        """Pydantic model configuration."""

        use_enum_values = True


class GitSyncConfiguration(pydantic.BaseModel):
    """Collector of all configuration parameters."""

    repo: RepoConfiguration

    application: ApplicationConfiguration = ApplicationConfiguration()


async def _load_configuration(
    configuration_file: pathlib.Path,
    is_daemon: bool,
    sleep_interval_seconds: typing.Optional[float],
) -> GitSyncConfiguration:
    """
    Acquire configuration values from storage.

    Args:
        configuration_file: Path to the expected configuration file.
        sleep_interval_seconds: User defined sleep interval between git sync
        polling.

    Returns:
        Configuration values acquired.
    """
    async with aiofiles.open(configuration_file, mode="r") as f:
        content = await f.read()

    yaml_parser = ruamel.yaml.YAML(typ="safe")
    yaml_data = yaml_parser.load(content)
    value = GitSyncConfiguration.parse_obj(yaml_data)

    value.application.is_daemon = is_daemon
    if sleep_interval_seconds:
        value.application.sleep_interval_seconds = sleep_interval_seconds

    return value
