#!/bin/bash

# Fix failed dependency updates in renovate branches
echo "Running update_fixer.sh"

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
    
    echo "Processing: $repo"
    cd "$repo"
    
    # Get renovate branches
    branches=$(git branch -r --list 'origin/renovate*' 2>/dev/null | sed 's/^[[:space:]]*origin\///')
    
    for branch in $branches; do
        echo "  Branch: $branch"
        
        # Update branch
        git fetch origin
        git reset --hard origin/"$branch"
        git clean -fd
        
        # Run tests
        if [ -f "Makefile" ]; then
            if ! make test; then
                echo "  Tests failed, using OpenAgent to fix"
                task \
  subagent_type="OpenAgent" \
  description="Fix failed tests using OpenAgent" \
  prompt="Fix the branch '$branch' that contains updates to dependencies and push them to the branch. The tests are currently failing, so identify and fix any issues preventing the tests from passing, then push the fixes to the branch." \
  workdir="$repo"
            fi
        fi
    done
done < repos.txt