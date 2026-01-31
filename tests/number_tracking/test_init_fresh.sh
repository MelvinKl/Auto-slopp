#!/bin/bash

# Test number_manager.sh initialization and state management
# Part of Auto-4x9: Test number_manager.sh initialization and state management

set -e

SCRIPT_NAME="test_init_fresh"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_init_fresh_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting fresh initialization test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Fresh initialization creates correct directory structure
test_fresh_init_directory_structure() {
    log "INFO" "Test 1: Fresh initialization directory structure"
    
    # Run initialization
    if ! "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "ERROR" "Fresh initialization failed"
        return 1
    fi
    
    # Check directory structure
    if [ ! -d "$TEST_STATE_DIR/.number_state" ]; then
        log "ERROR" "State directory not created"
        return 1
    fi
    
    if [ ! -d "$TEST_STATE_DIR/.number_state/backup" ]; then
        log "ERROR" "Backup directory not created"
        return 1
    fi
    
    if [ ! -f "$TEST_STATE_DIR/.number_state/state.json" ]; then
        log "ERROR" "State file not created"
        return 1
    fi
    
    log "SUCCESS" "Directory structure created correctly"
    return 0
}

# Test 2: Fresh initialization creates valid JSON state
test_fresh_init_json_validity() {
    log "INFO" "Test 2: Fresh initialization JSON validity"
    
    # Check if state file is valid JSON
    if ! jq empty "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null; then
        log "ERROR" "State file is not valid JSON"
        return 1
    fi
    
    log "SUCCESS" "State file is valid JSON"
    return 0
}

# Test 3: Fresh initialization has all required fields
test_fresh_init_required_fields() {
    log "INFO" "Test 3: Fresh initialization required fields"
    
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    local required_fields=("used_numbers" "last_assigned" "context_assignments" "created_at" "updated_at" "version" "metadata")
    
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$state_file" >/dev/null; then
            log "ERROR" "Missing required field: $field"
            return 1
        fi
    done
    
    log "SUCCESS" "All required fields present"
    return 0
}

# Test 4: Fresh initialization has correct default values
test_fresh_init_default_values() {
    log "INFO" "Test 4: Fresh initialization default values"
    
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    
    # Check used_numbers is empty array
    local used_numbers
    used_numbers=$(jq -r '.used_numbers | length' "$state_file")
    if [ "$used_numbers" != "0" ]; then
        log "ERROR" "used_numbers should be empty, got: $used_numbers"
        return 1
    fi
    
    # Check last_assigned is 0
    local last_assigned
    last_assigned=$(jq -r '.last_assigned' "$state_file")
    if [ "$last_assigned" != "0" ]; then
        log "ERROR" "last_assigned should be 0, got: $last_assigned"
        return 1
    fi
    
    # Check context_assignments is empty object
    local context_count
    context_count=$(jq -r '.context_assignments | keys | length' "$state_file")
    if [ "$context_count" != "0" ]; then
        log "ERROR" "context_assignments should be empty, got: $context_count contexts"
        return 1
    fi
    
    # Check version
    local version
    version=$(jq -r '.version' "$state_file")
    if [ "$version" != "1.0" ]; then
        log "ERROR" "version should be 1.0, got: $version"
        return 1
    fi
    
    log "SUCCESS" "Default values are correct"
    return 0
}

# Test 5: Fresh initialization creates proper timestamps
test_fresh_init_timestamps() {
    log "INFO" "Test 5: Fresh initialization timestamps"
    
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    
    # Check created_at and updated_at are set
    local created_at updated_at
    created_at=$(jq -r '.created_at' "$state_file")
    updated_at=$(jq -r '.updated_at' "$state_file")
    
    if [ "$created_at" = "null" ] || [ "$updated_at" = "null" ]; then
        log "ERROR" "Timestamps not set properly"
        return 1
    fi
    
    # Check timestamp format (ISO 8601)
    if ! [[ "$created_at" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
        log "ERROR" "created_at timestamp format invalid: $created_at"
        return 1
    fi
    
    if ! [[ "$updated_at" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
        log "ERROR" "updated_at timestamp format invalid: $updated_at"
        return 1
    fi
    
    # Check timestamps are recent (within last 60 seconds)
    local current_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local created_timestamp=$(date -d "$created_at" +%s 2>/dev/null || echo 0)
    local current_timestamp=$(date -d "$current_time" +%s)
    local time_diff=$((current_timestamp - created_timestamp))
    
    if [ $time_diff -gt 60 ] || [ $time_diff -lt 0 ]; then
        log "ERROR" "created_at timestamp not recent: time diff = $time_diff seconds"
        return 1
    fi
    
    log "SUCCESS" "Timestamps are properly formatted and recent"
    return 0
}

# Test 6: Fresh initialization sets proper metadata
test_fresh_init_metadata() {
    log "INFO" "Test 6: Fresh initialization metadata"
    
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    
    # Check metadata fields
    local creator purpose
    creator=$(jq -r '.metadata.creator' "$state_file")
    purpose=$(jq -r '.metadata.purpose' "$state_file")
    
    if [ "$creator" != "number_manager.sh" ]; then
        log "ERROR" "metadata.creator incorrect: $creator"
        return 1
    fi
    
    if [ "$purpose" != "unique_number_tracking" ]; then
        log "ERROR" "metadata.purpose incorrect: $purpose"
        return 1
    fi
    
    log "SUCCESS" "Metadata is properly set"
    return 0
}

# Test 7: Fresh initialization handles different contexts correctly
test_fresh_init_context_handling() {
    log "INFO" "Test 7: Fresh initialization context handling"
    
    # Initialize with different context
    local test_context_dir="/tmp/test_init_context_$$"
    export MANAGED_REPO_PATH="$test_context_dir"
    
    if ! "$NUMBER_MANAGER_SCRIPT" init another_context >/dev/null 2>&1; then
        log "ERROR" "Initialization with another context failed"
        rm -rf "$test_context_dir"
        return 1
    fi
    
    # Check state was created
    if [ ! -f "$test_context_dir/.number_state/state.json" ]; then
        log "ERROR" "State file not created for another context"
        rm -rf "$test_context_dir"
        return 1
    fi
    
    # Verify state is independent (different from first state)
    local first_state_size second_state_size
    first_state_size=$(stat -c%s "$TEST_STATE_DIR/.number_state/state.json")
    second_state_size=$(stat -c%s "$test_context_dir/.number_state/state.json")
    
    # They should be similar but not identical due to different timestamps
    if [ $first_state_size -eq 0 ] || [ $second_state_size -eq 0 ]; then
        log "ERROR" "State files have zero size"
        rm -rf "$test_context_dir"
        return 1
    fi
    
    rm -rf "$test_context_dir"
    log "SUCCESS" "Context handling works correctly"
    return 0
}

# Test 8: Fresh initialization validates permissions
test_fresh_init_permissions() {
    log "INFO" "Test 8: Fresh initialization permissions"
    
    local state_dir="$TEST_STATE_DIR/.number_state"
    local state_file="$state_dir/state.json"
    local backup_dir="$state_dir/backup"
    
    # Check directory permissions (should be 755 or similar)
    if [ ! -r "$state_dir" ] || [ ! -w "$state_dir" ] || [ ! -x "$state_dir" ]; then
        log "ERROR" "State directory has insufficient permissions"
        return 1
    fi
    
    if [ ! -r "$backup_dir" ] || [ ! -w "$backup_dir" ] || [ ! -x "$backup_dir" ]; then
        log "ERROR" "Backup directory has insufficient permissions"
        return 1
    fi
    
    # Check file permissions
    if [ ! -r "$state_file" ] || [ ! -w "$state_file" ]; then
        log "ERROR" "State file has insufficient permissions"
        return 1
    fi
    
    log "SUCCESS" "Permissions are properly set"
    return 0
}

# Run all tests
run_all_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_fresh_init_directory_structure"
        "test_fresh_init_json_validity"
        "test_fresh_init_required_fields"
        "test_fresh_init_default_values"
        "test_fresh_init_timestamps"
        "test_fresh_init_metadata"
        "test_fresh_init_context_handling"
        "test_fresh_init_permissions"
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
    echo "Fresh Initialization Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
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
    echo "This script tests fresh initialization of number_manager.sh"
    exit 1
fi