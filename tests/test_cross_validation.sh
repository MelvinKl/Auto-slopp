#!/bin/bash

# Test Cross-Repository Consistency Validation
# Tests validation across multiple repositories and contexts
# Ensures no cross-repo number conflicts and proper isolation

SCRIPT_NAME="test_cross_validation"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_cross_validation_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

# Create multiple repository directories
REPO1_TASKS="$TEST_STATE_DIR/repo1_tasks"
REPO2_TASKS="$TEST_STATE_DIR/repo2_tasks"
REPO3_TASKS="$TEST_STATE_DIR/repo3_tasks"

# Test results tracking
TESTS_RUN=0
TESTS_PASSED=0

log "INFO" "Starting cross-repository validation tests in $TEST_STATE_DIR"

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

# Setup multi-repository test environment
setup_multi_repo_env() {
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$REPO1_TASKS" "$REPO2_TASKS" "$REPO3_TASKS"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init >/dev/null 2>&1
    
    echo "Multi-repository test environment setup completed"
}

# Test 1: Independent number assignment across repositories
test_independent_number_assignment() {
    setup_multi_repo_env
    
    # Create tasks in different repositories
    touch "$REPO1_TASKS/0001-repo1-task.txt"
    touch "$REPO2_TASKS/0001-repo2-task.txt"
    touch "$REPO3_TASKS/0001-repo3-task.txt"
    
    # Assign numbers in different contexts
    "$NUMBER_MANAGER_SCRIPT" get "repo1" >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get "repo3" >/dev/null 2>&1
    
    # Validate each repository independently
    local repo1_output
    local repo2_output
    local repo3_output
    
    repo1_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO1_TASKS" "repo1" 2>&1)
    repo2_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO2_TASKS" "repo2" 2>&1)
    repo3_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO3_TASKS" "repo3" 2>&1)
    
    # All should be consistent within their contexts
    echo "$repo1_output" | grep -q "No inconsistencies found"
    echo "$repo2_output" | grep -q "No inconsistencies found"
    echo "$repo3_output" | grep -q "No inconsistencies found"
}

# Test 2: Context isolation validation
test_context_isolation() {
    setup_multi_repo_env
    
    # Create different scenarios in each repository
    touch "$REPO1_TASKS/0001-task1.txt"
    touch "$REPO1_TASKS/0003-task3.txt"  # Gap at 0002
    
    touch "$REPO2_TASKS/0005-task5.txt"
    touch "$REPO2_TASKS/0007-task7.txt"  # Gap at 0006
    
    touch "$REPO3_TASKS/0010-task10.txt"
    
    # Assign numbers with different patterns
    "$NUMBER_MANAGER_SCRIPT" get "repo1" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "repo1" >/dev/null 2>&1  # 0002 (no file)
    "$NUMBER_MANAGER_SCRIPT" get "repo1" >/dev/null 2>&1  # 0003
    
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0002
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0003
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0004
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0005
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0006 (no file)
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0007
    
    "$NUMBER_MANAGER_SCRIPT" get "repo3" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "repo3" >/dev/null 2>&1  # 0002
    "$NUMBER_MANAGER_SCRIPT" get "repo3" >/dev/null 2>&1  # 0003
    "$NUMBER_MANAGER_SCRIPT" get "repo3" >/dev/null 2>&1  # 0004
    "$NUMBER_MANAGER_SCRIPT" get "repo3" >/dev/null 2>&1  # 0005
    "$NUMBER_MANAGER_SCRIPT" get "repo3" >/dev/null 2>&1  # 0006
    "$NUMBER_MANAGER_SCRIPT" get "repo3" >/dev/null 2>&1  # 0007
    "$NUMBER_MANAGER_SCRIPT" get "repo3" >/dev/null 2>&1  # 0008
    "$NUMBER_MANAGER_SCRIPT" get "repo3" >/dev/null 2>&1  # 0009
    "$NUMBER_MANAGER_SCRIPT" get "repo3" >/dev/null 2>&1  # 0010
    
    # Validate each repository
    local repo1_output
    local repo2_output
    local repo3_output
    
    repo1_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO1_TASKS" "repo1" 2>&1)
    repo2_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO2_TASKS" "repo2" 2>&1)
    repo3_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO3_TASKS" "repo3" 2>&1)
    
    # Repo1 should have inconsistency (0002 in state only)
    echo "$repo1_output" | grep -q "Numbers in state but not in files:"
    echo "$repo1_output" | grep -q "2"
    
    # Repo2 should have inconsistency (0006 in state only)
    echo "$repo2_output" | grep -q "Numbers in state but not in files:"
    echo "$repo2_output" | grep -q "6"
    
    # Repo3 should be consistent
    echo "$repo3_output" | grep -q "No inconsistencies found"
}

# Test 3: Cross-repo conflict detection
test_cross_repo_conflict_detection() {
    setup_multi_repo_env
    
    # Create files with same numbers across repos (should be allowed)
    touch "$REPO1_TASKS/0001-shared-task.txt"
    touch "$REPO2_TASKS/0001-shared-task.txt"
    touch "$REPO3_TASKS/0001-shared-task.txt"
    
    # Assign same numbers in different contexts
    "$NUMBER_MANAGER_SCRIPT" get "shared_context" >/dev/null 2>&1
    
    # Verify that contexts are tracked separately
    local contexts_output
    contexts_output=$("$NUMBER_MANAGER_SCRIPT" contexts 2>&1)
    
    # Should show context assignments
    echo "$contexts_output" | jq -e '.shared_context' >/dev/null
    
    # Validation should work for each repository independently
    local repo1_output
    repo1_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO1_TASKS" "shared_context" 2>&1)
    
    echo "$repo1_output" | grep -q "No inconsistencies found"
}

# Test 4: Large-scale cross-repo validation
test_large_scale_cross_repo() {
    setup_multi_repo_env
    
    # Create many files across multiple repositories
    for repo in "$REPO1_TASKS" "$REPO2_TASKS" "$REPO3_TASKS"; do
        for i in {1..100}; do
            local num=$(printf "%04d" $i)
            touch "$repo/${num}-task-${repo##*/}-${i}.txt"
        done
    done
    
    # Assign numbers for each repository context
    for context in repo1 repo2 repo3; do
        for i in {1..100}; do
            "$NUMBER_MANAGER_SCRIPT" get "$context" >/dev/null 2>&1
        done
    done
    
    # Validate all repositories
    local repo1_output
    local repo2_output
    local repo3_output
    
    repo1_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO1_TASKS" "repo1" 2>&1)
    repo2_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO2_TASKS" "repo2" 2>&1)
    repo3_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO3_TASKS" "repo3" 2>&1)
    
    # All should be consistent
    echo "$repo1_output" | grep -q "No inconsistencies found"
    echo "$repo2_output" | grep -q "No inconsistencies found"
    echo "$repo3_output" | grep -q "No inconsistencies found"
}

# Test 5: Cross-repo gap analysis
test_cross_repo_gap_analysis() {
    setup_multi_repo_env
    
    # Create files with gaps in different patterns
    # Repo1: gaps at 0002, 0005
    touch "$REPO1_TASKS/0001-task1.txt"
    touch "$REPO1_TASKS/0003-task3.txt"
    touch "$REPO1_TASKS/0004-task4.txt"
    touch "$REPO1_TASKS/0006-task6.txt"
    
    # Repo2: gaps at 0003, 0007
    touch "$REPO2_TASKS/0001-task1.txt"
    touch "$REPO2_TASKS/0002-task2.txt"
    touch "$REPO2_TASKS/0004-task4.txt"
    touch "$REPO2_TASKS/0005-task5.txt"
    touch "$REPO2_TASKS/0006-task6.txt"
    touch "$REPO2_TASKS/0008-task8.txt"
    
    # Repo3: no gaps
    touch "$REPO3_TASKS/0001-task1.txt"
    touch "$REPO3_TASKS/0002-task2.txt"
    touch "$REPO3_TASKS/0003-task3.txt"
    
    # Assign numbers for each context
    for i in {1..6}; do
        "$NUMBER_MANAGER_SCRIPT" get "repo1" >/dev/null 2>&1
    done
    
    for i in {1..8}; do
        "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1
    done
    
    for i in {1..3}; do
        "$NUMBER_MANAGER_SCRIPT" get "repo3" >/dev/null 2>&1
    done
    
    # Check gaps for each repository
    local repo1_gaps
    local repo2_gaps
    local repo3_gaps
    
    repo1_gaps=$("$NUMBER_MANAGER_SCRIPT" gaps "repo1" 2>&1)
    repo2_gaps=$("$NUMBER_MANAGER_SCRIPT" gaps "repo2" 2>&1)
    repo3_gaps=$("$NUMBER_MANAGER_SCRIPT" gaps "repo3" 2>&1)
    
    # Repo1 should have gaps at 2, 5
    echo "$repo1_gaps" | grep -q "Gap found: 2"
    echo "$repo1_gaps" | grep -q "Gap found: 5"
    
    # Repo2 should have gaps at 3, 7
    echo "$repo2_gaps" | grep -q "Gap found: 3"
    echo "$repo2_gaps" | grep -q "Gap found: 7"
    
    # Repo3 should have no gaps
    ! echo "$repo3_gaps" | grep -q "Gap found"
}

# Test 6: Context isolation during concurrent operations
test_concurrent_context_isolation() {
    setup_multi_repo_env
    
    # Create initial files
    touch "$REPO1_TASKS/0001-task1.txt"
    touch "$REPO2_TASKS/0001-task1.txt"
    
    # Start background processes for different contexts
    (
        "$NUMBER_MANAGER_SCRIPT" get "concurrent1" >/dev/null 2>&1
        sleep 0.1
        "$NUMBER_MANAGER_SCRIPT" get "concurrent1" >/dev/null 2>&1
    ) &
    
    (
        "$NUMBER_MANAGER_SCRIPT" get "concurrent2" >/dev/null 2>&1
        sleep 0.1
        "$NUMBER_MANAGER_SCRIPT" get "concurrent2" >/dev/null 2>&1
    ) &
    
    (
        "$NUMBER_MANAGER_SCRIPT" get "concurrent3" >/dev/null 2>&1
        sleep 0.1
        "$NUMBER_MANAGER_SCRIPT" get "concurrent3" >/dev/null 2>&1
    ) &
    
    wait  # Wait for all background processes
    
    # Check context assignments
    local contexts_output
    contexts_output=$("$NUMBER_MANAGER_SCRIPT" contexts 2>&1)
    
    # Should have separate assignments for each context
    echo "$contexts_output" | jq -e '.concurrent1' >/dev/null
    echo "$contexts_output" | jq -e '.concurrent2' >/dev/null
    echo "$contexts_output" | jq -e '.concurrent3' >/dev/null
}

# Test 7: Cross-repo state consistency
test_cross_repo_state_consistency() {
    setup_multi_repo_env
    
    # Create complex scenario across repositories
    touch "$REPO1_TASKS/0001-task1.txt"
    touch "$REPO1_TASKS/0002-task2.txt"
    
    touch "$REPO2_TASKS/0005-task5.txt"
    touch "$REPO2_TASKS/0006-task6.txt"
    
    touch "$REPO3_TASKS/0010-task10.txt"
    
    # Mix assignments across contexts
    "$NUMBER_MANAGER_SCRIPT" get "repo1" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "repo1" >/dev/null 2>&1  # 0002
    "$NUMBER_MANAGER_SCRIPT" get "repo1" >/dev/null 2>&1  # 0003 (no file)
    
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0002
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0003
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0004
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0005
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0006
    
    "$NUMBER_MANAGER_SCRIPT" get "repo3" >/dev/null 2>&1  # 0001 through 0010
    
    # Get overall stats
    local stats_output
    stats_output=$("$NUMBER_MANAGER_SCRIPT" stats 2>&1)
    
    # Should track total assignments across all contexts
    local total_assignments
    total_assignments=$(echo "$stats_output" | jq -r '.total_assignments // 0')
    
    # Should have 3 (repo1) + 6 (repo2) + 10 (repo3) = 19 total assignments
    [ "$total_assignments" = "19" ]
}

# Test 8: Repository-specific validation with mixed contexts
test_mixed_context_validation() {
    setup_multi_repo_env
    
    # Create files across repositories
    touch "$REPO1_TASKS/0001-mixed-task.txt"
    touch "$REPO2_TASKS/0001-mixed-task.txt"
    touch "$REPO3_TASKS/0001-mixed-task.txt"
    
    # Use same context name across repositories (should be isolated by file path)
    "$NUMBER_MANAGER_SCRIPT" get "mixed" >/dev/null 2>&1
    
    # Validate with explicit context names
    local repo1_output
    local repo2_output
    local repo3_output
    
    repo1_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO1_TASKS" "mixed" 2>&1)
    repo2_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO2_TASKS" "mixed" 2>&1)
    repo3_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO3_TASKS" "mixed" 2>&1)
    
    # All should show files exist but state assignments might be distributed
    # This tests how the system handles same context names in different directories
    echo "$repo1_output" | grep -q "Validating number assignment consistency"
    echo "$repo2_output" | grep -q "Validating number assignment consistency"
    echo "$repo3_output" | grep -q "Validating number assignment consistency"
}

# Test 9: Cross-repo error handling
test_cross_repo_error_handling() {
    setup_multi_repo_env
    
    # Test validation with missing directory
    local missing_dir_output
    missing_dir_output=$("$NUMBER_MANAGER_SCRIPT" validate "/nonexistent/repo" "test_context" 2>&1)
    
    echo "$missing_dir_output" | grep -q "Error:"
    echo "$missing_dir_output" | grep -q "not found"
    
    # Test with valid directory but no state file
    rm -rf "$TEST_STATE_DIR/.number_state"
    local no_state_output
    no_state_output=$("$NUMBER_MANAGER_SCRIPT" validate "$REPO1_TASKS" "test_context" 2>&1)
    
    echo "$no_state_output" | grep -q "Error:"
    echo "$no_state_output" | grep -q "State file not found"
}

# Test 10: Cross-repo performance impact
test_cross_repo_performance() {
    setup_multi_repo_env
    
    # Create medium-sized datasets across repositories
    for repo in "$REPO1_TASKS" "$REPO2_TASKS" "$REPO3_TASKS"; do
        for i in {1..500}; do
            local num=$(printf "%04d" $i)
            touch "$repo/${num}-task-${i}.txt"
        done
    done
    
    # Assign numbers for each context
    for context in repo1 repo2 repo3; do
        for i in {1..500}; do
            "$NUMBER_MANAGER_SCRIPT" get "$context" >/dev/null 2>&1
        done
    done
    
    # Measure validation time for all repositories
    local start_time=$(date +%s.%N)
    
    "$NUMBER_MANAGER_SCRIPT" validate "$REPO1_TASKS" "repo1" >/dev/null 2>&1 &
    "$NUMBER_MANAGER_SCRIPT" validate "$REPO2_TASKS" "repo2" >/dev/null 2>&1 &
    "$NUMBER_MANAGER_SCRIPT" validate "$REPO3_TASKS" "repo3" >/dev/null 2>&1 &
    
    wait
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)
    
    echo "Cross-repo validation completed in: $(printf "%.2f" $duration)s"
    
    # Should complete in reasonable time (less than 10 seconds for 1500 total files)
    local comparison=$(echo "$duration <= 10.0" | bc -l)
    [ "$comparison" = "1" ]
}

# Run all tests
echo "Starting Cross-Repository Validation Tests..."

run_test "Independent Number Assignment" "test_independent_number_assignment"
run_test "Context Isolation" "test_context_isolation"
run_test "Cross-Repo Conflict Detection" "test_cross_repo_conflict_detection"
run_test "Large-Scale Cross-Repo" "test_large_scale_cross_repo"
run_test "Cross-Repo Gap Analysis" "test_cross_repo_gap_analysis"
run_test "Concurrent Context Isolation" "test_concurrent_context_isolation"
run_test "Cross-Repo State Consistency" "test_cross_repo_state_consistency"
run_test "Mixed Context Validation" "test_mixed_context_validation"
run_test "Cross-Repo Error Handling" "test_cross_repo_error_handling"
run_test "Cross-Repo Performance" "test_cross_repo_performance"

# Summary
echo ""
echo "=========================================="
echo "CROSS-REPOSITORY VALIDATION TEST SUMMARY"
echo "=========================================="
echo "Tests Run: $TESTS_RUN"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $((TESTS_RUN - TESTS_PASSED))"

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    echo "🎉 ALL CROSS-REPO TESTS PASSED!"
    exit 0
else
    echo "❌ SOME CROSS-REPO TESTS FAILED!"
    exit 1
fi