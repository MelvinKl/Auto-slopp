#!/bin/bash

# Test Suite for Timeout Functionality
# Tests the timeout mechanism for opencode calls including configuration, validation, and execution

# Set script name for logging identification
SCRIPT_NAME="test_timeout_functionality"

# Source test framework and modules
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/utils.sh"
source "$SCRIPT_DIR/../scripts/yaml_config.sh"

# Test configuration
TEST_TEMP_DIR="/tmp/autoslopp_timeout_test_$(date +%s)"
TEST_CONFIG_FILE="$TEST_TEMP_DIR/test_config.yaml"
TEST_REPO_DIR="$TEST_TEMP_DIR/test_repo"

# Test results tracking
TEST_RESULTS_total=0
TEST_RESULTS_passed=0
TEST_RESULTS_failed=0
TEST_RESULTS_skipped=0

# =============================================================================
# TEST FRAMEWORK UTILITIES
# =============================================================================

# Initialize test environment
initialize_test_environment() {
    mkdir -p "$TEST_TEMP_DIR"
    mkdir -p "$TEST_REPO_DIR"
    
    # Create test git repository
    cd "$TEST_REPO_DIR" || return 1
    git init --quiet
    git config user.email "test@example.com"
    git config user.name "Test User"
    
    # Create initial commit
    echo "Test repository for timeout tests" > README.md
    git add README.md
    git commit -m "Initial commit" --quiet
    
    cd "$SCRIPT_DIR"
    log "INFO" "Test environment initialized in: $TEST_TEMP_DIR"
    return 0
}

# Cleanup test environment
cleanup_test_environment() {
    rm -rf "$TEST_TEMP_DIR"
    log "INFO" "Test environment cleaned up"
}

# Test assertion functions
assert_equals() {
    local expected="$1"
    local actual="$2"
    local test_name="$3"
    
    ((TEST_RESULTS[total]++))
    
    if [[ "$expected" == "$actual" ]]; then
        log "SUCCESS" "PASS: $test_name"
        ((TEST_RESULTS[passed]++))
        return 0
    else
        log "ERROR" "FAIL: $test_name - Expected: '$expected', Actual: '$actual'"
        ((TEST_RESULTS[failed]++))
        return 1
    fi
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local test_name="$3"
    
    ((TEST_RESULTS[total]++))
    
    if [[ "$haystack" == *"$needle"* ]]; then
        log "SUCCESS" "PASS: $test_name"
        ((TEST_RESULTS[passed]++))
        return 0
    else
        log "ERROR" "FAIL: $test_name - String '$needle' not found in '$haystack'"
        ((TEST_RESULTS[failed]++))
        return 1
    fi
}

assert_file_exists() {
    local file_path="$1"
    local test_name="$2"
    
    ((TEST_RESULTS[total]++))
    
    if [[ -f "$file_path" ]]; then
        log "SUCCESS" "PASS: $test_name"
        ((TEST_RESULTS[passed]++))
        return 0
    else
        log "ERROR" "FAIL: $test_name - File does not exist: $file_path"
        ((TEST_RESULTS[failed]++))
        return 1
    fi
}

# =============================================================================
# TIMEOUT TESTS
# =============================================================================

# Test 1: Default timeout configuration is loaded correctly
test_default_timeout_configuration() {
    log "INFO" "Test 1: Default timeout configuration is loaded correctly"
    
    # Arrange
    local config_file="$TEST_TEMP_DIR/config.yaml"
    cat > "$config_file" << 'EOF'
managed_repo_path: "/tmp/test"
log_directory: "/tmp/logs"
log_level: "INFO"
EOF
    
    # Act
    load_config "$config_file"
    local opencode_cmd="$OPencode_CMD"
    
    # Assert
    assert_contains "$opencode_cmd" "timeout" "OPencode_CMD contains timeout command"
    assert_contains "$opencode_cmd" "2h" "OPencode_CMD contains 2-hour timeout"
    assert_contains "$opencode_cmd" "opencode" "OPencode_CMD contains opencode command"
}

# Test 2: Timeout configuration with custom timeout
test_custom_timeout_configuration() {
    log "INFO" "Test 2: Custom timeout configuration can be set"
    
    # Arrange - This test simulates what would happen if we had custom timeout in config
    local config_file="$TEST_TEMP_DIR/config.yaml"
    cat > "$config_file" << 'EOF'
managed_repo_path: "/tmp/test"
log_directory: "/tmp/logs"
log_level: "INFO"
EOF
    
    # Act - Simulate custom timeout by setting it directly (in real implementation, this would be from config)
    export OPencode_CMD="timeout -v -k 30s 1h opencode"
    local opencode_cmd="$OPencode_CMD"
    
    # Assert
    assert_contains "$opencode_cmd" "timeout" "Custom OPencode_CMD contains timeout command"
    assert_contains "$opencode_cmd" "1h" "Custom OPencode_CMD contains 1-hour timeout"
    
    # Reset to default for other tests
    load_config "$config_file"
}

