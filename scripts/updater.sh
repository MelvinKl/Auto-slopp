#!/bin/bash

# updater.sh - Updates repositories and merges changes into branches
# Does git pull in this repo and updates all repositories with main branch merges

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

# Function to update this repository
update_automation_repo() {
    log_info "Updating automation repository: $AUTOMATION_ROOT"
    
    cd "$AUTOMATION_ROOT" || return 1
    
    # Fetch latest changes
    log_debug "Fetching changes in automation repository"
    if ! retry 3 "git fetch --all"; then
        log_error "Failed to fetch changes in automation repository"
        return 1
    fi
    
    # Pull latest changes
    log_debug "Pulling latest changes"
    if ! git pull; then
        log_error "Failed to pull changes in automation repository"
        return 1
    fi
    
    log_info "Automation repository updated successfully"
    return 0
}

# Function to get all branches for a repository
get_all_branches() {
    local repo_path="$1"
    
    cd "$repo_path" || return 1
    
    # Get all remote branches
    local branches=$(git branch -r | grep -v 'HEAD' | sed 's/^[[:space:]]*origin\///')
    
    echo "$branches"
}

# Function to clean repository
clean_repository() {
    local repo_path="$1"
    
    cd "$repo_path" || return 1
    
    log_info "Cleaning repository: $repo_path"
    
    # Clean working directory
    if ! git clean -fd; then
        log_warn "Failed to clean $repo_path"
    fi
    
    # Reset to current branch
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    if ! git reset --hard; then
        log_error "Failed to reset $repo_path"
        return 1
    fi
    
    log_info "Repository cleaned: $repo_path"
}

# Function to fetch and update repository
fetch_and_reset_repository() {
    local repo_path="$1"
    
    cd "$repo_path" || return 1
    
    log_info "Fetching and resetting repository: $repo_path"
    
    # Fetch all changes
    if ! retry 3 "git fetch --all"; then
        log_error "Failed to fetch changes for $repo_path"
        return 1
    fi
    
    log_info "Repository fetched successfully: $repo_path"
}

# Function to merge main into a branch
merge_main_into_branch() {
    local repo_path="$1"
    local target_branch="$2"
    
    cd "$repo_path" || return 1
    
    log_info "Merging main into $target_branch in: $repo_path"
    
    # Switch to target branch
    if ! git checkout "$target_branch"; then
        log_error "Failed to switch to branch $target_branch in $repo_path"
        return 1
    fi
    
    # Reset to remote branch
    if ! git reset --hard "origin/$target_branch"; then
        log_error "Failed to reset branch $target_branch in $repo_path"
        return 1
    fi
    
    # Merge main into the branch
    if git merge origin/main -m "Merge main into $target_branch (automated)"; then
        log_info "Successfully merged main into $target_branch in $repo_path"
        
        # Push the merge
        if git push; then
            log_info "Successfully pushed merge to $target_branch in $repo_path"
            return 0
        else
            log_error "Failed to push merge to $target_branch in $repo_path"
            return 1
        fi
    else
        log_error "Failed to merge main into $target_branch in $repo_path"
        
        # Abort the merge if it failed
        git merge --abort 2>/dev/null || true
        return 1
    fi
}

# Function to get renovate branches
get_renovate_branches() {
    local repo_path="$1"
    
    cd "$repo_path" || return 1
    
    # Get all branches that start with "renovate"
    local branches=$(git branch -r --list 'origin/renovate*' 2>/dev/null | sed 's/^[[:space:]]*origin\///')
    
    echo "$branches"
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
    
    # Clean repository
    clean_repository "$repo_path"
    
    # Fetch and reset
    fetch_and_reset_repository "$repo_path"
    
    # Get branches to update
    local renovate_branches=$(get_renovate_branches "$repo_path")
    local ai_branch="ai"
    
    # Build list of branches to update
    local branches_to_update=()
    
    # Add renovate branches
    while IFS= read -r branch; do
        if [ -n "$branch" ]; then
            branches_to_update+=("$branch")
        fi
    done <<< "$renovate_branches"
    
    # Add ai branch if it exists
    cd "$repo_path" || return 1
    if git rev-parse --verify origin/ai >/dev/null 2>&1; then
        branches_to_update+=("$ai_branch")
    fi
    
    if [ ${#branches_to_update[@]} -eq 0 ]; then
        log_info "No branches to update in: $repo_name"
        return 0
    fi
    
    log_info "Found ${#branches_to_update[@]} branches to update in: $repo_name"
    
    local updated_branches=()
    local failed_branches=()
    
    # Update each branch
    for branch in "${branches_to_update[@]}"; do
        log_info "Updating branch: $branch"
        
        if merge_main_into_branch "$repo_path" "$branch"; then
            updated_branches+=("$branch")
        else
            failed_branches+=("$branch")
        fi
    done
    
    # Log results
    if [ ${#updated_branches[@]} -gt 0 ]; then
        log_info "Successfully updated branches in $repo_name: ${updated_branches[*]}"
    fi
    
    if [ ${#failed_branches[@]} -gt 0 ]; then
        log_error "Failed to update branches in $repo_name: ${failed_branches[*]}"
        return 1
    fi
    
    return 0
}

# Function to process all repositories
process_all_repositories() {
    log_info "Starting to update all repositories"
    
    local repositories=($(get_repositories))
    
    if [ ${#repositories[@]} -eq 0 ]; then
        log_warn "No repositories found to process"
        return 0
    fi
    
    log_info "Found ${#repositories[@]} repositories to process"
    
    local updated_repos=()
    local failed_repos=()
    
    for repo in "${repositories[@]}"; do
        if process_repository "$repo"; then
            updated_repos+=("$(get_repo_name "$repo")")
        else
            failed_repos+=("$(get_repo_name "$repo")")
        fi
    done
    
    # Log summary
    log_info "Updater completed. Updated: ${#updated_repos[@]}, Failed: ${#failed_repos[@]}"
    
    if [ ${#updated_repos[@]} -gt 0 ]; then
        log_info "Updated repositories: ${updated_repos[*]}"
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
    
    # Update this repository first
    if ! update_automation_repo; then
        log_error "Failed to update automation repository"
        exit 1
    fi
    
    # Process all repositories
    process_all_repositories
}

# Run main function if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi