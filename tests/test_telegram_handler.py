"""Tests for telegram_handler module."""

import logging
from pathlib import Path

from auto_slopp.telegram_handler import TelegramHandler, setup_telegram_logging


class TestTelegramHandler:
    """Test cases for TelegramHandler class."""

    def test_handler_initialization(self):
        """Test that handler is initialized correctly."""
        handler = TelegramHandler(
            token="test_token",
            chat_id="test_chat_id",
            api_url="https://api.telegram.org/bot{token}/sendMessage",
        )

        assert handler.token == "test_token"
        assert handler.chat_id == "test_chat_id"
        assert handler.api_url == "https://api.telegram.org/bot{token}/sendMessage"


class TestSetupTelegramLogging:
    """Test cases for setup_telegram_logging function."""

    def test_returns_none(self):
        """Test that setup_telegram_logging returns None."""
        result = setup_telegram_logging()

        assert result is None
