#!/bin/bash

# Test script for enhanced dry-run and confirmation features
# Tests Auto-683 implementation

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_REPO_DIR="/tmp/test_branch_cleanup_$(date +%s)"
ENHANCED_CLEANUP_SCRIPT="$SCRIPT_DIR/cleanup-branches-enhanced.sh"

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Test logging
log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Setup test environment
setup_test_repo() {
    log_info "Setting up test repository in: $TEST_REPO_DIR"
    
    mkdir -p "$TEST_REPO_DIR"
    cd "$TEST_REPO_DIR"
    
    # Initialize git repo
    git init
    git config user.email "test@example.com"
    git config user.name "Test User"
    
    # Create initial commit
    echo "# Test Repository" > README.md
    git add README.md
    git commit -m "Initial commit"
    
    # Create main branch and some feature branches
    git branch develop
    
    # Create feature branches that would be cleaned up
    git checkout -b feature/old-branch-1
    echo "Feature 1" > feature1.txt
    git add feature1.txt
    git commit -m "Add feature 1"
    git checkout main
    
    git checkout -b feature/old-branch-2
    echo "Feature 2" > feature2.txt
    git add feature2.txt
    git commit -m "Add feature 2"
    git checkout main
    
    # Create a protected branch pattern
    git checkout -b keep-important-branch
    echo "Important" > important.txt
    git add important.txt
    git commit -m "Add important branch"
    git checkout main
    
    log_info "Test repository setup complete"
}

# Cleanup test environment
cleanup_test_repo() {
    if [[ -d "$TEST_REPO_DIR" ]]; then
        rm -rf "$TEST_REPO_DIR"
        log_info "Cleaned up test repository"
    fi
}

# Test 1: Dry-run mode should not delete branches
test_dry_run_mode() {
    log_test "Testing dry-run mode..."
    
    # Set dry-run mode and test
    export DRY_RUN_MODE=true
    export INTERACTIVE_MODE=false
    export MANAGED_REPO_PATH="$(dirname "$TEST_REPO_DIR")"
    
    # Run the enhanced cleanup script
    if output=$("$ENHANCED_CLEANUP_SCRIPT" 2>&1); then
        # Check that dry-run messages are present
        if echo "$output" | grep -q "DRY RUN ANALYSIS" && \
           echo "$output" | grep -q "This is a DRY RUN" && \
           echo "$output" | grep -q "branches that would be DELETED"; then
            log_pass "Dry-run mode shows proper analysis messages"
        else
            log_fail "Dry-run mode missing expected messages"
            echo "$output" | head -20
        fi
        
        # Verify branches still exist
        cd "$TEST_REPO_DIR"
        local branch_count=$(git branch --format='%(refname:short)' | wc -l)
        if [[ $branch_count -gt 3 ]]; then  # Should have main, develop, feature branches, keep branch
            log_pass "Dry-run mode preserved all branches ($branch_count branches remain)"
        else
            log_fail "Dry-run mode may have deleted branches (only $branch_count branches remain)"
        fi
    else
        log_fail "Enhanced cleanup script failed in dry-run mode"
    fi
}

# Test 2: Configuration loading
test_configuration_loading() {
    log_test "Testing configuration loading..."
    
    # Test that configuration values are loaded correctly
    export branch_cleanup_dry_run_mode=true
    export branch_cleanup_interactive_mode=true
    export branch_cleanup_confirm_before_delete=true
    export branch_cleanup_confirmation_timeout=30
    
    # Source the enhanced cleanup script to test configuration loading
    if output=$(bash -c "source '$ENHANCED_CLEANUP_SCRIPT'; echo DRY_RUN_MODE: \$DRY_RUN_MODE; echo INTERACTIVE_MODE: \$INTERACTIVE_MODE; echo CONFIRM_BEFORE_DELETE: \$CONFIRM_BEFORE_DELETE; echo CONFIRMATION_TIMEOUT: \$CONFIRMATION_TIMEOUT" 2>&1); then
        if echo "$output" | grep -q "DRY_RUN_MODE: true" && \
           echo "$output" | grep -q "INTERACTIVE_MODE: true" && \
           echo "$output" | grep -q "CONFIRM_BEFORE_DELETE: true" && \
           echo "$output" | grep -q "CONFIRMATION_TIMEOUT: 30"; then
            log_pass "Configuration values loaded correctly"
        else
            log_fail "Configuration loading failed"
            echo "$output"
        fi
    else
        log_fail "Failed to source enhanced cleanup script for configuration test"
    fi
}

# Test 3: Interactive mode functions exist
test_interactive_functions() {
    log_test "Testing interactive function availability..."
    
    # Test that interactive functions are defined
    if output=$(bash -c "source '$ENHANCED_CLEANUP_SCRIPT'; declare -f | grep -E '^(show_dry_run_analysis|request_branch_deletion_confirmation|request_user_confirmation)'" 2>&1); then
        local function_count=$(echo "$output" | wc -l)
        if [[ $function_count -ge 3 ]]; then
            log_pass "Interactive functions are properly defined ($function_count functions found)"
        else
            log_fail "Missing interactive functions (only $function_count found)"
            echo "$output"
        fi
    else
        log_fail "Failed to check interactive functions"
    fi
}

# Test 4: Branch analysis functionality
test_branch_analysis() {
    log_test "Testing branch analysis functionality..."
    
    export MANAGED_REPO_PATH="$(dirname "$TEST_REPO_DIR")"
    
    # Test branch analysis function
    if output=$(bash -c "
        source '$ENHANCED_CLEANUP_SCRIPT'
        cd '$TEST_REPO_DIR'
        if analyze_branches_comprehensive '$TEST_REPO_DIR' >/dev/null 2>&1; then
            echo 'ANALYSIS_SUCCESS'
        else
            echo 'ANALYSIS_FAILED'
        fi
    " 2>&1); then
        if [[ "$output" == "ANALYSIS_SUCCESS" ]]; then
            log_pass "Branch analysis function works correctly"
        else
            log_fail "Branch analysis function failed"
        fi
    else
        log_fail "Failed to run branch analysis test"
    fi
}

# Test 5: Configuration validation
test_configuration_validation() {
    log_test "Testing configuration validation..."
    
    # Test that config.yaml has the new branch_cleanup section
    if grep -q "branch_cleanup:" "$PROJECT_DIR/config.yaml"; then
        if grep -q "dry_run_mode:" "$PROJECT_DIR/config.yaml" && \
           grep -q "interactive_mode:" "$PROJECT_DIR/config.yaml" && \
           grep -q "confirm_before_delete:" "$PROJECT_DIR/config.yaml"; then
            log_pass "Configuration file has required branch_cleanup settings"
        else
            log_fail "Configuration file missing required branch_cleanup settings"
        fi
    else
        log_fail "Configuration file missing branch_cleanup section"
    fi
}

# Run all tests
main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           Auto-683 Dry-Run & Confirmation Tests             ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    # Check if enhanced cleanup script exists
    if [[ ! -f "$ENHANCED_CLEANUP_SCRIPT" ]]; then
        echo -e "${RED}Error: Enhanced cleanup script not found: $ENHANCED_CLEANUP_SCRIPT${NC}"
        exit 1
    fi
    
    # Setup test environment
    setup_test_repo
    
    # Run tests
    test_configuration_validation
    test_configuration_loading
    test_interactive_functions
    test_branch_analysis
    test_dry_run_mode
    
    # Cleanup
    cleanup_test_repo
    
    # Summary
    echo
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                        TEST SUMMARY                        ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo -e "Tests Passed:  ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests Failed:  ${RED}$TESTS_FAILED${NC}"
    echo -e "Total Tests:   $((TESTS_PASSED + TESTS_FAILED))"
    echo
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✅ All tests passed! Auto-683 implementation is working correctly.${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed. Please review the implementation.${NC}"
        exit 1
    fi
}

# Run tests if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi