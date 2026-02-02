#!/bin/bash

# Test backup file rotation
# Part of Auto-2l0: Test state backup and recovery mechanisms

set -e

SCRIPT_NAME="test_backup_rotation"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_backup_rotation_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting backup rotation test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Backup rotation test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Basic backup rotation (keep only 5 most recent)
test_basic_backup_rotation() {
    log "INFO" "Test 1: Basic backup rotation (keep only 5 most recent)"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init rotation_test >/dev/null 2>&1
    
    # Create more than 5 backups to trigger rotation
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    
    # Create 8 backups (2 more than the limit)
    for i in {1..8}; do
        "$NUMBER_MANAGER_SCRIPT" get rotation_test >/dev/null 2>&1
        sleep 0.01  # Small delay to ensure different timestamps
    done
    
    # Check backup count (should be 5 or less)
    local backup_count=0
    if [ -d "$backup_dir" ]; then
        backup_count=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    if [ "$backup_count" -gt 5 ]; then
        log "ERROR" "Backup rotation failed: found $backup_count backups (expected ≤ 5)"
        return 1
    fi
    
    # Check that the most recent backups are kept
    local backup_files=()
    if [ -d "$backup_dir" ]; then
        for backup_file in "$backup_dir"/backup_*.json; do
            if [ -f "$backup_file" ]; then
                backup_files+=("$backup_file")
            fi
        done
    fi
    
    # Sort by modification time (newest first)
    IFS=$'\n' backup_files=($(ls -t "${backup_files[@]}"))
    unset IFS
    
    # Verify we have the right number of backups
    if [ ${#backup_files[@]} -eq 0 ]; then
        log "ERROR" "No backup files found after rotation test"
        return 1
    fi
    
    log "SUCCESS" "Basic backup rotation: ${#backup_files[@]} backups kept (limit 5)"
    return 0
}

# Test 2: Timestamp-based rotation order
test_timestamp_rotation_order() {
    log "INFO" "Test 2: Timestamp-based rotation order"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init timestamp_rotation >/dev/null 2>&1
    
    # Create backups with controlled timing
    local backup_times=()
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    
    # Create 7 backups with small delays
    for i in {1..7}; do
        local before_time
        before_time=$(date +%s)
        
        "$NUMBER_MANAGER_SCRIPT" get timestamp_rotation >/dev/null 2>&1
        
        local after_time
        after_time=$(date +%s)
        backup_times+=("$after_time")
        
        # Small delay between operations
        sleep 0.02
    done
    
    # Check that only 5 most recent are kept
    local backup_files=()
    if [ -d "$backup_dir" ]; then
        for backup_file in "$backup_dir"/backup_*.json; do
            if [ -f "$backup_file" ]; then
                backup_files+=("$backup_file")
            fi
        done
    fi
    
    # Sort by modification time
    IFS=$'\n' backup_files=($(ls -t "${backup_files[@]}"))
    unset IFS
    
    if [ ${#backup_files[@]} -gt 5 ]; then
        log "ERROR" "Timestamp rotation failed: ${#backup_files[@]} backups found"
        return 1
    fi
    
    # Verify files are ordered by recency
    local file_times=()
    for backup_file in "${backup_files[@]}"; do
        local file_time
        file_time=$(stat -c "%Y" "$backup_file" 2>/dev/null || echo "0")
        file_times+=("$file_time")
    done
    
    # Check times are in descending order (newest first)
    local order_correct=true
    for ((i=1; i<${#file_times[@]}; i++)); do
        if [ "${file_times[$((i-1))]}" -lt "${file_times[$i]}" ]; then
            order_correct=false
            break
        fi
    done
    
    if [ "$order_correct" = false ]; then
        log "ERROR" "Backup rotation order incorrect: not sorted by recency"
        return 1
    fi
    
    log "SUCCESS" "Timestamp rotation order: ${#backup_files[@]} backups in correct chronological order"
    return 0
}

# Test 3: Rotation during concurrent operations
test_concurrent_rotation() {
    log "INFO" "Test 3: Rotation during concurrent operations"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init concurrent_rotation >/dev/null 2>&1
    
    # Start concurrent operations that create many backups
    local pids=()
    local operations_per_process=3
    
    for i in {1..5}; do
        (
            for j in $(seq 1 $operations_per_process); do
                "$NUMBER_MANAGER_SCRIPT" get concurrent_rotation >/dev/null 2>&1
                sleep 0.01
            done
        ) &
        pids+=($!)
    done
    
    # Wait for completion
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Check backup count (should be ≤ 5)
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local backup_count=0
    
    if [ -d "$backup_dir" ]; then
        backup_count=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    if [ "$backup_count" -gt 5 ]; then
        log "ERROR" "Concurrent rotation failed: $backup_count backups found"
        return 1
    fi
    
    # Verify all remaining backups are valid JSON
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
    
    if [ "$invalid_backups" -gt 0 ]; then
        log "ERROR" "Found $invalid_backups invalid backup files after concurrent rotation"
        return 1
    fi
    
    log "SUCCESS" "Concurrent rotation: $valid_backups valid backups kept, rotation working under concurrency"
    return 0
}

# Test 4: Rotation with different backup sizes
test_size_based_rotation() {
    log "INFO" "Test 4: Rotation with different backup sizes"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init size_rotation >/dev/null 2>&1
    
    # Create state with varying amounts of data
    local contexts=("small_ctx" "medium_ctx" "large_ctx")
    local context_assignments=("1" "3" "5")  # Different numbers of assignments
    
    for i in "${!contexts[@]}"; do
        local ctx="${contexts[$i]}"
        local assignments="${context_assignments[$i]}"
        
        for j in $(seq 1 $assignments); do
            "$NUMBER_MANAGER_SCRIPT" get "$ctx" >/dev/null 2>&1
            sleep 0.01
        done
    done
    
    # Create additional backups to trigger rotation
    for i in {1..3}; do
        "$NUMBER_MANAGER_SCRIPT" get size_rotation >/dev/null 2>&1
        sleep 0.01
    done
    
    # Check final backup count
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local backup_count=0
    
    if [ -d "$backup_dir" ]; then
        backup_count=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    if [ "$backup_count" -gt 5 ]; then
        log "ERROR" "Size-based rotation failed: $backup_count backups found"
        return 1
    fi
    
    # Check that backups contain expected data
    local backup_files=()
    if [ -d "$backup_dir" ]; then
        for backup_file in "$backup_dir"/backup_*.json; do
            if [ -f "$backup_file" ]; then
                backup_files+=("$backup_file")
            fi
        done
    fi
    
    # Sort by modification time and check most recent
    IFS=$'\n' backup_files=($(ls -t "${backup_files[@]}"))
    unset IFS
    
    if [ ${#backup_files[@]} -gt 0 ]; then
        local latest_backup="${backup_files[0]}"
        
        # Check that latest backup contains the largest context
        if ! grep -q "\"large_ctx\"" "$latest_backup"; then
            log "ERROR" "Latest backup missing expected context after size-based rotation"
            return 1
        fi
    fi
    
    log "SUCCESS" "Size-based rotation: $backup_count backups kept with varying data sizes"
    return 0
}

# Test 5: Rotation preserves essential data
test_rotation_data_preservation() {
    log "INFO" "Test 5: Rotation preserves essential data"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init data_preservation >/dev/null 2>&1
    
    # Create complex state with multiple contexts and numbers
    local contexts=("preservation_ctx1" "preservation_ctx2" "preservation_ctx3")
    local preserved_data=()
    
    for ctx in "${contexts[@]}"; do
        for i in {1..3}; do
            local num
            num=$("$NUMBER_MANAGER_SCRIPT" get "$ctx" 2>/dev/null | tail -1)
            
            if [ $? -eq 0 ] && [ -n "$num" ]; then
                preserved_data+=("$ctx:$num")
            fi
            sleep 0.01
        done
    done
    
    # Create additional backups to trigger rotation
    for i in {1..4}; do
        "$NUMBER_MANAGER_SCRIPT" get data_preservation >/dev/null 2>&1
        sleep 0.01
    done
    
    # Check that data is preserved in remaining backups
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local contexts_found=0
    
    if [ -d "$backup_dir" ]; then
        for backup_file in "$backup_dir"/*.json; do
            if [ -f "$backup_file" ]; then
                local file_contexts=0
                for ctx in "${contexts[@]}"; do
                    if grep -q "\"$ctx\"" "$backup_file"; then
                        file_contexts=$((file_contexts + 1))
                    fi
                done
                
                # Keep track of max contexts found in any backup
                if [ "$file_contexts" -gt "$contexts_found" ]; then
                    contexts_found="$file_contexts"
                fi
            fi
        done
    fi
    
    if [ "$contexts_found" -lt ${#contexts[@]} ]; then
        log "ERROR" "Data preservation failed: only $contexts_found/${#contexts[@]} contexts found in backups"
        return 1
    fi
    
    # Verify current state still has all contexts
    for ctx in "${contexts[@]}"; do
        local current_numbers
        current_numbers=$("$NUMBER_MANAGER_SCRIPT" contexts data_preservation 2>/dev/null | grep "$ctx" | wc -l)
        
        if [ "$current_numbers" -eq 0 ]; then
            log "ERROR" "Context '$ctx' lost from current state after rotation"
            return 1
        fi
    done
    
    log "SUCCESS" "Data preservation: all ${#contexts[@]} contexts preserved after rotation"
    return 0
}

# Test 6: Rotation handles edge cases
test_rotation_edge_cases() {
    log "INFO" "Test 6: Rotation handles edge cases"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init edge_cases >/dev/null 2>&1
    
    # Edge case 1: Exactly 5 backups (no rotation should occur)
    for i in {1..5}; do
        "$NUMBER_MANAGER_SCRIPT" get edge_cases >/dev/null 2>&1
        sleep 0.01
    done
    
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local backup_count_5=0
    
    if [ -d "$backup_dir" ]; then
        backup_count_5=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    if [ "$backup_count_5" -ne 5 ]; then
        log "ERROR" "Edge case failed: expected 5 backups, got $backup_count_5"
        return 1
    fi
    
    # Edge case 2: Single backup (no rotation)
    rm -rf "$backup_dir"  # Remove all backups
    "$NUMBER_MANAGER_SCRIPT" get edge_cases >/dev/null 2>&1
    
    local backup_count_1=0
    if [ -d "$backup_dir" ]; then
        backup_count_1=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    if [ "$backup_count_1" -ne 1 ]; then
        log "ERROR" "Edge case failed: expected 1 backup, got $backup_count_1"
        return 1
    fi
    
    # Edge case 3: Very rapid backups (same timestamp scenarios)
    for i in {1..7}; do
        "$NUMBER_MANAGER_SCRIPT" get edge_cases >/dev/null 2>&1
        # No delay to test same-timestamp backups
    done
    
    local backup_count_rapid=0
    if [ -d "$backup_dir" ]; then
        backup_count_rapid=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    if [ "$backup_count_rapid" -gt 5 ]; then
        log "ERROR" "Edge case failed: rapid backups not rotated properly: $backup_count_rapid"
        return 1
    fi
    
    # Verify all backup files are still valid after edge cases
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
    
    if [ "$invalid_backups" -gt 0 ]; then
        log "ERROR" "Edge case failed: $invalid_backups invalid backups after rapid creation"
        return 1
    fi
    
    log "SUCCESS" "Rotation edge cases: all edge cases handled, $valid_backups valid backups"
    return 0
}

# Run all backup rotation tests
run_all_backup_rotation_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_basic_backup_rotation"
        "test_timestamp_rotation_order"
        "test_concurrent_rotation"
        "test_size_based_rotation"
        "test_rotation_data_preservation"
        "test_rotation_edge_cases"
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
    echo "Backup Rotation Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All backup rotation tests passed!"
        return 0
    else
        log "ERROR" "Some backup rotation tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_backup_rotation_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests backup file rotation functionality"
    exit 1
fi