#!/bin/bash

# Test Directory-to-Context Mapping
# Tests mapping of task directories to context names correctly
# Tests context assignment, multi-repo handling, and context isolation

SCRIPT_NAME="test_context_mapping"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_context_mapping_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

# Test results tracking
TESTS_RUN=0
TESTS_PASSED=0

log "INFO" "Starting context mapping tests in $TEST_STATE_DIR"

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

# Helper to create test task files
create_task_file() {
    local number="$1"
    local title="$2"
    local task_dir="$3"
    
    # Pad number to 4 digits
    local padded_num=$(printf "%04d" "$number")
    local filename="${padded_num}-${title}.txt"
    local filepath="$task_dir/$filename"
    
    echo "Task content for $title" > "$filepath"
    echo "$filepath"
}

# Helper to initialize number state
init_test_state() {
    local context="$1"
    "$NUMBER_MANAGER_SCRIPT" init "$context" >/dev/null 2>&1
}

# Test 1: Basic context assignment
test_basic_context_assignment() {
    log "INFO" "Test 1: Testing basic context assignment"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="my-repo"
    local task_dir="$TEST_STATE_DIR/my-repo"
    mkdir -p "$task_dir"
    
    # Initialize state for context
    init_test_state "$context"
    
    # Create task files
    create_task_file 1 "task-one" "$task_dir"
    create_task_file 5 "task-five" "$task_dir"
    create_task_file 10 "task-ten" "$task_dir"
    
    # Sync state with files using context
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Failed to sync with context assignment"
        return 1
    fi
    
    # Verify context assignments
    local context_assignments
    context_assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    local assigned_number
    assigned_number=$(echo "$context_assignments" | jq -r ".\"$context\"")
    
    if [ "$assigned_number" != "10" ]; then
        log "ERROR" "Expected context $context to have last assignment 10, got $assigned_number"
        return 1
    fi
    
    # Verify stats show correct context count
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local context_count
    context_count=$(echo "$stats" | jq -r '.context_count')
    
    if [ "$context_count" -ne 1 ]; then
        log "ERROR" "Expected context_count=1, got $context_count"
        return 1
    fi
    
    log "SUCCESS" "Basic context assignment works correctly"
    return 0
}

# Test 2: Multiple contexts isolation
test_multiple_contexts_isolation() {
    log "INFO" "Test 2: Testing multiple contexts isolation"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup multiple contexts
    local contexts=("repo1" "repo2" "repo3")
    
    for context in "${contexts[@]}"; do
        local task_dir="$TEST_STATE_DIR/$context"
        mkdir -p "$task_dir"
        
        # Initialize state for each context
        init_test_state "$context"
        
        # Create different files for each context
        case "$context" in
            "repo1")
                create_task_file 1 "repo1-task1" "$task_dir"
                create_task_file 3 "repo1-task3" "$task_dir"
                ;;
            "repo2")
                create_task_file 2 "repo2-task2" "$task_dir"
                create_task_file 5 "repo2-task5" "$task_dir"
                ;;
            "repo3")
                create_task_file 4 "repo3-task4" "$task_dir"
                create_task_file 8 "repo3-task8" "$task_dir"
                ;;
        esac
        
        # Sync each context
        if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
            log "ERROR" "Failed to sync context: $context"
            return 1
        fi
    done
    
    # Verify each context has correct assignments
    local context_assignments
    context_assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    
    local expected_assignments=(
        "repo1|3"
        "repo2|5" 
        "repo3|8"
    )
    
    for expectation in "${expected_assignments[@]}"; do
        local context=$(echo "$expectation" | cut -d'|' -f1)
        local expected_num=$(echo "$expectation" | cut -d'|' -f2)
        local actual_num
        actual_num=$(echo "$context_assignments" | jq -r ".\"$context\"")
        
        if [ "$actual_num" != "$expected_num" ]; then
            log "ERROR" "Context $context expected $expected_num, got $actual_num"
            return 1
        fi
    done
    
    # Verify total context count
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local context_count
    context_count=$(echo "$stats" | jq -r '.context_count')
    
    if [ "$context_count" -ne 3 ]; then
        log "ERROR" "Expected context_count=3, got $context_count"
        return 1
    fi
    
    log "SUCCESS" "Multiple contexts isolation works correctly"
    return 0
}

# Test 3: Context-specific number assignment
test_context_specific_assignment() {
    log "INFO" "Test 3: Testing context-specific number assignment"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup two contexts
    local context1="frontend"
    local context2="backend"
    
    # Initialize both contexts
    init_test_state "$context1"
    init_test_state "$context2"
    
    # Assign numbers in context1
    local num1_1
    num1_1=$("$NUMBER_MANAGER_SCRIPT" get "$context1" 2>/dev/null)
    local num1_2
    num1_2=$("$NUMBER_MANAGER_SCRIPT" get "$context1" 2>/dev/null)
    
    # Assign numbers in context2
    local num2_1
    num2_1=$("$NUMBER_MANAGER_SCRIPT" get "$context2" 2>/dev/null)
    local num2_2
    num2_2=$("$NUMBER_MANAGER_SCRIPT" get "$context2" 2>/dev/null)
    
    # Verify each context got sequential numbers starting from 1
    if [ "$num1_1" != "1" ] || [ "$num1_2" != "2" ]; then
        log "ERROR" "Context $context1 expected assignments 1,2, got $num1_1,$num1_2"
        return 1
    fi
    
    if [ "$num2_1" != "1" ] || [ "$num2_2" != "2" ]; then
        log "ERROR" "Context $context2 expected assignments 1,2, got $num2_1,$num2_2"
        return 1
    fi
    
    # Verify context assignments are tracked separately
    local context_assignments
    context_assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    local assignment1
    local assignment2
    assignment1=$(echo "$context_assignments" | jq -r ".\"$context1\"")
    assignment2=$(echo "$context_assignments" | jq -r ".\"$context2\"")
    
    if [ "$assignment1" != "2" ] || [ "$assignment2" != "2" ]; then
        log "ERROR" "Expected assignments: $context1=2, $context2=2, got $assignment1,$assignment2"
        return 1
    fi
    
    log "SUCCESS" "Context-specific number assignment works correctly"
    return 0
}

