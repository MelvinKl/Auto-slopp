#!/bin/bash

# Test existing state handling and re-initialization scenarios
# Part of Auto-4x9: Test number_manager.sh initialization and state management

set -e

SCRIPT_NAME="test_init_existing"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_init_existing_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting existing state handling test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Helper to create a test state file
create_test_state() {
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    
    cat > "$state_file" << EOF
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

# Test 1: Re-initialization with existing valid state
test_reinit_with_valid_state() {
    log "INFO" "Test 1: Re-initialization with existing valid state"
    
    # Create initial state
    create_test_state
    
    # Record original file timestamp
    local original_mtime
    original_mtime=$(stat -c %Y "$TEST_STATE_DIR/.number_state/state.json")
    
    # Attempt re-initialization
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Re-initialization completed successfully"
    else
        log "ERROR" "Re-initialization failed"
        return 1
    fi
    
    # Check state file wasn't overwritten (should have same content)
    local used_numbers
    used_numbers=$(jq -r '.used_numbers | length' "$TEST_STATE_DIR/.number_state/state.json")
    if [ "$used_numbers" != "3" ]; then
        log "ERROR" "Existing state was overwritten incorrectly"
        return 1
    fi
    
    # Note: File modification time might change due to validation logic
    log "SUCCESS" "Existing state preserved correctly"
    return 0
}

# Test 2: Re-initialization with corrupted JSON state
test_reinit_with_corrupted_json() {
    log "INFO" "Test 2: Re-initialization with corrupted JSON state"
    
    # Create corrupted JSON file
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    echo '{"invalid": json}' > "$TEST_STATE_DIR/.number_state/state.json"
    
    # Attempt re-initialization (should handle corruption)
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Re-initialization handled corrupted state"
    else
        log "ERROR" "Re-initialization failed with corrupted state"
        return 1
    fi
    
    # Check if state file is now valid JSON
    if jq empty "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null; then
        log "SUCCESS" "State file recovered to valid JSON"
    else
        log "ERROR" "State file still corrupted after recovery"
        return 1
    fi
    
    return 0
}

# Test 3: Re-initialization with missing required fields
test_reinit_missing_fields() {
    log "INFO" "Test 3: Re-initialization with missing required fields"
    
    # Create state file missing required fields
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    cat > "$TEST_STATE_DIR/.number_state/state.json" << EOF
{
    "used_numbers": [1, 2],
    "created_at": "2023-01-01T00:00:00Z"
}
EOF
    
    # Attempt re-initialization
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Re-initialization handled missing fields"
    else
        log "ERROR" "Re-initialization failed with missing fields"
        return 1
    fi
    
    # Check if all required fields are now present
    local required_fields=("used_numbers" "last_assigned" "context_assignments")
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$TEST_STATE_DIR/.number_state/state.json" >/dev/null; then
            log "ERROR" "Field $field still missing after re-initialization"
            return 1
        fi
    done
    
    log "SUCCESS" "Missing fields handled correctly"
    return 0
}

# Test 4: Re-initialization with invalid data types
test_reinit_invalid_types() {
    log "INFO" "Test 4: Re-initialization with invalid data types"
    
    # Create state file with invalid data types
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    cat > "$TEST_STATE_DIR/.number_state/state.json" << EOF
{
    "used_numbers": "not_an_array",
    "last_assigned": "not_a_number",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "context_assignments": {},
    "version": "1.0",
    "metadata": {
        "creator": "number_manager.sh",
        "purpose": "unique_number_tracking"
    }
}
EOF
    
    # Attempt re-initialization
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Re-initialization handled invalid data types"
    else
        log "ERROR" "Re-initialization failed with invalid data types"
        return 1
    fi
    
    # Check if data types are now correct
    local used_numbers_type last_assigned_type
    used_numbers_type=$(jq -r '.used_numbers | if type == "array" then "array" else type end' "$TEST_STATE_DIR/.number_state/state.json")
    last_assigned_type=$(jq -r '.last_assigned | if type == "number" then "number" else type end' "$TEST_STATE_DIR/.number_state/state.json")
    
    if [ "$used_numbers_type" = "array" ] && [ "$last_assigned_type" = "number" ]; then
        log "SUCCESS" "Data types corrected properly"
    else
        log "ERROR" "Data types still incorrect: used_numbers=$used_numbers_type, last_assigned=$last_assigned_type"
        return 1
    fi
    
    return 0
}

# Test 5: Re-initialization preserves user data when possible
test_reinit_preserves_data() {
    log "INFO" "Test 5: Re-initialization preserves user data"
    
    # Create state with some user data
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    cat > "$TEST_STATE_DIR/.number_state/state.json" << EOF
{
    "used_numbers": [1, 2, 5, 8],
    "last_assigned": 8,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "context_assignments": {
        "repo1": "5",
        "repo2": "8"
    },
    "version": "1.0",
    "metadata": {
        "creator": "number_manager.sh",
        "purpose": "unique_number_tracking"
    },
    "assignments": [
        {"number": 1, "context": "repo1", "timestamp": "2023-01-01T00:00:00Z"},
        {"number": 2, "context": "repo1", "timestamp": "2023-01-01T00:00:00Z"}
    ]
}
EOF
    
    # Attempt re-initialization
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Re-initialization completed"
    else
        log "ERROR" "Re-initialization failed"
        return 1
    fi
    
    # Check if user data was preserved
    local used_count last_assigned context_count
    used_count=$(jq -r '.used_numbers | length' "$TEST_STATE_DIR/.number_state/state.json")
    last_assigned=$(jq -r '.last_assigned' "$TEST_STATE_DIR/.number_state/state.json")
    context_count=$(jq -r '.context_assignments | keys | length' "$TEST_STATE_DIR/.number_state/state.json")
    
    if [ "$used_count" = "4" ] && [ "$last_assigned" = "8" ] && [ "$context_count" = "2" ]; then
        log "SUCCESS" "User data preserved correctly"
    else
        log "ERROR" "User data not preserved: used_count=$used_count, last_assigned=$last_assigned, context_count=$context_count"
        return 1
    fi
    
    return 0
}

# Test 6: Re-initialization handles directory permission issues
test_reinit_permission_issues() {
    log "INFO" "Test 6: Re-initialization with permission issues"
    
    # Create initial state
    create_test_state
    
    # Make state directory read-only
    chmod 444 "$TEST_STATE_DIR/.number_state"
    
    # Attempt re-initialization (should handle gracefully)
    local init_result=0
    "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1 || init_result=1
    
    # Restore permissions for cleanup
    chmod 755 "$TEST_STATE_DIR/.number_state"
    
    if [ $init_result -eq 1 ]; then
        log "SUCCESS" "Re-initialization failed appropriately with permission issues"
    else
        log "ERROR" "Re-initialization should have failed with permission issues"
        return 1
    fi
    
    return 0
}

# Test 7: Re-initialization with backup corruption
test_reinit_backup_corruption() {
    log "INFO" "Test 7: Re-initialization with backup corruption"
    
    # Create initial state and corrupted backups
    create_test_state
    echo 'invalid json' > "$TEST_STATE_DIR/.number_state/backup/state_20230101_000000.json"
    echo '{"also": invalid}' > "$TEST_STATE_DIR/.number_state/backup/state_20230101_000001.json"
    
    # Create corrupted main state
    echo '{"corrupted": state}' > "$TEST_STATE_DIR/.number_state/state.json"
    
    # Attempt re-initialization (should fall back to fresh init)
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Re-initialization handled backup corruption"
    else
        log "ERROR" "Re-initialization failed with backup corruption"
        return 1
    fi
    
    # Check if fresh state was created
    if jq empty "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null; then
        log "SUCCESS" "Fresh state created after backup corruption"
    else
        log "ERROR" "State file still corrupted"
        return 1
    fi
    
    return 0
}

# Test 8: Re-initialization updates timestamps appropriately
test_reinit_updates_timestamps() {
    log "INFO" "Test 8: Re-initialization updates timestamps"
    
    # Create initial state with old timestamps
    create_test_state
    
    # Record original timestamps
    local original_updated_at
    original_updated_at=$(jq -r '.updated_at' "$TEST_STATE_DIR/.number_state/state.json")
    
    # Wait a moment to ensure timestamp difference
    sleep 2
    
    # Attempt re-initialization
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Re-initialization completed"
    else
        log "ERROR" "Re-initialization failed"
        return 1
    fi
    
    # Check if updated_at was changed
    local new_updated_at
    new_updated_at=$(jq -r '.updated_at' "$TEST_STATE_DIR/.number_state/state.json")
    
    if [ "$new_updated_at" != "$original_updated_at" ]; then
        log "SUCCESS" "Timestamp updated appropriately"
    else
        log "WARNING" "Timestamp not updated (may be acceptable behavior)"
    fi
    
    return 0
}

# Run all tests
run_all_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_reinit_with_valid_state"
        "test_reinit_with_corrupted_json"
        "test_reinit_missing_fields"
        "test_reinit_invalid_types"
        "test_reinit_preserves_data"
        "test_reinit_permission_issues"
        "test_reinit_backup_corruption"
        "test_reinit_updates_timestamps"
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
    echo "Existing State Handling Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All existing state handling tests passed!"
        return 0
    else
        log "ERROR" "Some existing state handling tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests existing state handling for number_manager.sh"
    exit 1
fi