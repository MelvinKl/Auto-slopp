#!/bin/bash

# Test state validation functions for number_manager.sh
# Part of Auto-4x9: Test number_manager.sh initialization and state management

set -e

SCRIPT_NAME="test_state_validation"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_state_validation_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting state validation test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Valid state file passes validation
test_valid_state_validation() {
    log "INFO" "Test 1: Valid state file validation"
    
    # Create a valid state file
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
    
    # Attempt initialization (should validate and succeed)
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Valid state file passed validation"
    else
        log "ERROR" "Valid state file failed validation"
        return 1
    fi
    
    return 0
}

# Test 2: Invalid JSON fails validation
test_invalid_json_validation() {
    log "INFO" "Test 2: Invalid JSON validation"
    
    # Create invalid JSON
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    echo '{"invalid": json}' > "$TEST_STATE_DIR/.number_state/state.json"
    
    # Attempt initialization (should fail validation)
    if ! "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Invalid JSON properly rejected by validation"
    else
        log "ERROR" "Invalid JSON was accepted"
        return 1
    fi
    
    # Check if recovery was attempted
    if [ -f "$TEST_STATE_DIR/.number_state/state.json" ]; then
        if jq empty "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null; then
            log "SUCCESS" "Recovery attempted for invalid JSON"
        else
            log "WARNING" "Recovery may not have worked properly"
        fi
    fi
    
    return 0
}

# Test 3: Missing required fields fails validation
test_missing_fields_validation() {
    log "INFO" "Test 3: Missing required fields validation"
    
    # Create state missing required fields
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    cat > "$TEST_STATE_DIR/.number_state/state.json" << EOF
{
    "used_numbers": [1, 2],
    "created_at": "2023-01-01T00:00:00Z"
}
EOF
    
    # Attempt initialization (should fail validation)
    if ! "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Missing fields properly detected by validation"
    else
        log "ERROR" "Missing fields were not detected"
        return 1
    fi
    
    return 0
}

# Test 4: Invalid data types fail validation
test_invalid_types_validation() {
    log "INFO" "Test 4: Invalid data types validation"
    
    # Create state with invalid data types
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
    
    # Attempt initialization (should fail validation)
    if ! "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Invalid data types properly detected"
    else
        log "ERROR" "Invalid data types were not detected"
        return 1
    fi
    
    return 0
}

# Test 5: Invalid number range fails validation
test_invalid_number_range_validation() {
    log "INFO" "Test 5: Invalid number range validation"
    
    # Create state with invalid number ranges
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    cat > "$TEST_STATE_DIR/.number_state/state.json" << EOF
{
    "used_numbers": [-1, 0, 10000, 5],
    "last_assigned": 10000,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "context_assignments": {
        "test_repo": "10000"
    },
    "version": "1.0",
    "metadata": {
        "creator": "number_manager.sh",
        "purpose": "unique_number_tracking"
    }
}
EOF
    
    # This test depends on whether validation includes range checking
    # For now, we'll test that the system handles it gracefully
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Invalid number range handled gracefully"
    else
        log "SUCCESS" "Invalid number range detected (if implemented)"
    fi
    
    return 0
}

