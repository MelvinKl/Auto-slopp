#!/bin/bash

# Integration Test Runner for Auto-slopp
# Simple runner for integration tests with optional debugging and reporting
# Provides easy interface for running integration test suites

set -e

# Set script name for logging identification
SCRIPT_NAME="integration-test-runner"

# Get directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
source "$PROJECT_DIR/scripts/utils.sh"

# ============================================================================
# COMMAND LINE PARSING
# ============================================================================

# Show usage information
show_usage() {
    cat << EOF
USAGE: $(basename "$0") [OPTIONS] [TEST_TYPE]

Integration Test Runner for Auto-slopp system

TEST_TYPES:
    cleanup-automation    Run cleanup automation engine integration tests
    all                Run all available integration tests
    help, -h, --help   Show this help message

OPTIONS:
    -v, --verbose       Enable verbose output
    -d, --debug         Enable debug mode
    -q, --quiet         Suppress non-error output
    -f, --force         Run tests even if pre-checks fail
    -r, --report        Generate detailed report
    -c, --clean         Clean up test environments before/after tests
    --no-cleanup        Don't clean up test environments (for debugging)

EXAMPLES:
    $0 cleanup-automation                    # Run cleanup automation tests
    $0 cleanup-automation --verbose --report   # Run with verbose output and reporting
    $0 all --debug                          # Run all tests with debug mode
    $0 cleanup-automation --no-cleanup       # Run tests but keep test environment

EXIT CODES:
    0    All tests passed
    1    Some tests failed
    2    Invalid arguments or usage error
    3    Prerequisites not met

EOF
}

# Parse command line arguments
VERBOSE=false
DEBUG=false
QUIET=false
FORCE=false
GENERATE_REPORT=false
CLEANUP=true
TEST_TYPE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        cleanup-automation)
            TEST_TYPE="cleanup-automation"
            shift
            ;;
        all)
            TEST_TYPE="all"
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -d|--debug)
            DEBUG=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -r|--report)
            GENERATE_REPORT=true
            shift
            ;;
        -c|--clean)
            CLEANUP=true
            shift
            ;;
        --no-cleanup)
            CLEANUP=false
            shift
            ;;
        -h|--help|help)
            show_usage
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option or test type: $1"
            echo "Use --help for usage information"
            exit 2
            ;;
    esac
done

# Validate arguments
if [[ -z "$TEST_TYPE" ]]; then
    echo "ERROR: Must specify test type"
    echo "Use --help for usage information"
    exit 2
fi

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# Log function based on settings
runner_log() {
    local level="$1"
    local message="$2"
    
    if [[ "$QUIET" == "true" && "$level" != "ERROR" ]]; then
        return
    fi
    
    if [[ "$DEBUG" == "true" ]]; then
        log "$level" "$message"
    elif [[ "$VERBOSE" == "true" || "$level" == "ERROR" || "$level" == "WARNING" ]]; then
        log "$level" "$message"
    fi
}

