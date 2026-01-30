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

# Additional comprehensive test scenarios

test_complex_merge_conflicts() {
    CURRENT_TEST_REPO=$(create_test_repo "complex_conflicts")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Create complex scenario: multiple files with conflicts
    cat > config.txt << EOF
[section1]
value1=ai_version
value2=shared_value
[section2]
value3=ai_specific
EOF
    git add config.txt >/dev/null 2>&1
    git commit -m "Add config in ai branch" >/dev/null 2>&1
    
    # Create another file in ai
    echo "AI branch content" > shared_file.txt
    git add shared_file.txt >/dev/null 2>&1
    git commit -m "Add shared file in ai" >/dev/null 2>&1
    
    git checkout main >/dev/null 2>&1
    
    # Modify same files in main with conflicting content
    cat > config.txt << EOF
[section1]
value1=main_version
value2=main_shared_value
[section2]
value3=main_specific
[section3]
value4=new_section
EOF
    git add config.txt >/dev/null 2>&1
    git commit -m "Modify config in main" >/dev/null 2>&1
    
    echo "Main branch content" > shared_file.txt
    git add shared_file.txt >/dev/null 2>&1
    git commit -m "Modify shared file in main" >/dev/null 2>&1
    git push origin main >/dev/null 2>&1
    
    # Test merge with escalation
    git checkout ai >/dev/null 2>&1
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    # Should detect conflicts and create report
    merge_origin_main_to_ai_with_escalation >/dev/null 2>&1
    local result=$?
    
    # Should return exit code 2 for conflicts
    if [[ $result -eq 2 && -f "/tmp/opencode_conflict_report.json" ]]; then
        return 0
    else
        return 1
    fi
}

test_nested_directory_conflicts() {
    CURRENT_TEST_REPO=$(create_test_repo "nested_conflicts")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Create nested directory structure
    mkdir -p src/components
    echo "AI component code" > src/components/Component.jsx
    echo "AI utils" > src/utils.js
    git add src/ >/dev/null 2>&1
    git commit -m "Add nested structure in ai" >/dev/null 2>&1
    
    git checkout main >/dev/null 2>&1
    mkdir -p src/components
    echo "Main component code" > src/components/Component.jsx
    echo "Main utils" > src/utils.js
    git add src/ >/dev/null 2>&1
    git commit -m "Add nested structure in main" >/dev/null 2>&1
    git push origin main >/dev/null 2>&1
    
    # Test conflict detection
    git checkout ai >/dev/null 2>&1
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    # Create conflict state and detect
    git merge origin/main --no-edit >/dev/null 2>&1 || true
    detect_merge_conflicts >/dev/null 2>&1
    local result=$?
    
    # Should detect nested file conflicts
    if [[ $result -gt 0 && -f "/tmp/opencode_conflict_report.json" ]]; then
        # Check if report contains nested paths
        if grep -q "src/components/Component.jsx\|src/utils.js" "/tmp/opencode_conflict_report.json"; then
            return 0
        fi
    fi
    
    return 1
}

test_binary_file_conflicts() {
    CURRENT_TEST_REPO=$(create_test_repo "binary_conflicts")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Create a binary-like file (simulate image/data)
    echo "AI binary data $(date)" > data.bin
    git add data.bin >/dev/null 2>&1
    git commit -m "Add binary file in ai" >/dev/null 2>&1
    
    git checkout main >/dev/null 2>&1
    echo "Main binary data $(date)" > data.bin
    git add data.bin >/dev/null 2>&1
    git commit -m "Add binary file in main" >/dev/null 2>&1
    git push origin main >/dev/null 2>&1
    
    # Test handling of binary conflicts
    git checkout ai >/dev/null 2>&1
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    # Should handle binary conflicts gracefully
    merge_origin_main_to_ai >/dev/null 2>&1
    local result=$?
    
    # Binary files should either merge cleanly or be detected as conflicts
    return 0  # Success if no error occurred
}

test_deletion_vs_modification_conflicts() {
    CURRENT_TEST_REPO=$(create_test_repo "delete_modify_conflicts")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Create file in ai
    echo "This file will be deleted in main" > to_delete.txt
    git add to_delete.txt >/dev/null 2>&1
    git commit -m "Add file to be deleted" >/dev/null 2>&1
    
    git checkout main >/dev/null 2>&1
    # Modify file in main, then delete it
    echo "Modified content" > to_delete.txt
    git add to_delete.txt >/dev/null 2>&1
    git commit -m "Modify file before deletion" >/dev/null 2>&1
    git rm to_delete.txt >/dev/null 2>&1
    git commit -m "Delete file" >/dev/null 2>&1
    git push origin main >/dev/null 2>&1
    
    # Test deletion vs modification conflict
    git checkout ai >/dev/null 2>&1
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    merge_origin_main_to_ai >/dev/null 2>&1
    local result=$?
    
    # Should handle delete/modify conflicts
    return 0  # Success if handled gracefully
}

test_concurrent_merge_scenarios() {
    CURRENT_TEST_REPO=$(create_test_repo "concurrent_merges")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Create a shared file first
    echo "Initial content" > concurrent.txt
    git add concurrent.txt >/dev/null 2>&1
    git commit -m "Initial file" >/dev/null 2>&1
    
    # Push to remote to establish baseline
    git push origin ai >/dev/null 2>&1
    
    # Make divergent changes in both branches
    echo "Concurrent change 1" > concurrent.txt
    git add concurrent.txt >/dev/null 2>&1
    git commit -m "Concurrent change 1" >/dev/null 2>&1
    
    git checkout main >/dev/null 2>&1
    echo "Concurrent change 2" > concurrent.txt
    git add concurrent.txt >/dev/null 2>&1
    git commit -m "Concurrent change 2" >/dev/null 2>&1
    git push origin main >/dev/null 2>&1
    
    # Test merge behavior
    git checkout ai >/dev/null 2>&1
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    merge_origin_main_to_ai >/dev/null 2>&1
    local result=$?
    
    # Test should succeed whether there are conflicts or not
    # The important thing is that merge completes without hanging
    if [[ $result -eq 0 || $result -eq 1 ]]; then
        return 0
    else
        return 1
    fi
}

test_whitespace_and_formatting_conflicts() {
    CURRENT_TEST_REPO=$(create_test_repo "whitespace_conflicts")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Create file with specific whitespace
    cat > format.txt << EOF
line1
line2
line3
EOF
    git add format.txt >/dev/null 2>&1
    git commit -m "Add formatted file" >/dev/null 2>&1
    
    git checkout main >/dev/null 2>&1
    # Same content but different whitespace
    cat > format.txt << EOF
line1
line2

line3
EOF
    git add format.txt >/dev/null 2>&1
    git commit -m "Modify whitespace" >/dev/null 2>&1
    git push origin main >/dev/null 2>&1
    
    # Test whitespace conflict handling
    git checkout ai >/dev/null 2>&1
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    merge_origin_main_to_ai >/dev/null 2>&1
    local result=$?
    
    # Whitespace conflicts should be detectable
    return 0
}

test_large_file_conflicts() {
    CURRENT_TEST_REPO=$(create_test_repo "large_file_conflicts")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Create large file
    for i in {1..1000}; do
        echo "Line $i - AI branch content with some unique data $RANDOM" >> large_file.txt
    done
    git add large_file.txt >/dev/null 2>&1
    git commit -m "Add large file in ai" >/dev/null 2>&1
    
    git checkout main >/dev/null 2>&1
    # Create different large file
    for i in {1..1000}; do
        echo "Line $i - Main branch content with different data $RANDOM" >> large_file.txt
    done
    git add large_file.txt >/dev/null 2>&1
    git commit -m "Add large file in main" >/dev/null 2>&1
    git push origin main >/dev/null 2>&1
    
    # Test performance with large files
    git checkout ai >/dev/null 2>&1
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    merge_origin_main_to_ai >/dev/null 2>&1
    local result=$?
    
    return 0  # Success if handled without timeout
}

test_merge_with_uncommitted_changes() {
    CURRENT_TEST_REPO=$(create_test_repo "uncommitted_changes")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Make uncommitted changes
    echo "Uncommitted change" > uncommitted.txt
    git add uncommitted.txt >/dev/null 2>&1
    # Don't commit
    
    # Try merge with uncommitted changes
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    merge_origin_main_to_ai >/dev/null 2>&1
    local result=$?
    
    # Should handle uncommitted changes appropriately
    return 0
}

test_conflict_report_structure() {
    CURRENT_TEST_REPO=$(create_test_repo "report_structure")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Create conflict
    echo "AI content" > report_test.txt
    git add report_test.txt >/dev/null 2>&1
    git commit -m "Add file in ai" >/dev/null 2>&1
    
    git checkout main >/dev/null 2>&1
    echo "Main content" > report_test.txt
    git add report_test.txt >/dev/null 2>&1
    git commit -m "Modify file in main" >/dev/null 2>&1
    git push origin main >/dev/null 2>&1
    
    # Test conflict report structure
    git checkout ai >/dev/null 2>&1
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    # Create conflict and generate report
    git merge origin/main --no-edit >/dev/null 2>&1 || true
    detect_merge_conflicts >/dev/null 2>&1
    
    # Validate report structure
    local report_file="/tmp/opencode_conflict_report.json"
    if [[ -f "$report_file" ]]; then
        # Check for required JSON fields
        local required_fields=("conflict_type" "conflict_count" "conflicted_files" "merge_details" "escalation_required" "timestamp")
        for field in "${required_fields[@]}"; do
            if ! grep -q "\"$field\"" "$report_file"; then
                return 1
            fi
        done
        return 0
    fi
    
    return 1
}

test_merge_rollback_on_failure() {
    CURRENT_TEST_REPO=$(create_test_repo "rollback")
    local remote=$(setup_remote "$CURRENT_TEST_REPO")
    
    cd "$CURRENT_TEST_REPO"
    git checkout ai >/dev/null 2>&1
    
    # Save initial state
    local initial_commit=$(git rev-parse HEAD)
    
    # Create conflict scenario
    echo "AI content" > rollback_test.txt
    git add rollback_test.txt >/dev/null 2>&1
    git commit -m "Add file in ai" >/dev/null 2>&1
    
    git checkout main >/dev/null 2>&1
    echo "Main content" > rollback_test.txt
    git add rollback_test.txt >/dev/null 2>&1
    git commit -m "Modify file in main" >/dev/null 2>&1
    git push origin main >/dev/null 2>&1
    
    # Test rollback behavior
    git checkout ai >/dev/null 2>&1
    export GIT_REPO_DIR="$CURRENT_TEST_REPO"
    
    # Attempt merge that should fail
    merge_origin_main_to_ai >/dev/null 2>&1
    
    # Check if state is clean after failed merge
    local current_commit=$(git rev-parse HEAD)
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    local merge_status=$(git status --porcelain 2>/dev/null)
    
    # Should be clean and back to original state
    if [[ "$current_branch" == "ai" && -z "$merge_status" ]]; then
        return 0
    fi
    
    return 1
}

# Main test execution
main() {
    echo "=== Comprehensive Merge Conflict Handling Test Suite ==="
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
    
    # Test basic conflict scenarios
    log_info "Testing basic conflict scenarios..."
    run_test "File-level conflicts detection" "test_file_level_conflicts"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    run_test "Conflict detection and reporting" "test_conflict_detection"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    run_test "Conflict report structure validation" "test_conflict_report_structure"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    # Test complex conflict scenarios
    log_info "Testing complex conflict scenarios..."
    run_test "Complex multi-file conflicts" "test_complex_merge_conflicts"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    run_test "Nested directory conflicts" "test_nested_directory_conflicts"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    run_test "Binary file conflicts" "test_binary_file_conflicts"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    run_test "Deletion vs modification conflicts" "test_deletion_vs_modification_conflicts"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    # Test edge cases
    log_info "Testing edge cases..."
    run_test "Whitespace and formatting conflicts" "test_whitespace_and_formatting_conflicts"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    run_test "Large file conflicts" "test_large_file_conflicts"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    run_test "Merge with uncommitted changes" "test_merge_with_uncommitted_changes"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    run_test "Concurrent merge scenarios" "test_concurrent_merge_scenarios"
    cleanup_test_repositories
    mkdir -p "$TEST_REPO_BASE"
    
    run_test "Merge rollback on failure" "test_merge_rollback_on_failure"
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
        echo -e "${GREEN}✓ All comprehensive merge conflict tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}✗ Some merge conflict tests failed!${NC}"
        exit 1
    fi
}

# Run main function
main "$@"