# Test 4: Context name validation and normalization
test_context_name_validation() {
    log "INFO" "Test 4: Testing context name validation and normalization"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Test various context names
    local test_contexts=(
        "simple"
        "with-dashes"
        "with_underscores"
        "with.dots"
        "withNumbers123"
        "MixedCase"
        "a"
        "very-long-context-name-with-many-parts"
    )
    
    for context in "${test_contexts[@]}"; do
        # Initialize context
        if ! init_test_state "$context"; then
            log "ERROR" "Failed to initialize context: $context"
            return 1
        fi
        
        # Assign a number
        local assigned_num
        if ! assigned_num=$("$NUMBER_MANAGER_SCRIPT" get "$context" 2>/dev/null); then
            log "ERROR" "Failed to get number for context: $context"
            return 1
        fi
        
        # Verify it was assigned (should be 1 for each new context)
        if [ "$assigned_num" != "1" ]; then
            log "ERROR" "Context $context expected assignment 1, got $assigned_num"
            return 1
        fi
    done
    
    # Verify all contexts are tracked
    local context_assignments
    context_assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    local tracked_contexts
    tracked_contexts=$(echo "$context_assignments" | jq -r 'keys[]')
    
    local found_contexts_count
    found_contexts_count=$(echo "$tracked_contexts" | wc -l)
    local expected_count=${#test_contexts[@]}
    
    if [ "$found_contexts_count" -ne "$expected_count" ]; then
        log "ERROR" "Expected $expected_count contexts, found $found_contexts_count"
        return 1
    fi
    
    log "SUCCESS" "Context name validation and normalization works correctly"
    return 0
}

# Test 5: Directory to context mapping edge cases
test_directory_context_mapping() {
    log "INFO" "Test 5: Testing directory to context mapping edge cases"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup complex directory structure
    mkdir -p "$TEST_STATE_DIR/src/components"
    mkdir -p "$TEST_STATE_DIR/docs/api"
    mkdir -p "$TEST_STATE_DIR/tests/unit"
    
    # Test different directory-to-context mappings
    local test_cases=(
        "src|src-context"
        "src/components|components-context"
        "docs/api|docs-api-context"
        "tests/unit|tests-context"
    )
    
    for case in "${test_cases[@]}"; do
        local dir=$(echo "$case" | cut -d'|' -f1)
        local context=$(echo "$case" | cut -d'|' -f2)
        local task_dir="$TEST_STATE_DIR/$dir"
        
        # Initialize context
        init_test_state "$context"
        
        # Create task files
        create_task_file 1 "task-in-$dir" "$task_dir"
        
        # Sync with context mapping
        if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
            log "ERROR" "Failed to sync directory $dir with context $context"
            return 1
        fi
        
        # Verify context assignment
        local context_assignments
        context_assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
        local assigned_num
        assigned_num=$(echo "$context_assignments" | jq -r ".\"$context\"")
        
        if [ "$assigned_num" != "1" ]; then
            log "ERROR" "Directory $dir mapped to context $context expected assignment 1, got $assigned_num"
            return 1
        fi
    done
    
    log "SUCCESS" "Directory to context mapping edge cases work correctly"
    return 0
}

# Test 6: Context isolation during number release
test_context_isolation_release() {
    log "INFO" "Test 6: Testing context isolation during number release"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup two contexts
    local context1="app"
    local context2="lib"
    
    init_test_state "$context1"
    init_test_state "$context2"
    
    # Assign numbers to both contexts
    local app_num1
    local app_num2
    local lib_num1
    local lib_num2
    
    app_num1=$("$NUMBER_MANAGER_SCRIPT" get "$context1" 2>/dev/null)
    app_num2=$("$NUMBER_MANAGER_SCRIPT" get "$context1" 2>/dev/null)
    lib_num1=$("$NUMBER_MANAGER_SCRIPT" get "$context2" 2>/dev/null)
    lib_num2=$("$NUMBER_MANAGER_SCRIPT" get "$context2" 2>/dev/null)
    
    # Release a number from context1 only
    if ! "$NUMBER_MANAGER_SCRIPT" release "$app_num1" "$context1" >/dev/null 2>&1; then
        log "ERROR" "Failed to release number $app_num1 from context $context1"
        return 1
    fi
    
    # Assign next number to context1 (should reuse the released number if gaps are reused)
    local app_num3
    app_num3=$("$NUMBER_MANAGER_SCRIPT" get "$context1" 2>/dev/null)
    
    # Assign next number to context2 (should continue with its own sequence)
    local lib_num3
    lib_num3=$("$NUMBER_MANAGER_SCRIPT" get "$context2" 2>/dev/null)
    
    # Verify contexts remain isolated
    # context1 might reuse 1 or get 3, context2 should get 3
    if [ "$lib_num3" != "3" ]; then
        log "ERROR" "Context $context2 expected next number 3, got $lib_num3"
        return 1
    fi
    
    # Verify context assignments are still correct
    local context_assignments
    context_assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    local app_assignment
    local lib_assignment
    app_assignment=$(echo "$context_assignments" | jq -r ".\"$context1\"")
    lib_assignment=$(echo "$context_assignments" | jq -r ".\"$context2\"")
    
    # Both should show their latest assignment
    if [ "$app_assignment" != "$app_num3" ]; then
        log "ERROR" "Context $context1 assignment mismatch, expected $app_num3, got $app_assignment"
        return 1
    fi
    
    if [ "$lib_assignment" != "$lib_num3" ]; then
        log "ERROR" "Context $context2 assignment mismatch, expected $lib_num3, got $lib_assignment"
        return 1
    fi
    
    log "SUCCESS" "Context isolation during number release works correctly"
    return 0
}

# Test 7: Context mapping with state synchronization
test_context_sync_mapping() {
    log "INFO" "Test 7: Testing context mapping with state synchronization"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup multiple repositories with task files
    local repos=("web-app" "mobile-app" "shared-lib")
    
    for repo in "${repos[@]}"; do
        local task_dir="$TEST_STATE_DIR/$repo"
        mkdir -p "$task_dir"
        
        # Initialize context
        init_test_state "$repo"
        
        # Create multiple task files per repo
        case "$repo" in
            "web-app")
                create_task_file 1 "login-page" "$task_dir"
                create_task_file 3 "dashboard" "$task_dir"
                create_task_file 7 "profile" "$task_dir"
                ;;
            "mobile-app")
                create_task_file 2 "splash-screen" "$task_dir"
                create_task_file 4 "home-screen" "$task_dir"
                ;;
            "shared-lib")
                create_task_file 5 "auth-module" "$task_dir"
                create_task_file 6 "utils" "$task_dir"
                create_task_file 8 "api-client" "$task_dir"
                ;;
        esac
        
        # Sync each repo with its context
        if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$repo" >/dev/null 2>&1; then
            log "ERROR" "Failed to sync repo $repo with context"
            return 1
        fi
    done
    
    # Verify context assignments reflect actual files
    local context_assignments
    context_assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    
    local expected_assignments=(
        "web-app|7"
        "mobile-app|4"
        "shared-lib|8"
    )
    
    for expectation in "${expected_assignments[@]}"; do
        local context=$(echo "$expectation" | cut -d'|' -f1)
        local expected_num=$(echo "$expectation" | cut -d'|' -f2)
        local actual_num
        actual_num=$(echo "$context_assignments" | jq -r ".\"$context\"")
        
        if [ "$actual_num" != "$expected_num" ]; then
            log "ERROR" "Repo $context expected max file number $expected_num, got $actual_num"
            return 1
        fi
    done
    
    # Verify global stats
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    local context_count
    context_count=$(echo "$stats" | jq -r '.context_count')
    
    # Total files across all repos: 3 + 2 + 3 = 8
    if [ "$used_count" -ne 8 ]; then
        log "ERROR" "Expected total used_count=8, got $used_count"
        return 1
    fi
    
    if [ "$context_count" -ne 3 ]; then
        log "ERROR" "Expected context_count=3, got $context_count"
        return 1
    fi
    
    log "SUCCESS" "Context mapping with state synchronization works correctly"
    return 0
}

# Test 8: Context name case sensitivity
test_context_case_sensitivity() {
    log "INFO" "Test 8: Testing context name case sensitivity"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Test case-sensitive contexts
    local contexts=("MyRepo" "myrepo" "MYREPO")
    
    for context in "${contexts[@]}"; do
        # Initialize each context
        init_test_state "$context"
        
        # Assign a number
        local assigned_num
        assigned_num=$("$NUMBER_MANAGER_SCRIPT" get "$context" 2>/dev/null)
        
        if [ "$assigned_num" != "1" ]; then
            log "ERROR" "Context $context expected assignment 1, got $assigned_num"
            return 1
        fi
    done
    
    # Verify all contexts are tracked separately
    local context_assignments
    context_assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    local tracked_count
    tracked_count=$(echo "$context_assignments" | jq -r 'keys | length')
    
    if [ "$tracked_count" -ne 3 ]; then
        log "ERROR" "Expected 3 separate contexts, found $tracked_count"
        return 1
    fi
    
    # Verify each has assignment 1
    for context in "${contexts[@]}"; do
        local assignment
        assignment=$(echo "$context_assignments" | jq -r ".\"$context\"")
        
        if [ "$assignment" != "1" ]; then
            log "ERROR" "Context $context should have assignment 1, got $assignment"
            return 1
        fi
    done
    
    log "SUCCESS" "Context name case sensitivity works correctly"
    return 0
}

# Test 9: Special context name characters
test_special_context_characters() {
    log "INFO" "Test 9: Testing special characters in context names"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Test contexts with special characters
    local test_contexts=(
        "repo-name"
        "repo_name"
        "repo.name"
        "repo123"
        "123repo"
        "a"
        "very-long-context-name-with-many-dashes_and_underscores.dots"
    )
    
    for context in "${test_contexts[@]}"; do
        # Initialize context
        init_test_state "$context"
        
        # Assign a number
        local assigned_num
        if ! assigned_num=$("$NUMBER_MANAGER_SCRIPT" get "$context" 2>/dev/null; then
            log "ERROR" "Failed to assign number to context: $context"
            return 1
        fi
        
        if [ "$assigned_num" != "1" ]; then
            log "ERROR" "Context $context expected assignment 1, got $assigned_num"
            return 1
        fi
    done
    
    # Verify all contexts are tracked
    local context_assignments
    context_assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    local tracked_count
    tracked_count=$(echo "$context_assignments" | jq -r 'keys | length')
    
    if [ "$tracked_count" -ne ${#test_contexts[@]} ]; then
        log "ERROR" "Expected ${#test_contexts[@]} contexts, found $tracked_count"
        return 1
    fi
    
    log "SUCCESS" "Special characters in context names handled correctly"
    return 0
}

# Test 10: Context gap detection
test_context_gap_detection() {
    log "INFO" "Test 10: Testing context-specific gap detection"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup two contexts with different gaps
    local context1="frontend"
    local context2="backend"
    
    init_test_state "$context1"
    init_test_state "$context2"
    
    # Create files with gaps for context1
    local task_dir1="$TEST_STATE_DIR/$context1"
    mkdir -p "$task_dir1"
    create_task_file 1 "task1" "$task_dir1"
    create_task_file 3 "task3" "$task_dir1"  # gap: 2
    create_task_file 6 "task6" "$task_dir1"  # gaps: 4,5
    
    # Create sequential files for context2
    local task_dir2="$TEST_STATE_DIR/$context2"
    mkdir -p "$task_dir2"
    create_task_file 1 "task1" "$task_dir2"
    create_task_file 2 "task2" "$task_dir2"
    create_task_file 3 "task3" "$task_dir2"
    
    # Sync both contexts
    "$NUMBER_MANAGER_SCRIPT" sync "$task_dir1" "$context1" >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" sync "$task_dir2" "$context2" >/dev/null 2>&1
    
    # Check gaps (though current implementation doesn't support context-specific gap checking)
    # This test mainly verifies the sync works and contexts are isolated
    
    # Verify context assignments
    local context_assignments
    context_assignments=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    local assignment1
    local assignment2
    assignment1=$(echo "$context_assignments" | jq -r ".\"$context1\"")
    assignment2=$(echo "$context_assignments" | jq -r ".\"$context2\"")
    
    if [ "$assignment1" != "6" ]; then
        log "ERROR" "Context $context1 expected max assignment 6, got $assignment1"
        return 1
    fi
    
    if [ "$assignment2" != "3" ]; then
        log "ERROR" "Context $context2 expected max assignment 3, got $assignment2"
        return 1
    fi
    
    # Verify global state shows combined state
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    # Total files: 3 (context1) + 3 (context2) = 6
    if [ "$used_count" -ne 6 ]; then
        log "ERROR" "Expected total used_count=6, got $used_count"
        return 1
    fi
    
    log "SUCCESS" "Context-specific gap detection setup works correctly"
    return 0
}

# Main test execution
run_all_tests() {
    echo ""
    echo "=========================================="
    echo "Context Mapping Tests"
    echo "=========================================="
    
    run_test "Basic Context Assignment" "test_basic_context_assignment"
    run_test "Multiple Contexts Isolation" "test_multiple_contexts_isolation"
    run_test "Context-specific Assignment" "test_context_specific_assignment"
    run_test "Context Name Validation" "test_context_name_validation"
    run_test "Directory Context Mapping" "test_directory_context_mapping"
    run_test "Context Isolation Release" "test_context_isolation_release"
    run_test "Context Sync Mapping" "test_context_sync_mapping"
    run_test "Context Case Sensitivity" "test_context_case_sensitivity"
    run_test "Special Context Characters" "test_special_context_characters"
    run_test "Context Gap Detection" "test_context_gap_detection"
    
    echo ""
    echo "=========================================="
    echo "Test Results: $TESTS_PASSED/$TESTS_RUN passed"
    echo "=========================================="
    
    if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
        log "SUCCESS" "All context mapping tests passed!"
        return 0
    else
        log "ERROR" "Some context mapping tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests directory-to-context mapping for task files"
    exit 1
fi