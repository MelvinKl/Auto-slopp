#!/bin/bash

# Number State Manager for Unique Number Tracking
# Provides atomic, concurrent-safe number assignment operations
# Part of the unique number tracking system design

# Set script name for logging identification
SCRIPT_NAME="number_manager"

# Load utilities first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Set up error handling
setup_error_handling

# Configuration defaults
NUMBER_STATE_DIR="${MANAGED_REPO_PATH:-.}/.number_state"
LOCK_TIMEOUT=30
MAX_RETRIES=5
BACKUP_COUNT=5

# Initialize state directory and files
init_number_state() {
    local context_name="${1:-default}"
    
    mkdir -p "$NUMBER_STATE_DIR/backup"
    
    # Create state file if doesn't exist
    if [ ! -f "$NUMBER_STATE_DIR/state.json" ]; then
        cat > "$NUMBER_STATE_DIR/state.json" << EOF
{
    "used_numbers": [],
    "last_assigned": 0,
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "context_assignments": {},
    "version": "1.0",
    "metadata": {
        "creator": "number_manager.sh",
        "purpose": "unique_number_tracking"
    }
}
EOF
        log "INFO" "Initialized number state for context: $context_name"
    fi
    
    # Validate existing state
    if ! validate_state_file; then
        log "ERROR" "State file validation failed"
        return 1
    fi
    
    return 0
}

# Validate state file integrity
validate_state_file() {
    local state_file="$NUMBER_STATE_DIR/state.json"
    
    # Check if file exists and is readable
    [ ! -f "$state_file" ] && return 1
    
    # Check if it's valid JSON
    if ! jq empty "$state_file" 2>/dev/null; then
        log "WARNING" "State file is not valid JSON, attempting recovery"
        attempt_state_recovery || return 1
    fi
    
    # Check required fields
    local required_fields=("used_numbers" "last_assigned" "context_assignments")
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$state_file" >/dev/null; then
            log "ERROR" "Missing required field in state file: $field"
            return 1
        fi
    done
    
    return 0
}

# Attempt to recover corrupted state from backup
attempt_state_recovery() {
    local state_file="$NUMBER_STATE_DIR/state.json"
    local latest_backup
    
    latest_backup=$(ls -t "$NUMBER_STATE_DIR/backup/"*.json 2>/dev/null | head -1)
    if [ -f "$latest_backup" ]; then
        log "INFO" "Recovering state from backup: $(basename "$latest_backup")"
        cp "$latest_backup" "$state_file"
        return 0
    else
        log "WARNING" "No backup available, reinitializing state"
        rm -f "$state_file"
        init_number_state
        return $?
    fi
}

# Acquire exclusive lock on state with exponential backoff
acquire_lock() {
    local lock_file="$NUMBER_STATE_DIR/.lock"
    local timeout=$LOCK_TIMEOUT
    local attempt=0
    
    while [ $attempt -lt $timeout ]; do
        # Try to create lock atomically
        if (set -C; echo "$$:$(date +%s)" > "$lock_file") 2>/dev/null; then
            log "DEBUG" "Lock acquired successfully (attempt $((attempt + 1)))"
            return 0
        fi
        
        # Check if lock is stale
        if [ -f "$lock_file" ]; then
            local lock_info=$(cat "$lock_file")
            local lock_pid=$(echo "$lock_info" | cut -d: -f1)
            local lock_time=$(echo "$lock_info" | cut -d: -f2)
            local current_time=$(date +%s)
            
            # Check if process exists and is not us
            if [ "$lock_pid" != "$$" ]; then
                if ! kill -0 "$lock_pid" 2>/dev/null; then
                    log "WARNING" "Removing stale lock from dead process $lock_pid"
                    rm -f "$lock_file"
                    continue
                elif [ $((current_time - lock_time)) -gt 300 ]; then
                    log "WARNING" "Removing old lock (age: $((current_time - lock_time))s)"
                    rm -f "$lock_file"
                    continue
                fi
            fi
        fi
        
        # Exponential backoff with jitter
        local delay=$((1 + attempt / 2 + RANDOM % 2))
        sleep "$delay"
        attempt=$((attempt + 1))
    done
    
    log "ERROR" "Failed to acquire lock after $timeout seconds"
    return 1
}

# Release exclusive lock
release_lock() {
    local lock_file="$NUMBER_STATE_DIR/.lock"
    rm -f "$lock_file"
    log "DEBUG" "Lock released"
}

# Create backup of current state
backup_state() {
    local state_file="$NUMBER_STATE_DIR/state.json"
    local backup_file="$NUMBER_STATE_DIR/backup/state_$(date +%Y%m%d_%H%M%S).json"
    
    if [ -f "$state_file" ]; then
        cp "$state_file" "$backup_file"
        
        # Rotate old backups
        local backup_files=($(ls -t "$NUMBER_STATE_DIR/backup/"*.json))
        if [ ${#backup_files[@]} -gt $BACKUP_COUNT ]; then
            for ((i=$BACKUP_COUNT; i<${#backup_files[@]}; i++)); do
                rm -f "${backup_files[i]}"
            done
        fi
        
        log "DEBUG" "State backed up to: $(basename "$backup_file")"
    fi
}

# Get next unique number
get_next_number() {
    local task_context="$1"  # Context for tracking (e.g., repository name)
    local state_file="$NUMBER_STATE_DIR/state.json"
    
    if [ ! -f "$state_file" ]; then
        log "ERROR" "State file not found. Initialize with init_number_state() first."
        return 1
    fi
    
    if ! acquire_lock; then
        log "ERROR" "Failed to acquire lock for number assignment"
        return 1
    fi
    
    # Ensure lock is released on exit
    trap release_lock EXIT
    
    # Create backup before modification
    backup_state
    
    # Read current state
    local used_numbers last_assigned
    used_numbers=$(jq -r '.used_numbers[]?' "$state_file" 2>/dev/null || echo "")
    last_assigned=$(jq -r '.last_assigned' "$state_file" 2>/dev/null || echo "0")
    
    # Find next available number
    local next_num=$((last_assigned + 1))
    
    # Check if number is already used (find next available)
    while echo "$used_numbers" | grep -q "^${next_num}$"; do
        next_num=$((next_num + 1))
        
        # Prevent infinite loop
        if [ $next_num -gt 9999 ]; then
            log "ERROR" "Cannot assign number greater than 9999 (4-digit limit)"
            return 1
        fi
    done
    
    # Update state atomically
    local temp_file="${state_file}.tmp.$$"
    local update_result
    
    update_result=$(jq \
        --argjson num "$next_num" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --arg context "$task_context" \
        '.used_numbers += [$num] |
         .last_assigned = $num |
         .updated_at = $timestamp |
         .context_assignments[$context] = ($num | tostring) |
         .assignments += [{"number": $num, "context": $context, "timestamp": $timestamp}]' \
        "$state_file" > "$temp_file" 2>&1)
    
    if [ $? -eq 0 ]; then
        mv "$temp_file" "$state_file"
        log "INFO" "Assigned number $next_num for context: $task_context"
        echo "$next_num"
        return 0
    else
        log "ERROR" "Failed to update state: $update_result"
        rm -f "$temp_file"
        return 1
    fi
}

# Release a number (for cleanup or rollback)
release_number() {
    local number="$1"
    local task_context="${2:-unknown}"
    local state_file="$NUMBER_STATE_DIR/state.json"
    
    # Validate input
    if ! [[ "$number" =~ ^[0-9]+$ ]] || [ "$number" -lt 0 ] || [ "$number" -gt 9999 ]; then
        log "ERROR" "Invalid number: $number (must be 0-9999)"
        return 1
    fi
    
    if ! acquire_lock; then
        return 1
    fi
    
    trap release_lock EXIT
    backup_state
    
    # Remove number from used list and update assignments
    local temp_file="${state_file}.tmp.$$"
    local update_result
    
    update_result=$(jq \
        --argjson num "$number" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '.used_numbers -= [$num] |
         .updated_at = $timestamp |
         .releases += [{"number": $num, "context": "'$task_context'", "timestamp": $timestamp}]' \
        "$state_file" > "$temp_file" 2>&1)
    
    if [ $? -eq 0 ]; then
        mv "$temp_file" "$state_file"
        log "INFO" "Released number $number for context: $task_context"
        return 0
    else
        log "ERROR" "Failed to release number $number: $update_result"
        rm -f "$temp_file"
        return 1
    fi
}

# Get current state statistics
get_state_stats() {
    local state_file="$NUMBER_STATE_DIR/state.json"
    
    if [ ! -f "$state_file" ]; then
        echo '{"status": "not_initialized", "message": "State file not found"}'
        return
    fi
    
    if ! validate_state_file; then
        echo '{"status": "corrupted", "message": "State file is corrupted"}'
        return
    fi
    
    jq \
        '{
            status: "healthy",
            used_count: (.used_numbers | length),
            last_assigned: .last_assigned,
            created_at: .created_at,
            updated_at: .updated_at,
            context_count: (.context_assignments | keys | length),
            contexts: .context_assignments,
            version: .version
        }' \
        "$state_file"
}

# Show number usage by context
get_context_assignments() {
    local state_file="$NUMBER_STATE_DIR/state.json"
    
    if [ ! -f "$state_file" ]; then
        echo '{"error": "State file not found"}'
        return 1
    fi
    
    jq '.context_assignments' "$state_file"
}

# Check for gaps in numbering (for a specific context or all)
check_number_gaps() {
    local context_filter="${1:-}"
    local state_file="$NUMBER_STATE_DIR/state.json"
    
    if [ ! -f "$state_file" ]; then
        echo "No state file found"
        return 1
    fi
    
    local used_numbers max_num
    used_numbers=$(jq -r '.used_numbers[]?' "$state_file" | sort -n)
    max_num=$(jq -r '.last_assigned' "$state_file")
    
    echo "Checking for gaps in numbering (last assigned: $max_num):"
    
    local gaps_found=false
    for ((i=1; i<=max_num; i++)); do
        if ! echo "$used_numbers" | grep -q "^${i}$"; then
            echo "  Gap: number $i is not used"
            gaps_found=true
        fi
    done
    
    if [ "$gaps_found" = false ]; then
        echo "  No gaps found in numbering sequence"
    fi
}

# Synchronize state with actual files in task directory
sync_state_with_files() {
    local task_dir="$1"
    local context_name="${2:-$(basename "$task_dir")}"
    
    if [ ! -d "$task_dir" ]; then
        log "ERROR" "Task directory not found: $task_dir"
        return 1
    fi
    
    if ! acquire_lock; then
        return 1
    fi
    
    trap release_lock EXIT
    backup_state
    
    # Find actual files in task directory
    local actual_files=($(find "$task_dir" -maxdepth 1 -type f -name "[0-9][0-9][0-9][0-9]-*.txt" ! -name "*.used"))
    local actual_numbers=()
    
    # Extract numbers from actual files
    for file in "${actual_files[@]}"; do
        basename_num=$(basename "$file" | sed 's/^\([0-9][0-9][0-9][0-9]\)-.*/\1/')
        if [[ "$basename_num" =~ ^[0-9][0-9][0-9][0-9]$ ]]; then
            actual_numbers+=("$((10#$basename_num))")
        fi
    done
    
    # Update state to match reality
    local state_file="$NUMBER_STATE_DIR/state.json"
    local temp_file="${state_file}.tmp.$$"
    local update_result
    
    update_result=$(jq \
        --argjson actual "$(printf '%s\n' "${actual_numbers[@]}" | sort -n | jq -R . | jq -s .)" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --arg context "$context_name" \
        '.used_numbers = $actual |
         .updated_at = $timestamp |
         .context_assignments[$context] = ($actual | map(tostring) | if length > 0 then last else empty end) |
         .last_assigned = ($actual | max // 0)' \
        "$state_file" > "$temp_file" 2>&1)
    
    if [ $? -eq 0 ]; then
        mv "$temp_file" "$state_file"
        log "INFO" "Synchronized state with actual files in $task_dir (${#actual_numbers[@]} files)"
        echo "Synced ${#actual_numbers[@]} files for context: $context_name"
        return 0
    else
        log "ERROR" "Failed to sync state: $update_result"
        rm -f "$temp_file"
        return 1
    fi
}

# Cleanup old state files and optimize storage
cleanup_state() {
    local days_old="${1:-30}"
    local cutoff_date=$(date -d "$days_old days ago" +%Y%m%d)
    
    # Remove old backup files
    local removed_count=0
    for backup_file in "$NUMBER_STATE_DIR/backup/"state_*.json; do
        if [ -f "$backup_file" ]; then
            local file_date=$(basename "$backup_file" | sed 's/state_\([0-9][0-9][0-9][0-9]\)\([0-9][0-9]\)\([0-9][0-9]\)_\(.*\)\.json/\1\2\3/')
            if [ "$file_date" -lt "$cutoff_date" ]; then
                rm -f "$backup_file"
                removed_count=$((removed_count + 1))
            fi
        fi
    done
    
    log "INFO" "Cleanup completed: removed $removed_count old backup files"
    echo "Removed $removed_count backup files older than $days_old days"
}

# Validate number assignment consistency
validate_assignments() {
    local task_dir="$1"
    local context_name="${2:-$(basename "$task_dir")}"
    
    if [ ! -d "$task_dir" ]; then
        echo "Error: Task directory not found: $task_dir"
        return 1
    fi
    
    local state_file="$NUMBER_STATE_DIR/state.json"
    if [ ! -f "$state_file" ]; then
        echo "Error: State file not found"
        return 1
    fi
    
    echo "Validating number assignment consistency for context: $context_name"
    
    # Get state numbers
    local state_numbers
    state_numbers=$(jq -r ".used_numbers[]?" "$state_file" | sort -n)
    
    # Get file numbers
    local file_numbers=()
    local file_list=($(find "$task_dir" -maxdepth 1 -type f -name "[0-9][0-9][0-9][0-9]-*.txt" ! -name "*.used"))
    
    for file in "${file_list[@]}"; do
        basename_num=$(basename "$file" | sed 's/^\([0-9][0-9][0-9][0-9]\)-.*/\1/')
        if [[ "$basename_num" =~ ^[0-9][0-9][0-9][0-9]$ ]]; then
            file_numbers+=("$((10#$basename_num))")
        fi
    done
    
    # Compare and report inconsistencies
    local state_only file_only
    state_only=$(comm -23 <(echo "$state_numbers") <(printf '%s\n' "${file_numbers[@]}" | sort -n))
    file_only=$(comm -13 <(echo "$state_numbers") <(printf '%s\n' "${file_numbers[@]}" | sort -n))
    
    if [ -n "$state_only" ]; then
        echo "Numbers in state but not in files:"
        echo "$state_only" | sed 's/^/  /'
    fi
    
    if [ -n "$file_only" ]; then
        echo "Numbers in files but not in state:"
        echo "$file_only" | sed 's/^/  /'
    fi
    
    if [ -z "$state_only" ] && [ -z "$file_only" ]; then
        echo "No inconsistencies found"
        return 0
    else
        echo "Inconsistencies found - consider running sync_state_with_files"
        return 1
    fi
}

# Command line interface
case "${1:-}" in
    "init")
        init_number_state "${2:-default}"
        ;;
    "get")
        get_next_number "${2:-default}"
        ;;
    "release")
        release_number "$2" "${3:-unknown}"
        ;;
    "stats")
        get_state_stats | jq '.'
        ;;
    "contexts")
        get_context_assignments | jq '.'
        ;;
    "gaps")
        check_number_gaps "$2"
        ;;
    "sync")
        sync_state_with_files "$2" "$3"
        ;;
    "validate")
        validate_assignments "$2" "$3"
        ;;
    "cleanup")
        cleanup_state "${2:-30}"
        ;;
    *)
        echo "Usage: $0 {init|get|release|stats|contexts|gaps|sync|validate|cleanup} [args]"
        echo ""
        echo "Commands:"
        echo "  init [context]      - Initialize state tracking"
        echo "  get [context]       - Get next unique number"
        echo "  release <num> [ctx] - Release a number back to pool"
        echo "  stats               - Show state statistics"
        echo "  contexts            - Show context assignments"
        echo "  gaps [context]      - Check for numbering gaps"
        echo "  sync <dir> [ctx]    - Sync state with actual files"
        echo "  validate <dir> [ctx] - Validate consistency"
        echo "  cleanup [days]      - Clean up old backups"
        exit 1
        ;;
esac