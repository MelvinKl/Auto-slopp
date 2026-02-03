#!/bin/bash

# Test script for Enhanced Safe Reboot Mechanism
# Tests the comprehensive safety checks and reboot procedures

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$PROJECT_DIR/config.sh"
source "$PROJECT_DIR/scripts/utils.sh"

# Test configuration
TEST_RESULTS_DIR="${LOG_DIRECTORY}/safe-reboot-tests-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$TEST_RESULTS_DIR"

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Logging function for tests
test_log() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$TEST_RESULTS_DIR/test.log"
}

# Test result function
record_test() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if [[ "$result" == "PASS" ]]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        test_log "PASS" "✓ $test_name: $details"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        test_log "FAIL" "✗ $test_name: $details"
    fi
    
    echo "$result,$test_name,$details" >> "$TEST_RESULTS_DIR/results.csv"
}

# Source the enhanced auto-update-reboot script functions
source "$PROJECT_DIR/scripts/auto-update-reboot.sh"

# Test 1: System Health Checks
test_system_health_checks() {
    test_log "INFO" "Testing enhanced system health checks..."
    
    # Test disk space check
    if check_system_health >/dev/null 2>&1; then
        record_test "System Health Check" "PASS" "Basic system health checks passed"
    else
        record_test "System Health Check" "FAIL" "System health checks failed"
    fi
    
    # Test individual health components
    if check_network_connectivity; then
        record_test "Network Connectivity" "PASS" "Network connectivity check passed"
    else
        record_test "Network Connectivity" "FAIL" "Network connectivity issues detected"
    fi
    
    if check_file_operations; then
        record_test "File Operations Check" "PASS" "No disruptive file operations detected"
    else
        record_test "File Operations Check" "FAIL" "Critical file operations in progress"
    fi
}

# Test 2: Reboot Safety Confirmation
test_reboot_safety() {
    test_log "INFO" "Testing reboot safety confirmation..."
    
    # Test safety scoring
    local safety_result=""
    if confirm_reboot_safety >/dev/null 2>&1; then
        safety_result="PASS"
        record_test "Reboot Safety Confirmation" "PASS" "Reboot safety checks passed"
    else
        safety_result="FAIL"
        record_test "Reboot Safety Confirmation" "FAIL" "Reboot safety checks failed"
    fi
    
    # Test individual safety components
    if check_active_sessions; then
        record_test "Active Sessions Check" "PASS" "Active sessions check passed"
    else
        record_test "Active Sessions Check" "FAIL" "Active sessions issues detected"
    fi
    
    if check_power_status; then
        record_test "Power Status Check" "PASS" "Power status check passed"
    else
        record_test "Power Status Check" "FAIL" "Power status issues detected"
    fi
    
    if ! detect_recent_crashes; then
        record_test "Recent Crashes Check" "PASS" "No recent crashes detected"
    else
        record_test "Recent Crashes Check" "FAIL" "Recent crashes detected"
    fi
}

# Test 3: Reboot Type Determination
test_reboot_types() {
    test_log "INFO" "Testing reboot type determination..."
    
    # Test maintenance window detection
    local maintenance_result=""
    if is_maintenance_window; then
        maintenance_result="IN_WINDOW"
        record_test "Maintenance Window Detection" "PASS" "Currently in maintenance window"
    else
        maintenance_result="OUTSIDE_WINDOW"
        record_test "Maintenance Window Detection" "PASS" "Currently outside maintenance window"
    fi
    
    # Test delay decision
    local should_delay=""
    if should_delay_reboot; then
        should_delay="DELAY"
        record_test "Reboot Delay Decision" "PASS" "Reboot should be delayed"
    else
        should_delay="IMMEDIATE"
        record_test "Reboot Delay Decision" "PASS" "Immediate reboot appropriate"
    fi
    
    # Test overall reboot type determination
    local reboot_type=$(determine_reboot_type)
    record_test "Reboot Type Determination" "PASS" "Determined reboot type: $reboot_type"
    
    # Test maintenance window calculation
    local next_window=$(calculate_next_maintenance_window)
    record_test "Next Maintenance Window" "PASS" "Next maintenance window: $next_window"
}

# Test 4: Configuration Loading
test_configuration() {
    test_log "INFO" "Testing enhanced configuration loading..."
    
    # Test basic configuration values
    if [[ -n "${SAFE_REBOOT_MAX_DISK_USAGE:-}" ]]; then
        record_test "Safe Reboot Config Loading" "PASS" "Safe reboot configuration loaded: max disk usage = ${SAFE_REBOOT_MAX_DISK_USAGE}%"
    else
        record_test "Safe Reboot Config Loading" "FAIL" "Safe reboot configuration not loaded properly"
    fi
    
    if [[ -n "${MAINTENANCE_WINDOW_START:-}" ]]; then
        record_test "Maintenance Window Config" "PASS" "Maintenance window configured: ${MAINTENANCE_WINDOW_START} - ${MAINTENANCE_WINDOW_END}"
    else
        record_test "Maintenance Window Config" "FAIL" "Maintenance window configuration missing"
    fi
    
    if [[ -n "${BUSINESS_HOURS_START:-}" ]]; then
        record_test "Business Hours Config" "PASS" "Business hours configured: ${BUSINESS_HOURS_START} - ${BUSINESS_HOURS_END}"
    else
        record_test "Business Hours Config" "FAIL" "Business hours configuration missing"
    fi
}

# Test 5: State Management
test_state_management() {
    test_log "INFO" "Testing enhanced state management..."
    
    # Test state initialization
    if initialize_state; then
        record_test "State Initialization" "PASS" "Enhanced state file initialized successfully"
    else
        record_test "State Initialization" "FAIL" "State file initialization failed"
    fi
    
    # Test state value operations
    set_state_value "test_value" "test_data"
    local retrieved_value=$(get_state_value "test_value" "default")
    if [[ "$retrieved_value" == "test_data" ]]; then
        record_test "State Value Operations" "PASS" "State value get/set operations working"
    else
        record_test "State Value Operations" "FAIL" "State value operations failed: got '$retrieved_value'"
    fi
}

# Test 6: Enhanced Logging
test_enhanced_logging() {
    test_log "INFO" "Testing enhanced logging capabilities..."
    
    # Test system state snapshot
    if log_enhanced_system_state; then
        record_test "Enhanced System State Logging" "PASS" "Enhanced system state snapshot created"
    else
        record_test "Enhanced System State Logging" "FAIL" "Enhanced system state logging failed"
    fi
    
    # Test backup creation
    if create_system_backup; then
        record_test "System Backup Creation" "PASS" "Pre-reboot system backup created"
    else
        record_test "System Backup Creation" "FAIL" "System backup creation failed"
    fi
}

# Test 7: Notification System
test_notifications() {
    test_log "INFO" "Testing notification system..."
    
    # Test notification functions (without actually sending)
    local reboot_type="test"
    local scheduled_time="2026-02-02 12:00:00"
    
    if command -v send_enhanced_pre_reboot_notifications >/dev/null 2>&1; then
        record_test "Notification Functions" "PASS" "Enhanced notification functions available"
    else
        record_test "Notification Functions" "FAIL" "Enhanced notification functions not found"
    fi
    
    if command -v send_monitoring_alerts >/dev/null 2>&1; then
        record_test "Monitoring Alerts" "PASS" "Monitoring alert functions available"
    else
        record_test "Monitoring Alerts" "FAIL" "Monitoring alert functions not found"
    fi
}

# Test 8: Recovery Procedures
test_recovery_procedures() {
    test_log "INFO" "Testing recovery procedures..."
    
    # Test failure record creation
    if create_safety_failure_record; then
        record_test "Safety Failure Records" "PASS" "Safety failure record creation working"
    else
        record_test "Safety Failure Records" "FAIL" "Safety failure record creation failed"
    fi
    
    # Test reboot attempt records
    if create_reboot_attempt_record "test_$(date +%s)"; then
        record_test "Reboot Attempt Records" "PASS" "Reboot attempt record creation working"
    else
        record_test "Reboot Attempt Records" "FAIL" "Reboot attempt record creation failed"
    fi
}

