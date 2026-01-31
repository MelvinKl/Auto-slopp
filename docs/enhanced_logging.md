# Enhanced Logging System Documentation

## Overview

The Repository Automation System now includes an enhanced logging system with configurable timestamp formats, timezone support, and improved performance. The logging system follows functional programming principles with pure functions and modular design.

## Configuration

### Configuration File (config.yaml)

Add these settings to your `config.yaml` file:

```yaml
# Enhanced timestamp configuration
timestamp_format: default  # Timestamp format: "default", "iso8601", "compact", "readable", "debug", "microseconds"
timestamp_timezone: local   # Timezone for timestamps: "local" or "utc"
```

### Environment Variables

You can also override settings using environment variables:

```bash
export TIMESTAMP_FORMAT="iso8601"
export TIMESTAMP_TIMEZONE="utc"
export LOG_LEVEL="DEBUG"
export DEBUG_MODE="true"
```

## Timestamp Formats

### Available Formats

| Format | Description | Example | Use Case |
|--------|-------------|---------|----------|
| `default` | Standard readable format | `2026-01-30 20:25:08` | General logging |
| `iso8601` | ISO 8601 standard | `2026-01-30T20:25:08+00:00` | API integration, standards compliance |
| `compact` | Filename-friendly format | `20260130_202508` | Log file names, timestamps in filenames |
| `readable` | Human-friendly format | `2026-01-30 20:25:08` | User-facing logs |
| `debug` | With microseconds | `2026-01-30 20:25:08.354212` | Debugging, performance analysis |
| `microseconds` | High precision | `2026-01-30 20:25:08.354212` | Timing-sensitive operations |

### Timezone Support

- **local**: Use system's local timezone (default)
- **utc**: Use UTC timezone for consistent logs across systems

## Usage Examples

### Basic Logging

```bash
#!/bin/bash
source "scripts/utils.sh"

# Configure logging (optional - uses config.yaml defaults)
configure_logging "iso8601" "utc"

# Log messages with different levels
log "INFO" "Starting automation system"
log "SUCCESS" "Operation completed successfully"
log "WARNING" "Deprecated feature used"
log "ERROR" "Failed to connect to server"
log "DEBUG" "Detailed debugging information"
```

### Configuration in Scripts

```bash
#!/bin/bash
# Script-specific configuration
SCRIPT_NAME="my_script"
configure_logging "debug" "local"

# Enable debug mode for this script
DEBUG_MODE=true

log "DEBUG" "This will show with microseconds"
log "INFO" "Standard information"
```

### Dynamic Configuration

```bash
#!/bin/bash

# Use environment variable or fallback to config.yaml
format="${TIMESTAMP_FORMAT:-default}"
timezone="${TIMESTAMP_TIMEZONE:-local}"

configure_logging "$format" "$timezone"

log "INFO" "Logging configured with format: $format, timezone: $timezone"
```

## Advanced Functions

### Pure Functions

The enhanced system includes pure functions for advanced usage:

```bash
# Generate timestamp without logging
timestamp=$(generate_timestamp "iso8601" "utc")
echo "Timestamp: $timestamp"

# Validate timestamp format
if validate_timestamp_format "iso8601"; then
    echo "Format is valid"
fi

# Get script name
script_name=$(get_script_name)

# Format log entry manually
entry=$(format_log_entry "INFO" "2026-01-30 20:25:08" "$script_name" "custom message")
echo "$entry"
```

## Migration from Basic Logging

### Old Code

```bash
echo "Starting operation at $(date)"
echo "Error: Something went wrong"
```

### New Code

```bash
log "INFO" "Starting operation"
log "ERROR" "Something went wrong"
```

## Performance Considerations

- **Pure functions**: Minimal overhead for timestamp generation
- **Lazy evaluation**: Timestamps generated only when needed
- **Configurable precision**: Use "default" format for better performance
- **File logging**: Asynchronous writes with rotation

## Configuration Best Practices

### Production Environment

```yaml
timestamp_format: iso8601
timestamp_timezone: utc
log_level: INFO
```

### Development Environment

```yaml
timestamp_format: debug
timestamp_timezone: local
log_level: DEBUG
```

### Debugging Sessions

```bash
export TIMESTAMP_FORMAT="debug"
export DEBUG_MODE="true"
```

## Troubleshooting

### Common Issues

1. **Invalid timestamp format**
   - System falls back to "default" format
   - Check your config.yaml for typos

2. **Timezone not working**
   - Ensure you're using "local" or "utc" (case-sensitive)
   - Check system timezone configuration

3. **Microseconds not showing**
   - Your system's `date` command may not support `%N`
   - System falls back to seconds-only precision

### Debug Mode

Enable debug mode to troubleshoot logging:

```bash
export DEBUG_MODE="true"
export LOG_LEVEL="DEBUG"
```

## Integration with Existing Scripts

The enhanced logging system is fully backwards compatible. Existing scripts using the `log()` function will automatically benefit from improved timestamp generation and configuration options.

No changes are required for existing scripts unless you want to:
1. Use specific timestamp formats
2. Configure timezone settings
3. Access the pure functions for custom logging solutions