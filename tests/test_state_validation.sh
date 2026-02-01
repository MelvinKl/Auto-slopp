#!/bin/bash

# Test JSON Validation Functions for number_manager.sh
# Tests the validate_state_file function and various JSON structure validation scenarios
# including field validation, type checking, and edge cases

SCRIPT_NAME="test_state_validation"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_state_validation_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

# Test results tracking
TESTS_RUN=0
TESTS_PASSED=0

log "INFO" "Starting state validation tests in $TEST_STATE_DIR"

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

# Helper to create test state file with specific content
create_test_state() {
    local content="$1"
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    
    mkdir -p "$TEST_STATE_DIR/.number_state"
    echo "$content" > "$state_file"
}

# Test 1: Valid JSON structure passes validation
test_valid_json_structure() {
    log "INFO" "Test 1: Testing valid JSON structure passes validation"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create valid state file
    local valid_state='{
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
    }'
    
    create_test_state "$valid_state"
    
    # Test validation through stats command (which includes validation)
    local stats
    if stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null); then
        local status=$(echo "$stats" | jq -r '.status')
        if [ "$status" != "healthy" ]; then
            log "ERROR" "Valid JSON structure should pass validation, got status: $status"
            return 1
        fi
    else
        log "ERROR" "Stats command failed with valid JSON structure"
        return 1
    fi
    
    log "SUCCESS" "Valid JSON structure passes validation"
    return 0
}

# Test 2: Invalid JSON format fails validation
test_invalid_json_format() {
    log "INFO" "Test 2: Testing invalid JSON format fails validation"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create invalid JSON file
    local invalid_json='{"used_numbers": [1, 2, 3, "invalid": json}'
    create_test_state "$invalid_json"
    
    # Test validation should detect invalid JSON
    local stats
    if stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null); then
        local status=$(echo "$stats" | jq -r '.status')
        if [ "$status" != "corrupted" ]; then
            log "ERROR" "Invalid JSON should be marked as corrupted, got status: $status"
            return 1
        fi
    else
        # Stats command might fail entirely with invalid JSON, which is also valid behavior
        log "INFO" "Stats command correctly failed with invalid JSON"
    fi
    
    log "SUCCESS" "Invalid JSON format is properly detected"
    return 0
}

# Test 3: Missing required field fails validation
test_missing_required_field() {
    log "INFO" "Test 3: Testing missing required field fails validation"
    
    local required_fields=("used_numbers" "last_assigned" "context_assignments")
    
    for field in "${required_fields[@]}"; do
        # Ensure clean state
        rm -rf "$TEST_STATE_DIR"
        
        # Create state file missing one required field
        local incomplete_state='{
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
        }'
        
        # Remove the specific field
        incomplete_state=$(echo "$incomplete_state" | jq "del(.$field)")
        
        create_test_state "$incomplete_state"
        
        # Test validation should detect missing field
        # We need to test this indirectly since we can't call validate_state_file directly
        # Let's try to get a number which should fail if state is invalid
        if "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1; then
            log "ERROR" "State with missing field '$field' should fail validation"
            return 1
        fi
    done
    
    log "SUCCESS" "Missing required fields are properly detected"
    return 0
}

# Test 4: Wrong data types for fields fail validation
test_wrong_data_types() {
    log "INFO" "Test 4: Testing wrong data types fail validation"
    
    local type_mismatches=(
        'used_numbers|"[1, 2, 3]"|should be array but is string'
        'last_assigned|'"'"'3'"'"'|should be number but is string'
        'context_assignments|'"'"'{}'"'"'|should be object but is string'
    )
    
    for mismatch in "${type_mismatches[@]}"; do
        local field=$(echo "$mismatch" | cut -d'|' -f1)
        local wrong_value=$(echo "$mismatch" | cut -d'|' -f2)
        local description=$(echo "$mismatch" | cut -d'|' -f3)
        
        # Ensure clean state
        rm -rf "$TEST_STATE_DIR"
        
        # Create state with wrong type
        local base_state='{
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
        }'
        
        # Modify to have wrong type
        local bad_state=$(echo "$base_state" | jq --arg field "$field" --argjson value "$wrong_value" '.[$field] = $value')
        create_test_state "$bad_state"
        
        # Test should fail validation
        if "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1; then
            log "ERROR "Type mismatch not detected for $field ($description)"
            return 1
        fi
    done
    
    log "SUCCESS" "Wrong data types are properly detected"
    return 0
}

# Test 5: Empty state file fails validation
test_empty_state_file() {
    log "INFO" "Test 5: Testing empty state file fails validation"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create empty state file
    mkdir -p "$TEST_STATE_DIR/.number_state"
    touch "$TEST_STATE_DIR/.number_state/state.json"
    
    # Test validation should fail
    if "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1; then
        log "ERROR" "Empty state file should fail validation"
        return 1
    fi
    
    log "SUCCESS" "Empty state file is properly detected"
    return 0
}

# Test 6: Non-existent state file fails validation
test_nonexistent_state_file() {
    log "INFO" "Test 6: Testing non-existent state file fails validation"
    
    # Ensure clean state with directory but no file
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$TEST_STATE_DIR/.number_state"
    # Don't create state.json
    
    # Test should fail
    if "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1; then
        log "ERROR" "Non-existent state file should fail validation"
        return 1
    fi
    
    log "SUCCESS" "Non-existent state file is properly detected"
    return 0
}

# Test 7: Null values in required fields fail validation
test_null_values_in_fields() {
    log "INFO" "Test 7: Testing null values in required fields fail validation"
    
    local required_fields=("used_numbers" "last_assigned" "context_assignments")
    
    for field in "${required_fields[@]}"; do
        # Ensure clean state
        rm -rf "$TEST_STATE_DIR"
        
        # Create state with null field
        local null_field_state='{
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
        }'
        
        # Set field to null
        null_field_state=$(echo "$null_field_state" | jq --arg field "$field" '.[$field] = null')
        create_test_state "$null_field_state"
        
        # Test should fail validation
        if "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1; then
            log "ERROR "Null value in $field should fail validation"
            return 1
        fi
    done
    
    log "SUCCESS" "Null values in required fields are properly detected"
    return 0
}

# Test 8: Valid but incomplete state passes partial validation
test_valid_incomplete_state() {
    log "INFO" "Test 8: Testing valid but incomplete state passes partial validation"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create minimal valid state (only required fields)
    local minimal_state='{
        "used_numbers": [],
        "last_assigned": 0,
        "context_assignments": {}
    }'
    
    create_test_state "$minimal_state"
    
    # Test validation through get operation (which validates first)
    if "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1; then
        # Check that we actually get a number
        local number=$("$NUMBER_MANAGER_SCRIPT" get "test" 2>/dev/null | tail -1)
        if [ "$number" = "1" ]; then
            log "SUCCESS" "Minimal valid state passes validation"
        else
            log "ERROR "Minimal state should work but returned unexpected number: $number"
            return 1
        fi
    else
        log "ERROR "Minimal valid state should pass validation"
        return 1
    fi
    
    return 0
}

# Test 9: Valid JSON with extra fields passes validation
test_extra_fields_validation() {
    log "INFO" "Test 9: Testing valid JSON with extra fields passes validation"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Create state with extra fields
    local extra_fields_state='{
        "used_numbers": [1, 2, 3],
        "last_assigned": 3,
        "created_at": "2026-01-31T10:00:00Z",
        "updated_at": "2026-01-31T10:00:00Z",
        "context_assignments": {"test": "3"},
        "version": "1.0",
        "metadata": {
            "creator": "number_manager.sh",
            "purpose": "unique_number_tracking"
        },
        "extra_field": "should_not_break_validation",
        "another_extra": {
            "nested": "object"
        },
        "extra_array": [1, 2, 3]
    }'
    
    create_test_state "$extra_fields_state"
    
    # Test validation should pass
    if "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1; then
        log "SUCCESS" "Valid JSON with extra fields passes validation"
    else
        log "ERROR "Valid JSON with extra fields should pass validation"
        return 1
    fi
    
    return 0
}

# Test 10: Used numbers array validation
test_used_numbers_validation() {
    log "INFO" "Test 10: Testing used_numbers array validation"
    
    # Test various used_numbers scenarios
    local test_cases=(
        '[]|empty array|valid'
        '[1, 2, 3]|valid numbers|valid'
        '[0]|includes zero|valid'
        '["1", "2"]|strings in array|invalid'
        'null|null instead of array|invalid'
        '"[1,2,3]"|string instead of array|invalid'
        '{"not": "an array"}|object instead of array|invalid'
    )
    
    for case in "${test_cases[@]}"; do
        local used_numbers=$(echo "$case" | cut -d'|' -f1)
        local description=$(echo "$case" | cut -d'|' -f2)
        local expected=$(echo "$case" | cut -d'|' -f3)
        
        # Ensure clean state
        rm -rf "$TEST_STATE_DIR"
        
        # Create state with specific used_numbers
        local test_state="{
            \"used_numbers\": $used_numbers,
            \"last_assigned\": 3,
            \"context_assignments\": {\"test\": \"3\"}
        }"
        
        create_test_state "$test_state"
        
        if [ "$expected" = "valid" ]; then
            if ! "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1; then
                log "ERROR "Valid used_numbers case failed: $description"
                return 1
            fi
        else
            if "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1; then
                log "ERROR "Invalid used_numbers case should fail: $description"
                return 1
            fi
        fi
    done
    
    log "SUCCESS" "Used numbers array validation works correctly"
    return 0
}

# Test 11: Context assignments validation
test_context_assignments_validation() {
    log "INFO" "Test 11: Testing context_assignments validation"
    
    # Test various context_assignments scenarios
    local test_cases=(
        '{}|empty object|valid'
        '{"test": "3"}|valid object|valid'
        '{"test": 3}|number value|valid'
        'null|null instead of object|invalid'
        '"not object"|string instead of object|invalid'
        '["not", "object"]|array instead of object|invalid'
    )
    
    for case in "${test_cases[@]}"; do
        local context_assignments=$(echo "$case" | cut -d'|' -f1)
        local description=$(echo "$case" | cut -d'|' -f2)
        local expected=$(echo "$case" | cut -d'|' -f3)
        
        # Ensure clean state
        rm -rf "$TEST_STATE_DIR"
        
        # Create state with specific context_assignments
        local test_state="{
            \"used_numbers\": [1, 2, 3],
            \"last_assigned\": 3,
            \"context_assignments\": $context_assignments
        }"
        
        create_test_state "$test_state"
        
        if [ "$expected" = "valid" ]; then
            if ! "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1; then
                log "ERROR "Valid context_assignments case failed: $description"
                return 1
            fi
        else
            if "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1; then
                log "ERROR "Invalid context_assignments case should fail: $description"
                return 1
            fi
        fi
    done
    
    log "SUCCESS" "Context assignments validation works correctly"
    return 0
}

# Test 12: Last assigned validation
test_last_assigned_validation() {
    log "INFO" "Test 12: Testing last_assigned validation"
    
    # Test various last_assigned scenarios
    local test_cases=(
        '0|zero|valid'
        '1|positive number|valid'
        '999|large number|valid'
        '"1"|string number|invalid'
        '-1|negative number|should_fail_or_work'
        'null|null value|invalid'
        '"not number"|string text|invalid'
    )
    
    for case in "${test_cases[@]}"; do
        local last_assigned=$(echo "$case" | cut -d'|' -f1)
        local description=$(echo "$case" | cut -d'|' -f2)
        local expected=$(echo "$case" | cut -d'|' -f3)
        
        # Ensure clean state
        rm -rf "$TEST_STATE_DIR"
        
        # Create state with specific last_assigned
        local test_state="{
            \"used_numbers\": [1, 2, 3],
            \"last_assigned\": $last_assigned,
            \"context_assignments\": {\"test\": \"3\"}
        }"
        
        create_test_state "$test_state"
        
        if [ "$expected" = "valid" ]; then
            if ! "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1; then
                log "ERROR "Valid last_assigned case failed: $description"
                return 1
            fi
        elif [ "$expected" = "invalid" ]; then
            if "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1; then
                log "ERROR "Invalid last_assigned case should fail: $description"
                return 1
            fi
        else
            # should_fail_or_work - check that it doesn't crash
            "$NUMBER_MANAGER_SCRIPT" get "test" >/dev/null 2>&1 || true
        fi
    done
    
    log "SUCCESS" "Last assigned validation works correctly"
    return 0
}

# Main test execution
run_all_tests() {
    echo ""
    echo "=========================================="
    echo "State Validation Tests"
    echo "=========================================="
    
    run_test "Valid JSON Structure" "test_valid_json_structure"
    run_test "Invalid JSON Format" "test_invalid_json_format"
    run_test "Missing Required Fields" "test_missing_required_field"
    run_test "Wrong Data Types" "test_wrong_data_types"
    run_test "Empty State File" "test_empty_state_file"
    run_test "Non-existent State File" "test_nonexistent_state_file"
    run_test "Null Values in Fields" "test_null_values_in_fields"
    run_test "Valid Incomplete State" "test_valid_incomplete_state"
    run_test "Extra Fields Validation" "test_extra_fields_validation"
    run_test "Used Numbers Validation" "test_used_numbers_validation"
    run_test "Context Assignments Validation" "test_context_assignments_validation"
    run_test "Last Assigned Validation" "test_last_assigned_validation"
    
    echo ""
    echo "=========================================="
    echo "Test Results: $TESTS_PASSED/$TESTS_RUN passed"
    echo "=========================================="
    
    if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
        log "SUCCESS" "All state validation tests passed!"
        return 0
    else
        log "ERROR" "Some state validation tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests JSON validation functions for number_manager.sh"
    exit 1
fi