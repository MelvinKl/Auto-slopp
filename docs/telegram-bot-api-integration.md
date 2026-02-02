# Telegram Bot API Integration Requirements

This document provides comprehensive requirements and guidelines for integrating Telegram Bot API for log output in the Auto-slopp project.

## 1. Required Telegram Bot API Endpoints

### Core Message Endpoints
- **sendMessage**: `https://api.telegram.org/bot<token>/sendMessage`
  - Primary endpoint for sending text messages and logs
  - Supports HTML/Markdown formatting
  - Required parameters: `chat_id`, `text`
  - Optional parameters: `parse_mode`, `disable_web_page_preview`, `disable_notification`

### Additional Useful Endpoints
- **sendPhoto**: `https://api.telegram.org/bot<token>/sendPhoto`
  - For sending log screenshots or visual data
- **sendDocument**: `https://api.telegram.org/bot<token>/sendDocument`
  - For sending log files as attachments

## 2. Authentication Methods

### Bot Token Authentication
- **Token Format**: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
- **Retrieval**: Obtain from @BotFather on Telegram
- **Method**: Include token in URL as `bot<token>`
- **Example**: `https://api.telegram.org/bot1234567890:ABCdefGHIjklMNOpqrsTUVwxyz/sendMessage`

### Required Environment Variables
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=@channelname # or numeric chat ID
```

## 3. Message Format and Size Limitations

### Message Size Limits
- **Maximum Text Length**: 4096 characters per message
- **Recommended Safe Limit**: 4000 characters (to account for formatting overhead)
- **Caption Length**: 1024 characters for media attachments

### Message Format Support
- **Plain Text**: Default format
- **HTML Formatting**: `<b>bold</b>`, `<i>italic</i>`, `<code>code</code>`, `<pre>pre</pre>`
- **Markdown**: `*bold*`, `_italic_`, `` `code` ``, ```pre```
- **Parse Mode Parameter**: `parse_mode=HTML` or `parse_mode=Markdown`

### Message Splitting Strategy
```python
# Split large messages into chunks
max_length = 4000
if len(message) > max_length:
    chunks = []
    current_chunk = ""
    for line in message.splitlines(keepends=True):
        if len(current_chunk + line) > max_length:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk += line
    if current_chunk:
        chunks.append(current_chunk)
```

## 4. Rate Limiting and Best Practices

### Rate Limiting Rules
- **General Limit**: ~30 messages per second to the same chat
- **Broadcast Limit**: ~20 messages per second to different chats
- **Burst Limit**: Up to 100 messages, then throttling applies
- **Error Response**: HTTP 429 with `retry_after` parameter

### Rate Limit Response Format
```json
{
  "ok": false,
  "error_code": 429,
  "description": "Too Many Requests: retry after 3",
  "parameters": {
    "retry_after": 3
  }
}
```

### Best Practices for Rate Limiting
1. **Implement Exponential Backoff**: Use `retry_after` value when available
2. **Queue Messages**: Implement message queuing for high-volume logging
3. **Batch Operations**: Group log messages when possible
4. **Rate Limiting Logic**:
   ```python
   import time
   import random
   
   async def send_with_retry(bot, chat_id, text, max_retries=3):
       for attempt in range(max_retries):
           try:
               await bot.send_message(chat_id, text)
               return True
           except Exception as e:
               if e.error_code == 429:
                   retry_after = e.parameters.get('retry_after', 1)
                   await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
               elif attempt == max_retries - 1:
                   raise
               else:
                   await asyncio.sleep(2 ** attempt)  # Exponential backoff
       return False
   ```

## 5. Error Handling and Retry Mechanisms

### Common Error Codes
- **400 (Bad Request)**: Invalid parameters, malformed request
- **401 (Unauthorized)**: Invalid bot token
- **403 (Forbidden)**: Bot blocked by user, no permissions
- **404 (Not Found)**: Invalid chat ID
- **409 (Conflict)**: Bot token conflict (multiple instances)
- **429 (Too Many Requests)**: Rate limit exceeded
- **500+ (Server Errors)**: Telegram server issues

### Retry Strategy
1. **Immediate Retry**: For transient network errors
2. **Delayed Retry**: For rate limiting (429), use `retry_after`
3. **Exponential Backoff**: For server errors (5xx)
4. **Max Retries**: 3-5 attempts before giving up
5. **Dead Letter Queue**: Store failed messages for later retry

### Error Handling Implementation
```python
import logging
from typing import Optional

class TelegramErrorHandler:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
    
    async def send_with_error_handling(self, bot, chat_id: str, message: str) -> bool:
        for attempt in range(self.max_retries):
            try:
                await bot.send_message(chat_id=chat_id, text=message)
                return True
            except Exception as e:
                error_code = getattr(e, 'error_code', None)
                
                if error_code == 429:
                    # Rate limit error
                    retry_after = getattr(e, 'parameters', {}).get('retry_after', 1)
                    self.logger.warning(f"Rate limited, retrying after {retry_after}s")
                    await asyncio.sleep(retry_after)
                elif error_code in [400, 401, 403, 404]:
                    # Client errors - don't retry
                    self.logger.error(f"Client error {error_code}: {e}")
                    return False
                elif error_code and error_code >= 500:
                    # Server errors - retry with exponential backoff
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Server error {error_code}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    # Network or other errors
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Network error, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
        
        self.logger.error(f"Failed to send message after {self.max_retries} attempts")
        return False
```

## 6. Security Considerations for Bot Token Management

### Token Security Requirements
1. **Environment Variables**: Store tokens in environment variables, not in code
2. **File Permissions**: If stored in files, use 600 permissions
3. **No Hardcoding**: Never commit tokens to version control
4. **Access Control**: Restrict access to token to necessary processes only
5. **Token Rotation**: Implement periodic token rotation if possible

### Secure Storage Methods
```bash
# Environment variable (recommended)
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# File with restricted permissions
echo "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz" > ~/.telegram_token
chmod 600 ~/.telegram_token
```

### Configuration Examples
```yaml
# config.yaml
telegram:
  bot_token: ${TELEGRAM_BOT_TOKEN}  # Environment variable
  chat_id: "@your_channel"
  enabled: true
  rate_limit:
    messages_per_second: 10
    burst_size: 50
```

### Additional Security Measures
1. **Bot Privacy Settings**: Configure bot privacy via @BotFather
2. **Chat Validation**: Validate chat IDs before sending
3. **Input Sanitization**: Sanitize user inputs to prevent injection
4. **HTTPS Only**: Always use HTTPS endpoints
5. **Audit Logging**: Log bot usage for security monitoring

## 7. Implementation Recommendations

### Integration Architecture
```
Application Logs → Message Queue → Telegram Bot API → Chat/Channel
     ↓              ↓                    ↓              ↓
  Log Format    Rate Limiting      Error Handling    Delivery
```

### Key Components
1. **Message Formatter**: Convert logs to Telegram-friendly format
2. **Rate Limiter**: Control message sending rate
3. **Error Handler**: Manage retries and failures
4. **Configuration Manager**: Secure token and settings management
5. **Logger Interface**: Standardized logging interface

### Configuration Schema
```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "${TELEGRAM_BOT_TOKEN}",
    "default_chat_id": "@logs",
    "rate_limiting": {
      "messages_per_second": 5,
      "burst_size": 20
    },
    "formatting": {
      "parse_mode": "HTML",
      "max_message_length": 4000,
      "include_timestamp": true,
      "include_log_level": true
    },
    "retry": {
      "max_attempts": 3,
      "base_delay": 1.0,
      "max_delay": 30.0
    }
  }
}
```

## 8. Testing Requirements

### Unit Tests
- Token validation and secure storage
- Message formatting and size limits
- Error handling for various HTTP codes
- Rate limiting behavior

### Integration Tests
- End-to-end message delivery
- Rate limiting with real Telegram API
- Error recovery and retry mechanisms
- Large message splitting

### Load Tests
- High-volume message sending
- Concurrent access scenarios
- Rate limiting under load
- Memory usage and performance

## 9. Monitoring and Alerting

### Metrics to Track
- Message success/failure rates
- Rate limiting occurrences
- API response times
- Error types and frequencies

### Alerting Triggers
- High error rates (>5%)
- Prolonged rate limiting
- Authentication failures
- Token expiration warnings

This document provides the foundation for implementing robust and secure Telegram Bot API integration for log output in the Auto-slopp project.