"""Main settings configuration using Pydantic BaseSettings."""

from pathlib import Path
from typing import List, Literal, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings

DEFAULT_WORKERS = [
    "GitHubIssueWorker",
    "PRWorker",
    "StaleBranchCleanupWorker",
]


class CLIConfiguration(BaseModel):
    """Single CLI configuration entry for tiered failover."""

    cli_command: str = Field(
        description="CLI command to execute for automation tasks (e.g., opencode, claude, gemini)",
    )
    cli_args: List[str] = Field(
        default_factory=list,
        description="Arguments to pass to the CLI command",
    )


class Settings(BaseSettings):
    """Main application settings.

    Configuration is loaded from environment variables with sensible defaults.
    """

    base_repo_path: Path = Field(
        default_factory=lambda: Path.cwd(),
        description="Base path to the repository directory",
    )

    workers_disabled: List[str] = Field(
        default_factory=list,
        description="List of disabled worker names. Empty list means all workers are enabled.",
    )

    @field_validator(
        "base_repo_path",
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
        default=60.0,
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

    cli_configurations: List[CLIConfiguration] = Field(
        default_factory=lambda: [
            CLIConfiguration(cli_command="gemini", cli_args=["--yolo", "-p"]),
            CLIConfiguration(cli_command="codex", cli_args=["--dangerously-bypass-approvals-and-sandbox", "exec"]),
            CLIConfiguration(
                cli_command="opencode",
                cli_args=["--agent", "openagent", "--model", "zai-coding-plan/glm-4.7", "run"],
            ),
            CLIConfiguration(
                cli_command="opencode",
                cli_args=["--agent", "openagent", "--model", "zai-coding-plan/glm-4.7-flash", "run"],
            ),
        ],
        description=(
            "Tiered CLI configurations ordered by preference. " "Lower index entries are preferred and used first."
        ),
    )

    slop_timeout: int = Field(
        default=7200,
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

    additional_env_file: Optional[Path] = Field(
        default=None,
        description="Path to an additional .env file to be appended to subprocess calls for github_operations",
    )

    model_config = {
        "env_prefix": "AUTO_SLOPP_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# Load .env file automatically before creating settings instance
load_dotenv(override=True)

# Global settings instance
settings = Settings()
