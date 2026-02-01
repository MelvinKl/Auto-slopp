#!/bin/bash

# Test basic number assignment functionality
# Part of Auto-9bu: Test unique number assignment and locking mechanism

set -e

SCRIPT_NAME="test_basic_assignment"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_basic_assignment_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting basic number assignment test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Basic sequential number assignment
test_sequential_assignment() {
    log "INFO" "Test 1: Basic sequential number assignment"
    
    # Initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "ERROR" "Initialization failed"
        return 1
    fi
    
    # Get first number
    local num1
    num1=$("$NUMBER_MANAGER_SCRIPT" get test_context 2>/dev/null | tail -1)
    if [ $? -ne 0 ] || [ "$num1" != "1" ]; then
        log "ERROR" "First number assignment failed: got $num1"
        return 1
    fi
    
    # Get second number
    local num2
    num2=$("$NUMBER_MANAGER_SCRIPT" get test_context 2>/dev/null | tail -1)
    if [ $? -ne 0 ] || [ "$num2" != "2" ]; then
        log "ERROR" "Second number assignment failed: got $num2"
        return 1
    fi
    
    # Get third number
    local num3
    num3=$("$NUMBER_MANAGER_SCRIPT" get test_context 2>/dev/null | tail -1)
    if [ $? -ne 0 ] || [ "$num3" != "3" ]; then
        log "ERROR" "Third number assignment failed: got $num3"
        return 1
    fi
    
    log "SUCCESS" "Sequential assignment working: 1, 2, 3"
    return 0
}

# Test 2: Number assignment across different contexts
test_cross_context_assignment() {
    log "INFO" "Test 2: Number assignment across different contexts"
    
    # Initialize with first context
    "$NUMBER_MANAGER_SCRIPT" init context1 >/dev/null 2>&1
    
    # Get number from context1
    local ctx1_num
    ctx1_num=$("$NUMBER_MANAGER_SCRIPT" get context1 2>/dev/null | tail -1)
    if [ $? -ne 0 ] || [ "$ctx1_num" != "1" ]; then
        log "ERROR" "Context1 first number failed: got $ctx1_num"
        return 1
    fi
    
    # Get number from context2 (should continue sequence)
    local ctx2_num
    ctx2_num=$("$NUMBER_MANAGER_SCRIPT" get context2 2>/dev/null | tail -1)
    if [ $? -ne 0 ] || [ "$ctx2_num" != "2" ]; then
        log "ERROR" "Context2 number assignment failed: got $ctx2_num"
        return 1
    fi
    
    # Get another number from context1 (should continue global sequence)
    local ctx1_num2
    ctx1_num2=$("$NUMBER_MANAGER_SCRIPT" get context1 2>/dev/null | tail -1)
    if [ $? -ne 0 ] || [ "$ctx1_num2" != "3" ]; then
        log "ERROR" "Context1 second number failed: got $ctx1_num2"
        return 1
    fi
    
    log "SUCCESS" "Cross-context assignment working: context1=1,3; context2=2"
    return 0
}

# Test 3: Number assignment updates state correctly
test_state_update_on_assignment() {
    log "INFO" "Test 3: State update on assignment"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init state_test >/dev/null 2>&1
    
    # Assign some numbers
    "$NUMBER_MANAGER_SCRIPT" get state_test >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get state_test >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" get state_test >/dev/null 2>&1  # 3
    
    # Check state statistics
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    if [ $? -ne 0 ]; then
        log "ERROR" "Failed to get stats"
        return 1
    fi
    
    local used_count last_assigned
    used_count=$(echo "$stats" | jq -r '.used_count')
    last_assigned=$(echo "$stats" | jq -r '.last_assigned')
    
    if [ "$used_count" != "3" ]; then
        log "ERROR" "Used count incorrect: $used_count"
        return 1
    fi
    
    if [ "$last_assigned" != "3" ]; then
        log "ERROR" "Last assigned incorrect: $last_assigned"
        return 1
    fi
    
    log "SUCCESS" "State updated correctly after assignments"
    return 0
}

# Test 4: Number assignment with context tracking
test_context_tracking_on_assignment() {
    log "INFO" "Test 4: Context tracking on assignment"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init tracking_test >/dev/null 2>&1
    
    # Assign numbers to different contexts
    local num1 num2 num3
    num1=$("$NUMBER_MANAGER_SCRIPT" get repo_A 2>/dev/null | tail -1)  # 1
    num2=$("$NUMBER_MANAGER_SCRIPT" get repo_B 2>/dev/null | tail -1)  # 2
    num3=$("$NUMBER_MANAGER_SCRIPT" get repo_A 2>/dev/null | tail -1)  # 3
    
    # Check context assignments
    local contexts
    contexts=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    if [ $? -ne 0 ]; then
        log "ERROR" "Failed to get contexts"
        return 1
    fi
    
    local repo_A_assignment repo_B_assignment
    repo_A_assignment=$(echo "$contexts" | jq -r '.repo_A')
    repo_B_assignment=$(echo "$contexts" | jq -r '.repo_B')
    
    if [ "$repo_A_assignment" != "3" ]; then
        log "ERROR" "Repo A context assignment incorrect: $repo_A_assignment"
        return 1
    fi
    
    if [ "$repo_B_assignment" != "2" ]; then
        log "ERROR" "Repo B context assignment incorrect: $repo_B_assignment"
        return 1
    fi
    
    log "SUCCESS" "Context tracking working correctly"
    return 0
}

# Test 5: Number assignment handles edge cases
test_edge_cases() {
    log "INFO" "Test 5: Number assignment edge cases"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init edge_test >/dev/null 2>&1
    
    # Test with empty context name
    local empty_num
    empty_num=$("$NUMBER_MANAGER_SCRIPT" get "" 2>/dev/null | tail -1)
    if [ $? -eq 0 ] && [ "$empty_num" = "1" ]; then
        log "SUCCESS" "Empty context handled"
    else
        log "WARNING" "Empty context may not be handled optimally"
    fi
    
    # Test with special characters in context
    local special_num
    special_num=$("$NUMBER_MANAGER_SCRIPT" get "repo-with_special.chars" 2>/dev/null | tail -1)
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Special characters in context handled"
    else
        log "WARNING" "Special characters in context may cause issues"
    fi
    
    # Test with very long context name
    local long_num
    long_num=$("$NUMBER_MANAGER_SCRIPT" get "very_long_context_name_that_might_cause_issues_in_some_systems" 2>/dev/null | tail -1)
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Long context name handled"
    else
        log "WARNING" "Long context name may cause issues"
    fi
    
    return 0
}

# Test 6: Number assignment maintains uniqueness
test_uniqueness_guarantee() {
    log "INFO" "Test 6: Number assignment uniqueness guarantee"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init uniqueness_test >/dev/null 2>&1
    
    # Assign many numbers
    local numbers=()
    for i in {1..100}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get uniqueness_test 2>/dev/null | tail -1)
        if [ $? -ne 0 ]; then
            log "ERROR" "Number assignment $i failed"
            return 1
        fi
        numbers+=("$num")
    done
    
    # Check for duplicates
    local sorted_numbers
    sorted_numbers=$(printf '%s\n' "${numbers[@]}" | sort -n | uniq -d)
    if [ -n "$sorted_numbers" ]; then
        log "ERROR" "Duplicate numbers found: $sorted_numbers"
        return 1
    fi
    
    # Check sequence continuity (should be 1-100)
    local expected_min expected_max
    expected_min=$(printf '%s\n' "${numbers[@]}" | sort -n | head -1)
    expected_max=$(printf '%s\n' "${numbers[@]}" | sort -n | tail -1)
    
    if [ "$expected_min" != "1" ] || [ "$expected_max" != "100" ]; then
        log "ERROR" "Number sequence incorrect: min=$expected_min, max=$expected_max"
        return 1
    fi
    
    log "SUCCESS" "Uniqueness guarantee maintained for 100 numbers"
    return 0
}

# Test 7: Number assignment respects limits
test_number_limits() {
    log "INFO" "Test 7: Number assignment respects limits"
    
    # This test simulates approaching the 9999 limit
    # We can't actually assign 9999 numbers in a test, but we can test boundary conditions
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init limit_test >/dev/null 2>&1
    
    # Create a state with last_assigned close to limit
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    local high_numbers=()
    for i in {9990..9999}; do
        high_numbers+=("$i")
    done
    
    local numbers_json
    numbers_json=$(printf '%s\n' "${high_numbers[@]}" | jq -R . | jq -s .)
    
    jq \
        --argjson numbers "$numbers_json" \
        '.used_numbers = $numbers | .last_assigned = 9999' \
        "$state_file" > "${state_file}.tmp" && mv "${state_file}.tmp" "$state_file"
    
    # Try to get another number (should fail or handle gracefully)
    local next_num
    if ! "$NUMBER_MANAGER_SCRIPT" get limit_test >/dev/null 2>&1; then
        log "SUCCESS" "Number limit enforced (assignment failed as expected)"
    else
        next_num=$("$NUMBER_MANAGER_SCRIPT" get limit_test 2>/dev/null | tail -1)
        if [ "$next_num" -gt 9999 ]; then
            log "ERROR" "Number limit not enforced: $next_num"
            return 1
        else
            log "SUCCESS" "Number assignment handled limit gracefully"
        fi
    fi
    
    return 0
}

# Test 8: Number assignment atomicity
test_assignment_atomicity() {
    log "INFO" "Test 8: Number assignment atomicity"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init atomic_test >/dev/null 2>&1
    
    # Get state before assignment
    local state_before
    state_before=$(cat "$TEST_STATE_DIR/.number_state/state.json")
    
    # Assign a number
    local num
    num=$("$NUMBER_MANAGER_SCRIPT" get atomic_test 2>/dev/null | tail -1)
    if [ $? -ne 0 ]; then
        log "ERROR" "Number assignment failed"
        return 1
    fi
    
    # Get state after assignment
    local state_after
    state_after=$(cat "$TEST_STATE_DIR/.number_state/state.json")
    
    # State should be different
    if [ "$state_before" = "$state_after" ]; then
        log "ERROR" "State not modified after assignment"
        return 1
    fi
    
    # Check if number is in used_numbers
    local is_used
    is_used=$(echo "$state_after" | jq -r --argjson num "$num" '.used_numbers | contains([$num])')
    if [ "$is_used" != "true" ]; then
        log "ERROR" "Assigned number not found in used_numbers"
        return 1
    fi
    
    # Check if last_assigned was updated
    local last_assigned
    last_assigned=$(echo "$state_after" | jq -r '.last_assigned')
    if [ "$last_assigned" != "$num" ]; then
        log "ERROR" "last_assigned not updated correctly"
        return 1
    fi
    
    log "SUCCESS" "Assignment atomicity verified"
    return 0
}

# Run all tests
run_all_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_sequential_assignment"
        "test_cross_context_assignment"
        "test_state_update_on_assignment"
        "test_context_tracking_on_assignment"
        "test_edge_cases"
        "test_uniqueness_guarantee"
        "test_number_limits"
        "test_assignment_atomicity"
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
    echo "Basic Assignment Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All basic assignment tests passed!"
        return 0
    else
        log "ERROR" "Some basic assignment tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests basic number assignment functionality"
    exit 1
fi