# Telegram Bot API Configuration System Documentation

## Overview

This document describes the comprehensive Telegram Bot API configuration system designed for the Auto-slopp project. The system provides secure, reliable, and configurable Telegram integration for logging and notifications.

## Architecture

The Telegram configuration system consists of several integrated components:

### Core Modules

1. **`telegram_logger.sh`** - Core logging and message sending functionality
2. **`telegram_security.sh`** - Security, token management, and validation
3. **`telegram_queue.sh`** - Message queuing and rate limiting
4. **`telegram_health.sh`** - Health monitoring and status checking
5. **`telegram_config.sh`** - Configuration management and validation

### Integration Points

- **`config.yaml`** - Central configuration file with Telegram settings
- **`utils.sh`** - Enhanced logging function with Telegram integration
- **`yaml_config.sh`** - Configuration loading and parsing

## Configuration Schema

The Telegram configuration is defined in `config.yaml` under the `telegram` section:

```yaml
# Telegram Bot logging configuration (P0 Critical)
telegram:
  enabled: false                        # Enable/disable Telegram logging globally
  bot_token: "${TELEGRAM_BOT_TOKEN}"    # Environment variable for bot token (NEVER store in plain text)
  default_chat_id: "@logs_channel"      # Default channel/chat for sending messages
  api_timeout_seconds: 10               # Timeout for Telegram API requests
  connection_retries: 3                 # Maximum retry attempts for failed connections
  
  # Rate limiting configuration
  rate_limiting:
    messages_per_second: 5              # Conservative rate limit (far below Telegram's 30/sec)
    burst_size: 20                     # Burst capacity for handling logs
    rate_limit_window_seconds: 60      # Time window for rate limiting calculations
    backoff_multiplier: 2              # Multiplier for exponential backoff
    max_backoff_seconds: 30             # Maximum backoff delay
  
  # Message formatting configuration
  formatting:
    parse_mode: "HTML"                  # Message format: "HTML", "Markdown", or "plain"
    max_message_length: 4000            # Safe message length (below Telegram's 4096 limit)
    include_timestamp: true             # Include timestamps in messages
    include_log_level: true             # Include log level indicators
    include_script_name: true           # Include script name for context
    use_emoji_indicators: true          # Use emoji for log levels (🔴🟡🟢🔵)
  
  # Retry and error handling configuration
  retry:
    max_attempts: 3                     # Maximum retry attempts for failed messages
    base_delay: 1.0                     # Base delay in seconds for exponential backoff
    max_delay: 30.0                     # Maximum delay in seconds
    jitter: true                        # Add randomness to prevent thundering herd
  
  # Message filtering configuration
  filters:
    log_levels: ["ERROR", "WARNING", "SUCCESS"]  # Log levels to forward to Telegram
    scripts: ["main.sh", "updater.sh", "implementer.sh", "planner.sh"]  # Scripts to monitor
    exclude_patterns: []                # Regex patterns to exclude from Telegram
    include_patterns: []                # Regex patterns to include (if specified, acts as whitelist)
  
  # Security configuration
  security:
    validate_bot_token: true            # Validate bot token format and connectivity
    encrypt_config_storage: true         # Encrypt sensitive configuration in memory
    audit_token_access: true            # Log all token access attempts
    hide_tokens_in_logs: true           # Redact tokens in log outputs
    require_https: true                 # Enforce HTTPS for all API calls
  
  # Health monitoring configuration
  health:
    enable_health_checks: true          # Periodic health checks for Telegram integration
    health_check_interval_minutes: 15   # How often to run health checks
    api_connectivity_test: true         # Test API connectivity during health checks
    rate_limit_monitoring: true          # Monitor rate limiting status
    queue_size_monitoring: true         # Monitor message queue size
  
  # Configuration management
  config:
    auto_reload: true                   # Reload configuration without restart
    config_file_watch_interval_seconds: 30  # How often to check for config changes
    validation_strictness: "strict"     # Validation level: "strict", "warn", or "relaxed"
    backup_configuration: true          # Backup configuration changes
```

## Security Requirements

### Token Management

1. **NEVER hardcode bot tokens** in configuration files or scripts
2. **Use environment variables** for token storage: `TELEGRAM_BOT_TOKEN`
3. **Secure file storage** (600 permissions) for token persistence
4. **Token validation** before use and during health checks

### Secure Storage Setup

```bash
# Set up secure token storage
sudo mkdir -p /etc/telegram
sudo chmod 700 /etc/telegram

# Store token securely
echo "123456789:ABCdefGHIjklMNOpqrsTUVwxyz-123456789" | sudo tee /etc/telegram/token
sudo chmod 600 /etc/telegram/token
sudo chown root:root /etc/telegram/token

# Set up environment variable
echo 'export TELEGRAM_BOT_TOKEN="$(cat /etc/telegram/token 2>/dev/null)"' >> /etc/environment
```

### Security Auditing

- All token access attempts are logged to `/var/log/telegram_audit.log`
- Configuration is validated for security compliance
- Hardcoded tokens are automatically detected and flagged

## Message Processing Flow

### 1. Log Message Generation

```
Script calls log() function → Enhanced utils.sh log() → Telegram check → Queue message
```

### 2. Message Filtering

- Log level filtering (ERROR, WARNING, SUCCESS by default)
- Script name filtering
- Regex pattern filtering (include/exclude)

### 3. Message Queuing

- Messages are queued by priority (high, normal, low)
- Rate limiting is applied at queue level
- Background processor handles delivery

### 4. Message Formatting

```
Level + Emoji + Timestamp + Script Name + Message Content
```

Example output:
```
🔴 ERROR
📝 script_name
🕐 2026-02-02 14:30:15

Something went wrong during processing
```

## Rate Limiting Strategy

### Conservative Limits

- **Messages per second**: 5 (well below Telegram's 30/sec limit)
- **Burst capacity**: 20 messages
- **Exponential backoff**: 2^attempt with jitter
- **Maximum backoff**: 30 seconds

### Rate Limiting Logic

```python
if messages_in_window >= burst_limit:
    wait_until_window_resets()
elif time_since_last_message < min_interval:
    sleep(min_interval - time_since_last_message)
```

## Error Handling and Retry Logic

### Retry Strategy

1. **Immediate retry** for transient errors
2. **Exponential backoff** for persistent failures
3. **Maximum attempts** (default: 3)
4. **Message splitting** for oversized messages

### Error Categories

- **4xx errors**: No retry (client error)
- **5xx errors**: Retry with backoff (server error)
- **Network errors**: Retry with backoff
- **Rate limiting**: Wait for `retry_after` seconds

## Health Monitoring

### Health Check Categories

1. **API Connectivity** - Test Bot API endpoint
2. **Rate Limiting Status** - Monitor current limits
3. **Queue Health** - Check backlog and processing
4. **Configuration** - Validate settings
5. **Security** - Check token security
6. **Performance** - Response times and throughput

### Health Check Results

- **Healthy** - All systems functioning normally
- **Degraded** - Non-critical issues detected
- **Unhealthy** - Critical problems requiring attention

## Configuration Management

### Auto-Reload Feature

- Configuration changes detected automatically
- Validation performed before reload
- Backup created before applying changes
- Modules reinitialized with new settings

### Validation Levels

- **Strict** - All issues treated as errors
- **Warn** - Issues logged as warnings
- **Relaxed** - Minimal validation

## Integration with Existing Logging

### Enhanced Log Function

The existing `log()` function in `utils.sh` is automatically enhanced:

```bash
log "ERROR" "This message goes to console, file, and Telegram"
```

### Selective Forwarding

Only messages matching configured criteria are sent to Telegram:
- Log levels: ERROR, WARNING, SUCCESS (configurable)
- Scripts: main.sh, updater.sh, etc. (configurable)
- Patterns: Include/exclude regex filters

## Performance Considerations

### Asynchronous Processing

- Telegram sending happens in background processes
- No blocking of main script execution
- Queue system handles spikes gracefully

### Memory Management

- Message queues stored in temporary files
- Automatic cleanup of old messages
- Configurable retention periods

### Network Optimization

- Connection pooling (future enhancement)
- Message compression (future enhancement)
- Batch API calls (future enhancement)

## Testing and Validation

### Unit Tests

```bash
# Test configuration validation
./tests/test_telegram_config.sh

# Test token security
./tests/test_telegram_security.sh

# Test message sending
./tests/test_telegram_sending.sh
```

### Integration Tests

```bash
# Test full integration
./tests/test_telegram_integration.sh

# Test rate limiting
./tests/test_telegram_rate_limit.sh

# Test queue processing
./tests/test_telegram_queue.sh
```

### Manual Testing

```bash
# Send test message
source scripts/core/telegram_logger.sh
send_telegram_message "Test message from Auto-slopp"

# Check health status
source scripts/core/telegram_health.sh
run_telegram_health_check true

# View queue statistics
source scripts/core/telegram_queue.sh
get_queue_statistics
```

## Troubleshooting

### Common Issues

1. **Messages not sending**
   - Check `TELEGRAM_ENABLED=true`
   - Verify bot token format
   - Test API connectivity

2. **Rate limiting errors**
   - Reduce `messages_per_second` setting
   - Check for message loops
   - Review queue backlog

3. **Configuration validation failures**
   - Check syntax in config.yaml
   - Verify environment variables
   - Review validation logs

### Debug Mode

Enable debug logging:

```bash
export DEBUG_MODE=true
export TELEGRAM_ENABLED=true
source scripts/utils.sh
log "DEBUG" "This will show detailed Telegram processing"
```

### Log Locations

- **Application logs**: `~/git/Auto-logs/telegram_logger.log`
- **Audit logs**: `/var/log/telegram_audit.log`
- **Queue files**: `/tmp/telegram_queue/`
- **Config backups**: `/tmp/telegram_config_backups/`

## Migration Guide

### From Plain Text Configuration

1. Move bot token to environment variable
2. Update config.yaml to use `${TELEGRAM_BOT_TOKEN}`
3. Run security validation
4. Test with existing log messages

### From No Telegram Integration

1. Set up bot token (see security section)
2. Enable Telegram in config.yaml
3. Configure desired log levels and scripts
4. Test with a sample message
5. Gradually expand to full integration

## Best Practices

### Security

- Never commit bot tokens to version control
- Use environment variables for sensitive data
- Regularly rotate bot tokens
- Monitor access logs

### Performance

- Keep message length under 4000 characters
- Use appropriate rate limiting
- Monitor queue size regularly
- Test during high load periods

### Reliability

- Enable health monitoring
- Configure appropriate retry settings
- Monitor error rates
- Have backup notification channels

### Maintenance

- Regular configuration validation
- Clean up old queue files
- Review audit logs
- Update tokens periodically

## Future Enhancements

### Planned Features

1. **Message Batching** - Combine multiple log entries
2. **Rich Content** - Support for images and documents
3. **Interactive Commands** - Telegram bot commands for control
4. **Multi-Channel Support** - Different chats for different log types
5. **End-to-End Encryption** - For sensitive log data

### API Enhancements

1. **Webhook Support** - Receive Telegram messages
2. **Bot Commands** - Control Auto-slopp via Telegram
3. **Media Upload** - Send logs as files
4. **Location Support** - Include location data in messages

## Support and Contact

For issues with the Telegram integration:

1. Check health status: `run_telegram_health_check true`
2. Review configuration: `get_telegram_configuration_summary config.yaml`
3. Examine logs in the specified locations
4. Validate security settings: `validate_telegram_security`

This configuration system provides a robust, secure, and scalable foundation for Telegram Bot API integration in the Auto-slopp project.