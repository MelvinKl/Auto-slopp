#!/bin/bash

# Integration Test Suite for Cleanup Automation Engine
# Tests end-to-end workflows and component integration
# Follows AAA Pattern: Arrange → Act → Assert
# Tests integration between cleanup engine and other system components

set -e

# Set script name for logging identification
SCRIPT_NAME="test-cleanup-automation-integration"

# Get directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/test_framework.sh"

# Load utilities and dependencies
source "$PROJECT_DIR/scripts/utils.sh"
source "$PROJECT_DIR/scripts/yaml_config.sh"

# ============================================================================
# TEST DATA SETUP
# ============================================================================

# Integration test environment setup
setup_integration_test_environment() {
    log "INFO" "Setting up integration test environment"
    
    # Create isolated test environment
    export TEST_INTEGRATION_DIR="/tmp/cleanup_engine_integration_$$"
    mkdir -p "$TEST_INTEGRATION_DIR"
    
    # Set up test managed repositories path
    export MANAGED_REPO_PATH="$TEST_INTEGRATION_DIR/managed_repos"
    mkdir -p "$MANAGED_REPO_PATH"
    
    # Set up test configuration
    export TEST_CONFIG_DIR="$TEST_INTEGRATION_DIR/config"
    mkdir -p "$TEST_CONFIG_DIR"
    
    # Create test configuration file
    cat > "$TEST_CONFIG_DIR/config.yaml" << 'EOF'
# Test configuration for cleanup automation engine integration tests
sleep_duration: 1
managed_repo_path: "/tmp/cleanup_engine_integration_$$/managed_repos"
log_directory: "/tmp/cleanup_engine_integration_$$/logs"
log_level: INFO
timestamp_format: readable-precise

# Branch cleanup configuration for testing
branch_cleanup:
  dry_run_mode: true                  # Use dry-run for safety in tests
  interactive_mode: false              # Non-interactive for automated tests
  confirm_before_delete: false         # Auto-confirm for tests
  safety_mode: true                   # Keep safety enabled
  backup_before_delete: true          # Test backup functionality
  max_branches_per_run: 10            # Conservative limit for tests
  show_dry_run_summary: true
  show_branch_details: true

# Branch protection configuration
branch_protection:
  enable_protection: true
  protected_branches:
    - "main"
    - "master"
    - "develop"
  protect_current_branch: true
  protection_patterns:
    - "keep-*"
    - "protected-*"
EOF

    # Override config path for testing
    export PROJECT_CONFIG_PATH="$TEST_CONFIG_DIR/config.yaml"
    
    # Create test logs directory
    mkdir -p "$TEST_INTEGRATION_DIR/logs"
    
    log "INFO" "Integration test environment setup completed"
}

# Create realistic test repositories
setup_test_repositories() {
    log "INFO" "Setting up test repositories"
    
    # Repository 1: Active development
    local repo1="$MANAGED_REPO_PATH/repo1-active"
    create_test_repository "$repo1" "repo1-active"
    cd "$repo1"
    
    # Create additional branches that would be cleaned up
    git checkout -b feature-old-api --quiet
    echo "old api code" > api_old.py
    git add api_old.py
    git commit -m "Add old API code" --quiet
    
    git checkout -b hotfix-temp-patch --quiet
    echo "temporary fix" > fix.patch
    git add fix.patch
    git commit -m "Temporary fix" --quiet
    
    git checkout -b keep-important-work --quiet
    echo "important work" > work.txt
    git add work.txt
    git commit -m "Important work to keep" --quiet
    
    git checkout main --quiet
    
    # Repository 2: Stale project
    local repo2="$MANAGED_REPO_PATH/repo2-stale"
    create_test_repository "$repo2" "repo2-stale"
    cd "$repo2"
    
    # Create many stale branches
    for i in {1..5}; do
        git checkout -b "stale-feature-$i" --quiet
        echo "stale feature $i" > "feature_$i.txt"
        git add "feature_$i.txt"
        git commit -m "Add stale feature $i" --quiet
    done
    
    git checkout main --quiet
    
    # Repository 3: Repository with issues
    local repo3="$MANAGED_REPO_PATH/repo3-issues"
    create_test_repository "$repo3" "repo3-issues"
    cd "$repo3"
    
    # Create problematic branches
    git checkout -b conflicted-branch --quiet
    echo "conflicted work" > conflict.txt
    git add conflict.txt
    git commit -m "Conflicted work" --quiet
    
    git checkout main --quiet
    
    # Create a non-git directory (should be skipped)
    local not_repo="$MANAGED_REPO_PATH/not-a-repo"
    mkdir -p "$not_repo"
    echo "not a git repository" > "$not_repo/readme.txt"
    
    log "INFO" "Test repositories setup completed"
}

# Create a test repository with basic structure
create_test_repository() {
    local repo_path="$1"
    local repo_name="$2"
    
    mkdir -p "$repo_path"
    cd "$repo_path"
    
    # Initialize git repo
    git init --quiet
    git config user.name "Test User"
    git config user.email "test@example.com"
    
    # Create initial commit
    echo "# $repo_name" > README.md
    git add README.md
    git commit -m "Initial commit for $repo_name" --quiet
    
    # Create main branch structure
    git checkout -b develop --quiet
    echo "develop work" > develop.txt
    git add develop.txt
    git commit -m "Set up develop branch" --quiet
    
    git checkout main --quiet
    
    log "DEBUG" "Created test repository: $repo_name"
}

# ============================================================================
# INTEGRATION TEST CASES
# ============================================================================

# Test 1: Basic Engine Initialization and Configuration Integration
test_engine_initialization() {
    log "INFO" "Test 1: Engine initialization and configuration integration"
    
    # Arrange
    local engine_script="$PROJECT_DIR/scripts/cleanup-automation-engine.sh"
    
    # Act
    # Test that engine can initialize without errors
    if ! (cd "$PROJECT_DIR" && source "$engine_script" && initialize_engine); then
        fail "Engine initialization failed"
    fi
    
    # Assert
    # Check that environment variables are loaded correctly
    if [[ "$MANAGED_REPO_PATH" != "$TEST_INTEGRATION_DIR/managed_repos" ]]; then
        fail "MANAGED_REPO_PATH not set correctly from test config"
    fi
    
    # Check that configuration loading works
    if [[ -z "$DRY_RUN_MODE" ]]; then
        fail "Configuration not loaded properly - DRY_RUN_MODE not set"
    fi
    
    pass "Engine initialization and configuration integration test passed"
}

# Test 2: Branch Cleanup Integration
test_branch_cleanup_integration() {
    log "INFO" "Test 2: Branch cleanup integration"
    
    # Arrange
    local engine_script="$PROJECT_DIR/scripts/cleanup-automation-engine.sh"
    local branch_cleanup_script="$PROJECT_DIR/scripts/cleanup-branches-enhanced.sh"
    
    # Ensure scripts are executable
    chmod +x "$engine_script"
    chmod +x "$branch_cleanup_script"
    
    # Act - Test that cleanup engine can invoke branch cleanup
    local output
    cd "$PROJECT_DIR"
    output=$("$engine_script" run BRANCH 2>&1) || {
        log "DEBUG" "Branch cleanup integration exit code: $?"
        log "DEBUG" "Output: $output"
    }
    
    # Assert
    if [[ -z "$output" ]]; then
        fail "No output from branch cleanup integration"
    fi
    
    # Check that repositories are being processed
    if ! echo "$output" | grep -q "repo1-active\|repo2-stale\|repo3-issues\|operation\|cleanup"; then
        log "DEBUG" "Looking for repository names in output: $output"
        fail "Test repositories not found in output"
    fi
    
    pass "Branch cleanup integration test passed"
}

# Test 3: Configuration File Integration
test_configuration_integration() {
    log "INFO" "Test 3: Configuration file integration"
    
    # Arrange
    local engine_script="$PROJECT_DIR/scripts/cleanup-automation-engine.sh"
    
    # Act - Test configuration loading from test config file
    cd "$PROJECT_DIR"
    source "$PROJECT_DIR/scripts/yaml_config.sh"
    
    # Load test configuration
    if ! load_config "$TEST_CONFIG_DIR/config.yaml"; then
        fail "Failed to load test configuration"
    fi
    
    # Assert - Check that configuration values are loaded correctly
    if [[ "$DRY_RUN_MODE" != "true" ]]; then
        fail "DRY_RUN_MODE not loaded correctly from config"
    fi
    
    if [[ "$INTERACTIVE_MODE" != "false" ]]; then
        fail "INTERACTIVE_MODE not loaded correctly from config"
    fi
    
    if [[ "$MAX_BRANCHES_PER_RUN" != "10" ]]; then
        fail "MAX_BRANCHES_PER_RUN not loaded correctly from config"
    fi
    
    pass "Configuration file integration test passed"
}

# Test 4: Error Handling Integration
test_error_handling_integration() {
    log "INFO" "Test 4: Error handling integration"
    
    # Arrange
    local engine_script="$PROJECT_DIR/scripts/cleanup-automation-engine.sh"
    
    # Create a problematic repository (corrupted git repo)
    local broken_repo="$MANAGED_REPO_PATH/broken-repo"
    mkdir -p "$broken_repo"
    cd "$broken_repo"
    echo "broken" > README.md
    # Create .git directory but make it invalid
    mkdir .git
    echo "invalid" > .git/HEAD
    
    # Act - Test error handling with broken repository
    local output
    local exit_code
    output=$("$engine_script" --type HEALTH 2>&1)
    exit_code=$?
    
    # Assert
    # Should handle error gracefully and continue
    if [[ $exit_code -eq 0 ]]; then
        log "DEBUG" "Engine handled broken repository gracefully"
    else
        log "DEBUG" "Engine failed with exit code: $exit_code"
    fi
    
    # Should log error messages
    if ! echo "$output" | grep -q -i "error\|failed\|invalid"; then
        fail "Error handling not logging error messages properly"
    fi
    
    pass "Error handling integration test passed"
}

# Test 5: Repository Discovery Integration
test_repository_discovery_integration() {
    log "INFO" "Test 5: Repository discovery integration"
    
    # Arrange
    local engine_script="$PROJECT_DIR/scripts/cleanup-automation-engine.sh"
    
    # Act - Test repository discovery via health command
    local output
    cd "$PROJECT_DIR"
    output=$("$engine_script" health 2>&1) || {
        log "DEBUG" "Repository discovery exit code: $?"
        log "DEBUG" "Output: $output"
    }
    
    # Assert
    # Should process the valid repositories
    if ! echo "$output" | grep -q "repo1-active\|repo2-stale\|repo3-issues"; then
        log "DEBUG" "Looking for repository names in health output: $output"
        fail "Test repositories not discovered during health check"
    fi
    
    # Should show health check processing
    if ! echo "$output" | grep -q "health\|repository\|validation"; then
        log "DEBUG" "Health check pattern not found in: $output"
    fi
    
    pass "Repository discovery integration test passed"
}

# Test 6: Operation Queue Integration
test_operation_queue_integration() {
    log "INFO" "Test 6: Operation queue integration"
    
    # Arrange
    local engine_script="$PROJECT_DIR/scripts/cleanup-automation-engine.sh"
    
    # Act - Test operation queue creation and processing with specific repos
    local output
    cd "$PROJECT_DIR"
    output=$("$engine_script" run BRANCH repo1-active repo2-stale 2>&1) || {
        log "DEBUG" "Operation queue exit code: $?"
        log "DEBUG" "Output: $output"
    }
    
    # Assert
    # Should show processing of operations
    if ! echo "$output" | grep -q "operation\|queue\|process\|cleanup"; then
        log "DEBUG" "Operation processing not found in: $output"
        fail "Operation queue processing not detected"
    fi
    
    # Should show engine activity
    if ! echo "$output" | grep -q "engine\|cleanup\|automation"; then
        log "DEBUG" "Engine activity not found in: $output"
        fail "Engine activity not detected"
    fi
    
    pass "Operation queue integration test passed"
}

# Test 7: Logging Integration
test_logging_integration() {
    log "INFO" "Test 7: Logging integration"
    
    # Arrange
    local engine_script="$PROJECT_DIR/scripts/cleanup-automation-engine.sh"
    local test_log_file="$TEST_INTEGRATION_DIR/logs/integration_test.log"
    
    # Act - Run engine and check logging
    local output
    cd "$PROJECT_DIR"
    output=$("$engine_script" health 2>&1) || {
        log "DEBUG" "Logging integration exit code: $?"
    }
    
    # Assert
    # Check that output contains expected log patterns
    if ! echo "$output" | grep -q "INFO\|DEBUG\|WARNING\|ERROR\|log"; then
        log "DEBUG" "Log patterns not found in: $output"
        fail "Expected log levels not found in output"
    fi
    
    # Check timestamp format
    if ! echo "$output" | grep -q "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]"; then
        log "DEBUG" "Timestamps not found in: $output"
        fail "Timestamps not found in log output"
    fi
    
    pass "Logging integration test passed"
}

# Test 8: State Management Integration
test_state_management_integration() {
    log "INFO" "Test 8: State management integration"
    
    # Arrange
    local engine_script="$PROJECT_DIR/scripts/cleanup-automation-engine.sh"
    
    # Act - Test state management through engine run
    local output
    cd "$PROJECT_DIR"
    output=$("$engine_script" run BRANCH 2>&1) || {
        log "DEBUG" "State management exit code: $?"
    }
    
    # Assert
    # Check that engine reports state information
    if ! echo "$output" | grep -q "operations\|completed\|processed\|state"; then
        log "DEBUG" "State management not found in: $output"
        fail "State management information not found in output"
    fi
    
    pass "State management integration test passed"
}

# Test 9: Performance Metrics Integration
test_performance_metrics_integration() {
    log "INFO" "Test 9: Performance metrics integration"
    
    # Arrange
    local engine_script="$PROJECT_DIR/scripts/cleanup-automation-engine.sh"
    
    # Act - Test performance metrics collection
    local start_time=$(date +%s.%N)
    local output
    cd "$PROJECT_DIR"
    output=$("$engine_script" run BRANCH 2>&1) || {
        log "DEBUG" "Performance metrics exit code: $?"
    }
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    
    # Assert
    # Check that performance information is captured
    if ! echo "$output" | grep -q "operations\|completed\|duration\|report\|summary"; then
        log "DEBUG" "Performance information not found in: $output"
        fail "Performance metrics not found in output"
    fi
    
    # Check that duration is reasonable (should complete within 30 seconds)
    if (( $(echo "$duration > 30" | bc -l 2>/dev/null || echo "0") )); then
        log "DEBUG" "Engine duration: ${duration}s"
        fail "Engine performance is poor: ${duration}s duration"
    fi
    
    pass "Performance metrics integration test passed"
}

# Test 10: Integration with Branch Protection
test_branch_protection_integration() {
    log "INFO" "Test 10: Integration with branch protection"
    
    # Arrange
    local engine_script="$PROJECT_DIR/scripts/cleanup-automation-engine.sh"
    local branch_protection_script="$PROJECT_DIR/scripts/branch_protection.sh"
    
    # Ensure branch protection script is available
    if [[ ! -f "$branch_protection_script" ]]; then
        fail "Branch protection script not found"
    fi
    
    # Act - Test that engine can run and branch protection is available
    local output
    cd "$PROJECT_DIR"
    output=$("$engine_script" run BRANCH 2>&1) || {
        log "DEBUG" "Branch protection integration exit code: $?"
    }
    
    # Assert
    # Should show engine activity
    if ! echo "$output" | grep -q "engine\|cleanup\|operation\|process"; then
        log "DEBUG" "Engine activity not found in: $output"
        fail "Engine activity not detected"
    fi
    
    # Should complete without critical errors
    if echo "$output" | grep -q "CRITICAL\|FATAL\|ABORT"; then
        log "DEBUG" "Critical errors found in: $output"
        fail "Critical errors encountered during branch protection integration"
    fi
    
    pass "Branch protection integration test passed"
}

# ============================================================================
# TEST EXECUTION FRAMEWORK
# ============================================================================

# Run all integration tests
run_integration_tests() {
    log "INFO" "Starting cleanup automation engine integration tests"
    
    local total_tests=10
    local passed_tests=0
    local failed_tests=0
    
    # Setup test environment
    setup_integration_test_environment
    setup_test_repositories
    
    # Run each test
    local tests=(
        "test_engine_initialization"
        "test_branch_cleanup_integration"
        "test_configuration_integration"
        "test_error_handling_integration"
        "test_repository_discovery_integration"
        "test_operation_queue_integration"
        "test_logging_integration"
        "test_state_management_integration"
        "test_performance_metrics_integration"
        "test_branch_protection_integration"
    )
    
    for test_func in "${tests[@]}"; do
        log "INFO" "Running $test_func"
        if $test_func; then
            ((passed_tests++))
        else
            ((failed_tests++))
        fi
    done
    
    # Generate test report
    generate_integration_test_report "$total_tests" "$passed_tests" "$failed_tests"
    
    return $failed_tests
}

# Generate comprehensive integration test report
generate_integration_test_report() {
    local total_tests="$1"
    local passed_tests="$2"
    local failed_tests="$3"
    
    echo
    echo "==================================="
    echo "CLEANUP AUTOMATION ENGINE INTEGRATION TEST REPORT"
    echo "==================================="
    echo
    echo "Total Tests: $total_tests"
    echo "Passed: $passed_tests"
    echo "Failed: $failed_tests"
    echo "Success Rate: $(( passed_tests * 100 / total_tests ))%"
    echo
    
    if [[ $failed_tests -eq 0 ]]; then
        echo "🎉 ALL INTEGRATION TESTS PASSED!"
        echo "Cleanup automation engine is ready for production"
    else
        echo "❌ $failed_tests INTEGRATION TEST(S) FAILED"
        echo "Please review and fix integration issues before production deployment"
    fi
    
    echo
    echo "Test Environment: $TEST_INTEGRATION_DIR"
    echo "Configuration: $TEST_CONFIG_DIR/config.yaml"
    echo "Log Files: $TEST_INTEGRATION_DIR/logs/"
    echo
    
    # Show summary of test repositories
    echo "Test Repositories Created:"
    ls -la "$MANAGED_REPO_PATH" | grep '^d'
    echo
    
    # Performance summary
    echo "Integration test execution completed in: ${SECONDS}s"
    echo
}

# Cleanup function
cleanup_integration_test() {
    log "INFO" "Cleaning up integration test environment"
    
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    
    # Remove test environment
    if [[ -n "$TEST_INTEGRATION_DIR" && -d "$TEST_INTEGRATION_DIR" ]]; then
        rm -rf "$TEST_INTEGRATION_DIR"
    fi
    
    # Clean up any temporary files
    rm -f /tmp/cleanup_engine_state_test_*
    
    log "INFO" "Integration test cleanup completed"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Main function
main() {
    log "INFO" "Starting cleanup automation engine integration test suite"
    
    # Set up cleanup trap
    trap cleanup_integration_test EXIT
    
    # Record start time
    SECONDS=0
    
    # Run integration tests
    local exit_code=0
    run_integration_tests || exit_code=$?
    
    # Exit with appropriate code
    if [[ $exit_code -eq 0 ]]; then
        log "SUCCESS" "All integration tests completed successfully"
        exit 0
    else
        log "ERROR" "Some integration tests failed"
        exit 1
    fi
}

# Helper functions for test framework
pass() {
    local message="$1"
    echo "✅ PASS: $message"
}

fail() {
    local message="$1"
    echo "❌ FAIL: $message"
    return 1
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi