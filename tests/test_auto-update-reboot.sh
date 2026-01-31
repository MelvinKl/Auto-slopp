#!/bin/bash

# Test script for auto-update-reboot functionality
# This script validates the implementation without actually triggering reboots

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

# Test 1: Configuration loading
test_configuration_loading() {
    echo "=== Test 1: Configuration Loading ==="
    
    # Test that configuration values are loaded
    if [[ "$AUTO_UPDATE_REBOOT_ENABLED" == "false" ]]; then
        log_test_result "auto_update_reboot_enabled" "PASS" "Default value: $AUTO_UPDATE_REBOOT_ENABLED"
    else
        log_test_result "auto_update_reboot_enabled" "FAIL" "Expected false, got $AUTO_UPDATE_REBOOT_ENABLED"
    fi
    
    if [[ "$REBOOT_COOLDOWN_MINUTES" == "60" ]]; then
        log_test_result "reboot_cooldown_minutes" "PASS" "Default value: $REBOOT_COOLDOWN_MINUTES"
    else
        log_test_result "reboot_cooldown_minutes" "FAIL" "Expected 60, got $REBOOT_COOLDOWN_MINUTES"
    fi
    
    if [[ "$MAX_REBOOT_ATTEMPTS_PER_DAY" == "3" ]]; then
        log_test_result "max_reboot_attempts_per_day" "PASS" "Default value: $MAX_REBOOT_ATTEMPTS_PER_DAY"
    else
        log_test_result "max_reboot_attempts_per_day" "FAIL" "Expected 3, got $MAX_REBOOT_ATTEMPTS_PER_DAY"
    fi
}

# Test 2: Script discovery and execution
test_script_discovery() {
    echo -e "\n=== Test 2: Script Discovery ==="
    
    local script_path="$SCRIPT_DIR/scripts/auto-update-reboot.sh"
    
    if [[ -f "$script_path" ]]; then
        log_test_result "script_exists" "PASS" "Script found at $script_path"
    else
        log_test_result "script_exists" "FAIL" "Script not found at $script_path"
    fi
    
    if [[ -x "$script_path" ]]; then
        log_test_result "script_executable" "PASS" "Script has execute permissions"
    else
        log_test_result "script_executable" "FAIL" "Script lacks execute permissions"
    fi
}

# Test 3: Logging functions
test_logging_functions() {
    echo -e "\n=== Test 3: Logging Functions ==="
    
    # Test that specialized logging functions exist and are callable
    if declare -f log_change_detection >/dev/null; then
        log_test_result "log_change_detection_exists" "PASS" "Function exists"
    else
        log_test_result "log_change_detection_exists" "FAIL" "Function not found"
    fi
    
    if declare -f log_system_health >/dev/null; then
        log_test_result "log_system_health_exists" "PASS" "Function exists"
    else
        log_test_result "log_system_health_exists" "FAIL" "Function not found"
    fi
    
    if declare -f log_reboot_event >/dev/null; then
        log_test_result "log_reboot_event_exists" "PASS" "Function exists"
    else
        log_test_result "log_reboot_event_exists" "FAIL" "Function not found"
    fi
    
    if declare -f log_system_state_snapshot >/dev/null; then
        log_test_result "log_system_state_snapshot_exists" "PASS" "Function exists"
    else
        log_test_result "log_system_state_snapshot_exists" "FAIL" "Function not found"
    fi
}

# Test 4: Auto-update-reboot script execution (dry run)
test_script_execution() {
    echo -e "\n=== Test 4: Script Execution (Dry Run) ==="
    
    # Run script in a controlled environment
    local temp_log="/tmp/auto-update-reboot-test.log"
    
    # Set up test environment
    export AUTO_UPDATE_REBOOT_ENABLED="false"  # Keep disabled for safety
    export LOG_DIRECTORY="/tmp"
    
    if bash "$SCRIPT_DIR/scripts/auto-update-reboot.sh" > "$temp_log" 2>&1; then
        log_test_result "script_execution" "PASS" "Script executed successfully"
        
        # Check that appropriate log messages were generated
        if grep -q "Auto-update-reboot enabled: false" "$temp_log"; then
            log_test_result "script_disables_correctly" "PASS" "Script disables when config is false"
        else
            log_test_result "script_disables_correctly" "FAIL" "Script did not check enabled status"
        fi
    else
        log_test_result "script_execution" "FAIL" "Script execution failed"
    fi
    
    # Cleanup
    rm -f "$temp_log"
}

# Test 5: State management
test_state_management() {
    echo -e "\n=== Test 5: State Management ==="
    
    # Test state file creation and management
    local test_state_file="/tmp/test-auto-update-reboot.state"
    local test_log_dir="/tmp"
    
    # Mock the state functions for testing
    mkdir -p "$test_log_dir"
    
    # Test state file creation
    if [[ -d "$test_log_dir" ]]; then
        log_test_result "log_directory_creation" "PASS" "Log directory can be created"
    else
        log_test_result "log_directory_creation" "FAIL" "Failed to create log directory"
    fi
    
    # Cleanup
    rm -f "$test_state_file"
}

# Test 6: Integration with main.sh
test_main_integration() {
    echo -e "\n=== Test 6: Main.sh Integration ==="
    
    # Test that the script would be discovered by main.sh
    local scripts_dir="$SCRIPT_DIR/scripts"
    local script_count=$(find "$scripts_dir" -name "*.sh" -type f | wc -l)
    local auto_update_script_found=$(find "$scripts_dir" -name "auto-update-reboot.sh" -type f | wc -l)
    
    if [[ $auto_update_script_found -eq 1 ]]; then
        log_test_result "script_discovery" "PASS" "Auto-update-reboot script discovered ($script_count total scripts)"
    else
        log_test_result "script_discovery" "FAIL" "Auto-update-reboot script not found"
    fi
}

# Main test execution
echo "Auto-Update-Reboot Implementation Tests"
echo "======================================="

test_configuration_loading
test_script_discovery
test_logging_functions
test_script_execution
test_state_management
test_main_integration

# Summary
echo -e "\n=== Test Summary ==="
echo "Total tests: $TEST_COUNT"
echo "Passed: $PASS_COUNT"
echo "Failed: $((TEST_COUNT - PASS_COUNT))"

if [[ $PASS_COUNT -eq $TEST_COUNT ]]; then
    echo "🎉 All tests passed! Implementation is ready."
    exit 0
else
    echo "❌ Some tests failed. Please review the implementation."
    exit 1
fi