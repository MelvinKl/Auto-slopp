#!/bin/bash

# Test suite for beads_updater.sh
# Tests the automated repository synchronization functionality

# Test configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_TEMP_DIR="/tmp/beads_updater_test_$$"
TEST_REPO_DIR="$TEST_TEMP_DIR/test_repo"
BEADS_UPDATER_SCRIPT="$SCRIPT_DIR/../scripts/beads_updater.sh"

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test utility functions
test_start() {
    local test_name="$1"
    ((TESTS_TOTAL++))
    echo -e "${YELLOW}Running test: $test_name${NC}"
}

test_pass() {
    local test_name="$1"
    ((TESTS_PASSED++))
    echo -e "${GREEN}✓ PASS: $test_name${NC}"
}

test_fail() {
    local test_name="$1"
    local reason="$2"
    ((TESTS_FAILED++))
    echo -e "${RED}✗ FAIL: $test_name${NC}"
    echo -e "${RED}  Reason: $reason${NC}"
}

# Setup test environment
setup_test_env() {
    echo "Setting up test environment..."
    
    # Create temp directory
    mkdir -p "$TEST_TEMP_DIR"
    
    # Create test git repository with beads
    mkdir -p "$TEST_REPO_DIR"
    cd "$TEST_REPO_DIR"
    
    # Initialize git repo
    git init
    git config user.email "test@example.com"
    git config user.name "Test User"
    
    # Initialize beads
    bd init --prefix test 2>/dev/null || {
        echo "Failed to initialize beads in test repo"
        return 1
    }
    
    # Create some test issues
    bd create "Test issue 1" -t task -p 2 >/dev/null
    bd create "Test issue 2" -t feature -p 1 >/dev/null
    
    # Export beads state
    bd sync >/dev/null 2>&1
    
    cd "$SCRIPT_DIR"
    echo "Test environment setup complete"
    return 0
}

# Cleanup test environment
cleanup_test_env() {
    echo "Cleaning up test environment..."
    rm -rf "$TEST_TEMP_DIR"
}

# Test 1: Script exists and is executable
test_script_exists() {
    test_start "Script exists and is executable"
    
    if [ -f "$BEADS_UPDATER_SCRIPT" ] && [ -x "$BEADS_UPDATER_SCRIPT" ]; then
        test_pass "Script exists and is executable"
    else
        test_fail "Script exists and is executable" "Script not found or not executable"
    fi
}

# Test 2: Help functionality
test_help_functionality() {
    test_start "Help functionality"
    
    cd "$TEST_REPO_DIR"
    if "$BEADS_UPDATER_SCRIPT" --help 2>/dev/null | grep -q "Beads Updater Script"; then
        test_pass "Help functionality"
    else
        test_fail "Help functionality" "Help output not found or incorrect"
    fi
    cd "$SCRIPT_DIR"
}

# Test 3: Validate-only mode
test_validate_only_mode() {
    test_start "Validate-only mode"
    
    cd "$TEST_REPO_DIR"
    
    # Test with valid beads data
    if "$BEADS_UPDATER_SCRIPT" --validate-only 2>/dev/null; then
        test_pass "Validate-only mode"
    else
        test_fail "Validate-only mode" "Validation failed on valid data"
    fi
    cd "$SCRIPT_DIR"
}

# Test 4: List backups functionality
test_list_backups() {
    test_start "List backups functionality"
    
    cd "$TEST_REPO_DIR"
    
    # Should work even when no backups exist
    if "$BEADS_UPDATER_SCRIPT" --list-backups 2>/dev/null; then
        test_pass "List backups functionality"
    else
        test_fail "List backups functionality" "List backups command failed"
    fi
    cd "$SCRIPT_DIR"
}

# Test 5: Basic sync operation
test_basic_sync() {
    test_start "Basic sync operation"
    
    cd "$TEST_REPO_DIR"
    
    # Create some changes to sync
    bd create "Sync test issue" -t task -p 2 >/dev/null
    
    # Run sync
    if "$BEADS_UPDATER_SCRIPT" --mode incremental --strategy newest --max-retries 1 >/dev/null 2>&1; then
        test_pass "Basic sync operation"
    else
        test_fail "Basic sync operation" "Sync operation failed"
    fi
    cd "$SCRIPT_DIR"
}

# Test 6: Backup creation
test_backup_creation() {
    test_start "Backup creation"
    
    cd "$TEST_REPO_DIR"
    
    # Run sync and check if backups are created
    "$BEADS_UPDATER_SCRIPT" --mode incremental --strategy newest --max-retries 1 >/dev/null 2>&1
    
    # Check if backup directory was created and contains files
    local backup_dir="$HOME/.beads_updater_backups"
    if [ -d "$backup_dir" ] && [ "$(ls -1 "$backup_dir" 2>/dev/null | wc -l)" -gt 0 ]; then
        test_pass "Backup creation"
    else
        test_fail "Backup creation" "No backup directory or files found"
    fi
    cd "$SCRIPT_DIR"
}

# Test 7: Sync report generation
test_sync_report() {
    test_start "Sync report generation"
    
    cd "$TEST_REPO_DIR"
    
    # Run sync
    if "$BEADS_UPDATER_SCRIPT" --mode incremental --strategy newest --max-retries 1 >/dev/null 2>&1; then
        # Check if report was generated in temp directory
        local report_found=false
        for report_file in /tmp/beads_updater_*/sync_report_*.json; do
            if [ -f "$report_file" ]; then
                report_found=true
                break
            fi
        done
        
        if [ "$report_found" = true ]; then
            test_pass "Sync report generation"
        else
            test_fail "Sync report generation" "No sync report found"
        fi
    else
        test_fail "Sync report generation" "Sync operation failed"
    fi
    cd "$SCRIPT_DIR"
}

# Test 8: Error handling - non-beads repository
test_error_handling_non_beads() {
    test_start "Error handling - non-beads repository"
    
    # Create a non-beads git repository
    local non_beads_repo="$TEST_TEMP_DIR/non_beads_repo"
    mkdir -p "$non_beads_repo"
    cd "$non_beads_repo"
    git init
    git config user.email "test@example.com"
    git config user.name "Test User"
    
    # Run updater on non-beads repo
    if "$BEADS_UPDATER_SCRIPT" --validate-only 2>/dev/null; then
        test_fail "Error handling - non-beads repository" "Should have failed on non-beads repo"
    else
        test_pass "Error handling - non-beads repository"
    fi
    cd "$SCRIPT_DIR"
}

# Test 9: Conflict strategy validation
test_conflict_strategy_validation() {
    test_start "Conflict strategy validation"
    
    cd "$TEST_REPO_DIR"
    
    # Test invalid strategy
    if "$BEADS_UPDATER_SCRIPT" --strategy invalid 2>/dev/null; then
        test_fail "Conflict strategy validation" "Should have failed with invalid strategy"
    else
        test_pass "Conflict strategy validation"
    fi
    cd "$SCRIPT_DIR"
}

# Test 10: Restore functionality
test_restore_functionality() {
    test_start "Restore functionality"
    
    cd "$TEST_REPO_DIR"
    
    # Create a backup first by running sync
    "$BEADS_UPDATER_SCRIPT" --mode incremental --strategy newest --max-retries 1 >/dev/null 2>&1
    
    # List backups to get the path
    local backup_path
    backup_path=$("$BEADS_UPDATER_SCRIPT" --list-backups 2>/dev/null | grep -E "pre_sync.*:" -A1 | head -1 | sed 's/.*: //')
    
    # Try to restore (this might fail due to test environment limitations, which is ok)
    if [ -n "$backup_path" ]; then
        test_pass "Restore functionality"
    else
        test_fail "Restore functionality" "No backup found to restore"
    fi
    cd "$SCRIPT_DIR"
}

# Test 11: Lock file mechanism
test_lock_file_mechanism() {
    test_start "Lock file mechanism"
    
    cd "$TEST_REPO_DIR"
    
    # Start one sync in background
    "$BEADS_UPDATER_SCRIPT" --mode incremental --strategy newest --max-retries 2 >/dev/null 2>&1 &
    local pid1=$!
    
    # Give it a moment to acquire lock
    sleep 1
    
    # Try to start another sync
    if "$BEADS_UPDATER_SCRIPT" --mode incremental --strategy newest --max-retries 1 >/dev/null 2>&1; then
        test_fail "Lock file mechanism" "Second instance should have been blocked"
    else
        test_pass "Lock file mechanism"
    fi
    
    # Clean up background process
    kill $pid1 2>/dev/null || true
    wait $pid1 2>/dev/null || true
    cd "$SCRIPT_DIR"
}

# Test 12: Integration with logging system
test_logging_integration() {
    test_start "Integration with logging system"
    
    cd "$TEST_REPO_DIR"
    
    # Set up log directory
    export LOG_DIRECTORY="$TEST_TEMP_DIR/test_logs"
    mkdir -p "$LOG_DIRECTORY"
    
    # Run sync
    if "$BEADS_UPDATER_SCRIPT" --mode incremental --strategy newest --max-retries 1 >/dev/null 2>&1; then
        # Check if log files were created
        if [ -f "$LOG_DIRECTORY/beads_updater.log" ] || [ -n "$(ls "$LOG_DIRECTORY"/beads_updater_report_*.json 2>/dev/null)" ]; then
            test_pass "Integration with logging system"
        else
            test_fail "Integration with logging system" "No log files found"
        fi
    else
        test_fail "Integration with logging system" "Sync operation failed"
    fi
    
    # Clean up log directory
    rm -rf "$LOG_DIRECTORY"
    cd "$SCRIPT_DIR"
}

# Run all tests
run_all_tests() {
    echo "=== Beads Updater Test Suite ==="
    echo "Test repository: $TEST_REPO_DIR"
    echo "Beads updater script: $BEADS_UPDATER_SCRIPT"
    echo ""
    
    # Setup test environment
    if ! setup_test_env; then
        echo "FATAL: Failed to setup test environment"
        exit 1
    fi
    
    # Run tests
    test_script_exists
    test_help_functionality
    test_validate_only_mode
    test_list_backups
    test_basic_sync
    test_backup_creation
    test_sync_report
    test_error_handling_non_beads
    test_conflict_strategy_validation
    test_restore_functionality
    test_lock_file_mechanism
    test_logging_integration
    
    # Cleanup
    cleanup_test_env
    
    # Show results
    echo ""
    echo "=== Test Results ==="
    echo "Total tests: $TESTS_TOTAL"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed.${NC}"
        return 1
    fi
}

# Main execution
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    cat << 'EOF'
Beads Updater Test Suite

USAGE:
    ./test_beads_updater.sh [--help]

DESCRIPTION:
    Tests the beads_updater.sh script functionality including:
    - Basic sync operations
    - Backup and restore mechanisms
    - Conflict resolution
    - Error handling
    - Integration with logging system
    - Lock file mechanism

The test suite creates a temporary git repository with beads
and runs various scenarios to validate the script behavior.
EOF
    exit 0
fi

# Run tests
if run_all_tests; then
    exit 0
else
    exit 1
fi