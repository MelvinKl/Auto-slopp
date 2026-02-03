#!/bin/bash

# Simplified Telegram Configuration System Test Script
# Tests core functionality of Telegram configuration system

set -e

# Set script name for logging identification
SCRIPT_NAME="telegram_config_simple_test"

# Source utilities and modules
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${PROJECT_ROOT}/scripts/utils.sh"

# Set up error handling
setup_error_handling

# Test configuration file
TEST_CONFIG="/tmp/test_telegram_config.yaml"

# Cleanup function
cleanup_test() {
    [[ -f "$TEST_CONFIG" ]] && rm -f "$TEST_CONFIG"
}
trap cleanup_test EXIT

# Function to create simple test configuration
create_simple_test_config() {
    cat > "$TEST_CONFIG" << 'EOF'
# Simple test config with telegram section
sleep_duration: 100
log_level: INFO

# Telegram configuration
telegram:
  enabled: true
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  default_chat_id: "@test_channel"
  api_timeout_seconds: 10
  rate_limiting:
    messages_per_second: 5
  formatting:
    max_message_length: 4000
  retry:
    max_attempts: 3
EOF
}

# Function to test basic configuration loading
test_basic_loading() {
    log "INFO" "Testing basic configuration loading..."
    
    # Source yaml_config module
    source "${PROJECT_ROOT}/scripts/yaml_config.sh"
    
    # Load configuration
    if load_config "$TEST_CONFIG"; then
        log "SUCCESS" "Configuration loaded successfully"
        
        # Check if variables are set
        if [[ "${TELEGRAM_ENABLED:-false}" == "true" ]]; then
            log "SUCCESS" "TELEGRAM_ENABLED loaded correctly"
        else
            log "ERROR" "TELEGRAM_ENABLED not loaded correctly"
            return 1
        fi
        
        return 0
    else
        log "ERROR" "Failed to load configuration"
        return 1
    fi
}

# Function to test module loading
test_module_loading() {
    log "INFO" "Testing module loading..."
    
    # Test loading telegram modules
    if source "${PROJECT_ROOT}/scripts/core/telegram_logger.sh"; then
        log "SUCCESS" "Telegram logger module loaded"
    else
        log "ERROR" "Failed to load telegram logger module"
        return 1
    fi
    
    if source "${PROJECT_ROOT}/scripts/core/telegram_security.sh"; then
        log "SUCCESS" "Telegram security module loaded"
    else
        log "ERROR" "Failed to load telegram security module"
        return 1
    fi
    
    if source "${PROJECT_ROOT}/scripts/core/telegram_queue.sh"; then
        log "SUCCESS" "Telegram queue module loaded"
    else
        log "ERROR" "Failed to load telegram queue module"
        return 1
    fi
    
    if source "${PROJECT_ROOT}/scripts/core/telegram_config.sh"; then
        log "SUCCESS" "Telegram config module loaded"
    else
        log "ERROR" "Failed to load telegram config module"
        return 1
    fi
    
    if source "${PROJECT_ROOT}/scripts/core/telegram_health.sh"; then
        log "SUCCESS" "Telegram health module loaded"
    else
        log "ERROR" "Failed to load telegram health module"
        return 1
    fi
    
    return 0
}

# Function to test basic functions
test_basic_functions() {
    log "INFO" "Testing basic functions..."
    
    # Test message formatting
    local formatted
    if formatted=$(format_telegram_message "ERROR" "Test message" "test_script"); then
        if [[ "$formatted" =~ ERROR && "$formatted" =~ test_script && "$formatted" =~ "Test message" ]]; then
            log "SUCCESS" "Message formatting works"
        else
            log "ERROR" "Message formatting failed: $formatted"
            return 1
        fi
    else
        log "ERROR" "Failed to call format_telegram_message"
        return 1
    fi
    
    # Test token validation
    if validate_bot_token_format "123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789"; then
        log "SUCCESS" "Token validation works"
    else
        log "ERROR" "Token validation failed"
        return 1
    fi
    
    if ! validate_bot_token_format "invalid"; then
        log "SUCCESS" "Invalid token correctly rejected"
    else
        log "ERROR" "Invalid token was accepted"
        return 1
    fi
    
    # Test chat ID validation
    if validate_chat_id "@test_channel"; then
        log "SUCCESS" "Chat ID validation works"
    else
        log "ERROR" "Chat ID validation failed"
        return 1
    fi
    
    return 0
}

# Function to test integration with utils
test_utils_integration() {
    log "INFO" "Testing integration with utils.sh..."
    
    # Set up test environment
    export TELEGRAM_ENABLED="true"
    export TELEGRAM_FILTERS_LOG_LEVELS="ERROR,WARNING,SUCCESS"
    export TELEGRAM_BOT_TOKEN="test_token"
    export TELEGRAM_CHAT_ID="@test"
    
    # This should not cause any errors
    log "INFO" "Testing enhanced log function (should work silently)"
    
    # The enhanced log function should work without errors
    log "ERROR" "This is a test error message"
    
    log "SUCCESS" "Utils integration test completed"
    
    return 0
}

# Main test execution
main() {
    log "INFO" "Starting Simplified Telegram Configuration System Tests"
    
    # Create test configuration
    create_simple_test_config
    
    # Run tests
    local test_results=()
    
    # Test 1: Basic loading
    if test_basic_loading; then
        test_results+=("✅ Basic configuration loading")
    else
        test_results+=("❌ Basic configuration loading")
    fi
    
    # Test 2: Module loading
    if test_module_loading; then
        test_results+=("✅ Module loading")
    else
        test_results+=("❌ Module loading")
    fi
    
    # Test 3: Basic functions
    if test_basic_functions; then
        test_results+=("✅ Basic functions")
    else
        test_results+=("❌ Basic functions")
    fi
    
    # Test 4: Utils integration
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
        log "ERROR" "$failures tests failed. Please review issues above."
        return 1
    fi
}

# Run main function
main "$@"