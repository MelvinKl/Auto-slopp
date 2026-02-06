"""
System logging integration for Auto-slopp.

Provides integration with system logging utilities (syslog, journalctl)
and compatibility with bash logging functions.
"""

import logging
import logging.handlers
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from . import get_logger, LogLevel


class SystemLogger:
    """Integration with system logging utilities."""

    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(f"{__name__}.system")

        # Try to import config
        if config is None:
            try:
                from ..config import get_config

                self.config = get_config()
            except ImportError:
                self.config = None

    def setup_syslog_handler(self, logger_name: str = "auto_slopp") -> logging.Handler:
        """
        Set up syslog handler for system logging.

        Args:
            logger_name: Name to use for syslog entries

        Returns:
            Configured syslog handler
        """
        try:
            # Try to set up syslog handler
            handler = logging.handlers.SysLogHandler(
                address="/dev/log", facility=logging.handlers.SysLogHandler.LOG_LOCAL0
            )

            # Set formatter for syslog
            formatter = logging.Formatter(
                f"{logger_name}: %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)

            self.logger.info("Syslog handler configured successfully")
            return handler

        except Exception as e:
            self.logger.warning(f"Failed to set up syslog handler: {e}")
            return None

    def setup_journalctl_handler(
        self, logger_name: str = "auto_slopp"
    ) -> logging.Handler:
        """
        Set up systemd journal handler.

        Args:
            logger_name: Name to use for journal entries

        Returns:
            Configured journal handler or None if not available
        """
        try:
            # Try to import systemd journal handler
            try:
                from systemd.journal import JournalHandler

                handler = JournalHandler()
                handler.set_name(logger_name)

                self.logger.info("Systemd journal handler configured successfully")
                return handler

            except ImportError:
                self.logger.warning(
                    "systemd-python not available, cannot use journal handler"
                )
                return None

        except Exception as e:
            self.logger.warning(f"Failed to set up journal handler: {e}")
            return None

    def log_to_system(
        self, level: str, message: str, script_name: Optional[str] = None
    ):
        """
        Log message to system logging (syslog/journal).

        Args:
            level: Log level
            message: Log message
            script_name: Name of the script generating the log
        """
        try:
            # Map our log levels to system log levels
            system_level = self._map_to_system_level(level)

            # Format message for system logging
            if script_name:
                formatted_message = f"[{script_name}] {message}"
            else:
                formatted_message = message

            # Try logger first
            system_logger = logging.getLogger("auto_slopp_system")
            system_logger.log(system_level, formatted_message)

        except Exception as e:
            self.logger.error(f"Failed to log to system: {e}")

    def _map_to_system_level(self, level: str) -> int:
        """Map Auto-slopp log levels to system logging levels."""
        level_mapping = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
            LogLevel.SUCCESS: logging.INFO,  # Map SUCCESS to INFO
        }
        return level_mapping.get(level, logging.INFO)

    def get_system_logs(
        self, since: Optional[str] = None, lines: int = 100
    ) -> List[str]:
        """
        Retrieve logs from system logging.

        Args:
            since: Time filter (e.g., "1 hour ago", "2023-01-01")
            lines: Maximum number of lines to retrieve

        Returns:
            List of log entries
        """
        logs = []

        try:
            # Try journalctl first
            if self._is_journalctl_available():
                logs = self._get_journalctl_logs(since, lines)
            else:
                # Fallback to syslog files
                logs = self._get_syslog_logs(since, lines)

        except Exception as e:
            self.logger.error(f"Failed to retrieve system logs: {e}")

        return logs

    def _is_journalctl_available(self) -> bool:
        """Check if journalctl is available."""
        try:
            subprocess.run(
                ["journalctl", "--version"], capture_output=True, check=True, timeout=5
            )
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            return False

    def _get_journalctl_logs(self, since: Optional[str], lines: int) -> List[str]:
        """Get logs from journalctl."""
        cmd = ["journalctl", "--no-pager", "-n", str(lines)]

        if since:
            cmd.extend(["--since", since])

        # Filter for auto-slopp logs
        cmd.extend(["_SYSTEMD_UNIT=auto-slopp.service", "SYSLOG_IDENTIFIER=auto_slopp"])

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=10
            )
            return result.stdout.strip().split("\n") if result.stdout.strip() else []

        except subprocess.CalledProcessError as e:
            self.logger.error(f"journalctl command failed: {e}")
            return []
        except subprocess.TimeoutExpired:
            self.logger.error("journalctl command timed out")
            return []

    def _get_syslog_logs(self, since: Optional[str], lines: int) -> List[str]:
        """Get logs from syslog files."""
        logs = []

        # Common syslog file locations
        syslog_files = ["/var/log/syslog", "/var/log/messages", "/var/log/system.log"]

        for syslog_file in syslog_files:
            if Path(syslog_file).exists():
                try:
                    # Use grep to filter auto-slopp logs
                    cmd = ["grep", "auto_slopp", syslog_file]

                    if since:
                        # Add time filtering (basic implementation)
                        cmd.extend(["tail", f"-{lines}"])
                    else:
                        cmd.extend(["tail", f"-{lines}"])

                    result = subprocess.run(
                        cmd, capture_output=True, text=True, check=True, timeout=5
                    )

                    if result.stdout.strip():
                        logs.extend(result.stdout.strip().split("\n"))

                except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                    self.logger.warning(f"Failed to read {syslog_file}: {e}")

        return logs


