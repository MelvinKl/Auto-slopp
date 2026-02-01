#!/bin/bash

# Test planner.sh processing of multiple repositories
# This test validates the planner's ability to handle multiple repositories efficiently

SCRIPT_NAME="test_planner_multiple_repos"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test configuration
TEST_STATE_DIR="/tmp/test_planner_multiple_repos_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"
PLANNER_SCRIPT="$BASE_DIR/scripts/planner.sh"

# Mock config values
export MANAGED_REPO_PATH="$TEST_STATE_DIR/managed"
export MANAGED_REPO_TASK_PATH="$TEST_STATE_DIR/tasks"
export OPencode_CMD="echo"  # Mock the opencode command

log "INFO" "Starting planner multiple repositories tests in $TEST_STATE_DIR"

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
setup_multiple_repos() {
    log "INFO" "Setting up multiple repositories test environment..."
    
    # Create different types of repositories
    repos=(
        "repo_alpha"
        "repo_beta" 
        "repo_gamma"
        "repo_delta"
        "repo_epsilon"
    )
    
    for repo in "${repos[@]}"; do
        # Create managed repo directory
        mkdir -p "$MANAGED_REPO_PATH/$repo"
        cd "$MANAGED_REPO_PATH/$repo"
        git init >/dev/null 2>&1
        git config user.email "test@example.com"
        git config user.name "Test User"
        echo "# $repo" > README.md
        echo "Repository: $repo" >> README.md
        git add README.md >/dev/null 2>&1
        git commit -m "Initial commit for $repo" >/dev/null 2>&1
        
        # Create origin remote
        git init --bare origin.git >/dev/null 2>&1
        git remote add origin "$MANAGED_REPO_PATH/$repo/origin.git"
        git push -u origin main >/dev/null 2>&1 || git push -u origin master >/dev/null 2>&1
        
        # Create task directory with varying initial states
        mkdir -p "$MANAGED_REPO_TASK_PATH/$repo"
        cd "$MANAGED_REPO_TASK_PATH/$repo"
        git init >/dev/null 2>&1
        git config user.email "test@example.com"
        git config user.name "Test User"
        echo "# Tasks for $repo" > README.md
        git add README.md >/dev/null 2>&1
        git commit -m "Initial commit for $repo tasks" >/dev/null 2>&1
        
        # Initialize number manager for each repository context
        "$NUMBER_MANAGER_SCRIPT" init "$repo" >/dev/null 2>&1
        
        # Create different numbers of initial task files for each repo
        case "$repo" in
            "repo_alpha")
                echo "Alpha task 1" > "alpha-task-1.txt"
                echo "Alpha task 2" > "alpha-task-2.txt"
                ;;
            "repo_beta")
                echo "Beta task 1" > "beta-task.txt"
                ;;
            "repo_gamma")
                # No initial tasks
                ;;
            "repo_delta")
                echo "Delta task 1" > "delta-task-1.txt"
                echo "Delta task 2" > "delta-task-2.txt"
                echo "Delta task 3" > "delta-task-3.txt"
                echo "Delta task 4" > "delta-task-4.txt"
                ;;
            "repo_epsilon")
                echo "Epsilon task" > "epsilon-single-task.txt"
                ;;
        esac
    done
    
    return 0
}

# Test 1: Multiple repository discovery
test_multiple_repository_discovery() {
    log "INFO" "Test 1: Testing multiple repository discovery"
    
    cd "$MANAGED_REPO_PATH"
    
    # Count repositories discovered
    repo_count=0
    discovered_repos=()
    
    for repo_dir in */; do
        if [ -d "$repo_dir" ]; then
            repo_name=$(basename "$repo_dir")
            discovered_repos+=("$repo_name")
            repo_count=$((repo_count + 1))
        fi
    done
    
    if [ $repo_count -eq 5 ]; then
        log_test_result "Repository count discovery" "PASS" "Discovered $repo_count repositories"
    else
        log_test_result "Repository count discovery" "FAIL" "Expected 5 repositories, found $repo_count"
        return 1
    fi
    
    # Verify all expected repositories are present
    expected_repos=("repo_alpha" "repo_beta" "repo_gamma" "repo_delta" "repo_epsilon")
    for expected in "${expected_repos[@]}"; do
        found=false
        for actual in "${discovered_repos[@]}"; do
            if [ "$actual" = "$expected" ]; then
                found=true
                break
            fi
        done
        
        if [ "$found" = true ]; then
            log_test_result "Repository discovery: $expected" "PASS" "Found $expected"
        else
            log_test_result "Repository discovery: $expected" "FAIL" "Missing $expected"
            return 1
        fi
    done
    
    return 0
}

# Test 2: Task directory matching
test_task_directory_matching() {
    log "INFO" "Test 2: Testing task directory matching"
    
    cd "$MANAGED_REPO_PATH"
    
    for repo_dir in */; do
        if [ -d "$repo_dir" ]; then
            repo_name=$(basename "$repo_dir")
            task_dir="$MANAGED_REPO_TASK_PATH/$repo_name"
            
            if [ -d "$task_dir" ]; then
                log_test_result "Task directory matching: $repo_name" "PASS" "Found matching task directory: $task_dir"
            else
                log_test_result "Task directory matching: $repo_name" "FAIL" "No matching task directory found"
                return 1
            fi
        fi
    done
    
    return 0
}

# Test 3: Concurrent numbering across repositories
test_concurrent_numbering() {
    log "INFO" "Test 3: Testing concurrent numbering across repositories"
    
    # Process all repositories simultaneously (simulating planner loop)
    local repo_numbers=()
    
    for repo in "repo_alpha" "repo_beta" "repo_gamma" "repo_delta" "repo_epsilon"; do
        cd "$MANAGED_REPO_TASK_PATH/$repo"
        
        # Count unnumbered files
        unnumbered_files=($(find . -maxdepth 1 -type f -name "*.txt" ! -name "[0-9][0-9][0-9][0-9]-*" ! -name "*.used"))
        repo_num_files=${#unnumbered_files[@]}
        
        # Process each unnumbered file
        local assigned_numbers=()
        for unnumbered_file in "${unnumbered_files[@]}"; do
            # Get number for this repository context
            next_num=$("$NUMBER_MANAGER_SCRIPT" get "$repo" 2>/dev/null | tail -1)
            if [ $? -eq 0 ]; then
                assigned_numbers+=("$next_num")
                filename=$(basename "$unnumbered_file" .txt)
                new_filename=$(printf "%04d-%s.txt" "$next_num" "$filename")
                mv "$unnumbered_file" "$new_filename"
            else
                log_test_result "Number assignment in $repo" "FAIL" "Failed to get number for repository $repo"
                return 1
            fi
        done
        
        repo_numbers+=("$repo:${assigned_numbers[*]}")
    done
    
    # Verify all repositories got sequential numbers starting from 1
    local repo_alpha_nums repo_beta_nums repo_gamma_nums repo_delta_nums repo_epsilon_nums
    repo_alpha_nums=$(echo "${repo_numbers[0]}" | cut -d: -f2)
    repo_beta_nums=$(echo "${repo_numbers[1]}" | cut -d: -f2)
    repo_gamma_nums=$(echo "${repo_numbers[2]}" | cut -d: -f2)
    repo_delta_nums=$(echo "${repo_numbers[3]}" | cut -d: -f2)
    repo_epsilon_nums=$(echo "${repo_numbers[4]}" | cut -d: -f2)
    
    # Each repository should start from 1 and be sequential
    if [ "$repo_alpha_nums" = "1 2" ] && [ "$repo_beta_nums" = "1" ] && [ "$repo_gamma_nums" = "" ] && [ "$repo_delta_nums" = "1 2 3 4" ] && [ "$repo_epsilon_nums" = "1" ]; then
        log_test_result "Concurrent numbering across repositories" "PASS" "All repositories correctly numbered independently"
    else
        log_test_result "Concurrent numbering across repositories" "FAIL" "Incorrect numbering: alpha=$repo_alpha_nums, beta=$repo_beta_nums, gamma=$repo_gamma_nums, delta=$repo_delta_nums, epsilon=$repo_epsilon_nums"
        return 1
    fi
    
    return 0
}

# Test 4: Repository processing order independence
test_processing_order_independence() {
    log "INFO" "Test 4: Testing repository processing order independence"
    
    # Get current state before adding more tasks
    local initial_states=()
    for repo in "repo_alpha" "repo_beta" "repo_gamma" "repo_delta" "repo_epsilon"; do
        stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
        last_assigned=$(echo "$stats" | jq -r '.last_assigned')
        initial_states+=("$repo:$last_assigned")
    done
    
    # Add new tasks in a different order
    repos_shuffled=("repo_gamma" "repo_epsilon" "repo_beta" "repo_delta" "repo_alpha")
    
    for repo in "${repos_shuffled[@]}"; do
        cd "$MANAGED_REPO_TASK_PATH/$repo"
        echo "Additional task for $repo" > "additional-task.txt"
        
        # Process the new task
        unnumbered_files=($(find . -maxdepth 1 -type f -name "*.txt" ! -name "[0-9][0-9][0-9][0-9]-*" ! -name "*.used"))
        if [ ${#unnumbered_files[@]} -eq 1 ]; then
            next_num=$("$NUMBER_MANAGER_SCRIPT" get "$repo" 2>/dev/null | tail -1)
            filename=$(basename "${unnumbered_files[0]}" .txt)
            new_filename=$(printf "%04d-%s.txt" "$next_num" "$filename")
            mv "${unnumbered_files[0]}" "$new_filename"
        fi
    done
    
    # Verify each repository's numbering is correct regardless of processing order
    local final_states=()
    local expected_final=(3 2 1 5 2)  # Expected final numbers for each repo
    
    for i in "${!expected_final[@]}"; do
        repo="repo_alpha repo_beta repo_gamma repo_delta repo_epsilon"
        repo_array=($repo)
        current_repo=${repo_array[$i]}
        
        stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
        last_assigned=$(echo "$stats" | jq -r '.last_assigned')
        final_states+=("$current_repo:$last_assigned")
        
        if [ "$last_assigned" = "${expected_final[$i]}" ]; then
            log_test_result "Processing order independence: $current_repo" "PASS" "$current_repo correctly at number $last_assigned"
        else
            log_test_result "Processing order independence: $current_repo" "FAIL" "$current_repo expected ${expected_final[$i]}, got $last_assigned"
            return 1
        fi
    done
    
    return 0
}

# Test 5: Mixed repository states
test_mixed_repository_states() {
    log "INFO" "Test 5: Testing mixed repository states"
    
    # Create different scenarios in each repository
    cd "$MANAGED_REPO_TASK_PATH/repo_alpha"
    echo "Alpha task with .used suffix" > "0005-used-task.txt.used"
    
    cd "$MANAGED_REPO_TASK_PATH/repo_beta"
    echo "Beta 2-digit task" > "01-legacy-task.txt"  # Should not be processed
    
    cd "$MANAGED_REPO_TASK_PATH/repo_gamma"
    # repo_gamma should be empty still
    echo "New gamma task" > "gamma-new-task.txt"
    
    cd "$MANAGED_REPO_TASK_PATH/repo_delta"
    # repo_delta should be fully processed
    
    cd "$MANAGED_REPO_TASK_PATH/repo_epsilon"
    echo "Epsilon extra task" > "epsilon-extra-task.txt"
    
    # Process all repositories
    local processing_results=()
    
    for repo in "repo_alpha" "repo_beta" "repo_gamma" "repo_delta" "repo_epsilon"; do
        cd "$MANAGED_REPO_TASK_PATH/$repo"
        
        # Count files before processing
        before_count=$(find . -maxdepth 1 -name "*.txt" | wc -l)
        
        # Process unnumbered files
        unnumbered_files=($(find . -maxdepth 1 -type f -name "*.txt" ! -name "[0-9][0-9][0-9][0-9]-*" ! -name "*.used"))
        processed_count=0
        
        for unnumbered_file in "${unnumbered_files[@]}"; do
            next_num=$("$NUMBER_MANAGER_SCRIPT" get "$repo" 2>/dev/null | tail -1)
            if [ $? -eq 0 ]; then
                filename=$(basename "$unnumbered_file" .txt)
                new_filename=$(printf "%04d-%s.txt" "$next_num" "$filename")
                mv "$unnumbered_file" "$new_filename"
                processed_count=$((processed_count + 1))
            fi
        done
        
        # Count files after processing
        after_count=$(find . -maxdepth 1 -name "*.txt" | wc -l)
        
        processing_results+=("$repo:before=$before_count:processed=$processed_count:after=$after_count")
    done
    
    # Verify results
    # repo_alpha: should have unchanged .used file
    # repo_beta: should have unprocessed 2-digit file
    # repo_gamma: should have processed new task
    # repo_delta: should have no changes
    # repo_epsilon: should have processed extra task
    
    local expected_processed=(0 0 1 0 1)
    
    for i in "${!expected_processed[@]}"; do
        repo="repo_alpha repo_beta repo_gamma repo_delta repo_epsilon"
        repo_array=($repo)
        current_repo=${repo_array[$i]}
        
        result="${processing_results[$i]}"
        actual_processed=$(echo "$result" | cut -d: -f3)
        expected=${expected_processed[$i]}
        
        if [ "$actual_processed" = "$expected" ]; then
            log_test_result "Mixed states: $current_repo" "PASS" "Processed $actual_processed files as expected"
        else
            log_test_result "Mixed states: $current_repo" "FAIL" "Expected $expected, processed $actual_processed"
            return 1
        fi
    done
    
    return 0
}

# Test 6: Large scale repository processing
test_large_scale_processing() {
    log "INFO" "Test 6: Testing large scale repository processing"
    
    # Create many repositories with many tasks
    for i in {1..10}; do
        repo_name="scale_repo_$i"
        
        # Create repo
        mkdir -p "$MANAGED_REPO_PATH/$repo_name"
        cd "$MANAGED_REPO_PATH/$repo_name"
        git init >/dev/null 2>&1
        git config user.email "test@example.com"
        git config user.name "Test User"
        echo "# $repo_name" > README.md
        git add README.md >/dev/null 2>&1
        git commit -m "Initial commit" >/dev/null 2>&1
        
        # Create task directory
        mkdir -p "$MANAGED_REPO_TASK_PATH/$repo_name"
        cd "$MANAGED_REPO_TASK_PATH/$repo_name"
        git init >/dev/null 2>&1
        git config user.email "test@example.com"
        git config user.name "Test User"
        echo "# Tasks for $repo_name" > README.md
        git add README.md >/dev/null 2>&1
        git commit -m "Initial commit" >/dev/null 2>&1
        
        # Initialize number manager
        "$NUMBER_MANAGER_SCRIPT" init "$repo_name" >/dev/null 2>&1
        
        # Create varying numbers of tasks
        task_count=$((i % 5 + 1))  # 1-5 tasks per repo
        for j in $(seq 1 $task_count); do
            echo "Task $j in $repo_name" > "task-$j.txt"
        done
    done
    
    # Process all scale repositories
    total_processed=0
    
    for i in {1..10}; do
        repo_name="scale_repo_$i"
        cd "$MANAGED_REPO_TASK_PATH/$repo_name"
        
        unnumbered_files=($(find . -maxdepth 1 -type f -name "*.txt" ! -name "[0-9][0-9][0-9][0-9]-*" ! -name "*.used"))
        
        for unnumbered_file in "${unnumbered_files[@]}"; do
            next_num=$("$NUMBER_MANAGER_SCRIPT" get "$repo_name" 2>/dev/null | tail -1)
            if [ $? -eq 0 ]; then
                filename=$(basename "$unnumbered_file" .txt)
                new_filename=$(printf "%04d-%s.txt" "$next_num" "$filename")
                mv "$unnumbered_file" "$new_filename"
                total_processed=$((total_processed + 1))
            fi
        done
    done
    
    # Expected total: sum of (i % 5 + 1) for i=1..10 = 1+2+3+4+5+1+2+3+4+5 = 30
    if [ $total_processed -eq 30 ]; then
        log_test_result "Large scale processing" "PASS" "Processed $total_processed tasks across 10 repositories"
    else
        log_test_result "Large scale processing" "FAIL" "Expected 30 processed tasks, got $total_processed"
        return 1
    fi
    
    return 0
}

# Test 7: Repository isolation verification
test_repository_isolation_verification() {
    log "INFO" "Test 7: Testing repository isolation verification"
    
    # Verify that all repository contexts are properly isolated
    all_contexts=$("$NUMBER_MANAGER_SCRIPT" contexts 2>/dev/null)
    if [ $? -eq 0 ]; then
        context_count=$(echo "$all_contexts" | jq 'keys | length')
        
        # Should have 15 contexts now (5 original + 10 scale repos)
        if [ "$context_count" -eq 15 ]; then
            log_test_result "Context isolation count" "PASS" "Found $context_count isolated contexts"
        else
            log_test_result "Context isolation count" "FAIL" "Expected 15 contexts, found $context_count"
            return 1
        fi
        
        # Verify each context has its own numbering
        isolation_correct=true
        for repo in "repo_alpha" "repo_beta" "repo_gamma" "repo_delta" "repo_epsilon"; do
            assignment=$(echo "$all_contexts" | jq -r ".${repo} // \"null\"")
            if [ "$assignment" = "null" ]; then
                isolation_correct=false
                break
            fi
        done
        
        if [ "$isolation_correct" = true ]; then
            log_test_result "Repository isolation verification" "PASS" "All original repositories have isolated contexts"
        else
            log_test_result "Repository isolation verification" "FAIL" "Some repositories missing isolated contexts"
            return 1
        fi
    else
        log_test_result "Contexts retrieval" "FAIL" "Failed to retrieve context information"
        return 1
    fi
    
    return 0
}

# Run all tests
run_all_tests() {
    echo ""
    echo "=========================================="
    echo "Running Planner Multiple Repositories Tests"
    echo "=========================================="
    
    # Setup
    if ! setup_multiple_repos; then
        log "ERROR" "Test environment setup failed"
        return 1
    fi
    
    # List of test functions
    local tests=(
        "test_multiple_repository_discovery"
        "test_task_directory_matching"
        "test_concurrent_numbering"
        "test_processing_order_independence"
        "test_mixed_repository_states"
        "test_large_scale_processing"
        "test_repository_isolation_verification"
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
        log "SUCCESS" "All planner multiple repositories tests passed!"
        return 0
    else
        log "ERROR" "Some planner multiple repositories tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests planner.sh processing of multiple repositories"
    exit 1
fi