# Check prerequisites
check_prerequisites() {
    runner_log "INFO" "Checking prerequisites"
    
    local missing_prereqs=()
    
    # Check if in project directory
    if [[ ! -f "$PROJECT_DIR/config.yaml" ]]; then
        missing_prereqs+=("config.yaml not found in project root")
    fi
    
    # Check required scripts
    local required_scripts=(
        "scripts/cleanup-automation-engine.sh"
        "scripts/utils.sh"
        "scripts/yaml_config.sh"
        "tests/test_framework.sh"
    )
    
    for script in "${required_scripts[@]}"; do
        if [[ ! -f "$PROJECT_DIR/$script" ]]; then
            missing_prereqs+=("$script not found")
        fi
    done
    
    # Check if scripts are executable
    local executable_scripts=(
        "scripts/cleanup-automation-engine.sh"
        "tests/test_cleanup_automation_integration.sh"
    )
    
    for script in "${executable_scripts[@]}"; do
        if [[ -f "$PROJECT_DIR/$script" && ! -x "$PROJECT_DIR/$script" ]]; then
            missing_prereqs+=("$script is not executable")
        fi
    done
    
    # Report missing prerequisites
    if [[ ${#missing_prereqs[@]} -gt 0 ]]; then
        runner_log "ERROR" "Missing prerequisites:"
        for prereq in "${missing_prereqs[@]}"; do
            runner_log "ERROR" "  - $prereq"
        done
        
        if [[ "$FORCE" != "true" ]]; then
            runner_log "ERROR" "Use --force to run anyway (not recommended)"
            exit 3
        else
            runner_log "WARNING" "Proceeding despite missing prerequisites (force mode)"
        fi
    fi
    
    runner_log "SUCCESS" "Prerequisites check completed"
}

# Clean up test environments
cleanup_test_environments() {
    if [[ "$CLEANUP" != "true" ]]; then
        runner_log "INFO" "Skipping cleanup (no-cleanup mode)"
        return 0
    fi
    
    runner_log "INFO" "Cleaning up test environments"
    
    # Remove integration test directories
    for dir in /tmp/cleanup_engine_integration_*; do
        if [[ -d "$dir" ]]; then
            runner_log "DEBUG" "Removing $dir"
            rm -rf "$dir"
        fi
    done
    
    # Remove state files
    for file in /tmp/cleanup_engine_state_test_*; do
        if [[ -f "$file" ]]; then
            runner_log "DEBUG" "Removing $file"
            rm -f "$file"
        fi
    done
    
    # Kill any hanging processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    
    runner_log "SUCCESS" "Test environment cleanup completed"
}

# Generate detailed report
generate_detailed_report() {
    local test_type="$1"
    local exit_code="$2"
    local start_time="$3"
    local end_time="$4"
    
    if [[ "$GENERATE_REPORT" != "true" ]]; then
        return 0
    fi
    
    local report_file="$PROJECT_DIR/tests/integration_test_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# Integration Test Report

## Test Execution Summary

- **Test Type**: $test_type
- **Start Time**: $(date -d "@$start_time" '+%Y-%m-%d %H:%M:%S')
- **End Time**: $(date -d "@$end_time" '+%Y-%m-%d %H:%M:%S')
- **Duration**: $((end_time - start_time)) seconds
- **Exit Code**: $exit_code
- **Result**: $([[ $exit_code -eq 0 ]] && echo "PASSED" || echo "FAILED")

## Test Environment

- **Project Directory**: $PROJECT_DIR
- **Test Directory**: $SCRIPT_DIR
- **Working Directory**: $(pwd)
- **User**: $(whoami)
- **Hostname**: $(hostname)
- **Shell**: $SHELL

## Configuration

- **Verbose Mode**: $VERBOSE
- **Debug Mode**: $DEBUG
- **Quiet Mode**: $QUIET
- **Force Mode**: $FORCE
- **Generate Report**: $GENERATE_REPORT
- **Cleanup**: $CLEANUP

## System Information

- **OS**: $(uname -s)
- **Kernel**: $(uname -r)
- **Architecture**: $(uname -m)
- **Git Version**: $(git --version 2>/dev/null || echo "Not available")
- **Bash Version**: $BASH_VERSION

## Notes

This report was generated automatically by the integration test runner.
For detailed test logs, see the individual test output.

EOF

    runner_log "INFO" "Detailed report generated: $report_file"
}

# ============================================================================
# TEST EXECUTION FUNCTIONS
# ============================================================================

# Run cleanup automation integration tests
run_cleanup_automation_tests() {
    runner_log "INFO" "Running cleanup automation integration tests"
    
    local test_script="$PROJECT_DIR/tests/test_cleanup_automation_integration.sh"
    
    if [[ ! -f "$test_script" ]]; then
        runner_log "ERROR" "Cleanup automation test script not found: $test_script"
        return 1
    fi
    
    # Ensure script is executable
    chmod +x "$test_script"
    
    # Set up environment for tests
    local test_env=""
    if [[ "$DEBUG" == "true" ]]; then
        test_env="DEBUG_MODE=true"
    fi
    
    # Run the tests
    local exit_code=0
    if [[ "$VERBOSE" == "true" || "$DEBUG" == "true" ]]; then
        runner_log "INFO" "Executing: $test_env $test_script"
        eval "$test_env $test_script" || exit_code=$?
    else
        runner_log "INFO" "Executing: $test_script (quiet mode)"
        eval "$test_env $test_script" >/dev/null 2>&1 || exit_code=$?
    fi
    
    return $exit_code
}

# Run all integration tests
run_all_tests() {
    runner_log "INFO" "Running all integration tests"
    
    local overall_exit_code=0
    
    # Run cleanup automation tests
    runner_log "INFO" "--- Running Cleanup Automation Tests ---"
    if ! run_cleanup_automation_tests; then
        overall_exit_code=1
    fi
    
    # Add other test types here when available
    # runner_log "INFO" "--- Running Other Integration Tests ---"
    # if ! run_other_integration_tests; then
    #     overall_exit_code=1
    # fi
    
    return $overall_exit_code
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Main function
main() {
    local start_time=$(date +%s)
    runner_log "INFO" "Starting integration test runner"
    runner_log "INFO" "Test type: $TEST_TYPE"
    
    # Check prerequisites
    check_prerequisites
    
    # Clean up before tests if requested
    if [[ "$CLEANUP" == "true" ]]; then
        cleanup_test_environments
    fi
    
    # Run the specified tests
    local exit_code=0
    case "$TEST_TYPE" in
        cleanup-automation)
            run_cleanup_automation_tests || exit_code=$?
            ;;
        all)
            run_all_tests || exit_code=$?
            ;;
        *)
            runner_log "ERROR" "Unknown test type: $TEST_TYPE"
            exit_code=2
            ;;
    esac
    
    local end_time=$(date +%s)
    
    # Generate report if requested
    generate_detailed_report "$TEST_TYPE" "$exit_code" "$start_time" "$end_time"
    
    # Clean up after tests if requested
    if [[ "$CLEANUP" == "true" ]]; then
        cleanup_test_environments
    fi
    
    # Final summary
    runner_log "INFO" "Integration tests completed with exit code: $exit_code"
    if [[ $exit_code -eq 0 ]]; then
        runner_log "SUCCESS" "All integration tests passed!"
    else
        runner_log "ERROR" "Some integration tests failed!"
    fi
    
    exit $exit_code
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi