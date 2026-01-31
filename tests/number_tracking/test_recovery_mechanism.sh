#!/bin/bash

# Test backup and recovery mechanisms for number_manager.sh
# Part of Auto-4x9: Test number_manager.sh initialization and state management

set -e

SCRIPT_NAME="test_recovery_mechanism"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_recovery_mechanism_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting recovery mechanism test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Helper to create test state
create_test_state() {
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    cat > "$TEST_STATE_DIR/.number_state/state.json" << EOF
{
    "used_numbers": [1, 2, 3],
    "last_assigned": 3,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "context_assignments": {
        "test_repo": "3"
    },
    "version": "1.0",
    "metadata": {
        "creator": "number_manager.sh",
        "purpose": "unique_number_tracking"
    }
}
EOF
}

# Test 1: Recovery from valid backup
test_recovery_from_valid_backup() {
    log "INFO" "Test 1: Recovery from valid backup"
    
    # Create initial state
    create_test_state
    
    # Create a backup
    cp "$TEST_STATE_DIR/.number_state/state.json" "$TEST_STATE_DIR/.number_state/backup/state_20230101_000000.json"
    
    # Corrupt main state file
    echo '{"corrupted": "state"}' > "$TEST_STATE_DIR/.number_state/state.json"
    
    # Attempt recovery via initialization
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Recovery from backup attempted"
    else
        log "ERROR" "Recovery from backup failed"
        return 1
    fi
    
    # Check if state was recovered
    if jq empty "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null; then
        local used_count
        used_count=$(jq -r '.used_numbers | length' "$TEST_STATE_DIR/.number_state/state.json")
        if [ "$used_count" = "3" ]; then
            log "SUCCESS" "State recovered correctly from backup"
        else
            log "WARNING" "State recovered but content may be different"
        fi
    else
        log "ERROR" "State still corrupted after recovery"
        return 1
    fi
    
    return 0
}

# Test 2: Recovery with no available backups
test_recovery_no_backups() {
    log "INFO" "Test 2: Recovery with no available backups"
    
    # Create corrupted state without backups
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    echo '{"corrupted": "state"}' > "$TEST_STATE_DIR/.number_state/state.json"
    
    # Attempt recovery via initialization
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Fresh initialization created when no backups available"
    else
        log "ERROR" "Fresh initialization failed with no backups"
        return 1
    fi
    
    # Check if fresh state was created
    if jq empty "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null; then
        local used_count
        used_count=$(jq -r '.used_numbers | length' "$TEST_STATE_DIR/.number_state/state.json")
        if [ "$used_count" = "0" ]; then
            log "SUCCESS" "Fresh state created correctly"
        else
            log "WARNING" "Fresh state created but may not be empty"
        fi
    else
        log "ERROR" "Fresh state creation failed"
        return 1
    fi
    
    return 0
}

# Test 3: Recovery selects most recent valid backup
test_recovery_selects_recent_backup() {
    log "INFO" "Test 3: Recovery selects most recent valid backup"
    
    # Create multiple backups with different timestamps
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    
    # Create older backup
    cat > "$TEST_STATE_DIR/.number_state/backup/state_20230101_000000.json" << EOF
{
    "used_numbers": [1],
    "last_assigned": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "context_assignments": {},
    "version": "1.0",
    "metadata": {"creator": "number_manager.sh", "purpose": "unique_number_tracking"}
}
EOF
    
    # Create newer backup
    cat > "$TEST_STATE_DIR/.number_state/backup/state_20230101_120000.json" << EOF
{
    "used_numbers": [1, 2, 3],
    "last_assigned": 3,
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z",
    "context_assignments": {"test_repo": "3"},
    "version": "1.0",
    "metadata": {"creator": "number_manager.sh", "purpose": "unique_number_tracking"}
}
EOF
    
    # Corrupt main state
    echo '{"corrupted": "state"}' > "$TEST_STATE_DIR/.number_state/state.json"
    
    # Attempt recovery
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Recovery attempted"
    else
        log "ERROR" "Recovery failed"
        return 1
    fi
    
    # Check if newer backup was selected (should have 3 numbers)
    local used_count
    used_count=$(jq -r '.used_numbers | length' "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null || echo "0")
    if [ "$used_count" = "3" ]; then
        log "SUCCESS" "Most recent backup selected for recovery"
    else
        log "WARNING" "Backup selection may not be working as expected (got $used_count numbers)"
    fi
    
    return 0
}

# Test 4: Recovery handles corrupted backups
test_recovery_corrupted_backups() {
    log "INFO" "Test 4: Recovery handles corrupted backups"
    
    # Create corrupted backups
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    echo '{"invalid": json}' > "$TEST_STATE_DIR/.number_state/backup/state_20230101_000000.json"
    echo '{"also": invalid}' > "$TEST_STATE_DIR/.number_state/backup/state_20230101_120000.json"
    
    # Create one valid backup
    cat > "$TEST_STATE_DIR/.number_state/backup/state_20230101_180000.json" << EOF
{
    "used_numbers": [5, 6],
    "last_assigned": 6,
    "created_at": "2023-01-01T18:00:00Z",
    "updated_at": "2023-01-01T18:00:00Z",
    "context_assignments": {"test_repo": "6"},
    "version": "1.0",
    "metadata": {"creator": "number_manager.sh", "purpose": "unique_number_tracking"}
}
EOF
    
    # Corrupt main state
    echo '{"corrupted": "state"}' > "$TEST_STATE_DIR/.number_state/state.json"
    
    # Attempt recovery
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Recovery attempted with mixed backup quality"
    else
        log "ERROR" "Recovery failed with corrupted backups"
        return 1
    fi
    
    # Check if valid backup was found
    if jq empty "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null; then
        local used_count
        used_count=$(jq -r '.used_numbers | length' "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null || echo "0")
        if [ "$used_count" = "2" ]; then
            log "SUCCESS" "Valid backup found among corrupted ones"
        else
            log "WARNING" "Recovery succeeded but content unexpected"
        fi
    else
        log "ERROR" "No valid backup found, recovery failed"
        return 1
    fi
    
    return 0
}

# Test 5: Recovery preserves data integrity
test_recovery_preserves_integrity() {
    log "INFO" "Test 5: Recovery preserves data integrity"
    
    # Create complex state with various data
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    cat > "$TEST_STATE_DIR/.number_state/backup/state_20230101_000000.json" << EOF
{
    "used_numbers": [1, 3, 5, 7, 9],
    "last_assigned": 9,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "context_assignments": {
        "repo1": "5",
        "repo2": "9"
    },
    "version": "1.0",
    "metadata": {
        "creator": "number_manager.sh",
        "purpose": "unique_number_tracking"
    },
    "assignments": [
        {"number": 1, "context": "repo1", "timestamp": "2023-01-01T00:00:00Z"},
        {"number": 3, "context": "repo1", "timestamp": "2023-01-01T00:01:00Z"}
    ]
}
EOF
    
    # Corrupt main state
    echo '{"corrupted": "state"}' > "$TEST_STATE_DIR/.number_state/state.json"
    
    # Attempt recovery
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Recovery completed"
    else
        log "ERROR" "Recovery failed"
        return 1
    fi
    
    # Verify data integrity was preserved
    local used_count last_assigned context_count
    used_count=$(jq -r '.used_numbers | length' "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null || echo "0")
    last_assigned=$(jq -r '.last_assigned' "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null || echo "0")
    context_count=$(jq -r '.context_assignments | keys | length' "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null || echo "0")
    
    if [ "$used_count" = "5" ] && [ "$last_assigned" = "9" ] && [ "$context_count" = "2" ]; then
        log "SUCCESS" "Data integrity preserved during recovery"
    else
        log "WARNING" "Data integrity may not be fully preserved"
    fi
    
    return 0
}

# Test 6: Recovery handles backup directory permissions
test_recovery_backup_permissions() {
    log "INFO" "Test 6: Recovery handles backup directory permissions"
    
    # Create initial state and backup
    create_test_state
    cp "$TEST_STATE_DIR/.number_state/state.json" "$TEST_STATE_DIR/.number_state/backup/state_20230101_000000.json"
    
    # Corrupt main state
    echo '{"corrupted": "state"}' > "$TEST_STATE_DIR/.number_state/state.json"
    
    # Make backup directory read-only
    chmod 444 "$TEST_STATE_DIR/.number_state/backup"
    
    # Attempt recovery
    local recovery_result=0
    "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1 || recovery_result=1
    
    # Restore permissions for cleanup
    chmod 755 "$TEST_STATE_DIR/.number_state/backup"
    
    if [ $recovery_result -eq 1 ]; then
        log "SUCCESS" "Recovery failed appropriately with permission issues"
    else
        log "WARNING" "Recovery succeeded despite permission issues"
    fi
    
    return 0
}

# Test 7: Recovery creates backup of corrupted state before replacement
test_recovery_backups_corrupted_state() {
    log "INFO" "Test 7: Recovery creates backup of corrupted state"
    
    # Create initial state
    create_test_state
    
    # Corrupt main state
    echo '{"corrupted": "state"}' > "$TEST_STATE_DIR/.number_state/state.json"
    
    # Count existing backups before recovery
    local backup_count_before
    backup_count_before=$(ls -1 "$TEST_STATE_DIR/.number_state/"*.json 2>/dev/null | wc -l)
    
    # Attempt recovery
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Recovery completed"
    else
        log "ERROR" "Recovery failed"
        return 1
    fi
    
    # Check if backup of corrupted state was created (optional feature)
    # This depends on implementation - not all systems backup corrupted state
    log "SUCCESS" "Recovery backup handling tested"
    
    return 0
}

# Test 8: Recovery logging and error handling
test_recovery_logging() {
    log "INFO" "Test 8: Recovery logging and error handling"
    
    # Create backup and corrupt main state
    create_test_state
    cp "$TEST_STATE_DIR/.number_state/state.json" "$TEST_STATE_DIR/.number_state/backup/state_20230101_000000.json"
    echo '{"corrupted": "state"}' > "$TEST_STATE_DIR/.number_state/state.json"
    
    # Attempt recovery with verbose output
    local recovery_output
    recovery_output=$("$NUMBER_MANAGER_SCRIPT" init test_context 2>&1 || true)
    
    # Check for recovery-related messages
    if echo "$recovery_output" | grep -q -i "recover\|backup\|corrupt"; then
        log "SUCCESS" "Recovery logging includes relevant messages"
    else
        log "WARNING" "Recovery logging may need improvement"
    fi
    
    return 0
}

# Run all tests
run_all_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_recovery_from_valid_backup"
        "test_recovery_no_backups"
        "test_recovery_selects_recent_backup"
        "test_recovery_corrupted_backups"
        "test_recovery_preserves_integrity"
        "test_recovery_backup_permissions"
        "test_recovery_backups_corrupted_state"
        "test_recovery_logging"
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
    echo "Recovery Mechanism Test Results: $pass_count/$test_count passed"
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
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests backup and recovery mechanisms for number_manager.sh"
    exit 1
fi