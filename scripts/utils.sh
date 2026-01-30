#!/bin/bash

# Error handling and logging utilities for Repository Automation System
# Provides consistent error handling and logging across all scripts

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local script_name=${SCRIPT_NAME:-$(basename "${BASH_SOURCE[2]}")}
    
    local log_entry="[${level}] ${timestamp} ${script_name}: $message"
    
    # Output to console with colors
    case "$level" in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} ${timestamp} ${script_name}: $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} ${timestamp} ${script_name}: $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} ${timestamp} ${script_name}: $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} ${timestamp} ${script_name}: $message" >&2
            ;;
        "DEBUG")
            if [[ "${DEBUG_MODE:-false}" == "true" ]]; then
                echo -e "${BLUE}[DEBUG]${NC} ${timestamp} ${script_name}: $message" >&2
            fi
            ;;
    esac
    
    # Write to log file if log_directory is configured
    if [[ -n "${LOG_DIRECTORY}" && -d "${LOG_DIRECTORY}" ]]; then
        local log_file="${LOG_DIRECTORY}/${script_name}.log"
        echo "$log_entry" >> "$log_file"
    fi
}

# Error handling function
handle_error() {
    local exit_code=$?
    local line_number=$1
    local command="$2"
    
    if [ $exit_code -ne 0 ]; then
        log "ERROR" "Command failed with exit code $exit_code at line $line_number: $command"
        log "ERROR" "Script execution failed"
        exit $exit_code
    fi
}

# Set up error trap
setup_error_handling() {
    set -eE  # Exit on error, inherit ERR trap
    trap 'handle_error $LINENO "$BASH_COMMAND"' ERR
}

# Success message for script completion
script_success() {
    local script_name=$(basename "${BASH_SOURCE[1]}")
    log "SUCCESS" "$script_name completed successfully"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate required environment variables
validate_env_vars() {
    local required_vars=("$@")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log "ERROR" "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
}

# Function to check if a directory exists and is writable
check_directory() {
    local dir_path="$1"
    local dir_name="$2"
    
    if [ ! -d "$dir_path" ]; then
        log "ERROR" "$dir_name directory not found: $dir_path"
        exit 1
    fi
    
    if [ ! -w "$dir_path" ]; then
        log "ERROR" "$dir_name directory is not writable: $dir_path"
        exit 1
    fi
}

# Function to safely execute commands with logging
safe_execute() {
    local cmd="$*"
    log "DEBUG" "Executing: $cmd"
    
    if eval "$cmd"; then
        log "DEBUG" "Command succeeded: $cmd"
        return 0
    else
        local exit_code=$?
        log "ERROR" "Command failed with exit code $exit_code: $cmd"
        return $exit_code
    fi
}

# Function to handle git operations safely
safe_git() {
    local git_cmd="$*"
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    
    log "DEBUG" "Git operation in $repo_dir: $git_cmd"
    
    cd "$repo_dir" || {
        log "ERROR" "Cannot change to directory: $repo_dir"
        exit 1
    }
    
    if eval "git $git_cmd"; then
        log "DEBUG" "Git command succeeded: $git_cmd"
        return 0
    else
        local exit_code=$?
        log "ERROR" "Git command failed with exit code $exit_code: $git_cmd"
        return $exit_code
    fi
}

# Function to initialize log directory
setup_log_directory() {
    if [[ -n "${LOG_DIRECTORY}" ]]; then
        if [[ ! -d "${LOG_DIRECTORY}" ]]; then
            mkdir -p "${LOG_DIRECTORY}" || {
                echo "WARNING: Failed to create log directory: ${LOG_DIRECTORY}" >&2
                return 1
            }
            echo "INFO: Created log directory: ${LOG_DIRECTORY}"
        fi
        
        # Test write permissions
        if [[ ! -w "${LOG_DIRECTORY}" ]]; then
            echo "WARNING: Log directory is not writable: ${LOG_DIRECTORY}" >&2
            return 1
        fi
        
        echo "INFO: Log directory configured: ${LOG_DIRECTORY}"
    fi
}

# Function to execute script with stdout/stderr capture
execute_with_capture() {
    local script_path="$1"
    local script_name=$(basename "$script_path")
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local exit_code=0
    
    # Setup log directory if not already done
    setup_log_directory >/dev/null 2>&1
    
    if [[ -n "${LOG_DIRECTORY}" && -d "${LOG_DIRECTORY}" && -w "${LOG_DIRECTORY}" ]]; then
        # Create log file with timestamp
        local log_file="${LOG_DIRECTORY}/${script_name}_${timestamp}.log"
        
        # Execute script, capturing stdout and stderr to log file
        # Use tee to also show output on console
        echo "Executing: $script_name (capturing output to: $log_file)" >&2
        
        # Capture both stdout and stderr, while still showing on console
        if "$script_path" 2>&1 | tee "$log_file"; then
            exit_code=0
            echo "✓ $script_name completed successfully (captured to: $log_file)" >&2
        else
            exit_code=$?
            echo "✗ $script_name failed with exit code $exit_code (captured to: $log_file)" >&2
        fi
        
        # Create a symlink to the latest log for easy access
        local latest_log="${LOG_DIRECTORY}/${script_name}_latest.log"
        ln -sf "$(basename "$log_file")" "$latest_log" 2>/dev/null || true
        
    else
        # Fallback to normal execution if log directory not available
        echo "Log directory not available, executing without capture: $script_name" >&2
        if "$script_path"; then
            exit_code=0
            echo "✓ $script_name completed successfully" >&2
        else
            exit_code=$?
            echo "✗ $script_name failed with exit code $exit_code" >&2
        fi
    fi
    
    return $exit_code
}

export -f log handle_error setup_error_handling script_success command_exists validate_env_vars check_directory safe_execute safe_git setup_log_directory execute_with_capture
export RED GREEN YELLOW BLUE NC DEBUG_MODE