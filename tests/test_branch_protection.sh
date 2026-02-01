#!/bin/bash

# Test script for Enhanced Branch Protection
# This script tests the branch protection functionality

# Set script name for logging identification
SCRIPT_NAME="test-branch-protection"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load configuration and branch protection
source "$PROJECT_DIR/config.sh"
source "$PROJECT_DIR/scripts/branch_protection.sh"

# Test functions
test_configuration_loading() {
    echo "=== Testing Configuration Loading ==="
    echo "Protection enabled: $branch_protection_enable_protection"
    echo "Require confirmation: $branch_protection_require_confirmation"
    echo "Show warnings: $branch_protection_show_warnings"
    echo "Protected branches count: ${#branch_protection_protected_branches[@]}"
    echo "Protection patterns count: ${#branch_protection_protection_patterns[@]}"
    echo "Explicit confirmation branches count: ${#branch_protection_require_explicit_confirmation_for[@]}"
    echo
}

test_pattern_matching() {
    echo "=== Testing Pattern Matching ==="
    
    # Set up test patterns temporarily
    PROTECTION_PATTERNS=("keep-*" "protected-*" "temp-*" "backup-*")
    
    local test_branches=("main" "keep-feature" "protected-branch" "temp-work" "normal-branch" "backup-old")
    
    for branch in "${test_branches[@]}"; do
        if matches_protection_pattern "$branch"; then
            echo "✓ $branch matches protection pattern"
        else
            echo "✗ $branch does not match protection pattern"
        fi
    done
    echo
}

test_protected_list_checking() {
    echo "=== Testing Protected List Checking ==="
    
    # Set up test protected branches temporarily
    PROTECTED_BRANCHES=("main" "master" "develop" "staging" "production")
    
    local test_branches=("main" "feature-branch" "master" "hotfix" "develop" "test")
    
    for branch in "${test_branches[@]}"; do
        if is_in_protected_list "$branch"; then
            echo "✓ $branch is in protected list"
        else
            echo "✗ $branch is not in protected list"
        fi
    done
    echo
}

test_explicit_confirmation_checking() {
    echo "=== Testing Explicit Confirmation Checking ==="
    
    # Set up test explicit confirmation branches temporarily
    EXPLICIT_CONFIRMATION_BRANCHES=("main" "master" "develop" "staging" "production")
    
    local test_branches=("main" "feature-branch" "master" "hotfix" "develop" "test")
    
    for branch in "${test_branches[@]}"; do
        if requires_explicit_confirmation "$branch"; then
            echo "✓ $branch requires explicit confirmation"
        else
            echo "✗ $branch does not require explicit confirmation"
        fi
    done
    echo
}

test_comprehensive_protection() {
    echo "=== Testing Comprehensive Branch Protection ==="
    
    # Initialize with test data
    PROTECTED_BRANCHES=("main" "master" "develop")
    PROTECTION_PATTERNS=("keep-*" "temp-*")
    EXPLICIT_CONFIRMATION_BRANCHES=("main" "master")
    BRANCH_PROTECTION_ENABLED="true"
    
    local test_cases=(
        "main:protected-list"
        "master:protected-list" 
        "develop:protected-list"
        "keep-feature:pattern-match"
        "temp-work:pattern-match"
        "normal-branch:unprotected"
        "feature-branch:unprotected"
    )
    
    for case in "${test_cases[@]}"; do
        IFS=':' read -r branch expected <<< "$case"
        
        local should_be_protected=false
        case "$expected" in
            "protected-list"|"pattern-match")
                should_be_protected=true
                ;;
        esac
        
        if check_branch_protection "$branch" "$(pwd)" "test" 2>/dev/null; then
            # Protection check passed (not protected)
            if [[ "$should_be_protected" == "false" ]]; then
                echo "✓ $branch correctly identified as unprotected"
            else
                echo "✗ $branch should be protected but was allowed"
            fi
        else
            # Protection check failed (protected)
            if [[ "$should_be_protected" == "true" ]]; then
                echo "✓ $branch correctly identified as protected"
            else
                echo "✗ $branch should be unprotected but was blocked"
            fi
        fi
    done
    echo
}

test_current_branch_protection() {
    echo "=== Testing Current Branch Protection ==="
    
    # Set up test configuration
    PROTECT_CURRENT_BRANCH="true"
    
    local current_branch
    if current_branch=$(get_current_branch_safe "$(pwd)"); then
        echo "Current branch: $current_branch"
        
        if check_branch_protection "$current_branch" "$(pwd)" "test" 2>/dev/null; then
            echo "✗ Current branch should be protected but was allowed"
        else
            echo "✓ Current branch correctly identified as protected"
        fi
    else
        echo "⚠ Could not determine current branch"
    fi
    echo
}

# Main test execution
main() {
    echo "Enhanced Branch Protection - Test Suite"
    echo "====================================="
    echo
    
    # Test configuration validation
    if validate_branch_protection_config; then
        echo "✓ Branch protection configuration is valid"
    else
        echo "✗ Branch protection configuration is invalid"
    fi
    echo
    
    # Run individual tests
    test_configuration_loading
    test_pattern_matching
    test_protected_list_checking
    test_explicit_confirmation_checking
    test_comprehensive_protection
    test_current_branch_protection
    
    echo "=== Summary ==="
    echo "All tests completed. Review output above for any issues."
    echo
    echo "To test with actual branch operations, run:"
    echo "  $0 <repository_path> <branch_name>"
    echo
}

# Handle command line arguments
if [[ $# -ge 2 ]]; then
    repo_path="$1"
    branch_name="$2"
    
    echo "Testing branch protection for specific case:"
    echo "Repository: $repo_path"
    echo "Branch: $branch_name"
    echo
    
    if check_branch_protection "$branch_name" "$repo_path" "test"; then
        echo "Result: Branch is NOT protected"
        exit 0
    else
        echo "Result: Branch IS protected"
        exit 1
    fi
else
    main
fi