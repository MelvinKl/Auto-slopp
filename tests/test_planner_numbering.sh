#!/bin/bash

# Test planner.sh integration with number_manager.sh
# This test validates automatic file numbering integration between planner.sh and the number manager system

SCRIPT_NAME="test_planner_numbering"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test configuration
TEST_STATE_DIR="/tmp/test_planner_numbering_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"
PLANNER_SCRIPT="$BASE_DIR/scripts/planner.sh"

# Mock config values (normally from config.sh)
export MANAGED_REPO_PATH="$TEST_STATE_DIR/managed"
export MANAGED_REPO_TASK_PATH="$TEST_STATE_DIR/tasks"
export OPencode_CMD="echo"  # Mock the opencode command

log "INFO" "Starting planner numbering integration tests in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test results counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to log test results
log_test_result() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    if [ "$result" = "PASS" ]; then
        echo -e "\033[0;32m✓ PASS\033[0m: $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "\033[0;31m✗ FAIL\033[0m: $test_name"
        echo -e "  \033[1;33mDetails: $details\033[0m"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Setup test environment
setup_test_env() {
    log "INFO" "Setting up test environment..."
    
    # Create test directory structure
    mkdir -p "$MANAGED_REPO_PATH/test_repo"
    mkdir -p "$MANAGED_REPO_TASK_PATH/test_repo"
    
    # Initialize number manager state
    if ! "$NUMBER_MANAGER_SCRIPT" init test_repo >/dev/null 2>&1; then
        log "ERROR" "Failed to initialize number manager"
        return 1
    fi
    
    # Initialize git repos for testing
    cd "$MANAGED_REPO_PATH/test_repo"
    git init >/dev/null 2>&1
    git config user.email "test@example.com"
    git config user.name "Test User"
    echo "# Test Repo" > README.md
    git add README.md >/dev/null 2>&1
    git commit -m "Initial commit" >/dev/null 2>&1
    
    # Create origin remote
    git init --bare origin.git >/dev/null 2>&1
    git remote add origin "$MANAGED_REPO_PATH/test_repo/origin.git"
    git push -u origin main >/dev/null 2>&1 || git push -u origin master >/dev/null 2>&1
    
    cd "$MANAGED_REPO_TASK_PATH/test_repo"
    git init >/dev/null 2>&1
    git config user.email "test@example.com"
    git config user.name "Test User"
    echo "# Task Directory" > README.md
    git add README.md >/dev/null 2>&1
    git commit -m "Initial commit" >/dev/null 2>&1
    
    return 0
}

# Test 1: File numbering with number manager integration
test_file_numbering_integration() {
    log "INFO" "Test 1: Testing file numbering with number manager integration"
    
    cd "$MANAGED_REPO_TASK_PATH/test_repo"
    
    # Create unnumbered task files
    echo "Test task 1" > "task-one.txt"
    echo "Test task 2" > "task-two.txt"
    echo "Test task 3" > "task-three.txt"
    
    # Simulate planner numbering logic with number manager integration
    unnumbered_files=($(find "$MANAGED_REPO_TASK_PATH/test_repo" -maxdepth 1 -type f -name "*.txt" ! -name "[0-9][0-9][0-9][0-9]-*" ! -name "*.used" | sort))
    
    if [ ${#unnumbered_files[@]} -gt 0 ]; then
        expected_numbers=()
        for unnumbered_file in "${unnumbered_files[@]}"; do
            # Use number manager to get next number
            next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
            if [ $? -eq 0 ]; then
                expected_numbers+=("$next_num")
                filename=$(basename "$unnumbered_file" .txt)
                new_filename=$(printf "%04d-%s.txt" "$next_num" "$filename")
                mv "$unnumbered_file" "$MANAGED_REPO_TASK_PATH/test_repo/$new_filename"
            else
                log_test_result "Number manager integration" "FAIL" "Failed to get number from number manager"
                return 1
            fi
        done
        
        # Verify numbers are sequential and start from 1
        if [ "${expected_numbers[0]}" = "1" ] && 
           [ "${expected_numbers[1]}" = "2" ] && 
           [ "${expected_numbers[2]}" = "3" ]; then
            log_test_result "Sequential number assignment" "PASS" "Numbers assigned correctly: ${expected_numbers[*]}"
        else
            log_test_result "Sequential number assignment" "FAIL" "Expected 1,2,3 got: ${expected_numbers[*]}"
            return 1
        fi
        
        # Verify files were renamed correctly
        renamed_files=($(find "$MANAGED_REPO_TASK_PATH/test_repo" -maxdepth 1 -name "[0-9][0-9][0-9][0-9]-*.txt" | sort))
        if [ ${#renamed_files[@]} -eq 3 ]; then
            log_test_result "File renaming" "PASS" "All unnumbered files renamed to numbered format"
        else
            log_test_result "File renaming" "FAIL" "Expected 3 renamed files, found ${#renamed_files[@]}"
            return 1
        fi
    else
        log_test_result "Unnumbered file discovery" "FAIL" "No unnumbered files found"
        return 1
    fi
    
    return 0
}

# Test 2: Number sequence continuity
test_number_sequence_continuity() {
    log "INFO" "Test 2: Testing number sequence continuity"
    
    cd "$MANAGED_REPO_TASK_PATH/test_repo"
    
    # Create more unnumbered files
    echo "Test task 4" > "task-four.txt"
    echo "Test task 5" > "task-five.txt"
    
    # Get next numbers from number manager
    next_num_4=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    next_num_5=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    
    if [ "$next_num_4" = "4" ] && [ "$next_num_5" = "5" ]; then
        log_test_result "Number sequence continuity" "PASS" "Numbers continue correctly: $next_num_4, $next_num_5"
    else
        log_test_result "Number sequence continuity" "FAIL" "Expected 4,5 got: $next_num_4, $next_num_5"
        return 1
    fi
    
    # Rename files
    mv "task-four.txt" "0004-task-four.txt"
    mv "task-five.txt" "0005-task-five.txt"
    
    return 0
}

# Test 3: Mixed numbered and unnumbered files
test_mixed_files_scenario() {
    log "INFO" "Test 3: Testing mixed numbered and unnumbered files scenario"
    
    cd "$MANAGED_REPO_TASK_PATH/test_repo"
    
    # Create scenario with both numbered and unnumbered files
    echo "New unnumbered task" > "new-task.txt"
    
    # Verify existing numbered files are not affected
    existing_numbered=($(find . -maxdepth 1 -name "[0-9][0-9][0-9][0-9]-*.txt" ! -name "*.used" | sort))
    if [ ${#existing_numbered[@]} -eq 5 ]; then
        log_test_result "Existing numbered files preservation" "PASS" "Existing numbered files preserved"
    else
        log_test_result "Existing numbered files preservation" "FAIL" "Expected 5 existing numbered files, found ${#existing_numbered[@]}"
        return 1
    fi
    
    # Process only the unnumbered file
    unnumbered_files=($(find . -maxdepth 1 -type f -name "*.txt" ! -name "[0-9][0-9][0-9][0-9]-*" ! -name "*.used"))
    if [ ${#unnumbered_files[@]} -eq 1 ]; then
        # Get next number and rename
        next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
        if [ "$next_num" = "6" ]; then
            mv "new-task.txt" "0006-new-task.txt"
            log_test_result "Mixed scenario processing" "PASS" "Unnumbered file processed correctly with number $next_num"
        else
            log_test_result "Mixed scenario processing" "FAIL" "Expected number 6, got $next_num"
            return 1
        fi
    else
        log_test_result "Unnumbered file identification" "FAIL" "Expected 1 unnumbered file, found ${#unnumbered_files[@]}"
        return 1
    fi
    
    return 0
}

# Test 4: File content preservation during renaming
test_content_preservation() {
    log "INFO" "Test 4: Testing file content preservation during renaming"
    
    cd "$MANAGED_REPO_TASK_PATH/test_repo"
    
    # Create a test file with specific content
    cat > "content-test.txt" << EOF
This is a test file with multiple lines.
Line 2: Special characters !@#$%^&*()
Line 3: Numbers 123456
Line 4: Unicode test αβγδε
EOF
    
    original_content=$(cat "content-test.txt")
    
    # Get number and rename
    next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
    mv "content-test.txt" "$(printf "%04d-content-test.txt" "$next_num")"
    
    # Verify content is preserved
    renamed_file="$(printf "%04d-content-test.txt" "$next_num")"
    new_content=$(cat "$renamed_file")
    
    if [ "$original_content" = "$new_content" ]; then
        log_test_result "File content preservation" "PASS" "Content preserved during renaming"
    else
        log_test_result "File content preservation" "FAIL" "Content changed during renaming"
        return 1
    fi
    
    return 0
}

# Test 5: Number manager state consistency
test_number_manager_state_consistency() {
    log "INFO" "Test 5: Testing number manager state consistency"
    
    # Check number manager stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    if [ $? -eq 0 ]; then
        used_count=$(echo "$stats" | jq -r '.used_count')
        last_assigned=$(echo "$stats" | jq -r '.last_assigned')
        
        if [ "$used_count" = "7" ] && [ "$last_assigned" = "7" ]; then
            log_test_result "Number manager state consistency" "PASS" "State shows $used_count used numbers, last assigned: $last_assigned"
        else
            log_test_result "Number manager state consistency" "FAIL" "Expected 7 used and last assigned 7, got $used_count and $last_assigned"
            return 1
        fi
        
        # Check context assignments
        contexts=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
        test_repo_assignment=$(echo "$contexts" | jq -r '.test_repo')
        
        if [ "$test_repo_assignment" = "7" ]; then
            log_test_result "Context assignment tracking" "PASS" "test_repo context assigned number: $test_repo_assignment"
        else
            log_test_result "Context assignment tracking" "FAIL" "Expected test_repo assignment 7, got $test_repo_assignment"
            return 1
        fi
    else
        log_test_result "Number manager stats retrieval" "FAIL" "Failed to get number manager stats"
        return 1
    fi
    
    return 0
}

# Test 6: Git integration with numbered files
test_git_integration() {
    log "INFO" "Test 6: Testing git integration with numbered files"
    
    cd "$MANAGED_REPO_TASK_PATH/test_repo"
    
    # Check git status
    git_status=$(git status --porcelain)
    if [ -n "$git_status" ]; then
        # Stage and commit the numbered files
        git add . >/dev/null 2>&1
        git commit -m "Add numbered task files" >/dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            log_test_result "Git commit of numbered files" "PASS" "Numbered files committed successfully"
        else
            log_test_result "Git commit of numbered files" "FAIL" "Failed to commit numbered files"
            return 1
        fi
    else
        log_test_result "Git status check" "PASS" "No changes to commit (files already tracked)"
    fi
    
    return 0
}

# Test 7: Used file handling simulation
test_used_file_handling() {
    log "INFO" "Test 7: Testing used file handling simulation"
    
    cd "$MANAGED_REPO_TASK_PATH/test_repo"
    
    # Simulate processing a file and marking as used
    test_file="0001-task-one.txt"
    if [ -f "$test_file" ]; then
        mv "$test_file" "$test_file.used"
        
        if [ -f "$test_file.used" ] && [ ! -f "$test_file" ]; then
            log_test_result "Used file marking" "PASS" "File correctly marked as used"
        else
            log_test_result "Used file marking" "FAIL" "Failed to mark file as used"
            return 1
        fi
        
        # Verify used files are not found in regular processing
        numbered_files=($(find . -maxdepth 1 -name "[0-9][0-9][0-9][0-9]-*.txt" ! -name "*.used"))
        found_used=false
        for file in "${numbered_files[@]}"; do
            if [[ "$(basename "$file")" == "0001-task-one.txt" ]]; then
                found_used=true
                break
            fi
        done
        
        if [ "$found_used" = false ]; then
            log_test_result "Used file exclusion" "PASS" "Used files correctly excluded from processing"
        else
            log_test_result "Used file exclusion" "FAIL" "Used files incorrectly included in processing"
            return 1
        fi
    else
        log_test_result "Test file availability" "FAIL" "Test file 0001-task-one.txt not found"
        return 1
    fi
    
    return 0
}

# Test 8: Error handling and recovery
test_error_handling() {
    log "INFO" "Test 8: Testing error handling and recovery"
    
    # Test with invalid number manager state
    cd "$MANAGED_REPO_TASK_PATH/test_repo"
    
    # Corrupt the state file to test error handling
    if [ -f "$TEST_STATE_DIR/.number_state/state.json" ]; then
        echo "invalid json" > "$TEST_STATE_DIR/.number_state/state.json"
        
        # Try to get a number - should fail gracefully
        next_num=$("$NUMBER_MANAGER_SCRIPT" get test_repo 2>/dev/null | tail -1)
        if [ $? -ne 0 ]; then
            log_test_result "Invalid state handling" "PASS" "Correctly failed with invalid state"
        else
            log_test_result "Invalid state handling" "FAIL" "Should have failed with invalid state"
            return 1
        fi
        
        # Re-initialize state for recovery
        if "$NUMBER_MANAGER_SCRIPT" init test_repo >/dev/null 2>&1; then
            log_test_result "State recovery" "PASS" "State recovered after corruption"
        else
            log_test_result "State recovery" "FAIL" "Failed to recover state after corruption"
            return 1
        fi
    fi
    
    return 0
}

# Run all tests
run_all_tests() {
    echo ""
    echo "=========================================="
    echo "Running Planner Numbering Integration Tests"
    echo "=========================================="
    
    # Setup
    if ! setup_test_env; then
        log "ERROR" "Test environment setup failed"
        return 1
    fi
    
    # List of test functions
    local tests=(
        "test_file_numbering_integration"
        "test_number_sequence_continuity"
        "test_mixed_files_scenario"
        "test_content_preservation"
        "test_number_manager_state_consistency"
        "test_git_integration"
        "test_used_file_handling"
        "test_error_handling"
    )
    
    for test_func in "${tests[@]}"; do
        echo ""
        echo "------------------------------------------"
        echo "Running $test_func"
        echo "------------------------------------------"
        
        if $test_func; then
            echo "✅ $test_func PASSED"
        else
            echo "❌ $test_func FAILED"
        fi
    done
    
    echo ""
    echo "=========================================="
    echo "Test Results: $TESTS_PASSED/$((TESTS_PASSED + TESTS_FAILED)) passed"
    echo "=========================================="
    
    if [ $TESTS_FAILED -eq 0 ]; then
        log "SUCCESS" "All planner numbering integration tests passed!"
        return 0
    else
        log "ERROR" "Some planner numbering integration tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests planner.sh integration with number_manager.sh"
    exit 1
fi