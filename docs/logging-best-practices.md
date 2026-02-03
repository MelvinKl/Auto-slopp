# Logging Best Practices Guide

## Overview

This guide provides comprehensive best practices for using the enhanced logging system in the Repository Automation System. Following these practices ensures consistent, maintainable, and effective logging across all automation scripts.

## 🎯 Core Principles

### 1. Use Appropriate Log Levels

Choose the right log level for each message type:

```bash
# DEBUG: Detailed information for troubleshooting
log "DEBUG" "Variable values: user_id=$user_id, timestamp=$timestamp"

# INFO: General operational information
log "INFO" "Starting repository update for: $repo_name"

# SUCCESS: Completed operations
log "SUCCESS" "Repository $repo_name updated successfully"

# WARNING: Potential issues that don't stop execution
log "WARNING" "Repository $repo_name has uncommitted changes"

# ERROR: Failed operations that need attention
log "ERROR" "Failed to update repository $repo_name: $error_message"
```

### 2. Write Meaningful Messages

Include context and actionable information:

```bash
# ❌ Poor logging
log "INFO" "Processing repo"

# ✅ Good logging
log "INFO" "Processing repository: $repo_name (branch: $current_branch)"

# ❌ Poor error logging
log "ERROR" "Failed"

# ✅ Good error logging
log "ERROR" "Failed to merge branch '$source_branch' into '$target_branch': Conflict in file '$conflict_file'"
```

### 3. Use Structured Information

Include relevant variables and context in log messages:

```bash
# Before operation
log "INFO" "Starting operation: merge $source_branch → $target_branch in repository $repo_name"

# During operation
log "INFO" "Step 1/3: Fetching latest changes from origin"
log "INFO" "Step 2/3: Performing merge analysis"
log "INFO" "Step 3/3: Applying merge strategy: $merge_strategy"

# After operation
log "SUCCESS" "Merge completed: $commits_merged commits merged in ${elapsed_time}s"
```

## 📝 Script Integration Patterns

### Standard Script Template

All automation scripts should follow this pattern:

```bash
#!/bin/bash

# Set script name for logging identification
SCRIPT_NAME="your_script_name"

# Load utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# Set up error handling
setup_error_handling

# Main function
main() {
    log "INFO" "Starting $SCRIPT_NAME"
    
    # Your script logic here
    log "INFO" "Processing $item_count items"
    
    for item in "${items[@]}"; do
        log "DEBUG" "Processing item: $item"
        
        # Process item
        if process_item "$item"; then
            log "SUCCESS" "Item processed: $item"
        else
            log "ERROR" "Failed to process item: $item"
        fi
    done
    
    log "SUCCESS" "$SCRIPT_NAME completed successfully"
}

# Run main function with all arguments
main "$@"
```

### Error Handling Integration

```bash
# Function with proper error handling and logging
safe_git_operation() {
    local operation="$1"
    local repository="$2"
    
    log "INFO" "Starting git operation: $operation in $repository"
    
    if ! git -C "$repository" "$operation"; then
        log "ERROR" "Git operation failed: $operation in $repository (exit code: $?)"
        return 1
    fi
    
    log "SUCCESS" "Git operation completed: $operation in $repository"
    return 0
}

# Usage with error handling
if ! safe_git_operation "pull origin main" "$repo_path"; then
    log "WARNING" "Using fallback strategy for repository update"
    # Implement fallback logic
fi
```

## 🔧 Configuration Best Practices

### Environment-Specific Configurations

#### Production Environment
```yaml
# config.yaml - Production
timestamp_format: iso8601
timestamp_timezone: utc
log_level: INFO
log_directory: "/var/log/auto-slopp"
log_max_size_mb: 50
log_retention_days: 90
```

#### Development Environment
```yaml
# config.yaml - Development
timestamp_format: readable-precise
timestamp_timezone: local
log_level: DEBUG
log_directory: "~/git/Auto-logs"
log_max_size_mb: 10
log_retention_days: 7
```

#### Debugging Session
```bash
# Environment variables for debugging
export TIMESTAMP_FORMAT="debug"
export TIMESTAMP_TIMEZONE="local"
export LOG_LEVEL="DEBUG"
export DEBUG_MODE="true"
```

### Performance Considerations

For high-frequency operations, choose efficient logging settings:

```yaml
# High-performance logging
timestamp_format: compact-precise  # Faster than readable formats
log_level: WARNING                  # Reduce log volume
log_max_size_mb: 20                # Larger files reduce rotation overhead
```

## 🚨 Advanced Logging Patterns

### Specialized Logging Functions

Use specialized functions for specific event types:

```bash
# Change detection events
log_change_detection "repository-name" "5" "false"

# System health checks
log_system_health "disk_space" "pass"
log_system_health "memory_usage" "warning" "Memory usage at 85%"

# Reboot events
log_reboot_event "system_update" "2026-01-31 18:00:00"

# Performance logging
start_time=$(date +%s)
# ... perform operation ...
elapsed_time=$(($(date +%s) - start_time))
log "INFO" "Operation completed in ${elapsed_time}s"
```

### Structured Logging for Complex Events

```bash
# Complex operation with detailed logging
process_repository_update() {
    local repo_name="$1"
    local start_time=$(date +%s)
    
    log "INFO" "Starting repository update: $repo_name"
    log "DEBUG" "Repository path: $repo_path"
    log "DEBUG" "Current branch: $(git -C "$repo_path" branch --show-current)"
    
    # Step 1: Fetch changes
    if ! git -C "$repo_path" fetch origin; then
        log "ERROR" "Failed to fetch changes for $repo_name"
        return 1
    fi
    log "INFO" "Step 1/3: Fetched changes from origin"
    
    # Step 2: Analyze changes
    local changes_count=$(git -C "$repo_path" rev-list HEAD..origin/main --count)
    log "INFO" "Step 2/3: Found $changes_count changes to apply"
    
    # Step 3: Apply changes
    if ! git -C "$repo_path" merge origin/main; then
        log "ERROR" "Failed to merge changes for $repo_name"
        return 1
    fi
    log "INFO" "Step 3/3: Successfully merged changes"
    
    # Completion
    local elapsed_time=$(($(date +%s) - start_time))
    log "SUCCESS" "Repository update completed: $repo_name ($changes_count changes in ${elapsed_time}s)"
}
```

### Conditional Logging

```bash
# Log based on configuration or conditions
if [[ "${DEBUG_MODE:-false}" == "true" ]]; then
    log "DEBUG" "Detailed debugging information: $complex_data"
fi

# Log only for specific repositories
if [[ "$repo_name" =~ ^(critical|production)- ]]; then
    log "INFO" "Processing critical repository: $repo_name"
fi

# Performance logging
start_time=$(date +%s.%N 2>/dev/null || date +%s)
# ... operation ...
end_time=$(date +%s.%N 2>/dev/null || date +%s)
elapsed=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")

if (( $(echo "$elapsed > 5.0" | bc 2>/dev/null || echo "0") )); then
    log "WARNING" "Slow operation detected: took ${elapsed}s"
else
    log "DEBUG" "Operation completed in ${elapsed}s"
fi
```

## 🔍 Debugging Techniques

### Effective Debug Logging

```bash
# Function entry/exit logging
debug_function() {
    log "DEBUG" "Entering debug_function() with args: $1, $2"
    
    # Debug variable states
    log "DEBUG" "Variable state: user_id=$user_id, status=$status, timestamp=$timestamp"
    
    # Debug decision points
    if [[ "$status" == "active" ]]; then
        log "DEBUG" "Taking active path (status=$status)"
        # ... active logic ...
    else
        log "DEBUG" "Taking inactive path (status=$status)"
        # ... inactive logic ...
    fi
    
    log "DEBUG" "Exiting debug_function() with result: $result"
}
```

### Troubleshooting Configuration Issues

```bash
# Test logging configuration
test_logging_configuration() {
    log "INFO" "Testing logging configuration"
    log "INFO" "Timestamp format: $TIMESTAMP_FORMAT"
    log "INFO" "Timezone: $TIMESTAMP_TIMEZONE"
    log "INFO" "Log level: $LOG_LEVEL"
    log "INFO" "Debug mode: $DEBUG_MODE"
    
    # Test all log levels
    log "DEBUG" "This is a DEBUG message"
    log "INFO" "This is an INFO message"
    log "SUCCESS" "This is a SUCCESS message"
    log "WARNING" "This is a WARNING message"
    log "ERROR" "This is an ERROR message"
    
    # Test timestamp generation
    local timestamp=$(generate_timestamp "$TIMESTAMP_FORMAT" "$TIMESTAMP_TIMEZONE")
    log "INFO" "Generated timestamp: $timestamp"
}
```

## 📊 Log Analysis and Monitoring

### Log File Patterns

Understand the log file structure:

```bash
# View recent logs
tail -f ~/git/Auto-logs/main.log

# Search for errors
grep -i error ~/git/Auto-logs/*.log

# Filter by script
grep "script_name=updater" ~/git/Auto-logs/*.log

# Time-based filtering
grep "2026-01-31 1[4-5]:" ~/git/Auto-logs/main.log  # 2-4 PM

# Performance analysis
grep "elapsed_time" ~/git/Auto-logs/*.log | tail -20
```

### Monitoring Commands

```bash
# Real-time monitoring
watch -n 5 'tail -10 ~/git/Auto-logs/main.log'

# Error monitoring
watch -n 10 'grep -i error ~/git/Auto-logs/*.log | tail -5'

# Log file sizes
du -sh ~/git/Auto-logs/*.log | sort -hr

# Most active scripts
grep -o "script_name=[^:]*" ~/git/Auto-logs/*.log | sort | uniq -c | sort -nr
```

## ⚡ Performance Optimization

### Efficient Logging Practices

```bash
# Use appropriate log levels to reduce noise
if [[ "$item_count" -gt 100 ]]; then
    log "INFO" "Processing $item_count items"  # One message instead of many
else
    for item in "${items[@]}"; do
        log "DEBUG" "Processing item: $item"   # Debug for small batches
    done
fi

# Batch logging for high-frequency operations
log_batch_start() {
    BATCH_START_TIME=$(date +%s)
    BATCH_COUNT=0
}

log_batch_progress() {
    ((BATCH_COUNT++))
    if ((BATCH_COUNT % 100 == 0)); then
        local elapsed=$(($(date +%s) - BATCH_START_TIME))
        log "INFO" "Processed $BATCH_COUNT items in ${elapsed}s"
    fi
}

log_batch_end() {
    local elapsed=$(($(date +%s) - BATCH_START_TIME))
    log "SUCCESS" "Batch completed: $BATCH_COUNT items in ${elapsed}s"
}
```

## 🛡️ Security Considerations

### Secure Logging Practices

```bash
# Never log sensitive information
log "INFO" "User authenticated: $user_id"           # ✅ Safe
log "INFO" "User authenticated with token: $token"   # ❌ Unsafe - logs token

# Sanitize log messages
sanitize_log_message() {
    local message="$1"
    # Remove potential sensitive patterns
    echo "$message" | sed -E 's/(token|key|password|secret)[=:][^[:space:]]*/\1=***redacted***/gi'
}

# Usage
safe_log="INFO" "$(sanitize_log_message "API request with token=$api_token")"
```

## 🔧 Troubleshooting Guide

### Common Issues and Solutions

#### 1. Timestamps Not Showing

**Symptoms**: Log messages appear but timestamps are missing
**Causes**: 
- `utils.sh` not sourced before calling `log()`
- `date` command not available
- Invalid timestamp format

**Solution**:
```bash
# Ensure utils.sh is sourced first
source "$SCRIPT_DIR/utils.sh"

# Test timestamp generation
timestamp=$(generate_timestamp "$TIMESTAMP_FORMAT" "$TIMESTAMP_TIMEZONE")
echo "Test timestamp: $timestamp"

# Validate format
if validate_timestamp_format "$TIMESTAMP_FORMAT"; then
    echo "Format is valid"
else
    echo "Invalid format, using default"
fi
```

#### 2. Colors Not Working

**Symptoms**: Log output appears without color coding
**Causes**: 
- Terminal doesn't support ANSI colors
- `TERM` environment variable not set
- Output redirected to file

**Solution**:
```bash
# Check terminal support
echo -e "${RED}Red text${NC}"

# Set TERM variable
export TERM="xterm-256color"

# Force colors in scripts
export FORCE_COLOR=1
```

#### 3. Log Files Not Created

**Symptoms**: Console logging works but log files aren't created
**Causes**: 
- `LOG_DIRECTORY` not configured
- Directory permissions issue
- Directory doesn't exist

**Solution**:
```bash
# Check configuration
echo "Log directory: $LOG_DIRECTORY"

# Test directory access
if [[ -d "$LOG_DIRECTORY" ]]; then
    echo "Directory exists and is accessible"
    touch "$LOG_DIRECTORY/test.log" && rm "$LOG_DIRECTORY/test.log"
    echo "Directory is writable"
else
    echo "Directory does not exist or is not accessible"
    mkdir -p "$LOG_DIRECTORY"
fi
```

#### 4. Debug Messages Not Showing

**Symptoms**: DEBUG messages don't appear even when logged
**Causes**: 
- `DEBUG_MODE` not set to `true`
- `LOG_LEVEL` filtering out DEBUG messages
- Wrong log level specified

**Solution**:
```bash
# Enable debug mode
export DEBUG_MODE=true

# Set log level to DEBUG
export LOG_LEVEL=DEBUG

# Test debug logging
log "DEBUG" "This debug message should now appear"
```

## 📚 Additional Resources

### Related Documentation

- [Enhanced Logging Features Documentation](../enhanced_logging_documentation.md)
- [Logging System Architecture](../LOGGING_SYSTEM_DOCUMENTATION.md)
- [Configuration Guide](CONFIGURATION.md)
- [Troubleshooting Guide](../README.md#troubleshooting)

### Utility Functions Reference

- `configure_logging format timezone` - Configure logging settings
- `generate_timestamp format timezone` - Generate timestamp without logging
- `validate_timestamp_format format` - Validate timestamp format
- `validate_timezone timezone` - Validate timezone
- `get_supported_timestamp_formats` - List all available formats
- `benchmark_timestamp_generation format iterations` - Performance testing

---

**Best practices last updated**: 2026-01-31  
**Compatible with**: Auto-slopp v2.0+  
**Maintained by**: Repository Automation System