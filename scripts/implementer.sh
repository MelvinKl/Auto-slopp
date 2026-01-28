#!/bin/bash

# Implement ready bead tasks
echo "Running implementer.sh"

# Read repositories from repos.txt
while read -r repo; do
    # Skip comments and empty lines
    [[ $repo =~ ^[[:space:]]*# ]] && continue
    [[ -z "$repo" ]] && continue
    
    # Expand $HOME and other variables
    repo=$(eval echo "$repo")
    
    if [ ! -d "$repo" ]; then
        echo "Repository not found: $repo"
        continue
    fi
    
    echo "Implementing tasks for: $(basename "$repo")"
    cd "$repo"
    
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
  workdir="$repo"
    
    echo "  Task implementation completed"
done < repos.txt