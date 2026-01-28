#!/bin/bash

# Main script - runs all other scripts in a loop
echo "Starting Repository Automation System"

while true; do
    echo "=== Running automation cycle ==="
    
    # Run all scripts
    ./scripts/update_fixer.sh
    ./scripts/creator.sh
    ./scripts/planner.sh
    ./scripts/updater.sh
    ./scripts/implementer.sh
    
    echo "=== Cycle complete, sleeping 30 minutes ==="
    sleep 1800
done