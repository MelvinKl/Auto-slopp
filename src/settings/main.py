"""Main settings configuration using Pydantic BaseSettings."""

from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from dotenv import load_dotenv
from pydantic import AliasChoices, BaseModel, Field, field_validator
from pydantic_settings import BaseSettings


class TaskRating(BaseModel):
    """Rating configuration for a task type."""

    min_rating: int = Field(default=0, ge=0, le=10, description="Minimum capability required")
    max_rating: int = Field(default=10, ge=0, le=10, description="Maximum capability to use")
    recommended_rating: int = Field(default=5, ge=0, le=10, description="Preferred capability level")


class CLIConfiguration(BaseModel):
    """Single CLI configuration entry for tiered failover."""

    cli_command: str = Field(
        description="CLI command to execute for automation tasks (e.g., opencode, claude, gemini)",
    )
    cli_args: List[str] = Field(
        default_factory=list,
        description="Arguments to pass to the CLI command",
    )
    capability: int = Field(
        default=5,
        ge=0,
        le=10,
        description="Capability rating of this CLI tool (0-10)",
    )
    cooldown_seconds: int = Field(
        default=60,
        description="Cooldown time in seconds if the tool encounters errors",
    )
    name: str = Field(
        default="",
        description="Human-readable name for this CLI configuration",
    )
    blacklist_tasks: List[str] = Field(
        default_factory=list,
        description="Task names for which this CLI configuration should not be used",
    )


class Settings(BaseSettings):
    """Main application settings.

    Configuration is loaded from environment variables with sensible defaults.
    """

    base_repo_path: Path = Field(
        default_factory=lambda: Path.cwd(),
        description="Base path to the repository directory",
    )

    log_file_dir: Optional[Path] = Field(
        default=None,
        description="Directory for log files (WARNING+ severity). Set to None to disable file logging.",
    )

    workers_disabled: List[str] = Field(
        default_factory=list,
        description="List of disabled worker names. Empty list means all workers are enabled.",
    )

    @field_validator(
        "base_repo_path",
        "additional_env_file",
        "config_file_path",
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
        default=600.0,
        description="Sleep interval between executor iterations in seconds",
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

    config_file_path: Union[str, Path] = Field(
        default="config/default.yaml",
        description="Path to the configuration file for complex settings like cli_configurations",
        validation_alias=AliasChoices("AUTO_SLOPP_CONFIG_FILE_PATH", "AUTO_SLOPP_CONFIG_FILE"),
    )

    cli_configurations: List[CLIConfiguration] = Field(
        default_factory=list,  # Will be populated in _load_cli_configurations_from_file
        description=(
            "Tiered CLI configurations ordered by preference. " "Lower index entries are preferred and used first."
        ),
    )

    slop_timeout: int = Field(
        default=10000,
        description="Timeout for slopmachine execution in seconds (default: 2 hours)",
    )

    github_issue_worker_required_label: str = Field(
        default="ai",
        description="Required label for GitHubIssueWorker to process an issue",
    )

    github_issue_worker_allowed_creator: str = Field(
        default="MelvinKl",
        description="Allowed GitHub username for GitHubIssueWorker to process issues",
    )

    pr_review_worker_required_label: str = Field(
        default="AI",
        description="Required label for PrReviewWorker to process a PR",
    )
    pr_review_worker_min_comments: int = Field(
        default=0,
        ge=0,
        le=20,
        description="Minimum number of review comments per PR",
    )
    pr_review_worker_max_comments: int = Field(
        default=9,
        ge=1,
        le=20,
        description="Maximum number of review comments per PR",
    )

    additional_env_file: Optional[Path] = Field(
        default=None,
        description="Path to an additional .env file to be appended to subprocess calls for github_operations",
    )

    task_difficulties: Dict[str, TaskRating] = Field(
        default={
            "task_planning": TaskRating(min_rating=0, max_rating=10, recommended_rating=10),
            "implementation": TaskRating(min_rating=5, max_rating=10, recommended_rating=10),
            "task_implementation_validation": TaskRating(min_rating=0, max_rating=10, recommended_rating=6),
            "remaining_steps_update": TaskRating(min_rating=0, max_rating=10, recommended_rating=4),
            "pr_description": TaskRating(min_rating=0, max_rating=10, recommended_rating=1),
            "pr_review": TaskRating(min_rating=0, max_rating=10, recommended_rating=4),
            "git_checkout": TaskRating(min_rating=0, max_rating=10, recommended_rating=2),
            "default": TaskRating(min_rating=0, max_rating=10, recommended_rating=5),
        },
        description="Difficulty ratings for various task phases (0-10)",
    )

    ralph_max_loops: int = Field(
        default=500,
        ge=1,
        description="Maximum number of loops for Ralph step execution (default: 20)",
    )

    github_issue_step_max_iterations: int = Field(
        default=50,
        ge=1,
        description="Maximum step-iteration attempts for GitHub issue Ralph execution (default: 50)",
    )

    ralph_enabled: bool = Field(
        default=True,
        description="Enable Ralph loop-based step execution for GitHub issues",
    )

    stale_branch_days_threshold: int = Field(
        default=1,
        ge=0,
        description="Days after which a local branch without remote is considered stale and deleted (default: 1)",
    )

    auto_update_reboot_delay: int = Field(
        default=300,
        ge=0,
        description="Delay in seconds before reboot after auto-update (default: 5 minutes)",
    )

    model_config = {
        "env_prefix": "AUTO_SLOPP_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    def model_post_init(self, __context) -> None:
        """Load CLI configurations from file after model initialization."""
        # Only load from file if cli_configurations is empty (not set via env vars)
        if not self.cli_configurations:
            self._load_cli_configurations_from_file()

    def _load_cli_configurations_from_file(self) -> None:
        """Load CLI configurations from the specified file."""
        try:
            config_path = Path(self.config_file_path)
            # Handle relative paths by making them relative to the project root
            if not config_path.is_absolute():
                config_path = Path.cwd() / config_path

            if config_path.exists():
                with open(config_path, "r") as f:
                    config_data = yaml.safe_load(f)

                if config_data and "cli_configurations" in config_data:
                    configs = []
                    for config_dict in config_data["cli_configurations"]:
                        configs.append(CLIConfiguration(**config_dict))
                    self.cli_configurations = configs
            # If file doesn't exist, cli_configurations remains empty list
            # This allows env vars to override with an empty list if needed
        except Exception as e:
            # Log error but don't fail - allow empty configurations
            # In a real application, we might want to use proper logging
            pass
            # Keep cli_configurations as empty list


# Load .env file automatically before creating settings instance
load_dotenv(override=True)

# Global settings instance
settings = Settings()
