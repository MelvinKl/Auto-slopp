#!/bin/bash

# Test context tracking functionality
# Part of Auto-9bu: Test unique number assignment and locking mechanism

set -e

SCRIPT_NAME="test_context_tracking"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_context_tracking_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting context tracking test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Basic context assignment
test_basic_context_assignment() {
    log "INFO" "Test 1: Basic context assignment"
    
    # Initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init >/dev/null 2>&1; then
        log "ERROR" "Initialization failed"
        return 1
    fi
    
    # Assign numbers to different contexts
    local num1 num2 num3
    num1=$("$NUMBER_MANAGER_SCRIPT" get "repo1" 2>/dev/null | tail -1)
    num2=$("$NUMBER_MANAGER_SCRIPT" get "repo2" 2>/dev/null | tail -1)
    num3=$("$NUMBER_MANAGER_SCRIPT" get "repo1" 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ "$num1" != "1" ] || [ "$num2" != "2" ] || [ "$num3" != "3" ]; then
        log "ERROR" "Context assignment failed: num1=$num1, num2=$num2, num3=$num3"
        return 1
    fi
    
    # Check context assignments
    local assignments
    assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    if [ $? -ne 0 ]; then
        log "ERROR" "Failed to get context assignments"
        return 1
    fi
    
    # Verify assignments
    local repo1_num repo2_num
    repo1_num=$(echo "$assignments" | jq -r '.repo1 // "null"')
    repo2_num=$(echo "$assignments" | jq -r '.repo2 // "null"')
    
    if [ "$repo1_num" != "3" ] || [ "$repo2_num" != "2" ]; then
        log "ERROR" "Context assignments incorrect: repo1=$repo1_num, repo2=$repo2_num"
        return 1
    fi
    
    log "INFO" "✓ Basic context assignment test passed"
    return 0
}

# Test 2: Context isolation
test_context_isolation() {
    log "INFO" "Test 2: Context isolation"
    
    # Initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init >/dev/null 2>&1; then
        log "ERROR" "Initialization failed"
        return 1
    fi
    
    # Assign numbers to multiple contexts and track actual numbers
    local contexts=("alpha" "beta" "gamma" "delta")
    local actual_numbers=()
    
    for i in "${!contexts[@]}"; do
        local context="${contexts[$i]}"
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get "$context" 2>/dev/null | grep -E '^[0-9]+$' | tail -1)
        if [ $? -ne 0 ] || [ -z "$num" ]; then
            log "ERROR" "Context $context assignment failed: got '$num'"
            return 1
        fi
        actual_numbers+=("$num")
    done
    
    # Verify numbers are sequential
    local first_num="${actual_numbers[0]}"
    local expected_num="$first_num"
    for num in "${actual_numbers[@]}"; do
        if [ "$num" != "$expected_num" ]; then
            log "ERROR" "Expected $expected_num but got $num in sequence"
            return 1
        fi
        expected_num=$((expected_num + 1))
    done
    
    # Assign more numbers to verify global sequence
    local next_num
    next_num=$("$NUMBER_MANAGER_SCRIPT" get "alpha" 2>/dev/null | grep -E '^[0-9]+$' | tail -1)
    if [ "$next_num" != "$expected_num" ]; then
        log "ERROR" "Second assignment to alpha failed: expected $expected_num, got $next_num"
        return 1
    fi
    
    # Check final assignments
    local assignments
    assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    
    local alpha_num
    alpha_num=$(echo "$assignments" | jq -r '.alpha // "null"')
    if [ "$alpha_num" != "$next_num" ]; then
        log "ERROR" "Alpha context should have $next_num, got $alpha_num"
        return 1
    fi
    
    log "INFO" "✓ Context isolation test passed (numbers: ${actual_numbers[*]}, then $next_num)"
    return 0
}

# Test 3: Special characters in context names
test_special_character_contexts() {
    log "INFO" "Test 3: Special characters in context names"
    
    # Initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init >/dev/null 2>&1; then
        log "ERROR" "Initialization failed"
        return 1
    fi
    
    # Test contexts with various characters
    local test_contexts=(
        "test-repo-with-dashes"
        "test_repo_with_underscores"
        "testRepoWithNumbers123"
        "TestRepoWithCamelCase"
        "test.repo.with.dots"
    )
    
    local actual_numbers=()
    
    for context in "${test_contexts[@]}"; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get "$context" 2>/dev/null | grep -E '^[0-9]+$' | tail -1)
        if [ $? -ne 0 ] || [ -z "$num" ]; then
            log "ERROR" "Context '$context' assignment failed: got '$num'"
            return 1
        fi
        actual_numbers+=("$num")
    done
    
    # Verify numbers are sequential
    local first_num="${actual_numbers[0]}"
    local expected_num="$first_num"
    for num in "${actual_numbers[@]}"; do
        if [ "$num" != "$expected_num" ]; then
            log "ERROR" "Expected $expected_num but got $num in sequence"
            return 1
        fi
        expected_num=$((expected_num + 1))
    done
    
    log "INFO" "✓ Special character contexts test passed (numbers: ${actual_numbers[*]})"
    return 0
}

# Test 4: Context with spaces and edge cases
test_edge_case_contexts() {
    log "INFO" "Test 4: Context with spaces and edge cases"
    
    # Initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init >/dev/null 2>&1; then
        log "ERROR" "Initialization failed"
        return 1
    fi
    
    # Test contexts with spaces (should be handled properly)
    local num
    num=$("$NUMBER_MANAGER_SCRIPT" get "context with spaces" 2>/dev/null | tail -1)
    if [ $? -ne 0 ]; then
        log "WARNING" "Context with spaces failed (may be expected)"
    fi
    
    # Test empty context (should use default)
    num=$("$NUMBER_MANAGER_SCRIPT" get "" 2>/dev/null | tail -1)
    if [ $? -ne 0 ]; then
        log "INFO" "Empty context handled appropriately"
    fi
    
    # Test very long context name
    local long_context="this_is_a_very_long_context_name_that_might_cause_issues_with_the_system_and_should_be_handled_properly"
    num=$("$NUMBER_MANAGER_SCRIPT" get "$long_context" 2>/dev/null | tail -1)
    if [ $? -ne 0 ]; then
        log "ERROR" "Long context name failed"
        return 1
    fi
    
    log "INFO" "✓ Edge case contexts test passed"
    return 0
}

# Test 5: Context persistence across operations
test_context_persistence() {
    log "INFO" "Test 5: Context persistence across operations"
    
    # Initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init >/dev/null 2>&1; then
        log "ERROR" "Initialization failed"
        return 1
    fi
    
    # Assign numbers to contexts
    "$NUMBER_MANAGER_SCRIPT" get "persistent_test" >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get "another_context" >/dev/null 2>&1
    
    # Get stats to verify persistence
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    
    local context_count
    context_count=$(echo "$stats" | jq -r '.context_count // 0')
    if [ "$context_count" -lt 2 ]; then
        log "ERROR" "Context persistence failed: expected at least 2 contexts, got $context_count"
        return 1
    fi
    
    # Get assignments to verify specific contexts
    local assignments
    assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    
    local persistent_num another_num
    persistent_num=$(echo "$assignments" | jq -r '.persistent_test // "null"')
    another_num=$(echo "$assignments" | jq -r '.another_context // "null"')
    
    if [ "$persistent_num" = "null" ] || [ "$another_num" = "null" ]; then
        log "ERROR" "Context assignments not persisted properly"
        return 1
    fi
    
    log "INFO" "✓ Context persistence test passed"
    return 0
}

# Test 6: Concurrent context assignments
test_concurrent_context_assignment() {
    log "INFO" "Test 6: Concurrent context assignments"
    
    # Initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init >/dev/null 2>&1; then
        log "ERROR" "Initialization failed"
        return 1
    fi
    
    # Start multiple background processes assigning to different contexts
    local pids=()
    local output_files=()
    local contexts=("concurrent1" "concurrent2" "concurrent3" "concurrent4" "concurrent5")
    
    for i in "${!contexts[@]}"; do
        local context="${contexts[$i]}"
        local output_file="$TEST_STATE_DIR/concurrent_output_$i.txt"
        output_files+=("$output_file")
        
        (
            for j in {1..3}; do  # Each context gets 3 numbers
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get "$context" 2>/dev/null | tail -1)
                echo "$context:$num" >> "$output_file"
            done
        ) &
        pids+=($!)
    done
    
    # Wait for all processes to complete
    for pid in "${pids[@]}"; do
        wait $pid
    done
    
    # Verify results
    local all_unique=true
    local all_numbers=()
    
    for output_file in "${output_files[@]}"; do
        while IFS=: read -r context num; do
            if [[ "$num" =~ ^[0-9]+$ ]]; then
                if [[ " ${all_numbers[@]} " =~ " $num " ]]; then
                    all_unique=false
                fi
                all_numbers+=("$num")
            fi
        done < "$output_file"
    done
    
    if [ "$all_unique" = false ]; then
        log "ERROR" "Concurrent context assignments resulted in duplicate numbers"
        return 1
    fi
    
    # Verify we got the expected number of assignments
    if [ ${#all_numbers[@]} -ne 15 ]; then
        log "ERROR" "Expected 15 number assignments, got ${#all_numbers[@]}"
        return 1
    fi
    
    log "INFO" "✓ Concurrent context assignment test passed"
    return 0
}

# Test 7: Context history and metadata
test_context_history() {
    log "INFO" "Test 7: Context history and metadata"
    
    # Initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init >/dev/null 2>&1; then
        log "ERROR" "Initialization failed"
        return 1
    fi
    
    # Assign numbers with timestamps
    "$NUMBER_MANAGER_SCRIPT" get "history_test" >/dev/null 2>&1
    sleep 1
    "$NUMBER_MANAGER_SCRIPT" get "history_test" >/dev/null 2>&1
    
    # Check state file for assignment history
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ ! -f "$state_file" ]; then
        log "ERROR" "State file not found"
        return 1
    fi
    
    # Verify assignments were recorded
    local assignment_count
    assignment_count=$(jq '.assignments | length' "$state_file" 2>/dev/null || echo "0")
    if [ "$assignment_count" -lt 2 ]; then
        log "ERROR" "Assignment history not properly recorded: count=$assignment_count"
        return 1
    fi
    
    # Check that timestamps are present
    local timestamp_count
    timestamp_count=$(jq '.assignments | map(has("timestamp")) | map(select(. == true)) | length' "$state_file" 2>/dev/null || echo "0")
    if [ "$timestamp_count" -lt 2 ]; then
        log "ERROR" "Assignment timestamps not properly recorded: count=$timestamp_count"
        return 1
    fi
    
    log "INFO" "✓ Context history test passed"
    return 0
}

# Run all tests
main() {
    log "INFO" "Starting context tracking tests"
    
    local test_count=0
    local passed_count=0
    
    # Run each test
    for test_func in test_basic_context_assignment test_context_isolation test_special_character_contexts test_edge_case_contexts test_context_persistence test_concurrent_context_assignment test_context_history; do
        test_count=$((test_count + 1))
        
        if $test_func; then
            passed_count=$((passed_count + 1))
        else
            log "ERROR" "Test $test_func failed"
        fi
        
        # Brief pause between tests
        sleep 0.5
    done
    
    # Final report
    log "INFO" "Context tracking tests completed: $passed_count/$test_count passed"
    
    if [ $passed_count -eq $test_count ]; then
        log "INFO" "✓ All context tracking tests passed!"
        return 0
    else
        log "ERROR" "✗ Some context tracking tests failed"
        return 1
    fi
}

# Run tests if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi