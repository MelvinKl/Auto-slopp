"""Logging utility for writing logs to a file.

Provides helpers to set up a rotating file handler for logs at WARNING level
and above, complementing the console/Telegram handlers.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Module-level cache keyed by (log_dir, filename, level)
_file_handler_cache: dict[tuple[Path, str, int], RotatingFileHandler] = {}


def reset_file_handler_cache() -> None:
    """Reset the module-level handler cache (mainly for testing)."""
    global _file_handler_cache
    _file_handler_cache = {}


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
    # Idempotency: return cached handler if same (log_dir, filename, level)
    cache_key = (log_dir, filename, level)
    if cache_key in _file_handler_cache:
        return _file_handler_cache[cache_key]

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
    _file_handler_cache[cache_key] = handler
    return handler


def _find_existing_handler(
    logger: logging.Logger,
    log_dir: Path,
    filename: str,
) -> RotatingFileHandler | None:
    """Check if the logger already has a RotatingFileHandler for the same file.

    This avoids cross-logger contamination and duplicate handler attachment
    without relying on a module-level cache.

    Args:
        logger: Logger to check.
        log_dir: Expected log directory.
        filename: Expected log filename.

    Returns:
        The existing handler if found, otherwise None.
    """
    log_path = log_dir / filename
    for existing in logger.handlers:
        if isinstance(existing, RotatingFileHandler):
            existing_path = Path(existing.baseFilename)
            if existing_path.resolve() == log_path.resolve():
                return existing
    return None


def add_file_handler(
    logger: logging.Logger,
    log_dir: Path,
    filename: str = "auto_slopp.log",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    level: int = logging.WARNING,
) -> RotatingFileHandler:
    """Add a file handler to an existing logger.

    Checks the logger's existing handlers for a RotatingFileHandler pointing
    to the same file before creating a new one, avoiding duplicate attachment
    and cross-logger contamination.

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
    # Check if logger already has a handler for the same file
    existing = _find_existing_handler(logger, log_dir, filename)
    if existing is not None:
        return existing

    handler = setup_file_handler(
        log_dir=log_dir,
        filename=filename,
        max_bytes=max_bytes,
        backup_count=backup_count,
        level=level,
    )
    logger.addHandler(handler)
    return handler
