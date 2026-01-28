#!/bin/bash

# Process task files and generate bead tasks
echo "Running planner.sh"

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
    
    # Get repository name
    repo_name=$(basename "$repo")
    repo_name=$(echo "$repo_name" | sed 's/[^a-zA-Z0-9._-]/_/g')
    
    tasks_dir="$repo_name/tasks"
    
    if [ ! -d "$tasks_dir" ]; then
        echo "No tasks directory for: $repo_name"
        continue
    fi
    
    echo "Processing tasks for: $repo_name"
    
    # Process each .txt file in tasks directory
    for task_file in "$tasks_dir"/*.txt; do
        if [ ! -f "$task_file" ]; then
            continue
        fi
        
        filename=$(basename "$task_file")
        echo "  Processing: $filename"
        
        # Get file content
        content=$(cat "$task_file")
        
        # Switch to ai branch
        cd "$repo"
        git fetch origin
        
        # Create ai branch if it doesn't exist
        if ! git rev-parse --verify origin/ai >/dev/null 2>&1; then
            git checkout -b ai origin/main
            git push -u origin ai
        else
            git checkout ai
            git reset --hard origin/ai
        fi
        
        # Generate bead tasks
        echo "  Generating bead tasks for: $content"
        opencode "Generate bead tasks for: $content"
        
        # Commit and push
        git add .
        git commit -m "Add bead tasks from $filename" || true
        git push
        
        # Rename processed file
        mv "$task_file" "$task_file.processed"
    done
done < repos.txt