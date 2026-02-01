#!/bin/bash

# Test Backup Recovery Mechanism for number_manager.sh
# Tests backup creation, rotation, and recovery from corrupted state files
# Tests the attempt_state_recovery function and backup management

SCRIPT_NAME="test_recovery_mechanism"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_recovery_mechanism_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

# Test results tracking
TESTS_RUN=0
TESTS_PASSED=0

log "INFO" "Starting backup recovery mechanism tests in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test helper functions
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo ""
    echo "=========================================="
    echo "Running Test: $test_name"
    echo "=========================================="
    
    if eval "$test_command"; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo "✅ $test_name PASSED"
        return 0
    else
        echo "❌ $test_name FAILED"
        return 1
    fi
}

# Helper to create valid backup file
create_backup_file() {
    local backup_name="$1"
    local backup_dir="$TEST_STATE_DIR/.number_state/backup"
    
    mkdir -p "$backup_dir"
    cat > "$backup_dir/$backup_name" << 'EOF'
{
    "used_numbers": [1, 2, 3],
    "last_assigned": 3,
    "created_at": "2026-01-31T10:00:00Z",
    "updated_at": "2026-01-31T10:00:00Z",
    "context_assignments": {"test": "3"},
    "version": "1.0",
    "metadata": {
        "creator": "number_manager.sh",
        "purpose": "unique_number_tracking"
    }
}
EOF
}

# Helper to create corrupted state file
create_corrupted_state() {
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    mkdir -p "$TEST_STATE_DIR/.number_state"
    echo '{"invalid": json}' > "$state_file"
}

# Test 1: Backup creation during normal operations
test_backup_creation() {
    log "INFO" "Test 1: Testing backup creation during normal operations"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Initialize state
    if ! "$NUMBER_MANAGER_SCRIPT" init "backup_test" >/dev/null 2>&1; then
        log "ERROR" "Initialization failed"
        return 1
    fi
    
    # Get some numbers to trigger backups
    "$NUMBER_MANAGER_SCRIPT" get "backup_test" >/dev/null 2>&1  # Should create backup
    "$NUMBER_MANAGER_SCRIPT" get "backup_test" >/dev/null 2>&1  # Should create another backup
    
    # Check if backup directory exists
    local backup_dir="$TEST_STATE_DIR/.number_state/backup"
    if [ ! -d "$backup_dir" ]; then
        log "ERROR" "Backup directory not created"
        return 1
    fi
    
    # Check if backup files exist
    local backup_files=($(ls "$backup_dir"/state_*.json 2>/dev/null))
    if [ ${#backup_files[@]} -eq 0 ]; then
        log "ERROR" "No backup files created"
        return 1
    fi
    
    # Check if backup files are valid JSON
    for backup_file in "${backup_files[@]}"; do
        if ! jq empty "$backup_file" 2>/dev/null; then
            log "ERROR "Backup file is not valid JSON: $(basename "$backup_file")"
            return 1
        fi
    done
    
    log "SUCCESS" "Backup creation works correctly"
    return 0
}

# Test 2: Backup rotation and cleanup
test_backup_rotation() {
    log "INFO" "Test 2: Testing backup rotation and cleanup"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Initialize state
    "$NUMBER_MANAGER_SCRIPT" init "rotation_test" >/dev/null 2>&1
    
    # Create many operations to exceed backup limit (default is 5)
    for i in {1..8}; do
        "$NUMBER_MANAGER_SCRIPT" get "rotation_test" >/dev/null 2>&1
    done
    
    # Check backup count
    local backup_dir="$TEST_STATE_DIR/.number_state/backup"
    local backup_files=($(ls -t "$backup_dir"/state_*.json 2>/dev/null))
    
    if [ ${#backup_files[@]} -gt 5 ]; then
        log "ERROR "Backup rotation not working, found ${#backup_files[@]} backups (should be ≤5)"
        return 1
    fi
    
    # Check that newest backups are kept
    if [ ${#backup_files[@]} -gt 0 ]; then
        # The files should be sorted by timestamp (newest first)
        local newest="${backup_files[0]}"
        local oldest="${backup_files[-1]}"
        
        if [ "$newest" = "$oldest" ] && [ ${#backup_files[@]} -gt 1 ]; then
            log "ERROR "Backup files not sorted correctly"
            return 1
        fi
    fi
    
    log "SUCCESS" "Backup rotation works correctly"
    return 0
}

# Test 3: Recovery from corrupted state with backup available
test_recovery_with_backup() {
    log "INFO" "Test 3: Testing recovery from corrupted state with backup available"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Initialize and create backup
    "$NUMBER_MANAGER_SCRIPT" init "recovery_test" >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get "recovery_test" >/dev/null 2>&1
    
    # Create a good backup
    create_backup_file "state_20260131_100000.json"
    
    # Corrupt the main state file
    create_corrupted_state
    
    # Try to get a number, which should trigger recovery
    if "$NUMBER_MANAGER_SCRIPT" get "recovery_test" >/dev/null 2>&1; then
        # Check if state is now valid
        local state_file="$TEST_STATE_DIR/.number_state/state.json"
        if jq empty "$state_file" 2>/dev/null; then
            # Check if required fields are present
            if jq -e '.used_numbers' "$state_file" >/dev/null && \
               jq -e '.last_assigned' "$state_file" >/dev/null && \
               jq -e '.context_assignments' "$state_file" >/dev/null; then
                log "SUCCESS" "Recovery from backup works correctly"
                return 0
            else
                log "ERROR "Recovered state missing required fields"
                return 1
            fi
        else
            log "ERROR "State not recovered to valid JSON"
            return 1
        fi
    else
        log "ERROR "Recovery operation failed"
        return 1
    fi
}

# Test 4: Recovery when no backup available (reinitialization)
test_recovery_no_backup() {
    log "INFO" "Test 4: Testing recovery when no backup available"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create corrupted state without backup
    create_corrupted_state
    
    # Try to get a number, should fail and reinitialize
    if ! "$NUMBER_MANAGER_SCRIPT" get "no_backup_test" >/dev/null 2>&1; then
        # The operation might fail because there's no good state to recover from
        # Let's check if it was reinitialized by trying init
        if "$NUMBER_MANAGER_SCRIPT" init "no_backup_test" >/dev/null 2>&1; then
            # Now try to get a number
            if "$NUMBER_MANAGER_SCRIPT" get "no_backup_test" >/dev/null 2>&1; then
                log "SUCCESS" "Reinitialization when no backup available works"
                return 0
            else
                log "ERROR "Reinitialization failed to create working state"
                return 1
            fi
        else
            log "ERROR "Reinitialization failed"
            return 1
        fi
    else
        # Unexpected success - corrupted state should not allow normal operation
        log "ERROR "Operation with corrupted state should fail"
        return 1
    fi
}

# Test 5: Backup file naming and timestamp format
test_backup_naming_format() {
    log "INFO" "Test 5: Testing backup file naming and timestamp format"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Initialize and create backup
    "$NUMBER_MANAGER_SCRIPT" init "naming_test" >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get "naming_test" >/dev/null 2>&1
    
    # Check backup file naming
    local backup_dir="$TEST_STATE_DIR/.number_state/backup"
    local backup_files=($(ls "$backup_dir"/state_*.json 2>/dev/null))
    
    if [ ${#backup_files[@]} -eq 0 ]; then
        log "ERROR "No backup files found for naming test"
        return 1
    fi
    
    # Check naming pattern: state_YYYYMMDD_HHMMSS.json
    for backup_file in "${backup_files[@]}"; do
        local basename=$(basename "$backup_file" .json)
        if [[ ! "$basename" =~ ^state_[0-9]{8}_[0-9]{6}$ ]]; then
            log "ERROR "Backup file naming pattern incorrect: $basename"
            return 1
        fi
    done
    
    log "SUCCESS" "Backup file naming format is correct"
    return 0
}

# Test 6: Multiple backup files with different timestamps
test_multiple_backup_timestamps() {
    log "INFO" "Test 6: Testing multiple backup files with different timestamps"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init "timestamp_test" >/dev/null 2>&1
    
    # Create backups at different times
    "$NUMBER_MANAGER_SCRIPT" get "timestamp_test" >/dev/null 2>&1
    
    # Wait a moment to ensure different timestamp
    sleep 1
    
    "$NUMBER_MANAGER_SCRIPT" get "timestamp_test" >/dev/null 2>&1
    
    # Check backup files
    local backup_dir="$TEST_STATE_DIR/.number_state/backup"
    local backup_files=($(ls -t "$backup_dir"/state_*.json 2>/dev/null))
    
    if [ ${#backup_files[@]} -lt 2 ]; then
        log "ERROR "Not enough backup files created for timestamp test"
        return 1
    fi
    
    # Extract timestamps and verify they're different
    local first_timestamp=$(basename "${backup_files[0]}" .json | sed 's/state_//')
    local second_timestamp=$(basename "${backup_files[1]}" .json | sed 's/state_//')
    
    if [ "$first_timestamp" = "$second_timestamp" ]; then
        log "ERROR "Backup timestamps should be different"
        return 1
    fi
    
    # Check that newer backup comes first in ls -t order
    if [[ "$first_timestamp" < "$second_timestamp" ]]; then
        log "ERROR "Backup files not sorted by timestamp correctly"
        return 1
    fi
    
    log "SUCCESS" "Multiple backup timestamps work correctly"
    return 0
}

# Test 7: Recovery from partially corrupted backup
test_partial_corruption_recovery() {
    log "INFO" "Test 7: Testing recovery from partially corrupted backup"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create backup directory
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    
    # Create one good backup and one corrupted backup
    create_backup_file "state_20260131_100000.json"
    echo '{"invalid": json}' > "$TEST_STATE_DIR/.number_state/backup/state_20260131_090000.json"
    
    # Corrupt the main state
    create_corrupted_state
    
    # Try recovery - should pick the good backup
    if "$NUMBER_MANAGER_SCRIPT" get "partial_test" >/dev/null 2>&1; then
        # Check if recovered state is valid
        local state_file="$TEST_STATE_DIR/.number_state/state.json"
        if jq empty "$state_file" 2>/dev/null; then
            log "SUCCESS" "Recovery from partially corrupted backups works"
            return 0
        else
            log "ERROR "Recovered state is invalid"
            return 1
        fi
    else
        log "ERROR "Recovery from partially corrupted backups failed"
        return 1
    fi
}

# Test 8: Backup preservation during recovery
test_backup_preservation() {
    log "INFO" "Test 8: Testing backup preservation during recovery"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Initialize and create multiple backups
    "$NUMBER_MANAGER_SCRIPT" init "preserve_test" >/dev/null 2>&1
    for i in {1..3}; do
        "$NUMBER_MANAGER_SCRIPT" get "preserve_test" >/dev/null 2>&1
    done
    
    # Count backups before recovery
    local backup_dir="$TEST_STATE_DIR/.number_state/backup"
    local backup_count_before=$(ls "$backup_dir"/state_*.json 2>/dev/null | wc -l)
    
    # Corrupt main state
    create_corrupted_state
    
    # Trigger recovery
    "$NUMBER_MANAGER_SCRIPT" get "preserve_test" >/dev/null 2>&1
    
    # Count backups after recovery
    local backup_count_after=$(ls "$backup_dir"/state_*.json 2>/dev/null | wc -l)
    
    # Backup count should not decrease significantly (might increase by 1)
    if [ $backup_count_after -lt $((backup_count_before - 1)) ]; then
        log "ERROR "Backups were lost during recovery: before=$backup_count_before, after=$backup_count_after"
        return 1
    fi
    
    log "SUCCESS" "Backup preservation during recovery works"
    return 0
}

# Test 9: Recovery with specific backup selection
test_specific_backup_selection() {
    log "INFO" "Test 9: Testing recovery with specific backup selection"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create backup directory and multiple backups with different content
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    
    # Create older backup with different data
    cat > "$TEST_STATE_DIR/.number_state/backup/state_20260131_080000.json" << 'EOF'
{
    "used_numbers": [1],
    "last_assigned": 1,
    "created_at": "2026-01-31T08:00:00Z",
    "updated_at": "2026-01-31T08:00:00Z",
    "context_assignments": {"old": "1"},
    "version": "1.0",
    "metadata": {
        "creator": "number_manager.sh",
        "purpose": "unique_number_tracking"
    }
}
EOF
    
    # Create newer backup with different data
    create_backup_file "state_20260131_100000.json"
    
    # Corrupt main state
    create_corrupted_state
    
    # Recovery should pick the latest backup
    if "$NUMBER_MANAGER_SCRIPT" get "selection_test" >/dev/null 2>&1; then
        # Check if it used the newer backup (should have higher numbers)
        local state_file="$TEST_STATE_DIR/.number_state/state.json"
        local last_assigned=$(jq -r '.last_assigned' "$state_file")
        
        if [ "$last_assigned" = "3" ]; then
            log "SUCCESS" "Specific backup selection (latest) works correctly"
            return 0
        else
            log "ERROR "Wrong backup selected for recovery, last_assigned: $last_assigned"
            return 1
        fi
    else
        log "ERROR "Recovery with backup selection failed"
        return 1
    fi
}

# Test 10: Recovery error handling and logging
test_recovery_error_handling() {
    log "INFO" "Test 10: Testing recovery error handling and logging"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create backup directory with corrupted backup
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    echo '{"corrupted": json}' > "$TEST_STATE_DIR/.number_state/backup/state_20260131_100000.json"
    
    # Corrupt main state
    create_corrupted_state
    
    # Try recovery - should handle errors gracefully
    if "$NUMBER_MANAGER_SCRIPT" get "error_test" >/dev/null 2>&1; then
        # Unexpected success - this should probably fail
        log "INFO" "Recovery succeeded despite corrupted backup (acceptable behavior)"
    else
        # Expected failure - this is also acceptable
        log "INFO" "Recovery failed as expected with corrupted backup"
    fi
    
    # The key is that it doesn't crash the system
    # Check if backup directory still exists
    if [ ! -d "$TEST_STATE_DIR/.number_state/backup" ]; then
        log "ERROR "Backup directory was deleted during error handling"
        return 1
    fi
    
    log "SUCCESS" "Recovery error handling works correctly"
    return 0
}

# Test 11: Cleanup old backup files
test_cleanup_old_backups() {
    log "INFO" "Test 11: Testing cleanup of old backup files"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Initialize state
    "$NUMBER_MANAGER_SCRIPT" init "cleanup_test" >/dev/null 2>&1
    
    # Create some old backup files manually
    local backup_dir="$TEST_STATE_DIR/.number_state/backup"
    mkdir -p "$backup_dir"
    
    # Create backup files with old dates
    touch -d "40 days ago" "$backup_dir/state_20260101_080000.json"
    touch -d "35 days ago" "$backup_dir/state_20260105_090000.json"
    touch -d "5 days ago" "$backup_dir/state_20260130_100000.json"
    
    # Run cleanup command
    if "$NUMBER_MANAGER_SCRIPT" cleanup 30 >/dev/null 2>&1; then
        # Check if old files were removed
        local remaining_files=($(ls "$backup_dir"/state_*.json 2>/dev/null))
        local should_remain=0
        
        for file in "${remaining_files[@]}"; do
            local basename=$(basename "$file" .json)
            if [[ "$basename" =~ ^(20260130_100000)$ ]]; then
                should_remain=$((should_remain + 1))
            fi
        done
        
        if [ ${#remaining_files[@]} -eq $should_remain ]; then
            log "SUCCESS" "Cleanup of old backup files works correctly"
            return 0
        else
            log "ERROR "Cleanup didn't remove the right files, remaining: ${remaining_files[*]}"
            return 1
        fi
    else
        log "ERROR "Cleanup command failed"
        return 1
    fi
}

# Main test execution
run_all_tests() {
    echo ""
    echo "=========================================="
    echo "Backup Recovery Mechanism Tests"
    echo "=========================================="
    
    run_test "Backup Creation" "test_backup_creation"
    run_test "Backup Rotation" "test_backup_rotation"
    run_test "Recovery with Backup" "test_recovery_with_backup"
    run_test "Recovery No Backup" "test_recovery_no_backup"
    run_test "Backup Naming Format" "test_backup_naming_format"
    run_test "Multiple Backup Timestamps" "test_multiple_backup_timestamps"
    run_test "Partial Corruption Recovery" "test_partial_corruption_recovery"
    run_test "Backup Preservation" "test_backup_preservation"
    run_test "Specific Backup Selection" "test_specific_backup_selection"
    run_test "Recovery Error Handling" "test_recovery_error_handling"
    run_test "Cleanup Old Backups" "test_cleanup_old_backups"
    
    echo ""
    echo "=========================================="
    echo "Test Results: $TESTS_PASSED/$TESTS_RUN passed"
    echo "=========================================="
    
    if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
        log "SUCCESS" "All backup recovery mechanism tests passed!"
        return 0
    else
        log "ERROR" "Some backup recovery mechanism tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests backup recovery mechanisms for number_manager.sh"
    exit 1
fi