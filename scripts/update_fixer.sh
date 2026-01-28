#!/bin/bash

# update_fixer.sh - Fixes failed test runs in renovate branches
# Loops through all repositories and handles failed dependency updates

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

# Function to get renovate branches
get_renovate_branches() {
    local repo_path="$1"
    
    cd "$repo_path" || return 1
    
    # Get all branches that start with "renovate"
    local branches=$(git branch -r --list 'origin/renovate*' 2>/dev/null | sed 's/^[[:space:]]*origin\///')
    
    echo "$branches"
}

# Function to update repository state
update_repository() {
    local repo_path="$1"
    local branch="$2"
    
    cd "$repo_path" || return 1
    
    log_info "Updating repository: $repo_path (branch: $branch)"
    
    # Fetch latest changes
    log_debug "Fetching changes..."
    if ! retry 3 "git fetch --all"; then
        log_error "Failed to fetch changes for $repo_path"
        return 1
    fi
    
    # Reset to remote branch
    log_debug "Resetting to remote branch..."
    if ! git reset --hard "origin/$branch"; then
        log_error "Failed to reset branch $branch in $repo_path"
        return 1
    fi
    
    # Clean working directory
    log_debug "Cleaning working directory..."
    if ! git clean -fd; then
        log_warn "Failed to clean $repo_path"
    fi
    
    log_info "Repository updated successfully: $repo_path ($branch)"
}

# Function to run tests
run_tests() {
    local repo_path="$1"
    
    cd "$repo_path" || return 1
    
    log_info "Running tests in: $repo_path"
    
    # Check if Makefile exists
    if [ -f "Makefile" ]; then
        if make test; then
            log_info "Tests passed in: $repo_path"
            return 0
        else
            log_warn "Tests failed in: $repo_path"
            return 1
        fi
    else
        log_info "No Makefile found in $repo_path, skipping tests"
        return 0
    fi
}

# Function to fix failed updates using OpenCode CLI
fix_with_opencode() {
    local repo_path="$1"
    local branch="$2"
    
    cd "$repo_path" || return 1
    
    log_info "Attempting to fix failed updates in: $repo_path ($branch)"
    
    # Construct the instruction for OpenCode CLI
    local instruction="Fix the branch '$branch' that contains updates to dependencies and push them to the branch. The tests are currently failing, so identify and fix any issues preventing the tests from passing, then push the fixes to the branch."
    
    log_info "Running OpenCode CLI with instruction: $instruction"
    
    # Check if OpenCode CLI is available
    if ! command_exists "$OPencode_CLI"; then
        log_error "OpenCode CLI not found: $OPencode_CLI"
        return 1
    fi
    
    # Run OpenCode CLI with the instruction
    if "$OPencode_CLI" "$instruction"; then
        log_info "OpenCode CLI completed successfully for: $repo_path ($branch)"
        return 0
    else
        log_error "OpenCode CLI failed for: $repo_path ($branch)"
        return 1
    fi
}

# Function to process a single repository
process_repository() {
    local repo_path="$1"
    
    if [ ! -d "$repo_path" ]; then
        log_error "Repository not found: $repo_path"
        return 1
    fi
    
    cd "$repo_path" || return 1
    
    log_info "Processing repository: $repo_path"
    
    # Get renovate branches
    local renovate_branches=$(get_renovate_branches "$repo_path")
    
    if [ -z "$renovate_branches" ]; then
        log_info "No renovate branches found in: $repo_path"
        return 0
    fi
    
    local processed_branches=()
    local failed_branches=()
    
    # Process each renovate branch
    while IFS= read -r branch; do
        if [ -n "$branch" ]; then
            log_info "Processing branch: $branch"
            
            # Update repository state
            if update_repository "$repo_path" "$branch"; then
                # Run tests
                if run_tests "$repo_path"; then
                    processed_branches+=("$branch")
                else
                    # Tests failed, try to fix with OpenCode
                    if fix_with_opencode "$repo_path" "$branch"; then
                        processed_branches+=("$branch")
                    else
                        failed_branches+=("$branch")
                    fi
                fi
            else
                failed_branches+=("$branch")
            fi
        fi
    done <<< "$renovate_branches"
    
    # Log results
    if [ ${#processed_branches[@]} -gt 0 ]; then
        log_info "Successfully processed branches in $repo_path: ${processed_branches[*]}"
    fi
    
    if [ ${#failed_branches[@]} -gt 0 ]; then
        log_error "Failed to process branches in $repo_path: ${failed_branches[*]}"
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
        if process_repository "$repo"; then
            processed_repos+=("$repo")
        else
            failed_repos+=("$repo")
        fi
    done
    
    # Log summary
    log_info "Update fixer completed. Processed: ${#processed_repos[@]}, Failed: ${#failed_repos[@]}"
    
    if [ ${#failed_repos[@]} -gt 0 ]; then
        log_warn "Failed repositories: ${failed_repos[*]}"
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