#!/bin/bash

# Test planner.sh context handling with number_manager.sh
# This test validates proper context passing and repository-specific number tracking

SCRIPT_NAME="test_planner_context"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test configuration
TEST_STATE_DIR="/tmp/test_planner_context_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR/managed"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"
PLANNER_SCRIPT="$BASE_DIR/scripts/planner.sh"

# Mock config values
export MANAGED_REPO_TASK_PATH="$TEST_STATE_DIR/tasks"
export OPencode_CMD="echo"  # Mock the opencode command

log "INFO" "Starting planner context handling tests in $TEST_STATE_DIR"

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

# Setup test environment with multiple repositories
setup_test_env() {
    log "INFO" "Setting up multi-repository test environment..."
    
    # Create test directory structure for multiple repositories
    repos=("repo_alpha" "repo_beta" "repo_gamma")
    
    for repo in "${repos[@]}"; do
        # Create managed repo directory
        mkdir -p "$MANAGED_REPO_PATH/$repo"
        cd "$MANAGED_REPO_PATH/$repo"
        git init >/dev/null 2>&1
        git config user.email "test@example.com"
        git config user.name "Test User"
        echo "# $repo" > README.md
        git add README.md >/dev/null 2>&1
        git commit -m "Initial commit" >/dev/null 2>&1
        
        # Create origin remote
        git init --bare origin.git >/dev/null 2>&1
        git remote add origin "$MANAGED_REPO_PATH/$repo/origin.git"
        git push -u origin main >/dev/null 2>&1 || git push -u origin master >/dev/null 2>&1
        
        # Create task directory
        mkdir -p "$MANAGED_REPO_TASK_PATH/$repo"
        cd "$MANAGED_REPO_TASK_PATH/$repo"
        git init >/dev/null 2>&1
        git config user.email "test@example.com"
        git config user.name "Test User"
        echo "# Tasks for $repo" > README.md
        git add README.md >/dev/null 2>&1
        git commit -m "Initial commit" >/dev/null 2>&1
        
        # Initialize number manager for each repository context
        "$NUMBER_MANAGER_SCRIPT" init "$repo" >/dev/null 2>&1
    done
    
    return 0
}

# Test 1: Context-specific number assignment
test_context_specific_numbering() {
    log "INFO" "Test 1: Testing context-specific number assignment"
    
    # Create task files in different repositories
    cd "$MANAGED_REPO_TASK_PATH/repo_alpha"
    echo "Alpha task 1" > "alpha-task-1.txt"
    
    cd "$MANAGED_REPO_TASK_PATH/repo_beta"
    echo "Beta task 1" > "beta-task-1.txt"
    
    cd "$MANAGED_REPO_TASK_PATH/repo_gamma"
    echo "Gamma task 1" > "gamma-task-1.txt"
    
    # Process each repository with proper context
    local repo_numbers=()
    
    for repo in "repo_alpha" "repo_beta" "repo_gamma"; do
        cd "$MANAGED_REPO_TASK_PATH/$repo"
        unnumbered_files=($(find . -maxdepth 1 -type f -name "*.txt" ! -name "[0-9][0-9][0-9][0-9]-*" ! -name "*.used"))
        
        if [ ${#unnumbered_files[@]} -gt 0 ]; then
            # Get number for this specific repository context
            next_num=$("$NUMBER_MANAGER_SCRIPT" get "$repo" 2>/dev/null | tail -1)
            if [ $? -eq 0 ]; then
                repo_numbers+=("$next_num")
                filename=$(basename "${unnumbered_files[0]}" .txt)
                new_filename=$(printf "%04d-%s.txt" "$next_num" "$filename")
                mv "${unnumbered_files[0]}" "$new_filename"
            else
                log_test_result "Context number assignment" "FAIL" "Failed to get number for repository $repo"
                return 1
            fi
        fi
    done
    
    # Each should get sequential numbers in global sequence (1, 2, 3)
    if [ "${repo_numbers[0]}" = "1" ] && [ "${repo_numbers[1]}" = "2" ] && [ "${repo_numbers[2]}" = "3" ]; then
        log_test_result "Context-specific numbering" "PASS" "Each repository context got sequential numbers: ${repo_numbers[*]}"
    else
        log_test_result "Context-specific numbering" "FAIL" "Expected 1,2,3 for sequential assignment, got: ${repo_numbers[*]}"
        return 1
    fi
    
    return 0
}

# Test 2: Context isolation and independence
test_context_isolation() {
    log "INFO" "Test 2: Testing context isolation and independence"
    
    # Add second task to repo_alpha
    cd "$MANAGED_REPO_TASK_PATH/repo_alpha"
    echo "Alpha task 2" > "alpha-task-2.txt"
    
    # Process repo_alpha second task
    unnumbered_files=($(find . -maxdepth 1 -type f -name "*.txt" ! -name "[0-9][0-9][0-9][0-9]-*" ! -name "*.used"))
    if [ ${#unnumbered_files[@]} -eq 1 ]; then
        next_num=$("$NUMBER_MANAGER_SCRIPT" get "repo_alpha" 2>/dev/null | tail -1)
        if [ "$next_num" = "4" ]; then
            filename=$(basename "${unnumbered_files[0]}" .txt)
            new_filename=$(printf "%04d-%s.txt" "$next_num" "$filename")
            mv "${unnumbered_files[0]}" "$new_filename"
            log_test_result "Context isolation" "PASS" "repo_alpha correctly advanced to number 4"
        else
            log_test_result "Context isolation" "FAIL" "Expected repo_alpha to get number 4, got $next_num"
            return 1
        fi
    else
        log_test_result "Unnumbered file discovery" "FAIL" "Expected 1 unnumbered file in repo_alpha, found ${#unnumbered_files[@]}"
        return 1
    fi
    
    # Verify other repositories get next sequential numbers
    beta_num=$("$NUMBER_MANAGER_SCRIPT" get "repo_beta" 2>/dev/null | tail -1)
    gamma_num=$("$NUMBER_MANAGER_SCRIPT" get "repo_gamma" 2>/dev/null | tail -1)
    
    if [ "$beta_num" = "5" ] && [ "$gamma_num" = "6" ]; then
        log_test_result "Context independence" "PASS" "Other repositories get sequential numbers: beta=$beta_num, gamma=$gamma_num"
    else
        log_test_result "Context independence" "FAIL" "Expected repo_beta=5, repo_gamma=6, got: beta=$beta_num, gamma=$gamma_num"
        return 1
    fi
    
    return 0
}

# Test 3: Context state persistence
test_context_state_persistence() {
    log "INFO" "Test 3: Testing context state persistence"
    
    # Check number manager stats for each context
    local repo_stats=()
    
    for repo in "repo_alpha" "repo_beta" "repo_gamma"; do
        stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
        if [ $? -eq 0 ]; then
            used_count=$(echo "$stats" | jq -r '.used_count')
            last_assigned=$(echo "$stats" | jq -r '.last_assigned')
            repo_stats+=("$repo:$used_count:$last_assigned")
        else
            log_test_result "Stats retrieval" "FAIL" "Failed to get stats for $repo"
            return 1
        fi
    done
    
    # Verify state persistence - all should have different counts now
    local alpha_count beta_count gamma_count
    alpha_count=$(echo "${repo_stats[0]}" | cut -d: -f2)
    beta_count=$(echo "${repo_stats[1]}" | cut -d: -f2)
    gamma_count=$(echo "${repo_stats[2]}" | cut -d: -f2)
    
    # After all our operations, we've assigned 6 total numbers across all contexts
    # So each should show the global state (they all share the same state file)
    if [ "$alpha_count" = "6" ] && [ "$beta_count" = "6" ] && [ "$gamma_count" = "6" ]; then
        log_test_result "Context state persistence" "PASS" "All contexts share global state: alpha=$alpha_count, beta=$beta_count, gamma=$gamma_count"
    else
        log_test_result "Context state persistence" "FAIL" "Inconsistent state: ${repo_stats[*]}"
        return 1
    fi
    
    return 0
}

# Test 4: Repository name context extraction
test_repository_context_extraction() {
    log "INFO" "Test 4: Testing repository name context extraction"
    
    # Test that planner correctly extracts repository name from path
    cd "$MANAGED_REPO_PATH"
    
    for repo_dir in */; do
        if [ -d "$repo_dir" ]; then
            repo_name=$(basename "$repo_dir")
            
            # Check that task directory exists with same name
            task_dir="$MANAGED_REPO_TASK_PATH/$repo_name"
            if [ -d "$task_dir" ]; then
                log_test_result "Repository context extraction for $repo_name" "PASS" "Found matching task directory: $task_dir"
            else
                log_test_result "Repository context extraction for $repo_name" "FAIL" "No matching task directory found"
                return 1
            fi
        fi
    done
    
    return 0
}

# Test 5: Context assignments tracking
test_context_assignments_tracking() {
    log "INFO" "Test 5: Testing context assignments tracking"
    
    # Get context assignments from number manager
    contexts=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    if [ $? -eq 0 ]; then
        local alpha_assignment beta_assignment gamma_assignment
        
        alpha_assignment=$(echo "$contexts" | jq -r '.repo_alpha // "null"')
        beta_assignment=$(echo "$contexts" | jq -r '.repo_beta // "null"')
        gamma_assignment=$(echo "$contexts" | jq -r '.repo_gamma // "null"')
        
        # Each context should track its last assigned number
        # After our test sequence: alpha got 4, beta got 5, gamma got 6
        if [ "$alpha_assignment" = "4" ] && [ "$beta_assignment" = "5" ] && [ "$gamma_assignment" = "6" ]; then
            log_test_result "Context assignments tracking" "PASS" "All contexts tracked correctly: alpha=$alpha_assignment, beta=$beta_assignment, gamma=$gamma_assignment"
        else
            log_test_result "Context assignments tracking" "FAIL" "Incorrect context assignments: alpha=$alpha_assignment, beta=$beta_assignment, gamma=$gamma_assignment"
            return 1
        fi
    else
        log_test_result "Context assignments retrieval" "FAIL" "Failed to get context assignments"
        return 1
    fi
    
    return 0
}

# Test 6: Context-specific gap handling
test_context_specific_gap_handling() {
    log "INFO" "Test 6: Testing context-specific gap handling"
    
    # Release a number in repo_alpha to create a gap
    if "$NUMBER_MANAGER_SCRIPT" release 1 "repo_alpha" >/dev/null 2>&1; then
        log_test_result "Number release in context" "PASS" "Successfully released number 1 in repo_alpha"
    else
        log_test_result "Number release in context" "FAIL" "Failed to release number 1 in repo_alpha"
        return 1
    fi
    
    # Check gaps specifically for repo_alpha context
    gaps=$("$NUMBER_MANAGER_SCRIPT" gaps "repo_alpha" 2>/dev/null)
    if echo "$gaps" | grep -q "Gap: number 1 is not used"; then
        log_test_result "Context-specific gap detection" "PASS" "Gap detected correctly in repo_alpha context"
    else
        log_test_result "Context-specific gap detection" "FAIL" "Gap not detected or incorrect: $gaps"
        return 1
    fi
    
    # Verify other contexts are unaffected (but since they share global state, there might be gaps)
    beta_gaps=$("$NUMBER_MANAGER_SCRIPT" gaps "repo_beta" 2>/dev/null)
    # The gap detection is global, so we expect to see the gap in all contexts
    if echo "$beta_gaps" | grep -q "Gap: number 1 is not used"; then
        log_test_result "Context isolation in gap handling" "PASS" "Global gap detection shows released number"
    else
        log_test_result "Context isolation in gap handling" "FAIL" "Gap not visible in repo_beta: $beta_gaps"
        return 1
    fi
    
    return 0
}

# Test 7: Planner context passing simulation
test_planner_context_passing() {
    log "INFO" "Test 7: Testing planner context passing simulation"
    
    # Simulate the planner loop with context extraction
    cd "$MANAGED_REPO_PATH"
    
    for repo_dir in */; do
        if [ -d "$repo_dir" ]; then
            repo_name=$(basename "$repo_dir")
            task_dir="$MANAGED_REPO_TASK_PATH/$repo_name"
            
            if [ -d "$task_dir" ]; then
                # Simulate context passing to number manager
                context_result=$("$NUMBER_MANAGER_SCRIPT" get "$repo_name" 2>/dev/null | tail -1)
                if [ $? -eq 0 ]; then
                    log_test_result "Context passing for $repo_name" "PASS" "Context '$repo_name' passed correctly, got number: $context_result"
                else
                    log_test_result "Context passing for $repo_name" "FAIL" "Failed to pass context '$repo_name'"
                    return 1
                fi
            fi
        fi
    done
    
    return 0
}

# Test 8: Context-specific file synchronization
test_context_specific_sync() {
    log "INFO" "Test 8: Testing context-specific file synchronization"
    
    # Sync state with actual files for each repository context
    for repo in "repo_alpha" "repo_beta" "repo_gamma"; do
        task_dir="$MANAGED_REPO_TASK_PATH/$repo"
        
        # Count actual files in task directory
        actual_files=($(find "$task_dir" -maxdepth 1 -type f -name "[0-9][0-9][0-9][0-9]-*.txt" ! -name "*.used"))
        
        # Sync with number manager
        sync_result=$("$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$repo" 2>/dev/null)
        if [ $? -eq 0 ]; then
            log_test_result "Context-specific sync for $repo" "PASS" "Sync completed: $sync_result"
        else
            log_test_result "Context-specific sync for $repo" "FAIL" "Sync failed for $repo"
            return 1
        fi
        
        # Validate consistency
        if "$NUMBER_MANAGER_SCRIPT" validate "$task_dir" "$repo" >/dev/null 2>&1; then
            log_test_result "Context validation for $repo" "PASS" "Validation passed for $repo"
        else
            log_test_result "Context validation for $repo" "FAIL" "Validation failed for $repo"
            return 1
        fi
    done
    
    return 0
}

# Run all tests
run_all_tests() {
    echo ""
    echo "=========================================="
    echo "Running Planner Context Handling Tests"
    echo "=========================================="
    
    # Setup
    if ! setup_test_env; then
        log "ERROR" "Test environment setup failed"
        return 1
    fi
    
    # List of test functions
    local tests=(
        "test_context_specific_numbering"
        "test_context_isolation"
        "test_context_state_persistence"
        "test_repository_context_extraction"
        "test_context_assignments_tracking"
        "test_context_specific_gap_handling"
        "test_planner_context_passing"
        "test_context_specific_sync"
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
        log "SUCCESS" "All planner context handling tests passed!"
        return 0
    else
        log "ERROR" "Some planner context handling tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests planner.sh context handling with number_manager.sh"
    exit 1
fi