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
    
    # Enhanced reboot decision logic
    if [[ "$reboot_needed" == "true" ]]; then
        log "WARNING" "Reboot conditions detected, initiating reboot process"
        
        # Perform comprehensive system health check
        if check_system_health; then
            log "INFO" "System health check passed, proceeding with reboot"
            update_detection_stats "reboot"
            
            # Send pre-reboot notifications
            send_pre_reboot_notifications
            
            # Execute reboot with enhanced error handling
            if ! execute_reboot; then
                log "ERROR" "Reboot execution failed, manual intervention may be required"
                exit 1
            fi
        else
            log "WARNING" "System health check failed, reboot aborted"
            
            # Could implement alternative recovery strategies here
            log "INFO" "System will retry on next cycle"
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