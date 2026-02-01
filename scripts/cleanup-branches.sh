#!/bin/bash

# Branch Cleanup Script - Remove local branches that no longer exist on remote
# Identifies and safely removes local branches that no longer exist on the remote repository
# Integrates with Auto-slopp system architecture and follows established patterns

# Set script name for logging identification
SCRIPT_NAME="cleanup-branches"

# Load utilities and configuration first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/branch_protection.sh"
source "$PROJECT_DIR/config.sh"

# Set up error handling
setup_error_handling

# Initialize branch protection system
if ! initialize_branch_protection; then
    log "ERROR" "Failed to initialize branch protection system"
    exit 1
fi

log "INFO" "Starting branch cleanup script"
log "INFO" "Using managed_repo_path: $MANAGED_REPO_PATH"

# Check if managed_repo_path exists
if [ ! -d "$MANAGED_REPO_PATH" ]; then
    log "ERROR" "managed_repo_path not found: $MANAGED_REPO_PATH"
    exit 1
fi

# Track overall statistics
TOTAL_REPOS_PROCESSED=0
TOTAL_BRANCHES_CLEANED=0
TOTAL_ERRORS=0

# Function to get list of remote branches
get_remote_branches() {
    local repo_dir="$1"
    cd "$repo_dir" || return 1
    
    # Get remote branches excluding HEAD
    git ls-remote --heads origin 2>/dev/null | sed 's/.*\///' | sort || {
        log "ERROR" "Failed to list remote branches in $(basename "$repo_dir")"
        return 1
    }
}

# Function to get list of local branches
get_local_branches() {
    local repo_dir="$1"
    cd "$repo_dir" || return 1
    
    # Get local branches (exclude current branch with asterisk)
    git branch --format='%(refname:short)' 2>/dev/null | grep -v '^*' | sort || {
        log "ERROR" "Failed to list local branches in $(basename "$repo_dir")"
        return 1
    }
}

# Function to get current branch
get_current_branch() {
    local repo_dir="$1"
    cd "$repo_dir" || return 1
    
    git rev-parse --abbrev-ref HEAD 2>/dev/null || {
        log "ERROR" "Failed to determine current branch in $(basename "$repo_dir")"
        return 1
    }
}

# Function to check if branch is protected
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

# Function to safely delete a local branch (with enhanced protection)
safe_delete_branch() {
    local branch="$1"
    local repo_dir="$2"
    
    log "INFO" "Attempting to delete local branch: $branch"
    
    # Use enhanced branch protection for deletion
    if safe_delete_branch_with_protection "$branch" "$repo_dir" "false"; then
        log "SUCCESS" "Successfully deleted branch: $branch"
        return 0
    else
        log "ERROR" "Failed to delete branch: $branch (may be protected)"
        return 1
    fi
}

# Function to cleanup branches for a single repository
cleanup_repository_branches() {
    local repo_dir="$1"
    local repo_name=$(basename "$repo_dir")
    
    log "INFO" "Processing repository: $repo_name"
    
    # Verify it's a git repository
    if [ ! -d "$repo_dir/.git" ]; then
        log "WARNING" "Skipping $repo_name - not a git repository"
        return 0
    fi
    
    # Get current branch (cannot be deleted)
    local current_branch
    if ! current_branch=$(get_current_branch "$repo_dir"); then
        log "ERROR" "Failed to get current branch for $repo_name"
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
        return 1
    fi
    
    log "DEBUG" "Current branch in $repo_name: $current_branch"
    
    # Get remote and local branch lists
    local remote_branches local_branches
    if ! remote_branches=$(get_remote_branches "$repo_dir"); then
        log "ERROR" "Failed to get remote branches for $repo_name"
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
        return 1
    fi
    
    if ! local_branches=$(get_local_branches "$repo_dir"); then
        log "ERROR" "Failed to get local branches for $repo_name"
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
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
            # Branch doesn't exist on remote - check protection before marking for deletion
            if check_branch_protection "$local_branch" "$repo_dir" "delete"; then
                # Branch is not protected, mark for deletion
                branches_to_delete+=("$local_branch")
                log "DEBUG" "Marked for deletion: $local_branch"
            else
                # Branch is protected
                branches_skipped+=("$local_branch (protected)")
                log "DEBUG" "Skipping protected branch: $local_branch"
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
            TOTAL_BRANCHES_CLEANED=$((TOTAL_BRANCHES_CLEANED + 1))
        else
            TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
        fi
    done
    
    if [[ $repo_cleaned_count -gt 0 ]]; then
        log "SUCCESS" "Cleaned up $repo_cleaned_count branches in $repo_name"
    else
        log "INFO" "No branches needed cleanup in $repo_name"
    fi
    
    TOTAL_REPOS_PROCESSED=$((TOTAL_REPOS_PROCESSED + 1))
    return 0
}

# Main processing loop
log "INFO" "Starting branch cleanup for all repositories"

for repo_dir in "$MANAGED_REPO_PATH"/*; do
    if [ ! -d "$repo_dir" ]; then
        continue
    fi
    
    cleanup_repository_branches "$repo_dir"
done

# Final summary
log "INFO" "Branch cleanup completed"
log "INFO" "Repositories processed: $TOTAL_REPOS_PROCESSED"
log "INFO" "Total branches cleaned: $TOTAL_BRANCHES_CLEANED"
log "INFO" "Total errors encountered: $TOTAL_ERRORS"

if [[ $TOTAL_ERRORS -gt 0 ]]; then
    log "WARNING" "Completed with $TOTAL_ERRORS errors - check logs for details"
    exit 1
else
    log "SUCCESS" "Branch cleanup completed successfully"
    exit 0
fi