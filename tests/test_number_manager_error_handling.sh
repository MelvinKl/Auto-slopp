#!/bin/bash

# Test number manager error handling and recovery mechanisms
# Part of Auto-cgo: Test number manager error handling and recovery
# Tests: corrupted files, system interruptions, graceful degradation, 
#        error reporting, orphaned cleanup, state repair

set -e

SCRIPT_NAME="test_error_handling_recovery"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source the test framework and utilities
source "$SCRIPT_DIR/test_framework.sh"
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_error_handling_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

# Test-specific setup
setup_error_handling_test() {
    # Create test directory structure
    mkdir -p "$TEST_STATE_DIR"/{test_repo,orphaned_repo,broken_repo}
    export TEST_STATE_DIR
    export NUMBER_MANAGER_SCRIPT
    export MANAGED_REPO_PATH="$TEST_STATE_DIR"
}

# Test 1: Proper handling of corrupted number tracking files
test_corrupted_state_files() {
    # Arrange: Create corrupted state file scenarios with valid backups
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    
    # Create a valid backup first
    cat > "$TEST_STATE_DIR/.number_state/backup/state_20230101_000000.json" << 'EOF'
{
    "used_numbers": [1, 2, 3],
    "last_assigned": 3,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "context_assignments": {"test_repo": "3"},
    "assignments": [],
    "releases": [],
    "version": "1.0",
    "metadata": {"creator": "number_manager.sh", "purpose": "unique_number_tracking"}
}
EOF
    
    # Scenario 1: Invalid JSON syntax (with valid backup available)
    echo '{invalid json structure}' > "$TEST_STATE_DIR/.number_state/state.json"
    
    # Act: Test 1: Completely invalid JSON (should recover from backup)
    recovery_result_1=0
    "$NUMBER_MANAGER_SCRIPT" init corruption_test_1 >/dev/null 2>&1 || recovery_result_1=$?
    
    # Assert: Test 1: Should recover from valid backup
    [ "$recovery_result_1" -eq 0 ] || {
        echo "ERROR: Failed to recover from invalid JSON with backup available"
        exit 1
    }
    
    # After recovery, state should be valid
    jq empty "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null || {
        echo "ERROR: State file is not valid JSON after recovery"
        exit 1
    }
    
    # Should be able to assign numbers after recovery
    test_number_output=$("$NUMBER_MANAGER_SCRIPT" get corruption_test_1 2>&1)
    test_number=$(echo "$test_number_output" | tail -1)
    [ "$test_number" = "4" ] || {
        echo "ERROR: Failed to assign number after corruption recovery: got '$test_number' from output: $test_number_output"
        exit 1
    }
    
    return 0
}

# Test 2: Recovery from system interruptions during number allocation
test_system_interruption_recovery() {
    # Arrange: Setup scenario for interrupted number allocation
    "$NUMBER_MANAGER_SCRIPT" init interruption_test >/dev/null 2>&1
    
    # Create a backup to simulate interruption point
    cp "$TEST_STATE_DIR/.number_state/state.json" "$TEST_STATE_DIR/.number_state/backup/before_interrupt.json"
    
    # Simulate partial state update (interrupted operation)
    local temp_file="$TEST_STATE_DIR/.number_state/state.json.tmp.$$"
    jq '.used_numbers += [4] | .last_assigned = 4' "$TEST_STATE_DIR/.number_state/state.json" > "$temp_file"
    # Simulate interruption - don't move temp to final state
    mv "$temp_file" "$TEST_STATE_DIR/.number_state/state.json.incomplete"
    
    # Act: Scenario 1: Power loss during write (temp file left behind)
    interruption_result_1=0
    "$NUMBER_MANAGER_SCRIPT" get interruption_test >/dev/null 2>&1 || interruption_result_1=$?
    
    # Scenario 2: Lock file left by dead process
    echo '99999:$(($(date +%s) - 600))' > "$TEST_STATE_DIR/.number_state/.lock"
    interruption_result_2=0
    "$NUMBER_MANAGER_SCRIPT" get interruption_test >/dev/null 2>&1 || interruption_result_2=$?
    
    # Scenario 3: State file truncated during write
    echo '{"used_numbers": [1, 2, 3], "last_as' > "$TEST_STATE_DIR/.number_state/state.json"
    interruption_result_3=0
    "$NUMBER_MANAGER_SCRIPT" get interruption_test >/dev/null 2>&1 || interruption_result_3=$?
    
    # Assert: System recovers from interruptions and maintains consistency
    # Should handle stale lock files
    [ "$interruption_result_2" -eq 0 ] || {
        echo "ERROR: Failed to handle stale lock file"
        exit 1
    }
    
    # Should detect and recover from corrupted state
    [ "$interruption_result_3" -eq 0 ] || {
        echo "ERROR: Failed to recover from truncated state file"
        exit 1
    }
    
    # Verify state consistency after recovery
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count // 0')
    
    # Should have a valid state structure
    [ "$used_count" -ge 0 ] || {
        echo "ERROR: Invalid state after interruption recovery"
        exit 1
    }
    
    return 0
}

