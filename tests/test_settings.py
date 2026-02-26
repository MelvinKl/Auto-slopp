"""Tests for Pydantic settings validation."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from settings.main import Settings


def create_settings(**env_overrides):
    """Create Settings instance without loading .env file."""
    import sys

    # Clear existing AUTO_SLOPP_ env vars first
    for key in list(os.environ.keys()):
        if key.startswith("AUTO_SLOPP_"):
            del os.environ[key]

    env_vars = {}
    env_vars.update(env_overrides)

    with patch.dict(os.environ, env_vars, clear=True):
        with patch("dotenv.load_dotenv", return_value=None):
            # Clear settings modules to ensure fresh import
            for mod in list(sys.modules.keys()):
                if mod.startswith("settings"):
                    del sys.modules[mod]

            from settings.main import Settings

            # Remove env_file from model_config to prevent reading from .env file
            Settings.model_config = {k: v for k, v in Settings.model_config.items() if k != "env_file"}

            test_settings = Settings()
    return test_settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings_values(self):
        """Test that default settings values are correctly set when no env vars are set."""
        test_settings = create_settings()

        assert test_settings.base_repo_path == Path.cwd()
        assert test_settings.executor_sleep_interval == 1.0
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

    def test_worker_search_path_default(self):
        """Test that worker search path defaults correctly."""
        test_settings = create_settings()

        expected_path = Path(__file__).resolve().parent.parent / "src"

        assert test_settings.worker_search_path == expected_path

    def test_telegram_api_url_template(self):
        """Test that telegram_api_url contains token placeholder."""
        test_settings = create_settings()

        assert "{token}" in test_settings.telegram_api_url
        assert test_settings.telegram_api_url.startswith("https://api.telegram.org/bot")

    def test_partial_environment_override(self):
        """Test that environment variables override only specific defaults."""
        test_settings = create_settings(
            AUTO_SLOPP_DEBUG="true",
            AUTO_SLOPP_TELEGRAM_ENABLED="true",
            AUTO_SLOPP_BASE_REPO_PATH="~/custom/path",
            AUTO_SLOPP_EXECUTOR_SLEEP_INTERVAL="45.0",
            AUTO_SLOPP_TELEGRAM_BOT_TOKEN="test_token",
            AUTO_SLOPP_TELEGRAM_CHAT_ID="test_chat_id",
        )

        assert test_settings.base_repo_path == Path("~/custom/path").expanduser()
        assert test_settings.executor_sleep_interval == 45.0
        assert test_settings.telegram_bot_token == "test_token"
        assert test_settings.telegram_chat_id == "test_chat_id"

    def test_optional_telegram_fields(self):
        """Test optional telegram fields use configured values."""
        test_settings = create_settings()

        assert test_settings.telegram_enabled is False
        assert test_settings.telegram_bot_token is None
        assert test_settings.telegram_chat_id is None

    def test_env_prefix(self):
        """Test that environment variables use correct prefix."""
        test_settings = create_settings(
            AUTO_SLOPP_DEBUG="true",
            DEBUG="false",
        )

        assert test_settings.debug is True

    def test_settings_validation_error(self):
        """Test that Pydantic validation works correctly."""
        with pytest.raises(ValidationError):
            create_settings(AUTO_SLOPP_EXECUTOR_SLEEP_INTERVAL="invalid")

    def test_path_expansion(self):
        """Test that tilde paths are expanded correctly."""
        test_settings = create_settings(AUTO_SLOPP_BASE_REPO_PATH="~/test-repo")

        expanded_path = Path("~/test-repo").expanduser()
        assert test_settings.base_repo_path == expanded_path

    def test_global_settings_instance(self):
        """Test that global settings instance is available."""
        import sys

        # Reload settings module to get fresh state
        for mod in list(sys.modules.keys()):
            if mod.startswith("settings"):
                del sys.modules[mod]

        from settings.main import Settings, settings

        assert isinstance(settings, Settings)
        assert hasattr(settings, "base_repo_path")

    def test_slopmachine_codex_preset(self):
        """Test codex preset updates cli command and args."""
        test_settings = create_settings(AUTO_SLOPP_SLOPMACHINE="codex")

        assert test_settings.slopmachine == "codex"
        assert test_settings.cli_command == "codex"
        assert test_settings.cli_args == ["--dangerously-bypass-approvals-and-sandbox"]

    def test_slopmachine_preserves_explicit_cli_overrides(self):
        """Test explicit CLI settings are not overwritten by preset."""
        test_settings = create_settings(
            AUTO_SLOPP_SLOPMACHINE="codex",
            AUTO_SLOPP_CLI_COMMAND="custom-cli",
            AUTO_SLOPP_CLI_ARGS='["--flag"]',
        )

        assert test_settings.slopmachine == "codex"
        assert test_settings.cli_command == "custom-cli"
        assert test_settings.cli_args == ["--flag"]
