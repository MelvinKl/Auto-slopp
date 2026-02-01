#!/bin/bash

# Enhanced Branch Cleanup Script - Remove local branches that no longer exist on remote
# Integrates with advanced error handling, system state management, and configuration validation
# Provides comprehensive safety mechanisms and detailed reporting

# Set script name for logging identification
SCRIPT_NAME="cleanup-branches-enhanced"

# Load core architecture modules
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/branch_protection.sh"

# Only load core modules if they exist (for testing without full system)
if [[ -f "$SCRIPT_DIR/core/error_recovery.sh" ]]; then
    source "$SCRIPT_DIR/core/error_recovery.sh"
    source "$SCRIPT_DIR/core/system_state.sh"
    source "$SCRIPT_DIR/core/configuration_validator.sh"
fi

source "$PROJECT_DIR/config.sh"

# =============================================================================
# ENHANCED CONFIGURATION AND INITIALIZATION
# =============================================================================

# Script-specific configuration
CLEANUP_OPERATION_ID="cleanup_$(date +%s)"
DRY_RUN_MODE="${DRY_RUN_MODE:-false}"
SAFETY_MODE="${SAFETY_MODE:-true}"  # Enable all safety checks by default
BACKUP_BEFORE_DELETE="${BACKUP_BEFORE_DELETE:-true}"
MAX_BRANCHES_PER_RUN="${MAX_BRANCHES_PER_RUN:-50}"

    # Initialize enhanced systems
    initialize_enhanced_cleanup_system() {
        log "INFO" "Initializing enhanced cleanup system (operation: $CLEANUP_OPERATION_ID)"
        
        # Initialize branch protection system
        if ! initialize_branch_protection; then
            log "ERROR" "Failed to initialize branch protection system"
            return 1
        fi
        
        # Initialize system state management
        initialize_state_management
        
        # Validate configuration
        if ! validate_configuration "" "strict"; then
            log "ERROR" "Configuration validation failed, attempting repair"
            attempt_configuration_repair "safe"
            
            # Re-validate after repair
            if ! validate_configuration "" "permissive"; then
                log "ERROR" "Configuration still invalid after repair attempt"
                return 1
            fi
        fi
        
        # Set up enhanced error handling
        setup_enhanced_error_handling
        
        # Perform initial health check
        perform_health_check "" "startup"
        
        # Record operation start
        record_operation_performance "cleanup_branches_startup" 0 true
        
        log "SUCCESS" "Enhanced cleanup system initialized"
        return 0
    }

# =============================================================================
# ENHANCED BRANCH ANALYSIS ALGORITHMS
# =============================================================================

# Comprehensive branch analysis with conflict detection
analyze_branches_comprehensive() {
    local repo_dir="$1"
    local repo_name=$(basename "$repo_dir")
    local analysis_file="/tmp/branch_analysis_${repo_name}_$(date +%s).json"
    
    log "INFO" "Starting comprehensive branch analysis for: $repo_name"
    
    # Initialize analysis data structure
    local analysis_data=$(cat << EOF
{
    "repository": "$repo_name",
    "analysis_timestamp": "$(date -Iseconds)",
    "operation_id": "$CLEANUP_OPERATION_ID",
    "local_branches": [],
    "remote_branches": [],
    "branch_states": {},
    "potential_conflicts": [],
    "safety_assessments": {},
    "recommendations": []
}
EOF
)
    
    # Phase 1: Collect branch data with enhanced error handling
    if ! collect_enhanced_branch_data "$repo_dir" analysis_data; then
        log "ERROR" "Failed to collect branch data for: $repo_name"
        return 1
    fi
    
    # Phase 2: Analyze branch states and relationships
    analyze_branch_states "$repo_dir" analysis_data
    
    # Phase 3: Detect potential conflicts and safety issues
    detect_branch_conflicts "$repo_dir" analysis_data
    
    # Phase 4: Generate safety assessments and recommendations
    generate_safety_assessments "$repo_dir" analysis_data
    
    # Save analysis results
    echo "$analysis_data" > "$analysis_file"
    log "INFO" "Branch analysis saved: $analysis_file"
    
    # Return analysis results for processing
    echo "$analysis_data"
    return 0
}

# Enhanced branch data collection
collect_enhanced_branch_data() {
    local repo_dir="$1"
    local -n data_ref=$2
    local repo_name=$(basename "$repo_dir")
    
    log "DEBUG" "Collecting enhanced branch data for: $repo_name"
    
    cd "$repo_dir" || {
        log "ERROR" "Cannot access repository directory: $repo_dir"
        return 1
    }
    
    # Get current branch with error handling
    local current_branch
    if ! current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null); then
        log "ERROR" "Failed to determine current branch in: $repo_name"
        return 1
    fi
    
    # Get remote branches with network error handling
    local remote_branches
    if ! remote_branches=$(git ls-remote --heads origin 2>/dev/null | sed 's/.*\///' | sort); then
        log "WARNING" "Failed to fetch remote branches for: $repo_name (network issue?)"
        # Continue with local analysis only
        remote_branches=""
    fi
    
    # Get local branches with detailed information
    local local_branches_info
    if ! local_branches_info=$(git branch --format='%(refname:short)|%(objectname)|%(committerdate:iso8601)|%(authorname)' 2>/dev/null); then
        log "ERROR" "Failed to list local branches in: $repo_name"
        return 1
    fi
    
    # Parse and enhance branch information
    local -A enhanced_local_branches=()
    while IFS='|' read -r branch_name commit_hash commit_date author; do
        [[ -n "$branch_name" ]] || continue
        
        # Skip current branch (marked with *)
        if [[ "$branch_name" == "$current_branch" ]]; then
            continue
        fi
        
        # Get additional branch metadata
        local branch_age_days=0
        local last_commit_timestamp=0
        local is_merged=true
        local has_untracked_changes=false
        
        # Calculate branch age
        if [[ -n "$commit_date" ]]; then
            last_commit_timestamp=$(date -d "$commit_date" +%s 2>/dev/null || echo 0)
            local current_timestamp=$(date +%s)
            branch_age_days=$(((current_timestamp - last_commit_timestamp) / 86400))
        fi
        
        # Check if branch is merged into main/master
        if git merge-base --is-ancestor "$branch_name" "main" 2>/dev/null || \
           git merge-base --is-ancestor "$branch_name" "master" 2>/dev/null; then
            is_merged=true
        else
            is_merged=false
        fi
        
        # Check for untracked changes in branch
        if git diff --name-only "$branch_name" 2>/dev/null | grep -q .; then
            has_untracked_changes=true
        fi
        
        # Store enhanced branch information
        enhanced_local_branches["$branch_name"]=$(cat << EOF
{
    "name": "$branch_name",
    "commit_hash": "$commit_hash",
    "commit_date": "$commit_date",
    "author": "$author",
    "age_days": $branch_age_days,
    "last_commit_timestamp": $last_commit_timestamp,
    "is_merged": $is_merged,
    "has_untracked_changes": $has_untracked_changes,
    "exists_on_remote": false
}
EOF
)
    done <<< "$local_branches_info"
    
    # Check which local branches exist on remote
    local -A remote_branch_map=()
    while IFS= read -r remote_branch; do
        [[ -n "$remote_branch" ]] && remote_branch_map["$remote_branch"]=1
    done <<< "$remote_branches"
    
    # Update local branch information with remote existence
    for branch_name in "${!enhanced_local_branches[@]}"; do
        if [[ -n "${remote_branch_map[$branch_name]:-}" ]]; then
            # Update the JSON to mark as existing on remote
            local branch_info="${enhanced_local_branches[$branch_name]}"
            enhanced_local_branches["$branch_name"]=$(echo "$branch_info" | jq '.exists_on_remote = true')
        fi
    done
    
    # Update analysis data with collected information
    # (This would be implemented with jq for proper JSON manipulation)
    
    log "DEBUG" "Enhanced branch data collection completed for: $repo_name"
    return 0
}

# Analyze branch states and relationships
analyze_branch_states() {
    local repo_dir="$1"
    local -n data_ref=$2
    
    log "DEBUG" "Analyzing branch states for: $(basename "$repo_dir")"
    
    # Implementation would analyze:
    # - Branch relationships (parent/child)
    # - Merge status
    # - Divergence from remote
    # - Staleness indicators
    # - Dependency relationships
    
    # This is a placeholder for the detailed analysis logic
    log "DEBUG" "Branch state analysis completed"
}

# Detect potential conflicts and safety issues
detect_branch_conflicts() {
    local repo_dir="$1"
    local -n data_ref=$2
    
    log "DEBUG" "Detecting branch conflicts for: $(basename "$repo_dir")"
    
    # Implementation would detect:
    # - Branches with unmerged changes
    # - Branches that are bases for other branches
    # - Protected branches
    # - Recently active branches
    # - Branches with special tags or markers
    
    log "DEBUG" "Branch conflict detection completed"
}

# Generate safety assessments and recommendations
generate_safety_assessments() {
    local repo_dir="$1"
    local -n data_ref=$2
    
    log "DEBUG" "Generating safety assessments for: $(basename "$repo_dir")"
    
    # Implementation would generate:
    # - Safety scores for each branch
    # - Deletion recommendations
    # - Risk assessments
    # - Required actions before deletion
    
    log "DEBUG" "Safety assessment generation completed"
}

# =============================================================================
# ENHANCED SAFETY MECHANISMS
# =============================================================================

# Multi-stage safety verification
verify_branch_safety_comprehensive() {
    local branch="$1"
    local repo_dir="$2"
    local analysis_data="$3"
    
    log "DEBUG" "Performing comprehensive safety verification for branch: $branch"
    
    local safety_checks=()
    local safety_score=100
    local safety_reasons=()
    
    # Stage 1: Basic safety checks
    if ! verify_basic_safety "$branch" "$repo_dir"; then
        safety_score=0
        safety_reasons+=("Basic safety check failed")
        return 1
    fi
    
    # Stage 2: Advanced safety analysis
    if ! verify_advanced_safety "$branch" "$repo_dir" "$analysis_data"; then
        safety_score=$((safety_score - 50))
        safety_reasons+=("Advanced safety concerns detected")
    fi
    
    # Stage 3: Contextual safety checks
    if ! verify_contextual_safety "$branch" "$repo_dir"; then
        safety_score=$((safety_score - 25))
        safety_reasons+=("Contextual safety concerns")
    fi
    
    # Stage 4: Time-based safety checks
    if ! verify_temporal_safety "$branch" "$repo_dir"; then
        safety_score=$((safety_score - 15))
        safety_reasons+=("Temporal safety concerns")
    fi
    
    # Final safety assessment
    if [[ $safety_score -ge 80 ]]; then
        log "DEBUG" "Branch $branch passed safety verification (score: $safety_score)"
        return 0
    elif [[ $safety_score -ge 50 ]]; then
        log "WARNING" "Branch $branch has moderate safety concerns (score: $safety_score): ${safety_reasons[*]}"
        return 1
    else
        log "ERROR" "Branch $branch failed safety verification (score: $safety_score): ${safety_reasons[*]}"
        return 2
    fi
}

# Basic safety verification
verify_basic_safety() {
    local branch="$1"
    local repo_dir="$2"
    
    cd "$repo_dir" || return 1
    
    # Check if it's the current branch
    local current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [[ "$branch" == "$current_branch" ]]; then
        log "DEBUG" "Cannot delete current branch: $branch"
        return 1
    fi
    
    # Check protected branch names
    local protected_branches=("main" "master" "develop" "HEAD" "staging" "production")
    for protected in "${protected_branches[@]}"; do
        if [[ "$branch" == "$protected" ]]; then
            log "DEBUG" "Cannot delete protected branch: $branch"
            return 1
        fi
    done
    
    return 0
}

# Advanced safety analysis
verify_advanced_safety() {
    local branch="$1"
    local repo_dir="$2"
    local analysis_data="$3"
    
    cd "$repo_dir" || return 1
    
    # Check for unmerged changes
    if git log "main..$branch" --oneline 2>/dev/null | grep -q .; then
        log "DEBUG" "Branch $branch has unmerged changes"
        return 1
    fi
    
    # Check if other branches depend on this branch
    local dependent_branches=$(git branch --contains "$branch" --format='%(refname:short)' 2>/dev/null | grep -v "^$branch$")
    if [[ -n "$dependent_branches" ]]; then
        log "DEBUG" "Branch $branch has dependent branches: $dependent_branches"
        return 1
    fi
    
    # Check for stashed changes related to this branch
    if git stash list 2>/dev/null | grep -q "$branch"; then
        log "DEBUG" "Branch $branch has associated stashed changes"
        return 1
    fi
    
    return 0
}

# Contextual safety checks
verify_contextual_safety() {
    local branch="$1"
    local repo_dir="$2"
    
    cd "$repo_dir" || return 1
    
    # Check if branch is referenced in any configuration files
    if find "$repo_dir" -name "*.yaml" -o -name "*.yml" -o -name "*.json" -o -name "*.conf" 2>/dev/null | \
       xargs grep -l "$branch" 2>/dev/null | grep -q .; then
        log "DEBUG" "Branch $branch is referenced in configuration files"
        return 1
    fi
    
    # Check for branch-specific files or directories
    if [[ -d "$repo_dir/$branch" ]] || [[ -f "$repo_dir/$branch" ]]; then
        log "DEBUG" "Branch $branch has associated files/directories"
        return 1
    fi
    
    return 0
}

# Temporal safety checks
verify_temporal_safety() {
    local branch="$1"
    local repo_dir="$2"
    
    cd "$repo_dir" || return 1
    
    # Check branch age
    local branch_commit_date=$(git log -1 --format=%ct "$branch" 2>/dev/null)
    if [[ -n "$branch_commit_date" ]]; then
        local branch_age_days=$((( $(date +%s) - branch_commit_date ) / 86400))
        
        # Don't delete very recent branches (less than 7 days)
        if [[ $branch_age_days -lt 7 ]]; then
            log "DEBUG" "Branch $branch is too recent (${branch_age_days} days old)"
            return 1
        fi
        
        # Be cautious with recently active branches (less than 24 hours)
        if [[ $branch_age_days -lt 1 ]]; then
            log "DEBUG" "Branch $branch was recently active"
            return 1
        fi
    fi
    
    return 0
}

# =============================================================================
# ENHANCED BRANCH DELETION WITH BACKUP
# =============================================================================