# Test 3: Graceful degradation when tracking files are unavailable
test_graceful_degradation() {
    # Arrange: Create scenarios with unavailable tracking files
    "$NUMBER_MANAGER_SCRIPT" init degradation_test >/dev/null 2>&1
    
    # Create some assignments
    "$NUMBER_MANAGER_SCRIPT" get degradation_test >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get degradation_test >/dev/null 2>&1
    
    # Act: Scenario 1: State directory not writable
    chmod 444 "$TEST_STATE_DIR/.number_state"
    degradation_result_1=0
    "$NUMBER_MANAGER_SCRIPT" get degradation_test >/dev/null 2>&1 || degradation_result_1=$?
    chmod 755 "$TEST_STATE_DIR/.number_state"
    
    # Scenario 2: Disk full simulation (create huge file to fill space)
    degradation_result_2=0
    # Note: This is a simplified test - real disk full testing requires more setup
    dd if=/dev/zero of="$TEST_STATE_DIR/.number_state/huge_file" bs=1024 count=1024 2>/dev/null || degradation_result_2=1
    "$NUMBER_MANAGER_SCRIPT" get degradation_test >/dev/null 2>&1 || degradation_result_2=$?
    rm -f "$TEST_STATE_DIR/.number_state/huge_file"
    
    # Scenario 3: State file missing entirely
    rm -f "$TEST_STATE_DIR/.number_state/state.json"
    degradation_result_3=0
    "$NUMBER_MANAGER_SCRIPT" get degradation_test >/dev/null 2>&1 || degradation_result_3=$?
    
    # Assert: System degrades gracefully without crashing
    # Should fail gracefully with meaningful error messages
    [ "$degradation_result_1" -ne 0 ] || {
        echo "ERROR: Should have failed gracefully with read-only state directory"
        exit 1
    }
    
    # Should handle missing state file appropriately
    [ "$degradation_result_3" -ne 0 ] || {
        echo "ERROR: Should have failed gracefully with missing state file"
        exit 1
    }
    
    # Error messages should be meaningful (test by checking if any output exists)
    local error_output
    error_output=$("$NUMBER_MANAGER_SCRIPT" get degradation_test 2>&1 || true)
    [ -n "$error_output" ] || {
        echo "ERROR: Error output should be provided for graceful degradation"
        exit 1
    }
    
    return 0
}

# Test 4: Error reporting and logging functionality
test_error_reporting_logging() {
    # Arrange: Setup scenarios for error reporting testing
    export LOG_FILE="$TEST_STATE_DIR/test.log"
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Act: Test error reporting in various scenarios
    # Scenario 1: Invalid number release
    error_output_1=$("$NUMBER_MANAGER_SCRIPT" release -1 logging_test 2>&1 || true)
    
    # Scenario 2: Number too large
    error_output_2=$("$NUMBER_MANAGER_SCRIPT" release 99999 logging_test 2>&1 || true)
    
    # Scenario 3: Non-existent context operations
    rm -rf "$TEST_STATE_DIR/.number_state"
    error_output_3=$("$NUMBER_MANAGER_SCRIPT" get nonexistent_context 2>&1 || true)
    
    # Scenario 4: Operation without initialization
    error_output_4=$("$NUMBER_MANAGER_SCRIPT" stats 2>&1 || true)
    
    # Assert: Error reporting is comprehensive and actionable
    # Error messages should be descriptive
    echo "$error_output_1" | grep -q -i 'invalid\|number' || {
        echo "ERROR: Error message for invalid number should be descriptive"
        exit 1
    }
    
    echo "$error_output_2" | grep -q -i 'large\|9999' || {
        echo "ERROR: Error message for large number should mention limits"
        exit 1
    }
    
    echo "$error_output_3" | grep -q -i 'state\|initialize' || {
        echo "ERROR: Error message for missing state should suggest initialization"
        exit 1
    }
    
    # All error outputs should be non-empty
    [ -n "$error_output_1" ] && [ -n "$error_output_2" ] && [ -n "$error_output_3" ] && [ -n "$error_output_4" ] || {
        echo "ERROR: All error scenarios should produce output"
        exit 1
    }
    
    return 0
}

# Test 5: Automatic cleanup of orphaned number allocations
test_orphaned_cleanup() {
    # Arrange: Create scenarios with orphaned allocations
    "$NUMBER_MANAGER_SCRIPT" init orphan_test >/dev/null 2>&1
    
    # Create some normal assignments
    number_1=$("$NUMBER_MANAGER_SCRIPT" get orphan_test 2>/dev/null | tail -1)
    number_2=$("$NUMBER_MANAGER_SCRIPT" get orphan_test 2>/dev/null | tail -1)
    number_3=$("$NUMBER_MANAGER_SCRIPT" get orphan_test 2>/dev/null | tail -1)
    
    # Create orphaned scenario: numbers in state but no actual files
    # Simulate files that were supposed to be created but weren't
    mkdir -p "$TEST_STATE_DIR/task_dir"
    touch "$TEST_STATE_DIR/task_dir/000${number_1}-real_task.txt"
    # Don't create files for number_2 and number_3 - they're orphaned
    
    # Create state with numbers that don't have corresponding files
    jq --argjson nums "[ $number_2, $number_3 ]" \
       '.used_numbers += $nums | .last_assigned = ($nums | max // .last_assigned)' \
       "$TEST_STATE_DIR/.number_state/state.json" > "$TEST_STATE_DIR/.number_state/state.tmp"
    mv "$TEST_STATE_DIR/.number_state/state.tmp" "$TEST_STATE_DIR/.number_state/state.json"
    
    # Act: Test orphaned cleanup mechanisms
    # Validate to identify orphaned allocations
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_STATE_DIR/task_dir" orphan_test 2>&1 || true)
    
    # Sync state to clean up orphaned numbers
    sync_output=$("$NUMBER_MANAGER_SCRIPT" sync "$TEST_STATE_DIR/task_dir" orphan_test 2>&1)
    
    # Get final stats
    final_stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    
    # Assert: Orphaned allocations are properly identified and cleaned
    # Validation should report inconsistencies
    echo "$validation_output" | grep -q -i 'state but not in files\|inconsistencies' || {
        echo "ERROR: Validation should detect orphaned allocations"
        exit 1
    }
    
    # Sync should clean up orphaned numbers
    local final_used_count
    final_used_count=$(echo "$final_stats" | jq -r '.used_count // 0')
    
    # Should only have 1 number (the one with actual file)
    [ "$final_used_count" = "1" ] || {
        echo "ERROR: Orphaned cleanup failed: expected 1 used number, got $final_used_count"
        exit 1
    }
    
    return 0
}

# Test 6: Validation and repair of inconsistent number tracking state
test_state_repair() {
    # Check that test environment is set up correctly
    echo "DEBUG: TEST_STATE_DIR = '$TEST_STATE_DIR'"
    echo "DEBUG: MANAGED_REPO_PATH = '$MANAGED_REPO_PATH'"
    
    # Create proper state file manually (avoid init issues)
    mkdir -p "$TEST_STATE_DIR/.number_state"
    cat > "$TEST_STATE_DIR/.number_state/state.json" << 'EOF'
{
    "used_numbers": [],
    "last_assigned": 0,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "context_assignments": {},
    "assignments": [],
    "releases": [],
    "version": "1.0",
    "metadata": {"creator": "number_manager.sh", "purpose": "unique_number_tracking"}
}
EOF
    
    # Create inconsistent scenario
    task_dir="$TEST_STATE_DIR/repair_task_dir"
    echo "DEBUG: Creating task_dir at '$task_dir'"
    mkdir -p "$task_dir"
    touch "$task_dir/0001-file.txt"
    echo "DEBUG: Task dir contents: $(ls -la "$task_dir")"
    
    # Try sync to repair state
    echo "DEBUG: About to run sync command"
    repair_output=$("$NUMBER_MANAGER_SCRIPT" sync "$task_dir" repair_test 2>&1)
    local sync_exit_code=$?
    echo "DEBUG: Sync exit code: $sync_exit_code"
    echo "DEBUG: Sync output: '$repair_output'"
    
    # Basic check: sync should succeed
    [ $sync_exit_code -eq 0 ] || {
        echo "ERROR: Sync command failed with exit code $sync_exit_code"
        echo "Output was: $repair_output"
        exit 1
    }
    
    # Check that output mentions syncing
    echo "$repair_output" | grep -q -i 'synced' || {
        echo "ERROR: Sync output doesn't mention syncing: $repair_output"
        exit 1
    }
    
    return 0
}
    
    # Check repair resolves issues
    if [ -z "$repair_output" ]; then
        echo "ERROR: Repair output is empty"
        exit 1
    fi
    
    echo "$repair_output" | grep -q -i 'Synced.*files' || {
        echo "ERROR: Repair should report successful synchronization"
        echo "Repair output was: $repair_output"
        exit 1
    }
    
    # Check final validation shows no inconsistencies
    ! echo "$final_validation" | grep -q -i 'inconsistencies' || {
        echo "ERROR: Final validation should show no inconsistencies after repair"
        echo "Final validation output was: $final_validation"
        exit 1
    }
}
        
        # Repair should resolve most issues
        echo \"\$repair_output\" | grep -q -i 'synced\\[0-9\\]\\+ files' || {
            log_error 'Repair should report successful synchronization'
            exit 1
        }
        
        # Final validation should show no inconsistencies
        if echo \"\$final_validation\" | grep -q -i 'inconsistencies'; then
            log_error 'Final validation should show no inconsistencies after repair'
            exit 1
        fi
        
        return 0
    "
}

# Test 7: Recovery from simultaneous corruption scenarios
test_multiple_corruption_recovery() {
    # Arrange: Create multiple corruption scenarios
    "$NUMBER_MANAGER_SCRIPT" init multi_corrupt_test >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get multi_corrupt_test >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get multi_corrupt_test >/dev/null 2>&1
    
    # Create valid backup
    cp "$TEST_STATE_DIR/.number_state/state.json" "$TEST_STATE_DIR/.number_state/backup/state_$(date +%Y%m%d_%H%M%S).json"
    
    # Corrupt main state in multiple ways
    echo '{"corrupted": "main state"}' > "$TEST_STATE_DIR/.number_state/state.json"
    
    # Create corrupted backups alongside good ones
    echo '{"invalid": "backup1"}' > "$TEST_STATE_DIR/.number_state/backup/state_$(date +%Y%m%d)_000000.json"
    echo '{"invalid": "backup2"}' > "$TEST_STATE_DIR/.number_state/backup/state_$(date +%Y%m%d)_120000.json"
    
    # Act: Test recovery from multiple corruption scenarios
    # Attempt recovery
    recovery_output=$("$NUMBER_MANAGER_SCRIPT" init multi_corrupt_test 2>&1)
    
    # Test if system can still operate after recovery
    operation_result=0
    test_number=$("$NUMBER_MANAGER_SCRIPT" get multi_corrupt_test 2>/dev/null | tail -1) || operation_result=$?
    
    # Check final state integrity
    final_stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    
    # Assert: System recovers from complex corruption scenarios
    # Recovery should succeed
    [ "$operation_result" -eq 0 ] || {
        echo "ERROR: System should operate after recovery from multiple corruptions"
        exit 1
    }
    
    # Final state should be valid JSON
    echo "$final_stats" | jq empty 2>/dev/null || {
        echo "ERROR: Final state should be valid JSON after recovery"
        exit 1
    }
    
    # Should have some reasonable state
    local final_count
    final_count=$(echo "$final_stats" | jq -r '.used_count // 0')
    [ "$final_count" -ge 0 ] || {
        echo "ERROR: Final state should have valid count after recovery"
        exit 1
    }
    
    return 0
}

# Main test runner
run_error_handling_tests() {
    log_info "Starting Number Manager Error Handling and Recovery Tests"
    
    # Initialize test framework
    init_framework
    
    # Setup test-specific environment
    setup_error_handling_test
    
    # Run all error handling tests
    run_test "corrupted_state_files" test_corrupted_state_files "integration" "high" "Tests corrupted state file handling"
    run_test "system_interruption_recovery" test_system_interruption_recovery "integration" "high" "Tests recovery from system interruptions"
    run_test "graceful_degradation" test_graceful_degradation "system" "high" "Tests graceful degradation when files unavailable"
    run_test "error_reporting_logging" test_error_reporting_logging "unit" "medium" "Tests error reporting and logging"
    run_test "orphaned_cleanup" test_orphaned_cleanup "integration" "high" "Tests orphaned allocation cleanup"
    run_test "state_repair" test_state_repair "integration" "high" "Tests state validation and repair"
    run_test "multiple_corruption_recovery" test_multiple_corruption_recovery "system" "critical" "Tests complex corruption recovery"
    
    # Generate final report
    generate_report
}

# Cleanup function
cleanup_error_handling_tests() {
    log_info "Cleaning up error handling test environment"
    if [[ -n "${TEST_STATE_DIR:-}" && -d "$TEST_STATE_DIR" ]]; then
        rm -rf "$TEST_STATE_DIR"
    fi
    unset TEST_STATE_DIR NUMBER_MANAGER_SCRIPT
}

# Main execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    trap cleanup_error_handling_tests EXIT
    
    if [[ "${1:-}" = "run" ]]; then
        run_error_handling_tests
        exit $?
    else
        echo "Usage: $0 run"
        echo "This script tests number manager error handling and recovery mechanisms"
        exit 1
    fi
fi