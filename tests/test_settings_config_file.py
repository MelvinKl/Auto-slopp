"""Tests for settings configuration file functionality."""

import os
from unittest.mock import patch

from settings.main import Settings


class TestSettingsConfigFile:
    """Test cases for Settings configuration file functionality."""

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
            env_vars = {
                "AUTO_SLOPP_CONFIG_FILE_PATH": temp_file_path,
            }
            # Clear all environment variables and set only the ones we need
            with patch.dict(os.environ, env_vars, clear=True):
                test_settings = Settings()

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
            "AUTO_SLOPP_CLI_CONFIGURATIONS": (
                '[{"cli_command": "env-override", "cli_args": ["--env-arg"], "capability": 3}]'
            ),
        }
        with patch.dict(os.environ, env_vars, clear=False):
            test_settings = Settings()

            # Should use env var override, not file config
            assert len(test_settings.cli_configurations) == 1
            assert test_settings.cli_configurations[0].cli_command == "env-override"
            assert test_settings.cli_configurations[0].cli_args == ["--env-arg"]
            assert test_settings.cli_configurations[0].capability == 3

    def test_cli_configurations_env_path_override(self):
        """Test that AUTO_SLOPP_CONFIG_FILE env var overrides the default config file path."""
        # Create a temporary config file for testing
        import tempfile

        test_config_content = """
cli_configurations:
  - cli_command: path-override-test
    cli_args: ["--path-override-arg"]
    capability: 7
    name: path-override-test
    cooldown_seconds: 3600
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(test_config_content)
            temp_file_path = f.name

        try:
            env_vars = {
                "AUTO_SLOPP_CONFIG_FILE": temp_file_path,
            }
            with patch.dict(os.environ, env_vars, clear=False):
                # Clear any CLI config env vars to ensure we try to load from file
                env_vars_to_clear = {k: v for k, v in os.environ.items() if k.startswith("AUTO_SLOPP_") and "CLI" in k}
                for key in env_vars_to_clear:
                    if key in os.environ:
                        del os.environ[key]

                test_settings = Settings()

                # Should load configurations from the custom file specified by AUTO_SLOPP_CONFIG_FILE
                assert len(test_settings.cli_configurations) == 1
                assert test_settings.cli_configurations[0].cli_command == "path-override-test"
                assert test_settings.cli_configurations[0].capability == 7
                assert test_settings.cli_configurations[0].name == "path-override-test"
                assert test_settings.cli_configurations[0].cli_args == ["--path-override-arg"]
                assert test_settings.cli_configurations[0].cooldown_seconds == 3600
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)

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
