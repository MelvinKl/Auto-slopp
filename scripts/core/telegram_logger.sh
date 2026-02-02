#!/bin/bash

# Telegram Bot API Integration Module
# Handles Telegram message sending with rate limiting, error handling, and security
# Integrates with existing Auto-slopp logging system

# Set script name for logging identification
SCRIPT_NAME="telegram_logger"

# Source utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../utils.sh"
source "${SCRIPT_DIR}/../yaml_config.sh"

# Set up error handling
setup_error_handling

# Global variables for Telegram state
declare -g TELEGRAM_QUEUE_FILE="/tmp/telegram_queue_$$"
declare -g TELEGRAM_RATE_LIMIT_FILE="/tmp/telegram_rate_limit_$$"
declare -g TELEGRAM_LAST_SENT_TIME=0
declare -g TELEGRAM_MESSAGE_COUNT=0

# Function to validate Telegram configuration
validate_telegram_config() {
    local bot_token="${TELEGRAM_BOT_TOKEN:-}"
    local chat_id="${TELEGRAM_CHAT_ID:-}"
    
    # Check if Telegram is enabled
    if [[ "${TELEGRAM_ENABLED:-false}" != "true" ]]; then
        log "DEBUG" "Telegram logging is disabled"
        return 1
    fi
    
    # Validate bot token
    if [[ -z "$bot_token" ]]; then
        log "ERROR" "TELEGRAM_BOT_TOKEN not configured"
        return 1
    fi
    
    # Validate bot token format (basic pattern matching)
    if [[ ! "$bot_token" =~ ^[0-9]+:[a-zA-Z0-9_-]{35}$ ]]; then
        log "ERROR" "Invalid bot token format"
        return 1
    fi
    
    # Validate chat ID
    if [[ -z "$chat_id" ]]; then
        log "ERROR" "TELEGRAM_CHAT_ID not configured"
        return 1
    fi
    
    log "DEBUG" "Telegram configuration validated successfully"
    return 0
}

# Function to escape HTML characters for Telegram messages
escape_html() {
    local text="$1"
    # Escape HTML special characters
    text="${text//&/&amp;}"
    text="${text//</&lt;}"
    text="${text//>/&gt;}"
    text="${text//\"/&quot;}"
    echo "$text"
}

# Function to build JSON payload for Telegram API
build_telegram_payload() {
    local message="$1"
    local chat_id="${2:-${TELEGRAM_CHAT_ID}}"
    local parse_mode="${3:-HTML}"
    
    local payload
    if [[ "$parse_mode" == "HTML" ]]; then
        message=$(escape_html "$message")
    fi
    
    payload=$(cat << EOF
{
    "chat_id": "$chat_id",
    "text": "$message",
    "parse_mode": "$parse_mode",
    "disable_web_page_preview": true,
    "disable_notification": false
}
EOF
)
    echo "$payload"
}

# Function to send HTTP request to Telegram API
send_telegram_request() {
    local payload="$1"
    local bot_token="${TELEGRAM_BOT_TOKEN}"
    local timeout="${TELEGRAM_API_TIMEOUT_SECONDS:-10}"
    local url="https://api.telegram.org/bot${bot_token}/sendMessage"
    
    local response
    if response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --connect-timeout "$timeout" \
        --max-time "$timeout" \
        "$url" 2>/dev/null); then
        
        local http_code="${response: -3}"
        local response_body="${response%???}"
        
        echo "$http_code|$response_body"
        return 0
    else
        echo "000|Connection failed"
        return 1
    fi
}

# Function to handle Telegram API responses
handle_telegram_response() {
    local response="$1"
    local attempt="$2"
    local max_attempts="$3"
    
    local http_code="${response%%|*}"
    local response_body="${response#*|}"
    
    case "$http_code" in
        "200")
            log "DEBUG" "Telegram message sent successfully (attempt $attempt/$max_attempts)"
            return 0
            ;;
        "429")
            # Rate limited
            local retry_after
            retry_after=$(echo "$response_body" | jq -r '.parameters.retry_after // 1' 2>/dev/null || echo "1")
            log "WARNING" "Rate limited by Telegram, waiting ${retry_after}s"
            echo "RATE_LIMIT:$retry_after"
            return 2
            ;;
        40[0-9])
            # Client errors (4xx) - don't retry
            local error_desc
            error_desc=$(echo "$response_body" | jq -r '.description // "Unknown client error"' 2>/dev/null || echo "Unknown client error")
            log "ERROR" "Telegram client error $http_code: $error_desc"
            return 3
            ;;
        5[0-9])
            # Server errors (5xx) - retry
            local error_desc
            error_desc=$(echo "$response_body" | jq -r '.description // "Unknown server error"' 2>/dev/null || echo "Unknown server error")
            log "WARNING" "Telegram server error $http_code (attempt $attempt/$max_attempts): $error_desc"
            return 4
            ;;
        "000")
            # Connection failed
            log "ERROR" "Failed to connect to Telegram API (attempt $attempt/$max_attempts)"
            return 5
            ;;
        *)
            # Unknown response
            log "ERROR" "Unknown Telegram response: $http_code (attempt $attempt/$max_attempts)"
            return 6
            ;;
    esac
}

# Function to send a message to Telegram with comprehensive error handling
send_telegram_message() {
    local message="$1"
    local chat_id="${2:-${TELEGRAM_CHAT_ID}}"
    local parse_mode="${3:-HTML}"
    local max_retries="${4:-3}"
    
    if ! validate_telegram_config; then
        return 1
    fi
    
    # Check message length and split if necessary
    local max_length="${TELEGRAM_MAX_MESSAGE_LENGTH:-4000}"
    if [[ ${#message} -gt $max_length ]]; then
        log "DEBUG" "Message too long (${#message} chars), splitting into chunks"
        return send_message_chunks "$message" "$chat_id" "$parse_mode" "$max_retries"
    fi
    
    # Build JSON payload
    local payload
    if ! payload=$(build_telegram_payload "$message" "$chat_id" "$parse_mode"); then
        log "ERROR" "Failed to build Telegram payload"
        return 1
    fi
    
    # Send with retry logic
    local base_delay="${TELEGRAM_RETRY_BASE_DELAY:-1.0}"
    local max_delay="${TELEGRAM_RETRY_MAX_DELAY:-30.0}"
    local backoff_multiplier="${TELEGRAM_RETRY_BACKOFF_MULTIPLIER:-2}"
    local use_jitter="${TELEGRAM_RETRY_JITTER:-true}"
    
    for ((attempt=1; attempt<=max_retries; attempt++)); do
        # Rate limiting check
        if ! check_rate_limit; then
            return 1
        fi
        
        # Send request
        local response
        if response=$(send_telegram_request "$payload"); then
            local result
            result=$(handle_telegram_response "$response" "$attempt" "$max_retries")
            case "$result" in
                0)
                    # Success
                    update_rate_limit
                    return 0
                    ;;
                2)
                    # Rate limited
                    local retry_after="${result#RATE_LIMIT:}"
                    sleep "$retry_after"
                    continue
                    ;;
                3)
                    # Client error - don't retry
                    return 1
                    ;;
                *)
                    # Server error or other - retry
                    if [[ $attempt -lt $max_retries ]]; then
                        local delay
                        delay=$(calculate_backoff_delay "$attempt" "$base_delay" "$max_delay" "$backoff_multiplier" "$use_jitter")
                        sleep "$delay"
                    fi
                    ;;
            esac
        else
            log "ERROR" "Failed to send Telegram request (attempt $attempt/$max_retries)"
            if [[ $attempt -lt $max_retries ]]; then
                local delay
                delay=$(calculate_backoff_delay "$attempt" "$base_delay" "$max_delay" "$backoff_multiplier" "$use_jitter")
                sleep "$delay"
            fi
        fi
    done
    
    log "ERROR" "Failed to send Telegram message after $max_retries attempts"
    return 1
}

# Function to calculate exponential backoff delay with optional jitter
calculate_backoff_delay() {
    local attempt="$1"
    local base_delay="$2"
    local max_delay="$3"
    local multiplier="$4"
    local use_jitter="$5"
    
    local delay
    delay=$(echo "$base_delay * $multiplier ^ ($attempt - 1)" | bc -l 2>/dev/null || echo "$base_delay")
    
    # Cap at maximum delay
    if (( $(echo "$delay > $max_delay" | bc -l 2>/dev/null || echo "0") )); then
        delay="$max_delay"
    fi
    
    # Add jitter if enabled
    if [[ "$use_jitter" == "true" ]]; then
        local jitter
        jitter=$(echo "$delay * 0.1 * $RANDOM / 32767" | bc -l 2>/dev/null || echo "0")
        delay=$(echo "$delay + $jitter" | bc -l 2>/dev/null || echo "$delay")
    fi
    
    # Convert to integer seconds
    echo "${delay%.*}"
}

# Function to check rate limiting
check_rate_limit() {
    local messages_per_second="${TELEGRAM_RATE_LIMITING_MESSAGES_PER_SECOND:-5}"
    local current_time
    current_time=$(date +%s)
    
    # Simple rate limiting - check if we're sending too fast
    local time_diff=$((current_time - TELEGRAM_LAST_SENT_TIME))
    local min_interval=$((1 / messages_per_second))
    
    if [[ $time_diff -lt $min_interval ]]; then
        local sleep_time=$((min_interval - time_diff))
        log "DEBUG" "Rate limiting: sleeping for ${sleep_time}s"
        sleep "$sleep_time"
    fi
    
    return 0
}

# Function to update rate limiting state
update_rate_limit() {
    TELEGRAM_LAST_SENT_TIME=$(date +%s)
    ((TELEGRAM_MESSAGE_COUNT++))
}

# Function to split long messages into chunks
send_message_chunks() {
    local message="$1"
    local chat_id="$2"
    local parse_mode="$3"
    local max_retries="$4"
    local chunk_size="${TELEGRAM_MAX_MESSAGE_LENGTH:-4000}"
    local chunks=()
    
    # Split by lines to preserve readability
    local current_chunk=""
    while IFS= read -r line; do
        if [[ $(( ${#current_chunk} + ${#line} + 1 )) -gt $chunk_size ]]; then
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

# Function to format message for Telegram
format_telegram_message() {
    local level="$1"
    local message="$2"
    local script_name="${3:-$SCRIPT_NAME}"
    local timestamp
    
    timestamp=$(generate_timestamp "${TIMESTAMP_FORMAT:-default}" "${TIMESTAMP_TIMEZONE:-local}")
    
    # Get formatting options
    local include_timestamp="${TELEGRAM_FORMATTING_INCLUDE_TIMESTAMP:-true}"
    local include_log_level="${TELEGRAM_FORMATTING_INCLUDE_LOG_LEVEL:-true}"
    local include_script_name="${TELEGRAM_FORMATTING_INCLUDE_SCRIPT_NAME:-true}"
    local use_emoji="${TELEGRAM_FORMATTING_USE_EMOJI_INDICATORS:-true}"
    local parse_mode="${TELEGRAM_FORMATTING_PARSE_MODE:-HTML}"
    
    local formatted_message=""
    
    # Add emoji and log level
    if [[ "$use_emoji" == "true" ]]; then
        case "$level" in
            "ERROR") formatted_message+="🔴" ;;
            "WARNING") formatted_message+="🟡" ;;
            "SUCCESS") formatted_message+="🟢" ;;
            "INFO") formatted_message+="🔵" ;;
            "DEBUG") formatted_message+="⚪" ;;
            *) formatted_message+="📝" ;;
        esac
        formatted_message+=" "
    fi
    
    if [[ "$include_log_level" == "true" ]]; then
        if [[ "$parse_mode" == "HTML" ]]; then
            formatted_message+="<b>${level}</b>"
        else
            formatted_message+="*${level}*"
        fi
    fi
    
    # Add script name
    if [[ "$include_script_name" == "true" ]]; then
        if [[ "$parse_mode" == "HTML" ]]; then
            formatted_message+="\n📝 <i>${script_name}</i>"
        else
            formatted_message+="\n📝 _${script_name}_"
        fi
    fi
    
    # Add timestamp
    if [[ "$include_timestamp" == "true" ]]; then
        if [[ "$parse_mode" == "HTML" ]]; then
            formatted_message+="\n🕐 <code>${timestamp}</code>"
        else
            formatted_message+="\n🕐 \`${timestamp}\`"
        fi
    fi
    
    # Add message content
    formatted_message+="\n\n${message}"
    
    echo "$formatted_message"
}

# Function to check if log level should be sent to Telegram
should_send_to_telegram() {
    local level="$1"
    local script_name="${2:-$SCRIPT_NAME}"
    
    # Check if Telegram logging is enabled
    if [[ "${TELEGRAM_ENABLED:-false}" != "true" ]]; then
        return 1
    fi
    
    # Check log level filter
    local telegram_levels="${TELEGRAM_FILTERS_LOG_LEVELS:-ERROR,WARNING,SUCCESS}"
    if [[ ",$telegram_levels," != *",$level,"* ]]; then
        return 1
    fi
    
    # Check script filter
    local telegram_scripts="${TELEGRAM_FILTERS_SCRIPTS:-}"
    if [[ -n "$telegram_scripts" && ",$telegram_scripts," != *",$script_name,"* ]]; then
        return 1
    fi
    
    # Check exclude patterns
    local exclude_patterns="${TELEGRAM_FILTERS_EXCLUDE_PATTERNS:-}"
    if [[ -n "$exclude_patterns" ]]; then
        # This is a simplified check - in practice, you'd want more sophisticated pattern matching
        for pattern in ${exclude_patterns//,/ }; do
            if [[ "$level" =~ $pattern ]]; then
                return 1
            fi
        done
    fi
    
    return 0
}

# Function to send log message to Telegram (main entry point)
send_log_to_telegram() {
    local level="$1"
    shift
    local message="$*"
    local script_name="${SCRIPT_NAME}"
    
    if ! should_send_to_telegram "$level" "$script_name"; then
        return 0
    fi
    
    local formatted_message
    formatted_message=$(format_telegram_message "$level" "$message" "$script_name")
    
    # Send asynchronously to avoid blocking the main script
    send_telegram_message "$formatted_message" &
    
    return 0
}

# Function to cleanup temporary files
cleanup_telegram_files() {
    [[ -f "$TELEGRAM_QUEUE_FILE" ]] && rm -f "$TELEGRAM_QUEUE_FILE"
    [[ -f "$TELEGRAM_RATE_LIMIT_FILE" ]] && rm -f "$TELEGRAM_RATE_LIMIT_FILE"
}

# Cleanup on exit
trap cleanup_telegram_files EXIT

log "DEBUG" "Telegram logger module loaded"