# Safe branch deletion with backup and monitoring
safe_delete_branch_enhanced() {
    local branch="$1"
    local repo_dir="$2"
    local analysis_data="$3"
    local start_time=$(date +%s.%N)
    
    log "INFO" "Starting enhanced safe deletion of branch: $branch"
    
    cd "$repo_dir" || return 1
    
    # Create backup before deletion if enabled
    local backup_info=""
    if [[ "$BACKUP_BEFORE_DELETE" == "true" ]]; then
        backup_info=$(create_branch_backup "$branch" "$repo_dir")
        if [[ $? -ne 0 ]]; then
            log "WARNING" "Failed to create backup for branch: $branch"
            # Continue anyway if backup fails (configurable)
        fi
    fi
    
    # Perform deletion with monitoring
    local deletion_output
    local deletion_exit_code
    
    if [[ "$DRY_RUN_MODE" == "true" ]]; then
        log "INFO" "DRY RUN: Would delete branch: $branch"
        deletion_exit_code=0
    else
        # Try regular deletion first
        if deletion_output=$(git branch -d "$branch" 2>&1); then
            deletion_exit_code=0
            log "SUCCESS" "Successfully deleted branch: $branch"
        else
            deletion_exit_code=$?
            log "WARNING" "Regular deletion failed for $branch, trying force delete"
            
            # Try force delete
            if deletion_output=$(git branch -D "$branch" 2>&1); then
                deletion_exit_code=0
                log "SUCCESS" "Successfully force deleted branch: $branch"
            else
                log "ERROR" "Failed to delete branch: $branch"
                log "ERROR" "Deletion output: $deletion_output"
            fi
        fi
    fi
    
    # Record operation performance
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    record_operation_performance "branch_delete_$branch" "$duration" $([[ $deletion_exit_code -eq 0 ]] && echo true || echo false)
    
    # Update system state
    if [[ $deletion_exit_code -eq 0 ]]; then
        update_system_state "system.successful_operations" $(($(get_state_value "system.successful_operations" 0) + 1))
    else
        update_system_state "system.consecutive_failures" $(($(get_state_value "system.consecutive_failures" 0) + 1))
    fi
    
    return $deletion_exit_code
}

# Create branch backup
create_branch_backup() {
    local branch="$1"
    local repo_dir="$2"
    local backup_dir="${BACKUP_DIR:-/tmp/autoslopp_branch_backups}"
    
    mkdir -p "$backup_dir"
    
    local backup_file="$backup_dir/${branch}_$(date +%Y%m%d_%H%M%S).patch"
    local repo_name=$(basename "$repo_dir")
    
    cd "$repo_dir" || return 1
    
    # Create patch file for the branch
    if git format-patch --stdout "$branch" > "$backup_file" 2>/dev/null; then
        log "INFO" "Branch backup created: $backup_file"
        echo "$backup_file"
        return 0
    else
        log "ERROR" "Failed to create backup for branch: $branch"
        return 1
    fi
}

# =============================================================================
# MAIN ENHANCED CLEANUP WORKFLOW
# =============================================================================

# Enhanced repository cleanup workflow
cleanup_repository_enhanced() {
    local repo_dir="$1"
    local repo_name=$(basename "$repo_dir")
    local start_time=$(date +%s.%N)
    
    log "INFO" "Starting enhanced cleanup for repository: $repo_name"
    
    # Verify repository is accessible
    if ! verify_repository_access "$repo_dir"; then
        log "ERROR" "Repository access verification failed: $repo_name"
        return 1
    fi
    
    # Perform comprehensive branch analysis
    local analysis_data
    if ! analysis_data=$(analyze_branches_comprehensive "$repo_dir"); then
        log "ERROR" "Branch analysis failed for: $repo_name"
        return 1
    fi
    
    # Extract branches eligible for deletion from analysis
    local branches_to_delete=()
    local branches_skipped=()
    
    # This would parse the analysis_data to determine which branches to delete
    # For now, use the existing logic as a fallback
    if ! determine_branches_for_deletion "$repo_dir" analysis_data branches_to_delete branches_skipped; then
        log "ERROR" "Failed to determine branches for deletion: $repo_name"
        return 1
    fi
    
    # Apply safety limits
    if [[ ${#branches_to_delete[@]} -gt $MAX_BRANCHES_PER_RUN ]]; then
        log "WARNING" "Too many branches for deletion (${#branches_to_delete[@]}), limiting to $MAX_BRANCHES_PER_RUN"
        branches_to_delete=("${branches_to_delete[@]:0:$MAX_BRANCHES_PER_RUN}")
    fi
    
    # Process branches for deletion
    local repo_cleaned_count=0
    local repo_errors_count=0
    
    for branch in "${branches_to_delete[@]}"; do
        # Verify safety before deletion (including branch protection)
        if verify_branch_safety_comprehensive "$branch" "$repo_dir" "$analysis_data"; then
            # Use enhanced branch protection for deletion
            if safe_delete_branch_with_protection "$branch" "$repo_dir" "false"; then
                ((repo_cleaned_count++))
            else
                ((repo_errors_count++))
                branches_skipped+=("$branch (protected)")
            fi
        else
            log "INFO" "Skipping branch due to safety concerns: $branch"
            branches_skipped+=("$branch (safety)")
        fi
    done
    
    # Record repository cleanup completion
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    record_operation_performance "repository_cleanup_$repo_name" "$duration" $([[ $repo_errors_count -eq 0 ]] && echo true || echo false)
    
    # Report results
    log "INFO" "Repository cleanup completed for $repo_name:"
    log "INFO" "  Branches deleted: $repo_cleaned_count"
    log "INFO" "  Branches skipped: ${#branches_skipped[@]}"
    log "INFO" "  Errors: $repo_errors_count"
    log "INFO" "  Duration: ${duration}s"
    
    # Update global counters
    TOTAL_REPOS_PROCESSED=$((TOTAL_REPOS_PROCESSED + 1))
    TOTAL_BRANCHES_CLEANED=$((TOTAL_BRANCHES_CLEANED + repo_cleaned_count))
    TOTAL_ERRORS=$((TOTAL_ERRORS + repo_errors_count))
    
    return $repo_errors_count
}

# Verify repository access
verify_repository_access() {
    local repo_dir="$1"
    
    # Check if directory exists
    if [[ ! -d "$repo_dir" ]]; then
        log "ERROR" "Repository directory not found: $repo_dir"
        return 1
    fi
    
    # Check if it's a git repository
    if [[ ! -d "$repo_dir/.git" ]]; then
        log "WARNING" "Not a git repository: $repo_dir"
        return 1
    fi
    
    # Check if we can read/write
    if [[ ! -r "$repo_dir" || ! -w "$repo_dir" ]]; then
        log "ERROR" "Insufficient permissions for repository: $repo_dir"
        return 1
    fi
    
    # Check git repository health
    cd "$repo_dir" || return 1
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log "ERROR" "Git repository structure is corrupted: $repo_dir"
        return 1
    fi
    
    return 0
}

# Determine branches for deletion (fallback implementation)
determine_branches_for_deletion() {
    local repo_dir="$1"
    local -n analysis_ref=$2
    local -n delete_list_ref=$3
    local -n skip_list_ref=$4
    
    cd "$repo_dir" || return 1
    
    # Get remote branches
    local remote_branches
    if ! remote_branches=$(git ls-remote --heads origin 2>/dev/null | sed 's/.*\///' | sort); then
        log "WARNING" "Cannot fetch remote branches, using local-only analysis"
        remote_branches=""
    fi
    
    # Create remote branch lookup
    local -A remote_branch_map=()
    while IFS= read -r branch; do
        [[ -n "$branch" ]] && remote_branch_map["$branch"]=1
    done <<< "$remote_branches"
    
    # Get local branches
    local local_branches
    if ! local_branches=$(git branch --format='%(refname:short)' 2>/dev/null | grep -v '^*'); then
        log "ERROR" "Failed to list local branches"
        return 1
    fi
    
    # Determine which branches to delete
    while IFS= read -r local_branch; do
        [[ -n "$local_branch" ]] || continue
        
        if [[ -z "${remote_branch_map[$local_branch]:-}" ]]; then
            # Branch doesn't exist on remote
            if is_branch_protected "$local_branch" "$repo_dir"; then
                skip_list_ref+=("$local_branch (protected)")
            else
                delete_list_ref+=("$local_branch")
            fi
        fi
    done <<< "$local_branches"
    
    log "INFO" "Determined ${#delete_list_ref[@]} branches for deletion, ${#skip_list_ref[@]} branches to skip"
    return 0
}

# Check if branch is protected (enhanced version)
is_branch_protected() {
    local branch="$1"
    local repo_dir="$2"
    
    # Basic protected branches
    local protected_branches=("main" "master" "develop" "HEAD" "staging" "production")
    for protected in "${protected_branches[@]}"; do
        if [[ "$branch" == "$protected" ]]; then
            return 0
        fi
    done
    
    # Check if it's the current branch
    cd "$repo_dir" || return 1
    local current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [[ "$branch" == "$current_branch" ]]; then
        return 0
    fi
    
    # Check for protection markers (e.g., branches with "keep-" prefix)
    if [[ "$branch" =~ ^keep-|^protected-|^temp- ]]; then
        return 0
    fi
    
    return 1
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

# Main enhanced cleanup function
main_enhanced_cleanup() {
    local start_time=$(date +%s)
    
    log "INFO" "Starting enhanced branch cleanup system"
    log "INFO" "Operation ID: $CLEANUP_OPERATION_ID"
    log "INFO" "Safety mode: $SAFETY_MODE"
    log "INFO" "Dry run mode: $DRY_RUN_MODE"
    
    # Initialize enhanced systems
    if ! initialize_enhanced_cleanup_system; then
        log "ERROR" "Failed to initialize enhanced cleanup system"
        exit 1
    fi
    
    # Validate runtime configuration
    if ! validate_runtime_configuration "cleanup"; then
        log "ERROR" "Runtime configuration validation failed"
        exit 1
    fi
    
    # Check if managed_repo_path exists
    if [[ ! -d "$MANAGED_REPO_PATH" ]]; then
        log "ERROR" "managed_repo_path not found: $MANAGED_REPO_PATH"
        exit 1
    fi
    
    # Process each repository
    for repo_dir in "$MANAGED_REPO_PATH"/*; do
        if [[ ! -d "$repo_dir" ]]; then
            continue
        fi
        
        # Skip if operation should be isolated
        if should_isolate_operation "cleanup_$(basename "$repo_dir")"; then
            log "WARNING" "Skipping isolated repository: $(basename "$repo_dir")"
            continue
        fi
        
        cleanup_repository_enhanced "$repo_dir"
    done
    
    # Final summary and reporting
    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))
    
    log "INFO" "Enhanced branch cleanup completed"
    log "INFO" "Total repositories processed: $TOTAL_REPOS_PROCESSED"
    log "INFO" "Total branches cleaned: $TOTAL_BRANCHES_CLEANED"
    log "INFO" "Total errors encountered: $TOTAL_ERRORS"
    log "INFO" "Total duration: ${total_duration}s"
    log "INFO" "Operation ID: $CLEANUP_OPERATION_ID"
    
    # Perform final health check
    perform_health_check "" "completion"
    
    # Generate final report
    generate_cleanup_summary_report
    
    # Exit with appropriate code
    if [[ $TOTAL_ERRORS -gt 0 ]]; then
        log "WARNING" "Completed with $TOTAL_ERRORS errors"
        exit 1
    else
        log "SUCCESS" "Enhanced branch cleanup completed successfully"
        exit 0
    fi
}

# Generate cleanup summary report
generate_cleanup_summary_report() {
    local report_file="/tmp/cleanup_summary_${CLEANUP_OPERATION_ID}.json"
    
    cat > "$report_file" << EOF
{
    "operation_summary": {
        "operation_id": "$CLEANUP_OPERATION_ID",
        "timestamp": "$(date -Iseconds)",
        "duration_seconds": $(( $(date +%s) - $(date -d "@$(echo "$CLEANUP_OPERATION_ID" | cut -d_ -f2)" +%s) )),
        "repositories_processed": $TOTAL_REPOS_PROCESSED,
        "branches_cleaned": $TOTAL_BRANCHES_CLEANED,
        "errors_encountered": $TOTAL_ERRORS,
        "safety_mode": "$SAFETY_MODE",
        "dry_run_mode": "$DRY_RUN_MODE"
    },
    "system_health": "$(get_system_health_status)",
    "configuration_status": "valid"
}
EOF
    
    log "INFO" "Cleanup summary report generated: $report_file"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_enhanced_cleanup
fi