"""
Configuration management for Auto-slopp.

This module handles loading and validating configuration from YAML files,
providing type-safe access to configuration settings throughout the application.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Union

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)


class LoggingConfig(BaseModel):
    """Logging configuration settings."""

    log_directory: str = "~/git/Auto-logs"
    log_max_size_mb: int = 10
    log_max_files: int = 5
    log_retention_days: int = 30
    log_level: str = "INFO"
    timestamp_format: str = "default"
    timestamp_timezone: str = "local"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "SUCCESS"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @field_validator("log_directory")
    @classmethod
    def expand_log_directory(cls, v):
        """Expand ~ to user home directory for log directory."""
        return os.path.expanduser(v)


class SafeRebootConfig(BaseModel):
    """Safe reboot mechanism configuration."""

    max_disk_usage_percent: int = 85
    max_memory_usage_percent: int = 85
    max_system_load_multiplier: float = 2.0
    max_failed_services: int = 5
    max_degraded_critical_services: int = 2
    maintenance_window_start: str = "02:00"
    maintenance_window_end: str = "04:00"
    business_hours_start: str = "09:00"
    business_hours_end: str = "17:00"
    graceful_shutdown_enabled: bool = True
    graceful_shutdown_timeout: int = 30
    stop_non_critical_services: bool = True
    sync_filesystems: bool = True
    create_pre_reboot_backup: bool = True
    enhanced_state_logging: bool = True
    monitor_during_countdown: bool = True
    countdown_check_interval: int = 30


class AutoUpdateRebootConfig(BaseModel):
    """Auto-update-reboot configuration."""

    enabled: bool = False
    reboot_cooldown_minutes: int = 60
    change_detection_interval_minutes: int = 5
    reboot_delay_seconds: int = 30
    max_reboot_attempts_per_day: int = 3
    maintenance_mode: bool = False
    emergency_override: bool = False
    safe_reboot: SafeRebootConfig = SafeRebootConfig()


class TelegramRateLimitingConfig(BaseModel):
    """Telegram rate limiting configuration."""

    messages_per_second: int = 5
    burst_size: int = 20
    rate_limit_window_seconds: int = 60
    backoff_multiplier: float = 2.0
    max_backoff_seconds: int = 30


class TelegramFormattingConfig(BaseModel):
    """Telegram message formatting configuration."""

    parse_mode: str = "HTML"
    max_message_length: int = 4000
    include_timestamp: bool = True
    include_log_level: bool = True
    include_script_name: bool = True
    use_emoji_indicators: bool = True

    @field_validator("parse_mode")
    @classmethod
    def validate_parse_mode(cls, v):
        valid_modes = ["HTML", "Markdown", "plain"]
        if v not in valid_modes:
            raise ValueError(f"Parse mode must be one of: {valid_modes}")
        return v


class TelegramSecurityConfig(BaseModel):
    """Telegram security configuration."""

    validate_bot_token: bool = True
    encrypt_config_storage: bool = True
    audit_token_access: bool = True
    hide_tokens_in_logs: bool = True
    require_https: bool = True


class TelegramConfig(BaseModel):
    """Telegram bot configuration."""

    enabled: bool = True
    bot_token: str = Field(default="")
    default_chat_id: str = "7649674603"
    api_timeout_seconds: int = 10
    connection_retries: int = 3
    rate_limiting: TelegramRateLimitingConfig = Field(
        default_factory=TelegramRateLimitingConfig
    )
    formatting: TelegramFormattingConfig = Field(
        default_factory=TelegramFormattingConfig
    )
    security: TelegramSecurityConfig = Field(default_factory=TelegramSecurityConfig)


class GitConfig(BaseModel):
    """Git operation configuration."""

    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay_seconds: int = 5
    network_timeout_seconds: int = 60


class BranchProtectionConfig(BaseModel):
    """Branch protection configuration."""

    enable_protection: bool = True
    require_confirmation: bool = True
    show_warnings: bool = True
    protected_branches: List[str] = [
        "main",
        "master",
        "develop",
        "staging",
        "production",
    ]
    protect_current_branch: bool = True
    protection_patterns: List[str] = ["keep-*", "protected-*", "temp-*", "backup-*"]
    require_explicit_confirmation_for: List[str] = [
        "main",
        "master",
        "develop",
        "staging",
        "production",
    ]


class BeadsUpdaterConfig(BaseModel):
    """Beads updater configuration."""

    default_sync_mode: str = "auto"
    default_conflict_strategy: str = "newest"
    default_max_retries: int = 3
    backup_retention_days: int = 30
    enable_detailed_reporting: bool = True
    cleanup_temp_files: bool = True
    lock_timeout_minutes: int = 30

    @field_validator("default_sync_mode")
    @classmethod
    def validate_sync_mode(cls, v):
        valid_modes = ["auto", "manual", "safe"]
        if v not in valid_modes:
            raise ValueError(f"Sync mode must be one of: {valid_modes}")
        return v

    @field_validator("default_conflict_strategy")
    @classmethod
    def validate_conflict_strategy(cls, v):
        valid_strategies = ["newest", "manual", "keep_local", "keep_remote"]
        if v not in valid_strategies:
            raise ValueError(f"Conflict strategy must be one of: {valid_strategies}")
        return v


class AutoSloppConfig(BaseModel):
    """Main Auto-slopp configuration model."""

    sleep_duration: int = 100
    managed_repo_path: str = "~/git/managed"
    managed_repo_task_path: str = "~/git/repo_task_path"
    logging: LoggingConfig = LoggingConfig()
    auto_update_reboot: AutoUpdateRebootConfig = AutoUpdateRebootConfig()
    telegram: TelegramConfig = TelegramConfig()
    git: GitConfig = GitConfig()
    branch_protection: BranchProtectionConfig = BranchProtectionConfig()
    beads_updater: BeadsUpdaterConfig = BeadsUpdaterConfig()

    @field_validator("managed_repo_path", "managed_repo_task_path")
    @classmethod
    def expand_user_paths(cls, v):
        """Expand ~ to user home directory."""
        return os.path.expanduser(v)

    @model_validator(mode="before")
    @classmethod
    def validate_config_consistency(cls, values):
        """Validate configuration consistency across sections."""
        # Add cross-section validation logic here
        return values


class ConfigManager:
    """Manages loading and accessing configuration."""

    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """
        Initialize configuration manager.

        Args:
            config_file: Path to configuration YAML file
        """
        self.config_file = (
            Path(config_file) if config_file else self._find_config_file()
        )
        self._config: Optional[AutoSloppConfig] = None
        self._last_modified: Optional[float] = None

    def _find_config_file(self) -> Path:
        """Find configuration file in standard locations."""
        possible_locations = [
            Path.cwd() / "config.yaml",
            Path(__file__).parent.parent / "config.yaml",
            Path.home() / ".auto-slopp" / "config.yaml",
            Path("/etc/auto-slopp/config.yaml"),
        ]

        for location in possible_locations:
            if location.exists():
                logger.debug(f"Found config file at: {location}")
                return location

        # Default to creating config in current directory
        default_location = Path.cwd() / "config.yaml"
        logger.warning(f"No config file found, will create at: {default_location}")
        return default_location

    def load_config(self, force_reload: bool = False) -> AutoSloppConfig:
        """
        Load configuration from file.

        Args:
            force_reload: Force reload even if already loaded

        Returns:
            Loaded configuration object
        """
        if not force_reload and self._config is not None:
            # Check if file has been modified
            try:
                current_modified = self.config_file.stat().st_mtime
                if (
                    self._last_modified is not None
                    and current_modified <= self._last_modified
                ):
                    return self._config
            except OSError:
                pass

        if not self.config_file.exists():
            logger.info(
                f"Config file not found at {self.config_file}, creating default"
            )
            self._create_default_config()

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            if not config_data:
                config_data = {}

            self._config = AutoSloppConfig(**config_data)
            self._last_modified = self.config_file.stat().st_mtime

            logger.info(f"Configuration loaded from: {self.config_file}")
            return self._config

        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML config: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def _create_default_config(self) -> None:
        """Create a default configuration file."""
        default_config = AutoSloppConfig()

        # Ensure parent directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(default_config.dict(), f, default_flow_style=False, indent=2)

            logger.info(f"Created default configuration at: {self.config_file}")

        except Exception as e:
            logger.error(f"Failed to create default config: {e}")
            raise

    def get_config(self) -> AutoSloppConfig:
        """Get current configuration."""
        if self._config is None:
            return self.load_config()
        return self._config

    def save_config(self, config: Optional[AutoSloppConfig] = None) -> None:
        """
        Save configuration to file.

        Args:
            config: Configuration to save, uses current if None
        """
        config_to_save = config or self.get_config()

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(config_to_save.dict(), f, default_flow_style=False, indent=2)

            self._config = config_to_save
            self._last_modified = self.config_file.stat().st_mtime

            logger.info(f"Configuration saved to: {self.config_file}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def reload_if_changed(self) -> bool:
        """
        Reload configuration if file has changed.

        Returns:
            True if configuration was reloaded, False otherwise
        """
        try:
            current_modified = self.config_file.stat().st_mtime
            if self._last_modified is None or current_modified > self._last_modified:
                logger.info("Configuration file changed, reloading...")
                self.load_config(force_reload=True)
                return True
        except OSError:
            pass

        return False


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_file: Optional[Union[str, Path]] = None) -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_file)
    return _config_manager


def get_config() -> AutoSloppConfig:
    """Get the current configuration."""
    return get_config_manager().get_config()


def reload_config() -> AutoSloppConfig:
    """Reload the configuration."""
    return get_config_manager().load_config(force_reload=True)
