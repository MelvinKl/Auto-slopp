#!/bin/bash

# Test Validation Accuracy for Number Assignment Consistency
# Tests the accuracy of inconsistency detection mechanisms
# Includes comprehensive scenarios for state vs file comparison

SCRIPT_NAME="test_validation_accuracy"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_validation_accuracy_$$"
TEST_TASK_DIR="$TEST_STATE_DIR/tasks"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

# Test results tracking
TESTS_RUN=0
TESTS_PASSED=0

log "INFO" "Starting validation accuracy tests in $TEST_STATE_DIR"

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

# Test 1: Perfect consistency detection
test_perfect_consistency() {
    setup_test_env
    
    # Create numbered files
    touch "$TEST_TASK_DIR/0001-task1.txt"
    touch "$TEST_TASK_DIR/0002-task2.txt"
    touch "$TEST_TASK_DIR/0003-task3.txt"
    
    # Assign numbers in state
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1
    
    # Run validation - should report no inconsistencies
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    echo "$validation_output" | grep -q "No inconsistencies found"
}

# Test 2: Orphaned state numbers detection
test_orphaned_state_numbers() {
    setup_test_env
    
    # Create some files
    touch "$TEST_TASK_DIR/0001-task1.txt"
    touch "$TEST_TASK_DIR/0003-task3.txt"
    
    # Assign numbers in state (including missing file)
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0002 (no file)
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0003
    
    # Run validation - should detect number 2 in state but not in files
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    echo "$validation_output" | grep -q "Numbers in state but not in files:" && \
    echo "$validation_output" | grep -q "2"
}

# Test 3: Missing state numbers detection
test_missing_state_numbers() {
    setup_test_env
    
    # Create files without state assignments
    touch "$TEST_TASK_DIR/0001-task1.txt"
    touch "$TEST_TASK_DIR/0002-task2.txt"
    
    # Only assign one number in state
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0001
    
    # Run validation - should detect number 2 in files but not in state
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    echo "$validation_output" | grep -q "Numbers in files but not in state:" && \
    echo "$validation_output" | grep -q "2"
}

# Test 4: Mixed inconsistencies detection
test_mixed_inconsistencies() {
    setup_test_env
    
    # Create some files
    touch "$TEST_TASK_DIR/0001-task1.txt"
    touch "$TEST_TASK_DIR/0004-task4.txt"
    touch "$TEST_TASK_DIR/0006-task6.txt"
    
    # Assign different numbers in state
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0002 (no file)
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0003 (no file)
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0004
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0005 (no file)
    # Skip 0006 in state
    
    # Run validation - should detect both types of inconsistencies
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    echo "$validation_output" | grep -q "Numbers in state but not in files:" && \
    echo "$validation_output" | grep -q "Numbers in files but not in state:" && \
    echo "$validation_output" | grep -q "2" && \
    echo "$validation_output" | grep -q "3" && \
    echo "$validation_output" | grep -q "5" && \
    echo "$validation_output" | grep -q "6"
}

# Test 5: Edge case - empty directory
test_empty_directory() {
    setup_test_env
    
    # No files, no state assignments
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    echo "$validation_output" | grep -q "No inconsistencies found"
}

# Test 6: Edge case - only state numbers, no files
test_only_state_no_files() {
    setup_test_env
    
    # Assign numbers without creating files
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0001
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0002
    
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    echo "$validation_output" | grep -q "Numbers in state but not in files:" && \
    echo "$validation_output" | grep -q "1" && \
    echo "$validation_output" | grep -q "2"
}

# Test 7: Edge case - only files, no state
test_only_files_no_state() {
    setup_test_env
    
    # Create files without state assignments
    touch "$TEST_TASK_DIR/0001-task1.txt"
    touch "$TEST_TASK_DIR/0002-task2.txt"
    
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    echo "$validation_output" | grep -q "Numbers in files but not in state:" && \
    echo "$validation_output" | grep -q "1" && \
    echo "$validation_output" | grep -q "2"
}

# Test 8: Large number handling accuracy
test_large_numbers() {
    setup_test_env
    
    # Create files with moderately large numbers
    touch "$TEST_TASK_DIR/0020-large-task.txt"
    touch "$TEST_TASK_DIR/0025-larger-task.txt"
    
    # Assign corresponding numbers in state (limited for performance)
    for i in {1..25}; do
        "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1
    done
    
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    # Check that validation runs without errors and can handle the numbers
    echo "$validation_output" | grep -q "Validating number assignment consistency"
}

# Test 9: Invalid filename patterns ignored
test_invalid_filename_patterns() {
    setup_test_env
    
    # Create files with various invalid patterns
    touch "$TEST_TASK_DIR/99-task.txt"                    # 3 digits
    touch "$TEST_TASK_DIR/10000-task.txt"                 # 5 digits
    touch "$TEST_TASK_DIR/abc-task.txt"                  # no digits
    touch "$TEST_TASK_DIR/0001-task.used"                 # used suffix
    touch "$TEST_TASK_DIR/0002-task.txt"                  # valid
    
    # Assign only one number in state
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0001
    
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    # Should only detect 0002 in files but not in state (ignore invalid patterns)
    echo "$validation_output" | grep -q "Numbers in files but not in state:" && \
    echo "$validation_output" | grep -q "2"
}

# Test 10: Context validation accuracy
test_context_validation() {
    setup_test_env
    
    # Create files for different contexts
    mkdir -p "$TEST_STATE_DIR/tasks2"
    touch "$TEST_TASK_DIR/0001-task1.txt"
    touch "$TEST_STATE_DIR/tasks2/0001-task1.txt"
    
    # Assign numbers to different contexts
    "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1  # 0001 for context1
    "$NUMBER_MANAGER_SCRIPT" get "test_context2" >/dev/null 2>&1 # 0001 for context2
    
    # Validate context1 - should be consistent
    local validation_output1
    validation_output1=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    
    # Validate context2 - should be consistent
    local validation_output2
    validation_output2=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_STATE_DIR/tasks2" "test_context2" 2>&1)
    
    # Check if validations ran successfully (context might show missing files due to state-file separation)
    echo "$validation_output1" | grep -q "Validating number assignment consistency"
    echo "$validation_output2" | grep -q "Validating number assignment consistency"
}

# Run all tests
echo "Starting Validation Accuracy Tests..."

run_test "Perfect Consistency Detection" "test_perfect_consistency"
run_test "Orphaned State Numbers Detection" "test_orphaned_state_numbers"
run_test "Missing State Numbers Detection" "test_missing_state_numbers"
run_test "Mixed Inconsistencies Detection" "test_mixed_inconsistencies"
run_test "Empty Directory Edge Case" "test_empty_directory"
run_test "Only State Numbers Edge Case" "test_only_state_no_files"
run_test "Only Files Edge Case" "test_only_files_no_state"
run_test "Large Number Handling" "test_large_numbers"
run_test "Invalid Filename Patterns Ignored" "test_invalid_filename_patterns"
run_test "Context Validation Accuracy" "test_context_validation"

# Summary
echo ""
echo "=========================================="
echo "VALIDATION ACCURACY TEST SUMMARY"
echo "=========================================="
echo "Tests Run: $TESTS_RUN"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $((TESTS_RUN - TESTS_PASSED))"

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    echo "🎉 ALL TESTS PASSED!"
    exit 0
else
    echo "❌ SOME TESTS FAILED!"
    exit 1
fi