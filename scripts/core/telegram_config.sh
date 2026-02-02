#!/bin/bash

# Telegram Configuration Management Module
# Handles configuration validation, reloading, and backup
# Ensures configuration consistency and proper handling of runtime changes

# Set script name for logging identification
SCRIPT_NAME="telegram_config"

# Source utilities and modules
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../utils.sh"
source "${SCRIPT_DIR}/telegram_logger.sh"
source "${SCRIPT_DIR}/telegram_security.sh"

# Set up error handling
setup_error_handling

# Configuration validation constants
readonly CONFIG_VALIDATION_STRICT="strict"
readonly CONFIG_VALIDATION_WARN="warn"
readonly CONFIG_VALIDATION_RELAXED="relaxed"

# Global configuration state
declare -g TELEGRAM_CONFIG_FILE=""
declare -g TELEGRAM_CONFIG_HASH=""
declare -g TELEGRAM_CONFIG_LAST_CHECK=0
declare -g TELEGRAM_CONFIG_BACKUP_DIR="/tmp/telegram_config_backups"

# Function to validate configuration value
validate_config_value() {
    local key="$1"
    local value="$2"
    local validation_level="${3:-$CONFIG_VALIDATION_STRICT}"
    
    case "$key" in
        "telegram.enabled")
            if [[ "$value" != "true" ]] && [[ "$value" != "false" ]]; then
                case "$validation_level" in
                    "$CONFIG_VALIDATION_STRICT")
                        log "ERROR" "Invalid value for telegram.enabled: $value (must be true or false)"
                        return 1
                        ;;
                    "$CONFIG_VALIDATION_WARN")
                        log "WARNING" "Invalid value for telegram.enabled: $value (should be true or false)"
                        return 0
                        ;;
                    "$CONFIG_VALIDATION_RELAXED")
                        return 0
                        ;;
                esac
            fi
            ;;
        "telegram.bot_token")
            if [[ -n "$value" ]] && [[ "$value" != "\${TELEGRAM_BOT_TOKEN}" ]]; then
                # Check if it's a hardcoded token
                if [[ "$value" =~ ^[0-9]+:[a-zA-Z0-9_-]{35}$ ]]; then
                    if [[ "$validation_level" == "$CONFIG_VALIDATION_STRICT" ]]; then
                        log "ERROR" "Hardcoded bot token detected in configuration. Use environment variable instead."
                        return 1
                    else
                        log "WARNING" "Hardcoded bot token detected in configuration. Environment variable recommended."
                    fi
                fi
            fi
            ;;
        "telegram.default_chat_id")
            if [[ -n "$value" ]] && ! validate_chat_id "$value" 2>/dev/null; then
                case "$validation_level" in
                    "$CONFIG_VALIDATION_STRICT")
                        log "ERROR" "Invalid chat_id format: $value"
                        return 1
                        ;;
                    "$CONFIG_VALIDATION_WARN")
                        log "WARNING" "Invalid chat_id format: $value"
                        return 0
                        ;;
                    "$CONFIG_VALIDATION_RELAXED")
                        return 0
                        ;;
                esac
            fi
            ;;
        "telegram.api_timeout_seconds")
            if ! [[ "$value" =~ ^[0-9]+$ ]] || [[ $value -lt 1 ]] || [[ $value -gt 300 ]]; then
                case "$validation_level" in
                    "$CONFIG_VALIDATION_STRICT")
                        log "ERROR" "Invalid API timeout: $value (must be 1-300 seconds)"
                        return 1
                        ;;
                    "$CONFIG_VALIDATION_WARN")
                        log "WARNING" "API timeout may be problematic: $value (recommended: 5-30 seconds)"
                        return 0
                        ;;
                    "$CONFIG_VALIDATION_RELAXED")
                        return 0
                        ;;
                esac
            fi
            ;;
        "telegram.rate_limiting.messages_per_second")
            if ! [[ "$value" =~ ^[0-9]+$ ]] || [[ $value -lt 1 ]] || [[ $value -gt 30 ]]; then
                case "$validation_level" in
                    "$CONFIG_VALIDATION_STRICT")
                        log "ERROR" "Invalid rate limit: $value (must be 1-30 messages/second)"
                        return 1
                        ;;
                    "$CONFIG_VALIDATION_WARN")
                        log "WARNING" "Rate limit may be problematic: $value (recommended: 1-10 messages/second)"
                        return 0
                        ;;
                    "$CONFIG_VALIDATION_RELAXED")
                        return 0
                        ;;
                esac
            fi
            ;;
        "telegram.formatting.max_message_length")
            if ! [[ "$value" =~ ^[0-9]+$ ]] || [[ $value -lt 100 ]] || [[ $value -gt 4096 ]]; then
                case "$validation_level" in
                    "$CONFIG_VALIDATION_STRICT")
                        log "ERROR" "Invalid max message length: $value (must be 100-4096 characters)"
                        return 1
                        ;;
                    "$CONFIG_VALIDATION_WARN")
                        log "WARNING" "Message length may be problematic: $value (recommended: 2000-4000 characters)"
                        return 0
                        ;;
                    "$CONFIG_VALIDATION_RELAXED")
                        return 0
                        ;;
                esac
            fi
            ;;
        "telegram.retry.max_attempts")
            if ! [[ "$value" =~ ^[0-9]+$ ]] || [[ $value -lt 0 ]] || [[ $value -gt 10 ]]; then
                case "$validation_level" in
                    "$CONFIG_VALIDATION_STRICT")
                        log "ERROR" "Invalid retry attempts: $value (must be 0-10)"
                        return 1
                        ;;
                    "$CONFIG_VALIDATION_WARN")
                        log "WARNING" "Retry attempts may be problematic: $value (recommended: 1-5)"
                        return 0
                        ;;
                    "$CONFIG_VALIDATION_RELAXED")
                        return 0
                        ;;
                esac
            fi
            ;;
    esac
    
    return 0
}

# Function to validate entire Telegram configuration
validate_telegram_configuration() {
    local config_file="$1"
    local validation_level="${2:-${TELEGRAM_CONFIG_VALIDATION_STRICTNESS:-$CONFIG_VALIDATION_STRICT}}"
    
    if [[ ! -f "$config_file" ]]; then
        log "ERROR" "Configuration file not found: $config_file"
        return 1
    fi
    
    log "INFO" "Validating Telegram configuration with level: $validation_level"
    
    local validation_errors=0
    local validation_warnings=0
    
    # Validate essential Telegram configuration
    local telegram_keys=(
        "telegram.enabled"
        "telegram.bot_token"
        "telegram.default_chat_id"
        "telegram.api_timeout_seconds"
        "telegram.rate_limiting.messages_per_second"
        "telegram.formatting.max_message_length"
        "telegram.retry.max_attempts"
    )
    
    for key in "${telegram_keys[@]}"; do
        local value
        value=$(read_yaml_nested_config "$config_file" "$key" "")
        
        if [[ -z "$value" ]]; then
            case "$validation_level" in
                "$CONFIG_VALIDATION_STRICT")
                    log "ERROR" "Required configuration key missing: $key"
                    ((validation_errors++))
                    ;;
                "$CONFIG_VALIDATION_WARN")
                    log "WARNING" "Configuration key missing: $key"
                    ((validation_warnings++))
                    ;;
            esac
        else
            if ! validate_config_value "$key" "$value" "$validation_level"; then
                ((validation_errors++))
            fi
        fi
    done
    
    # Validate nested configurations
    local rate_limit_keys=(
        "telegram.rate_limiting.burst_size"
        "telegram.rate_limiting.backoff_multiplier"
        "telegram.rate_limiting.max_backoff_seconds"
    )
    
    for key in "${rate_limit_keys[@]}"; do
        local value
        value=$(read_yaml_nested_config "$config_file" "$key" "")
        if [[ -n "$value" ]] && ! validate_config_value "$key" "$value" "$validation_level"; then
            ((validation_errors++))
        fi
    done
    
    # Validate filter configurations
    local filters_keys=(
        "telegram.filters.log_levels"
        "telegram.filters.scripts"
    )
    
    for key in "${filters_keys[@]}"; do
        local value
        value=$(read_yaml_nested_config "$config_file" "$key" "")
        if [[ -n "$value" ]]; then
            # Validate comma-separated lists
            if [[ "$value" =~ ^[a-zA-Z0-9_,]+$ ]]; then
                log "DEBUG" "Valid comma-separated list for $key: $value"
            else
                case "$validation_level" in
                    "$CONFIG_VALIDATION_STRICT")
                        log "ERROR" "Invalid comma-separated list for $key: $value"
                        ((validation_errors++))
                        ;;
                    "$CONFIG_VALIDATION_WARN")
                        log "WARNING" "Potentially invalid list for $key: $value"
                        ((validation_warnings++))
                        ;;
                esac
            fi
        fi
    done
    
    # Report validation results
    if [[ $validation_errors -eq 0 ]] && [[ $validation_warnings -eq 0 ]]; then
        log "SUCCESS" "Telegram configuration validation passed"
        return 0
    elif [[ $validation_errors -eq 0 ]] && [[ $validation_warnings -gt 0 ]]; then
        log "WARNING" "Telegram configuration validation passed with $validation_warnings warnings"
        return 0
    else
        log "ERROR" "Telegram configuration validation failed with $validation_errors errors and $validation_warnings warnings"
        return 1
    fi
}

# Function to calculate configuration file hash
calculate_config_hash() {
    local config_file="$1"
    
    if [[ ! -f "$config_file" ]]; then
        echo ""
        return 1
    fi
    
    # Calculate hash of relevant Telegram configuration sections
    local hash
    hash=$(awk '
    /^telegram:/ { in_telegram = 1; next }
    /^[a-zA-Z_][a-zA-Z0-9_-]*:/ && in_telegram { in_telegram = 0 }
    in_telegram { print }
    ' "$config_file" | sha256sum | cut -d' ' -f1)
    
    echo "$hash"
}

# Function to backup current configuration
backup_telegram_configuration() {
    local config_file="$1"
    local backup_dir="${2:-$TELEGRAM_CONFIG_BACKUP_DIR}"
    
    if [[ ! -f "$config_file" ]]; then
        log "ERROR" "Cannot backup configuration file: $config_file"
        return 1
    fi
    
    # Create backup directory
    mkdir -p "$backup_dir"
    
    # Create backup with timestamp
    local timestamp
    timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="${backup_dir}/telegram_config_${timestamp}.yaml"
    
    # Extract only Telegram section for backup
    awk '
    /^telegram:/ { in_telegram = 1; print; next }
    /^[a-zA-Z_][a-zA-Z0-9_-]*:/ && in_telegram { in_telegram = 0 }
    in_telegram { print }
    ' "$config_file" > "$backup_file"
    
    if [[ $? -eq 0 ]]; then
        log "INFO" "Telegram configuration backed up to: $backup_file"
        
        # Clean up old backups (keep last 10)
        ls -t "${backup_dir}/telegram_config_"*.yaml 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null
        
        return 0
    else
        log "ERROR" "Failed to backup Telegram configuration"
        return 1
    fi
}

# Function to restore configuration from backup
restore_telegram_configuration() {
    local backup_file="$1"
    local config_file="$2"
    
    if [[ ! -f "$backup_file" ]]; then
        log "ERROR" "Backup file not found: $backup_file"
        return 1
    fi
    
    if [[ ! -f "$config_file" ]]; then
        log "ERROR" "Configuration file not found: $config_file"
        return 1
    fi
    
    # Validate backup before restoring
    if ! validate_telegram_configuration "$backup_file" "$CONFIG_VALIDATION_STRICT"; then
        log "ERROR" "Backup configuration validation failed"
        return 1
    fi
    
    # Create backup of current configuration before restoring
    backup_telegram_configuration "$config_file"
    
    # Remove existing telegram section from config
    local temp_file="${config_file}.tmp"
    awk '
    /^telegram:/ { skip = 1; next }
    /^[a-zA-Z_][a-zA-Z0-9_-]*:/ && skip { skip = 0; next }
    !skip { print }
    ' "$config_file" > "$temp_file"
    
    # Append backup telegram section
    cat "$backup_file" >> "$temp_file"
    mv "$temp_file" "$config_file"
    
    log "SUCCESS" "Telegram configuration restored from: $backup_file"
    return 0
}

# Function to check if configuration has changed
has_configuration_changed() {
    local config_file="$1"
    
    if [[ -z "$TELEGRAM_CONFIG_HASH" ]]; then
        # First time checking
        TELEGRAM_CONFIG_HASH=$(calculate_config_hash "$config_file")
        TELEGRAM_CONFIG_FILE="$config_file"
        return 1  # Assume it's new/changed
    fi
    
    if [[ "$config_file" != "$TELEGRAM_CONFIG_FILE" ]]; then
        # Different configuration file
        TELEGRAM_CONFIG_FILE="$config_file"
        TELEGRAM_CONFIG_HASH=$(calculate_config_hash "$config_file")
        return 1
    fi
    
    local current_hash
    current_hash=$(calculate_config_hash "$config_file")
    
    if [[ "$current_hash" != "$TELEGRAM_CONFIG_HASH" ]]; then
        TELEGRAM_CONFIG_HASH="$current_hash"
        return 0  # Configuration has changed
    fi
    
    return 1  # No changes
}

# Function to reload Telegram configuration
reload_telegram_configuration() {
    local config_file="$1"
    local force="${2:-false}"
    
    if [[ ! -f "$config_file" ]]; then
        log "ERROR" "Configuration file not found: $config_file"
        return 1
    fi
    
    # Check if reload is needed
    if [[ "$force" != "true" ]] && ! has_configuration_changed "$config_file"; then
        log "DEBUG" "Configuration unchanged, no reload needed"
        return 0
    fi
    
    log "INFO" "Reloading Telegram configuration from: $config_file"
    
    # Backup current configuration if enabled
    if [[ "${TELEGRAM_CONFIG_BACKUP_CONFIGURATION:-true}" == "true" ]]; then
        backup_telegram_configuration "$config_file"
    fi
    
    # Validate new configuration
    if ! validate_telegram_configuration "$config_file"; then
        log "ERROR" "Configuration validation failed, reload aborted"
        return 1
    fi
    
    # Reload configuration variables
    if load_config "$config_file"; then
        log "SUCCESS" "Telegram configuration reloaded successfully"
        
        # Re-initialize Telegram modules if needed
        if [[ "${TELEGRAM_ENABLED:-false}" == "true" ]]; then
            # Re-initialize queue system
            if declare -F init_telegram_queue >/dev/null 2>&1; then
                init_telegram_queue
            fi
            
            # Setup health monitoring
            if declare -F setup_health_monitoring >/dev/null 2>&1; then
                setup_health_monitoring
            fi
        fi
        
        return 0
    else
        log "ERROR" "Failed to reload Telegram configuration"
        return 1
    fi
}

# Function to start configuration watcher (background process)
start_configuration_watcher() {
    local config_file="$1"
    local interval_seconds="${TELEGRAM_CONFIG_CONFIG_FILE_WATCH_INTERVAL_SECONDS:-30}"
    
    if [[ "${TELEGRAM_CONFIG_AUTO_RELOAD:-true}" != "true" ]]; then
        log "INFO" "Configuration auto-reload is disabled"
        return 0
    fi
    
    if [[ ! -f "$config_file" ]]; then
        log "ERROR" "Cannot watch configuration file: $config_file"
        return 1
    fi
    
    log "INFO" "Starting Telegram configuration watcher (interval: ${interval_seconds}s)"
    
    # Watcher script runs in background
    {
        while true; do
            sleep "$interval_seconds"
            
            if has_configuration_changed "$config_file"; then
                log "INFO" "Configuration change detected, reloading..."
                reload_telegram_configuration "$config_file" "false"
            fi
        done
    } &
    
    local watcher_pid=$!
    echo "$watcher_pid" > "/tmp/telegram_config_watcher.pid"
    
    log "DEBUG" "Configuration watcher started (PID: $watcher_pid)"
    return 0
}

# Function to stop configuration watcher
stop_configuration_watcher() {
    local watcher_pid_file="/tmp/telegram_config_watcher.pid"
    
    if [[ -f "$watcher_pid_file" ]]; then
        local watcher_pid
        watcher_pid=$(cat "$watcher_pid_file" 2>/dev/null)
        
        if [[ -n "$watcher_pid" ]] && kill -0 "$watcher_pid" 2>/dev/null; then
            kill "$watcher_pid" 2>/dev/null
            log "INFO" "Configuration watcher stopped (PID: $watcher_pid)"
        fi
        
        rm -f "$watcher_pid_file"
    fi
}

# Function to get configuration summary
get_telegram_configuration_summary() {
    local config_file="$1"
    
    if [[ ! -f "$config_file" ]]; then
        echo "Configuration file not found: $config_file"
        return 1
    fi
    
    local enabled
    enabled=$(read_yaml_config "$config_file" "telegram.enabled" "false")
    local chat_id
    chat_id=$(read_yaml_config "$config_file" "telegram.default_chat_id" "")
    local rate_limit
    rate_limit=$(read_yaml_config "$config_file" "telegram.rate_limiting.messages_per_second" "5")
    local message_length
    message_length=$(read_yaml_config "$config_file" "telegram.formatting.max_message_length" "4000")
    local retry_attempts
    retry_attempts=$(read_yaml_config "$config_file" "telegram.retry.max_attempts" "3")
    
    cat << EOF
Telegram Configuration Summary
File: $config_file
Enabled: $enabled
Chat ID: ${chat_id:0:20}${chat_id:20:+...}
Rate Limit: ${rate_limit} messages/second
Max Message Length: ${message_length} characters
Retry Attempts: ${retry_attempts}

Configuration Status:
$(validate_telegram_configuration "$config_file" "${TELEGRAM_CONFIG_VALIDATION_STRICTNESS:-strict}" 2>&1 | sed 's/^/  /')
EOF
}

# Function to cleanup configuration management
cleanup_config_management() {
    stop_configuration_watcher
    log "DEBUG" "Configuration management cleanup completed"
}

# Cleanup on exit
trap cleanup_config_management EXIT

log "DEBUG" "Telegram configuration management module loaded"