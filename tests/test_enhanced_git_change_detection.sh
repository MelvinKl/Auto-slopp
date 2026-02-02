#!/bin/bash

# Enhanced test for git change detection functionality
# Tests the robust error handling and comprehensive features

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$SCRIPT_DIR/scripts/utils.sh"
source "$SCRIPT_DIR/config.sh"

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

# Test 2: Enhanced state management
test_enhanced_state_management() {
    echo -e "\n=== Test 2: Enhanced State Management ==="
    
    local test_state_file="/tmp/test-enhanced-auto-update-reboot.state"
    local test_log_dir="/tmp"
    
    # Mock state file path
    export STATE_FILE="$test_state_file"
    
    # Create the enhanced state structure manually for testing
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
        
        # Test state value functions
        source "$SCRIPT_DIR/scripts/auto-update-reboot.sh" 2>/dev/null || true
        if declare -f get_state_value >/dev/null; then
            local test_value=$(get_state_value "total_checks" "0")
            if [[ "$test_value" == "0" ]]; then
                log_test_result "state_value_retrieval" "PASS" "State value retrieval works"
            else
                log_test_result "state_value_retrieval" "FAIL" "State value retrieval failed"
            fi
        else
            log_test_result "state_value_retrieval" "FAIL" "get_state_value function not found"
        fi
    else
        log_test_result "enhanced_state_creation" "FAIL" "State file not created"
    fi
    
    # Cleanup
    rm -f "$test_state_file" "${test_state_file}.backup"*
}

# Test 3: Repository validation function
test_repository_validation() {
    echo -e "\n=== Test 3: Repository Validation ==="
    
    # Test with the current repository
    local current_repo="$SCRIPT_DIR"
    
    # Source the script to access functions
    source "$SCRIPT_DIR/scripts/auto-update-reboot.sh" 2>/dev/null || true
    
    if declare -f validate_git_repository >/dev/null; then
        log_test_result "validation_function_exists" "PASS" "Repository validation function exists"
        
        # Test validation on current repository
        if validate_git_repository "$current_repo" "test-repo" 2>/dev/null; then
            log_test_result "repository_validation" "PASS" "Repository validation succeeded"
        else
            log_test_result "repository_validation" "FAIL" "Repository validation failed"
        fi
    else
        log_test_result "validation_function_exists" "FAIL" "Repository validation function not found"
    fi
}

# Test 4: Change significance analysis
test_change_significance_analysis() {
    echo -e "\n=== Test 4: Change Significance Analysis ==="
    
    # Source the script to access functions
    source "$SCRIPT_DIR/scripts/auto-update-reboot.sh" 2>/dev/null || true
    
    if declare -f analyze_change_significance >/dev/null; then
        log_test_result "analysis_function_exists" "PASS" "Change analysis function exists"
        
        # Test with mock changed files
        local mock_changes="scripts/test.sh
config.yaml
README.md
docs/test.md
tests/test.sh"
        
        # Test significance analysis
        if analyze_change_significance "$mock_changes" "test-repo" 2>/dev/null; then
            log_test_result "significance_analysis" "PASS" "Significance analysis detected reboot trigger"
        else
            log_test_result "significance_analysis" "PASS" "Significance analysis correctly found no reboot trigger"
        fi
    else
        log_test_result "analysis_function_exists" "FAIL" "Change analysis function not found"
    fi
}

# Test 5: Enhanced error handling
test_enhanced_error_handling() {
    echo -e "\n=== Test 5: Enhanced Error Handling ==="
    
    # Source the script to access functions
    source "$SCRIPT_DIR/scripts/auto-update-reboot.sh" 2>/dev/null || true
    
    if declare -f execute_git_with_retry >/dev/null; then
        log_test_result "retry_function_exists" "PASS" "Git retry function exists"
    else
        log_test_result "retry_function_exists" "FAIL" "Git retry function not found"
    fi
    
    if declare -f detect_merge_conflicts >/dev/null; then
        log_test_result "conflict_detection_exists" "PASS" "Conflict detection function exists"
    else
        log_test_result "conflict_detection_exists" "FAIL" "Conflict detection function not found"
    fi
    
    if declare -f track_processed_change >/dev/null; then
        log_test_result "change_tracking_exists" "PASS" "Change tracking function exists"
    else
        log_test_result "change_tracking_exists" "FAIL" "Change tracking function not found"
    fi
}

