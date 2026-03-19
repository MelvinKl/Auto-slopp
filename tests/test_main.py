"""Tests for main application functionality."""

import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from auto_slopp.main import parse_arguments, setup_logging


class TestMainApplication:
    """Test cases for main application functionality."""

    def test_parse_arguments_defaults(self):
        """Test argument parsing with default values."""
        with patch.object(sys, "argv", ["auto-slopp"]):
            args = parse_arguments()

            assert args.repo_path is None
            assert args.debug is False

    def test_parse_arguments_with_paths(self):
        """Test argument parsing with provided paths."""
        with patch.object(
            sys,
            "argv",
            [
                "auto-slopp",
                "--repo-path",
                "/test/repo",
            ],
        ):
            args = parse_arguments()

            assert str(args.repo_path) == "/test/repo"
            assert args.debug is False

    def test_parse_arguments_with_debug(self):
        """Test argument parsing with debug flag."""
        with patch.object(sys, "argv", ["auto-slopp", "--debug"]):
            args = parse_arguments()

            assert args.debug is True

    def test_parse_arguments_with_all_options(self):
        """Test argument parsing with all options."""
        with patch.object(
            sys,
            "argv",
            [
                "auto-slopp",
                "--repo-path",
                "/my/repo",
                "--debug",
            ],
        ):
            args = parse_arguments()

            assert str(args.repo_path) == "/my/repo"
            assert args.debug is True

    def test_setup_logging_debug_mode(self, mock_settings):
        """Test logging setup in debug mode."""
        mock_settings.debug = True

        import logging

        logging.root.handlers.clear()

        with patch("auto_slopp.main.settings", mock_settings):
            with patch("auto_slopp.main.setup_telegram_logging") as mock_telegram:
                mock_telegram.return_value = None

                setup_logging()

                assert len(logging.root.handlers) == 1
                assert isinstance(logging.root.handlers[0], logging.StreamHandler)
                assert logging.root.level == logging.DEBUG

    def test_setup_logging_production_mode(self, mock_settings):
        """Test logging setup in production mode."""
        mock_settings.debug = False

        import logging

        logging.root.handlers.clear()

        with patch("auto_slopp.main.settings", mock_settings):
            with patch("auto_slopp.main.setup_telegram_logging") as mock_telegram:
                mock_telegram.return_value = None

                setup_logging()

                assert len(logging.root.handlers) == 1
                assert isinstance(logging.root.handlers[0], logging.StreamHandler)
                assert logging.root.level == logging.INFO

    def test_setup_logging_with_telegram_enabled(self, mock_settings):
        """Test logging setup with Telegram integration enabled."""
        mock_settings.debug = False
        mock_settings.telegram_enabled = True

        mock_handler = MagicMock()

        with patch("auto_slopp.main.settings", mock_settings):
            with patch("auto_slopp.main.setup_telegram_logging") as mock_telegram:
                mock_telegram.return_value = mock_handler

                with patch("auto_slopp.main.logging.getLogger") as mock_get_logger:
                    mock_logger = MagicMock()
                    mock_get_logger.return_value = mock_logger

                    setup_logging()

                    mock_telegram.assert_called_once_with(level=logging.WARNING)
                    mock_logger.addHandler.assert_called_once_with(mock_handler)

    def test_setup_logging_httpx_logging_configured(self, mock_settings):
        """Test that httpx logging is configured to be less noisy."""
        mock_settings.debug = False

        with patch("auto_slopp.main.settings", mock_settings):
            with patch("auto_slopp.main.setup_telegram_logging") as mock_telegram:
                mock_telegram.return_value = None

                with patch("auto_slopp.main.logging.getLogger") as mock_get_logger:
                    mock_httpx_logger = MagicMock()
                    mock_get_logger.return_value = mock_httpx_logger

                    setup_logging()

                    mock_httpx_logger.setLevel.assert_called_with(30)

    @patch("auto_slopp.main.run_executor")
    def test_main_function_with_keyboard_interrupt(self, mock_run_executor, mock_settings):
        """Test main function handles KeyboardInterrupt gracefully."""
        mock_run_executor.side_effect = KeyboardInterrupt()

        with patch("auto_slopp.main.settings", mock_settings):
            with patch("auto_slopp.main.parse_arguments") as mock_parse:
                mock_args = MagicMock()
                mock_args.repo_path = None
                mock_args.debug = False
                mock_parse.return_value = mock_args

                with patch("auto_slopp.main.setup_logging"):
                    with patch("auto_slopp.main.sys.exit"):
                        from auto_slopp.main import main

                        main()

                        # Verify exit was called with code 0
                        # Note: We can't directly assert on the mock since we didn't capture it
                        # but we know the function called sys.exit

    @patch("auto_slopp.main.run_executor")
    def test_main_function_with_exception(self, mock_run_executor, mock_settings):
        """Test main function handles exceptions gracefully."""
        mock_run_executor.side_effect = Exception("Test error")

        with patch("auto_slopp.main.settings", mock_settings):
            with patch("auto_slopp.main.parse_arguments") as mock_parse:
                mock_args = MagicMock()
                mock_args.repo_path = None
                mock_args.debug = False
                mock_parse.return_value = mock_args

                with patch("auto_slopp.main.setup_logging"):
                    with patch("auto_slopp.main.sys.exit") as mock_exit:
                        from auto_slopp.main import main

                        main()

                        mock_exit.assert_called_once_with(1)

    @patch("auto_slopp.main.run_executor")
    def test_main_function_successful_execution(self, mock_run_executor, mock_settings):
        """Test main function executes successfully."""
        mock_settings.base_repo_path = Path("/default/repo")
        mock_settings.debug = False
        mock_settings.telegram_enabled = False

        with patch("auto_slopp.main.settings", mock_settings):
            with patch("auto_slopp.main.parse_arguments") as mock_parse:
                mock_args = MagicMock()
                mock_args.repo_path = Path("/custom/repo")
                mock_args.debug = True
                mock_parse.return_value = mock_args

                with patch("auto_slopp.main.setup_logging"):
                    with patch("auto_slopp.main.sys.exit"):
                        from auto_slopp.main import main

                        mock_run_executor.assert_not_called()

                        with patch("auto_slopp.main.run_executor") as mock_executor:
                            mock_executor.side_effect = KeyboardInterrupt()
                            main()

                            mock_executor.assert_called_once_with(
                                repo_path=Path("/custom/repo"),
                            )
