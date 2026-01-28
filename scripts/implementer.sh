#!/bin/bash

# Implement ready bead tasks using YAML configuration
echo "Running implementer.sh"

# Load configuration from YAML
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../config.sh"

echo "Using managed_repo_path: $MANAGED_REPO_PATH"

# Check if managed_repo_path exists
if [ ! -d "$MANAGED_REPO_PATH" ]; then
    echo "Error: managed_repo_path not found: $MANAGED_REPO_PATH"
    exit 1
fi

# Process each subdirectory in managed_repo_path
for repo_dir in "$MANAGED_REPO_PATH"/*; do
    if [ ! -d "$repo_dir" ]; then
        continue
    fi
    
    echo "Implementing tasks for: $(basename "$repo_dir")"
    cd "$repo_dir"
    
    # Switch to ai branch
    git fetch origin
    
    # Create ai branch if it doesn't exist
    if ! git rev-parse --verify origin/ai >/dev/null 2>&1; then
        git checkout -b ai origin/main
        git push -u origin ai
    else
        git checkout ai
        git reset --hard origin/ai
    fi
    
    # Use OpenAgent to find and implement next ready task
    echo "  Using OpenAgent to find and implement next ready task"
    task \
  subagent_type="OpenAgent" \
  description="Implement next ready bead task" \
  prompt="Find the next ready bead task and implement it. Use the beads CLI to discover ready tasks, then implement the task and manage the beads workflow (mark in progress, close when complete). Commit all changes and push to the current branch." \
  workdir="$repo_dir"
    
    echo "  Task implementation completed"
done

echo "Implementer.sh completed."