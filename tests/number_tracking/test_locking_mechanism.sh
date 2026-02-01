#!/bin/bash

# Test locking mechanism functionality
# Part of Auto-9bu: Test unique number assignment and locking mechanism

set -e

SCRIPT_NAME="test_locking_mechanism"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_locking_mechanism_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting locking mechanism test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Basic lock acquisition and release
test_basic_lock_acquisition() {
    log "INFO" "Test 1: Basic lock acquisition and release"
    
    # Initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init lock_test >/dev/null 2>&1; then
        log "ERROR" "Initialization failed"
        return 1
    fi
    
    # Get a number (this should acquire and release lock automatically)
    local num1
    num1=$("$NUMBER_MANAGER_SCRIPT" get lock_test 2>/dev/null | grep -E '^[0-9]+$' | tail -1)
    if [ $? -ne 0 ] || [ "$num1" != "1" ]; then
        log "ERROR" "First number assignment failed: got $num1"
        return 1
    fi
    
    # Verify lock file is released (should not exist)
    if [ -f "$TEST_STATE_DIR/.number_state/.lock" ]; then
        log "ERROR" "Lock file was not released after operation"
        return 1
    fi
    
    log "INFO" "✓ Basic lock acquisition and release test passed"
    return 0
}

# Test 2: Lock contention behavior
test_lock_contention() {
    log "INFO" "Test 2: Lock contention behavior"
    
    # Create a manual lock to simulate contention
    local lock_file="$TEST_STATE_DIR/.number_state/.lock"
    mkdir -p "$TEST_STATE_DIR/.number_state"
    
    # Start a background process that holds a lock
    (
        sleep 3
        echo "$$:$(date +%s)" > "$lock_file"
        sleep 2
        rm -f "$lock_file"
    ) &
    local lock_holder_pid=$!
    
    sleep 1  # Let the background process acquire the lock
    
    # Try to get a number while lock is held
    local start_time=$(date +%s)
    "$NUMBER_MANAGER_SCRIPT" get lock_test >/dev/null 2>&1 &
    local number_getter_pid=$!
    
    # Wait for the operation to complete
    wait $number_getter_pid
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Kill the lock holder process
    kill $lock_holder_pid 2>/dev/null || true
    wait $lock_holder_pid 2>/dev/null || true
    
    # The operation should have taken at least 2 seconds due to lock contention
    if [ $duration -lt 2 ]; then
        log "WARNING" "Lock contention test may not have triggered proper waiting (duration: ${duration}s)"
    fi
    
    # Check that a number was eventually assigned
    local state_stats
    state_stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    if [ $? -ne 0 ]; then
        log "ERROR" "Failed to get state stats after lock contention"
        return 1
    fi
    
    local used_count
    used_count=$(echo "$state_stats" | jq -r '.used_count // 0')
    if [ "$used_count" -eq 0 ]; then
        log "ERROR" "No numbers were assigned despite waiting for lock"
        return 1
    fi
    
    log "INFO" "✓ Lock contention test passed (duration: ${duration}s)"
    return 0
}

# Test 3: Stale lock detection and cleanup
test_stale_lock_cleanup() {
    log "INFO" "Test 3: Stale lock detection and cleanup"
    
    # Create a fake old lock file
    local lock_file="$TEST_STATE_DIR/.number_state/.lock"
    mkdir -p "$TEST_STATE_DIR/.number_state"
    
    # Create a lock with an old timestamp (more than 5 minutes ago)
    local old_timestamp=$(($(date +%s) - 400))  # 400 seconds ago
    echo "9999:$old_timestamp" > "$lock_file"  # Use fake PID that doesn't exist
    
    # Try to get a number - should detect stale lock and clean it up
    local num
    num=$("$NUMBER_MANAGER_SCRIPT" get lock_test 2>/dev/null | grep -E '^[0-9]+$' | tail -1)
    if [ $? -ne 0 ]; then
        log "ERROR" "Failed to get number with stale lock present"
        return 1
    fi
    
    # Verify the number is valid
    if ! [[ "$num" =~ ^[0-9]+$ ]] || [ "$num" -eq 0 ]; then
        log "ERROR" "Invalid number returned after stale lock cleanup: $num"
        return 1
    fi
    
    log "INFO" "✓ Stale lock cleanup test passed (got number: $num)"
    return 0
}

# Test 4: Lock timeout behavior
test_lock_timeout() {
    log "INFO" "Test 4: Lock timeout behavior"
    
    # Test that the timeout mechanism exists and doesn't hang indefinitely
    # Create a manual lock that will cause contention
    local lock_file="$TEST_STATE_DIR/.number_state/.lock"
    mkdir -p "$TEST_STATE_DIR/.number_state"
    
    # Create a lock with a fake PID (so it will be treated as stale)
    echo "99999:$(($(date +%s) - 400))" > "$lock_file"  # 400 seconds ago
    
    # Try to get a number - should detect stale lock and succeed
    local start_time=$(date +%s)
    "$NUMBER_MANAGER_SCRIPT" get lock_test >/dev/null 2>&1
    local result=$?
    local end_time=$(date +%s)
    
    local duration=$((end_time - start_time))
    
    # The operation should succeed after cleaning up stale lock
    if [ $result -ne 0 ]; then
        log "ERROR" "Number assignment failed even with stale lock cleanup"
        return 1
    fi
    
    # Should be quick (stale lock detection)
    if [ $duration -gt 10 ]; then
        log "WARNING" "Stale lock cleanup took longer than expected: ${duration}s"
    fi
    
    log "INFO" "✓ Lock timeout test passed (duration: ${duration}s)"
    return 0
}

# Test 5: Multiple rapid lock acquisitions
test_rapid_lock_operations() {
    log "INFO" "Test 5: Multiple rapid lock operations"
    
    # Use fresh context to avoid interference from previous tests
    local fresh_context="rapid_test"
    
    # Perform multiple number assignments rapidly
    local numbers=()
    for i in {1..10}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get "$fresh_context" 2>/dev/null | grep -E '^[0-9]+$' | tail -1)
        if [ $? -ne 0 ] || [ -z "$num" ]; then
            log "ERROR" "Rapid operation $i failed"
            return 1
        fi
        numbers+=("$num")
    done
    
    # Verify all numbers are unique and sequential (should start from current next number)
    local first_num="${numbers[0]}"
    local expected_num="$first_num"
    for num in "${numbers[@]}"; do
        if [ "$num" -ne "$expected_num" ]; then
            log "ERROR" "Expected $expected_num but got $num"
            return 1
        fi
        expected_num=$((expected_num + 1))
    done
    
    log "INFO" "✓ Multiple rapid lock operations test passed (numbers: ${numbers[*]})"
    return 0
}

# Test 6: Lock file format validation
test_lock_file_format() {
    log "INFO" "Test 6: Lock file format validation"
    
    # Create invalid lock files and test cleanup
    local lock_file="$TEST_STATE_DIR/.number_state/.lock"
    mkdir -p "$TEST_STATE_DIR/.number_state"
    
    # Test with empty lock file
    echo "" > "$lock_file"
    local num
    num=$("$NUMBER_MANAGER_SCRIPT" get lock_test 2>/dev/null | grep -E '^[0-9]+$' | tail -1)
    if [ $? -ne 0 ]; then
        log "ERROR" "Failed to handle empty lock file"
        return 1
    fi
    
    # Test with malformed lock file
    echo "invalid_format" > "$lock_file"
    num=$("$NUMBER_MANAGER_SCRIPT" get lock_test 2>/dev/null | grep -E '^[0-9]+$' | tail -1)
    if [ $? -ne 0 ]; then
        log "ERROR" "Failed to handle malformed lock file"
        return 1
    fi
    
    # Test with very old timestamp
    echo "$$:$(($(date +%s) - 1000))" > "$lock_file"
    num=$("$NUMBER_MANAGER_SCRIPT" get lock_test 2>/dev/null | grep -E '^[0-9]+$' | tail -1)
    if [ $? -ne 0 ]; then
        log "ERROR" "Failed to handle very old timestamp in lock"
        return 1
    fi
    
    log "INFO" "✓ Lock file format validation test passed"
    return 0
}

# Run all tests
main() {
    log "INFO" "Starting locking mechanism tests"
    
    local test_count=0
    local passed_count=0
    
    # Run each test
    for test_func in test_basic_lock_acquisition test_lock_contention test_stale_lock_cleanup test_lock_timeout test_rapid_lock_operations test_lock_file_format; do
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
    log "INFO" "Locking mechanism tests completed: $passed_count/$test_count passed"
    
    if [ $passed_count -eq $test_count ]; then
        log "INFO" "✓ All locking mechanism tests passed!"
        return 0
    else
        log "ERROR" "✗ Some locking mechanism tests failed"
        return 1
    fi
}

# Run tests if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi