#!/bin/bash

# Test Validation Reporting Mechanisms
# Tests the clarity, accuracy, and actionability of validation reports
# Includes error categorization and repair suggestion testing

SCRIPT_NAME="test_validation_reporting"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_validation_reporting_$$"
TEST_TASK_DIR="$TEST_STATE_DIR/tasks"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

# Test results tracking
TESTS_RUN=0
TESTS_PASSED=0

log "INFO" "Starting validation reporting tests in $TEST_STATE_DIR"

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

# Setup test environment
setup_test_env() {
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$TEST_TASK_DIR"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init "test_context" >/dev/null 2>&1
    
    echo "Test environment setup completed"
}

# Test 1: Clear reporting format
test_clear_reporting_format() {
    setup_test_env
    
    # Create inconsistent state
    touch "$TEST_TASK_DIR/0001-task1.txt"
    touch "$TEST_TASK_DIR/0003-task3.txt"
    
    # Assign different numbers in state
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0002 (no file)
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0003
    
    # Run validation and capture output
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    # Check for clear section headers
    echo "$validation_output" | grep -q "Validating number assignment consistency"
    echo "$validation_output" | grep -q "Numbers in state but not in files:"
    echo "$validation_output" | grep -q "Numbers in files but not in state:"
    
    # Check for proper indentation
    echo "$validation_output" | grep -q "  2"
}

# Test 2: Error categorization
test_error_categorization() {
    setup_test_env
    
    # Create complex inconsistent scenario
    touch "$TEST_TASK_DIR/0001-file1.txt"
    touch "$TEST_TASK_DIR/0005-file5.txt"
    touch "$TEST_TASK_DIR/0008-file8.txt"
    
    # Create mixed state assignments
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0002 (orphaned)
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0003 (orphaned)
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0004 (orphaned)
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0005
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0006 (orphaned)
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0007 (orphaned)
    # Skip 0008 in state (missing)
    
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    # Check that different error types are properly categorized
    local orphaned_count
    local missing_count
    
    orphaned_count=$(echo "$validation_output" | sed -n '/Numbers in state but not in files:/,/Numbers in files but not in state:/p' | grep -c "  [0-9]")
    missing_count=$(echo "$validation_output" | sed -n '/Numbers in files but not in state:/,/Inconsistencies found/p' | grep -c "  [0-9]")
    
    # Should have 4 orphaned (2,3,4,6,7) and 1 missing (8)
    [ $orphaned_count -eq 5 ] && [ $missing_count -eq 1 ]
}

# Test 3: Actionable recommendations
test_actionable_recommendations() {
    setup_test_env
    
    # Create inconsistent state
    touch "$TEST_TASK_DIR/0001-task1.txt"
    
    # Assign number without creating file
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0002 (no file)
    
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    # Check for actionable recommendations
    echo "$validation_output" | grep -qi "consider running sync_state_with_files"
    echo "$validation_output" | grep -qi "inconsistencies found"
}

# Test 4: Statistics reporting accuracy
test_statistics_accuracy() {
    setup_test_env
    
    # Create scenario with known counts
    touch "$TEST_TASK_DIR/0001-file1.txt"
    touch "$TEST_TASK_DIR/0003-file3.txt"
    touch "$TEST_TASK_DIR/0004-file4.txt"
    
    # Assign known numbers
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0002 (orphaned)
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0003
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0004
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0005 (orphaned)
    
    # Get detailed stats from number manager
    local stats_output
    stats_output=$("$NUMBER_MANAGER_SCRIPT" stats 2>&1)
    
    # Extract counts from stats
    local used_numbers_count
    used_numbers_count=$(echo "$stats_output" | jq -r '.used_numbers_count // 0')
    
    # Should have 5 numbers assigned in state
    [ "$used_numbers_count" = "5" ]
}

# Test 5: Context-specific reporting
test_context_specific_reporting() {
    setup_test_env
    
    # Create files for different contexts
    mkdir -p "$TEST_STATE_DIR/tasks2"
    touch "$TEST_TASK_DIR/0001-context1-task.txt"
    touch "$TEST_STATE_DIR/tasks2/0001-context2-task.txt"
    
    # Assign to different contexts
    "$NUMBER_MANAGER_SCRIPT" get "context1" >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get "context2" >/dev/null 2>&1
    
    # Get context assignments
    local contexts_output
    contexts_output=$("$NUMBER_MANAGER_SCRIPT" contexts 2>&1)
    
    # Check that context assignments are properly reported
    echo "$contexts_output" | jq -e '.context1' >/dev/null
    echo "$contexts_output" | jq -e '.context2' >/dev/null
}

# Test 6: Detailed gap reporting
test_gap_reporting() {
    setup_test_env
    
    # Create files with gaps
    touch "$TEST_TASK_DIR/0001-file1.txt"
    touch "$TEST_TASK_DIR/0005-file5.txt"
    touch "$TEST_TASK_DIR/0010-file10.txt"
    
    # Assign numbers for existing files
    for i in {1..10}; do
        "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1
    done
    
    # Check gap reporting
    local gaps_output
    gaps_output=$("$NUMBER_MANAGER_SCRIPT" gaps "test_context" 2>&1)
    
    # Should report gaps for numbers 2,3,4,6,7,8,9
    local gap_count
    gap_count=$(echo "$gaps_output" | grep -c "Gap found")
    
    [ $gap_count -eq 7 ]
}

# Test 7: Error message clarity
test_error_message_clarity() {
    setup_test_env
    
    # Test with non-existent directory
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "/nonexistent/directory" "test_context" 2>&1)
    
    # Should have clear error message
    echo "$validation_output" | grep -q "Error:"
    echo "$validation_output" | grep -q "not found"
    
    # Test with no state file
    rm -rf "$NUMBER_STATE_DIR"
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    echo "$validation_output" | grep -q "Error:"
    echo "$validation_output" | grep -q "State file not found"
}

# Test 8: Multi-context reporting
test_multi_context_reporting() {
    setup_test_env
    
    # Create multiple task directories
    mkdir -p "$TEST_STATE_DIR/repo1_tasks"
    mkdir -p "$TEST_STATE_DIR/repo2_tasks"
    
    # Create inconsistent scenarios in both contexts
    touch "$TEST_STATE_DIR/repo1_tasks/0001-task1.txt"
    touch "$TEST_STATE_DIR/repo2_tasks/0002-task2.txt"
    
    # Assign to different contexts
    "$NUMBER_MANAGER_SCRIPT" get "repo1" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "repo2" >/dev/null 2>&1  # 0002
    
    # Validate each context separately
    local repo1_output
    local repo2_output
    
    repo1_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_STATE_DIR/repo1_tasks" "repo1" 2>&1)
    repo2_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_STATE_DIR/repo2_tasks" "repo2" 2>&1)
    
    # Both should be consistent within their own contexts
    echo "$repo1_output" | grep -q "No inconsistencies found"
    echo "$repo2_output" | grep -q "No inconsistencies found"
}

# Test 9: Progress reporting during validation
test_progress_reporting() {
    setup_test_env
    
    # Create a larger dataset to potentially see progress
    for i in {1..50}; do
        local num=$(printf "%04d" $i)
        touch "$TEST_TASK_DIR/${num}-task${i}.txt"
    done
    
    # Assign numbers in state
    for i in {1..40}; do
        "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1
    done
    
    # Run validation with output capture
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    # Output should contain context information
    echo "$validation_output" | grep -q "Validating number assignment consistency"
    
    # Should detect missing numbers (41-50)
    echo "$validation_output" | grep -q "Numbers in files but not in state:"
}

# Test 10: Summary information reporting
test_summary_reporting() {
    setup_test_env
    
    # Create consistent scenario
    touch "$TEST_TASK_DIR/0001-task1.txt"
    touch "$TEST_TASK_DIR/0002-task2.txt"
    
    # Assign numbers
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1
    
    # Get stats
    local stats_output
    stats_output=$("$NUMBER_MANAGER_SCRIPT" stats 2>&1)
    
    # Check for summary fields
    echo "$stats_output" | jq -e '.used_numbers_count' >/dev/null
    echo "$stats_output" | jq -e '.last_assigned' >/dev/null
    echo "$stats_output" | jq -e '.total_assignments' >/dev/null
    echo "$stats_output" | jq -e '.context_assignments' >/dev/null
}

# Run all tests
echo "Starting Validation Reporting Tests..."

run_test "Clear Reporting Format" "test_clear_reporting_format"
run_test "Error Categorization" "test_error_categorization"
run_test "Actionable Recommendations" "test_actionable_recommendations"
run_test "Statistics Accuracy" "test_statistics_accuracy"
run_test "Context-Specific Reporting" "test_context_specific_reporting"
run_test "Gap Reporting" "test_gap_reporting"
run_test "Error Message Clarity" "test_error_message_clarity"
run_test "Multi-Context Reporting" "test_multi_context_reporting"
run_test "Progress Reporting" "test_progress_reporting"
run_test "Summary Information Reporting" "test_summary_reporting"

# Summary
echo ""
echo "=========================================="
echo "VALIDATION REPORTING TEST SUMMARY"
echo "=========================================="
echo "Tests Run: $TESTS_RUN"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $((TESTS_RUN - TESTS_PASSED))"

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    echo "🎉 ALL REPORTING TESTS PASSED!"
    exit 0
else
    echo "❌ SOME REPORTING TESTS FAILED!"
    exit 1
fi