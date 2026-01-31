#!/bin/bash

# Task Status Detection Script - Core functionality for detecting and tracking cleanup task status
# Monitors repository cleanup operations and provides comprehensive status reporting
# Follows Auto-slopp patterns and integrates with existing infrastructure

# Set script name for logging identification
SCRIPT_NAME="task-status-detection"

# Load utilities and configuration first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# Set up error handling
setup_error_handling

log "INFO" "Starting task status detection script"

# Task status enumeration (following functional approach)
declare -A TASK_STATUS=(
    ["PENDING"]=0
    ["IN_PROGRESS"]=1
    ["COMPLETED"]=2
    ["FAILED"]=3
    ["BLOCKED"]=4
    ["SKIPPED"]=5
    ["TIMEOUT"]=6
    ["CANCELLED"]=7
)

# Task type enumeration
declare -A TASK_TYPES=(
    ["DISCOVERY"]="repository_discovery"
    ["BRANCH_CLEANUP"]="branch_cleanup"
    ["CONFLICT_RESOLUTION"]="conflict_resolution"
    ["MERGE"]="merge_operations"
    ["VALIDATION"]="validation"
    ["CLEANUP"]="general_cleanup"
    ["HEALTH_CHECK"]="health_check"
)

# Global arrays for status tracking
declare -A TASK_CACHE=()
declare -A STATUS_CACHE=()
declare -A LAST_CHECK_CACHE=()

# Pure function to get status code from status name
get_status_code() {
    local status_name="$1"
    echo "${TASK_STATUS[$status_name]:-0}"
}

# Pure function to get status name from status code
get_status_name() {
    local status_code="$1"
    for status in "${!TASK_STATUS[@]}"; do
        if [[ "${TASK_STATUS[$status]}" == "$status_code" ]]; then
            echo "$status"
            return 0
        fi
    done
    echo "PENDING"
}

# Pure function to get task type identifier
get_task_type_id() {
    local task_type="$1"
    echo "${TASK_TYPES[$task_type]:-general_cleanup}"
}

# Function to get status file path for a repository and task
get_status_file_path() {
    local repo_path="$1"
    local task_type="$2"
    local task_id="$3"
    local repo_name=$(basename "$repo_path")
    
    # Create task status directory if it doesn't exist
    local status_dir="${repo_path}/.cleanup-status"
    mkdir -p "$status_dir" 2>/dev/null || true
    
    echo "${status_dir}/${task_type}_${task_id}.status"
}

# Function to write task status atomically
write_task_status() {
    local repo_path="$1"
    local task_type="$2"
    local task_id="$3"
    local status="$4"
    local message="$5"
    local metadata="$6"
    
    local status_file
    status_file=$(get_status_file_path "$repo_path" "$task_type" "$task_id")
    local temp_file="${status_file}.tmp"
    
    local timestamp=$(date -Iseconds)
    local status_code
    status_code=$(get_status_code "$status")
    
    # Write to temporary file first (atomic operation)
    cat > "$temp_file" << EOF
{
    "task_id": "$task_id",
    "task_type": "$task_type",
    "status": "$status",
    "status_code": $status_code,
    "message": "$message",
    "timestamp": "$timestamp",
    "metadata": $metadata,
    "script_name": "$(basename "${BASH_SOURCE[0]}")",
    "hostname": "$(hostname 2>/dev/null || echo 'unknown')",
    "user": "${USER:-unknown}"
}
EOF
    
    # Atomic move
    mv "$temp_file" "$status_file" 2>/dev/null || {
        log "ERROR" "Failed to write status file: $status_file"
        rm -f "$temp_file" 2>/dev/null
        return 1
    }
    
    # Update cache
    local cache_key="${repo_path}:${task_type}:${task_id}"
    TASK_CACHE["$cache_key"]="$(cat "$status_file")"
    STATUS_CACHE["$cache_key"]="$status"
    LAST_CHECK_CACHE["$cache_key"]="$timestamp"
    
    log "DEBUG" "Task status written: $task_type/$task_id for $(basename "$repo_path") -> $status"
    return 0
}

# Function to read task status with caching
read_task_status() {
    local repo_path="$1"
    local task_type="$2"
    local task_id="$3"
    local cache_duration="${4:-300}"  # Default 5 minutes cache
    
    local cache_key="${repo_path}:${task_type}:${task_id}"
    local current_time=$(date +%s)
    local last_check="${LAST_CHECK_CACHE[$cache_key]:-0}"
    
    # Check cache validity
    if [[ $((current_time - last_check)) -lt $cache_duration && -n "${STATUS_CACHE[$cache_key]}" ]]; then
        echo "${TASK_CACHE[$cache_key]}"
        return 0
    fi
    
    local status_file
    status_file=$(get_status_file_path "$repo_path" "$task_type" "$task_id")
    
    if [[ ! -f "$status_file" ]]; then
        log "DEBUG" "Status file not found: $task_type/$task_id for $(basename "$repo_path")"
        return 1
    fi
    
    local status_content
    if ! status_content=$(cat "$status_file" 2>/dev/null); then
        log "WARNING" "Failed to read status file: $status_file"
        return 1
    fi
    
    # Update cache
    TASK_CACHE["$cache_key"]="$status_content"
    STATUS_CACHE["$cache_key"]="$(echo "$status_content" | jq -r '.status' 2>/dev/null || echo 'UNKNOWN')"
    LAST_CHECK_CACHE["$cache_key"]="$current_time"
    
    echo "$status_content"
    return 0
}

# Function to check if task is currently active (in progress or pending)
is_task_active() {
    local status_data="$1"
    
    if [[ -z "$status_data" ]]; then
        return 1
    fi
    
    local status
    status=$(echo "$status_data" | jq -r '.status' 2>/dev/null || echo "PENDING")
    local status_code
    status_code=$(get_status_code "$status")
    
    # Active if pending or in progress
    [[ $status_code -le 1 ]]
}

# Function to check if task completed successfully
is_task_completed() {
    local status_data="$1"
    
    if [[ -z "$status_data" ]]; then
        return 1
    fi
    
    local status
    status=$(echo "$status_data" | jq -r '.status' 2>/dev/null || echo "PENDING")
    [[ "$status" == "COMPLETED" ]]
}

# Function to check if task failed
is_task_failed() {
    local status_data="$1"
    
    if [[ -z "$status_data" ]]; then
        return 1
    fi
    
    local status
    status=$(echo "$status_data" | jq -r '.status' 2>/dev/null || echo "PENDING")
    [[ "$status" == "FAILED" ]] || [[ "$status" == "TIMEOUT" ]]
}

# Function to detect branch cleanup task status
detect_branch_cleanup_status() {
    local repo_path="$1"
    local repo_name=$(basename "$repo_path")
    
    log "DEBUG" "Detecting branch cleanup status for: $repo_name"
    
    cd "$repo_path" || return 1
    
    # Check for active cleanup operations
    local cleanup_pid_file="${repo_path}/.cleanup.pid"
    local status_file
    status_file=$(get_status_file_path "$repo_path" "branch_cleanup" "current")
    
    # Check for running process
    if [[ -f "$cleanup_pid_file" ]]; then
        local pid
        pid=$(cat "$cleanup_pid_file" 2>/dev/null)
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            write_task_status "$repo_path" "branch_cleanup" "current" "IN_PROGRESS" \
                "Branch cleanup process running (PID: $pid)" \
                '{"pid": "'$pid'", "detection_method": "process_check"}'
            echo "IN_PROGRESS"
            return 0
        else
            # Clean up stale PID file
            rm -f "$cleanup_pid_file"
        fi
    fi
    
    # Check git status for cleanup indicators
    local branch_count modified_files untracked_files
    
    branch_count=$(git branch --format='%(refname:short)' 2>/dev/null | wc -l)
    modified_files=$(git diff --name-only 2>/dev/null | wc -l)
    untracked_files=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l)
    
    # Determine status based on repository state
    if [[ $branch_count -gt 2 || $modified_files -gt 0 || $untracked_files -gt 0 ]]; then
        write_task_status "$repo_path" "branch_cleanup" "current" "PENDING" \
            "Repository requires cleanup (branches: $branch_count, modified: $modified_files, untracked: $untracked_files)" \
            '{"branch_count": '$branch_count', "modified_files": '$modified_files', "untracked_files": '$untracked_files', "detection_method": "git_analysis"}'
        echo "PENDING"
    else
        write_task_status "$repo_path" "branch_cleanup" "current" "COMPLETED" \
            "Repository is clean (branches: $branch_count, no modified/untracked files)" \
            '{"branch_count": '$branch_count', "detection_method": "git_analysis"}'
        echo "COMPLETED"
    fi
}

# Function to detect merge conflict resolution status
detect_merge_conflict_status() {
    local repo_path="$1"
    local repo_name=$(basename "$repo_path")
    
    log "DEBUG" "Detecting merge conflict status for: $repo_name"
    
    cd "$repo_path" || return 1
    
    # Check for merge conflicts
    local conflicted_files
    conflicted_files=$(git diff --name-only --diff-filter=U 2>/dev/null)
    local conflict_count=0
    
    if [[ -n "$conflicted_files" ]]; then
        conflict_count=$(echo "$conflicted_files" | wc -l)
    fi
    
    # Check if in merge state
    local merge_head
    merge_head=$(git rev-parse --MERGE_HEAD 2>/dev/null 2>/dev/null)
    local in_merge_state=$?
    
    if [[ $conflict_count -gt 0 || $in_merge_state -eq 0 ]]; then
        write_task_status "$repo_path" "conflict_resolution" "current" "FAILED" \
            "Merge conflicts detected ($conflict_count files)" \
            '{"conflict_count": '$conflict_count', "in_merge_state": '$in_merge_state', "conflicted_files": ['$(echo "$conflicted_files" | sed 's/"/\\"/g' | tr '\n' ',' | sed 's/,$//')']}'
        echo "FAILED"
    else
        write_task_status "$repo_path" "conflict_resolution" "current" "COMPLETED" \
            "No merge conflicts detected" \
            '{"detection_method": "git_analysis"}'
        echo "COMPLETED"
    fi
}

# Function to detect repository health status
detect_repository_health_status() {
    local repo_path="$1"
    local repo_name=$(basename "$repo_path")
    
    log "DEBUG" "Detecting repository health status for: $repo_name"
    
    cd "$repo_path" || return 1
    
    # Perform health checks
    local health_issues=()
    local health_metadata='{}'
    
    # Check git repository integrity
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        health_issues+=("git_repository_corrupt")
    fi
    
    # Check for lock files
    if [[ -f ".git/index.lock" ]] || [[ -f ".git/refs/heads/main.lock" ]]; then
        health_issues+=("git_lock_files")
    fi
    
    # Check disk space (basic)
    local available_space
    available_space=$(df . | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 1024 ]]; then  # Less than 1MB
        health_issues+=("low_disk_space")
    fi
    
    # Check network connectivity (optional)
    if git remote get-url origin >/dev/null 2>&1; then
        if ! git ls-remote origin >/dev/null 2>&1; then
            health_issues+=("network_connectivity")
        fi
    fi
    
    # Determine overall health
    if [[ ${#health_issues[@]} -eq 0 ]]; then
        write_task_status "$repo_path" "health_check" "current" "COMPLETED" \
            "Repository health is good" \
            '{"health_score": 100, "issues": [], "checks_performed": ["git_integrity", "lock_files", "disk_space", "network"]}'
        echo "COMPLETED"
    else
        local issues_json
        issues_json=$(printf '%s,' "${health_issues[@]}" | sed 's/,$//')
        health_metadata='{"health_score": '$((100 - ${#health_issues[@]} * 20))', "issues": ['$issues_json'], "checks_performed": ["git_integrity", "lock_files", "disk_space", "network"]}'
        
        write_task_status "$repo_path" "health_check" "current" "FAILED" \
            "Repository has ${#health_issues[@]} health issues: ${health_issues[*]}" \
            "$health_metadata"
        echo "FAILED"
    fi
}

# Function to detect overall cleanup task status for a repository
detect_repository_task_status() {
    local repo_path="$1"
    local repo_name=$(basename "$repo_path")
    
    log "INFO" "Detecting task status for repository: $repo_name"
    
    # Detect status for different task types
    local branch_status conflict_status health_status
    local overall_status="COMPLETED"
    local failed_tasks=()
    local pending_tasks=()
    local in_progress_tasks=()
    
    # Check each task type
    branch_status=$(detect_branch_cleanup_status "$repo_path")
    conflict_status=$(detect_merge_conflict_status "$repo_path")
    health_status=$(detect_repository_health_status "$repo_path")
    
    # Determine overall status
    if [[ "$branch_status" == "FAILED" || "$conflict_status" == "FAILED" || "$health_status" == "FAILED" ]]; then
        overall_status="FAILED"
        [[ "$branch_status" == "FAILED" ]] && failed_tasks+=("branch_cleanup")
        [[ "$conflict_status" == "FAILED" ]] && failed_tasks+=("conflict_resolution")
        [[ "$health_status" == "FAILED" ]] && failed_tasks+=("health_check")
    elif [[ "$branch_status" == "IN_PROGRESS" || "$conflict_status" == "IN_PROGRESS" || "$health_status" == "IN_PROGRESS" ]]; then
        overall_status="IN_PROGRESS"
        [[ "$branch_status" == "IN_PROGRESS" ]] && in_progress_tasks+=("branch_cleanup")
        [[ "$conflict_status" == "IN_PROGRESS" ]] && in_progress_tasks+=("conflict_resolution")
        [[ "$health_status" == "IN_PROGRESS" ]] && in_progress_tasks+=("health_check")
    elif [[ "$branch_status" == "PENDING" || "$conflict_status" == "PENDING" || "$health_status" == "PENDING" ]]; then
        overall_status="PENDING"
        [[ "$branch_status" == "PENDING" ]] && pending_tasks+=("branch_cleanup")
        [[ "$conflict_status" == "PENDING" ]] && pending_tasks+=("conflict_resolution")
        [[ "$health_status" == "PENDING" ]] && pending_tasks+=("health_check")
    fi
    
    # Write overall status
    local task_list_json
    task_list_json="[]"
    if [[ ${#failed_tasks[@]} -gt 0 || ${#pending_tasks[@]} -gt 0 || ${#in_progress_tasks[@]} -gt 0 ]]; then
        local all_tasks=("${failed_tasks[@]}" "${pending_tasks[@]}" "${in_progress_tasks[@]}")
        task_list_json=$(printf '"%s",' "${all_tasks[@]}" | sed 's/,$//')
        task_list_json="[$task_list_json]"
    fi
    
    local failed_json pending_json in_progress_json
    failed_json=$(printf '"%s",' "${failed_tasks[@]}" | sed 's/,$//')
    pending_json=$(printf '"%s",' "${pending_tasks[@]}" | sed 's/,$//')
    in_progress_json=$(printf '"%s",' "${in_progress_tasks[@]}" | sed 's/,$//')
    
    write_task_status "$repo_path" "overall" "current" "$overall_status" \
        "Overall repository status: $overall_status" \
        '{
            "task_types": '"$task_list_json"',
            "failed_tasks": ['"$failed_json"'],
            "pending_tasks": ['"$pending_json"'],
            "in_progress_tasks": ['"$in_progress_json"'],
            "branch_cleanup_status": "'"$branch_status"'",
            "conflict_resolution_status": "'"$conflict_status"'",
            "health_check_status": "'"$health_status"'",
            "detection_timestamp": "'$(date -Iseconds)'"
        }'
    
    log "INFO" "Repository '$repo_name' status: $overall_status"
    echo "$overall_status"
    return 0
}

# Function to get all task status files for a repository
get_repository_task_statuses() {
    local repo_path="$1"
    local repo_name=$(basename "$repo_path")
    
    local status_dir="${repo_path}/.cleanup-status"
    
    if [[ ! -d "$status_dir" ]]; then
        log "DEBUG" "No status directory found for repository: $repo_name"
        return 0
    fi
    
    log "DEBUG" "Reading task status files for repository: $repo_name"
    
    # Find all status files
    local status_files=()
    while IFS= read -r -d '' file; do
        status_files+=("$file")
    done < <(find "$status_dir" -name "*.status" -type f -print0 2>/dev/null)
    
    # Output combined status information
    printf '{\n'
    printf '  "repository": "%s",\n' "$repo_name"
    printf '  "repository_path": "%s",\n' "$repo_path"
    printf '  "scan_timestamp": "%s",\n' "$(date -Iseconds)"
    printf '  "total_status_files": %d,\n' "${#status_files[@]}"
    printf '  "tasks": [\n'
    
    local file_count=${#status_files[@]}
    for ((i=0; i<file_count; i++)); do
        local status_file="${status_files[$i]}"
        local file_content
        file_content=$(cat "$status_file" 2>/dev/null || echo '{}')
        
        # Add comma between entries (except last)
        if [[ $i -gt 0 ]]; then
            printf ',\n'
        fi
        
        printf '    %s' "$file_content"
    done
    
    printf '\n'
    printf '  ]\n'
    printf '}\n'
}

# Function to generate comprehensive status report for all repositories
generate_status_report() {
    local repositories=("$@")
    local report_file="${MANAGED_REPO_PATH}/.task-status-report-$(date +%Y%m%d_%H%M%S).json"
    
    log "INFO" "Generating comprehensive status report: $report_file"
    
    printf '{\n' > "$report_file"
    printf '  "report_timestamp": "%s",\n' "$(date -Iseconds)"
    printf '  "managed_repo_path": "%s",\n' "$MANAGED_REPO_PATH"
    printf '  "repositories_processed": %d,\n' "${#repositories[@]}"
    printf '  "script_version": "1.0.0",\n'
    printf '  "repositories": [\n' >> "$report_file"
    
    local repo_count=${#repositories[@]}
    for ((i=0; i<repo_count; i++)); do
        local repo_path="${repositories[$i]}"
        
        # Add comma between entries (except last)
        if [[ $i -gt 0 ]]; then
            printf ',\n' >> "$report_file"
        fi
        
        # Get repository status
        detect_repository_task_status "$repo_path" >/dev/null
        get_repository_task_statuses "$repo_path" >> "$report_file"
    done
    
    printf '\n' >> "$report_file"
    printf '  ],\n' >> "$report_file"
    
    # Add summary statistics
    printf '  "summary": {\n' >> "$report_file"
    
    # Count different statuses (simplified for now)
    printf '    "status_distribution": {\n' >> "$report_file"
    printf '      "completed": 0,\n' >> "$report_file"
    printf '      "failed": 0,\n' >> "$report_file"
    printf '      "pending": 0,\n' >> "$report_file"
    printf '      "in_progress": 0\n' >> "$report_file"
    printf '    }\n' >> "$report_file"
    
    printf '  }\n' >> "$report_file"
    printf '}\n' >> "$report_file"
    
    log "SUCCESS" "Status report generated: $report_file"
    echo "$report_file"
}

# Main execution function
main() {
    log "INFO" "Task status detection started"
    
    # Validate required environment variables
    validate_env_vars MANAGED_REPO_PATH
    
    # Check if managed_repo_path exists and is accessible
    check_directory "$MANAGED_REPO_PATH" "managed_repo_path"
    
    # Get repositories to check (can be passed as arguments or use discovery)
    local repositories=("$@")
    
    if [[ ${#repositories[@]} -eq 0 ]]; then
        log "INFO" "No repositories specified, using repository discovery"
        
        # Run repository discovery and capture output
        local discovery_output
        if ! discovery_output=$("$SCRIPT_DIR/repository-discovery.sh" 2>/dev/null); then
            log "ERROR" "Repository discovery failed"
            return 1
        fi
        
        # Read discovered repositories into array
        local discovered_repos=()
        while IFS= read -r repo_path; do
            if [[ -n "$repo_path" ]]; then
                discovered_repos+=("$repo_path")
            fi
        done <<< "$discovery_output"
        
        repositories=("${discovered_repos[@]}")
    fi
    
    if [[ ${#repositories[@]} -eq 0 ]]; then
        log "WARNING" "No repositories found for status detection"
        return 1
    fi
    
    log "INFO" "Processing ${#repositories[@]} repositories for task status detection"
    
    # Process each repository
    local processed_count=0
    local success_count=0
    local error_count=0
    
    for repo_path in "${repositories[@]}"; do
        if [[ ! -d "$repo_path" ]]; then
            log "WARNING" "Repository path does not exist: $repo_path"
            ((error_count++))
            continue
        fi
        
        # Always count as success if the function runs (FAILED status is valid)
        local status_result
        status_result=$(detect_repository_task_status "$repo_path")
        success_count=$((success_count + 1))
        
        processed_count=$((processed_count + 1))
    done
    
    # Generate comprehensive report
    local report_file
    report_file=$(generate_status_report "${repositories[@]}")
    
    # Log summary
    log "INFO" "Task status detection completed"
    log "INFO" "Repositories processed: $processed_count"
    log "INFO" "Successful detections: $success_count"
    log "INFO" "Errors encountered: $error_count"
    log "INFO" "Status report: $report_file"
    
    return $((error_count > 0 ? 1 : 0))
}

# Execute main function if script is run directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi