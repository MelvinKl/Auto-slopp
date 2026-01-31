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
        
        # Merge origin/main into ai branch before starting work with conflict detection
        log "INFO" "Merging origin/main into ai branch before task implementation"
        merge_result=$(merge_origin_main_to_ai_with_escalation)
        merge_exit_code=$?
        
        if [[ $merge_exit_code -eq 0 ]]; then
            log "SUCCESS" "Pre-work merge completed successfully"
        elif [[ $merge_exit_code -eq 2 ]]; then
            log "ERROR" "Pre-work merge conflicts detected - cannot proceed with task implementation"
            log "ERROR" "Opencode escalation required before continuing"
            
            # Update opencode prompt to include conflict resolution requirement
            opencode_prompt="Find the next ready bead task and implement it. Do only one task, not multiple. Use the beads CLI to discover ready tasks, then implement the task and manage the beads workflow (mark in progress, close when complete). FIRST: resolve merge conflicts from previous attempt using conflict report at $(echo $merge_result). Then commit all changes and push to the current branch. Ensure that the current branch has all changes from origin/main"
            
            # Execute opencode with conflict resolution requirement
            safe_execute "$OPencode_CMD run \"$opencode_prompt\" --agent OpenAgent"
            log "SUCCESS" "Task implementation completed after conflict resolution"
            continue  # Skip to next repository
        else
            log "WARNING" "Pre-work merge failed due to non-conflict issues, proceeding with existing state"
        fi
    fi
    
    # Use opencode CLI to find and implement next ready task
    log "INFO" "Using opencode CLI to find and implement next ready task"
    if command_exists "${OPencode_CMD##* }"; then
        safe_execute "$OPencode_CMD run \"Find the next ready bead task and implement it. Use the beads CLI to discover ready tasks, then implement the task and manage the beads workflow (mark in progress, close when complete). Commit all changes and push to the current branch. Ensure that the current branch has all changes from origin/main\" --agent OpenAgent"
        
        # After opencode completes, validate and push changes with conflict detection
        opencode_exit_code=$?
        if [ $opencode_exit_code -eq 0 ]; then
            log "INFO" "Task implementation completed, validating changes before push"
            
            # Check if there are changes to push
            if [ -n "$(git status --porcelain 2>/dev/null)" ] || [ -n "$(git log origin/ai..HEAD --oneline 2>/dev/null)" ]; then
                log "INFO" "Changes detected, performing merge-before-push validation with conflict detection"
                
                # Merge latest main before pushing with conflict detection
                merge_result=$(merge_origin_main_to_ai_with_escalation)
                merge_exit_code=$?
                
                if [[ $merge_exit_code -eq 0 ]]; then
                    log "SUCCESS" "Merge validation passed, pushing changes to ai branch"
                    safe_git "push origin ai"
                    log "SUCCESS" "Changes successfully pushed to ai branch"
                elif [[ $merge_exit_code -eq 2 ]]; then
                    log "ERROR" "Push-time merge conflicts detected - escalating to opencode"
                    log "INFO" "Conflict report available at: $(echo $merge_result)"
                    
                    # Update opencode prompt for conflict resolution
                    opencode_prompt="Resolve merge conflicts from push validation using conflict report at $(echo $merge_result). Then commit all changes and push to the current branch. Ensure that the current branch has all changes from origin/main"
                    
                    # Execute opencode for conflict resolution
                    safe_execute "$OPencode_CMD run \"$opencode_prompt\" --agent OpenAgent"
                    log "SUCCESS" "Changes pushed after conflict resolution"
                else
                    log "ERROR" "Merge validation failed due to non-conflict issues, changes not pushed"
                    log "WARNING" "Manual intervention may be required to resolve merge issues"
                fi
            else
                log "INFO" "No changes detected, nothing to push"
            fi
            
            log "SUCCESS" "Task implementation and validation completed"
        else
            log "ERROR" "OpenCode CLI execution failed with exit code: $opencode_exit_code"
            exit 1
        fi
    else
        log "ERROR" "OpenCode CLI not found: ${OPencode_CMD##* }"
        exit 1
    fi
done

script_success
