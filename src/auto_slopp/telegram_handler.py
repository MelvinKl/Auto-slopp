"""Telegram logging handler for sending log messages to Telegram."""

import asyncio
import logging
import time
from typing import Optional

import httpx

from settings.main import settings


class TelegramHandler(logging.Handler):
    """A logging handler that sends messages to Telegram via Bot API.

    This handler integrates with Python's standard logging module and
    sends formatted log messages to a Telegram chat using the Bot API.
    """

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        timeout: float = 30.0,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = True,
        disable_notification: bool = False,
    ):
        """Initialize the Telegram handler.

        Args:
            bot_token: Telegram bot token. If None, uses settings.
            chat_id: Telegram chat ID. If None, uses settings.
            timeout: Request timeout in seconds.
            retry_attempts: Number of retry attempts for failed requests.
            retry_delay: Delay between retry attempts in seconds.
            parse_mode: Message parse mode (HTML, Markdown, or None).
            disable_web_page_preview: Disable web page preview in messages.
            disable_notification: Disable notification sound.
        """
        super().__init__()
        self.bot_token = bot_token or settings.telegram_bot_token
        self.chat_id = chat_id or settings.telegram_chat_id
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview
        self.disable_notification = disable_notification

        if not self.bot_token or not self.chat_id:
            raise ValueError(
                "Both bot_token and chat_id must be provided or configured in settings"
            )

        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        self.client = httpx.AsyncClient(timeout=timeout)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record by sending it to Telegram.

        This method runs the async send operation in an event loop.

        Args:
            record: The log record to send.
        """
        try:
            # Try to get the current event loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, create a new one
                loop = asyncio.new_event_loop()
                loop.run_until_complete(self._send_message_async(record))
                loop.close()
                return

            # If we have a running loop, create a task
            if loop.is_running():
                # Create a new task in the running loop
                task = loop.create_task(self._send_message_async(record))
                # We can't await here, so we'll set up error handling
                task.add_done_callback(self._handle_task_result)
            else:
                loop.run_until_complete(self._send_message_async(record))

        except Exception:
            # Don't let logging errors break the application
            self.handleError(record)

    def _handle_task_result(self, task: asyncio.Task) -> None:
        """Handle the result of an async task."""
        try:
            task.result()
        except Exception:
            # Error already logged in _send_message_async
            pass

    async def _send_message_async(self, record: logging.LogRecord) -> None:
        """Send a log message to Telegram asynchronously.

        Args:
            record: The log record to send.
        """
        try:
            message = self.format(record)

            # Escape HTML characters if using HTML parse mode
            if self.parse_mode == "HTML":
                message = self._escape_html(message)

            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": self.parse_mode if self.parse_mode else None,
                "disable_web_page_preview": self.disable_web_page_preview,
                "disable_notification": self.disable_notification,
            }

             # Remove None values from payload
             payload = {k: v for k, v in payload.items() if v is not None}
             
             for attempt in range(self.retry_attempts):
                 try:
                     response = await self.client.post(self.api_url, json=payload)
                     response.raise_for_status()
                     break
                 except httpx.HTTPStatusError as e:
                     if e.response.status_code == 429:  # Rate limited
                         retry_after = int(
                             e.response.headers.get("retry-after", self.retry_delay)
                         )
                         await asyncio.sleep(retry_after)
                         continue
                     elif attempt == self.retry_attempts - 1:
                         raise
                     await asyncio.sleep(self.retry_delay)
                 except Exception:
                     if attempt == self.retry_attempts - 1:
                         raise
                     await asyncio.sleep(self.retry_delay)

        except Exception as e:
            # Log the error but don't raise it
            logging.getLogger(__name__).error(f"Failed to send Telegram message: {e}")

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters for Telegram messages.

        Args:
            text: Text to escape.

        Returns:
            Escaped text safe for HTML parse mode.
        """
        html_escape_table = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
        }
        return "".join(html_escape_table.get(c, c) for c in text)

    def close(self) -> None:
        """Close the HTTP client."""
        if hasattr(self, "client"):
            try:
                loop = asyncio.get_running_loop()
                asyncio.create_task(self.client.aclose())
            except RuntimeError:
                # No running loop, close synchronously
                loop = asyncio.new_event_loop()
                loop.run_until_complete(self.client.aclose())
                loop.close()
        super().close()


def setup_telegram_logging(
    level: int = logging.INFO, format_string: Optional[str] = None, **handler_kwargs
) -> Optional[logging.Handler]:
    """Set up Telegram logging handler.

    Args:
        level: Logging level for the handler.
        format_string: Custom format string for log messages.
        **handler_kwargs: Additional arguments for TelegramHandler.

    Returns:
        Configured TelegramHandler or None if Telegram logging is disabled.
    """
    if not settings.telegram_enabled:
        return None

    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logging.warning(
            "Telegram logging is enabled but bot_token or chat_id is not configured"
        )
        return None

    # Create handler with default settings from configuration
    handler = TelegramHandler(
        timeout=settings.telegram_timeout,
        retry_attempts=settings.telegram_retry_attempts,
        retry_delay=settings.telegram_retry_delay,
        parse_mode=settings.telegram_parse_mode,
        disable_web_page_preview=settings.telegram_disable_web_page_preview,
        disable_notification=settings.telegram_disable_notification,
        **handler_kwargs,
    )

    handler.setLevel(level)

    if format_string is None:
        format_string = (
            "<b>{levelname}</b> ({name})\nMessage: {message}\nTime: {asctime}"
        )

    formatter = logging.Formatter(format_string, style="{")
    handler.setFormatter(formatter)

    return handler
