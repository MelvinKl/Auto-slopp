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

# Function to detect and format structured log data (JSON)
format_structured_message() {
    local message="$1"
    local parse_mode="${2:-HTML}"
    
    # Check if message looks like JSON
    if [[ "$message" =~ ^\{.*\}$ ]] || [[ "$message" =~ ^\[.*\]$ ]]; then
        # Try to parse with jq
        local formatted_json
        if formatted_json=$(echo "$message" | jq -r 'to_entries | map("\(.key): \(.value)") | join("\n")' 2>/dev/null); then
            # Successfully parsed as JSON
            if [[ "$parse_mode" == "HTML" ]]; then
                echo "<b>📋 Structured Data:</b>\n<pre><code>${formatted_json}</code></pre>"
            else
                echo "*📋 Structured Data:*\n\`\`\`${formatted_json}\`\`\`"
            fi
            return 0
        fi
    fi
    
    # Check if it contains JSON embedded in the message
    if [[ "$message" =~ \{.*[^[:space:]]\}.* ]]; then
        # Extract JSON parts and format them
        local enhanced_message="$message"
        while [[ "$enhanced_message" =~ (\{[^\{\}]*\}) ]]; do
            local json_part="${BASH_REMATCH[1]}"
            local formatted_json_part
            if formatted_json_part=$(echo "$json_part" | jq -r 'to_entries | map("\(.key): \(.value)") | join(", ")' 2>/dev/null); then
                if [[ "$parse_mode" == "HTML" ]]; then
                    enhanced_message="${enhanced_message//$json_part/<i>$formatted_json_part</i>}"
                else
                    enhanced_message="${enhanced_message//$json_part/_$formatted_json_part_}"
                fi
            else
                break
            fi
        done
        echo "$enhanced_message"
        return 0
    fi
    
    # Return original message if not JSON
    echo "$message"
}

# Function to highlight and format error messages
highlight_error_message() {
    local message="$1"
    local level="$2"
    local parse_mode="${3:-HTML}"
    
    # Only apply error highlighting for ERROR and WARNING levels
    if [[ "$level" != "ERROR" && "$level" != "WARNING" ]]; then
        echo "$message"
        return 0
    fi
    
    local highlighted_message="$message"
    
    # Highlight common error patterns
    local error_patterns=(
        "Error:"
        "ERROR"
        "Failed"
        "Exception"
        "Cannot"
        "Unable"
        "Permission denied"
        "No such file"
        "Command not found"
        "Segmentation fault"
        "Stack trace"
    )
    
    for pattern in "${error_patterns[@]}"; do
        if [[ "$parse_mode" == "HTML" ]]; then
            highlighted_message="${highlighted_message//$pattern/<b><i>$pattern</i></b>}"
        else
            highlighted_message="${highlighted_message//$pattern/*$pattern*}"
        fi
    done
    
    # Highlight file paths and line numbers
    if [[ "$parse_mode" == "HTML" ]]; then
        highlighted_message=$(echo "$highlighted_message" | sed -E 's|(/[a-zA-Z0-9_/-]+\.[a-zA-Z0-9_:-]+)|<code>\1</code>|g')
        highlighted_message=$(echo "$highlighted_message" | sed -E 's|([a-zA-Z0-9_/-]+\.sh:[0-9]+)|<code>\1</code>|g')
    else
        highlighted_message=$(echo "$highlighted_message" | sed -E 's|(/[a-zA-Z0-9_/-]+\.[a-zA-Z0-9_:-]+)|`\1`|g')
        highlighted_message=$(echo "$highlighted_message" | sed -E 's|([a-zA-Z0-9_/-]+\.sh:[0-9]+)|`\1`|g')
    fi
    
    echo "$highlighted_message"
}

# Function to truncate message for Telegram size limits
truncate_message() {
    local message="$1"
    local max_length="${2:-4000}"
    local truncation_indicator="${3:-...}"
    
    if [[ ${#message} -le $max_length ]]; then
        echo "$message"
        return 0
    fi
    
    # Try to truncate at word boundary
    local truncated="${message:0:$((max_length - ${#truncation_indicator}))}"
    
    # Find last space or newline before the truncation point
    local last_space="${truncated##*[[:space:]]}"
    local last_newline="${truncated##*$'\n'}"
    
    if [[ ${#last_space} -gt 0 ]] && [[ ${#last_space} -lt ${#truncated} ]]; then
        truncated="${truncated%${last_space}}${truncation_indicator}"
    elif [[ ${#last_newline} -gt 0 ]] && [[ ${#last_newline} -lt ${#truncated} ]]; then
        truncated="${truncated%${last_newline}}${truncation_indicator}"
    else
        truncated="${truncated}${truncation_indicator}"
    fi
    
    echo "$truncated"
}

# Function to add context information formatting
format_context_info() {
    local script_name="$1"
    local level="$2"
    local parse_mode="${3:-HTML}"
    local additional_context="${4:-}"
    
    local context_section=""
    
    # Script name with icon
    if [[ -n "$script_name" ]]; then
        if [[ "$parse_mode" == "HTML" ]]; then
            context_section+="📝 <i>${script_name}</i>"
        else
            context_section+="📝 _${script_name}_"
        fi
    fi
    
    # Process ID (useful for debugging)
    local pid="$$"
    if [[ "$parse_mode" == "HTML" ]]; then
        context_section+="\n🔢 <code>PID: ${pid}</code>"
    else
        context_section+="\n🔢 \`PID: ${pid}\`"
    fi
    
    # User and host info (for security context)
    local user="${USER:-unknown}"
    local host="${HOSTNAME:-unknown}"
    if [[ "$parse_mode" == "HTML" ]]; then
        context_section+="\n👤 <code>${user}@${host}</code>"
    else
        context_section+="\n👤 \`${user}@${host}\`"
    fi
    
    # Working directory for context
    local working_dir="${PWD:-unknown}"
    # Shorten long paths for better readability
    if [[ ${#working_dir} -gt 40 ]]; then
        working_dir="...${working_dir: -37}"
    fi
    if [[ "$parse_mode" == "HTML" ]]; then
        context_section+="\n📂 <code>${working_dir}</code>"
    else
        context_section+="\n📂 \`${working_dir}\`"
    fi
    
    # Additional context if provided
    if [[ -n "$additional_context" ]]; then
        if [[ "$parse_mode" == "HTML" ]]; then
            context_section+="\n📌 <i>${additional_context}</i>"
        else
            context_section+="\n📌 _${additional_context}_"
        fi
    fi
    
    echo "$context_section"
}

# Function to determine message type and format accordingly
format_message_by_type() {
    local message="$1"
    local level="$2"
    local parse_mode="${3:-HTML}"
    
    # Detect message type
    local message_type="general"
    
    # System/operational messages
    if [[ "$message" =~ ^(Started|Completed|Failed|Running|Executing|Processing) ]]; then
        message_type="operation"
    # Configuration messages
    elif [[ "$message" =~ (config|setting|parameter|option) ]]; then
        message_type="config"
    # Network/API messages
    elif [[ "$message" =~ (HTTP|API|request|response|connection|timeout) ]]; then
        message_type="network"
    # File system messages
    elif [[ "$message" =~ (file|directory|path|created|deleted|modified) ]]; then
        message_type="filesystem"
    # Security messages
    elif [[ "$message" =~ (authentication|permission|access|denied|unauthorized) ]]; then
        message_type="security"
    # Performance messages
    elif [[ "$message" =~ (performance|memory|cpu|time|duration|speed) ]]; then
        message_type="performance"
    fi
    
    # Add type-specific formatting
    local type_icon=""
    case "$message_type" in
        "operation") type_icon="⚙️" ;;
        "config") type_icon="⚙️" ;;
        "network") type_icon="🌐" ;;
        "filesystem") type_icon="📁" ;;
        "security") type_icon="🔒" ;;
        "performance") type_icon="📊" ;;
        *) type_icon="📝" ;;
    esac
    
    if [[ "$parse_mode" == "HTML" ]]; then
        echo "${type_icon} ${message}"
    else
        echo "${type_icon} ${message}"
    fi
}

# Enhanced function to format message for Telegram
format_telegram_message() {
    local level="$1"
    local message="$2"
    local script_name="${3:-$SCRIPT_NAME}"
    local additional_context="${4:-}"
    
    # Generate timestamp with enhanced format support
    local timestamp
    timestamp=$(generate_timestamp "${TIMESTAMP_FORMAT:-readable}" "${TIMESTAMP_TIMEZONE:-local}")
    
    # Get formatting options
    local include_timestamp="${TELEGRAM_FORMATTING_INCLUDE_TIMESTAMP:-true}"
    local include_log_level="${TELEGRAM_FORMATTING_INCLUDE_LOG_LEVEL:-true}"
    local include_script_name="${TELEGRAM_FORMATTING_INCLUDE_SCRIPT_NAME:-true}"
    local include_context="${TELEGRAM_FORMATTING_INCLUDE_CONTEXT:-true}"
    local include_pid="${TELEGRAM_FORMATTING_INCLUDE_PID:-false}"
    local use_emoji="${TELEGRAM_FORMATTING_USE_EMOJI_INDICATORS:-true}"
    local parse_mode="${TELEGRAM_FORMATTING_PARSE_MODE:-HTML}"
    local max_message_length="${TELEGRAM_MAX_MESSAGE_LENGTH:-4000}"
    local enable_structured_formatting="${TELEGRAM_FORMATTING_ENABLE_STRUCTURED:-true}"
    local enable_error_highlighting="${TELEGRAM_FORMATTING_ENABLE_ERROR_HIGHLIGHTING:-true}"
    
    local formatted_message=""
    
    # Header section with level indicator
    if [[ "$use_emoji" == "true" ]]; then
        case "$level" in
            "ERROR") formatted_message+="🔴" ;;
            "WARNING") formatted_message+="🟡" ;;
            "SUCCESS") formatted_message+="🟢" ;;
            "INFO") formatted_message+="🔵" ;;
            "DEBUG") formatted_message+="⚪" ;;
            "CRITICAL") formatted_message="🚨" ;;
            "TRACE") formatted_message+="🔍" ;;
            *) formatted_message+="📝" ;;
        esac
        formatted_message+=" "
    fi
    
    # Add log level with emphasis
    if [[ "$include_log_level" == "true" ]]; then
        if [[ "$parse_mode" == "HTML" ]]; then
            formatted_message+="<b>${level}</b>"
        else
            formatted_message+="*${level}*"
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
    
    # Add context information
    if [[ "$include_context" == "true" ]]; then
        local context_info
        context_info=$(format_context_info "$script_name" "$level" "$parse_mode" "$additional_context")
        formatted_message+="\n${context_info}"
    elif [[ "$include_script_name" == "true" ]]; then
        # Fallback to just script name if full context is disabled
        if [[ "$parse_mode" == "HTML" ]]; then
            formatted_message+="\n📝 <i>${script_name}</i>"
        else
            formatted_message+="\n📝 _${script_name}_"
        fi
    fi
    
    # Process message content
    local processed_message="$message"
    
    # Apply structured data formatting if enabled
    if [[ "$enable_structured_formatting" == "true" ]]; then
        processed_message=$(format_structured_message "$processed_message" "$parse_mode")
    fi
    
    # Apply error highlighting if enabled
    if [[ "$enable_error_highlighting" == "true" ]]; then
        processed_message=$(highlight_error_message "$processed_message" "$level" "$parse_mode")
    fi
    
    # Apply message type formatting
    processed_message=$(format_message_by_type "$processed_message" "$level" "$parse_mode")
    
    # Add separator and processed message
    formatted_message+="\n\n${processed_message}"
    
    # Apply message truncation if needed
    formatted_message=$(truncate_message "$formatted_message" "$max_message_length")
    
    echo "$formatted_message"
}

# Function to convert log level to numeric value for comparison
log_level_to_number() {
    local level="$1"
    case "$level" in
        "TRACE") echo 0 ;;
        "DEBUG") echo 1 ;;
        "INFO") echo 2 ;;
        "SUCCESS") echo 3 ;;
        "WARNING") echo 4 ;;
        "ERROR") echo 5 ;;
        "CRITICAL") echo 6 ;;
        *) echo 2 ;;  # Default to INFO level
    esac
}

# Function to check if log level meets minimum threshold
check_log_level_threshold() {
    local level="$1"
    local min_level="${2:-ERROR}"
    
    local level_num min_level_num
    level_num=$(log_level_to_number "$level")
    min_level_num=$(log_level_to_number "$min_level")
    
    [[ $level_num -ge $min_level_num ]]
}

# Function to check if message matches content filters
check_content_filters() {
    local level="$1"
    local message="$2"
    local script_name="$3"
    
    # Check include patterns (only send if message contains these)
    local include_patterns="${TELEGRAM_FILTERS_INCLUDE_PATTERNS:-}"
    if [[ -n "$include_patterns" ]]; then
        local pattern_found=false
        for pattern in ${include_patterns//,/ }; do
            if [[ "$message" =~ $pattern ]] || [[ "$level" =~ $pattern ]] || [[ "$script_name" =~ $pattern ]]; then
                pattern_found=true
                break
            fi
        done
        [[ "$pattern_found" == "true" ]] || return 1
    fi
    
    # Check exclude patterns (don't send if message contains these)
    local exclude_patterns="${TELEGRAM_FILTERS_EXCLUDE_PATTERNS:-}"
    if [[ -n "$exclude_patterns" ]]; then
        for pattern in ${exclude_patterns//,/ }; do
            if [[ "$message" =~ $pattern ]] || [[ "$level" =~ $pattern ]] || [[ "$script_name" =~ $pattern ]]; then
                return 1
            fi
        done
    fi
    
    return 0
}

# Function to check rate limiting per log level
check_level_rate_limit() {
    local level="$1"
    local current_time
    current_time=$(date +%s)
    
    # Level-specific rate limiting (e.g., limit DEBUG messages more than ERROR messages)
    declare -A level_limits=(
        ["DEBUG"]=10
        ["INFO"]=5
        ["SUCCESS"]=3
        ["WARNING"]=10
        ["ERROR"]=50
        ["CRITICAL"]=100
    )
    
    local per_minute_limit="${level_limits[$level]:-5}"
    local rate_limit_file="/tmp/telegram_rate_limit_${level}_$$"
    
    # Clean old entries (older than 1 minute)
    if [[ -f "$rate_limit_file" ]]; then
        tmp_file=$(mktemp)
        while IFS= read -r timestamp; do
            if [[ $((current_time - timestamp)) -lt 60 ]]; then
                echo "$timestamp" >> "$tmp_file"
            fi
        done < "$rate_limit_file"
        mv "$tmp_file" "$rate_limit_file"
    fi
    
    # Count recent messages
    local recent_count=0
    if [[ -f "$rate_limit_file" ]]; then
        recent_count=$(wc -l < "$rate_limit_file")
    fi
    
    # Check if we've exceeded the limit
    if [[ $recent_count -ge $per_minute_limit ]]; then
        log "DEBUG" "Rate limiting ${level} messages: ${recent_count}/${per_minute_limit} in last minute"
        return 1
    fi
    
    # Record this message
    echo "$current_time" >> "$rate_limit_file"
    return 0
}

# Enhanced function to check if log level should be sent to Telegram
should_send_to_telegram() {
    local level="$1"
    local message="$2"
    local script_name="${3:-$SCRIPT_NAME}"
    
    # Check if Telegram logging is enabled
    if [[ "${TELEGRAM_ENABLED:-false}" != "true" ]]; then
        return 1
    fi
    
    # Enhanced log level filtering with threshold support
    local min_level="${TELEGRAM_FILTERS_MIN_LEVEL:-ERROR}"
    if ! check_log_level_threshold "$level" "$min_level"; then
        return 1
    fi
    
    # Explicit log level list filter (backward compatibility)
    local telegram_levels="${TELEGRAM_FILTERS_LOG_LEVELS:-}"
    if [[ -n "$telegram_levels" ]]; then
        if [[ ",$telegram_levels," != *",$level,"* ]]; then
            return 1
        fi
    fi
    
    # Script filter - only allow specified scripts
    local telegram_scripts="${TELEGRAM_FILTERS_SCRIPTS:-}"
    if [[ -n "$telegram_scripts" ]]; then
        if [[ ",$telegram_scripts," != *",$script_name,"* ]]; then
            return 1
        fi
    fi
    
    # Script exclusion filter - block specified scripts
    local exclude_scripts="${TELEGRAM_FILTERS_EXCLUDE_SCRIPTS:-}"
    if [[ -n "$exclude_scripts" && ",$exclude_scripts," == *",$script_name,"* ]]; then
        return 1
    fi
    
    # Content-based filtering
    if ! check_content_filters "$level" "$message" "$script_name"; then
        return 1
    fi
    
    # Time-based filtering (e.g., only send during certain hours)
    local time_filter="${TELEGRAM_FILTERS_TIME_WINDOW:-}"
    if [[ -n "$time_filter" ]]; then
        local current_hour
        current_hour=$(date +%H)
        local start_hour end_hour
        start_hour=$(echo "$time_filter" | cut -d'-' -f1)
        end_hour=$(echo "$time_filter" | cut -d'-' -f2)
        
        if [[ $current_hour -lt $start_hour ]] || [[ $current_hour -gt $end_hour ]]; then
            log "DEBUG" "Time filter: current hour $current_hour not in window $start_hour-$end_hour"
            return 1
        fi
    fi
    
    # Level-specific rate limiting
    local enable_level_rate_limiting="${TELEGRAM_FILTERS_ENABLE_LEVEL_RATE_LIMITING:-true}"
    if [[ "$enable_level_rate_limiting" == "true" ]]; then
        if ! check_level_rate_limit "$level"; then
            return 1
        fi
    fi
    
    # Check if we're in quiet hours (reduce but don't block all messages)
    local quiet_hours="${TELEGRAM_FILTERS_QUIET_HOURS:-}"
    if [[ -n "$quiet_hours" ]]; then
        local current_hour
        current_hour=$(date +%H)
        local quiet_start quiet_end
        quiet_start=$(echo "$quiet_hours" | cut -d'-' -f1)
        quiet_end=$(echo "$quiet_hours" | cut -d'-' -f2)
        
        if [[ $current_hour -ge $quiet_start ]] && [[ $current_hour -lt $quiet_end ]]; then
            # During quiet hours, only allow ERROR and CRITICAL messages
            if [[ "$level" != "ERROR" && "$level" != "CRITICAL" ]]; then
                log "DEBUG" "Quiet hours: filtering out $level message"
                return 1
            fi
        fi
    fi
    
    return 0
}

# Function to extract structured data from log message
extract_structured_data() {
    local message="$1"
    local structured_data=""
    
    # Extract key-value pairs from structured messages
    if [[ "$message" =~ ([a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*=[[:space:]]*[^[:space:]]+) ]]; then
        structured_data="Extracted key-value pairs found in message"
    fi
    
    # Extract file paths
    local file_paths
    file_paths=$(echo "$message" | grep -oE '[/][a-zA-Z0-9_/.-]+' | sort -u | tr '\n' ', ' | sed 's/,$//')
    if [[ -n "$file_paths" ]]; then
        structured_data="${structured_data:+$structured_data | }Files: $file_paths"
    fi
    
    # Extract URLs
    local urls
    urls=$(echo "$message" | grep -oE 'https?://[a-zA-Z0-9.-]+' | sort -u | tr '\n' ', ' | sed 's/,$//')
    if [[ -n "$urls" ]]; then
        structured_data="${structured_data:+$structured_data | }URLs: $urls"
    fi
    
    # Extract IP addresses
    local ips
    ips=$(echo "$message" | grep -oE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' | sort -u | tr '\n' ', ' | sed 's/,$//')
    if [[ -n "$ips" ]]; then
        structured_data="${structured_data:+$structured_data | }IPs: $ips"
    fi
    
    echo "$structured_data"
}

# Function to add message metadata for better categorization
add_message_metadata() {
    local level="$1"
    local message="$2"
    local script_name="$3"
    
    local metadata=""
    
    # Message complexity analysis
    local message_length=${#message}
    if [[ $message_length -gt 1000 ]]; then
        metadata="${metadata:+$metadata | }Complex message (${message_length} chars)"
    fi
    
    # Command detection
    if [[ "$message" =~ \`[^\`]+\` ]] || [[ "$message" =~ \$[a-zA-Z_][a-zA-Z0-9_]* ]]; then
        metadata="${metadata:+$metadata | }Contains commands"
    fi
    
    # Error code detection
    if [[ "$message" =~ (exit code|status)[[:space:]]*([0-9]+) ]]; then
        local exit_code="${BASH_REMATCH[2]}"
        metadata="${metadata:+$metadata | }Exit code: $exit_code"
    fi
    
    # Performance indicators
    if [[ "$message" =~ ([0-9]+(\.[0-9]+)?[[:space:]]*(ms|sec|min|hour|s|seconds)) ]]; then
        metadata="${metadata:+$metadata | }Performance metric"
    fi
    
    # Security indicators
    if [[ "$message" =~ (password|token|key|secret|credential) ]]; then
        metadata="${metadata:+$metadata | }Security-related"
    fi
    
    echo "$metadata"
}

# Function to sanitize sensitive information from messages
sanitize_message() {
    local message="$1"
    local sanitized="$message"
    
    # Replace common sensitive patterns
    sanitized=$(echo "$sanitized" | sed -E 's/(password|token|key|secret|credential)[[:space:]]*[:=][[:space:]]*[^\s]+/\1=***REDACTED***/gi')
    
    # Replace potential API keys (alphanumeric strings > 20 chars)
    sanitized=$(echo "$sanitized" | sed -E 's/\b[a-zA-Z0-9]{25,}\b/***REDACTED***/g')
    
    # Replace email addresses
    sanitized=$(echo "$sanitized" | sed -E 's/\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b/***EMAIL***/g')
    
    # Replace IP addresses (optional, based on configuration)
    local redact_ips="${TELEGRAM_REDACT_IPS:-false}"
    if [[ "$redact_ips" == "true" ]]; then
        sanitized=$(echo "$sanitized" | sed -E 's/\b([0-9]{1,3}\.){3}[0-9]{1,3}\b/***IP***/g')
    fi
    
    echo "$sanitized"
}

# Enhanced function to send log message to Telegram (main entry point)
send_log_to_telegram() {
    local level="$1"
    shift
    local message="$*"
    local script_name="${SCRIPT_NAME}"
    local additional_context="${1:-}"
    
    # Pre-filter check before any processing
    if ! should_send_to_telegram "$level" "$message" "$script_name"; then
        return 0
    fi
    
    # Sanitize message for sensitive information if enabled
    local enable_sanitization="${TELEGRAM_ENABLE_MESSAGE_SANITIZATION:-false}"
    if [[ "$enable_sanitization" == "true" ]]; then
        message=$(sanitize_message "$message")
    fi
    
    # Extract additional metadata if enabled
    local enable_metadata="${TELEGRAM_ENABLE_MESSAGE_METADATA:-false}"
    if [[ "$enable_metadata" == "true" ]]; then
        local metadata
        metadata=$(add_message_metadata "$level" "$message" "$script_name")
        if [[ -n "$metadata" ]]; then
            additional_context="${additional_context:+$additional_context | }$metadata"
        fi
    fi
    
    # Extract structured data if enabled
    local enable_structured_extraction="${TELEGRAM_ENABLE_STRUCTURED_EXTRACTION:-false}"
    if [[ "$enable_structured_extraction" == "true" ]]; then
        local structured_data
        structured_data=$(extract_structured_data "$message")
        if [[ -n "$structured_data" ]]; then
            additional_context="${additional_context:+$additional_context | }$structured_data"
        fi
    fi
    
    # Format the message with all enhancements
    local formatted_message
    formatted_message=$(format_telegram_message "$level" "$message" "$script_name" "$additional_context")
    
    # Log the attempt locally for debugging
    log "DEBUG" "Sending to Telegram: $level from $script_name"
    
    # Send asynchronously to avoid blocking the main script
    local send_async="${TELEGRAM_SEND_ASYNC:-true}"
    if [[ "$send_async" == "true" ]]; then
        send_telegram_message "$formatted_message" &
    else
        send_telegram_message "$formatted_message"
    fi
    
    return 0
}

# Convenience function for different message types
send_telegram_error() {
    send_log_to_telegram "ERROR" "$@"
}

send_telegram_warning() {
    send_log_to_telegram "WARNING" "$@"
}

send_telegram_info() {
    send_log_to_telegram "INFO" "$@"
}

send_telegram_success() {
    send_log_to_telegram "SUCCESS" "$@"
}

send_telegram_debug() {
    send_log_to_telegram "DEBUG" "$@"
}

send_telegram_critical() {
    send_log_to_telegram "CRITICAL" "$@"
}

# Function to send structured data as Telegram message
send_structured_to_telegram() {
    local level="$1"
    local data="$2"
    local script_name="${3:-$SCRIPT_NAME}"
    
    # Check if data is valid JSON
    if ! echo "$data" | jq . >/dev/null 2>&1; then
        send_log_to_telegram "ERROR" "Invalid JSON data sent to structured logging" "$script_name"
        return 1
    fi
    
    # Create a formatted version of the JSON for Telegram
    local formatted_json
    formatted_json=$(echo "$data" | jq -r 'to_entries | map("\(.key): \(.value)") | join("\n")' 2>/dev/null)
    
    if [[ -n "$formatted_json" ]]; then
        send_log_to_telegram "$level" "📋 Structured Data:\n$formatted_json" "$script_name"
        return 0
    else
        send_log_to_telegram "$level" "Failed to format structured data" "$script_name"
        return 1
    fi
}

# Function to send performance metrics to Telegram
send_performance_to_telegram() {
    local operation="$1"
    local duration="$2"
    local details="${3:-}"
    local script_name="${4:-$SCRIPT_NAME}"
    
    local message="⏱️ Performance: $operation completed in ${duration}s"
    if [[ -n "$details" ]]; then
        message+="\n📊 Details: $details"
    fi
    
    send_log_to_telegram "INFO" "$message" "$script_name"
}

# Function to validate Telegram logging configuration
validate_telegram_logging_config() {
    local errors=()
    local warnings=()
    
    # Check required settings
    if [[ "${TELEGRAM_ENABLED:-false}" == "true" ]]; then
        # Validate bot token
        if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
            errors+=("TELEGRAM_BOT_TOKEN is required when Telegram logging is enabled")
        fi
        
        # Validate chat ID
        if [[ -z "${TELEGRAM_CHAT_ID:-}" ]]; then
            errors+=("TELEGRAM_CHAT_ID is required when Telegram logging is enabled")
        fi
        
        # Validate log level filter
        local valid_levels="TRACE,DEBUG,INFO,SUCCESS,WARNING,ERROR,CRITICAL"
        local configured_levels="${TELEGRAM_FILTERS_LOG_LEVELS:-ERROR,WARNING,SUCCESS}"
        for level in ${configured_levels//,/ }; do
            if [[ ",$valid_levels," != *",$level,"* ]]; then
                warnings+=("Invalid log level in filter: $level (valid: $valid_levels)")
            fi
        done
        
        # Validate message length limit
        local max_length="${TELEGRAM_MAX_MESSAGE_LENGTH:-4000}"
        if [[ ! "$max_length" =~ ^[0-9]+$ ]] || [[ $max_length -lt 100 ]] || [[ $max_length -gt 4096 ]]; then
            warnings+=("TELEGRAM_MAX_MESSAGE_LENGTH should be between 100 and 4096 (current: $max_length)")
        fi
        
        # Validate retry configuration
        local max_retries="${TELEGRAM_MAX_RETRIES:-3}"
        if [[ ! "$max_retries" =~ ^[0-9]+$ ]] || [[ $max_retries -lt 0 ]] || [[ $max_retries -gt 10 ]]; then
            warnings+=("TELEGRAM_MAX_RETRIES should be between 0 and 10 (current: $max_retries)")
        fi
        
        # Validate timeout settings
        local timeout="${TELEGRAM_API_TIMEOUT_SECONDS:-10}"
        if [[ ! "$timeout" =~ ^[0-9]+$ ]] || [[ $timeout -lt 1 ]] || [[ $timeout -gt 60 ]]; then
            warnings+=("TELEGRAM_API_TIMEOUT_SECONDS should be between 1 and 60 (current: $timeout)")
        fi
    fi
    
    # Report validation results
    if [[ ${#errors[@]} -gt 0 ]]; then
        log "ERROR" "Telegram logging configuration errors:"
        for error in "${errors[@]}"; do
            log "ERROR" "  - $error"
        done
        return 1
    fi
    
    if [[ ${#warnings[@]} -gt 0 ]]; then
        log "WARNING" "Telegram logging configuration warnings:"
        for warning in "${warnings[@]}"; do
            log "WARNING" "  - $warning"
        done
    fi
    
    log "DEBUG" "Telegram logging configuration validated successfully"
    return 0
}

# Function to get Telegram logging statistics
get_telegram_logging_stats() {
    local stats_file="/tmp/telegram_stats_$$"
    local current_time
    current_time=$(date +%s)
    
    # Initialize stats file if it doesn't exist
    if [[ ! -f "$stats_file" ]]; then
        cat > "$stats_file" << EOF
{
    "total_messages_sent": 0,
    "total_messages_failed": 0,
    "last_message_time": 0,
    "rate_limit_hits": 0,
    "level_counts": {
        "ERROR": 0,
        "WARNING": 0,
        "INFO": 0,
        "SUCCESS": 0,
        "DEBUG": 0,
        "CRITICAL": 0,
        "TRACE": 0
    },
    "start_time": $current_time
}
EOF
    fi
    
    # Read and return stats
    cat "$stats_file"
}

# Function to update Telegram logging statistics
update_telegram_stats() {
    local level="$1"
    local success="$2"  # true or false
    
    local stats_file="/tmp/telegram_stats_$$"
    local current_time
    current_time=$(date +%s)
    
    # Ensure stats file exists
    get_telegram_logging_stats >/dev/null
    
    # Update stats
    if [[ "$success" == "true" ]]; then
        jq --arg level "$level" --arg time "$current_time" '
            .total_messages_sent += 1 |
            .last_message_time = ($time | tonumber) |
            .level_counts[$level] += 1
        ' "$stats_file" > "${stats_file}.tmp" && mv "${stats_file}.tmp" "$stats_file"
    else
        jq --arg time "$current_time" '
            .total_messages_failed += 1 |
            .last_message_time = ($time | tonumber)
        ' "$stats_file" > "${stats_file}.tmp" && mv "${stats_file}.tmp" "$stats_file"
    fi
}

# Enhanced function to cleanup temporary files
cleanup_telegram_files() {
    # Clean main files
    [[ -f "$TELEGRAM_QUEUE_FILE" ]] && rm -f "$TELEGRAM_QUEUE_FILE"
    [[ -f "$TELEGRAM_RATE_LIMIT_FILE" ]] && rm -f "$TELEGRAM_RATE_LIMIT_FILE"
    
    # Clean level-specific rate limit files
    for level in TRACE DEBUG INFO SUCCESS WARNING ERROR CRITICAL; do
        local level_file="/tmp/telegram_rate_limit_${level}_$$"
        [[ -f "$level_file" ]] && rm -f "$level_file"
    done
    
    # Clean stats file
    local stats_file="/tmp/telegram_stats_$$"
    [[ -f "$stats_file" ]] && rm -f "$stats_file"
    
    # Clean any temporary backup files
    for tmp_file in /tmp/telegram_*_$$; do
        [[ -f "$tmp_file" ]] && rm -f "$tmp_file"
    done
    
    log "DEBUG" "Telegram temporary files cleaned up"
}

# Function to test Telegram logging configuration
test_telegram_logging() {
    local test_level="${1:-INFO}"
    local test_message="${2:-Test message from Auto-slopp Telegram logging system}"
    
    log "INFO" "Testing Telegram logging configuration..."
    
    # Validate configuration first
    if ! validate_telegram_logging_config; then
        log "ERROR" "Telegram logging configuration validation failed"
        return 1
    fi
    
    # Send test message
    if send_log_to_telegram "$test_level" "$test_message" "${SCRIPT_NAME}"; then
        log "SUCCESS" "Telegram logging test completed successfully"
        return 0
    else
        log "ERROR" "Telegram logging test failed"
        return 1
    fi
}

# Enhanced send function with statistics tracking
send_telegram_message_with_stats() {
    local message="$1"
    local level="${2:-INFO}"
    local result
    
    # Send the message
    if result=$(send_telegram_message "$message" 2>&1); then
        update_telegram_stats "$level" "true"
        return 0
    else
        update_telegram_stats "$level" "false"
        log "ERROR" "Telegram message failed: $result"
        return 1
    fi
}

# Cleanup on exit
trap cleanup_telegram_files EXIT

# Validate configuration on module load
if [[ "${TELEGRAM_ENABLED:-false}" == "true" ]]; then
    validate_telegram_logging_config
fi

log "DEBUG" "Enhanced Telegram logger module loaded"