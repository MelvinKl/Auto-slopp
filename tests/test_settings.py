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
        # Arrange - Create settings instance without environment variables
        with patch.dict(os.environ, {}, clear=True):
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

    def test_settings_from_environment_variables(self):
        """Test loading settings from environment variables."""
        # Arrange - Set environment variables
        env_vars = {
            "AUTO_SLOPP_BASE_REPO_PATH": "/custom/repo",
            "AUTO_SLOPP_BASE_TASK_PATH": "/custom/tasks",
            "AUTO_SLOPP_EXECUTOR_SLEEP_INTERVAL": "2.5",
            "AUTO_SLOPP_DEBUG": "true",
            "AUTO_SLOPP_TELEGRAM_ENABLED": "true",
            "AUTO_SLOPP_TELEGRAM_BOT_TOKEN": "test_bot_token",
            "AUTO_SLOPP_TELEGRAM_CHAT_ID": "test_chat_id",
            "AUTO_SLOPP_TELEGRAM_TIMEOUT": "60.0",
            "AUTO_SLOPP_TELEGRAM_RETRY_ATTEMPTS": "5",
            "AUTO_SLOPP_TELEGRAM_RETRY_DELAY": "2.0",
            "AUTO_SLOPP_TELEGRAM_PARSE_MODE": "Markdown",
            "AUTO_SLOPP_TELEGRAM_DISABLE_WEB_PAGE_PREVIEW": "false",
            "AUTO_SLOPP_TELEGRAM_DISABLE_NOTIFICATION": "true",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        # Act & Assert - Check that environment variables are loaded
        assert test_settings.base_repo_path == Path("/custom/repo")
        assert test_settings.base_task_path == Path("/custom/tasks")
        assert test_settings.executor_sleep_interval == 2.5
        assert test_settings.debug is True
        assert test_settings.telegram_enabled is True
        assert test_settings.telegram_bot_token == "test_bot_token"
        assert test_settings.telegram_chat_id == "test_chat_id"
        assert test_settings.telegram_timeout == 60.0
        assert test_settings.telegram_retry_attempts == 5
        assert test_settings.telegram_retry_delay == 2.0
        assert test_settings.telegram_parse_mode == "Markdown"
        assert test_settings.telegram_disable_web_page_preview is False
        assert test_settings.telegram_disable_notification is True

    def test_settings_from_env_file(self):
        """Test loading settings from .env file."""
        # Arrange - Create temporary .env file
        env_content = """
AUTO_SLOPP_DEBUG=true
AUTO_SLOPP_TELEGRAM_ENABLED=true
AUTO_SLOPP_TELEGRAM_BOT_TOKEN=env_file_token
AUTO_SLOPP_TELEGRAM_CHAT_ID=env_file_chat
AUTO_SLOPP_EXECUTOR_SLEEP_INTERVAL=0.5
"""

        with tempfile.TemporaryDirectory() as tmp_dir:
            env_file = Path(tmp_dir) / ".env"
            env_file.write_text(env_content)

            # Change to temp directory and create settings
            original_cwd = Path.cwd()
            try:
                os.chdir(tmp_dir)
                with patch.dict(os.environ, {}, clear=True):
                    test_settings = Settings()
            finally:
                os.chdir(original_cwd)

            # Act & Assert - Check values from .env file
            assert test_settings.debug is True
            assert test_settings.telegram_enabled is True
            assert test_settings.telegram_bot_token == "env_file_token"
            assert test_settings.telegram_chat_id == "env_file_chat"
            assert test_settings.executor_sleep_interval == 0.5

    def test_path_conversion(self):
        """Test that string paths are correctly converted to Path objects."""
        # Arrange
        env_vars = {
            "AUTO_SLOPP_BASE_REPO_PATH": "/test/repo",
            "AUTO_SLOPP_BASE_TASK_PATH": "/test/tasks",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        # Act & Assert - Check that paths are Path objects
        assert isinstance(test_settings.base_repo_path, Path)
        assert isinstance(test_settings.base_task_path, Path)
        assert test_settings.base_repo_path == Path("/test/repo")
        assert test_settings.base_task_path == Path("/test/tasks")

    def test_type_validation(self):
        """Test type validation for settings fields."""
        # Arrange - Test invalid types for various fields
        invalid_cases = [
            {"AUTO_SLOPP_EXECUTOR_SLEEP_INTERVAL": "not_a_number"},  # Should be float
            {"AUTO_SLOPP_DEBUG": "not_a_boolean"},  # Should be bool
            {"AUTO_SLOPP_TELEGRAM_TIMEOUT": "not_a_number"},  # Should be float
            {"AUTO_SLOPP_TELEGRAM_RETRY_ATTEMPTS": "not_an_integer"},  # Should be int
            {"AUTO_SLOPP_TELEGRAM_RETRY_DELAY": "not_a_number"},  # Should be float
        ]

        # Act & Assert - Each invalid case should raise ValidationError
        for env_vars in invalid_cases:
            with patch.dict(os.environ, env_vars, clear=True):
                with pytest.raises(ValidationError):
                    Settings()

    def test_field_validation_constraints(self):
        """Test field validation constraints."""
        # Arrange - Test boundary and constraint validation
        constraint_cases = [
            # Negative values that should be allowed (no constraints specified)
            {"AUTO_SLOPP_EXECUTOR_SLEEP_INTERVAL": "-1.0"},
            {"AUTO_SLOPP_TELEGRAM_TIMEOUT": "-10.0"},
            {"AUTO_SLOPP_TELEGRAM_RETRY_ATTEMPTS": "-1"},
            {"AUTO_SLOPP_TELEGRAM_RETRY_DELAY": "-0.5"},
        ]

        # Act & Assert - These should be valid since no constraints are specified
        for env_vars in constraint_cases:
            with patch.dict(os.environ, env_vars, clear=True):
                test_settings = Settings()
                # Just verify it doesn't raise ValidationError
                assert test_settings is not None

    def test_worker_search_path_default(self):
        """Test that worker_search_path defaults to correct location."""
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()

        # The settings file is in src/settings/main.py, so parent.parent is src/
        expected_path = Path(__file__).parent.parent / "src"
        assert test_settings.worker_search_path == expected_path

    def test_telegram_api_url_template(self):
        """Test that telegram_api_url contains token placeholder."""
        with patch.dict(os.environ, {}, clear=True):
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

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        # Act & Assert - Check that specified values are overridden, others use defaults
        assert test_settings.debug is True  # Overridden
        assert test_settings.telegram_enabled is True  # Overridden
        assert test_settings.base_repo_path == Path.cwd()  # Default
        assert test_settings.executor_sleep_interval == 1.0  # Default
        assert test_settings.telegram_bot_token is None  # Default

    def test_global_settings_instance(self):
        """Test that the global settings instance is available."""
        # Act & Assert - Check that global settings instance exists
        from settings.main import settings

        assert isinstance(settings, Settings)
        assert hasattr(settings, "base_repo_path")
        assert hasattr(settings, "telegram_enabled")

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

    def test_optional_telegram_fields(self):
        """Test that optional Telegram fields can be None."""
        # Arrange - Enable Telegram but don't set optional fields
        env_vars = {
            "AUTO_SLOPP_TELEGRAM_ENABLED": "true",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        # Act & Assert - Optional fields should be None when not set
        assert test_settings.telegram_enabled is True
        assert test_settings.telegram_bot_token is None
        assert test_settings.telegram_chat_id is None
