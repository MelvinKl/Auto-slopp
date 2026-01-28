#!/bin/bash

# Fix failed dependency updates in renovate branches using YAML configuration
echo "Running update_fixer.sh"

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
    
    echo "Processing: $repo_dir"
    cd "$repo_dir"
    
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
  workdir="$repo_dir"
            fi
        fi
    done
done

echo "Update_fixer.sh completed."