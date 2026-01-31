#!/bin/bash

# Repository Discovery Script - Core discovery functionality for cleanup operations
# Identifies and validates repositories for cleanup processing
# Provides repository filtering, validation, and metadata collection
# Follows Auto-slopp patterns and integrates with existing infrastructure

# Set script name for logging identification
SCRIPT_NAME="repository-discovery"

# Load utilities and configuration first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# Set up error handling
setup_error_handling

log "INFO" "Starting repository discovery script"
log "INFO" "Using managed_repo_path: $MANAGED_REPO_PATH"

# Validate required environment variables
validate_env_vars MANAGED_REPO_PATH

# Check if managed_repo_path exists and is accessible
check_directory "$MANAGED_REPO_PATH" "managed_repo_path"

# Global arrays to store discovered repositories
declare -a DISCOVERED_REPOS=()
declare -a SKIPPED_REPOS=()
declare -a ERROR_REPOS=()

# Function to validate if a directory is a proper git repository
validate_git_repository() {
    local repo_dir="$1"
    local repo_name=$(basename "$repo_dir")
    
    log "DEBUG" "Validating repository: $repo_name"
    
    # Check if it's a directory
    if [ ! -d "$repo_dir" ]; then
        log "DEBUG" "Not a directory: $repo_name"
        return 1
    fi
    
    # Check if it's a git repository
    if [ ! -d "$repo_dir/.git" ]; then
        log "DEBUG" "Not a git repository: $repo_name"
        return 1
    fi
    
    # Verify git repository integrity
    cd "$repo_dir" || return 1
    
    # Check if git repository is accessible
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log "WARNING" "Git repository not accessible: $repo_name"
        return 1
    fi
    
    # Check for remote origin (optional but recommended)
    if ! git remote get-url origin >/dev/null 2>&1; then
        log "DEBUG" "No remote origin found: $repo_name (this is OK for local repos)"
    fi
    
    log "DEBUG" "Repository validation passed: $repo_name"
    return 0
}

# Function to get repository metadata
get_repository_metadata() {
    local repo_dir="$1"
    local repo_name=$(basename "$repo_dir")
    
    cd "$repo_dir" || return 1
    
    # Get basic git information
    local current_branch remote_url last_commit_date repo_size
    
    current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    remote_url=$(git remote get-url origin 2>/dev/null || echo "local")
    last_commit_date=$(git log -1 --format="%ci" 2>/dev/null || echo "unknown")
    
    # Get repository size (approximate)
    repo_size=$(du -sh "$repo_dir" 2>/dev/null | cut -f1 || echo "unknown")
    
    # Get active branches count
    local branch_count
    branch_count=$(git branch --format='%(refname:short)' 2>/dev/null | wc -l || echo "0")
    
    # Get uncommitted changes status
    local status_clean
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        status_clean="true"
    else
        status_clean="false"
    fi
    
    # Create JSON object using printf for better control
    printf '{"name":"%s","path":"%s","current_branch":"%s","remote_url":"%s","last_commit_date":"%s","size":"%s","branch_count":"%s","status_clean":%s,"discovery_timestamp":"%s"}' \
        "$repo_name" \
        "$repo_dir" \
        "$current_branch" \
        "$remote_url" \
        "$last_commit_date" \
        "$repo_size" \
        "$branch_count" \
        "$status_clean" \
        "$(date -Iseconds)"
}

# Function to check if repository should be excluded based on configuration
should_exclude_repository() {
    local repo_name="$1"
    
    # Default exclusion patterns (can be made configurable)
    local exclude_patterns=(
        ".*-backup"
        ".*-old"
        ".*-archive"
        ".*-tmp"
        "test-repo.*"
        ".*-test"
    )
    
    # Check against exclusion patterns
    for pattern in "${exclude_patterns[@]}"; do
        if [[ "$repo_name" =~ $pattern ]]; then
            log "DEBUG" "Repository '$repo_name' matches exclusion pattern '$pattern'"
            return 0
        fi
    done
    
    return 1
}

# Function to discover a single repository
discover_repository() {
    local repo_dir="$1"
    local repo_name=$(basename "$repo_dir")
    
    log "DEBUG" "Discovering repository: $repo_name"
    
    # Check if repository should be excluded
    if should_exclude_repository "$repo_name"; then
        log "INFO" "Excluding repository: $repo_name (matches exclusion pattern)"
        SKIPPED_REPOS+=("$repo_name (excluded)")
        return 0
    fi
    
    # Validate repository
    if validate_git_repository "$repo_dir"; then
        local metadata
        metadata=$(get_repository_metadata "$repo_dir")
        
        DISCOVERED_REPOS+=("$repo_dir:$metadata")
        log "SUCCESS" "Discovered valid repository: $repo_name"
        
        # Log key metadata
        log "DEBUG" "Repository metadata for $repo_name:"
        log "DEBUG" "$(echo "$metadata" | jq -r '. | to_entries[] | "  \(.key): \(.value)"' 2>/dev/null || echo "$metadata")"
        
        return 0
    else
        log "WARNING" "Repository validation failed: $repo_name"
        ERROR_REPOS+=("$repo_name (validation failed)")
        return 1
    fi
}

# Function to discover all repositories
discover_all_repositories() {
    log "INFO" "Starting repository discovery in: $MANAGED_REPO_PATH"
    
    # Reset arrays
    DISCOVERED_REPOS=()
    SKIPPED_REPOS=()
    ERROR_REPOS=()
    
    # Process each subdirectory in managed_repo_path
    local repo_count=0
    for repo_dir in "$MANAGED_REPO_PATH"/*; do
        [ ! -d "$repo_dir" ] && continue
        
        repo_count=$((repo_count + 1))
        discover_repository "$repo_dir"
    done
    
    log "INFO" "Repository discovery completed"
    log "INFO" "Total directories processed: $repo_count"
    log "INFO" "Valid repositories discovered: ${#DISCOVERED_REPOS[@]}"
    log "INFO" "Repositories skipped: ${#SKIPPED_REPOS[@]}"
    log "INFO" "Repositories with errors: ${#ERROR_REPOS[@]}"
}

# Function to generate discovery report
generate_discovery_report() {
    local report_file="${MANAGED_REPO_PATH}/.discovery-report-$(date +%Y%m%d_%H%M%S).json"
    
    log "INFO" "Generating discovery report: $report_file"
    
    # Calculate counts
    local discovered_count=${#DISCOVERED_REPOS[@]}
    local skipped_count=${#SKIPPED_REPOS[@]}
    local error_count=${#ERROR_REPOS[@]}
    local total_count=$((discovered_count + skipped_count + error_count))
    
    # Create simple but valid JSON using printf
    printf '{\n' > "$report_file"
    printf '  "discovery_timestamp": "%s",\n' "$(date -Iseconds)" >> "$report_file"
    printf '  "managed_repo_path": "%s",\n' "$MANAGED_REPO_PATH" >> "$report_file"
    printf '  "summary": {\n' >> "$report_file"
    printf '    "total_directories_processed": %d,\n' $total_count >> "$report_file"
    printf '    "valid_repositories": %d,\n' $discovered_count >> "$report_file"
    printf '    "skipped_repositories": %d,\n' $skipped_count >> "$report_file"
    printf '    "error_repositories": %d\n' $error_count >> "$report_file"
    printf '  },\n' >> "$report_file"
    printf '  "repositories": [\n' >> "$report_file"
    
    # Add discovered repositories
    if [ ${#DISCOVERED_REPOS[@]} -gt 0 ]; then
        for i in "${!DISCOVERED_REPOS[@]}"; do
            local repo_entry="${DISCOVERED_REPOS[$i]}"
            # Extract metadata after first colon
            local metadata="${repo_entry#*:}"
            
            if [ $i -gt 0 ]; then
                printf ',\n' >> "$report_file"
            else
                printf '\n' >> "$report_file"
            fi
            printf '    %s' "$metadata" >> "$report_file"
        done
        printf '\n' >> "$report_file"
    fi
    
    printf '  ],\n' >> "$report_file"
    printf '  "skipped": [\n' >> "$report_file"
    
    # Add skipped repositories
    if [ ${#SKIPPED_REPOS[@]} -gt 0 ]; then
        for i in "${!SKIPPED_REPOS[@]}"; do
            local skipped="${SKIPPED_REPOS[$i]}"
            
            if [ $i -gt 0 ]; then
                printf ',\n' >> "$report_file"
            fi
            printf '    "%s"' "$skipped" >> "$report_file"
        done
        printf '\n' >> "$report_file"
    fi
    
    printf '  ],\n' >> "$report_file"
    printf '  "errors": [\n' >> "$report_file"
    
    # Add error repositories
    if [ ${#ERROR_REPOS[@]} -gt 0 ]; then
        for i in "${!ERROR_REPOS[@]}"; do
            local error="${ERROR_REPOS[$i]}"
            
            if [ $i -gt 0 ]; then
                printf ',\n' >> "$report_file"
            fi
            printf '    "%s"' "$error" >> "$report_file"
        done
        printf '\n' >> "$report_file"
    fi
    
    printf '  ]\n' >> "$report_file"
    printf '}\n' >> "$report_file"
    
    log "SUCCESS" "Discovery report written to: $report_file"
    
    # Log summary
    log "INFO" "Discovery Summary:"
    log "INFO" "  Valid repositories: ${#DISCOVERED_REPOS[@]}"
    log "INFO" "  Skipped repositories: ${#SKIPPED_REPOS[@]}"
    log "INFO" "  Error repositories: ${#ERROR_REPOS[@]}"
}

# Function to get list of discovered repository paths
get_discovered_repositories() {
    local repo_paths=()
    
    for repo_entry in "${DISCOVERED_REPOS[@]}"; do
        local repo_path="${repo_entry%%:*}"
        repo_paths+=("$repo_path")
    done
    
    printf '%s\n' "${repo_paths[@]}"
}

# Main execution
main() {
    log "INFO" "Repository discovery script started"
    
    # Discover all repositories
    discover_all_repositories
    
    # Generate discovery report
    generate_discovery_report
    
    # Export discovered repositories for other scripts
    if [ ${#DISCOVERED_REPOS[@]} -gt 0 ]; then
        log "SUCCESS" "Repository discovery completed successfully"
        log "INFO" "Found ${#DISCOVERED_REPOS[@]} valid repositories for cleanup processing"
        
        # Output repository list for pipe consumption
        get_discovered_repositories
        return 0
    else
        log "WARNING" "No valid repositories discovered for cleanup processing"
        return 1
    fi
}

# Execute main function if script is run directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi