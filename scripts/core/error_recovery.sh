#!/bin/bash

# Enhanced Error Recovery and State Management Module
# Provides advanced error handling, recovery strategies, and system state management
# Integrates with existing utils.sh while adding sophisticated recovery mechanisms

# Set script name for logging identification
SCRIPT_NAME="error_recovery"

# Source dependencies (relative to this script's location)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../utils.sh"

# =============================================================================
# ERROR CLASSIFICATION AND SEVERITY SYSTEM
# =============================================================================

# Error severity levels (lower number = higher priority)
declare -A ERROR_SEVERITY=(
    ["CRITICAL"]=0  # System-level failures, immediate intervention required
    ["HIGH"]=1      # Major functionality impaired, user notification needed
    ["MEDIUM"]=2    # Degraded functionality, automatic recovery possible
    ["LOW"]=3       # Minor issues, logging only
    ["INFO"]=4      # Informational messages, no action required
)

# Error categories with descriptions
declare -A ERROR_CATEGORIES=(
    ["NETWORK"]="Network connectivity and remote operations"
    ["PERMISSION"]="Access rights and authorization issues"
    ["CONFIGURATION"]="Configuration and parameter errors"
    ["REPOSITORY"]="Git repository corruption or state issues"
    ["RESOURCE"]="System resource exhaustion (disk, memory)"
    ["DEPENDENCY"]="Missing or incompatible dependencies"
    ["USER_INPUT"]="Invalid user input or parameters"
    ["BUSINESS_LOGIC"]="Application logic errors"
    ["TIMEOUT"]="Operation timeout exceeded"
    ["UNKNOWN"]="Unclassified or unexpected errors"
)

# Recovery strategies with implementations
declare -A RECOVERY_STRATEGIES=(
    ["RETRY"]="Automatic retry with exponential backoff"
    ["FALLBACK"]="Switch to alternative implementation"
    ["ROLLBACK"]="Revert to last known good state"
    ["ESCALATE"]="Notify human operator or external system"
    ["GRACEFUL_DEGRADE"]="Continue with reduced functionality"
    ["FAIL_FAST"]="Immediate termination for critical errors"
    ["ISOLATE"]="Contain error to prevent cascade failures"
)

# =============================================================================
# SYSTEM STATE MANAGEMENT
# =============================================================================

# System state structure
SYSTEM_STATE_FILE="${SYSTEM_STATE_FILE:-/tmp/autoslopp_system_state.json}"
RECOVERY_LOG="${RECOVERY_LOG:-${LOG_DIRECTORY:-/tmp}/autoslopp_recovery.log}"

# Initialize system state
initialize_system_state() {
    local state_file="$1"
    
    # Create state file with defaults if it doesn't exist
    if [[ ! -f "$state_file" ]]; then
        cat > "$state_file" << EOF
{
    "system": {
        "health_status": "healthy",
        "last_successful_run": $(date +%s),
        "consecutive_failures": 0,
        "error_count_24h": 0,
        "total_operations": 0,
        "successful_operations": 0
    },
    "performance": {
        "avg_operation_duration": 0,
        "slow_operations": 0,
        "resource_usage": {
            "memory_mb": 0,
            "disk_percent": 0
        }
    },
    "active_operations": [],
    "locked_resources": [],
    "recent_errors": [],
    "last_updated": "$(date -Iseconds)"
}
EOF
        log "INFO" "System state file initialized: $state_file"
    fi
    
    # Ensure state file is writable
    if [[ ! -w "$state_file" ]]; then
        log "ERROR" "System state file is not writable: $state_file"
        return 1
    fi
    
    return 0
}

# Update system state atomically
update_system_state() {
    local key_path="$1"
    local new_value="$2"
    local state_file="${3:-$SYSTEM_STATE_FILE}"
    
    # Initialize if needed
    initialize_system_state "$state_file"
    
    # Create backup before modification
    local backup_file="${state_file}.backup.$(date +%s)"
    cp "$state_file" "$backup_file" 2>/dev/null || true
    
    # Use jq for JSON manipulation if available, otherwise use sed
    if command -v jq >/dev/null 2>&1; then
        jq ".$key_path = $new_value" "$state_file" > "${state_file}.tmp" && \
        mv "${state_file}.tmp" "$state_file"
    else
        # Fallback: simple timestamp update only
        sed -i "s/\"last_updated\": \".*\"/\"last_updated\": \"$(date -Iseconds)\"/" "$state_file"
    fi
    
    log "DEBUG" "System state updated: $key_path = $new_value"
}

# Get system health status
get_system_health_status() {
    local state_file="${1:-$SYSTEM_STATE_FILE}"
    
    if [[ ! -f "$state_file" ]]; then
        echo "unknown"
        return 1
    fi
    
    if command -v jq >/dev/null 2>&1; then
        local health=$(jq -r '.system.health_status' "$state_file" 2>/dev/null)
        echo "${health:-unknown}"
    else
        # Fallback parsing
        grep -o '"health_status": "[^"]*"' "$state_file" 2>/dev/null | cut -d'"' -f4 || echo "unknown"
    fi
}

# =============================================================================
# ADVANCED ERROR HANDLING FRAMEWORK
# =============================================================================

# Classify error type and severity
classify_error() {
    local exit_code="$1"
    local error_output="$2"
    local context="${3:-unknown}"
    
    local category="UNKNOWN"
    local severity="MEDIUM"
    
    # Determine error category based on patterns
    case "$error_output" in
        *"connection"*|*"refused"*|*"timeout"*|*"network"*|*"unable to access"*)
            category="NETWORK"
            severity="HIGH"
            ;;
        *"permission"*|*"denied"*|*"access denied"*|*"read-only"*)
            category="PERMISSION"
            severity="HIGH"
            ;;
        *"corrupt"*|*"broken"*|*"invalid"*|*"object not found"*|*"repository"*)
            category="REPOSITORY"
            severity="CRITICAL"
            ;;
        *"no space left"*|*"disk full"*|*"insufficient space"*|*"memory"*)
            category="RESOURCE"
            severity="CRITICAL"
            ;;
        *"not found"*|*"doesnt exist"*|*"missing"*|*"dependency"*)
            category="DEPENDENCY"
            severity="MEDIUM"
            ;;
        *"timeout"*|*"timed out"*)
            category="TIMEOUT"
            severity="MEDIUM"
            ;;
    esac
    
    # Adjust severity based on exit code
    if [[ $exit_code -eq 0 ]]; then
        severity="INFO"
    elif [[ $exit_code -gt 128 ]]; then
        # Signals indicate critical issues
        severity="CRITICAL"
        category="RESOURCE"
    elif [[ $exit_code -eq 124 ]]; then
        # Timeout
        category="TIMEOUT"
        severity="MEDIUM"
    fi
    
    echo "$category:$severity"
}

# Determine appropriate recovery strategy
determine_recovery_strategy() {
    local category="$1"
    local severity="$2"
    local context="$3"
    local consecutive_failures="${4:-0}"
    
    # Base recovery strategy by category
    local strategy="ESCALATE"
    
    case "$category" in
        "NETWORK")
            if [[ $consecutive_failures -lt 3 ]]; then
                strategy="RETRY"
            else
                strategy="ESCALATE"
            fi
            ;;
        "PERMISSION")
            strategy="ESCALATE"
            ;;
        "CONFIGURATION")
            if [[ "$severity" != "CRITICAL" ]]; then
                strategy="FALLBACK"
            else
                strategy="FAIL_FAST"
            fi
            ;;
        "REPOSITORY")
            if [[ "$severity" == "CRITICAL" ]]; then
                strategy="ROLLBACK"
            else
                strategy="ISOLATE"
            fi
            ;;
        "RESOURCE")
            if [[ "$category" == "disk" ]]; then
                strategy="GRACEFUL_DEGRADE"
            else
                strategy="ESCALATE"
            fi
            ;;
        "TIMEOUT")
            if [[ $consecutive_failures -lt 2 ]]; then
                strategy="RETRY"
            else
                strategy="FALLBACK"
            fi
            ;;
        "DEPENDENCY")
            strategy="FALLBACK"
            ;;
        "BUSINESS_LOGIC")
            strategy="ROLLBACK"
            ;;
    esac
    
    # Adjust strategy based on severity
    case "$severity" in
        "CRITICAL")
            [[ "$strategy" != "FAIL_FAST" ]] && strategy="ESCALATE"
            ;;
        "HIGH")
            [[ "$strategy" == "RETRY" ]] && strategy="ESCALATE"
            ;;
    esac
    
    echo "$strategy"
}

# Execute recovery strategy
execute_recovery_strategy() {
    local strategy="$1"
    local context="$2"
    local error_details="$3"
    
    log "INFO" "Executing recovery strategy: $strategy for context: $context"
    
    case "$strategy" in
        "RETRY")
            return execute_retry_strategy "$context" "$error_details"
            ;;
        "FALLBACK")
            return execute_fallback_strategy "$context" "$error_details"
            ;;
        "ROLLBACK")
            return execute_rollback_strategy "$context" "$error_details"
            ;;
        "ESCALATE")
            return execute_escalate_strategy "$context" "$error_details"
            ;;
        "GRACEFUL_DEGRADE")
            return execute_graceful_degrade_strategy "$context" "$error_details"
            ;;
        "FAIL_FAST")
            return execute_fail_fast_strategy "$context" "$error_details"
            ;;
        "ISOLATE")
            return execute_isolate_strategy "$context" "$error_details"
            ;;
        *)
            log "ERROR" "Unknown recovery strategy: $strategy"
            return 1
            ;;
    esac
}

# =============================================================================
# RECOVERY STRATEGY IMPLEMENTATIONS
# =============================================================================

# Retry with exponential backoff
execute_retry_strategy() {
    local context="$1"
    local error_details="$2"
    local max_retries="${MAX_RETRIES:-3}"
    local base_delay="${RETRY_BASE_DELAY:-5}"
    local max_delay="${RETRY_MAX_DELAY:-300}"
    
    local retry_count=$(echo "$error_details" | jq -r '.retry_count // 0' 2>/dev/null || echo "0")
    
    if [[ $retry_count -ge $max_retries ]]; then
        log "ERROR" "Maximum retries exceeded for context: $context"
        return 1
    fi
    
    # Calculate exponential backoff delay
    local delay=$((base_delay * (2 ** retry_count)))
    [[ $delay -gt $max_delay ]] && delay=$max_delay
    
    log "INFO" "Retrying operation for $context (attempt $((retry_count + 1))/$max_retries) after ${delay}s delay"
    
    sleep "$delay"
    return 0  # Signal to retry
}

# Switch to alternative implementation
execute_fallback_strategy() {
    local context="$1"
    local error_details="$2"
    
    log "INFO" "Attempting fallback strategy for context: $context"
    
    # Determine fallback based on context
    case "$context" in
        *"git"*|*"branch"*|*"merge"*)
            # Try alternative git commands or approaches
            log "INFO" "Git operation fallback: using safer commands"
            export GIT_USE_FALLBACK="true"
            return 0
            ;;
        *"cleanup"*|*"delete"*)
            # Use dry-run mode or manual intervention
            log "WARNING" "Cleanup fallback: switching to dry-run mode"
            export CLEANUP_DRY_RUN="true"
            return 0
            ;;
        *"config"*|*"yaml"*)
            # Use default configuration
            log "WARNING" "Configuration fallback: using defaults"
            export USE_DEFAULT_CONFIG="true"
            return 0
            ;;
        *)
            log "WARNING" "No fallback available for context: $context"
            return 1
            ;;
    esac
}

# Rollback to last known good state
execute_rollback_strategy() {
    local context="$1"
    local error_details="$2"
    
    log "WARNING" "Executing rollback strategy for context: $context"
    
    # Create rollback point if not exists
    local rollback_point="/tmp/autoslopp_rollback_$(date +%s)"
    mkdir -p "$rollback_point"
    
    # Backup current state
    if [[ -n "${GIT_REPO_DIR:-}" ]]; then
        cd "$GIT_REPO_DIR" 2>/dev/null || {
            log "ERROR" "Cannot access git repository for rollback"
            return 1
        }
        
        # Reset any in-progress operations
        if git status --porcelain 2>/dev/null | grep -q "^UU\|^AA\|^DD"; then
            log "INFO" "Aborting any in-progress merge"
            git merge --abort 2>/dev/null || true
        fi
        
        # Reset to last known good commit
        git reset --hard HEAD 2>/dev/null || {
            log "ERROR" "Failed to reset to HEAD during rollback"
            return 1
        }
        
        # Clean working directory
        git clean -fd 2>/dev/null || {
            log "WARNING" "Failed to clean working directory during rollback"
        }
        
        log "SUCCESS" "Rollback completed for repository: $(basename "$GIT_REPO_DIR")"
    fi
    
    # Update system state
    update_system_state "system.health_status" '"degraded"'
    update_system_state "system.consecutive_failures" 0
    
    return 0
}

