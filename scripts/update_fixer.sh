#!/bin/bash

# Fix failed dependency updates in renovate branches using YAML configuration
# Set script name for logging identification
SCRIPT_NAME="update_fixer"

# Load utilities and configuration first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# Set up error handling
setup_error_handling

log "INFO" "Starting update_fixer.sh"
log "INFO" "Using managed_repo_path: $MANAGED_REPO_PATH"

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
    
    log "INFO" "Processing: $repo_dir"
    cd "$repo_dir"
    
    # Get renovate branches
    branches=$(safe_git "branch -r --list 'origin/renovate*'" 2>/dev/null | sed 's/^[[:space:]]*origin\///')
    
    for branch in $branches; do
        log "DEBUG" "Branch: $branch"
        
        # Update branch
        safe_git "fetch origin"
        safe_git "reset --hard origin/$branch"
        safe_git "clean -fd"
        
        # Run tests
        if [ -f "Makefile" ]; then
            if ! make test; then
                log "WARNING" "Tests failed, using opencode CLI to fix"
                safe_execute_opencode "$OPencode_CMD run \"Fix the branch '$branch' that contains updates to dependencies and push them to the branch. The tests are currently failing, so identify and fix any issues preventing the tests from passing, then push the fixes to the branch.\" --agent OpenAgent"
            fi
        fi
    done
done

script_success