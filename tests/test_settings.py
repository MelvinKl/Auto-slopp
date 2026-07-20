"""Tests for Pydantic settings validation."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from settings.main import Settings


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
        from settings.main import settings

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
        assert test_settings.cli_configurations[0].cli_command == "codex"
        assert test_settings.cli_configurations[1].cli_command == "opencode"
        assert test_settings.cli_configurations[2].cli_command == "opencode"
        assert test_settings.cli_configurations[3].cli_command == "opencode"
        assert test_settings.cli_configurations[4].cli_command == "opencode"
        assert test_settings.cli_configurations[5].cli_command == "opencode"
        assert test_settings.cli_configurations[6].cli_command == "opencode"
        assert test_settings.cli_configurations[7].cli_command == "gemini"
        assert test_settings.cli_configurations[8].cli_command == "claude"
        assert test_settings.cli_configurations[9].cli_command == "gemini"
        assert "gemini-ultra" in str(test_settings.cli_configurations[9].cli_args)

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
        assert test_settings.github_issue_step_max_iterations == 50

    def test_github_issue_step_max_iterations_validation(self):
        """Test github_issue_step_max_iterations must be at least 1."""
        env_vars = {
            "AUTO_SLOPP_GITHUB_ISSUE_STEP_MAX_ITERATIONS": "0",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError):
                Settings()

    def test_stale_branch_days_threshold_default(self):
        """Test default stale_branch_days_threshold value."""
        test_settings = Settings()
        assert test_settings.stale_branch_days_threshold == 1

    def test_stale_branch_days_threshold_custom(self):
        """Test that stale_branch_days_threshold can be customized."""
        env_vars = {
            "AUTO_SLOPP_STALE_BRANCH_DAYS_THRESHOLD": "7",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        assert test_settings.stale_branch_days_threshold == 7

    def test_stale_branch_days_threshold_validation(self):
        """Test that stale_branch_days_threshold must be non-negative."""
        env_vars = {
            "AUTO_SLOPP_STALE_BRANCH_DAYS_THRESHOLD": "-1",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError):
                Settings()

    def test_stale_branch_days_threshold_zero(self):
        """Test that stale_branch_days_threshold can be set to zero."""
        env_vars = {
            "AUTO_SLOPP_STALE_BRANCH_DAYS_THRESHOLD": "0",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            test_settings = Settings()

        assert test_settings.stale_branch_days_threshold == 0

    def test_cli_configurations_from_file(self):
        """Test loading CLI configurations from the default config file."""
        # Clear any CLI config env vars to ensure we load from file
        env_vars_to_clear = {k: v for k, v in os.environ.items() if k.startswith("AUTO_SLOPP_") and "CLI" in k}
        with patch.dict(os.environ, {}, clear=False):
            for key in env_vars_to_clear:
                if key in os.environ:
                    del os.environ[key]

            test_settings = Settings()

            # Should load configurations from the default file
            assert len(test_settings.cli_configurations) == 10
            assert test_settings.cli_configurations[0].cli_command == "claude"
            assert test_settings.cli_configurations[0].capability == 10
            assert test_settings.cli_configurations[0].name == "claude opus"

            assert test_settings.cli_configurations[1].cli_command == "claude"
            assert test_settings.cli_configurations[1].capability == 8
            assert test_settings.cli_configurations[1].name == "claude sonnet"

    def test_cli_configurations_custom_file_path(self):
        """Test loading CLI configurations from a custom file path specified by env var."""
        # Create a temporary config file for testing
        import os
        import tempfile

        test_config_content = """
cli_configurations:
  - cli_command: test-cli
    cli_args: ["--test-arg"]
    capability: 9
    name: test-cli
    cooldown_seconds: 1800
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(test_config_content)
            temp_file_path = f.name

        try:
            print(
                f"DEBUG: Original environment has AUTO_SLOPP_CONFIG_FILE_PATH: {os.environ.get('AUTO_SLOPP_CONFIG_FILE_PATH')}"
            )

            env_vars = {
                "AUTO_SLOPP_CONFIG_FILE_PATH": temp_file_path,
            }
            print(f"DEBUG: Setting environment variable AUTO_SLOPP_CONFIG_FILE_PATH={temp_file_path}")

            # Clear all environment variables and set only the ones we need
            with patch.dict(os.environ, env_vars, clear=True):
                print(
                    f"DEBUG: After patch.dict, environment has AUTO_SLOPP_CONFIG_FILE_PATH: {os.environ.get('AUTO_SLOPP_CONFIG_FILE_PATH')}"
                )

                test_settings = Settings()

                # Debug: Print the actual config_file_path value
                print(f"DEBUG: test_settings.config_file_path = {test_settings.config_file_path}")
                print(f"DEBUG: Expected: {temp_file_path}")
                print(
                    f"DEBUG: Types - actual: {type(test_settings.config_file_path)}, expected: {type(temp_file_path)}"
                )

                # Should load configurations from the custom file
                assert len(test_settings.cli_configurations) == 1
                assert test_settings.cli_configurations[0].cli_command == "test-cli"
                assert test_settings.cli_configurations[0].capability == 9
                assert test_settings.cli_configurations[0].name == "test-cli"
                assert test_settings.cli_configurations[0].cli_args == ["--test-arg"]
                assert test_settings.cli_configurations[0].cooldown_seconds == 1800
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)

    def test_cli_configurations_env_override_takes_precedence(self):
        """Test that environment variable override takes precedence over file configuration."""
        env_vars = {
            "AUTO_SLOPP_CLI_CONFIGURATIONS": '[{"cli_command": "env-override", "cli_args": ["--env-arg"], "capability": 3}]',
        }
        with patch.dict(os.environ, env_vars, clear=False):
            test_settings = Settings()

            # Debug: Print what we actually got
            print(f"DEBUG: Got cli_configurations length: {len(test_settings.cli_configurations)}")
            if len(test_settings.cli_configurations) > 0:
                print(f"DEBUG: First config: {test_settings.cli_configurations[0]}")
                print(f"DEBUG: First config capability: {test_settings.cli_configurations[0].capability}")

            # Should use env var override, not file config
            assert len(test_settings.cli_configurations) == 1
            assert test_settings.cli_configurations[0].cli_command == "env-override"
            assert test_settings.cli_configurations[0].cli_args == ["--env-arg"]
            assert test_settings.cli_configurations[0].capability == 3

    def test_cli_configurations_file_not_found(self):
        """Test graceful handling when config file is not found."""
        env_vars = {
            "AUTO_SLOPP_CONFIG_FILE_PATH": "/non/existent/path/config.yaml",
        }
        with patch.dict(os.environ, env_vars, clear=False):
            # Clear any CLI config env vars to ensure we try to load from file
            env_vars_to_clear = {k: v for k, v in os.environ.items() if k.startswith("AUTO_SLOPP_") and "CLI" in k}
            for key in env_vars_to_clear:
                if key in os.environ:
                    del os.environ[key]

            test_settings = Settings()

            # Should have empty configurations when file not found
            assert len(test_settings.cli_configurations) == 0

    def test_cli_configurations_malformed_file(self):
        """Test graceful handling of malformed config file."""
        # Create a temporary malformed config file
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: :")
            temp_file_path = f.name

        try:
            env_vars = {
                "AUTO_SLOPP_CONFIG_FILE_PATH": temp_file_path,
            }
            with patch.dict(os.environ, env_vars, clear=False):
                # Clear any CLI config env vars to ensure we try to load from file
                env_vars_to_clear = {k: v for k, v in os.environ.items() if k.startswith("AUTO_SLOPP_") and "CLI" in k}
                for key in env_vars_to_clear:
                    if key in os.environ:
                        del os.environ[key]

                test_settings = Settings()

                # Should have empty configurations when file is malformed
                assert len(test_settings.cli_configurations) == 0
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)

    def test_task_difficulties_keys(self):
        """Test that task_difficulties contains all expected phase-based keys."""
        test_settings = Settings()
        assert set(test_settings.task_difficulties.keys()) == {
            "task_planning",
            "implementation",
            "task_implementation_validation",
            "remaining_steps_update",
            "pr_description",
            "pr_review",
            "git_checkout",
            "default",
        }

    def test_pr_review_worker_settings_defaults(self):
        """Test that PR review worker settings have correct defaults."""
        env_vars_to_keep = {k: v for k, v in os.environ.items() if not k.startswith("AUTO_SLOPP_")}
        with patch.dict(os.environ, env_vars_to_keep, clear=True):
            with patch("dotenv.load_dotenv", return_value=None):
                test_settings = Settings()

        assert test_settings.pr_review_worker_required_label == "AI"
        assert test_settings.pr_review_worker_min_comments == 0
        assert test_settings.pr_review_worker_max_comments == 9
