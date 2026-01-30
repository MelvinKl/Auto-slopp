#!/bin/bash

# Process task files and generate bead tasks using YAML configuration
# Load utilities and configuration first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# Set up error handling
setup_error_handling

log "INFO" "Starting planner.sh"
log "INFO" "Using managed_repo_path: $MANAGED_REPO_PATH"
log "INFO" "Using managed_repo_task_path: $MANAGED_REPO_TASK_PATH"

# Check if managed directories exist
if [ ! -d "$MANAGED_REPO_PATH" ]; then
    echo "Error: managed_repo_path not found: $MANAGED_REPO_PATH"
    exit 1
fi

if [ ! -d "$MANAGED_REPO_TASK_PATH" ]; then
    echo "Error: managed_repo_task_path not found: $MANAGED_REPO_TASK_PATH"
    exit 1
fi

# Track if any changes were made in task path
TASK_PATH_CHANGES=false

# Process each subdirectory in managed_repo_path
for repo_dir in "$MANAGED_REPO_PATH"/*; do
    if [ ! -d "$repo_dir" ]; then
        continue
    fi
    
    # Get repository name
    repo_name=$(basename "$repo_dir")
    echo "Processing repository: $repo_name"
    
    # Check for matching task directory
    task_dir="$MANAGED_REPO_TASK_PATH/$repo_name"
    if [ ! -d "$task_dir" ]; then
        echo "  No task directory found: $task_dir"
        continue
    fi
    
    echo "  Found task directory: $task_dir"
    
    # Ensure files are numbered, then process in numerical order
    # First, assign numbers to any unnumbered task files
    unnumbered_files=($(find "$task_dir" -maxdepth 1 -type f -name "*.txt" ! -name "[0-9][0-9][0-9][0-9]-*" ! -name "*.used" | sort))
    if [ ${#unnumbered_files[@]} -gt 0 ]; then
        # Find the next available number
        max_num=0
        numbered_files=($(find "$task_dir" -maxdepth 1 -type f -name "[0-9][0-9][0-9][0-9]-*.txt" ! -name "*.used" 2>/dev/null))
        for num_file in "${numbered_files[@]}"; do
            basename_num=$(basename "$num_file" | sed 's/^\([0-9][0-9][0-9][0-9]\)-.*/\1/')
            if [[ "$basename_num" =~ ^[0-9][0-9][0-9][0-9]$ ]]; then
                num_val=$((10#$basename_num))
                if [ $num_val -gt $max_num ]; then
                    max_num=$num_val
                fi
            fi
        done
        
        # Assign numbers to unnumbered files
        next_num=$((max_num + 1))
        for unnumbered_file in "${unnumbered_files[@]}"; do
            filename=$(basename "$unnumbered_file" .txt)
            new_filename=$(printf "%04d-%s.txt" "$next_num" "$filename")
            echo "    Renaming $(basename "$unnumbered_file") to $new_filename"
            mv "$unnumbered_file" "$task_dir/$new_filename"
            next_num=$((next_num + 1))
        done
    fi
    
    # Process each numbered file in task directory that doesn't end with '.used'
    for task_file in "$task_dir"/[0-9][0-9][0-9][0-9]-*.txt; do
        if [ ! -f "$task_file" ]; then
            continue
        fi
        
        # Skip files that already end with '.used'
        if [[ "$task_file" == *.used ]]; then
            echo "    Skipping already used file: $(basename "$task_file")"
            continue
        fi
        
        filename=$(basename "$task_file")
        echo "    Processing: $filename"
        
        # Get file content
        content=$(cat "$task_file")
        
        # Switch to ai branch in the repository
        cd "$repo_dir"
        git fetch origin
        
        # Create ai branch if it doesn't exist
        if ! git rev-parse --verify origin/ai >/dev/null 2>&1; then
            git checkout -b ai origin/main
            git push -u origin ai
        else
            git checkout ai
            git reset --hard origin/ai
        fi
        
        # Generate bead tasks using opencode CLI
        echo "    Generating bead tasks for: $content"
        $OPencode_CMD run "Generate bead tasks for: $content" --agent OpenAgent
        
        # Commit and push changes in repository
        git add .
        git commit -m "Add bead tasks from $filename" || true
        git push
        
        # Rename processed file to add '.used' suffix
        mv "$task_file" "$task_file.used"
        echo "    Renamed $filename to $filename.used"
        
        # Mark that changes were made in task path
        TASK_PATH_CHANGES=true
    done
done

# Commit and push changes in managed_repo_task_path if any files were processed
if [ "$TASK_PATH_CHANGES" = true ]; then
    echo "Committing changes in task path..."
    cd "$MANAGED_REPO_TASK_PATH"
    git add .
    git commit -m "Mark task files as used by planner.sh" || true
    git push
    echo "Task path changes committed and pushed."
else
    echo "No task files were processed."
fi

script_success