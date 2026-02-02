# Enhanced Telegram Logging Formatter Documentation

## Overview

The enhanced Telegram logging formatter provides comprehensive message formatting capabilities specifically designed for Telegram's chat interface. It transforms raw log messages into well-structured, readable, and informative Telegram messages with proper formatting, highlighting, and context.

## Key Features

### 1. Message Type Detection & Formatting
- **Operation Messages**: `⚙️ Started processing data`
- **Config Messages**: `⚙️ Updated configuration settings`
- **Network Messages**: `🌐 HTTP request completed`
- **Filesystem Messages**: `📁 File created successfully`
- **Security Messages**: `🔒 Authentication failed`
- **Performance Messages**: `📊 Performance metric detected`

### 2. Log Level Indicators
- **CRITICAL**: 🚨 (Red alert)
- **ERROR**: 🔴 (Red circle)
- **WARNING**: 🟡 (Yellow circle)
- **SUCCESS**: 🟢 (Green circle)
- **INFO**: 🔵 (Blue circle)
- **DEBUG**: ⚪ (White circle)
- **TRACE**: 🔍 (Magnifying glass)

### 3. Structured Data Formatting
- **JSON Detection**: Automatically detects JSON in messages
- **Code Blocks**: Formats JSON data in HTML `<pre><code>` blocks
- **Key-Value Extraction**: Converts JSON to readable key-value pairs
- **Embedded JSON**: Handles JSON embedded within regular messages

### 4. Error Message Highlighting
- **Error Patterns**: Highlights common error indicators (Error, Failed, Exception)
- **File Paths**: Formats file paths in code tags (`<code>/path/to/file</code>`)
- **Line Numbers**: Highlights script line numbers (`<code>script.sh:123</code>`)
- **Exit Codes**: Emphasizes exit codes and status information

### 5. Message Sanitization
- **Password Redaction**: `password=secret` → `password=***REDACTED***`
- **Token Redaction**: Long alphanumeric strings → `***REDACTED***`
- **Email Protection**: `user@example.com` → `***EMAIL***`
- **IP Masking**: Optional IP address redaction

### 6. Context Information
- **Script Name**: Source script identification
- **Process ID**: `🔢 PID: 12345`
- **User & Host**: `👤 user@hostname`
- **Working Directory**: `📂 /current/working/directory`
- **Additional Context**: Custom context information

### 7. Message Truncation
- **Size Limits**: Respects Telegram's 4096 character limit
- **Smart Truncation**: Preserves word boundaries when possible
- **Truncation Indicators**: Adds `...` to truncated messages
- **Configurable Limits**: Adjustable maximum message length

### 8. Advanced Filtering
- **Log Level Thresholds**: `TELEGRAM_FILTERS_MIN_LEVEL=ERROR`
- **Explicit Level Lists**: `TELEGRAM_FILTERS_LOG_LEVELS=ERROR,WARNING,SUCCESS`
- **Script Filtering**: Include/exclude specific scripts
- **Content Patterns**: Include/exclude message patterns
- **Time Windows**: Limit messages to specific hours
- **Quiet Hours**: Only allow critical messages during quiet periods

## Configuration Options

### Basic Settings
```bash
TELEGRAM_ENABLED="true"                    # Enable Telegram logging
TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."     # Bot token (required)
TELEGRAM_CHAT_ID="-1001234567890"          # Chat ID (required)
```

### Formatting Options
```bash
TELEGRAM_FORMATTING_INCLUDE_TIMESTAMP="true"
TELEGRAM_FORMATTING_INCLUDE_LOG_LEVEL="true"
TELEGRAM_FORMATTING_INCLUDE_SCRIPT_NAME="true"
TELEGRAM_FORMATTING_INCLUDE_CONTEXT="true"
TELEGRAM_FORMATTING_USE_EMOJI_INDICATORS="true"
TELEGRAM_FORMATTING_PARSE_MODE="HTML"
TELEGRAM_FORMATTING_ENABLE_STRUCTURED="true"
TELEGRAM_FORMATTING_ENABLE_ERROR_HIGHLIGHTING="true"
```

### Filtering Options
```bash
TELEGRAM_FILTERS_MIN_LEVEL="ERROR"
TELEGRAM_FILTERS_LOG_LEVELS="ERROR,WARNING,SUCCESS"
TELEGRAM_FILTERS_SCRIPTS="planner,implementer"
TELEGRAM_FILTERS_EXCLUDE_SCRIPTS="debug_script"
TELEGRAM_FILTERS_INCLUDE_PATTERNS="critical,urgent"
TELEGRAM_FILTERS_EXCLUDE_PATTERNS="test,debug"
TELEGRAM_FILTERS_TIME_WINDOW="9-17"
TELEGRAM_FILTERS_QUIET_HOURS="22-7"
```

### Security Options
```bash
TELEGRAM_ENABLE_MESSAGE_SANITIZATION="true"
TELEGRAM_REDACT_IPS="false"
```

### Performance Options
```bash
TELEGRAM_SEND_ASYNC="true"
TELEGRAM_MAX_MESSAGE_LENGTH="4000"
TELEGRAM_MAX_RETRIES="3"
TELEGRAM_API_TIMEOUT_SECONDS="10"
```

## Usage Examples

### Basic Usage
```bash
# Simple message
send_log_to_telegram "ERROR" "Database connection failed" "planner.sh"

# Success message
send_telegram_success "Deployment completed successfully"

# Error with context
send_log_to_telegram "WARNING" "Memory usage high" "monitor.sh" "Server: web01"
```

### Structured Data
```bash
# JSON message
json_data='{"user": "john", "action": "login", "timestamp": "2024-01-01T12:00:00Z"}'
send_structured_to_telegram "INFO" "$json_data" "auth.sh"
```

### Performance Metrics
```bash
# Performance monitoring
send_performance_to_telegram "database_query" "2.5" "Rows: 1000" "query.sh"
```

### Error Highlighting
```bash
# Error messages get automatic highlighting
send_telegram_error "Error: Failed to open config file at /etc/app/config.json: Permission denied"
```

## Message Format Examples

### Standard INFO Message
```
🔵 <b>INFO</b>
🕐 <code>2024-01-01 12:00:00</code>
📝 <i>planner.sh</i>
🔢 <code>PID: 12345</code>
👤 <code>user@hostname</code>
📂 <code>/home/user/projects</code>

📝 Task planning completed successfully
```

### ERROR Message with Highlighting
```
🔴 <b>ERROR</b>
🕐 <code>2024-01-01 12:00:00</code>
📝 <i>deploy.sh</i>
🔢 <code>PID: 12346</code>
👤 <code>user@hostname</code>

<b><i>Error:</i></b> <b><i>Failed</i></b> to connect to database at <code>/var/run/postgresql/.s.PGSQL.5432</code>
Exit code: 1
```

### Structured Data Message
```
🔵 <b>INFO</b>
🕐 <code>2024-01-01 12:00:00</code>
📝 <i>api.sh</i>

<b>📋 Structured Data:</b>
<pre><code>{"user": "john", "action": "login", "timestamp": "2024-01-01T12:00:00Z"}</code></pre>
```

## Testing

The formatter includes comprehensive test coverage:

```bash
# Run the test suite
./tests/test_telegram_formatter_simple.sh
```

### Test Coverage
- ✅ Basic message formatting
- ✅ Error message highlighting
- ✅ Structured data formatting
- ✅ Message truncation
- ✅ Message sanitization
- ✅ Context information formatting
- ✅ Message type detection
- ✅ Log level filtering
- ✅ Configuration validation

## Integration with Existing System

The enhanced formatter is designed to seamlessly integrate with the existing Auto-slopp logging system:

1. **Backward Compatibility**: Existing code continues to work unchanged
2. **Configuration-Based**: All features controlled via environment variables
3. **Async by Default**: Non-blocking message sending
4. **Graceful Degradation**: Continues working even if Telegram is unavailable

## Performance Considerations

- **Async Processing**: Messages are sent asynchronously to avoid blocking
- **Rate Limiting**: Built-in rate limiting prevents Telegram API abuse
- **Level-Specific Limits**: Different limits per log level (DEBUG < INFO < ERROR)
- **Smart Caching**: Configuration validation cached for efficiency
- **Minimal Overhead**: Disabled features don't add processing overhead

## Security Features

- **Input Sanitization**: Automatically redacts sensitive information
- **Configurable Redaction**: Choose what to redact (passwords, emails, IPs)
- **Validation**: Comprehensive configuration validation
- **Audit Logging**: Tracks message statistics and failures
- **Secure Defaults**: Secure by default, opt-in for less secure features

## Troubleshooting

### Common Issues

1. **Messages Not Sending**: Check `TELEGRAM_ENABLED` and bot token/chat ID
2. **Too Many Messages**: Adjust rate limiting or log level filters
3. **Missing Formatting**: Verify `TELEGRAM_FORMATTING_*` settings
4. **Large Messages**: Messages over 4096 chars are automatically truncated
5. **Rate Limits**: Check rate limiting configuration

### Debug Mode
```bash
export DEBUG_MODE="true"
export TELEGRAM_ENABLED="true"  # Keep enabled for debugging
```

### Testing Configuration
```bash
# Test configuration without sending
validate_telegram_logging_config

# Send a test message
test_telegram_logging "INFO" "Test message from formatter"
```

## Migration from Basic Formatter

The enhanced formatter is backward compatible. To upgrade:

1. Existing code continues to work unchanged
2. Enable new features by setting configuration variables
3. Gradually adopt advanced features as needed

### Recommended Migration Steps

1. **Phase 1**: Enable basic formatting features
   ```bash
   export TELEGRAM_FORMATTING_ENABLE_STRUCTURED="true"
   export TELEGRAM_FORMATTING_ENABLE_ERROR_HIGHLIGHTING="true"
   ```

2. **Phase 2**: Enable security features
   ```bash
   export TELEGRAM_ENABLE_MESSAGE_SANITIZATION="true"
   ```

3. **Phase 3**: Enable advanced filtering
   ```bash
   export TELEGRAM_FILTERS_MIN_LEVEL="WARNING"
   export TELEGRAM_FILTERS_ENABLE_LEVEL_RATE_LIMITING="true"
   ```

## Future Enhancements

- **Message Templates**: Customizable message formats per log level
- **Interactive Messages**: Buttons and inline keyboards for critical alerts
- **Message Threading**: Group related messages
- **Analytics**: Message statistics and trends
- **Multi-Language Support**: Internationalization support