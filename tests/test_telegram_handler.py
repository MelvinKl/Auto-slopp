"""Tests for Telegram logging handler."""

import asyncio
import logging
from unittest.mock import AsyncMock, patch

import pytest

from auto_slopp.telegram_handler import TelegramHandler, setup_telegram_logging
from settings.main import settings


class TestTelegramHandler:
    """Test cases for TelegramHandler."""

    def test_init_missing_credentials(self):
        """Test initialization fails without bot token and chat ID."""
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': None,
            'telegram_chat_id': None
        }):
            with pytest.raises(ValueError, match="Both bot_token and chat_id must be provided"):
                TelegramHandler()

    def test_init_success(self):
        """Test successful initialization with credentials."""
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            handler = TelegramHandler()
            assert handler.bot_token == 'test_token'
            assert handler.chat_id == 'test_chat'
            assert 'test_token' in handler.api_url

    @patch('httpx.AsyncClient')
    def test_emit_success(self, mock_client_class):
        """Test successful message emission."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            handler = TelegramHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))

            # Create a test log record
            record = logging.LogRecord(
                name='test_logger',
                level=logging.INFO,
                pathname='',
                lineno=0,
                msg='Test message',
                args=(),
                exc_info=None
            )

            # Test the async method directly
            import asyncio
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(handler._send_message_async(record))
            finally:
                loop.close()
                
            # Verify the message was sent
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert 'json' in call_args.kwargs
            payload = call_args.kwargs['json']
            assert payload['chat_id'] == 'test_chat'
            assert 'Test message' in payload['text']

    def test_escape_html(self):
        """Test HTML escaping functionality."""
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            handler = TelegramHandler()
            
            test_text = "Test & <test> & more"
            escaped = handler._escape_html(test_text)
            assert escaped == "Test &amp; &lt;test&gt; &amp; more"

    def test_setup_telegram_logging_disabled(self):
        """Test setup returns None when Telegram logging is disabled."""
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_enabled': False
        }):
            handler = setup_telegram_logging()
            assert handler is None

    def test_setup_telegram_logging_no_credentials(self):
        """Test setup returns None when credentials are missing."""
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_enabled': True,
            'telegram_bot_token': None,
            'telegram_chat_id': 'test_chat'
        }):
            handler = setup_telegram_logging()
            assert handler is None

    @patch('httpx.AsyncClient')
    def test_setup_telegram_logging_success(self, mock_client_class):
        """Test successful setup returns configured handler."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_enabled': True,
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            handler = setup_telegram_logging()
            assert handler is not None
            assert isinstance(handler, TelegramHandler)
            assert handler.level == logging.INFO  # Default level