#!/bin/bash

# Error handling and logging utilities for Repository Automation System
# Provides consistent error handling and logging across all scripts

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to remove ANSI color codes from text
strip_colors() {
    local text="$1"
    # Remove ANSI escape sequences
    echo -e "$text" | sed 's/\x1b\[[0-9;]*m//g'
}

# Function to check if log level should be processed
should_log() {
    local level="$1"
    local current_level="${LOG_LEVEL:-INFO}"
    
    # Define log level hierarchy (numbers indicate priority)
    declare -A log_levels=(
        ["DEBUG"]=0
        ["INFO"]=1
        ["SUCCESS"]=1
        ["WARNING"]=2
        ["ERROR"]=3
    )
    
    local level_priority=${log_levels[$level]:-1}
    local current_priority=${log_levels[$current_level]:-1}
    
    # Process if level priority is >= current priority
    [[ $level_priority -ge $current_priority ]]
}

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local script_name=${SCRIPT_NAME:-$(basename "${BASH_SOURCE[2]}")}
    
    # Check if we should log this level
    if ! should_log "$level"; then
        return 0
    fi
    
    local log_entry="[${level}] ${timestamp} ${script_name}: $message"
    local clean_log_entry=$(strip_colors "$log_entry")
    
    # Output to console with colors
    case "$level" in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} ${timestamp} ${script_name}: $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} ${timestamp} ${script_name}: $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} ${timestamp} ${script_name}: $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} ${timestamp} ${script_name}: $message" >&2
            ;;
        "DEBUG")
            if [[ "${DEBUG_MODE:-false}" == "true" ]]; then
                echo -e "${BLUE}[DEBUG]${NC} ${timestamp} ${script_name}: $message" >&2
            fi
            ;;
    esac
    
    # Write to log file if log_directory is configured
    if [[ -n "${LOG_DIRECTORY}" && -d "${LOG_DIRECTORY}" ]]; then
        local log_file="${LOG_DIRECTORY}/${script_name}.log"
        
        # Check if log rotation is needed
        rotate_log_if_needed "$log_file"
        
        # Write clean log entry (without colors)
        echo "$clean_log_entry" >> "$log_file"
    fi
}

# Error handling function
handle_error() {
    local exit_code=$?
    local line_number=$1
    local command="$2"
    
    if [ $exit_code -ne 0 ]; then
        log "ERROR" "Command failed with exit code $exit_code at line $line_number: $command"
        log "ERROR" "Script execution failed"
        exit $exit_code
    fi
}

# Set up error trap
setup_error_handling() {
    set -eE  # Exit on error, inherit ERR trap
    trap 'handle_error $LINENO "$BASH_COMMAND"' ERR
}

# Success message for script completion
script_success() {
    local script_name=$(basename "${BASH_SOURCE[1]}")
    log "SUCCESS" "$script_name completed successfully"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate required environment variables
validate_env_vars() {
    local required_vars=("$@")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log "ERROR" "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
}

# Function to check if a directory exists and is writable
check_directory() {
    local dir_path="$1"
    local dir_name="$2"
    
    if [ ! -d "$dir_path" ]; then
        log "ERROR" "$dir_name directory not found: $dir_path"
        exit 1
    fi
    
    if [ ! -w "$dir_path" ]; then
        log "ERROR" "$dir_name directory is not writable: $dir_path"
        exit 1
    fi
}

# Function to safely execute commands with logging
safe_execute() {
    local cmd="$*"
    log "DEBUG" "Executing: $cmd"
    
    if eval "$cmd"; then
        log "DEBUG" "Command succeeded: $cmd"
        return 0
    else
        local exit_code=$?
        log "ERROR" "Command failed with exit code $exit_code: $cmd"
        return $exit_code
    fi
}

# Function to handle git operations safely
safe_git() {
    local git_cmd="$*"
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    
    log "DEBUG" "Git operation in $repo_dir: $git_cmd"
    
    cd "$repo_dir" || {
        log "ERROR" "Cannot change to directory: $repo_dir"
        exit 1
    }
    
    if eval "git $git_cmd"; then
        log "DEBUG" "Git command succeeded: $git_cmd"
        return 0
    else
        local exit_code=$?
        log "ERROR" "Git command failed with exit code $exit_code: $git_cmd"
        return $exit_code
    fi
}

# Function to rotate log file if it exceeds size limit
rotate_log_if_needed() {
    local log_file="$1"
    local max_size_mb="${LOG_MAX_SIZE_MB:-10}"
    
    # Check if log file exists and get its size in KB
    if [[ -f "$log_file" ]]; then
        local size_kb=$(du -k "$log_file" | cut -f1)
        local max_kb
        
        # Convert max_size_mb to integer KB, handling decimal values
        if [[ "$max_size_mb" == *.* ]]; then
            # Handle decimal MB values by converting to KB
            if command -v bc >/dev/null 2>&1; then
                max_kb=$(echo "$max_size_mb * 1024" | bc | cut -d. -f1)
            else
                # Fallback: truncate decimal and multiply
                max_kb=$((${max_size_mb%.*} * 1024))
            fi
        else
            max_kb=$((max_size_mb * 1024))
        fi
        
        if [[ $size_kb -ge $max_kb ]]; then
            local max_files="${LOG_MAX_FILES:-5}"
            local base_name="${log_file%.*}"
            local extension="${log_file##*.}"
            
            # Rotate existing files
            for ((i=$max_files; i>1; i--)); do
                local old_file="${base_name}.${i}.${extension}"
                local new_file="${base_name}.$((i+1)).${extension}"
                if [[ -f "$old_file" ]]; then
                    mv "$old_file" "$new_file" 2>/dev/null || true
                fi
            done
            
            # Move current log to .1.extension
            local rotated_file="${base_name}.1.${extension}"
            mv "$log_file" "$rotated_file"
            
            local size_mb_display=$(echo "scale=2; $size_kb / 1024" | bc 2>/dev/null || echo "$((size_kb/1024))")
            log "INFO" "Log rotated: $log_file -> $rotated_file (size: ${size_mb_display}MB)"
        fi
    fi
}

# Function to cleanup old log files based on retention policy
cleanup_old_logs() {
    if [[ -z "${LOG_DIRECTORY}" || ! -d "${LOG_DIRECTORY}" ]]; then
        return 0
    fi
    
    local retention_days="${LOG_RETENTION_DAYS:-30}"
    local max_files="${LOG_MAX_FILES:-5}"
    local current_date=$(date +%s)
    local cleanup_count=0
    
    # Find and remove old rotated log files
    while IFS= read -r -d '' log_file; do
        local file_date=$(stat -c %Y "$log_file" 2>/dev/null || echo 0)
        local days_old=$(( (current_date - file_date) / 86400 ))
        
        if [[ $days_old -gt $retention_days ]]; then
            rm -f "$log_file" && ((cleanup_count++))
        fi
    done < <(find "$LOG_DIRECTORY" -name "*.*.log" -type f -print0 2>/dev/null)
    
    # Also limit number of rotated files per script
    for script_log in "$LOG_DIRECTORY"/*.log; do
        if [[ -f "$script_log" ]]; then
            local base_name="${script_log%.*}"
            local extension="${script_log##*.}"
            
            # List rotated files and remove excess ones
            find "$LOG_DIRECTORY" -name "${base_name##*/}.*.${extension}" -type f | \
                sort -r | tail -n +$((max_files + 1)) | xargs -r rm -f
        fi
    done
    
    if [[ $cleanup_count -gt 0 ]]; then
        log "INFO" "Cleaned up $cleanup_count old log files (older than ${retention_days} days)"
    fi
}

# Function to initialize log directory
setup_log_directory() {
    if [[ -n "${LOG_DIRECTORY}" ]]; then
        if [[ ! -d "${LOG_DIRECTORY}" ]]; then
            mkdir -p "${LOG_DIRECTORY}" || {
                echo "WARNING: Failed to create log directory: ${LOG_DIRECTORY}" >&2
                return 1
            }
            echo "INFO: Created log directory: ${LOG_DIRECTORY}"
        fi
        
        # Test write permissions
        if [[ ! -w "${LOG_DIRECTORY}" ]]; then
            echo "WARNING: Log directory is not writable: ${LOG_DIRECTORY}" >&2
            return 1
        fi
        
        echo "INFO: Log directory configured: ${LOG_DIRECTORY}"
        
        # Cleanup old logs on startup
        cleanup_old_logs
    fi
}

# Function to execute script with stdout/stderr capture
execute_with_capture() {
    local script_path="$1"
    local script_name=$(basename "$script_path")
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local exit_code=0
    
    # Setup log directory if not already done
    setup_log_directory >/dev/null 2>&1
    
    if [[ -n "${LOG_DIRECTORY}" && -d "${LOG_DIRECTORY}" && -w "${LOG_DIRECTORY}" ]]; then
        # Create log file with timestamp
        local log_file="${LOG_DIRECTORY}/${script_name}_${timestamp}.log"
        
        # Execute script, capturing stdout and stderr to log file
        # Use tee to also show output on console
        echo "Executing: $script_name (capturing output to: $log_file)" >&2
        
        # Capture both stdout and stderr, while still showing on console
        # Create a named pipe to process output for clean logging
        local temp_script="${LOG_DIRECTORY}/${script_name}_${timestamp}_temp.sh"
        cat > "$temp_script" << 'EOF'
#!/bin/bash
# Process input and output both to console and to file with color stripping
input_file="$1"
output_file="$2"

if [[ -f "$input_file" ]]; then
    # Show on console with colors
    cat "$input_file"
    # Write to file without colors
    strip_colors "$(cat "$input_file")" > "$output_file"
fi
EOF
        chmod +x "$temp_script"
        
        # Execute and capture
        local temp_capture="${LOG_DIRECTORY}/${script_name}_${timestamp}_capture.tmp"
        if "$script_path" 2>&1 | tee "$temp_capture"; then
            exit_code=0
            echo "✓ $script_name completed successfully (captured to: $log_file)" >&2
        else
            exit_code=$?
            echo "✗ $script_name failed with exit code $exit_code (captured to: $log_file)" >&2
        fi
        
        # Process the captured file to remove colors
        if [[ -f "$temp_capture" ]]; then
            strip_colors "$(cat "$temp_capture")" > "$log_file"
            rm -f "$temp_capture"
        fi
        
        # Clean up temp script
        rm -f "$temp_script"
        
        # Create a symlink to the latest log for easy access
        local latest_log="${LOG_DIRECTORY}/${script_name}_latest.log"
        ln -sf "$(basename "$log_file")" "$latest_log" 2>/dev/null || true
        
    else
        # Fallback to normal execution if log directory not available
        echo "Log directory not available, executing without capture: $script_name" >&2
        if "$script_path"; then
            exit_code=0
            echo "✓ $script_name completed successfully" >&2
        else
            exit_code=$?
            echo "✗ $script_name failed with exit code $exit_code" >&2
        fi
    fi
    
    return $exit_code
}

export -f log strip_colors should_log rotate_log_if_needed cleanup_old_logs handle_error setup_error_handling script_success command_exists validate_env_vars check_directory safe_execute safe_git setup_log_directory execute_with_capture
export RED GREEN YELLOW BLUE NC DEBUG_MODE