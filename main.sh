#!/bin/bash

# Main orchestration script for Repository Automation System
# Calls all scripts in the scripts directory in an endless loop

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Function to run a single script
run_script() {
    local script_name="$1"
    local script_path="$SCRIPT_DIR/$script_name"
    
    if [ ! -f "$script_path" ]; then
        log_warn "Script not found: $script_path"
        return 1
    fi
    
    if [ ! -x "$script_path" ]; then
        log_warn "Script not executable: $script_path"
        return 1
    fi
    
    log_info "Running script: $script_name"
    
    # Run the script with error handling
    if "$script_path"; then
        log_info "Script $script_name completed successfully"
        return 0
    else
        local exit_code=$?
        log_error "Script $script_name failed with exit code $exit_code"
        return $exit_code
    fi
}

# Function to run all scripts in order
run_all_scripts() {
    log_info "Starting script execution cycle"
    
    local scripts=(
        "update_fixer.sh"
        "creator.sh"
        "planner.sh"
        "updater.sh"
        "implementer.sh"
    )
    
    local failed_scripts=()
    
    for script in "${scripts[@]}"; do
        if ! run_script "$script"; then
            failed_scripts+=("$script")
        fi
        
        # Small delay between scripts to prevent overwhelming the system
        sleep 5
    done
    
    if [ ${#failed_scripts[@]} -gt 0 ]; then
        log_warn "Some scripts failed: ${failed_scripts[*]}"
        return 1
    else
        log_info "All scripts completed successfully"
        return 0
    fi
}

# Function to sleep with progress indication
sleep_with_progress() {
    local duration="$1"
    local message="${2:-Waiting before next cycle}"
    
    log_info "$message for $duration seconds"
    
    # Show progress every minute
    for ((i=0; i<duration; i+=60)); do
        if [ $((i + 60)) -lt $duration ]; then
            log_debug "Sleeping... ($((i + 60))/$duration seconds)"
            sleep 60
        else
            local remaining=$((duration - i))
            sleep $remaining
            break
        fi
    done
}

# Function to handle graceful shutdown
graceful_shutdown() {
    log_info "Received shutdown signal, finishing current cycle..."
    # Let the current cycle complete, then exit
    exit 0
}

# Function to validate environment
validate_environment() {
    log_info "Validating environment"
    
    # Check required directories
    if [ ! -d "$SCRIPTS_DIR" ]; then
        log_error "Scripts directory not found: $SCRIPTS_DIR"
        return 1
    fi
    
    # Check configuration file
    if [ ! -f "$AUTOMATION_ROOT/config.sh" ]; then
        log_error "Configuration file not found: $AUTOMATION_ROOT/config.sh"
        return 1
    fi
    
    # Check required commands
    validate_dependencies "git" "sleep" || return 1
    
    log_info "Environment validation passed"
}

# Function to display startup banner
show_banner() {
    echo "=================================================="
    echo "  Repository Automation System - Main Orchestration"
    echo "=================================================="
    echo "Sleep duration: $MAIN_SLEEP_DURATION seconds"
    echo "Scripts directory: $SCRIPTS_DIR"
    echo "Log directory: $LOGS_DIR"
    echo "Repo directory: $REPO_DIRECTORY"
    echo "=================================================="
}

# Main execution loop
main() {
    init_common
    validate_environment || exit 1
    show_banner
    
    # Set up signal handlers for graceful shutdown
    trap graceful_shutdown SIGTERM SIGINT
    
    local cycle_count=0
    
    while true; do
        cycle_count=$((cycle_count + 1))
        log_info "=== Starting cycle $cycle_count ==="
        
        if run_all_scripts; then
            log_info "=== Cycle $cycle_count completed successfully ==="
        else
            log_warn "=== Cycle $cycle_count completed with some failures ==="
        fi
        
        log_info "Sleeping for $MAIN_SLEEP_DURATION seconds before next cycle"
        sleep_with_progress "$MAIN_SLEEP_DURATION" "Waiting before next cycle"
    done
}

# Run main function if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi