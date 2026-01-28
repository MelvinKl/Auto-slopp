#!/bin/bash

# planner.sh - Processes task files and generates bead tasks using OpenCode CLI
# Checks repositories, processes files, and creates bead tasks

# Load common functions and file numbering system
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
source "$SCRIPT_DIR/file_numbering.sh"

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

# Function to check if repository directory exists in automation repo
check_repo_directory_exists() {
    local repo_path="$1"
    local repo_name=$(get_repo_name "$repo_path")
    local repo_dir="$AUTOMATION_ROOT/$repo_name"
    
    if [ -d "$repo_dir" ]; then
        return 0
    else
        return 1
    fi
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

# Function to get file content
get_file_content() {
    local file_path="$1"
    
    if [ ! -f "$file_path" ]; then
        log_error "File not found: $file_path"
        return 1
    fi
    
    cat "$file_path"
}

# Function to generate bead tasks using OpenCode CLI
generate_bead_tasks() {
    local repo_path="$1"
    local file_content="$2"
    local repo_name=$(get_repo_name "$repo_path")
    
    cd "$repo_path" || return 1
    
    log_info "Generating bead tasks for repository: $repo_name"
    
    # Check if OpenCode CLI is available
    if ! command_exists "$OPencode_CLI"; then
        log_error "OpenCode CLI not found: $OPencode_CLI"
        return 1
    fi
    
    # Check if Beads CLI is available
    if ! command_exists "$BEADS_CLI"; then
        log_error "Beads CLI not found: $BEADS_CLI"
        return 1
    fi
    
    # Construct the instruction for OpenCode CLI
    local instruction="Generate bead tasks for the following request: $file_content"
    
    log_info "Running OpenCode CLI to generate bead tasks"
    log_debug "Instruction: $instruction"
    
    # Run OpenCode CLI with the instruction
    if "$OPencode_CLI" "$instruction"; then
        log_info "OpenCode CLI completed successfully for: $repo_name"
        return 0
    else
        log_error "OpenCode CLI failed for: $repo_name"
        return 1
    fi
}

# Function to commit and push changes
commit_and_push_changes() {
    local repo_path="$1"
    local repo_name=$(get_repo_name "$repo_path")
    
    cd "$repo_path" || return 1
    
    log_info "Committing and pushing changes for: $repo_name"
    
    # Check if there are any changes to commit
    if git diff --quiet && git diff --cached --quiet; then
        log_info "No changes to commit in: $repo_name"
        return 0
    fi
    
    # Add all changes
    if ! git add .; then
        log_error "Failed to add changes in: $repo_name"
        return 1
    fi
    
    # Commit changes
    local commit_message="Automated: Generate bead tasks from planner.sh

Generated by Repository Automation System
Repository: $repo_name
Timestamp: $(date)"
    
    if ! git commit -m "$commit_message"; then
        log_error "Failed to commit changes in: $repo_name"
        return 1
    fi
    
    # Push changes
    if ! git push; then
        log_error "Failed to push changes in: $repo_name"
        return 1
    fi
    
    log_info "Successfully committed and pushed changes for: $repo_name"
    return 0
}

# Function to process files in repository directory
process_repository_files() {
    local repo_path="$1"
    local repo_name=$(get_repo_name "$repo_path")
    local repo_dir="$AUTOMATION_ROOT/$repo_name"
    local tasks_dir="$repo_dir/tasks"
    
    if [ ! -d "$tasks_dir" ]; then
        log_warn "Tasks directory not found: $tasks_dir"
        return 0
    fi
    
    log_info "Processing files in: $tasks_dir"
    
    # Find ready files to process
    local ready_files=($(find_ready_files "$tasks_dir" "txt"))
    
    if [ ${#ready_files[@]} -eq 0 ]; then
        log_info "No ready files to process in: $tasks_dir"
        return 0
    fi
    
    log_info "Found ${#ready_files[@]} ready files to process"
    
    local processed_files=()
    local failed_files=()
    
    for file_path in "${ready_files[@]}"; do
        local filename=$(basename "$file_path")
        
        log_info "Processing file: $filename"
        
        # Get file content
        local file_content=$(get_file_content "$file_path")
        if [ $? -ne 0 ]; then
            failed_files+=("$filename")
            continue
        fi
        
        # Switch repository to ai branch
        if ! switch_to_ai_branch "$repo_path"; then
            failed_files+=("$filename")
            continue
        fi
        
        # Generate bead tasks using OpenCode CLI
        if generate_bead_tasks "$repo_path" "$file_content"; then
            # Commit and push changes
            if commit_and_push_changes "$repo_path"; then
                # Mark file as processed (increment number)
                mark_file_processed "$file_path"
                processed_files+=("$filename")
            else
                failed_files+=("$filename")
            fi
        else
            failed_files+=("$filename")
        fi
    done
    
    # Log results
    if [ ${#processed_files[@]} -gt 0 ]; then
        log_info "Successfully processed files in $repo_name: ${processed_files[*]}"
    fi
    
    if [ ${#failed_files[@]} -gt 0 ]; then
        log_error "Failed to process files in $repo_name: ${failed_files[*]}"
        return 1
    fi
    
    return 0
}

# Function to process all repositories
process_all_repositories() {
    log_info "Starting to process all repositories"
    
    local repositories=($(get_repositories))
    
    if [ ${#repositories[@]} -eq 0 ]; then
        log_warn "No repositories found to process"
        return 0
    fi
    
    log_info "Found ${#repositories[@]} repositories to process"
    
    local processed_repos=()
    local failed_repos=()
    
    for repo in "${repositories[@]}"; do
        local repo_name=$(get_repo_name "$repo")
        
        # Check if repository directory exists
        if check_repo_directory_exists "$repo"; then
            log_info "Processing repository: $repo_name"
            
            if process_repository_files "$repo"; then
                processed_repos+=("$repo_name")
            else
                failed_repos+=("$repo_name")
            fi
        else
            log_warn "Repository directory not found for: $repo_name (skipping)"
        fi
    done
    
    # Log summary
    log_info "Planner completed. Processed: ${#processed_repos[@]}, Failed: ${#failed_repos[@]}"
    
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
    validate_dependencies "git" "find" || exit 1
    
    # Process all repositories
    process_all_repositories
}

# Run main function if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi