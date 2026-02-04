#!/bin/bash

# Main script - dynamically runs all scripts in scripts directory
# Set script name for logging identification
SCRIPT_NAME="main"

# Load configuration from YAML
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/scripts/utils.sh"

log "INFO" "Configuration loaded:"
log "INFO" "  Sleep duration: $SLEEP_DURATION seconds"
log "INFO" "  Managed repo path: $MANAGED_REPO_PATH"
log "INFO" "  Task path: $MANAGED_REPO_TASK_PATH"
log "INFO" "  Log directory: ${LOG_DIRECTORY:-'Not configured'}"

# Initialize log directory
setup_log_directory

# Configure enhanced logging with settings from config.yaml
configure_logging "$TIMESTAMP_FORMAT" "$TIMESTAMP_TIMEZONE"

# Log that the system is starting up
log "INFO" "Starting Repository Automation System"

 while true; do
    log "INFO" "=== Running automation cycle ==="
    
    # Reset SCRIPT_DIR to this script's directory (scripts may modify it)
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Discover all scripts in scripts directory
    SCRIPTS_DIR="$SCRIPT_DIR/scripts"
    
    # Find all .sh files in scripts directory, sort alphabetically
    scripts_found=($(find "$SCRIPTS_DIR" -name "*.sh" -type f | sort))
    
    if [ ${#scripts_found[@]} -eq 0 ]; then
        log "WARNING" "No scripts found in $SCRIPTS_DIR"
    else
        log "INFO" "Found ${#scripts_found[@]} scripts to execute"
        
        # Execute each script with stdout capture
        for script in "${scripts_found[@]}"; do
            script_name=$(basename "$script")
            
            # Execute script with capture mechanism
            if execute_with_capture "$script"; then
                log "SUCCESS" "$script_name execution completed"
            else
                log "ERROR" "$script_name execution failed"
            fi
        done
    fi
    
    log "INFO" "=== Cycle complete, sleeping $SLEEP_DURATION seconds ==="
    sleep "$SLEEP_DURATION"
done