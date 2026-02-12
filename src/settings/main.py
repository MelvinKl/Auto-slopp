"""Main settings configuration using Pydantic BaseSettings."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Dictionary containing the configuration values.
    """
    if not config_path.exists():
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if config is None:
        return {}

    if not isinstance(config, dict):
        return {}

    return config


class Settings(BaseSettings):
    """Main application settings.

    Configuration is loaded from environment variables with sensible defaults.
    """

    base_repo_path: Path = Field(
        default_factory=lambda: Path.cwd(),
        description="Base path to the repository directory",
    )

    base_task_path: Path = Field(
        default_factory=lambda: Path.cwd() / "tasks",
        description="Base path to the task directory",
    )

    worker_search_path: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent,
        description="Path to search for worker implementations",
    )

    task_repo_path: Path = Field(
        default_factory=lambda: Path.cwd() / "tasks",
        description="Path to the task repository directory",
    )

    @field_validator(
        "base_repo_path",
        "base_task_path",
        "task_repo_path",
        "worker_search_path",
        "yaml_config_path",
        mode="before",
    )
    @classmethod
    def expand_user_paths(cls, v):
        """Expand user (~) paths in path fields."""
        if isinstance(v, str):
            return Path(v).expanduser()
        elif isinstance(v, Path):
            return v.expanduser()
        return v

    executor_sleep_interval: float = Field(
        default=1.0, description="Sleep interval between executor iterations in seconds"
    )

    debug: bool = Field(default=False, description="Enable debug mode with verbose logging")

    # Telegram logger settings
    telegram_enabled: bool = Field(default=False, description="Enable Telegram logging integration")

    telegram_bot_token: Optional[str] = Field(default=None, description="Telegram bot token for API authentication")

    telegram_chat_id: Optional[str] = Field(default=None, description="Telegram chat ID to send messages to")

    telegram_api_url: str = Field(
        default="https://api.telegram.org/bot{token}/sendMessage",
        description="Telegram API URL for sending messages",
    )

    telegram_timeout: float = Field(default=30.0, description="Timeout for Telegram API requests in seconds")

    telegram_retry_attempts: int = Field(default=3, description="Number of retry attempts for failed Telegram requests")

    telegram_retry_delay: float = Field(default=1.0, description="Delay between retry attempts in seconds")

    telegram_parse_mode: str = Field(
        default="HTML",
        description="Message parse mode for Telegram (HTML, Markdown, or None)",
    )

    telegram_disable_web_page_preview: bool = Field(
        default=True, description="Disable web page preview in Telegram messages"
    )

    telegram_disable_notification: bool = Field(
        default=False, description="Disable notification sound for Telegram messages"
    )

    yaml_config_path: Optional[Path] = Field(default=None, description="Path to YAML configuration file")

    def __init__(self, **data):
        """Initialize settings with optional YAML config file support.

        Args:
            **data: Configuration key-value pairs.
        """
        yaml_config = {}
        yaml_path = data.get("yaml_config_path")

        if yaml_path:
            yaml_path = Path(yaml_path) if isinstance(yaml_path, str) else yaml_path
            if yaml_path and yaml_path.exists():
                yaml_config = load_yaml_config(yaml_path)

        for key, value in yaml_config.items():
            if key not in data:
                data[key] = value

        super().__init__(**data)

    model_config = {
        "env_prefix": "AUTO_SLOPP_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# Load .env file automatically before creating settings instance
load_dotenv()

# Global settings instance
settings = Settings()
