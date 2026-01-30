#!/bin/bash

# Implement ready bead tasks using YAML configuration
# Load utilities and configuration first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# Set up error handling
setup_error_handling

log "INFO" "Starting implementer.sh"
log "INFO" "Using managed_repo_path: $MANAGED_REPO_PATH"

# Validate required environment variables
validate_env_vars MANAGED_REPO_PATH OPencode_CMD

# Check if directories exist and are accessible
check_directory "$MANAGED_REPO_PATH" "managed_repo_path"

# Process each subdirectory in managed_repo_path
for repo_dir in "$MANAGED_REPO_PATH"/*; do
    if [ ! -d "$repo_dir" ]; then
        continue
    fi
    
    log "INFO" "Implementing tasks for: $(basename "$repo_dir")"
    export GIT_REPO_DIR="$repo_dir"
    cd "$repo_dir"
    
    # Switch to ai branch
    safe_git "fetch origin"
    
    # Create ai branch if it doesn't exist
    if ! git rev-parse --verify origin/ai >/dev/null 2>&1; then
        safe_git "checkout -b ai origin/main"
        safe_git "push -u origin ai"
    else
        safe_git "checkout ai"
        safe_git "reset --hard origin/ai"
    fi
    
    # Use opencode CLI to find and implement next ready task
    log "INFO" "Using opencode CLI to find and implement next ready task"
    if command_exists "$OPencode_CMD"; then
        safe_execute "$OPencode_CMD run \"Find the next ready bead task and implement it. Use the beads CLI to discover ready tasks, then implement the task and manage the beads workflow (mark in progress, close when complete). Commit all changes and push to the current branch. Ensure that the current branch has all changes from origin/main\" --agent OpenAgent"
        log "SUCCESS" "Task implementation completed"
    else
        log "ERROR" "OpenCode CLI not found: $OPencode_CMD"
        exit 1
    fi
done

script_success