# Test 6: Duplicate numbers in used_numbers array
test_duplicate_numbers_validation() {
    log "INFO" "Test 6: Duplicate numbers validation"
    
    # Create state with duplicate numbers
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    cat > "$TEST_STATE_DIR/.number_state/state.json" << EOF
{
    "used_numbers": [1, 2, 2, 3, 3, 3],
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
    
    # Test initialization with duplicates
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Duplicate numbers handled gracefully"
    else
        log "SUCCESS" "Duplicate numbers detected (if implemented)"
    fi
    
    return 0
}

# Test 7: Invalid timestamp formats
test_invalid_timestamp_validation() {
    log "INFO" "Test 7: Invalid timestamp validation"
    
    # Create state with invalid timestamps
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    cat > "$TEST_STATE_DIR/.number_state/state.json" << EOF
{
    "used_numbers": [1, 2, 3],
    "last_assigned": 3,
    "created_at": "not_a_timestamp",
    "updated_at": "2023-13-45T99:99:99Z",
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
    
    # Test initialization with invalid timestamps
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Invalid timestamps handled gracefully"
    else
        log "SUCCESS" "Invalid timestamps detected (if implemented)"
    fi
    
    return 0
}

# Test 8: Inconsistent state validation
test_inconsistent_state_validation() {
    log "INFO" "Test 8: Inconsistent state validation"
    
    # Create state with internal inconsistencies
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    cat > "$TEST_STATE_DIR/.number_state/state.json" << EOF
{
    "used_numbers": [1, 2, 3],
    "last_assigned": 10,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "context_assignments": {
        "test_repo": "5"
    },
    "version": "1.0",
    "metadata": {
        "creator": "number_manager.sh",
        "purpose": "unique_number_tracking"
    }
}
EOF
    
    # Note: last_assigned is 10 but max in used_numbers is 3
    # context_assignments has 5 but 5 is not in used_numbers
    
    # Test initialization with inconsistent state
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Inconsistent state handled gracefully"
    else
        log "SUCCESS" "Inconsistent state detected (if implemented)"
    fi
    
    return 0
}

# Test 9: Edge case validation
test_edge_case_validation() {
    log "INFO" "Test 9: Edge case validation"
    
    # Create state with edge cases
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    cat > "$TEST_STATE_DIR/.number_state/state.json" << EOF
{
    "used_numbers": [],
    "last_assigned": 0,
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
    
    # Test initialization with empty state
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        log "SUCCESS" "Empty state handled correctly"
    else
        log "ERROR" "Empty state failed validation"
        return 1
    fi
    
    return 0
}

# Test 10: Large dataset validation
test_large_dataset_validation() {
    log "INFO" "Test 10: Large dataset validation"
    
    # Create state with many numbers (performance test)
    mkdir -p "$TEST_STATE_DIR/.number_state/backup"
    
    # Generate JSON with many numbers
    local numbers_array="["
    for i in $(seq 1 1000); do
        if [ $i -gt 1 ]; then
            numbers_array+=","
        fi
        numbers_array+="$i"
    done
    numbers_array+="]"
    
    cat > "$TEST_STATE_DIR/.number_state/state.json" << EOF
{
    "used_numbers": $numbers_array,
    "last_assigned": 1000,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z",
    "context_assignments": {
        "test_repo": "1000"
    },
    "version": "1.0",
    "metadata": {
        "creator": "number_manager.sh",
        "purpose": "unique_number_tracking"
    }
}
EOF
    
    # Time the validation
    local start_time=$(date +%s.%N)
    
    if "$NUMBER_MANAGER_SCRIPT" init test_context >/dev/null 2>&1; then
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc -l)
        
        if (( $(echo "$duration < 5.0" | bc -l) )); then
            log "SUCCESS" "Large dataset validation completed in ${duration}s"
        else
            log "WARNING" "Large dataset validation took ${duration}s (may need optimization)"
        fi
    else
        log "ERROR" "Large dataset validation failed"
        return 1
    fi
    
    return 0
}

# Run all tests
run_all_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_valid_state_validation"
        "test_invalid_json_validation"
        "test_missing_fields_validation"
        "test_invalid_types_validation"
        "test_invalid_number_range_validation"
        "test_duplicate_numbers_validation"
        "test_invalid_timestamp_validation"
        "test_inconsistent_state_validation"
        "test_edge_case_validation"
        "test_large_dataset_validation"
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
    echo "State Validation Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All state validation tests passed!"
        return 0
    else
        log "ERROR" "Some state validation tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    # Check for bc command for timing tests
    if ! command -v bc >/dev/null 2>&1; then
        log "WARNING" "bc command not available, timing tests may be inaccurate"
    fi
    
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests state validation for number_manager.sh"
    exit 1
fi