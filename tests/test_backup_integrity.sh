#!/bin/bash

# Test backup file validity and completeness
# Part of Auto-2l0: Test state backup and recovery mechanisms

set -e

SCRIPT_NAME="test_backup_integrity"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_backup_integrity_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting backup integrity test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Backup integrity test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Verify backup files are valid JSON
test_backup_json_validity() {
    log "INFO" "Test 1: Verify backup files are valid JSON"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init json_validity >/dev/null 2>&1
    
    # Create multiple backups
    local backup_count=0
    for i in {1..5}; do
        "$NUMBER_MANAGER_SCRIPT" get json_validity >/dev/null 2>&1
        sleep 0.01
        backup_count=$((backup_count + 1))
    done
    
    # Check all backup files for JSON validity
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local valid_backups=0
    local invalid_backups=0
    local total_backups=0
    
    if [ -d "$backup_dir" ]; then
        for backup_file in "$backup_dir"/*.json; do
            if [ -f "$backup_file" ]; then
                total_backups=$((total_backups + 1))
                
                if python3 -m json.tool "$backup_file" >/dev/null 2>&1; then
                    valid_backups=$((valid_backups + 1))
                else
                    invalid_backups=$((invalid_backups + 1))
                    log "ERROR" "Invalid JSON in backup: $(basename "$backup_file")"
                fi
            fi
        done
    fi
    
    if [ "$invalid_backups" -gt 0 ]; then
        log "ERROR" "Found $invalid_backups invalid JSON backup files"
        return 1
    fi
    
    if [ "$valid_backups" -eq 0 ]; then
        log "ERROR" "No valid backup files found"
        return 1
    fi
    
    log "SUCCESS" "Backup JSON validity: $valid_backups/$total_backups backup files are valid JSON"
    return 0
}

# Test 2: Verify backup files contain required fields
test_backup_required_fields() {
    log "INFO" "Test 2: Verify backup files contain required fields"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init required_fields >/dev/null 2>&1
    
    # Create state with multiple contexts
    local contexts=("field_ctx1" "field_ctx2" "field_ctx3")
    for ctx in "${contexts[@]}"; do
        for i in {1..2}; do
            "$NUMBER_MANAGER_SCRIPT" get "$ctx" >/dev/null 2>&1
            sleep 0.01
        done
    done
    
    # Create additional backups
    for i in {1..3}; do
        "$NUMBER_MANAGER_SCRIPT" get required_fields >/dev/null 2>&1
        sleep 0.01
    done
    
    # Check required fields in all backups
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local required_fields=("next_number" "assigned_numbers" "contexts")
    local complete_backups=0
    local incomplete_backups=0
    local total_backups=0
    
    if [ -d "$backup_dir" ]; then
        for backup_file in "$backup_dir"/*.json; do
            if [ -f "$backup_file" ]; then
                total_backups=$((total_backups + 1))
                local file_complete=true
                
                for field in "${required_fields[@]}"; do
                    if ! grep -q "\"$field\"" "$backup_file"; then
                        log "ERROR" "Backup missing required field '$field': $(basename "$backup_file")"
                        file_complete=false
                    fi
                done
                
                if [ "$file_complete" = true ]; then
                    complete_backups=$((complete_backups + 1))
                else
                    incomplete_backups=$((incomplete_backups + 1))
                fi
            fi
        done
    fi
    
    if [ "$incomplete_backups" -gt 0 ]; then
        log "ERROR" "Found $incomplete_backups incomplete backup files"
        return 1
    fi
    
    log "SUCCESS" "Backup required fields: $complete_backups/$total_backups backup files contain all required fields"
    return 0
}

# Test 3: Verify backup data completeness
test_backup_data_completeness() {
    log "INFO" "Test 3: Verify backup data completeness"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init data_completeness >/dev/null 2>&1
    
    # Create complex state
    local contexts=("complete_ctx1" "complete_ctx2" "complete_ctx3" "complete_ctx4")
    local expected_assignments=()
    
    for ctx in "${contexts[@]}"; do
        local ctx_assignments=()
        for i in {1..3}; do
            local num
            num=$("$NUMBER_MANAGER_SCRIPT" get "$ctx" 2>/dev/null | tail -1)
            
            if [ $? -eq 0 ] && [ -n "$num" ]; then
                ctx_assignments+=("$num")
                expected_assignments+=("$ctx:$num")
            fi
            sleep 0.01
        done
        log "INFO" "Context '$ctx' assigned: ${ctx_assignments[*]}"
    done
    
    # Create backup
    "$NUMBER_MANAGER_SCRIPT" backup data_completeness >/dev/null 2>&1
    
    # Check backup data completeness
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local latest_backup
    
    if [ -d "$backup_dir" ]; then
        latest_backup=$(ls -t "$backup_dir"/*.json | head -1)
    fi
    
    if [ -z "$latest_backup" ] || [ ! -f "$latest_backup" ]; then
        log "ERROR" "No backup file found for completeness test"
        return 1
    fi
    
    # Verify all contexts are present
    local contexts_in_backup=0
    for ctx in "${contexts[@]}"; do
        if grep -q "\"$ctx\"" "$latest_backup"; then
            contexts_in_backup=$((contexts_in_backup + 1))
        else
            log "ERROR" "Context '$ctx' missing from backup"
        fi
    done
    
    if [ "$contexts_in_backup" -ne ${#contexts[@]} ]; then
        log "ERROR" "Backup missing contexts: $contexts_in_backup/${#contexts[@]} found"
        return 1
    fi
    
    # Verify backup JSON structure is complete
    if ! python3 -m json.tool "$latest_backup" >/dev/null 2>&1; then
        log "ERROR" "Backup JSON structure is invalid"
        return 1
    fi
    
    # Check backup file size is reasonable
    local backup_size
    backup_size=$(wc -c < "$latest_backup")
    if [ "$backup_size" -lt 100 ]; then
        log "ERROR" "Backup file seems too small: $backup_size bytes"
        return 1
    fi
    
    log "SUCCESS" "Backup data completeness: all ${#contexts[@]} contexts preserved, backup size $backup_size bytes"
    return 0
}

# Test 4: Verify backup timestamp accuracy
test_backup_timestamp_accuracy() {
    log "INFO" "Test 4: Verify backup timestamp accuracy"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init timestamp_accuracy >/dev/null 2>&1
    
    # Create backups with known timing
    local backup_times=()
    local backup_files=()
    
    for i in {1..4}; do
        local before_time
        before_time=$(date +%s)
        
        "$NUMBER_MANAGER_SCRIPT" get timestamp_accuracy >/dev/null 2>&1
        
        local after_time
        after_time=$(date +%s)
        
        # Find the backup file created during this operation
        local backup_dir="$TEST_STATE_DIR/.number_state/backups"
        if [ -d "$backup_dir" ]; then
            for backup_file in "$backup_dir"/backup_*.json; do
                if [ -f "$backup_file" ]; then
                    local file_time
                    file_time=$(stat -c "%Y" "$backup_file" 2>/dev/null || echo "0")
                    
                    # Check if this file was created during our time window
                    if [ "$file_time" -ge "$before_time" ] && [ "$file_time" -le "$after_time" ]; then
                        backup_files+=("$backup_file")
                        backup_times+=("$file_time")
                        break
                    fi
                fi
            done
        fi
        
        sleep 0.1  # Ensure different timestamps
    done
    
    if [ ${#backup_files[@]} -eq 0 ]; do
        log "ERROR" "No backup files found for timestamp accuracy test"
        return 1
    fi
    
    # Verify timestamps are in chronological order
    local timestamps_ordered=true
    for ((i=1; i<${#backup_times[@]}; i++)); do
        if [ "${backup_times[$((i-1))]}" -gt "${backup_times[$i]}" ]; then
            timestamps_ordered=false
            break
        fi
    done
    
    if [ "$timestamps_ordered" = false ]; then
        log "ERROR" "Backup timestamps not in chronological order"
        return 1
    fi
    
    # Verify backup filenames contain timestamps
    local timestamp_files=0
    for backup_file in "${backup_files[@]}"; do
        local filename
        filename=$(basename "$backup_file")
        
        if echo "$filename" | grep -q "backup_[0-9]\{8\}_[0-9]\{6\}_[0-9]\{9\}\.json"; then
            timestamp_files=$((timestamp_files + 1))
        else
            log "WARNING" "Backup filename doesn't match timestamp format: $filename"
        fi
    done
    
    log "SUCCESS" "Backup timestamp accuracy: $timestamp_files/${#backup_files[@]} files with proper timestamps, chronological order verified"
    return 0
}

# Test 5: Verify backup integrity during concurrent operations
test_concurrent_backup_integrity() {
    log "INFO" "Test 5: Verify backup integrity during concurrent operations"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init concurrent_integrity >/dev/null 2>&1
    
    # Start concurrent operations that create backups
    local pids=()
    local operations_per_process=3
    
    for i in {1..5}; do
        (
            for j in $(seq 1 $operations_per_process); do
                "$NUMBER_MANAGER_SCRIPT" get concurrent_integrity >/dev/null 2>&1
                sleep 0.01
            done
        ) &
        pids+=($!)
    done
    
    # Wait for completion
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Check all backup files for integrity
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local valid_backups=0
    local invalid_backups=0
    local total_backups=0
    
    if [ -d "$backup_dir" ]; then
        for backup_file in "$backup_dir"/*.json; do
            if [ -f "$backup_file" ]; then
                total_backups=$((total_backups + 1))
                
                # Check JSON validity
                if python3 -m json.tool "$backup_file" >/dev/null 2>&1; then
                    # Check required fields
                    local has_required_fields=true
                    local required_fields=("next_number" "assigned_numbers" "contexts")
                    
                    for field in "${required_fields[@]}"; do
                        if ! grep -q "\"$field\"" "$backup_file"; then
                            has_required_fields=false
                            break
                        fi
                    done
                    
                    if [ "$has_required_fields" = true ]; then
                        valid_backups=$((valid_backups + 1))
                    else
                        invalid_backups=$((invalid_backups + 1))
                        log "ERROR" "Backup missing required fields: $(basename "$backup_file")"
                    fi
                else
                    invalid_backups=$((invalid_backups + 1))
                    log "ERROR" "Invalid JSON in backup: $(basename "$backup_file")"
                fi
            fi
        done
    fi
    
    if [ "$invalid_backups" -gt 0 ]; then
        log "ERROR" "Found $invalid_backups invalid backup files during concurrent operations"
        return 1
    fi
    
    if [ "$valid_backups" -eq 0 ]; then
        log "ERROR" "No valid backup files found after concurrent operations"
        return 1
    fi
    
    log "SUCCESS" "Concurrent backup integrity: $valid_backups/$total_backups backup files are valid and complete"
    return 0
}

# Test 6: Verify backup consistency with current state
test_backup_state_consistency() {
    log "INFO" "Test 6: Verify backup consistency with current state"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init state_consistency >/dev/null 2>&1
    
    # Create state
    local contexts=("consistency_ctx1" "consistency_ctx2")
    local state_numbers=()
    
    for ctx in "${contexts[@]}"; do
        for i in {1..3}; do
            local num
            num=$("$NUMBER_MANAGER_SCRIPT" get "$ctx" 2>/dev/null | tail -1)
            
            if [ $? -eq 0 ] && [ -n "$num" ]; then
                state_numbers+=("$ctx:$num")
            fi
            sleep 0.01
        done
    done
    
    # Create backup
    "$NUMBER_MANAGER_SCRIPT" backup state_consistency >/dev/null 2>&1
    
    # Get current state
    local current_next
    current_next=$("$NUMBER_MANAGER_SCRIPT" status state_consistency 2>/dev/null | grep "next_number" | cut -d: -f2 | tr -d ' ')
    
    # Get backup state
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local latest_backup
    
    if [ -d "$backup_dir" ]; then
        latest_backup=$(ls -t "$backup_dir"/*.json | head -1)
    fi
    
    if [ -z "$latest_backup" ] || [ ! -f "$latest_backup" ]; then
        log "ERROR" "No backup file found for consistency test"
        return 1
    fi
    
    # Extract next number from backup
    local backup_next
    backup_next=$(grep '"next_number"' "$latest_backup" | grep -o '[0-9]*' | head -1)
    
    # Check consistency (backup should be slightly behind current state)
    if [ -n "$backup_next" ] && [ -n "$current_next" ]; then
        local difference=$((current_next - backup_next))
        
        if [ "$difference" -lt 0 ] || [ "$difference" -gt 2 ]; then
            log "ERROR" "Backup state inconsistent with current state: backup_next=$backup_next, current_next=$current_next"
            return 1
        fi
    fi
    
    # Check that all contexts in current state are in backup
    local backup_contexts=0
    for ctx in "${contexts[@]}"; do
        if grep -q "\"$ctx\"" "$latest_backup"; then
            backup_contexts=$((backup_contexts + 1))
        fi
    done
    
    if [ "$backup_contexts" -ne ${#contexts[@]} ]; then
        log "ERROR" "Backup missing contexts: $backup_contexts/${#contexts[@]}"
        return 1
    fi
    
    log "SUCCESS" "Backup state consistency: backup_next=$backup_next, current_next=$current_next, all contexts preserved"
    return 0
}

# Test 7: Verify backup file permissions and accessibility
test_backup_file_permissions() {
    log "INFO" "Test 7: Verify backup file permissions and accessibility"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init file_permissions >/dev/null 2>&1
    
    # Create backups
    for i in {1..3}; do
        "$NUMBER_MANAGER_SCRIPT" get file_permissions >/dev/null 2>&1
        sleep 0.01
    done
    
    # Check backup file permissions
    local backup_dir="$TEST_STATE_DIR/.number_state/backups"
    local accessible_files=0
    local inaccessible_files=0
    local total_files=0
    
    if [ -d "$backup_dir" ]; then
        for backup_file in "$backup_dir"/*.json; do
            if [ -f "$backup_file" ]; then
                total_files=$((total_files + 1))
                
                # Check file is readable
                if [ -r "$backup_file" ]; then
                    # Check file permissions
                    local file_perms
                    file_perms=$(stat -c "%a" "$backup_file" 2>/dev/null || echo "unknown")
                    
                    # Should be readable by owner (644 or 600)
                    if [ "$file_perms" = "644" ] || [ "$file_perms" = "600" ]; then
                        accessible_files=$((accessible_files + 1))
                    else
                        log "WARNING" "Unexpected backup file permissions: $(basename "$backup_file") has $file_perms"
                        accessible_files=$((accessible_files + 1))  # Still count as accessible
                    fi
                else
                    inaccessible_files=$((inaccessible_files + 1))
                    log "ERROR" "Backup file not readable: $(basename "$backup_file")"
                fi
            fi
        done
    fi
    
    if [ "$inaccessible_files" -gt 0 ]; then
        log "ERROR" "Found $inaccessible_files inaccessible backup files"
        return 1
    fi
    
    if [ "$accessible_files" -eq 0 ]; then
        log "ERROR" "No accessible backup files found"
        return 1
    fi
    
    # Check backup directory permissions
    local dir_perms
    dir_perms=$(stat -c "%a" "$backup_dir" 2>/dev/null || echo "unknown")
    
    if [ "$dir_perms" != "755" ] && [ "$dir_perms" != "700" ]; then
        log "WARNING" "Unexpected backup directory permissions: $dir_perms"
    fi
    
    log "SUCCESS" "Backup file permissions: $accessible_files/$total_files files accessible, directory permissions $dir_perms"
    return 0
}

# Run all backup integrity tests
run_all_backup_integrity_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_backup_json_validity"
        "test_backup_required_fields"
        "test_backup_data_completeness"
        "test_backup_timestamp_accuracy"
        "test_concurrent_backup_integrity"
        "test_backup_state_consistency"
        "test_backup_file_permissions"
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
    echo "Backup Integrity Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All backup integrity tests passed!"
        return 0
    else
        log "ERROR" "Some backup integrity tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_backup_integrity_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests backup file validity and completeness"
    exit 1
fi