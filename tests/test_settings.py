"""Tests for settings module."""

from pathlib import Path

import pytest

from auto_slopp.settings import Settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings(self):
        """Test that default settings are correctly set."""
        settings = Settings()

        assert settings.task_directory == Path.cwd()
        assert settings.verbose is False

    def test_custom_settings(self):
        """Test that custom settings are correctly set."""
        settings = Settings(
            task_directory=Path("/test/path"),
            verbose=True,
        )

        assert settings.task_directory == Path("/test/path")
        assert settings.verbose is True

    def test_from_dict(self):
        """Test creating settings from dictionary."""
        data = {
            "task_directory": "/custom/path",
            "verbose": True,
        }

        settings = Settings.from_dict(data)

        assert settings.task_directory == Path("/custom/path")
        assert settings.verbose is True

    def test_to_dict(self):
        """Test converting settings to dictionary."""
        settings = Settings(
            task_directory=Path("/test/path"),
            verbose=True,
        )

        data = settings.to_dict()

        assert data["task_directory"] == "/test/path"
        assert data["verbose"] is True
