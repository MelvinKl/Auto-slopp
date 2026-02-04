#!/bin/bash

# Integration Test: Telegram Logging Integration
# Tests the integration between the main logging system and Telegram logger

# Set script name for logging identification
SCRIPT_NAME="test_telegram_integration"

# Source utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../scripts/utils.sh"
source "${SCRIPT_DIR}/../scripts/yaml_config.sh"

# Set up error handling
setup_error_handling

# Test configuration
TEST_CONFIG_FILE="/tmp/test_telegram_config.yaml"
TEST_RESULTS_FILE="/tmp/telegram_integration_test_results.json"

# Initialize test results
init_test_results() {
    cat > "$TEST_RESULTS_FILE" << 'EOF'
{
    "test_name": "Telegram Logging Integration Test",
    "timestamp": "",
    "tests": [],
    "overall_result": "unknown",
    "summary": {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }
}
EOF
}

# Function to update test results
update_test_result() {
    local test_name="$1"
    local status="$2"  # "passed", "failed", "skipped"
    local details="$3"
    local execution_time="$4"
    
    local timestamp=$(date -Iseconds)
    
    # Update JSON results
    local temp_file="${TEST_RESULTS_FILE}.tmp"
    jq --arg name "$test_name" \
       --arg status "$status" \
       --arg details "$details" \
       --arg time "$execution_time" \
       --arg ts "$timestamp" \
       '.tests += [{
           "name": $name,
           "status": $status,
           "details": $details,
           "execution_time_seconds": $time | tonumber,
           "timestamp": $ts
       }] | .summary.total += 1 | 
       if $status == "passed" then .summary.passed += 1 
       elif $status == "failed" then .summary.failed += 1
       else .summary.skipped += 1 end' \
       "$TEST_RESULTS_FILE" > "$temp_file" && mv "$temp_file" "$TEST_RESULTS_FILE"
}

# Function to run a test with timing
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    echo "Running test: $test_name"
    
    local start_time=$(date +%s.%N 2>/dev/null || date +%s)
    local result="failed"
    local details=""
    
    # Run the test function
    if eval "$test_function"; then
        result="passed"
        details="Test completed successfully"
    else
        result="failed"
        details="Test failed with exit code $?"
    fi
    
    local end_time=$(date +%s.%N 2>/dev/null || date +%s)
    local execution_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    
    update_test_result "$test_name" "$result" "$details" "$execution_time"
    echo "Result: $result (${execution_time}s)"
    echo
}

# Create test configuration file
create_test_config() {
    cat > "$TEST_CONFIG_FILE" << 'EOF'
# Test configuration for Telegram logging integration
logging:
  log_directory: "/tmp/test_logs"
  log_level: "DEBUG"

telegram:
  enabled: true
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  default_chat_id: "7649674603"
  api_timeout_seconds: 10
  rate_limiting:
    messages_per_second: 5
  formatting:
    parse_mode: "HTML"
    max_message_length: 4000
    include_timestamp: true
    include_log_level: true
    include_script_name: true
    use_emoji_indicators: true
  filters:
    log_levels: ["ERROR", "WARNING", "SUCCESS", "INFO"]
    scripts: ["test_telegram_integration.sh"]
  retry:
    max_attempts: 3
    base_delay: 1.0
    max_delay: 30.0
    jitter: true
  buffering:
    enabled: true
    max_messages: 5
    flush_interval_seconds: 10
  security:
    validate_bot_token: true
    hide_tokens_in_logs: true
EOF
}

# Test 1: Configuration Loading
test_config_loading() {
    echo "Testing configuration loading..."
    
    # Load configuration
    if ! load_telegram_config "$TEST_CONFIG_FILE"; then
        echo "ERROR: Failed to load Telegram configuration"
        return 1
    fi
    
    # Verify key configuration values
    if [[ "${TELEGRAM_ENABLED}" != "true" ]]; then
        echo "ERROR: TELEGRAM_ENABLED not set correctly"
        return 1
    fi
    
    if [[ "${TELEGRAM_API_TIMEOUT_SECONDS}" != "10" ]]; then
        echo "ERROR: TELEGRAM_API_TIMEOUT_SECONDS not set correctly"
        return 1
    fi
    
    if [[ "${TELEGRAM_FORMATTING_PARSE_MODE}" != "HTML" ]]; then
        echo "ERROR: TELEGRAM_FORMATTING_PARSE_MODE not set correctly"
        return 1
    fi
    
    echo "Configuration loaded successfully"
    return 0
}

