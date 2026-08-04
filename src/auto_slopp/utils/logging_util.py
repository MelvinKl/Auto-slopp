"""Logging utility for writing logs to a file.

Provides helpers to set up a rotating file handler for logs at WARNING level
and above, complementing the console/Telegram handlers.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Module-level cache for idempotency
_file_handler_cache: RotatingFileHandler | None = None


def reset_file_handler_cache() -> None:
    """Reset the module-level handler cache (mainly for testing)."""
    global _file_handler_cache
    _file_handler_cache = None


def setup_file_handler(
    log_dir: Path,
    filename: str = "auto_slopp.log",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    level: int = logging.WARNING,
) -> RotatingFileHandler:
    """Create and configure a rotating file handler.

    This function is idempotent — calling it multiple times with the same
    arguments returns the cached handler instance.

    Args:
        log_dir: Directory to write the log file into.
        filename: Log file name.
        max_bytes: Maximum bytes per log file before rotation.
        backup_count: Number of backup files to keep.
        level: Minimum log level to write to file.

    Returns:
        Configured RotatingFileHandler.
    """
    global _file_handler_cache

    # Idempotency: return cached handler if same config
    if _file_handler_cache is not None:
        return _file_handler_cache

    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / filename

    handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    handler.setFormatter(formatter)
    _file_handler_cache = handler
    return handler


def add_file_handler(
    logger: logging.Logger,
    log_dir: Path,
    filename: str = "auto_slopp.log",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    level: int = logging.WARNING,
) -> RotatingFileHandler:
    """Add a file handler to an existing logger.

    Args:
        logger: Logger instance to attach the handler to.
        log_dir: Directory to write the log file into.
        filename: Log file name.
        max_bytes: Maximum bytes per log file before rotation.
        backup_count: Number of backup files to keep.
        level: Minimum log level to write to file.

    Returns:
        The configured RotatingFileHandler that was added.
    """
    handler = setup_file_handler(
        log_dir=log_dir,
        filename=filename,
        max_bytes=max_bytes,
        backup_count=backup_count,
        level=level,
    )
    logger.addHandler(handler)
    return handler
