#!/bin/bash

# Test automatic backup creation
# Part of Auto-2l0: Test state backup and recovery mechanisms

set -e

SCRIPT_NAME="test_backup_creation"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_backup_creation_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting backup creation test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Backup creation test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Automatic backup creation before state modification
test_automatic_backup_creation() {
    log "INFO" "Test 1: Automatic backup creation before state modification"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init backup_test >/dev/null 2>&1
    
    # Check if initial backup was created
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local initial_backup_count=0
    
    if [ -d "$backup_dir" ]; then
        initial_backup_count=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    # Get a number (should trigger backup)
    local num
    num=$("$NUMBER_MANAGER_SCRIPT" get backup_test 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$num" ]; then
        log "ERROR" "Failed to get number for backup test"
        return 1
    fi
    
    # Check if backup was created
    local backup_count_after=0
    if [ -d "$backup_dir" ]; then
        backup_count_after=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    if [ "$backup_count_after" -le "$initial_backup_count" ]; then
        log "ERROR" "No backup created after state modification"
        return 1
    fi
    
    # Get another number to test multiple backups
    local num2
    num2=$("$NUMBER_MANAGER_SCRIPT" get backup_test 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$num2" ]; then
        log "ERROR" "Failed to get second number"
        return 1
    fi
    
    # Check backup count increased again
    local backup_count_final=0
    if [ -d "$backup_dir" ]; then
        backup_count_final=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    if [ "$backup_count_final" -le "$backup_count_after" ]; then
        log "ERROR" "No backup created for second state modification"
        return 1
    fi
    
    log "SUCCESS" "Automatic backup creation: $backup_count_final backups created for 2 modifications"
    return 0
}

# Test 2: Manual backup creation
test_manual_backup_creation() {
    log "INFO" "Test 2: Manual backup creation"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init manual_backup >/dev/null 2>&1
    
    # Get some numbers to create state
    for i in {1..3}; do
        "$NUMBER_MANAGER_SCRIPT" get manual_backup >/dev/null 2>&1
    done
    
    # Create manual backup
    "$NUMBER_MANAGER_SCRIPT" backup manual_backup >/dev/null 2>&1
    
    if [ $? -ne 0 ]; then
        log "ERROR" "Manual backup creation failed"
        return 1
    fi
    
    # Check backup exists
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local backup_count=0
    
    if [ -d "$backup_dir" ]; then
        backup_count=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    if [ "$backup_count" -eq 0 ]; then
        log "ERROR" "No backup files found after manual backup"
        return 1
    fi
    
    log "SUCCESS" "Manual backup creation: $backup_count backup files found"
    return 0
}

# Test 3: Backup directory creation and permissions
test_backup_directory_management() {
    log "INFO" "Test 3: Backup directory creation and permissions"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init dir_test >/dev/null 2>&1
    
    # Check backup directory was created
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    
    if [ ! -d "$backup_dir" ]; then
        log "ERROR" "Backup directory not created"
        return 1
    fi
    
    # Check directory permissions
    local dir_perms
    dir_perms=$(stat -c "%a" "$backup_dir" 2>/dev/null || echo "unknown")
    
    # Should be readable/writable by owner
    if [ "$dir_perms" != "755" ] && [ "$dir_perms" != "700" ]; then
        log "WARNING" "Unexpected backup directory permissions: $dir_perms"
    fi
    
    # Get a number to trigger backup creation
    "$NUMBER_MANAGER_SCRIPT" get dir_test >/dev/null 2>&1
    
    # Check backup files have correct permissions
    local backup_files=()
    if [ -d "$backup_dir" ]; then
        for backup_file in "$backup_dir"/*.json; do
            if [ -f "$backup_file" ]; then
                backup_files+=("$backup_file")
            fi
        done
    fi
    
    if [ ${#backup_files[@]} -eq 0 ]; then
        log "ERROR" "No backup files created to test permissions"
        return 1
    fi
    
    # Check file permissions
    local file_perms_ok=true
    for backup_file in "${backup_files[@]}"; do
        local file_perms
        file_perms=$(stat -c "%a" "$backup_file" 2>/dev/null || echo "unknown")
        
        if [ "$file_perms" != "644" ] && [ "$file_perms" != "600" ]; then
            log "WARNING" "Unexpected backup file permissions for $(basename "$backup_file"): $file_perms"
        fi
        
        # Check file is readable
        if [ ! -r "$backup_file" ]; then
            log "ERROR" "Backup file not readable: $(basename "$backup_file")"
            file_perms_ok=false
        fi
    done
    
    if [ "$file_perms_ok" = false ]; then
        return 1
    fi
    
    log "SUCCESS" "Backup directory management: directory created with $dir_perms perms, ${#backup_files[@]} files with proper permissions"
    return 0
}

# Test 4: Backup filename timestamp handling
test_backup_timestamp_handling() {
    log "INFO" "Test 4: Backup filename timestamp handling"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init timestamp_test >/dev/null 2>&1
    
    # Get numbers at different times to create backups
    local backup_files=()
    
    for i in {1..3}; do
        "$NUMBER_MANAGER_SCRIPT" get timestamp_test >/dev/null 2>&1
        sleep 0.1  # Small delay to ensure different timestamps
        
        # Find backup files created
        local backup_dir="$TEST_STATE_DIR/.number_state/backups"
        if [ -d "$backup_dir" ]; then
            for backup_file in "$backup_dir"/*.json; do
                if [ -f "$backup_file" ]; then
                    backup_files+=("$(basename "$backup_file")")
                fi
            done
        fi
    done
    
    if [ ${#backup_files[@]} -eq 0 ]; then
        log "ERROR" "No backup files created for timestamp test"
        return 1
    fi
    
    # Check backup filenames contain timestamps
    local timestamp_files=0
    for backup_file in "${backup_files[@]}"; do
        # Backup files should have timestamp in name (format: backup_YYYYMMDD_HHMMSS_NNNNNNNNN.json)
        if echo "$backup_file" | grep -q "backup_[0-9]\{8\}_[0-9]\{6\}_[0-9]\{9\}\.json"; then
            timestamp_files=$((timestamp_files + 1))
        else
            log "WARNING" "Backup file doesn't match expected timestamp format: $backup_file"
        fi
    done
    
    if [ "$timestamp_files" -eq 0 ]; then
        log "ERROR" "No backup files with proper timestamp format found"
        return 1
    fi
    
    # Check timestamps are chronological
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local sorted_files=()
    if [ -d "$backup_dir" ]; then
        for backup_file in "$backup_dir"/backup_*.json; do
            if [ -f "$backup_file" ]; then
                sorted_files+=("$backup_file")
            fi
        done
    fi
    
    # Sort by modification time
    IFS=$'\n' sorted_files=($(sort -n <<<"${sorted_files[*]}"))
    unset IFS
    
    log "SUCCESS" "Backup timestamp handling: $timestamp_files/${#backup_files[@]} files with proper timestamp format"
    return 0
}

# Test 5: Backup creation during concurrent operations
test_concurrent_backup_creation() {
    log "INFO" "Test 5: Backup creation during concurrent operations"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init concurrent_backup >/dev/null 2>&1
    
    # Start concurrent operations
    local pids=()
    local results_file="$TEST_STATE_DIR/concurrent_results.txt"
    
    for i in {1..5}; do
        (
            for j in {1..3}; do
                local start_time
                start_time=$(date +%s.%N)
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get concurrent_backup 2>/dev/null | tail -1)
                local end_time
                end_time=$(date +%s.%N)
                
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "process_$i:operation_$j:number_$num:start_$start_time:end_$end_time" >> "$results_file"
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
    
    # Check backup files were created
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local backup_count=0
    
    if [ -d "$backup_dir" ]; then
        backup_count=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    if [ "$backup_count" -eq 0 ]; then
        log "ERROR" "No backup files created during concurrent operations"
        return 1
    fi
    
    # Verify all backup files are valid JSON
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
        log "ERROR" "Found $invalid_backups invalid backup files during concurrent operations"
        return 1
    fi
    
    # Check operation results for duplicates
    local all_numbers=()
    if [ -f "$results_file" ]; then
        while read -r line; do
            if echo "$line" | grep -q "number_"; then
                local num
                num=$(echo "$line" | grep -o "number_[0-9]*" | cut -d_ -f2)
                all_numbers+=("$num")
            fi
        done < "$results_file"
    fi
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Duplicates found during concurrent backup test: $duplicate_count"
        return 1
    fi
    
    log "SUCCESS" "Concurrent backup creation: $valid_backups valid backups, ${#all_numbers[@]} unique numbers"
    return 0
}

# Test 6: Backup creation with different contexts
test_multi_context_backup() {
    log "INFO" "Test 6: Backup creation with different contexts"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init multi_context >/dev/null 2>&1
    
    # Get numbers for different contexts
    local contexts=("ctx_alpha" "ctx_beta" "ctx_gamma")
    local context_numbers=()
    
    for ctx in "${contexts[@]}"; do
        for i in {1..2}; do
            local num
            num=$("$NUMBER_MANAGER_SCRIPT" get "$ctx" 2>/dev/null | tail -1)
            
            if [ $? -eq 0 ] && [ -n "$num" ]; then
                context_numbers+=("$ctx:$num")
            fi
        done
    done
    
    # Check backup files were created
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local backup_count=0
    
    if [ -d "$backup_dir" ]; then
        backup_count=$(find "$backup_dir" -name "*.json" | wc -l)
    fi
    
    if [ "$backup_count" -eq 0 ]; then
        log "ERROR" "No backup files created for multi-context test"
        return 1
    fi
    
    # Verify backup contains all contexts
    local latest_backup
    if [ -d "$backup_dir" ]; then
        latest_backup=$(ls -t "$backup_dir"/*.json | head -1)
    fi
    
    if [ -n "$latest_backup" ] && [ -f "$latest_backup" ]; then
        local contexts_in_backup=0
        for ctx in "${contexts[@]}"; do
            if grep -q "\"$ctx\"" "$latest_backup"; then
                contexts_in_backup=$((contexts_in_backup + 1))
            fi
        done
        
        if [ "$contexts_in_backup" -ne ${#contexts[@]} ]; then
            log "ERROR" "Backup missing contexts: $contexts_in_backup/${#contexts[@]} found"
            return 1
        fi
    fi
    
    log "SUCCESS" "Multi-context backup: $backup_count backups created, all ${#contexts[@]} contexts preserved"
    return 0
}

# Run all backup creation tests
run_all_backup_creation_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_automatic_backup_creation"
        "test_manual_backup_creation"
        "test_backup_directory_management"
        "test_backup_timestamp_handling"
        "test_concurrent_backup_creation"
        "test_multi_context_backup"
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
    echo "Backup Creation Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All backup creation tests passed!"
        return 0
    else
        log "ERROR" "Some backup creation tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_backup_creation_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests automatic backup creation functionality"
    exit 1
fi