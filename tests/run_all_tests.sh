#!/bin/bash

# Master Test Runner for Auto-slopp
# This script provides a single entry point for running all test suites
# Organizes tests by category and provides comprehensive reporting

set -e

# Directory setup
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

# Test suites available
declare -A TEST_SUITES=(
    ["basic"]="Basic syntax and executability tests"
    ["enhanced"]="Enhanced framework tests with coverage analysis"
    ["comprehensive"]="Comprehensive tests for all scripts"
    ["number-tracking"]="Number manager and tracking tests"
    ["telegram"]="Telegram integration tests"
    ["planner"]="Planner script tests"
    ["validation"]="Validation accuracy tests"
    ["backup"]="Backup and recovery tests"
    ["performance"]="Performance and stress tests"
    ["all"]="Run all test suites"
)

# Default configuration
QUICK_MODE=false
VERBOSE=false
COVERAGE_TARGET=85
FAIL_FAST=false

# Test results tracking
TOTAL_SUITES=0
PASSED_SUITES=0
FAILED_SUITES=0
TOTAL_TESTS=0
TOTAL_PASSED=0
TOTAL_FAILED=0

# Logging functions
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
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_header() {
    echo ""
    echo -e "${PURPLE}==============================================${NC}"
    echo -e "${PURPLE} $1${NC}"
    echo -e "${PURPLE}==============================================${NC}"
}

# Run a specific test suite
run_test_suite() {
    local suite_name="$1"
    local suite_description="${TEST_SUITES[$1]}"
    
    log_header "Running $suite_name Suite"
    echo "Description: $suite_description"
    echo ""
    
    local suite_start_time=$(date +%s)
    local suite_exit_code=0
    
    # Construct command based on suite type
    local cmd=""
    case "$suite_name" in
        "basic")
            cmd="bash '$SCRIPT_DIR/test_suite.sh'"
            if [[ "$QUICK_MODE" == true ]]; then
                cmd="$cmd --no-make --no-logging --no-merge --no-number-tracking"
            fi
            ;;
        "enhanced")
            cmd="bash '$SCRIPT_DIR/test_suite_enhanced.sh'"
            if [[ "$QUICK_MODE" == true ]]; then
                cmd="$cmd --quick"
            else
                cmd="$cmd --category unit --category integration"
            fi
            ;;
        "comprehensive")
            cmd="bash '$SCRIPT_DIR/test_comprehensive_suite.sh'"
            if [[ "$QUICK_MODE" == true ]]; then
                cmd="$cmd --quick --category core"
            else
                cmd="$cmd --coverage $COVERAGE_TARGET"
            fi
            ;;
        "number-tracking")
            if [[ -d "$SCRIPT_DIR/number_tracking" ]]; then
                cmd="bash '$SCRIPT_DIR/number_tracking/test_suite_runner.sh'"
                if [[ "$QUICK_MODE" == true ]]; then
                    cmd="$cmd --quick"
                fi
            else
                log_warning "Number tracking tests not found, skipping"
                return 0
            fi
            ;;
        "telegram")
            # Run all telegram-related tests
            local telegram_tests=(
                "$SCRIPT_DIR/test_telegram_config.sh"
                "$SCRIPT_DIR/test_telegram_security_basic.sh"
                "$SCRIPT_DIR/test_telegram_security_enhanced.sh"
                "$SCRIPT_DIR/test_telegram_formatter_simple.sh"
                "$SCRIPT_DIR/test_telegram_config_simple.sh"
            )
            
            local test_count=0
            local passed_count=0
            
            for test_file in "${telegram_tests[@]}"; do
                if [[ -f "$test_file" ]]; then
                    test_count=$((test_count + 1))
                    log_info "Running $(basename "$test_file")"
                    
                    if bash "$test_file" >/dev/null 2>&1; then
                        log_success "$(basename "$test_file")"
                        passed_count=$((passed_count + 1))
                    else
                        log_error "$(basename "$test_file") failed"
                        if [[ "$FAIL_FAST" == true ]]; then
                            suite_exit_code=1
                            break
                        fi
                    fi
                fi
            done
            
            echo "Telegram tests: $passed_count/$test_count passed"
            [[ $passed_count -eq $test_count ]] || suite_exit_code=1
            ;;
        "planner")
            # Run planner-specific tests
            local planner_tests=(
                "$SCRIPT_DIR/test_planner_integration.sh"
                "$SCRIPT_DIR/test_planner_error_handling.sh"
                "$SCRIPT_DIR/test_planner_context.sh"
                "$SCRIPT_DIR/test_planner_multiple_repos.sh"
                "$SCRIPT_DIR/test_planner_numbering.sh"
            )
            
            local test_count=0
            local passed_count=0
            
            for test_file in "${planner_tests[@]}"; do
                if [[ -f "$test_file" ]]; then
                    test_count=$((test_count + 1))
                    log_info "Running $(basename "$test_file")"
                    
                    if bash "$test_file" >/dev/null 2>&1; then
                        log_success "$(basename "$test_file")"
                        passed_count=$((passed_count + 1))
                    else
                        log_error "$(basename "$test_file") failed"
                        if [[ "$FAIL_FAST" == true ]]; then
                            suite_exit_code=1
                            break
                        fi
                    fi
                fi
            done
            
            echo "Planner tests: $passed_count/$test_count passed"
            [[ $passed_count -eq $test_count ]] || suite_exit_code=1
            ;;
        "validation")
            if [[ -f "$SCRIPT_DIR/test_validation_accuracy.sh" ]]; then
                cmd="bash '$SCRIPT_DIR/test_validation_accuracy.sh'"
            else
                log_warning "Validation tests not found, skipping"
                return 0
            fi
            ;;
        "backup")
            # Run backup-related tests
            local backup_tests=(
                "$SCRIPT_DIR/test_backup_creation.sh"
                "$SCRIPT_DIR/test_backup_integrity.sh"
                "$SCRIPT_DIR/test_backup_rotation.sh"
                "$SCRIPT_DIR/test_recovery_mechanisms.sh"
                "$SCRIPT_DIR/test_crash_recovery.sh"
            )
            
            local test_count=0
            local passed_count=0
            
            for test_file in "${backup_tests[@]}"; do
                if [[ -f "$test_file" ]]; then
                    test_count=$((test_count + 1))
                    log_info "Running $(basename "$test_file")"
                    
                    if bash "$test_file" >/dev/null 2>&1; then
                        log_success "$(basename "$test_file")"
                        passed_count=$((passed_count + 1))
                    else
                        log_error "$(basename "$test_file") failed"
                        if [[ "$FAIL_FAST" == true ]]; then
                            suite_exit_code=1
                            break
                        fi
                    fi
                fi
            done
            
            echo "Backup tests: $passed_count/$test_count passed"
            [[ $passed_count -eq $test_count ]] || suite_exit_code=1
            ;;
        "performance")
            # Run performance-related tests
            local perf_tests=(
                "$SCRIPT_DIR/test_validation_performance.sh"
                "$SCRIPT_DIR/test_timeout_functionality.sh"
                "$SCRIPT_DIR/test_concurrent_stress.sh"
                "$SCRIPT_DIR/test_race_condition_detection.sh"
            )
            
            local test_count=0
            local passed_count=0
            
            for test_file in "${perf_tests[@]}"; do
                if [[ -f "$test_file" ]]; then
                    test_count=$((test_count + 1))
                    log_info "Running $(basename "$test_file")"
                    
                    if bash "$test_file" >/dev/null 2>&1; then
                        log_success "$(basename "$test_file")"
                        passed_count=$((passed_count + 1))
                    else
                        log_error "$(basename "$test_file") failed"
                        if [[ "$FAIL_FAST" == true ]]; then
                            suite_exit_code=1
                            break
                        fi
                    fi
                fi
            done
            
            echo "Performance tests: $passed_count/$test_count passed"
            [[ $passed_count -eq $test_count ]] || suite_exit_code=1
            ;;
        *)
            log_error "Unknown test suite: $suite_name"
            return 1
            ;;
    esac
    
    # Execute the command if set
    if [[ -n "$cmd" ]]; then
        log_info "Executing: $cmd"
        
        if [[ "$VERBOSE" == true ]]; then
            eval "$cmd"
            suite_exit_code=$?
        else
            # Capture output and extract key metrics
            local output
            output=$(eval "$cmd" 2>&1 || true)
            suite_exit_code=$?
            
            # Extract test counts if available
            if [[ "$output" =~ Total\ tests:\ ([0-9]+) ]]; then
                local suite_total=${BASH_REMATCH[1]}
                TOTAL_TESTS=$((TOTAL_TESTS + suite_total))
                
                if [[ "$output" =~ Passed:\ ([0-9]+) ]]; then
                    local suite_passed=${BASH_REMATCH[1]}
                    TOTAL_PASSED=$((TOTAL_PASSED + suite_passed))
                fi
                
                if [[ "$output" =~ Failed:\ ([0-9]+) ]]; then
                    local suite_failed=${BASH_REMATCH[1]}
                    TOTAL_FAILED=$((TOTAL_FAILED + suite_failed))
                fi
            fi
            
            # Show key output lines
            echo "$output" | grep -E "(PASS|FAIL|Total tests|Passed:|Failed:|Pass rate|Coverage)" || true
        fi
    fi
    
    local suite_end_time=$(date +%s)
    local suite_duration=$((suite_end_time - suite_start_time))
    
    TOTAL_SUITES=$((TOTAL_SUITES + 1))
    
    if [[ $suite_exit_code -eq 0 ]]; then
        PASSED_SUITES=$((PASSED_SUITES + 1))
        log_success "$suite_name suite passed (${suite_duration}s)"
    else
        FAILED_SUITES=$((FAILED_SUITES + 1))
        log_error "$suite_name suite failed (${suite_duration}s)"
        if [[ "$FAIL_FAST" == true ]]; then
            exit 1
        fi
    fi
    
    echo ""
}

