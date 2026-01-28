#!/bin/bash

# Update repositories and merge main into branches using YAML configuration
echo "Running updater.sh"

# Load configuration from YAML
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../config.sh"

echo "Using managed_repo_path: $MANAGED_REPO_PATH"

# First update this repository
echo "Updating automation repository"
git pull

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
    
    echo "Updating: $repo_dir"
    cd "$repo_dir"
    
    # Fetch and clean
    git fetch --all
    git clean -fd
    
    # Get branches to update
    branches=$(git branch -r | grep -v 'HEAD' | sed 's/^[[:space:]]*origin\///')
    
    for branch in $branches; do
        # Only update renovate and ai branches
        if [[ $branch == renovate* ]] || [ "$branch" = "ai" ]; then
            echo "  Updating branch: $branch"
            
            # Switch to branch
            git checkout "$branch" 2>/dev/null || {
                # Create ai branch if it doesn't exist
                git checkout -b "$branch" origin/main
                git push -u origin "$branch"
                continue
            }
            
            git reset --hard origin/"$branch"
            
            # Merge main into branch
            if git merge origin/main -m "Merge main into $branch (automated)"; then
                git push
            else
                echo "  Merge failed for $branch"
                git merge --abort 2>/dev/null || true
            fi
        fi
    done
done

echo "Updater.sh completed."