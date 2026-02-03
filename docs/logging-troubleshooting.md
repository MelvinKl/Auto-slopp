# Logging System Troubleshooting Guide

## Overview

This guide provides comprehensive troubleshooting steps for common issues with the enhanced logging system in the Repository Automation System.

## 🔍 Diagnostic Commands

### Quick Health Check

Run these commands to diagnose logging system health:

```bash
# 1. Check if utils.sh is properly sourced
source scripts/utils.sh && echo "utils.sh loaded successfully"

# 2. Test basic logging functionality
log "INFO" "Test message - basic functionality"

# 3. Test timestamp generation
timestamp=$(generate_timestamp "default" "local")
echo "Generated timestamp: $timestamp"

# 4. Validate current configuration
echo "Timestamp format: $TIMESTAMP_FORMAT"
echo "Timezone: $TIMESTAMP_TIMEZONE"
echo "Log level: $LOG_LEVEL"
echo "Debug mode: $DEBUG_MODE"

# 5. Check log directory access
[[ -d "$LOG_DIRECTORY" ]] && echo "Log directory accessible" || echo "Log directory not accessible"

# 6. Test all log levels
log "DEBUG" "DEBUG level test"
log "INFO" "INFO level test"
log "SUCCESS" "SUCCESS level test"
log "WARNING" "WARNING level test"
log "ERROR" "ERROR level test"
```

### Advanced Diagnostics

```bash
# Validate timestamp format
if validate_timestamp_format "$TIMESTAMP_FORMAT"; then
    echo "✅ Timestamp format '$TIMESTAMP_FORMAT' is valid"
else
    echo "❌ Timestamp format '$TIMESTAMP_FORMAT' is invalid"
fi

# Validate timezone
if validate_timezone "$TIMESTAMP_TIMEZONE"; then
    echo "✅ Timezone '$TIMESTAMP_TIMEZONE' is valid"
else
    echo "❌ Timezone '$TIMESTAMP_TIMEZONE' is invalid"
fi

# Show supported formats
echo "Supported timestamp formats:"
get_supported_timestamp_formats

# Performance benchmark
echo "Performance benchmark (100 iterations):"
benchmark_timestamp_generation "$TIMESTAMP_FORMAT" 100 "$TIMESTAMP_TIMEZONE"
```

## 🚨 Common Issues and Solutions

### Issue 1: No Timestamps in Log Output

**Symptoms:**
- Log messages appear but without timestamps
- Output shows only log level and message

**Diagnostic Steps:**
```bash
# Check if utils.sh is sourced
declare -f log >/dev/null && echo "log function exists" || echo "log function missing"

# Check timestamp format
echo "Current format: $TIMESTAMP_FORMAT"

# Test timestamp generation directly
test_timestamp=$(generate_timestamp "$TIMESTAMP_FORMAT" "$TIMESTAMP_TIMEZONE")
echo "Direct timestamp test: $test_timestamp"
```

**Solutions:**

1. **Ensure utils.sh is sourced:**
```bash
# In your script, add this before any log() calls:
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
```

2. **Validate timestamp format:**
```bash
# Check if format is valid
if ! validate_timestamp_format "$TIMESTAMP_FORMAT"; then
    echo "Invalid format, setting to default"
    export TIMESTAMP_FORMAT="default"
fi
```

3. **Test date command availability:**
```bash
if command -v date >/dev/null 2>&1; then
    echo "date command available: $(date)"
else
    echo "❌ date command not found"
fi
```

### Issue 2: Colors Not Working

**Symptoms:**
- All log output appears in plain text
- No color coding for different log levels

**Diagnostic Steps:**
```bash
# Check terminal support
echo -e "${RED}Red${NC} ${GREEN}Green${NC} ${YELLOW}Yellow${NC}"

# Check TERM variable
echo "TERM: $TERM"

# Test color variables
echo "RED code: '$RED'"
echo "NC code: '$NC'"
```

**Solutions:**

1. **Set terminal type:**
```bash
export TERM="xterm-256color"
export COLORTERM="truecolor"
```

2. **Force color output:**
```bash
# Add to script or environment
export FORCE_COLOR=1

# Or modify utils.sh to force colors
if [[ "${FORCE_COLOR:-false}" == "true" || -t 1 ]]; then
    # Use color codes
    echo -e "${RED}[ERROR]${NC} ..."
fi
```

3. **Check if output is being redirected:**
```bash
# Colors are disabled when output is redirected to files
# To force colors even when redirected:
log_with_color() {
    log "$@" | cat
}
```

### Issue 3: Log Files Not Created

**Symptoms:**
- Console logging works fine
- No log files appear in LOG_DIRECTORY

**Diagnostic Steps:**
```bash
# Check log directory configuration
echo "LOG_DIRECTORY: '$LOG_DIRECTORY'"

# Check if directory exists
[[ -d "$LOG_DIRECTORY" ]] && echo "Directory exists" || echo "Directory does not exist"

# Check directory permissions
if [[ -d "$LOG_DIRECTORY" ]]; then
    touch "$LOG_DIRECTORY/test_write.log" && echo "Directory writable" || echo "Directory not writable"
    rm -f "$LOG_DIRECTORY/test_write.log"
fi

# Check disk space
df -h "$LOG_DIRECTORY"
```

**Solutions:**

1. **Create log directory:**
```bash
mkdir -p "$LOG_DIRECTORY"
chmod 755 "$LOG_DIRECTORY"
```

2. **Fix permissions:**
```bash
# Set appropriate ownership
sudo chown $USER:$USER "$LOG_DIRECTORY"

# Set write permissions
chmod u+w "$LOG_DIRECTORY"
```

3. **Update configuration:**
```yaml
# In config.yaml
log_directory: "~/git/Auto-logs"  # Use tilde for home directory
```

4. **Test manually:**
```bash
# Manual test of log file creation
echo "Test log entry" >> "$LOG_DIRECTORY/test.log"
ls -la "$LOG_DIRECTORY/"
```

### Issue 4: Debug Messages Not Showing

**Symptoms:**
- DEBUG level messages don't appear even when logged
- Only INFO, WARNING, and ERROR messages show

**Diagnostic Steps:**
```bash
# Check debug mode
echo "DEBUG_MODE: '$DEBUG_MODE'"

# Check log level
echo "LOG_LEVEL: '$LOG_LEVEL'"

# Test level filtering
if should_log "DEBUG"; then
    echo "DEBUG messages should appear"
else
    echo "DEBUG messages are filtered out"
fi

# Test with debug mode enabled
DEBUG_MODE=true log "DEBUG" "Test with DEBUG_MODE=true"
```

**Solutions:**

1. **Enable debug mode:**
```bash
# Temporary (current session only)
export DEBUG_MODE=true

# Permanent (add to ~/.bashrc or config.sh)
echo 'export DEBUG_MODE=true' >> ~/.bashrc
```

2. **Set log level to DEBUG:**
```bash
export LOG_LEVEL=DEBUG

# Or in config.yaml
log_level: DEBUG
```

3. **Test both methods:**
```bash
DEBUG_MODE=true LOG_LEVEL=DEBUG log "DEBUG" "This should definitely appear"
```

### Issue 5: Invalid Timestamp Format

**Symptoms:**
- Warning messages about invalid timestamp format
- Timestamps fall back to default format

**Diagnostic Steps:**
```bash
# Check current format
echo "Current format: '$TIMESTAMP_FORMAT'"

# Validate format
if validate_timestamp_format "$TIMESTAMP_FORMAT"; then
    echo "✅ Format is valid"
else
    echo "❌ Format is invalid"
    echo "Available formats:"
    get_supported_timestamp_formats
fi
```

**Solutions:**

1. **Use valid format:**
```bash
# Valid formats
export TIMESTAMP_FORMAT="default"
export TIMESTAMP_FORMAT="iso8601"
export TIMESTAMP_FORMAT="readable-precise"
export TIMESTAMP_FORMAT="debug"

# Invalid formats (these will cause warnings)
export TIMESTAMP_FORMAT="invalid"
export TIMESTAMP_FORMAT="custom"
```

2. **Reset to safe default:**
```bash
export TIMESTAMP_FORMAT="default"
```

### Issue 6: Timezone Problems

**Symptoms:**
- Timestamps show wrong timezone
- UTC/local timezone not working as expected

**Diagnostic Steps:**
```bash
# Check current timezone setting
echo "Current timezone: '$TIMESTAMP_TIMEZONE'"

# Test timezone validation
if validate_timezone "$TIMESTAMP_TIMEZONE"; then
    echo "✅ Timezone is valid"
else
    echo "❌ Timezone is invalid"
fi

# Test different timezones
echo "Local: $(generate_timestamp 'default' 'local')"
echo "UTC: $(generate_timestamp 'default' 'utc')"
```

**Solutions:**

1. **Use valid timezone:**
```bash
# Valid options
export TIMESTAMP_TIMEZONE="local"
export TIMESTAMP_TIMEZONE="utc"

# For specific timezone (if supported)
export TIMESTAMP_TIMEZONE="America/New_York"
export TIMESTAMP_TIMEZONE="+05:30"
```

2. **Check system timezone:**
```bash
# System timezone
timedatectl status

# Or
date
```

### Issue 7: Performance Issues

**Symptoms:**
- Logging seems slow
- High CPU usage during logging
- Scripts take longer to execute

**Diagnostic Steps:**
```bash
# Benchmark current format
echo "Benchmarking current format:"
benchmark_timestamp_generation "$TIMESTAMP_FORMAT" 1000 "$TIMESTAMP_TIMEZONE"

# Test different formats
echo "Benchmarking default format:"
benchmark_timestamp_generation "default" 1000 "local"

echo "Benchmarking compact format:"
benchmark_timestamp_generation "compact" 1000 "local"
```

**Solutions:**

1. **Use faster format:**
```bash
# Faster formats
export TIMESTAMP_FORMAT="default"
export TIMESTAMP_FORMAT="compact"
export TIMESTAMP_FORMAT="readable"
```

2. **Reduce log level:**
```bash
# Filter out verbose debug messages
export LOG_LEVEL="WARNING"
```

3. **Increase log rotation thresholds:**
```yaml
# In config.yaml
log_max_size_mb: 50  # Larger files reduce rotation overhead
```

## 🔧 Repair and Recovery

### Reset Logging Configuration

```bash
# Reset to safe defaults
export TIMESTAMP_FORMAT="default"
export TIMESTAMP_TIMEZONE="local"
export LOG_LEVEL="INFO"
export DEBUG_MODE="false"

# Test the reset
source scripts/utils.sh
log "INFO" "Logging system reset to defaults"
```

### Reinstall utils.sh

```bash
# Backup current version
cp scripts/utils.sh scripts/utils.sh.backup

# Check for syntax errors
bash -n scripts/utils.sh && echo "✅ Syntax OK" || echo "❌ Syntax error"

# Reload utilities
source scripts/utils.sh
```

### Clear Log Files (If Needed)

```bash
# Clear log files (WARNING: This deletes log history)
if [[ -d "$LOG_DIRECTORY" ]]; then
    echo "Clearing log files in: $LOG_DIRECTORY"
    rm -f "$LOG_DIRECTORY"/*.log*
    echo "Log files cleared"
fi
```

## 📞 Getting Help

### Creating a Support Request

When creating an issue, include this diagnostic information:

```bash
# Run this and include the output in your issue
cat << 'EOF'
=== Logging System Diagnostic Report ===
Date: $(date)
System: $(uname -a)
Bash version: $BASH_VERSION

Configuration:
- Timestamp format: $TIMESTAMP_FORMAT
- Timezone: $TIMESTAMP_TIMEZONE
- Log level: $LOG_LEVEL
- Debug mode: $DEBUG_MODE
- Log directory: $LOG_DIRECTORY

Function Availability:
- log function: $(declare -f log >/dev/null && echo "Available" || echo "Missing")
- generate_timestamp: $(declare -f generate_timestamp >/dev/null && echo "Available" || echo "Missing")
- validate_timestamp_format: $(declare -f validate_timestamp_format >/dev/null && echo "Available" || echo "Missing")

Tests:
- Basic logging: $(log "INFO" "Test" 2>&1 | head -1)
- Timestamp generation: $(generate_timestamp "default" "local")
- Directory access: $([[ -d "$LOG_DIRECTORY" ]] && echo "Accessible" || echo "Not accessible")
=== End Diagnostic Report ===
EOF
```

### Log Analysis Commands

```bash
# Recent errors
grep -i error ~/git/Auto-logs/*.log | tail -10

# Configuration issues
grep -i "warning\|invalid" ~/git/Auto-logs/*.log | tail -10

# Performance issues
grep "elapsed_time" ~/git/Auto-logs/*.log | tail -10

# Script-specific issues
grep "script_name=$(basename "$0")" ~/git/Auto-logs/*.log | tail -10
```

## 📚 Additional Resources

- [Logging Best Practices Guide](logging-best-practices.md)
- [Enhanced Logging Features Documentation](../enhanced_logging_documentation.md)
- [Logging System Architecture](../LOGGING_SYSTEM_DOCUMENTATION.md)
- [Configuration Guide](CONFIGURATION.md)

---

**Troubleshooting guide last updated**: 2026-01-31  
**Compatible with**: Auto-slopp v2.0+  
**Maintained by**: Repository Automation System