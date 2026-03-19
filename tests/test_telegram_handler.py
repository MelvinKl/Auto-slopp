"""Tests for Telegram logging handler."""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from auto_slopp.telegram_handler import TelegramHandler, setup_telegram_logging
from settings.main import settings


class TestTelegramHandler:
    """Test cases for TelegramHandler."""

    def test_init_missing_credentials(self):
        """Test initialization fails without bot token and chat ID."""
        # Arrange - Mock settings with missing credentials
        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__", {"telegram_bot_token": None, "telegram_chat_id": None}
        ):
            # Act & Assert - Should raise ValueError
            with pytest.raises(ValueError, match="Both bot_token and chat_id must be provided"):
                TelegramHandler()

    def test_init_with_direct_credentials(self):
        """Test initialization with direct credentials (ignoring settings)."""
        # Arrange - Mock settings with different credentials
        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_bot_token": "settings_token", "telegram_chat_id": "settings_chat"},
        ):
            # Act - Create handler with direct credentials
            handler = TelegramHandler(bot_token="direct_token", chat_id="direct_chat")

            # Assert - Direct credentials should override settings
            assert handler.bot_token == "direct_token"
            assert handler.chat_id == "direct_chat"
            assert "direct_token" in handler.api_url

    def test_init_success_with_settings(self):
        """Test successful initialization with settings credentials."""
        # Arrange - Mock settings with valid credentials
        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            # Act - Create handler
            handler = TelegramHandler()

            # Assert - Should use settings credentials
            assert handler.bot_token == "test_token"
            assert handler.chat_id == "test_chat"
            assert "test_token" in handler.api_url
            assert handler.timeout == 30.0  # Default timeout
            assert handler.retry_attempts == 3  # Default retry attempts

    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters."""
        # Arrange - Mock settings
        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            # Act - Create handler with custom parameters
            handler = TelegramHandler(
                timeout=60.0,
                retry_attempts=5,
                retry_delay=2.0,
                parse_mode="Markdown",
                disable_web_page_preview=False,
                disable_notification=True,
            )

            # Assert - Custom parameters should be set
            assert handler.timeout == 60.0
            assert handler.retry_attempts == 5
            assert handler.retry_delay == 2.0
            assert handler.parse_mode == "Markdown"
            assert handler.disable_web_page_preview is False
            assert handler.disable_notification is True

    @patch("httpx.AsyncClient")
    def test_emit_success_with_running_loop(self, mock_client_class):
        """Test successful message emission with running event loop."""
        # Arrange - Mock HTTP client and response
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create a test log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test message",
                args=(),
                exc_info=None,
            )

             # Act - Test with running loop
             async def test_with_running_loop():
                 asyncio.get_running_loop()
                 handler.emit(record)
                 # Give some time for the async task to complete
                 await asyncio.sleep(0.1)

                # Assert - Message should be sent
                mock_client.post.assert_called_once()
                call_args = mock_client.post.call_args
                assert "json" in call_args.kwargs
                payload = call_args.kwargs["json"]
                assert payload["chat_id"] == "test_chat"
                assert "Test message" in payload["text"]

            # Run the test
            asyncio.run(test_with_running_loop())

    @patch("httpx.AsyncClient")
    def test_emit_with_no_running_loop(self, mock_client_class):
        """Test message emission when no event loop is running."""
        # Arrange - Mock HTTP client
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create a test log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            # Act - Emit without running loop
            handler.emit(record)

            # Assert - Message should be sent
            mock_client.post.assert_called_once()

    @patch("httpx.AsyncClient")
    def test_emit_with_http_error(self, mock_client_class):
        """Test handling of HTTP errors during emission."""
        # Arrange - Mock HTTP client with error
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=MagicMock(), response=MagicMock(status_code=400)
        )

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler(retry_attempts=1)  # Only try once
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create a test log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg="Error message",
                args=(),
                exc_info=None,
            )

            # Act - Emit with error
            handler.emit(record)

            # Assert - Error should be handled (no exception raised)
            mock_client.post.assert_called_once()

    @patch("httpx.AsyncClient")
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
        http_error = httpx.HTTPStatusError("Server Error", request=MagicMock(), response=error_response)

        # First call fails, second succeeds
        mock_client.post.side_effect = [http_error, mock_response_success]

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler(retry_attempts=2, retry_delay=0.01)
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create a test log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            # Act - Send message
            asyncio.run(handler._send_message_async(record))

            # Assert - Should retry and succeed
            assert mock_client.post.call_count == 2

    @patch("httpx.AsyncClient")
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
        rate_limit_response.headers = {"retry-after": "1"}
        rate_limit_error = httpx.HTTPStatusError("Too Many Requests", request=MagicMock(), response=rate_limit_response)

        # First call rate limited, second succeeds
        mock_client.post.side_effect = [rate_limit_error, mock_response_success]

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler(retry_attempts=2, retry_delay=0.01)
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create a test log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            # Act - Send message
            asyncio.run(handler._send_message_async(record))

            # Assert - Should respect retry-after header
            assert mock_client.post.call_count == 2

    def test_escape_html_comprehensive(self):
        """Test HTML escaping with various special characters."""
        # Arrange
        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
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

    @patch("httpx.AsyncClient")
    def test_payload_construction(self, mock_client_class):
        """Test that payload is correctly constructed with various settings."""
        # Arrange - Mock HTTP client
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler(parse_mode="HTML", disable_web_page_preview=True, disable_notification=False)

            # Create a test log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            # Act - Send message
            asyncio.run(handler._send_message_async(record))

            # Assert - Check payload structure
            call_args = mock_client.post.call_args
            payload = call_args.kwargs["json"]

            assert payload["chat_id"] == "test_chat"
            assert "Test message" in payload["text"]
            assert payload["parse_mode"] == "HTML"
            assert payload["disable_web_page_preview"] is True
            assert payload["disable_notification"] is False

    @patch("httpx.AsyncClient")
    def test_payload_with_none_parse_mode(self, mock_client_class):
        """Test payload construction when parse_mode is None."""
        # Arrange - Mock HTTP client
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler(parse_mode="")

            # Create a test log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            # Act - Send message
            asyncio.run(handler._send_message_async(record))

            # Assert - parse_mode should not be in payload (empty string becomes None)
            call_args = mock_client.post.call_args
            payload = call_args.kwargs["json"]
            assert "parse_mode" not in payload

    @patch("httpx.AsyncClient")
    def test_close_handler(self, mock_client_class):
        """Test closing the HTTP client."""
        # Arrange
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler()

            # Act - Close handler
            handler.close()

            # Assert - Client should be closed
            mock_client.aclose.assert_called_once()

    def test_setup_telegram_logging_disabled(self):
        """Test setup returns None when Telegram logging is disabled."""
        # Arrange
        with patch.dict("auto_slopp.telegram_handler.settings.__dict__", {"telegram_enabled": False}):
            # Act
            handler = setup_telegram_logging()

            # Assert
            assert handler is None

    def test_setup_telegram_logging_no_bot_token(self):
        """Test setup returns None when bot token is missing."""
        # Arrange
        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": None, "telegram_chat_id": "test_chat"},
        ):
            # Act
            handler = setup_telegram_logging()

            # Assert
            assert handler is None

    def test_setup_telegram_logging_no_chat_id(self):
        """Test setup returns None when chat ID is missing."""
        # Arrange
        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": None},
        ):
            # Act
            handler = setup_telegram_logging()

            # Assert
            assert handler is None

    @patch("httpx.AsyncClient")
    def test_setup_telegram_logging_success(self, mock_client_class):
        """Test successful setup returns configured handler."""
        # Arrange
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {
                "telegram_enabled": True,
                "telegram_bot_token": "test_token",
                "telegram_chat_id": "test_chat",
                "telegram_timeout": 60.0,
                "telegram_retry_attempts": 5,
                "telegram_parse_mode": "Markdown",
            },
        ):
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

    @patch("httpx.AsyncClient")
    def test_full_logging_flow(self, mock_client_class):
        """Test complete logging flow from logger to Telegram."""
        # Arrange
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            # Set up logger with Telegram handler
            logger = logging.getLogger("test_integration")
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
            payload = call_args.kwargs["json"]
            assert "Integration test message" in payload["text"]

            # Cleanup
            logger.removeHandler(telegram_handler)
            telegram_handler.close()


class TestTelegramPerformance:
    """Performance tests for Telegram logging."""

    @patch("httpx.AsyncClient")
    def test_concurrent_message_sending(self, mock_client_class):
        """Test sending multiple messages concurrently."""
        # Arrange - Mock HTTP client
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create multiple log records
            records = [
                logging.LogRecord(
                    name="test_logger",
                    level=logging.INFO,
                    pathname="",
                    lineno=0,
                    msg=f"Concurrent message {i}",
                    args=(),
                    exc_info=None,
                )
                for i in range(10)
            ]

            # Act - Send messages concurrently
            async def send_concurrent():
                tasks = [handler._send_message_async(record) for record in records]
                await asyncio.gather(*tasks, return_exceptions=True)

            import time

            start_time = time.time()
            asyncio.run(send_concurrent())
            end_time = time.time()

            # Assert - All messages should be sent and time should be reasonable
            assert mock_client.post.call_count == 10
            assert end_time - start_time < 5.0  # Should complete within 5 seconds

    @patch("httpx.AsyncClient")
    def test_large_message_handling(self, mock_client_class):
        """Test handling of large messages."""
        # Arrange - Mock HTTP client
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create a large message (close to Telegram's 4096 character limit)
            large_message = "A" * 4000

            # Create a test log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg=large_message,
                args=(),
                exc_info=None,
            )

            # Act - Send large message
            asyncio.run(handler._send_message_async(record))

            # Assert - Message should be sent successfully
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            payload = call_args.kwargs["json"]
            assert len(payload["text"]) == 4000

    @patch("httpx.AsyncClient")
    def test_message_sending_speed(self, mock_client_class):
        """Test the speed of message sending."""
        # Arrange - Mock HTTP client with controlled delay
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()

        # Add a small delay to simulate network latency
        async def delayed_post(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms delay
            return mock_response

        mock_client.post.side_effect = delayed_post

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create a test log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Speed test message",
                args=(),
                exc_info=None,
            )

            # Act - Measure sending time
            import time

            start_time = time.time()
            asyncio.run(handler._send_message_async(record))
            end_time = time.time()

            # Assert - Should complete within reasonable time (including simulated delay)
            assert end_time - start_time < 1.0  # Should complete within 1 second
            mock_client.post.assert_called_once()


class TestTelegramErrorScenarios:
    """Additional error scenario tests for Telegram logging."""

    @patch("httpx.AsyncClient")
    def test_network_timeout_error(self, mock_client_class):
        """Test handling of network timeout errors."""
        # Arrange - Mock HTTP client with timeout error
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.post.side_effect = httpx.TimeoutException("Request timeout")

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler(retry_attempts=2, retry_delay=0.01)
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create a test log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg="Timeout test message",
                args=(),
                exc_info=None,
            )

            # Act - Send message with timeout error
            with patch("auto_slopp.telegram_handler.logging.getLogger") as mock_logger:
                mock_error_logger = MagicMock()
                mock_logger.return_value = mock_error_logger

                handler.emit(record)  # Should not raise exception

            # Assert - Should retry and log error but not raise exception
            assert mock_client.post.call_count == 2  # Initial attempt + 1 retry
            mock_error_logger.error.assert_called_once()

    @patch("httpx.AsyncClient")
    def test_authentication_error(self, mock_client_class):
        """Test handling of authentication errors (401)."""
        # Arrange - Mock HTTP client with auth error
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        auth_response = MagicMock()
        auth_response.status_code = 401
        auth_error = httpx.HTTPStatusError("Unauthorized", request=MagicMock(), response=auth_response)
        mock_client.post.side_effect = auth_error

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "invalid_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler(retry_attempts=1)  # Only try once
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create a test log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg="Auth test message",
                args=(),
                exc_info=None,
            )

            # Act - Send message with auth error
            with patch("auto_slopp.telegram_handler.logging.getLogger") as mock_logger:
                mock_error_logger = MagicMock()
                mock_logger.return_value = mock_error_logger

                handler.emit(record)  # Should not raise exception

            # Assert - Should log error but not retry (auth errors are not retryable)
            assert mock_client.post.call_count == 1
            mock_error_logger.error.assert_called_once()

    @patch("httpx.AsyncClient")
    def test_chat_not_found_error(self, mock_client_class):
        """Test handling of chat not found errors (404)."""
        # Arrange - Mock HTTP client with 404 error
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        not_found_response = MagicMock()
        not_found_response.status_code = 404
        not_found_error = httpx.HTTPStatusError("Chat not found", request=MagicMock(), response=not_found_response)
        mock_client.post.side_effect = not_found_error

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "invalid_chat"},
        ):
            handler = TelegramHandler(retry_attempts=1)  # Only try once
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create a test log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.WARNING,
                pathname="",
                lineno=0,
                msg="Chat not found test message",
                args=(),
                exc_info=None,
            )

            # Act - Send message with 404 error
            with patch("auto_slopp.telegram_handler.logging.getLogger") as mock_logger:
                mock_error_logger = MagicMock()
                mock_logger.return_value = mock_error_logger

                handler.emit(record)  # Should not raise exception

            # Assert - Should log error but not retry (404 errors are not retryable)
            assert mock_client.post.call_count == 1
            mock_error_logger.error.assert_called_once()

    @patch("httpx.AsyncClient")
    def test_connection_error(self, mock_client_class):
        """Test handling of connection errors."""
        # Arrange - Mock HTTP client with connection error
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.post.side_effect = httpx.ConnectError("Connection failed")

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler(retry_attempts=3, retry_delay=0.01)
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create a test log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.CRITICAL,
                pathname="",
                lineno=0,
                msg="Connection error test message",
                args=(),
                exc_info=None,
            )

            # Act - Send message with connection error
            with patch("auto_slopp.telegram_handler.logging.getLogger") as mock_logger:
                mock_error_logger = MagicMock()
                mock_logger.return_value = mock_error_logger

                handler.emit(record)  # Should not raise exception

            # Assert - Should retry connection errors
            assert mock_client.post.call_count == 3  # All retries should be attempted
            mock_error_logger.error.assert_called_once()

    def test_malformed_bot_token(self):
        """Test initialization with malformed bot token."""
        # Test cases with malformed tokens
        malformed_tokens = [
            "123",  # Too short
            "not_a_token",  # Missing colon
            "123456:abc",  # Valid format but potentially invalid
        ]

        for token in malformed_tokens:
            with patch.dict(
                "auto_slopp.telegram_handler.settings.__dict__",
                {"telegram_bot_token": token, "telegram_chat_id": "test_chat"},
            ):
                # Should initialize but fail when trying to send
                handler = TelegramHandler()
                assert handler.bot_token == token
                assert f"bot{token}" in handler.api_url

        # Test empty token should fail
        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_bot_token": "", "telegram_chat_id": "test_chat"},
        ):
            with pytest.raises(ValueError, match="Both bot_token and chat_id must be provided"):
                TelegramHandler()

    def test_invalid_chat_id_formats(self):
        """Test initialization with various chat ID formats."""
        # Test cases with different chat ID formats
        chat_ids = [
            "123456789",  # Numeric (user ID)
            "-123456789",  # Negative numeric (group ID)
            "@channel_name",  # Channel username
            "invalid",  # Invalid format
        ]

        for chat_id in chat_ids:
            with patch.dict(
                "auto_slopp.telegram_handler.settings.__dict__",
                {"telegram_bot_token": "test_token", "telegram_chat_id": chat_id},
            ):
                handler = TelegramHandler()
                assert handler.chat_id == chat_id


class TestTelegramConfigurationValidation:
    """Configuration validation tests for Telegram logging."""

    def test_configuration_defaults(self):
        """Test that default configuration values are properly set."""
        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {
                "telegram_enabled": True,
                "telegram_bot_token": "test_token",
                "telegram_chat_id": "test_chat",
                # Use defaults for other settings
            },
        ):
            handler = TelegramHandler()

            # Assert default values
            assert handler.timeout == 30.0
            assert handler.retry_attempts == 3
            assert handler.retry_delay == 1.0
            assert handler.parse_mode == "HTML"
            assert handler.disable_web_page_preview is True
            assert handler.disable_notification is False

    def test_configuration_boundary_values(self):
        """Test configuration with boundary values."""
        boundary_configs = [
            {"timeout": 0.1, "retry_attempts": 0, "retry_delay": 0.0},  # Minimum values
            {"timeout": 300.0, "retry_attempts": 10, "retry_delay": 60.0},  # Maximum values
        ]

        for config in boundary_configs:
            with patch.dict(
                "auto_slopp.telegram_handler.settings.__dict__",
                {"telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
            ):
                handler = TelegramHandler(**config)
                assert handler.timeout == config["timeout"]
                assert handler.retry_attempts == config["retry_attempts"]
                assert handler.retry_delay == config["retry_delay"]

    @patch("httpx.AsyncClient")
    def test_parse_mode_validation(self, mock_client_class):
        """Test different parse_mode values."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        parse_modes = ["HTML", "Markdown", None, ""]

        for parse_mode in parse_modes:
            with patch.dict(
                "auto_slopp.telegram_handler.settings.__dict__",
                {"telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
            ):
                handler = TelegramHandler(parse_mode=parse_mode)
                handler.setFormatter(logging.Formatter("%(message)s"))

                # Create a test log record
                record = logging.LogRecord(
                    name="test_logger",
                    level=logging.INFO,
                    pathname="",
                    lineno=0,
                    msg=f"Parse mode test: {parse_mode}",
                    args=(),
                    exc_info=None,
                )

                # Act - Send message
                asyncio.run(handler._send_message_async(record))

                # Assert - Check payload
                call_args = mock_client.post.call_args
                payload = call_args.kwargs["json"]

                if parse_mode:
                    assert payload.get("parse_mode") == parse_mode
                else:
                    assert "parse_mode" not in payload

    def test_setup_with_custom_format_string(self):
        """Test setup_telegram_logging with custom format string."""
        custom_format = "CUSTOM: {levelname} - {message} - {asctime}"

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = setup_telegram_logging(format_string=custom_format)

            assert handler is not None
            assert isinstance(handler, TelegramHandler)
            formatter = handler.formatter
            assert formatter is not None
            assert formatter._fmt == custom_format

    @patch("httpx.AsyncClient")
    def test_handler_level_filtering(self, mock_client_class):
        """Test that handler properly filters messages by level."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            # Set up handler with WARNING level
            handler = TelegramHandler()
            handler.setLevel(logging.WARNING)
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create log records at different levels
            warning_record = logging.LogRecord(
                name="test_logger",
                level=logging.WARNING,
                pathname="",
                lineno=0,
                msg="Warning message",
                args=(),
                exc_info=None,
            )
            error_record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg="Error message",
                args=(),
                exc_info=None,
            )

            # Act - Send messages that should pass through
            handler.emit(warning_record)  # Should pass through
            handler.emit(error_record)  # Should pass through

            # Wait for async processing
            asyncio.run(asyncio.sleep(0.1))

            # Assert - Only WARNING and ERROR should be sent
            assert mock_client.post.call_count == 2


class TestTelegramEndToEnd:
    """End-to-end tests for Telegram logging."""

    @patch("httpx.AsyncClient")
    def test_full_logging_lifecycle(self, mock_client_class):
        """Test complete logging lifecycle from setup to cleanup."""
        # Arrange
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            # Act - Set up logger
            logger = logging.getLogger("test_e2e")
            logger.setLevel(logging.DEBUG)

            telegram_handler = setup_telegram_logging(level=logging.INFO)
            assert telegram_handler is not None
            logger.addHandler(telegram_handler)

            # Send various types of log messages
            logger.debug("Debug message")  # Should be filtered
            logger.info("Info message")  # Should be sent
            logger.warning("Warning message")  # Should be sent
            logger.error("Error message")  # Should be sent

            # Log with exception
            try:
                raise ValueError("Test exception")
            except ValueError:
                logger.exception("Exception occurred")

            # Wait for async processing
            asyncio.run(asyncio.sleep(0.2))

            # Assert - Check that messages were sent
            assert mock_client.post.call_count == 4  # info, warning, error, exception

            # Verify message content
            calls = mock_client.post.call_args_list
            messages = [call.kwargs["json"]["text"] for call in calls]

            assert any("Info message" in msg for msg in messages)
            assert any("Warning message" in msg for msg in messages)
            assert any("Error message" in msg for msg in messages)
            assert any("Exception occurred" in msg and "ValueError" in msg for msg in messages)

            # Cleanup
            logger.removeHandler(telegram_handler)
            telegram_handler.close()

    @patch("httpx.AsyncClient")
    def test_multiple_loggers_telegram_integration(self, mock_client_class):
        """Test Telegram integration with multiple loggers."""
        # Arrange
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            # Set up multiple loggers with the same Telegram handler
            telegram_handler = setup_telegram_logging()
            assert telegram_handler is not None

            loggers = []
            for name in ["logger1", "logger2", "logger3"]:
                logger = logging.getLogger(f"test_multi_{name}")
                logger.setLevel(logging.INFO)
                logger.addHandler(telegram_handler)
                loggers.append(logger)

            # Act - Log messages from different loggers
            loggers[0].info("Message from logger1")
            loggers[1].info("Message from logger2")
            loggers[2].info("Message from logger3")

            # Wait for async processing
            asyncio.run(asyncio.sleep(0.2))

            # Assert - All messages should be sent
            assert mock_client.post.call_count == 3

            # Cleanup
            for logger in loggers:
                logger.removeHandler(telegram_handler)
            telegram_handler.close()

    @patch("httpx.AsyncClient")
    def test_handler_removal_and_addition(self, mock_client_class):
        """Test adding and removing Telegram handler dynamically."""
        # Arrange
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            logger = logging.getLogger("test_dynamic")
            logger.setLevel(logging.INFO)

            # Act - Add handler, log messages, remove handler, log more
            telegram_handler = setup_telegram_logging()
            assert telegram_handler is not None
            logger.addHandler(telegram_handler)

            logger.info("Message with handler")
            asyncio.run(asyncio.sleep(0.1))

            # Remove handler
            logger.removeHandler(telegram_handler)
            logger.info("Message without handler")
            asyncio.run(asyncio.sleep(0.1))

            # Re-add handler
            logger.addHandler(telegram_handler)
            logger.info("Message with handler again")
            asyncio.run(asyncio.sleep(0.1))

            # Assert - Only messages with handler should be sent
            assert mock_client.post.call_count == 2

            # Cleanup
            logger.removeHandler(telegram_handler)
            telegram_handler.close()

    @patch("httpx.AsyncClient")
    def test_error_recovery_and_continued_operation(self, mock_client_class):
        """Test that handler continues working after transient errors."""
        # Arrange - Mock HTTP client with intermittent failures
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()

        # Simulate: success, failure, success, failure, success
        error_response = MagicMock()
        error_response.status_code = 500
        http_error = httpx.HTTPStatusError("Server Error", request=MagicMock(), response=error_response)

        mock_client.post.side_effect = [
            mock_response,  # Success
            http_error,  # Failure (will retry)
            http_error,  # Failure (final retry fails)
            mock_response,  # Success
            mock_response,  # Success
        ]

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler(retry_attempts=2, retry_delay=0.01)
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Create log records
            records = [
                logging.LogRecord(
                    name="test", level=logging.INFO, pathname="", lineno=0, msg=f"Message {i}", args=(), exc_info=None
                )
                for i in range(5)
            ]

            with patch("auto_slopp.telegram_handler.logging.getLogger") as mock_logger:
                mock_error_logger = MagicMock()
                mock_logger.return_value = mock_error_logger

                # Act - Send all messages
                for record in records:
                    handler.emit(record)
                    asyncio.run(asyncio.sleep(0.01))

            # Assert - Should continue operation despite failures
            # 3 successful sends, 1 failed after retries, 1 successful retry
            assert mock_client.post.call_count >= 4  # At least 4 attempts (retry counts)
            mock_error_logger.error.assert_called()  # Error should be logged

    @patch("httpx.AsyncClient")
    def test_concurrent_access_safety(self, mock_client_class):
        """Test that handler is safe for concurrent access."""
        # Arrange
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch.dict(
            "auto_slopp.telegram_handler.settings.__dict__",
            {"telegram_enabled": True, "telegram_bot_token": "test_token", "telegram_chat_id": "test_chat"},
        ):
            handler = TelegramHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))

            # Act - Emit records from multiple "threads" (using async tasks)
            async def emit_from_task(task_id):
                for i in range(5):
                    record = logging.LogRecord(
                        name=f"task_{task_id}",
                        level=logging.INFO,
                        pathname="",
                        lineno=0,
                        msg=f"Task {task_id} Message {i}",
                        args=(),
                        exc_info=None,
                    )
                    handler.emit(record)
                    await asyncio.sleep(0.01)

            # Run multiple tasks concurrently
            async def run_all_tasks():
                tasks = [emit_from_task(i) for i in range(3)]
                await asyncio.gather(*tasks)

            asyncio.run(run_all_tasks())

            # Assert - All messages should be sent
            assert mock_client.post.call_count == 15  # 3 tasks * 5 messages each
