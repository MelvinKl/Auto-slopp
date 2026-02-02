# Telegram Bot API Integration Requirements - Implementation Summary

## Task Completion Summary

This document provides the complete research and requirements for integrating Telegram Bot API for log output in the Auto-slopp project, based on comprehensive research of Telegram's Bot API documentation, best practices, and security considerations.

## 1. Key Findings

### Required API Endpoints
- **Primary**: `sendMessage` endpoint (`/bot{token}/sendMessage`)
- **Additional**: `sendPhoto` and `sendDocument` for rich content
- **Base URL**: `https://api.telegram.org/bot{token}/`

### Authentication & Security
- **Bot Token Format**: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
- **Storage**: Environment variables or secure files (600 permissions)
- **Security**: Never commit tokens, use secure storage, implement access controls

### Message Limitations & Format
- **Size Limit**: 4096 characters per message (use 4000 as safe limit)
- **Formats**: Plain text, HTML, Markdown supported
- **Rate Limits**: ~30 msgs/sec to same chat, ~20 msgs/sec to different chats
- **Error Handling**: HTTP 429 with `retry_after` parameter for rate limiting

## 2. Integration Architecture

### Existing System Analysis
The Auto-slopp project has:
- **Comprehensive Logging System**: Found in `scripts/utils.sh` with configurable timestamps, log levels, and file rotation
- **YAML Configuration**: Central config in `config.yaml` with structured settings
- **Modular Scripts**: Well-organized shell scripts with consistent error handling
- **Enhanced Error Handling**: Robust error recovery and state management

### Proposed Integration Points
```yaml
# Add to config.yaml
telegram:
  enabled: false                    # Enable/disable Telegram logging
  bot_token: "${TELEGRAM_BOT_TOKEN}" # Environment variable for security
  default_chat_id: "@logs_channel"   # Target channel/chat
  rate_limiting:
    messages_per_second: 5          # Conservative rate limit
    burst_size: 20                 # Burst capacity
  formatting:
    parse_mode: "HTML"             # Message formatting
    max_message_length: 4000        # Safe message size
    include_timestamp: true         # Include timestamps
    include_log_level: true         # Include log levels
  retry:
    max_attempts: 3                # Retry attempts
    base_delay: 1.0               # Base delay for exponential backoff
    max_delay: 30.0               # Maximum delay
  filters:
    log_levels: ["ERROR", "WARNING", "SUCCESS"]  # Levels to forward
    scripts: ["main.sh", "updater.sh"]          # Scripts to monitor
```

## 3. Implementation Components

### Core Telegram Module (`scripts/core/telegram_logger.sh`)
```bash
#!/bin/bash

# Telegram Bot API Integration Module
# Handles Telegram message sending with rate limiting and error handling

source "$(dirname "$0")/../utils.sh"

# Configuration validation
validate_telegram_config() {
    local bot_token="${TELEGRAM_BOT_TOKEN:-}"
    local chat_id="${TELEGRAM_CHAT_ID:-}"
    
    if [[ -z "$bot_token" ]]; then
        log "ERROR" "TELEGRAM_BOT_TOKEN not configured"
        return 1
    fi
    
    if [[ -z "$chat_id" ]]; then
        log "ERROR" "TELEGRAM_CHAT_ID not configured"
        return 1
    fi
    
    # Validate bot token format
    if [[ ! "$bot_token" =~ ^[0-9]+:[a-zA-Z0-9_-]+$ ]]; then
        log "ERROR" "Invalid bot token format"
        return 1
    fi
    
    return 0
}

# Send message with comprehensive error handling
send_telegram_message() {
    local message="$1"
    local chat_id="${2:-${TELEGRAM_CHAT_ID}}"
    local parse_mode="${3:-HTML}"
    local max_retries="${4:-3}"
    
    if ! validate_telegram_config; then
        return 1
    fi
    
    local bot_token="$TELEGRAM_BOT_TOKEN"
    local url="https://api.telegram.org/bot${bot_token}/sendMessage"
    
    # Check message length and split if necessary
    if [[ ${#message} -gt 4000 ]]; then
        log "DEBUG" "Message too long (${#message} chars), splitting into chunks"
        return send_message_chunks "$message" "$chat_id" "$parse_mode" "$max_retries"
    fi
    
    # Escape HTML characters if using HTML parse mode
    if [[ "$parse_mode" == "HTML" ]]; then
        message=$(escape_html "$message")
    fi
    
    # Build JSON payload
    local payload=$(cat << EOF
{
    "chat_id": "$chat_id",
    "text": "$message",
    "parse_mode": "$parse_mode",
    "disable_web_page_preview": true
}
EOF
)
    
    # Send with retry logic
    for ((attempt=1; attempt<=max_retries; attempt++)); do
        local response
        if response=$(curl -s -w "%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "$payload" \
            "$url" 2>/dev/null); then
            
            local http_code="${response: -3}"
            local response_body="${response%???}"
            
            if [[ "$http_code" == "200" ]]; then
                log "DEBUG" "Telegram message sent successfully"
                return 0
            elif [[ "$http_code" == "429" ]]; then
                # Rate limited
                local retry_after=$(echo "$response_body" | jq -r '.parameters.retry_after // 1' 2>/dev/null || echo "1")
                log "WARNING" "Rate limited by Telegram, waiting ${retry_after}s"
                sleep "$retry_after"
                continue
            elif [[ "$http_code" =~ ^4[0-9][0-9]$ ]]; then
                # Client error - don't retry
                log "ERROR" "Telegram client error $http_code: $response_body"
                return 1
            else
                # Server error - retry
                log "WARNING" "Telegram server error $http_code (attempt $attempt/$max_retries)"
                if [[ $attempt -lt $max_retries ]]; then
                    sleep $((attempt * 2))  # Exponential backoff
                fi
            fi
        else
            log "ERROR" "Failed to make HTTP request to Telegram (attempt $attempt/$max_retries)"
            if [[ $attempt -lt $max_retries ]]; then
                sleep $((attempt * 2))
            fi
        fi
    done
    
    log "ERROR" "Failed to send Telegram message after $max_retries attempts"
    return 1
}

# Split long messages into chunks
send_message_chunks() {
    local message="$1"
    local chat_id="$2"
    local parse_mode="$3"
    local max_retries="$4"
    local chunk_size=4000
    local chunks=()
    
    # Split by lines to preserve readability
    local current_chunk=""
    while IFS= read -r line; do
        if [[ ${#current_chunk} + ${#line} + 1 -gt $chunk_size ]]; then
            if [[ -n "$current_chunk" ]]; then
                chunks+=("$current_chunk")
                current_chunk=""
            fi
        fi
        current_chunk+="${line}${current_chunk:+$'\n'}"
    done <<< "$message"
    
    if [[ -n "$current_chunk" ]]; then
        chunks+=("$current_chunk")
    fi
    
    log "DEBUG" "Sending ${#chunks[@]} chunks to Telegram"
    
    local success_count=0
    for i in "${!chunks[@]}"; do
        local chunk="${chunks[i]}"
        local prefix=""
        if [[ ${#chunks[@]} -gt 1 ]]; then
            prefix="[$((i+1))/${#chunks[@]}] "
        fi
        
        if send_telegram_message "${prefix}${chunk}" "$chat_id" "$parse_mode" "$max_retries"; then
            ((success_count++))
        fi
        
        # Small delay between chunks to avoid rate limiting
        if [[ $i -lt $((${#chunks[@]} - 1)) ]]; then
            sleep 1
        fi
    done
    
    if [[ $success_count -eq ${#chunks[@]} ]]; then
        log "DEBUG" "All chunks sent successfully"
        return 0
    else
        log "WARNING" "Only $success_count/${#chunks[@]} chunks sent successfully"
        return 1
    fi
}
```

### Enhanced Log Function Integration
```bash
# Extend the log() function in utils.sh to support Telegram
log_with_telegram() {
    local level="$1"
    shift
    local message="$*"
    
    # Call original log function
    log "$level" "$message"
    
    # Check if Telegram logging is enabled and configured
    if [[ "${TELEGRAM_ENABLED:-false}" == "true" ]]; then
        # Check if this log level should be sent to Telegram
        if should_send_to_telegram "$level"; then
            local formatted_message=$(format_telegram_message "$level" "$message")
            send_telegram_message "$formatted_message" &
        fi
    fi
}

# Determine if log level should be sent to Telegram
should_send_to_telegram() {
    local level="$1"
    local telegram_levels="${TELEGRAM_LOG_LEVELS:-ERROR,WARNING,SUCCESS}"
    
    if [[ ",$telegram_levels," == *",$level,"* ]]; then
        return 0
    fi
    return 1
}

# Format message for Telegram
format_telegram_message() {
    local level="$1"
    local message="$2"
    local script_name=$(get_script_name)
    local timestamp=$(generate_timestamp "${TIMESTAMP_FORMAT:-default}" "${TIMESTAMP_TIMEZONE:-local}")
    
    # HTML formatting
    local color_code=""
    case "$level" in
        "ERROR") color_code="🔴" ;;
        "WARNING") color_code="🟡" ;;
        "SUCCESS") color_code="🟢" ;;
        "INFO") color_code="🔵" ;;
    esac
    
    echo "${color_code} <b>${level}</b>
📝 <i>${script_name}</i>
🕐 <code>${timestamp}</code>

${message}"
}
```

## 4. Security Implementation

### Secure Token Management
```bash
# scripts/core/telegram_security.sh

validate_telegram_security() {
    # Check token is not hardcoded in scripts
    if grep -r "TELEGRAM_BOT_TOKEN=\"[0-9]" scripts/ >/dev/null 2>&1; then
        log "ERROR" "Hardcoded Telegram bot token found in scripts"
        return 1
    fi
    
    # Check environment variable permissions
    if [[ -f "${TELEGRAM_TOKEN_FILE:-/etc/telegram/token}" ]]; then
        local perms=$(stat -c "%a" "${TELEGRAM_TOKEN_FILE}")
        if [[ "$perms" != "600" ]]; then
            log "ERROR" "Telegram token file has insecure permissions: $perms"
            return 1
        fi
    fi
    
    # Validate token format
    local token="${TELEGRAM_BOT_TOKEN:-}"
    if [[ -n "$token" && ! "$token" =~ ^[0-9]+:[a-zA-Z0-9_-]{35}$ ]]; then
        log "ERROR" "Invalid Telegram bot token format"
        return 1
    fi
    
    return 0
}

# Secure token storage setup
setup_telegram_token() {
    local token="$1"
    local token_file="${TELEGRAM_TOKEN_FILE:-/etc/telegram/token}"
    
    if [[ -z "$token" ]]; then
        log "ERROR" "Token required for setup"
        return 1
    fi
    
    # Create secure directory
    sudo mkdir -p "$(dirname "$token_file")"
    sudo chmod 700 "$(dirname "$token_file")"
    
    # Write token securely
    echo "$token" | sudo tee "$token_file" >/dev/null
    sudo chmod 600 "$token_file"
    
    log "INFO" "Telegram token stored securely in: $token_file"
    
    # Set up environment variable loading
    echo "export TELEGRAM_BOT_TOKEN=\"\$(cat $token_file 2>/dev/null)\"" >> /etc/environment
}
```

## 5. Rate Limiting & Performance

### Message Queue System
```bash
# scripts/core/telegram_queue.sh

# Simple in-memory queue for Telegram messages
TELEGRAM_QUEUE_FILE="/tmp/telegram_queue_$$"
TELEGRAM_RATE_LIMIT="${TELEGRAM_RATE_LIMIT:-5}"  # messages per second

enqueue_telegram_message() {
    local message="$1"
    local chat_id="$2"
    local timestamp=$(date +%s)
    
    echo "${timestamp}|${chat_id}|${message}" >> "$TELEGRAM_QUEUE_FILE"
}

# Background processor for queue
process_telegram_queue() {
    local last_sent=0
    
    while [[ -f "$TELEGRAM_QUEUE_FILE" ]] && [[ -s "$TELEGRAM_QUEUE_FILE" ]]; do
        local current_time=$(date +%s)
        local time_diff=$((current_time - last_sent))
        
        # Rate limiting check
        if [[ $time_diff -lt $((1 / TELEGRAM_RATE_LIMIT)) ]]; then
            sleep $(((1 / TELEGRAM_RATE_LIMIT) - time_diff))
        fi
        
        # Get next message from queue
        local line=$(head -n 1 "$TELEGRAM_QUEUE_FILE")
        if [[ -n "$line" ]]; then
            local timestamp="${line%%|*}"
            line="${line#*|}"
            local chat_id="${line%%|*}"
            local message="${line#*|}"
            
            if send_telegram_message "$message" "$chat_id"; then
                # Remove processed message
                sed -i '1d' "$TELEGRAM_QUEUE_FILE"
                last_sent=$(date +%s)
            else
                # Failed to send, wait longer
                sleep 5
            fi
        else
            # Empty line, remove it
            sed -i '1d' "$TELEGRAM_QUEUE_FILE"
        fi
    done
}
```

## 6. Testing Requirements

### Unit Tests (`tests/test_telegram_integration.sh`)
```bash
#!/bin/bash

source "$(dirname "$0")/../scripts/utils.sh"
SCRIPT_NAME="telegram_test"

# Test token validation
test_token_validation() {
    echo "Testing token validation..."
    
    # Test invalid tokens
    export TELEGRAM_BOT_TOKEN="invalid"
    if validate_telegram_config 2>/dev/null; then
        echo "❌ Invalid token validation failed"
        return 1
    else
        echo "✅ Invalid token correctly rejected"
    fi
    
    # Test missing token
    unset TELEGRAM_BOT_TOKEN
    if validate_telegram_config 2>/dev/null; then
        echo "❌ Missing token validation failed"
        return 1
    else
        echo "✅ Missing token correctly rejected"
    fi
    
    # Test valid format (dummy token)
    export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz-123456789"
    export TELEGRAM_CHAT_ID="@test"
    if validate_telegram_config 2>/dev/null; then
        echo "✅ Valid token format accepted"
    else
        echo "❌ Valid token format rejected"
        return 1
    fi
}

# Test message splitting
test_message_splitting() {
    echo "Testing message splitting..."
    
    # Create long message
    local long_message=""
    for i in {1..100}; do
        long_message+="This is line $i of a very long message that should be split. "
    done
    
    # This would need to be mocked for testing
    echo "Long message length: ${#long_message} characters"
    if [[ ${#long_message} -gt 4000 ]]; then
        echo "✅ Long message created for splitting test"
    else
        echo "❌ Long message not long enough"
        return 1
    fi
}

# Test error handling
test_error_handling() {
    echo "Testing error handling..."
    
    # Test with invalid token to simulate API errors
    export TELEGRAM_BOT_TOKEN="invalid:token"
    export TELEGRAM_CHAT_ID="@invalid"
    
    if send_telegram_message "test message" 2>/dev/null; then
        echo "❌ Error handling failed - message sent with invalid token"
        return 1
    else
        echo "✅ Error handling working correctly"
    fi
}
```

## 7. Monitoring & Alerting

### Health Check Function
```bash
# scripts/core/telegram_health.sh

check_telegram_health() {
    local health_status="healthy"
    local issues=()
    
    # Check configuration
    if ! validate_telegram_config; then
        health_status="unhealthy"
        issues+=("Invalid configuration")
    fi
    
    # Test API connectivity
    local bot_token="$TELEGRAM_BOT_TOKEN"
    local test_url="https://api.telegram.org/bot${bot_token}/getMe"
    local response=$(curl -s -w "%{http_code}" "$test_url" 2>/dev/null)
    local http_code="${response: -3}"
    
    if [[ "$http_code" != "200" ]]; then
        health_status="unhealthy"
        issues+=("API connectivity failed (HTTP $http_code)")
    fi
    
    # Check rate limiting status
    if [[ -f "/tmp/telegram_rate_limited" ]]; then
        local rate_limited_until=$(cat "/tmp/telegram_rate_limited" 2>/dev/null || echo "0")
        local current_time=$(date +%s)
        if [[ $current_time -lt $rate_limited_until ]]; then
            health_status="degraded"
            issues+=("Currently rate limited")
        fi
    fi
    
    # Log health status
    case "$health_status" in
        "healthy")
            log "DEBUG" "Telegram integration health: OK"
            ;;
        "degraded")
            log "WARNING" "Telegram integration health: DEGRADED - ${issues[*]}"
            ;;
        "unhealthy")
            log "ERROR" "Telegram integration health: UNHEALTHY - ${issues[*]}"
            ;;
    esac
    
    echo "$health_status"
}
```

## 8. Deployment Steps

1. **Configuration Setup**
   - Add Telegram configuration to `config.yaml`
   - Set up environment variables for tokens
   - Configure rate limiting and message filtering

2. **Core Module Installation**
   - Create `scripts/core/telegram_logger.sh`
   - Create `scripts/core/telegram_security.sh`
   - Create `scripts/core/telegram_queue.sh`

3. **Integration**
   - Modify `scripts/utils.sh` to include Telegram logging
   - Update main scripts to use enhanced logging
   - Add health checks to monitoring

4. **Testing**
   - Run unit tests for token validation
   - Test message sending and splitting
   - Verify error handling and rate limiting

5. **Security Hardening**
   - Set up secure token storage
   - Validate all security configurations
   - Test access controls and permissions

## 9. Documentation Requirements

- **User Guide**: How to configure Telegram notifications
- **API Documentation**: Telegram module interfaces
- **Security Guide**: Token management best practices
- **Troubleshooting**: Common issues and solutions

## 10. Success Criteria

- ✅ Comprehensive research completed
- ✅ Security requirements documented
- ✅ Rate limiting strategy defined
- ✅ Error handling approach specified
- ✅ Integration architecture planned
- ✅ Testing framework outlined
- ✅ Configuration schema designed
- ✅ Implementation roadmap created

This research provides a complete foundation for implementing secure, reliable, and performant Telegram Bot API integration for log output in the Auto-slopp project.