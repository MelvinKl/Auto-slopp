"""Tests for Telegram logging handler."""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import httpx

from auto_slopp.telegram_handler import TelegramHandler, setup_telegram_logging
from settings.main import settings


class TestTelegramHandler:
    """Test cases for TelegramHandler."""

    def test_init_missing_credentials(self):
        """Test initialization fails without bot token and chat ID."""
        # Arrange - Mock settings with missing credentials
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': None,
            'telegram_chat_id': None
        }):
            # Act & Assert - Should raise ValueError
            with pytest.raises(ValueError, match="Both bot_token and chat_id must be provided"):
                TelegramHandler()

    def test_init_with_direct_credentials(self):
        """Test initialization with direct credentials (ignoring settings)."""
        # Arrange - Mock settings with different credentials
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': 'settings_token',
            'telegram_chat_id': 'settings_chat'
        }):
            # Act - Create handler with direct credentials
            handler = TelegramHandler(
                bot_token='direct_token',
                chat_id='direct_chat'
            )
            
            # Assert - Direct credentials should override settings
            assert handler.bot_token == 'direct_token'
            assert handler.chat_id == 'direct_chat'
            assert 'direct_token' in handler.api_url

    def test_init_success_with_settings(self):
        """Test successful initialization with settings credentials."""
        # Arrange - Mock settings with valid credentials
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            # Act - Create handler
            handler = TelegramHandler()
            
            # Assert - Should use settings credentials
            assert handler.bot_token == 'test_token'
            assert handler.chat_id == 'test_chat'
            assert 'test_token' in handler.api_url
            assert handler.timeout == 30.0  # Default timeout
            assert handler.retry_attempts == 3  # Default retry attempts

    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters."""
        # Arrange - Mock settings
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            # Act - Create handler with custom parameters
            handler = TelegramHandler(
                timeout=60.0,
                retry_attempts=5,
                retry_delay=2.0,
                parse_mode="Markdown",
                disable_web_page_preview=False,
                disable_notification=True
            )
            
            # Assert - Custom parameters should be set
            assert handler.timeout == 60.0
            assert handler.retry_attempts == 5
            assert handler.retry_delay == 2.0
            assert handler.parse_mode == "Markdown"
            assert handler.disable_web_page_preview is False
            assert handler.disable_notification is True

    @patch('httpx.AsyncClient')
    def test_emit_success_with_running_loop(self, mock_client_class):
        """Test successful message emission with running event loop."""
        # Arrange - Mock HTTP client and response
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

            # Act - Test with running loop
            async def test_with_running_loop():
                loop = asyncio.get_running_loop()
                handler.emit(record)
                # Give some time for the async task to complete
                await asyncio.sleep(0.1)
                
                # Assert - Message should be sent
                mock_client.post.assert_called_once()
                call_args = mock_client.post.call_args
                assert 'json' in call_args.kwargs
                payload = call_args.kwargs['json']
                assert payload['chat_id'] == 'test_chat'
                assert 'Test message' in payload['text']

            # Run the test
            asyncio.run(test_with_running_loop())

    @patch('httpx.AsyncClient')
    def test_emit_with_no_running_loop(self, mock_client_class):
        """Test message emission when no event loop is running."""
        # Arrange - Mock HTTP client
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

            # Act - Emit without running loop
            handler.emit(record)
            
            # Assert - Message should be sent
            mock_client.post.assert_called_once()

    @patch('httpx.AsyncClient')
    def test_emit_with_http_error(self, mock_client_class):
        """Test handling of HTTP errors during emission."""
        # Arrange - Mock HTTP client with error
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=MagicMock(), response=MagicMock(status_code=400)
        )

        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            handler = TelegramHandler(retry_attempts=1)  # Only try once
            handler.setFormatter(logging.Formatter('%(message)s'))

            # Create a test log record
            record = logging.LogRecord(
                name='test_logger',
                level=logging.ERROR,
                pathname='',
                lineno=0,
                msg='Error message',
                args=(),
                exc_info=None
            )

            # Act - Emit with error
            handler.emit(record)
            
            # Assert - Error should be handled (no exception raised)
            mock_client.post.assert_called_once()

    @patch('httpx.AsyncClient')
    def test_retry_mechanism(self, mock_client_class):
        """Test retry mechanism for failed requests."""
        # Arrange - Mock HTTP client with initial failure then success
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response_success = AsyncMock()
        mock_response_success.raise_for_status = AsyncMock()
        
        # Create an exception that will be raised on first call
        error_response = MagicMock()
        error_response.status_code = 500
        http_error = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=error_response
        )
        
        # First call fails, second succeeds
        mock_client.post.side_effect = [http_error, mock_response_success]

        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            handler = TelegramHandler(retry_attempts=2, retry_delay=0.01)
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

            # Act - Send message
            asyncio.run(handler._send_message_async(record))
            
            # Assert - Should retry and succeed
            assert mock_client.post.call_count == 2

    @patch('httpx.AsyncClient')
    def test_rate_limiting_handling(self, mock_client_class):
        """Test handling of rate limiting (HTTP 429)."""
        # Arrange - Mock HTTP client with rate limit response
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response_success = AsyncMock()
        mock_response_success.raise_for_status = AsyncMock()
        
        # Create rate limit error response
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {'retry-after': '1'}
        rate_limit_error = httpx.HTTPStatusError(
            "Too Many Requests", request=MagicMock(), response=rate_limit_response
        )
        
        # First call rate limited, second succeeds
        mock_client.post.side_effect = [rate_limit_error, mock_response_success]

        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            handler = TelegramHandler(retry_attempts=2, retry_delay=0.01)
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

            # Act - Send message
            asyncio.run(handler._send_message_async(record))
            
            # Assert - Should respect retry-after header
            assert mock_client.post.call_count == 2

    def test_escape_html_comprehensive(self):
        """Test HTML escaping with various special characters."""
        # Arrange
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            handler = TelegramHandler()
            
            # Test cases with various special characters
            test_cases = [
                ("Test & <test> & more", "Test &amp; &lt;test&gt; &amp; more"),
                ("<script>alert('xss')</script>", "&lt;script&gt;alert('xss')&lt;/script&gt;"),
                ("Normal text", "Normal text"),
                ("", ""),
                ("&<>", "&amp;&lt;&gt;"),
            ]
            
            # Act & Assert - Test each case
            for input_text, expected_output in test_cases:
                result = handler._escape_html(input_text)
                assert result == expected_output

    @patch('httpx.AsyncClient')
    def test_payload_construction(self, mock_client_class):
        """Test that payload is correctly constructed with various settings."""
        # Arrange - Mock HTTP client
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response
        
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            handler = TelegramHandler(parse_mode="HTML", disable_web_page_preview=True, disable_notification=False)
            
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
            
            # Act - Send message
            asyncio.run(handler._send_message_async(record))
            
            # Assert - Check payload structure
            call_args = mock_client.post.call_args
            payload = call_args.kwargs['json']
            
            assert payload['chat_id'] == 'test_chat'
            assert 'Test message' in payload['text']
            assert payload['parse_mode'] == 'HTML'
            assert payload['disable_web_page_preview'] is True
            assert payload['disable_notification'] is False

    @patch('httpx.AsyncClient')
    def test_payload_with_none_parse_mode(self, mock_client_class):
        """Test payload construction when parse_mode is None."""
        # Arrange - Mock HTTP client
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response
        
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            handler = TelegramHandler(parse_mode="")
            
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
            
            # Act - Send message
            asyncio.run(handler._send_message_async(record))
            
            # Assert - parse_mode should not be in payload (empty string becomes None)
            call_args = mock_client.post.call_args
            payload = call_args.kwargs['json']
            assert 'parse_mode' not in payload

    @patch('httpx.AsyncClient')
    def test_close_handler(self, mock_client_class):
        """Test closing the HTTP client."""
        # Arrange
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            handler = TelegramHandler()
            
            # Act - Close handler
            handler.close()
            
            # Assert - Client should be closed
            mock_client.aclose.assert_called_once()

    def test_setup_telegram_logging_disabled(self):
        """Test setup returns None when Telegram logging is disabled."""
        # Arrange
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_enabled': False
        }):
            # Act
            handler = setup_telegram_logging()
            
            # Assert
            assert handler is None

    def test_setup_telegram_logging_no_bot_token(self):
        """Test setup returns None when bot token is missing."""
        # Arrange
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_enabled': True,
            'telegram_bot_token': None,
            'telegram_chat_id': 'test_chat'
        }):
            # Act
            handler = setup_telegram_logging()
            
            # Assert
            assert handler is None

    def test_setup_telegram_logging_no_chat_id(self):
        """Test setup returns None when chat ID is missing."""
        # Arrange
        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_enabled': True,
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': None
        }):
            # Act
            handler = setup_telegram_logging()
            
            # Assert
            assert handler is None

    @patch('httpx.AsyncClient')
    def test_setup_telegram_logging_success(self, mock_client_class):
        """Test successful setup returns configured handler."""
        # Arrange
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_enabled': True,
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat',
            'telegram_timeout': 60.0,
            'telegram_retry_attempts': 5,
            'telegram_parse_mode': 'Markdown'
        }):
            # Act
            handler = setup_telegram_logging(level=logging.WARNING)
            
# Assert
            assert handler is not None
            assert isinstance(handler, TelegramHandler)
            # Access TelegramHandler-specific attributes
            telegram_handler = handler  # type: TelegramHandler
            assert telegram_handler.timeout == 60.0  # From settings
            assert telegram_handler.retry_attempts == 5  # From settings


class TestTelegramIntegration:
    """Integration tests for Telegram logging."""

    @patch('httpx.AsyncClient')
    def test_full_logging_flow(self, mock_client_class):
        """Test complete logging flow from logger to Telegram."""
        # Arrange
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict('auto_slopp.telegram_handler.settings.__dict__', {
            'telegram_enabled': True,
            'telegram_bot_token': 'test_token',
            'telegram_chat_id': 'test_chat'
        }):
            # Set up logger with Telegram handler
            logger = logging.getLogger('test_integration')
            logger.setLevel(logging.INFO)
            
            telegram_handler = setup_telegram_logging()
            assert telegram_handler is not None  # Ensure we have a handler
            logger.addHandler(telegram_handler)
            
            # Act - Log a message
            logger.info("Integration test message")
            
            # Give some time for async processing
            import asyncio
            asyncio.run(asyncio.sleep(0.1))
            
            # Assert - Message should be sent
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            payload = call_args.kwargs['json']
            assert 'Integration test message' in payload['text']
            
            # Cleanup
            logger.removeHandler(telegram_handler)
            telegram_handler.close()