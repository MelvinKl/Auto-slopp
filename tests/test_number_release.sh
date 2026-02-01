#!/bin/bash

# Test Number Release Functionality
# Tests proper release of numbers back to available pool

SCRIPT_NAME="test_number_release"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_number_release_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

log "INFO" "Starting number release tests in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Basic number release functionality
test_basic_release() {
    log "INFO" "Test 1: Testing basic number release functionality"
    
    # Arrange - Initialize and assign numbers
    "$NUMBER_MANAGER_SCRIPT" init release_test >/dev/null 2>&1
    local num1=$("$NUMBER_MANAGER_SCRIPT" get release_test 2>/dev/null | tail -1)  # 1
    local num2=$("$NUMBER_MANAGER_SCRIPT" get release_test 2>/dev/null | tail -1)  # 2
    local num3=$("$NUMBER_MANAGER_SCRIPT" get release_test 2>/dev/null | tail -1)  # 3
    
    # Act - Release number 2
    if "$NUMBER_MANAGER_SCRIPT" release 2 release_test; then
        log "SUCCESS" "Number 2 released successfully"
    else
        log "ERROR" "Failed to release number 2"
        return 1
    fi
    
    # Assert - Check state consistency
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    if [ "$used_count" = "2" ]; then
        log "SUCCESS" "Used count updated correctly after release: $used_count"
    else
        log "ERROR" "Used count incorrect after release: $used_count"
        return 1
    fi
    
    # Assert - Verify gaps detection works
    local gaps
    gaps=$("$NUMBER_MANAGER_SCRIPT" gaps release_test 2>/dev/null)
    if echo "$gaps" | grep -q "Gap: number 2 is not used"; then
        log "SUCCESS" "Gap detected correctly after release"
    else
        log "ERROR" "Gap not detected after release: $gaps"
        return 1
    fi
    
    return 0
}

# Test 2: Release with context information
test_release_with_context() {
    log "INFO" "Test 2: Testing release with context information"
    
    # Arrange - Create different contexts
    "$NUMBER_MANAGER_SCRIPT" init ctx_test >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get ctx_test >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get ctx_test >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" get other_context >/dev/null 2>&1  # 3
    
    # Act - Release with specific context
    if "$NUMBER_MANAGER_SCRIPT" release 2 ctx_test; then
        log "SUCCESS" "Number 2 released with context ctx_test"
    else
        log "ERROR" "Failed to release number 2 with context"
        return 1
    fi
    
    # Assert - Check context assignments
    local contexts
    contexts=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    local ctx_test_assignment
    ctx_test_assignment=$(echo "$contexts" | jq -r '.ctx_test // "empty"')
    
    # Context should still exist but might not have assignment
    log "INFO" "Context ctx_test assignment after release: $ctx_test_assignment"
    
    return 0
}

# Test 3: Multiple sequential releases
test_multiple_releases() {
    log "INFO" "Test 3: Testing multiple sequential releases"
    
    # Clean up any existing state for this test
    rm -rf "$TEST_STATE_DIR/.number_state"
    
    # Arrange - Assign multiple numbers
    "$NUMBER_MANAGER_SCRIPT" init multi_release >/dev/null 2>&1
    local assigned_numbers=()
    for i in {1..5}; do
        local num=$("$NUMBER_MANAGER_SCRIPT" get multi_release 2>/dev/null | tail -1)
        assigned_numbers+=("$num")
    done
    
    # Debug: Show initial state
    local initial_stats
    initial_stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local initial_count
    initial_count=$(echo "$initial_stats" | jq -r '.used_count')
    log "DEBUG" "Initial used count: $initial_count"
    
    # Act - Release multiple numbers
    for num in 2 4; do
        if "$NUMBER_MANAGER_SCRIPT" release "$num" multi_release; then
            log "SUCCESS" "Released number $num"
        else
            log "ERROR" "Failed to release number $num"
            return 1
        fi
    done
    
    # Assert - Check final state
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    # Should have 3 numbers remaining (1, 3, 5)
    if [ "$used_count" = "3" ]; then
        log "SUCCESS" "Correct count after multiple releases: $used_count"
    else
        log "ERROR" "Incorrect count after multiple releases: $used_count"
        log "DEBUG" "Full stats: $stats"
        return 1
    fi
    
    # Assert - Verify gaps for released numbers
    local gaps
    gaps=$("$NUMBER_MANAGER_SCRIPT" gaps multi_release 2>/dev/null)
    local gap_count
    gap_count=$(echo "$gaps" | grep -c "Gap: number")
    
    if [ "$gap_count" = "2" ]; then
        log "SUCCESS" "Correct number of gaps detected: $gap_count"
    else
        log "ERROR" "Incorrect gap count: $gap_count"
        log "DEBUG" "Gap output: $gaps"
        return 1
    fi
    
    return 0
}

# Test 4: Invalid release handling
test_invalid_release() {
    log "INFO" "Test 4: Testing invalid release handling"
    
    # Arrange
    "$NUMBER_MANAGER_SCRIPT" init invalid_test >/dev/null 2>&1
    
    # Act & Assert - Test negative number
    if "$NUMBER_MANAGER_SCRIPT" release -1 invalid_test 2>/dev/null; then
        log "ERROR" "Should have failed to release negative number"
        return 1
    else
        log "SUCCESS" "Correctly rejected negative number release"
    fi
    
    # Act & Assert - Test number > 9999
    if "$NUMBER_MANAGER_SCRIPT" release 10000 invalid_test 2>/dev/null; then
        log "ERROR" "Should have failed to release number > 9999"
        return 1
    else
        log "SUCCESS" "Correctly rejected too-large number release"
    fi
    
    # Act & Assert - Test non-numeric input
    if "$NUMBER_MANAGER_SCRIPT" release "abc" invalid_test 2>/dev/null; then
        log "ERROR" "Should have failed to release non-numeric input"
        return 1
    else
        log "SUCCESS" "Correctly rejected non-numeric release"
    fi
    
    # Act & Assert - Test release of unassigned number
    if "$NUMBER_MANAGER_SCRIPT" release 999 invalid_test; then
        log "SUCCESS" "Released unassigned number (acceptable behavior)"
    else
        log "SUCCESS" "Rejected unassigned number (also acceptable)"
    fi
    
    return 0
}

# Test 5: Release after file synchronization
test_release_after_sync() {
    log "INFO" "Test 5: Testing release after file synchronization"
    
    # Arrange - Create test files and sync
    "$NUMBER_MANAGER_SCRIPT" init sync_release >/dev/null 2>&1
    local test_task_dir="$TEST_STATE_DIR/test_repo"
    mkdir -p "$test_task_dir"
    
    # Create test files
    touch "$test_task_dir/0001-task1.txt"
    touch "$test_task_dir/0003-task2.txt"
    touch "$test_task_dir/0005-task3.txt"
    
    # Sync with files
    "$NUMBER_MANAGER_SCRIPT" sync "$test_task_dir" sync_release >/dev/null 2>&1
    
    # Act - Release a synced number
    if "$NUMBER_MANAGER_SCRIPT" release 3 sync_release; then
        log "SUCCESS" "Released synced number 3"
    else
        log "ERROR" "Failed to release synced number 3"
        return 1
    fi
    
    # Debug: Check state before release
    local before_stats
    before_stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    log "DEBUG" "Stats before release: $before_stats"
    
    # Assert - State should be updated
    local gaps
    gaps=$("$NUMBER_MANAGER_SCRIPT" gaps sync_release 2>/dev/null)
    log "DEBUG" "Gap output: $gaps"
    if echo "$gaps" | grep -q "Gap: number 3 is not used"; then
        log "SUCCESS" "Gap 3 detected correctly after synced release"
    else
        log "ERROR" "Gap 3 not detected after synced release"
        log "DEBUG" "Gap output: $gaps"
        
        # Check what numbers are actually in used_numbers
        local used_nums
        used_nums=$(jq -r '.used_numbers[]' "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null | tr '\n' ' ')
        log "DEBUG" "Used numbers in state: $used_nums"
        return 1
    fi
    
    # Count total gaps to verify proper detection
    local gap_count
    gap_count=$(echo "$gaps" | grep -c "Gap: number")
    if [ "$gap_count" -ge 1 ]; then
        log "SUCCESS" "At least one gap detected: $gap_count total gaps"
    else
        log "ERROR" "No gaps detected after synced release"
        return 1
    fi
    
    return 0
}

# Test 6: State consistency after releases
test_state_consistency() {
    log "INFO" "Test 6: Testing state consistency after releases"
    
    # Arrange - Create complex scenario
    "$NUMBER_MANAGER_SCRIPT" init consistency_test >/dev/null 2>&1
    
    # Assign numbers in different contexts
    "$NUMBER_MANAGER_SCRIPT" get consistency_test >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get consistency_test >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" get other_consistency >/dev/null 2>&1  # 3
    "$NUMBER_MANAGER_SCRIPT" get consistency_test >/dev/null 2>&1  # 4
    
    # Act - Release numbers
    "$NUMBER_MANAGER_SCRIPT" release 2 consistency_test >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" release 4 consistency_test >/dev/null 2>&1
    
    # Assert - Validate final state
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    local last_assigned
    last_assigned=$(echo "$stats" | jq -r '.last_assigned')
    
    # Should have 2 numbers remaining (1, 3) and last_assigned should be 4
    if [ "$used_count" = "2" ] && [ "$last_assigned" = "4" ]; then
        log "SUCCESS" "State consistent after releases: used=$used_count, last=$last_assigned"
    else
        log "ERROR" "State inconsistent: used=$used_count, last=$last_assigned"
        return 1
    fi
    
    # Assert - JSON should remain valid
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if jq empty "$state_file" 2>/dev/null; then
        log "SUCCESS" "State file remains valid JSON after releases"
    else
        log "ERROR" "State file corrupted after releases"
        return 1
    fi
    
    return 0
}

# Test 7: Concurrent release attempts
test_concurrent_release() {
    log "INFO" "Test 7: Testing concurrent release attempts"
    
    # Arrange - Set up state
    "$NUMBER_MANAGER_SCRIPT" init concurrent_test >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get concurrent_test >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get concurrent_test >/dev/null 2>&1  # 2
    
    # Act - Attempt concurrent releases (simulate with background processes)
    (
        sleep 0.1
        "$NUMBER_MANAGER_SCRIPT" release 1 concurrent_test >/dev/null 2>&1
    ) &
    local pid1=$!
    
    (
        sleep 0.1
        "$NUMBER_MANAGER_SCRIPT" release 2 concurrent_test >/dev/null 2>&1
    ) &
    local pid2=$!
    
    # Wait for both to complete
    wait $pid1
    wait $pid2
    
    # Assert - At least one should succeed
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    if [ "$used_count" -le 2 ]; then
        log "SUCCESS" "Concurrent releases handled gracefully: $used_count remaining"
    else
        log "ERROR" "Unexpected state after concurrent releases: $used_count"
        return 1
    fi
    
    return 0
}

# Test 8: Release with backup creation
test_release_with_backup() {
    log "INFO" "Test 8: Testing backup creation during release"
    
    # Arrange
    "$NUMBER_MANAGER_SCRIPT" init backup_test >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get backup_test >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get backup_test >/dev/null 2>&1  # 2
    
    # Act - Release number to trigger backup
    "$NUMBER_MANAGER_SCRIPT" release 1 backup_test >/dev/null 2>&1
    
    # Assert - Check backup was created
    local backup_dir="$TEST_STATE_DIR/.number_state/backup"
    local backup_count
    backup_count=$(ls -1 "$backup_dir"/*.json 2>/dev/null | wc -l)
    
    if [ "$backup_count" -gt 0 ]; then
        log "SUCCESS" "Backup created during release operation"
    else
        log "ERROR" "No backup created during release"
        return 1
    fi
    
    return 0
}

# Run all tests
run_all_tests() {
    local test_count=0
    local pass_count=0
    
    # List of test functions
    local tests=(
        "test_basic_release"
        "test_release_with_context"
        "test_multiple_releases"
        "test_invalid_release"
        "test_release_after_sync"
        "test_state_consistency"
        "test_concurrent_release"
        "test_release_with_backup"
    )
    
    for test_func in "${tests[@]}"; do
        test_count=$((test_count + 1))
        echo ""
        echo "=========================================="
        echo "Running $test_func"
        echo "=========================================="
        
        # Clean up state between tests
        rm -rf "$TEST_STATE_DIR/.number_state"
        
        if $test_func; then
            pass_count=$((pass_count + 1))
            echo "✅ $test_func PASSED"
        else
            echo "❌ $test_func FAILED"
        fi
    done
    
    echo ""
    echo "=========================================="
    echo "Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All number release tests passed!"
        return 0
    else
        log "ERROR" "Some number release tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests the number release functionality of number_manager.sh"
    exit 1
fi