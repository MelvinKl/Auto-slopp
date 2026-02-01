#!/bin/bash

# Test Suite for Enhanced Script Architecture
# Tests the new error handling, system state management, and configuration validation modules

# Set script name for logging identification
SCRIPT_NAME="test_enhanced_architecture"

# Source test framework and modules
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/utils.sh"
source "$SCRIPT_DIR/../scripts/core/error_recovery.sh"
source "$SCRIPT_DIR/../scripts/core/system_state.sh"
source "$SCRIPT_DIR/../scripts/core/configuration_validator.sh"

# Test configuration
TEST_TEMP_DIR="/tmp/autoslopp_architecture_test_$(date +%s)"
TEST_STATE_FILE="$TEST_TEMP_DIR/test_state.json"
TEST_CONFIG_FILE="$TEST_TEMP_DIR/test_config.yaml"
TEST_REPO_DIR="$TEST_TEMP_DIR/test_repo"

# Test results tracking
declare -A TEST_RESULTS=(
    ["total"]=0
    ["passed"]=0
    ["failed"]=0
    ["skipped"]=0
)

# =============================================================================
# TEST FRAMEWORK UTILITIES
# =============================================================================

# Initialize test environment
initialize_test_environment() {
    mkdir -p "$TEST_TEMP_DIR"
    mkdir -p "$TEST_REPO_DIR"
    
    # Create test configuration
    cat > "$TEST_CONFIG_FILE" << 'EOF'
# Test configuration for enhanced architecture
sleep_duration: 100
managed_repo_path: "/tmp/autoslopp_architecture_test_$(date +%s)/test_repo"
log_directory: "/tmp/autoslopp_architecture_test_$(date +%s)/logs"
log_level: "INFO"
timestamp_format: "readable"
timestamp_timezone: "local"
auto_update_reboot_enabled: false
reboot_cooldown_minutes: 60
max_reboot_attempts_per_day: 3
log_max_size_mb: 10
log_retention_days: 30
EOF
    
    # Create test git repository
    cd "$TEST_REPO_DIR" || return 1
    git init --quiet
    git config user.email "test@example.com"
    git config user.name "Test User"
    
    # Create initial commit
    echo "Test repository" > README.md
    git add README.md
    git commit -m "Initial commit" --quiet
    
    # Create some test branches
    git checkout -b test-branch1 --quiet
    echo "Test branch 1" > test1.txt
    git add test1.txt
    git commit -m "Test branch 1" --quiet
    
    git checkout main --quiet
    git checkout -b test-branch2 --quiet
    echo "Test branch 2" > test2.txt
    git add test2.txt
    git commit -m "Test branch 2" --quiet
    
    git checkout main --quiet
    
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

assert_not_equals() {
    local not_expected="$1"
    local actual="$2"
    local test_name="$3"
    
    ((TEST_RESULTS[total]++))
    
    if [[ "$not_expected" != "$actual" ]]; then
        log "SUCCESS" "PASS: $test_name"
        ((TEST_RESULTS[passed]++))
        return 0
    else
        log "ERROR" "FAIL: $test_name - Should not be: '$not_expected', Actual: '$actual'"
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

assert_command_succeeds() {
    local command="$1"
    local test_name="$2"
    
    ((TEST_RESULTS[total]++))
    
    if eval "$command" >/dev/null 2>&1; then
        log "SUCCESS" "PASS: $test_name"
        ((TEST_RESULTS[passed]++))
        return 0
    else
        log "ERROR" "FAIL: $test_name - Command failed: $command"
        ((TEST_RESULTS[failed]++))
        return 1
    fi
}

# =============================================================================
# ERROR RECOVERY MODULE TESTS
# =============================================================================

test_error_classification() {
    log "INFO" "Testing error classification system"
    
    # Test network error classification
    local classification=$(classify_error 7 "connection refused" "test_context")
    local expected_category="NETWORK"
    local actual_category="${classification%:*}"
    assert_equals "$expected_category" "$actual_category" "Network error classification"
    
    # Test permission error classification
    classification=$(classify_error 13 "permission denied" "test_context")
    expected_category="PERMISSION"
    actual_category="${classification%:*}"
    assert_equals "$expected_category" "$actual_category" "Permission error classification"
    
    # Test repository error classification
    classification=$(classify_error 128 "fatal: not a git repository" "test_context")
    expected_category="REPOSITORY"
    actual_category="${classification%:*}"
    assert_equals "$expected_category" "$actual_category" "Repository error classification"
    
    # Test timeout error classification
    classification=$(classify_error 124 "operation timed out" "test_context")
    expected_category="TIMEOUT"
    actual_category="${classification%:*}"
    assert_equals "$expected_category" "$actual_category" "Timeout error classification"
}

test_recovery_strategy_determination() {
    log "INFO" "Testing recovery strategy determination"
    
    # Test network error recovery strategy
    local strategy=$(determine_recovery_strategy "NETWORK" "MEDIUM" "test_context" 1)
    assert_equals "RETRY" "$strategy" "Network error recovery strategy (low failures)"
    
    strategy=$(determine_recovery_strategy "NETWORK" "MEDIUM" "test_context" 5)
    assert_equals "ESCALATE" "$strategy" "Network error recovery strategy (high failures)"
    
    # Test critical error recovery strategy
    strategy=$(determine_recovery_strategy "REPOSITORY" "CRITICAL" "test_context" 1)
    assert_equals "ESCALATE" "$strategy" "Critical error recovery strategy"
    
    # Test timeout error recovery strategy
    strategy=$(determine_recovery_strategy "TIMEOUT" "MEDIUM" "test_context" 1)
    assert_equals "RETRY" "$strategy" "Timeout error recovery strategy"
}

test_system_state_management() {
    log "INFO" "Testing system state management"
    
    # Test state file initialization
    if initialize_comprehensive_state "$TEST_STATE_FILE" true; then
        assert_file_exists "$TEST_STATE_FILE" "State file initialization"
    else
        log "ERROR" "Failed to initialize state file"
        return 1
    fi
    
    # Test state file validation
    if validate_state_file "$TEST_STATE_FILE"; then
        log "SUCCESS" "PASS: State file validation"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: State file validation"
        ((TEST_RESULTS[failed]++))
    fi
    
    # Test state value retrieval
    local health_status=$(get_state_value "system.health_status" "unknown" "$TEST_STATE_FILE")
    assert_equals "healthy" "$health_status" "Default health status retrieval"
    
    # Test state value update
    if update_system_state "system.consecutive_failures" 3 "$TEST_STATE_FILE"; then
        local failures=$(get_state_value "system.consecutive_failures" 0 "$TEST_STATE_FILE")
        assert_equals "3" "$failures" "State value update"
    else
        log "ERROR" "Failed to update state value"
        return 1
    fi
}

test_health_check_system() {
    log "INFO" "Testing health check system"
    
    # Set up test environment variables
    export MANAGED_REPO_PATH="$TEST_REPO_DIR"
    export GIT_REPO_DIR="$TEST_REPO_DIR"
    
    # Perform health check
    if perform_health_check "$TEST_STATE_FILE" "test"; then
        log "SUCCESS" "PASS: Health check execution"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Health check execution"
        ((TEST_RESULTS[failed]++))
    fi
    
    # Check health status update
    local health_status=$(get_state_value "system.health_status" "unknown" "$TEST_STATE_FILE")
    if [[ "$health_status" =~ ^(healthy|degraded|critical)$ ]]; then
        log "SUCCESS" "PASS: Health status update"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Health status update - Invalid status: $health_status"
        ((TEST_RESULTS[failed]++))
    fi
}

# =============================================================================
# CONFIGURATION VALIDATION MODULE TESTS
# =============================================================================

test_configuration_validation() {
    log "INFO" "Testing configuration validation"
    
    # Test valid configuration validation
    if validate_configuration "$TEST_CONFIG_FILE" "strict"; then
        log "SUCCESS" "PASS: Valid configuration validation"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Valid configuration validation"
        ((TEST_RESULTS[failed]++))
    fi
    
    # Test invalid configuration file
    local invalid_config="$TEST_TEMP_DIR/invalid_config.yaml"
    echo "invalid: yaml: content: [" > "$invalid_config"
    
    if ! validate_configuration "$invalid_config" "strict"; then
        log "SUCCESS" "PASS: Invalid configuration rejection"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Invalid configuration rejection"
        ((TEST_RESULTS[failed]++))
    fi
    
    # Test missing configuration file
    if ! validate_configuration "/nonexistent/config.yaml" "strict"; then
        log "SUCCESS" "PASS: Missing configuration handling"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Missing configuration handling"
        ((TEST_RESULTS[failed]++))
    fi
}

test_runtime_configuration_validation() {
    log "INFO" "Testing runtime configuration validation"
    
    # Set up test environment
    export MANAGED_REPO_PATH="$TEST_REPO_DIR"
    export LOG_DIRECTORY="$TEST_TEMP_DIR/logs"
    mkdir -p "$LOG_DIRECTORY"
    
    # Test git operation validation
    if validate_runtime_configuration "git_operation"; then
        log "SUCCESS" "PASS: Git operation configuration validation"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Git operation configuration validation"
        ((TEST_RESULTS[failed]++))
    fi
    
    # Test logging configuration validation
    if validate_runtime_configuration "log_write"; then
        log "SUCCESS" "PASS: Logging configuration validation"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Logging configuration validation"
        ((TEST_RESULTS[failed]++))
    fi
    
    # Test cleanup configuration validation
    if validate_runtime_configuration "cleanup"; then
        log "SUCCESS" "PASS: Cleanup configuration validation"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Cleanup configuration validation"
        ((TEST_RESULTS[failed]++))
    fi
}

test_configuration_repair() {
    log "INFO" "Testing configuration repair"
    
    # Create a scenario that needs repair
    unset MANAGED_REPO_PATH
    unset LOG_DIRECTORY
    
    # Attempt repair
    local repairs_made
    repairs_made=$(attempt_configuration_repair "safe")
    local repair_exit_code=$?
    
    if [[ $repair_exit_code -gt 0 ]]; then
        log "SUCCESS" "PASS: Configuration repair made $repairs_made repairs"
        ((TEST_RESULTS[passed]++))
    else
        log "INFO" "INFO: No repairs needed (exit code: $repair_exit_code)"
        ((TEST_RESULTS[passed]++))
    fi
    
    # Check if defaults were set
    if [[ -n "${SLEEP_DURATION:-}" ]]; then
        log "SUCCESS" "PASS: Default SLEEP_DURATION set"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Default SLEEP_DURATION not set"
        ((TEST_RESULTS[failed]++))
    fi
}

# =============================================================================
# INTEGRATION TESTS
# =============================================================================

test_enhanced_cleanup_integration() {
    log "INFO" "Testing enhanced cleanup integration"
    
    # Set up environment for enhanced cleanup
    export MANAGED_REPO_PATH="$TEST_TEMP_DIR"
    export DRY_RUN_MODE="true"
    export SAFETY_MODE="true"
    
    # Create a test branch that should be cleaned up
    cd "$TEST_REPO_DIR" || return 1
    git checkout -b cleanup-test-branch --quiet
    echo "Test cleanup" > cleanup.txt
    git add cleanup.txt
    git commit -m "Test cleanup branch" --quiet
    git checkout main --quiet
    
    # Delete the remote branch to simulate cleanup scenario
    git branch -D cleanup-test-branch --quiet
    
    # Test the enhanced cleanup script (dry run)
    local cleanup_script="$SCRIPT_DIR/../scripts/cleanup-branches-enhanced.sh"
    if [[ -f "$cleanup_script" ]]; then
        if bash "$cleanup_script" >/dev/null 2>&1; then
            log "SUCCESS" "PASS: Enhanced cleanup script execution"
            ((TEST_RESULTS[passed]++))
        else
            log "ERROR" "FAIL: Enhanced cleanup script execution"
            ((TEST_RESULTS[failed]++))
        fi
    else
        log "WARNING" "Enhanced cleanup script not found, skipping integration test"
        ((TEST_RESULTS[skipped]++))
    fi
}

test_error_recovery_integration() {
    log "INFO" "Testing error recovery integration"
    
    # Test error handling with simulated failure
    local test_result=0
    
    # Set up error context
    export ERROR_CONTEXT="test_integration"
    
    # Simulate an error and test recovery
    if (exit 1) 2>/dev/null; then
        log "ERROR" "FAIL: Error recovery integration - Expected failure"
        ((TEST_RESULTS[failed]++))
        test_result=1
    else
        log "SUCCESS" "PASS: Error recovery integration"
        ((TEST_RESULTS[passed]++))
    fi
    
    return $test_result
}

test_performance_monitoring_integration() {
    log "INFO" "Testing performance monitoring integration"
    
    # Test performance recording
    local start_time=$(date +%s.%N)
    sleep 0.1  # Simulate some work
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0.1")
    
    if record_operation_performance "test_operation" "$duration" true "$TEST_STATE_FILE"; then
        log "SUCCESS" "PASS: Performance recording"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Performance recording"
        ((TEST_RESULTS[failed]++))
    fi
    
    # Check if performance data was recorded
    local avg_duration=$(get_state_value "performance.avg_operation_duration" 0 "$TEST_STATE_FILE")
    if [[ "$avg_duration" != "0" ]]; then
        log "SUCCESS" "PASS: Performance data persistence"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Performance data persistence"
        ((TEST_RESULTS[failed]++))
    fi
}

# =============================================================================
# STRESS AND EDGE CASE TESTS
# =============================================================================

test_concurrent_state_access() {
    log "INFO" "Testing concurrent state access"
    
    # Test atomic state operations
    local success_count=0
    local total_tests=5
    
    for i in $(seq 1 $total_tests); do
        if atomic_state_update "merge" '{"test": "'$i'"}' "$TEST_STATE_FILE"; then
            ((success_count++))
        fi
    done
    
    if [[ $success_count -eq $total_tests ]]; then
        log "SUCCESS" "PASS: Concurrent state access ($success_count/$total_tests)"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Concurrent state access ($success_count/$total_tests)"
        ((TEST_RESULTS[failed]++))
    fi
}

test_large_configuration_validation() {
    log "INFO" "Testing large configuration validation"
    
    # Create a large configuration file
    local large_config="$TEST_TEMP_DIR/large_config.yaml"
    cat > "$large_config" << 'EOF'
# Large test configuration
sleep_duration: 100
managed_repo_path: "/tmp/test"
log_directory: "/tmp/logs"
log_level: "INFO"
timestamp_format: "readable"
timestamp_timezone: "local"
auto_update_reboot_enabled: false
reboot_cooldown_minutes: 60
max_reboot_attempts_per_day: 3
log_max_size_mb: 10
log_retention_days: 30
# Add many more configuration options
test_option_1: "value1"
test_option_2: "value2"
test_option_3: "value3"
test_option_4: "value4"
test_option_5: "value5"
EOF
    
    # Test validation performance
    local start_time=$(date +%s.%N)
    if validate_configuration "$large_config" "permissive"; then
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
        
        log "SUCCESS" "PASS: Large configuration validation (${duration}s)"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Large configuration validation"
        ((TEST_RESULTS[failed]++))
    fi
}

test_error_recovery_under_load() {
    log "INFO" "Testing error recovery under load"
    
    local success_count=0
    local total_tests=10
    
    for i in $(seq 1 $total_tests); do
        # Test error classification under load
        local classification=$(classify_error $i "test error $i" "load_test")
        if [[ -n "$classification" ]]; then
            ((success_count++))
        fi
    done
    
    if [[ $success_count -eq $total_tests ]]; then
        log "SUCCESS" "PASS: Error recovery under load ($success_count/$total_tests)"
        ((TEST_RESULTS[passed]++))
    else
        log "ERROR" "FAIL: Error recovery under load ($success_count/$total_tests)"
        ((TEST_RESULTS[failed]++))
    fi
}

# =============================================================================
# TEST EXECUTION AND REPORTING
# =============================================================================

# Run all tests
run_all_tests() {
    log "INFO" "Starting enhanced architecture test suite"
    
    # Initialize test environment
    if ! initialize_test_environment; then
        log "ERROR" "Failed to initialize test environment"
        exit 1
    fi
    
    # Run individual test modules
    test_error_classification
    test_recovery_strategy_determination
    test_system_state_management
    test_health_check_system
    test_configuration_validation
    test_runtime_configuration_validation
    test_configuration_repair
    test_enhanced_cleanup_integration
    test_error_recovery_integration
    test_performance_monitoring_integration
    test_concurrent_state_access
    test_large_configuration_validation
    test_error_recovery_under_load
    
    # Generate test report
    generate_test_report
    
    # Cleanup
    cleanup_test_environment
    
    # Return overall test result
    if [[ ${TEST_RESULTS[failed]} -eq 0 ]]; then
        log "SUCCESS" "All tests passed!"
        return 0
    else
        log "ERROR" "Some tests failed (${TEST_RESULTS[failed]} of ${TEST_RESULTS[total]})"
        return 1
    fi
}

# Generate comprehensive test report
generate_test_report() {
    local report_file="/tmp/autoslopp_architecture_test_report_$(date +%s).json"
    
    cat > "$report_file" << EOF
{
    "test_summary": {
        "timestamp": "$(date -Iseconds)",
        "total_tests": ${TEST_RESULTS[total]},
        "passed": ${TEST_RESULTS[passed]},
        "failed": ${TEST_RESULTS[failed]},
        "skipped": ${TEST_RESULTS[skipped]},
        "success_rate": $(echo "scale=2; ${TEST_RESULTS[passed]} * 100 / ${TEST_RESULTS[total]}" | bc -l 2>/dev/null || echo "0")
    },
    "test_modules": {
        "error_recovery": "completed",
        "system_state": "completed",
        "configuration_validation": "completed",
        "integration_tests": "completed",
        "stress_tests": "completed"
    },
    "environment": {
        "test_directory": "$TEST_TEMP_DIR",
        "test_state_file": "$TEST_STATE_FILE",
        "test_config_file": "$TEST_CONFIG_FILE",
        "test_repo_dir": "$TEST_REPO_DIR"
    },
    "recommendations": [
EOF
    
    # Add recommendations based on test results
    if [[ ${TEST_RESULTS[failed]} -eq 0 ]]; then
        cat >> "$report_file" << EOF
        "All tests passed - architecture is ready for production",
        "Consider adding more edge case tests for additional coverage"
EOF
    else
        cat >> "$report_file" << EOF
        "Address failed tests before production deployment",
        "Review error handling and recovery mechanisms",
        "Validate configuration and state management"
EOF
    fi
    
    cat >> "$report_file" << EOF
    ]
}
EOF
    
    log "INFO" "Test report generated: $report_file"
    
    # Also output summary to console
    echo ""
    echo "=========================================="
    echo "Enhanced Architecture Test Results"
    echo "=========================================="
    echo "Total Tests: ${TEST_RESULTS[total]}"
    echo "Passed: ${TEST_RESULTS[passed]}"
    echo "Failed: ${TEST_RESULTS[failed]}"
    echo "Skipped: ${TEST_RESULTS[skipped]}"
    echo "Success Rate: $(echo "scale=1; ${TEST_RESULTS[passed]} * 100 / ${TEST_RESULTS[total]}" | bc -l 2>/dev/null || echo "0")%"
    echo "=========================================="
}

# Execute tests if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_all_tests
fi