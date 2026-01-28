#!/bin/bash

# Update repositories and merge main into branches
echo "Running updater.sh"

# First update this repository
echo "Updating automation repository"
git pull

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
    
    echo "Updating: $repo"
    cd "$repo"
    
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
done < repos.txt