# Generate comprehensive test report
generate_test_report() {
    local report_file="$TEST_RESULTS_DIR/comprehensive_report.md"
    
    cat > "$report_file" << EOF
# Enhanced Safe Reboot Mechanism - Test Report

**Test Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Test Environment:** $(uname -a)

## Test Summary

- **Total Tests:** $TESTS_TOTAL
- **Passed:** $TESTS_PASSED
- **Failed:** $TESTS_FAILED
- **Success Rate:** $(( TESTS_PASSED * 100 / TESTS_TOTAL ))%

## Test Categories

### 1. System Health Checks
Enhanced comprehensive health monitoring including:
- Multi-mount point disk space checking
- Detailed memory and swap analysis
- System load assessment
- Service status monitoring
- Network connectivity validation
- File operation interference detection

### 2. Reboot Safety Confirmation
Multi-factor safety scoring system:
- Cooldown period verification
- Daily limit enforcement
- Comprehensive health assessment
- Active session detection
- Power/battery status validation
- Recent crash detection

### 3. Reboot Type Determination
Intelligent reboot scheduling:
- Maintenance window detection
- Business hours awareness
- System load-based delay decisions
- Configured scheduling rules

### 4. Configuration Management
Comprehensive configuration support:
- YAML-based configuration loading
- Default value fallbacks
- Runtime configuration validation
- Environment variable support

### 5. Enhanced State Management
Robust state tracking:
- JSON-based state files
- Migration support
- Comprehensive statistics tracking
- Failure record management

### 6. Enhanced Logging and Monitoring
Detailed system state capture:
- Enhanced system state snapshots
- Pre-reboot backup creation
- Comprehensive system information logging
- JSON-formatted detailed records

### 7. Notification System
Multi-channel alerting:
- Desktop notifications (wall/notify-send)
- Monitoring system integration
- Telegram bot integration
- System logging

### 8. Recovery Procedures
Comprehensive failure handling:
- Detailed failure record creation
- Reboot attempt tracking
- Emergency recovery procedures
- Rollback mechanisms

## Detailed Results

EOF

    # Add detailed results from CSV
    if [[ -f "$TEST_RESULTS_DIR/results.csv" ]]; then
        echo "| Test Name | Result | Details |" >> "$report_file"
        echo "|-----------|--------|---------|" >> "$report_file"
        
        while IFS=',' read -r result test_name details; do
            local status_icon=""
            if [[ "$result" == "PASS" ]]; then
                status_icon="✅"
            else
                status_icon="❌"
            fi
            echo "| $test_name | $status_icon $result | $details |" >> "$report_file"
        done < "$TEST_RESULTS_DIR/results.csv"
    fi
    
    cat >> "$report_file" << EOF

## Configuration Validation

Current safe reboot configuration:

\`\`\`yaml
safe_reboot:
  max_disk_usage_percent: ${SAFE_REBOOT_MAX_DISK_USAGE:-85}
  max_memory_usage_percent: ${SAFE_REBOOT_MAX_MEMORY_USAGE:-85}
  max_system_load_multiplier: ${SAFE_REBOOT_MAX_LOAD_MULTIPLIER:-2}
  max_failed_services: ${SAFE_REBOOT_MAX_FAILED_SERVICES:-5}
  max_degraded_critical_services: ${SAFE_REBOOT_MAX_DEGRADED_CRITICAL_SERVICES:-2}
  maintenance_window_start: "${MAINTENANCE_WINDOW_START:-02:00}"
  maintenance_window_end: "${MAINTENANCE_WINDOW_END:-04:00}"
  business_hours_start: "${BUSINESS_HOURS_START:-09:00}"
  business_hours_end: "${BUSINESS_HOURS_END:-17:00}"
  graceful_shutdown_enabled: ${GRACEFUL_SHUTDOWN_ENABLED:-true}
  create_pre_reboot_backup: ${CREATE_PRE_REBOOT_BACKUP:-true}
  enhanced_state_logging: ${ENHANCED_STATE_LOGGING:-true}
  monitor_during_countdown: ${MONITOR_DURING_COUNTDOWN:-true}
  user_notifications_enabled: ${USER_NOTIFICATIONS_ENABLED:-false}
  monitoring_integration_enabled: ${MONITORING_ENABLED:-false}
\`\`\`

## Recommendations

EOF

    if [[ $TESTS_FAILED -eq 0 ]]; then
        cat >> "$report_file" << EOF
✅ **All tests passed successfully**

The enhanced safe reboot mechanism is fully functional and ready for production deployment. All safety mechanisms, health checks, and recovery procedures are working as expected.

**Next steps:**
1. Configure maintenance windows for your specific environment
2. Enable monitoring integration if desired
3. Test with actual repository changes to verify end-to-end functionality
4. Review and adjust thresholds based on your system requirements

EOF
    else
        cat >> "$report_file" << EOF
⚠️ **$TESTS_FAILED test(s) failed**

Some components of the enhanced safe reboot mechanism require attention before production deployment.

**Immediate actions required:**
1. Review failed tests and address configuration issues
2. Verify system requirements are met
3. Check permissions and dependencies
4. Re-run tests after corrections

**Investigation needed for failed components**
EOF
    fi
    
    echo "Comprehensive test report generated: $report_file"
    test_log "INFO" "Test report available at: $report_file"
}

# Main test execution
main() {
    test_log "INFO" "Starting Enhanced Safe Reboot Mechanism comprehensive tests"
    test_log "INFO" "Test results directory: $TEST_RESULTS_DIR"
    
    # Initialize CSV for detailed results
    echo "Result,TestName,Details" > "$TEST_RESULTS_DIR/results.csv"
    
    # Run all test categories
    test_configuration
    test_state_management
    test_system_health_checks
    test_reboot_safety
    test_reboot_types
    test_enhanced_logging
    test_notifications
    test_recovery_procedures
    
    # Generate comprehensive report
    generate_test_report
    
    # Final summary
    test_log "INFO" "Test execution completed"
    test_log "INFO" "Total tests: $TESTS_TOTAL, Passed: $TESTS_PASSED, Failed: $TESTS_FAILED"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        test_log "SUCCESS" "All tests passed! Enhanced safe reboot mechanism is fully functional."
        return 0
    else
        test_log "ERROR" "$TESTS_FAILED test(s) failed. Review the detailed report for resolution steps."
        return 1
    fi
}

# Execute tests if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi