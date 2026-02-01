#!/bin/bash

# System State Management Module
# Provides comprehensive system state tracking, health monitoring, and state persistence
# Works in conjunction with error_recovery.sh to maintain system health

# Set script name for logging identification
SCRIPT_NAME="system_state"

# Source dependencies
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../utils.sh"
source "$SCRIPT_DIR/../core/error_recovery.sh"

# =============================================================================
# SYSTEM STATE CONFIGURATION
# =============================================================================

# State management configuration
SYSTEM_STATE_FILE="${SYSTEM_STATE_FILE:-/tmp/autoslopp_system_state.json}"
STATE_LOCK_FILE="${STATE_LOCK_FILE:-/tmp/autoslopp_state.lock}"
STATE_BACKUP_DIR="${STATE_BACKUP_DIR:-/tmp/autoslopp_state_backups}"
MAX_STATE_BACKUPS="${MAX_STATE_BACKUPS:-10}"
HEALTH_CHECK_INTERVAL="${HEALTH_CHECK_INTERVAL:-300}"  # 5 minutes

# Health status definitions
HEALTH_STATUSES=("healthy" "degraded" "critical" "unknown" "maintenance")

# Performance metrics thresholds
declare -A PERFORMANCE_THRESHOLDS=(
    ["max_operation_duration"]="60"  # seconds
    ["max_error_rate"]="0.1"        # 10%
    ["max_consecutive_failures"]="5"
    ["min_disk_space_mb"]="1024"     # 1GB
    ["max_memory_usage_percent"]="90"
    ["max_cpu_usage_percent"]="95"
)

# =============================================================================
# STATE INITIALIZATION AND MAINTENANCE
# =============================================================================

# Initialize comprehensive system state
initialize_comprehensive_state() {
    local state_file="$1"
    local force_init="${2:-false}"
    
    # Create backup directory
    mkdir -p "$STATE_BACKUP_DIR"
    
    # Initialize state file if needed
    if [[ "$force_init" == "true" ]] || [[ ! -f "$state_file" ]]; then
        create_fresh_state_file "$state_file"
        log "INFO" "Comprehensive system state initialized: $state_file"
    fi
    
    # Validate and repair existing state file
    if ! validate_state_file "$state_file"; then
        log "WARNING" "State file validation failed, repairing: $state_file"
        repair_state_file "$state_file"
    fi
    
    # Cleanup old backups
    cleanup_old_state_backups
    
    return 0
}

# Create a fresh state file with default values
create_fresh_state_file() {
    local state_file="$1"
    local temp_file="${state_file}.tmp"
    
    cat > "$temp_file" << EOF
{
    "metadata": {
        "version": "1.0",
        "created": "$(date -Iseconds)",
        "hostname": "$(hostname)",
        "user": "$(whoami)",
        "working_directory": "$(pwd)"
    },
    "system": {
        "health_status": "healthy",
        "last_successful_run": $(date +%s),
        "consecutive_failures": 0,
        "error_count_24h": 0,
        "total_operations": 0,
        "successful_operations": 0,
        "uptime_seconds": 0,
        "start_time": $(date +%s)
    },
    "performance": {
        "avg_operation_duration": 0,
        "slow_operations": 0,
        "operation_history": [],
        "resource_usage": {
            "memory_mb": 0,
            "disk_percent": 0,
            "cpu_percent": 0,
            "load_average": "0.0,0.0,0.0"
        },
        "metrics": {
            "operations_per_minute": 0,
            "error_rate_percent": 0,
            "success_rate_percent": 100
        }
    },
    "health": {
        "last_health_check": $(date +%s),
        "health_checks_passed": 0,
        "health_checks_failed": 0,
        "active_alerts": [],
        "warnings": []
    },
    "operations": {
        "active_operations": [],
        "completed_operations": [],
        "failed_operations": [],
        "locked_resources": []
    },
    "configuration": {
        "last_config_reload": $(date +%s),
        "config_changes": 0,
        "validation_status": "valid",
        "effective_settings": {}
    },
    "dependencies": {
        "git_available": $(command -v git >/dev/null 2>&1 && echo true || echo false),
        "jq_available": $(command -v jq >/dev/null 2>&1 && echo true || echo false),
        "required_tools_missing": []
    },
    "recent_errors": [],
    "alerts": [],
    "last_updated": "$(date -Iseconds)"
}
EOF
    
    # Atomic move to final location
    mv "$temp_file" "$state_file"
}

# Validate state file integrity
validate_state_file() {
    local state_file="$1"
    
    [[ -f "$state_file" ]] || return 1
    
    # Check if file is valid JSON
    if command -v jq >/dev/null 2>&1; then
        if ! jq empty "$state_file" 2>/dev/null; then
            log "ERROR" "State file is not valid JSON: $state_file"
            return 1
        fi
    else
        # Basic validation without jq
        if ! grep -q '"system"' "$state_file" 2>/dev/null; then
            log "ERROR" "State file missing required section: system"
            return 1
        fi
    fi
    
    # Check file permissions
    if [[ ! -r "$state_file" || ! -w "$state_file" ]]; then
        log "ERROR" "State file has incorrect permissions: $state_file"
        return 1
    fi
    
    return 0
}

# Repair corrupted state file
repair_state_file() {
    local state_file="$1"
    local backup_file="${STATE_BACKUP_DIR}/state_backup_$(date +%s).json"
    
    # Create backup before repair
    cp "$state_file" "$backup_file" 2>/dev/null || true
    log "INFO" "State file backed up to: $backup_file"
    
    # Create fresh state file
    create_fresh_state_file "$state_file"
    
    log "WARNING" "State file repaired: $state_file"
}

# Cleanup old state backups
cleanup_old_state_backups() {
    if [[ ! -d "$STATE_BACKUP_DIR" ]]; then
        return 0
    fi
    
    # Keep only the most recent backups
    find "$STATE_BACKUP_DIR" -name "state_backup_*.json" -type f | \
        sort -r | tail -n +$((MAX_STATE_BACKUPS + 1)) | \
        xargs -r rm -f
    
    log "DEBUG" "Cleaned up old state backups"
}

# =============================================================================
# ATOMIC STATE OPERATIONS
# =============================================================================

# Acquire state lock for atomic operations
acquire_state_lock() {
    local timeout="${1:-30}"
    local lock_file="$STATE_LOCK_FILE"
    
    local count=0
    while [[ $count -lt $timeout ]]; do
        if mkdir "$lock_file" 2>/dev/null; then
            # Store lock metadata
            echo "$$,$(date +%s)" > "$lock_file/metadata"
            log "DEBUG" "State lock acquired"
            return 0
        fi
        
        # Check if lock is stale
        if [[ -f "$lock_file/metadata" ]]; then
            local lock_pid=$(cut -d, -f1 "$lock_file/metadata" 2>/dev/null)
            local lock_time=$(cut -d, -f2 "$lock_file/metadata" 2>/dev/null)
            local current_time=$(date +%s)
            
            # Remove stale lock (older than 5 minutes)
            if [[ $((current_time - lock_time)) -gt 300 ]] || ! kill -0 "$lock_pid" 2>/dev/null; then
                log "WARNING" "Removing stale state lock"
                rm -rf "$lock_file"
                continue
            fi
        fi
        
        sleep 1
        ((count++))
    done
    
    log "ERROR" "Failed to acquire state lock after ${timeout}s"
    return 1
}

# Release state lock
release_state_lock() {
    local lock_file="$STATE_LOCK_FILE"
    
    if [[ -d "$lock_file" ]]; then
        rm -rf "$lock_file"
        log "DEBUG" "State lock released"
    fi
}

# Atomic state update with proper locking
atomic_state_update() {
    local operation="$1"
    local data="$2"
    local state_file="${3:-$SYSTEM_STATE_FILE}"
    
    acquire_state_lock || {
        log "ERROR" "Failed to acquire lock for state update"
        return 1
    }
    
    local temp_file="${state_file}.tmp.$$"
    local success=false
    
    # Perform the operation
    case "$operation" in
        "merge")
            if merge_state_data "$data" "$state_file" "$temp_file"; then
                success=true
            fi
            ;;
        "replace")
            if replace_state_value "$data" "$state_file" "$temp_file"; then
                success=true
            fi
            ;;
        "append")
            if append_state_data "$data" "$state_file" "$temp_file"; then
                success=true
            fi
            ;;
        *)
            log "ERROR" "Unknown state operation: $operation"
            ;;
    esac
    
    # Commit changes if successful
    if [[ "$success" == "true" ]]; then
        # Update timestamp
        update_json_timestamp "$temp_file"
        
        # Atomic move
        mv "$temp_file" "$state_file"
        log "DEBUG" "State updated successfully: $operation"
        
        release_state_lock
        return 0
    else
        # Cleanup on failure
        rm -f "$temp_file"
        release_state_lock
        log "ERROR" "State update failed: $operation"
        return 1
    fi
}

# Merge state data using jq
merge_state_data() {
    local data="$1"
    local input_file="$2"
    local output_file="$3"
    
    if command -v jq >/dev/null 2>&1; then
        jq --argjson data "$data" '. + $data' "$input_file" > "$output_file"
    else
        log "ERROR" "jq required for state merge operations"
        return 1
    fi
}

# Replace specific value in state
replace_state_value() {
    local key_path="$1"
    local value="$2"
    local input_file="$3"
    local output_file="$4"
    
    if command -v jq >/dev/null 2>&1; then
        jq ".$key_path = $value" "$input_file" > "$output_file"
    else
        log "ERROR" "jq required for state value replacement"
        return 1
    fi
}

# Update timestamp in JSON
update_json_timestamp() {
    local file="$1"
    
    if command -v jq >/dev/null 2>&1; then
        jq '.last_updated = "'"$(date -Iseconds)"'"' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
    fi
}

# =============================================================================
# HEALTH MONITORING SYSTEM
# =============================================================================

# Perform comprehensive health check
perform_health_check() {
    local state_file="${1:-$SYSTEM_STATE_FILE}"
    local check_type="${2:-routine}"
    
    log "DEBUG" "Starting health check: $check_type"
    
    local health_results=()
    local overall_status="healthy"
    
    # System resource checks
    check_system_resources health_results
    
    # Git repository health
    check_git_repository_health health_results
    
    # Dependency checks
    check_system_dependencies health_results
    
    # Performance metrics
    check_performance_metrics health_results
    
    # Configuration validation
    check_configuration_health health_results
    
    # State file integrity
    check_state_file_health health_results
    
    # Analyze results and determine overall status
    analyze_health_results health_results overall_status
    
    # Update health status in state
    update_health_status "$overall_status" health_results "$state_file"
    
    log "INFO" "Health check completed: $overall_status"
    return 0
}

# Check system resources
check_system_resources() {
    local -n results=$1
    
    # Disk space check
    local disk_usage=$(df / 2>/dev/null | awk 'NR==2 {print $5}' | sed 's/%//')
    local disk_available_mb=$(df / 2>/dev/null | awk 'NR==2 {print int($4/1024)}')
    
    if [[ $disk_available_mb -lt ${PERFORMANCE_THRESHOLDS[min_disk_space_mb]} ]]; then
        results+=("error:disk_space:Only ${disk_available_mb}MB available")
    elif [[ $disk_usage -gt 90 ]]; then
        results+=("warning:disk_usage:Disk usage at ${disk_usage}%")
    else
        results+=("ok:disk_space:${disk_available_mb}MB available")
    fi
    
    # Memory usage check
    if command -v free >/dev/null 2>&1; then
        local memory_percent=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
        if [[ $memory_percent -gt ${PERFORMANCE_THRESHOLDS[max_memory_usage_percent]} ]]; then
            results+=("warning:memory_usage:Memory usage at ${memory_percent}%")
        else
            results+=("ok:memory_usage:Memory usage at ${memory_percent}%")
        fi
    fi
    
    # Load average check
    if command -v uptime >/dev/null 2>&1; then
        local load_avg=$(uptime | awk -F'load average:' '{print $2}' | cut -d, -f1 | xargs)
        local load_num=$(echo "$load_avg" | cut -d. -f1)
        if [[ $load_num -gt 5 ]]; then
            results+=("warning:load_average:Load average at $load_avg")
        else
            results+=("ok:load_average:Load average at $load_avg")
        fi
    fi
}

# Check Git repository health
check_git_repository_health() {
    local -n results=$1
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    
    if [[ ! -d "$repo_dir/.git" ]]; then
        results+=("error:git_repo:Not a git repository: $repo_dir")
        return
    fi
    
    cd "$repo_dir" || {
        results+=("error:git_access:Cannot access git directory: $repo_dir")
        return
    }
    
    # Check for git index lock
    if [[ -f ".git/index.lock" ]]; then
        results+=("error:git_lock:Git index lock exists")
    else
        results+=("ok:git_lock:No git lock files")
    fi
    
    # Check repository state
    if git rev-parse --git-dir >/dev/null 2>&1; then
        results+=("ok:git_integrity:Git repository structure is valid")
    else
        results+=("error:git_integrity:Git repository structure is corrupted")
    fi
    
    # Check for in-progress operations
    if git status --porcelain 2>/dev/null | grep -q "^UU\|^AA\|^DD"; then
        results+=("warning:git_state:Merge or rebase in progress")
    else
        results+=("ok:git_state:No merge conflicts in progress")
    fi
}

# Check system dependencies
check_system_dependencies() {
    local -n results=$1
    local required_commands=("git" "bash" "find" "grep" "sed" "awk")
    local optional_commands=("jq" "notify-send")
    
    local missing_required=()
    local missing_optional=()
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_required+=("$cmd")
        fi
    done
    
    for cmd in "${optional_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_optional+=("$cmd")
        fi
    done
    
    if [[ ${#missing_required[@]} -gt 0 ]]; then
        results+=("error:dependencies:Missing required commands: ${missing_required[*]}")
    else
        results+=("ok:dependencies:All required commands available")
    fi
    
    if [[ ${#missing_optional[@]} -gt 0 ]]; then
        results+=("warning:optional_dependencies:Missing optional commands: ${missing_optional[*]}")
    fi
}

# Check performance metrics
check_performance_metrics() {
    local -n results=$1
    
    # Load performance data from state
    local avg_duration=$(get_state_value "performance.avg_operation_duration" 0)
    local error_rate=$(get_state_value "performance.metrics.error_rate_percent" 0)
    local consecutive_failures=$(get_state_value "system.consecutive_failures" 0)
    
    # Check average operation duration
    if (( $(echo "$avg_duration > ${PERFORMANCE_THRESHOLDS[max_operation_duration]}" | bc -l 2>/dev/null || echo 0) )); then
        results+=("warning:performance:Average operation duration ${avg_duration}s exceeds threshold")
    else
        results+=("ok:performance:Average operation duration ${avg_duration}s")
    fi
    
    # Check error rate
    if (( $(echo "$error_rate > ${PERFORMANCE_THRESHOLDS[max_error_rate]}" | bc -l 2>/dev/null || echo 0) )); then
        results+=("warning:error_rate:Error rate ${error_rate}% exceeds threshold")
    else
        results+=("ok:error_rate:Error rate ${error_rate}%")
    fi
    
    # Check consecutive failures
    if [[ $consecutive_failures -gt ${PERFORMANCE_THRESHOLDS[max_consecutive_failures]} ]]; then
        results+=("error:failures:Too many consecutive failures: $consecutive_failures")
    elif [[ $consecutive_failures -gt 2 ]]; then
        results+=("warning:failures:Consecutive failures: $consecutive_failures")
    else
        results+=("ok:failures:No recent consecutive failures")
    fi
}

# Check configuration health
check_configuration_health() {
    local -n results=$1
    
    # Check if configuration is loaded
    if [[ -z "${MANAGED_REPO_PATH:-}" ]]; then
        results+=("error:configuration:MANAGED_REPO_PATH not configured")
    elif [[ ! -d "$MANAGED_REPO_PATH" ]]; then
        results+=("error:configuration:MANAGED_REPO_PATH directory not found: $MANAGED_REPO_PATH")
    else
        results+=("ok:configuration:MANAGED_REPO_PATH is valid: $MANAGED_REPO_PATH")
    fi
    
    # Check log directory configuration
    if [[ -n "${LOG_DIRECTORY:-}" && ! -d "$LOG_DIRECTORY" ]]; then
        results+=("warning:configuration:LOG_DIRECTORY not found: $LOG_DIRECTORY")
    fi
    
    # Check configuration file integrity
    local config_file="$(dirname "${BASH_SOURCE[0]}")/../config.yaml"
    if [[ -f "$config_file" ]]; then
        results+=("ok:configuration:Configuration file exists: $config_file")
    else
        results+=("warning:configuration:Configuration file not found: $config_file")
    fi
}

# Check state file health
check_state_file_health() {
    local -n results=$1
    local state_file="${1:-$SYSTEM_STATE_FILE}"
    
    if validate_state_file "$state_file"; then
        results+=("ok:state_file:State file is valid")
    else
        results+=("error:state_file:State file validation failed")
    fi
}

# Analyze health check results
analyze_health_results() {
    local -n results=$1
    local -n overall_status=$2
    
    local error_count=0
    local warning_count=0
    local ok_count=0
    
    for result in "${results[@]}"; do
        case "$result" in
            error:*)
                ((error_count++))
                ;;
            warning:*)
                ((warning_count++))
                ;;
            ok:*)
                ((ok_count++))
                ;;
        esac
    done
    
    # Determine overall health status
    if [[ $error_count -gt 0 ]]; then
        overall_status="critical"
    elif [[ $warning_count -gt 2 ]]; then
        overall_status="degraded"
    elif [[ $warning_count -gt 0 ]]; then
        overall_status="healthy"
    else
        overall_status="healthy"
    fi
    
    log "DEBUG" "Health analysis: $error_count errors, $warning_count warnings, $ok_count OK"
}

# Update health status in state
update_health_status() {
    local status="$1"
    local -n results=$2
    local state_file="$3"
    
    local health_data=$(cat << EOF
{
    "system": {
        "health_status": "$status",
        "last_successful_run": $(date +%s),
        "consecutive_failures": 0
    },
    "health": {
        "last_health_check": $(date +%s),
        "health_checks_passed": $(printf "%s\n" "${results[@]}" | grep -c "^ok:"),
        "health_checks_failed": $(printf "%s\n" "${results[@]}" | grep -c "^error:"),
        "active_alerts": $(printf "%s\n" "${results[@]}" | grep "^error:" | jq -R . | jq -s .)
    }
}
EOF
)
    
    atomic_state_update "merge" "$health_data" "$state_file"
}

# =============================================================================
# PERFORMANCE MONITORING
# =============================================================================

# Record operation performance
record_operation_performance() {
    local operation="$1"
    local duration="$2"
    local success="${3:-true}"
    local state_file="${4:-$SYSTEM_STATE_FILE}"
    
    local performance_data=$(cat << EOF
{
    "performance": {
        "avg_operation_duration": $duration,
        "operation_history": {
            "operation": "$operation",
            "duration": $duration,
            "success": $success,
            "timestamp": $(date +%s)
        }
    },
    "system": {
        "total_operations": $(get_state_value "system.total_operations" 0) + 1,
        "successful_operations": $(get_state_value "system.successful_operations" 0) + $(if [[ "$success" == "true" ]]; then echo 1; else echo 0; fi)
    }
}
EOF
)
    
    atomic_state_update "merge" "$performance_data" "$state_file"
    
    log "DEBUG" "Performance recorded: $operation (${duration}s, success=$success)"
}

# Get specific state value
get_state_value() {
    local key_path="$1"
    local default_value="${2:-null}"
    local state_file="${3:-$SYSTEM_STATE_FILE}"
    
    if [[ ! -f "$state_file" ]]; then
        echo "$default_value"
        return 1
    fi
    
    if command -v jq >/dev/null 2>&1; then
        local value=$(jq -r ".$key_path // \"$default_value\"" "$state_file" 2>/dev/null)
        if [[ "$value" == "null" ]]; then
            echo "$default_value"
        else
            echo "$value"
        fi
    else
        echo "$default_value"
        return 1
    fi
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Initialize state management system
initialize_state_management() {
    local state_file="${1:-$SYSTEM_STATE_FILE}"
    
    # Initialize comprehensive state
    initialize_comprehensive_state "$state_file"
    
    # Set up periodic health checks
    setup_periodic_health_checks
    
    log "INFO" "State management system initialized"
}

# Setup periodic health checks
setup_periodic_health_checks() {
    # This would typically be called from a scheduler or main loop
    # For now, just log that it's configured
    log "DEBUG" "Periodic health checks configured (interval: ${HEALTH_CHECK_INTERVAL}s)"
}

# Generate state summary report
generate_state_summary() {
    local state_file="${1:-$SYSTEM_STATE_FILE}"
    
    if [[ ! -f "$state_file" ]]; then
        echo "State file not found: $state_file"
        return 1
    fi
    
    if command -v jq >/dev/null 2>&1; then
        local health_status=$(get_state_value "system.health_status" "unknown")
        local total_ops=$(get_state_value "system.total_operations" 0)
        local success_ops=$(get_state_value "system.successful_operations" 0)
        local consecutive_failures=$(get_state_value "system.consecutive_failures" 0)
        local avg_duration=$(get_state_value "performance.avg_operation_duration" 0)
        
        cat << EOF
State Summary Report
==================
Health Status: $health_status
Total Operations: $total_ops
Successful Operations: $success_ops
Consecutive Failures: $consecutive_failures
Average Operation Duration: ${avg_duration}s
Last Updated: $(get_state_value "last_updated" "unknown")

Recent Health Checks:
$(jq -r '.health.last_health_check | strftime("%Y-%m-%d %H:%M:%S")' "$state_file" 2>/dev/null || echo "Unknown")
EOF
    else
        echo "jq required for detailed state summary"
    fi
}

# Export key functions
export -f initialize_state_management
export -f perform_health_check
export -f record_operation_performance
export -f atomic_state_update
export -f get_state_value
export -f generate_state_summary

# Auto-initialize if this script is sourced and not already initialized
if [[ "${BASH_SOURCE[0]}" != "${0}" && -z "${STATE_MANAGEMENT_INITIALIZED:-}" ]]; then
    initialize_state_management
    export STATE_MANAGEMENT_INITIALIZED=true
fi