"""Logging configuration."""

import datetime
import logging
import logging.handlers
import pathlib
import typing

import pydantic

from ._declarations import (
    DEFAULT_FILE_ROTATION_BACKUPS,
    DEFAULT_FILE_ROTATION_ENABLED,
    DEFAULT_FILE_ROTATION_SIZE_MB,
    DEFAULT_LOG_FILE,
)

log = logging.getLogger(__name__)


class LoggingConfiguration(pydantic.BaseModel):
    """Logging configuration data."""

    disable_file_logging: bool
    enable_console_logging: bool
    enable_file_rotation: bool
    file_rotation_size_megabytes: int
    log_file_path: typing.Optional[pathlib.Path]
    log_level: int
    max_rotation_backup_files: int


T = typing.TypeVar("T", bound="Iso8601Time")


class Iso8601Time(logging.Filter):
    """Add custom ISO-8601 date/time record to log data."""

    def filter(self: T, record: typing.Any) -> bool:
        """Implement method to add ISO-8601 record."""
        record.iso8601time = f"{datetime.datetime.utcnow().isoformat()}Z"
        return True


U = typing.TypeVar("U", bound="LoggingState")


class LoggingState:
    """Logging configuration parameters."""

    configuration: LoggingConfiguration
    rotation_handler: typing.Optional[logging.handlers.RotatingFileHandler]

    def __init__(
        self: U,
        disable_file_logging: bool,
        enable_console_logging: bool,
        log_level_text: str,
    ) -> None:
        """
        Construct ``LoggingState`` object.

        Args:
            disable_file_logging: Disable file logging flag.
            enable_console_logging: Enable console logging flag.
        """
        self.configuration = LoggingConfiguration(
            **{
                "disable_file_logging": disable_file_logging,
                "enable_console_logging": enable_console_logging,
                "enable_file_rotation": DEFAULT_FILE_ROTATION_ENABLED,
                "file_rotation_size_megabytes": DEFAULT_FILE_ROTATION_SIZE_MB,
                "log_file_path": (
                    pathlib.Path(DEFAULT_LOG_FILE)
                    if not disable_file_logging
                    else None
                ),
                "log_level": getattr(logging, log_level_text.upper()),
                "max_rotation_backup_files": DEFAULT_FILE_ROTATION_BACKUPS,
            }
        )
        self.filter = Iso8601Time()
        self.formatter = logging.Formatter(
            "%(iso8601time)s::%(name)s::%(levelname)s::%(message)s"
        )
        self.rotation_handler = None

        self.set_logging_state()

    def set_logging_state(self: U) -> None:
        """Apply the logging state from configured parameters."""
        root_logger = logging.getLogger()
        root_logger.addFilter(self.filter)
        self.__set_log_level(root_logger)
        self.__set_file_logging(root_logger)
        self.__set_console_logging(root_logger)

        log.info("Logging state set")
        log.debug(
            "Applied logging configuration, {0}".format(
                self.configuration.dict()
            )
        )

    def __set_file_logging(self: U, root_logger: logging.Logger) -> None:
        """
        Enable or disable file logging.

        Args:
            root_logger: Root logger to modify.
        """
        if not self.configuration.disable_file_logging:
            # No change if a rotation handler already exists.
            if not self.rotation_handler:
                this_handler = logging.handlers.RotatingFileHandler(
                    str(self.configuration.log_file_path),
                    backupCount=self.configuration.max_rotation_backup_files,
                    maxBytes=self.configuration.file_rotation_size_megabytes
                    * (1024**2),
                )
                this_handler.addFilter(self.filter)
                this_handler.setLevel(self.configuration.log_level)
                this_handler.setFormatter(self.formatter)
                self.rotation_handler = this_handler

                root_logger.addHandler(self.rotation_handler)
        elif self.rotation_handler:
            root_logger.removeHandler(self.rotation_handler)
            self.rotation_handler = None
        # else self.rotation_handler is None and self.disable_file_logging
        # so do nothing

    def __set_console_logging(self: U, root_logger: logging.Logger) -> None:
        """
        Enable or disable console logging.

        Args:
            root_logger: Root logger to modify.
        """

        def remove_stream_handlers() -> None:
            for this_handler in root_logger.handlers:
                if type(this_handler) == logging.StreamHandler:
                    root_logger.removeHandler(this_handler)

        remove_stream_handlers()
        if self.configuration.enable_console_logging:
            console_handler = logging.StreamHandler()
            console_handler.addFilter(self.filter)
            console_handler.setFormatter(self.formatter)
            console_handler.setLevel(self.configuration.log_level)

            root_logger.addHandler(console_handler)

    def __set_log_level(self: U, root_logger: logging.Logger) -> None:
        """
        Set log level on any existing handlers.

        Args:
            root_logger: Root logger to modify.
        """
        for this_handler in root_logger.handlers:
            this_handler.setLevel(self.configuration.log_level)
        # Ensure that the logging level propagates to any subsequently created
        # handlers.
        root_logger.setLevel(self.configuration.log_level)
