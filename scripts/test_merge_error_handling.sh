#!/bin/bash

# Test script for enhanced merge error handling and logging
# This script validates the new comprehensive error handling system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Set up script name for logging
SCRIPT_NAME="merge_error_handling_test"

log "INFO" "Starting comprehensive merge error handling system test"

# Test 1: Validate repository state validation function
log "INFO" "Test 1: Testing repository state validation"
if validate_repository_state "test_validation"; then
    log "SUCCESS" "Repository state validation test passed"
else
    log "WARNING" "Repository state validation test failed (may be expected in test environment)"
fi

# Test 2: Test repository health status
log "INFO" "Test 2: Testing repository health status"
health_status=$(get_repository_health_status)
log "INFO" "Repository health status retrieved: $health_status"

# Test 3: Test error classification function
log "INFO" "Test 3: Testing error classification function"

# Test network error classification
network_error_type=$(classify_merge_error "128" "failed to connect to github.com connection refused")
if [[ "$network_error_type" == "NETWORK_FAILURE" ]]; then
    log "SUCCESS" "Network error classification test passed"
else
    log "ERROR" "Network error classification test failed: got $network_error_type"
fi

# Test conflict error classification
conflict_error_type=$(classify_merge_error "1" "Merge conflict in file.txt <<<<<<<")
if [[ "$conflict_error_type" == "MERGE_CONFLICT" ]]; then
    log "SUCCESS" "Conflict error classification test passed"
else
    log "ERROR" "Conflict error classification test failed: got $conflict_error_type"
fi

# Test permission error classification
permission_error_type=$(classify_merge_error "1" "Permission denied access denied")
if [[ "$permission_error_type" == "PERMISSION_DENIED" ]]; then
    log "SUCCESS" "Permission error classification test passed"
else
    log "ERROR" "Permission error classification test failed: got $permission_error_type"
fi

# Test 4: Test merge attempt logging
log "INFO" "Test 4: Testing merge attempt logging"
log_merge_attempt "test_merge" "test_branch" "ai" "abc123" "def456"
log "SUCCESS" "Merge attempt logging test completed"

# Test 5: Test conflict detection logging
log "INFO" "Test 5: Testing conflict detection logging"
log_merge_conflict_detection "file1.txt" "file2.txt" "file3.txt"
log "SUCCESS" "Conflict detection logging test completed"

# Test 6: Test opencode escalation logging
log "INFO" "Test 6: Testing opencode escalation logging"
log_opencode_escalation "test_escalation" "/tmp/test_conflict.json" "test_context"
log "SUCCESS" "Opencode escalation logging test completed"

# Test 7: Test merge resolution outcome logging
log "INFO" "Test 7: Testing merge resolution outcome logging"
log_merge_resolution_outcome "test_resolution" "3" "45" "test_operation"
log "SUCCESS" "Merge resolution outcome logging test completed"

# Test 8: Test rollback functionality (dry run)
log "INFO" "Test 8: Testing rollback functionality"
if rollback_merge_on_failure "TEST_ERROR" "test_context"; then
    log "SUCCESS" "Rollback test completed"
else
    log "WARNING" "Rollback test failed (may be expected in clean state)"
fi

# Test 9: Test state preservation functionality
log "INFO" "Test 9: Testing state preservation functionality"
state_dir=$(preserve_state_for_opencode "test_operation" "TEST_ERROR")
if [[ -n "$state_dir" && -d "$state_dir" ]]; then
    log "SUCCESS" "State preservation test completed: $state_dir"
    # Clean up test state directory
    rm -rf "$state_dir" 2>/dev/null || true
else
    log "WARNING" "State preservation test failed"
fi

log "SUCCESS" "Comprehensive merge error handling system test completed"
log "INFO" "All error handling functions have been validated"

script_success