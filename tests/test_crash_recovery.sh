#!/bin/bash

# Test crash recovery from interrupted operations
# Part of Auto-58z: Test concurrent access and race condition handling

set -e

SCRIPT_NAME="test_crash_recovery"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_crash_recovery_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting crash recovery test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Crash recovery test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Recovery from SIGKILL during number assignment
test_sigkill_recovery() {
    log "INFO" "Test 1: Recovery from SIGKILL during number assignment"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init sigkill_recovery >/dev/null 2>&1
    
    # Get initial state
    local initial_next
    initial_next=$("$NUMBER_MANAGER_SCRIPT" status sigkill_recovery 2>/dev/null | grep "next_number" | cut -d: -f2 | tr -d ' ')
    
    # Start a process that will be killed
    (
        # This process will try to get multiple numbers
        for i in {1..5}; do
            local num
            num=$("$NUMBER_MANAGER_SCRIPT" get sigkill_recovery 2>/dev/null | tail -1)
            if [ $? -eq 0 ] && [ -n "$num" ]; then
                echo "before_kill:$num" >> "$TEST_STATE_DIR/sigkill_before.txt"
            fi
            sleep 0.1
        done
    ) &
    local victim_pid=$!
    
    # Let it get at least one number
    sleep 0.2
    
    # Kill the process abruptly
    kill -9 "$victim_pid" 2>/dev/null || true
    wait "$victim_pid" 2>/dev/null || true
    
    # Check state after crash
    local state_after_crash
    state_after_crash=$("$NUMBER_MANAGER_SCRIPT" status sigkill_recovery 2>/dev/null | grep "next_number" | cut -d: -f2 | tr -d ' ')
    
    # Try to get a new number (should work after recovery)
    local recovery_num
    recovery_num=$("$NUMBER_MANAGER_SCRIPT" get sigkill_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$recovery_num" ]; then
        log "ERROR" "Failed to recover after SIGKILL"
        return 1
    fi
    
    # Verify state consistency
    local final_state
    final_state=$("$NUMBER_MANAGER_SCRIPT" status sigkill_recovery 2>/dev/null | grep "next_number" | cut -d: -f2 | tr -d ' ')
    
    # Check that state file is valid JSON
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "State file corrupted after SIGKILL recovery"
            return 1
        fi
    fi
    
    log "SUCCESS" "SIGKILL recovery: initial=$initial_next, after_crash=$state_after_crash, recovery=$recovery_num, final=$final_state"
    return 0
}

# Test 2: Recovery from state file corruption
test_state_corruption_recovery() {
    log "INFO" "Test 2: Recovery from state file corruption"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init corruption_recovery >/dev/null 2>&1
    
    # Get some numbers first
    local numbers_before=()
    for i in {1..3}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get corruption_recovery 2>/dev/null | tail -1)
        if [ $? -eq 0 ] && [ -n "$num" ]; then
            numbers_before+=("$num")
        fi
    done
    
    # Corrupt the state file
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        echo '{"corrupted": "data", "invalid": true}' > "$state_file"
    fi
    
    # Try to get a number (should trigger recovery)
    local recovery_num
    recovery_num=$("$NUMBER_MANAGER_SCRIPT" get corruption_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$recovery_num" ]; then
        log "ERROR" "Failed to recover from state corruption"
        return 1
    fi
    
    # Verify state file is now valid
    if [ -f "$state_file" ]; then
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "State file still corrupted after recovery"
            return 1
        fi
        
        # Check for required fields
        local required_fields=("next_number" "assigned_numbers" "contexts")
        for field in "${required_fields[@]}"; do
            if ! grep -q "\"$field\"" "$state_file"; then
                log "ERROR" "Recovered state missing field: $field"
                return 1
            fi
        done
    fi
    
    # Get another number to verify continued operation
    local continued_num
    continued_num=$("$NUMBER_MANAGER_SCRIPT" get corruption_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$continued_num" ]; then
        log "ERROR" "Failed to continue operation after recovery"
        return 1
    fi
    
    # Check for duplicates
    local all_numbers=("${numbers_before[@]}" "$recovery_num" "$continued_num")
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Duplicates found after corruption recovery: $duplicate_count"
        return 1
    fi
    
    log "SUCCESS" "State corruption recovery: before=${numbers_before[*]}, recovery=$recovery_num, continued=$continued_num"
    return 0
}

# Test 3: Recovery from lock file stale state
test_stale_lock_recovery() {
    log "INFO" "Test 3: Recovery from lock file stale state"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init stale_lock_recovery >/dev/null 2>&1
    
    # Create a stale lock file
    local lock_file="$TEST_STATE_DIR/.number_state/.lock"
    local old_timestamp
    old_timestamp=$(($(date +%s) - 3600))  # 1 hour ago
    
    echo "99999:$old_timestamp" > "$lock_file"
    
    # Try to get a number (should clean up stale lock)
    local recovery_num
    recovery_num=$("$NUMBER_MANAGER_SCRIPT" get stale_lock_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$recovery_num" ]; then
        log "ERROR" "Failed to recover from stale lock"
        return 1
    fi
    
    # Check that lock file was cleaned up or updated
    local lock_exists=false
    if [ -f "$lock_file" ]; then
        local lock_timestamp
        lock_timestamp=$(cat "$lock_file" 2>/dev/null | cut -d: -f2)
        local current_time
        current_time=$(date +%s)
        
        # Lock should be recent (not the old timestamp)
        if [ "$lock_timestamp" -gt $((current_time - 300)) ]; then
            lock_exists=true
        fi
    fi
    
    # Get another number to verify continued operation
    local continued_num
    continued_num=$("$NUMBER_MANAGER_SCRIPT" get stale_lock_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$continued_num" ]; then
        log "ERROR" "Failed to continue after stale lock recovery"
        return 1
    fi
    
    # Check for duplicates
    local duplicate_count
    duplicate_count=$(printf '%s\n' "$recovery_num" "$continued_num" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Duplicates found after stale lock recovery: $duplicate_count"
        return 1
    fi
    
    log "SUCCESS" "Stale lock recovery: recovery=$recovery_num, continued=$continued_num, lock_cleaned=$lock_exists"
    return 0
}

# Test 4: Recovery from partial state write
test_partial_write_recovery() {
    log "INFO" "Test 4: Recovery from partial state write"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init partial_write_recovery >/dev/null 2>&1
    
    # Get some numbers to establish state
    local numbers_before=()
    for i in {1..4}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get partial_write_recovery 2>/dev/null | tail -1)
        if [ $? -eq 0 ] && [ -n "$num" ]; then
            numbers_before+=("$num")
        fi
    done
    
    # Simulate partial write by truncating state file
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        # Truncate to simulate incomplete write
        local original_size
        original_size=$(wc -c < "$state_file")
        truncate -s $((original_size / 2)) "$state_file" 2>/dev/null || true
    fi
    
    # Try to get a number (should trigger recovery)
    local recovery_num
    recovery_num=$("$NUMBER_MANAGER_SCRIPT" get partial_write_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$recovery_num" ]; then
        log "ERROR" "Failed to recover from partial write"
        return 1
    fi
    
    # Verify state file is now complete and valid
    if [ -f "$state_file" ]; then
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "State file invalid after partial write recovery"
            return 1
        fi
        
        # Check that file is complete (has required structure)
        local file_size
        file_size=$(wc -c < "$state_file")
        if [ "$file_size" -lt 50 ]; then  # Should be much larger for valid JSON
            log "ERROR" "State file appears incomplete after recovery: $file_size bytes"
            return 1
        fi
    fi
    
    # Get another number to verify continued operation
    local continued_num
    continued_num=$("$NUMBER_MANAGER_SCRIPT" get partial_write_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$continued_num" ]; then
        log "ERROR" "Failed to continue after partial write recovery"
        return 1
    fi
    
    log "SUCCESS" "Partial write recovery: before=${numbers_before[*]}, recovery=$recovery_num, continued=$continued_num"
    return 0
}

# Test 5: Recovery from concurrent process crashes
test_concurrent_crash_recovery() {
    log "INFO" "Test 5: Recovery from concurrent process crashes"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init concurrent_crash_recovery >/dev/null 2>&1
    
    # Start multiple processes, then kill some abruptly
    local pids=()
    local crash_log="$TEST_STATE_DIR/concurrent_crash_log.txt"
    
    for i in {1..10}; do
        (
            # Each process tries to get multiple numbers
            for j in {1..3}; do
                local start_time
                start_time=$(date +%s.%N)
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get concurrent_crash_recovery 2>/dev/null | tail -1)
                local end_time
                end_time=$(date +%s.%N)
                
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "process_$i:attempt_$j:success:$num:start_$start_time:end_$end_time" >> "$crash_log"
                else
                    echo "process_$i:attempt_$j:failed:start_$start_time:end_$end_time" >> "$crash_log"
                fi
                
                sleep 0.01
            done
        ) &
        pids+=($!)
    done
    
    # Let them start and get some numbers
    sleep 0.1
    
    # Kill some processes abruptly
    for i in {1..3}; do
        if [ ${#pids[@]} -gt $i ]; then
            kill -9 "${pids[$i]}" 2>/dev/null || true
        fi
    done
    
    # Wait for remaining processes
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Try to get a number after the crashes (should work)
    local recovery_num
    recovery_num=$("$NUMBER_MANAGER_SCRIPT" get concurrent_crash_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$recovery_num" ]; then
        log "ERROR" "Failed to recover after concurrent crashes"
        return 1
    fi
    
    # Analyze results for consistency
    local all_numbers=()
    if [ -f "$crash_log" ]; then
        while read -r line; do
            if echo "$line" | grep -q "success"; then
                local num
                num=$(echo "$line" | cut -d: -f4)
                all_numbers+=("$num")
            fi
        done < "$crash_log"
    fi
    
    # Add recovery number
    all_numbers+=("$recovery_num")
    
    # Check for duplicates (should be none if recovery worked)
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Duplicates found after concurrent crash recovery: $duplicate_count"
        return 1
    fi
    
    # Verify state file integrity
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "State file corrupted after concurrent crash recovery"
            return 1
        fi
    fi
    
    log "SUCCESS" "Concurrent crash recovery: ${#all_numbers[@]} unique numbers, recovery=$recovery_num"
    return 0
}

# Test 6: Recovery from backup system failure
test_backup_failure_recovery() {
    log "INFO" "Test 6: Recovery from backup system failure"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init backup_failure_recovery >/dev/null 2>&1
    
    # Get some numbers to create state
    local numbers_before=()
    for i in {1..3}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get backup_failure_recovery 2>/dev/null | tail -1)
        if [ $? -eq 0 ] && [ -n "$num" ]; then
            numbers_before+=("$num")
        fi
    done
    
    # Corrupt backup directory
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    if [ -d "$backup_dir" ]; then
        # Create corrupted backup files
        for backup_file in "$backup_dir"/*.json; do
            if [ -f "$backup_file" ]; then
                echo '{"corrupted": "backup"}' > "$backup_file"
            fi
        done
    fi
    
    # Also corrupt main state
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        echo '{"corrupted": "main"}' > "$state_file"
    fi
    
    # Try to get a number (should trigger recovery from somewhere)
    local recovery_num
    recovery_num=$("$NUMBER_MANAGER_SCRIPT" get backup_failure_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$recovery_num" ]; then
        log "ERROR" "Failed to recover from backup system failure"
        return 1
    fi
    
    # Verify system is working again
    local continued_num
    continued_num=$("$NUMBER_MANAGER_SCRIPT" get backup_failure_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$continued_num" ]; then
        log "ERROR" "Failed to continue after backup failure recovery"
        return 1
    fi
    
    # Check state file is now valid
    if [ -f "$state_file" ]; then
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "State file still invalid after backup failure recovery"
            return 1
        fi
    fi
    
    log "SUCCESS" "Backup failure recovery: before=${numbers_before[*]}, recovery=$recovery_num, continued=$continued_num"
    return 0
}

# Test 7: Recovery from resource exhaustion
test_resource_exhaustion_recovery() {
    log "INFO" "Test 7: Recovery from resource exhaustion"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init resource_exhaustion_recovery >/dev/null 2>&1
    
    # Consume file descriptors to simulate resource exhaustion
    local temp_fds=()
    for i in {1..50}; do
        local temp_file="$TEST_STATE_DIR/temp_fd_$i.tmp"
        touch "$temp_file"
        exec {fd}<"$temp_file" 2>/dev/null || true
        temp_fds+=("$fd")
    done
    
    # Try to get a number under resource pressure
    local pressure_num
    pressure_num=$("$NUMBER_MANAGER_SCRIPT" get resource_exhaustion_recovery 2>/dev/null | tail -1)
    
    # Clean up file descriptors
    for fd in "${temp_fds[@]}"; do
        exec {fd}<&- 2>/dev/null || true
    done
    
    # Try to get another number after resource cleanup
    local recovery_num
    recovery_num=$("$NUMBER_MANAGER_SCRIPT" get resource_exhaustion_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$recovery_num" ]; then
        log "ERROR" "Failed to recover from resource exhaustion"
        return 1
    fi
    
    # Verify continued operation
    local continued_num
    continued_num=$("$NUMBER_MANAGER_SCRIPT" get resource_exhaustion_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$continued_num" ]; then
        log "ERROR" "Failed to continue after resource exhaustion recovery"
        return 1
    fi
    
    # Check for duplicates
    local all_numbers=()
    if [ -n "$pressure_num" ]; then
        all_numbers+=("$pressure_num")
    fi
    all_numbers+=("$recovery_num" "$continued_num")
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Duplicates found after resource exhaustion recovery: $duplicate_count"
        return 1
    fi
    
    log "SUCCESS" "Resource exhaustion recovery: pressure=$pressure_num, recovery=$recovery_num, continued=$continued_num"
    return 0
}

# Run all crash recovery tests
run_all_crash_recovery_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_sigkill_recovery"
        "test_state_corruption_recovery"
        "test_stale_lock_recovery"
        "test_partial_write_recovery"
        "test_concurrent_crash_recovery"
        "test_backup_failure_recovery"
        "test_resource_exhaustion_recovery"
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
    echo "Crash Recovery Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All crash recovery tests passed!"
        return 0
    else
        log "ERROR" "Some crash recovery tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_crash_recovery_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests crash recovery from interrupted operations"
    exit 1
fi