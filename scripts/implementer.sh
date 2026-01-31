#!/bin/bash

# Implement ready bead tasks using YAML configuration
# Set script name for logging identification
SCRIPT_NAME="implementer"

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
        
        # Merge origin/main into ai branch before starting work with comprehensive error handling
        log "INFO" "Starting pre-work merge with comprehensive error handling and logging"
        merge_result=$(merge_origin_main_to_ai_with_escalation)
        merge_exit_code=$?
        
        if [[ $merge_exit_code -eq 0 ]]; then
            log "SUCCESS" "Pre-work merge completed successfully with full logging"
            log_merge_resolution_outcome "pre_work_success" "0" "0" "pre_work_merge"
        elif [[ $merge_exit_code -eq 2 ]]; then
            log "ERROR" "Pre-work merge conflicts detected - escalating to opencode with full context"
            log_opencode_escalation "pre_work_merge_conflicts" "$merge_result" "pre_work_phase"
            
            # Update opencode prompt to include conflict resolution requirement with enhanced context
            opencode_prompt="Find the next ready bead task and implement it. Use the beads CLI to discover ready tasks, then implement the task and manage the beads workflow (mark in progress, close when complete). FIRST: resolve merge conflicts from previous attempt using conflict report at $(echo $merge_result). Use the comprehensive error handling system to log all resolution steps. Then commit all changes and push to the current branch. Ensure that the current branch has all changes from origin/main. Log all merge operations using the enhanced logging functions."
            
            # Execute opencode with conflict resolution requirement
            safe_execute "$OPencode_CMD run \"$opencode_prompt\" --agent OpenAgent"
            
            # After opencode resolution, verify and log the outcome
            local opencode_exit_code=$?
            if [[ $opencode_exit_code -eq 0 ]]; then
                log_merge_resolution_outcome "opencode_resolved" "0" "0" "pre_work_conflict_resolution"
                log "SUCCESS" "Pre-work conflicts resolved by opencode, task implementation completed"
            else
                log "ERROR" "Opencode conflict resolution failed with exit code: $opencode_exit_code"
            fi
            
            continue  # Skip to next repository
        else
            log "WARNING" "Pre-work merge failed due to non-conflict issues, proceeding with existing state"
            # Log the failure for tracking
            local error_type=$(classify_merge_error "$merge_exit_code" "Pre-work merge failed")
            log "ERROR" "Pre-work merge failure type: $error_type"
        fi
    fi
    
    # Check if there are open bead tasks before calling opencode
    log "INFO" "Checking for available open bead tasks before calling opencode"
    repo_name=$(basename "$repo_dir")
    
    if has_open_bead_tasks "$repo_dir"; then
        open_tasks_count=$(get_open_bead_tasks_count "$repo_dir")
        log_task_availability_decision "$repo_name" "true" "$open_tasks_count" "proceed" "tasks found"
        
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
                
                # Merge latest main before pushing with comprehensive error handling and logging
                log "INFO" "Starting push-time merge validation with comprehensive error handling"
                merge_result=$(merge_origin_main_to_ai_with_escalation)
                merge_exit_code=$?
                
                if [[ $merge_exit_code -eq 0 ]]; then
                    log "SUCCESS" "Push-time merge validation passed, pushing changes to ai branch"
                    log_merge_resolution_outcome "push_validation_success" "0" "0" "push_time_merge"
                    safe_git "push origin ai"
                    log "SUCCESS" "Changes successfully pushed to ai branch"
                elif [[ $merge_exit_code -eq 2 ]]; then
                    log "ERROR" "Push-time merge conflicts detected - escalating to opencode with full context"
                    log_opencode_escalation "push_time_merge_conflicts" "$merge_result" "push_validation_phase"
                    
                    # Update opencode prompt for conflict resolution with enhanced logging requirements
                    opencode_prompt="Resolve merge conflicts from push validation using conflict report at $(echo $merge_result). Use the comprehensive error handling system to log all resolution steps. Then commit all changes and push to the current branch. Ensure that the current branch has all changes from origin/main. Document all merge resolution actions using the enhanced logging functions."
                    
                    # Execute opencode for conflict resolution
                    safe_execute "$OPencode_CMD run \"$opencode_prompt\" --agent OpenAgent"
                    
                    # After opencode resolution, verify and log the outcome
                    local opencode_exit_code=$?
                    if [[ $opencode_exit_code -eq 0 ]]; then
                        log_merge_resolution_outcome "push_time_opencode_resolved" "0" "0" "push_time_conflict_resolution"
                        log "SUCCESS" "Push-time conflicts resolved and changes pushed successfully"
                    else
                        log "ERROR" "Push-time opencode conflict resolution failed with exit code: $opencode_exit_code"
                    fi
                else
                    log "ERROR" "Push-time merge validation failed due to non-conflict issues, changes not pushed"
                    log "WARNING" "Manual intervention may be required to resolve merge issues"
                    
                    # Log the specific error type for debugging
                    local error_type=$(classify_merge_error "$merge_exit_code" "Push-time merge validation failed")
                    log "ERROR" "Push-time merge failure type: $error_type"
                    
                    # Attempt rollback and preserve state
                    rollback_merge_on_failure "$error_type" "push_validation"
                    preserve_state_for_opencode "push_validation_failed" "$error_type"
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
    else
        log_task_availability_decision "$repo_name" "false" "0" "skip" "no open tasks found"
        log "INFO" "Skipping opencode call for $repo_name - no open bead tasks available"
    fi
done

script_success
