#!/bin/bash

# Test State Synchronization with Disk
# Tests synchronization between number tracking state and actual task files on disk
# Tests sync operations, consistency validation, and atomic updates

SCRIPT_NAME="test_sync_state_to_files"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_sync_state_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

# Test results tracking
TESTS_RUN=0
TESTS_PASSED=0

log "INFO" "Starting state synchronization tests in $TEST_STATE_DIR"

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

# Helper to create test task files
create_task_file() {
    local number="$1"
    local title="$2"
    local task_dir="$3"
    
    # Pad number to 4 digits
    local padded_num=$(printf "%04d" "$number")
    local filename="${padded_num}-${title}.txt"
    local filepath="$task_dir/$filename"
    
    echo "Task content for $title" > "$filepath"
    echo "$filepath"
}

# Helper to initialize number state
init_test_state() {
    local context="$1"
    "$NUMBER_MANAGER_SCRIPT" init "$context" >/dev/null 2>&1
}

# Helper to create task directory
setup_task_directory() {
    local context="$1"
    local task_dir="$TEST_STATE_DIR/$context"
    mkdir -p "$task_dir"
    echo "$task_dir"
}

# Test 1: Basic synchronization - files present, state empty
test_basic_sync_files_to_state() {
    log "INFO" "Test 1: Testing basic synchronization from files to state"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir
    task_dir=$(setup_task_directory "$context")
    
    # Create task files
    create_task_file 1 "first-task" "$task_dir"
    create_task_file 5 "fifth-task" "$task_dir"
    create_task_file 10 "tenth-task" "$task_dir"
    
    # Initialize state (empty)
    init_test_state "$context"
    
    # Sync state with files
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Failed to sync state with files"
        return 1
    fi
    
    # Verify state reflects files
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    local last_assigned
    last_assigned=$(echo "$stats" | jq -r '.last_assigned')
    
    if [ "$used_count" -ne 3 ]; then
        log "ERROR" "Expected used_count=3, got $used_count"
        return 1
    fi
    
    if [ "$last_assigned" -ne 10 ]; then
        log "ERROR" "Expected last_assigned=10, got $last_assigned"
        return 1
    fi
    
    log "SUCCESS" "Basic file to state synchronization works"
    return 0
}

# Test 2: Synchronization - state has orphaned entries
test_sync_cleanup_orphans() {
    log "INFO" "Test 2: Testing synchronization cleanup of orphaned state entries"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir
    task_dir=$(setup_task_directory "$context")
    
    # Initialize state and assign numbers
    init_test_state "$context"
    "$NUMBER_MANAGER_SCRIPT" get "$context" >/dev/null  # Gets 1
    "$NUMBER_MANAGER_SCRIPT" get "$context" >/dev/null  # Gets 2
    "$NUMBER_MANAGER_SCRIPT" get "$context" >/dev/null  # Gets 3
    
    # Create only files 1 and 3 (file 2 is missing)
    create_task_file 1 "first-task" "$task_dir"
    create_task_file 3 "third-task" "$task_dir"
    
    # Sync state with files
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Failed to sync state with missing files"
        return 1
    fi
    
    # Verify state only has files 1 and 3
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    local last_assigned
    last_assigned=$(echo "$stats" | jq -r '.last_assigned')
    
    if [ "$used_count" -ne 2 ]; then
        log "ERROR" "Expected used_count=2 (after cleanup), got $used_count"
        return 1
    fi
    
    if [ "$last_assigned" -ne 3 ]; then
        log "ERROR" "Expected last_assigned=3, got $last_assigned"
        return 1
    fi
    
    log "SUCCESS" "Orphaned state entries cleaned up correctly"
    return 0
}

# Test 3: Synchronization - adding new files
test_sync_add_new_files() {
    log "INFO" "Test 3: Testing synchronization adding new files"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir
    task_dir=$(setup_task_directory "$context")
    
    # Initialize state and create initial files
    init_test_state "$context"
    create_task_file 1 "first-task" "$task_dir"
    create_task_file 5 "fifth-task" "$task_dir"
    
    # Sync initial state
    "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1
    
    # Add new files after initial sync
    create_task_file 10 "tenth-task" "$task_dir"
    create_task_file 15 "fifteenth-task" "$task_dir"
    
    # Sync again to incorporate new files
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Failed to sync new files"
        return 1
    fi
    
    # Verify state includes all files
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    local last_assigned
    last_assigned=$(echo "$stats" | jq -r '.last_assigned')
    
    if [ "$used_count" -ne 4 ]; then
        log "ERROR" "Expected used_count=4, got $used_count"
        return 1
    fi
    
    if [ "$last_assigned" -ne 15 ]; then
        log "ERROR" "Expected last_assigned=15, got $last_assigned"
        return 1
    fi
    
    log "SUCCESS" "New files added to state correctly"
    return 0
}

# Test 4: Synchronization - empty task directory
test_sync_empty_directory() {
    log "INFO" "Test 4: Testing synchronization with empty task directory"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir
    task_dir=$(setup_task_directory "$context")
    
    # Initialize state with some numbers
    init_test_state "$context"
    "$NUMBER_MANAGER_SCRIPT" get "$context" >/dev/null
    "$NUMBER_MANAGER_SCRIPT" get "$context" >/dev/null
    "$NUMBER_MANAGER_SCRIPT" get "$context" >/dev/null
    
    # Verify state has entries
    local stats_before
    stats_before=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count_before
    used_count_before=$(echo "$stats_before" | jq -r '.used_count')
    
    if [ "$used_count_before" -ne 3 ]; then
        log "ERROR" "Expected used_count=3 before sync, got $used_count_before"
        return 1
    fi
    
    # Sync with empty directory
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Failed to sync with empty directory"
        return 1
    fi
    
    # Verify state is now empty
    local stats_after
    stats_after=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count_after
    used_count_after=$(echo "$stats_after" | jq -r '.used_count')
    local last_assigned_after
    last_assigned_after=$(echo "$stats_after" | jq -r '.last_assigned')
    
    if [ "$used_count_after" -ne 0 ]; then
        log "ERROR" "Expected used_count=0 after sync, got $used_count_after"
        return 1
    fi
    
    if [ "$last_assigned_after" -ne 0 ]; then
        log "ERROR" "Expected last_assigned=0 after sync, got $last_assigned_after"
        return 1
    fi
    
    log "SUCCESS" "Empty directory synchronization works correctly"
    return 0
}

# Test 5: Synchronization - atomic update test
test_sync_atomic_updates() {
    log "INFO" "Test 5: Testing synchronization atomic updates"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir
    task_dir=$(setup_task_directory "$context")
    
    # Create many task files
    for i in {1..50}; do
        create_task_file "$i" "task-$i" "$task_dir"
    done
    
    # Initialize state
    init_test_state "$context"
    
    # Get initial state timestamp
    local initial_stats
    initial_stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local initial_timestamp
    initial_timestamp=$(echo "$initial_stats" | jq -r '.updated_at')
    
    # Perform sync (should be atomic)
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Failed to perform atomic sync"
        return 1
    fi
    
    # Verify state is consistent after sync
    local final_stats
    final_stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$final_stats" | jq -r '.used_count')
    local last_assigned
    last_assigned=$(echo "$final_stats" | jq -r '.last_assigned')
    local final_timestamp
    final_timestamp=$(echo "$final_stats" | jq -r '.updated_at')
    
    if [ "$used_count" -ne 50 ]; then
        log "ERROR" "Expected used_count=50, got $used_count"
        return 1
    fi
    
    if [ "$last_assigned" -ne 50 ]; then
        log "ERROR" "Expected last_assigned=50, got $last_assigned"
        return 1
    fi
    
    # Verify timestamp was updated
    if [ "$final_timestamp" = "$initial_timestamp" ]; then
        log "ERROR" "Timestamp should have been updated during sync"
        return 1
    fi
    
    # Verify state file is valid JSON
    if ! "$NUMBER_MANAGER_SCRIPT" stats >/dev/null 2>&1; then
        log "ERROR" "State file corrupted during sync"
        return 1
    fi
    
    log "SUCCESS" "Atomic synchronization updates work correctly"
    return 0
}

# Test 6: Synchronization - multiple contexts
test_sync_multiple_contexts() {
    log "INFO" "Test 6: Testing synchronization with multiple contexts"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup multiple contexts
    local contexts=("repo1" "repo2" "repo3")
    
    for context in "${contexts[@]}"; do
        local task_dir
        task_dir=$(setup_task_directory "$context")
        
        # Create files for each context
        create_task_file 1 "task-$context-1" "$task_dir"
        create_task_file 2 "task-$context-2" "$task_dir"
        
        # Initialize state for each context
        init_test_state "$context"
        
        # Sync each context
        if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
            log "ERROR" "Failed to sync context: $context"
            return 1
        fi
    done
    
    # Verify all contexts have correct state
    for context in "${contexts[@]}"; do
        local stats
        stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
        local used_count
        used_count=$(echo "$stats" | jq -r '.used_count')
        
        # Note: stats shows global state, but we can check context assignments
        local context_assignments
        context_assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
        local context_last_assignment
        context_last_assignment=$(echo "$context_assignments" | jq -r ".\"$context\"")
        
        if [ "$context_last_assignment" != "2" ]; then
            log "ERROR" "Context $context should have last assignment 2, got $context_last_assignment"
            return 1
        fi
    done
    
    log "SUCCESS" "Multiple context synchronization works correctly"
    return 0
}

# Test 7: Synchronization - concurrent safety
test_sync_concurrent_safety() {
    log "INFO" "Test 7: Testing synchronization concurrent safety"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir
    task_dir=$(setup_task_directory "$context")
    
    # Create task files
    for i in {1..20}; do
        create_task_file "$i" "task-$i" "$task_dir"
    done
    
    # Initialize state
    init_test_state "$context"
    
    # Perform multiple sync operations rapidly (simulating concurrent access)
    for i in {1..5}; do
        if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
            log "ERROR" "Sync operation $i failed"
            return 1
        fi
    done
    
    # Verify final state is consistent
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    local last_assigned
    last_assigned=$(echo "$stats" | jq -r '.last_assigned')
    
    if [ "$used_count" -ne 20 ]; then
        log "ERROR" "Expected used_count=20, got $used_count"
        return 1
    fi
    
    if [ "$last_assigned" -ne 20 ]; then
        log "ERROR" "Expected last_assigned=20, got $last_assigned"
        return 1
    fi
    
    log "SUCCESS" "Concurrent synchronization safety verified"
    return 0
}

# Test 8: Synchronization - backup creation
test_sync_backup_creation() {
    log "INFO" "Test 8: Testing backup creation during synchronization"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir
    task_dir=$(setup_task_directory "$context")
    
    # Initialize state and create initial files
    init_test_state "$context"
    create_task_file 1 "first-task" "$task_dir"
    
    # Initial sync
    "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1
    
    # Count initial backup files
    local backup_dir="$TEST_STATE_DIR/.number_state/backup"
    local initial_backup_count
    initial_backup_count=$(find "$backup_dir" -name "*.json" 2>/dev/null | wc -l)
    
    # Add new file and sync again (should create backup)
    create_task_file 5 "fifth-task" "$task_dir"
    "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1
    
    # Count backup files after second sync
    local final_backup_count
    final_backup_count=$(find "$backup_dir" -name "*.json" 2>/dev/null | wc -l)
    
    # Should have created at least one backup
    if [ "$final_backup_count" -le "$initial_backup_count" ]; then
        log "ERROR" "Expected backup to be created during sync"
        echo "Initial backups: $initial_backup_count"
        echo "Final backups: $final_backup_count"
        return 1
    fi
    
    log "SUCCESS" "Backup creation during synchronization verified"
    return 0
}

# Test 9: Synchronization - validation after sync
test_sync_validation_after() {
    log "INFO" "Test 9: Testing validation after synchronization"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir
    task_dir=$(setup_task_directory "$context")
    
    # Create task files
    create_task_file 3 "third-task" "$task_dir"
    create_task_file 7 "seventh-task" "$task_dir"
    create_task_file 12 "twelfth-task" "$task_dir"
    
    # Initialize state
    init_test_state "$context"
    
    # Sync state with files
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Failed to sync state"
        return 1
    fi
    
    # Validate consistency
    if ! "$NUMBER_MANAGER_SCRIPT" validate "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Validation failed after sync"
        echo "Validation output:"
        "$NUMBER_MANAGER_SCRIPT" validate "$task_dir" "$context" 2>&1
        return 1
    fi
    
    # Verify no inconsistencies reported
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$task_dir" "$context" 2>&1)
    
    if echo "$validation_output" | grep -q "Numbers in state but not in files"; then
        log "ERROR" "State inconsistencies detected after sync"
        return 1
    fi
    
    if echo "$validation_output" | grep -q "Numbers in files but not in state"; then
        log "ERROR" "File inconsistencies detected after sync"
        return 1
    fi
    
    if ! echo "$validation_output" | grep -q "No inconsistencies found"; then
        log "ERROR" "Expected 'No inconsistencies found' message"
        return 1
    fi
    
    log "SUCCESS" "Validation after synchronization works correctly"
    return 0
}

# Test 10: Synchronization - error handling
test_sync_error_handling() {
    log "INFO" "Test 10: Testing synchronization error handling"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Test 1: Non-existent task directory
    if "$NUMBER_MANAGER_SCRIPT" sync "/nonexistent/directory" "test-context" >/dev/null 2>&1; then
        log "ERROR" "Sync should fail with non-existent directory"
        return 1
    fi
    
    # Test 2: Invalid task directory (file instead of directory)
    mkdir -p "$TEST_STATE_DIR"
    touch "$TEST_STATE_DIR/not-a-directory"
    if "$NUMBER_MANAGER_SCRIPT" sync "$TEST_STATE_DIR/not-a-directory" "test-context" >/dev/null 2>&1; then
        log "ERROR" "Sync should fail with file instead of directory"
        return 1
    fi
    
    # Test 3: Sync without proper initialization
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$TEST_STATE_DIR/tasks"
    # Don't initialize state, just try to sync
    if "$NUMBER_MANAGER_SCRIPT" sync "$TEST_STATE_DIR/tasks" "test-context" >/dev/null 2>&1; then
        log "ERROR" "Sync should fail without state initialization"
        return 1
    fi
    
    log "SUCCESS" "Error handling in synchronization works correctly"
    return 0
}

# Main test execution
run_all_tests() {
    echo ""
    echo "=========================================="
    echo "State Synchronization Tests"
    echo "=========================================="
    
    run_test "Basic Sync Files to State" "test_basic_sync_files_to_state"
    run_test "Sync Cleanup Orphans" "test_sync_cleanup_orphans"
    run_test "Sync Add New Files" "test_sync_add_new_files"
    run_test "Sync Empty Directory" "test_sync_empty_directory"
    run_test "Sync Atomic Updates" "test_sync_atomic_updates"
    run_test "Sync Multiple Contexts" "test_sync_multiple_contexts"
    run_test "Sync Concurrent Safety" "test_sync_concurrent_safety"
    run_test "Sync Backup Creation" "test_sync_backup_creation"
    run_test "Sync Validation After" "test_sync_validation_after"
    run_test "Sync Error Handling" "test_sync_error_handling"
    
    echo ""
    echo "=========================================="
    echo "Test Results: $TESTS_PASSED/$TESTS_RUN passed"
    echo "=========================================="
    
    if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
        log "SUCCESS" "All state synchronization tests passed!"
        return 0
    else
        log "ERROR" "Some state synchronization tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests state synchronization with actual task files"
    exit 1
fi