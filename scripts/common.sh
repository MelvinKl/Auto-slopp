#!/bin/bash

# Common error handling and logging functions
# Source this file in all scripts

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTOMATION_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$AUTOMATION_ROOT/config.sh"

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"

# Logging functions
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local script_name=$(basename "$0")
    local log_file="$LOGS_DIR/${script_name%.*}.log"
    
    # Only log if the level is at or above the configured log level
    case "$LOG_LEVEL" in
        "DEBUG") ;;
        "INFO") [[ "$level" == "DEBUG" ]] && return ;;
        "WARN") [[ "$level" == "DEBUG" || "$level" == "INFO" ]] && return ;;
        "ERROR") [[ "$level" != "ERROR" && "$level" != "WARN" ]] && return ;;
    esac
    
    echo "[$timestamp] [$level] [$script_name] $message" | tee -a "$log_file"
}

log_debug() { log "DEBUG" "$@"; }
log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }

# Error handling functions
handle_error() {
    local exit_code=$?
    local line_number=$1
    local command="$2"
    
    log_error "Command failed with exit code $exit_code at line $line_number: $command"
    
    # Send notification if configured (you can add email/slack etc.)
    # send_notification "Error in $0: $command failed"
    
    exit $exit_code
}

# Set up error trapping
setup_error_handling() {
    set -eE
    trap 'handle_error $LINENO "$BASH_COMMAND"' ERR
}

# Cleanup function
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_error "Script exited with error code $exit_code"
    else
        log_info "Script completed successfully"
    fi
}

# Set up cleanup trap
setup_cleanup() {
    trap cleanup EXIT
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate required commands
validate_dependencies() {
    local missing_commands=()
    
    for cmd in "$@"; do
        if ! command_exists "$cmd"; then
            missing_commands+=("$cmd")
        fi
    done
    
    if [ ${#missing_commands[@]} -gt 0 ]; then
        log_error "Missing required commands: ${missing_commands[*]}"
        return 1
    fi
    
    log_info "All required commands are available"
}

# Function to retry a command
retry() {
    local retries=$1
    shift
    local command="$*"
    
    for ((i=1; i<=retries; i++)); do
        log_info "Attempt $i/$retries: $command"
        if eval "$command"; then
            log_info "Command succeeded on attempt $i"
            return 0
        else
            log_warn "Command failed on attempt $i"
            if [ $i -lt $retries ]; then
                local wait_time=$((i * 5))
                log_info "Waiting $wait_time seconds before retry..."
                sleep $wait_time
            fi
        fi
    done
    
    log_error "Command failed after $retries attempts: $command"
    return 1
}

# Initialize error handling and logging
init_common() {
    setup_error_handling
    setup_cleanup
    log_info "Starting $(basename "$0")"
}