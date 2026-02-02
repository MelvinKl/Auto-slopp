#!/bin/bash

# Telegram Bot API Security Module
# Handles secure token storage, validation, and access control
# Ensures compliance with security best practices

# Set script name for logging identification
SCRIPT_NAME="telegram_security"

# Source utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../utils.sh"

# Set up error handling
setup_error_handling

# Security configuration constants (declare if not already set)
[[ -z "$CONFIG_VALIDATION_STRICT" ]] && readonly CONFIG_VALIDATION_STRICT="strict"
[[ -z "$CONFIG_VALIDATION_WARN" ]] && readonly CONFIG_VALIDATION_WARN="warn"
[[ -z "$CONFIG_VALIDATION_RELAXED" ]] && readonly CONFIG_VALIDATION_RELAXED="relaxed"
TELEGRAM_TOKEN_FILE_DEFAULT="/etc/telegram/token"
TELEGRAM_CONFIG_PERMISSIONS=600
TELEGRAM_DIR_PERMISSIONS=700

# Function to validate Telegram bot token format
validate_bot_token_format() {
    local token="$1"
    
    if [[ -z "$token" ]]; then
        log "ERROR" "Bot token is empty"
        return 1
    fi
    
    # Check basic token format:数字:字符串 (numbers:alphanumeric+underscores+dashes)
    if [[ ! "$token" =~ ^[0-9]+:[a-zA-Z0-9_-]{35}$ ]]; then
        log "ERROR" "Invalid bot token format. Expected format: numbers:alphanumeric_underscores_dashes (35 characters after colon)"
        return 1
    fi
    
    # Additional security checks
    local bot_id="${token%%:*}"
    local token_hash="${token#*:}"
    
    # Bot ID should be a reasonable number (between 1 and 9999999999)
    if [[ ! "$bot_id" =~ ^[1-9][0-9]{0,9}$ ]]; then
        log "ERROR" "Invalid bot ID format: $bot_id"
        return 1
    fi
    
    # Token hash should contain only valid characters
    if [[ ! "$token_hash" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        log "ERROR" "Token hash contains invalid characters"
        return 1
    fi
    
    log "DEBUG" "Bot token format validation passed"
    return 0
}

# Function to validate chat ID format
validate_chat_id() {
    local chat_id="$1"
    
    if [[ -z "$chat_id" ]]; then
        log "ERROR" "Chat ID is empty"
        return 1
    fi
    
    # Chat ID can be:
    # 1. Negative numbers (for private chats/groups)
    # 2. Positive numbers (for channels)
    # 3. @username (for public channels)
    
    if [[ ! "$chat_id" =~ ^-?[0-9]+$ ]] && [[ ! "$chat_id" =~ ^@[a-zA-Z0-9_]+$ ]]; then
        log "ERROR" "Invalid chat ID format. Expected: number, @username, or negative number"
        return 1
    fi
    
    # For usernames, check length and character restrictions
    if [[ "$chat_id" =~ ^@ ]]; then
        local username="${chat_id#@}"
        if [[ ${#username} -lt 5 ]] || [[ ${#username} -gt 32 ]]; then
            log "ERROR" "Chat username must be between 5 and 32 characters"
            return 1
        fi
        
        if [[ ! "$username" =~ ^[a-zA-Z0-9_]+$ ]]; then
            log "ERROR" "Chat username can only contain letters, numbers, and underscores"
            return 1
        fi
    fi
    
    log "DEBUG" "Chat ID validation passed for: ${chat_id:0:20}..."
    return 0
}

# Function to check for hardcoded tokens in scripts
check_hardcoded_tokens() {
    local script_dir="${1:-$(dirname "${SCRIPT_DIR}")}"
    local violations=()
    
    log "DEBUG" "Checking for hardcoded Telegram tokens in: $script_dir"
    
    # Check for common patterns of hardcoded tokens
    local patterns=(
        "TELEGRAM_BOT_TOKEN=\"[0-9]+:[a-zA-Z0-9_-]{35}\""
        "telegram_token=\"[0-9]+:[a-zA-Z0-9_-]{35}\""
        "bot_token=\"[0-9]+:[a-zA-Z0-9_-]{35}\""
        "TELEGRAM_TOKEN=[0-9]+:[a-zA-Z0-9_-]{35}"
    )
    
    for pattern in "${patterns[@]}"; do
        local matches
        if matches=$(grep -r -E "$pattern" "$script_dir" 2>/dev/null); then
            while IFS= read -r line; do
                local file_path="${line%%:*}"
                local line_content="${line#*:}"
                violations+=("$file_path: $line_content")
            done <<< "$matches"
        fi
    done
    
    if [[ ${#violations[@]} -gt 0 ]]; then
        log "ERROR" "Found ${#violations[@]} hardcoded token violations:"
        for violation in "${violations[@]}"; do
            log "ERROR" "  $violation"
        done
        return 1
    fi
    
    log "DEBUG" "No hardcoded tokens found in scripts"
    return 0
}

# Function to validate token file permissions
validate_token_file_permissions() {
    local token_file="${1:-$TELEGRAM_TOKEN_FILE_DEFAULT}"
    
    if [[ ! -f "$token_file" ]]; then
        log "WARNING" "Token file does not exist: $token_file"
        return 0  # Not an error, file might not exist yet
    fi
    
    # Check file permissions
    local perms
    perms=$(stat -c "%a" "$token_file" 2>/dev/null || stat -f "%A" "$token_file" 2>/dev/null)
    
    if [[ "$perms" != "$TELEGRAM_CONFIG_PERMISSIONS" ]]; then
        log "ERROR" "Token file has insecure permissions: $perms (should be $TELEGRAM_CONFIG_PERMISSIONS)"
        return 1
    fi
    
    # Check directory permissions
    local dir_perms
    dir_perms=$(stat -c "%a" "$(dirname "$token_file")" 2>/dev/null || stat -f "%A" "$(dirname "$token_file")" 2>/dev/null)
    
    if [[ "$dir_perms" != "$TELEGRAM_DIR_PERMISSIONS" ]]; then
        log "WARNING" "Token directory permissions may be too open: $dir_perms (recommended: $TELEGRAM_DIR_PERMISSIONS)"
    fi
    
    # Check file ownership (should be root or current user)
    local owner
    owner=$(stat -c "%U" "$token_file" 2>/dev/null || stat -f "%Su" "$token_file" 2>/dev/null)
    
    if [[ "$owner" != "root" ]] && [[ "$owner" != "$(whoami)" ]]; then
        log "WARNING" "Token file owned by unexpected user: $owner"
    fi
    
    log "DEBUG" "Token file permissions validated: $token_file"
    return 0
}

# Function to set up secure token storage
setup_secure_token_storage() {
    local token="$1"
    local token_file="${2:-$TELEGRAM_TOKEN_FILE_DEFAULT}"
    
    if [[ -z "$token" ]]; then
        log "ERROR" "Token is required for secure storage setup"
        return 1
    fi
    
    if ! validate_bot_token_format "$token"; then
        return 1
    fi
    
    # Create secure directory
    local token_dir
    token_dir="$(dirname "$token_file")"
    
    if [[ ! -d "$token_dir" ]]; then
        log "INFO" "Creating secure token directory: $token_dir"
        if ! sudo mkdir -p "$token_dir"; then
            log "ERROR" "Failed to create token directory: $token_dir"
            return 1
        fi
        sudo chmod "$TELEGRAM_DIR_PERMISSIONS" "$token_dir"
        sudo chown root:root "$token_dir"
    fi
    
    # Write token securely
    log "INFO" "Storing Telegram token securely in: $token_file"
    if ! echo "$token" | sudo tee "$token_file" >/dev/null; then
        log "ERROR" "Failed to write token to: $token_file"
        return 1
    fi
    
    # Set secure permissions
    sudo chmod "$TELEGRAM_CONFIG_PERMISSIONS" "$token_file"
    sudo chown root:root "$token_file"
    
    # Validate the setup
    if validate_token_file_permissions "$token_file"; then
        log "SUCCESS" "Secure token storage setup completed"
        
        # Provide instructions for environment variable setup
        cat << EOF

To complete the setup, add the following to your environment:
export TELEGRAM_BOT_TOKEN="\$(cat $token_file 2>/dev/null)"

Or add this line to /etc/environment for system-wide access:
TELEGRAM_BOT_TOKEN="\$(cat $token_file 2>/dev/null)"

EOF
        return 0
    else
        return 1
    fi
}

# Function to load token from secure storage
load_token_from_storage() {
    local token_file="${1:-$TELEGRAM_TOKEN_FILE_DEFAULT}"
    
    if [[ -n "$TELEGRAM_BOT_TOKEN" ]]; then
        log "DEBUG" "Token already loaded from environment"
        return 0
    fi
    
    if [[ -f "$token_file" ]]; then
        if validate_token_file_permissions "$token_file"; then
            local token
            token=$(cat "$token_file" 2>/dev/null)
            if validate_bot_token_format "$token"; then
                export TELEGRAM_BOT_TOKEN="$token"
                log "DEBUG" "Token loaded successfully from secure storage"
                return 0
            else
                log "ERROR" "Token in secure storage has invalid format"
                return 1
            fi
        else
            log "ERROR" "Cannot load token due to permission issues"
            return 1
        fi
    else
        log "DEBUG" "Token file not found: $token_file"
        return 1
    fi
}

# Function to test Telegram API connectivity
test_telegram_connectivity() {
    local bot_token="${1:-$TELEGRAM_BOT_TOKEN}"
    
    if [[ -z "$bot_token" ]]; then
        log "ERROR" "No bot token available for connectivity test"
        return 1
    fi
    
    if ! validate_bot_token_format "$bot_token"; then
        return 1
    fi
    
    log "INFO" "Testing Telegram API connectivity..."
    
    local test_url="https://api.telegram.org/bot${bot_token}/getMe"
    local response
    local timeout="${TELEGRAM_API_TIMEOUT_SECONDS:-10}"
    
    if response=$(curl -s -w "%{http_code}" \
        --connect-timeout "$timeout" \
        --max-time "$timeout" \
        "$test_url" 2>/dev/null); then
        
        local http_code="${response: -3}"
        local response_body="${response%???}"
        
        if [[ "$http_code" == "200" ]]; then
            local bot_info
            bot_info=$(echo "$response_body" | jq -r '.result.username // "unknown"' 2>/dev/null || echo "unknown")
            log "SUCCESS" "Telegram API connectivity test passed (@$bot_info)"
            return 0
        elif [[ "$http_code" == "401" ]]; then
            log "ERROR" "Telegram API authentication failed - invalid token"
            return 1
        elif [[ "$http_code" =~ ^4[0-9][0-9]$ ]]; then
            log "ERROR" "Telegram API client error: HTTP $http_code"
            return 1
        elif [[ "$http_code" =~ ^5[0-9][0-9]$ ]]; then
            log "WARNING" "Telegram API server error: HTTP $http_code"
            return 2  # Temporary error
        else
            log "ERROR" "Telegram API returned unexpected status: HTTP $http_code"
            return 1
        fi
    else
        log "ERROR" "Failed to connect to Telegram API - network error"
        return 1
    fi
}

# Function to perform comprehensive security validation
validate_telegram_security() {
    local config_file="${1:-config.yaml}"
    local token_file="${2:-$TELEGRAM_TOKEN_FILE_DEFAULT}"
    local issues=0
    
    log "INFO" "Starting comprehensive Telegram security validation..."
    
    # Check for hardcoded tokens
    if ! check_hardcoded_tokens "$(dirname "${SCRIPT_DIR}")"; then
        ((issues++))
    fi
    
    # Validate token file permissions
    if [[ -f "$token_file" ]]; then
        if ! validate_token_file_permissions "$token_file"; then
            ((issues++))
        fi
    fi
    
    # Validate bot token format
    if [[ -n "$TELEGRAM_BOT_TOKEN" ]]; then
        if ! validate_bot_token_format "$TELEGRAM_BOT_TOKEN"; then
            ((issues++))
        fi
    fi
    
    # Validate chat ID
    if [[ -n "$TELEGRAM_CHAT_ID" ]]; then
        if ! validate_chat_id "$TELEGRAM_CHAT_ID"; then
            ((issues++))
        fi
    fi
    
    # Test API connectivity
    if [[ -n "$TELEGRAM_BOT_TOKEN" ]]; then
        if ! test_telegram_connectivity "$TELEGRAM_BOT_TOKEN"; then
            ((issues++))
        fi
    fi
    
    # Check environment for security
    if [[ "${TELEGRAM_SECURITY_HIDE_TOKENS_IN_LOGS:-true}" == "true" ]]; then
        # This would be implemented by the logging system
        log "DEBUG" "Token hiding in logs is enabled"
    fi
    
    if [[ $issues -eq 0 ]]; then
        log "SUCCESS" "Telegram security validation completed - no issues found"
        return 0
    else
        log "ERROR" "Telegram security validation completed - $issues issues found"
        return 1
    fi
}

# Function to audit token access
audit_token_access() {
    local operation="$1"
    local result="$2"
    
    if [[ "${TELEGRAM_SECURITY_AUDIT_TOKEN_ACCESS:-true}" != "true" ]]; then
        return 0
    fi
    
    local timestamp
    timestamp=$(generate_timestamp "${TIMESTAMP_FORMAT:-default}" "${TIMESTAMP_TIMEZONE:-local}")
    local user="${USER:-$(whoami)}"
    local pid="$$"
    
    # Log to audit file (with secure permissions)
    local audit_file="/var/log/telegram_audit.log"
    
    # Ensure audit file exists with secure permissions
    if [[ ! -f "$audit_file" ]]; then
        sudo touch "$audit_file" 2>/dev/null || return 0
        sudo chmod 600 "$audit_file" 2>/dev/null || return 0
        sudo chown root:root "$audit_file" 2>/dev/null || return 0
    fi
    
    # Write audit entry
    local audit_entry="[$timestamp] User: $user PID: $pid Operation: $operation Result: $result"
    
    if echo "$audit_entry" | sudo tee -a "$audit_file" >/dev/null 2>&1; then
        log "DEBUG" "Token access audited: $operation"
    else
        log "WARNING" "Failed to write to audit log"
    fi
}

# Function to clean up audit logs
cleanup_audit_logs() {
    local audit_file="/var/log/telegram_audit.log"
    local retention_days="${TELEGRAM_SECURITY_AUDIT_RETENTION_DAYS:-30}"
    
    if [[ ! -f "$audit_file" ]]; then
        return 0
    fi
    
    # Clean up old entries (this is a simplified approach)
    local cutoff_date
    cutoff_date=$(date -d "$retention_days days ago" +%s 2>/dev/null || date -v-"$retention_days"d +%s 2>/dev/null)
    
    if [[ -n "$cutoff_date" ]]; then
        local temp_file="${audit_file}.tmp"
        while IFS= read -r line; do
            # Extract timestamp from audit entry
            local entry_timestamp
            entry_timestamp=$(echo "$line" | sed 's/^\[\([^]]*\)\].*/\1/' 2>/dev/null)
            
            if [[ -n "$entry_timestamp" ]]; then
                local entry_time
                entry_time=$(date -d "$entry_timestamp" +%s 2>/dev/null || date -j -f "%Y-%m-%d %H:%M:%S" "$entry_timestamp" +%s 2>/dev/null)
                
                if [[ -n "$entry_time" ]] && [[ $entry_time -ge $cutoff_date ]]; then
                    echo "$line" >> "$temp_file"
                fi
            fi
        done < "$audit_file"
        
        if [[ -f "$temp_file" ]]; then
            sudo mv "$temp_file" "$audit_file" 2>/dev/null
            sudo chmod 600 "$audit_file" 2>/dev/null
        fi
    fi
    
    log "DEBUG" "Audit log cleanup completed"
}

log "DEBUG" "Telegram security module loaded"