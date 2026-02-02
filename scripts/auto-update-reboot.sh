#!/bin/bash

# Auto-update-reboot script with change detection and conditional reboot
# Load utilities and configuration first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# Set up error handling
setup_error_handling

# Configure script-specific variables
SCRIPT_NAME="auto-update-reboot"
STATE_FILE="${LOG_DIRECTORY}/auto-update-reboot.state"

# Default configuration values (will be overridden by config.yaml if present)
AUTO_UPDATE_REBOOT_ENABLED=${AUTO_UPDATE_REBOOT_ENABLED:-false}
REBOOT_COOLDOWN_MINUTES=${REBOOT_COOLDOWN_MINUTES:-60}
CHANGE_DETECTION_INTERVAL_MINUTES=${CHANGE_DETECTION_INTERVAL_MINUTES:-5}
REBOOT_DELAY_SECONDS=${REBOOT_DELAY_SECONDS:-30}
MAX_REBOOT_ATTEMPTS_PER_DAY=${MAX_REBOOT_ATTEMPTS_PER_DAY:-3}
MAINTENANCE_MODE=${MAINTENANCE_MODE:-false}
EMERGENCY_OVERRIDE=${EMERGENCY_OVERRIDE:-false}

# Enhanced safe reboot mechanism configuration
SAFE_REBOOT_MAX_DISK_USAGE=${SAFE_REBOOT_MAX_DISK_USAGE:-85}
SAFE_REBOOT_MAX_MEMORY_USAGE=${SAFE_REBOOT_MAX_MEMORY_USAGE:-85}
SAFE_REBOOT_MAX_LOAD_MULTIPLIER=${SAFE_REBOOT_MAX_LOAD_MULTIPLIER:-2}
SAFE_REBOOT_MAX_FAILED_SERVICES=${SAFE_REBOOT_MAX_FAILED_SERVICES:-5}
SAFE_REBOOT_MAX_DEGRADED_CRITICAL_SERVICES=${SAFE_REBOOT_MAX_DEGRADED_CRITICAL_SERVICES:-2}
MAINTENANCE_WINDOW_START=${MAINTENANCE_WINDOW_START:-"02:00"}
MAINTENANCE_WINDOW_END=${MAINTENANCE_WINDOW_END:-"04:00"}
BUSINESS_HOURS_START=${BUSINESS_HOURS_START:-"09:00"}
BUSINESS_HOURS_END=${BUSINESS_HOURS_END:-"17:00"}
GRACEFUL_SHUTDOWN_ENABLED=${GRACEFUL_SHUTDOWN_ENABLED:-true}
GRACEFUL_SHUTDOWN_TIMEOUT=${GRACEFUL_SHUTDOWN_TIMEOUT:-30}
STOP_NON_CRITICAL_SERVICES=${STOP_NON_CRITICAL_SERVICES:-true}
SYNC_FILESYSTEMS=${SYNC_FILESYSTEMS:-true}
CREATE_PRE_REBOOT_BACKUP=${CREATE_PRE_REBOOT_BACKUP:-true}
ENHANCED_STATE_LOGGING=${ENHANCED_STATE_LOGGING:-true}
MONITOR_DURING_COUNTDOWN=${MONITOR_DURING_COUNTDOWN:-true}
COUNTDOWN_CHECK_INTERVAL=${COUNTDOWN_CHECK_INTERVAL:-30}
USER_NOTIFICATIONS_ENABLED=${USER_NOTIFICATIONS_ENABLED:-false}
MONITORING_ENABLED=${MONITORING_ENABLED:-false}
CRITICAL_ENDPOINTS=${CRITICAL_ENDPOINTS:-""}
CREATE_FAILURE_RECORDS=${CREATE_FAILURE_RECORDS:-true}
EMERGENCY_RECOVERY_ENABLED=${EMERGENCY_RECOVERY_ENABLED:-true}

# Enhanced git change detection configuration
GIT_TIMEOUT_SECONDS=${GIT_TIMEOUT_SECONDS:-30}
GIT_RETRY_ATTEMPTS=${GIT_RETRY_ATTEMPTS:-3}
GIT_RETRY_DELAY_SECONDS=${GIT_RETRY_DELAY_SECONDS:-5}
NETWORK_TIMEOUT_SECONDS=${NETWORK_TIMEOUT_SECONDS:-60}

# Change significance filtering (default patterns that trigger reboot)
REBOOT_TRIGGER_PATTERNS=${REBOOT_TRIGGER_PATTERNS:-"scripts/*.sh|config.yaml|main.sh|scripts/utils.sh|scripts/core/*.sh"}
IGNORE_CHANGE_PATTERNS=${IGNORE_CHANGE_PATTERNS:-"*.md|*.txt|*.log|tests/*.sh|.*"}

# Change significance thresholds
MIN_CHANGED_FILES_FOR_REBOOT=${MIN_CHANGED_FILES_FOR_REBOOT:-1}
MAX_CHANGE_COUNT_FOR_REBOOT=${MAX_CHANGE_COUNT_FOR_REBOOT:-100}

log "INFO" "Starting auto-update-reboot.sh"
log "INFO" "Auto-update-reboot enabled: $AUTO_UPDATE_REBOOT_ENABLED"

# Check if auto-update-reboot functionality is enabled
if [[ "$AUTO_UPDATE_REBOOT_ENABLED" != "true" ]]; then
    log "INFO" "Auto-update-reboot is disabled, exiting gracefully"
    exit 0
fi

# Check maintenance mode
if [[ "$MAINTENANCE_MODE" == "true" ]]; then
    log "INFO" "Maintenance mode enabled, skipping auto-update-reboot cycle"
    exit 0
fi

# Initialize state management with enhanced tracking
initialize_state() {
    local state_dir=$(dirname "$STATE_FILE")
    mkdir -p "$state_dir"
    
    if [[ ! -f "$STATE_FILE" ]]; then
        log "INFO" "Initializing enhanced state file: $STATE_FILE"
        cat > "$STATE_FILE" << 'EOF'
{
  "last_reboot_timestamp": null,
  "reboot_attempts_today": 0,
  "current_date": "2026-02-02",
  "last_known_heads": {},
  "system_health_status": "unknown",
  "last_processed_changes": {},
  "reboot_history": [],
  "failed_operations": [],
  "change_detection_stats": {
    "total_checks": 0,
    "successful_checks": 0,
    "reboots_triggered": 0
  }
}
EOF
    else
        # Migrate existing state file to new format if needed
        migrate_state_file
    fi
}

# Migrate state file to new enhanced format
migrate_state_file() {
    # Check if state file needs migration
    if ! grep -q "change_detection_stats" "$STATE_FILE"; then
        log "INFO" "Migrating state file to enhanced format"
        
        # Create backup of current state
        cp "$STATE_FILE" "${STATE_FILE}.backup.$(date +%s)"
        
        # Add new fields to existing state
        local temp_file="${STATE_FILE}.migrate"
        
        # Basic migration - add new fields before closing brace
        sed '/^}/i\
  "last_processed_changes": {},\
  "reboot_history": [],\
  "failed_operations": [],\
  "change_detection_stats": {\
    "total_checks": 0,\
    "successful_checks": 0,\
    "reboots_triggered": 0\
  }' "$STATE_FILE" > "$temp_file" && mv "$temp_file" "$STATE_FILE"
        
        log "INFO" "State file migration completed"
    fi
}

# Get state value from state file (enhanced version)
get_state_value() {
    local key="$1"
    local default_value="${2:-null}"
    
    if [[ -f "$STATE_FILE" ]]; then
        # Enhanced JSON parsing that handles nested objects
        local value
        
        # Try to extract string value
        value=$(grep -o "\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" "$STATE_FILE" | sed 's/.*: *"\([^"]*\)".*/\1/')
        
        # If not found as string, try numeric value
        if [[ -z "$value" ]]; then
            value=$(grep -o "\"$key\"[[:space:]]*:[[:space:]]*[0-9]\+" "$STATE_FILE" | sed 's/.*: *\([0-9]\+\).*/\1/')
        fi
        
        # If not found as numeric, try boolean or null
        if [[ -z "$value" ]]; then
            value=$(grep -o "\"$key\"[[:space:]]*:[[:space:]]*\(true\|false\|null\)" "$STATE_FILE" | sed 's/.*: *\(true\|false\|null\).*/\1/')
        fi
        
        echo "${value:-$default_value}"
    else
        echo "$default_value"
    fi
}

# Set state value in state file (enhanced version)
set_state_value() {
    local key="$1"
    local value="$2"
    
    if [[ ! -f "$STATE_FILE" ]]; then
        log "WARNING" "State file does not exist, cannot set value for key: $key"
        return 1
    fi
    
    # Enhanced JSON value replacement that handles different value types
    local temp_file="${STATE_FILE}.tmp"
    
    # Handle different value types
    if [[ "$value" =~ ^[0-9]+$ ]]; then
        # Numeric value
        sed "s/\"$key\"[[:space:]]*:[[:space:]]*[^,}]*/\"$key\": $value/" "$STATE_FILE" > "$temp_file"
    elif [[ "$value" == "true" || "$value" == "false" || "$value" == "null" ]]; then
        # Boolean or null value
        sed "s/\"$key\"[[:space:]]*:[[:space:]]*[^,}]*/\"$key\": $value/" "$STATE_FILE" > "$temp_file"
    else
        # String value
        sed "s/\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"/\"$key\": \"$value\"/" "$STATE_FILE" > "$temp_file"
    fi
    
    # Check if the key exists, if not add it
    if ! grep -q "\"$key\":" "$temp_file"; then
        # Add new key before closing brace
        if [[ "$value" =~ ^[0-9]+$ || "$value" == "true" || "$value" == "false" || "$value" == "null" ]]; then
            sed "s/}/,\n  \"$key\": $value\n}/" "$temp_file" > "${STATE_FILE}.tmp2"
        else
            sed "s/}/,\n  \"$key\": \"$value\"\n}/" "$temp_file" > "${STATE_FILE}.tmp2"
        fi
        mv "${STATE_FILE}.tmp2" "$temp_file"
    fi
    
    mv "$temp_file" "$STATE_FILE"
}

# Track processed changes to prevent duplicate reboots
track_processed_change() {
    local repo_path="$1"
    local commit_hash="$2"
    local change_signature="$3"
    
    local processed_key="${repo_path}:${commit_hash}"
    local current_timestamp=$(date -Iseconds)
    
    # Add to processed changes
    if [[ -f "$STATE_FILE" ]]; then
        # Use sed to add to last_processed_changes object
        local temp_file="${STATE_FILE}.tmp"
        sed "s/\"last_processed_changes\": {[^}]*}/\"last_processed_changes\": {\"$processed_key\": {\"timestamp\": \"$current_timestamp\", \"signature\": \"$change_signature\"}}/" "$STATE_FILE" > "$temp_file" && mv "$temp_file" "$STATE_FILE"
        
        log "DEBUG" "Tracked processed change: $processed_key"
    fi
}

# Check if change was already processed
is_change_already_processed() {
    local repo_path="$1"
    local commit_hash="$2"
    local change_signature="$3"
    
    local processed_key="${repo_path}:${commit_hash}"
    
    # Check if this change was already processed recently
    if [[ -f "$STATE_FILE" ]]; then
        local existing_entry=$(grep -o "\"$processed_key\"[[:space:]]*:[[:space:]]*{[^}]*}" "$STATE_FILE")
        
        if [[ -n "$existing_entry" ]]; then
            local existing_timestamp=$(echo "$existing_entry" | grep -o '"timestamp"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*: *"\([^"]*\)".*/\1/')
            local existing_signature=$(echo "$existing_entry" | grep -o '"signature"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*: *"\([^"]*\)".*/\1/')
            
            if [[ "$existing_signature" == "$change_signature" ]]; then
                log "DEBUG" "Change already processed: $processed_key (timestamp: $existing_timestamp)"
                return 0  # Already processed
            fi
        fi
    fi
    
    return 1  # Not processed
}

# Update change detection statistics
update_detection_stats() {
    local operation_type="$1"  # "check", "success", "reboot"
    
    if [[ ! -f "$STATE_FILE" ]]; then
        return 1
    fi
    
    case "$operation_type" in
        "check")
            local total_checks=$(get_state_value "total_checks" "0")
            set_state_value "total_checks" "$((total_checks + 1))"
            ;;
        "success")
            local successful_checks=$(get_state_value "successful_checks" "0")
            set_state_value "successful_checks" "$((successful_checks + 1))"
            ;;
        "reboot")
            local reboots_triggered=$(get_state_value "reboots_triggered" "0")
            set_state_value "reboots_triggered" "$((reboots_triggered + 1))"
            ;;
    esac
}

# Check if we're in cooldown period
check_cooldown() {
    local last_reboot=$(get_state_value "last_reboot_timestamp")
    
    if [[ -n "$last_reboot" && "$last_reboot" != "null" ]]; then
        local seconds_since_reboot=$(($(date +%s) - $(date -d "$last_reboot" +%s) 2>/dev/null || echo 86400))
        local cooldown_seconds=$((REBOOT_COOLDOWN_MINUTES * 60))
        
        if [[ $seconds_since_reboot -lt $cooldown_seconds ]]; then
            local remaining_minutes=$(((cooldown_seconds - seconds_since_reboot) / 60))
            log "WARNING" "Reboot cooldown active. ${remaining_minutes} minutes remaining."
            return 1
        fi
    fi
    return 0
}

# Check daily reboot limit
check_daily_limit() {
    local current_date=$(date +%Y-%m-%d)
    local stored_date=$(get_state_value "current_date")
    local attempts_today=$(get_state_value "reboot_attempts_today" "0")
    
    # Reset counter if it's a new day
    if [[ "$current_date" != "$stored_date" ]]; then
        set_state_value "current_date" "$current_date"
        set_state_value "reboot_attempts_today" "0"
        attempts_today=0
    fi
    
    if [[ $attempts_today -ge $MAX_REBOOT_ATTEMPTS_PER_DAY ]]; then
        log "WARNING" "Daily reboot limit reached ($MAX_REBOOT_ATTEMPTS_PER_DAY attempts). Skipping reboot."
        return 1
    fi
    
    return 0
}

# Enhanced system health checks with comprehensive safeguards
check_system_health() {
    log "INFO" "Performing comprehensive system health checks"
    
    local health_issues=0
    
    # Check disk space on multiple critical mount points
    local critical_mounts=("/" "/home" "/var" "/tmp")
    for mount in "${critical_mounts[@]}"; do
        if [[ -d "$mount" ]]; then
            local disk_usage=$(df "$mount" | awk 'NR==2 {print $5}' | sed 's/%//' 2>/dev/null || echo "0")
        if [[ $disk_usage -gt ${SAFE_REBOOT_MAX_DISK_USAGE:-85} ]]; then
            log "ERROR" "Disk usage too high on $mount: ${disk_usage}% (must be < ${SAFE_REBOOT_MAX_DISK_USAGE:-85}%)"
            health_issues=$((health_issues + 1))
            else
                log_system_health "disk_space_$mount" "pass" "Disk usage on $mount: ${disk_usage}%"
            fi
        fi
    done
    
    # Check memory usage with detailed analysis
    if command -v free >/dev/null 2>&1; then
        local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
        local swap_usage=$(free | awk 'NR==3{printf "%.0f", $3*100/$2}' 2>/dev/null || echo "0")
        
        if [[ $memory_usage -gt ${SAFE_REBOOT_MAX_MEMORY_USAGE:-85} ]]; then
            log "ERROR" "Memory usage too high: ${memory_usage}% (must be < ${SAFE_REBOOT_MAX_MEMORY_USAGE:-85}%)"
            health_issues=$((health_issues + 1))
        else
            log_system_health "memory_usage" "pass" "Memory usage: ${memory_usage}%"
        fi
        
        if [[ $swap_usage -gt 50 ]]; then
            log "WARNING" "High swap usage: ${swap_usage}% (system may be under memory pressure)"
        fi
    fi
    
    # Check system load averages
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | sed 's/^[ \t]*//' | cut -d',' -f1 | sed 's/^[ \t]*//')
    local cpu_count=$(nproc 2>/dev/null || echo "1")
    local load_threshold=$((cpu_count * SAFE_REBOOT_MAX_LOAD_MULTIPLIER))
    
    # Convert load to integer for comparison (remove decimal)
    local load_int=$(echo "$load_avg" | cut -d'.' -f1)
    if [[ $load_int -gt $load_threshold ]]; then
        log "WARNING" "High system load: $load_avg (threshold: $load_threshold)"
        health_issues=$((health_issues + 1))
    else
        log_system_health "system_load" "pass" "System load: $load_avg"
    fi
    
    # Check critical services status
    if command -v systemctl >/dev/null 2>&1; then
        local critical_services=("sshd" "networking" "systemd-journald")
        local failed_services=$(systemctl list-units --failed --no-legend | wc -l)
        local degraded_services=0
        
        for service in "${critical_services[@]}"; do
            if systemctl is-active --quiet "$service" 2>/dev/null; then
                log_system_health "service_$service" "pass" "Service $service is running"
            elif systemctl list-unit-files | grep -q "^$service.service"; then
                log "WARNING" "Critical service $service is not active"
                degraded_services=$((degraded_services + 1))
            fi
        done
        
        if [[ $failed_services -gt ${SAFE_REBOOT_MAX_FAILED_SERVICES:-5} ]]; then
            log "ERROR" "Too many failed services: $failed_services (threshold: ${SAFE_REBOOT_MAX_FAILED_SERVICES:-5})"
            health_issues=$((health_issues + 1))
        elif [[ $failed_services -gt 0 ]]; then
            log "WARNING" "Found $failed_services failed services"
        fi
        
        if [[ $degraded_services -gt ${SAFE_REBOOT_MAX_DEGRADED_CRITICAL_SERVICES:-2} ]]; then
            log "ERROR" "Too many degraded critical services: $degraded_services (threshold: ${SAFE_REBOOT_MAX_DEGRADED_CRITICAL_SERVICES:-2})"
            health_issues=$((health_issues + 1))
        fi
    fi
    
    # Check network connectivity
    check_network_connectivity
    local network_status=$?
    if [[ $network_status -ne 0 ]]; then
        log "WARNING" "Network connectivity issues detected"
        health_issues=$((health_issues + 1))
    fi
    
    # Check for ongoing file operations that might be disrupted
    check_file_operations
    local file_ops_status=$?
    if [[ $file_ops_status -ne 0 ]]; then
        log "WARNING" "Critical file operations in progress"
        health_issues=$((health_issues + 1))
    fi
    
    # Overall health assessment
    if [[ $health_issues -eq 0 ]]; then
        log_system_health "system_health" "pass" "All comprehensive health checks passed"
        set_state_value "system_health_status" "healthy"
        return 0
    elif [[ $health_issues -le 2 ]]; then
        log_system_health "system_health" "warning" "System has minor health issues ($health_issues)"
        set_state_value "system_health_status" "warning"
        return 0  # Allow reboot with warnings
    else
        log "ERROR" "System has too many health issues ($health_issues), reboot blocked"
        set_state_value "system_health_status" "critical"
        return 1
    fi
}

