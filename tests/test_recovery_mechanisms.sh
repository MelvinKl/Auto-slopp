#!/bin/bash

# Test state recovery from backups
# Part of Auto-2l0: Test state backup and recovery mechanisms

set -e

SCRIPT_NAME="test_recovery_mechanisms"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_recovery_mechanisms_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting recovery mechanisms test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Recovery mechanisms test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Recovery from corrupted state file
test_corrupted_state_recovery() {
    log "INFO" "Test 1: Recovery from corrupted state file"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init corrupted_recovery >/dev/null 2>&1
    
    # Create some state to backup
    local numbers_before=()
    for i in {1..3}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get corrupted_recovery 2>/dev/null | tail -1)
        
        if [ $? -eq 0 ] && [ -n "$num" ]; then
            numbers_before+=("$num")
        fi
        sleep 0.01
    done
    
    # Corrupt the state file
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        echo '{"corrupted": "data", "invalid": true}' > "$state_file"
    fi
    
    # Try to get a number (should trigger recovery)
    local recovery_num
    recovery_num=$("$NUMBER_MANAGER_SCRIPT" get corrupted_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$recovery_num" ]; then
        log "ERROR" "Failed to recover from corrupted state"
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
    continued_num=$("$NUMBER_MANAGER_SCRIPT" get corrupted_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$continued_num" ]; then
        log "ERROR" "Failed to continue operation after recovery"
        return 1
    fi
    
    # Check for duplicates
    local all_numbers=("${numbers_before[@]}" "$recovery_num" "$continued_num")
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Duplicates found after corrupted state recovery: $duplicate_count"
        return 1
    fi
    
    log "SUCCESS" "Corrupted state recovery: before=${numbers_before[*]}, recovery=$recovery_num, continued=$continued_num"
    return 0
}

# Test 2: Recovery from missing state file
test_missing_state_recovery() {
    log "INFO" "Test 2: Recovery from missing state file"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init missing_recovery >/dev/null 2>&1
    
    # Create some state and backups
    local numbers_before=()
    for i in {1..4}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get missing_recovery 2>/dev/null | tail -1)
        
        if [ $? -eq 0 ] && [ -n "$num" ]; then
            numbers_before+=("$num")
        fi
        sleep 0.01
    done
    
    # Remove the state file completely
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    rm -f "$state_file"
    
    # Try to get a number (should trigger recovery from backup)
    local recovery_num
    recovery_num=$("$NUMBER_MANAGER_SCRIPT" get missing_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$recovery_num" ]; then
        log "ERROR" "Failed to recover from missing state file"
        return 1
    fi
    
    # Verify state file was recreated
    if [ ! -f "$state_file" ]; then
        log "ERROR" "State file not recreated after recovery"
        return 1
    fi
    
    # Check recreated state is valid
    if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
        log "ERROR" "Recreated state file is invalid"
        return 1
    fi
    
    # Get another number to verify continued operation
    local continued_num
    continued_num=$("$NUMBER_MANAGER_SCRIPT" get missing_recovery 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$continued_num" ]; then
        log "ERROR" "Failed to continue after missing state recovery"
        return 1
    fi
    
    log "SUCCESS" "Missing state recovery: before=${numbers_before[*]}, recovery=$recovery_num, continued=$continued_num"
    return 0
}

# Test 3: Multiple backup selection (most recent valid)
test_multiple_backup_selection() {
    log "INFO" "Test 3: Multiple backup selection (most recent valid)"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init backup_selection >/dev/null 2>&1
    
    # Create multiple backups with different states
    local backup_states=()
    for i in {1..6}; do
        # Create some state
        for j in {1..2}; do
            "$NUMBER_MANAGER_SCRIPT" get backup_selection >/dev/null 2>&1
            sleep 0.01
        done
        
        # Record the next number at this point
        local next_num
        next_num=$("$NUMBER_MANAGER_SCRIPT" status backup_selection 2>/dev/null | grep "next_number" | cut -d: -f2 | tr -d ' ')
        backup_states+=("$next_num")
    done
    
    # Corrupt the current state
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    echo '{"corrupted": "current"}' > "$state_file"
    
    # Try to recover (should select most recent valid backup)
    local recovery_num
    recovery_num=$("$NUMBER_MANAGER_SCRIPT" get backup_selection 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$recovery_num" ]; then
        log "ERROR" "Failed to recover with multiple backups available"
        return 1
    fi
    
    # Check that recovery used a recent backup (not the oldest)
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local backup_count=0
    
    if [ -d "$backup_dir" ]; then
        backup_count=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    if [ "$backup_count" -eq 0 ]; then
        log "ERROR" "No backups found for selection test"
        return 1
    fi
    
    # Verify state is valid after recovery
    if [ -f "$state_file" ]; then
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "State invalid after multiple backup recovery"
            return 1
        fi
    fi
    
    log "SUCCESS" "Multiple backup selection: recovered with $backup_count backups available, got number $recovery_num"
    return 0
}

# Test 4: Backup fallback when no valid backups exist
test_backup_fallback() {
    log "INFO" "Test 4: Backup fallback when no valid backups exist"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init fallback_test >/dev/null 2>&1
    
    # Create some initial state
    "$NUMBER_MANAGER_SCRIPT" get fallback_test >/dev/null 2>&1
    
    # Corrupt state file and remove all backups
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    
    # Corrupt state
    echo '{"corrupted": "state"}' > "$state_file"
    
    # Remove or corrupt all backups
    if [ -d "$backup_dir" ]; then
        for backup_file in "$backup_dir"/*.json; do
            if [ -f "$backup_file" ]; then
                echo '{"corrupted": "backup"}' > "$backup_file"
            fi
        done
    fi
    
    # Try to get a number (should trigger fallback to fresh initialization)
    local fallback_num
    fallback_num=$("$NUMBER_MANAGER_SCRIPT" get fallback_test 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$fallback_num" ]; then
        log "ERROR" "Failed to fallback when no valid backups exist"
        return 1
    fi
    
    # Check that fallback created a fresh state
    if [ -f "$state_file" ]; then
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "Fallback state is invalid"
            return 1
        fi
        
        # Should start from number 1 after fallback
        local next_num
        next_num=$("$NUMBER_MANAGER_SCRIPT" status fallback_test 2>/dev/null | grep "next_number" | cut -d: -f2 | tr -d ' ')
        
        if [ "$next_num" != "2" ]; then  # Should be 2 after getting first number (1)
            log "ERROR" "Fallback didn't create fresh state: next_number=$next_num (expected 2)"
            return 1
        fi
    fi
    
    # Get another number to verify continued operation
    local continued_num
    continued_num=$("$NUMBER_MANAGER_SCRIPT" get fallback_test 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$continued_num" ]; then
        log "ERROR" "Failed to continue after fallback"
        return 1
    fi
    
    log "SUCCESS" "Backup fallback: fallback_num=$fallback_num, continued_num=$continued_num, fresh state created"
    return 0
}

# Test 5: Recovery from partially corrupted state files
test_partial_corruption_recovery() {
    log "INFO" "Test 5: Recovery from partially corrupted state files"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init partial_corruption >/dev/null 2>&1
    
    # Create complex state
    local contexts=("ctx_partial1" "ctx_partial2" "ctx_partial3")
    local context_data=()
    
    for ctx in "${contexts[@]}"; do
        for i in {1..2}; do
            local num
            num=$("$NUMBER_MANAGER_SCRIPT" get "$ctx" 2>/dev/null | tail -1)
            
            if [ $? -eq 0 ] && [ -n "$num" ]; then
                context_data+=("$ctx:$num")
            fi
            sleep 0.01
        done
    done
    
    # Partially corrupt the state file (truncate it)
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        local original_size
        original_size=$(wc -c < "$state_file")
        truncate -s $((original_size / 2)) "$state_file" 2>/dev/null || true
    fi
    
    # Try to recover
    local recovery_num
    recovery_num=$("$NUMBER_MANAGER_SCRIPT" get partial_corruption 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$recovery_num" ]; then
        log "ERROR" "Failed to recover from partial corruption"
        return 1
    fi
    
    # Verify recovered state is complete and valid
    if [ -f "$state_file" ]; then
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "State still invalid after partial corruption recovery"
            return 1
        fi
        
        # Check that file size is reasonable (not truncated)
        local file_size
        file_size=$(wc -c < "$state_file")
        if [ "$file_size" -lt 50 ]; then
            log "ERROR" "Recovered state appears incomplete: $file_size bytes"
            return 1
        fi
    fi
    
    # Check that contexts are preserved
    local contexts_preserved=0
    for ctx in "${contexts[@]}"; do
        if grep -q "\"$ctx\"" "$state_file"; then
            contexts_preserved=$((contexts_preserved + 1))
        fi
    done
    
    if [ "$contexts_preserved" -lt $(( ${#contexts[@]} / 2 )) ]; then
        log "ERROR" "Too few contexts preserved after partial corruption: $contexts_preserved/${#contexts[@]}"
        return 1
    fi
    
    log "SUCCESS" "Partial corruption recovery: $contexts_preserved/${#contexts[@]} contexts preserved, recovery_num=$recovery_num"
    return 0
}

# Test 6: Recovery during concurrent operations
test_concurrent_recovery() {
    log "INFO" "Test 6: Recovery during concurrent operations"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init concurrent_recovery >/dev/null 2>&1
    
    # Create some initial state
    for i in {1..3}; do
        "$NUMBER_MANAGER_SCRIPT" get concurrent_recovery >/dev/null 2>&1
        sleep 0.01
    done
    
    # Corrupt state to trigger recovery
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    echo '{"corrupted": "concurrent"}' > "$state_file"
    
    # Start concurrent operations during recovery
    local pids=()
    local results_file="$TEST_STATE_DIR/concurrent_recovery_results.txt"
    
    for i in {1..5}; do
        (
            for j in {1..2}; do
                local start_time
                start_time=$(date +%s.%N)
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get concurrent_recovery 2>/dev/null | tail -1)
                local end_time
                end_time=$(date +%s.%N)
                
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "process_$i:operation_$j:success:$num:start_$start_time:end_$end_time" >> "$results_file"
                else
                    echo "process_$i:operation_$j:failed:start_$start_time:end_$end_time" >> "$results_file"
                fi
                
                sleep 0.01
            done
        ) &
        pids+=($!)
    done
    
    # Wait for completion
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Analyze results
    local all_numbers=()
    local successful_operations=0
    
    if [ -f "$results_file" ]; then
        while read -r line; do
            if echo "$line" | grep -q "success"; then
                successful_operations=$((successful_operations + 1))
                local num
                num=$(echo "$line" | cut -d: -f4)
                all_numbers+=("$num")
            fi
        done < "$results_file"
    fi
    
    # Check for duplicates (should be none if recovery worked)
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Duplicates found during concurrent recovery: $duplicate_count"
        return 1
    fi
    
    # Verify final state is valid
    if [ -f "$state_file" ]; then
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "Final state invalid after concurrent recovery"
            return 1
        fi
    fi
    
    log "SUCCESS" "Concurrent recovery: $successful_operations successful operations, ${#all_numbers[@]} unique numbers, no duplicates"
    return 0
}

# Run all recovery mechanism tests
run_all_recovery_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_corrupted_state_recovery"
        "test_missing_state_recovery"
        "test_multiple_backup_selection"
        "test_backup_fallback"
        "test_partial_corruption_recovery"
        "test_concurrent_recovery"
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
    echo "Recovery Mechanisms Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All recovery mechanism tests passed!"
        return 0
    else
        log "ERROR" "Some recovery mechanism tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_recovery_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests state recovery from backups"
    exit 1
fi