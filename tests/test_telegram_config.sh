#!/bin/bash

# Telegram Configuration System Test Script
# Tests the complete configuration system including validation, loading, and integration

set -e

# Set script name for logging identification
SCRIPT_NAME="telegram_config_test"

# Source utilities and modules
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${PROJECT_ROOT}/scripts/utils.sh"

# Set up error handling
setup_error_handling

# Test configuration file
TEST_CONFIG="/tmp/test_telegram_config.yaml"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_CONFIG=""

# Cleanup function
cleanup_test() {
    [[ -f "$TEST_CONFIG" ]] && rm -f "$TEST_CONFIG"
    [[ -n "$BACKUP_CONFIG" && -f "$BACKUP_CONFIG" ]] && mv "$BACKUP_CONFIG" "$TEST_CONFIG"
}
trap cleanup_test EXIT

# Function to create test configuration
create_test_config() {
    # Use the existing config.yaml but ensure telegram section exists
    if [[ -f "$PROJECT_ROOT/config.yaml" ]]; then
        cp "$PROJECT_ROOT/config.yaml" "$TEST_CONFIG"
    else
        # Create minimal config with telegram section
        cat > "$TEST_CONFIG" << 'EOF'
sleep_duration: 100
managed_repo_path: "~/git/managed"
log_directory: "~/git/Auto-logs"
log_level: INFO
EOF
    fi
    
    # Append telegram configuration
    cat >> "$TEST_CONFIG" << 'EOF'

# Telegram Bot logging configuration
telegram:
  enabled: true
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  default_chat_id: "@test_channel"
  api_timeout_seconds: 10
  connection_retries: 3
  
  rate_limiting:
    messages_per_second: 5
    burst_size: 20
    rate_limit_window_seconds: 60
    backoff_multiplier: 2
    max_backoff_seconds: 30
  
  formatting:
    parse_mode: "HTML"
    max_message_length: 4000
    include_timestamp: true
    include_log_level: true
    include_script_name: true
    use_emoji_indicators: true
  
  retry:
    max_attempts: 3
    base_delay: 1.0
    max_delay: 30.0
    jitter: true
  
  filters:
    log_levels: ["ERROR", "WARNING", "SUCCESS"]
    scripts: ["main.sh", "updater.sh"]
    exclude_patterns: []
    include_patterns: []
  
  security:
    validate_bot_token: true
    encrypt_config_storage: true
    audit_token_access: true
    hide_tokens_in_logs: true
    require_https: true
  
  health:
    enable_health_checks: true
    health_check_interval_minutes: 15
    api_connectivity_test: true
    rate_limit_monitoring: true
    queue_size_monitoring: true
  
  config:
    auto_reload: true
    config_file_watch_interval_seconds: 30
    validation_strictness: "strict"
    backup_configuration: true
EOF
}

# Function to test configuration loading
test_config_loading() {
    log "INFO" "Testing configuration loading..."
    
    # Create test config first
    create_test_config
    
    # Source yaml_config module
    source "${PROJECT_ROOT}/scripts/yaml_config.sh"
    
    # Load configuration
    if load_config "$TEST_CONFIG"; then
        log "SUCCESS" "Configuration loaded successfully"
        
        # Check key variables
        if [[ "${TELEGRAM_ENABLED}" == "true" ]]; then
            log "SUCCESS" "TELEGRAM_ENABLED loaded correctly"
        else
            log "ERROR" "TELEGRAM_ENABLED not loaded correctly (value: '${TELEGRAM_ENABLED:-unset}')"
            return 1
        fi
        
        if [[ "${TELEGRAM_RATE_LIMITING_MESSAGES_PER_SECOND}" == "5" ]]; then
            log "SUCCESS" "Rate limiting loaded correctly"
        else
            log "ERROR" "Rate limiting not loaded correctly (value: '${TELEGRAM_RATE_LIMITING_MESSAGES_PER_SECOND:-unset}')"
            return 1
        fi
        
        return 0
    else
        log "ERROR" "Failed to load configuration"
        return 1
    fi
}

# Function to test configuration validation
test_config_validation() {
    log "INFO" "Testing configuration validation..."
    
    # First load the basic configuration to set up variables
    source "${PROJECT_ROOT}/scripts/yaml_config.sh"
    load_config "$TEST_CONFIG"
    
    # Source config module
    source "${PROJECT_ROOT}/scripts/core/telegram_config.sh"
    
    # Test valid configuration
    if validate_telegram_configuration "$TEST_CONFIG" "strict"; then
        log "SUCCESS" "Valid configuration passed validation"
    else
        log "ERROR" "Valid configuration failed validation"
        return 1
    fi
    
    # Test invalid configuration (hardcoded token)
    cp "$TEST_CONFIG" "${TEST_CONFIG}.backup"
    BACKUP_CONFIG="${TEST_CONFIG}.backup"
    
    sed -i 's/bot_token: "${TELEGRAM_BOT_TOKEN}"/bot_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789"/' "$TEST_CONFIG"
    
    if ! validate_telegram_configuration "$TEST_CONFIG" "strict"; then
        log "SUCCESS" "Invalid configuration (hardcoded token) correctly rejected"
    else
        log "ERROR" "Invalid configuration (hardcoded token) was accepted"
        return 1
    fi
    
    # Restore valid configuration
    mv "$BACKUP_CONFIG" "$TEST_CONFIG"
    BACKUP_CONFIG=""
    
    return 0
}

# Function to test security validation
test_security_validation() {
    log "INFO" "Testing security validation..."
    
    # Source security module
    source "${PROJECT_ROOT}/scripts/core/telegram_security.sh"
    
    # Test token format validation
    if validate_bot_token_format "123456789:ABCdefGHIjklMNOpqrsTUVwxyz-123456789"; then
        log "SUCCESS" "Valid token format accepted"
    else
        log "ERROR" "Valid token format rejected"
        return 1
    fi
    
    if ! validate_bot_token_format "invalid"; then
        log "SUCCESS" "Invalid token format rejected"
    else
        log "ERROR" "Invalid token format accepted"
        return 1
    fi
    
    # Test chat ID validation
    if validate_chat_id "@test_channel"; then
        log "SUCCESS" "Valid chat ID (@username) accepted"
    else
        log "ERROR" "Valid chat ID (@username) rejected"
        return 1
    fi
    
    if validate_chat_id "-1001234567890"; then
        log "SUCCESS" "Valid chat ID (negative) accepted"
    else
        log "ERROR" "Valid chat ID (negative) rejected"
        return 1
    fi
    
    if ! validate_chat_id "invalid"; then
        log "SUCCESS" "Invalid chat ID rejected"
    else
        log "ERROR" "Invalid chat ID accepted"
        return 1
    fi
    
    return 0
}

# Function to test message formatting
test_message_formatting() {
    log "INFO" "Testing message formatting..."
    
    # Set up test environment
    export TELEGRAM_ENABLED="true"
    export TELEGRAM_FORMATTING_PARSE_MODE="HTML"
    export TELEGRAM_FORMATTING_INCLUDE_TIMESTAMP="true"
    export TELEGRAM_FORMATTING_INCLUDE_LOG_LEVEL="true"
    export TELEGRAM_FORMATTING_INCLUDE_SCRIPT_NAME="true"
    export TELEGRAM_FORMATTING_USE_EMOJI_INDICATORS="true"
    
    # Source logger module
    source "${PROJECT_ROOT}/scripts/core/telegram_logger.sh"
    
    # Test message formatting
    local formatted_message
    formatted_message=$(format_telegram_message "ERROR" "Test error message" "test_script")
    
    if [[ "$formatted_message" =~ 🔴.*ERROR.*test_script.*Test\ error\ message ]]; then
        log "SUCCESS" "Message formatting working correctly"
    else
        log "ERROR" "Message formatting failed: $formatted_message"
        return 1
    fi
    
    return 0
}

# Function to test rate limiting logic
test_rate_limiting() {
    log "INFO" "Testing rate limiting logic..."
    
    # Source queue module
    source "${PROJECT_ROOT}/scripts/core/telegram_queue.sh"
    
    # Initialize rate limiting
    TELEGRAM_MESSAGES_SENT=0
    TELEGRAM_WINDOW_START=$(date +%s)
    TELEGRAM_LAST_RESET=$(date +%s)
    
    # Test rate limiting check
    if check_rate_limit_queue; then
        log "SUCCESS" "Initial rate limiting check passed"
    else
        log "ERROR" "Initial rate limiting check failed"
        return 1
    fi
    
    return 0
}