# Check network connectivity to critical endpoints
check_network_connectivity() {
    local connectivity_issues=0
    
    # Test basic internet connectivity
    if ! ping -c 1 -W 5 8.8.8.8 >/dev/null 2>&1; then
        log "DEBUG" "Cannot reach 8.8.8.8 (basic connectivity test)"
        connectivity_issues=$((connectivity_issues + 1))
    fi
    
    # Test DNS resolution
    if ! nslookup github.com >/dev/null 2>&1; then
        log "DEBUG" "DNS resolution failed for github.com"
        connectivity_issues=$((connectivity_issues + 1))
    fi
    
    # Test specific critical endpoints if configured
    if [[ -n "${CRITICAL_ENDPOINTS:-}" ]]; then
        IFS=',' read -ra ENDPOINTS <<< "$CRITICAL_ENDPOINTS"
        for endpoint in "${ENDPOINTS[@]}"; do
            if ! curl -s --connect-timeout 5 --max-time 10 "$endpoint" >/dev/null 2>&1; then
                log "DEBUG" "Cannot reach critical endpoint: $endpoint"
                connectivity_issues=$((connectivity_issues + 1))
            fi
        done
    fi
    
    return $connectivity_issues
}

# Check for critical file operations that shouldn't be interrupted
check_file_operations() {
    local file_op_issues=0
    
    # Check for large file transfers
    if command -v lsof >/dev/null 2>&1; then
        local large_transfers=$(lsof +L -n -P | awk '$5 ~ /^[0-9]+$/ && $5 > 104857600 {print}' | wc -l)
        if [[ $large_transfers -gt 0 ]]; then
            log "WARNING" "Found $large_transfers large file transfers in progress"
            file_op_issues=$((file_op_issues + 1))
        fi
    fi
    
    # Check for active package management operations
    local package_managers=("apt" "yum" "dnf" "pacman")
    for manager in "${package_managers[@]}"; do
        if pgrep -f "$manager" >/dev/null 2>&1; then
            log "WARNING" "Package manager $manager is running"
            file_op_issues=$((file_op_issues + 1))
        fi
    done
    
    # Check for database operations
    local db_processes=("mysqld" "postgres" "mongodb")
    for db in "${db_processes[@]}"; do
        if pgrep "$db" >/dev/null 2>&1; then
            log "DEBUG" "Database process $db is running (normal)"
        fi
    done
    
    return $file_op_issues
}

# Enhanced reboot confirmation logic with multiple safety checks
confirm_reboot_safety() {
    log "INFO" "Performing comprehensive reboot safety confirmation"
    
    local confirmation_score=0
    local max_score=10
    
    # Check 1: Cooldown period (weight: 2)
    if check_cooldown; then
        confirmation_score=$((confirmation_score + 2))
        log "DEBUG" "Reboot safety check 1/10: Cooldown period - PASSED"
    else
        log "DEBUG" "Reboot safety check 1/10: Cooldown period - FAILED"
    fi
    
    # Check 2: Daily limit (weight: 2)
    if check_daily_limit; then
        confirmation_score=$((confirmation_score + 2))
        log "DEBUG" "Reboot safety check 2/10: Daily limit - PASSED"
    else
        log "DEBUG" "Reboot safety check 2/10: Daily limit - FAILED"
    fi
    
    # Check 3: System health (weight: 3)
    if check_system_health; then
        confirmation_score=$((confirmation_score + 3))
        log "DEBUG" "Reboot safety check 3/10: System health - PASSED"
    else
        log "DEBUG" "Reboot safety check 3/10: System health - FAILED"
    fi
    
    # Check 4: No active user sessions (weight: 1)
    if check_active_sessions; then
        confirmation_score=$((confirmation_score + 1))
        log "DEBUG" "Reboot safety check 4/10: Active sessions - PASSED"
    else
        log "DEBUG" "Reboot safety check 4/10: Active sessions - FAILED (warning)"
    fi
    
    # Check 5: Power status (weight: 1)
    if check_power_status; then
        confirmation_score=$((confirmation_score + 1))
        log "DEBUG" "Reboot safety check 5/10: Power status - PASSED"
    else
        log "DEBUG" "Reboot safety check 5/10: Power status - FAILED"
    fi
    
    # Check 6: Recent crash detection (weight: 1)
    if ! detect_recent_crashes; then
        confirmation_score=$((confirmation_score + 1))
        log "DEBUG" "Reboot safety check 6/10: Recent crashes - PASSED"
    else
        log "DEBUG" "Reboot safety check 6/10: Recent crashes - FAILED"
    fi
    
    # Calculate safety percentage
    local safety_percentage=$((confirmation_score * 100 / max_score))
    log "INFO" "Reboot safety score: $confirmation_score/$max_score ($safety_percentage%)"
    
    # Decision logic
    if [[ $safety_percentage -ge 80 ]]; then
        log "INFO" "Reboot safety confirmed: Safe to proceed ($safety_percentage%)"
        return 0
    elif [[ $safety_percentage -ge 60 ]]; then
        log "WARNING" "Reboot safety marginal: Proceeding with caution ($safety_percentage%)"
        return 0  # Allow but with warning
    else
        log "ERROR" "Reboot safety failed: Too many safety issues ($safety_percentage%)"
        return 1
    fi
}

# Check for active user sessions
check_active_sessions() {
    local active_sessions=0
    
    # Check for logged-in users
    if command -v who >/dev/null 2>&1; then
        active_sessions=$(who | wc -l)
    fi
    
    # Check for SSH sessions specifically
    local ssh_sessions=0
    if command -v ss >/dev/null 2>&1; then
        ssh_sessions=$(ss -tn state established '( dport = :ssh or sport = :ssh )' | wc -l)
    fi
    
    if [[ $active_sessions -gt 0 ]] || [[ $ssh_sessions -gt 0 ]]; then
        log "WARNING" "Active sessions detected: $active_sessions users, $ssh_sessions SSH connections"
        # Not a hard failure, but worth noting
    fi
    
    return 0  # Allow reboot even with active sessions (just log warning)
}

# Check power/battery status (for laptops)
check_power_status() {
    # Check if we're on a system with battery
    if [[ -d /sys/class/power_supply ]] && ls /sys/class/power_supply/BAT* >/dev/null 2>&1; then
        local battery_status=""
        local battery_capacity=100
        
        for battery in /sys/class/power_supply/BAT*; do
            if [[ -f "$battery/status" ]]; then
                battery_status=$(cat "$battery/status")
            fi
            if [[ -f "$battery/capacity" ]]; then
                battery_capacity=$(cat "$battery/capacity")
            fi
        done
        
        if [[ "$battery_status" == "Discharging" ]] && [[ $battery_capacity -lt 20 ]]; then
            log "ERROR" "Low battery ($battery_capacity%) while discharging - reboot unsafe"
            return 1
        fi
        
        log "DEBUG" "Power status: $battery_status, Battery: $battery_capacity%"
    fi
    
    return 0
}

# Detect recent system crashes or reboots
detect_recent_crashes() {
    local recent_crashes=false
    
    # Check for recent kernel panics (if available)
    if [[ -f /var/log/kern.log ]] && command -v journalctl >/dev/null 2>&1; then
        local recent_panics=$(journalctl --since "1 hour ago" -k | grep -i "kernel panic" | wc -l)
        if [[ $recent_panics -gt 0 ]]; then
            log "WARNING" "Detected $recent_panics kernel panics in the last hour"
            recent_crashes=true
        fi
    fi
    
    # Check for rapid reboots from our own state
    local last_reboot=$(get_state_value "last_reboot_timestamp")
    if [[ -n "$last_reboot" && "$last_reboot" != "null" ]]; then
        local seconds_since_reboot=$(($(date +%s) - $(date -d "$last_reboot" +%s) 2>/dev/null || echo 3600))
        if [[ $seconds_since_reboot -lt 300 ]]; then  # Less than 5 minutes
            log "WARNING" "Very recent reboot detected ($seconds_since_reboot seconds ago)"
            recent_crashes=true
        fi
    fi
    
    # Check system uptime
    local uptime_seconds=$(cat /proc/uptime | cut -d' ' -f1 | cut -d'.' -f1)
    if [[ $uptime_seconds -lt 300 ]]; then  # Less than 5 minutes uptime
        log "WARNING" "Very low system uptime: ${uptime_seconds}s"
        recent_crashes=true
    fi
    
    if [[ "$recent_crashes" == "true" ]]; then
        return 0  # Recent crashes detected
    else
        return 1  # No recent crashes
    fi
}

# Validate git repository state
validate_git_repository() {
    local repo_path="$1"
    local repo_name="$2"
    
    cd "$repo_path" || {
        log "ERROR" "Cannot access repository path: $repo_path"
        return 1
    }
    
    # Check if it's a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log "ERROR" "Not a git repository: $repo_path"
        return 1
    fi
    
    # Check for detached HEAD state
    local branch_name=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [[ "$branch_name" == "HEAD" ]]; then
        log "WARNING" "Repository $repo_name is in detached HEAD state"
        # Not a fatal error, but worth noting
    fi
    
    # Check if repository has commits
    if ! git log --oneline -1 >/dev/null 2>&1; then
        log "WARNING" "Repository $repo_name has no commits (empty repository)"
        return 1
    fi
    
    # Check remote connectivity
    if ! git remote >/dev/null 2>&1; then
        log "WARNING" "Repository $repo_name has no remote configured"
        return 1
    fi
    
    return 0
}

# Execute git command with timeout and retry logic
execute_git_with_retry() {
    local git_command="$1"
    local repo_path="$2"
    local repo_name="$3"
    local attempt=1
    local max_attempts=${GIT_RETRY_ATTEMPTS:-3}
    local retry_delay=${GIT_RETRY_DELAY_SECONDS:-5}
    
    cd "$repo_path" || {
        log "ERROR" "Cannot access repository path: $repo_path"
        return 1
    }
    
    while [[ $attempt -le $max_attempts ]]; do
        log "DEBUG" "Git command attempt $attempt/$max_attempts for $repo_name: $git_command"
        
        # Execute git command with timeout
        if timeout ${GIT_TIMEOUT_SECONDS:-30} bash -c "$git_command" 2>/dev/null; then
            log "DEBUG" "Git command succeeded on attempt $attempt for $repo_name"
            return 0
        else
            local exit_code=$?
            log "WARNING" "Git command failed (attempt $attempt/$max_attempts) for $repo_name: $git_command (exit code: $exit_code)"
            
            if [[ $attempt -lt $max_attempts ]]; then
                log "INFO" "Retrying in ${retry_delay}s for $repo_name..."
                sleep $retry_delay
                attempt=$((attempt + 1))
                # Exponential backoff
                retry_delay=$((retry_delay * 2))
            else
                log "ERROR" "All git command attempts failed for $repo_name: $git_command"
                return $exit_code
            fi
        fi
    done
    
    return 1
}

# Detect and handle merge conflicts
detect_merge_conflicts() {
    local repo_path="$1"
    local repo_name="$2"
    
    cd "$repo_path" || return 1
    
    # Check for merge conflicts
    if git diff --name-only --diff-filter=U 2>/dev/null | grep -q .; then
        log "ERROR" "Merge conflicts detected in $repo_name"
        local conflicted_files=$(git diff --name-only --diff-filter=U)
        
        while IFS= read -r file; do
            log "ERROR" "Conflicted file: $file"
        done <<< "$conflicted_files"
        
        # Attempt to abort merge and restore to known good state
        log "INFO" "Attempting to abort merge and restore clean state for $repo_name"
        if git merge --abort >/dev/null 2>&1; then
            log "INFO" "Merge aborted successfully for $repo_name"
            return 1  # Indicate failure but with recovery
        else
            log "ERROR" "Failed to abort merge for $repo_name, manual intervention required"
            return 2  # Critical failure
        fi
    fi
    
    return 0  # No conflicts
}

# Analyze change significance based on file patterns
analyze_change_significance() {
    local changed_files="$1"
    local repo_name="$2"
    local reboot_patterns="${REBOOT_TRIGGER_PATTERNS:-"scripts/*.sh|config.yaml|main.sh|scripts/utils.sh|scripts/core/*.sh"}"
    local ignore_patterns="${IGNORE_CHANGE_PATTERNS:-"*.md|*.txt|*.log|tests/*.sh|.*"}"
    
    local significant_files=0
    local ignored_files=0
    local reboot_triggered=false
    local significant_file_list=""
    
    # Create associative arrays for pattern matching
    local -A reboot_pattern_array
    local -A ignore_pattern_array
    
    # Parse reboot patterns
    IFS='|' read -ra REBOOT_PATTERN_ARRAY <<< "$reboot_patterns"
    for pattern in "${REBOOT_PATTERN_ARRAY[@]}"; do
        reboot_pattern_array["$pattern"]=1
    done
    
    # Parse ignore patterns
    IFS='|' read -ra IGNORE_PATTERN_ARRAY <<< "$ignore_patterns"
    for pattern in "${IGNORE_PATTERN_ARRAY[@]}"; do
        ignore_pattern_array["$pattern"]=1
    done
    
    # Analyze each changed file
    while IFS= read -r file; do
        [[ -z "$file" ]] && continue
        
        local is_ignored=false
        local is_significant=false
        
        # Check ignore patterns first
        for pattern in "${IGNORE_PATTERN_ARRAY[@]}"; do
            if [[ "$file" == $pattern ]]; then
                is_ignored=true
                ignored_files=$((ignored_files + 1))
                log "DEBUG" "Ignoring file change in $repo_name: $file (matches pattern: $pattern)"
                break
            fi
        done
        
        # If not ignored, check reboot patterns
        if [[ "$is_ignored" == "false" ]]; then
            for pattern in "${REBOOT_PATTERN_ARRAY[@]}"; do
                if [[ "$file" == $pattern ]]; then
                    is_significant=true
                    significant_files=$((significant_files + 1))
                    significant_file_list+="$file "
                    log "WARNING" "Significant file changed in $repo_name: $file (matches pattern: $pattern)"
                    break
                fi
            done
            
            # If not significant and not ignored, it's a normal change
            if [[ "$is_significant" == "false" ]]; then
                log "DEBUG" "Non-significant file changed in $repo_name: $file"
            fi
        fi
    done <<< "$changed_files"
    
    local total_changes=$(echo "$changed_files" | grep -c .)
    log "INFO" "Change analysis for $repo_name: total=$total_changes, significant=$significant_files, ignored=$ignored_files"
    
    # Determine if reboot should be triggered
    local min_changes=${MIN_CHANGED_FILES_FOR_REBOOT:-1}
    local max_changes=${MAX_CHANGE_COUNT_FOR_REBOOT:-100}
    
    if [[ $significant_files -ge $min_changes ]] && [[ $total_changes -le $max_changes ]]; then
        reboot_triggered=true
        log "WARNING" "Reboot triggered for $repo_name: $significant_files significant changes detected"
        if [[ -n "$significant_file_list" ]]; then
            log "WARNING" "Significant files: $significant_file_list"
        fi
    elif [[ $total_changes -gt $max_changes ]]; then
        log "WARNING" "Too many changes for $repo_name ($total_changes > $max_changes), requiring manual review"
        reboot_triggered=false
    fi
    
    # Return status
    if [[ "$reboot_triggered" == "true" ]]; then
        return 0  # Reboot needed
    else
        return 1  # No reboot needed
    fi
}

# Enhanced git change detection with comprehensive error handling
detect_repository_changes() {
    local repo_path="$1"
    local repo_name="$2"
    
    if [[ ! -d "$repo_path" ]]; then
        log "ERROR" "Repository path not found: $repo_path"
        return 1
    fi
    
    log "INFO" "Starting enhanced change detection for repository: $repo_name"
    
    # Validate repository state
    if ! validate_git_repository "$repo_path" "$repo_name"; then
        log "ERROR" "Repository validation failed for $repo_name"
        return 1
    fi
    
    cd "$repo_path" || return 1
    
    # Store current HEAD and state
    local current_head=$(git rev-parse HEAD 2>/dev/null)
    if [[ -z "$current_head" ]]; then
        log "ERROR" "Failed to get current HEAD for $repo_name"
        return 1
    fi
    
    # Get last known HEAD from state
    local last_known_head=$(get_state_value "last_known_heads" | grep -o "\"$repo_path\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | sed 's/.*: *"\([^"]*\)".*/\1/' || echo "")
    
    # Fetch latest changes with retry logic
    log "INFO" "Fetching latest changes for $repo_name"
    if ! execute_git_with_retry "git fetch origin" "$repo_path" "$repo_name"; then
        log "WARNING" "Failed to fetch changes for $repo_name, continuing with local state"
        return 1
    fi
    
    # Pull latest changes with retry logic
    log "INFO" "Pulling latest changes for $repo_name"
    if ! execute_git_with_retry "git pull origin" "$repo_path" "$repo_name"; then
        log "WARNING" "Git pull failed for $repo_name, continuing with current state"
        return 1
    fi
    
    # Check for merge conflicts
    local conflict_result
    conflict_result=$(detect_merge_conflicts "$repo_path" "$repo_name")
    local conflict_exit_code=$?
    
    if [[ $conflict_exit_code -eq 2 ]]; then
        log "ERROR" "Critical merge conflict in $repo_name requiring manual intervention"
        return 1
    elif [[ $conflict_exit_code -eq 1 ]]; then
        log "WARNING" "Merge conflict resolved by aborting merge in $repo_name"
        return 1
    fi
    
    # Get new HEAD after pull
    local new_head=$(git rev-parse HEAD 2>/dev/null)
    
    # Check if HEAD changed
    if [[ "$current_head" != "$new_head" ]]; then
        log "INFO" "Repository $repo_name has updates: $current_head -> $new_head"
        
        # Get comprehensive change information
        local changed_files=$(git diff --name-only "$current_head" "$new_head")
        local changes_count=$(echo "$changed_files" | wc -l)
        local change_stats=$(git diff --stat "$current_head" "$new_head")
        
        log "INFO" "Change statistics for $repo_name: $changes_count files changed"
        log "DEBUG" "Change details for $repo_name: $change_stats"
        
        # Analyze change significance
        if analyze_change_significance "$changed_files" "$repo_name"; then
            log_change_detection "$repo_name" "$changes_count" "true"
            
            # Update last known HEAD in state before returning
            update_last_known_head "$repo_name" "$new_head"
            
            return 0  # Signal reboot needed
        else
            log_change_detection "$repo_name" "$changes_count" "false"
            log "INFO" "Changes detected in $repo_name but no reboot trigger found"
        fi
    else
        log "INFO" "No changes detected in $repo_name"
    fi
    
    # Update last known HEAD in state
    update_last_known_head "$repo_name" "$new_head"
    
    return 1  # No reboot needed
}

# Update last known HEAD for a repository
update_last_known_head() {
    local repo_path="$1"
    local new_head="$2"
    
    # Simple approach: append to state file (basic JSON update)
    # In a more robust implementation, use proper JSON parsing
    local temp_file="${STATE_FILE}.tmp"
    if [[ -f "$STATE_FILE" ]]; then
        # This is a simplified approach - real implementation would use jq or similar
        sed "s/\"last_known_heads\": {[^}]*}/\"last_known_heads\": {\"$repo_path\": \"$new_head\"}/" "$STATE_FILE" > "$temp_file" && mv "$temp_file" "$STATE_FILE"
    fi
}

# Determine reboot type based on system conditions and configuration
determine_reboot_type() {
    local reboot_type="immediate"
    
    # Check if this is a maintenance window
    if is_maintenance_window; then
        reboot_type="scheduled"
        log "INFO" "Reboot scheduled during maintenance window"
    elif should_delay_reboot; then
        reboot_type="delayed"
        log "INFO" "Reboot will be delayed due to system conditions"
    else
        reboot_type="immediate"
        log "INFO" "Immediate reboot authorized"
    fi
    
    echo "$reboot_type"
}

# Check if current time is within maintenance window
is_maintenance_window() {
    # Check if maintenance window is configured
    if [[ -z "${MAINTENANCE_WINDOW_START:-}" ]] || [[ -z "${MAINTENANCE_WINDOW_END:-}" ]]; then
        return 1  # No maintenance window configured
    fi
    
    local current_hour=$(date +%H)
    local current_minute=$(date +%M)
    local current_time=$((current_hour * 60 + current_minute))
    
    local start_hour=$(echo "$MAINTENANCE_WINDOW_START" | cut -d':' -f1)
    local start_minute=$(echo "$MAINTENANCE_WINDOW_START" | cut -d':' -f2)
    local start_time=$((start_hour * 60 + start_minute))
    
    local end_hour=$(echo "$MAINTENANCE_WINDOW_END" | cut -d':' -f1)
    local end_minute=$(echo "$MAINTENANCE_WINDOW_END" | cut -d':' -f2)
    local end_time=$((end_hour * 60 + end_minute))
    
    # Handle overnight maintenance windows
    if [[ $start_time -gt $end_time ]]; then
        if [[ $current_time -ge $start_time ]] || [[ $current_time -lt $end_time ]]; then
            return 0  # Within overnight window
        fi
    else
        if [[ $current_time -ge $start_time ]] && [[ $current_time -lt $end_time ]]; then
            return 0  # Within normal window
        fi
    fi
    
    return 1  # Not in maintenance window
}

# Check if reboot should be delayed based on system conditions
should_delay_reboot() {
    local delay_reasons=0
    
    # Check if system load is high (but not critical)
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | sed 's/^[ \t]*//' | cut -d',' -f1 | sed 's/^[ \t]*//')
    local cpu_count=$(nproc 2>/dev/null || echo "1")
    local load_threshold=$((cpu_count))
    
    local load_int=$(echo "$load_avg" | cut -d'.' -f1)
    if [[ $load_int -gt $load_threshold ]]; then
        log "DEBUG" "High system load suggests delayed reboot: $load_avg"
        delay_reasons=$((delay_reasons + 1))
    fi
    
    # Check if it's during business hours
    local current_hour=$(date +%H)
    local business_start=$(echo "${BUSINESS_HOURS_START:-09:00}" | cut -d':' -f1)
    local business_end=$(echo "${BUSINESS_HOURS_END:-17:00}" | cut -d':' -f1)
    if [[ $current_hour -ge $business_start ]] && [[ $current_hour -le $business_end ]]; then
        log "DEBUG" "Business hours suggest delayed reboot"
        delay_reasons=$((delay_reasons + 1))
    fi
    
    # Check for active user sessions
    if command -v who >/dev/null 2>&1; then
        local active_sessions=$(who | wc -l)
        if [[ $active_sessions -gt 1 ]]; then
            log "DEBUG" "Active user sessions suggest delayed reboot: $active_sessions"
            delay_reasons=$((delay_reasons + 1))
        fi
    fi
    
    # Decision: delay if 2 or more reasons
    if [[ $delay_reasons -ge 2 ]]; then
        return 0  # Should delay
    else
        return 1  # Should not delay
    fi
}

# Enhanced pre-reboot notifications with system monitoring integration
send_enhanced_pre_reboot_notifications() {
    local reboot_type="$1"
    local scheduled_time=""
    
    case "$reboot_type" in
        "scheduled")
            # Schedule for next maintenance window
            scheduled_time=$(calculate_next_maintenance_window)
            ;;
        "delayed")
            # Add additional delay for safety
            local delay_seconds=$((REBOOT_DELAY_SECONDS + 300))  # Add 5 minutes
            scheduled_time=$(date -d "+${delay_seconds} seconds" '+%Y-%m-%d %H:%M:%S')
            ;;
        "immediate"|*)
            scheduled_time=$(date -d "+${REBOOT_DELAY_SECONDS} seconds" '+%Y-%m-%d %H:%M:%S')
            ;;
    esac
    
    log_reboot_event "Enhanced safety reboot triggered: $reboot_type" "$scheduled_time"
    
    # Enhanced system state logging
    log_enhanced_system_state
    
    # Send systemd notification with enhanced status
    if command -v systemd-notify >/dev/null 2>&1 && [[ -n "$NOTIFY_SOCKET" ]]; then
        systemd-notify --status="Enhanced reboot ($reboot_type) scheduled for: $scheduled_time"
    fi
    
    # Send monitoring alerts
    send_monitoring_alerts "$reboot_type" "$scheduled_time"
    
    # Send user notifications
    send_user_notifications "$reboot_type" "$scheduled_time"
    
    log "WARNING" "Enhanced reboot sequence initiated: $reboot_type type, scheduled for $scheduled_time"
}

# Calculate next maintenance window time
calculate_next_maintenance_window() {
    if [[ -z "${MAINTENANCE_WINDOW_START:-}" ]] || [[ -z "${MAINTENANCE_WINDOW_END:-}" ]]; then
        # Fallback to immediate if no maintenance window
        date -d "+${REBOOT_DELAY_SECONDS} seconds" '+%Y-%m-%d %H:%M:%S'
        return
    fi
    
    local start_hour=$(echo "$MAINTENANCE_WINDOW_START" | cut -d':' -f1)
    local start_minute=$(echo "$MAINTENANCE_WINDOW_START" | cut -d':' -f2)
    local current_hour=$(date +%H)
    local current_minute=$(date +%M)
    
    # If currently in maintenance window, use current time + delay
    if is_maintenance_window; then
        date -d "+${REBOOT_DELAY_SECONDS} seconds" '+%Y-%m-%d %H:%M:%S'
    else
        # Schedule for next maintenance window
        local target_hour=$start_hour
        local target_minute=$start_minute
        local target_date=$(date '+%Y-%m-%d')
        
        # If current time is past today's maintenance window, schedule for tomorrow
        if [[ $current_hour -gt $start_hour ]] || ([[ $current_hour -eq $start_hour ]] && [[ $current_minute -ge $start_minute ]]); then
            target_date=$(date -d "+1 day" '+%Y-%m-%d')
        fi
        
        date -d "$target_date $target_hour:$target_minute" '+%Y-%m-%d %H:%M:%S'
    fi
}

# Enhanced system state logging
log_enhanced_system_state() {
    local enhanced_snapshot_file="${LOG_DIRECTORY}/enhanced-system-state-$(date +%Y%m%d-%H%M%S).json"
    
    mkdir -p "${LOG_DIRECTORY}"
    
    {
        echo "{"
        echo "  \"timestamp\": \"$(date -Iseconds)\","
        echo "  \"reboot_reason\": \"$(get_state_value 'last_reboot_reason' 'Unknown')\","
        echo "  \"uptime\": \"$(uptime)\","
        echo "  \"system\": {"
        echo "    \"kernel\": \"$(uname -r)\","
        echo "    \"os\": \"$(uname -s)\","
        echo "    \"architecture\": \"$(uname -m)\","
        echo "    \"hostname\": \"$(hostname)\","
        echo "    \"timezone\": \"$(timedatectl show --property=Timezone --value 2>/dev/null || echo 'Unknown')\""
        echo "  },"
        echo "  \"resources\": {"
        echo "    \"disk_usage\": \"$(df -h / | tail -1 | awk '{print $5}')\","
        echo "    \"memory_usage\": \"$(free -h | grep '^Mem:' | awk '{print $3"/"$2}')\","
        echo "    \"swap_usage\": \"$(free -h | grep '^Swap:' | awk '{print $3"/"$2}')\","
        echo "    \"load_average\": \"$(uptime | awk -F'load average:' '{print $2}')\""
        echo "  },"
        echo "  \"processes\": {"
        echo "    \"total\": \"$(ps aux | wc -l)\","
        echo "    \"running\": \"$(ps aux | awk '$8 ~ /^R/ {count++} END {print count+0}')\""
        echo "  },"
        echo "  \"network\": {"
        echo "    \"interfaces\": \"$(ip link show | grep '^[0-9]' | wc -l)\","
        echo "    \"connections\": \"$(ss -tn state established | wc -l)\""
        echo "  },"
        echo "  \"services\": {"
        if command -v systemctl >/dev/null 2>&1; then
            echo "    \"running\": \"$(systemctl list-units --type=service --state=running --no-legend | wc -l)\","
            echo "    \"failed\": \"$(systemctl list-units --type=service --state=failed --no-legend | wc -l)\""
        else
            echo "    \"systemd\": \"not_available\""
        fi
        echo "  },"
        echo "  \"automation\": {"
        echo "    \"reboot_attempts_today\": \"$(get_state_value 'reboot_attempts_today' '0')\","
        echo "    \"last_reboot\": \"$(get_state_value 'last_reboot_timestamp' 'Never')\","
        echo "    \"system_health\": \"$(get_state_value 'system_health_status' 'unknown')\""
        echo "  }"
        echo "}"
    } > "$enhanced_snapshot_file"
    
    log "INFO" "Enhanced system state snapshot saved: $enhanced_snapshot_file"
}

# Send monitoring alerts
send_monitoring_alerts() {
    local reboot_type="$1"
    local scheduled_time="$2"
    
    # Send to monitoring systems if configured
    if [[ "${MONITORING_ENABLED:-false}" == "true" ]]; then
        # This could integrate with Prometheus, Nagios, etc.
        log "INFO" "Monitoring alert sent: Reboot $reboot_type scheduled for $scheduled_time"
    fi
    
    # Send to system log
    logger -t "auto-update-reboot" "CRITICAL: System reboot scheduled ($reboot_type) for $scheduled_time"
    
    # Send to Telegram if configured
    if [[ "${TELEGRAM_ENABLED:-false}" == "true" ]] && command -v telegram_logger >/dev/null 2>&1; then
        local message="🔄 **Auto-Reboot Alert**

Type: $reboot_type
Scheduled: $scheduled_time
Reason: Repository changes detected

System will reboot automatically."
        telegram_logger "WARNING" "$message"
    fi
}

# Send user notifications
send_user_notifications() {
    local reboot_type="$1"
    local scheduled_time="$2"
    
    # Check if user notifications are enabled
    if [[ "${USER_NOTIFICATIONS_ENABLED:-false}" != "true" ]]; then
        return 0
    fi
    
    # Send desktop notification if possible
    if command -v notify-send >/dev/null 2>&1 && [[ -n "${DISPLAY:-}" ]]; then
        notify-send "System Reboot Scheduled" "Type: $reboot_type\nTime: $scheduled_time\nReason: Repository changes" --urgency=critical --icon=system-reboot
    fi
    
    # Send wall message to all logged-in users
    if [[ "$reboot_type" == "immediate" ]] || [[ "$reboot_type" == "delayed" ]]; then
        wall << EOF
*** SYSTEM REBOOT NOTIFICATION ***
The system will reboot automatically in $REBOOT_DELAY_SECONDS seconds.

Type: $reboot_type
Scheduled time: $scheduled_time
Reason: Repository changes detected

Please save your work immediately.
EOF
    fi
}

# Create safety failure record
create_safety_failure_record() {
    local failure_file="${LOG_DIRECTORY}/safety-failure-$(date +%Y%m%d-%H%M%S).json"
    
    mkdir -p "${LOG_DIRECTORY}"
    
    {
        echo "{"
        echo "  \"timestamp\": \"$(date -Iseconds)\","
        echo "  \"failure_type\": \"safety_confirmation\","
        echo "  \"system_health\": \"$(get_state_value 'system_health_status' 'unknown')\","
        echo "  \"last_reboot\": \"$(get_state_value 'last_reboot_timestamp' 'Never')\","
        echo "  \"reboot_attempts_today\": \"$(get_state_value 'reboot_attempts_today' '0')\","
        echo "  \"system_state\": {"
        echo "    \"uptime\": \"$(uptime)\","
        echo "    \"disk_usage\": \"$(df -h / | tail -1 | awk '{print $5}')\","
        echo "    \"memory_usage\": \"$(free -h | grep '^Mem:' | awk '{print $3"/"$2}')\""
        echo "  }"
        echo "}"
    } > "$failure_file"
    
    log "WARNING" "Safety failure record created: $failure_file"
}

# Update reboot state
update_reboot_state() {
    local current_timestamp=$(date -Iseconds)
    local current_date=$(date +%Y-%m-%d)
    local current_attempts=$(get_state_value "reboot_attempts_today" "0")
    
    set_state_value "last_reboot_timestamp" "$current_timestamp"
    set_state_value "current_date" "$current_date"
    set_state_value "reboot_attempts_today" "$((current_attempts + 1))"
}

# Enhanced system reboot execution with graceful shutdown and rollback
execute_reboot() {
    log "WARNING" "Executing enhanced safe reboot sequence"
    
    # Create reboot attempt record
    local attempt_id=$(date +%s)
    create_reboot_attempt_record "$attempt_id"
    
    # Update state before reboot
    update_reboot_state
    
    # Perform graceful shutdown procedures
    if ! perform_graceful_shutdown; then
        log "ERROR" "Graceful shutdown failed, attempting emergency reboot"
        return 1
    fi
    
    # Wait for the configured delay with countdown
    if [[ $REBOOT_DELAY_SECONDS -gt 0 ]]; then
        log "INFO" "Waiting ${REBOOT_DELAY_SECONDS} seconds before reboot..."
        countdown_with_checks "$REBOOT_DELAY_SECONDS"
    fi
    
    # Final safety check
    if ! confirm_reboot_safety; then
        log "ERROR" "Final safety check failed, aborting reboot"
        abort_reboot "$attempt_id"
        return 1
    fi
    
    # Attempt reboot with enhanced methods and monitoring
    if ! attempt_system_reboot "$attempt_id"; then
        handle_reboot_failure "$attempt_id" "primary"
        return 1
    fi
    
    # This should not be reached if reboot succeeds
    log "ERROR" "Reboot command returned unexpectedly - possible failure"
    return 1
}

# Create a record of the reboot attempt
create_reboot_attempt_record() {
    local attempt_id="$1"
    local record_file="${LOG_DIRECTORY}/reboot-attempt-${attempt_id}.json"
    
    mkdir -p "${LOG_DIRECTORY}"
    
    {
        echo "{"
        echo "  \"attempt_id\": \"$attempt_id\","
        echo "  \"timestamp\": \"$(date -Iseconds)\","
        echo "  \"reason\": \"Repository changes detected\","
        echo "  \"trigger_files\": \"$(get_state_value 'last_reboot_reason' 'Unknown')\","
        echo "  \"pre_reboot_state\": {"
        echo "    \"uptime\": \"$(uptime)\","
        echo "    \"disk_usage\": \"$(df -h / | tail -1 | awk '{print $5}')\","
        echo "    \"memory_usage\": \"$(free -h | grep '^Mem:' | awk '{print $3"/"$2}')\","
        echo "    \"load_average\": \"$(uptime | awk -F'load average:' '{print $2}')\""
        echo "  },"
        echo "  \"health_checks\": \"$(get_state_value 'system_health_status' 'unknown')\","
        echo "  \"status\": \"initiated\""
        echo "}"
    } > "$record_file"
    
    log "INFO" "Reboot attempt record created: $record_file"
}

# Perform graceful shutdown procedures
perform_graceful_shutdown() {
    log "INFO" "Performing graceful shutdown procedures"
    
    # Create pre-shutdown system state backup if enabled
    if [[ "${CREATE_PRE_REBOOT_BACKUP:-true}" == "true" ]]; then
        create_system_backup
    fi
    
    # Gracefully stop non-critical services if enabled
    if [[ "${STOP_NON_CRITICAL_SERVICES:-true}" == "true" ]]; then
        graceful_stop_services
    fi
    
    # Sync filesystems if enabled
    if [[ "${SYNC_FILESYSTEMS:-true}" == "true" ]]; then
        sync_filesystems
    fi
    
    # Final log flush
    if command -v journalctl >/dev/null 2>&1; then
        journalctl --sync >/dev/null 2>&1
    fi
    
    log "INFO" "Graceful shutdown procedures completed"
    return 0
}

# Create system state backup before reboot
create_system_backup() {
    local backup_dir="${LOG_DIRECTORY}/pre-reboot-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup critical system information
    {
        echo "# Pre-reboot system state backup - $(date)"
        echo "## System Information"
        uname -a
        echo
        echo "## Uptime"
        uptime
        echo
        echo "## Disk Usage"
        df -h
        echo
        echo "## Memory Usage"
        free -h
        echo
        echo "## Network Interfaces"
        ip addr show
        echo
        echo "## Running Services"
        if command -v systemctl >/dev/null 2>&1; then
            systemctl list-units --type=service --state=running --no-legend
        fi
        echo
        echo "## Recent Logs (last 20 lines)"
        if [[ -f "${LOG_DIRECTORY}/auto-update-reboot.log" ]]; then
            tail -20 "${LOG_DIRECTORY}/auto-update-reboot.log"
        fi
    } > "$backup_dir/system-state.txt"
    
    # Backup current configuration
    if [[ -f "${SCRIPT_DIR}/../config.yaml" ]]; then
        cp "${SCRIPT_DIR}/../config.yaml" "$backup_dir/config.yaml.backup"
    fi
    
    # Backup current working state
    if [[ -f "$STATE_FILE" ]]; then
        cp "$STATE_FILE" "$backup_dir/state-file.backup"
    fi
    
    log "INFO" "System state backup created: $backup_dir"
}

# Gracefully stop critical services
graceful_stop_services() {
    if ! command -v systemctl >/dev/null 2>&1; then
        return 0  # Systemd not available
    fi
    
    local critical_services=("nginx" "apache2" "mysql" "postgresql" "docker")
    
    log "INFO" "Attempting graceful shutdown of non-critical services"
    
    # Stop non-critical services first
    for service in "${critical_services[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            log "DEBUG" "Stopping service: $service"
            systemctl stop "$service" >/dev/null 2>&1 || log "WARNING" "Failed to stop $service"
        fi
    done
    
    # Give services time to stop
    sleep 5
    
    log "INFO" "Graceful service shutdown completed"
}

# Sync filesystems to ensure data integrity
sync_filesystems() {
    log "INFO" "Syncing filesystems"
    sync
    sleep 2
    sync
    log "DEBUG" "Filesystems synced"
}

# Countdown with periodic safety checks during delay
countdown_with_checks() {
    local total_seconds="$1"
    local check_interval=30  # Check every 30 seconds
    
    log "INFO" "Starting ${total_seconds}s countdown with periodic safety checks"
    
    for ((i=total_seconds; i>0; i-=check_interval)); do
        local sleep_time=$((i < check_interval ? i : check_interval))
        sleep "$sleep_time"
        
        # Quick safety check every 30 seconds
        if ! quick_safety_check; then
            log "ERROR" "Safety check failed during countdown, aborting reboot"
            return 1
        fi
        
        local remaining=$((i - sleep_time))
        if [[ $remaining -gt 0 ]]; then
            log "INFO" "${remaining}s remaining until reboot..."
        fi
    done
    
    return 0
}

# Quick safety check during countdown
quick_safety_check() {
    # Quick disk space check
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 95 ]]; then
        log "ERROR" "Critical disk usage detected during countdown: ${disk_usage}%"
        return 1
    fi
    
    # Quick memory check
    local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [[ $memory_usage -gt 95 ]]; then
        log "ERROR" "Critical memory usage detected during countdown: ${memory_usage}%"
        return 1
    fi
    
    return 0
}

# Enhanced reboot attempt with multiple methods and monitoring
attempt_system_reboot() {
    local attempt_id="$1"
    local reboot_methods=("systemctl reboot" "shutdown -r now" "reboot" "init 6")
    
    for method in "${reboot_methods[@]}"; do
        log "INFO" "Attempting reboot via: $method"
        
        # Update attempt record
        update_reboot_attempt_record "$attempt_id" "attempting_$method"
        
        case "$method" in
            "systemctl reboot")
                if command -v systemctl >/dev/null 2>&1; then
                    timeout 30 systemctl reboot
                    local exit_code=$?
                    if [[ $exit_code -eq 0 ]]; then
                        update_reboot_attempt_record "$attempt_id" "success_systemctl"
                        return 0
                    fi
                fi
                ;;
            "shutdown -r now")
                if command -v shutdown >/dev/null 2>&1; then
                    timeout 30 shutdown -r now
                    local exit_code=$?
                    if [[ $exit_code -eq 0 ]]; then
                        update_reboot_attempt_record "$attempt_id" "success_shutdown"
                        return 0
                    fi
                fi
                ;;
            "reboot")
                if command -v reboot >/dev/null 2>&1; then
                    timeout 30 reboot
                    local exit_code=$?
                    if [[ $exit_code -eq 0 ]]; then
                        update_reboot_attempt_record "$attempt_id" "success_reboot"
                        return 0
                    fi
                fi
                ;;
            "init 6")
                if command -v init >/dev/null 2>&1; then
                    timeout 30 init 6
                    local exit_code=$?
                    if [[ $exit_code -eq 0 ]]; then
                        update_reboot_attempt_record "$attempt_id" "success_init"
                        return 0
                    fi
                fi
                ;;
        esac
        
        log "WARNING" "Reboot method '$method' failed, trying next method"
        sleep 2
    done
    
    log "ERROR" "All reboot methods failed"
    update_reboot_attempt_record "$attempt_id" "failed_all_methods"
    return 1
}

# Update reboot attempt record
update_reboot_attempt_record() {
    local attempt_id="$1"
    local status="$2"
    local record_file="${LOG_DIRECTORY}/reboot-attempt-${attempt_id}.json"
    
    if [[ -f "$record_file" ]]; then
        # Update the status field
        sed "s/\"status\": \"[^\"]*\"/\"status\": \"$status\"/" "$record_file" > "${record_file}.tmp" && mv "${record_file}.tmp" "$record_file"
    fi
}

# Abort reboot and restore system
abort_reboot() {
    local attempt_id="$1"
    
    log "WARNING" "Reboot aborted, restoring normal operations"
    update_reboot_attempt_record "$attempt_id" "aborted"
    
    # Send notification about aborted reboot
    if command -v systemd-notify >/dev/null 2>&1 && [[ -n "$NOTIFY_SOCKET" ]]; then
        systemd-notify --status="Reboot aborted - System restored"
    fi
    
    # Log the abort
    log "WARNING" "Reboot sequence aborted - System continuing normal operations"
}

# Enhanced reboot failure handler with rollback
handle_reboot_failure() {
    local attempt_id="$1"
    local failure_stage="${2:-unknown}"
    
    log "ERROR" "Reboot failure in stage: $failure_stage"
    update_reboot_attempt_record "$attempt_id" "failed_${failure_stage}"
    
    # Attempt recovery procedures
    attempt_recovery_procedures "$attempt_id" "$failure_stage"
    
    # Log system state after failure
    log_system_state_snapshot
    
    # Send failure notification
    send_failure_notification "$attempt_id" "$failure_stage"
    
    return 1
}

# Attempt recovery procedures after reboot failure
attempt_recovery_procedures() {
    local attempt_id="$1"
    local failure_stage="$2"
    
    log "INFO" "Attempting recovery procedures after reboot failure"
    
    case "$failure_stage" in
        "primary")
            log "INFO" "Primary reboot failed, trying emergency methods"
            # Try emergency reboot methods
            echo 1 > /proc/sys/kernel/sysrq 2>/dev/null
            echo b > /proc/sysrq-trigger 2>/dev/null
            ;;
        "graceful_shutdown")
            log "WARNING" "Graceful shutdown failed, system may be unstable"
            # Force filesystem sync
            sync; sync; sync
            ;;
        *)
            log "WARNING" "Unknown failure stage, attempting basic recovery"
            # Basic recovery: sync filesystems and log status
            sync
            ;;
    esac
    
    log "INFO" "Recovery procedures completed"
}

# Send failure notification
send_failure_notification() {
    local attempt_id="$1"
    local failure_stage="$2"
    
    log "ERROR" "REBOOT FAILURE: Attempt $attempt_id failed at stage: $failure_stage"
    log "ERROR" "Manual intervention may be required"
    
    # If Telegram is configured, send alert
    if [[ "${TELEGRAM_ENABLED:-false}" == "true" ]] && command -v telegram_logger >/dev/null 2>&1; then
        telegram_logger "CRITICAL" "Auto-reboot failed: $failure_stage (attempt: $attempt_id)"
    fi
    
    # Send systemd notification if available
    if command -v systemd-notify >/dev/null 2>&1 && [[ -n "$NOTIFY_SOCKET" ]]; then
        systemd-notify --status="Reboot failed: $failure_stage"
    fi
}

# Handle reboot failure
handle_reboot_failure() {
    local command="$1"
    local exit_code="$2"
    
    log "ERROR" "Reboot command '$command' failed with exit code: $exit_code"
    log_system_state_snapshot
    
    # Try alternative methods
    if [[ "$command" != "systemctl reboot" ]] && command -v systemctl >/dev/null 2>&1; then
        log "INFO" "Trying systemctl reboot as fallback"
        systemctl reboot
    elif [[ "$command" != "shutdown -r now" ]] && command -v shutdown >/dev/null 2>&1; then
        log "INFO" "Trying shutdown -r now as fallback"
        shutdown -r now
    else
        log "ERROR" "All reboot methods failed"
        return 1
    fi
}

# Enhanced main execution logic with comprehensive error handling
main() {
    local start_time=$(date +%s)
    log "INFO" "Starting enhanced auto-update-reboot cycle"
    
    # Initialize components
    initialize_state
    
    # Update detection statistics
    update_detection_stats "check"
    
    # Check safety mechanisms first
    if ! check_cooldown; then
        log "INFO" "Reboot cooldown active, exiting gracefully"
        update_detection_stats "success"
        exit 0
    fi
    
    if ! check_daily_limit; then
        log "INFO" "Daily reboot limit reached, exiting gracefully"
        update_detection_stats "success"
        exit 0
    fi
    
    # Check emergency override
    if [[ "$EMERGENCY_OVERRIDE" == "true" ]]; then
        log "WARNING" "Emergency override active, bypassing change detection"
        if check_system_health; then
            send_pre_reboot_notifications
            execute_reboot
        else
            log "ERROR" "System health check failed even with emergency override"
        fi
        exit $?
    fi
    
    # Enhanced repository checking with multiple fallback strategies
    local primary_repo="${MANAGED_REPO_PATH}/Auto-slopp"
    local backup_repo=""  # Could be configured for backup checking
    local reboot_needed=false
    local detection_success=false
    
    # Normalize repository path (expand ~)
    primary_repo=$(eval echo "$primary_repo")
    
    # Primary repository detection
    if detect_repository_changes "$primary_repo" "Auto-slopp"; then
        reboot_needed=true
        detection_success=true
        log "INFO" "Primary repository detection completed with reboot trigger"
    else
        local detection_exit_code=$?
        log "INFO" "Primary repository detection completed (exit code: $detection_exit_code)"
        
        # Determine if detection failed or just no changes
        if [[ $detection_exit_code -eq 0 ]]; then
            detection_success=true
            log "INFO" "Primary repository processed successfully (no reboot needed)"
        else
            log "WARNING" "Primary repository detection encountered issues"
            
            # Could implement fallback repositories here
            # if [[ -n "$backup_repo" ]]; then
            #     log "INFO" "Attempting backup repository detection"
            #     if detect_repository_changes "$backup_repo" "backup"; then
            #         reboot_needed=true
            #         detection_success=true
            #     fi
            # fi
        fi
    fi
    
    # Update statistics based on detection success
    if [[ "$detection_success" == "true" ]]; then
        update_detection_stats "success"
    else
        log "WARNING" "Repository detection failed, skipping this cycle"
        exit 1
    fi
    
    # Enhanced reboot decision logic with comprehensive safety checks
    if [[ "$reboot_needed" == "true" ]]; then
        log "WARNING" "Reboot conditions detected, initiating enhanced safety confirmation"
        
        # Perform comprehensive reboot safety confirmation
        if confirm_reboot_safety; then
            log "INFO" "Reboot safety confirmed, proceeding with enhanced reboot sequence"
            update_detection_stats "reboot"
            
            # Store reboot reason for logging
            set_state_value "last_reboot_reason" "Repository changes detected"
            
            # Determine reboot type (scheduled vs immediate)
            local reboot_type=$(determine_reboot_type)
            log "INFO" "Reboot type determined: $reboot_type"
            
            # Send enhanced pre-reboot notifications
            send_enhanced_pre_reboot_notifications "$reboot_type"
            
            # Execute enhanced reboot with comprehensive safeguards
            if ! execute_reboot; then
                log "ERROR" "Enhanced reboot execution failed, initiating failure recovery"
                handle_reboot_failure "unknown" "main_execution"
                exit 1
            fi
        else
            log "WARNING" "Reboot safety confirmation failed, reboot aborted for safety"
            
            # Create safety failure record
            create_safety_failure_record
            
            # Could implement alternative recovery strategies here
            log "INFO" "System will retry on next cycle with updated safety assessment"
            exit 1
        fi
    else
        log "INFO" "No reboot-triggering changes detected in this cycle"
        
        # Perform periodic maintenance tasks on successful non-reboot cycles
        perform_periodic_maintenance
    fi
    
    # Log completion with timing
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    log "INFO" "Auto-update-reboot cycle completed successfully in ${duration}s"
}

# Perform periodic maintenance tasks
perform_periodic_maintenance() {
    log "DEBUG" "Performing periodic maintenance tasks"
    
    # Clean up old state entries
    cleanup_old_state_entries
    
    # Log current statistics
    log_detection_statistics
    
    # Could add more maintenance tasks here
    return 0
}

# Clean up old state entries to prevent state file bloat
cleanup_old_state_entries() {
    local retention_days=7  # Keep state entries for 7 days
    local cutoff_timestamp=$(date -d "$retention_days days ago" -Iseconds 2>/dev/null)
    
    if [[ -z "$cutoff_timestamp" ]]; then
        # Fallback for systems without date -d support
        local cutoff_seconds=$(($(date +%s) - (retention_days * 24 * 3600)))
        cutoff_timestamp=$(date -d "@$cutoff_seconds" -Iseconds 2>/dev/null || echo "")
    fi
    
    if [[ -n "$cutoff_timestamp" && -f "$STATE_FILE" ]]; then
        log "DEBUG" "Cleaning up state entries older than $cutoff_timestamp"
        # Implementation would go here for cleaning old entries
        # This is a placeholder for the cleanup logic
    fi
}

# Log current detection statistics
log_detection_statistics() {
    local total_checks=$(get_state_value "total_checks" "0")
    local successful_checks=$(get_state_value "successful_checks" "0")
    local reboots_triggered=$(get_state_value "reboots_triggered" "0")
    
    log "INFO" "Detection statistics: Total checks: $total_checks, Successful: $successful_checks, Reboots: $reboots_triggered"
    
    # Calculate success rate
    if [[ $total_checks -gt 0 ]]; then
        local success_rate=$((successful_checks * 100 / total_checks))
        log "INFO" "Detection success rate: ${success_rate}%"
    fi
}

# Execute main function
main
log "INFO" "Auto-update-reboot cycle completed"