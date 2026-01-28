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
    
    # Get next ready task
    task_id=$(bd ready --json 2>/dev/null | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -n "$task_id" ]; then
        echo "  Implementing task: $task_id"
        
        # Get task details
        task_details=$(bd show "$task_id" --json 2>/dev/null)
        title=$(echo "$task_details" | grep -o '"title":"[^"]*"' | cut -d'"' -f4)
        
        # Mark as in progress
        bd update "$task_id" --status in_progress
        
        # Implement task
        opencode "Implement the next bd task that is ready. Task ID: $task_id. Task: $title. Please implement this task, commit the changes, and push to the current branch."
        
        # Push changes
        git push
        
        # Close task
        bd close "$task_id" --reason "Implemented by automation system"
        
        echo "  Completed task: $task_id"
    else
        echo "  No ready tasks"
    fi
done < repos.txt