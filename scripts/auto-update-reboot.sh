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

# Initialize state management
initialize_state() {
    local state_dir=$(dirname "$STATE_FILE")
    mkdir -p "$state_dir"
    
    if [[ ! -f "$STATE_FILE" ]]; then
        log "INFO" "Initializing state file: $STATE_FILE"
        cat > "$STATE_FILE" << 'EOF'
{
  "last_reboot_timestamp": null,
  "reboot_attempts_today": 0,
  "current_date": "2026-01-30",
  "last_known_heads": {},
  "system_health_status": "unknown"
}
EOF
    fi
}

# Get state value from state file
get_state_value() {
    local key="$1"
    local default_value="${2:-null}"
    
    if [[ -f "$STATE_FILE" ]]; then
        # Extract value using simple JSON parsing (bash compatible)
        local value=$(grep -o "\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" "$STATE_FILE" | sed 's/.*: *"\([^"]*\)".*/\1/')
        echo "${value:-$default_value}"
    else
        echo "$default_value"
    fi
}

# Set state value in state file
set_state_value() {
    local key="$1"
    local value="$2"
    
    # Simple JSON value replacement (works for string values)
    if [[ -f "$STATE_FILE" ]]; then
        if grep -q "\"$key\":" "$STATE_FILE"; then
            # Update existing key
            sed -i "s/\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"/\"$key\": \"$value\"/" "$STATE_FILE"
        else
            # Add new key (before closing brace)
            sed -i "s/}/,  \"$key\": \"$value\"\n}/" "$STATE_FILE"
        fi
    fi
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

# Check system health before reboot
check_system_health() {
    log "INFO" "Performing system health checks"
    
    # Check disk space (must have at least 10% free)
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        log "ERROR" "Disk usage too high: ${disk_usage}% (must be < 90%)"
        return 1
    fi
    log_system_health "disk_space" "pass" "Disk usage: ${disk_usage}%"
    
    # Check memory usage (must have at least 10% free)
    local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [[ $memory_usage -gt 90 ]]; then
        log "ERROR" "Memory usage too high: ${memory_usage}% (must be < 90%)"
        return 1
    fi
    log_system_health "memory_usage" "pass" "Memory usage: ${memory_usage}%"
    
    # Check if critical processes are running (basic check)
    if command -v systemctl >/dev/null 2>&1; then
        local failed_services=$(systemctl list-units --failed --no-legend | wc -l)
        if [[ $failed_services -gt 0 ]]; then
            log "WARNING" "Found $failed_services failed services"
            # Not a hard failure, but worth noting
        fi
    fi
    
    log_system_health "system_health" "pass" "All health checks passed"
    set_state_value "system_health_status" "healthy"
    return 0
}

# Detect changes in a git repository
detect_repository_changes() {
    local repo_path="$1"
    local repo_name="$2"
    
    if [[ ! -d "$repo_path" ]]; then
        log "WARNING" "Repository path not found: $repo_path"
        return 1
    fi
    
    log "INFO" "Checking for changes in repository: $repo_name"
    
    cd "$repo_path" || return 1
    
    # Store current HEAD
    local current_head=$(git rev-parse HEAD 2>/dev/null)
    if [[ -z "$current_head" ]]; then
        log "ERROR" "Failed to get current HEAD for $repo_name"
        return 1
    fi
    
    # Get last known HEAD from state
    local last_known_head=$(get_state_value "last_known_heads" | grep -o "\"$repo_path\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | sed 's/.*: *"\([^"]*\)".*/\1/' || echo "")
    
    # Pull latest changes
    log "INFO" "Pulling latest changes for $repo_name"
    if ! git pull origin 2>/dev/null; then
        log "WARNING" "Git pull failed for $repo_name, continuing with current state"
        return 1
    fi
    
    # Get new HEAD after pull
    local new_head=$(git rev-parse HEAD 2>/dev/null)
    
    # Check if HEAD changed
    if [[ "$current_head" != "$new_head" ]]; then
        log "INFO" "Repository $repo_name has updates: $current_head -> $new_head"
        
        # Get list of changed files
        local changed_files=$(git diff --name-only "$current_head" "$new_head")
        local changes_count=$(echo "$changed_files" | wc -l)
        
        log_change_detection "$repo_name" "$changes_count" "false"
        
        # Check if any changes match reboot triggers
        # Default reboot triggers for automation system
        local reboot_triggered=false
        while IFS= read -r file; do
            if [[ "$file" =~ ^(scripts/.*\.sh|config\.yaml|main\.sh|scripts/utils\.sh)$ ]]; then
                log "WARNING" "Reboot-triggering file changed in $repo_name: $file"
                reboot_triggered=true
                break
            fi
        done <<< "$changed_files"
        
        if [[ "$reboot_triggered" == "true" ]]; then
            log_change_detection "$repo_name" "$changes_count" "true"
            return 0  # Signal reboot needed
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

# Send pre-reboot notifications
send_pre_reboot_notifications() {
    local scheduled_time=$(date -d "+${REBOOT_DELAY_SECONDS} seconds" '+%Y-%m-%d %H:%M:%S')
    
    log_reboot_event "Repository changes detected requiring system reboot" "$scheduled_time"
    
    # Log system state before reboot
    log_system_state_snapshot
    
    # Send systemd notification if available
    if command -v systemd-notify >/dev/null 2>&1 && [[ -n "$NOTIFY_SOCKET" ]]; then
        systemd-notify --status="Preparing for reboot due to repository changes"
    fi
    
    log "WARNING" "System will reboot in ${REBOOT_DELAY_SECONDS} seconds"
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

# Execute system reboot
execute_reboot() {
    log "WARNING" "Executing system reboot"
    
    # Update state before reboot
    update_reboot_state
    
    # Wait for the configured delay
    if [[ $REBOOT_DELAY_SECONDS -gt 0 ]]; then
        log "INFO" "Waiting ${REBOOT_DELAY_SECONDS} seconds before reboot..."
        sleep "$REBOOT_DELAY_SECONDS"
    fi
    
    # Attempt reboot with multiple methods
    if command -v systemctl >/dev/null 2>&1; then
        log "INFO" "Rebooting via systemctl"
        systemctl reboot || handle_reboot_failure "systemctl reboot" "$?"
    elif command -v shutdown >/dev/null 2>&1; then
        log "INFO" "Rebooting via shutdown"
        shutdown -r now || handle_reboot_failure "shutdown -r now" "$?"
    else
        log "ERROR" "No supported reboot command found"
        return 1
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

# Main execution logic
main() {
    # Initialize components
    initialize_state
    
    # Check safety mechanisms
    if ! check_cooldown; then
        exit 0
    fi
    
    if ! check_daily_limit; then
        exit 0
    fi
    
    # Check primary repository (Auto-slopp)
    local primary_repo="${MANAGED_REPO_PATH}/Auto-slopp"
    local reboot_needed=false
    
    if detect_repository_changes "$primary_repo" "Auto-slopp"; then
        reboot_needed=true
    fi
    
    # If reboot is needed and system health is OK, proceed with reboot
    if [[ "$reboot_needed" == "true" ]]; then
        if check_system_health; then
            send_pre_reboot_notifications
            execute_reboot
        else
            log "WARNING" "System health check failed, reboot aborted"
        fi
    else
        log "INFO" "No reboot-triggering changes detected"
    fi
}

# Execute main function
main
log "INFO" "Auto-update-reboot cycle completed"