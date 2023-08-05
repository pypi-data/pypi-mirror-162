"""Common constants for command definitions."""

DEFAULT_FILE_ROTATION_BACKUPS = 10
DEFAULT_FILE_ROTATION_ENABLED = False
DEFAULT_FILE_ROTATION_SIZE_MB = 1
DEFAULT_LOG_FILE = "pygitsync.log"

DEFAULT_LOG_LEVEL = "warning"
VALID_LOG_LEVELS = [
    "fatal",
    "critical",
    "error",
    "warning",
    "info",
    "debug",
    "notset",
]
