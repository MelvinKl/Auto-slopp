#!/bin/bash

# Beads Updater Script - Automated Repository Synchronization
# CRITICAL P0: Provides automated sync engine for beads state across repositories
# Integrates with existing logging, config, and error handling systems
# Set script name for logging identification
SCRIPT_NAME="beads_updater"

# Load utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# Set up error handling
setup_error_handling

# Beads updater specific configuration
BEADS_UPDATER_VERSION="1.0.0"
BEADS_UPDATER_TEMP_DIR="/tmp/beads_updater_$$"
BEADS_UPDATER_BACKUP_DIR="$HOME/.beads_updater_backups"
BEADS_UPDATER_LOG_PREFIX="beads_updater"
BEADS_UPDATER_LOCK_FILE="/tmp/beads_updater.lock"

# Conflict resolution strategies
CONFLICT_STRATEGY_NEWEST=1
CONFLICT_STRATEGY_MANUAL=2
CONFLICT_STRATEGY_KEEP_LOCAL=3
CONFLICT_STRATEGY_KEEP_REMOTE=4

# Default sync mode (can be overridden by config)
DEFAULT_SYNC_MODE="incremental"  # "incremental" or "full"
DEFAULT_CONFLICT_STRATEGY=$CONFLICT_STRATEGY_NEWEST
DEFAULT_MAX_RETRIES=3
DEFAULT_RETRY_DELAY=5

# Initialize beads updater environment
init_beads_updater() {
    local sync_mode="${1:-$DEFAULT_SYNC_MODE}"
    
    log "INFO" "Initializing Beads Updater v$BEADS_UPDATER_VERSION"
    log "INFO" "Sync mode: $sync_mode"
    log "INFO" "Conflict strategy: $(get_conflict_strategy_name $DEFAULT_CONFLICT_STRATEGY)"
    
    # Create required directories
    mkdir -p "$BEADS_UPDATER_TEMP_DIR" || {
        log "ERROR" "Failed to create temp directory: $BEADS_UPDATER_TEMP_DIR"
        return 1
    }
    
    mkdir -p "$BEADS_UPDATER_BACKUP_DIR" || {
        log "ERROR" "Failed to create backup directory: $BEADS_UPDATER_BACKUP_DIR"
        return 1
    }
    
    # Check if bd command is available
    if ! command_exists bd; then
        log "ERROR" "bd command not found - beads CLI is required"
        return 1
    fi
    
    # Check if we're in a git repository with beads
    if [ ! -d ".beads" ]; then
        log "ERROR" "No .beads directory found - not a beads-enabled repository"
        return 1
    fi
    
    # Initialize backup counter
    export BEADS_UPDATER_BACKUP_COUNTER=0
    
    log "SUCCESS" "Beads updater initialized successfully"
    return 0
}

# Cleanup function for temporary files and locks
cleanup_beads_updater() {
    local exit_code=$?
    
    log "INFO" "Cleaning up beads updater"
    
    # Remove temp directory
    if [ -d "$BEADS_UPDATER_TEMP_DIR" ]; then
        rm -rf "$BEADS_UPDATER_TEMP_DIR"
    fi
    
    # Remove lock file
    if [ -f "$BEADS_UPDATER_LOCK_FILE" ]; then
        rm -f "$BEADS_UPDATER_LOCK_FILE"
    fi
    
    # Log cleanup completion
    if [ $exit_code -eq 0 ]; then
        log "SUCCESS" "Beads updater cleanup completed successfully"
    else
        log "WARNING" "Beads updater cleanup completed with exit code: $exit_code"
    fi
    
    return $exit_code
}

# Set up cleanup trap
trap cleanup_beads_updater EXIT

# Check if another updater instance is running
check_updater_lock() {
    if [ -f "$BEADS_UPDATER_LOCK_FILE" ]; then
        local pid=$(cat "$BEADS_UPDATER_LOCK_FILE" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            log "WARNING" "Another beads updater instance is running (PID: $pid)"
            log "INFO" "If this is incorrect, remove $BEADS_UPDATER_LOCK_FILE"
            return 1
        else
            log "INFO" "Removing stale lock file"
            rm -f "$BEADS_UPDATER_LOCK_FILE"
        fi
    fi
    
    # Create lock file with current PID
    echo $$ > "$BEADS_UPDATER_LOCK_FILE" || {
        log "ERROR" "Failed to create lock file: $BEADS_UPDATER_LOCK_FILE"
        return 1
    }
    
    log "DEBUG" "Updater lock acquired (PID: $$)"
    return 0
}

# Get human-readable name for conflict strategy
get_conflict_strategy_name() {
    local strategy="$1"
    
    case "$strategy" in
        $CONFLICT_STRATEGY_NEWEST) echo "newest" ;;
        $CONFLICT_STRATEGY_MANUAL) echo "manual" ;;
        $CONFLICT_STRATEGY_KEEP_LOCAL) echo "keep_local" ;;
        $CONFLICT_STRATEGY_KEEP_REMOTE) echo "keep_remote" ;;
        *) echo "unknown" ;;
    esac
}

# Create backup of current beads state
backup_beads_state() {
    local backup_name="$1"
    local backup_dir="$BEADS_UPDATER_BACKUP_DIR/${backup_name}_$(date +%Y%m%d_%H%M%S)"
    
    log "INFO" "Creating backup: $backup_name"
    
    mkdir -p "$backup_dir" || {
        log "ERROR" "Failed to create backup directory: $backup_dir"
        return 1
    }
    
    # Backup critical beads files
    local files_to_backup=(
        ".beads/issues.jsonl"
        ".beads/interactions.jsonl"
        ".beads/metadata.json"
        ".beads/config.yaml"
    )
    
    for file in "${files_to_backup[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$backup_dir/" || {
                log "WARNING" "Failed to backup file: $file"
            }
        fi
    done
    
    # Create backup metadata
    cat > "$backup_dir/backup_info.json" << EOF
{
    "backup_name": "$backup_name",
    "created_at": "$(date -Iseconds)",
    "script_version": "$BEADS_UPDATER_VERSION",
    "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "git_branch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')",
    "beads_version": "$(bd --version 2>/dev/null || echo 'unknown')",
    "files_backed_up": $(ls -1 "$backup_dir" | grep -v backup_info.json | wc -l)
}
EOF
    
    export BEADS_UPDATER_BACKUP_COUNTER=$((BEADS_UPDATER_BACKUP_COUNTER + 1))
    log "SUCCESS" "Backup created: $backup_dir"
    
    # Return backup path for potential restore
    echo "$backup_dir"
    return 0
}

# Validate beads data integrity
validate_beads_data() {
    local data_path="${1:-.beads/issues.jsonl}"
    
    log "DEBUG" "Validating beads data: $data_path"
    
    if [ ! -f "$data_path" ]; then
        log "ERROR" "Beads data file not found: $data_path"
        return 1
    fi
    
    # Check if file is valid JSONL
    local line_count=0
    local invalid_lines=0
    
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            ((line_count++))
            # Basic JSON validation - check for opening/closing braces
            if ! echo "$line" | python3 -m json.tool >/dev/null 2>&1; then
                ((invalid_lines++))
                log "WARNING" "Invalid JSON line $line_count: ${line:0:100}..."
            fi
        fi
    done < "$data_path"
    
    if [ $invalid_lines -gt 0 ]; then
        log "ERROR" "Found $invalid_lines invalid JSON lines out of $line_count total"
        return 1
    fi
    
    log "DEBUG" "Beads data validation passed: $line_count valid lines"
    return 0
}

# Get current sync status
get_sync_status() {
    log "DEBUG" "Getting beads sync status"
    
    local sync_output
    if ! sync_output=$(bd sync --status 2>/dev/null); then
        log "ERROR" "Failed to get sync status"
        return 1
    fi
    
    # Parse sync status for key information
    local pending_changes=$(echo "$sync_output" | grep "Pending changes" | grep -o '[0-9]\+' || echo "0")
    local last_export=$(echo "$sync_output" | grep "Last export" | cut -d':' -f2- | xargs || echo "never")
    local conflicts=$(echo "$sync_output" | grep "Conflicts" | cut -d':' -f2- | xargs || echo "none")
    
    log "DEBUG" "Sync status - Pending: $pending_changes, Last export: $last_export, Conflicts: $conflicts"
    
    echo "$pending_changes|$last_export|$conflicts"
    return 0
}

# Perform git pull with error handling
safe_git_pull() {
    local remote="${1:-origin}"
    local branch="${2:-main}"
    
    log "INFO" "Pulling latest changes from $remote/$branch"
    
    # Get current commit before pull
    local before_commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    
    if git pull "$remote" "$branch" 2>/dev/null; then
        local after_commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
        
        if [ "$before_commit" != "$after_commit" ]; then
            log "INFO" "Git pull successful - changes detected"
            log "DEBUG" "Before: $before_commit, After: $after_commit"
            return 0
        else
            log "DEBUG" "Git pull successful - no changes"
            return 0
        fi
    else
        log "ERROR" "Git pull failed from $remote/$branch"
        return 1
    fi
}

# Detect beads conflicts
detect_beads_conflicts() {
    log "DEBUG" "Detecting beads conflicts"
    
    local sync_status
    if ! sync_status=$(get_sync_status); then
        log "ERROR" "Failed to get sync status for conflict detection"
        return 1
    fi
    
    local conflicts=$(echo "$sync_status" | cut -d'|' -f3)
    
    if [ "$conflicts" != "none" ] && [ -n "$conflicts" ]; then
        log "WARNING" "Beads conflicts detected: $conflicts"
        return 2  # Special exit code for conflicts
    else
        log "DEBUG" "No beads conflicts detected"
        return 0
    fi
}

# Resolve beads conflicts using specified strategy
resolve_beads_conflicts() {
    local strategy="${1:-$DEFAULT_CONFLICT_STRATEGY}"
    
    log "INFO" "Resolving beads conflicts using strategy: $(get_conflict_strategy_name $strategy)"
    
    case "$strategy" in
        $CONFLICT_STRATEGY_NEWEST)
            log "INFO" "Using newest conflict resolution (default beads behavior)"
            # Beads automatically uses newest strategy, just continue
            ;;
            
        $CONFLICT_STRATEGY_KEEP_LOCAL)
            log "INFO" "Keeping local changes - forcing export"
            if ! bd sync --force-export 2>/dev/null; then
                log "ERROR" "Failed to force export local changes"
                return 1
            fi
            ;;
            
        $CONFLICT_STRATEGY_KEEP_REMOTE)
            log "INFO" "Keeping remote changes - forcing import"
            if ! bd sync --force-import 2>/dev/null; then
                log "ERROR" "Failed to force import remote changes"
                return 1
            fi
            ;;
            
        $CONFLICT_STRATEGY_MANUAL)
            log "ERROR" "Manual conflict resolution required - automated resolution not possible"
            log "INFO" "Please run 'bd sync' manually to resolve conflicts"
            return 2
            ;;
            
        *)
            log "ERROR" "Unknown conflict strategy: $strategy"
            return 1
            ;;
    esac
    
    return 0
}

# Perform beads sync operation
perform_beads_sync() {
    local sync_mode="${1:-$DEFAULT_SYNC_MODE}"
    local strategy="${2:-$DEFAULT_CONFLICT_STRATEGY}"
    local max_retries="${3:-$DEFAULT_MAX_RETRIES}"
    
    log "INFO" "Performing beads sync (mode: $sync_mode, strategy: $(get_conflict_strategy_name $strategy))"
    
    local attempt=1
    local sync_success=false
    
    while [ $attempt -le $max_retries ]; do
        log "INFO" "Sync attempt $attempt of $max_retries"
        
        # Create backup before sync attempt
        backup_beads_state "pre_sync_attempt_${attempt}"
        
        # Get sync status before
        local before_status
        if ! before_status=$(get_sync_status); then
            log "ERROR" "Failed to get pre-sync status"
        else
            local pending_before=$(echo "$before_status" | cut -d'|' -f1)
            log "DEBUG" "Pre-sync pending changes: $pending_before"
        fi
        
        # Perform the sync
        if bd sync 2>/dev/null; then
            log "SUCCESS" "Beads sync completed successfully"
            sync_success=true
            break
        else
            local exit_code=$?
            log "WARNING" "Beads sync failed (attempt $attempt, exit code: $exit_code)"
            
            # Check if it's a conflict issue
            if detect_beads_conflicts; then
                log "INFO" "Attempting to resolve conflicts with strategy: $(get_conflict_strategy_name $strategy)"
                
                if resolve_beads_conflicts "$strategy"; then
                    log "INFO" "Conflicts resolved, retrying sync"
                    sleep $DEFAULT_RETRY_DELAY
                    ((attempt++))
                    continue
                else
                    log "ERROR" "Failed to resolve conflicts"
                    break
                fi
            else
                log "WARNING" "Sync failed for non-conflict reasons, retrying..."
                sleep $DEFAULT_RETRY_DELAY
                ((attempt++))
                continue
            fi
        fi
    done
    
    if [ "$sync_success" = true ]; then
        # Validate sync result
        local after_status
        if after_status=$(get_sync_status); then
            local pending_after=$(echo "$after_status" | cut -d'|' -f1)
            log "DEBUG" "Post-sync pending changes: $pending_after"
            
            if [ "$pending_after" = "0" ]; then
                log "SUCCESS" "All changes synced successfully"
                return 0
            else
                log "WARNING" "Sync completed but $pending_after changes still pending"
                return 1
            fi
        else
            log "WARNING" "Sync completed but couldn't validate status"
            return 0
        fi
    else
        log "ERROR" "Beads sync failed after $max_retries attempts"
        return 1
    fi
}

# Generate comprehensive sync report
generate_sync_report() {
    local exit_code="$1"
    local sync_duration="$2"
    local backup_count="$3"
    
    # Ensure temp directory exists
    mkdir -p "$BEADS_UPDATER_TEMP_DIR"
    local report_file="$BEADS_UPDATER_TEMP_DIR/sync_report_$(date +%Y%m%d_%H%M%S).json"
    
    log "INFO" "Generating sync report: $report_file"
    
    # Gather system information
    local git_status=$(git status --porcelain 2>/dev/null | wc -l)
    local git_commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    local git_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    local beads_version=$(bd --version 2>/dev/null || echo "unknown")
    
    # Get final sync status
    local final_status
    if final_status=$(get_sync_status 2>/dev/null); then
        local pending_changes=$(echo "$final_status" | cut -d'|' -f1)
        local last_export=$(echo "$final_status" | cut -d'|' -f2)
        local conflicts=$(echo "$final_status" | cut -d'|' -f3)
    else
        local pending_changes="unknown"
        local last_export="unknown"
        local conflicts="unknown"
    fi
    
    # Generate JSON report
    cat > "$report_file" << EOF
{
    "sync_report": {
        "timestamp": "$(date -Iseconds)",
        "script_version": "$BEADS_UPDATER_VERSION",
        "exit_code": $exit_code,
        "duration_seconds": $sync_duration,
        "success": $([ $exit_code -eq 0 ] && echo "true" || echo "false"),
        
        "sync_operation": {
            "mode": "${SYNC_MODE:-$DEFAULT_SYNC_MODE}",
            "conflict_strategy": "$(get_conflict_strategy_name ${CONFLICT_STRATEGY:-$DEFAULT_CONFLICT_STRATEGY})",
            "max_retries": ${MAX_RETRIES:-$DEFAULT_MAX_RETRIES},
            "backups_created": $backup_count
        },
        
        "beads_status": {
            "pending_changes": $pending_changes,
            "last_export": "$last_export",
            "conflicts": "$conflicts",
            "version": "$beads_version"
        },
        
        "git_status": {
            "modified_files": $git_status,
            "current_commit": "$git_commit",
            "current_branch": "$git_branch",
            "working_directory_clean": $([ $git_status -eq 0 ] && echo "true" || echo "false")
        },
        
        "system_info": {
            "hostname": "$(hostname)",
            "user": "$(whoami)",
            "working_directory": "$(pwd)",
            "uptime": "$(uptime | cut -d',' -f1 | xargs)"
        }
    }
}
EOF
    
    log "SUCCESS" "Sync report generated: $report_file"
    
    # Copy to log directory if configured
    if [ -n "${LOG_DIRECTORY}" ] && [ -d "${LOG_DIRECTORY}" ]; then
        local report_copy="${LOG_DIRECTORY}/beads_updater_report_$(date +%Y%m%d_%H%M%S).json"
        cp "$report_file" "$report_copy" 2>/dev/null || log "WARNING" "Failed to copy report to log directory"
        log "DEBUG" "Sync report copied to log directory: $report_copy"
    fi
    
    echo "$report_file"
}

# Main sync execution function
execute_sync() {
    local sync_mode="${1:-$DEFAULT_SYNC_MODE}"
    local strategy="${2:-$DEFAULT_CONFLICT_STRATEGY}"
    local max_retries="${3:-$DEFAULT_MAX_RETRIES}"
    
    local start_time=$(date +%s)
    local exit_code=0
    
    log "INFO" "=== Starting Beads Sync Operation ==="
    
    # Export variables for report generation
    export SYNC_MODE="$sync_mode"
    export CONFLICT_STRATEGY="$strategy"
    export MAX_RETRIES="$max_retries"
    
    # Validate environment
    if ! init_beads_updater "$sync_mode"; then
        log "ERROR" "Failed to initialize beads updater"
        return 1
    fi
    
    # Check for running instance
    if ! check_updater_lock; then
        return 1
    fi
    
    # Ensure we have latest git changes
    if ! safe_git_pull; then
        log "WARNING" "Git pull failed, proceeding with current state"
    fi
    
    # Validate current beads data
    if ! validate_beads_data; then
        log "ERROR" "Current beads data validation failed"
        return 1
    fi
    
    # Create initial backup
    local initial_backup
    if ! initial_backup=$(backup_beads_state "pre_sync"); then
        log "WARNING" "Failed to create initial backup, proceeding anyway"
    fi
    
    # Perform the sync operation
    if ! perform_beads_sync "$sync_mode" "$strategy" "$max_retries"; then
        log "ERROR" "Beads sync operation failed"
        exit_code=1
    fi
    
    # Validate sync result
    if ! validate_beads_data; then
        log "ERROR" "Post-sync beads data validation failed"
        exit_code=1
    fi
    
    # Calculate duration
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log "INFO" "=== Sync Operation Completed ==="
    log "INFO" "Duration: ${duration} seconds"
    
    # Generate report
    local report_file
    report_file=$(generate_sync_report $exit_code $duration ${BEADS_UPDATER_BACKUP_COUNTER:-0})
    
    # Log final status
    if [ $exit_code -eq 0 ]; then
        log "SUCCESS" "Beads updater completed successfully"
        log "INFO" "Report available: $report_file"
    else
        log "ERROR" "Beads updater failed"
        log "INFO" "Report available: $report_file"
        log "INFO" "Backups available in: $BEADS_UPDATER_BACKUP_DIR"
    fi
    
    return $exit_code
}

# Restore beads state from backup
restore_beads_backup() {
    local backup_dir="$1"
    
    if [ ! -d "$backup_dir" ]; then
        log "ERROR" "Backup directory not found: $backup_dir"
        return 1
    fi
    
    log "WARNING" "Restoring beads state from backup: $backup_dir"
    
    # Create current state backup before restore
    backup_beads_state "pre_restore"
    
    # Restore files from backup
    local files_to_restore=(
        "issues.jsonl"
        "interactions.jsonl" 
        "metadata.json"
        "config.yaml"
    )
    
    for file in "${files_to_restore[@]}"; do
        if [ -f "$backup_dir/$file" ]; then
            cp "$backup_dir/$file" ".beads/$file" || {
                log "ERROR" "Failed to restore file: $file"
                return 1
            }
            log "DEBUG" "Restored file: $file"
        else
            log "DEBUG" "File not found in backup: $file"
        fi
    done
    
    log "SUCCESS" "Beads state restored from backup"
    return 0
}

# List available backups
list_backups() {
    log "INFO" "Available beads backups:"
    
    if [ ! -d "$BEADS_UPDATER_BACKUP_DIR" ]; then
        log "INFO" "No backup directory found"
        return 0
    fi
    
    local backup_count=0
    for backup_dir in "$BEADS_UPDATER_BACKUP_DIR"/*; do
        if [ -d "$backup_dir" ] && [ -f "$backup_dir/backup_info.json" ]; then
            ((backup_count++))
            local backup_name=$(basename "$backup_dir")
            local backup_info="$backup_dir/backup_info.json"
            
            echo "  $backup_name:"
            if command -v jq >/dev/null 2>&1; then
                jq -r '"    Created: " + .created_at + "\n    Git commit: " + .git_commit + "\n    Files: " + (.files_backed_up|tostring)' "$backup_info" 2>/dev/null || echo "    Failed to parse backup info"
            else
                echo "    Created: $(grep created_at "$backup_info" 2>/dev/null | cut -d'"' -f4 || echo 'unknown')"
            fi
            echo ""
        fi
    done
    
    if [ $backup_count -eq 0 ]; then
        log "INFO" "No backups found"
    else
        log "INFO" "Found $backup_count backup(s)"
    fi
    
    return 0
}

# Show help information
show_help() {
    cat << 'EOF'
Beads Updater Script - Automated Repository Synchronization

USAGE:
    ./beads_updater.sh [OPTIONS]

OPTIONS:
    --mode MODE               Sync mode: "incremental" (default) or "full"
    --strategy STRATEGY       Conflict strategy: "newest" (default), "manual", "keep_local", "keep_remote"
    --max-retries COUNT       Maximum retry attempts (default: 3)
    --restore BACKUP_DIR      Restore beads state from specified backup
    --list-backups           List all available backups
    --validate-only          Only validate beads data, don't sync
    --help                   Show this help message

EXAMPLES:
    ./beads_updater.sh                          # Use defaults (incremental sync, newest strategy)
    ./beads_updater.sh --mode full              # Full sync with newest conflict resolution
    ./beads_updater.sh --strategy keep_local    # Keep local changes on conflicts
    ./beads_updater.sh --list-backups           # Show available backups
    ./beads_updater.sh --restore /path/to/backup # Restore from backup

ENVIRONMENT VARIABLES:
    LOG_LEVEL             Logging level (DEBUG, INFO, WARNING, ERROR)
    LOG_DIRECTORY         Directory for log files
    DEBUG_MODE            Enable debug logging (true/false)

CONFLICT STRATEGIES:
    newest     - Use newest timestamp (default beads behavior)
    manual     - Require manual conflict resolution
    keep_local - Force keeping local changes
    keep_remote- Force keeping remote changes

INTEGRATION:
    Integrates with existing Repository Automation System:
    - Uses utils.sh for logging and error handling
    - Reads config.yaml for configuration
    - Compatible with timestamped logging system
    - Generates detailed sync reports in JSON format

EXIT CODES:
    0 - Success
    1 - General error
    2 - Conflict requires manual resolution
    3 - Validation failed
EOF
}

# Main execution logic
main() {
    local sync_mode="$DEFAULT_SYNC_MODE"
    local strategy="$DEFAULT_CONFLICT_STRATEGY"
    local max_retries="$DEFAULT_MAX_RETRIES"
    local validate_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --mode)
                sync_mode="$2"
                shift 2
                ;;
            --strategy)
                case "$2" in
                    newest) strategy=$CONFLICT_STRATEGY_NEWEST ;;
                    manual) strategy=$CONFLICT_STRATEGY_MANUAL ;;
                    keep_local) strategy=$CONFLICT_STRATEGY_KEEP_LOCAL ;;
                    keep_remote) strategy=$CONFLICT_STRATEGY_KEEP_REMOTE ;;
                    *) log "ERROR" "Invalid conflict strategy: $2"; exit 1 ;;
                esac
                shift 2
                ;;
            --max-retries)
                max_retries="$2"
                shift 2
                ;;
            --restore)
                restore_beads_backup "$2"
                exit $?
                ;;
            --list-backups)
                list_backups
                exit 0
                ;;
            --validate-only)
                validate_only=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # These are now set above
    
    # Set SCRIPT_NAME for proper logging
    export SCRIPT_NAME="beads_updater"
    
    log "INFO" "Beads Updater Script v$BEADS_UPDATER_VERSION starting"
    
    # Change to repository root directory
    if ! cd "$(git rev-parse --show-toplevel 2>/dev/null)"; then
        log "ERROR" "Not in a git repository"
        exit 1
    fi
    
    # Check if we're in a beads-enabled repository
    if [ ! -d ".beads" ]; then
        log "ERROR" "No .beads directory found - not a beads-enabled repository"
        exit 1
    fi
    
    # Validate-only mode
    if [ "$validate_only" = true ]; then
        log "INFO" "Running in validation-only mode"
        
        if validate_beads_data; then
            log "SUCCESS" "Beads data validation passed"
            exit 0
        else
            log "ERROR" "Beads data validation failed"
            exit 3
        fi
    fi
    
    # Execute sync
    if execute_sync "$sync_mode" "$strategy" "$max_retries"; then
        log "SUCCESS" "Beads updater completed successfully"
        exit 0
    else
        log "ERROR" "Beads updater failed"
        exit 1
    fi
}

# Execute main function with all arguments
main "$@"