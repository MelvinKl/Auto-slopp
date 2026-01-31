#!/bin/bash

# Update repositories and merge main into branches using YAML configuration
# Set script name for logging identification
SCRIPT_NAME="updater"

# Load utilities and configuration first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# Set up error handling
setup_error_handling

log "INFO" "Starting updater.sh"
log "INFO" "Using managed_repo_path: $MANAGED_REPO_PATH"

# First update this repository
log "INFO" "Updating automation repository"
safe_git "pull"

# Check if managed_repo_path exists
if [ ! -d "$MANAGED_REPO_PATH" ]; then
    log "ERROR" "managed_repo_path not found: $MANAGED_REPO_PATH"
    exit 1
fi

# Process each subdirectory in managed_repo_path
for repo_dir in "$MANAGED_REPO_PATH"/*; do
    if [ ! -d "$repo_dir" ]; then
        continue
    fi
    
    log "INFO" "Updating repository: $(basename "$repo_dir")"
    cd "$repo_dir"
    
    # Fetch and clean
    log "DEBUG" "Fetching all remotes and cleaning working directory"
    safe_git "fetch --all"
    safe_git "clean -fd"
    
    # Get branches to update
    branches=$(git branch -r | grep -v 'HEAD' | sed 's/^[[:space:]]*origin\///')
    
    for branch in $branches; do
        # Only update renovate and ai branches
        if [[ $branch == renovate* ]] || [ "$branch" = "ai" ]; then
            log "DEBUG" "Updating branch: $branch"
            
            # Switch to branch
            if safe_git "checkout $branch" 2>/dev/null; then
                log "DEBUG" "Successfully switched to branch: $branch"
            else
                # Create ai branch if it doesn't exist
                log "INFO" "Branch $branch doesn't exist locally, creating from origin/main"
                safe_git "checkout -b $branch origin/main"
                safe_git "push -u origin $branch"
                continue
            fi
            
            log "DEBUG" "Resetting branch to origin/$branch"
            safe_git "reset --hard origin/$branch"
            
            # Merge main into branch
            log "DEBUG" "Merging origin/main into $branch"
            if safe_git "merge origin/main -m \"Merge main into $branch (automated)\""; then
                log "SUCCESS" "Successfully merged main into $branch"
                safe_git "push"
                log "SUCCESS" "Successfully pushed $branch to origin"
            else
                log "ERROR" "Merge failed for $branch, aborting merge"
                safe_git "merge --abort" 2>/dev/null || true
            fi
        fi
    done
done

script_success