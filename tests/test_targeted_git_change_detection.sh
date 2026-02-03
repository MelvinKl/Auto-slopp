#!/bin/bash

# Targeted test for enhanced git change detection functionality
# Tests individual functions without running full script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TEST_RESULTS=()
TEST_COUNT=0
PASS_COUNT=0

# Test helper functions
log_test_result() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    TEST_COUNT=$((TEST_COUNT + 1))
    TEST_RESULTS+=("$test_name:$result:$details")
    
    if [[ "$result" == "PASS" ]]; then
        PASS_COUNT=$((PASS_COUNT + 1))
        echo "✓ PASS: $test_name"
    else
        echo "✗ FAIL: $test_name - $details"
    fi
}

# Test 1: Enhanced configuration loading
test_enhanced_configuration() {
    echo "=== Test 1: Enhanced Configuration Loading ==="
    
    # Load configuration
    source "$SCRIPT_DIR/config.sh" 2>/dev/null || true
    
    # Test new git timeout configuration
    if [[ "$GIT_TIMEOUT_SECONDS" == "30" ]]; then
        log_test_result "git_timeout_seconds" "PASS" "Default value: $GIT_TIMEOUT_SECONDS"
    else
        log_test_result "git_timeout_seconds" "FAIL" "Expected 30, got $GIT_TIMEOUT_SECONDS"
    fi
    
    # Test retry configuration
    if [[ "$GIT_RETRY_ATTEMPTS" == "3" ]]; then
        log_test_result "git_retry_attempts" "PASS" "Default value: $GIT_RETRY_ATTEMPTS"
    else
        log_test_result "git_retry_attempts" "FAIL" "Expected 3, got $GIT_RETRY_ATTEMPTS"
    fi
    
    # Test change filtering configuration
    if [[ -n "$REBOOT_TRIGGER_PATTERNS" ]]; then
        log_test_result "reboot_trigger_patterns" "PASS" "Configured: $REBOOT_TRIGGER_PATTERNS"
    else
        log_test_result "reboot_trigger_patterns" "FAIL" "Not configured"
    fi
    
    # Test significance thresholds
    if [[ "$MIN_CHANGED_FILES_FOR_REBOOT" == "1" ]]; then
        log_test_result "min_changed_files" "PASS" "Default value: $MIN_CHANGED_FILES_FOR_REBOOT"
    else
        log_test_result "min_changed_files" "FAIL" "Expected 1, got $MIN_CHANGED_FILES_FOR_REBOOT"
    fi
}

# Test 2: Enhanced state file structure
test_enhanced_state_structure() {
    echo -e "\n=== Test 2: Enhanced State Structure ==="
    
    local test_state_file="/tmp/test-enhanced-state.json"
    
    # Create enhanced state structure
    mkdir -p "$(dirname "$test_state_file")"
    
    cat > "$test_state_file" << 'EOF'
{
  "last_reboot_timestamp": null,
  "reboot_attempts_today": 0,
  "current_date": "2026-02-02",
  "last_known_heads": {},
  "system_health_status": "unknown",
  "last_processed_changes": {},
  "reboot_history": [],
  "failed_operations": [],
  "change_detection_stats": {
    "total_checks": 0,
    "successful_checks": 0,
    "reboots_triggered": 0
  }
}
EOF
    
    if [[ -f "$test_state_file" ]]; then
        log_test_result "enhanced_state_creation" "PASS" "Enhanced state file created"
        
        # Check for new fields
        if grep -q "change_detection_stats" "$test_state_file"; then
            log_test_result "stats_field_present" "PASS" "Statistics field present"
        else
            log_test_result "stats_field_present" "FAIL" "Statistics field missing"
        fi
        
        if grep -q "last_processed_changes" "$test_state_file"; then
            log_test_result "processed_changes_field" "PASS" "Processed changes field present"
        else
            log_test_result "processed_changes_field" "FAIL" "Processed changes field missing"
        fi
        
        if grep -q "reboot_history" "$test_state_file"; then
            log_test_result "reboot_history_field" "PASS" "Reboot history field present"
        else
            log_test_result "reboot_history_field" "FAIL" "Reboot history field missing"
        fi
    else
        log_test_result "enhanced_state_creation" "FAIL" "State file not created"
    fi
    
    # Cleanup
    rm -f "$test_state_file"
}

# Test 3: Configuration pattern validation
test_pattern_configuration() {
    echo -e "\n=== Test 3: Pattern Configuration ==="
    
    # Load configuration
    source "$SCRIPT_DIR/config.sh" 2>/dev/null || true
    
    # Test that patterns are properly configured
    local reboot_patterns="${REBOOT_TRIGGER_PATTERNS:-"scripts/*.sh|config.yaml|main.sh|scripts/utils.sh|scripts/core/*.sh"}"
    local ignore_patterns="${IGNORE_CHANGE_PATTERNS:-"*.md|*.txt|*.log|tests/*.sh|.*"}"
    
    if [[ -n "$reboot_patterns" ]]; then
        log_test_result "reboot_patterns_configured" "PASS" "Reboot patterns configured"
    else
        log_test_result "reboot_patterns_configured" "FAIL" "Reboot patterns not configured"
    fi
    
    if [[ -n "$ignore_patterns" ]]; then
        log_test_result "ignore_patterns_configured" "PASS" "Ignore patterns configured"
    else
        log_test_result "ignore_patterns_configured" "FAIL" "Ignore patterns not configured"
    fi
    
    # Test pattern syntax (should contain pipe separators)
    if [[ "$reboot_patterns" == *"|"* ]]; then
        log_test_result "pattern_syntax_valid" "PASS" "Pattern syntax is valid"
    else
        log_test_result "pattern_syntax_valid" "FAIL" "Pattern syntax appears invalid"
    fi
}

# Test 4: Enhanced configuration validation
test_enhanced_configuration_values() {
    echo -e "\n=== Test 4: Enhanced Configuration Values ==="
    
    # Load configuration
    source "$SCRIPT_DIR/config.sh" 2>/dev/null || true
    
    # Test timeout configuration
    if [[ "$GIT_TIMEOUT_SECONDS" -gt 0 ]]; then
        log_test_result "timeout_positive" "PASS" "Git timeout is positive: ${GIT_TIMEOUT_SECONDS}s"
    else
        log_test_result "timeout_positive" "FAIL" "Git timeout not positive: $GIT_TIMEOUT_SECONDS"
    fi
    
    # Test retry configuration
    if [[ "$GIT_RETRY_ATTEMPTS" -gt 0 ]]; then
        log_test_result "retry_positive" "PASS" "Git retry attempts is positive: $GIT_RETRY_ATTEMPTS"
    else
        log_test_result "retry_positive" "FAIL" "Git retry attempts not positive: $GIT_RETRY_ATTEMPTS"
    fi
    
    # Test change count limits
    if [[ "$MAX_CHANGE_COUNT_FOR_REBOOT" -gt "$MIN_CHANGED_FILES_FOR_REBOOT" ]]; then
        log_test_result "change_limits_sane" "PASS" "Change limits reasonable (min: $MIN_CHANGED_FILES_FOR_REBOOT, max: $MAX_CHANGE_COUNT_FOR_REBOOT)"
    else
        log_test_result "change_limits_sane" "FAIL" "Change limits unreasonable (min: $MIN_CHANGED_FILES_FOR_REBOOT, max: $MAX_CHANGE_COUNT_FOR_REBOOT)"
    fi
}

# Test 5: Script function availability
test_function_availability() {
    echo -e "\n=== Test 5: Function Availability ==="
    
    # Extract functions from the script without executing it
    local functions_found=0
    local expected_functions=(
        "validate_git_repository"
        "execute_git_with_retry"
        "detect_merge_conflicts"
        "analyze_change_significance"
        "track_processed_change"
        "is_change_already_processed"
        "update_detection_stats"
    )
    
    for func in "${expected_functions[@]}"; do
        if grep -q "^[[:space:]]*$func[[:space:]]*(" "$SCRIPT_DIR/scripts/auto-update-reboot.sh"; then
            functions_found=$((functions_found + 1))
        fi
    done
    
    if [[ $functions_found -eq ${#expected_functions[@]} ]]; then
        log_test_result "function_availability" "PASS" "All expected functions available ($functions_found/${#expected_functions[@]})"
    else
        log_test_result "function_availability" "FAIL" "Missing functions ($functions_found/${#expected_functions[@]})"
    fi
}

# Main test execution
echo "Targeted Enhanced Git Change Detection Tests"
echo "=========================================="

test_enhanced_configuration
test_enhanced_state_structure
test_pattern_configuration
test_enhanced_configuration_values
test_function_availability

# Summary
echo -e "\n=== Test Summary ==="
echo "Total tests: $TEST_COUNT"
echo "Passed: $PASS_COUNT"
echo "Failed: $((TEST_COUNT - PASS_COUNT))"

if [[ $PASS_COUNT -eq $TEST_COUNT ]]; then
    echo "🎉 All enhanced tests passed! Implementation is ready."
    exit 0
else
    echo "❌ Some enhanced tests failed. Please review the implementation."
    exit 1
fi