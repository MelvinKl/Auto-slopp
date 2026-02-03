#!/bin/bash

# Branch Analysis Core Logic Module
# Implements core functions for listing and comparing local vs remote branches
# Handles edge cases and provides efficient git operations with proper error handling

# Set script name for logging identification
SCRIPT_NAME="branch-analysis-core"

# =============================================================================
# CORE BRANCH LISTING FUNCTIONS
# =============================================================================

# Function to list remote branches with comprehensive error handling
# Args: $1 - repository directory
# Returns: List of remote branches, one per line
# Exit codes: 0=success, 1=network error, 2=repository error, 3=permission error
list_remote_branches() {
    local repo_dir="$1"
    local operation_start=$(date +%s.%N)
    
    log "DEBUG" "Starting remote branch listing for: $(basename "$repo_dir")"
    
    # Validate repository directory
    if ! validate_repository_directory "$repo_dir"; then
        log "ERROR" "Invalid repository directory: $repo_dir"
        record_operation_performance "list_remote_branches" "$(calculate_duration "$operation_start")" false
        return 2
    fi
    
    # Change to repository directory with error handling
    if ! cd "$repo_dir"; then
        log "ERROR" "Cannot access repository directory: $repo_dir"
        record_operation_performance "list_remote_branches" "$(calculate_duration "$operation_start")" false
        return 2
    fi
    
    # Check if it's a git repository
    if ! validate_git_repository; then
        log "ERROR" "Not a valid git repository: $repo_dir"
        record_operation_performance "list_remote_branches" "$(calculate_duration "$operation_start")" false
        return 2
    fi
    
    # Check network connectivity first
    if ! check_remote_connectivity; then
        log "WARNING" "Remote unreachable, attempting offline analysis"
        record_operation_performance "list_remote_branches" "$(calculate_duration "$operation_start")" false
        return 1
    fi
    
    # Fetch remote branch information with timeout
    local remote_branches
    local git_timeout="${GIT_TIMEOUT:-30}"
    
    log "DEBUG" "Fetching remote branches (timeout: ${git_timeout}s)"
    
    # Use timeout command to prevent hanging
    if remote_branches=$(timeout "$git_timeout" git ls-remote --heads origin 2>/dev/null); then
        # Extract branch names from full references
        local branch_list
        if branch_list=$(echo "$remote_branches" | sed 's/.*\///' | sort -u); then
            if [[ -n "$branch_list" ]]; then
                log "DEBUG" "Successfully listed $(echo "$branch_list" | wc -l) remote branches"
                echo "$branch_list"
                record_operation_performance "list_remote_branches" "$(calculate_duration "$operation_start")" true
                return 0
            else
                log "INFO" "No remote branches found"
                echo ""
                record_operation_performance "list_remote_branches" "$(calculate_duration "$operation_start")" true
                return 0
            fi
        else
            log "ERROR" "Failed to process remote branch data"
            record_operation_performance "list_remote_branches" "$(calculate_duration "$operation_start")" false
            return 2
        fi
    else
        local exit_code=$?
        if [[ $exit_code -eq 124 ]]; then
            log "ERROR" "Remote branch listing timed out after ${git_timeout}s"
        else
            log "ERROR" "Failed to list remote branches (exit code: $exit_code)"
        fi
        record_operation_performance "list_remote_branches" "$(calculate_duration "$operation_start")" false
        return 1
    fi
}

# Function to list local branches with comprehensive error handling
# Args: $1 - repository directory
# Returns: List of local branches, one per line (excluding current branch)
# Exit codes: 0=success, 1=warning, 2=error
list_local_branches() {
    local repo_dir="$1"
    local operation_start=$(date +%s.%N)
    
    log "DEBUG" "Starting local branch listing for: $(basename "$repo_dir")"
    
    # Validate repository directory
    if ! validate_repository_directory "$repo_dir"; then
        log "ERROR" "Invalid repository directory: $repo_dir"
        record_operation_performance "list_local_branches" "$(calculate_duration "$operation_start")" false
        return 2
    fi
    
    # Change to repository directory
    if ! cd "$repo_dir"; then
        log "ERROR" "Cannot access repository directory: $repo_dir"
        record_operation_performance "list_local_branches" "$(calculate_duration "$operation_start")" false
        return 2
    fi
    
    # Check for detached HEAD state
    local current_branch
    if current_branch=$(get_current_branch_safe); then
        log "DEBUG" "Current branch: $current_branch"
        
        if [[ "$current_branch" == "HEAD" ]]; then
            log "WARNING" "Repository is in detached HEAD state"
            # Continue processing but note the warning
        fi
    else
        log "ERROR" "Failed to determine current branch"
        record_operation_performance "list_local_branches" "$(calculate_duration "$operation_start")" false
        return 2
    fi
    
    # Get local branches using git command with detailed format
    local local_branches_info
    if local_branches_info=$(git branch --format='%(refname:short)' 2>/dev/null); then
        # Process and filter branches
        local branch_list
        if branch_list=$(echo "$local_branches_info" | grep -v '^$' | grep -v "^$current_branch$" | sort); then
            local branch_count=$(echo "$branch_list" | wc -l)
            log "DEBUG" "Successfully listed $branch_count local branches (excluding current: $current_branch)"
            echo "$branch_list"
            record_operation_performance "list_local_branches" "$(calculate_duration "$operation_start")" true
            return 0
        else
            log "WARNING" "Failed to filter local branch list"
            record_operation_performance "list_local_branches" "$(calculate_duration "$operation_start")" false
            return 1
        fi
    else
        log "ERROR" "Failed to execute git branch command"
        record_operation_performance "list_local_branches" "$(calculate_duration "$operation_start")" false
        return 2
    fi
}

# Function to compare local and remote branches and identify differences
# Args: $1 - repository directory
# Returns: JSON object with analysis results
# Exit codes: 0=success, 1=partial success, 2=error
compare_branches() {
    local repo_dir="$1"
    local repo_name=$(basename "$repo_dir")
    local operation_start=$(date +%s.%N)
    
    log "INFO" "Starting branch comparison for: $repo_name"
    
    # Initialize analysis results
    local analysis_result
    analysis_result=$(cat << EOF
{
    "repository": "$repo_name",
    "timestamp": "$(date -Iseconds)",
    "analysis": {
        "local_branches": [],
        "remote_branches": [],
        "local_only_branches": [],
        "remote_only_branches": [],
        "common_branches": [],
        "status": "in_progress"
    }
}
EOF
)
    
    # Get local branches
    local local_branches
    if local_branches=$(list_local_branches "$repo_dir"); then
        local local_count=$(echo "$local_branches" | wc -l)
        log "DEBUG" "Found $local_count local branches"
        
        # Add to analysis result
        if [[ -n "$local_branches" ]]; then
            analysis_result=$(echo "$analysis_result" | jq --arg branches "$local_branches" '.analysis.local_branches = ($branches | split("\n") | map(select(length > 0)))')
        else
            analysis_result=$(echo "$analysis_result" | jq '.analysis.local_branches = []')
        fi
    else
        log "WARNING" "Failed to get local branches, continuing with partial analysis"
        analysis_result=$(echo "$analysis_result" | jq '.analysis.status = "partial"')
    fi
    
    # Get remote branches
    local remote_branches
    local remote_result
    if remote_result=$(list_remote_branches "$repo_dir"); then
        local remote_code=$?
        remote_branches="$remote_result"
        
        if [[ $remote_code -eq 0 ]]; then
            local remote_count=$(echo "$remote_branches" | wc -l)
            log "DEBUG" "Found $remote_count remote branches"
            
            # Add to analysis result
            if [[ -n "$remote_branches" ]]; then
                analysis_result=$(echo "$analysis_result" | jq --arg branches "$remote_branches" '.analysis.remote_branches = ($branches | split("\n") | map(select(length > 0)))')
            else
                analysis_result=$(echo "$analysis_result" | jq '.analysis.remote_branches = []')
            fi
        else
            log "WARNING" "Remote branches unavailable (network/connectivity issue)"
            analysis_result=$(echo "$analysis_result" | jq '.analysis.status = "offline"')
            # Continue with local-only analysis
        fi
    else
        log "ERROR" "Failed to get remote branches"
        analysis_result=$(echo "$analysis_result" | jq '.analysis.status = "error"')
        record_operation_performance "compare_branches" "$(calculate_duration "$operation_start")" false
        return 2
    fi
    
    # Perform comparison if we have both lists
    if [[ -n "$local_branches" ]] && [[ -n "$remote_branches" ]]; then
        log "DEBUG" "Performing branch comparison"
        
        # Create arrays for efficient comparison
        local -A local_branch_map
        local -A remote_branch_map
        
        # Populate local branch map
        while IFS= read -r branch; do
            [[ -n "$branch" ]] && local_branch_map["$branch"]=1
        done <<< "$local_branches"
        
        # Populate remote branch map
        while IFS= read -r branch; do
            [[ -n "$branch" ]] && remote_branch_map["$branch"]=1
        done <<< "$remote_branches"
        
        # Find local-only branches
        local local_only=()
        for branch in "${!local_branch_map[@]}"; do
            if [[ -z "${remote_branch_map[$branch]:-}" ]]; then
                local_only+=("$branch")
            fi
        done
        
        # Find remote-only branches
        local remote_only=()
        for branch in "${!remote_branch_map[@]}"; do
            if [[ -z "${local_branch_map[$branch]:-}" ]]; then
                remote_only+=("$branch")
            fi
        done
        
        # Find common branches
        local common=()
        for branch in "${!local_branch_map[@]}"; do
            if [[ -n "${remote_branch_map[$branch]:-}" ]]; then
                common+=("$branch")
            fi
        done
        
        # Update analysis results (handle empty arrays properly)
        local local_only_json="[]"
        local remote_only_json="[]"
        local common_json="[]"
        
        if [[ ${#local_only[@]} -gt 0 ]]; then
            local_only_json=$(printf '%s\n' "${local_only[@]}" | jq -R . | jq -s .)
        fi
        
        if [[ ${#remote_only[@]} -gt 0 ]]; then
            remote_only_json=$(printf '%s\n' "${remote_only[@]}" | jq -R . | jq -s .)
        fi
        
        if [[ ${#common[@]} -gt 0 ]]; then
            common_json=$(printf '%s\n' "${common[@]}" | jq -R . | jq -s .)
        fi
        
        analysis_result=$(echo "$analysis_result" | jq --argjson branches "$local_only_json" '.analysis.local_only_branches = $branches')
        analysis_result=$(echo "$analysis_result" | jq --argjson branches "$remote_only_json" '.analysis.remote_only_branches = $branches')
        analysis_result=$(echo "$analysis_result" | jq --argjson branches "$common_json" '.analysis.common_branches = $branches')
        
        local local_only_count=${#local_only[@]}
        local remote_only_count=${#remote_only[@]}
        local common_count=${#common[@]}
        
        log "INFO" "Branch comparison completed for $repo_name:"
        log "INFO" "  Local-only branches: $local_only_count"
        log "INFO" "  Remote-only branches: $remote_only_count"
        log "INFO" "  Common branches: $common_count"
        
        analysis_result=$(echo "$analysis_result" | jq '.analysis.status = "complete"')
    else
        log "WARNING" "Incomplete branch data, analysis limited"
        if [[ "$analysis_result" == *"offline"* ]]; then
            analysis_result=$(echo "$analysis_result" | jq '.analysis.status = "offline_complete"')
        else
            analysis_result=$(echo "$analysis_result" | jq '.analysis.status = "incomplete"')
        fi
    fi
    
    # Output final analysis to stdout, logs to stderr
    echo "$analysis_result" >&1
    
    local final_status=$(echo "$analysis_result" | jq -r '.analysis.status')
    if [[ "$final_status" == "complete" ]] || [[ "$final_status" == "offline_complete" ]]; then
        record_operation_performance "compare_branches" "$(calculate_duration "$operation_start")" true
        return 0
    elif [[ "$final_status" == "partial" ]] || [[ "$final_status" == "incomplete" ]]; then
        record_operation_performance "compare_branches" "$(calculate_duration "$operation_start")" true
        return 1
    else
        record_operation_performance "compare_branches" "$(calculate_duration "$operation_start")" false
        return 2
    fi
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Validate repository directory exists and is accessible
validate_repository_directory() {
    local repo_dir="$1"
    
    # Check if directory exists
    if [[ ! -d "$repo_dir" ]]; then
        log "ERROR" "Repository directory does not exist: $repo_dir"
        return 1
    fi
    
    # Check if directory is readable
    if [[ ! -r "$repo_dir" ]]; then
        log "ERROR" "Repository directory is not readable: $repo_dir"
        return 1
    fi
    
    return 0
}

# Validate that current directory is a git repository
validate_git_repository() {
    # Check for .git directory or file
    if [[ ! -d ".git" ]] && [[ ! -f ".git" ]]; then
        log "ERROR" "Current directory is not a git repository"
        return 1
    fi
    
    # Check git repository integrity
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log "ERROR" "Git repository structure is corrupted"
        return 1
    fi
    
    return 0
}

# Check remote connectivity with multiple methods
check_remote_connectivity() {
    log "DEBUG" "Checking remote connectivity"
    
    # Method 1: Check if remote is configured
    if ! git remote get-url origin >/dev/null 2>&1; then
        log "WARNING" "No 'origin' remote configured"
        return 1
    fi
    
    # Method 2: Quick connectivity check
    if git ls-remote --heads origin --quiet 2>/dev/null; then
        log "DEBUG" "Remote connectivity confirmed"
        return 0
    else
        log "DEBUG" "Remote connectivity check failed"
        return 1
    fi
}

# Safely get current branch name with detached HEAD handling
get_current_branch_safe() {
    local current_branch
    if current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null); then
        echo "$current_branch"
        return 0
    else
        log "ERROR" "Failed to determine current branch"
        return 1
    fi
}

# Calculate operation duration
calculate_duration() {
    local start_time="$1"
    local end_time=$(date +%s.%N)
    
    # Use bc if available, otherwise fallback to integer math
    if command -v bc >/dev/null 2>&1; then
        echo "$end_time - $start_time" | bc -l
    else
        echo "${end_time%.*} - ${start_time%.*}" | bc 2>/dev/null || echo "0"
    fi
}

# Record operation performance (placeholder - would integrate with system)
record_operation_performance() {
    local operation="$1"
    local duration="$2"
    local success="$3"
    
    log "DEBUG" "Performance: $operation completed in ${duration}s (success: $success)"
    
    # In a full implementation, this would update system state
    # For now, just log the performance metric
}

# =============================================================================
# EDGE CASE HANDLING FUNCTIONS
# =============================================================================

# Handle detached HEAD state gracefully
handle_detached_head() {
    local repo_dir="$1"
    
    cd "$repo_dir" || return 1
    
    local current_branch
    if current_branch=$(get_current_branch_safe); then
        if [[ "$current_branch" == "HEAD" ]]; then
            log "WARNING" "Repository is in detached HEAD state"
            log "INFO" "Current commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
            
            # Attempt to find a suitable branch to checkout
            local main_branch
            if main_branch=$(find_main_branch); then
                log "INFO" "Suggested action: checkout '$main_branch' to leave detached HEAD state"
                return 0
            else
                log "WARNING" "Cannot determine main branch for recovery"
                return 1
            fi
        fi
    fi
    
    return 0
}

# Find the main branch (main/master/develop)
find_main_branch() {
    local branches=("main" "master" "develop")
    
    for branch in "${branches[@]}"; do
        if git rev-parse --verify "$branch" >/dev/null 2>&1; then
            echo "$branch"
            return 0
        fi
    done
    
    return 1
}

# Handle network connectivity issues
handle_network_issues() {
    local repo_dir="$1"
    local max_retries="${MAX_RETRIES:-3}"
    local retry_delay="${RETRY_DELAY:-5}"
    
    log "INFO" "Attempting to handle network connectivity issues"
    
    for ((i=1; i<=max_retries; i++)); do
        log "INFO" "Network attempt $i of $max_retries"
        
        if check_remote_connectivity; then
            log "SUCCESS" "Network connectivity restored"
            return 0
        fi
        
        if [[ $i -lt $max_retries ]]; then
            log "INFO" "Waiting ${retry_delay}s before retry..."
            sleep "$retry_delay"
        fi
    done
    
    log "WARNING" "Network connectivity could not be restored after $max_retries attempts"
    return 1
}

# =============================================================================
# MAIN DEMONSTRATION FUNCTION
# =============================================================================

# Demonstrate the core functionality (for testing)
demonstrate_core_logic() {
    local repo_dir="${1:-$PWD}"
    
    log "INFO" "Demonstrating branch analysis core logic"
    log "INFO" "Repository: $(basename "$repo_dir")"
    log "INFO" "Repository directory: $repo_dir"
    
    echo "========================================"
    echo "REMOTE BRANCHES:"
    echo "========================================"
    if remote_branches=$(list_remote_branches "$repo_dir"); then
        echo "$remote_branches" | nl
    else
        echo "Failed to list remote branches"
    fi
    
    echo ""
    echo "========================================"
    echo "LOCAL BRANCHES:"
    echo "========================================"
    if local_branches=$(list_local_branches "$repo_dir"); then
        echo "$local_branches" | nl
    else
        echo "Failed to list local branches"
    fi
    
    echo ""
    echo "========================================"
    echo "BRANCH ANALYSIS SUMMARY:"
    echo "========================================"
    
    # Simple demonstration without complex JSON parsing
    local remote_branches local_branches
    if remote_branches=$(list_remote_branches "$repo_dir" 2>/dev/null); then
        echo "Remote branches found:"
        echo "$remote_branches" | sed 's/^/  - /'
    else
        echo "Could not fetch remote branches"
    fi
    
    echo ""
    if local_branches=$(list_local_branches "$repo_dir" 2>/dev/null); then
        echo "Local branches found:"
        echo "$local_branches" | sed 's/^/  - /'
    else
        echo "Could not list local branches"
    fi
    
    echo ""
    if [[ -n "$remote_branches" ]] && [[ -n "$local_branches" ]]; then
        echo "Branches that exist locally but not on remote:"
        while IFS= read -r local_branch; do
            if [[ -n "$local_branch" ]] && ! echo "$remote_branches" | grep -q "^$local_branch$"; then
                echo "  - $local_branch (candidate for cleanup)"
            fi
        done <<< "$local_branches"
        
        echo ""
        echo "Branches that exist on remote but not locally:"
        while IFS= read -r remote_branch; do
            if [[ -n "$remote_branch" ]] && ! echo "$local_branches" | grep -q "^$remote_branch$"; then
                echo "  - $remote_branch (consider pulling)"
            fi
        done <<< "$remote_branches"
    fi
}

# Execute demonstration if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Load utils for logging if available
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
    
    if [[ -f "$SCRIPT_DIR/utils.sh" ]]; then
        source "$SCRIPT_DIR/utils.sh"
        setup_error_handling 2>/dev/null || true
    else
        # Basic logging fallback
        log() {
            local level="$1"
            shift
            echo "[$level] $*" >&2
        }
    fi
    
    # Check if first argument is "demonstrate_core_logic"
    if [[ "${1:-}" == "demonstrate_core_logic" ]]; then
        # Pass the second argument as repository directory
        demonstrate_core_logic "${2:-$PWD}"
    else
        # Otherwise, treat first argument as repository directory
        demonstrate_core_logic "${1:-$PWD}"
    fi
fi