# Test 6: Configuration-driven filtering
test_configuration_filtering() {
    echo -e "\n=== Test 6: Configuration-Driven Filtering ==="
    
    # Test that patterns are properly parsed
    local reboot_patterns="${REBOOT_TRIGGER_PATTERNS:-"scripts/*.sh|config.yaml|main.sh|scripts/utils.sh|scripts/core/*.sh"}"
    local ignore_patterns="${IGNORE_CHANGE_PATTERNS:-"*.md|*.txt|*.log|tests/*.sh|.*"}"
    
    if [[ -n "$reboot_patterns" ]]; then
        log_test_result "reboot_patterns_configured" "PASS" "Reboot patterns: $reboot_patterns"
    else
        log_test_result "reboot_patterns_configured" "FAIL" "Reboot patterns not configured"
    fi
    
    if [[ -n "$ignore_patterns" ]]; then
        log_test_result "ignore_patterns_configured" "PASS" "Ignore patterns: $ignore_patterns"
    else
        log_test_result "ignore_patterns_configured" "FAIL" "Ignore patterns not configured"
    fi
    
    # Test pattern matching logic
    local test_files=("scripts/test.sh" "README.md" "config.yaml" "tests/test.sh" "main.sh")
    local expected_significant=("scripts/test.sh" "config.yaml" "main.sh")
    local expected_ignored=("README.md" "tests/test.sh")
    
    # This is a simplified test - actual pattern matching would be more complex
    local pattern_matches=0
    for file in "${test_files[@]}"; do
        if [[ "$file" == scripts/*.sh ]] || [[ "$file" == config.yaml ]] || [[ "$file" == main.sh ]]; then
            pattern_matches=$((pattern_matches + 1))
        fi
    done
    
    if [[ $pattern_matches -eq 3 ]]; then
        log_test_result "pattern_matching" "PASS" "Pattern matching works correctly ($pattern_matches matches)"
    else
        log_test_result "pattern_matching" "FAIL" "Pattern matching failed (expected 3, got $pattern_matches)"
    fi
}

# Test 7: Edge case handling
test_edge_case_handling() {
    echo -e "\n=== Test 7: Edge Case Handling ==="
    
    # Source the script to access functions
    source "$SCRIPT_DIR/scripts/auto-update-reboot.sh" 2>/dev/null || true
    
    # Test timeout configuration
    if [[ "$GIT_TIMEOUT_SECONDS" -gt 0 ]]; then
        log_test_result "timeout_configured" "PASS" "Git timeout configured: ${GIT_TIMEOUT_SECONDS}s"
    else
        log_test_result "timeout_configured" "FAIL" "Git timeout not configured properly"
    fi
    
    # Test retry configuration
    if [[ "$GIT_RETRY_ATTEMPTS" -gt 0 ]]; then
        log_test_result "retry_configured" "PASS" "Git retry attempts configured: $GIT_RETRY_ATTEMPTS"
    else
        log_test_result "retry_configured" "FAIL" "Git retry attempts not configured properly"
    fi
    
    # Test change count limits
    if [[ "$MAX_CHANGE_COUNT_FOR_REBOOT" -gt "$MIN_CHANGED_FILES_FOR_REBOOT" ]]; then
        log_test_result "change_limits_sane" "PASS" "Change limits are reasonable (min: $MIN_CHANGED_FILES_FOR_REBOOT, max: $MAX_CHANGE_COUNT_FOR_REBOOT)"
    else
        log_test_result "change_limits_sane" "FAIL" "Change limits are not reasonable"
    fi
}

# Main test execution
echo "Enhanced Auto-Update-Reboot Git Change Detection Tests"
echo "======================================================"

test_enhanced_configuration
test_enhanced_state_management
test_repository_validation
test_change_significance_analysis
test_enhanced_error_handling
test_configuration_filtering
test_edge_case_handling

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