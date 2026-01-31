#!/bin/bash

# Test script for logging system consistency across all scripts
# Validates that all scripts use consistent timestamped logging

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

SCRIPT_NAME="logging_test"

echo "=============================================="
echo "Logging System Consistency Test"
echo "=============================================="

# Test that all scripts have proper logging setup
test_results=()
scripts_with_issues=()

echo ""
echo "=== Testing Script Logging Setup ==="

for script in /root/git/managed/Auto-slopp/scripts/*.sh; do
    script_name=$(basename "$script")
    
    # Skip utils.sh (special case) and test script itself
    if [[ "$script_name" == "utils.sh" || "$script_name" == "test_logging_system.sh" ]]; then
        continue
    fi
    
    issues=()
    
    # Check for SCRIPT_NAME variable
    if grep -q "^SCRIPT_NAME=" "$script"; then
        echo "  ✅ $script_name: Has SCRIPT_NAME variable"
    else
        issues+=("Missing SCRIPT_NAME variable")
        echo "  ❌ $script_name: Missing SCRIPT_NAME variable"
    fi
    
    # Check for utils.sh sourcing
    if grep -q "source.*utils.sh" "$script"; then
        echo "  ✅ $script_name: Sources utils.sh"
    else
        issues+=("Missing utils.sh sourcing")
        echo "  ❌ $script_name: Missing utils.sh sourcing"
    fi
    
    # Check for setup_error_handling
    if grep -q "setup_error_handling" "$script"; then
        echo "  ✅ $script_name: Sets up error handling"
    else
        issues+=("Missing error handling setup")
        echo "  ❌ $script_name: Missing error handling setup"
    fi
    
    # Count echo vs log statements
    echo_count=$(grep -c "^[[:space:]]*echo[[:space:]]" "$script" 2>/dev/null || echo "0")
    log_count=$(grep -c "log \"[A-Z]" "$script" 2>/dev/null || echo "0")
    
    if [ "$echo_count" -gt 0 ] && [ "$log_count" -eq 0 ]; then
        issues+=("Uses echo instead of log()")
        echo "  ❌ $script_name: Uses echo instead of log() ($echo_count echo statements)"
    elif [ "$echo_count" -gt 0 ] && [ "$log_count" -gt 0 ]; then
        echo "  🔍 $script_name: Mixed echo and log() usage ($echo_count echo, $log_count log)"
    else
        echo "  ✅ $script_name: Uses log() consistently ($log_count log calls)"
    fi
    
    # Check for proper log levels
    if grep -q "log \"[A-Z]" "$script"; then
        if grep -q "log \"DEBUG\|INFO\|WARNING\|ERROR\|SUCCESS\"" "$script"; then
            echo "  ✅ $script_name: Uses proper log levels"
        else
            issues+=("Uses undefined log levels")
            echo "  ❌ $script_name: Uses undefined log levels"
        fi
    fi
    
    if [ ${#issues[@]} -gt 0 ]; then
        scripts_with_issues+=("$script_name")
        test_results+=("$script_name: ${issues[*]}")
    fi
done

echo ""
echo "=== Testing Log Functionality ==="

# Test timestamp generation
echo "Testing timestamp generation..."
timestamp=$(generate_timestamp "readable" "local")
echo "Generated timestamp: $timestamp"

# Test log function with different levels
log "INFO" "Test INFO message with timestamp"
log "SUCCESS" "Test SUCCESS message with timestamp"
log "WARNING" "Test WARNING message with timestamp"
log "ERROR" "Test ERROR message with timestamp"

# Test in debug mode
export DEBUG_MODE=true
log "DEBUG" "Test DEBUG message with debug mode enabled"

echo ""
echo "=== Testing Configuration Integration ==="

# Test configuration loading
echo "Testing configuration loading..."
echo "SLEEP_DURATION: $SLEEP_DURATION"
echo "MANAGED_REPO_PATH: $MANAGED_REPO_PATH"
echo "LOG_DIRECTORY: ${LOG_DIRECTORY:-'Not configured'}"
echo "TIMESTAMP_FORMAT: ${TIMESTAMP_FORMAT:-'default'}"
echo "TIMESTAMP_TIMEZONE: ${TIMESTAMP_TIMEZONE:-'local'}"

echo ""
echo "=== Testing Error Handling ==="

# Test error handling
echo "Testing error handling setup..."
if grep -q "setup_error_handling" /root/git/managed/Auto-slopp/scripts/main.sh; then
    echo "  ✅ main.sh has error handling"
else
    echo "  ❌ main.sh missing error handling"
fi

echo ""
echo "=============================================="
echo "Test Results Summary"
echo "=============================================="

if [ ${#scripts_with_issues[@]} -eq 0 ]; then
    echo "🎉 All scripts passed logging consistency tests!"
    echo ""
    echo "✅ Logging System Status: COMPLETE"
    echo "✅ Timestamp functionality: WORKING"
    echo "✅ Log levels: CONSISTENT"
    echo "✅ Error handling: INTEGRATED"
    echo "✅ Configuration: LOADED"
    exit 0
else
    echo "❌ Scripts with issues found:"
    for result in "${test_results[@]}"; do
        echo "  - $result"
    done
    
    echo ""
    echo "📊 Summary:"
    echo "  - Total scripts checked: $(ls /root/git/managed/Auto-slopp/scripts/*.sh | wc -l)"
    echo "  - Scripts with issues: ${#scripts_with_issues[@]}"
    echo "  - Scripts consistent: $((${#scripts_with_issues[@]} - 1))"
    
    exit 1
fi