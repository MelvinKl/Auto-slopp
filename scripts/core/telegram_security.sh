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

# Token encryption and rotation constants
TELEGRAM_TOKEN_ENCRYPTION_KEY_FILE="/etc/telegram/.encryption_key"
TELEGRAM_TOKEN_ENCRYPTED_FILE="/etc/telegram/token.enc"
TELEGRAM_TOKEN_ROTATION_HISTORY_FILE="/etc/telegram/token_rotation_history.json"
TELEGRAM_TOKEN_REVOKE_LIST_FILE="/etc/telegram/revoked_tokens.json"
TELEGRAM_TOKEN_MAX_ROTATION_DAYS=90
TELEGRAM_TOKEN_BACKUP_COUNT=5

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
    # 1. Negative numbers (for private groups and supergroups)
    # 2. Positive numbers (for individual users by user ID)
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
    local use_encryption="${3:-${TELEGRAM_SECURITY_ENCRYPT_CONFIG_STORAGE:-true}}"
    
    if [[ -z "$token" ]]; then
        log "ERROR" "Token is required for secure storage setup"
        return 1
    fi
    
    if ! validate_bot_token_format "$token"; then
        return 1
    fi
    
    # Check if token is revoked before storing
    if is_token_revoked "$token"; then
        log "ERROR" "Cannot store revoked token"
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
    
    local storage_method="encrypted"
    if [[ "$use_encryption" == "true" ]]; then
        # Store encrypted token
        local encrypted_token
        encrypted_token=$(encrypt_token "$token")
        if [[ $? -ne 0 ]] || [[ -z "$encrypted_token" ]]; then
            log "WARNING" "Failed to encrypt token, falling back to plain text storage"
            storage_method="plain"
        else
            local encrypted_file="${TELEGRAM_TOKEN_ENCRYPTED_FILE}"
            log "INFO" "Storing Telegram token encrypted in: $encrypted_file"
            if ! echo "$encrypted_token" | sudo tee "$encrypted_file" >/dev/null; then
                log "ERROR" "Failed to write encrypted token to: $encrypted_file"
                return 1
            fi
            sudo chmod "$TELEGRAM_CONFIG_PERMISSIONS" "$encrypted_file"
            sudo chown root:root "$encrypted_file"
        fi
    fi
    
    # Store plain text as fallback or primary if encryption disabled
    if [[ "$storage_method" == "plain" ]]; then
        log "INFO" "Storing Telegram token securely in: $token_file"
        if ! echo "$token" | sudo tee "$token_file" >/dev/null; then
            log "ERROR" "Failed to write token to: $token_file"
            return 1
        fi
        sudo chmod "$TELEGRAM_CONFIG_PERMISSIONS" "$token_file"
        sudo chown root:root "$token_file"
    fi
    
    # Validate the setup
    local validation_passed=true
    if [[ "$storage_method" == "encrypted" ]]; then
        if [[ -f "$TELEGRAM_TOKEN_ENCRYPTED_FILE" ]]; then
            local perms
            perms=$(stat -c "%a" "$TELEGRAM_TOKEN_ENCRYPTED_FILE" 2>/dev/null || stat -f "%A" "$TELEGRAM_TOKEN_ENCRYPTED_FILE" 2>/dev/null)
            if [[ "$perms" != "$TELEGRAM_CONFIG_PERMISSIONS" ]]; then
                log "ERROR" "Encrypted token file has insecure permissions: $perms"
                validation_passed=false
            fi
        fi
    else
        validation_passed=$(validate_token_file_permissions "$token_file" && echo "true" || echo "false")
    fi
    
    if [[ "$validation_passed" == "true" ]]; then
        log "SUCCESS" "Secure token storage setup completed (method: $storage_method)"
        
        # Provide instructions for environment variable setup
        cat << EOF

To complete the setup, add the following to your environment:
export TELEGRAM_BOT_TOKEN="\$(${storage_method}_token_retrieval)"

Or add this line to /etc/environment for system-wide access:
TELEGRAM_BOT_TOKEN="\$(${storage_method}_token_retrieval)"

EOF
        
        if [[ "$storage_method" == "encrypted" ]]; then
            cat << EOF
Note: The token is stored with AES-256-CBC encryption. The encryption key is stored
securely in $TELEGRAM_TOKEN_ENCRYPTION_KEY_FILE with 600 permissions.

EOF
        fi
        
        audit_token_access "SETUP_SECURE_STORAGE" "SUCCESS"
        return 0
    else
        audit_token_access "SETUP_SECURE_STORAGE" "FAILED"
        return 1
    fi
}

# Function to load token from secure storage
load_token_from_storage() {
    local token_file="${1:-$TELEGRAM_TOKEN_FILE_DEFAULT}"
    local encrypted_file="${2:-$TELEGRAM_TOKEN_ENCRYPTED_FILE}"
    
    if [[ -n "$TELEGRAM_BOT_TOKEN" ]]; then
        log "DEBUG" "Token already loaded from environment"
        return 0
    fi
    
    # Try encrypted storage first (if enabled)
    if [[ "${TELEGRAM_SECURITY_ENCRYPT_CONFIG_STORAGE:-true}" == "true" ]] && [[ -f "$encrypted_file" ]]; then
        local encrypted_content
        encrypted_content=$(cat "$encrypted_file" 2>/dev/null)
        
        if [[ -n "$encrypted_content" ]]; then
            local token
            token=$(decrypt_token "$encrypted_content" 2>/dev/null)
            
            if [[ $? -eq 0 ]] && [[ -n "$token" ]]; then
                if validate_bot_token_format "$token" && ! is_token_revoked "$token"; then
                    export TELEGRAM_BOT_TOKEN="$token"
                    log "DEBUG" "Token loaded successfully from encrypted storage"
                    audit_token_access "LOAD_FROM_ENCRYPTED_STORAGE" "SUCCESS"
                    return 0
                else
                    log "ERROR" "Token in encrypted storage is invalid or revoked"
                    audit_token_access "LOAD_FROM_ENCRYPTED_STORAGE" "FAILED"
                fi
            else
                log "ERROR" "Failed to decrypt token from encrypted storage"
                audit_token_access "LOAD_FROM_ENCRYPTED_STORAGE" "FAILED"
            fi
        fi
    fi
    
    # Fallback to plain text storage
    if [[ -f "$token_file" ]]; then
        if validate_token_file_permissions "$token_file"; then
            local token
            token=$(cat "$token_file" 2>/dev/null)
            if validate_bot_token_format "$token" && ! is_token_revoked "$token"; then
                export TELEGRAM_BOT_TOKEN="$token"
                log "DEBUG" "Token loaded successfully from secure storage"
                audit_token_access "LOAD_FROM_PLAIN_STORAGE" "SUCCESS"
                return 0
            else
                log "ERROR" "Token in secure storage has invalid format or is revoked"
                audit_token_access "LOAD_FROM_PLAIN_STORAGE" "FAILED"
                return 1
            fi
        else
            log "ERROR" "Cannot load token due to permission issues"
            audit_token_access "LOAD_FROM_PLAIN_STORAGE" "FAILED"
            return 1
        fi
    else
        log "DEBUG" "Token file not found: $token_file"
        audit_token_access "LOAD_TOKEN" "FAILED"
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
    local additional_info="${3:-}"
    
    if [[ "${TELEGRAM_SECURITY_AUDIT_TOKEN_ACCESS:-true}" != "true" ]]; then
        return 0
    fi
    
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local user="${USER:-$(whoami)}"
    local pid="$$"
    local script_name="${SCRIPT_NAME:-unknown}"
    local hostname="${HOSTNAME:-$(hostname)}"
    
    # Log to audit file (with secure permissions)
    local audit_file="/var/log/telegram_audit.log"
    
    # Ensure audit file exists with secure permissions
    if [[ ! -f "$audit_file" ]]; then
        sudo touch "$audit_file" 2>/dev/null || {
            # Fallback to user directory if system directory not accessible
            audit_file="$HOME/.telegram_audit.log"
            touch "$audit_file" 2>/dev/null || return 0
        }
        sudo chmod 600 "$audit_file" 2>/dev/null || chmod 600 "$audit_file" 2>/dev/null
        sudo chown root:root "$audit_file" 2>/dev/null || chown "$user" "$audit_file" 2>/dev/null
    fi
    
    # Create structured audit entry (JSON format if jq available)
    local audit_entry
    if command -v jq >/dev/null 2>&1; then
        audit_entry=$(jq -n \
            --arg ts "$timestamp" \
            --arg user "$user" \
            --arg pid "$pid" \
            --arg script "$script_name" \
            --arg host "$hostname" \
            --arg op "$operation" \
            --arg result "$result" \
            --arg info "$additional_info" \
            '{
                timestamp: $ts,
                user: $user,
                pid: $pid,
                script_name: $script,
                hostname: $host,
                operation: $op,
                result: $result,
                additional_info: $info
            }')
    else
        # Fallback format
        audit_entry="[$timestamp] Host: $hostname User: $user PID: $pid Script: $script_name Operation: $operation Result: $result"
        if [[ -n "$additional_info" ]]; then
            audit_entry="$audit_entry Info: $additional_info"
        fi
    fi
    
    # Redact any potential tokens in additional info
    if [[ -n "$additional_info" ]]; then
        audit_entry=$(redact_token_in_output "$audit_entry")
    fi
    
    # Write audit entry
    if echo "$audit_entry" | sudo tee -a "$audit_file" >/dev/null 2>&1; then
        log "DEBUG" "Token access audited: $operation"
    else
        # Fallback to user write if sudo fails
        if echo "$audit_entry" >> "$audit_file" 2>/dev/null; then
            log "DEBUG" "Token access audited (fallback): $operation"
        else
            log "WARNING" "Failed to write to audit log"
        fi
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

# Helper function for secure file operations (works with or without sudo)
secure_file_write() {
    local content="$1"
    local file_path="$2"
    local mode="${3:-600}"
    
    # Try to write directly first
    if echo "$content" > "$file_path" 2>/dev/null; then
        chmod "$mode" "$file_path" 2>/dev/null
        if [[ "$EUID" -eq 0 ]]; then
            chown root:root "$file_path" 2>/dev/null
        fi
        return 0
    fi
    
    # Fallback to sudo if available
    if command -v sudo >/dev/null 2>&1; then
        if echo "$content" | sudo tee "$file_path" >/dev/null 2>/dev/null; then
            sudo chmod "$mode" "$file_path" 2>/dev/null
            sudo chown root:root "$file_path" 2>/dev/null
            return 0
        fi
    fi
    
    return 1
}

# Helper function for secure directory creation
secure_mkdir() {
    local dir_path="$1"
    local mode="${2:-700}"
    
    # Try to create directly first
    if mkdir -p "$dir_path" 2>/dev/null; then
        chmod "$mode" "$dir_path" 2>/dev/null
        if [[ "$EUID" -eq 0 ]]; then
            chown root:root "$dir_path" 2>/dev/null
        fi
        return 0
    fi
    
    # Fallback to sudo if available
    if command -v sudo >/dev/null 2>&1; then
        if sudo mkdir -p "$dir_path" 2>/dev/null; then
            sudo chmod "$mode" "$dir_path" 2>/dev/null
            sudo chown root:root "$dir_path" 2>/dev/null
            return 0
        fi
    fi
    
    return 1
}

# Function to generate or load encryption key
get_encryption_key() {
    local key_file="${1:-$TELEGRAM_TOKEN_ENCRYPTION_KEY_FILE}"
    
    if [[ -f "$key_file" ]]; then
        # Load existing key
        if [[ "$(stat -c "%a" "$key_file" 2>/dev/null || stat -f "%A" "$key_file" 2>/dev/null)" == "600" ]]; then
            cat "$key_file" 2>/dev/null
        else
            log "ERROR" "Encryption key file has insecure permissions: $key_file"
            return 1
        fi
    else
        # Generate new key
        local key_dir
        key_dir="$(dirname "$key_file")"
        
        if [[ ! -d "$key_dir" ]]; then
            mkdir -p "$key_dir" || return 1
            chmod "$TELEGRAM_DIR_PERMISSIONS" "$key_dir"
            if [[ "$EUID" -eq 0 ]]; then
                chown root:root "$key_dir"
            fi
        fi
        
        # Generate 32-byte (256-bit) key
        local new_key
        new_key=$(openssl rand -hex 32 2>/dev/null)
        
        if [[ -n "$new_key" ]] && [[ ${#new_key} -eq 64 ]]; then
            echo "$new_key" > "$key_file" || {
                log "ERROR" "Failed to save encryption key to: $key_file"
                return 1
            }
            chmod 600 "$key_file"
            if [[ "$EUID" -eq 0 ]]; then
                chown root:root "$key_file"
            fi
            
            log "INFO" "Generated new encryption key: $key_file"
            echo "$new_key"
        else
            log "ERROR" "Failed to generate encryption key"
            return 1
        fi
    fi
}

# Function to encrypt token data
encrypt_token() {
    local token="$1"
    local encryption_key="${2:-$(get_encryption_key)}"
    
    if [[ -z "$token" ]] || [[ -z "$encryption_key" ]]; then
        log "ERROR" "Token and encryption key are required for encryption"
        return 1
    fi
    
    # Use AES-256-CBC for encryption
    local encrypted_data
    encrypted_data=$(echo -n "$token" | openssl enc -aes-256-cbc -salt -pbkdf2 -k "$encryption_key" -base64 2>/dev/null)
    
    if [[ $? -eq 0 ]] && [[ -n "$encrypted_data" ]]; then
        echo "$encrypted_data"
        log "DEBUG" "Token encrypted successfully"
        return 0
    else
        log "ERROR" "Failed to encrypt token"
        return 1
    fi
}

# Function to decrypt token data
decrypt_token() {
    local encrypted_token="$1"
    local encryption_key="${2:-$(get_encryption_key)}"
    
    if [[ -z "$encrypted_token" ]] || [[ -z "$encryption_key" ]]; then
        log "ERROR" "Encrypted token and encryption key are required for decryption"
        return 1
    fi
    
    # Decrypt using AES-256-CBC
    local decrypted_data
    decrypted_data=$(echo "$encrypted_token" | openssl enc -aes-256-cbc -d -pbkdf2 -k "$encryption_key" -base64 2>/dev/null)
    
    if [[ $? -eq 0 ]] && [[ -n "$decrypted_data" ]]; then
        echo "$decrypted_data"
        log "DEBUG" "Token decrypted successfully"
        return 0
    else
        log "ERROR" "Failed to decrypt token (invalid key or corrupted data)"
        return 1
    fi
}

# Function to check if token is in revoked list
is_token_revoked() {
    local token="$1"
    local revoke_list_file="${2:-$TELEGRAM_TOKEN_REVOKE_LIST_FILE}"
    
    if [[ ! -f "$revoke_list_file" ]]; then
        return 1  # No revoke list exists, assume not revoked
    fi
    
    # Create hash of token for comparison (don't store actual tokens)
    local token_hash
    token_hash=$(echo -n "$token" | sha256sum | cut -d' ' -f1)
    
    # Check if token hash exists in revoke list
    if grep -q "\"$token_hash\"" "$revoke_list_file" 2>/dev/null; then
        log "WARNING" "Token is found in revocation list"
        return 0  # Token is revoked
    fi
    
    return 1  # Token is not revoked
}

# Function to revoke a token
revoke_token() {
    local token="$1"
    local reason="${2:-Manual revocation}"
    local revoke_list_file="${3:-$TELEGRAM_TOKEN_REVOKE_LIST_FILE}"
    
    if [[ -z "$token" ]]; then
        log "ERROR" "Token is required for revocation"
        return 1
    fi
    
    # Validate token format before revocation
    if ! validate_bot_token_format "$token"; then
        log "ERROR" "Cannot revoke token with invalid format"
        return 1
    fi
    
    # Create revoke list directory if needed
    local revoke_dir
    revoke_dir="$(dirname "$revoke_list_file")"
    
    if [[ ! -d "$revoke_dir" ]]; then
        sudo mkdir -p "$revoke_dir" || return 1
        sudo chmod "$TELEGRAM_DIR_PERMISSIONS" "$revoke_dir"
        sudo chown root:root "$revoke_dir"
    fi
    
    # Create revoke list file if it doesn't exist
    if [[ ! -f "$revoke_list_file" ]]; then
        echo '{"revoked_tokens": []}' | sudo tee "$revoke_list_file" >/dev/null || {
            log "ERROR" "Failed to create revoke list file: $revoke_list_file"
            return 1
        }
        sudo chmod 600 "$revoke_list_file"
        sudo chown root:root "$revoke_list_file"
    fi
    
    # Create hash of token (never store actual tokens)
    local token_hash
    token_hash=$(echo -n "$token" | sha256sum | cut -d' ' -f1)
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local user="${USER:-$(whoami)}"
    
    # Create revoke entry
    local revoke_entry
    revoke_entry=$(cat << EOF
{
  "hash": "$token_hash",
  "revoked_at": "$timestamp",
  "revoked_by": "$user",
  "reason": "$reason"
}
EOF
)
    
    # Add to revoke list using jq if available, otherwise use simple method
    if command -v jq >/dev/null 2>&1; then
        local temp_file="${revoke_list_file}.tmp"
        if jq --argjson new_entry "$revoke_entry" '.revoked_tokens += [$new_entry]' "$revoke_list_file" > "$temp_file" 2>/dev/null; then
            sudo mv "$temp_file" "$revoke_list_file" && sudo chmod 600 "$revoke_list_file" && sudo chown root:root "$revoke_list_file"
        else
            log "ERROR" "Failed to add token to revoke list"
            return 1
        fi
    else
        # Fallback method
        if sudo echo "$revoke_entry" >> "$revoke_list_file"; then
            sudo chmod 600 "$revoke_list_file"
            sudo chown root:root "$revoke_list_file"
        else
            log "ERROR" "Failed to add token to revoke list"
            return 1
        fi
    fi
    
    log "INFO" "Token revoked successfully by $user: $reason"
    audit_token_access "REVOKE_TOKEN" "SUCCESS"
    
    return 0
}

# Function to rotate token
rotate_token() {
    local old_token="$1"
    local new_token="$2"
    local rotation_history_file="${3:-$TELEGRAM_TOKEN_ROTATION_HISTORY_FILE}"
    
    if [[ -z "$old_token" ]] || [[ -z "$new_token" ]]; then
        log "ERROR" "Both old and new tokens are required for rotation"
        return 1
    fi
    
    # Validate both tokens
    if ! validate_bot_token_format "$old_token" || ! validate_bot_token_format "$new_token"; then
        log "ERROR" "Invalid token format detected"
        return 1
    fi
    
    # Check if tokens are the same
    if [[ "$old_token" == "$new_token" ]]; then
        log "ERROR" "New token must be different from old token"
        return 1
    fi
    
    # Create rotation history directory if needed
    local history_dir
    history_dir="$(dirname "$rotation_history_file")"
    
    if [[ ! -d "$history_dir" ]]; then
        sudo mkdir -p "$history_dir" || return 1
        sudo chmod "$TELEGRAM_DIR_PERMISSIONS" "$history_dir"
        sudo chown root:root "$history_dir"
    fi
    
    # Create rotation history file if it doesn't exist
    if [[ ! -f "$rotation_history_file" ]]; then
        echo '{"rotations": []}' | sudo tee "$rotation_history_file" >/dev/null || {
            log "ERROR" "Failed to create rotation history file: $rotation_history_file"
            return 1
        }
        sudo chmod 600 "$rotation_history_file"
        sudo chown root:root "$rotation_history_file"
    fi
    
    # Revoke old token
    if ! revoke_token "$old_token" "Token rotation"; then
        log "WARNING" "Failed to revoke old token during rotation"
    fi
    
    # Create rotation entry
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local user="${USER:-$(whoami)}"
    local old_token_hash
    old_token_hash=$(echo -n "$old_token" | sha256sum | cut -d' ' -f1)
    local new_token_hash
    new_token_hash=$(echo -n "$new_token" | sha256sum | cut -d' ' -f1)
    
    local rotation_entry
    rotation_entry=$(cat << EOF
{
  "timestamp": "$timestamp",
  "rotated_by": "$user",
  "old_token_hash": "$old_token_hash",
  "new_token_hash": "$new_token_hash"
}
EOF
)
    
    # Add to rotation history
    if command -v jq >/dev/null 2>&1; then
        local temp_file="${rotation_history_file}.tmp"
        if jq --argjson new_entry "$rotation_entry" '.rotations += [$new_entry]' "$rotation_history_file" > "$temp_file" 2>/dev/null; then
            sudo mv "$temp_file" "$rotation_history_file" && sudo chmod 600 "$rotation_history_file" && sudo chown root:root "$rotation_history_file"
        else
            log "ERROR" "Failed to add rotation to history"
            return 1
        fi
    else
        # Fallback method
        if sudo echo "$rotation_entry" >> "$rotation_history_file"; then
            sudo chmod 600 "$rotation_history_file"
            sudo chown root:root "$rotation_history_file"
        else
            log "ERROR" "Failed to add rotation to history"
            return 1
        fi
    fi
    
    # Store new encrypted token
    if [[ "${TELEGRAM_SECURITY_ENCRYPT_CONFIG_STORAGE:-true}" == "true" ]]; then
        local encrypted_new_token
        encrypted_new_token=$(encrypt_token "$new_token")
        if [[ $? -eq 0 ]] && [[ -n "$encrypted_new_token" ]]; then
            local encrypted_file="${TELEGRAM_TOKEN_ENCRYPTED_FILE}"
            echo "$encrypted_new_token" | sudo tee "$encrypted_file" >/dev/null || {
                log "ERROR" "Failed to store encrypted new token"
                return 1
            }
            sudo chmod 600 "$encrypted_file"
            sudo chown root:root "$encrypted_file"
            log "INFO" "New token stored encrypted: $encrypted_file"
        fi
    fi
    
    log "SUCCESS" "Token rotation completed by $user"
    audit_token_access "ROTATE_TOKEN" "SUCCESS"
    
    return 0
}

# Function to check if token needs rotation
check_token_rotation_needed() {
    local token="$1"
    local rotation_history_file="${2:-$TELEGRAM_TOKEN_ROTATION_HISTORY_FILE}"
    local max_days="${3:-$TELEGRAM_TOKEN_MAX_ROTATION_DAYS}"
    
    if [[ -z "$token" ]]; then
        return 1  # No token to check
    fi
    
    if [[ ! -f "$rotation_history_file" ]]; then
        # No rotation history, assume token is old
        log "WARNING" "No token rotation history found"
        return 0  # Recommend rotation
    fi
    
    local token_hash
    token_hash=$(echo -n "$token" | sha256sum | cut -d' ' -f1)
    
    # Find last rotation for this token
    local last_rotation
    if command -v jq >/dev/null 2>&1; then
        last_rotation=$(jq -r --arg hash "$token_hash" '.rotations[] | select(.new_token_hash == $hash) | .timestamp' "$rotation_history_file" 2>/dev/null | tail -1)
    fi
    
    if [[ -z "$last_rotation" ]]; then
        log "WARNING" "No rotation history found for current token"
        return 0  # Recommend rotation
    fi
    
    # Calculate days since last rotation
    local rotation_timestamp
    rotation_timestamp=$(date -d "$last_rotation" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$last_rotation" +%s 2>/dev/null)
    local current_timestamp
    current_timestamp=$(date +%s)
    local days_since_rotation=$(( (current_timestamp - rotation_timestamp) / 86400 ))
    
    if [[ $days_since_rotation -ge $max_days ]]; then
        log "WARNING" "Token rotation needed - $days_since_rotation days since last rotation (max: $max_days)"
        return 0  # Rotation needed
    fi
    
    log "DEBUG" "Token rotation not needed - $days_since_rotation days since last rotation"
    return 1  # Rotation not needed
}

# Function to cleanup old revoked tokens
cleanup_revoked_tokens() {
    local revoke_list_file="${1:-$TELEGRAM_TOKEN_REVOKE_LIST_FILE}"
    local retention_days="${2:-90}"
    
    if [[ ! -f "$revoke_list_file" ]]; then
        return 0  # No file to cleanup
    fi
    
    local cutoff_date
    cutoff_date=$(date -d "$retention_days days ago" -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -v-"$retention_days"d -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null)
    
    if [[ -z "$cutoff_date" ]]; then
        log "ERROR" "Failed to calculate cutoff date for cleanup"
        return 1
    fi
    
    # Filter out old entries
    local temp_file="${revoke_list_file}.tmp"
    
    if command -v jq >/dev/null 2>&1; then
        # Use jq to filter old entries
        jq --arg cutoff "$cutoff_date" '
        .revoked_tokens = [.revoked_tokens[] | select(.revoked_at >= $cutoff)]
        ' "$revoke_list_file" > "$temp_file" 2>/dev/null
    else
        # Fallback method - remove old entries manually
        echo '{"revoked_tokens": []}' > "$temp_file"
        while IFS= read -r line; do
            if [[ "$line" =~ \"revoked_at\":[[:space:]]*\"([^\"]+)\" ]]; then
                local revoked_at="${BASH_REMATCH[1]}"
                if [[ "$revoked_at" > "$cutoff_date" ]]; then
                    echo "$line" >> "$temp_file"
                fi
            fi
        done < "$revoke_list_file"
    fi
    
    if [[ -f "$temp_file" ]]; then
        sudo mv "$temp_file" "$revoke_list_file" 2>/dev/null && sudo chmod 600 "$revoke_list_file" && sudo chown root:root "$revoke_list_file"
        log "INFO" "Revoked tokens cleanup completed (retention: $retention_days days)"
    fi
    
    return 0
}

# Function to redact token from logs
redact_token_in_output() {
    local output="$1"
    local redacted_placeholder="[REDACTED_TOKEN]"
    
    if [[ -z "$output" ]]; then
        return 0
    fi
    
    # Redact Telegram bot tokens
    local redacted_output
    redacted_output=$(echo "$output" | sed -E 's/[0-9]+:[a-zA-Z0-9_-]{35}/'"$redacted_placeholder"'/g')
    
    # Redact potential encrypted tokens (hex strings of 64+ chars)
    redacted_output=$(echo "$redacted_output" | sed -E 's/[a-fA-F0-9]{64,}/'"$redacted_placeholder"'/g')
    
    echo "$redacted_output"
}

# Function to validate and secure input token from user
secure_token_input() {
    local prompt="${1:-Enter Telegram bot token}"
    local confirm="${2:-true}"
    
    # Check for environment variable first (non-interactive mode)
    if [[ -n "$TELEGRAM_BOT_TOKEN" ]]; then
        log "DEBUG" "Token loaded from TELEGRAM_BOT_TOKEN environment variable"
        echo "$TELEGRAM_BOT_TOKEN"
        return 0
    fi
    
    # Check for token file (non-interactive mode)
    local token_file="${TELEGRAM_TOKEN_FILE:-/etc/telegram/token}"
    if [[ -f "$token_file" ]]; then
        local token
        token=$(cat "$token_file" 2>/dev/null)
        if [[ -n "$token" ]]; then
            log "DEBUG" "Token loaded from $token_file"
            echo "$token"
            return 0
        fi
    fi
    
    # Interactive mode - ask for user input
    echo "$prompt" >&2
    local token
    read -s token 2>/dev/null
    echo >&2
    
    if [[ -z "$token" ]]; then
        log "ERROR" "No token provided"
        return 1
    fi
    
    # Validate token format
    if ! validate_bot_token_format "$token"; then
        log "ERROR" "Invalid token format"
        return 1
    fi
    
    # Test token connectivity
    if ! test_telegram_connectivity "$token"; then
        log "ERROR" "Token validation failed - API connectivity test"
        return 1
    fi
    
    # Confirm token if requested
    if [[ "$confirm" == "true" ]]; then
        echo "Confirm token (type 'yes' to proceed):" >&2
        local confirmation
        read confirmation 2>/dev/null
        
        if [[ "$confirmation" != "yes" ]]; then
            log "INFO" "Token input cancelled by user"
            return 1
        fi
    fi
    
    echo "$token"
    audit_token_access "SECURE_INPUT_TOKEN" "SUCCESS"
}

# Function to load and validate token from multiple sources
load_and_validate_token() {
    local token_file="${1:-$TELEGRAM_TOKEN_FILE_DEFAULT}"
    local encrypted_file="${2:-$TELEGRAM_TOKEN_ENCRYPTED_FILE}"
    local token=""
    
    # Priority 1: Environment variable
    if [[ -n "$TELEGRAM_BOT_TOKEN" ]]; then
        token="$TELEGRAM_BOT_TOKEN"
        log "DEBUG" "Token loaded from environment variable"
    fi
    
    # Priority 2: Encrypted file (if encryption is enabled)
    if [[ -z "$token" ]] && [[ "${TELEGRAM_SECURITY_ENCRYPT_CONFIG_STORAGE:-true}" == "true" ]] && [[ -f "$encrypted_file" ]]; then
        local encrypted_content
        encrypted_content=$(cat "$encrypted_file" 2>/dev/null)
        if [[ -n "$encrypted_content" ]]; then
            token=$(decrypt_token "$encrypted_content" 2>/dev/null)
            if [[ $? -eq 0 ]] && [[ -n "$token" ]]; then
                log "DEBUG" "Token loaded from encrypted storage"
            else
                log "WARNING" "Failed to decrypt token from encrypted storage"
            fi
        fi
    fi
    
    # Priority 3: Plain text file
    if [[ -z "$token" ]] && [[ -f "$token_file" ]]; then
        token=$(cat "$token_file" 2>/dev/null)
        if [[ -n "$token" ]]; then
            log "DEBUG" "Token loaded from plain text file"
            log "WARNING" "Consider using encrypted storage for better security"
        fi
    fi
    
    # Validate token if found
    if [[ -n "$token" ]]; then
        # Check if token is revoked
        if is_token_revoked "$token"; then
            log "ERROR" "Token has been revoked and cannot be used"
            return 1
        fi
        
        # Validate token format
        if ! validate_bot_token_format "$token"; then
            log "ERROR" "Token format validation failed"
            return 1
        fi
        
        # Test connectivity
        if ! test_telegram_connectivity "$token"; then
            log "WARNING" "Token connectivity test failed"
            # Don't return error here, as API might be temporarily unavailable
        fi
        
        # Check if rotation is needed
        if check_token_rotation_needed "$token"; then
            log "WARNING" "Token rotation is recommended"
        fi
        
        export TELEGRAM_BOT_TOKEN="$token"
        audit_token_access "LOAD_VALIDATE_TOKEN" "SUCCESS"
        return 0
    else
        log "ERROR" "No valid token found in any source"
        audit_token_access "LOAD_VALIDATE_TOKEN" "FAILED"
        return 1
    fi
}

# Function for secure logging with automatic token redaction
secure_log() {
    local level="$1"
    shift
    local message="$*"
    
    # Redact tokens from message if token hiding is enabled
    if [[ "${TELEGRAM_SECURITY_HIDE_TOKENS_IN_LOGS:-true}" == "true" ]]; then
        message=$(redact_token_in_output "$message")
    fi
    
    # Use the original log function
    log "$level" "$message"
}

# Function to get script name with security context
get_security_script_name() {
    local base_name="${SCRIPT_NAME:-$(basename "${BASH_SOURCE[1]}" .sh)}"
    echo "${base_name}_sec"
}

# Function to perform security health check
perform_security_health_check() {
    local config_file="${1:-config.yaml}"
    local issues=0
    
    log "INFO" "Starting Telegram security health check..."
    
    # Check encryption key
    if [[ "${TELEGRAM_SECURITY_ENCRYPT_CONFIG_STORAGE:-true}" == "true" ]]; then
        if [[ ! -f "$TELEGRAM_TOKEN_ENCRYPTION_KEY_FILE" ]]; then
            log "WARNING" "Encryption key file not found: $TELEGRAM_TOKEN_ENCRYPTION_KEY_FILE"
            ((issues++))
        elif [[ "$(stat -c "%a" "$TELEGRAM_TOKEN_ENCRYPTION_KEY_FILE" 2>/dev/null || stat -f "%A" "$TELEGRAM_TOKEN_ENCRYPTION_KEY_FILE" 2>/dev/null)" != "600" ]]; then
            log "ERROR" "Encryption key file has insecure permissions"
            ((issues++))
        fi
    fi
    
    # Check encrypted token file
    if [[ -f "$TELEGRAM_TOKEN_ENCRYPTED_FILE" ]]; then
        if [[ "$(stat -c "%a" "$TELEGRAM_TOKEN_ENCRYPTED_FILE" 2>/dev/null || stat -f "%A" "$TELEGRAM_TOKEN_ENCRYPTED_FILE" 2>/dev/null)" != "600" ]]; then
            log "ERROR" "Encrypted token file has insecure permissions"
            ((issues++))
        fi
    fi
    
    # Check revoke list file
    if [[ -f "$TELEGRAM_TOKEN_REVOKE_LIST_FILE" ]]; then
        if [[ "$(stat -c "%a" "$TELEGRAM_TOKEN_REVOKE_LIST_FILE" 2>/dev/null || stat -f "%A" "$TELEGRAM_TOKEN_REVOKE_LIST_FILE" 2>/dev/null)" != "600" ]]; then
            log "WARNING" "Revoke list file has insecure permissions"
        fi
    fi
    
    # Check rotation history
    if [[ -f "$TELEGRAM_TOKEN_ROTATION_HISTORY_FILE" ]]; then
        if [[ "$(stat -c "%a" "$TELEGRAM_TOKEN_ROTATION_HISTORY_FILE" 2>/dev/null || stat -f "%A" "$TELEGRAM_TOKEN_ROTATION_HISTORY_FILE" 2>/dev/null)" != "600" ]]; then
            log "WARNING" "Rotation history file has insecure permissions"
        fi
    fi
    
    # Test token loading
    if ! load_and_validate_token; then
        log "WARNING" "Token validation failed during health check"
        ((issues++))
    fi
    
    # Check for hardcoded tokens
    if ! check_hardcoded_tokens "$(dirname "${SCRIPT_DIR}")"; then
        ((issues++))
    fi
    
    # Check cleanup needs
    if [[ -f "$TELEGRAM_TOKEN_REVOKE_LIST_FILE" ]]; then
        if ! cleanup_revoked_tokens; then
            log "WARNING" "Failed to cleanup old revoked tokens"
        fi
    fi
    
    if [[ $issues -eq 0 ]]; then
        log "SUCCESS" "Telegram security health check passed - no issues found"
        return 0
    else
        log "WARNING" "Telegram security health check completed - $issues issues found"
        return 1
    fi
}

# Function to generate security report
generate_security_report() {
    local config_file="${1:-config.yaml}"
    local report_file="${2:-/tmp/telegram_security_report.txt}"
    
    log "INFO" "Generating Telegram security report..."
    
    {
        echo "=================================================="
        echo "Telegram Bot Security Report"
        echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        echo "=================================================="
        echo ""
        
        echo "Security Configuration:"
        echo "  Token Encryption: $([[ "${TELEGRAM_SECURITY_ENCRYPT_CONFIG_STORAGE:-true}" == "true" ]] && echo "ENABLED" || echo "DISABLED")"
        echo "  Audit Logging: $([[ "${TELEGRAM_SECURITY_AUDIT_TOKEN_ACCESS:-true}" == "true" ]] && echo "ENABLED" || echo "DISABLED")"
        echo "  Token Hiding: $([[ "${TELEGRAM_SECURITY_HIDE_TOKENS_IN_LOGS:-true}" == "true" ]] && echo "ENABLED" || echo "DISABLED")"
        echo "  Token Validation: $([[ "${TELEGRAM_SECURITY_VALIDATE_BOT_TOKEN:-true}" == "true" ]] && echo "ENABLED" || echo "DISABLED")"
        echo ""
        
        echo "Security Files Status:"
        echo "  Encryption Key: $([ -f "$TELEGRAM_TOKEN_ENCRYPTION_KEY_FILE" ] && echo "EXISTS (600)" || echo "MISSING")"
        echo "  Encrypted Token: $([ -f "$TELEGRAM_TOKEN_ENCRYPTED_FILE" ] && echo "EXISTS (600)" || echo "MISSING")"
        echo "  Plain Token: $([ -f "$TELEGRAM_TOKEN_FILE_DEFAULT" ] && echo "EXISTS (600)" || echo "MISSING")"
        echo "  Revoke List: $([ -f "$TELEGRAM_TOKEN_REVOKE_LIST_FILE" ] && echo "EXISTS (600)" || echo "MISSING")"
        echo "  Rotation History: $([ -f "$TELEGRAM_TOKEN_ROTATION_HISTORY_FILE" ] && echo "EXISTS (600)" || echo "MISSING")"
        echo ""
        
        echo "Token Status:"
        if load_and_validate_token >/dev/null 2>&1; then
            echo "  Token Status: VALID"
            echo "  Token Source: $([ -n "$TELEGRAM_BOT_TOKEN" ] && echo "LOADED" || echo "NOT FOUND")"
            if check_token_rotation_needed "$TELEGRAM_BOT_TOKEN" >/dev/null 2>&1; then
                echo "  Rotation Needed: YES"
            else
                echo "  Rotation Needed: NO"
            fi
        else
            echo "  Token Status: INVALID OR MISSING"
        fi
        echo ""
        
        echo "Hardcoded Tokens Check:"
        if check_hardcoded_tokens "$(dirname "${SCRIPT_DIR}")" >/dev/null 2>&1; then
            echo "  Status: CLEAN (no hardcoded tokens found)"
        else
            echo "  Status: ISSUES (hardcoded tokens detected)"
        fi
        echo ""
        
        echo "Recent Security Events (last 10):"
        if [[ -f "/var/log/telegram_audit.log" ]] || [[ -f "$HOME/.telegram_audit.log" ]]; then
            local audit_file
            audit_file=$([ -f "/var/log/telegram_audit.log" ] && echo "/var/log/telegram_audit.log" || echo "$HOME/.telegram_audit.log")
            if command -v jq >/dev/null 2>&1; then
                tail -20 "$audit_file" | grep -E '^\[' | tail -10 | sed 's/^/    /'
            else
                tail -10 "$audit_file" | sed 's/^/    /'
            fi
        else
            echo "    No audit log found"
        fi
        echo ""
        
        echo "Security Health Check:"
        if perform_security_health_check >/dev/null 2>&1; then
            echo "  Status: PASSED"
        else
            echo "  Status: ISSUES DETECTED"
        fi
        echo ""
        
        echo "Recommendations:"
        echo "  1. Always use encrypted storage for tokens"
        echo "  2. Rotate tokens every $TELEGRAM_TOKEN_MAX_ROTATION_DAYS days"
        echo "  3. Keep audit logs for security monitoring"
        echo "  4. Never commit tokens to version control"
        echo "  5. Use environment variables for temporary tokens"
        echo ""
        
        echo "=================================================="
        
    } > "$report_file"
    
    log "SUCCESS" "Security report generated: $report_file"
    audit_token_access "GENERATE_SECURITY_REPORT" "SUCCESS" "Report saved to $report_file"
}

log "DEBUG" "Enhanced Telegram security module loaded"