class BashLogCompatibility:
    """Provides compatibility with bash logging functions."""

    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(f"{__name__}.bash_compat")
        self.system_logger = SystemLogger(config)

        # Environment variables that control logging
        self.timestamp_format = os.getenv("TIMESTAMP_FORMAT", "default")
        self.timezone = os.getenv("TIMESTAMP_TIMEZONE", "local")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"

        # Log directory
        self.log_directory = os.getenv("LOG_DIRECTORY")
        if self.log_directory and not Path(self.log_directory).is_absolute():
            self.log_directory = Path.home() / self.log_directory.lstrip("~/")

    def log(
        self, level: str, message: str, script_name: Optional[str] = None, **kwargs
    ):
        """
        Compatibility function for bash log() function.

        Args:
            level: Log level (DEBUG, INFO, SUCCESS, WARNING, ERROR)
            message: Log message
            script_name: Name of the script
            **kwargs: Additional arguments (for future compatibility)
        """
        # Check if we should log this level
        if not self._should_log(level):
            return

        # Generate timestamp (bash compatibility)
        timestamp = self._generate_timestamp()

        # Get script name (bash compatibility)
        if not script_name:
            script_name = self._get_script_name()

        # Log to our Python logger
        python_logger = get_logger()
        python_logger.log(level, message, script_name=script_name)

        # Also log to system if configured
        self.system_logger.log_to_system(level, message, script_name)

        # Write to log file if configured (bash compatibility)
        if self.log_directory:
            self._write_to_log_file(level, timestamp, script_name, message)

    def _should_log(self, level: str) -> bool:
        """Check if we should log this level (bash compatibility)."""
        if self.debug_mode:
            return True

        # Define log level hierarchy
        level_hierarchy = {
            "DEBUG": 0,
            "INFO": 1,
            "SUCCESS": 2,
            "WARNING": 3,
            "ERROR": 4,
            "CRITICAL": 5,
        }

        current_level = level_hierarchy.get(self.log_level.upper(), 1)
        message_level = level_hierarchy.get(level.upper(), 1)

        return message_level >= current_level

    def _generate_timestamp(self) -> str:
        """Generate timestamp in bash-compatible format."""

        if self.timezone == "utc":
            now = datetime.utcnow()
        else:
            now = datetime.now()

        # Format based on timestamp_format
        if self.timestamp_format == "iso8601":
            return now.isoformat()
        elif self.timestamp_format == "compact":
            return now.strftime("%Y%m%d_%H%M%S")
        elif self.timestamp_format == "readable":
            return now.strftime("%B %d, %Y at %I:%M:%S %p")
        elif self.timestamp_format == "syslog":
            return now.strftime("%b %d %H:%M:%S")
        else:  # default
            return now.strftime("%Y-%m-%d %H:%M:%S")

    def _get_script_name(self) -> str:
        """Get script name (bash compatibility)."""
        # Try to get from environment first
        script_name = os.getenv("SCRIPT_NAME")
        if script_name:
            return script_name

        # Try to get from sys.argv
        if len(sys.argv) > 0:
            return Path(sys.argv[0]).stem

        return "python"

    def _write_to_log_file(
        self, level: str, timestamp: str, script_name: str, message: str
    ):
        """Write to log file (bash compatibility)."""
        try:
            log_dir = Path(self.log_directory)
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / f"{script_name}.log"

            # Format log entry (bash compatibility)
            log_entry = f"[{level}] {timestamp} {script_name}: {message}\n"

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

        except Exception as e:
            self.logger.error(f"Failed to write to log file: {e}")


# Global instances
_system_logger: Optional[SystemLogger] = None
_bash_compatibility: Optional[BashLogCompatibility] = None


def get_system_logger(config=None) -> SystemLogger:
    """Get the global system logger instance."""
    global _system_logger
    if _system_logger is None:
        _system_logger = SystemLogger(config)
    return _system_logger


def get_bash_log_compatibility(config=None) -> BashLogCompatibility:
    """Get the global bash compatibility instance."""
    global _bash_compatibility
    if _bash_compatibility is None:
        _bash_compatibility = BashLogCompatibility(config)
    return _bash_compatibility


def setup_system_logging(
    config=None, logger_name: str = "auto_slopp"
) -> List[logging.Handler]:
    """
    Set up system logging handlers.

    Args:
        config: Configuration object
        logger_name: Name for system log entries

    Returns:
        List of configured handlers
    """
    handlers = []
    system_logger = get_system_logger(config)

    # Try syslog first
    syslog_handler = system_logger.setup_syslog_handler(logger_name)
    if syslog_handler:
        handlers.append(syslog_handler)

    # Try systemd journal
    journal_handler = system_logger.setup_journalctl_handler(logger_name)
    if journal_handler:
        handlers.append(journal_handler)

    return handlers


# Bash compatibility functions
def bash_log(level: str, message: str, script_name: Optional[str] = None, **kwargs):
    """Bash-compatible log function."""
    compat = get_bash_log_compatibility()
    compat.log(level, message, script_name, **kwargs)


def log_info(message: str, script_name: Optional[str] = None):
    """Bash-compatible info log."""
    bash_log("INFO", message, script_name)


def log_warning(message: str, script_name: Optional[str] = None):
    """Bash-compatible warning log."""
    bash_log("WARNING", message, script_name)


def log_error(message: str, script_name: Optional[str] = None):
    """Bash-compatible error log."""
    bash_log("ERROR", message, script_name)


def log_success(message: str, script_name: Optional[str] = None):
    """Bash-compatible success log."""
    bash_log("SUCCESS", message, script_name)


def log_debug(message: str, script_name: Optional[str] = None):
    """Bash-compatible debug log."""
    bash_log("DEBUG", message, script_name)


def get_system_logs(since: Optional[str] = None, lines: int = 100) -> List[str]:
    """Get logs from system logging."""
    system_logger = get_system_logger()
    return system_logger.get_system_logs(since, lines)
