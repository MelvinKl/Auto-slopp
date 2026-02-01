#!/bin/bash

# Test planner.sh error handling with number_manager.sh integration
# This test validates robust error handling and recovery scenarios

SCRIPT_NAME="test_planner_error_handling"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test configuration
TEST_STATE_DIR="/tmp/test_planner_error_handling_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"
PLANNER_SCRIPT="$BASE_DIR/scripts/planner.sh"

# Mock config values
export MANAGED_REPO_PATH="$TEST_STATE_DIR/managed"
export MANAGED_REPO_TASK_PATH="$TEST_STATE_DIR/tasks"
export OPencode_CMD="echo"  # Mock the opencode command

log "INFO" "Starting planner error handling tests in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test results counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to log test results
log_test_result() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    if [ "$result" = "PASS" ]; then
        echo -e "\033[0;32m✓ PASS\033[0m: $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "\033[0;31m✗ FAIL\033[0m: $test_name"
        echo -e "  \033[1;33mDetails: $details\033[0m"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Setup test environment
setup_test_env() {
    log "INFO" "Setting up test environment for error handling..."
    
    # Create test directory structure
    mkdir -p "$MANAGED_REPO_PATH/test_repo"
    mkdir -p "$MANAGED_REPO_TASK_PATH/test_repo"
    
    # Initialize number manager state
    if ! "$NUMBER_MANAGER_SCRIPT" init test_repo >/dev/null 2>&1; then
        log "ERROR" "Failed to initialize number manager"
        return 1
    fi
    
    # Initialize git repos for testing
    cd "$MANAGED_REPO_PATH/test_repo"
    git init >/dev/null 2>&1
    git config user.email "test@example.com"
    git config user.name "Test User"
    echo "# Test Repo" > README.md
    git add README.md >/dev/null 2>&1
    git commit -m "Initial commit" >/dev/null 2>&1
    
    # Create origin remote
    git init --bare origin.git >/dev/null 2>&1
    git remote add origin "$MANAGED_REPO_PATH/test_repo/origin.git"
    git push -u origin main >/dev/null 2>&1 || git push -u origin master >/dev/null 2>&1
    
    cd "$MANAGED_REPO_TASK_PATH/test_repo"
    git init >/dev/null 2>&1
    git config user.email "test@example.com"
    git config user.name "Test User"
    echo "# Task Directory" > README.md
    git add README.md >/dev/null 2>&1
    git commit -m "Initial commit" >/dev/null 2>&1
    
    return 0
}

# Test 1: Number manager unavailable scenario
test_number_manager_unavailable() {
    log "INFO" "Test 1: Testing number manager unavailable scenario"
    
    # Temporarily make number manager script non-executable
    chmod -x "$NUMBER_MANAGER_SCRIPT"
    
    cd "$MANAGED_REPO_TASK_PATH/test_repo"
    echo "Test task" > "task.txt"
    
    # Try to get a number from number manager
    next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    exit_code=$?
    
    # Restore permissions
    chmod +x "$NUMBER_MANAGER_SCRIPT"
    
    if [ $exit_code -ne 0 ]; then
        log_test_result "Number manager unavailable handling" "PASS" "Correctly failed when number manager unavailable"
    else
        log_test_result "Number manager unavailable handling" "FAIL" "Should have failed when number manager unavailable"
        return 1
    fi
    
    # Clean up test file
    rm -f "task.txt"
    
    return 0
}

# Test 2: Corrupted state file recovery
test_corrupted_state_recovery() {
    log "INFO" "Test 2: Testing corrupted state file recovery"
    
    # Ensure state directory exists
    mkdir -p "$TEST_STATE_DIR/.number_state"
    
    # Create a corrupted state file
    state_file="$TEST_STATE_DIR/.number_state/state.json"
    echo "{ invalid json content" > "$state_file"
    
    # Try to get a number - should trigger recovery
    next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ] && [ -n "$next_num" ]; then
        log_test_result "Corrupted state recovery" "PASS" "Successfully recovered from corrupted state, got number: $next_num"
    else
        log_test_result "Corrupted state recovery" "FAIL" "Failed to recover from corrupted state"
        return 1
    fi
    
    # Verify state file is now valid
    if jq empty "$state_file" 2>/dev/null; then
        log_test_result "State file validation after recovery" "PASS" "State file is valid JSON after recovery"
    else
        log_test_result "State file validation after recovery" "FAIL" "State file is still invalid after recovery"
        return 1
    fi
    
    return 0
}

# Test 3: Missing state directory handling
test_missing_state_directory() {
    log "INFO" "Test 3: Testing missing state directory handling"
    
    # Remove state directory
    rm -rf "$TEST_STATE_DIR/.number_state"
    
    # Try to get a number - should initialize automatically  
    next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ] && [ -n "$next_num" ]; then
        log_test_result "Missing state directory handling" "PASS" "Auto-initialized state and got number: $next_num"
    else
        log_test_result "Missing state directory handling" "FAIL" "Failed to handle missing state directory"
        return 1
    fi
    
    # Verify state directory was created
    if [ -d "$TEST_STATE_DIR/.number_state" ] && [ -f "$TEST_STATE_DIR/.number_state/state.json" ]; then
        log_test_result "State directory creation" "PASS" "State directory and file created automatically"
    else
        log_test_result "State directory creation" "FAIL" "State directory not created properly"
        return 1
    fi
    
    return 0
}

# Test 4: Permission denied scenarios
test_permission_denied_scenarios() {
    log "INFO" "Test 4: Testing permission denied scenarios"
    
    # Ensure state directory exists first
    mkdir -p "$TEST_STATE_DIR/.number_state"
    
    # Remove write permissions from state directory
    chmod -w "$TEST_STATE_DIR/.number_state"
    
    # Try to get a number
    next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    exit_code=$?
    
    # Restore permissions
    chmod +w "$TEST_STATE_DIR/.number_state"
    
    if [ $exit_code -ne 0 ]; then
        log_test_result "Permission denied handling" "PASS" "Correctly failed with permission denied"
    else
        log_test_result "Permission denied handling" "FAIL" "Should have failed with permission denied"
        return 1
    fi
    
    # Verify it works again after permissions restored
    next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    if [ $? -eq 0 ]; then
        log_test_result "Recovery after permission fix" "PASS" "Recovered after permissions restored"
    else
        log_test_result "Recovery after permission fix" "FAIL" "Did not recover after permissions restored"
        return 1
    fi
    
    return 0
}

# Test 5: Disk space simulation
test_disk_space_exhaustion() {
    log "INFO" "Test 5: Testing disk space exhaustion simulation"
    
    # Create a small temporary filesystem to simulate full disk
    # Since we can't easily simulate full disk, we'll test file creation failures
    
    # Try to create a backup file in a non-existent directory
    state_dir="$TEST_STATE_DIR/.number_state"
    mkdir -p "$state_dir/invalid_subdir"
    chmod 000 "$state_dir/invalid_subdir"  # Make it inaccessible
    
    # Try to trigger backup (should fail gracefully)
    next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    exit_code=$?
    
    # Clean up
    chmod 755 "$state_dir/invalid_subdir"
    rm -rf "$state_dir/invalid_subdir"
    
    # This should still work despite backup issues
    if [ $exit_code -eq 0 ]; then
        log_test_result "Disk space error handling" "PASS" "Handled backup directory issues gracefully"
    else
        log_test_result "Disk space error handling" "FAIL" "Did not handle backup directory issues"
        return 1
    fi
    
    return 0
}

# Test 6: Invalid repository context handling
test_invalid_repository_context() {
    log "INFO" "Test 6: Testing invalid repository context handling"
    
    # Try to use invalid context names
    invalid_contexts=("" " " "repo with spaces" "repo/with/slashes" "repo-with-dots.sh")
    
    for context in "${invalid_contexts[@]}"; do
        if [ -n "$context" ]; then
            # Try to initialize with invalid context
            if "$NUMBER_MANAGER_SCRIPT" init "$context" >/dev/null 2>&1; then
                log_test_result "Invalid context rejection" "FAIL" "Should have rejected invalid context: '$context'"
                return 1
            fi
        fi
    done
    
    log_test_result "Invalid context rejection" "PASS" "Correctly rejected invalid context names"
    
    # Test with valid context that doesn't have corresponding directories
    next_num=$("$NUMBER_MANAGER_SCRIPT" get "nonexistent_repo" 2>/dev/null | tail -1)
    if [ $? -eq 0 ]; then
        log_test_result "Nonexistent context handling" "PASS" "Handled nonexistent repository context"
    else
        log_test_result "Nonexistent context handling" "FAIL" "Failed to handle nonexistent repository context"
        return 1
    fi
    
    return 0
}

# Test 7: Concurrent access simulation
test_concurrent_access_simulation() {
    log "INFO" "Test 7: Testing concurrent access simulation"
    
    # Create a lock file manually to simulate another process
    lock_file="$TEST_STATE_DIR/.number_state/.lock"
    echo "$$:$(( $(date +%s) - 100 ))" > "$lock_file"  # Old lock
    
    # Try to get a number - should remove stale lock
    next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_test_result "Stale lock removal" "PASS" "Removed stale lock and proceeded"
    else
        log_test_result "Stale lock removal" "FAIL" "Failed to remove stale lock"
        return 1
    fi
    
    # Test with active lock (simulate using current PID)
    echo "$$:$(( $(date +%s) - 10 ))" > "$lock_file"
    
    # Try again - should fail due to active lock
    next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    exit_code=$?
    
    # Clean up lock
    rm -f "$lock_file"
    
    if [ $exit_code -ne 0 ]; then
        log_test_result "Active lock respect" "PASS" "Respected active lock and failed appropriately"
    else
        log_test_result "Active lock respect" "FAIL" "Did not respect active lock"
        return 1
    fi
    
    return 0
}

# Test 8: File system corruption handling
test_file_system_corruption() {
    log "INFO" "Test 8: Testing file system corruption handling"
    
    # Create a state file with incomplete write
    state_file="$TEST_STATE_DIR/.number_state/state.json"
    cat > "$state_file" << 'EOF'
{
    "used_numbers": [1, 2, 3],
    "last_assigned": 3,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "context_assignments": {
EOF
    
    # File is incomplete JSON, should trigger recovery
    
    next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_test_result "File system corruption recovery" "PASS" "Recovered from incomplete file write"
    else
        log_test_result "File system corruption recovery" "FAIL" "Failed to recover from incomplete file write"
        return 1
    fi
    
    return 0
}

# Test 9: Number overflow handling
test_number_overflow() {
    log "INFO" "Test 9: Testing number overflow handling"
    
    # Ensure state exists
    "$NUMBER_MANAGER_SCRIPT" init test_repo >/dev/null 2>&1
    
    # Manually set last assigned to near limit
    state_file="$TEST_STATE_DIR/.number_state/state.json"
    jq '.last_assigned = 9998 | .used_numbers = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98]' "$state_file" > "${state_file}.tmp" && mv "${state_file}.tmp" "$state_file"
    
    # Get a few numbers to approach limit
    num1=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    
    # Try to get number beyond limit
    num2=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    exit_code=$?
    
    if [ "$num1" = "9999" ] && [ $exit_code -ne 0 ]; then
        log_test_result "Number overflow handling" "PASS" "Correctly handled number limit"
    else
        log_test_result "Number overflow handling" "FAIL" "Did not handle number limit correctly: got $num1, exit $exit_code"
        return 1
    fi
    
    # Reset to normal state
    jq '.last_assigned = 2 | .used_numbers = [1, 2]' "$state_file" > "${state_file}.tmp" && mv "${state_file}.tmp" "$state_file"
    
    return 0
}

# Test 10: Git operation failures
test_git_operation_failures() {
    log "INFO" "Test 10: Testing git operation failures"
    
    cd "$MANAGED_REPO_TASK_PATH/test_repo"
    
    # Create an unnumbered task file
    echo "Test task" > "git-test.txt"
    
    # Get a number
    next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    if [ $? -eq 0 ]; then
        # Rename file
        new_filename=$(printf "%04d-%s.txt" "$next_num" "git-test")
        mv "git-test.txt" "$new_filename"
        
        # Try git operations in a read-only directory
        chmod -w .
        git add . >/dev/null 2>&1
        git_exit_code=$?
        chmod +w .
        
        # Even if git fails, the number assignment should still work
        if [ "$next_num" = "3" ]; then
            log_test_result "Git failure independence" "PASS" "Number assignment worked despite potential git issues"
        else
            log_test_result "Git failure independence" "FAIL" "Number assignment affected by git issues"
            return 1
        fi
    else
        log_test_result "Number assignment before git test" "FAIL" "Failed to assign number for git test"
        return 1
    fi
    
    return 0
}

# Run all tests
run_all_tests() {
    echo ""
    echo "=========================================="
    echo "Running Planner Error Handling Tests"
    echo "=========================================="
    
    # Setup
    if ! setup_test_env; then
        log "ERROR" "Test environment setup failed"
        return 1
    fi
    
    # List of test functions
    local tests=(
        "test_number_manager_unavailable"
        "test_corrupted_state_recovery"
        "test_missing_state_directory"
        "test_permission_denied_scenarios"
        "test_disk_space_exhaustion"
        "test_invalid_repository_context"
        "test_concurrent_access_simulation"
        "test_file_system_corruption"
        "test_number_overflow"
        "test_git_operation_failures"
    )
    
    for test_func in "${tests[@]}"; do
        echo ""
        echo "------------------------------------------"
        echo "Running $test_func"
        echo "------------------------------------------"
        
        if $test_func; then
            echo "✅ $test_func PASSED"
        else
            echo "❌ $test_func FAILED"
        fi
    done
    
    echo ""
    echo "=========================================="
    echo "Test Results: $TESTS_PASSED/$((TESTS_PASSED + TESTS_FAILED)) passed"
    echo "=========================================="
    
    if [ $TESTS_FAILED -eq 0 ]; then
        log "SUCCESS" "All planner error handling tests passed!"
        return 0
    else
        log "ERROR" "Some planner error handling tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests planner.sh error handling with number_manager.sh integration"
    exit 1
fi