# Function to test configuration summary
test_config_summary() {
    log "INFO" "Testing configuration summary..."
    
    # Source config module
    source "${PROJECT_ROOT}/scripts/core/telegram_config.sh"
    
    # Generate summary
    local summary
    summary=$(get_telegram_configuration_summary "$TEST_CONFIG")
    
    if [[ "$summary" =~ "Configuration Summary" ]] && [[ "$summary" =~ "Enabled: true" ]]; then
        log "SUCCESS" "Configuration summary generated correctly"
    else
        log "ERROR" "Configuration summary generation failed"
        return 1
    fi
    
    return 0
}

# Function to test integration with utils.sh
test_utils_integration() {
    log "INFO" "Testing integration with utils.sh..."
    
    # Set up test environment
    export TELEGRAM_ENABLED="true"
    export TELEGRAM_FILTERS_LOG_LEVELS="ERROR,WARNING,SUCCESS"
    export TELEGRAM_BOT_TOKEN="test_token"
    export TELEGRAM_CHAT_ID="@test"
    
    # Load modules
    source "${PROJECT_ROOT}/scripts/core/telegram_logger.sh"
    source "${PROJECT_ROOT}/scripts/core/telegram_security.sh"
    source "${PROJECT_ROOT}/scripts/core/telegram_queue.sh"
    
    # Test should_send_to_telegram function
    if should_send_to_telegram "ERROR" "test_script"; then
        log "SUCCESS" "should_send_to_telegram correctly allows ERROR messages"
    else
        log "ERROR" "should_send_to_telegram incorrectly blocks ERROR messages"
        return 1
    fi
    
    # Test filtered levels
    if ! should_send_to_telegram "DEBUG" "test_script"; then
        log "SUCCESS" "should_send_to_telegram correctly blocks DEBUG messages"
    else
        log "ERROR" "should_send_to_telegram incorrectly allows DEBUG messages"
        return 1
    fi
    
    return 0
}

# Main test execution
main() {
    log "INFO" "Starting Telegram Configuration System Tests"
    
    # Run tests
    local test_results=()
    
    # Test 1: Configuration loading
    if test_config_loading; then
        test_results+=("✅ Configuration loading")
    else
        test_results+=("❌ Configuration loading")
    fi
    
    # Test 2: Configuration validation
    if test_config_validation; then
        test_results+=("✅ Configuration validation")
    else
        test_results+=("❌ Configuration validation")
    fi
    
    # Test 3: Security validation
    if test_security_validation; then
        test_results+=("✅ Security validation")
    else
        test_results+=("❌ Security validation")
    fi
    
    # Test 4: Message formatting
    if test_message_formatting; then
        test_results+=("✅ Message formatting")
    else
        test_results+=("❌ Message formatting")
    fi
    
    # Test 5: Rate limiting
    if test_rate_limiting; then
        test_results+=("✅ Rate limiting")
    else
        test_results+=("❌ Rate limiting")
    fi
    
    # Test 6: Configuration summary
    if test_config_summary; then
        test_results+=("✅ Configuration summary")
    else
        test_results+=("❌ Configuration summary")
    fi
    
    # Test 7: Utils integration
    if test_utils_integration; then
        test_results+=("✅ Utils integration")
    else
        test_results+=("❌ Utils integration")
    fi
    
    # Report results
    log "INFO" "Test Results:"
    for result in "${test_results[@]}"; do
        log "INFO" "  $result"
    done
    
    # Count failures
    local failures=0
    for result in "${test_results[@]}"; do
        if [[ "$result" =~ ❌ ]]; then
            ((failures++))
        fi
    done
    
    if [[ $failures -eq 0 ]]; then
        log "SUCCESS" "All tests passed! Telegram configuration system is working correctly."
        return 0
    else
        log "ERROR" "$failures tests failed. Please review the issues above."
        return 1
    fi
}

# Run main function
main "$@"