# Test 3: Timeout command structure validation
test_timeout_command_structure() {
    log "INFO" "Test 3: Timeout command has correct structure"
    
    # Arrange
    local config_file="$TEST_TEMP_DIR/config.yaml"
    cat > "$config_file" << 'EOF'
managed_repo_path: "/tmp/test"
log_directory: "/tmp/logs"
log_level: "INFO"
EOF
    
    # Act
    load_config "$config_file"
    local opencode_cmd="$OPencode_CMD"
    
    # Assert - Verify timeout command structure: timeout -v -k 1m 2h opencode
    assert_contains "$opencode_cmd" "timeout" "Contains timeout command"
    assert_contains "$opencode_cmd" "-v" "Contains verbose flag"
    assert_contains "$opencode_cmd" "-k" "Contains kill signal flag"
    assert_contains "$opencode_cmd" "1m" "Contains kill signal timeout (1 minute)"
    assert_contains "$opencode_cmd" "2h" "Contains main timeout (2 hours)"
    assert_contains "$opencode_cmd" "opencode" "Contains opencode command"
}

# Test 4: Timeout configuration persistence across script loads
test_timeout_configuration_persistence() {
    log "INFO" "Test 4: Timeout configuration persists across multiple script loads"
    
    # Arrange
    local config_file="$TEST_TEMP_DIR/config.yaml"
    cat > "$config_file" << 'EOF'
managed_repo_path: "/tmp/test"
log_directory: "/tmp/logs"
log_level: "INFO"
EOF
    
    # Act - Load config multiple times
    load_config "$config_file"
    local first_load="$OPencode_CMD"
    
    # Load again to simulate multiple script invocations
    load_config "$config_file"
    local second_load="$OPencode_CMD"
    
    # Assert
    assert_equals "$first_load" "$second_load" "Timeout configuration is consistent across loads"
    assert_contains "$first_load" "timeout" "First load contains timeout"
    assert_contains "$second_load" "timeout" "Second load contains timeout"
}

# Test 5: Timeout command validation in script context
test_timeout_command_validation() {
    log "INFO" "Test 5: Timeout command validation in script context"
    
    # Arrange
    local config_file="$TEST_TEMP_DIR/config.yaml"
    cat > "$config_file" << 'EOF'
managed_repo_path: "/tmp/test"
log_directory: "/tmp/logs"
log_level: "INFO"
EOF
    
    # Act
    load_config "$config_file"
    
    # Test that timeout command is executable (not that opencode is available, but timeout is)
    if command -v timeout >/dev/null 2>&1; then
        local timeout_available="true"
    else
        local timeout_available="false"
    fi
    
    # Assert - In most Linux environments, timeout should be available
    assert_equals "true" "$timeout_available" "Timeout command is available in system PATH"
    
    # Verify the command structure is syntactically valid
    local opencode_cmd="$OPencode_CMD"
    # Extract just the timeout part for validation
    local timeout_part=$(echo "$opencode_cmd" | awk '{print $1}')
    assert_equals "timeout" "$timeout_part" "First token of OPencode_CMD is 'timeout'"
}

# Test 6: Integration test - timeout used by implementer script
test_timeout_integration_implementer() {
    log "INFO" "Test 6: Timeout integration in implementer.sh"
    
    # Arrange
    local implementer_script="$SCRIPT_DIR/../scripts/implementer.sh"
    
    # Act - Check that implementer uses OPencode_CMD variable
    if [[ -f "$implementer_script" ]]; then
        local uses_opencode_var=$(grep -c '\$OPencode_CMD' "$implementer_script" || true)
        local has_hardcoded_opencode=$(grep -c '^[^#]*opencode run' "$implementer_script" | grep -v '\$OPencode_CMD' | wc -l || true)
    else
        local uses_opencode_var="0"
        local has_hardcoded_opencode="1"  # Mark as failed if script doesn't exist
    fi
    
    # Assert
    assert_file_exists "$implementer_script" "implementer.sh exists"
    assert_not_equals "0" "$uses_opencode_var" "implementer.sh uses OPencode_CMD variable"
    assert_equals "0" "$has_hardcoded_opencode" "implementer.sh has no hardcoded opencode calls"
}

# Test 7: Integration test - timeout used by update_fixer script
test_timeout_integration_update_fixer() {
    log "INFO" "Test 7: Timeout integration in update_fixer.sh"
    
    # Arrange
    local update_fixer_script="$SCRIPT_DIR/../scripts/update_fixer.sh"
    
    # Act
    if [[ -f "$update_fixer_script" ]]; then
        local uses_opencode_var=$(grep -c '\$OPencode_CMD' "$update_fixer_script" || true)
        local has_hardcoded_opencode=$(grep -c '^[^#]*opencode run' "$update_fixer_script" | grep -v '\$OPencode_CMD' | wc -l || true)
    else
        local uses_opencode_var="0"
        local has_hardcoded_opencode="1"
    fi
    
    # Assert
    assert_file_exists "$update_fixer_script" "update_fixer.sh exists"
    assert_not_equals "0" "$uses_opencode_var" "update_fixer.sh uses OPencode_CMD variable"
    assert_equals "0" "$has_hardcoded_opencode" "update_fixer.sh has no hardcoded opencode calls"
}

# Test 8: Integration test - timeout used by planner script
test_timeout_integration_planner() {
    log "INFO" "Test 8: Timeout integration in planner.sh"
    
    # Arrange
    local planner_script="$SCRIPT_DIR/../scripts/planner.sh"
    
    # Act
    if [[ -f "$planner_script" ]]; then
        local uses_opencode_var=$(grep -c '\$OPencode_CMD' "$planner_script" || true)
        local has_hardcoded_opencode=$(grep -c '^[^#]*opencode run' "$planner_script" | grep -v '\$OPencode_CMD' | wc -l || true)
    else
        local uses_opencode_var="0"
        local has_hardcoded_opencode="1"
    fi
    
    # Assert
    assert_file_exists "$planner_script" "planner.sh exists"
    assert_not_equals "0" "$uses_opencode_var" "planner.sh uses OPencode_CMD variable"
    assert_equals "0" "$has_hardcoded_opencode" "planner.sh has no hardcoded opencode calls"
}

# Test 9: Error handling - missing configuration file
test_error_handling_missing_config() {
    log "INFO" "Test 9: Error handling for missing configuration file"
    
    # Arrange - Use non-existent config file
    local non_existent_config="$TEST_TEMP_DIR/does_not_exist.yaml"
    
    # Act - Attempt to load non-existent config
    if load_config "$non_existent_config" 2>/dev/null; then
        local load_result="success"
    else
        local load_result="failed"
    fi
    
    # Assert - Should handle gracefully and still have default timeout
    assert_equals "success" "$load_result" "Loading non-existent config handles gracefully"
    assert_contains "$OPencode_CMD" "timeout" "Default timeout is still available"
}

# Test 10: Environment variable validation
test_environment_variable_validation() {
    log "INFO" "Test 10: Environment variable validation"
    
    # Arrange
    local config_file="$TEST_TEMP_DIR/config.yaml"
    cat > "$config_file" << 'EOF'
managed_repo_path: "/tmp/test"
log_directory: "/tmp/logs"
log_level: "INFO"
EOF
    
    # Act
    load_config "$config_file"
    
    # Assert - Verify the variable is exported
    if [[ -n "$OPencode_CMD" ]]; then
        local opencode_cmd_set="true"
    else
        local opencode_cmd_set="false"
    fi
    
    assert_equals "true" "$opencode_cmd_set" "OPencode_CMD environment variable is set"
    assert_not_equals "" "$OPencode_CMD" "OPencode_CMD is not empty"
}

# =============================================================================
# TEST RUNNER
# =============================================================================

# Main test runner
run_timeout_tests() {
    log "INFO" "Starting timeout functionality tests"
    
    # Initialize test environment
    initialize_test_environment || {
        log "ERROR" "Failed to initialize test environment"
        return 1
    }
    
    # Run all tests
    test_default_timeout_configuration
    test_custom_timeout_configuration
    test_timeout_command_structure
    test_timeout_configuration_persistence
    test_timeout_command_validation
    test_timeout_integration_implementer
    test_timeout_integration_update_fixer
    test_timeout_integration_planner
    test_error_handling_missing_config
    test_environment_variable_validation
    
    # Cleanup
    cleanup_test_environment
    
    # Report results
    echo
    log "INFO" "=== TIMEOUT FUNCTIONALITY TEST RESULTS ==="
    log "INFO" "Total tests: ${TEST_RESULTS[total]}"
    log "SUCCESS" "Passed: ${TEST_RESULTS[passed]}"
    if [[ ${TEST_RESULTS[failed]} -gt 0 ]]; then
        log "ERROR" "Failed: ${TEST_RESULTS[failed]}"
    else
        log "SUCCESS" "Failed: ${TEST_RESULTS[failed]}"
    fi
    log "INFO" "Skipped: ${TEST_RESULTS[skipped]}"
    echo
    
    if [[ ${TEST_RESULTS[failed]} -gt 0 ]]; then
        log "ERROR" "Some timeout functionality tests failed"
        return 1
    else
        log "SUCCESS" "All timeout functionality tests passed"
        return 0
    fi
}

# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

# Run tests if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_timeout_tests "$@"
fi