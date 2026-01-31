#!/bin/bash

# Cleanup Automation Engine - Core automation engine for repository cleanup operations
# Orchestrates discovery, task status detection, and cleanup workflows
# Provides scheduling, coordination, and comprehensive reporting
# Follows Auto-slopp patterns and integrates with existing infrastructure

# Set script name for logging identification
SCRIPT_NAME="cleanup-automation-engine"

# Load utilities and configuration first
CLEANUP_ENGINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$CLEANUP_ENGINE_DIR/utils.sh"
source "$CLEANUP_ENGINE_DIR/../config.sh"

# Set up error handling
setup_error_handling

log "INFO" "Starting cleanup automation engine"

# Load component modules (functions only, without execution)
# We'll load utilities and then source specific functions as needed

# Task state enumeration
declare -A TASK_STATES=(
    ["INITIALIZED"]=0
    ["DISCOVERING"]=1
    ["ANALYZING"]=2
    ["CLEANING"]=3
    ["VALIDATING"]=4
    ["COMPLETED"]=5
    ["FAILED"]=6
    ["CANCELLED"]=7
)

# Cleanup operation types
declare -A CLEANUP_TYPES=(
    ["BRANCH"]="branch_cleanup"
    ["CONFLICT"]="conflict_resolution"
    ["MERGE"]="merge_operations"
    ["HEALTH"]="health_check"
    ["FULL"]="full_cleanup"
)

# Global engine state
declare -A ENGINE_STATE=()
declare -a ACTIVE_TASKS=()
declare -A TASK_RESULTS=()
declare -a OPERATION_QUEUE=()

# Initialize engine state
initialize_engine() {
    log "INFO" "Initializing cleanup automation engine"
    
    # Initialize engine state variables
    ENGINE_STATE["start_time"]=$(date +%s)
    ENGINE_STATE["current_phase"]="INITIALIZED"
    ENGINE_STATE["repositories_processed"]=0
    ENGINE_STATE["operations_completed"]=0
    ENGINE_STATE["errors_encountered"]=0
    ENGINE_STATE["last_activity"]=$(date +%s)
    
    # Validate required environment
    validate_env_vars MANAGED_REPO_PATH
    
    # Check managed repository path
    check_directory "$MANAGED_REPO_PATH" "managed_repo_path"
    
    # Initialize component subsystems
    log "INFO" "Initializing repository discovery subsystem"
    # Repository discovery is available via discover_all_repositories()
    
    log "INFO" "Initializing task status detection subsystem"
    # Status detection is available via generate_status_report()
    
    log "INFO" "Cleanup automation engine initialized successfully"
}

# Create cleanup operation queue
create_operation_queue() {
    local operation_type="$1"
    local target_repos=("${@:2}")
    
    log "INFO" "Creating operation queue for type: $operation_type"
    
    # Clear existing queue
    OPERATION_QUEUE=()
    
    # If no target repos specified, discover all repositories
    if [ ${#target_repos[@]} -eq 0 ]; then
        log "INFO" "No target repositories specified, discovering all repositories"
        # Get the repositories from managed_repo_path
        for repo_dir in "$MANAGED_REPO_PATH"/*; do
            if [ -d "$repo_dir" ] && [ -d "$repo_dir/.git" ]; then
                target_repos+=("$repo_dir")
            fi
        done
    fi
    
    # Create operations for each repository
    for repo in "${target_repos[@]}"; do
        local operation_id="cleanup_$(date +%s)_$(basename "$repo")"
        local operation_entry="$operation_id:$operation_type:$repo"
        OPERATION_QUEUE+=("$operation_entry")
        log "DEBUG" "Queued operation: $operation_entry"
    done
    
    log "INFO" "Created ${#OPERATION_QUEUE[@]} operations in queue"
}

# Process single operation
process_operation() {
    local operation_entry="$1"
    local operation_id operation_type repo_dir
    IFS=':' read -r operation_id operation_type repo_dir <<< "$operation_entry"
    
    log "INFO" "Processing operation: $operation_id ($operation_type on $(basename "$repo_dir"))"
    
    local start_time=$(date +%s)
    local operation_result="FAILED"
    local error_message=""
    
    # Update engine state
    ENGINE_STATE["current_operation"]="$operation_id"
    ENGINE_STATE["last_activity"]=$(date +%s)
    
    # Add to active tasks
    ACTIVE_TASKS+=("$operation_id")
    # Task status tracking is handled via TASK_RESULTS array
    
    # Process operation based on type
    case "$operation_type" in
        "BRANCH")
            if perform_branch_cleanup "$repo_dir"; then
                operation_result="COMPLETED"
            else
                error_message="Branch cleanup failed"
            fi
            ;;
        "HEALTH")
            if validate_repository_health "$repo_dir"; then
                operation_result="COMPLETED"
            else
                error_message="Health check failed"
            fi
            ;;
        "FULL")
            if perform_full_cleanup "$repo_dir"; then
                operation_result="COMPLETED"
            else
                error_message="Full cleanup failed"
            fi
            ;;
        *)
            log "ERROR" "Unknown operation type: $operation_type"
            error_message="Unknown operation type: $operation_type"
            ;;
    esac
    
    # Calculate operation duration
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Store operation result
    TASK_RESULTS["$operation_id"]="$operation_result:$duration:$error_message"
    # Task status tracking is handled via TASK_RESULTS array
    
    # Remove from active tasks
    ACTIVE_TASKS=("${ACTIVE_TASKS[@]/$operation_id}")
    
    # Update engine statistics
    ENGINE_STATE["operations_completed"]=$((${ENGINE_STATE["operations_completed"]} + 1))
    if [[ "$operation_result" == "FAILED" ]]; then
        ENGINE_STATE["errors_encountered"]=$((${ENGINE_STATE["errors_encountered"]} + 1))
    fi
    
    log "INFO" "Operation $operation_id completed with result: $operation_result (duration: ${duration}s)"
}

# Validate repository health
validate_repository_health() {
    local repo_dir="$1"
    local repo_name=$(basename "$repo_dir")
    
    log "INFO" "Validating health of repository: $repo_name"
    
    # Check if it's a valid git repository
    if [ ! -d "$repo_dir/.git" ]; then
        log "ERROR" "Repository $repo_name is not a valid git repository"
        return 1
    fi
    
    # Check repository status
    cd "$repo_dir" || return 1
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log "WARNING" "Repository $repo_name has uncommitted changes"
    fi
    
    # Check remote connectivity
    if ! git ls-remote origin >/dev/null 2>&1; then
        log "WARNING" "Repository $repo_name cannot reach remote 'origin'"
    fi
    
    # Check for merge conflicts
    if [ -f "$repo_dir/.git/MERGE_HEAD" ]; then
        log "WARNING" "Repository $repo_name has unresolved merge conflicts"
        return 1
    fi
    
    log "SUCCESS" "Repository $repo_name health validation completed"
    return 0
}

# Perform branch cleanup operation
perform_branch_cleanup() {
    local repo_dir="$1"
    local repo_name=$(basename "$repo_dir")
    
    log "INFO" "Performing branch cleanup on repository: $repo_name"
    
    # Check if it's a valid git repository
    if [ ! -d "$repo_dir/.git" ]; then
        log "ERROR" "Repository $repo_name is not a valid git repository"
        return 1
    fi
    
    cd "$repo_dir" || return 1
    
    # Get current branch (cannot be deleted)
    local current_branch
    if ! current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null); then
        log "ERROR" "Failed to determine current branch for $repo_name"
        return 1
    fi
    
    log "DEBUG" "Current branch in $repo_name: $current_branch"
    
    # Get remote and local branch lists
    local remote_branches local_branches
    if ! remote_branches=$(git ls-remote --heads origin 2>/dev/null | sed 's/.*\///' | sort); then
        log "ERROR" "Failed to list remote branches for $repo_name"
        return 1
    fi
    
    if ! local_branches=$(git branch --format='%(refname:short)' 2>/dev/null | grep -v '^*' | sort); then
        log "ERROR" "Failed to list local branches for $repo_name"
        return 1
    fi
    
    # Convert remote branches to array for efficient lookup
    local -A remote_branch_map
    while IFS= read -r branch; do
        [[ -n "$branch" ]] && remote_branch_map["$branch"]=1
    done <<< "$remote_branches"
    
    # Find branches to delete (local but not on remote)
    local branches_to_delete=()
    local branches_skipped=()
    
    while IFS= read -r local_branch; do
        [[ -n "$local_branch" ]] || continue
        
        # Check if branch exists on remote
        if [[ -z "${remote_branch_map[$local_branch]:-}" ]]; then
            # Branch doesn't exist on remote
            if is_protected_branch "$local_branch" "$current_branch"; then
                branches_skipped+=("$local_branch (protected)")
                log "DEBUG" "Skipping protected branch: $local_branch"
            else
                branches_to_delete+=("$local_branch")
                log "DEBUG" "Marked for deletion: $local_branch"
            fi
        else
            log "DEBUG" "Branch exists on remote: $local_branch"
        fi
    done <<< "$local_branches"
    
    # Report findings
    local branches_to_delete_count=${#branches_to_delete[@]}
    local branches_skipped_count=${#branches_skipped[@]}
    
    log "INFO" "Found $branches_to_delete_count branches to delete, $branches_skipped_count branches skipped in $repo_name"
    
    # Show branches that will be skipped
    if [[ $branches_skipped_count -gt 0 ]]; then
        log "INFO" "Skipped protected branches: ${branches_skipped[*]}"
    fi
    
    # Delete branches
    local repo_cleaned_count=0
    for branch in "${branches_to_delete[@]}"; do
        if safe_delete_branch "$branch" "$repo_dir"; then
            repo_cleaned_count=$((repo_cleaned_count + 1))
        else
            return 1
        fi
    done
    
    if [[ $repo_cleaned_count -gt 0 ]]; then
        log "SUCCESS" "Cleaned up $repo_cleaned_count branches in $repo_name"
    else
        log "INFO" "No branches needed cleanup in $repo_name"
    fi
    
    return 0
}

# Check if branch is protected
is_protected_branch() {
    local branch="$1"
    local current_branch="$2"
    
    # Define protected branches (can be made configurable later)
    local protected_branches=("main" "master" "develop" "HEAD")
    
    # Never delete current branch
    if [[ "$branch" == "$current_branch" ]]; then
        return 0  # Protected (current branch)
    fi
    
    # Check against protected branch names
    for protected in "${protected_branches[@]}"; do
        if [[ "$branch" == "$protected" ]]; then
            return 0  # Protected
        fi
    done
    
    return 1  # Not protected
}

# Safely delete a local branch
safe_delete_branch() {
    local branch="$1"
    local repo_dir="$2"
    
    cd "$repo_dir" || return 1
    
    log "INFO" "Deleting local branch: $branch"
    
    if git branch -d "$branch" 2>/dev/null; then
        log "SUCCESS" "Successfully deleted branch: $branch"
        return 0
    else
        # Try force delete if regular delete fails
        log "WARNING" "Regular delete failed for $branch, trying force delete..."
        if git branch -D "$branch" 2>/dev/null; then
            log "SUCCESS" "Successfully force deleted branch: $branch"
            return 0
        else
            log "ERROR" "Failed to delete branch: $branch"
            return 1
        fi
    fi
}

# Perform full cleanup (comprehensive cleanup operations)
perform_full_cleanup() {
    local repo_dir="$1"
    local repo_name=$(basename "$repo_dir")
    
    log "INFO" "Performing full cleanup on repository: $repo_name"
    
    # Step 1: Health validation
    if ! validate_repository_health "$repo_dir"; then
        log "ERROR" "Health validation failed for $repo_name, cannot proceed with full cleanup"
        return 1
    fi
    
    # Step 2: Branch cleanup
    if ! perform_branch_cleanup "$repo_dir"; then
        log "WARNING" "Branch cleanup encountered issues for $repo_name"
    fi
    
    # Step 3: Git cleanup (gc, prune)
    cd "$repo_dir" || return 1
    log "INFO" "Running git garbage collection on $repo_name"
    if safe_git "gc --prune=now --aggressive"; then
        log "SUCCESS" "Git garbage collection completed for $repo_name"
    else
        log "WARNING" "Git garbage collection failed for $repo_name"
    fi
    
    log "SUCCESS" "Full cleanup completed for repository: $repo_name"
    return 0
}

# Process all operations in queue
process_operation_queue() {
    local total_operations=${#OPERATION_QUEUE[@]}
    local operations_completed=0
    
    log "INFO" "Processing $total_operations operations in queue"
    
    # Update engine state
    ENGINE_STATE["current_phase"]="PROCESSING"
    ENGINE_STATE["queue_size"]=$total_operations
    
    for operation in "${OPERATION_QUEUE[@]}"; do
        local operation_id operation_type repo_dir
        IFS=':' read -r operation_id operation_type repo_dir <<< "$operation"
        
        log "INFO" "Starting operation $((operations_completed + 1))/$total_operations: $operation_id"
        
        # Update engine state
        ENGINE_STATE["current_operation"]="$operation_id"
        ENGINE_STATE["repositories_processed"]=$((operations_completed + 1))
        
        # Process the operation
        process_operation "$operation"
        operations_completed=$((operations_completed + 1))
        
        # Update progress
        local progress=$((operations_completed * 100 / total_operations))
        log "INFO" "Progress: $progress% ($operations_completed/$total_operations operations completed)"
    done
    
    # Clear queue
    OPERATION_QUEUE=()
    
    log "INFO" "Operation queue processing completed ($operations_completed operations processed)"
}

# Generate comprehensive engine report
generate_engine_report() {
    local report_file="$1"
    
    log "INFO" "Generating cleanup automation engine report"
    
    {
        echo "# Cleanup Automation Engine Report"
        echo "Generated on: $(date)"
        echo ""
        echo "## Engine Summary"
        echo "- Start Time: $(date -d @${ENGINE_STATE["start_time"]})"
        echo "- Current Phase: ${ENGINE_STATE["current_phase"]}"
        echo "- Repositories Processed: ${ENGINE_STATE["repositories_processed"]}"
        echo "- Operations Completed: ${ENGINE_STATE["operations_completed"]}"
        echo "- Errors Encountered: ${ENGINE_STATE["errors_encountered"]}"
        echo "- Last Activity: $(date -d @${ENGINE_STATE["last_activity"]})"
        echo ""
        
        if [ ${#ACTIVE_TASKS[@]} -gt 0 ]; then
            echo "## Active Tasks"
            for task in "${ACTIVE_TASKS[@]}"; do
                echo "- $task"
            done
            echo ""
        fi
        
        if [ ${#TASK_RESULTS[@]} -gt 0 ]; then
            echo "## Operation Results"
            echo "| Operation ID | Result | Duration (s) | Error Message |"
            echo "|--------------|--------|-------------|---------------|"
            for operation_id in "${!TASK_RESULTS[@]}"; do
                local result_info="${TASK_RESULTS[$operation_id]}"
                local result duration error
                IFS=':' read -r result duration error <<< "$result_info"
                echo "| $operation_id | $result | $duration | ${error:-N/A} |"
            done
            echo ""
        fi
        
        echo "## Repository Discovery Summary"
        echo "- Discovered Repositories: ${#DISCOVERED_REPOS[@]}"
        echo "- Skipped Repositories: ${#SKIPPED_REPOS[@]}"
        echo "- Error Repositories: ${#ERROR_REPOS[@]}"
        
        if [ ${#DISCOVERED_REPOS[@]} -gt 0 ]; then
            echo ""
            echo "### Discovered Repositories:"
            for repo in "${DISCOVERED_REPOS[@]}"; do
                echo "- $(basename "$repo")"
            done
        fi
        
        if [ ${#SKIPPED_REPOS[@]} -gt 0 ]; then
            echo ""
            echo "### Skipped Repositories:"
            for repo in "${SKIPPED_REPOS[@]}"; do
                echo "- $(basename "$repo")"
            done
        fi
        
        if [ ${#ERROR_REPOS[@]} -gt 0 ]; then
            echo ""
            echo "### Error Repositories:"
            for repo in "${ERROR_REPOS[@]}"; do
                echo "- $(basename "$repo")"
            done
        fi
        
    } > "$report_file"
    
    log "SUCCESS" "Engine report generated: $report_file"
}

# Engine main execution function
run_cleanup_engine() {
    local operation_type="${1:-BRANCH}"
    local target_repos=("${@:2}")
    local report_file="$LOG_DIRECTORY/cleanup_engine_report_$(date +%Y%m%d_%H%M%S).md"
    
    log "INFO" "Running cleanup automation engine with operation type: $operation_type"
    
    # Initialize engine
    initialize_engine
    
    # Create operation queue
    create_operation_queue "$operation_type" "${target_repos[@]}"
    
    # Process all operations
    if [ ${#OPERATION_QUEUE[@]} -gt 0 ]; then
        process_operation_queue
    else
        log "WARNING" "No operations to process"
    fi
    
    # Generate final report
    ENGINE_STATE["current_phase"]="COMPLETED"
    generate_engine_report "$report_file"
    
    # Final summary
    local total_operations=${ENGINE_STATE["operations_completed"]}
    local total_errors=${ENGINE_STATE["errors_encountered"]}
    
    log "INFO" "Cleanup automation engine completed"
    log "INFO" "Total operations: $total_operations"
    log "INFO" "Total errors: $total_errors"
    log "INFO" "Report generated: $report_file"
    
    if [[ $total_errors -gt 0 ]]; then
        log "WARNING" "Engine completed with $total_errors errors"
        return 1
    else
        log "SUCCESS" "Engine completed successfully"
        return 0
    fi
}

# Function to schedule periodic cleanup runs
schedule_periodic_cleanup() {
    local interval_minutes="${1:-60}"
    local operation_type="${2:-BRANCH}"
    
    log "INFO" "Scheduling periodic cleanup every $interval_minutes minutes with operation type: $operation_type"
    
    while true; do
        log "INFO" "Starting scheduled cleanup run"
        
        if run_cleanup_engine "$operation_type"; then
            log "SUCCESS" "Scheduled cleanup completed successfully"
        else
            log "WARNING" "Scheduled cleanup completed with errors"
        fi
        
        log "INFO" "Next scheduled cleanup in $interval_minutes minutes"
        sleep $((interval_minutes * 60))
    done
}

# Main execution logic
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Parse command line arguments
    case "${1:-run}" in
        "run")
            run_cleanup_engine "${@:2}"
            ;;
        "schedule")
            schedule_periodic_cleanup "${2:-60}" "${3:-BRANCH}"
            ;;
        "health")
            for repo_dir in "$MANAGED_REPO_PATH"/*; do
                if [ -d "$repo_dir" ]; then
                    validate_repository_health "$repo_dir"
                fi
            done
            ;;
        "full")
            run_cleanup_engine "FULL" "${@:2}"
            ;;
        *)
            echo "Usage: $0 {run|schedule|health|full} [options]"
            echo "  run [operation_type] [repos...]  - Run cleanup engine (default: BRANCH)"
            echo "  schedule [minutes] [operation_type] - Schedule periodic cleanup"
            echo "  health                         - Run health checks on all repositories"
            echo "  full [repos...]                - Run full cleanup on repositories"
            exit 1
            ;;
    esac
fi