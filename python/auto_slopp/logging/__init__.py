"""
Enhanced logging system for Auto-slopp.

Provides structured logging with multiple handlers including file rotation,
Telegram integration, and console output with rich formatting.
"""

import logging
import logging.handlers
import sys

import glob
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from rich.console import Console
from rich.logging import RichHandler

try:
    from ..config import get_config
except ImportError:
    # Handle circular import during initial setup
    get_config = None


@dataclass
class LogEntry:
    """Structured log entry."""

    timestamp: datetime
    level: str
    message: str
    script_name: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class LogLevel:
    """Standardized log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    CRITICAL = "CRITICAL"


class TelegramFormatter(logging.Formatter):
    """Custom formatter for Telegram messages."""

    EMOJI_MAP = {
        "DEBUG": "🔵",
        "INFO": "ℹ️",
        "WARNING": "⚠️",
        "ERROR": "🔴",
        "SUCCESS": "🟢",
        "CRITICAL": "🚨",
    }

    def __init__(self, config):
        super().__init__()
        self.config = config

    def format(self, record):
        """Format log record for Telegram."""
        # Get emoji for log level
        emoji = self.EMOJI_MAP.get(record.levelname, "📝")

        if not self.config:
            return f"{emoji} {record.levelname}: {record.getMessage()}"

        # Build message
        parts = [f"{emoji} <b>{record.levelname}</b>"]

        if self.config.formatting.include_timestamp:
            timestamp = datetime.fromtimestamp(record.created).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            parts.append(f"<i>{timestamp}</i>")

        if self.config.formatting.include_script_name and hasattr(
            record, "script_name"
        ):
            script_name = getattr(record, "script_name", "unknown")
            parts.append(f"<code>{script_name}</code>")

        # Main message
        message = record.getMessage()
        if self.config and hasattr(self.config, "max_message_length"):
            if len(message) > self.config.max_message_length:
                message = message[: self.config.max_message_length - 3] + "..."

        parts.append(message)

        # Combine parts
        formatted_message = "\n".join(parts) if parts else ""

        # Ensure we don't exceed Telegram's limit
        if self.config and hasattr(self.config, "max_message_length"):
            if len(formatted_message) > self.config.max_message_length:
                formatted_message = (
                    formatted_message[: self.config.max_message_length - 3] + "..."
                )

        return formatted_message


class RotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Enhanced rotating file handler with better naming."""

    def __init__(self, filename: Path, config):
        self.config = config
        self.filename = filename

        # Ensure log directory exists
        filename.parent.mkdir(parents=True, exist_ok=True)

        super().__init__(
            filename=str(filename),
            maxBytes=config.log_max_size_mb * 1024 * 1024,
            backupCount=config.log_max_files,
            encoding="utf-8",
        )

        self.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(script_name)-15s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    def emit(self, record):
        """Emit a record with enhanced error handling."""
        try:
            super().emit(record)
        except Exception:
            # Fallback to stderr if file logging fails
            print(
                f"Failed to write to log file: {record.getMessage()}", file=sys.stderr
            )


class TelegramHandler(logging.Handler):
    """Handler for sending logs to Telegram."""

    def __init__(self, bot, chat_id: str, config):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id
        self.config = config
        self.formatter = TelegramFormatter(config)
        self._rate_limiter = RateLimiter(config)

    def emit(self, record):
        """Emit log record to Telegram."""
        if not self._should_log(record):
            return

        try:
            if self.formatter:
                message = self.formatter.format(record)
            else:
                message = f"{record.levelname}: {record.getMessage()}"

            # Send with rate limiting
            self._rate_limiter.send_with_rate_limit(
                lambda: self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode=self.config.formatting.parse_mode,
                )
            )

        except Exception as e:
            # Don't let Telegram errors crash the application
            print(f"Failed to send to Telegram: {e}", file=sys.stderr)

    def _should_log(self, record) -> bool:
        """Check if this record should be sent to Telegram."""
        # Check log level filters
        if hasattr(self.config, "filters") and self.config.filters.log_levels:
            if record.levelname not in self.config.filters.log_levels:
                return False

        # Check script filters
        if hasattr(self.config, "filters") and self.config.filters.scripts:
            if (
                hasattr(record, "script_name")
                and record.script_name not in self.config.filters.scripts
            ):
                return False

        return True


class RateLimiter:
    """Simple rate limiter for Telegram API calls."""

    def __init__(self, config):
        self.config = config.rate_limiting
        self.messages_sent = []
        self.last_cleanup = datetime.now()

    def send_with_rate_limit(self, send_func):
        """Send message with rate limiting."""
        now = datetime.now()

        # Clean old messages from tracking
        self._cleanup_old_messages(now)

        # Check if we can send
        if self._can_send_message(now):
            send_func()
            self.messages_sent.append(now)
        else:
            # Wait and retry
            import time

            time.sleep(self._get_wait_time(now))
            send_func()
            self.messages_sent.append(now)

    def _cleanup_old_messages(self, now):
        """Clean up old message records."""
        if (now - self.last_cleanup).seconds < self.config.rate_limit_window_seconds:
            return

        cutoff = now.timestamp() - self.config.rate_limit_window_seconds
        self.messages_sent = [
            msg_time for msg_time in self.messages_sent if msg_time.timestamp() > cutoff
        ]
        self.last_cleanup = now

    def _can_send_message(self, now) -> bool:
        """Check if we can send a message now."""
        recent_count = len(self.messages_sent)
        return recent_count < self.config.messages_per_second

    def _get_wait_time(self, now) -> float:
        """Calculate wait time before next message."""
        if not self.messages_sent:
            return 0.0

        oldest_recent = min(self.messages_sent)
        wait_until = oldest_recent.timestamp() + 1.0  # 1 second between messages
        wait_time = wait_until - now.timestamp()
        return max(0.0, wait_time)


class AutoSloppLogger:
    """Main logger class for Auto-slopp."""

    def __init__(self, name: str = "auto_slopp"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._handlers_configured = False
        self._config_version = None

    def setup_logging(self, config=None):
        """Setup logging with configuration."""
        if config is None:
            from ..config import get_config

            config = get_config()

        # Check if config has changed
        config_hash = hash(str(config.logging))
        if self._config_version == config_hash and self._handlers_configured:
            return

        # Clear existing handlers
        self.logger.handlers.clear()

        # Set log level
        level = getattr(logging, config.logging.log_level.upper(), logging.INFO)
        self.logger.setLevel(level)

        # Setup console handler
        self._setup_console_handler(config.logging)

        # Setup file handler
        self._setup_file_handler(config.logging)

        # Setup Telegram handler if enabled
        if config.telegram.enabled and config.telegram.bot_token:
            self._setup_telegram_handler(config.telegram)

        self._handlers_configured = True
        self._config_version = config_hash

    def _setup_console_handler(self, config):
        """Setup console handler with rich formatting."""
        console = Console(stderr=True)
        handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
        )
        self.logger.addHandler(handler)

    def _setup_file_handler(self, config):
        """Setup file handler with rotation."""
        log_file = (
            Path(config.log_directory) / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        )
        handler = RotatingFileHandler(log_file, config)
        self.logger.addHandler(handler)

    def _setup_telegram_handler(self, config):
        """Setup Telegram handler."""
        try:
            # Import telegram module to avoid circular dependency
            # from ..telegram import TelegramBotManager
            # bot_manager = TelegramBotManager(config)
            # handler = TelegramHandler(bot_manager.bot, config.default_chat_id, config)
            # self.logger.addHandler(handler)
            print(
                "Telegram logging setup temporarily disabled during conversion",
                file=sys.stderr,
            )
        except Exception as e:
            print(f"Failed to setup Telegram logging: {e}", file=sys.stderr)

    def log(
        self, level: str, message: str, script_name: Optional[str] = None, **kwargs
    ):
        """Log a message with specified level."""
        if not self._handlers_configured:
            self.setup_logging()

        # Create extra dict for additional context
        extra = {"script_name": script_name or "unknown"}
        extra.update(kwargs)

        # Log the message
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, message, extra=extra)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self.log(LogLevel.ERROR, message, **kwargs)

    def success(self, message: str, **kwargs):
        """Log success message."""
        self.log(LogLevel.SUCCESS, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.log(LogLevel.CRITICAL, message, **kwargs)


# Global logger instance
_logger: Optional[AutoSloppLogger] = None


def get_logger(name: str = "auto_slopp") -> AutoSloppLogger:
    """Get logger instance."""
    global _logger
    if _logger is None:
        _logger = AutoSloppLogger(name)
    return _logger


def setup_logging(config=None):
    """Setup logging globally."""
    logger = get_logger()
    logger.setup_logging(config)


def log(level: str, message: str, script_name: Optional[str] = None, **kwargs):
    """Global logging function."""
    logger = get_logger()
    logger.log(level, message, script_name=script_name, **kwargs)


# Convenience functions matching bash script interface
def log_info(message: str, script_name: Optional[str] = None):
    """Log info message."""
    log(LogLevel.INFO, message, script_name=script_name)


def log_warning(message: str, script_name: Optional[str] = None):
    """Log warning message."""
    log(LogLevel.WARNING, message, script_name=script_name)


def log_error(message: str, script_name: Optional[str] = None):
    """Log error message."""
    log(LogLevel.ERROR, message, script_name=script_name)


def log_success(message: str, script_name: Optional[str] = None):
    """Log success message."""
    log(LogLevel.SUCCESS, message, script_name=script_name)


def log_debug(message: str, script_name: Optional[str] = None):
    """Log debug message."""
    log(LogLevel.DEBUG, message, script_name=script_name)


class LogRotationManager:
    """Manages log rotation and cleanup operations."""

    def __init__(self, config=None):
        self.config = config
        if config is None:
            try:
                from ..config import get_config

                self.config = get_config()
            except ImportError:
                # Use defaults if config not available
                self.config = type(
                    "Config",
                    (),
                    {
                        "logging": type(
                            "Logging",
                            (),
                            {
                                "log_directory": "~/git/Auto-logs",
                                "log_max_size_mb": 10,
                                "log_max_files": 5,
                                "log_retention_days": 30,
                            },
                        )()
                    },
                )()

        self.logger = get_logger(f"{__name__}.rotation")
        self.log_dir = Path(self.config.logging.log_directory).expanduser()

    def setup_log_rotation(self, logger_name: str = "auto_slopp") -> logging.Handler:
        """
        Set up rotating file handler for logger.

        Args:
            logger_name: Name of the logger to set up

        Returns:
            Configured rotating file handler
        """
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create log file path
        log_file = self.log_dir / f"{logger_name}.log"

        # Set up rotating file handler
        max_bytes = self.config.logging.log_max_size_mb * 1024 * 1024
        backup_count = self.config.logging.log_max_files

        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )

        # Set formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        self.logger.info(
            f"Log rotation set up: {log_file} "
            f"(max {max_bytes} bytes, {backup_count} backups)"
        )
        return handler

    def rotate_logs(self, force: bool = False) -> Dict[str, Any]:
        """
        Perform log rotation for all log files.

        Args:
            force: Force rotation even if size threshold not met

        Returns:
            Dictionary with rotation results
        """
        results = {
            "rotated": [],
            "errors": [],
            "total_size_before": 0,
            "total_size_after": 0,
        }

        try:
            # Ensure log directory exists
            self.log_dir.mkdir(parents=True, exist_ok=True)

            # Find all log files
            log_files = list(self.log_dir.glob("*.log*"))

            for log_file in log_files:
                try:
                    # Check file size
                    file_size = log_file.stat().st_size
                    max_size = self.config.logging.log_max_size_mb * 1024 * 1024
                    results["total_size_before"] += file_size

                    if force or file_size > max_size:
                        # Rotate the file
                        self._rotate_single_file(log_file)
                        results["rotated"].append(str(log_file))
                        self.logger.info(f"Rotated log file: {log_file}")

                except Exception as e:
                    error_msg = f"Failed to rotate {log_file}: {e}"
                    results["errors"].append(error_msg)
                    self.logger.error(error_msg)

            # Calculate new total size
            for log_file in log_files:
                if log_file.exists():
                    results["total_size_after"] += log_file.stat().st_size

            self.logger.info(
                f"Log rotation completed: {len(results['rotated'])} files rotated, "
                f"{len(results['errors'])} errors"
            )

        except Exception as e:
            error_msg = f"Log rotation failed: {e}"
            results["errors"].append(error_msg)
            self.logger.error(error_msg)

        return results

    def _rotate_single_file(self, log_file: Path):
        """Rotate a single log file."""
        if not log_file.exists():
            return

        # Create backup name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{log_file.stem}_{timestamp}{log_file.suffix}"
        backup_path = log_file.parent / backup_name

        # Move current log to backup
        shutil.move(str(log_file), str(backup_path))

        # Create new empty log file
        log_file.touch()

    def cleanup_old_logs(self) -> Dict[str, Any]:
        """
        Clean up log files older than retention period.

        Returns:
            Dictionary with cleanup results
        """
        results = {"deleted": [], "errors": [], "space_freed": 0}

        try:
            # Calculate cutoff date
            retention_days = self.config.logging.log_retention_days
            cutoff_date = datetime.now() - timedelta(days=retention_days)

            # Find all log files (including rotated ones)
            log_pattern = str(self.log_dir / "*.log*")
            log_files = glob.glob(log_pattern)

            for log_file_path in log_files:
                log_file = Path(log_file_path)
                try:
                    # Get file modification time
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

                    if mtime < cutoff_date:
                        # Calculate space to be freed
                        file_size = log_file.stat().st_size
                        results["space_freed"] += file_size

                        # Delete the file
                        log_file.unlink()
                        results["deleted"].append(str(log_file))
                        self.logger.info(f"Deleted old log file: {log_file}")

                except Exception as e:
                    error_msg = f"Failed to delete {log_file}: {e}"
                    results["errors"].append(error_msg)
                    self.logger.error(error_msg)

            self.logger.info(
                f"Log cleanup completed: {len(results['deleted'])} files deleted, "
                f"{results['space_freed']} bytes freed"
            )

        except Exception as e:
            error_msg = f"Log cleanup failed: {e}"
            results["errors"].append(error_msg)
            self.logger.error(error_msg)

        return results

    def get_log_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about log files.

        Returns:
            Dictionary with log statistics
        """
        stats = {
            "total_files": 0,
            "total_size": 0,
            "oldest_file": None,
            "newest_file": None,
            "files_by_size": [],
            "directory": str(self.log_dir),
        }

        try:
            if not self.log_dir.exists():
                return stats

            # Find all log files
            log_files = list(self.log_dir.glob("*.log*"))
            stats["total_files"] = len(log_files)

            if not log_files:
                return stats

            # Collect file information
            file_info = []
            oldest_time = None
            newest_time = None

            for log_file in log_files:
                if log_file.exists():
                    file_size = log_file.stat().st_size
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

                    stats["total_size"] += file_size
                    file_info.append(
                        {
                            "file": str(log_file),
                            "size": file_size,
                            "modified": mtime.isoformat(),
                        }
                    )

                    if oldest_time is None or mtime < oldest_time:
                        oldest_time = mtime
                        stats["oldest_file"] = str(log_file)

                    if newest_time is None or mtime > newest_time:
                        newest_time = mtime
                        stats["newest_file"] = str(log_file)

            # Sort files by size (largest first)
            stats["files_by_size"] = sorted(
                file_info, key=lambda x: x["size"], reverse=True
            )

        except Exception as e:
            self.logger.error(f"Failed to get log statistics: {e}")
            stats["error"] = str(e)

        return stats

    def monitor_log_sizes(self) -> List[Dict[str, Any]]:
        """
        Monitor log file sizes and return files needing attention.

        Returns:
            List of files that exceed size threshold
        """
        attention_needed = []
        max_size = self.config.logging.log_max_size_mb * 1024 * 1024

        try:
            log_files = list(self.log_dir.glob("*.log"))

            for log_file in log_files:
                if log_file.exists():
                    file_size = log_file.stat().st_size
                    size_mb = file_size / (1024 * 1024)

                    if file_size > max_size:
                        attention_needed.append(
                            {
                                "file": str(log_file),
                                "size_bytes": file_size,
                                "size_mb": round(size_mb, 2),
                                "threshold_mb": self.config.logging.log_max_size_mb,
                                "percentage": round((file_size / max_size) * 100, 1),
                            }
                        )

        except Exception as e:
            self.logger.error(f"Failed to monitor log sizes: {e}")

        return attention_needed


# Global log rotation manager
_rotation_manager: Optional[LogRotationManager] = None


def get_log_rotation_manager(config=None) -> LogRotationManager:
    """Get the global log rotation manager instance."""
    global _rotation_manager
    if _rotation_manager is None:
        _rotation_manager = LogRotationManager(config)
    return _rotation_manager


def setup_log_rotation(logger_name: str = "auto_slopp", config=None) -> logging.Handler:
    """Set up log rotation for a logger."""
    manager = get_log_rotation_manager(config)
    return manager.setup_log_rotation(logger_name)


def rotate_logs(force: bool = False) -> Dict[str, Any]:
    """Rotate all log files."""
    manager = get_log_rotation_manager()
    return manager.rotate_logs(force)


def cleanup_old_logs() -> Dict[str, Any]:
    """Clean up old log files."""
    manager = get_log_rotation_manager()
    return manager.cleanup_old_logs()


def get_log_statistics() -> Dict[str, Any]:
    """Get log file statistics."""
    manager = get_log_rotation_manager()
    return manager.get_log_statistics()
