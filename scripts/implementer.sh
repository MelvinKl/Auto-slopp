#!/bin/bash

# implementer.sh - Implements the next ready bead task in each repository
# Switches to ai branch and uses OpenCode CLI to implement tasks

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Function to get list of repositories
get_repositories() {
    local repos_file="$AUTOMATION_ROOT/repos.txt"
    
    if [ ! -f "$repos_file" ]; then
        log_error "Repository list file not found: $repos_file"
        return 1
    fi
    
    # Read and expand repository paths
    local repos=()
    while IFS= read -r line; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        
        # Expand variables like $HOME
        local expanded_path=$(eval echo "$line")
        
        if [ -d "$expanded_path" ]; then
            repos+=("$expanded_path")
        else
            log_warn "Repository directory not found: $expanded_path"
        fi
    done < "$repos_file"
    
    echo "${repos[@]}"
}

# Function to get repository name from path
get_repo_name() {
    local repo_path="$1"
    
    # Extract the last directory name from the path
    local repo_name=$(basename "$repo_path")
    
    # Sanitize the name (remove special characters, replace spaces)
    repo_name=$(echo "$repo_name" | sed 's/[^a-zA-Z0-9._-]/_/g')
    
    echo "$repo_name"
}

# Function to switch repository to ai branch
switch_to_ai_branch() {
    local repo_path="$1"
    
    cd "$repo_path" || return 1
    
    log_info "Switching repository to ai branch: $repo_path"
    
    # Fetch latest changes
    if ! git fetch --all; then
        log_error "Failed to fetch changes for $repo_path"
        return 1
    fi
    
    # Check if ai branch exists
    if ! git rev-parse --verify origin/ai >/dev/null 2>&1; then
        log_info "ai branch does not exist in $repo_path, creating it"
        
        # Create ai branch from main
        if ! git checkout -b ai origin/main; then
            log_error "Failed to create ai branch in $repo_path"
            return 1
        fi
        
        # Push the new branch
        if ! git push -u origin ai; then
            log_error "Failed to push ai branch in $repo_path"
            return 1
        fi
    else
        # Switch to existing ai branch
        if ! git checkout ai; then
            log_error "Failed to switch to ai branch in $repo_path"
            return 1
        fi
        
        # Reset to remote ai branch
        if ! git reset --hard origin/ai; then
            log_error "Failed to reset ai branch in $repo_path"
            return 1
        fi
    fi
    
    log_info "Successfully switched to ai branch in $repo_path"
    return 0
}

# Function to get next ready bead task
get_next_ready_task() {
    local repo_path="$1"
    
    cd "$repo_path" || return 1
    
    log_info "Getting next ready bead task in: $repo_path"
    
    # Check if Beads CLI is available
    if ! command_exists "$BEADS_CLI"; then
        log_error "Beads CLI not found: $BEADS_CLI"
        return 1
    fi
    
    # Get ready tasks
    local ready_tasks=$("$BEADS_CLI" ready --json 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        log_error "Failed to get ready tasks from beads in: $repo_path"
        return 1
    fi
    
    # Parse JSON and extract task IDs
    local task_ids=$(echo "$ready_tasks" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -n "$task_ids" ]; then
        echo "$task_ids"
        return 0
    else
        log_info "No ready tasks found in: $repo_path"
        return 1
    fi
}

# Function to get task details
get_task_details() {
    local repo_path="$1"
    local task_id="$2"
    
    cd "$repo_path" || return 1
    
    log_info "Getting details for task: $task_id"
    
    # Get task details
    local task_details=$("$BEADS_CLI" show "$task_id" --json 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        log_error "Failed to get task details for: $task_id"
        return 1
    fi
    
    echo "$task_details"
}

# Function to extract task title and description
extract_task_info() {
    local task_details="$1"
    
    # Extract title
    local title=$(echo "$task_details" | grep -o '"title":"[^"]*"' | cut -d'"' -f4)
    
    # Extract description
    local description=$(echo "$task_details" | grep -o '"description":"[^"]*"' | cut -d'"' -f4)
    
    # Combine title and description
    if [ -n "$title" ] && [ -n "$description" ]; then
        echo "$title: $description"
    elif [ -n "$title" ]; then
        echo "$title"
    else
        echo "Implement bead task"
    fi
}

# Function to implement task using OpenCode CLI
implement_task() {
    local repo_path="$1"
    local task_id="$2"
    local task_info="$3"
    
    cd "$repo_path" || return 1
    
    log_info "Implementing task $task_id: $task_info"
    
    # Check if OpenCode CLI is available
    if ! command_exists "$OPencode_CLI"; then
        log_error "OpenCode CLI not found: $OPencode_CLI"
        return 1
    fi
    
    # Construct the instruction for OpenCode CLI
    local instruction="Implement the next bd task that is ready. Task ID: $task_id. Task description: $task_info. Please implement this task, commit the changes, and push to the current branch."
    
    log_info "Running OpenCode CLI to implement task"
    log_debug "Instruction: $instruction"
    
    # Run OpenCode CLI with the instruction
    if "$OPencode_CLI" "$instruction"; then
        log_info "OpenCode CLI completed successfully for task: $task_id"
        return 0
    else
        log_error "OpenCode CLI failed for task: $task_id"
        return 1
    fi
}

# Function to mark task as in progress
mark_task_in_progress() {
    local repo_path="$1"
    local task_id="$2"
    
    cd "$repo_path" || return 1
    
    log_info "Marking task as in progress: $task_id"
    
    if "$BEADS_CLI" update "$task_id" --status in_progress --json >/dev/null 2>&1; then
        log_info "Successfully marked task as in progress: $task_id"
        return 0
    else
        log_warn "Failed to mark task as in progress: $task_id"
        return 1
    fi
}

# Function to close task
close_task() {
    local repo_path="$1"
    local task_id="$2"
    
    cd "$repo_path" || return 1
    
    log_info "Closing task: $task_id"
    
    if "$BEADS_CLI" close "$task_id" --reason "Implemented by automation system" --json >/dev/null 2>&1; then
        log_info "Successfully closed task: $task_id"
        return 0
    else
        log_warn "Failed to close task: $task_id"
        return 1
    fi
}

# Function to push changes
push_changes() {
    local repo_path="$1"
    
    cd "$repo_path" || return 1
    
    log_info "Pushing changes in: $repo_path"
    
    # Check if there are any changes to push
    if git diff --quiet && git diff --cached --quiet; then
        log_info "No changes to push in: $repo_path"
        return 0
    fi
    
    # Push changes
    if git push; then
        log_info "Successfully pushed changes in: $repo_path"
        return 0
    else
        log_error "Failed to push changes in: $repo_path"
        return 1
    fi
}

# Function to process a single repository
process_repository() {
    local repo_path="$1"
    local repo_name=$(get_repo_name "$repo_path")
    
    if [ ! -d "$repo_path" ]; then
        log_error "Repository not found: $repo_path"
        return 1
    fi
    
    log_info "Processing repository: $repo_name"
    
    # Switch to ai branch
    if ! switch_to_ai_branch "$repo_path"; then
        return 1
    fi
    
    # Get next ready task
    local task_id=$(get_next_ready_task "$repo_path")
    if [ $? -ne 0 ] || [ -z "$task_id" ]; then
        log_info "No ready tasks in: $repo_name"
        return 0
    fi
    
    log_info "Found ready task: $task_id in: $repo_name"
    
    # Get task details
    local task_details=$(get_task_details "$repo_path" "$task_id")
    if [ $? -ne 0 ]; then
        return 1
    fi
    
    # Extract task info
    local task_info=$(extract_task_info "$task_details")
    
    # Mark task as in progress
    mark_task_in_progress "$repo_path" "$task_id"
    
    # Implement the task
    if implement_task "$repo_path" "$task_id" "$task_info"; then
        # Push changes
        push_changes "$repo_path"
        
        # Close the task
        close_task "$repo_path" "$task_id"
        
        log_info "Successfully implemented and closed task: $task_id in: $repo_name"
        return 0
    else
        log_error "Failed to implement task: $task_id in: $repo_name"
        
        # Reset task status (let it be tried again later)
        "$BEADS_CLI" update "$task_id" --status ready --json >/dev/null 2>&1 || true
        
        return 1
    fi
}

# Function to process all repositories
process_all_repositories() {
    log_info "Starting to implement next ready task in all repositories"
    
    local repositories=($(get_repositories))
    
    if [ ${#repositories[@]} -eq 0 ]; then
        log_warn "No repositories found to process"
        return 0
    fi
    
    log_info "Found ${#repositories[@]} repositories to process"
    
    local processed_repos=()
    local failed_repos=()
    local tasks_implemented=0
    
    for repo in "${repositories[@]}"; do
        local repo_name=$(get_repo_name "$repo")
        
        log_info "Processing repository: $repo_name"
        
        if process_repository "$repo"; then
            processed_repos+=("$repo_name")
            tasks_implemented=$((tasks_implemented + 1))
        else
            failed_repos+=("$repo_name")
        fi
    done
    
    # Log summary
    log_info "Implementer completed. Processed: ${#processed_repos[@]}, Failed: ${#failed_repos[@]}, Tasks implemented: $tasks_implemented"
    
    if [ ${#processed_repos[@]} -gt 0 ]; then
        log_info "Processed repositories: ${processed_repos[*]}"
    fi
    
    if [ ${#failed_repos[@]} -gt 0 ]; then
        log_error "Failed repositories: ${failed_repos[*]}"
        return 1
    fi
    
    return 0
}

# Main execution function
main() {
    init_common
    
    # Validate dependencies
    validate_dependencies "git" || exit 1
    
    # Process all repositories
    process_all_repositories
}

# Run main function if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi