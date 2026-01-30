#!/bin/bash

# Comprehensive test suite for merge-before-push functionality
# Tests merge operations, conflict detection, and opencode escalation workflow

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TESTS_DIR="$SCRIPT_DIR"

# Source utility functions for testing
source "$PROJECT_DIR/scripts/utils.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test directory setup
TEST_REPO_BASE="/tmp/merge_test_repos_$$"
CURRENT_TEST_REPO=""

# Helper functions
log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    log_test "Running: $test_name"
    
    if eval "$test_command"; then
        log_success "$test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "$test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Create test repository - simplified approach
create_test_repo() {
    local repo_name="$1"
    local repo_path="$TEST_REPO_BASE/$repo_name"
    
    mkdir -p "$repo_path"
    cd "$repo_path"
    
    # Initialize git repository
    git init -b main >/dev/null 2>&1
    git config user.name "Test User"
    git config user.email "test@example.com"
    
    # Create initial commit
    echo "# Test Repository: $repo_name" > README.md
    git add README.md >/dev/null 2>&1
    git commit -m "Initial commit" >/dev/null 2>&1
    
    # Create ai branch with different content
    git checkout -b ai >/dev/null 2>&1
    echo "# AI Branch specific content" >> README.md
    git add README.md >/dev/null 2>&1
    git commit -m "Create ai branch" >/dev/null 2>&1
    
    # Go back to main for remote setup
    git checkout main >/dev/null 2>&1
    
    echo "$repo_path"
}

# Set up remote repository - simplified
setup_remote() {
    local repo_path="$1"
    
    cd "$repo_path"
    
    # Create a bare remote in the same location
    mkdir -p "${repo_path}_remote"
    cp -r .git "${repo_path}_remote/"
    cd "${repo_path}_remote"
    git config --bool core.bare true >/dev/null 2>&1
    
    # Set up origin in original repo
    cd "$repo_path"
    git remote add origin "${repo_path}_remote" >/dev/null 2>&1
    git push -u origin main >/dev/null 2>&1
    git push -u origin ai >/dev/null 2>&1
    
    echo "${repo_path}_remote"
}

# Cleanup test repositories
cleanup_test_repositories() {
    if [[ -d "$TEST_REPO_BASE" ]]; then
        rm -rf "$TEST_REPO_BASE"
    fi
}

# Test successful merge scenarios
test_successful_merge_no_conflicts() {
    CURRENT_TEST_REPO=$(create_test_repo "no_conflicts")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Create a change in main that won't conflict
    git checkout main >/dev/null 2>&1
    echo "Main branch change" > main_only.txt
    git add main_only.txt >/dev/null 2>&1
    git commit -m "Add main-only file" >/dev/null 2>&1
    git push origin main >/dev/null 2>&1
    
    # Test merge function
    git checkout ai >/dev/null 2>&1
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    # This should succeed without conflicts
    merge_origin_main_to_ai >/dev/null 2>&1
    local result=$?
    
    return $result
}

test_no_changes_to_merge() {
    CURRENT_TEST_REPO=$(create_test_repo "no_changes")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Don't make any changes to main
    
    # Test merge function
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    merge_origin_main_to_ai >/dev/null 2>&1
    local result=$?
    
    return $result
}

# Test conflict scenarios
test_file_level_conflicts() {
    CURRENT_TEST_REPO=$(create_test_repo "file_conflicts")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Modify same file in both branches with different content
    echo "AI branch content" > shared.txt
    git add shared.txt >/dev/null 2>&1
    git commit -m "Modify shared file in ai branch" >/dev/null 2>&1
    
    git checkout main >/dev/null 2>&1
    echo "Main branch content" > shared.txt
    git add shared.txt >/dev/null 2>&1
    git commit -m "Modify shared file in main branch" >/dev/null 2>&1
    git push origin main >/dev/null 2>&1
    
    # Test merge function should fail with conflicts
    git checkout ai >/dev/null 2>&1
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    # Capture exit code
    merge_origin_main_to_ai >/dev/null 2>&1
    local result=$?
    
    # Should fail with conflicts (exit code 1)
    return $([ $result -ne 0 ] && echo 0 || echo 1)
}

# Test conflict detection and reporting
test_conflict_detection() {
    CURRENT_TEST_REPO=$(create_test_repo "conflict_detection")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Create conflict
    echo "AI content" > conflict_file.txt
    git add conflict_file.txt >/dev/null 2>&1
    git commit -m "Modify file in ai" >/dev/null 2>&1
    
    git checkout main >/dev/null 2>&1
    echo "Main content" > conflict_file.txt
    git add conflict_file.txt >/dev/null 2>&1
    git commit -m "Modify same file in main" >/dev/null 2>&1
    git push origin main >/dev/null 2>&1
    
    # Test conflict detection
    git checkout ai >/dev/null 2>&1
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    # First, try merge to create conflict state
    git merge origin/main --no-edit >/dev/null 2>&1 || true
    
    # Test conflict detection function
    detect_merge_conflicts >/dev/null 2>&1
    local result=$?
    
    # Check if conflict report was created
    local conflict_file="/tmp/opencode_conflict_report.json"
    if [[ $result -gt 0 && -f "$conflict_file" ]]; then
        # Basic JSON validation - check if it starts and ends properly
        if head -1 "$conflict_file" | grep -q '^{' && tail -1 "$conflict_file" | grep -q '^}'; then
            return 0
        fi
    fi
    
    return 1
}

# Test edge cases
test_branch_validation() {
    CURRENT_TEST_REPO=$(create_test_repo "branch_validation")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    # Stay on main branch (not ai) - this should fail
    git checkout main >/dev/null 2>&1
    
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    # Should fail because we're not on ai branch
    merge_origin_main_to_ai >/dev/null 2>&1
    local result=$?
    
    return $([ $result -ne 0 ] && echo 0 || echo 1)
}

test_merge_function_existence() {
    # Test that all required merge functions exist and are callable
    local functions=("merge_origin_main_to_ai" "detect_merge_conflicts" "merge_origin_main_to_ai_with_escalation")
    
    for func in "${functions[@]}"; do
        if ! declare -f "$func" >/dev/null; then
            return 1
        fi
    done
    
    return 0
}

test_logging_integration() {
    # Test that merge functions use the logging system
    CURRENT_TEST_REPO=$(create_test_repo "logging")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    # Test that function completes without errors and logs output
    local output
    output=$(merge_origin_main_to_ai 2>&1)
    local result=$?
    
    # Check if output contains expected logging patterns
    if [[ $result -eq 0 ]] && echo "$output" | grep -q "Starting merge\|ai branch is already up to date\|Successfully merged"; then
        return 0
    else
        return 1
    fi
}

# Main test execution
main() {
    echo "=== Merge-Before-Push Functionality Test Suite ==="
    echo "Test repository base: $TEST_REPO_BASE"
    echo ""
    
    # Create test directory
    mkdir -p "$TEST_REPO_BASE"
    
    # Set up cleanup on exit
    trap cleanup_test_repositories EXIT
    
    # Test function existence first
    log_info "Testing function existence..."
    run_test "Merge functions exist" "test_merge_function_existence"
    
    # Test logging integration
    log_info "Testing logging integration..."
    run_test "Logging integration test" "test_logging_integration"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    # Test successful merge scenarios
    log_info "Testing successful merge scenarios..."
    run_test "Successful merge with no conflicts" "test_successful_merge_no_conflicts"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    run_test "No changes to merge" "test_no_changes_to_merge"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    # Test conflict scenarios
    log_info "Testing conflict scenarios..."
    run_test "File-level conflicts detection" "test_file_level_conflicts"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    run_test "Conflict detection and reporting" "test_conflict_detection"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    # Test validation scenarios
    log_info "Testing validation scenarios..."
    run_test "Branch validation" "test_branch_validation"
    cleanup_test_repositories
    
    # Print results
    echo ""
    echo "=== Test Results ==="
    echo "Total tests: $TESTS_TOTAL"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ All merge-before-push tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}✗ Some merge-before-push tests failed!${NC}"
        exit 1
    fi
}

# Run main function
main "$@"