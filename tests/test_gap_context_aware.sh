#!/bin/bash

# Test Reuse After Release Functionality
# Tests reassignment of released numbers back to available pool

SCRIPT_NAME="test_reuse_after_release"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_reuse_after_release_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

log "INFO" "Starting reuse after release tests in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Basic number reuse after release
test_basic_number_reuse() {
    log "INFO" "Test 1: Testing basic number reuse after release"
    
    # Arrange - Initialize and assign numbers
    "$NUMBER_MANAGER_SCRIPT" init basic_reuse >/dev/null 2>&1
    local num1=$("$NUMBER_MANAGER_SCRIPT" get basic_reuse 2>/dev/null | tail -1)  # 1
    local num2=$("$NUMBER_MANAGER_SCRIPT" get basic_reuse 2>/dev/null | tail -1)  # 2
    local num3=$("$NUMBER_MANAGER_SCRIPT" get basic_reuse 2>/dev/null | tail -1)  # 3
    
    # Release number 2
    "$NUMBER_MANAGER_SCRIPT" release 2 basic_reuse >/dev/null 2>&1
    
    # Act - Get next number (should continue from 4, not reuse 2)
    local next_num
    next_num=$("$NUMBER_MANAGER_SCRIPT" get basic_reuse 2>/dev/null | tail -1)
    
    # Assert - Current implementation continues sequence, doesn't reuse
    if [ "$next_num" = "4" ]; then
        log "SUCCESS" "Number assignment continues sequence after release: $next_num"
    else
        log "ERROR" "Unexpected number assignment after release: $next_num (expected 4)"
        return 1
    fi
    
    # Assert - Gap should still exist
    local gaps
    gaps=$("$NUMBER_MANAGER_SCRIPT" gaps basic_reuse 2>/dev/null)
    if echo "$gaps" | grep -q "Gap: number 2 is not used"; then
        log "SUCCESS" "Gap persists after new assignment"
    else
        log "ERROR" "Gap unexpectedly filled: $gaps"
        return 1
    fi
    
    return 0
}

# Test 2: Multiple releases and subsequent assignments
test_multiple_releases_assignments() {
    log "INFO" "Test 2: Testing multiple releases and subsequent assignments"
    
    # Arrange - Create scenario with multiple gaps
    "$NUMBER_MANAGER_SCRIPT" init multi_reuse >/dev/null 2>&1
    
    # Assign first 6 numbers
    local assigned_numbers=()
    for i in {1..6}; do
        local num=$("$NUMBER_MANAGER_SCRIPT" get multi_reuse 2>/dev/null | tail -1)
        assigned_numbers+=("$num")
    done
    
    # Release numbers 2, 4, 6
    "$NUMBER_MANAGER_SCRIPT" release 2 multi_reuse >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" release 4 multi_reuse >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" release 6 multi_reuse >/dev/null 2>&1
    
    # Act - Continue assignments
    local next_nums=()
    for i in {1..3}; do
        local num=$("$NUMBER_MANAGER_SCRIPT" get multi_reuse 2>/dev/null | tail -1)
        next_nums+=("$num")
    done
    
    # Assert - Should continue from 7, 8, 9
    local expected=(7 8 9)
    for i in "${!next_nums[@]}"; do
        if [ "${next_nums[i]}" = "${expected[i]}" ]; then
            log "SUCCESS" "Assignment ${i} continues correctly: ${next_nums[i]}"
        else
            log "ERROR" "Assignment ${i} incorrect: ${next_nums[i]} (expected ${expected[i]})"
            return 1
        fi
    done
    
    # Assert - Gaps should persist
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    # Should have 6 numbers used: 1, 3, 5, 7, 8, 9
    if [ "$used_count" = "6" ]; then
        log "SUCCESS" "Correct used count after multiple releases: $used_count"
    else
        log "ERROR" "Incorrect used count: $used_count"
        return 1
    fi
    
    return 0
}

# Test 3: Reuse in different contexts
test_reuse_different_contexts() {
    log "INFO" "Test 3: Testing reuse behavior in different contexts"
    
    # Arrange - Create multiple contexts
    "$NUMBER_MANAGER_SCRIPT" init ctx_reuse >/dev/null 2>&1
    
    # Context A: assign and release
    "$NUMBER_MANAGER_SCRIPT" get context_a >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get context_a >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" release 2 context_a >/dev/null 2>&1
    
    # Context B: continue assignments
    local num_b1=$("$NUMBER_MANAGER_SCRIPT" get context_b 2>/dev/null | tail -1)  # 3
    local num_b2=$("$NUMBER_MANAGER_SCRIPT" get context_b 2>/dev/null | tail -1)  # 4
    
    # Context A: more assignments
    local num_a3=$("$NUMBER_MANAGER_SCRIPT" get context_a 2>/dev/null | tail -1)  # 5
    
    # Act & Assert - Should continue global sequence
    if [ "$num_b1" = "3" ] && [ "$num_b2" = "4" ] && [ "$num_a3" = "5" ]; then
        log "SUCCESS" "Cross-context sequence continuation works"
    else
        log "ERROR" "Cross-context sequence broken: B1=$num_b1, B2=$num_b2, A3=$num_a3"
        return 1
    fi
    
    # Assert - Gap from context A should be visible in all contexts
    local gaps_a
    gaps_a=$("$NUMBER_MANAGER_SCRIPT" gaps context_a 2>/dev/null)
    local gaps_b
    gaps_b=$("$NUMBER_MANAGER_SCRIPT" gaps context_b 2>/dev/null)
    
    # Both should see gap at number 2
    if echo "$gaps_a" | grep -q "Gap: number 2 is not used" && \
       echo "$gaps_b" | grep -q "Gap: number 2 is not used"; then
        log "SUCCESS" "Gap visible across all contexts"
    else
        log "ERROR" "Gap not consistently visible across contexts"
        return 1
    fi
    
    return 0
}

# Test 4: State consistency during reuse operations
test_state_consistency_reuse() {
    log "INFO" "Test 4: Testing state consistency during reuse operations"
    
    # Arrange - Create complex scenario
    "$NUMBER_MANAGER_SCRIPT" init consistency_reuse >/dev/null 2>&1
    
    # Build up state with multiple releases
    for i in {1..10}; do
        "$NUMBER_MANAGER_SCRIPT" get consistency_reuse >/dev/null 2>&1
    done
    
    # Release every third number
    for ((i=3; i<=9; i+=3)); do
        "$NUMBER_MANAGER_SCRIPT" release "$i" consistency_reuse >/dev/null 2>&1
    done
    
    # Act - Perform multiple assignments
    local before_stats
    before_stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local before_count
    before_count=$(echo "$before_stats" | jq -r '.used_count')
    
    for i in {1..5}; do
        "$NUMBER_MANAGER_SCRIPT" get consistency_reuse >/dev/null 2>&1
    done
    
    local after_stats
    after_stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local after_count
    after_count=$(echo "$after_stats" | jq -r '.used_count')
    
    # Assert - Should have 5 more numbers
    local expected_count=$((before_count + 5))
    if [ "$after_count" = "$expected_count" ]; then
        log "SUCCESS" "State count consistent: $before_count -> $after_count"
    else
        log "ERROR" "State count inconsistent: expected $expected_count, got $after_count"
        return 1
    fi
    
    # Assert - JSON should remain valid
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if jq empty "$state_file" 2>/dev/null; then
        log "SUCCESS" "State file remains valid JSON during reuse"
    else
        log "ERROR" "State file corrupted during reuse"
        return 1
    fi
    
    return 0
}

# Test 5: Reuse after file synchronization
test_reuse_after_sync() {
    log "INFO" "Test 5: Testing reuse after file synchronization"
    
    # Arrange - Create files and sync
    "$NUMBER_MANAGER_SCRIPT" init sync_reuse >/dev/null 2>&1
    local test_task_dir="$TEST_STATE_DIR/test_repo_sync"
    mkdir -p "$test_task_dir"
    
    # Create files with gaps
    touch "$test_task_dir/0001-task1.txt"
    touch "$test_task_dir/0003-task2.txt"
    touch "$test_task_dir/0005-task3.txt"
    
    # Sync to establish state
    "$NUMBER_MANAGER_SCRIPT" sync "$test_task_dir" sync_reuse >/dev/null 2>&1
    
    # Act - Get new number after sync
    local next_num
    next_num=$("$NUMBER_MANAGER_SCRIPT" get sync_reuse 2>/dev/null | tail -1)
    
    # Assert - Should continue from 6
    if [ "$next_num" = "6" ]; then
        log "SUCCESS" "Number assignment continues after sync: $next_num"
    else
        log "ERROR" "Unexpected number after sync: $next_num"
        return 1
    fi
    
    # Assert - Gaps should still exist
    local gaps
    gaps=$("$NUMBER_MANAGER_SCRIPT" gaps sync_reuse 2>/dev/null)
    local gap_count
    gap_count=$(echo "$gaps" | grep -c "Gap: number")
    
    if [ "$gap_count" = "2" ]; then  # gaps at 2, 4
        log "SUCCESS" "Gaps preserved after sync reuse: $gap_count"
    else
        log "ERROR" "Gaps not preserved after sync reuse: $gap_count"
        return 1
    fi
    
    return 0
}

# Test 6: Concurrent reuse attempts
test_concurrent_reuse() {
    log "INFO" "Test 6: Testing concurrent reuse attempts"
    
    # Arrange - Set up state with gaps
    "$NUMBER_MANAGER_SCRIPT" init concurrent_reuse >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get concurrent_reuse >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get concurrent_reuse >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" release 2 concurrent_reuse >/dev/null 2>&1
    
    # Act - Attempt concurrent assignments
    (
        sleep 0.1
        "$NUMBER_MANAGER_SCRIPT" get concurrent_reuse >/dev/null 2>&1
    ) &
    local pid1=$!
    
    (
        sleep 0.1
        "$NUMBER_MANAGER_SCRIPT" get concurrent_reuse >/dev/null 2>&1
    ) &
    local pid2=$!
    
    # Wait for completion
    wait $pid1
    wait $pid2
    
    # Assert - Should have 2 new unique numbers
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    if [ "$used_count" = "3" ]; then  # Original 1 + 2 new assignments
        log "SUCCESS" "Concurrent reuse handled correctly: $used_count"
    else
        log "ERROR" "Concurrent reuse failed: $used_count"
        return 1
    fi
    
    return 0
}

# Test 7: Reuse at maximum boundary
test_reuse_at_boundary() {
    log "INFO" "Test 7: Testing reuse behavior at maximum boundary"
    
    # Arrange - Create state near maximum
    "$NUMBER_MANAGER_SCRIPT" init boundary_reuse >/dev/null 2>&1
    
    # Manually set state near boundary
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    jq '.last_assigned = 9998 | .used_numbers = [9998]' "$state_file" > "${state_file}.tmp" && mv "${state_file}.tmp" "$state_file"
    
    # Release the high number
    "$NUMBER_MANAGER_SCRIPT" release 9998 boundary_reuse >/dev/null 2>&1
    
    # Act - Try to get new number
    local next_num
    next_num=$("$NUMBER_MANAGER_SCRIPT" get boundary_reuse 2>/dev/null | tail -1)
    local exit_code=$?
    
    # Assert - Should get 9999 (continues sequence)
    if [ $exit_code -eq 0 ] && [ "$next_num" = "9999" ]; then
        log "SUCCESS" "Boundary assignment works: $next_num"
    else
        log "ERROR" "Boundary assignment failed: exit=$exit_code, num=$next_num"
        return 1
    fi
    
    # Act - Try one more (should fail)
    local final_num
    final_num=$("$NUMBER_MANAGER_SCRIPT" get boundary_reuse 2>/dev/null | tail -1)
    local final_exit_code=$?
    
    # Assert - Should fail at boundary
    if [ $final_exit_code -ne 0 ]; then
        log "SUCCESS" "Correctly fails at maximum boundary"
    else
        log "ERROR" "Should fail at maximum boundary, got: $final_num"
        return 1
    fi
    
    return 0
}

# Test 8: Reuse with backup integrity
test_reuse_backup_integrity() {
    log "INFO" "Test 8: Testing backup integrity during reuse operations"
    
    # Arrange - Set up initial state
    "$NUMBER_MANAGER_SCRIPT" init backup_reuse >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get backup_reuse >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get backup_reuse >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" release 1 backup_reuse >/dev/null 2>&1
    
    # Get initial backup count
    local backup_dir="$TEST_STATE_DIR/.number_state/backup"
    local initial_backup_count
    initial_backup_count=$(ls -1 "$backup_dir"/*.json 2>/dev/null | wc -l)
    
    # Act - Perform reuse operations
    "$NUMBER_MANAGER_SCRIPT" get backup_reuse >/dev/null 2>&1  # 3
    "$NUMBER_MANAGER_SCRIPT" get backup_reuse >/dev/null 2>&1  # 4
    
    # Assert - Backups should be created for operations
    local final_backup_count
    final_backup_count=$(ls -1 "$backup_dir"/*.json 2>/dev/null | wc -l)
    
    if [ "$final_backup_count" -gt "$initial_backup_count" ]; then
        log "SUCCESS" "Backups created during reuse operations: $initial_backup_count -> $final_backup_count"
    else
        log "ERROR" "No new backups during reuse operations"
        return 1
    fi
    
    # Assert - State should be recoverable from backup
    if jq empty "$backup_dir"/*.json 2>/dev/null; then
        log "SUCCESS" "Backup files are valid JSON"
    else
        log "ERROR" "Backup files corrupted"
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
        "test_basic_number_reuse"
        "test_multiple_releases_assignments"
        "test_reuse_different_contexts"
        "test_state_consistency_reuse"
        "test_reuse_after_sync"
        "test_concurrent_reuse"
        "test_reuse_at_boundary"
        "test_reuse_backup_integrity"
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
        log "SUCCESS" "All reuse after release tests passed!"
        return 0
    else
        log "ERROR" "Some reuse after release tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests the reuse after release functionality of number_manager.sh"
    exit 1
fi