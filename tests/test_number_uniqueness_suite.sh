#!/bin/bash

# Number Uniqueness Test Suite Runner
# Auto-54t: Master test runner for all number uniqueness verification tests
# Combines basic tests, integration tests, concurrent tests, and comprehensive tests

set -e

SCRIPT_NAME="test_number_uniqueness_suite"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# List of all number uniqueness test scripts
ALL_NUMBER_TESTS=(
    "tests/test_basic_number_uniqueness.sh"
    "tests/test_number_manager_integration.sh" 
    "tests/number_tracking/test_concurrent_assignment.sh"
    "tests/test_comprehensive_number_uniqueness.sh"
)

log "INFO" "Starting Number Uniqueness Test Suite - Auto-54t"
log "INFO" "This comprehensive test suite verifies number uniqueness in all scenarios"

# Function to run a single test script
run_single_test() {
    local test_script="$1"
    local test_name
    test_name=$(basename "$test_script" .sh)
    
    echo ""
    echo "🧪 Running: $test_name"
    echo "=================================================="
    
    local start_time=$(date +%s)
    
    if "$PROJECT_DIR/$test_script" run; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        echo "✅ $test_name PASSED (took ${duration}s)"
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        echo "❌ $test_name FAILED (took ${duration}s)"
        return 1
    fi
}

# Function to run all tests with detailed reporting
run_all_number_tests() {
    local total_tests=${#ALL_NUMBER_TESTS[@]}
    local passed_tests=0
    local failed_tests=()
    local total_start_time=$(date +%s)
    
    echo ""
    echo "🎯 Number Uniqueness Test Suite - Auto-54t"
    echo "=================================================="
    echo "Running $total_tests test scripts covering:"
    echo "  • Basic number allocation and uniqueness tracking"
    echo "  • Integration scenarios and error handling"
    echo "  • Concurrent assignment and race conditions"
    echo "  • Comprehensive verification with edge cases"
    echo "  • Performance testing and regression validation"
    echo ""
    
    # Run each test script
    for test_script in "${ALL_NUMBER_TESTS[@]}"; do
        if run_single_test "$test_script"; then
            passed_tests=$((passed_tests + 1))
        else
            failed_tests+=("$test_script")
        fi
    done
    
    local total_end_time=$(date +%s)
    local total_duration=$((total_end_time - total_start_time))
    
    # Final summary
    echo ""
    echo "=================================================="
    echo "📊 FINAL TEST SUITE RESULTS"
    echo "=================================================="
    echo "Total Test Scripts: $total_tests"
    echo "Passed: $passed_tests"
    echo "Failed: $((${#failed_tests[@]}))"
    echo "Total Duration: ${total_duration}s"
    echo ""
    
    if [ ${#failed_tests[@]} -gt 0 ]; then
        echo "❌ FAILED TEST SCRIPTS:"
        for failed_test in "${failed_tests[@]}"; do
            echo "   • $failed_test"
        done
        echo ""
        log "ERROR" "Number uniqueness test suite completed with failures"
        return 1
    else
        echo "🎉 ALL TESTS PASSED!"
        echo ""
        echo "✨ Number Uniqueness System Verification Complete:"
        echo "   ✓ Basic number allocation and tracking verified"
        echo "   ✓ Integration scenarios tested and working"
        echo "   ✓ Concurrent operations handling validated"
        echo "   ✓ Edge cases and regression tests passed"
        echo "   ✓ Performance benchmarks established"
        echo "   ✓ Original bug (number reuse) fixed and verified"
        echo ""
        log "SUCCESS" "All number uniqueness tests passed - Auto-54t completed successfully!"
        return 0
    fi
}

# Function to run specific test categories
run_test_category() {
    local category="$1"
    local category_tests=()
    
    case "$category" in
        "basic")
            category_tests=("tests/test_basic_number_uniqueness.sh")
            ;;
        "integration")
            category_tests=("tests/test_number_manager_integration.sh")
            ;;
        "concurrent")
            category_tests=("tests/number_tracking/test_concurrent_assignment.sh")
            ;;
        "comprehensive")
            category_tests=("tests/test_comprehensive_number_uniqueness.sh")
            ;;
        "all")
            run_all_number_tests
            return $?
            ;;
        *)
            echo "Error: Unknown category '$category'"
            echo "Available categories: basic, integration, concurrent, comprehensive, all"
            return 1
            ;;
    esac
    
    echo ""
    echo "🎯 Running '$category' test category"
    echo "=================================================="
    
    local passed=0
    local failed=0
    
    for test_script in "${category_tests[@]}"; do
        if run_single_test "$test_script"; then
            passed=$((passed + 1))
        else
            failed=$((failed + 1))
        fi
    done
    
    echo ""
    echo "Category '$category' results: $passed passed, $failed failed"
    
    if [ $failed -gt 0 ]; then
        return 1
    else
        return 0
    fi
}

# Function to show test suite information
show_suite_info() {
    echo "Number Uniqueness Test Suite - Auto-54t"
    echo "======================================"
    echo ""
    echo "Available Test Scripts:"
    for i in "${!ALL_NUMBER_TESTS[@]}"; do
        local num=$((i + 1))
        echo "  $num. ${ALL_NUMBER_TESTS[$i]}"
    done
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  run              - Run all number uniqueness tests"
    echo "  basic            - Run basic number allocation tests"
    echo "  integration      - Run integration scenario tests"
    echo "  concurrent       - Run concurrent assignment tests"
    echo "  comprehensive    - Run comprehensive verification tests"
    echo "  info             - Show this information"
    echo ""
    echo "Test Categories:"
    echo "  • Basic: Core number allocation and uniqueness logic"
    echo "  • Integration: System integration and error handling"
    echo "  • Concurrent: Race conditions and locking mechanisms"
    echo "  • Comprehensive: All scenarios including edge cases and performance"
    echo ""
    echo "Auto-54t: Add tests to verify number uniqueness works correctly"
}

# Main execution logic
case "${1:-run}" in
    "run"|"all")
        run_all_number_tests
        exit $?
        ;;
    "basic")
        run_test_category "basic"
        exit $?
        ;;
    "integration")
        run_test_category "integration"
        exit $?
        ;;
    "concurrent")
        run_test_category "concurrent"
        exit $?
        ;;
    "comprehensive")
        run_test_category "comprehensive"
        exit $?
        ;;
    "info")
        show_suite_info
        exit 0
        ;;
    *)
        echo "Error: Unknown command '$1'"
        echo ""
        show_suite_info
        exit 1
        ;;
esac