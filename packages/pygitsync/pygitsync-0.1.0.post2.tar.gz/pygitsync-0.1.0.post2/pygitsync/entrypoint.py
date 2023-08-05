"""Entry to the main execution path."""

import asyncio
import contextlib
import logging
import pathlib
import tempfile
import typing

import click
import daemon  # type: ignore

from ._configuration import DEFAULT_CONFIGURATION_FILE, _load_configuration
from ._declarations import DEFAULT_LOG_LEVEL, VALID_LOG_LEVELS
from ._logging import LoggingState
from ._repo import _fetch_repo

log = logging.getLogger(__name__)


T = typing.TypeVar("T", bound="WhileContext")


class WhileContext:
    """Define exit status of the consuming while loop.

    If ``is_daemon`` is true, then the ``keep_running`` method always returns
    true. If not, then ``keep_running`` return true the first call, and then
    false after that.
    """

    def __init__(self: T, run_once: bool = False) -> None:
        """Construct ``WhileContext`` object.

        Args:
            run_once: Flag if the system is supposed to only execute once.
                      Should only be used for debugging. (default: False)
        """
        self._continue = True
        self.run_once = run_once

    def keep_running(self: T) -> bool:
        """Define the run state of the caller.

        Returns:
            True for the consumer to continue running, False for the consumer
            to stop running.
        """
        if not self.run_once:
            # always keep running
            return True
        if self.run_once and self._continue:
            # let the loop run this time, but subsequent calls indicate exit
            self._continue = False
            return True
        else:
            # stop running
            return False


@contextlib.asynccontextmanager
async def _working_directory(
    user_directory: typing.Optional[pathlib.Path],
) -> typing.AsyncGenerator[pathlib.Path, None]:
    if user_directory:
        user_directory.mkdir(exist_ok=True, parents=True)

        yield user_directory
    else:
        with tempfile.TemporaryDirectory() as d:
            working_directory = pathlib.Path(d)

            yield working_directory


async def main(
    configuration_file: pathlib.Path,
    is_daemon: bool,
    sleep_interval_seconds: typing.Optional[float],
    user_directory: typing.Optional[pathlib.Path],
) -> None:
    """
    Primary execution path of the utility.

    ``is_daemon`` true means the loop will never exit, otherwise the loop only
    runs once and then exits.

    Args:
        configuration_file: Path to ``pygitsync`` configuration file.
        is_daemon: Flag to prevent execution from exiting.
        sleep_interval_seconds: Duration of period between git fetches.
        user_directory: User specified working directory. Created if necessary.
    """
    async with _working_directory(user_directory) as working_directory:
        this_configuration = await _load_configuration(
            configuration_file,
            is_daemon,
            sleep_interval_seconds,
        )

        loop = WhileContext()
        while loop.keep_running():
            try:
                await _fetch_repo(this_configuration.repo, working_directory)

                log.debug(
                    "sleeping for, "
                    f"{this_configuration.application.sleep_interval_seconds} "
                    "seconds"
                )
                await asyncio.sleep(
                    this_configuration.application.sleep_interval_seconds
                )
            except Exception as e:
                log.critical(f"unhandled exception detected, {str(e)}")
                # sleep after logging this exception to avoid consuming CPU
                # if exception occurs very early in the loop (before the loop
                # hits its own sleep delay).
                await asyncio.sleep(
                    this_configuration.application.exception_sleep_seconds
                )


@click.command()
@click.option(
    "--configuration",
    "-c",
    "configuration_file",
    default=DEFAULT_CONFIGURATION_FILE,
    help="Path to pygitsync configuration file.",
    show_default=True,
    type=click.Path(path_type=pathlib.Path),
)
@click.option(
    "--daemon",
    "-d",
    "is_daemon",
    default=False,
    help="Run utility indefinitely in the background. "
    "Default: run utility indefinitely in foreground.",
    is_flag=True,
)
@click.option(
    "--interval",
    "-i",
    "sleep_interval_seconds",
    default=None,
    help="Duration in seconds between git fetches.",
    show_default=True,
    type=float,
)
@click.option(
    "--log-disable-console",
    "disable_console_log",
    default=False,
    help="Disable console logging.",
    is_flag=True,
)
@click.option(
    "--log-enable-file",
    "enable_file_log",
    default=False,
    help="Enable file logging.",
    is_flag=True,
)
@click.option(
    "--log-level",
    "log_level",
    default=DEFAULT_LOG_LEVEL,
    help="Select logging level to apply to all enabled log sinks.",
    type=click.Choice(VALID_LOG_LEVELS, case_sensitive=False),
)
@click.option(
    "--working",
    "-w",
    "working_directory",
    default=None,
    help="Working directory for repo storage. "
    "(default: session based temporary directory)",
    show_default=False,
    type=click.Path(path_type=pathlib.Path),
)
def process_cli_arguments(
    configuration_file: pathlib.Path,
    disable_console_log: bool,
    enable_file_log: bool,
    is_daemon: bool,
    log_level: str,
    sleep_interval_seconds: typing.Optional[float],
    working_directory: typing.Optional[pathlib.Path],
) -> None:
    """Process CLI options."""
    LoggingState((not enable_file_log), (not disable_console_log), log_level)
    if is_daemon:
        with daemon.DaemonContext():
            asyncio.run(
                main(
                    configuration_file,
                    is_daemon,
                    sleep_interval_seconds,
                    working_directory,
                )
            )
    else:
        # run with the daemon context.
        asyncio.run(
            main(
                configuration_file,
                is_daemon,
                sleep_interval_seconds,
                working_directory,
            )
        )


def flit_entry() -> None:
    """Flit script entry point."""
    process_cli_arguments()
