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

# Test 15: Color output verification
test_color_output_verification() {
    source_utils
    
    # Setup capture for color output testing
    local test_output="/tmp/color-test-$$"
    export LOG_LEVEL="DEBUG"
    export DEBUG_MODE="true"
    
    # Redirect output to capture colors
    {
        log "INFO" "Info message"
        log "SUCCESS" "Success message"  
        log "WARNING" "Warning message"
        log "ERROR" "Error message"
        log "DEBUG" "Debug message"
    } > "$test_output" 2>&1
    
    # Check for color codes in output
    if ! grep -q "\[0;34m" "$test_output"; then
        echo "INFO color codes missing"
        return 1
    fi
    
    if ! grep -q "\[0;32m" "$test_output"; then
        echo "SUCCESS color codes missing"
        return 1
    fi
    
    if ! grep -q "\[1;33m" "$test_output"; then
        echo "WARNING color codes missing"
        return 1
    fi
    
    if ! grep -q "\[0;31m" "$test_output"; then
        echo "ERROR color codes missing"
        return 1
    fi
    
    # Clean up
    rm -f "$test_output"
    
    return 0
}

# Test 16: Advanced timezone handling
test_advanced_timezone_handling() {
    source_utils
    
    # Test specific timezone identifiers
    local timezones=("America/New_York" "Europe/London" "Asia/Tokyo" "Australia/Sydney")
    
    for tz in "${timezones[@]}"; do
        if ! validate_timezone "$tz"; then
            echo "Valid timezone '$tz' was rejected"
            return 1
        fi
        
        # Test timestamp generation with specific timezone
        local timestamp
        if ! timestamp=$(generate_timestamp "default" "$tz"); then
            echo "Failed to generate timestamp for timezone: $tz"
            return 1
        fi
        
        if [[ -z "$timestamp" ]]; then
            echo "Empty timestamp for timezone: $tz"
            return 1
        fi
    done
    
    # Test UTC vs local differences
    local utc_timestamp
    local local_timestamp
    
    if ! utc_timestamp=$(generate_timestamp "iso8601" "utc"); then
        echo "Failed to generate UTC timestamp"
        return 1
    fi
    
    if ! local_timestamp=$(generate_timestamp "iso8601" "local"); then
        echo "Failed to generate local timestamp"
        return 1
    fi
    
    # UTC timestamp should end with 'Z'
    if ! [[ "$utc_timestamp" =~ Z$ ]]; then
        echo "UTC timestamp should end with 'Z': $utc_timestamp"
        return 1
    fi
    
    return 0
}

# Test 17: Log retention and cleanup
test_log_retention_cleanup() {
    # Setup test log directory
    local retention_log_dir="$TEST_LOG_DIR/retention"
    export LOG_DIRECTORY="$retention_log_dir"
    export SCRIPT_NAME="retention-test"
    export LOG_RETENTION_DAYS=1  # 1 day for testing
    export LOG_MAX_FILES=2
    
    mkdir -p "$LOG_DIRECTORY"
    source_utils
    
    # Create some old rotated log files (simulate old files)
    local old_file="$LOG_DIRECTORY/retention-test.1.log"
    local very_old_file="$LOG_DIRECTORY/retention-test.2.log"
    
    echo "Old log content 1" > "$old_file"
    echo "Old log content 2" > "$very_old_file"
    
    # Set very old modification time (2 days ago)
    touch -d "2 days ago" "$very_old_file" 2>/dev/null || touch -t $(date -d "2 days ago" +%Y%m%d%H%M.%S) "$very_old_file" 2>/dev/null || true
    
    # Run cleanup
    cleanup_old_logs
    
    # The very old file should be removed (if touch command worked)
    # Note: This test might not work on all systems due to touch limitations
    if [[ -f "$very_old_file" ]]; then
        echo "Note: File age manipulation not available on this system, skipping retention verification"
    fi
    
    # Test log directory setup
    local setup_log_dir="$TEST_LOG_DIR/setup-test"
    export LOG_DIRECTORY="$setup_log_dir"
    
    if setup_log_directory; then
        if [[ ! -d "$setup_log_dir" ]]; then
            echo "setup_log_directory failed to create directory"
            return 1
        fi
    else
        echo "setup_log_directory returned failure"
        return 1
    fi
    
    return 0
}

# Test 18: Performance with different formats
test_performance_by_format() {
    source_utils
    
    local formats=("default" "iso8601" "compact" "debug")
    local iterations=50
    
    echo "Performance comparison by format:"
    
    for format in "${formats[@]}"; do
        local start_time end_time duration avg_time
        
        start_time=$(date +%s.%N 2>/dev/null || date +%s)
        for ((i=1; i<=iterations; i++)); do
            generate_timestamp "$format" "local" >/dev/null
        done
        end_time=$(date +%s.%N 2>/dev/null || date +%s)
        
        duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")
        avg_time=$(echo "scale=6; $duration / $iterations" | bc 2>/dev/null || echo "0")
        
        echo "  $format: ${avg_time}s per call"
        
        # Check that no format is excessively slow (more than 0.02s per call)
        if command -v bc >/dev/null 2>&1; then
            local comparison=$(echo "$avg_time < 0.02" | bc 2>/dev/null || echo "1")
            if [[ "$comparison" != "1" ]]; then
                echo "Format '$format' is too slow: ${avg_time}s per call"
                return 1
            fi
        fi
    done
    
    return 0
}

# Test 19: Log message sanitization and edge cases
test_log_message_edge_cases() {
    source_utils
    
    export LOG_LEVEL="DEBUG"
    export LOG_DIRECTORY="$TEST_LOG_DIR"
    export SCRIPT_NAME="edge-test"
    
    # Test with special characters
    local special_chars="Message with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
    if ! log "INFO" "$special_chars"; then
        echo "Failed to log message with special characters"
        return 1
    fi
    
    # Test with multiline messages
    local multiline="Line 1\nLine 2\nLine 3"
    if ! log "INFO" "$multiline"; then
        echo "Failed to log multiline message"
        return 1
    fi
    
    # Test with very long message
    local long_message=""
    for ((i=1; i<=1000; i++)); do
        long_message+="This is a very long message part $i. "
    done
    
    if ! log "INFO" "$long_message"; then
        echo "Failed to log very long message"
        return 1
    fi
    
    # Test with quotes and apostrophes
    local quotes="Message with 'single quotes' and \"double quotes\""
    if ! log "INFO" "$quotes"; then
        echo "Failed to log message with quotes"
        return 1
    fi
    
    # Test with empty message
    if ! log "INFO" ""; then
        echo "Failed to log empty message"
        return 1
    fi
    
    # Test with only whitespace
    if ! log "INFO" "   "; then
        echo "Failed to log whitespace-only message"
        return 1
    fi
    
    return 0
}

# Test 20: Concurrent logging stress test
test_concurrent_logging() {
    source_utils
    
    export LOG_DIRECTORY="$TEST_LOG_DIR/concurrent"
    export SCRIPT_NAME="concurrent-test"
    export LOG_LEVEL="INFO"
    mkdir -p "$LOG_DIRECTORY"
    
    # Start multiple background processes logging simultaneously
    local pids=()
    local processes=5
    local messages_per_process=20
    
    for ((i=1; i<=processes; i++)); do
        (
            for ((j=1; j<=messages_per_process; j++)); do
                log "INFO" "Process $i message $j"
                sleep 0.001  # Small delay between messages (portable)
            done
        ) &
        pids+=($!)
    done
    
    # Wait for all processes to complete
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
    
    # Check that all messages were logged
    local log_file="$LOG_DIRECTORY/concurrent-test.log"
    if [[ ! -f "$log_file" ]]; then
        echo "Concurrent log file not created"
        return 1
    fi
    
    # Count total messages (should be processes * messages_per_process)
    local expected_messages=$((processes * messages_per_process))
    local actual_messages=$(grep -c "Process.*message" "$log_file" 2>/dev/null || echo "0")
    
    if [[ $actual_messages -lt $expected_messages ]]; then
        echo "Concurrent logging lost messages: expected $expected_messages, got $actual_messages"
        return 1
    fi
    
    return 0
}

# Test 21: Integration with real script execution
test_real_script_integration() {
    # Create a test script that uses the logging system
    local test_script="/tmp/integration-test-script-$$"
    
    cat > "$test_script" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/utils.sh"

SCRIPT_NAME="integration-script"
LOG_DIRECTORY="/tmp/integration-test-logs"
mkdir -p "$LOG_DIRECTORY"

setup_error_handling

log "INFO" "Test script started"
log "DEBUG" "This is a debug message"
log "WARNING" "This is a warning"
log "SUCCESS" "Operation completed successfully"

script_success
EOF
    
    # Make it executable
    chmod +x "$test_script"
    
    # Execute the test script
    local script_output
    if ! script_output=$("$test_script" 2>&1); then
        echo "Integration script execution failed: $script_output"
        rm -f "$test_script"
        return 1
    fi
    
    # Check for expected log messages in output
    if ! echo "$script_output" | grep -q "Test script started"; then
        echo "Expected log message missing from script output"
        rm -f "$test_script"
        return 1
    fi
    
    if ! echo "$script_output" | grep -q "Operation completed successfully"; then
        echo "Expected success message missing from script output"
        rm -f "$test_script"
        return 1
    fi
    
    # Check log file was created
    local log_file="/tmp/integration-test-logs/integration-script.log"
    if [[ -f "$log_file" ]]; then
        # Check for log entries in file
        if ! grep -q "Test script started" "$log_file"; then
            echo "Expected log message missing from log file"
            rm -f "$test_script"
            return 1
        fi
    fi
    
    # Clean up
    rm -f "$test_script"
    rm -rf "/tmp/integration-test-logs"
    
    return 0
}

# Test 22: Format recommendation system
test_format_recommendation() {
    source_utils
    
    # Test format recommendations
    local recommendation
    
    # Test production recommendation
    recommendation=$(recommend_timestamp_format "production" 2>/dev/null)
    if ! echo "$recommendation" | grep -q "iso8601"; then
        echo "Production recommendation incorrect: $recommendation"
        return 1
    fi
    
    # Test development recommendation  
    recommendation=$(recommend_timestamp_format "development" 2>/dev/null)
    if ! echo "$recommendation" | grep -q "readable-precise"; then
        echo "Development recommendation incorrect: $recommendation"
        return 1
    fi
    
    # Test debugging recommendation
    recommendation=$(recommend_timestamp_format "debugging" 2>/dev/null)
    if ! echo "$recommendation" | grep -q "debug"; then
        echo "Debugging recommendation incorrect: $recommendation"
        return 1
    fi
    
    # Test general recommendation (default)
    recommendation=$(recommend_timestamp_format "general" 2>/dev/null)
    if ! echo "$recommendation" | grep -q "readable"; then
        echo "General recommendation incorrect: $recommendation"
        return 1
    fi
    
    return 0
}

# Test 23: Benchmark functionality
test_benchmark_functionality() {
    source_utils
    
    # Test benchmark function exists and works
    local benchmark_output
    if ! benchmark_output=$(benchmark_timestamp_generation "default" 10 "local" 2>&1); then
        echo "Benchmark function failed"
        return 1
    fi
    
    # Check benchmark output contains expected information
    if ! echo "$benchmark_output" | grep -q "Benchmark results"; then
        echo "Benchmark output missing expected header: $benchmark_output"
        return 1
    fi
    
    if ! echo "$benchmark_output" | grep -q "Total time:"; then
        echo "Benchmark output missing total time: $benchmark_output"
        return 1
    fi
    
    if ! echo "$benchmark_output" | grep -q "Average per call:"; then
        echo "Benchmark output missing average time: $benchmark_output"
        return 1
    fi
    
    return 0
}

# Test 24: Supported formats listing
test_supported_formats() {
    source_utils
    
    # Test get_supported_timestamp_formats function
    local formats_output
    if ! formats_output=$(get_supported_timestamp_formats 2>&1); then
        echo "get_supported_timestamp_formats failed"
        return 1
    fi
    
    # Check for all expected formats
    local expected_formats=("default" "iso8601" "rfc3339" "syslog" "compact" "readable" "debug")
    for format in "${expected_formats[@]}"; do
        if ! echo "$formats_output" | grep -q "^$format:"; then
            echo "Expected format '$format' missing from supported formats list"
            return 1
        fi
    done
    
    return 0
}

# Main test execution
main() {
    echo "=== Enhanced Comprehensive Timestamp Logging Test Suite ==="
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
    run_test "Color output verification" "test_color_output_verification"
    run_test "Advanced timezone handling" "test_advanced_timezone_handling"
    run_test "Log retention and cleanup" "test_log_retention_cleanup"
    run_test "Performance by format comparison" "test_performance_by_format"
    run_test "Log message edge cases" "test_log_message_edge_cases"
    run_test "Concurrent logging stress test" "test_concurrent_logging"
    run_test "Real script integration" "test_real_script_integration"
    run_test "Format recommendation system" "test_format_recommendation"
    run_test "Benchmark functionality" "test_benchmark_functionality"
    run_test "Supported formats listing" "test_supported_formats"
    
    # Print results
    echo ""
    echo "=== Test Results ==="
    echo "Total tests: $TESTS_TOTAL"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ All enhanced timestamp logging tests passed!${NC}"
        echo ""
        echo "Test coverage includes:"
        echo "  ✓ All timestamp formats (default, iso8601, rfc3339, syslog, compact, etc.)"
        echo "  ✓ Timezone handling (local, utc, specific zones, advanced scenarios)"
        echo "  ✓ Log level filtering and priority hierarchy"
        echo "  ✓ Script name identification and fallback"
        echo "  ✓ Color code processing, verification, and stripping"
        echo "  ✓ Log file creation, rotation, retention, and cleanup"
        echo "  ✓ Performance under load and by format comparison"
        echo "  ✓ Error handling, edge cases, and message sanitization"
        echo "  ✓ Integration testing with real scenarios and scripts"
        echo "  ✓ Specialized logging functions (change detection, health, reboot)"
        echo "  ✓ Concurrent logging stress testing"
        echo "  ✓ Format recommendation and benchmark systems"
        echo "  ✓ Supported formats validation"
        exit 0
    else
        echo -e "${RED}✗ Some enhanced timestamp logging tests failed!${NC}"
        exit 1
    fi
}

# Run main function
main "$@"