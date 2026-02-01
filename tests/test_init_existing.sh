#!/bin/bash

# Test Re-initialization Scenarios for number_manager.sh
# Tests behavior when running init on existing state, including state preservation,
# no-overwrite behavior, and handling of different existing state conditions

SCRIPT_NAME="test_init_existing"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_init_existing_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

# Test results tracking
TESTS_RUN=0
TESTS_PASSED=0

log "INFO" "Starting re-initialization tests in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test helper functions
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo ""
    echo "=========================================="
    echo "Running Test: $test_name"
    echo "=========================================="
    
    if eval "$test_command"; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo "✅ $test_name PASSED"
        return 0
    else
        echo "❌ $test_name FAILED"
        return 1
    fi
}

# Helper to create initial state with some data
create_initial_state() {
    local context="$1"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init "$context" >/dev/null 2>&1
    
    # Add some numbers to make state interesting
    "$NUMBER_MANAGER_SCRIPT" get "$context" >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get "$context" >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" get "$context" >/dev/null 2>&1  # 3
}

# Test 1: Re-initialization preserves existing state data
test_reinit_preserves_state() {
    log "INFO" "Test 1: Testing re-initialization preserves existing state"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create initial state with data
    create_initial_state "preserve_test"
    
    # Get state before re-init
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    local original_last_assigned=$(jq -r '.last_assigned' "$state_file")
    local original_used_count=$(jq -r '.used_numbers | length' "$state_file")
    local original_created_at=$(jq -r '.created_at' "$state_file")
    
    # Re-initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init "preserve_test" >/dev/null 2>&1; then
        log "ERROR" "Re-initialization failed"
        return 1
    fi
    
    # Check state preservation
    local new_last_assigned=$(jq -r '.last_assigned' "$state_file")
    local new_used_count=$(jq -r '.used_numbers | length' "$state_file")
    local new_created_at=$(jq -r '.created_at' "$state_file")
    local new_updated_at=$(jq -r '.updated_at' "$state_file")
    
    # Last assigned and used count should be preserved
    if [ "$original_last_assigned" != "$new_last_assigned" ]; then
        log "ERROR" "last_assigned not preserved: $original_last_assigned -> $new_last_assigned"
        return 1
    fi
    
    if [ "$original_used_count" != "$new_used_count" ]; then
        log "ERROR" "used_numbers not preserved: $original_used_count -> $new_used_count"
        return 1
    fi
    
    # Created_at should be preserved, updated_at should change
    if [ "$original_created_at" != "$new_created_at" ]; then
        log "ERROR" "created_at should be preserved: $original_created_at -> $new_created_at"
        return 1
    fi
    
    if [ "$original_created_at" = "$new_updated_at" ]; then
        log "ERROR" "updated_at should change on re-initialization"
        return 1
    fi
    
    log "SUCCESS" "Re-initialization preserves existing state correctly"
    return 0
}

# Test 2: Re-initialization does not overwrite existing state file
test_reinit_no_overwrite() {
    log "INFO" "Test 2: Testing re-initialization does not overwrite existing state file"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create initial state
    create_initial_state "no_overwrite_test"
    
    # Get state file inode (file identity)
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    local original_inode=$(stat -c %i "$state_file" 2>/dev/null || stat -f %i "$state_file" 2>/dev/null)
    
    # Re-initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init "no_overwrite_test" >/dev/null 2>&1; then
        log "ERROR" "Re-initialization failed"
        return 1
    fi
    
    # Check file wasn't recreated (same inode)
    local new_inode=$(stat -c %i "$state_file" 2>/dev/null || stat -f %i "$state_file" 2>/dev/null)
    
    if [ "$original_inode" != "$new_inode" ]; then
        log "ERROR" "State file was overwritten during re-initialization"
        return 1
    fi
    
    log "SUCCESS" "Re-initialization does not overwrite existing state file"
    return 0
}

# Test 3: Re-initialization with different context updates appropriately
test_reinit_different_context() {
    log "INFO" "Test 3: Testing re-initialization with different context"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Initialize with first context
    "$NUMBER_MANAGER_SCRIPT" init "context1" >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get "context1" >/dev/null 2>&1
    
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    local original_last_assigned=$(jq -r '.last_assigned' "$state_file")
    local original_context_count=$(jq -r '.context_assignments | keys | length' "$state_file")
    
    # Re-initialize with different context
    if ! "$NUMBER_MANAGER_SCRIPT" init "context2" >/dev/null 2>&1; then
        log "ERROR" "Re-initialization with different context failed"
        return 1
    fi
    
    # Get number with new context
    "$NUMBER_MANAGER_SCRIPT" get "context2" >/dev/null 2>&1
    
    local new_last_assigned=$(jq -r '.last_assigned' "$state_file")
    local new_context_count=$(jq -r '.context_assignments | keys | length' "$state_file")
    
    # Last assigned should increment
    if [ "$new_last_assigned" -le "$original_last_assigned" ]; then
        log "ERROR" "last_assigned not incremented properly: $original_last_assigned -> $new_last_assigned"
        return 1
    fi
    
    # Context count should increase
    if [ "$new_context_count" -le "$original_context_count" ]; then
        log "ERROR "context_assignments not updated: $original_context_count -> $new_context_count"
        return 1
    fi
    
    log "SUCCESS" "Re-initialization with different context works correctly"
    return 0
}

# Test 4: Re-initialization validates existing state integrity
test_reinit_validates_existing() {
    log "INFO" "Test 4: Testing re-initialization validates existing state integrity"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create initial state
    create_initial_state "validation_test"
    
    # Corrupt the state file slightly (remove a required field)
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    local corrupted_file="${state_file}.corrupted"
    
    jq 'del(.last_assigned)' "$state_file" > "$corrupted_file"
    mv "$corrupted_file" "$state_file"
    
    # Re-initialization should detect corruption and handle it
    if ! "$NUMBER_MANAGER_SCRIPT" init "validation_test" >/dev/null 2>&1; then
        log "ERROR" "Re-initialization failed with corrupted state"
        return 1
    fi
    
    # Check if state is now valid
    if ! jq empty "$state_file" 2>/dev/null; then
        log "ERROR" "State file still invalid after re-initialization"
        return 1
    fi
    
    # Check if required field is restored
    if ! jq -e '.last_assigned' "$state_file" >/dev/null; then
        log "ERROR" "Required field not restored after re-initialization"
        return 1
    fi
    
    log "SUCCESS" "Re-initialization validates and repairs existing state"
    return 0
}

# Test 5: Re-initialization handles partial directory structure
test_reinit_partial_structure() {
    log "INFO" "Test 5: Testing re-initialization with partial directory structure"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create partial structure (missing backup directory)
    mkdir -p "$TEST_STATE_DIR/.number_state"
    
    # Create a state file
    cat > "$TEST_STATE_DIR/.number_state/state.json" << 'EOF'
{
    "used_numbers": [1, 2, 3],
    "last_assigned": 3,
    "created_at": "2026-01-31T10:00:00Z",
    "updated_at": "2026-01-31T10:00:00Z",
    "context_assignments": {"test": "3"},
    "version": "1.0",
    "metadata": {
        "creator": "number_manager.sh",
        "purpose": "unique_number_tracking"
    }
}
EOF
    
    # Re-initialize should complete the structure
    if ! "$NUMBER_MANAGER_SCRIPT" init "structure_test" >/dev/null 2>&1; then
        log "ERROR" "Re-initialization with partial structure failed"
        return 1
    fi
    
    # Check if backup directory was created
    if [ ! -d "$TEST_STATE_DIR/.number_state/backup" ]; then
        log "ERROR" "Backup directory not created during re-initialization"
        return 1
    fi
    
    # Check if state is still valid
    if ! jq empty "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null; then
        log "ERROR" "State file became invalid during re-initialization"
        return 1
    fi
    
    log "SUCCESS" "Re-initialization completes partial directory structure"
    return 0
}

# Test 6: Re-initialization with corrupted JSON triggers recovery
test_reinit_corrupted_json_recovery() {
    log "INFO" "Test 6: Testing re-initialization with corrupted JSON triggers recovery"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create initial state with backup
    create_initial_state "corruption_test"
    
    # Create a backup by copying valid state
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    local backup_dir="$TEST_STATE_DIR/.number_state/backup"
    cp "$state_file" "$backup_dir/state_20260131_100000.json"
    
    # Corrupt the main state file
    echo '{"invalid": json}' > "$state_file"
    
    # Re-initialization should attempt recovery
    if ! "$NUMBER_MANAGER_SCRIPT" init "corruption_test" >/dev/null 2>&1; then
        log "ERROR" "Re-initialization failed with corrupted JSON"
        return 1
    fi
    
    # Check if state is valid again
    if ! jq empty "$state_file" 2>/dev/null; then
        log "ERROR" "State file not recovered from corruption"
        return 1
    fi
    
    # Check if required fields are present
    local required_fields=("used_numbers" "last_assigned" "context_assignments")
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$state_file" >/dev/null; then
            log "ERROR" "Field $field missing after recovery"
            return 1
        fi
    done
    
    log "SUCCESS" "Re-initialization recovers from corrupted JSON"
    return 0
}

# Test 7: Re-initialization preserves assignments and metadata
test_reinit_preserves_metadata() {
    log "INFO" "Test 7: Testing re-initialization preserves assignments and metadata"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create initial state with multiple contexts
    "$NUMBER_MANAGER_SCRIPT" init "metadata_test" >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" get "context1" >/dev/null 2>&1  # 1
    "$NUMBER_MANAGER_SCRIPT" get "context2" >/dev/null 2>&1  # 2
    "$NUMBER_MANAGER_SCRIPT" get "context1" >/dev/null 2>&1  # 3
    
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    
    # Get original assignments and metadata
    local original_contexts=$(jq -r '.context_assignments' "$state_file")
    local original_version=$(jq -r '.version' "$state_file")
    local original_creator=$(jq -r '.metadata.creator' "$state_file")
    local original_purpose=$(jq -r '.metadata.purpose' "$state_file")
    
    # Re-initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init "metadata_test" >/dev/null 2>&1; then
        log "ERROR" "Re-initialization failed"
        return 1
    fi
    
    # Check preservation
    local new_contexts=$(jq -r '.context_assignments' "$state_file")
    local new_version=$(jq -r '.version' "$state_file")
    local new_creator=$(jq -r '.metadata.creator' "$state_file")
    local new_purpose=$(jq -r '.metadata.purpose' "$state_file")
    
    if [ "$original_contexts" != "$new_contexts" ]; then
        log "ERROR" "context_assignments not preserved during re-initialization"
        return 1
    fi
    
    if [ "$original_version" != "$new_version" ]; then
        log "ERROR" "version not preserved during re-initialization"
        return 1
    fi
    
    if [ "$original_creator" != "$new_creator" ]; then
        log "ERROR" "metadata.creator not preserved during re-initialization"
        return 1
    fi
    
    if [ "$original_purpose" != "$new_purpose" ]; then
        log "ERROR" "metadata.purpose not preserved during re-initialization"
        return 1
    fi
    
    log "SUCCESS" "Re-initialization preserves assignments and metadata"
    return 0
}

# Test 8: Re-initialization concurrent safety
test_reinit_concurrent_safety() {
    log "INFO" "Test 8: Testing re-initialization concurrent safety"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create initial state
    create_initial_state "concurrent_test"
    
    # Run multiple re-initializations in parallel
    local pids=()
    for i in {1..3}; do
        "$NUMBER_MANAGER_SCRIPT" init "concurrent_test" >/dev/null 2>&1 &
        pids+=($!)
    done
    
    # Wait for all to complete
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
    
    # Check state is still valid
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if ! jq empty "$state_file" 2>/dev/null; then
        log "ERROR" "State file corrupted after concurrent re-initialization"
        return 1
    fi
    
    # Check required fields are present
    local required_fields=("used_numbers" "last_assigned" "context_assignments")
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$state_file" >/dev/null; then
            log "ERROR" "Field $field missing after concurrent re-initialization"
            return 1
        fi
    done
    
    log "SUCCESS" "Re-initialization is concurrent-safe"
    return 0
}

# Test 9: Re-initialization updates timestamps correctly
test_reinit_updates_timestamps() {
    log "INFO" "Test 9: Testing re-initialization updates timestamps correctly"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create initial state
    create_initial_state "timestamp_test"
    
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    local original_created_at=$(jq -r '.created_at' "$state_file")
    local original_updated_at=$(jq -r '.updated_at' "$state_file")
    
    # Wait a moment to ensure different timestamp
    sleep 1
    
    # Re-initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init "timestamp_test" >/dev/null 2>&1; then
        log "ERROR" "Re-initialization failed"
        return 1
    fi
    
    local new_created_at=$(jq -r '.created_at' "$state_file")
    local new_updated_at=$(jq -r '.updated_at' "$state_file")
    
    # Created_at should be preserved, updated_at should change
    if [ "$original_created_at" != "$new_created_at" ]; then
        log "ERROR" "created_at should be preserved during re-initialization"
        return 1
    fi
    
    if [ "$original_updated_at" = "$new_updated_at" ]; then
        log "ERROR" "updated_at should change during re-initialization"
        return 1
    fi
    
    log "SUCCESS" "Re-initialization updates timestamps correctly"
    return 0
}

# Main test execution
run_all_tests() {
    echo ""
    echo "=========================================="
    echo "Re-initialization Tests"
    echo "=========================================="
    
    run_test "Preserves Existing State" "test_reinit_preserves_state"
    run_test "No Overwrite Behavior" "test_reinit_no_overwrite"
    run_test "Different Context Handling" "test_reinit_different_context"
    run_test "Validates Existing State" "test_reinit_validates_existing"
    run_test "Partial Structure Completion" "test_reinit_partial_structure"
    run_test "Corrupted JSON Recovery" "test_reinit_corrupted_json_recovery"
    run_test "Preserves Metadata" "test_reinit_preserves_metadata"
    run_test "Concurrent Safety" "test_reinit_concurrent_safety"
    run_test "Updates Timestamps" "test_reinit_updates_timestamps"
    
    echo ""
    echo "=========================================="
    echo "Test Results: $TESTS_PASSED/$TESTS_RUN passed"
    echo "=========================================="
    
    if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
        log "SUCCESS" "All re-initialization tests passed!"
        return 0
    else
        log "ERROR" "Some re-initialization tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests re-initialization scenarios for number_manager.sh"
    exit 1
fi