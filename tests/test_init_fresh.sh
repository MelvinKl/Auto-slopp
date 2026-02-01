#!/bin/bash

# Test Fresh Initialization for number_manager.sh
# Tests brand new initialization scenarios including directory structure, 
# default configuration, and validation of created state files

SCRIPT_NAME="test_init_fresh"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_init_fresh_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

# Test results tracking
TESTS_RUN=0
TESTS_PASSED=0

log "INFO" "Starting fresh initialization tests in $TEST_STATE_DIR"

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

# Test 1: Fresh initialization creates required directory structure
test_fresh_directory_structure() {
    log "INFO" "Test 1: Testing fresh initialization directory structure"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Run initialization
    if ! "$NUMBER_MANAGER_SCRIPT" init fresh_context >/dev/null 2>&1; then
        log "ERROR" "Fresh initialization failed"
        return 1
    fi
    
    # Check if .number_state directory exists
    if [ ! -d "$TEST_STATE_DIR/.number_state" ]; then
        log "ERROR" ".number_state directory not created"
        return 1
    fi
    
    # Check if backup directory exists
    if [ ! -d "$TEST_STATE_DIR/.number_state/backup" ]; then
        log "ERROR" "backup directory not created"
        return 1
    fi
    
    # Check if state.json file exists
    if [ ! -f "$TEST_STATE_DIR/.number_state/state.json" ]; then
        log "ERROR" "state.json file not created"
        return 1
    fi
    
    # Check directory permissions
    if [ ! -r "$TEST_STATE_DIR/.number_state" ] || [ ! -w "$TEST_STATE_DIR/.number_state" ]; then
        log "ERROR" ".number_state directory has incorrect permissions"
        return 1
    fi
    
    log "SUCCESS" "Directory structure created correctly"
    return 0
}

# Test 2: Fresh initialization creates valid JSON structure
test_fresh_json_structure() {
    log "INFO" "Test 2: Testing fresh initialization JSON structure"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Run initialization
    if ! "$NUMBER_MANAGER_SCRIPT" init json_test >/dev/null 2>&1; then
        log "ERROR" "Fresh initialization failed"
        return 1
    fi
    
    # Validate JSON format
    if ! jq empty "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null; then
        log "ERROR" "Created state.json is not valid JSON"
        return 1
    fi
    
    # Check required fields exist
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    local required_fields=("used_numbers" "last_assigned" "context_assignments" "created_at" "updated_at" "version" "metadata")
    
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$state_file" >/dev/null; then
            log "ERROR" "Missing required field in fresh initialization: $field"
            return 1
        fi
    done
    
    log "SUCCESS" "JSON structure is valid with all required fields"
    return 0
}

# Test 3: Fresh initialization sets correct default values
test_fresh_default_values() {
    log "INFO" "Test 3: Testing fresh initialization default values"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Run initialization
    if ! "$NUMBER_MANAGER_SCRIPT" init defaults_test >/dev/null 2>&1; then
        log "ERROR" "Fresh initialization failed"
        return 1
    fi
    
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    
    # Check used_numbers is empty array
    local used_numbers=$(jq -r '.used_numbers | length' "$state_file")
    if [ "$used_numbers" != "0" ]; then
        log "ERROR" "used_numbers should be empty in fresh init, got length: $used_numbers"
        return 1
    fi
    
    # Check last_assigned is 0
    local last_assigned=$(jq -r '.last_assigned' "$state_file")
    if [ "$last_assigned" != "0" ]; then
        log "ERROR" "last_assigned should be 0 in fresh init, got: $last_assigned"
        return 1
    fi
    
    # Check context_assignments is empty object
    local context_count=$(jq -r '.context_assignments | keys | length' "$state_file")
    if [ "$context_count" != "0" ]; then
        log "ERROR" "context_assignments should be empty in fresh init, got: $context_count"
        return 1
    fi
    
    # Check version is set
    local version=$(jq -r '.version' "$state_file")
    if [ -z "$version" ] || [ "$version" = "null" ]; then
        log "ERROR" "version should be set in fresh init"
        return 1
    fi
    
    # Check metadata exists and has required fields
    local creator=$(jq -r '.metadata.creator' "$state_file")
    local purpose=$(jq -r '.metadata.purpose' "$state_file")
    
    if [ "$creator" != "number_manager.sh" ]; then
        log "ERROR" "metadata.creator should be 'number_manager.sh', got: $creator"
        return 1
    fi
    
    if [ "$purpose" != "unique_number_tracking" ]; then
        log "ERROR" "metadata.purpose should be 'unique_number_tracking', got: $purpose"
        return 1
    fi
    
    log "SUCCESS" "Default values are correctly set in fresh initialization"
    return 0
}

# Test 4: Fresh initialization creates valid timestamps
test_fresh_timestamps() {
    log "INFO" "Test 4: Testing fresh initialization timestamps"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Record start time
    local start_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    # Run initialization
    if ! "$NUMBER_MANAGER_SCRIPT" init timestamp_test >/dev/null 2>&1; then
        log "ERROR" "Fresh initialization failed"
        return 1
    fi
    
    # Record end time
    local end_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    local created_at=$(jq -r '.created_at' "$state_file")
    local updated_at=$(jq -r '.updated_at' "$state_file")
    
    # Validate timestamp format (ISO 8601 UTC)
    if ! [[ "$created_at" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
        log "ERROR" "created_at has invalid format: $created_at"
        return 1
    fi
    
    if ! [[ "$updated_at" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
        log "ERROR" "updated_at has invalid format: $updated_at"
        return 1
    fi
    
    # Check timestamps are within reasonable range
    if [[ "$created_at" < "$start_time" ]] || [[ "$created_at" > "$end_time" ]]; then
        log "ERROR" "created_at is outside expected time range: $created_at"
        return 1
    fi
    
    if [[ "$updated_at" < "$start_time" ]] || [[ "$updated_at" > "$end_time" ]]; then
        log "ERROR" "updated_at is outside expected time range: $updated_at"
        return 1
    fi
    
    # Check created_at equals updated_at for fresh init
    if [ "$created_at" != "$updated_at" ]; then
        log "ERROR" "created_at and updated_at should be equal in fresh init"
        return 1
    fi
    
    log "SUCCESS" "Timestamps are correctly formatted and valid"
    return 0
}

# Test 5: Fresh initialization with different contexts
test_fresh_different_contexts() {
    log "INFO" "Test 5: Testing fresh initialization with different contexts"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Test initialization with various context names
    local contexts=("test_context" "repo-name" "repo_name_with_underscores" "123numbers" "")
    
    for context in "${contexts[@]}"; do
        local context_arg="$context"
        if [ -z "$context" ]; then
            context_arg="default"
        fi
        
        # Clean state for each test
        rm -rf "$TEST_STATE_DIR/.number_state"
        
        if ! "$NUMBER_MANAGER_SCRIPT" init "$context" >/dev/null 2>&1; then
            log "ERROR" "Initialization failed for context: $context"
            return 1
        fi
        
        # Verify state file was created
        if [ ! -f "$TEST_STATE_DIR/.number_state/state.json" ]; then
            log "ERROR" "State file not created for context: $context"
            return 1
        fi
        
        # Validate JSON structure
        if ! jq empty "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null; then
            log "ERROR" "Invalid JSON created for context: $context"
            return 1
        fi
    done
    
    log "SUCCESS" "Fresh initialization works with different contexts"
    return 0
}

# Test 6: Fresh initialization handles permission errors gracefully
test_fresh_permission_errors() {
    log "INFO" "Test 6: Testing fresh initialization with permission errors"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create test directory
    mkdir -p "$TEST_STATE_DIR"
    
    # Create a read-only directory to simulate permission error
    local readonly_dir="$TEST_STATE_DIR/readonly"
    mkdir -p "$readonly_dir"
    chmod 444 "$readonly_dir"
    
    # Try to initialize in read-only directory
    export MANAGED_REPO_PATH="$readonly_dir"
    if "$NUMBER_MANAGER_SCRIPT" init permission_test >/dev/null 2>&1; then
        # This shouldn't succeed, but if it does, make sure we can clean up
        chmod -R 755 "$readonly_dir"
        log "ERROR" "Initialization should fail in read-only directory"
        return 1
    fi
    
    # Restore permissions for cleanup
    chmod -R 755 "$readonly_dir"
    
    # Restore original test directory
    export MANAGED_REPO_PATH="$TEST_STATE_DIR"
    
    log "SUCCESS" "Permission errors are handled gracefully"
    return 0
}

# Test 7: Fresh initialization creates atomically
test_fresh_atomic_creation() {
    log "INFO" "Test 7: Testing fresh initialization atomic creation"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Run initialization multiple times rapidly
    for i in {1..5}; do
        # Clean state for each attempt
        rm -rf "$TEST_STATE_DIR/.number_state"
        
        if ! "$NUMBER_MANAGER_SCRIPT" init "atomic_test_$i" >/dev/null 2>&1; then
            log "ERROR" "Atomic initialization failed on attempt $i"
            return 1
        fi
        
        # Verify state is complete and valid
        if [ ! -f "$TEST_STATE_DIR/.number_state/state.json" ]; then
            log "ERROR" "State file missing after atomic init attempt $i"
            return 1
        fi
        
        if ! jq empty "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null; then
            log "ERROR" "State file invalid after atomic init attempt $i"
            return 1
        fi
    done
    
    log "SUCCESS" "Fresh initialization creates atomically"
    return 0
}

# Test 8: Fresh initialization state file validation passes
test_fresh_state_validation() {
    log "INFO" "Test 8: Testing fresh initialization passes state validation"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Run initialization
    if ! "$NUMBER_MANAGER_SCRIPT" init validation_test >/dev/null 2>&1; then
        log "ERROR" "Fresh initialization failed"
        return 1
    fi
    
    # Run validation through the script's validate_state_file function
    # We can't call the function directly, but we can test it indirectly
    # by trying to get stats which includes validation
    
    local stats
    if stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null); then
        local status=$(echo "$stats" | jq -r '.status')
        if [ "$status" != "healthy" ]; then
            log "ERROR" "Fresh initialization state validation failed, status: $status"
            return 1
        fi
    else
        log "ERROR" "Stats command failed on fresh initialization"
        return 1
    fi
    
    log "SUCCESS" "Fresh initialization passes state validation"
    return 0
}

# Main test execution
run_all_tests() {
    echo ""
    echo "=========================================="
    echo "Fresh Initialization Tests"
    echo "=========================================="
    
    run_test "Directory Structure Creation" "test_fresh_directory_structure"
    run_test "JSON Structure Validation" "test_fresh_json_structure"
    run_test "Default Values Verification" "test_fresh_default_values"
    run_test "Timestamp Format Validation" "test_fresh_timestamps"
    run_test "Different Context Support" "test_fresh_different_contexts"
    run_test "Permission Error Handling" "test_fresh_permission_errors"
    run_test "Atomic Creation Test" "test_fresh_atomic_creation"
    run_test "State Validation Passes" "test_fresh_state_validation"
    
    echo ""
    echo "=========================================="
    echo "Test Results: $TESTS_PASSED/$TESTS_RUN passed"
    echo "=========================================="
    
    if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
        log "SUCCESS" "All fresh initialization tests passed!"
        return 0
    else
        log "ERROR" "Some fresh initialization tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests fresh initialization scenarios for number_manager.sh"
    exit 1
fi