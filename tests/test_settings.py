"""Tests for Pydantic settings validation."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from settings.main import Settings, settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings_values(self):
        """Test that default settings values are correctly set."""
        # Arrange - Clear all environment variables that start with AUTO_SLOPP_
        # and also temporarily disable .env file loading
        env_vars_to_clear = {k: v for k, v in os.environ.items() if k.startswith("AUTO_SLOPP_")}

        with patch.dict(os.environ, env_vars_to_clear, clear=True):
            with patch("dotenv.load_dotenv", return_value=None):
                test_settings = Settings()

        # Act & Assert - Check default values
        assert test_settings.base_repo_path == Path.cwd()
        assert test_settings.base_task_path == Path.cwd() / "tasks"
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
        """Test that worker_search_path defaults to correct location."""
        env_vars_to_clear = {k: v for k, v in os.environ.items() if k.startswith("AUTO_SLOPP_")}
        with patch.dict(os.environ, env_vars_to_clear, clear=True):
            with patch("dotenv.load_dotenv", return_value=None):
                test_settings = Settings()

        # The settings file is in src/settings/main.py, so parent.parent is src/
        expected_path = Path(__file__).parent.parent / "src"
        assert test_settings.worker_search_path == expected_path

    def test_telegram_api_url_template(self):
        """Test that telegram_api_url contains token placeholder."""
        env_vars_to_clear = {k: v for k, v in os.environ.items() if k.startswith("AUTO_SLOPP_")}
        with patch.dict(os.environ, env_vars_to_clear, clear=True):
            with patch("dotenv.load_dotenv", return_value=None):
                test_settings = Settings()

        # Act & Assert - Check URL template
        assert "{token}" in test_settings.telegram_api_url
        assert test_settings.telegram_api_url.startswith("https://api.telegram.org/bot")

    def test_partial_environment_override(self):
        """Test that environment variables override only specific defaults."""
        # Arrange - Set only some environment variables
        env_vars = {
            "AUTO_SLOPP_DEBUG": "true",
            "AUTO_SLOPP_TELEGRAM_ENABLED": "true",
        }
        env_vars_to_clear = {k: v for k, v in os.environ.items() if k.startswith("AUTO_SLOPP_") and k not in env_vars}

        with patch.dict(os.environ, env_vars, clear=True):
            with patch("dotenv.load_dotenv", return_value=None):
                test_settings = Settings()

        # Act & Assert - Check that specified values are overridden, others use defaults
        assert test_settings.debug is True  # Overridden
        assert test_settings.telegram_enabled is True  # Overridden
        assert test_settings.base_repo_path == Path.cwd()  # Default
        assert test_settings.executor_sleep_interval == 1.0  # Default
        assert test_settings.telegram_bot_token is None  # Default

    def test_optional_telegram_fields(self):
        """Test that optional Telegram fields can be None."""
        # Arrange - Enable Telegram but don't set optional fields
        env_vars = {
            "AUTO_SLOPP_TELEGRAM_ENABLED": "true",
        }
        env_vars_to_clear = {k: v for k, v in os.environ.items() if k.startswith("AUTO_SLOPP_") and k not in env_vars}

        with patch.dict(os.environ, env_vars, clear=True):
            with patch("dotenv.load_dotenv", return_value=None):
                test_settings = Settings()

        # Act & Assert - Optional fields should be None when not set
        assert test_settings.telegram_enabled is True
        assert test_settings.telegram_bot_token is None
        assert test_settings.telegram_chat_id is None

    def test_env_prefix(self):
        """Test that environment variables use correct prefix."""
        # Arrange - Create settings with prefixed env vars
        env_vars = {
            "AUTO_SLOPP_DEBUG": "true",
            "DEBUG": "false",  # Without prefix - should be ignored
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        # Act & Assert - Only prefixed variable should be used
        assert test_settings.debug is True

    def test_settings_validation_error(self):
        """Test that Pydantic validation works correctly."""
        # Arrange - Create invalid settings
        with patch.dict(os.environ, {"AUTO_SLOPP_EXECUTOR_SLEEP_INTERVAL": "invalid"}):
            with pytest.raises(ValidationError):
                Settings()  # Should raise ValidationError for invalid float

    def test_path_expansion(self):
        """Test that tilde paths are expanded correctly."""
        # Arrange - Set path with ~
        env_vars = {
            "AUTO_SLOPP_BASE_REPO_PATH": "~/test-repo",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        # Act & Assert - Path should be expanded
        expanded_path = Path("~/test-repo").expanduser()
        assert test_settings.base_repo_path == expanded_path

    def test_global_settings_instance(self):
        """Test that global settings instance is available."""
        # Act & Assert - Check that global settings instance exists
        from settings.main import settings

        assert isinstance(settings, Settings)
        assert hasattr(settings, "base_repo_path")