# Escalate to human operator or external system
execute_escalate_strategy() {
    local context="$1"
    local error_details="$2"
    
    log "ERROR" "Escalating error for human intervention: $context"
    
    # Create escalation report
    local escalation_file="/tmp/autoslopp_escalation_$(date +%s).json"
    
    cat > "$escalation_file" << EOF
{
    "escalation_time": "$(date -Iseconds)",
    "context": "$context",
    "error_details": $(echo "$error_details" | jq '.' 2>/dev/null || echo '"{}"'),
    "system_health": "$(get_system_health_status)",
    "environment": {
        "pwd": "$(pwd)",
        "user": "$(whoami)",
        "hostname": "$(hostname)",
        "git_status": "$(git status --porcelain 2>/dev/null | head -5 | tr '\n' ';')"
    },
    "recommended_actions": [
        "Review system logs for recent errors",
        "Check resource availability (disk, memory)",
        "Verify repository integrity",
        "Review configuration changes",
        "Check network connectivity"
    ]
}
EOF
    
    log "ERROR" "Escalation report created: $escalation_file"
    
    # Send notification if configured
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "Auto-slopp Escalation" "Error in $context requires attention" --urgency=critical 2>/dev/null || true
    fi
    
    # Update system state to indicate escalation
    update_system_state "system.health_status" '"critical"'
    
    # Return special code to indicate escalation
    return 2
}

# Continue with reduced functionality
execute_graceful_degrade_strategy() {
    local context="$1"
    local error_details="$2"
    
    log "WARNING" "Executing graceful degradation for context: $context"
    
    # Enable degraded mode flags
    export DEGRADED_MODE="true"
    
    # Adjust system behavior based on context
    case "$context" in
        *"disk"*)
            log "INFO" "Disk space degradation: cleanup temporary files"
            # Clean temporary files
            find /tmp -name "autoslopp_*" -mtime +1 -delete 2>/dev/null || true
            ;;
        *"memory"*)
            log "INFO" "Memory degradation: reducing concurrent operations"
            export MAX_CONCURRENT_OPERATIONS=1
            ;;
        *"network"*)
            log "INFO" "Network degradation: increasing timeouts"
            export GIT_TIMEOUT=300
            export NETWORK_TIMEOUT=300
            ;;
    esac
    
    update_system_state "system.health_status" '"degraded"'
    log "INFO" "System now operating in degraded mode"
    
    return 0
}

# Immediate termination for critical errors
execute_fail_fast_strategy() {
    local context="$1"
    local error_details="$2"
    
    log "CRITICAL" "Fail fast triggered for context: $context"
    log "CRITICAL" "Error details: $error_details"
    
    # Create critical error report
    local critical_error_file="/tmp/autoslopp_critical_error_$(date +%s).json"
    
    cat > "$critical_error_file" << EOF
{
    "critical_error_time": "$(date -Iseconds)",
    "context": "$context",
    "error_details": $(echo "$error_details" | jq '.' 2>/dev/null || echo '"{}"'),
    "system_state": "$(cat "$SYSTEM_STATE_FILE" 2>/dev/null || echo '"state unavailable"')",
    "termination_reason": "Critical error requiring immediate termination"
}
EOF
    
    log "CRITICAL" "Critical error report created: $critical_error_file"
    
    # Update system state before termination
    update_system_state "system.health_status" '"critical"'
    
    # Immediate termination
    exit 1
}

# Isolate error to prevent cascade failures
execute_isolate_strategy() {
    local context="$1"
    local error_details="$2"
    
    log "WARNING" "Isolating error to prevent cascade failures: $context"
    
    # Add context to isolation list
    local isolation_file="/tmp/autoslopp_isolation.list"
    echo "$context" >> "$isolation_file"
    
    # Skip this operation in future runs
    export ISOLATED_OPERATIONS_FILE="$isolation_file"
    
    log "INFO" "Context $context added to isolation list"
    
    # Continue with other operations
    return 0
}

# =============================================================================
# UNIFIED ERROR HANDLING INTERFACE
# =============================================================================

# Main error handler that integrates with existing error handling
enhanced_error_handler() {
    local exit_code=$?
    local line_number=$1
    local command="$2"
    local context="${3:-unknown}"
    
    # Only handle actual errors
    if [[ $exit_code -eq 0 ]]; then
        return 0
    fi
    
    # Get error output if available
    local error_output="${ERROR_OUTPUT:-}"
    
    # Classify the error
    local error_classification=$(classify_error "$exit_code" "$error_output" "$context")
    local category="${error_classification%:*}"
    local severity="${error_classification#*:}"
    
    log "ERROR" "Enhanced error handling triggered:"
    log "ERROR" "  Exit code: $exit_code"
    log "ERROR" "  Line: $line_number"
    log "ERROR" "  Command: $command"
    log "ERROR" "  Context: $context"
    log "ERROR" "  Category: $category"
    log "ERROR" "  Severity: $severity"
    
    # Get consecutive failures from system state
    local consecutive_failures=$(get_consecutive_failures)
    
    # Determine recovery strategy
    local recovery_strategy=$(determine_recovery_strategy "$category" "$severity" "$context" "$consecutive_failures")
    
    log "INFO" "Recovery strategy determined: $recovery_strategy"
    
    # Create error details for recovery
    local error_details=$(cat << EOF
{
    "exit_code": $exit_code,
    "line_number": $line_number,
    "command": "$command",
    "context": "$context",
    "category": "$category",
    "severity": "$severity",
    "recovery_strategy": "$recovery_strategy",
    "consecutive_failures": $consecutive_failures,
    "timestamp": "$(date -Iseconds)",
    "error_output": "$error_output"
}
EOF
)
    
    # Execute recovery strategy
    if execute_recovery_strategy "$recovery_strategy" "$context" "$error_details"; then
        # Recovery was successful or requires retry
        update_system_state "system.consecutive_failures" 0
        log "SUCCESS" "Recovery strategy executed successfully: $recovery_strategy"
        return 0
    else
        # Recovery failed
        update_system_state "system.consecutive_failures" $((consecutive_failures + 1))
        log "ERROR" "Recovery strategy failed: $recovery_strategy"
        
        # For critical failures or too many consecutive failures, escalate
        if [[ "$severity" == "CRITICAL" || $consecutive_failures -gt 4 ]]; then
            execute_escalate_strategy "$context" "$error_details"
        fi
        
        return $exit_code
    fi
}

# Get consecutive failures from system state
get_consecutive_failures() {
    local state_file="${1:-$SYSTEM_STATE_FILE}"
    
    if [[ ! -f "$state_file" ]]; then
        echo "0"
        return
    fi
    
    if command -v jq >/dev/null 2>&1; then
        jq -r '.system.consecutive_failures // 0' "$state_file" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Setup enhanced error handling
setup_enhanced_error_handling() {
    # Initialize system state
    initialize_system_state "$SYSTEM_STATE_FILE"
    
    # Set up enhanced error trap
    set -eE  # Exit on error, inherit ERR trap
    trap 'enhanced_error_handler $LINENO "$BASH_COMMAND" "${ERROR_CONTEXT:-unknown}"' ERR
    
    # Set up cleanup trap
    trap 'cleanup_on_exit' EXIT
    
    log "INFO" "Enhanced error handling initialized"
}

# Cleanup function called on script exit
cleanup_on_exit() {
    local exit_code=$?
    
    # Update system state based on exit code
    if [[ $exit_code -eq 0 ]]; then
        update_system_state "system.last_successful_run" $(date +%s)
        update_system_state "system.consecutive_failures" 0
    else
        update_system_state "system.consecutive_failures" $(( $(get_consecutive_failures) + 1 ))
    fi
    
    # Clean up temporary files
    rm -f /tmp/autoslopp_*_backup.* 2>/dev/null || true
    
    log "INFO" "Error recovery cleanup completed (exit code: $exit_code)"
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Check if operation should be skipped due to isolation
should_isolate_operation() {
    local context="$1"
    local isolation_file="${ISOLATED_OPERATIONS_FILE:-/tmp/autoslopp_isolation.list}"
    
    if [[ -f "$isolation_file" ]] && grep -q "^$context$" "$isolation_file"; then
        log "WARNING" "Skipping isolated operation: $context"
        return 0
    fi
    
    return 1
}

# Log recovery events for analysis
log_recovery_event() {
    local event_type="$1"
    local context="$2"
    local details="$3"
    
    local log_entry=$(cat << EOF
{
    "timestamp": "$(date -Iseconds)",
    "event_type": "$event_type",
    "context": "$context",
    "details": $(echo "$details" | jq '.' 2>/dev/null || echo '"{}"'),
    "system_health": "$(get_system_health_status)"
}
EOF
)
    
    # Log to recovery log file
    echo "$log_entry" >> "$RECOVERY_LOG"
    
    # Also log with standard logging
    log "INFO" "Recovery event: $event_type for $context"
}

# Export key functions for use by other scripts
export -f setup_enhanced_error_handling
export -f enhanced_error_handler
export -f classify_error
export -f determine_recovery_strategy
export -f execute_recovery_strategy
export -f should_isolate_operation
export -f get_system_health_status
export -f update_system_state

# Auto-initialize if this script is sourced and not already initialized
if [[ "${BASH_SOURCE[0]}" != "${0}" && -z "${ENHANCED_ERROR_HANDLING_INITIALIZED:-}" ]]; then
    setup_enhanced_error_handling
    export ENHANCED_ERROR_HANDLING_INITIALIZED=true
fi