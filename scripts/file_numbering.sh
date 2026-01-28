#!/bin/bash

# File numbering system for planner.sh
# Provides functions to manage file numbering and increment logic

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Function to extract number from filename
extract_number() {
    local filename="$1"
    # Extract the number after the last dot
    echo "$filename" | grep -oE '\.[0-9]+$' | sed 's/^.//'
}

# Function to check if file should be processed based on number
should_process_file() {
    local filename="$1"
    local file_number=$(extract_number "$filename")
    
    # If no number, it's a new file and should be processed
    if [ -z "$file_number" ]; then
        return 0
    fi
    
    # Check if number is less than or equal to max
    if [ "$file_number" -le "$MAX_FILE_NUMBER" ]; then
        return 0
    fi
    
    return 1
}

# Function to increment file number
increment_file_number() {
    local filepath="$1"
    local dir=$(dirname "$filepath")
    local filename=$(basename "$filepath")
    local name="${filename%.*}"
    local extension="${filename##*.}"
    
    # Extract current number
    local current_number=$(extract_number "$filename")
    
    if [ -z "$current_number" ]; then
        # No number, add .1
        local new_name="${name}.1.${extension}"
    else
        # Increment the number
        local new_number=$((current_number + 1))
        local name_without_number="${name%.*}"
        local new_name="${name_without_number}.${new_number}.${extension}"
    fi
    
    local new_filepath="$dir/$new_name"
    
    # Rename the file
    log_info "Renaming $filepath to $new_filepath"
    mv "$filepath" "$new_filepath"
    
    echo "$new_filepath"
}

# Function to get next available number for a base filename
get_next_number() {
    local dir="$1"
    local base_name="$2"
    local extension="$3"
    
    local max_number=0
    
    # Find all files with this base name and any number
    for file in "$dir"/"${base_name}".*."${extension}"; do
        if [ -f "$file" ]; then
            local filename=$(basename "$file")
            local number=$(extract_number "$filename")
            if [ -n "$number" ] && [ "$number" -gt "$max_number" ]; then
                max_number=$number
            fi
        fi
    done
    
    echo $((max_number + 1))
}

# Function to create new numbered filename
create_numbered_filename() {
    local dir="$1"
    local base_name="$2"
    local extension="$3"
    local content="$4"
    
    local next_number=$(get_next_number "$dir" "$base_name" "$extension")
    local filename="${base_name}.${next_number}.${extension}"
    local filepath="$dir/$filename"
    
    # Write content to file
    echo "$content" > "$filepath"
    
    log_info "Created new file: $filepath"
    echo "$filepath"
}

# Function to find files ready for processing
find_ready_files() {
    local dir="$1"
    local extension="${2:-txt}"
    
    log_info "Searching for files ready to process in $dir"
    
    local ready_files=()
    
    for file in "$dir"/*."${extension}"; do
        if [ -f "$file" ]; then
            if should_process_file "$(basename "$file")"; then
                ready_files+=("$file")
                log_debug "Ready file: $file"
            else
                log_debug "Skipping file (number too high): $file"
            fi
        fi
    done
    
    echo "${ready_files[@]}"
}

# Function to mark file as processed
mark_file_processed() {
    local filepath="$1"
    local new_filepath=$(increment_file_number "$filepath")
    log_info "Marked file as processed: $new_filepath"
}

# Test function to verify the numbering system
test_numbering_system() {
    local test_dir="/tmp/beads_numbering_test"
    mkdir -p "$test_dir"
    
    log_info "Testing numbering system in $test_dir"
    
    # Test creating new files
    create_numbered_filename "$test_dir" "test" "txt" "Content 1"
    create_numbered_filename "$test_dir" "test" "txt" "Content 2"
    
    # Test incrementing
    local file1="$test_dir/test.1.txt"
    increment_file_number "$file1"
    
    # Test finding ready files
    local ready_files=$(find_ready_files "$test_dir" "txt")
    log_info "Ready files: $ready_files"
    
    # Cleanup
    rm -rf "$test_dir"
    
    log_info "Numbering system test completed"
}