#!/bin/bash

# Enhanced Planner Integration with Number Manager
# This script demonstrates how to integrate the number manager with the existing planner.sh

SCRIPT_NAME="planner_enhanced"

# Load utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# We'll call the number manager as a script, not source it
NUMBER_MANAGER_SCRIPT="$SCRIPT_DIR/number_manager.sh"

# Set up error handling
setup_error_handling

log "INFO" "Testing enhanced planner integration with number manager"

# Test function to demonstrate enhanced numbering
test_enhanced_numbering() {
    local test_dir="/tmp/test_enhanced_planner_$$"
    local repo_name="test_repo"
    local task_dir="$test_dir/tasks/$repo_name"
    
    # Setup test environment
    mkdir -p "$task_dir"
    
    # Create some test task files
    echo "Test task 1" > "$task_dir/task1.txt"
    echo "Test task 2" > "$task_dir/task2.txt"
    echo "Test task 3" > "$task_dir/task3.txt"
    
    # Initialize number state
    export MANAGED_REPO_PATH="$test_dir"
    if ! "$NUMBER_MANAGER_SCRIPT" init "$repo_name" >/dev/null 2>&1; then
        log "ERROR" "Failed to initialize number state"
        return 1
    fi
    
    # Process unnumbered files using enhanced numbering
    unnumbered_files=($(find "$task_dir" -maxdepth 1 -type f -name "*.txt" ! -name "[0-9][0-9][0-9][0-9]-*" ! -name "*.used" | sort))
    
    log "INFO" "Found ${#unnumbered_files[@]} unnumbered files to process"
    
    for unnumbered_file in "${unnumbered_files[@]}"; do
        filename=$(basename "$unnumbered_file" .txt)
        
        # Get next unique number using number manager
        task_context="$repo_name/$(basename "$task_dir")"
        next_num=$("$NUMBER_MANAGER_SCRIPT" get "$task_context" 2>/dev/null | tail -1)
        
        if [ $? -ne 0 ]; then
            log "ERROR" "Failed to get unique number for $task_context"
            continue
        fi
        
        new_filename=$(printf "%04d-%s.txt" "$next_num" "$filename")
        
        log "INFO" "Enhanced numbering: $filename → $new_filename (context: $task_context)"
        
        # Simulate file rename (in real planner, this would be actual mv)
        if mv "$unnumbered_file" "$task_dir/$new_filename"; then
            log "SUCCESS" "Successfully renamed to $new_filename"
        else
            log "ERROR" "Failed to rename $unnumbered_file"
            # Release the number back to pool on failure
            "$NUMBER_MANAGER_SCRIPT" release "$next_num" "$task_context" >/dev/null 2>&1
        fi
    done
    
    # Show final state statistics
    log "INFO" "Final number state:"
    "$NUMBER_MANAGER_SCRIPT" stats | jq '.' 2>/dev/null || log "WARNING" "Could not display stats"
    
    # Cleanup
    rm -rf "$test_dir"
    log "INFO" "Enhanced planner test completed successfully"
    
    return 0
}

# Run the test
if test_enhanced_numbering; then
    log "SUCCESS" "Enhanced planner integration test passed"
    exit 0
else
    log "ERROR" "Enhanced planner integration test failed"
    exit 1
fi