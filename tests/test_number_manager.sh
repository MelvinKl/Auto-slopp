#!/bin/bash

# Test script for number_manager.sh
# Validates basic functionality and edge cases

SCRIPT_NAME="test_number_manager"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_number_state_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

log "INFO" "Starting number manager tests in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Initialization
test_initialization() {
    log "INFO" "Test 1: Testing initialization"
    
    if "$NUMBER_MANAGER_SCRIPT" init test_context; then
        if [ -f "$TEST_STATE_DIR/.number_state/state.json" ]; then
            log "SUCCESS" "State file created successfully"
            
            # Validate JSON structure
            if jq empty "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null; then
                log "SUCCESS" "State file is valid JSON"
            else
                log "ERROR" "State file is not valid JSON"
                return 1
            fi
        else
            log "ERROR" "State file not created"
            return 1
        fi
    else
        log "ERROR" "Initialization failed"
        return 1
    fi
    
    return 0
}

# Test 2: Basic number assignment
test_basic_assignment() {
    log "INFO" "Test 2: Testing basic number assignment"
    
    # Get first number
    local num1
    num1=$("$NUMBER_MANAGER_SCRIPT" get test_context 2>/dev/null | tail -1)
    if [ $? -eq 0 ] && [ "$num1" = "1" ]; then
        log "SUCCESS" "First number assigned correctly: $num1"
    else
        log "ERROR" "First number assignment failed: got $num1"
        return 1
    fi
    
    # Get second number
    local num2
    num2=$("$NUMBER_MANAGER_SCRIPT" get test_context 2>/dev/null | tail -1)
    if [ $? -eq 0 ] && [ "$num2" = "2" ]; then
        log "SUCCESS" "Second number assigned correctly: $num2"
    else
        log "ERROR" "Second number assignment failed: got $num2"
        return 1
    fi
    
    # Test different context
    local num3
    num3=$("$NUMBER_MANAGER_SCRIPT" get other_context 2>/dev/null | tail -1)
    if [ $? -eq 0 ] && [ "$num3" = "3" ]; then
        log "SUCCESS" "Different context continues sequence: $num3"
    else
        log "ERROR" "Different context assignment failed: got $num3"
        return 1
    fi
    
    return 0
}

# Test 3: Stats and context tracking
test_stats_and_contexts() {
    log "INFO" "Test 3: Testing statistics and context tracking"
    
    # Get stats
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    if [ $? -eq 0 ]; then
        local used_count
        used_count=$(echo "$stats" | jq -r '.used_count')
        if [ "$used_count" = "3" ]; then
            log "SUCCESS" "Stats show correct used count: $used_count"
        else
            log "ERROR" "Stats show incorrect used count: $used_count"
            return 1
        fi
        
        local last_assigned
        last_assigned=$(echo "$stats" | jq -r '.last_assigned')
        if [ "$last_assigned" = "3" ]; then
            log "SUCCESS" "Stats show correct last assigned: $last_assigned"
        else
            log "ERROR" "Stats show incorrect last assigned: $last_assigned"
            return 1
        fi
    else
        log "ERROR" "Failed to get stats"
        return 1
    fi
    
    # Get contexts
    local contexts
    contexts=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    if [ $? -eq 0 ]; then
        local context_count
        context_count=$(echo "$contexts" | jq -r 'keys | length')
        if [ "$context_count" = "2" ]; then
            log "SUCCESS" "Correct number of contexts tracked: $context_count"
        else
            log "ERROR" "Incorrect context count: $context_count"
            return 1
        fi
    else
        log "ERROR" "Failed to get contexts"
        return 1
    fi
    
    return 0
}

# Test 4: Number release
test_number_release() {
    log "INFO" "Test 4: Testing number release"
    
    # Release number 2
    if "$NUMBER_MANAGER_SCRIPT" release 2 test_context; then
        log "SUCCESS" "Number 2 released successfully"
    else
        log "ERROR" "Failed to release number 2"
        return 1
    fi
    
    # Get next number (should still be 4, not 2)
    local next_num
    next_num=$("$NUMBER_MANAGER_SCRIPT" get test_context 2>/dev/null | tail -1)
    if [ $? -eq 0 ] && [ "$next_num" = "4" ]; then
        log "SUCCESS" "Next number assignment works after release: $next_num"
    else
        log "ERROR" "Next number assignment failed after release: got $next_num"
        return 1
    fi
    
    return 0
}

# Test 5: File synchronization
test_file_sync() {
    log "INFO" "Test 5: Testing file synchronization"
    
    # Create test task directory with numbered files
    local test_task_dir="$TEST_STATE_DIR/test_repo"
    mkdir -p "$test_task_dir"
    
    # Create some test files
    touch "$test_task_dir/0001-task1.txt"
    touch "$test_task_dir/0003-task2.txt"
    touch "$test_task_dir/0005-task3.txt"
    
    # Sync state with files
    if "$NUMBER_MANAGER_SCRIPT" sync "$test_task_dir" test_repo; then
        log "SUCCESS" "File synchronization completed"
        
        # Check if state was updated correctly
        local stats
        stats=$("$NUMBER_MANAGER_SCRIPT" stats)
        local last_assigned
        last_assigned=$(echo "$stats" | jq -r '.last_assigned')
        if [ "$last_assigned" = "5" ]; then
            log "SUCCESS" "State updated correctly after sync: $last_assigned"
        else
            log "ERROR" "State not updated correctly after sync: $last_assigned"
            return 1
        fi
    else
        log "ERROR" "File synchronization failed"
        return 1
    fi
    
    # Test validation
    if "$NUMBER_MANAGER_SCRIPT" validate "$test_task_dir" test_repo; then
        log "SUCCESS" "Validation passed"
    else
        log "ERROR" "Validation failed"
        return 1
    fi
    
    return 0
}

# Test 6: Error handling
test_error_handling() {
    log "INFO" "Test 6: Testing error handling"
    
    # Test invalid release
    if "$NUMBER_MANAGER_SCRIPT" release -1 test_context; then
        log "ERROR" "Should have failed to release invalid number"
        return 1
    else
        log "SUCCESS" "Correctly rejected invalid number release"
    fi
    
    # Test too-large number release
    if "$NUMBER_MANAGER_SCRIPT" release 10000 test_context; then
        log "ERROR" "Should have failed to release too-large number"
        return 1
    else
        log "SUCCESS" "Correctly rejected too-large number release"
    fi
    
    # Test operation without initialization
    rm -rf "$TEST_STATE_DIR/.number_state"
    if "$NUMBER_MANAGER_SCRIPT" get test_context 2>/dev/null; then
        log "ERROR" "Should have failed without initialization"
        return 1
    else
        log "SUCCESS" "Correctly failed without initialization"
    fi
    
    # Re-initialize for other tests
    "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get test_context >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get test_context >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get test_context >/dev/null 2>&1
    
    return 0
}

# Test 7: Gap detection
test_gap_detection() {
    log "INFO" "Test 7: Testing gap detection"
    
    # Create a scenario with gaps
    rm -rf "$TEST_STATE_DIR/.number_state"
    "$NUMBER_MANAGER_SCRIPT" init gap_test >/dev/null
    
    # Assign some numbers
    "$NUMBER_MANAGER_SCRIPT" get gap_test >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get gap_test >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" get gap_test >/dev/null 2>&1  # 3
    
    # Release number 2 to create a gap
    "$NUMBER_MANAGER_SCRIPT" release 2 gap_test >/dev/null 2>&1
    
    # Get next number (should be 4)
    "$NUMBER_MANAGER_SCRIPT" get gap_test >/dev/null 2>&1  # 4
    
    # Check for gaps
    local gaps
    gaps=$("$NUMBER_MANAGER_SCRIPT" gaps gap_test)
    if echo "$gaps" | grep -q "Gap: number 2 is not used"; then
        log "SUCCESS" "Gap detection working correctly"
    else
        log "ERROR" "Gap detection failed: $gaps"
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
        "test_initialization"
        "test_basic_assignment"
        "test_stats_and_contexts"
        "test_number_release"
        "test_file_sync"
        "test_error_handling"
        "test_gap_detection"
    )
    
    for test_func in "${tests[@]}"; do
        test_count=$((test_count + 1))
        echo ""
        echo "=========================================="
        echo "Running $test_func"
        echo "=========================================="
        
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
        log "SUCCESS" "All tests passed!"
        return 0
    else
        log "ERROR" "Some tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests the number_manager.sh functionality"
    exit 1
fi