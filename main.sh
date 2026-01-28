#!/bin/bash

# Main script - dynamically runs all scripts in scripts directory
echo "Starting Repository Automation System"

# Load configuration from YAML
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo "Configuration loaded:"
echo "  Sleep duration: $SLEEP_DURATION seconds"
echo "  Managed repo path: $MANAGED_REPO_PATH"
echo "  Task path: $MANAGED_REPO_TASK_PATH"

while true; do
    echo "=== Running automation cycle at $(date) ==="
    
    # Discover all scripts in scripts directory
    SCRIPTS_DIR="$SCRIPT_DIR/scripts"
    
    # Find all .sh files in scripts directory, sort alphabetically
    scripts_found=($(find "$SCRIPTS_DIR" -name "*.sh" -type f | sort))
    
    if [ ${#scripts_found[@]} -eq 0 ]; then
        echo "No scripts found in $SCRIPTS_DIR"
    else
        echo "Found ${#scripts_found[@]} scripts to execute"
        
        # Execute each script
        for script in "${scripts_found[@]}"; do
            script_name=$(basename "$script")
            echo "Executing: $script_name"
            
            # Execute script and capture exit status
            if "$script"; then
                echo "✓ $script_name completed successfully"
            else
                echo "✗ $script_name failed with exit code $?"
            fi
            echo "---"
        done
    fi
    
    echo "=== Cycle complete, sleeping $SLEEP_DURATION seconds ==="
    sleep "$SLEEP_DURATION"
done