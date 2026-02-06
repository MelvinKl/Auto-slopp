# Telegram Logging Setup Guide

## Overview

The Auto-slopp system includes comprehensive Telegram logging integration that allows you to receive real-time notifications directly in Telegram. This guide covers everything from bot creation to advanced configuration and troubleshooting.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Bot Setup](#bot-setup)
3. [Configuration](#configuration)
4. [Security Best Practices](#security-best-practices)
5. [API Reference](#api-reference)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)
8. [Integration](#integration)

## Quick Start

### Prerequisites
- Python 3.11+ with uv package manager
- Auto-slopp system installed
- Telegram account

### 5-Minute Setup

1. **Create a Telegram Bot** (see [Bot Setup](#bot-setup))
2. **Enable Telegram Logging** in your `config.yaml`:
   ```yaml
   telegram:
     enabled: true
     bot_token: "YOUR_BOT_TOKEN_HERE"
     default_chat_id: "YOUR_CHAT_ID_HERE"
   ```
3. **Test the Integration**:
   ```python
   from auto_slopp.telegram import telegram_log_info
   
   telegram_log_info("Hello from Auto-slopp!", "test_script")
   ```

That's it! You'll receive notifications in your Telegram chat.

## Bot Setup

### Step 1: Create a Telegram Bot

1. **Open Telegram** and search for **@BotFather**
2. **Start a chat** with BotFather and send `/start`
3. **Create a new bot** by sending `/newbot`
4. **Provide bot details**:
   - Bot name: `Auto-slopp Logger` (or your preferred name)
   - Bot username: `auto_slopp_logger_bot` (must be unique and end in `_bot`)
5. **Save your bot token** - it looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### Step 2: Get Your Chat ID

1. **Start a chat** with your new bot
2. **Send any message** to the bot
3. **Visit** `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. **Find your chat ID** in the response under `chat.id`

### Step 3: Test the Bot

```bash
# Test using curl (replace YOUR_BOT_TOKEN and YOUR_CHAT_ID)
curl -X POST \
  "https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "YOUR_CHAT_ID",
    "text": "Hello from Auto-slopp! 🚀"
  }'
```

## Configuration

### Basic Configuration

Add this to your `config.yaml`:

```yaml
# Telegram Logging Configuration
telegram:
  enabled: true
  bot_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
  default_chat_id: "7649674603"
  api_timeout_seconds: 10
  connection_retries: 3
  
  # Rate Limiting
  rate_limiting:
    messages_per_second: 5
    burst_size: 20
    rate_limit_window_seconds: 60
    backoff_multiplier: 2.0
    max_backoff_seconds: 30
  
  # Message Formatting
  formatting:
    parse_mode: "HTML"
    max_message_length: 4000
    include_timestamp: true
    include_log_level: true
    include_script_name: true
    use_emoji_indicators: true
  
  # Security Settings
  security:
    validate_bot_token: true
    encrypt_config_storage: true
    audit_token_access: true
    hide_tokens_in_logs: true
    require_https: true
```

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable/disable Telegram logging |
| `bot_token` | string | `""` | Your bot's API token |
| `default_chat_id` | string | `""` | Default chat ID for messages |
| `api_timeout_seconds` | integer | `10` | API request timeout |
| `connection_retries` | integer | `3` | Number of retry attempts |

#### Rate Limiting Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `messages_per_second` | integer | `5` | Maximum messages per second |
| `burst_size` | integer | `20` | Maximum burst messages |
| `rate_limit_window_seconds` | integer | `60` | Rate limit window size |
| `backoff_multiplier` | float | `2.0` | Exponential backoff multiplier |
| `max_backoff_seconds` | integer | `30` | Maximum backoff time |

#### Formatting Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `parse_mode` | string | `"HTML"` | Message parsing mode (`HTML`, `Markdown`) |
| `max_message_length` | integer | `4000` | Maximum message length |
| `include_timestamp` | boolean | `true` | Include timestamp in messages |
| `include_log_level` | boolean | `true` | Include log level in messages |
| `include_script_name` | boolean | `true` | Include script name in messages |
| `use_emoji_indicators` | boolean | `true` | Use emoji indicators for log levels |

#### Security Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `validate_bot_token` | boolean | `true` | Validate bot token format |
| `encrypt_config_storage` | boolean | `true` | Encrypt token in config files |
| `audit_token_access` | boolean | `true` | Log token access attempts |
| `hide_tokens_in_logs` | boolean | `true` | Hide tokens in log files |
| `require_https` | boolean | `true` | Require HTTPS for API calls |

## Security Best Practices

### Bot Token Security

1. **Never expose your bot token** in public repositories or logs
2. **Use environment variables** for sensitive configurations:
   ```bash
   export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
   ```
3. **Limit bot permissions** - Only grant necessary permissions
4. **Use private bots** for sensitive applications

### Chat Security

1. **Create a private group** for notifications instead of using personal chats
2. **Restrict bot access** to only authorized users
3. **Enable two-factor authentication** on your Telegram account
4. **Regularly rotate bot tokens** if compromised

### Network Security

1. **Use HTTPS** for all API calls (enforced by default)
2. **Validate webhook URLs** if using webhooks
3. **Monitor API usage** for unusual activity
4. **Implement rate limiting** (built-in to the system)

## API Reference

### TelegramLogger Class

```python
class TelegramLogger:
    """Main Telegram logging integration class."""
    
    def __init__(self, config=None):
        """Initialize Telegram logger with optional config."""
    
    def log(self, level: str, message: str, script_name: Optional[str] = None, **kwargs):
        """Send log message to Telegram."""
    
    def stop(self):
        """Stop Telegram logging and cleanup resources."""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Telegram logging statistics."""
```

### Convenience Functions

```python
# Send messages directly
send_log_to_telegram(level: str, message: str, script_name: Optional[str] = None)

# Level-specific functions
telegram_log_info(message: str, script_name: Optional[str] = None)
telegram_log_warning(message: str, script_name: Optional[str] = None)
telegram_log_error(message: str, script_name: Optional[str] = None)
telegram_log_success(message: str, script_name: Optional[str] = None)
telegram_log_debug(message: str, script_name: Optional[str] = None)

# Get logger instance
get_telegram_logger(config=None) -> TelegramLogger

# Cleanup resources
cleanup_telegram_logger()
```

### Configuration Classes

```python
@dataclass
class TelegramConfig:
    """Configuration for Telegram logging."""
    enabled: bool
    bot_token: str
    default_chat_id: str
    api_timeout_seconds: int
    connection_retries: int
    rate_limiting: TelegramRateLimitingConfig
    formatting: TelegramFormattingConfig
    security: TelegramSecurityConfig
```

## Examples

### Basic Usage

```python
from auto_slopp.telegram import telegram_log_info

# Send a simple info message
telegram_log_info("System started successfully", "main.py")

# Send an error message
telegram_log_error("Failed to connect to database", "db_manager.py")
```

### Advanced Usage

```python
from auto_slopp.telegram import get_telegram_logger

# Get logger instance
logger = get_telegram_logger()

# Send message with metadata
logger.log(
    level="INFO",
    message="Deployment completed",
    script_name="deploy.sh",
    deployment_id="deploy-123",
    duration="45s",
    status="success"
)
```

### Integration with Existing Logging

```python
from auto_slopp.logging import get_logger
from auto_slopp.telegram import telegram_log_info

# Get standard logger
logger = get_logger()

# Log to both file and Telegram
logger.info("Processing user request")
telegram_log_info("Processing user request", "api_handler.py")
```

### Custom Message Formatting

```python
from auto_slopp.telegram import TelegramLogger, TelegramConfig

# Custom configuration
config = TelegramConfig(
    enabled=True,
    bot_token="YOUR_TOKEN",
    default_chat_id="YOUR_CHAT_ID",
    formatting=TelegramFormattingConfig(
        parse_mode="Markdown",
        use_emoji_indicators=False,
        include_timestamp=False
    )
)

# Create logger with custom config
logger = TelegramLogger(config)
logger.log("INFO", "Custom formatted message")
```

## Troubleshooting

### Common Issues

#### Bot Not Responding

**Problem**: Messages aren't being delivered to Telegram.

**Solutions**:
1. **Check bot token**: Ensure it's correct and not expired
2. **Verify chat ID**: Make sure you're using the right chat ID
3. **Test API directly**: Use curl to test the API
4. **Check logs**: Look for error messages in the logs

```bash
# Test API directly
curl -X POST \
  "https://api.telegram.org/botYOUR_TOKEN/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "YOUR_CHAT_ID", "text": "Test message"}'
```

#### Rate Limiting Issues

**Problem**: Messages are being delayed or dropped.

**Solutions**:
1. **Check rate limits**: Telegram limits messages per second
2. **Adjust configuration**: Increase `messages_per_second` if needed
3. **Monitor queue stats**: Check if the queue is full
4. **Use burst mode**: Configure appropriate burst size

```python
# Check queue statistics
logger = get_telegram_logger()
stats = logger.get_stats()
print(f"Queue size: {stats['queue_stats']['queue_size']}")
print(f"Success rate: {stats['queue_stats']['success_rate']:.2%}")
```

#### Configuration Errors

**Problem**: Configuration validation fails.

**Solutions**:
1. **Validate YAML**: Check YAML syntax with online validator
2. **Check field types**: Ensure all fields have correct types
3. **Verify nested structures**: Rate limiting and formatting must be nested correctly
4. **Check required fields**: `bot_token` and `default_chat_id` are required

#### Authentication Issues

**Problem**: "Unauthorized" errors from Telegram API.

**Solutions**:
1. **Verify bot token**: Check if token is valid and not revoked
2. **Check bot permissions**: Ensure bot has message sending permission
3. **Validate chat access**: Make sure bot can access the target chat
4. **Check bot status**: Ensure bot is not blocked or restricted

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug in config
telegram_config = TelegramConfig(
    enabled=True,
    # ... other config
)

# Get detailed logs
logger = get_telegram_logger(telegram_config)
logger.get_stats()  # This will show detailed statistics
```

### Performance Issues

**Problem**: Telegram logging is slowing down the application.

**Solutions**:
1. **Use async queue**: Messages are queued and sent asynchronously
2. **Adjust rate limits**: Optimize `messages_per_second` for your use case
3. **Monitor queue size**: Ensure queue isn't backing up
4. **Use filtering**: Only send important log levels to Telegram

```python
# Monitor performance
stats = logger.get_stats()
if stats['queue_stats']['queue_size'] > 100:
    logger.warning("Telegram queue backing up, consider filtering messages")
```

## Integration

### With Existing Logging System

The Telegram logger integrates seamlessly with the existing Auto-slopp logging system:

```python
from auto_slopp.logging import get_logger
from auto_slopp.telegram import telegram_log_info

# Standard logging (goes to file)
logger = get_logger()
logger.info("This goes to log file")

# Telegram logging (goes to Telegram)
telegram_log_info("This goes to Telegram")

# Both (recommended for important messages)
logger.info("Important event")
telegram_log_info("Important event")
```

### Environment Variables

You can use environment variables for configuration:

```bash
# Enable Telegram logging
export TELEGRAM_ENABLED=true

# Set bot token
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"

# Set chat ID
export TELEGRAM_CHAT_ID="7649674603"

# Set log level filtering
export TELEGRAM_LOG_LEVELS="ERROR,WARNING,SUCCESS"
```

### Docker Integration

For Docker deployments, use environment variables or config maps:

```yaml
# docker-compose.yml
services:
  auto-slopp:
    environment:
      - TELEGRAM_ENABLED=true
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
    volumes:
      - ./config.yaml:/app/config.yaml
```

### Monitoring and Alerting

Monitor Telegram logging health:

```python
def check_telegram_health():
    """Check Telegram logging health status."""
    logger = get_telegram_logger()
    stats = logger.get_stats()
    
    # Check if enabled
    if not stats['enabled']:
        return "disabled"
    
    # Check success rate
    success_rate = stats['queue_stats']['success_rate']
    if success_rate < 0.9:
        return f"low_success_rate_{success_rate:.2f}"
    
    # Check queue size
    queue_size = stats['queue_stats']['queue_size']
    if queue_size > 50:
        return f"high_queue_size_{queue_size}"
    
    return "healthy"

# Health check
health_status = check_telegram_health()
print(f"Telegram logging health: {health_status}")
```

## Log Samples

### Info Message
```
ℹ️ INFO
🕒 2024-02-06 15:30:45
📄 main.py
📝 System started successfully
```

### Error Message
```
❌ ERROR
🕒 2024-02-06 15:31:02
📄 database.py
📝 Failed to connect to database
🔧 error: Connection timeout
```

### Success Message
```
✅ SUCCESS
🕒 2024-02-06 15:32:15
📄 deploy.sh
📝 Deployment completed
🔧 deployment_id: deploy-123
🔧 duration: 45s
🔧 status: success
```

### Warning Message
```
⚠️ WARNING
🕒 2024-02-06 15:33:20
📄 api_handler.py
📝 High memory usage detected
🔧 memory_usage: 85%
🔧 threshold: 80%
```

## Support

For additional support:

1. **Check the logs**: Look for detailed error messages
2. **Test the API**: Use curl to test Telegram API directly
3. **Review configuration**: Ensure all required fields are set
4. **Monitor performance**: Check queue statistics and success rates

For bug reports or feature requests, please create an issue in the Auto-slopp repository with:
- Detailed description of the problem
- Configuration used
- Error messages or logs
- Steps to reproduce the issue

---

*This guide covers Auto-slopp Telegram logging version 1.0. For the latest updates and additional features, please check the project documentation.*