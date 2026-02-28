# Telegram Logging Guide

This guide provides comprehensive documentation for setting up and configuring Telegram logging in Auto-slopp. Telegram integration allows you to receive real-time log notifications directly on your Telegram client, making it easy to monitor your automation workflows remotely.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Setting Up Telegram Bot](#setting-up-telegram-bot)
3. [Configuration Options](#configuration-options)
4. [Integration with Existing Logging](#integration-with-existing-logging)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Example Use Cases](#example-use-cases)
8. [API Reference](#api-reference)

## Quick Start

### 1. Create Telegram Bot
1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow prompts to create your bot and get the bot token
4. Save your bot token for configuration

### 2. Get Chat ID
1. Start a conversation with your new bot
2. Send any message to the bot
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for `chat.id` in the response - this is your chat ID

### 3. Configure Auto-slopp
Create or update your `.env` file:

```bash
# Enable Telegram logging
AUTO_SLOPP_TELEGRAM_ENABLED=true
AUTO_SLOPP_TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
AUTO_SLOPP_TELEGRAM_CHAT_ID=123456789
```

### 4. Test Configuration
Run Auto-slopp with debug mode to verify:

```bash
auto-slopp --debug
```

You should see Telegram connection logs in the output.

## Setting Up Telegram Bot

### Creating the Bot

1. **Start with BotFather**
   - Open Telegram and search for `@BotFather`
   - Start a conversation with BotFather

2. **Create New Bot**
   ```
   /newbot
   ```
   
3. **Choose Bot Details**
   - Bot name: `My Auto-slopp Bot` (display name)
   - Bot username: `my_auto_slopp_bot` (must end with `_bot`)
   - BotFather will provide you with a token like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

4. **Important Security Settings**
   ```
   /setprivacy
   ```
   Choose "Disable" to allow your bot to read all messages in groups (optional for private use)

   ```
   /setjoingroups
   ```
   Choose "Enable" or "Disable" based on your needs

### Finding Chat ID

#### For Private Messages (Recommended)

1. Send a message to your bot (any text)
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for the chat ID in the response:
   ```json
   {
     "ok": true,
     "result": [
       {
         "update_id": 123456789,
         "message": {
           "message_id": 1,
           "from": {
             "id": 987654321,
             "is_bot": false,
             "first_name": "Your Name"
           },
           "chat": {
             "id": 987654321,
             "first_name": "Your Name",
             "type": "private"
           },
           "date": 1640995200,
           "text": "Hello bot!"
         }
       }
     ]
   }
   ```
   The `chat.id` (987654321) is your chat ID.

#### For Groups/Channels

1. Add your bot to the group or channel
2. Send a message in the chat
3. Use the same API endpoint to get updates
4. Group chat IDs are negative numbers (e.g., -123456789)
5. Channel usernames can be used directly (e.g., `@yourchannel`)

### Alternative Methods to Get Chat ID

#### Using a Bot
Many bots can help you find your chat ID:
- Search for `@userinfobot` or `@get_id_bot`
- Send them `/start` and they'll tell you your ID

#### Using Python Script
```python
import requests

BOT_TOKEN = "your_bot_token_here"
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)
print(response.json())
```

## Configuration Options

### Required Settings

| Setting | Environment Variable | Description | Example |
|---------|---------------------|-------------|---------|
| Enable Telegram | `AUTO_SLOPP_TELEGRAM_ENABLED` | Enable/disable Telegram logging | `true` |
| Bot Token | `AUTO_SLOPP_TELEGRAM_BOT_TOKEN` | Bot token from BotFather | `123456:ABC-DEF...` |
| Chat ID | `AUTO_SLOPP_TELEGRAM_CHAT_ID` | Target chat ID for messages | `123456789` |

### Optional Settings

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| API Timeout | `AUTO_SLOPP_TELEGRAM_TIMEOUT` | `30.0` | Request timeout in seconds |
| Retry Attempts | `AUTO_SLOPP_TELEGRAM_RETRY_ATTEMPTS` | `3` | Number of retry attempts for failed requests |
| Retry Delay | `AUTO_SLOPP_TELEGRAM_RETRY_DELAY` | `1.0` | Delay between retries in seconds |
| Parse Mode | `AUTO_SLOPP_TELEGRAM_PARSE_MODE` | `HTML` | Message formatting (`HTML`, `Markdown`, or empty) |
| Disable Web Preview | `AUTO_SLOPP_TELEGRAM_DISABLE_WEB_PAGE_PREVIEW` | `true` | Disable link previews in messages |
| Disable Notification | `AUTO_SLOPP_TELEGRAM_DISABLE_NOTIFICATION` | `false` | Send messages silently (no notification sound) |

### Example Configuration Files

#### Basic Configuration (.env)
```bash
# Essential settings
AUTO_SLOPP_TELEGRAM_ENABLED=true
AUTO_SLOPP_TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
AUTO_SLOPP_TELEGRAM_CHAT_ID=123456789
```

#### Advanced Configuration (.env)
```bash
# Telegram logging with custom settings
AUTO_SLOPP_TELEGRAM_ENABLED=true
AUTO_SLOPP_TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
AUTO_SLOPP_TELEGRAM_CHAT_ID=-1001234567890  # Group chat
AUTO_SLOPP_TELEGRAM_TIMEOUT=60.0
AUTO_SLOPP_TELEGRAM_RETRY_ATTEMPTS=5
AUTO_SLOPP_TELEGRAM_RETRY_DELAY=2.0
AUTO_SLOPP_TELEGRAM_PARSE_MODE=Markdown
AUTO_SLOPP_TELEGRAM_DISABLE_WEB_PAGE_PREVIEW=false
AUTO_SLOPP_TELEGRAM_DISABLE_NOTIFICATION=true
```

#### Production Configuration
```bash
# Production environment with reliability focus
AUTO_SLOPP_TELEGRAM_ENABLED=true
AUTO_SLOPP_TELEGRAM_BOT_TOKEN=prod_bot_token_here
AUTO_SLOPP_TELEGRAM_CHAT_ID=prod_alerts_channel
AUTO_SLOPP_TELEGRAM_TIMEOUT=45.0
AUTO_SLOPP_TELEGRAM_RETRY_ATTEMPTS=7
AUTO_SLOPP_TELEGRAM_RETRY_DELAY=3.0
AUTO_SLOPP_TELEGRAM_PARSE_MODE=HTML
AUTO_SLOPP_TELEGRAM_DISABLE_WEB_PAGE_PREVIEW=true
```

## Integration with Existing Logging

### Automatic Integration

When Telegram logging is enabled, Auto-slopp automatically integrates with the main logging system. By default, only WARNING level and higher log messages are sent to Telegram, while INFO and DEBUG messages appear only in console logs. This reduces noise while ensuring you receive important notifications. You don't need to modify your existing code - just configure the environment variables.

### Manual Integration

For custom applications or workers, you can manually set up Telegram logging:

```python
import logging
from auto_slopp.telegram_handler import setup_telegram_logging

# Set up logger
logger = logging.getLogger("my_custom_worker")
logger.setLevel(logging.INFO)

# Add Telegram handler
telegram_handler = setup_telegram_logging(level=logging.WARNING)
if telegram_handler:
    logger.addHandler(telegram_handler)

# Now WARNING and above messages go to Telegram
logger.info("This goes to console only")
logger.warning("This goes to console AND Telegram")
logger.error("This goes to console AND Telegram")
```

### Message Formatting

Default message format in HTML mode:
```
<b>ERROR</b> (auto_slopp.workers.MyWorker)
Message: Task execution failed with error code 500
Time: 2024-01-01 12:00:00
```

Custom formatting example:
```python
# Custom format string
custom_format = "🚨 {levelname}: {message}\n📁 {name}\n🕐 {asctime}"
telegram_handler = setup_telegram_logging(
    level=logging.ERROR,
    format_string=custom_format
)
```

### Log Level Filtering

Telegram handler respects standard Python logging levels:
- `DEBUG` (10) - Detailed debugging information
- `INFO` (20) - General information messages  
- `WARNING` (30) - Warning messages
- `ERROR` (40) - Error messages
- `CRITICAL` (50) - Critical error messages

Example: Only send ERROR and CRITICAL to Telegram:
```python
telegram_handler = setup_telegram_logging(level=logging.ERROR)
```

## Security Best Practices

### Bot Token Security

1. **Never share your bot token** - It's equivalent to a password
2. **Use environment variables** - Don't hardcode tokens in code
3. **Restrict bot access** - Only add bot to necessary chats
4. **Regular token rotation** - Consider regenerating tokens periodically

#### Example Secure Setup
```bash
# Use environment variables (recommended)
export AUTO_SLOPP_TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
export AUTO_SLOPP_TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID"

# Or in .env file (ensure .env is in .gitignore)
AUTO_SLOPP_TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
AUTO_SLOPP_TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
```

### Chat Privacy

1. **Private chats for sensitive information** - Use 1-on-1 chats instead of groups
2. **Access control** - Only add trusted users to notification groups
3. **Message deletion** - Consider implementing automatic message cleanup for sensitive data

#### Bot Privacy Settings
```
/setprivacy
```
- **Enable**: Bot only reads commands and messages that mention it
- **Disable**: Bot reads all messages in the group

### Network Security

1. **HTTPS only** - Telegram API only uses HTTPS
2. **Timeout configuration** - Set appropriate timeouts to prevent hanging
3. **Rate limiting** - Telegram has built-in rate limiting; respect retry delays

### Data Protection

1. **Avoid sensitive data** - Don't log passwords, API keys, or personal data
2. **Message size limits** - Telegram has 4096 character limit per message
3. **Log sanitization** - Consider removing or masking sensitive information

```python
# Example of sanitizing logs before sending
import re

def sanitize_message(message: str) -> str:
    """Remove sensitive information from log messages."""
    # Remove potential passwords
    message = re.sub(r'(password["\s]*[:=]["\s]*)([^"\s]+)', r'\1***', message, flags=re.IGNORECASE)
    # Remove API keys
    message = re.sub(r'(api[_-]?key["\s]*[:=]["\s]*)([^"\s]+)', r'\1***', message, flags=re.IGNORECASE)
    return message
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Messages Not Sending

**Symptoms:** No messages received, no error logs

**Possible Causes:**
- Bot token or chat ID incorrect
- Telegram logging not enabled
- Network connectivity issues

**Solutions:**
1. Verify bot token format: `123456:ABC-DEF...`
2. Check chat ID is correct (private chat: positive, group: negative)
3. Ensure `AUTO_SLOPP_TELEGRAM_ENABLED=true`
4. Test connectivity:
   ```bash
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
   ```

#### 2. Authentication Errors

**Symptoms:** 401 Unauthorized errors in logs

**Solutions:**
1. Regenerate bot token from BotFather:
   ```
   /revoke
   ```
2. Update configuration with new token
3. Verify bot is not deleted or disabled

#### 3. Chat Not Found Errors

**Symptoms:** 404 Chat not found errors

**Solutions:**
1. Verify chat ID format and value
2. Ensure bot is member of the group/channel
3. For groups, check bot has permission to send messages

#### 4. Rate Limiting

**Symptoms:** 429 Too Many Requests errors

**Solutions:**
1. Increase retry delays:
   ```bash
   AUTO_SLOPP_TELEGRAM_RETRY_DELAY=5.0
   AUTO_SLOPP_TELEGRAM_RETRY_ATTEMPTS=3
   ```
2. Reduce log frequency
3. Use log level filtering to send fewer messages

#### 5. Message Format Issues

**Symptoms:** Messages not displaying correctly

**Solutions:**
1. Check parse mode setting:
   ```bash
   AUTO_SLOPP_TELEGRAM_PARSE_MODE=HTML  # or Markdown
   ```
2. Verify HTML/Markdown syntax in messages
3. For plain text, use empty parse mode

### Debug Mode

Enable comprehensive logging for troubleshooting:

```bash
# Method 1: Command line
auto-slopp --debug

# Method 2: Environment variable
AUTO_SLOPP_DEBUG=true auto-slopp

# Method 3: .env file
AUTO_SLOPP_DEBUG=true
```

Debug mode provides:
- Detailed Telegram API error messages
- Network request/response information
- Configuration loading details
- Handler lifecycle events

### Testing Telegram Connection

#### Python Test Script
```python
import asyncio
import logging
from auto_slopp.telegram_handler import TelegramHandler
from settings.main import settings

async def test_telegram():
    """Test Telegram connection and message sending."""
    try:
        handler = TelegramHandler()
        handler.setFormatter(logging.Formatter("Test message: %(message)s"))
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Telegram test successful! 🎉",
            args=(),
            exc_info=None,
        )
        
        await handler._send_message_async(record)
        print("✅ Telegram test successful")
        
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
    finally:
        if 'handler' in locals():
            handler.close()

if __name__ == "__main__":
    asyncio.run(test_telegram())
```

#### API Testing with curl
```bash
# Test bot token validity
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe

# Test sending a message
curl -X POST \
  https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage \
  -H 'Content-Type: application/json' \
  -d '{
    "chat_id": "<YOUR_CHAT_ID>",
    "text": "Test message from curl",
    "parse_mode": "HTML"
  }'
```

### Getting Help

1. **Check logs first** - Enable debug mode for detailed information
2. **Verify configuration** - Double-check all environment variables
3. **Test API directly** - Use curl or browser to test Telegram API
4. **Check Telegram status** - Verify Telegram services are operational
5. **Review rate limits** - Ensure you're not exceeding Telegram's limits

## Example Use Cases

### 1. Production Monitoring

Monitor critical production processes and get immediate alerts:

```bash
# Production configuration
AUTO_SLOPP_TELEGRAM_ENABLED=true
AUTO_SLOPP_TELEGRAM_BOT_TOKEN=prod_bot_token
AUTO_SLOPP_TELEGRAM_CHAT_ID=production_alerts
AUTO_SLOPP_TELEGRAM_PARSE_MODE=HTML

# Only send critical errors
logger.setLevel(logging.CRITICAL)
```

**Sample Messages:**
```
🚨 CRITICAL (auto_slopp.production.data_processor)
Message: Database connection failed after 5 retries
Time: 2024-01-01 15:30:45
```

### 2. Development Notifications

Get notified about build status and deployment events:

```python
# Development notification setup
dev_handler = setup_telegram_logging(
    level=logging.INFO,
    format_string="🔧 {levelname}: {message}\n🏗️ Build: {build_id}"
)

# Usage examples
logger.info("Build #1234 completed successfully")
logger.warning("Build #1235: Test suite has 3 failures")
logger.error("Deploy to staging failed: Container timeout")
```

### 3. Scheduled Task Monitoring

Monitor automated tasks and report completion status:

```python
class ScheduledTaskMonitor:
    def __init__(self):
        self.logger = logging.getLogger("scheduled_tasks")
        self.telegram_handler = setup_telegram_logging(
            level=logging.INFO,
            format_string="📅 Task Update\n\n<b>{levelname}</b>\nTask: {task_name}\nStatus: {message}\nTime: {asctime}"
        )
        
    def task_completed(self, task_name: str, duration: float):
        self.logger.info(f"{task_name} completed in {duration:.2f}s", extra={"task_name": task_name})
        
    def task_failed(self, task_name: str, error: str):
        self.logger.error(f"{task_name} failed: {error}", extra={"task_name": task_name})
```

### 4. Multi-Environment Notifications

Different notification channels for different environments:

```python
# Environment-specific configuration
if os.getenv("ENVIRONMENT") == "production":
    # Critical errors to production ops channel
    prod_handler = setup_telegram_logging(
        level=logging.ERROR,
        chat_id="-1001234567890",  # Production ops group
        format_string="🚨 PRODUCTION ALERT: {message}"
    )
elif os.getenv("ENVIRONMENT") == "staging":
    # All messages to dev team
    staging_handler = setup_telegram_logging(
        level=logging.INFO,
        chat_id="123456789",  # Dev team chat
        format_string="🧪 Staging: {levelname} - {message}"
    )
```

### 5. Health Check Notifications

Regular system health status updates:

```python
async def health_check_notifier():
    """Send periodic health status updates."""
    while True:
        try:
            # Check system health
            cpu_usage = get_cpu_usage()
            memory_usage = get_memory_usage()
            disk_space = get_disk_space()
            
            # Create health message
            health_status = f"🏥 System Health\n\n"
            health_status += f"CPU: {cpu_usage}%\n"
            health_status += f"Memory: {memory_usage}%\n"
            health_status += f"Disk: {disk_space}%\n"
            
            # Send to health monitoring channel
            logger.info(health_status)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            
        await asyncio.sleep(3600)  # Every hour
```

## API Reference

### TelegramHandler Class

The main class for handling Telegram logging.

#### Constructor
```python
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
)
```

**Parameters:**
- `bot_token`: Telegram bot token (overrides settings)
- `chat_id`: Target chat ID (overrides settings)
- `timeout`: HTTP request timeout in seconds
- `retry_attempts`: Number of retry attempts for failed requests
- `retry_delay`: Delay between retry attempts in seconds
- `parse_mode`: Message format (`HTML`, `Markdown`, or `""`)
- `disable_web_page_preview`: Disable link previews in messages
- `disable_notification`: Send messages silently

#### Methods

##### emit(record: LogRecord)
Standard logging handler method to send log records to Telegram.

##### _send_message_async(record: LogRecord)
Async method to send a formatted message to Telegram.

##### _escape_html(text: str) -> str
Escapes HTML special characters for safe HTML parse mode usage.

##### close()
Closes the HTTP client and cleans up resources.

### setup_telegram_logging Function

Convenience function to create and configure a Telegram handler.

#### Signature
```python
def setup_telegram_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    **handler_kwargs
) -> Optional[logging.Handler]:
```

**Parameters:**
- `level`: Logging level for the handler
- `format_string`: Custom message format string
- `**handler_kwargs`: Additional arguments for TelegramHandler

**Returns:**
- Configured TelegramHandler or None if Telegram logging is disabled

#### Example Usage
```python
# Basic setup
handler = setup_telegram_logging()

# Custom setup
handler = setup_telegram_logging(
    level=logging.WARNING,
    format_string="⚠️ {levelname}: {message}",
    timeout=60.0,
    retry_attempts=5
)

# With custom credentials
handler = setup_telegram_logging(
    bot_token="custom_token",
    chat_id="custom_chat_id"
)
```

### Settings Class

Configuration settings for Telegram integration (partial view):

```python
class Settings(BaseSettings):
    # Telegram settings
    telegram_enabled: bool = Field(default=False, description="Enable Telegram logging")
    telegram_bot_token: Optional[str] = Field(default=None, description="Bot token")
    telegram_chat_id: Optional[str] = Field(default=None, description="Chat ID")
    telegram_timeout: float = Field(default=30.0, description="Request timeout")
    telegram_retry_attempts: int = Field(default=3, description="Retry attempts")
    telegram_retry_delay: float = Field(default=1.0, description="Retry delay")
    telegram_parse_mode: str = Field(default="HTML", description="Parse mode")
    telegram_disable_web_page_preview: bool = Field(default=True)
    telegram_disable_notification: bool = Field(default=False)
```

### Error Handling

The Telegram handler implements comprehensive error handling:

1. **Graceful Degradation** - Logging errors don't crash the application
2. **Automatic Retries** - Configurable retry logic for transient failures
3. **Rate Limiting** - Respects Telegram's rate limiting with `429` response handling
4. **Network Errors** - Handles timeouts, connection errors, and DNS failures
5. **Authentication Errors** - Detects and reports invalid tokens/permissions

### Message Limits

- **Maximum message length**: 4096 characters (Telegram API limit)
- **Rate limits**: Approximately 30 messages per second per bot
- **File size limits**: Not applicable for text messages
- **Unicode support**: Full Unicode emoji and character support

For messages longer than 4096 characters, consider implementing message splitting:

```python
def split_message(message: str, max_length: int = 4096) -> list[str]:
    """Split long messages into multiple parts."""
    if len(message) <= max_length:
        return [message]
    
    parts = []
    current_part = ""
    
    for line in message.split('\n'):
        if len(current_part) + len(line) + 1 > max_length:
            if current_part:
                parts.append(current_part)
            current_part = line
        else:
            if current_part:
                current_part += '\n' + line
            else:
                current_part = line
    
    if current_part:
        parts.append(current_part)
    
    return parts
```

---

For additional help or questions about Telegram logging, please refer to the main [README.md](../README.md) or open an issue in the project repository.