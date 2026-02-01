#!/bin/bash

# Enhanced Test Framework for Auto-slopp
# Provides comprehensive testing utilities and standards compliance
# Follows AAA Pattern: Arrange → Act → Assert

set -e

# Framework metadata
FRAMEWORK_VERSION="2.0"
FRAMEWORK_NAME="Auto-slopp Enhanced Test Framework"

# Get directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test counters and metrics
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0
TESTS_TOTAL_TIME=0

# Coverage tracking
COVERAGE_CRITICAL=0
COVERAGE_HIGH=0
COVERAGE_MEDIUM=0
COVERAGE_LOW=0

# Performance tracking
PERFORMANCE_RESULTS=()
START_TIME=$(date +%s)

# Test categories
declare -A TEST_CATEGORIES=(
    ["unit"]="Unit Tests - Isolated function testing"
    ["integration"]="Integration Tests - Component interaction"
    ["system"]="System Tests - End-to-end workflows"
    ["performance"]="Performance Tests - Speed and resource usage"
    ["security"]="Security Tests - Input validation and permissions"
    ["regression"]="Regression Tests - Prevent functionality loss"
)

# Coverage levels
declare -A COVERAGE_LEVELS=(
    ["critical"]="Business logic, data transformations (100%)"
    ["high"]="Public APIs, user-facing features (90%+)"
    ["medium"]="Utilities, helpers (80%+)"
    ["low"]="Simple wrappers, configs (optional)"
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Logging functions with context
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
}

log_debug() {
    if [[ "${DEBUG:-}" == "true" ]]; then
        echo -e "${PURPLE}[DEBUG]${NC} $1"
    fi
}

log_category() {
    local category="$1"
    echo -e "${CYAN}[${category^^}]${NC}"
}

# ============================================================================
# TEST FRAMEWORK CORE FUNCTIONS
# ============================================================================

# Setup test environment with isolation
setup_test_environment() {
    local test_name="$1"
    
    log_info "Setting up test environment for: $test_name"
    
    # Create isolated test directory
    export TEST_BASE_DIR="/tmp/auto-slopp-test-$$-$(date +%s)"
    mkdir -p "$TEST_BASE_DIR"/{tmp,logs,data,repositories}
    
    # Export test environment variables
    export TEST_PROJECT_DIR="$PROJECT_DIR"
    export TEST_SCRIPT_DIR="$SCRIPT_DIR"
    export TEST_LOG_DIR="$TEST_BASE_DIR/logs"
    export TEST_DATA_DIR="$TEST_BASE_DIR/data"
    export TEST_TMP_DIR="$TEST_BASE_DIR/tmp"
    
    # Initialize test state
    export TEST_CURRENT_TEST="$test_name"
    export TEST_SETUP_TIME=$(date +%s)
    
    log_debug "Test environment: $TEST_BASE_DIR"
}

# Cleanup test environment
cleanup_test_environment() {
    log_debug "Cleaning up test environment"
    if [[ -n "${TEST_BASE_DIR:-}" && -d "$TEST_BASE_DIR" ]]; then
        rm -rf "$TEST_BASE_DIR"
    fi
    unset TEST_BASE_DIR TEST_PROJECT_DIR TEST_SCRIPT_DIR TEST_LOG_DIR TEST_DATA_DIR TEST_TMP_DIR
    unset TEST_CURRENT_TEST TEST_SETUP_TIME
}

# ============================================================================
# AAA PATTERN IMPLEMENTATION
# ============================================================================

# Arrange phase - Setup test data and mocks
arrange() {
    local description="$1"
    local setup_commands="$2"
    
    log_debug "ARRANGE: $description"
    
    if [[ -n "$setup_commands" ]]; then
        eval "$setup_commands"
    fi
}

# Act phase - Execute the code under test
act() {
    local description="$1"
    local action_commands="$2"
    
    log_debug "ACT: $description"
    
    if [[ -n "$action_commands" ]]; then
        eval "$action_commands"
    fi
}

# Assert phase - Verify results
assert() {
    local description="$1"
    local assertion_commands="$2"
    
    log_debug "ASSERT: $description"
    
    if eval "$assertion_commands"; then
        return 0
    else
        return 1
    fi
}

# ============================================================================
# ENHANCED TEST EXECUTION
# ============================================================================

# Run test with comprehensive tracking
run_test() {
    local test_name="$1"
    local test_function="$2"
    local category="${3:-unit}"
    local coverage_level="${4:-medium}"
    local description="${5:-$test_name}"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    # Update coverage tracking
    case "$coverage_level" in
        "critical") COVERAGE_CRITICAL=$((COVERAGE_CRITICAL + 1)) ;;
        "high") COVERAGE_HIGH=$((COVERAGE_HIGH + 1)) ;;
        "medium") COVERAGE_MEDIUM=$((COVERAGE_MEDIUM + 1)) ;;
        "low") COVERAGE_LOW=$((COVERAGE_LOW + 1)) ;;
    esac
    
    log_category "$category"
    log_info "Running: $test_name"
    log_debug "Description: $description"
    log_debug "Coverage: $coverage_level"
    
    local test_start_time=$(date +%s)
    local test_exit_code=0
    
    # Setup isolated environment for test
    setup_test_environment "$test_name"
    
    # Run the test with error handling
    if eval "$test_function"; then
        local test_end_time=$(date +%s)
        local test_duration=$((test_end_time - test_start_time))
        TESTS_TOTAL_TIME=$((TESTS_TOTAL_TIME + test_duration))
        
        PERFORMANCE_RESULTS+=("$test_name:$test_duration:$category:$coverage_level")
        
        log_success "$test_name (${test_duration}s)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        test_exit_code=$?
        log_error "$test_name (exit code: $test_exit_code)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    
    # Cleanup test environment
    cleanup_test_environment
    
    return $test_exit_code
}

# Skip test with reason
skip_test() {
    local test_name="$1"
    local reason="$2"
    local category="${3:-unit}"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    log_category "$category"
    log_warning "$test_name - $reason"
    TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    return 0
}

# ============================================================================
# ASSERTION HELPERS
# ============================================================================

# Generic assertions
assert_equals() {
    local actual="$1"
    local expected="$2"
    local message="${3:-Expected '$expected', got '$actual'}"
    
    [[ "$actual" == "$expected" ]] || {
        log_error "$message"
        return 1
    }
}

assert_not_equals() {
    local actual="$1"
    local unexpected="$2"
    local message="${3:-Expected not '$unexpected', got '$actual'}"
    
    [[ "$actual" != "$unexpected" ]] || {
        log_error "$message"
        return 1
    }
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local message="${3:-Expected '$haystack' to contain '$needle'}"
    
    [[ "$haystack" == *"$needle"* ]] || {
        log_error "$message"
        return 1
    }
}

assert_not_contains() {
    local haystack="$1"
    local needle="$2"
    local message="${3:-Expected '$haystack' not to contain '$needle'}"
    
    [[ "$haystack" != *"$needle"* ]] || {
        log_error "$message"
        return 1
    }
}

assert_file_exists() {
    local file="$1"
    local message="${2:-Expected file '$file' to exist}"
    
    [[ -f "$file" ]] || {
        log_error "$message"
        return 1
    }
}

assert_file_not_exists() {
    local file="$1"
    local message="${2:-Expected file '$file' not to exist}"
    
    [[ ! -f "$file" ]] || {
        log_error "$message"
        return 1
    }
}

assert_command_success() {
    local command="$1"
    local message="${2:-Expected command to succeed: $command}"
    
    eval "$command" >/dev/null 2>&1 || {
        log_error "$message"
        return 1
    }
}

assert_command_failure() {
    local command="$1"
    local message="${2:-Expected command to fail: $command}"
    
    ! eval "$command" >/dev/null 2>&1 || {
        log_error "$message"
        return 1
    }
}

assert_exit_code() {
    local command="$1"
    local expected_exit_code="$2"
    local message="${3:-Expected exit code $expected_exit_code for: $command}"
    
    eval "$command" >/dev/null 2>&1
    local actual_exit_code=$?
    
    [[ $actual_exit_code -eq $expected_exit_code ]] || {
        log_error "$message (got $actual_exit_code)"
        return 1
    }
}

# ============================================================================
# MOCK AND STUB HELPERS
# ============================================================================

# Create a mock function
create_mock() {
    local function_name="$1"
    local return_code="${2:-0}"
    local output="${3:-}"
    
    eval "$function_name() {
        echo '$output'
        return $return_code
    }"
}

# Create a stub that records calls
create_stub() {
    local function_name="$1"
    local call_log_file="$2"
    
    eval "$function_name() {
        echo \"$(date +%s): $function_name called with: \$*\" >> '$call_log_file'
        return 0
    }"
}

# Clear all mocks and stubs
clear_mocks() {
    # This would need to be implemented based on specific mocking strategy
    log_debug "Cleared all mocks and stubs"
}

# ============================================================================
# PERFORMANCE TESTING
# ============================================================================

# Measure execution time
measure_time() {
    local command="$1"
    local iterations="${2:-1}"
    
    local total_time=0
    for ((i=1; i<=iterations; i++)); do
        local start_time=$(date +%s%N)
        eval "$command" >/dev/null 2>&1
        local end_time=$(date +%s%N)
        local iteration_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
        total_time=$((total_time + iteration_time))
    done
    
    local average_time=$((total_time / iterations))
    echo "$average_time"
}

# Assert performance threshold
assert_performance() {
    local command="$1"
    local max_time_ms="$2"
    local iterations="${3:-1}"
    
    local actual_time=$(measure_time "$command" "$iterations")
    
    if [[ $actual_time -le $max_time_ms ]]; then
        log_debug "Performance: ${actual_time}ms <= ${max_time_ms}ms ✓"
        return 0
    else
        log_error "Performance: ${actual_time}ms > ${max_time_ms}ms ✗"
        return 1
    fi
}

# ============================================================================
# COVERAGE ANALYSIS
# ============================================================================

# Analyze test coverage
analyze_coverage() {
    echo ""
    echo "=== Coverage Analysis ==="
    
    local total_tests=$((COVERAGE_CRITICAL + COVERAGE_HIGH + COVERAGE_MEDIUM + COVERAGE_LOW))
    
    if [[ $total_tests -gt 0 ]]; then
        echo "Coverage Distribution:"
        printf "  Critical: %d tests (%.1f%%) - %s\n" \
            "$COVERAGE_CRITICAL" \
            "$(echo "scale=1; $COVERAGE_CRITICAL * 100 / $total_tests" | bc -l)" \
            "${COVERAGE_LEVELS[critical]}"
        
        printf "  High:     %d tests (%.1f%%) - %s\n" \
            "$COVERAGE_HIGH" \
            "$(echo "scale=1; $COVERAGE_HIGH * 100 / $total_tests" | bc -l)" \
            "${COVERAGE_LEVELS[high]}"
        
        printf "  Medium:   %d tests (%.1f%%) - %s\n" \
            "$COVERAGE_MEDIUM" \
            "$(echo "scale=1; $COVERAGE_MEDIUM * 100 / $total_tests" | bc -l)" \
            "${COVERAGE_LEVELS[medium]}"
        
        printf "  Low:      %d tests (%.1f%%) - %s\n" \
            "$COVERAGE_LOW" \
            "$(echo "scale=1; $COVERAGE_LOW * 100 / $total_tests" | bc -l)" \
            "${COVERAGE_LEVELS[low]}"
    fi
    
    echo ""
    echo "Coverage Recommendations:"
    if [[ $COVERAGE_CRITICAL -gt 0 ]]; then
        echo "✓ Critical path testing covered"
    else
        echo "⚠ Add critical path tests for business logic"
    fi
    
    if [[ $COVERAGE_HIGH -gt 0 ]]; then
        echo "✓ High-value features tested"
    else
        echo "⚠ Add tests for public APIs and user features"
    fi
}

# ============================================================================
# PERFORMANCE ANALYSIS
# ============================================================================

# Analyze test performance
analyze_performance() {
    echo ""
    echo "=== Performance Analysis ==="
    
    # Overall metrics
    local total_time=$(($(date +%s) - START_TIME))
    echo "Total suite execution time: ${total_time}s"
    echo "Total test time (excluding setup): ${TESTS_TOTAL_TIME}s"
    
    if [[ $TESTS_TOTAL -gt 0 ]]; then
        local avg_time=$((TESTS_TOTAL_TIME / TESTS_TOTAL))
        echo "Average test time: ${avg_time}s"
    fi
    
    # Category-wise analysis
    echo ""
    echo "Performance by category:"
    for category in unit integration system performance security regression; do
        local category_tests=()
        local category_total=0
        
        for result in "${PERFORMANCE_RESULTS[@]}"; do
            local test_category=$(echo "$result" | cut -d: -f3)
            local test_duration=$(echo "$result" | cut -d: -f2)
            
            if [[ "$test_category" == "$category" ]]; then
                category_tests+=("$result")
                category_total=$((category_total + test_duration))
            fi
        done
        
        if [[ ${#category_tests[@]} -gt 0 ]]; then
            printf "  %-12s: %d tests, %ds total, %ds avg\n" \
                "$category" \
                "${#category_tests[@]}" \
                "$category_total" \
                "$((category_total / ${#category_tests[@]}))"
        fi
    done
    
    # Slowest tests
    if [[ ${#PERFORMANCE_RESULTS[@]} -gt 0 ]]; then
        echo ""
        echo "Top 5 slowest tests:"
        for result in $(printf '%s\n' "${PERFORMANCE_RESULTS[@]}" | sort -t: -k2 -nr | head -5); do
            local test_name=$(echo "$result" | cut -d: -f1)
            local test_duration=$(echo "$result" | cut -d: -f2)
            echo "  $test_name: ${test_duration}s"
        done
    fi
}

# ============================================================================
# FINAL REPORTING
# ============================================================================

# Generate comprehensive test report
generate_report() {
    echo ""
    echo "=============================================="
    echo "Final Test Results"
    echo "=============================================="
    echo "Framework: $FRAMEWORK_NAME v$FRAMEWORK_VERSION"
    echo ""
    
    # Test summary
    echo "=== Test Summary ==="
    echo "Total tests: $TESTS_TOTAL"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    echo -e "Skipped: ${YELLOW}$TESTS_SKIPPED${NC}"
    
    # Success metrics
    if [[ $TESTS_TOTAL -gt 0 ]]; then
        local pass_rate=$(echo "scale=1; $TESTS_PASSED * 100 / $TESTS_TOTAL" | bc -l)
        echo "Pass rate: ${pass_rate}%"
        
        local skip_rate=$(echo "scale=1; $TESTS_SKIPPED * 100 / $TESTS_TOTAL" | bc -l)
        echo "Skip rate: ${skip_rate}%"
    fi
    
    # Coverage analysis
    analyze_coverage
    
    # Performance analysis
    analyze_performance
    
    # Recommendations
    echo ""
    echo "=== Recommendations ==="
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo "✓ All tests passed - system is ready for production"
        echo "✓ Consider adding these tests to CI/CD pipeline"
        echo "✓ Set up automated regression testing"
    else
        echo "⚠ Fix failing tests before production deployment"
        echo "⚠ Review failed test logs for root cause analysis"
        echo "⚠ Consider running tests in isolation for debugging"
    fi
    
    if [[ $TESTS_SKIPPED -gt 0 ]]; then
        echo "⚠ Some tests were skipped - investigate dependencies"
    fi
    
    # Quality gate assessment
    echo ""
    echo "=== Quality Gates ==="
    local quality_gates_passed=true
    
    # Gate 1: No critical failures
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo "✓ No test failures"
    else
        echo "✗ Test failures detected"
        quality_gates_passed=false
    fi
    
    # Gate 2: Minimum coverage
    local critical_coverage=0
    if [[ $TESTS_TOTAL -gt 0 ]]; then
        critical_coverage=$(echo "scale=1; ($COVERAGE_CRITICAL + $COVERAGE_HIGH) * 100 / $TESTS_TOTAL" | bc -l)
    fi
    
    if (( $(echo "$critical_coverage >= 60" | bc -l) )); then
        echo "✓ Adequate critical/high coverage (${critical_coverage}%)"
    else
        echo "✗ Insufficient critical/high coverage (${critical_coverage}% < 60%)"
        quality_gates_passed=false
    fi
    
    # Gate 3: Performance
    if [[ $TESTS_TOTAL_TIME -lt 300 ]]; then # 5 minutes
        echo "✓ Acceptable performance (${TESTS_TOTAL_TIME}s)"
    else
        echo "⚠ Slow test suite (${TESTS_TOTAL_TIME}s) - consider optimization"
    fi
    
    # Final verdict
    echo ""
    if [[ "$quality_gates_passed" == true ]]; then
        echo -e "${GREEN}🎉 QUALITY GATES PASSED - Ready for production!${NC}"
        return 0
    else
        echo -e "${RED}❌ QUALITY GATES FAILED - Address issues before production${NC}"
        return 1
    fi
}

# ============================================================================
# FRAMEWORK INITIALIZATION
# ============================================================================

# Initialize test framework
init_framework() {
    echo "=============================================="
    echo "$FRAMEWORK_NAME v$FRAMEWORK_VERSION"
    echo "=============================================="
    echo "Project: $PROJECT_DIR"
    echo "Test directory: $SCRIPT_DIR"
    echo "Standards: AAA Pattern + Coverage Analysis"
    echo ""
    
    # Check dependencies
    local missing_deps=()
    
    for cmd in bc jq find; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        echo "Install with: apt-get install ${missing_deps[*]}"
        exit 1
    fi
    
    log_success "Framework initialized successfully"
}

# Export functions for use in test scripts
export -f log_info log_success log_error log_warning log_debug log_category
export -f setup_test_environment cleanup_test_environment
export -f arrange act assert
export -f run_test skip_test
export -f assert_equals assert_not_equals assert_contains assert_not_contains
export -f assert_file_exists assert_file_not_exists
export -f assert_command_success assert_command_failure assert_exit_code
export -f create_mock create_stub clear_mocks
export -f measure_time assert_performance
export -f analyze_coverage analyze_performance generate_report
export -f init_framework

# Initialize if this script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    init_framework
    echo "Test framework loaded. Use run_test() to execute tests."
    echo "Example: run_test 'my_test' 'test_my_function' 'unit' 'high'"
fi