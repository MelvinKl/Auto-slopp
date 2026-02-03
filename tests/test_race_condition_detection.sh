#!/bin/bash

# Test race condition detection and prevention
# Part of Auto-58z: Test concurrent access and race condition handling

set -e

SCRIPT_NAME="test_race_condition_detection"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_race_condition_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting race condition detection test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Race condition test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Time-of-check to time-of-use (TOCTOU) race condition
test_toctou_race_condition() {
    log "INFO" "Test 1: Time-of-check to time-of-use (TOCTOU) race condition"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init toctou_test >/dev/null 2>&1
    
    # Create a scenario where state is checked and then used
    local pids=()
    local results_file="$TEST_STATE_DIR/toctou_results.txt"
    
    for i in {1..20}; do
        (
            # Simulate TOCTOU: check state, then use it
            local state_check
            state_check=$("$NUMBER_MANAGER_SCRIPT" status toctou_test 2>/dev/null | grep "next_number" | cut -d: -f2 | tr -d ' ')
            
            if [ -n "$state_check" ]; then
                # Small delay to create race condition window
                sleep 0.01
                
                # Now try to use the checked state
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get toctou_test 2>/dev/null | tail -1)
                
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "process_$i:checked_$state_check:got_$num" >> "$results_file"
                fi
            fi
        ) &
        pids+=($!)
    done
    
    # Wait for all processes
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Analyze results for race conditions
    local all_numbers=()
    local race_conditions=0
    
    if [ -f "$results_file" ]; then
        while read -r line; do
            local num
            num=$(echo "$line" | cut -d: -f3 | cut -d_ -f2)
            if [ -n "$num" ]; then
                all_numbers+=("$num")
                
                # Check if checked number differs from got number (potential race)
                local checked
                checked=$(echo "$line" | cut -d: -f2 | cut -d_ -f2)
                if [ "$checked" != "$num" ]; then
                    race_conditions=$((race_conditions + 1))
                fi
            fi
        done < "$results_file"
    fi
    
    # Check for duplicates (indicates race condition)
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "TOCTOU race condition detected: $duplicate_count duplicates"
        return 1
    fi
    
    log "SUCCESS" "TOCTOU test: ${#all_numbers[@]} unique numbers, $race_conditions state changes detected"
    return 0
}

# Test 2: Lock file race condition
test_lock_race_condition() {
    log "INFO" "Test 2: Lock file race condition"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init lock_race >/dev/null 2>&1
    
    # Simulate lock file race condition
    local pids=()
    local lock_results="$TEST_STATE_DIR/lock_results.txt"
    
    for i in {1..15}; do
        (
            # Try to create race condition with lock file
            local lock_file="$TEST_STATE_DIR/.number_state/.lock"
            local state_file="$TEST_STATE_DIR/.number_state/state.json"
            
            # Multiple attempts to create race condition
            for j in {1..3}; do
                # Check if lock exists
                if [ -f "$lock_file" ]; then
                    local lock_content
                    lock_content=$(cat "$lock_file" 2>/dev/null || echo "")
                    echo "process_$i:attempt_$j:lock_exists:$lock_content" >> "$lock_results"
                fi
                
                # Try to get number
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get lock_race 2>/dev/null | tail -1)
                
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "process_$i:attempt_$j:got_number:$num" >> "$lock_results"
                fi
                
                sleep 0.005
            done
        ) &
        pids+=($!)
    done
    
    # Wait for completion
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Analyze for duplicates
    local all_numbers=()
    if [ -f "$lock_results" ]; then
        while read -r line; do
            if echo "$line" | grep -q "got_number"; then
                local num
                num=$(echo "$line" | cut -d: -f4)
                all_numbers+=("$num")
            fi
        done < "$lock_results"
    fi
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Lock race condition detected: $duplicate_count duplicates"
        return 1
    fi
    
    log "SUCCESS" "Lock race test: ${#all_numbers[@]} unique numbers, no lock races detected"
    return 0
}

# Test 3: State file corruption race condition
test_state_corruption_race() {
    log "INFO" "Test 3: State file corruption race condition"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init corruption_race >/dev/null 2>&1
    
    # Create race condition with state file writes
    local pids=()
    local corruption_results="$TEST_STATE_DIR/corruption_results.txt"
    
    for i in {1..10}; do
        (
            # Each process tries to create corruption
            for j in {1..5}; do
                # Try to get number
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get corruption_race 2>/dev/null | tail -1)
                
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "process_$i:attempt_$j:success:$num" >> "$corruption_results"
                else
                    echo "process_$i:attempt_$j:failed" >> "$corruption_results"
                fi
                
                # Small delay to increase race probability
                sleep 0.002
            done
        ) &
        pids+=($!)
    done
    
    # Wait for completion
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Verify state file integrity
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        # Check if JSON is valid
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "State file corruption detected: invalid JSON"
            return 1
        fi
        
        # Check for missing required fields
        local required_fields=("next_number" "assigned_numbers" "contexts")
        for field in "${required_fields[@]}"; do
            if ! grep -q "\"$field\"" "$state_file"; then
                log "ERROR" "State file corruption: missing field '$field'"
                return 1
            fi
        done
    else
        log "ERROR" "State file missing after race condition test"
        return 1
    fi
    
    # Check results for duplicates
    local all_numbers=()
    if [ -f "$corruption_results" ]; then
        while read -r line; do
            if echo "$line" | grep -q "success"; then
                local num
                num=$(echo "$line" | cut -d: -f4)
                all_numbers+=("$num")
            fi
        done < "$corruption_results"
    fi
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "State corruption race condition: $duplicate_count duplicates"
        return 1
    fi
    
    log "SUCCESS" "State corruption race test: ${#all_numbers[@]} unique numbers, state file intact"
    return 0
}

# Test 4: Simultaneous context race condition
test_simultaneous_context_race() {
    log "INFO" "Test 4: Simultaneous context race condition"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init context_race >/dev/null 2>&1
    
    # Create race condition with multiple contexts simultaneously
    local pids=()
    local context_results="$TEST_STATE_DIR/context_results.txt"
    local contexts=("ctx_A" "ctx_B" "ctx_C" "ctx_D")
    
    for ctx in "${contexts[@]}"; do
        for i in {1..5}; do
            (
                # Each process works with different context but simultaneously
                for j in {1..3}; do
                    local num
                    num=$("$NUMBER_MANAGER_SCRIPT" get "$ctx" 2>/dev/null | tail -1)
                    
                    if [ $? -eq 0 ] && [ -n "$num" ]; then
                        echo "context_$ctx:process_$i:attempt_$j:number_$num" >> "$context_results"
                    fi
                    
                    sleep 0.01
                done
            ) &
            pids+=($!)
        done
    done
    
    # Wait for completion
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Analyze cross-context duplicates
    local all_numbers=()
    if [ -f "$context_results" ]; then
        while read -r line; do
            local num
            num=$(echo "$line" | grep -o "number_[0-9]*" | cut -d_ -f2)
            if [ -n "$num" ]; then
                all_numbers+=("$num")
            fi
        done < "$context_results"
    fi
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Simultaneous context race condition: $duplicate_count cross-context duplicates"
        return 1
    fi
    
    log "SUCCESS" "Simultaneous context race test: ${#all_numbers[@]} unique numbers across contexts"
    return 0
}

# Test 5: Interrupted operation race condition
test_interrupted_operation_race() {
    log "INFO" "Test 5: Interrupted operation race condition"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init interrupt_race >/dev/null 2>&1
    
    # Create race condition by interrupting operations
    local pids=()
    local interrupt_results="$TEST_STATE_DIR/interrupt_results.txt"
    
    # Start processes that will be interrupted
    for i in {1..10}; do
        (
            # Process that can be interrupted
            trap 'echo "process_$i:interrupted" >> "$interrupt_results"; exit 0' TERM
            
            for j in {1..5}; do
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get interrupt_race 2>/dev/null | tail -1)
                
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "process_$i:attempt_$j:success:$num" >> "$interrupt_results"
                fi
                
                # Random chance of being interrupted
                if [ $((RANDOM % 20)) -eq 0 ]; then
                    sleep 0.1  # Give chance for interruption
                fi
            done
        ) &
        pids+=($!)
    done
    
    # Let them start, then interrupt some
    sleep 0.1
    for i in {1..3}; do
        if [ ${#pids[@]} -gt $i ]; then
            kill "${pids[$i]}" 2>/dev/null || true
        fi
    done
    
    # Wait for remaining processes
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Check for state consistency
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        # Verify JSON integrity
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "Interrupted operation caused state corruption"
            return 1
        fi
    fi
    
    # Check successful assignments for duplicates
    local all_numbers=()
    if [ -f "$interrupt_results" ]; then
        while read -r line; do
            if echo "$line" | grep -q "success"; then
                local num
                num=$(echo "$line" | cut -d: -f4)
                all_numbers+=("$num")
            fi
        done < "$interrupt_results"
    fi
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Interrupted operation race condition: $duplicate_count duplicates"
        return 1
    fi
    
    log "SUCCESS" "Interrupted operation race test: ${#all_numbers[@]} unique numbers, state consistent"
    return 0
}

# Test 6: Backup/restore race condition
test_backup_restore_race() {
    log "INFO" "Test 6: Backup/restore race condition"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init backup_race >/dev/null 2>&1
    
    # Create race condition during backup/restore operations
    local pids=()
    local backup_results="$TEST_STATE_DIR/backup_results.txt"
    
    # Process that continuously requests numbers
    (
        for i in {1..20}; do
            local num
            num=$("$NUMBER_MANAGER_SCRIPT" get backup_race 2>/dev/null | tail -1)
            
            if [ $? -eq 0 ] && [ -n "$num" ]; then
                echo "number_request:$num" >> "$backup_results"
            fi
            
            sleep 0.01
        done
    ) &
    local request_pid=$!
    
    # Process that triggers backup operations
    (
        for i in {1..5}; do
            # Force backup creation
            "$NUMBER_MANAGER_SCRIPT" backup backup_race >/dev/null 2>&1
            echo "backup_created:$i" >> "$backup_results"
            sleep 0.05
        done
    ) &
    local backup_pid=$!
    
    # Process that might trigger restore
    (
        sleep 0.1
        # Corrupt state to trigger restore
        local state_file="$TEST_STATE_DIR/.number_state/state.json"
        if [ -f "$state_file" ]; then
            cp "$state_file" "$state_file.bak"
            echo '{"corrupted": "data"}' > "$state_file"
            sleep 0.02
            mv "$state_file.bak" "$state_file"
        fi
        echo "restore_triggered" >> "$backup_results"
    ) &
    local restore_pid=$!
    
    # Wait for all processes
    wait "$request_pid" 2>/dev/null || true
    wait "$backup_pid" 2>/dev/null || true
    wait "$restore_pid" 2>/dev/null || true
    
    # Verify final state integrity
    local final_state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$final_state_file" ]; then
        if ! python3 -m json.tool "$final_state_file" >/dev/null 2>&1; then
            log "ERROR" "Backup/restore race condition corrupted final state"
            return 1
        fi
    fi
    
    # Check for duplicates in number requests
    local all_numbers=()
    if [ -f "$backup_results" ]; then
        while read -r line; do
            if echo "$line" | grep -q "number_request"; then
                local num
                num=$(echo "$line" | cut -d: -f2)
                all_numbers+=("$num")
            fi
        done < "$backup_results"
    fi
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Backup/restore race condition: $duplicate_count duplicates"
        return 1
    fi
    
    log "SUCCESS" "Backup/restore race test: ${#all_numbers[@]} unique numbers, state intact"
    return 0
}

# Run all race condition tests
run_all_race_condition_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_toctou_race_condition"
        "test_lock_race_condition"
        "test_state_corruption_race"
        "test_simultaneous_context_race"
        "test_interrupted_operation_race"
        "test_backup_restore_race"
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
    echo "Race Condition Detection Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All race condition detection tests passed!"
        return 0
    else
        log "ERROR" "Some race condition detection tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_race_condition_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests race condition detection and prevention mechanisms"
    exit 1
fi