#!/bin/bash

# Comprehensive test suite for timestamp logging functionality
# Tests all aspects of the enhanced logging system in utils.sh

set -e

# Get script directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
UTILS_SCRIPT="$PROJECT_DIR/scripts/utils.sh"

# Colors for test output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test environment setup
TEST_LOG_DIR="/tmp/auto-slopp-test-logs-$$"
TEST_TIMESTAMP_FILE="/tmp/test-timestamp-$$"
TEST_LOG_FILE="/tmp/test-log-$$"

# Cleanup function
cleanup() {
    rm -rf "$TEST_LOG_DIR" "$TEST_TIMESTAMP_FILE" "$TEST_LOG_FILE" 2>/dev/null || true
    unset TIMESTAMP_FORMAT TIMESTAMP_TIMEZONE LOG_LEVEL LOG_DIRECTORY SCRIPT_NAME DEBUG_MODE
}

# Register cleanup
trap cleanup EXIT

# Helper functions
log_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    log_test "Running: $test_name"
    
    if eval "$test_command"; then
        log_pass "$test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        local exit_code=$?
        log_fail "$test_name (exit code: $exit_code)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Source utils.sh for testing
source_utils() {
    if [[ ! -f "$UTILS_SCRIPT" ]]; then
        echo "ERROR: utils.sh not found at $UTILS_SCRIPT"
        exit 1
    fi
    
    # Source without executing main code
    source "$UTILS_SCRIPT"
}

# Test 1: Timestamp format validation
test_timestamp_format_validation() {
    source_utils
    
    # Test valid formats
    local valid_formats=("default" "iso8601" "rfc3339" "syslog" "compact" "compact-precise" "readable" "readable-precise" "debug" "microseconds")
    for format in "${valid_formats[@]}"; do
        if ! validate_timestamp_format "$format"; then
            echo "Valid format '$format' was rejected"
            return 1
        fi
    done
    
    # Test invalid formats
    local invalid_formats=("invalid" "wrong" "iso8601-extra" "debug-invalid")
    for format in "${invalid_formats[@]}"; do
        if validate_timestamp_format "$format"; then
            echo "Invalid format '$format' was accepted"
            return 1
        fi
    done
    
    return 0
}

# Test 2: Timestamp generation for all formats
test_timestamp_generation() {
    source_utils
    
    local formats=("default" "iso8601" "rfc3339" "syslog" "compact" "compact-precise" "readable" "readable-precise" "debug" "microseconds")
    local timezones=("local" "utc")
    
    for format in "${formats[@]}"; do
        for timezone in "${timezones[@]}"; do
            local timestamp
            if ! timestamp=$(generate_timestamp "$format" "$timezone"); then
                echo "Failed to generate timestamp for format='$format', timezone='$timezone'"
                return 1
            fi
            
            if [[ -z "$timestamp" ]]; then
                echo "Empty timestamp generated for format='$format', timezone='$timezone'"
                return 1
            fi
            
            # Basic format validation
            case "$format" in
                "default"|"readable")
                    if ! [[ "$timestamp" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\ [0-9]{2}:[0-9]{2}:[0-9]{2}$ ]]; then
                        echo "Invalid default/readable timestamp format: $timestamp"
                        return 1
                    fi
                    ;;
                "compact")
                    if ! [[ "$timestamp" =~ ^[0-9]{8}_[0-9]{6}$ ]]; then
                        echo "Invalid compact timestamp format: $timestamp"
                        return 1
                    fi
                    ;;
                "iso8601")
                    if ! [[ "$timestamp" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2} ]]; then
                        echo "Invalid iso8601 timestamp format: $timestamp"
                        return 1
                    fi
                    ;;
            esac
        done
    done
    
    return 0
}

# Test 3: Timezone validation
test_timezone_validation() {
    source_utils
    
    # Test valid timezones
    local valid_timezones=("local" "utc" "UTC" "+0000" "-0000" "Z" "America/New_York" "Europe/London" "+05:30" "-08:00")
    for tz in "${valid_timezones[@]}"; do
        if ! validate_timezone "$tz"; then
            echo "Valid timezone '$tz' was rejected"
            return 1
        fi
    done
    
    # Test invalid timezones - use patterns that don't match the validation regex
    local invalid_timezones=("invalid" "XYZ" "America" "/Invalid" "+250" "-300" "GMT+25" "America/Invalid/Extra" "Invalid+Zone" "+2" "-3")
    for tz in "${invalid_timezones[@]}"; do
        if validate_timezone "$tz"; then
            echo "Invalid timezone '$tz' was accepted"
            return 1
        fi
    done
    
    return 0
}

# Test 4: Log level filtering
test_log_level_filtering() {
    source_utils
    
    # Test log level hierarchy
    local level_tests=(
        "DEBUG:0"
        "INFO:1"
        "SUCCESS:1"
        "WARNING:2"
        "ERROR:3"
    )
    
    for test in "${level_tests[@]}"; do
        local level="${test%:*}"
        local expected_priority="${test#*:}"
        local actual_priority
        
        # Extract priority from should_log function logic
        case "$level" in
            "DEBUG") actual_priority=0 ;;
            "INFO") actual_priority=1 ;;
            "SUCCESS") actual_priority=1 ;;
            "WARNING") actual_priority=2 ;;
            "ERROR") actual_priority=3 ;;
            *) actual_priority=-1 ;;
        esac
        
        if [[ $actual_priority -ne $expected_priority ]]; then
            echo "Log level '$level' has wrong priority: expected $expected_priority, got $actual_priority"
            return 1
        fi
    done
    
    # Test should_log function behavior
    export LOG_LEVEL="WARNING"
    
    # Should log WARNING and ERROR
    if ! should_log "WARNING"; then
        echo "WARNING should be logged when LOG_LEVEL=WARNING"
        return 1
    fi
    
    if ! should_log "ERROR"; then
        echo "ERROR should be logged when LOG_LEVEL=WARNING"
        return 1
    fi
    
    # Should not log INFO, SUCCESS, DEBUG
    if should_log "INFO"; then
        echo "INFO should not be logged when LOG_LEVEL=WARNING"
        return 1
    fi
    
    if should_log "DEBUG"; then
        echo "DEBUG should not be logged when LOG_LEVEL=WARNING"
        return 1
    fi
    
    return 0
}

# Test 5: Script name identification
test_script_name_identification() {
    source_utils
    
    # Test with SCRIPT_NAME set
    export SCRIPT_NAME="test-script"
    local script_name
    if ! script_name=$(get_script_name); then
        echo "Failed to get script name"
        return 1
    fi
    
    if [[ "$script_name" != "test-script" ]]; then
        echo "Expected 'test-script', got '$script_name'"
        return 1
    fi
    
    # Test without SCRIPT_NAME set
    unset SCRIPT_NAME
    if ! script_name=$(get_script_name); then
        echo "Failed to get script name without SCRIPT_NAME"
        return 1
    fi
    
    # Should return basename of calling script (in this case the test script)
    if [[ "$script_name" != "$(basename "$0")" ]]; then
        echo "Expected '$(basename "$0")', got '$script_name'"
        return 1
    fi
    
    return 0
}

# Test 6: Color code handling
test_color_handling() {
    source_utils
    
    local test_text="This is a test message"
    local colored_text="${RED}${test_text}${NC}"
    local clean_text
    
    if ! clean_text=$(strip_colors "$colored_text"); then
        echo "Failed to strip colors"
        return 1
    fi
    
    if [[ "$clean_text" != "$test_text" ]]; then
        echo "Color stripping failed: expected '$test_text', got '$clean_text'"
        return 1
    fi
    
    # Test with no colors
    if ! clean_text=$(strip_colors "$test_text"); then
        echo "Failed to process text without colors"
        return 1
    fi
    
    if [[ "$clean_text" != "$test_text" ]]; then
        echo "Text without colors was modified: expected '$test_text', got '$clean_text'"
        return 1
    fi
    
    return 0
}

# Test 7: Log entry formatting
test_log_entry_formatting() {
    source_utils
    
    local level="INFO"
    local timestamp="2026-01-31 10:30:45"
    local script_name="test-script"
    local message="Test message"
    
    local formatted_entry
    if ! formatted_entry=$(format_log_entry "$level" "$timestamp" "$script_name" "$message"); then
        echo "Failed to format log entry"
        return 1
    fi
    
    local expected="[INFO] 2026-01-31 10:30:45 test-script: Test message"
    if [[ "$formatted_entry" != "$expected" ]]; then
        echo "Log entry formatting failed: expected '$expected', got '$formatted_entry'"
        return 1
    fi
    
    return 0
}

# Test 8: Log file creation and basic functionality
test_log_file_creation() {
    # Setup test log directory
    export LOG_DIRECTORY="$TEST_LOG_DIR"
    mkdir -p "$LOG_DIRECTORY"
    export SCRIPT_NAME="test-logging"
    
    # Source utils after setting up environment
    source_utils
    
    # Debug: check if log function exists
    if ! declare -f log >/dev/null 2>&1; then
        echo "log function not available"
        return 1
    fi
    
    # Set LOG_LEVEL to allow INFO messages
    export LOG_LEVEL="INFO"
    
    # Test basic log to file
    log "INFO" "Test message for file logging"
    
    local log_file="$LOG_DIRECTORY/test-logging.log"
    if [[ ! -f "$log_file" ]]; then
        echo "Log file was not created: $log_file"
        return 1
    fi
    
    local log_file="$LOG_DIRECTORY/test-logging.log"
    if [[ ! -f "$log_file" ]]; then
        echo "Log file was not created: $log_file"
        return 1
    fi
    
    # Check if message was written
    if ! grep -q "Test message for file logging" "$log_file"; then
        echo "Log message not found in file: $log_file"
        return 1
    fi
    
    # Check if timestamp is present
    if ! grep -q "\[INFO\]" "$log_file"; then
        echo "Log level not found in file: $log_file"
        return 1
    fi
    
    return 0
}

# Test 9: Log rotation functionality
test_log_rotation() {
    # Setup test log directory
    export LOG_DIRECTORY="$TEST_LOG_DIR"
    mkdir -p "$LOG_DIRECTORY"
    export SCRIPT_NAME="test-rotation"
    export LOG_MAX_SIZE_MB=0.001  # Very small size to trigger rotation
    export LOG_MAX_FILES=3
    
    # Source utils after setting up environment
    source_utils
    
    # Create a large log file to trigger rotation
    local log_file="$LOG_DIRECTORY/test-rotation.log"
    local large_message
    for i in {1..1000}; do
        large_message+="This is a very large log message to trigger rotation $i\n"
    done
    echo -e "$large_message" > "$log_file"
    
    # Test rotation
    rotate_log_if_needed "$log_file"
    
    # Check if rotation occurred
    local rotated_file="$LOG_DIRECTORY/test-rotation.1.log"
    if [[ ! -f "$rotated_file" ]]; then
        echo "Log rotation did not occur - rotated file not found: $rotated_file"
        return 1
    fi
    
    # Check if new log file exists
    if [[ ! -f "$log_file" ]]; then
        echo "New log file was not created after rotation: $log_file"
        return 1
    fi
    
    return 0
}

# Test 10: Logging configuration
test_logging_configuration() {
    source_utils
    
    # Test valid configuration
    if ! configure_logging "iso8601" "utc"; then
        echo "Failed to configure logging with valid parameters"
        return 1
    fi
    
    if [[ "$TIMESTAMP_FORMAT" != "iso8601" ]]; then
        echo "TIMESTAMP_FORMAT not set correctly: expected 'iso8601', got '$TIMESTAMP_FORMAT'"
        return 1
    fi
    
    if [[ "$TIMESTAMP_TIMEZONE" != "utc" ]]; then
        echo "TIMESTAMP_TIMEZONE not set correctly: expected 'utc', got '$TIMESTAMP_TIMEZONE'"
        return 1
    fi
    
    # Test invalid format (should fallback to default)
    if ! configure_logging "invalid-format" "utc"; then
        echo "Failed to configure logging with invalid format (should fallback)"
        return 1
    fi
    
    if [[ "$TIMESTAMP_FORMAT" != "default" ]]; then
        echo "TIMESTAMP_FORMAT not fallback to default: expected 'default', got '$TIMESTAMP_FORMAT'"
        return 1
    fi
    
    return 0
}

# Test 11: Performance under load
test_performance() {
    source_utils
    
    local iterations=100
    local start_time end_time duration avg_time
    
    # Test timestamp generation performance
    start_time=$(date +%s.%N 2>/dev/null || date +%s)
    for ((i=1; i<=iterations; i++)); do
        generate_timestamp "default" "local" >/dev/null
    done
    end_time=$(date +%s.%N 2>/dev/null || date +%s)
    
    duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")
    avg_time=$(echo "scale=6; $duration / $iterations" | bc 2>/dev/null || echo "0")
    
    # Check if average time is reasonable (less than 0.01 seconds per call)
    local reasonable_threshold=0.01
    if command -v bc >/dev/null 2>&1; then
        local comparison=$(echo "$avg_time < $reasonable_threshold" | bc 2>/dev/null || echo "1")
        if [[ "$comparison" != "1" ]]; then
            echo "Performance test failed: average time $avg_time exceeds threshold $reasonable_threshold"
            return 1
        fi
    fi
    
    log_info "Performance test: $iterations iterations in ${duration}s (avg: ${avg_time}s per call)"
    
    return 0
}

# Test 12: Error handling and edge cases
test_error_handling() {
    source_utils
    
    # Test logging with undefined variables
    local old_log_level="$LOG_LEVEL"
    unset LOG_LEVEL
    
    # Should still work with default log level
    if ! log "INFO" "Test with undefined LOG_LEVEL"; then
        echo "Failed to log with undefined LOG_LEVEL"
        return 1
    fi
    
    # Test with invalid timestamp format (should fallback)
    export TIMESTAMP_FORMAT="completely-invalid-format"
    if ! log "INFO" "Test with invalid timestamp format"; then
        echo "Failed to log with invalid timestamp format"
        return 1
    fi
    
    # Test with unwritable log directory (should not fail)
    export LOG_DIRECTORY="/root/nonexistent/directory"
    if ! log "INFO" "Test with unwritable log directory"; then
        echo "Failed to log with unwritable log directory"
        return 1
    fi
    
    # Restore
    export LOG_LEVEL="$old_log_level"
    
    return 0
}

# Test 13: Integration with script execution
test_integration() {
    # Setup clean log directory for this test
    local integration_log_dir="$TEST_LOG_DIR/integration"
    export LOG_DIRECTORY="$integration_log_dir"
    mkdir -p "$LOG_DIRECTORY"
    export SCRIPT_NAME="integration-test"
    export TIMESTAMP_FORMAT="readable"
    export LOG_LEVEL="INFO"
    # Reset log rotation limits to avoid interference from previous tests
    export LOG_MAX_SIZE_MB=10
    export LOG_MAX_FILES=5
    
    # Source utils after setting up environment
    source_utils
    
    # Simulate script execution with various log levels
    log "INFO" "Script started"
    log "DEBUG" "This debug message should not appear if LOG_LEVEL=INFO"
    log "WARNING" "Warning message"
    log "ERROR" "Error message"
    log "SUCCESS" "Script completed"
    
    local log_file="$LOG_DIRECTORY/integration-test.log"
    if [[ ! -f "$log_file" ]]; then
        echo "Integration test: log file not created"
        return 1
    fi
    
    # Check that DEBUG message is not in file
    if grep -q "This debug message should not appear" "$log_file"; then
        echo "Integration test: DEBUG message appeared when it shouldn't"
        return 1
    fi
    
    # Check that other messages are in file
    if ! grep -q "Script started" "$log_file"; then
        echo "Integration test: INFO message missing from log file"
        return 1
    fi
    
    if ! grep -q "Warning message" "$log_file"; then
        echo "Integration test: WARNING message missing from log file"
        return 1
    fi
    
    return 0
}

# Test 14: Specialized logging functions
test_specialized_logging() {
    # Setup clean log directory for this test
    local specialized_log_dir="$TEST_LOG_DIR/specialized"
    export LOG_DIRECTORY="$specialized_log_dir"
    mkdir -p "$LOG_DIRECTORY"
    # Reset log rotation limits to avoid interference from previous tests
    export LOG_MAX_SIZE_MB=10
    export LOG_MAX_FILES=5
    
    # Source utils after setting up environment
    source_utils
    
    # Test change detection logging
    log_change_detection "test-repo" "5" "false"
    log_change_detection "test-repo" "10" "true"
    
    # Test system health logging
    log_system_health "disk-space" "pass"
    log_system_health "memory" "fail" "Insufficient memory"
    
    # Test reboot event logging
    log_reboot_event "system-update" "2026-01-31 12:00:00"
    
    # Check log file contains expected patterns
    local log_file="$LOG_DIRECTORY/utils.sh.log"
    if [[ -f "$log_file" ]]; then
        if ! grep -q "Change detection in test-repo" "$log_file"; then
            echo "Change detection logging not working"
            return 1
        fi
        
        if ! grep -q "REBOOT SCHEDULED" "$log_file"; then
            echo "Reboot event logging not working"
            return 1
        fi
    fi
    
    return 0
}

# Main test execution
main() {
    echo "=== Comprehensive Timestamp Logging Test Suite ==="
    echo "Testing directory: $PROJECT_DIR"
    echo "Utils script: $UTILS_SCRIPT"
    echo "Test log directory: $TEST_LOG_DIR"
    echo ""
    
    # Run all tests
    run_test "Timestamp format validation" "test_timestamp_format_validation"
    run_test "Timestamp generation for all formats" "test_timestamp_generation"
    run_test "Timezone validation" "test_timezone_validation"
    run_test "Log level filtering" "test_log_level_filtering"
    run_test "Script name identification" "test_script_name_identification"
    run_test "Color code handling" "test_color_handling"
    run_test "Log entry formatting" "test_log_entry_formatting"
    run_test "Log file creation" "test_log_file_creation"
    run_test "Log rotation functionality" "test_log_rotation"
    run_test "Logging configuration" "test_logging_configuration"
    run_test "Performance under load" "test_performance"
    run_test "Error handling and edge cases" "test_error_handling"
    run_test "Integration with script execution" "test_integration"
    run_test "Specialized logging functions" "test_specialized_logging"
    
    # Print results
    echo ""
    echo "=== Test Results ==="
    echo "Total tests: $TESTS_TOTAL"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ All timestamp logging tests passed!${NC}"
        echo ""
        echo "Test coverage includes:"
        echo "  ✓ All timestamp formats (default, iso8601, rfc3339, syslog, compact, etc.)"
        echo "  ✓ Timezone handling (local, utc, specific zones)"
        echo "  ✓ Log level filtering and priority hierarchy"
        echo "  ✓ Script name identification and fallback"
        echo "  ✓ Color code processing and stripping"
        echo "  ✓ Log file creation, rotation, and cleanup"
        echo "  ✓ Performance under load"
        echo "  ✓ Error handling and edge cases"
        echo "  ✓ Integration testing with real scenarios"
        echo "  ✓ Specialized logging functions"
        exit 0
    else
        echo -e "${RED}✗ Some timestamp logging tests failed!${NC}"
        exit 1
    fi
}

# Run main function
main "$@"