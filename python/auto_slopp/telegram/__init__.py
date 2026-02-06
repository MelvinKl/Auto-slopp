"""
Telegram Bot API Integration Module for Auto-slopp.

Handles Telegram message sending with rate limiting, error handling, and security.
Integrates with existing Auto-slopp logging system.
"""

import json
import time
import threading
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from queue import Queue, Empty

# from ..config import get_config
from ..logging import get_logger, LogLevel


@dataclass
class TelegramRateLimitingConfig:
    """Rate limiting configuration."""

    messages_per_second: int = 5
    burst_size: int = 20
    rate_limit_window_seconds: int = 60
    backoff_multiplier: float = 2.0
    max_backoff_seconds: int = 30


@dataclass
class TelegramFormattingConfig:
    """Message formatting configuration."""

    parse_mode: str = "HTML"
    max_message_length: int = 4000
    include_timestamp: bool = True
    include_log_level: bool = True
    include_script_name: bool = True
    use_emoji_indicators: bool = True


@dataclass
class TelegramSecurityConfig:
    """Security configuration."""

    validate_bot_token: bool = True
    encrypt_config_storage: bool = True
    audit_token_access: bool = True
    hide_tokens_in_logs: bool = True
    require_https: bool = True


@dataclass
class TelegramConfig:
    """Configuration for Telegram logging."""

    enabled: bool = False
    bot_token: str = ""
    default_chat_id: str = ""
    api_timeout_seconds: int = 10
    connection_retries: int = 3
    rate_limiting: TelegramRateLimitingConfig = None
    formatting: TelegramFormattingConfig = None
    security: TelegramSecurityConfig = None

    def __post_init__(self):
        if self.rate_limiting is None:
            self.rate_limiting = TelegramRateLimitingConfig()

        if self.formatting is None:
            self.formatting = TelegramFormattingConfig()

        if self.security is None:
            self.security = TelegramSecurityConfig()


@dataclass
class TelegramMessage:
    """Data structure for Telegram messages."""

    text: str
    chat_id: str
    parse_mode: str = "HTML"
    disable_web_page_preview: bool = True
    disable_notification: bool = False
    reply_to_message_id: Optional[int] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TelegramRateLimiter:
    """Rate limiting for Telegram API calls."""

    def __init__(self, config: TelegramConfig):
        self.config = config
        self.logger = get_logger(f"{__name__}.rate_limiter")

        # Rate limiting state
        self.message_times: List[float] = []
        self.last_request_time = 0.0
        self.current_backoff = 0.0
        self.consecutive_failures = 0

        # Rate limiting parameters
        self.messages_per_second = config.rate_limiting.messages_per_second
        self.burst_size = config.rate_limiting.burst_size
        self.window_seconds = config.rate_limiting.rate_limit_window_seconds
        self.backoff_multiplier = config.rate_limiting.backoff_multiplier
        self.max_backoff_seconds = config.rate_limiting.max_backoff_seconds

    def can_send_message(self) -> bool:
        """Check if a message can be sent without violating rate limits."""
        now = time.time()

        # Clean old message times
        cutoff = now - self.window_seconds
        self.message_times = [t for t in self.message_times if t > cutoff]

        # Check if we're within limits
        if len(self.message_times) < self.burst_size:
            return True

        # Check if we can send based on rate limit
        if len(self.message_times) >= self.messages_per_second:
            oldest_recent = min(self.message_times[-self.messages_per_second :])
            if now - oldest_recent < 1.0:
                return False

        return True

    def record_message_sent(self):
        """Record that a message was sent."""
        self.message_times.append(time.time())
        self.last_request_time = time.time()
        self.consecutive_failures = 0
        self.current_backoff = 0.0

    def record_failure(self):
        """Record a failure and calculate backoff."""
        self.consecutive_failures += 1
        self.current_backoff = min(
            self.backoff_multiplier**self.consecutive_failures, self.max_backoff_seconds
        )

        self.logger.warning(
            f"Telegram API failure #{self.consecutive_failures}, "
            f"backoff: {self.current_backoff:.2f}s"
        )

    def get_wait_time(self) -> float:
        """Get the time to wait before next message."""
        if self.current_backoff > 0:
            return self.current_backoff

        now = time.time()
        if self.message_times:
            oldest_allowed = now - 1.0 / self.messages_per_second
            recent_messages = [t for t in self.message_times if t > oldest_allowed]

            if len(recent_messages) >= self.messages_per_second:
                oldest_recent = min(recent_messages)
                return max(0, 1.0 - (now - oldest_recent))

        return 0.0


class TelegramQueue:
    """Message queue for Telegram with async processing."""

    def __init__(self, config: TelegramConfig):
        self.config = config
        self.logger = get_logger(f"{__name__}.queue")

        # Queue and processing
        self.queue = Queue()
        self.worker_thread = None
        self.stop_event = threading.Event()
        self.rate_limiter = TelegramRateLimiter(config)

        # Statistics
        self.messages_sent = 0
        self.messages_failed = 0
        self.start_time = time.time()

    def start(self):
        """Start the queue worker thread."""
        if self.worker_thread and self.worker_thread.is_alive():
            return

        self.stop_event.clear()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

        self.logger.info("Telegram queue worker started")

    def stop(self):
        """Stop the queue worker thread."""
        self.stop_event.set()

        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)

        self.logger.info("Telegram queue worker stopped")

    def enqueue_message(self, message: TelegramMessage) -> bool:
        """
        Enqueue a message for sending.

        Args:
            message: Telegram message to send

        Returns:
            True if message was enqueued, False if queue is full
        """
        try:
            self.queue.put(message, timeout=1.0)
            return True
        except Exception:
            self.logger.warning("Telegram queue is full, message dropped")
            return False

    def _worker_loop(self):
        """Worker thread loop for processing messages."""
        while not self.stop_event.is_set():
            try:
                # Get message from queue
                message = self.queue.get(timeout=1.0)

                # Wait for rate limit
                wait_time = self.rate_limiter.get_wait_time()
                if wait_time > 0:
                    time.sleep(wait_time)

                # Send message
                sender = TelegramSender(self.config)
                success = sender.send_message(message)

                if success:
                    self.rate_limiter.record_message_sent()
                    self.messages_sent += 1
                else:
                    self.rate_limiter.record_failure()
                    self.messages_failed += 1

                self.queue.task_done()

            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in Telegram queue worker: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        uptime = time.time() - self.start_time

        return {
            "messages_sent": self.messages_sent,
            "messages_failed": self.messages_failed,
            "queue_size": self.queue.qsize(),
            "uptime_seconds": uptime,
            "messages_per_second": self.messages_sent / uptime if uptime > 0 else 0,
            "success_rate": (
                self.messages_sent / (self.messages_sent + self.messages_failed)
                if (self.messages_sent + self.messages_failed) > 0
                else 0
            ),
        }


class TelegramSender:
    """Handles actual Telegram API requests."""

    def __init__(self, config: TelegramConfig):
        self.config = config
        self.logger = get_logger(f"{__name__}.sender")

        # API endpoint
        self.api_url = "https://api.telegram.org/bot"

        # Session for requests
        self.session = requests.Session()
        # Set timeout on individual requests instead of session

    def send_message(self, message: TelegramMessage) -> bool:
        """
        Send a message via Telegram Bot API.

        Args:
            message: Telegram message to send

        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            # Validate configuration
            if not self._validate_config():
                return False

            # Build request payload
            payload = self._build_payload(message)

            # Make API request
            response = self._make_api_request("sendMessage", payload)

            # Handle response
            return self._handle_response(response)

        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return False

    def _validate_config(self) -> bool:
        """Validate Telegram configuration."""
        if not self.config.enabled:
            self.logger.debug("Telegram logging is disabled")
            return False

        if not self.config.bot_token:
            self.logger.error("TELEGRAM_BOT_TOKEN not configured")
            return False

        if not self.config.default_chat_id:
            self.logger.error("TELEGRAM_CHAT_ID not configured")
            return False

        # Validate bot token format
        if not self._validate_bot_token(self.config.bot_token):
            self.logger.error("Invalid bot token format")
            return False

        return True

    def _validate_bot_token(self, token: str) -> bool:
        """Validate bot token format."""
        import re

        return bool(re.match(r"^\d+:[a-zA-Z0-9_-]{35}$", token))

    def _build_payload(self, message: TelegramMessage) -> Dict[str, Any]:
        """Build API request payload."""
        payload = {
            "chat_id": message.chat_id,
            "text": message.text,
            "parse_mode": message.parse_mode,
            "disable_web_page_preview": message.disable_web_page_preview,
            "disable_notification": message.disable_notification,
        }

        # Add optional parameters
        if message.reply_to_message_id:
            payload["reply_to_message_id"] = message.reply_to_message_id

        return payload

    def _make_api_request(
        self, method: str, payload: Dict[str, Any]
    ) -> requests.Response:
        """Make API request to Telegram."""
        url = f"{self.api_url}{self.config.bot_token}/{method}"

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Auto-slopp-Telegram-Logger/1.0",
        }

        response = self.session.post(url, json=payload, headers=headers)
        return response

    def _handle_response(self, response: requests.Response) -> bool:
        """Handle API response."""
        try:
            response.raise_for_status()

            data = response.json()

            if data.get("ok"):
                self.logger.debug(
                    f"Telegram message sent successfully: {data.get('message_id')}"
                )
                return True
            else:
                error_code = data.get("error_code", "unknown")
                description = data.get("description", "unknown error")
                self.logger.error(f"Telegram API error {error_code}: {description}")
                return False

        except requests.RequestException as e:
            self.logger.error(f"Telegram API request failed: {e}")
            return False
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode Telegram API response: {e}")
            return False


class TelegramLogger:
    """Main Telegram logging integration class."""

    def __init__(self, config=None):
        self.config = config or self._load_config()
        self.logger = get_logger(f"{__name__}.telegram")

        # Initialize components
        self.sender = TelegramSender(self.config)
        self.queue = TelegramQueue(self.config)

        # Message formatting
        self.emoji_indicators = {
            LogLevel.DEBUG: "🔍",
            LogLevel.INFO: "ℹ️",
            LogLevel.WARNING: "⚠️",
            LogLevel.ERROR: "❌",
            LogLevel.CRITICAL: "🚨",
            LogLevel.SUCCESS: "✅",
        }

        # Start queue if enabled
        if self.config.enabled:
            self.queue.start()

    def log(
        self, level: str, message: str, script_name: Optional[str] = None, **kwargs
    ):
        """
        Send log message to Telegram.

        Args:
            level: Log level
            message: Log message
            script_name: Name of the script generating the log
            **kwargs: Additional metadata
        """
        if not self.config.enabled:
            return

        try:
            # Format message
            formatted_message = self._format_message(
                level, message, script_name, **kwargs
            )

            # Create Telegram message
            telegram_message = TelegramMessage(
                text=formatted_message,
                chat_id=self.config.default_chat_id,
                parse_mode=self.config.formatting.parse_mode,
                disable_web_page_preview=True,
                metadata={
                    "level": level,
                    "script_name": script_name,
                    "timestamp": datetime.now().isoformat(),
                    **kwargs,
                },
            )

            # Enqueue message
            self.queue.enqueue_message(telegram_message)

        except Exception as e:
            self.logger.error(f"Failed to enqueue Telegram message: {e}")

    def _format_message(
        self, level: str, message: str, script_name: Optional[str] = None, **kwargs
    ) -> str:
        """Format log message for Telegram."""
        lines = []

        # Add emoji indicator if enabled
        if self.config.formatting.use_emoji_indicators:
            emoji = self.emoji_indicators.get(level, "📝")
            lines.append(f"{emoji} <b>{level.upper()}</b>")

        # Add timestamp if enabled
        if self.config.formatting.include_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"🕒 <code>{timestamp}</code>")

        # Add script name if enabled and provided
        if self.config.formatting.include_script_name and script_name:
            lines.append(f"📄 <b>{script_name}</b>")

        # Add the main message
        lines.append(f"📝 {message}")

        # Add additional metadata if any
        for key, value in kwargs.items():
            if key not in ["script_name", "timestamp"]:
                lines.append(f"🔧 <b>{key}:</b> {value}")

        # Join lines
        formatted_message = "\n".join(lines)

        # Truncate if too long
        max_length = self.config.formatting.max_message_length
        if len(formatted_message) > max_length:
            truncated = formatted_message[: max_length - 20] + "\n\n... (truncated)"
            formatted_message = truncated

        return formatted_message

    def _load_config(self) -> TelegramConfig:
        """Load configuration from config system."""
        try:
            from ..config import get_config

            config = get_config()

            # Extract Telegram configuration
            telegram_config = config.telegram

            return TelegramConfig(
                enabled=telegram_config.enabled,
                bot_token=telegram_config.bot_token,
                default_chat_id=telegram_config.default_chat_id,
                api_timeout_seconds=telegram_config.api_timeout_seconds,
                connection_retries=telegram_config.connection_retries,
                rate_limiting=telegram_config.rate_limiting,
                formatting=telegram_config.formatting,
                security=telegram_config.security,
            )

        except Exception as e:
            self.logger.error(f"Failed to load Telegram config: {e}")
            return TelegramConfig()

    def stop(self):
        """Stop Telegram logging."""
        if self.queue:
            self.queue.stop()

    def get_stats(self) -> Dict[str, Any]:
        """Get Telegram logging statistics."""
        stats = {
            "enabled": self.config.enabled,
            "queue_stats": self.queue.get_stats() if self.queue else {},
        }

        return stats


# Global instance
_telegram_logger: Optional[TelegramLogger] = None


def get_telegram_logger(config=None) -> TelegramLogger:
    """Get the global Telegram logger instance."""
    global _telegram_logger
    if _telegram_logger is None:
        _telegram_logger = TelegramLogger(config)
    return _telegram_logger


# Convenience functions matching bash script interface
def send_log_to_telegram(level: str, message: str, script_name: Optional[str] = None):
    """Send log message to Telegram (bash compatibility)."""
    logger = get_telegram_logger()
    logger.log(level, message, script_name)


def telegram_log_info(message: str, script_name: Optional[str] = None):
    """Send info message to Telegram."""
    send_log_to_telegram("INFO", message, script_name)


def telegram_log_warning(message: str, script_name: Optional[str] = None):
    """Send warning message to Telegram."""
    send_log_to_telegram("WARNING", message, script_name)


def telegram_log_error(message: str, script_name: Optional[str] = None):
    """Send error message to Telegram."""
    send_log_to_telegram("ERROR", message, script_name)


def telegram_log_success(message: str, script_name: Optional[str] = None):
    """Send success message to Telegram."""
    send_log_to_telegram("SUCCESS", message, script_name)


def telegram_log_debug(message: str, script_name: Optional[str] = None):
    """Send debug message to Telegram."""
    send_log_to_telegram("DEBUG", message, script_name)


# Cleanup function
def cleanup_telegram_logger():
    """Cleanup Telegram logger resources."""
    global _telegram_logger
    if _telegram_logger:
        _telegram_logger.stop()
        _telegram_logger = None
