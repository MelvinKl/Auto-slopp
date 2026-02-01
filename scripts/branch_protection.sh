#!/bin/bash

# Enhanced Branch Protection Module
# Provides comprehensive branch protection with warnings and confirmation mechanisms
# Integrates with Auto-slopp system architecture and follows established patterns

# Set script name for logging identification
SCRIPT_NAME="branch-protection"

# Load utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# =============================================================================
# ENHANCED BRANCH PROTECTION CONFIGURATION
# =============================================================================

# Extract configuration values with defaults
BRANCH_PROTECTION_ENABLED="${branch_protection_enable_protection:-true}"
REQUIRE_CONFIRMATION="${branch_protection_require_confirmation:-true}"
SHOW_WARNINGS="${branch_protection_show_warnings:-true}"
PROTECTED_BRANCHES=("${branch_protection_protected_branches[@]}")
PROTECT_CURRENT_BRANCH="${branch_protection_protect_current_branch:-true}"
PROTECTION_PATTERNS=("${branch_protection_protection_patterns[@]}")
EXPLICIT_CONFIRMATION_BRANCHES=("${branch_protection_require_explicit_confirmation_for[@]}")

# =============================================================================
# CORE BRANCH PROTECTION FUNCTIONS
# =============================================================================

# Check if branch protection is enabled
is_branch_protection_enabled() {
    [[ "$BRANCH_PROTECTION_ENABLED" == "true" ]]
}

# Check if a branch name matches any protection pattern
matches_protection_pattern() {
    local branch="$1"
    
    for pattern in "${PROTECTION_PATTERNS[@]}"; do
        if [[ "$branch" == ${pattern//\*/} ]] || [[ "$branch" =~ ^${pattern//\*/.*}$ ]]; then
            return 0
        fi
    done
    
    return 1
}

# Check if a branch is in the protected branches list
is_in_protected_list() {
    local branch="$1"
    
    for protected in "${PROTECTED_BRANCHES[@]}"; do
        if [[ "$branch" == "$protected" ]]; then
            return 0
        fi
    done
    
    return 1
}

# Check if a branch requires explicit confirmation
requires_explicit_confirmation() {
    local branch="$1"
    
    for confirmation_branch in "${EXPLICIT_CONFIRMATION_BRANCHES[@]}"; do
        if [[ "$branch" == "$confirmation_branch" ]]; then
            return 0
        fi
    done
    
    return 1
}

# Check if the current branch (in a repository) should be protected
should_protect_current_branch() {
    [[ "$PROTECT_CURRENT_BRANCH" == "true" ]]
}

# =============================================================================
# ENHANCED PROTECTION VERIFICATION
# =============================================================================

# Comprehensive branch protection check
check_branch_protection() {
    local branch="$1"
    local repo_dir="$2"
    local operation="${3:-delete}"  # delete, modify, rename, etc.
    
    if ! is_branch_protection_enabled; then
        log "DEBUG" "Branch protection is disabled, allowing operation on: $branch"
        return 0
    fi
    
    log "DEBUG" "Checking branch protection for: $branch (operation: $operation)"
    
    # Check if it's the current branch and should be protected
    if should_protect_current_branch; then
        local current_branch
        if current_branch=$(get_current_branch_safe "$repo_dir"); then
            if [[ "$branch" == "$current_branch" ]]; then
                handle_protected_branch "$branch" "$repo_dir" "current branch"
                return $?
            fi
        fi
    fi
    
    # Check protected branches list
    if is_in_protected_list "$branch"; then
        handle_protected_branch "$branch" "$repo_dir" "protected branch"
        return $?
    fi
    
    # Check protection patterns
    if matches_protection_pattern "$branch"; then
        handle_protected_branch "$branch" "$repo_dir" "pattern-matched branch"
        return $?
    fi
    
    # Show warning if enabled
    if [[ "$SHOW_WARNINGS" == "true" ]]; then
        show_branch_operation_warning "$branch" "$repo_dir" "$operation"
    fi
    
    return 0
}

# Safely get current branch with error handling
get_current_branch_safe() {
    local repo_dir="$1"
    
    cd "$repo_dir" || {
        log "ERROR" "Cannot access repository directory: $repo_dir"
        return 1
    }
    
    git rev-parse --abbrev-ref HEAD 2>/dev/null || {
        log "ERROR" "Failed to determine current branch in: $(basename "$repo_dir")"
        return 1
    }
}

# Handle protected branch scenarios
handle_protected_branch() {
    local branch="$1"
    local repo_dir="$2"
    local protection_reason="$3"
    
    log "WARNING" "Protected branch detected: $branch (reason: $protection_reason)"
    
    # Check if explicit confirmation is required
    if requires_explicit_confirmation "$branch" && [[ "$REQUIRE_CONFIRMATION" == "true" ]]; then
        request_explicit_confirmation "$branch" "$repo_dir" "$protection_reason"
        return $?
    else
        # Show warning and deny operation
        show_protection_warning "$branch" "$repo_dir" "$protection_reason"
        return 1
    fi
}

# Request explicit confirmation from user
request_explicit_confirmation() {
    local branch="$1"
    local repo_dir="$2"
    local protection_reason="$3"
    local repo_name=$(basename "$repo_dir")
    
    echo
    echo "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo "${YELLOW} PROTECTED BRANCH CONFIRMATION REQUIRED${NC}"
    echo "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo
    echo "${RED}WARNING: You are attempting to delete a protected branch!${NC}"
    echo
    echo "Repository: ${BLUE}$repo_name${NC}"
    echo "Branch: ${RED}$branch${NC}"
    echo "Protection reason: $protection_reason"
    echo
    echo "${YELLOW}This operation may be dangerous and could cause issues with:${NC}"
    echo "  • Repository synchronization"
    echo "  • CI/CD pipelines"
    echo "  • Development workflows"
    echo "  • Team collaboration"
    echo
    echo "${YELLOW}Are you absolutely sure you want to proceed?${NC}"
    echo
    echo "Options:"
    echo "  ${RED}yes${NC}    - Proceed with branch deletion (DANGEROUS)"
    echo "  ${GREEN}no${NC}     - Cancel the operation (SAFE)"
    echo "  ${YELLOW}info${NC}  - Show detailed branch information"
    echo
    echo -n "Your choice [no]: "
    
    read -r user_input
    echo
    
    case "$user_input" in
        "yes"|"YES"|"y"|"Y")
            log "WARNING" "User explicitly confirmed deletion of protected branch: $branch"
            echo "${RED}Proceeding with deletion of protected branch: $branch${NC}"
            echo "${YELLOW}This operation was explicitly confirmed by the user.${NC}"
            echo
            return 0
            ;;
        "info"|"INFO"|"i"|"I")
            show_branch_detailed_info "$branch" "$repo_dir"
            request_explicit_confirmation "$branch" "$repo_dir" "$protection_reason"
            return $?
            ;;
        "no"|"NO"|"n"|"N"|"")
            log "INFO" "User cancelled deletion of protected branch: $branch"
            echo "${GREEN}Operation cancelled. Branch $branch remains safe.${NC}"
            echo
            return 1
            ;;
        *)
            echo "${RED}Invalid choice. Operation cancelled for safety.${NC}"
            echo
            return 1
            ;;
    esac
}

# Show protection warning
show_protection_warning() {
    local branch="$1"
    local repo_dir="$2"
    local protection_reason="$3"
    local repo_name=$(basename "$repo_dir")
    
    echo
    echo "${YELLOW}⚠️  BRANCH PROTECTION WARNING${NC}"
    echo "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo
    echo "${RED}Operation blocked:${NC} Cannot delete protected branch"
    echo
    echo "Repository: ${BLUE}$repo_name${NC}"
    echo "Branch: ${RED}$branch${NC}"
    echo "Protection reason: $protection_reason"
    echo
    echo "${YELLOW}This branch is protected for safety reasons. To delete it:${NC}"
    echo "  1. Enable confirmation in config: require_confirmation: true"
    echo "  2. Run the operation again and confirm when prompted"
    echo "  3. Or remove it from the protected branches list in config"
    echo
    echo "Operation cancelled for safety."
    echo
}

# Show branch operation warning
show_branch_operation_warning() {
    local branch="$1"
    local repo_dir="$2"
    local operation="$3"
    local repo_name=$(basename "$repo_dir")
    
    echo
    echo "${YELLOW}ℹ️  BRANCH OPERATION WARNING${NC}"
    echo "Repository: ${BLUE}$repo_name${NC}"
    echo "Branch: $branch"
    echo "Operation: $operation"
    echo
    echo "${YELLOW}Please verify this is the correct branch before proceeding.${NC}"
    echo
}

# Show detailed branch information
show_branch_detailed_info() {
    local branch="$1"
    local repo_dir="$2"
    
    cd "$repo_dir" || return 1
    
    echo
    echo "${BLUE}📋 DETAILED BRANCH INFORMATION${NC}"
    echo "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo
    
    # Branch basic info
    echo "Branch name: ${YELLOW}$branch${NC}"
    
    # Last commit info
    local last_commit
    if last_commit=$(git log -1 --format="%h | %an | %ad | %s" --date=short "$branch" 2>/dev/null); then
        echo "Last commit: $last_commit"
    else
        echo "Last commit: ${RED}Unable to retrieve${NC}"
    fi
    
    # Branch age
    local commit_timestamp
    if commit_timestamp=$(git log -1 --format=%ct "$branch" 2>/dev/null); then
        local age_days=$((( $(date +%s) - commit_timestamp ) / 86400))
        echo "Branch age: $age_days days"
    fi
    
    # Check if merged
    if git merge-base --is-ancestor "$branch" "main" 2>/dev/null || \
       git merge-base --is-ancestor "$branch" "master" 2>/dev/null; then
        echo "Merge status: ${GREEN}Merged${NC}"
    else
        echo "Merge status: ${RED}Not merged${NC}"
    fi
    
    # Check for unmerged commits
    local unmerged_count
    if unmerged_count=$(git log "main..$branch" --oneline 2>/dev/null | wc -l); then
        if [[ $unmerged_count -gt 0 ]]; then
            echo "Unmerged commits: ${RED}$unmerged_count${NC}"
        else
            echo "Unmerged commits: ${GREEN}None${NC}"
        fi
    fi
    
    # Check if other branches depend on this
    local dependent_branches
    if dependent_branches=$(git branch --contains "$branch" --format='%(refname:short)' 2>/dev/null | grep -v "^$branch$" | head -5); then
        if [[ -n "$dependent_branches" ]]; then
            echo "Dependent branches: ${YELLOW}$dependent_branches${NC}"
        else
            echo "Dependent branches: ${GREEN}None${NC}"
        fi
    fi
    
    echo
}

# =============================================================================
# SAFE BRANCH DELETION WITH PROTECTION
# =============================================================================

# Enhanced safe branch deletion function
safe_delete_branch_with_protection() {
    local branch="$1"
    local repo_dir="$2"
    local force_delete="${3:-false}"
    
    log "INFO" "Attempting to delete branch: $branch"
    
    # Check branch protection first
    if ! check_branch_protection "$branch" "$repo_dir" "delete"; then
        log "WARNING" "Branch deletion blocked by protection: $branch"
        return 1
    fi
    
    cd "$repo_dir" || return 1
    
    # Attempt deletion
    local deletion_output
    local deletion_exit_code
    
    if [[ "$force_delete" == "true" ]]; then
        log "INFO" "Attempting force delete of branch: $branch"
        if deletion_output=$(git branch -D "$branch" 2>&1); then
            deletion_exit_code=0
            log "SUCCESS" "Successfully force deleted branch: $branch"
        else
            deletion_exit_code=$?
            log "ERROR" "Failed to force delete branch: $branch"
            log "ERROR" "Deletion output: $deletion_output"
        fi
    else
        log "INFO" "Attempting regular delete of branch: $branch"
        if deletion_output=$(git branch -d "$branch" 2>&1); then
            deletion_exit_code=0
            log "SUCCESS" "Successfully deleted branch: $branch"
        else
            deletion_exit_code=$?
            log "WARNING" "Regular delete failed for $branch, trying force delete"
            
            # Try force delete as fallback
            if deletion_output=$(git branch -D "$branch" 2>&1); then
                deletion_exit_code=0
                log "SUCCESS" "Successfully force deleted branch: $branch"
            else
                log "ERROR" "Failed to delete branch: $branch"
                log "ERROR" "Deletion output: $deletion_output"
            fi
        fi
    fi
    
    return $deletion_exit_code
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Get all protected branches for a repository
get_protected_branches_for_repo() {
    local repo_dir="$1"
    local protected_branches=()
    
    # Add static protected branches
    for protected in "${PROTECTED_BRANCHES[@]}"; do
        protected_branches+=("$protected")
    done
    
    # Add current branch if protection is enabled
    if should_protect_current_branch; then
        local current_branch
        if current_branch=$(get_current_branch_safe "$repo_dir"); then
            protected_branches+=("$current_branch")
        fi
    fi
    
    # Add pattern-matched branches
    cd "$repo_dir" || return 1
    local local_branches
    if local_branches=$(git branch --format='%(refname:short)' 2>/dev/null); then
        while IFS= read -r branch; do
            [[ -n "$branch" ]] || continue
            if matches_protection_pattern "$branch"; then
                protected_branches+=("$branch")
            fi
        done <<< "$local_branches"
    fi
    
    # Return unique branches
    printf '%s\n' "${protected_branches[@]}" | sort -u
}

# Validate branch protection configuration
validate_branch_protection_config() {
    local errors=()
    
    if [[ "$BRANCH_PROTECTION_ENABLED" != "true" && "$BRANCH_PROTECTION_ENABLED" != "false" ]]; then
        errors+=("Invalid enable_protection value: $BRANCH_PROTECTION_ENABLED")
    fi
    
    if [[ "$REQUIRE_CONFIRMATION" != "true" && "$REQUIRE_CONFIRMATION" != "false" ]]; then
        errors+=("Invalid require_confirmation value: $REQUIRE_CONFIRMATION")
    fi
    
    if [[ "$SHOW_WARNINGS" != "true" && "$SHOW_WARNINGS" != "false" ]]; then
        errors+=("Invalid show_warnings value: $SHOW_WARNINGS")
    fi
    
    if [[ ${#errors[@]} -gt 0 ]]; then
        log "ERROR" "Branch protection configuration validation failed:"
        for error in "${errors[@]}"; do
            log "ERROR" "  - $error"
        done
        return 1
    fi
    
    log "DEBUG" "Branch protection configuration validated successfully"
    return 0
}

# Initialize branch protection system
initialize_branch_protection() {
    log "INFO" "Initializing enhanced branch protection system"
    
    # Validate configuration
    if ! validate_branch_protection_config; then
        log "ERROR" "Branch protection configuration validation failed"
        return 1
    fi
    
    # Log configuration status
    log "INFO" "Branch protection status: $BRANCH_PROTECTION_ENABLED"
    log "INFO" "Confirmation required: $REQUIRE_CONFIRMATION"
    log "INFO" "Warnings enabled: $SHOW_WARNINGS"
    log "INFO" "Protected branches: ${#PROTECTED_BRANCHES[@]} static, ${#PROTECTION_PATTERNS[@]} patterns"
    log "INFO" "Explicit confirmation branches: ${#EXPLICIT_CONFIRMATION_BRANCHES[@]}"
    
    log "SUCCESS" "Enhanced branch protection system initialized"
    return 0
}

# =============================================================================
# MAIN EXECUTION (for testing)
# =============================================================================

# Main function for testing branch protection
main_branch_protection() {
    local repo_dir="${1:-$(pwd)}"
    local branch_to_test="${2:-}"
    
    if ! initialize_branch_protection; then
        echo "Failed to initialize branch protection system"
        exit 1
    fi
    
    if [[ -n "$branch_to_test" ]]; then
        echo "Testing protection for branch: $branch_to_test"
        if check_branch_protection "$branch_to_test" "$repo_dir" "test"; then
            echo "Result: Branch is NOT protected"
        else
            echo "Result: Branch IS protected"
        fi
    else
        echo "Protected branches in repository:"
        get_protected_branches_for_repo "$repo_dir"
    fi
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_branch_protection "$@"
fi