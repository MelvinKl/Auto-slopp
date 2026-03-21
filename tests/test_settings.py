"""Tests for Pydantic settings validation."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from settings.main import Settings, settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings_values(self):
        """Test that default settings values are correctly set when no env vars are set."""
        env_vars_to_keep = {k: v for k, v in os.environ.items() if not k.startswith("AUTO_SLOPP_")}
        with patch.dict(os.environ, env_vars_to_keep, clear=True):
            with patch("dotenv.load_dotenv", return_value=None):
                test_settings = Settings()

        assert test_settings.base_repo_path == Path.cwd()
        assert test_settings.executor_sleep_interval == 60.0
        assert test_settings.debug is False
        assert test_settings.telegram_enabled is False
        assert test_settings.telegram_bot_token is None
        assert test_settings.telegram_chat_id is None
        assert test_settings.telegram_api_url == "https://api.telegram.org/bot{token}/sendMessage"
        assert test_settings.telegram_timeout == 30.0
        assert test_settings.telegram_retry_attempts == 3
        assert test_settings.telegram_retry_delay == 1.0
        assert test_settings.telegram_parse_mode == "HTML"
        assert test_settings.telegram_disable_web_page_preview is True
        assert test_settings.telegram_disable_notification is False

    def test_telegram_api_url_template(self):
        """Test that telegram_api_url contains token placeholder."""
        env_vars_to_clear = {k: v for k, v in os.environ.items() if k.startswith("AUTO_SLOPP_")}
        with patch.dict(os.environ, env_vars_to_clear, clear=True):
            with patch("dotenv.load_dotenv", return_value=None):
                test_settings = Settings()

        assert "{token}" in test_settings.telegram_api_url
        assert test_settings.telegram_api_url.startswith("https://api.telegram.org/bot")

    def test_partial_environment_override(self):
        """Test that environment variables override only specific defaults."""
        env_vars = {
            "AUTO_SLOPP_DEBUG": "true",
            "AUTO_SLOPP_TELEGRAM_ENABLED": "true",
            "AUTO_SLOPP_BASE_REPO_PATH": "~/custom/path",
            "AUTO_SLOPP_EXECUTOR_SLEEP_INTERVAL": "45.0",
            "AUTO_SLOPP_TELEGRAM_BOT_TOKEN": "test_token",
            "AUTO_SLOPP_TELEGRAM_CHAT_ID": "test_chat_id",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        assert test_settings.base_repo_path == Path("~/custom/path").expanduser()
        assert test_settings.executor_sleep_interval == 45.0
        assert test_settings.telegram_bot_token == "test_token"
        assert test_settings.telegram_chat_id == "test_chat_id"

    def test_optional_telegram_fields(self):
        """Test optional telegram fields use configured values."""
        env_vars_to_keep = {k: v for k, v in os.environ.items() if not k.startswith("AUTO_SLOPP_")}
        with patch.dict(os.environ, env_vars_to_keep, clear=True):
            with patch("dotenv.load_dotenv", return_value=None):
                test_settings = Settings()

        assert test_settings.telegram_enabled is False
        assert test_settings.telegram_bot_token is None
        assert test_settings.telegram_chat_id is None

    def test_env_prefix(self):
        """Test that environment variables use correct prefix."""
        env_vars = {
            "AUTO_SLOPP_DEBUG": "true",
            "DEBUG": "false",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        assert test_settings.debug is True

    def test_settings_validation_error(self):
        """Test that Pydantic validation works correctly."""
        with patch.dict(os.environ, {"AUTO_SLOPP_EXECUTOR_SLEEP_INTERVAL": "invalid"}):
            with pytest.raises(ValidationError):
                Settings()

    def test_path_expansion(self):
        """Test that tilde paths are expanded correctly."""
        env_vars = {
            "AUTO_SLOPP_BASE_REPO_PATH": "~/test-repo",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        expanded_path = Path("~/test-repo").expanduser()
        assert test_settings.base_repo_path == expanded_path

    def test_global_settings_instance(self):
        """Test that global settings instance is available."""

        assert isinstance(settings, Settings)
        assert hasattr(settings, "base_repo_path")

    def test_workers_disabled_default(self):
        """Test that workers_disabled has correct default value."""
        test_settings = Settings()

        assert test_settings.workers_disabled == []

    def test_workers_disabled_custom(self):
        """Test that workers_disabled can be customized."""
        env_vars = {
            "AUTO_SLOPP_WORKERS_DISABLED": '["GitHubIssueWorker"]',
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        assert test_settings.workers_disabled == ["GitHubIssueWorker"]

    def test_workers_disabled_empty(self):
        """Test that workers_disabled can be set to empty list."""
        env_vars = {
            "AUTO_SLOPP_WORKERS_DISABLED": "[]",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        assert test_settings.workers_disabled == []

    def test_slop_timeout_default(self):
        """Test default slop_timeout value."""
        test_settings = Settings()
        assert test_settings.slop_timeout == 7200

    def test_cli_configurations_default(self):
        """Test default tiered CLI configurations."""
        test_settings = Settings()
        assert len(test_settings.cli_configurations) == 10
        assert test_settings.cli_configurations[0].cli_command == "claude"
        assert test_settings.cli_configurations[1].cli_command == "claude"
        assert test_settings.cli_configurations[2].cli_command == "claude"
        assert test_settings.cli_configurations[3].cli_command == "opencode"
        assert test_settings.cli_configurations[4].cli_command == "opencode"
        assert test_settings.cli_configurations[5].cli_command == "gemini"
        assert test_settings.cli_configurations[6].cli_command == "codex"
        assert test_settings.cli_configurations[7].cli_command == "opencode"
        assert test_settings.cli_configurations[8].cli_command == "opencode"
        assert test_settings.cli_configurations[9].cli_command == "opencode"
        assert "glm-4.7-flash" in str(test_settings.cli_configurations[9].cli_args)

    def test_cli_configurations_env_override(self):
        """Test overriding CLI configurations via environment variable."""
        env_vars = {
            "AUTO_SLOPP_CLI_CONFIGURATIONS": '[{"cli_command": "custom", "cli_args": ["--arg"]}]',
        }
        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        assert len(test_settings.cli_configurations) == 1
        assert test_settings.cli_configurations[0].cli_command == "custom"
        assert test_settings.cli_configurations[0].cli_args == ["--arg"]

    def test_auto_update_reboot_delay_default(self):
        """Test default auto_update_reboot_delay value."""
        test_settings = Settings()
        assert test_settings.auto_update_reboot_delay == 300

    def test_auto_update_reboot_delay_custom(self):
        """Test that auto_update_reboot_delay can be customized."""
        env_vars = {
            "AUTO_SLOPP_AUTO_UPDATE_REBOOT_DELAY": "600",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        assert test_settings.auto_update_reboot_delay == 600

    def test_auto_update_reboot_delay_validation(self):
        """Test that auto_update_reboot_delay must be non-negative."""
        env_vars = {
            "AUTO_SLOPP_AUTO_UPDATE_REBOOT_DELAY": "-1",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError):
                Settings()

    def test_github_issue_step_max_iterations_default(self):
        """Test default github_issue_step_max_iterations value."""
        test_settings = Settings()
        assert test_settings.github_issue_step_max_iterations == 25

    def test_github_issue_step_max_iterations_validation(self):
        """Test github_issue_step_max_iterations must be at least 1."""
        env_vars = {
            "AUTO_SLOPP_GITHUB_ISSUE_STEP_MAX_ITERATIONS": "0",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError):
                Settings()
