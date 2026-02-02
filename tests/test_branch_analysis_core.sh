#!/bin/bash

# Test Suite for Branch Analysis Core Logic
# Tests all core functions with various scenarios and edge cases

SCRIPT_NAME="test-branch-analysis-core"

# Load utilities and core module
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$PROJECT_DIR/scripts/utils.sh"
source "$PROJECT_DIR/scripts/branch-analysis-core.sh"

# Test configuration
TEST_REPO_DIR="/tmp/test_repo_$$"
REMOTE_TEST_REPO_DIR="/tmp/remote_test_repo_$$"
TEST_RESULTS_FILE="/tmp/branch_analysis_test_results_$$"

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# =============================================================================
# TEST FRAMEWORK FUNCTIONS
# =============================================================================

# Initialize test framework
init_test_framework() {
    log "INFO" "Initializing branch analysis core test framework"
    
    # Create test results file
    cat > "$TEST_RESULTS_FILE" << EOF
{
    "test_suite": "branch-analysis-core",
    "timestamp": "$(date -Iseconds)",
    "tests": [],
    "summary": {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "success_rate": 0
    }
}
EOF
    
    # Setup error handling for tests
    setup_error_handling
    
    # Create test repositories
    setup_test_repositories
}

# Setup test repositories with various branch scenarios
setup_test_repositories() {
    log "INFO" "Setting up test repositories"
    
    # Create remote repository
    mkdir -p "$REMOTE_TEST_REPO_DIR"
    cd "$REMOTE_TEST_REPO_DIR"
    git init --bare >/dev/null 2>&1
    
    # Create local repository and connect to remote
    mkdir -p "$TEST_REPO_DIR"
    cd "$TEST_REPO_DIR"
    git init >/dev/null 2>&1
    git remote add origin "$REMOTE_TEST_REPO_DIR"
    
    # Create initial commit and main branch
    echo "# Test Repository" > README.md
    git add README.md
    git commit -m "Initial commit" >/dev/null 2>&1
    git branch -M main
    git push -u origin main >/dev/null 2>&1
    
    # Create additional branches on remote
    git checkout -b develop >/dev/null 2>&1
    echo "develop content" > develop.txt
    git add develop.txt
    git commit -m "Add develop branch" >/dev/null 2>&1
    git push origin develop >/dev/null 2>&1
    
    git checkout main >/dev/null 2>&1
    git checkout -b feature/test >/dev/null 2>&1
    echo "feature content" > feature.txt
    git add feature.txt
    git commit -m "Add feature branch" >/dev/null 2>&1
    git push origin feature/test >/dev/null 2>&1
    
    # Create local-only branches
    git checkout main >/dev/null 2>&1
    git checkout -b local-only-1 >/dev/null 2>&1
    echo "local only content" > local1.txt
    git add local1.txt
    git commit -m "Local only branch 1" >/dev/null 2>&1
    
    git checkout main >/dev/null 2>&1
    git checkout -b local-only-2 >/dev/null 2>&1
    echo "local only content" > local2.txt
    git add local2.txt
    git commit -m "Local only branch 2" >/dev/null 2>&1
    
    # Return to main for clean state
    git checkout main >/dev/null 2>&1
    
    log "INFO" "Test repositories setup completed"
}

# Record test result
record_test() {
    local test_name="$1"
    local expected="$2"
    local actual="$3"
    local status="$4"
    local details="$5"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if [[ "$status" == "PASS" ]]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    
    # Add to results JSON
    local test_entry=$(cat << EOF
{
    "name": "$test_name",
    "expected": "$expected",
    "actual": "$actual",
    "status": "$status",
    "details": "$details",
    "timestamp": "$(date -Iseconds)"
}
EOF
)
    
    # Update results file
    jq --argjson test "$test_entry" '.tests += [$test]' "$TEST_RESULTS_FILE" > "${TEST_RESULTS_FILE}.tmp" && mv "${TEST_RESULTS_FILE}.tmp" "$TEST_RESULTS_FILE"
    
    # Log result
    local color=""
    case "$status" in
        "PASS") color="$GREEN" ;;
        "FAIL") color="$RED" ;;
        "SKIP") color="$YELLOW" ;;
    esac
    
    echo -e "${color}[${status}]${NC} $test_name"
    [[ -n "$details" ]] && echo "    $details"
}

# Clean up test environment
cleanup_test_environment() {
    log "INFO" "Cleaning up test environment"
    
    rm -rf "$TEST_REPO_DIR" "$REMOTE_TEST_REPO_DIR" "$TEST_RESULTS_FILE"
    
    # Update final summary
    local success_rate=0
    if [[ $TESTS_TOTAL -gt 0 ]]; then
        success_rate=$(( (TESTS_PASSED * 100) / TESTS_TOTAL ))
    fi
    
    echo -e "\n${BLUE}=== TEST SUMMARY ===${NC}"
    echo "Total Tests: $TESTS_TOTAL"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    echo "Success Rate: ${success_rate}%"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "\n${GREEN}All tests passed!${NC}"
        return 0
    else
        echo -e "\n${RED}Some tests failed.${NC}"
        return 1
    fi
}

# =============================================================================
# CORE FUNCTION TESTS
# =============================================================================

# Test repository validation
test_repository_validation() {
    log "INFO" "Testing repository validation"
    
    # Test with valid repository
    if validate_repository_directory "$TEST_REPO_DIR"; then
        record_test "Valid repository directory" "success" "success" "PASS" "Valid repository directory passed validation"
    else
        record_test "Valid repository directory" "success" "failure" "FAIL" "Valid repository directory failed validation"
    fi
    
    # Test with invalid directory
    if ! validate_repository_directory "/nonexistent/directory"; then
        record_test "Invalid repository directory" "failure" "failure" "PASS" "Invalid directory properly rejected"
    else
        record_test "Invalid repository directory" "failure" "success" "FAIL" "Invalid directory was incorrectly accepted"
    fi
}

# Test git repository validation
test_git_repository_validation() {
    log "INFO" "Testing git repository validation"
    
    cd "$TEST_REPO_DIR"
    
    # Test with valid git repository
    if validate_git_repository; then
        record_test "Valid git repository" "success" "success" "PASS" "Valid git repository passed validation"
    else
        record_test "Valid git repository" "success" "failure" "FAIL" "Valid git repository failed validation"
    fi
    
    # Test with non-git directory
    cd /tmp
    if ! validate_git_repository; then
        record_test "Non-git directory" "failure" "failure" "PASS" "Non-git directory properly rejected"
    else
        record_test "Non-git directory" "failure" "success" "FAIL" "Non-git directory was incorrectly accepted"
    fi
}

# Test remote branch listing
test_remote_branch_listing() {
    log "INFO" "Testing remote branch listing"
    
    local remote_branches
    if remote_branches=$(list_remote_branches "$TEST_REPO_DIR"); then
        local branch_count=$(echo "$remote_branches" | wc -l)
        
        # Should find main, develop, feature/test (3 branches)
        if [[ $branch_count -ge 3 ]]; then
            record_test "Remote branch listing" ">=3 branches" "$branch_count branches" "PASS" "Found expected number of remote branches"
        else
            record_test "Remote branch listing" ">=3 branches" "$branch_count branches" "FAIL" "Found fewer remote branches than expected"
        fi
        
        # Check for specific expected branches
        if echo "$remote_branches" | grep -q "^main$"; then
            record_test "Main branch in remote list" "found" "found" "PASS" "Main branch found in remote list"
        else
            record_test "Main branch in remote list" "found" "not found" "FAIL" "Main branch missing from remote list"
        fi
        
        if echo "$remote_branches" | grep -q "^develop$"; then
            record_test "Develop branch in remote list" "found" "found" "PASS" "Develop branch found in remote list"
        else
            record_test "Develop branch in remote list" "found" "not found" "FAIL" "Develop branch missing from remote list"
        fi
    else
        record_test "Remote branch listing" "success" "failure" "FAIL" "Failed to list remote branches"
    fi
}

# Test local branch listing
test_local_branch_listing() {
    log "INFO" "Testing local branch listing"
    
    local local_branches
    if local_branches=$(list_local_branches "$TEST_REPO_DIR"); then
        local branch_count=$(echo "$local_branches" | wc -l)
        
        # Should find develop, feature/test, local-only-1, local-only-2 (4 branches, excluding main which is current)
        if [[ $branch_count -ge 4 ]]; then
            record_test "Local branch listing" ">=4 branches" "$branch_count branches" "PASS" "Found expected number of local branches"
        else
            record_test "Local branch listing" ">=4 branches" "$branch_count branches" "FAIL" "Found fewer local branches than expected"
        fi
        
        # Check for local-only branches
        if echo "$local_branches" | grep -q "local-only-1"; then
            record_test "Local-only branch in list" "found" "found" "PASS" "Local-only branch found in list"
        else
            record_test "Local-only branch in list" "found" "not found" "FAIL" "Local-only branch missing from list"
        fi
        
        # Check that current branch (main) is NOT in the list
        if ! echo "$local_branches" | grep -q "^main$"; then
            record_test "Current branch excluded" "excluded" "excluded" "PASS" "Current branch properly excluded from list"
        else
            record_test "Current branch excluded" "excluded" "included" "FAIL" "Current branch incorrectly included in list"
        fi
    else
        record_test "Local branch listing" "success" "failure" "FAIL" "Failed to list local branches"
    fi
}

# Test branch comparison (simplified approach)
test_branch_comparison() {
    log "INFO" "Testing branch comparison"
    
    # Test by comparing the core functions directly
    local remote_branches local_branches
    
    if remote_branches=$(list_remote_branches "$TEST_REPO_DIR") && local_branches=$(list_local_branches "$TEST_REPO_DIR"); then
        # Debug output
        log "DEBUG" "Remote branches: $(echo "$remote_branches" | tr '\n' ' ')"
        log "DEBUG" "Local branches: $(echo "$local_branches" | tr '\n' ' ')"
        
        # Manually check for local-only branches
        local local_only_count=0
        local common_count=0
        
        while IFS= read -r local_branch; do
            if [[ -n "$local_branch" ]]; then
                if echo "$remote_branches" | grep -q "^$local_branch$"; then
                    log "DEBUG" "Found common branch: $local_branch"
                    common_count=$((common_count + 1))
                else
                    log "DEBUG" "Found local-only branch: $local_branch"
                    local_only_count=$((local_only_count + 1))
                fi
            fi
        done <<< "$local_branches"
        
        log "DEBUG" "Final counts - Local-only: $local_only_count, Common: $common_count"
        
        # Should find local-only branches (local-only-1, local-only-2)
        if [[ $local_only_count -ge 2 ]]; then
            record_test "Local-only branches detected" ">=2" "$local_only_count" "PASS" "Found expected local-only branches"
        else
            record_test "Local-only branches detected" ">=2" "$local_only_count" "FAIL" "Found fewer local-only branches than expected"
        fi
        
        # Should find common branches (develop, main)
        # Note: list_local_branches excludes current branch (main)
        if [[ $common_count -ge 1 ]]; then
            record_test "Common branches detected" ">=1" "$common_count" "PASS" "Found expected common branches"
        else
            record_test "Common branches detected" ">=1" "$common_count" "FAIL" "Found fewer common branches than expected"
        fi
        
        # Test that compare_branches function runs without error
        local comparison_result
        if comparison_result=$(compare_branches "$TEST_REPO_DIR" >/dev/null 2>&1); then
            record_test "Comparison function execution" "success" "success" "PASS" "compare_branches function executed successfully"
        else
            record_test "Comparison function execution" "success" "failure" "FAIL" "compare_branches function failed"
        fi
    else
        record_test "Branch comparison" "success" "failure" "FAIL" "Failed to get branch lists for comparison"
    fi
}

# Test edge case handling
test_edge_cases() {
    log "INFO" "Testing edge case handling"
    
    # Test disconnected remote
    cd "$TEST_REPO_DIR"
    git remote set-url origin "http://nonexistent.remote.example.com/repo.git"
    
    local remote_result
    if remote_result=$(list_remote_branches "$TEST_REPO_DIR"); then
        local exit_code=$?
        if [[ $exit_code -eq 1 ]]; then  # Network error expected
            record_test "Unreachable remote handling" "network error" "network error" "PASS" "Properly handled unreachable remote"
        else
            record_test "Unreachable remote handling" "network error" "other result" "FAIL" "Unexpected result for unreachable remote"
        fi
    else
        local exit_code=$?
        if [[ $exit_code -eq 1 ]]; then
            record_test "Unreachable remote handling" "network error" "network error" "PASS" "Properly handled unreachable remote"
        else
            record_test "Unreachable remote handling" "network error" "exit code $exit_code" "FAIL" "Unexpected exit code for unreachable remote"
        fi
    fi
    
    # Restore remote
    git remote set-url origin "$REMOTE_TEST_REPO_DIR"
    
    # Test detached HEAD state (create a commit first to ensure HEAD~1 exists)
    cd "$TEST_REPO_DIR"
    echo "test change" > test_file.txt
    git add test_file.txt
    git commit -m "Test commit for detached HEAD" >/dev/null 2>&1
    
    if git checkout HEAD~1 --detach >/dev/null 2>&1; then
        local current_branch
        if current_branch=$(get_current_branch_safe); then
            if [[ "$current_branch" == "HEAD" ]]; then
                record_test "Detached HEAD detection" "HEAD" "$current_branch" "PASS" "Properly detected detached HEAD state"
            else
                record_test "Detached HEAD detection" "HEAD" "$current_branch" "FAIL" "Failed to detect detached HEAD state"
            fi
        else
            record_test "Detached HEAD detection" "success" "failure" "FAIL" "Failed to get current branch in detached HEAD"
        fi
    else
        record_test "Detached HEAD creation" "success" "failure" "FAIL" "Failed to create detached HEAD state"
    fi
    
    # Return to main
    git checkout main >/dev/null 2>&1
}

# Test performance and efficiency
test_performance() {
    log "INFO" "Testing performance and efficiency"
    
    local start_time=$(date +%s.%N)
    
    # Run all core functions
    list_remote_branches "$TEST_REPO_DIR" >/dev/null
    list_local_branches "$TEST_REPO_DIR" >/dev/null
    compare_branches "$TEST_REPO_DIR" >/dev/null
    
    local end_time=$(date +%s.%N)
    local duration
    if command -v bc >/dev/null 2>&1; then
        duration=$(echo "$end_time - $start_time" | bc -l)
    else
        duration="0"  # Fallback
    fi
    
    # Should complete within reasonable time (5 seconds)
    local duration_int=${duration%.*}
    if [[ $duration_int -le 5 ]]; then
        record_test "Performance test" "<=5s" "${duration}s" "PASS" "Operations completed within time limit"
    else
        record_test "Performance test" "<=5s" "${duration}s" "FAIL" "Operations exceeded time limit"
    fi
}

# =============================================================================
# MAIN TEST EXECUTION
# =============================================================================

# Run all tests
run_all_tests() {
    log "INFO" "Starting branch analysis core test suite"
    
    init_test_framework
    
    echo -e "${BLUE}=== BRANCH ANALYSIS CORE TEST SUITE ===${NC}\n"
    
    # Run individual test suites
    test_repository_validation
    test_git_repository_validation
    test_remote_branch_listing
    test_local_branch_listing
    test_branch_comparison
    test_edge_cases
    test_performance
    
    # Clean up and show summary
    cleanup_test_environment
}

# Execute tests if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_all_tests
fi