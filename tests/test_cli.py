"""Tests for CLI module."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from auto_slopp.cli import cli, create_parser


class TestCreateParser:
    """Test cases for CLI parser."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        parser = create_parser()

        args = parser.parse_args([])

        assert args.directory == Path.cwd()
        assert args.verbose is False

    def test_verbose_flag(self):
        """Test that verbose flag is parsed correctly."""
        parser = create_parser()

        args = parser.parse_args(["-v"])

        assert args.verbose is True

    def test_directory_option(self):
        """Test that directory option is parsed correctly."""
        parser = create_parser()

        args = parser.parse_args(["-d", "/test/dir"])

        assert args.directory == Path("/test/dir")

    def test_version_option(self):
        """Test that version option is available."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["--version"])


class TestCli:
    """Test cases for CLI function."""

    def test_cli_default(self, tmp_path, capsys):
        """Test CLI runs with default settings."""
        with patch.object(sys, "argv", ["auto-slopp"]):
            with patch("auto_slopp.cli.Processor") as mock_processor:
                mock_instance = mock_processor.return_value
                mock_instance.count_pending.return_value = 0
                mock_instance.count_completed.return_value = 0
                mock_instance.process.return_value = 0

                with patch("auto_slopp.cli.Settings") as mock_settings:
                    mock_settings.return_value.verbose = False

                    result = cli()

                    assert result == 0

    def test_cli_verbose(self, tmp_path, capsys):
        """Test CLI runs with verbose settings."""
        with patch.object(sys, "argv", ["auto-slopp", "-v"]):
            with patch("auto_slopp.cli.Processor") as mock_processor:
                mock_instance = mock_processor.return_value
                mock_instance.count_pending.return_value = 2
                mock_instance.count_completed.return_value = 3
                mock_instance.process.return_value = 2

                with patch("auto_slopp.cli.Settings") as mock_settings:
                    mock_settings.return_value.verbose = True

                    result = cli()

                    assert result == 0
                    captured = capsys.readouterr()
                    assert "Pending tasks: 2" in captured.out
                    assert "Completed tasks: 3" in captured.out