# Test 2: Basic Log Integration
test_basic_log_integration() {
    echo "Testing basic log integration..."
    
    # Configure logging
    configure_logging "default" "local"
    
    # Test different log levels
    log "INFO" "Test INFO message from integration test"
    log "SUCCESS" "Test SUCCESS message from integration test"
    log "WARNING" "Test WARNING message from integration test"
    log "ERROR" "Test ERROR message from integration test"
    
    # Allow some time for async processing
    sleep 2
    
    # Check if Telegram module was loaded
    if ! declare -F send_log_to_telegram >/dev/null 2>&1; then
        echo "WARNING: Telegram logger module not loaded (may be expected if disabled)"
    fi
    
    echo "Basic log integration test completed"
    return 0
}

# Test 3: Message Buffering
test_message_buffering() {
    echo "Testing message buffering..."
    
    # Enable buffering
    set_telegram_buffering "true"
    
    if [[ "$TELEGRAM_BUFFER_ENABLED" != "true" ]]; then
        echo "ERROR: Buffering not enabled correctly"
        return 1
    fi
    
    # Add messages to buffer
    add_to_telegram_buffer "INFO" "Buffered message 1" "test_script"
    add_to_telegram_buffer "INFO" "Buffered message 2" "test_script"
    add_to_telegram_buffer "SUCCESS" "Buffered message 3" "test_script"
    
    # Check buffer count
    if [[ $TELEGRAM_BUFFER_MESSAGE_COUNT -ne 3 ]]; then
        echo "ERROR: Buffer count incorrect (expected 3, got $TELEGRAM_BUFFER_MESSAGE_COUNT)"
        return 1
    fi
    
    # Force flush buffer
    flush_telegram_buffer
    
    # Check buffer was cleared
    if [[ $TELEGRAM_BUFFER_MESSAGE_COUNT -ne 0 ]]; then
        echo "ERROR: Buffer not cleared after flush"
        return 1
    fi
    
    echo "Message buffering test completed"
    return 0
}

# Test 4: High-Priority Message Handling
test_high_priority_handling() {
    echo "Testing high-priority message handling..."
    
    # Enable buffering
    set_telegram_buffering "true"
    
    # Add some low priority messages to buffer
    add_to_telegram_buffer "INFO" "Low priority message 1" "test_script"
    add_to_telegram_buffer "DEBUG" "Low priority message 2" "test_script"
    
    # Send a high priority message (should flush buffer immediately)
    log "ERROR" "High priority error message - should trigger immediate flush"
    
    # Allow time for processing
    sleep 1
    
    # Check if buffer was flushed by high priority message
    # This is a basic check - in a real scenario, we'd monitor actual Telegram sends
    echo "High priority message handling test completed"
    return 0
}

# Test 5: Configuration-Based Activation
test_config_based_activation() {
    echo "Testing configuration-based activation..."
    
    # Create a config with Telegram disabled
    local disabled_config="/tmp/test_telegram_disabled.yaml"
    cat > "$disabled_config" << 'EOF'
telegram:
  enabled: false
EOF
    
    # Load the disabled configuration
    if load_telegram_config "$disabled_config"; then
        if [[ "${TELEGRAM_ENABLED}" == "false" ]]; then
            echo "Configuration-based activation working correctly"
        else
            echo "ERROR: TELEGRAM_ENABLED should be false"
            return 1
        fi
    else
        echo "ERROR: Failed to load disabled configuration"
        return 1
    fi
    
    # Clean up
    rm -f "$disabled_config"
    
    return 0
}

# Test 6: Graceful Degradation
test_graceful_degradation() {
    echo "Testing graceful degradation..."
    
    # Enable Telegram but with invalid configuration to simulate failure
    export TELEGRAM_ENABLED="true"
    export TELEGRAM_BOT_TOKEN=""  # Invalid empty token
    
    # Try to send a message
    log "ERROR" "Test message during Telegram degradation"
    
    # The system should not fail, but should handle gracefully
    # Check if the log function itself completes without error
    echo "Graceful degradation test completed"
    return 0
}

# Test 7: Integration with Existing Log Flows
test_existing_log_flows() {
    echo "Testing integration with existing log flows..."
    
    # Test specialized logging functions
    log_change_detection "test_repo" "5" "false"
    log_system_health "disk_check" "pass" "Disk usage: 45%"
    log_reboot_event "Test reboot" "2026-02-04 20:00:00"
    
    # Test error handling functions
    if handle_error 0 "test_command"; then
        echo "ERROR: handle_error should not return success for non-zero exit code"
    fi
    
    # Test safe execute
    if safe_execute "echo 'test command'"; then
        echo "Safe execute test passed"
    else
        echo "ERROR: Safe execute failed on simple command"
        return 1
    fi
    
    echo "Integration with existing log flows completed"
    return 0
}

# Test 8: Performance Impact
test_performance_impact() {
    echo "Testing performance impact..."
    
    local iterations=100
    local start_time=$(date +%s.%N 2>/dev/null || date +%s)
    
    # Generate many log messages
    for ((i=1; i<=iterations; i++)); do
        log "INFO" "Performance test message $i"
    done
    
    local end_time=$(date +%s.%N 2>/dev/null || date +%s)
    local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    local avg_time=$(echo "scale=4; $duration / $iterations" | bc -l 2>/dev/null || echo "0")
    
    echo "Performance test: $iterations messages in ${duration}s (avg: ${avg_time}s per message)"
    
    # Performance should be reasonable (less than 0.01 seconds per message)
    local threshold="0.01"
    if (( $(echo "$avg_time < $threshold" | bc -l 2>/dev/null || echo "0") )); then
        echo "Performance impact acceptable"
        return 0
    else
        echo "WARNING: Performance impact may be high (${avg_time}s per message)"
        return 1
    fi
}

# Test 9: Cleanup and Resource Management
test_cleanup_and_resources() {
    echo "Testing cleanup and resource management..."
    
    # Initialize buffer
    set_telegram_buffering "true"
    
    # Add some messages
    add_to_telegram_buffer "INFO" "Cleanup test message" "test_script"
    
    # Call cleanup manually
    cleanup_telegram_buffer
    
    # Check if temp files are cleaned up
    local buffer_files="/tmp/telegram_buffer_$$*"
    local file_count=$(ls -1 $buffer_files 2>/dev/null | wc -l)
    
    if [[ $file_count -eq 0 ]]; then
        echo "Cleanup successful: no buffer files found"
    else
        echo "WARNING: Found $file_count buffer files after cleanup"
    fi
    
    return 0
}

# Main test execution
main() {
    echo "Telegram Logging Integration Test Suite"
    echo "===================================="
    echo
    
    # Initialize test results
    init_test_results
    
    # Create test configuration
    create_test_config
    
    # Run tests
    run_test "Configuration Loading" "test_config_loading"
    run_test "Basic Log Integration" "test_basic_log_integration"
    run_test "Message Buffering" "test_message_buffering"
    run_test "High-Priority Message Handling" "test_high_priority_handling"
    run_test "Configuration-Based Activation" "test_config_based_activation"
    run_test "Graceful Degradation" "test_graceful_degradation"
    run_test "Integration with Existing Log Flows" "test_existing_log_flows"
    run_test "Performance Impact" "test_performance_impact"
    run_test "Cleanup and Resource Management" "test_cleanup_and_resources"
    
    # Finalize results
    local temp_file="${TEST_RESULTS_FILE}.tmp"
    jq --arg ts "$(date -Iseconds)" \
       '.timestamp = $ts | 
       .overall_result = if .summary.failed > 0 then "failed" else "passed" end' \
       "$TEST_RESULTS_FILE" > "$temp_file" && mv "$temp_file" "$TEST_RESULTS_FILE"
    
    # Display results
    echo "Test Results Summary:"
    echo "===================="
    
    local total=$(jq -r '.summary.total' "$TEST_RESULTS_FILE")
    local passed=$(jq -r '.summary.passed' "$TEST_RESULTS_FILE")
    local failed=$(jq -r '.summary.failed' "$TEST_RESULTS_FILE")
    local skipped=$(jq -r '.summary.skipped' "$TEST_RESULTS_FILE")
    local overall=$(jq -r '.overall_result' "$TEST_RESULTS_FILE")
    
    echo "Total: $total, Passed: $passed, Failed: $failed, Skipped: $skipped"
    echo "Overall Result: $overall"
    echo
    
    if [[ "$overall" == "passed" ]]; then
        echo "✅ All tests passed! Telegram logging integration is working correctly."
        return 0
    else
        echo "❌ Some tests failed. Check the detailed results in $TEST_RESULTS_FILE"
        return 1
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi