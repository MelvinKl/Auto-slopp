#!/bin/bash

# Another test file for number manager integration
# Part of Auto-eoi: Another test file for number manager integration

set -e

SCRIPT_NAME="test_number_manager_integration"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_number_manager_integration_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting number manager integration test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Number manager integration test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Basic number manager functionality
test_basic_number_manager() {
    log "INFO" "Test 1: Basic number manager functionality"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init basic_test >/dev/null 2>&1
    
    # Test getting numbers
    local numbers=()
    for i in {1..5}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get basic_test 2>/dev/null | tail -1)
        
        if [ $? -eq 0 ] && [ -n "$num" ]; then
            numbers+=("$num")
        fi
    done
    
    if [ ${#numbers[@]} -ne 5 ]; then
        log "ERROR" "Expected 5 numbers, got ${#numbers[@]}"
        return 1
    fi
    
    # Check numbers are sequential
    local expected_numbers=("1" "2" "3" "4" "5")
    for i in "${!expected_numbers[@]}"; do
        if [ "${numbers[$i]}" != "${expected_numbers[$i]}" ]; then
            log "ERROR" "Expected number ${expected_numbers[$i]}, got ${numbers[$i]}"
            return 1
        fi
    done
    
    log "SUCCESS" "Basic number manager: got sequential numbers ${numbers[*]}"
    return 0
}

# Test 2: Multi-context number management
test_multi_context_management() {
    log "INFO" "Test 2: Multi-context number management"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init multi_context >/dev/null 2>&1
    
    # Test multiple contexts
    local contexts=("web_app" "mobile_app" "api_service")
    local context_assignments=()
    
    for ctx in "${contexts[@]}"; do
        local ctx_numbers=()
        for i in {1..3}; do
            local num
            num=$("$NUMBER_MANAGER_SCRIPT" get "$ctx" 2>/dev/null | tail -1)
            
            if [ $? -eq 0 ] && [ -n "$num" ]; then
                ctx_numbers+=("$num")
                context_assignments+=("$ctx:$num")
            fi
        done
        
        log "INFO" "Context '$ctx' assigned: ${ctx_numbers[*]}"
    done
    
    # Verify all assignments are unique across contexts
    local all_numbers=()
    for assignment in "${context_assignments[@]}"; do
        local num
        num=$(echo "$assignment" | cut -d: -f2)
        all_numbers+=("$num")
    done
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Found $duplicate_count duplicate numbers across contexts"
        return 1
    fi
    
    log "SUCCESS" "Multi-context management: ${#context_assignments[@]} unique assignments across ${#contexts[@]} contexts"
    return 0
}

# Test 3: Number release and gap handling
test_number_release_and_gaps() {
    log "INFO" "Test 3: Number release and gap handling"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init release_test >/dev/null 2>&1
    
    # Get some numbers
    local numbers=()
    for i in {1..5}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get release_test 2>/dev/null | tail -1)
        
        if [ $? -eq 0 ] && [ -n "$num" ]; then
            numbers+=("$num")
        fi
    done
    
    # Release a number
    local release_num="${numbers[2]}"  # Release the third number (3)
    "$NUMBER_MANAGER_SCRIPT" release "$release_num" release_test >/dev/null 2>&1
    
    # Get another number (should reuse the released number)
    local reuse_num
    reuse_num=$("$NUMBER_MANAGER_SCRIPT" get release_test 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$reuse_num" ]; then
        log "ERROR" "Failed to get number after release"
        return 1
    fi
    
    # Check for gaps
    "$NUMBER_MANAGER_SCRIPT" gaps release_test >/dev/null 2>&1
    
    log "SUCCESS" "Number release and gaps: released $release_num, reused $reuse_num"
    return 0
}

# Test 4: State synchronization with files
test_state_file_synchronization() {
    log "INFO" "Test 4: State synchronization with files"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init sync_test >/dev/null 2>&1
    
    # Create some mock files that would represent tasks
    local task_files=()
    for i in {1..4}; do
        local task_file="$TEST_STATE_DIR/task_${i}.md"
        echo "# Task $i
Number: $i
" > "$task_file"
        task_files+=("$task_file")
    done
    
    # Sync state with files
    "$NUMBER_MANAGER_SCRIPT" sync "$TEST_STATE_DIR" sync_test >/dev/null 2>&1
    
    # Get a new number (should be 5 after syncing)
    local next_num
    next_num=$("$NUMBER_MANAGER_SCRIPT" get sync_test 2>/dev/null | tail -1)
    
    if [ "$next_num" != "5" ]; then
        log "ERROR" "Expected next number to be 5, got $next_num"
        return 1
    fi
    
    log "SUCCESS" "State file synchronization: synced with ${#task_files[@]} files, next number is $next_num"
    return 0
}

# Test 5: Statistics and reporting
test_statistics_and_reporting() {
    log "INFO" "Test 5: Statistics and reporting"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init stats_test >/dev/null 2>&1
    
    # Create activity in multiple contexts
    local contexts=("stats_ctx1" "stats_ctx2")
    for ctx in "${contexts[@]}"; do
        for i in {1..3}; do
            "$NUMBER_MANAGER_SCRIPT" get "$ctx" >/dev/null 2>&1
        done
    done
    
    # Get statistics
    local stats_output
    stats_output=$("$NUMBER_MANAGER_SCRIPT" stats stats_test 2>/dev/null)
    
    if [ $? -ne 0 ] || [ -z "$stats_output" ]; then
        log "ERROR" "Failed to get statistics"
        return 1
    fi
    
    # Get contexts
    local contexts_output
    contexts_output=$("$NUMBER_MANAGER_SCRIPT" contexts stats_test 2>/dev/null)
    
    if [ $? -ne 0 ] || [ -z "$contexts_output" ]; then
        log "ERROR" "Failed to get contexts"
        return 1
    fi
    
    log "SUCCESS" "Statistics and reporting: stats and contexts retrieved successfully"
    return 0
}

# Test 6: Error handling and recovery
test_error_handling_and_recovery() {
    log "INFO" "Test 6: Error handling and recovery"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init error_test >/dev/null 2>&1
    
    # Test error scenarios
    
    # Scenario 1: Invalid number release
    "$NUMBER_MANAGER_SCRIPT" release "999" error_test >/dev/null 2>&1
    
    # Scenario 2: Invalid context
    local num
    num=$("$NUMBER_MANAGER_SCRIPT" get "invalid@context#name" 2>/dev/null | tail -1)
    
    # Scenario 3: Get number after potential error
    local recovery_num
    recovery_num=$("$NUMBER_MANAGER_SCRIPT" get error_test 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$recovery_num" ]; then
        log "ERROR" "Failed to recover after error scenarios"
        return 1
    fi
    
    # Verify state is still valid
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "State file corrupted after error scenarios"
            return 1
        fi
    fi
    
    log "SUCCESS" "Error handling and recovery: system recovered from error scenarios, got number $recovery_num"
    return 0
}

# Test 7: Performance with large datasets
test_performance_large_dataset() {
    log "INFO" "Test 7: Performance with large dataset"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init performance_test >/dev/null 2>&1
    
    # Create a larger dataset
    local start_time
    start_time=$(date +%s.%N)
    
    local numbers_assigned=0
    for i in {1..50}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get performance_test 2>/dev/null | tail -1)
        
        if [ $? -eq 0 ] && [ -n "$num" ]; then
            numbers_assigned=$((numbers_assigned + 1))
        fi
        
        # Small delay to simulate real usage
        sleep 0.001
    done
    
    local end_time
    end_time=$(date +%s.%N)
    
    if [ "$numbers_assigned" -lt 40 ]; then
        log "ERROR" "Performance test: only $numbers_assigned numbers assigned out of 50 attempts"
        return 1
    fi
    
    # Calculate performance
    local duration
    duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "N/A")
    
    if command -v bc >/dev/null 2>&1 && [ "$duration" != "N/A" ]; then
        local avg_time
        avg_time=$(echo "scale=3; $duration / $numbers_assigned" | bc -l)
        log "SUCCESS" "Performance test: $numbers_assigned numbers in ${duration}s (avg: ${avg_time}s per number)"
    else
        log "SUCCESS" "Performance test: $numbers_assigned numbers assigned"
    fi
    
    return 0
}

# Run all number manager integration tests
run_all_integration_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_basic_number_manager"
        "test_multi_context_management"
        "test_number_release_and_gaps"
        "test_state_file_synchronization"
        "test_statistics_and_reporting"
        "test_error_handling_and_recovery"
        "test_performance_large_dataset"
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
    echo "Number Manager Integration Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All number manager integration tests passed!"
        return 0
    else
        log "ERROR" "Some number manager integration tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_integration_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests number manager integration scenarios"
    exit 1
fi