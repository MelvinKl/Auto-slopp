#!/bin/bash

# Test Reuse After Release Functionality
# Tests reassignment of released numbers back to available pool

SCRIPT_NAME="test_reuse_after_release"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_gap_detection_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

log "INFO" "Starting gap detection tests in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Basic gap detection
test_basic_gap_detection() {
    log "INFO" "Test 1: Testing basic gap detection"
    
    # Arrange - Create scenario with gaps
    "$NUMBER_MANAGER_SCRIPT" init basic_gap >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get basic_gap >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get basic_gap >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" get basic_gap >/dev/null 2>&1  # 3
    "$NUMBER_MANAGER_SCRIPT" get basic_gap >/dev/null 2>&1  # 4
    
    # Release numbers 2 and 4 to create gaps
    "$NUMBER_MANAGER_SCRIPT" release 2 basic_gap >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" release 4 basic_gap >/dev/null 2>&1
    
    # Act - Check for gaps
    local gaps_output
    gaps_output=$("$NUMBER_MANAGER_SCRIPT" gaps basic_gap 2>/dev/null)
    
    # Assert - Verify gaps are detected
    local gap_count
    gap_count=$(echo "$gaps_output" | grep -c "Gap: number")
    
    if [ "$gap_count" = "2" ]; then
        log "SUCCESS" "Correct number of gaps detected: $gap_count"
    else
        log "ERROR" "Incorrect gap count: $gap_count"
        echo "Gap output: $gaps_output"
        return 1
    fi
    
    # Assert - Verify specific gaps
    if echo "$gaps_output" | grep -q "Gap: number 2 is not used" && \
       echo "$gaps_output" | grep -q "Gap: number 4 is not used"; then
        log "SUCCESS" "Specific gaps detected correctly"
    else
        log "ERROR" "Specific gaps not detected correctly"
        return 1
    fi
    
    return 0
}

# Test 2: No gaps scenario
test_no_gaps() {
    log "INFO" "Test 2: Testing scenario with no gaps"
    
    # Arrange - Create sequential assignment with no gaps
    "$NUMBER_MANAGER_SCRIPT" init no_gaps >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get no_gaps >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get no_gaps >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" get no_gaps >/dev/null 2>&1  # 3
    
    # Act - Check for gaps
    local gaps_output
    gaps_output=$("$NUMBER_MANAGER_SCRIPT" gaps no_gaps 2>/dev/null)
    
    # Assert - Should report no gaps
    if echo "$gaps_output" | grep -q "No gaps found"; then
        log "SUCCESS" "Correctly reported no gaps"
    else
        log "ERROR" "Failed to report no gaps scenario"
        echo "Output: $gaps_output"
        return 1
    fi
    
    return 0
}

# Test 3: Context-specific gap detection
test_context_specific_gaps() {
    log "INFO" "Test 3: Testing context-specific gap detection"
    
    # Arrange - Create multiple contexts with different gap patterns
    "$NUMBER_MANAGER_SCRIPT" init ctx_gap_test >/dev/null 2>&1
    
    # Context A: numbers 1, 3, 5 (gaps at 2, 4)
    "$NUMBER_MANAGER_SCRIPT" get context_a >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get context_a >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" get context_a >/dev/null 2>&1  # 3
    "$NUMBER_MANAGER_SCRIPT" release 2 context_a >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get context_a >/dev/null 2>&1  # 4
    "$NUMBER_MANAGER_SCRIPT" release 4 context_a >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get context_a >/dev/null 2>&1  # 5
    
    # Context B: numbers 1, 2, 4 (gap at 3)
    "$NUMBER_MANAGER_SCRIPT" get context_b >/dev/null 2>&1  # 6
    "$NUMBER_MANAGER_SCRIPT" release 6 context_b >/dev/null 2>&1  # Reset for B
    "$NUMBER_MANAGER_SCRIPT" get context_b >/dev/null 2>&1  # 6
    "$NUMBER_MANAGER_SCRIPT" get context_b >/dev/null 2>&1  # 7
    "$NUMBER_MANAGER_SCRIPT" get context_b >/dev/null 2>&1  # 8
    "$NUMBER_MANAGER_SCRIPT" release 7 context_b >/dev/null 2>&1
    
    # Act - Check gaps for context A
    local gaps_a
    gaps_a=$("$NUMBER_MANAGER_SCRIPT" gaps context_a 2>/dev/null)
    local gap_count_a
    gap_count_a=$(echo "$gaps_a" | grep -c "Gap: number")
    
    # Check gaps for context B (should be same since it's global state)
    local gaps_b
    gaps_b=$("$NUMBER_MANAGER_SCRIPT" gaps context_b 2>/dev/null)
    local gap_count_b
    gap_count_b=$(echo "$gaps_b" | grep -c "Gap: number")
    
    # Assert - Both should see the same global gaps
    if [ "$gap_count_a" = "$gap_count_b" ]; then
        log "SUCCESS" "Context filtering works consistently: A=$gap_count_a, B=$gap_count_b"
    else
        log "ERROR" "Context filtering inconsistent: A=$gap_count_a, B=$gap_count_b"
        return 1
    fi
    
    return 0
}

# Test 4: Large gaps detection
test_large_gaps() {
    log "INFO" "Test 4: Testing large gaps detection"
    
    # Arrange - Create scenario with large gap
    "$NUMBER_MANAGER_SCRIPT" init large_gap >/dev/null 2>&1
    
    # Assign first few numbers, then skip to create large gap
    "$NUMBER_MANAGER_SCRIPT" get large_gap >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get large_gap >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" get large_gap >/dev/null 2>&1  # 3
    
    # Manually manipulate state to create large gap scenario
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    # Set last_assigned to 100 but only use 1-3
    jq '.last_assigned = 100' "$state_file" > "${state_file}.tmp" && mv "${state_file}.tmp" "$state_file"
    
    # Act - Check for gaps
    local gaps_output
    gaps_output=$("$NUMBER_MANAGER_SCRIPT" gaps large_gap 2>/dev/null)
    
    # Assert - Should detect many gaps
    local gap_count
    gap_count=$(echo "$gaps_output" | grep -c "Gap: number")
    
    if [ "$gap_count" -gt 90 ]; then  # At least 90 gaps from 4-100
        log "SUCCESS" "Large number of gaps detected: $gap_count"
    else
        log "ERROR" "Insufficient gaps detected for large gap scenario: $gap_count"
        return 1
    fi
    
    # Assert - Should report specific large range
    if echo "$gaps_output" | grep -q "last assigned: 100"; then
        log "SUCCESS" "Large gap scenario reported correctly"
    else
        log "ERROR" "Large gap scenario not reported correctly"
        return 1
    fi
    
    return 0
}

# Test 5: Gap detection with file synchronization
test_gap_detection_with_sync() {
    log "INFO" "Test 5: Testing gap detection with file synchronization"
    
    # Arrange - Create files with gaps
    "$NUMBER_MANAGER_SCRIPT" init sync_gap >/dev/null 2>&1
    local test_task_dir="$TEST_STATE_DIR/test_repo_sync"
    mkdir -p "$test_task_dir"
    
    # Create files with gaps: 1, 3, 5, 7
    touch "$test_task_dir/0001-task1.txt"
    touch "$test_task_dir/0003-task2.txt"
    touch "$test_task_dir/0005-task3.txt"
    touch "$test_task_dir/0007-task4.txt"
    
    # Sync state with files
    "$NUMBER_MANAGER_SCRIPT" sync "$test_task_dir" sync_gap >/dev/null 2>&1
    
    # Act - Check for gaps
    local gaps_output
    gaps_output=$("$NUMBER_MANAGER_SCRIPT" gaps sync_gap 2>/dev/null)
    
    # Assert - Should detect gaps at 2, 4, 6
    local gap_count
    gap_count=$(echo "$gaps_output" | grep -c "Gap: number")
    
    if [ "$gap_count" = "3" ]; then
        log "SUCCESS" "Correct gap count after sync: $gap_count"
    else
        log "ERROR" "Incorrect gap count after sync: $gap_count"
        echo "Gap output: $gaps_output"
        return 1
    fi
    
    # Assert - Verify specific missing numbers
    for missing_num in 2 4 6; do
        if echo "$gaps_output" | grep -q "Gap: number $missing_num is not used"; then
            log "SUCCESS" "Gap $missing_num detected correctly"
        else
            log "ERROR" "Gap $missing_num not detected"
            return 1
        fi
    done
    
    return 0
}

# Test 6: Gap detection edge cases
test_gap_detection_edge_cases() {
    log "INFO" "Test 6: Testing gap detection edge cases"
    
    # Test empty state
    "$NUMBER_MANAGER_SCRIPT" init empty_gap >/dev/null 2>&1
    local gaps_empty
    gaps_empty=$("$NUMBER_MANAGER_SCRIPT" gaps empty_gap 2>/dev/null)
    
    if echo "$gaps_empty" | grep -q "No gaps found" || echo "$gaps_empty" | grep -q "last assigned: 0"; then
        log "SUCCESS" "Empty state handled correctly"
    else
        log "ERROR" "Empty state not handled correctly"
        return 1
    fi
    
    # Test single number assignment
    "$NUMBER_MANAGER_SCRIPT" get empty_gap >/dev/null 2>&1  # 1
    local gaps_single
    gaps_single=$("$NUMBER_MANAGER_SCRIPT" gaps empty_gap 2>/dev/null)
    
    if echo "$gaps_single" | grep -q "No gaps found"; then
        log "SUCCESS" "Single number assignment handled correctly"
    else
        log "ERROR" "Single number assignment not handled correctly"
        return 1
    fi
    
    # Test maximum number boundary
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    jq '.last_assigned = 9999 | .used_numbers = [9999]' "$state_file" > "${state_file}.tmp" && mv "${state_file}.tmp" "$state_file"
    local gaps_max
    gaps_max=$("$NUMBER_MANAGER_SCRIPT" gaps empty_gap 2>/dev/null)
    
    if echo "$gaps_max" | grep -q "last assigned: 9999"; then
        log "SUCCESS" "Maximum number boundary handled correctly"
    else
        log "ERROR" "Maximum number boundary not handled correctly"
        return 1
    fi
    
    return 0
}

# Test 7: Gap reporting format
test_gap_reporting_format() {
    log "INFO" "Test 7: Testing gap reporting format"
    
    # Arrange - Create predictable gap scenario
    "$NUMBER_MANAGER_SCRIPT" init format_test >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get format_test >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get format_test >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" get format_test >/dev/null 2>&1  # 3
    "$NUMBER_MANAGER_SCRIPT" release 2 format_test >/dev/null 2>&1
    
    # Act - Get gap report
    local gaps_output
    gaps_output=$("$NUMBER_MANAGER_SCRIPT" gaps format_test 2>/dev/null)
    
    # Assert - Check format requirements
    # Should contain header with last assigned
    if echo "$gaps_output" | grep -q "Checking for gaps.*last assigned:"; then
        log "SUCCESS" "Gap report header format correct"
    else
        log "ERROR" "Gap report header format incorrect"
        return 1
    fi
    
    # Should contain properly formatted gap lines
    if echo "$gaps_output" | grep -q "  Gap: number 2 is not used"; then
        log "SUCCESS" "Gap line format correct"
    else
        log "ERROR" "Gap line format incorrect"
        return 1
    fi
    
    # Should be indented properly
    local gap_lines
    gap_lines=$(echo "$gaps_output" | grep "Gap: number")
    while IFS= read -r line; do
        if [[ "$line" =~ ^[[:space:]]+Gap: ]]; then
            continue  # Properly indented
        else
            log "ERROR" "Gap line not properly indented: $line"
            return 1
        fi
    done <<< "$gap_lines"
    
    log "SUCCESS" "All gap lines properly indented"
    
    return 0
}

# Test 8: Gap detection performance
test_gap_detection_performance() {
    log "INFO" "Test 8: Testing gap detection performance"
    
    # Arrange - Create state with many numbers
    "$NUMBER_MANAGER_SCRIPT" init perf_test >/dev/null 2>&1
    
    # Create many assignments (simulate performance scenario)
    for i in {1..100}; do
        "$NUMBER_MANAGER_SCRIPT" get perf_test >/dev/null 2>&1
    done
    
    # Release every other number to create many gaps
    for ((i=2; i<=100; i+=2)); do
        "$NUMBER_MANAGER_SCRIPT" release "$i" perf_test >/dev/null 2>&1
    done
    
    # Act - Time the gap detection
    local start_time
    start_time=$(date +%s.%N)
    local gaps_output
    gaps_output=$("$NUMBER_MANAGER_SCRIPT" gaps perf_test 2>/dev/null)
    local end_time
    end_time=$(date +%s.%N)
    
    local duration
    duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "1")
    
    # Assert - Should complete in reasonable time (< 5 seconds)
    if (( $(echo "$duration < 5" | bc -l 2>/dev/null || echo "1") )); then
        log "SUCCESS" "Gap detection performance acceptable: ${duration}s"
    else
        log "ERROR" "Gap detection too slow: ${duration}s"
        return 1
    fi
    
    # Assert - Should detect correct number of gaps (50 gaps)
    local gap_count
    gap_count=$(echo "$gaps_output" | grep -c "Gap: number")
    if [ "$gap_count" = "50" ]; then
        log "SUCCESS" "Performance test correct gap count: $gap_count"
    else
        log "ERROR" "Performance test incorrect gap count: $gap_count"
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
        "test_basic_gap_detection"
        "test_no_gaps"
        "test_context_specific_gaps"
        "test_large_gaps"
        "test_gap_detection_with_sync"
        "test_gap_detection_edge_cases"
        "test_gap_reporting_format"
        "test_gap_detection_performance"
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
        log "SUCCESS" "All gap detection tests passed!"
        return 0
    else
        log "ERROR" "Some gap detection tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests the gap detection functionality of number_manager.sh"
    exit 1
fi