# Generate final report
generate_final_report() {
    log_header "Final Test Report"
    
    echo "Suite Summary:"
    echo "  Total suites: $TOTAL_SUITES"
    echo -e "  Passed suites: ${GREEN}$PASSED_SUITES${NC}"
    echo -e "  Failed suites: ${RED}$FAILED_SUITES${NC}"
    
    if [[ $TOTAL_SUITES -gt 0 ]]; then
        local suite_pass_rate=$(echo "scale=1; $PASSED_SUITES * 100 / $TOTAL_SUITES" | bc -l)
        echo "  Suite pass rate: ${suite_pass_rate}%"
    fi
    
    echo ""
    echo "Test Summary:"
    echo "  Total tests: $TOTAL_TESTS"
    echo -e "  Passed: ${GREEN}$TOTAL_PASSED${NC}"
    echo -e "  Failed: ${RED}$TOTAL_FAILED${NC}"
    
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        local test_pass_rate=$(echo "scale=1; $TOTAL_PASSED * 100 / $TOTAL_TESTS" | bc -l)
        echo "  Test pass rate: ${test_pass_rate}%"
        
        if (( $(echo "$test_pass_rate >= 90" | bc -l) )); then
            echo -e "${GREEN}✓ Excellent test coverage${NC}"
        elif (( $(echo "$test_pass_rate >= 80" | bc -l) )); then
            echo -e "${YELLOW}⚠ Good test coverage${NC}"
        else
            echo -e "${RED}✗ Poor test coverage - needs improvement${NC}"
        fi
    fi
    
    echo ""
    
    # Quality gates
    local quality_gates_passed=true
    
    if [[ $FAILED_SUITES -gt 0 ]]; then
        echo -e "${RED}✗ Some test suites failed${NC}"
        quality_gates_passed=false
    fi
    
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        local pass_rate=$(echo "scale=1; $TOTAL_PASSED * 100 / $TOTAL_TESTS" | bc -l)
        if (( $(echo "$pass_rate < $COVERAGE_TARGET" | bc -l) )); then
            echo -e "${RED}✗ Coverage target of ${COVERAGE_TARGET}% not met (actual: ${pass_rate}%)${NC}"
            quality_gates_passed=false
        fi
    fi
    
    if [[ "$quality_gates_passed" == true ]]; then
        echo -e "${GREEN}🎉 ALL QUALITY GATES PASSED${NC}"
        echo -e "${GREEN}✓ System is ready for production!${NC}"
        return 0
    else
        echo -e "${RED}❌ QUALITY GATES FAILED${NC}"
        echo -e "${RED}⚠ Address issues before production deployment${NC}"
        return 1
    fi
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                QUICK_MODE=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --fail-fast)
                FAIL_FAST=true
                shift
                ;;
            --coverage)
                COVERAGE_TARGET="$2"
                shift 2
                ;;
            --suites)
                shift
                SELECTED_SUITES=("$@")
                break
                ;;
            --help|-h)
                echo "Master Test Runner for Auto-slopp"
                echo ""
                echo "Usage: $0 [options] [suite...]"
                echo ""
                echo "Options:"
                echo "  --quick              Run only essential tests"
                echo "  --verbose            Show full test output"
                echo "  --fail-fast          Stop on first test failure"
                echo "  --coverage PERCENT    Set coverage target (default: 85)"
                echo "  --suites SUITE1...   Run specific suites only"
                echo "  --help, -h           Show this help message"
                echo ""
                echo "Available Test Suites:"
                for suite in "${!TEST_SUITES[@]}"; do
                    printf "  %-15s %s\n" "$suite" "${TEST_SUITES[$suite]}"
                done
                echo ""
                echo "Examples:"
                echo "  $0                           # Run all test suites"
                echo "  $0 --quick basic enhanced      # Run quick basic and enhanced tests"
                echo "  $0 --suites comprehensive   # Run comprehensive tests only"
                echo "  $0 --coverage 90 all          # Run all tests with 90% coverage target"
                echo ""
                exit 0
                ;;
            *)
                # Assume it's a suite name
                SELECTED_SUITES+=("$1")
                shift
                ;;
        esac
    done
}

# Main execution
main() {
    local start_time=$(date +%s)
    
    # Default to running all suites if none specified
    if [[ ${#SELECTED_SUITES[@]} -eq 0 ]]; then
        SELECTED_SUITES=("all")
    fi
    
    log_header "Auto-slopp Test Execution"
    echo "Quick mode: $QUICK_MODE"
    echo "Verbose: $VERBOSE"
    echo "Fail fast: $FAIL_FAST"
    echo "Coverage target: ${COVERAGE_TARGET}%"
    echo "Selected suites: ${SELECTED_SUITES[*]}"
    echo ""
    
    # Execute selected suites
    for suite in "${SELECTED_SUITES[@]}"; do
        if [[ "$suite" == "all" ]]; then
            # Run all suites except 'all' itself
            for all_suite in "${!TEST_SUITES[@]}"; do
                if [[ "$all_suite" != "all" ]]; then
                    run_test_suite "$all_suite"
                fi
            done
            break
        elif [[ -n "${TEST_SUITES[$suite]:-}" ]]; then
            run_test_suite "$suite"
        else
            log_error "Unknown test suite: $suite"
            echo "Available suites: ${!TEST_SUITES[*]}"
            exit 1
        fi
    done
    
    # Generate final report
    generate_final_report
    
    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))
    
    echo "Total execution time: ${total_duration}s"
    echo ""
    
    # Exit with appropriate code
    if [[ $FAILED_SUITES -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Initialize selected suites array
SELECTED_SUITES=()

# Parse arguments
parse_arguments "$@"

# Run main function
main "$@"