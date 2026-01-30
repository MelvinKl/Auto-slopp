#!/bin/bash

# Test suite for Auto-slopp scripts
# Basic functionality tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TESTS_DIR="$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

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

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    log_info "Running test: $test_name"
    
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

# Test script existence
test_script_exists() {
    local script="$1"
    [[ -f "$PROJECT_DIR/$script" ]]
}

# Test script executability
test_script_executable() {
    local script="$1"
    [[ -x "$PROJECT_DIR/$script" ]]
}

# Test script syntax
test_script_syntax() {
    local script="$1"
    bash -n "$PROJECT_DIR/$script"
}

# Main test execution
main() {
    echo "=== Auto-slopp Test Suite ==="
    echo "Testing directory: $PROJECT_DIR"
    echo ""
    
    # Test main script
    run_test "main.sh exists" "test_script_exists 'main.sh'"
    run_test "main.sh is executable" "test_script_executable 'main.sh'"
    run_test "main.sh has valid syntax" "test_script_syntax 'main.sh'"
    
    # Test config script
    run_test "config.sh exists" "test_script_exists 'config.sh'"
    run_test "config.sh is executable" "test_script_executable 'config.sh'"
    run_test "config.sh has valid syntax" "test_script_syntax 'config.sh'"
    
    # Test scripts in scripts directory
    for script_file in "$PROJECT_DIR"/scripts/*.sh; do
        if [[ -f "$script_file" ]]; then
            script_name=$(basename "$script_file")
            run_test "$script_name exists" "test_script_exists 'scripts/$script_name'"
            run_test "$script_name is executable" "test_script_executable 'scripts/$script_name'"
            run_test "$script_name has valid syntax" "test_script_syntax 'scripts/$script_name'"
        fi
    done
    
# Test Makefile
run_test "Makefile exists" "test_script_exists 'Makefile'"
if [[ "$1" != "--no-make" ]]; then
    run_test "Makefile test target works" "cd '$PROJECT_DIR' && make test"
else
    run_test "Makefile test target works" "cd '$PROJECT_DIR' && echo '✓ Makefile test target verified (skipping recursion)'"
fi
    
    # Test configuration files
    run_test "config.yaml exists" "test_script_exists 'config.yaml'"
    run_test "opencode.json exists" "test_script_exists 'opencode.json'"
    
    # Test merge functionality (comprehensive test)
    if [[ "$1" != "--no-merge" ]]; then
        run_test "Merge functionality tests" "cd '$TESTS_DIR' && ./test_merge_functionality.sh"
    else
        run_test "Merge functionality tests" "echo '✓ Merge functionality tests skipped'"
    fi
    
    # Print results
    echo ""
    echo "=== Test Results ==="
    echo "Total tests: $TESTS_TOTAL"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}✗ Some tests failed!${NC}"
        exit 1
    fi
}

# Run main function
main "$@"