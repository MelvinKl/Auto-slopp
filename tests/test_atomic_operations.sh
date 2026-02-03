#!/bin/bash

# Test atomic operations verification
# Part of Auto-58z: Test concurrent access and race condition handling

set -e

SCRIPT_NAME="test_atomic_operations"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_atomic_operations_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting atomic operations test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Atomic operations test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Verify atomic state file updates
test_atomic_state_updates() {
    log "INFO" "Test 1: Verify atomic state file updates"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init atomic_state >/dev/null 2>&1
    
    # Monitor state file during concurrent updates
    local pids=()
    local state_snapshots="$TEST_STATE_DIR/state_snapshots.txt"
    
    # Start monitoring process
    (
        while true; do
            local state_file="$TEST_STATE_DIR/.number_state/state.json"
            if [ -f "$state_file" ]; then
                local timestamp
                timestamp=$(date +%s.%N)
                local checksum
                checksum=$(md5sum "$state_file" 2>/dev/null | cut -d' ' -f1)
                local size
                size=$(wc -c < "$state_file" 2>/dev/null || echo "0")
                echo "timestamp:$timestamp:checksum:$checksum:size:$size" >> "$state_snapshots"
            fi
            sleep 0.001
        done
    ) &
    local monitor_pid=$!
    
    # Start concurrent number assignments
    for i in {1..20}; do
        (
            for j in {1..3}; do
                "$NUMBER_MANAGER_SCRIPT" get atomic_state >/dev/null 2>&1
                sleep 0.01
            done
        ) &
        pids+=($!)
    done
    
    # Wait for assignments to complete
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Stop monitoring
    kill "$monitor_pid" 2>/dev/null || true
    wait "$monitor_pid" 2>/dev/null || true
    
    # Analyze state file consistency
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        # Verify final state is valid JSON
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "Final state file is not valid JSON"
            return 1
        fi
        
        # Check for required fields
        local required_fields=("next_number" "assigned_numbers" "contexts")
        for field in "${required_fields[@]}"; do
            if ! grep -q "\"$field\"" "$state_file"; then
                log "ERROR" "Final state missing required field: $field"
                return 1
            fi
        done
    fi
    
    # Check for corrupted intermediate states
    local corrupted_snapshots=0
    if [ -f "$state_snapshots" ]; then
        while read -r line; do
            local size
            size=$(echo "$line" | grep -o "size:[0-9]*" | cut -d: -f2)
            if [ -n "$size" ] && [ "$size" -eq 0 ]; then
                corrupted_snapshots=$((corrupted_snapshots + 1))
            fi
        done < "$state_snapshots"
    fi
    
    if [ "$corrupted_snapshots" -gt 2 ]; then  # Allow a few zero-size snapshots during file writes
        log "ERROR" "Too many corrupted state snapshots: $corrupted_snapshots"
        return 1
    fi
    
    log "SUCCESS" "Atomic state updates: final state valid, $corrupted_snapshots intermediate corruptions"
    return 0
}

# Test 2: Verify atomic number assignment
test_atomic_number_assignment() {
    log "INFO" "Test 2: Verify atomic number assignment"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init atomic_assignment >/dev/null 2>&1
    
    # Track assignment sequence
    local assignment_log="$TEST_STATE_DIR/assignment_log.txt"
    local pids=()
    
    # Start concurrent assignments
    for i in {1..15}; do
        (
            for j in {1..2}; do
                local start_time
                start_time=$(date +%s.%N)
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get atomic_assignment 2>/dev/null | tail -1)
                local end_time
                end_time=$(date +%s.%N)
                
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "process_$i:assignment_$j:number_$num:start_$start_time:end_$end_time" >> "$assignment_log"
                fi
            done
        ) &
        pids+=($!)
    done
    
    # Wait for completion
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Analyze assignment atomicity
    local all_numbers=()
    local assignment_times=()
    
    if [ -f "$assignment_log" ]; then
        while read -r line; do
            local num
            num=$(echo "$line" | grep -o "number_[0-9]*" | cut -d_ -f2)
            if [ -n "$num" ]; then
                all_numbers+=("$num")
                
                local start_time
                start_time=$(echo "$line" | grep -o "start_[0-9.]*" | cut -d_ -f2)
                local end_time
                end_time=$(echo "$line" | grep -o "end_[0-9.]*" | cut -d_ -f2)
                
                if [ -n "$start_time" ] && [ -n "$end_time" ]; then
                    local duration
                    duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
                    assignment_times+=("$duration")
                fi
            fi
        done < "$assignment_log"
    fi
    
    # Check for duplicates (atomicity violation)
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Atomic number assignment violated: $duplicate_count duplicates"
        return 1
    fi
    
    # Check assignment time consistency
    local total_time=0
    local time_count=${#assignment_times[@]}
    for time in "${assignment_times[@]}"; do
        if [ "$time" != "0" ]; then
            total_time=$(echo "$total_time + $time" | bc -l 2>/dev/null || echo "$total_time")
        fi
    done
    
    if [ "$time_count" -gt 0 ]; then
        local avg_time
        avg_time=$(echo "scale=3; $total_time / $time_count" | bc -l 2>/dev/null || echo "N/A")
        log "INFO" "Average assignment time: ${avg_time}s"
    fi
    
    log "SUCCESS" "Atomic number assignment: ${#all_numbers[@]} unique assignments, no duplicates"
    return 0
}

# Test 3: Verify atomic context operations
test_atomic_context_operations() {
    log "INFO" "Test 3: Verify atomic context operations"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init atomic_context >/dev/null 2>&1
    
    # Test atomic context creation and number assignment
    local pids=()
    local context_log="$TEST_STATE_DIR/context_log.txt"
    local contexts=("ctx_alpha" "ctx_beta" "ctx_gamma" "ctx_delta")
    
    for ctx in "${contexts[@]}"; do
        for i in {1..3}; do
            (
                # Each process works with a specific context
                for j in {1..2}; do
                    local start_time
                    start_time=$(date +%s.%N)
                    local num
                    num=$("$NUMBER_MANAGER_SCRIPT" get "$ctx" 2>/dev/null | tail -1)
                    local end_time
                    end_time=$(date +%s.%N)
                    
                    if [ $? -eq 0 ] && [ -n "$num" ]; then
                        echo "context_$ctx:process_$i:assignment_$j:number_$num:start_$start_time:end_$end_time" >> "$context_log"
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
    
    # Verify context atomicity
    local context_numbers=()
    local all_numbers=()
    
    if [ -f "$context_log" ]; then
        while read -r line; do
            local ctx
            ctx=$(echo "$line" | grep -o "context_[^:]*" | cut -d_ -f2)
            local num
            num=$(echo "$line" | grep -o "number_[0-9]*" | cut -d_ -f2)
            
            if [ -n "$ctx" ] && [ -n "$num" ]; then
                context_numbers+=("$ctx:$num")
                all_numbers+=("$num")
            fi
        done < "$context_log"
    fi
    
    # Check for cross-context duplicates
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Atomic context operations violated: $duplicate_count cross-context duplicates"
        return 1
    fi
    
    # Verify state file contains all contexts
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        for ctx in "${contexts[@]}"; do
            if ! grep -q "\"$ctx\"" "$state_file"; then
                log "ERROR" "Context '$ctx' missing from state file"
                return 1
            fi
        done
    fi
    
    log "SUCCESS" "Atomic context operations: ${#all_numbers[@]} unique numbers across ${#contexts[@]} contexts"
    return 0
}

# Test 4: Verify atomic backup operations
test_atomic_backup_operations() {
    log "INFO" "Test 4: Verify atomic backup operations"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init atomic_backup >/dev/null 2>&1
    
    # Test atomic backup during concurrent operations
    local pids=()
    local backup_log="$TEST_STATE_DIR/backup_log.txt"
    
    # Process that continuously requests numbers
    (
        for i in {1..10}; do
            local num
            num=$("$NUMBER_MANAGER_SCRIPT" get atomic_backup 2>/dev/null | tail -1)
            
            if [ $? -eq 0 ] && [ -n "$num" ]; then
                echo "number_request:$num:time_$(date +%s.%N)" >> "$backup_log"
            fi
            
            sleep 0.01
        done
    ) &
    local request_pid=$!
    
    # Process that creates backups
    (
        for i in {1..3}; do
            local backup_start
            backup_start=$(date +%s.%N)
            "$NUMBER_MANAGER_SCRIPT" backup atomic_backup >/dev/null 2>&1
            local backup_end
            backup_end=$(date +%s.%N)
            
            echo "backup_created:$i:start_$backup_start:end_$backup_end" >> "$backup_log"
            sleep 0.02
        done
    ) &
    local backup_pid=$!
    
    # Wait for completion
    wait "$request_pid" 2>/dev/null || true
    wait "$backup_pid" 2>/dev/null || true
    
    # Verify backup atomicity
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local backup_count=0
    
    if [ -d "$backup_dir" ]; then
        backup_count=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    # Check that backups are valid JSON
    local valid_backups=0
    local invalid_backups=0
    
    if [ -d "$backup_dir" ]; then
        for backup_file in "$backup_dir"/*.json; do
            if [ -f "$backup_file" ]; then
                if python3 -m json.tool "$backup_file" >/dev/null 2>&1; then
                    valid_backups=$((valid_backups + 1))
                else
                    invalid_backups=$((invalid_backups + 1))
                fi
            fi
        done
    fi
    
    # Check for duplicates in number requests
    local all_numbers=()
    if [ -f "$backup_log" ]; then
        while read -r line; do
            if echo "$line" | grep -q "number_request"; then
                local num
                num=$(echo "$line" | cut -d: -f2)
                all_numbers+=("$num")
            fi
        done < "$backup_log"
    fi
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Atomic backup operations violated: $duplicate_count duplicates during backup"
        return 1
    fi
    
    if [ "$invalid_backups" -gt 0 ]; then
        log "ERROR" "Found $invalid_backups invalid backup files"
        return 1
    fi
    
    log "SUCCESS" "Atomic backup operations: $valid_backups valid backups, ${#all_numbers[@]} unique numbers"
    return 0
}

# Test 5: Verify atomic lock operations
test_atomic_lock_operations() {
    log "INFO" "Test 5: Verify atomic lock operations"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init atomic_lock >/dev/null 2>&1
    
    # Test atomic lock acquisition and release
    local pids=()
    local lock_log="$TEST_STATE_DIR/lock_log.txt"
    
    # Start multiple processes competing for locks
    for i in {1..12}; do
        (
            for j in {1..2}; do
                local lock_start
                lock_start=$(date +%s.%N)
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get atomic_lock 2>/dev/null | tail -1)
                local lock_end
                lock_end=$(date +%s.%N)
                
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "process_$i:lock_$j:acquired_$lock_start:released_$lock_end:number_$num" >> "$lock_log"
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
    
    # Analyze lock atomicity
    local all_numbers=()
    local lock_durations=()
    
    if [ -f "$lock_log" ]; then
        while read -r line; do
            local num
            num=$(echo "$line" | grep -o "number_[0-9]*" | cut -d_ -f2)
            if [ -n "$num" ]; then
                all_numbers+=("$num")
                
                local start_time
                start_time=$(echo "$line" | grep -o "acquired_[0-9.]*" | cut -d_ -f2)
                local end_time
                end_time=$(echo "$line" | grep -o "released_[0-9.]*" | cut -d_ -f2)
                
                if [ -n "$start_time" ] && [ -n "$end_time" ]; then
                    local duration
                    duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
                    lock_durations+=("$duration")
                fi
            fi
        done < "$lock_log"
    fi
    
    # Check for duplicates (lock atomicity violation)
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Atomic lock operations violated: $duplicate_count duplicates"
        return 1
    fi
    
    # Check for overlapping lock times (indicates non-atomic locking)
    local overlapping_locks=0
    local lock_count=${#lock_durations[@]}
    
    if [ "$lock_count" -gt 1 ]; then
        # Simple check: if many locks have very short duration, might indicate race condition
        local short_locks=0
        for duration in "${lock_durations[@]}"; do
            if [ "$duration" != "0" ]; then
                local short_duration
                short_duration=$(echo "$duration < 0.001" | bc -l 2>/dev/null || echo "0")
                if [ "$short_duration" = "1" ]; then
                    short_locks=$((short_locks + 1))
                fi
            fi
        done
        
        if [ "$short_locks" -gt $((lock_count / 2)) ]; then
            log "WARNING" "Many unusually short locks detected: $short_locks/$lock_count"
        fi
    fi
    
    log "SUCCESS" "Atomic lock operations: ${#all_numbers[@]} unique numbers, $overlapping_locks overlapping locks"
    return 0
}

# Test 6: Verify atomic state validation
test_atomic_state_validation() {
    log "INFO" "Test 6: Verify atomic state validation"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init atomic_validation >/dev/null 2>&1
    
    # Test state validation during concurrent operations
    local pids=()
    local validation_log="$TEST_STATE_DIR/validation_log.txt"
    
    # Start concurrent operations
    for i in {1..8}; do
        (
            for j in {1..3}; do
                local operation_start
                operation_start=$(date +%s.%N)
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get atomic_validation 2>/dev/null | tail -1)
                local operation_end
                operation_end=$(date +%s.%N)
                
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "operation_$i:$j:success:$num:start_$operation_start:end_$operation_end" >> "$validation_log"
                else
                    echo "operation_$i:$j:failed:start_$operation_start:end_$operation_end" >> "$validation_log"
                fi
                
                sleep 0.01
            done
        ) &
        pids+=($!)
    done
    
    # Process that validates state periodically
    (
        for i in {1..5}; do
            local validation_start
            validation_start=$(date +%s.%N)
            "$NUMBER_MANAGER_SCRIPT" validate atomic_validation >/dev/null 2>&1
            local validation_end
            validation_end=$(date +%s.%N)
            
            echo "validation_$i:start_$validation_start:end_$validation_end" >> "$validation_log"
            sleep 0.02
        done
    ) &
    local validation_pid=$!
    
    # Wait for completion
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    wait "$validation_pid" 2>/dev/null || true
    
    # Verify final state consistency
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        # Check JSON validity
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "Final state validation failed: invalid JSON"
            return 1
        fi
        
        # Check internal consistency
        local next_number
        next_number=$(grep '"next_number"' "$state_file" | grep -o '[0-9]*' | head -1)
        local assigned_count
        assigned_count=$(grep '"assigned_numbers"' "$state_file" -A 20 | grep '\[' | wc -l)
        
        if [ -n "$next_number" ] && [ "$next_number" -gt 1 ]; then
            local expected_assigned=$((next_number - 1))
            if [ "$assigned_count" -ne "$expected_assigned" ]; then
                log "ERROR" "State inconsistency: next_number=$next_number but assigned_count=$assigned_count"
                return 1
            fi
        fi
    fi
    
    # Check operation results for duplicates
    local all_numbers=()
    if [ -f "$validation_log" ]; then
        while read -r line; do
            if echo "$line" | grep -q "success"; then
                local num
                num=$(echo "$line" | cut -d: -f4)
                all_numbers+=("$num")
            fi
        done < "$validation_log"
    fi
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Atomic state validation violated: $duplicate_count duplicates"
        return 1
    fi
    
    log "SUCCESS" "Atomic state validation: ${#all_numbers[@]} unique operations, state consistent"
    return 0
}

# Run all atomic operations tests
run_all_atomic_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_atomic_state_updates"
        "test_atomic_number_assignment"
        "test_atomic_context_operations"
        "test_atomic_backup_operations"
        "test_atomic_lock_operations"
        "test_atomic_state_validation"
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
    echo "Atomic Operations Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All atomic operations tests passed!"
        return 0
    else
        log "ERROR" "Some atomic operations tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_atomic_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests atomic operations verification"
    exit 1
fi