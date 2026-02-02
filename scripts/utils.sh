#!/bin/bash

# Enhanced Error handling and logging utilities for Repository Automation System
# Provides consistent error handling and configurable timestamped logging across all scripts
# 
# Configuration Variables (can be set in config.sh or environment):
# - TIMESTAMP_FORMAT: "default", "iso8601", "compact", "readable", "debug", "microseconds", "rfc3339", "syslog"
# - TIMESTAMP_TIMEZONE: "local", "utc", or specific timezone (e.g., "America/New_York")
# - LOG_LEVEL: "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR"
# - LOG_DIRECTORY: Directory for log files (optional)
# - LOG_MAX_SIZE_MB: Maximum log file size before rotation (default: 10)
# - LOG_MAX_FILES: Number of rotated log files to keep (default: 5)
# - LOG_RETENTION_DAYS: Days to keep old log files (default: 30)
# - DEBUG_MODE: Enable debug logging (default: false)

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to configure logging settings
configure_logging() {
    local timestamp_format="${1:-default}"
    local timezone="${2:-local}"
    
    # Validate and set timestamp format
    if validate_timestamp_format "$timestamp_format"; then
        export TIMESTAMP_FORMAT="$timestamp_format"
    else
        export TIMESTAMP_FORMAT="default"
        echo "WARNING: Invalid timestamp format '$timestamp_format', using 'default'" >&2
    fi
    
    # Validate and set timezone with enhanced support
    if validate_timezone "$timezone"; then
        export TIMESTAMP_TIMEZONE="$timezone"
    else
        export TIMESTAMP_TIMEZONE="local"
        echo "WARNING: Invalid timezone '$timezone', using 'local'" >&2
    fi
    
    # Test timestamp generation to catch issues early
    local test_timestamp
    if ! test_timestamp=$(generate_timestamp "$TIMESTAMP_FORMAT" "$TIMESTAMP_TIMEZONE" 2>/dev/null); then
        export TIMESTAMP_FORMAT="default"
        export TIMESTAMP_TIMEZONE="local"
        echo "WARNING: Timestamp generation failed, falling back to default format and local timezone" >&2
    fi
    
    # Log the configuration change if log function is available
    if declare -f log >/dev/null 2>&1; then
        log "DEBUG" "Logging configured: format=$TIMESTAMP_FORMAT, timezone=$TIMESTAMP_TIMEZONE"
        
        # Show example timestamp in debug mode
        if [[ "${DEBUG_MODE:-false}" == "true" ]]; then
            local example_timestamp=$(generate_timestamp "$TIMESTAMP_FORMAT" "$TIMESTAMP_TIMEZONE")
            log "DEBUG" "Example timestamp format: $example_timestamp"
        fi
    fi
}

# Function to recommend timestamp format based on use case
recommend_timestamp_format() {
    local use_case="${1:-general}"
    
    case "$use_case" in
        "production"|"prod")
            echo "Recommended format: iso8601"
            echo "Reason: Standardized, timezone-aware, machine-readable"
            echo "Usage: configure_logging 'iso8601' 'utc'"
            ;;
        "development"|"dev")
            echo "Recommended format: readable-precise"
            echo "Reason: Human-readable with millisecond precision for debugging"
            echo "Usage: configure_logging 'readable-precise' 'local'"
            ;;
        "debugging"|"debug")
            echo "Recommended format: debug"
            echo "Reason: Microsecond precision for detailed analysis"
            echo "Usage: configure_logging 'debug' 'local'"
            ;;
        "system"|"syslog")
            echo "Recommended format: syslog"
            echo "Reason: Compatible with system log management tools"
            echo "Usage: configure_logging 'syslog' 'local'"
            ;;
        "api"|"web")
            echo "Recommended format: rfc3339"
            echo "Reason: Web standard, JSON-friendly, precise"
            echo "Usage: configure_logging 'rfc3339' 'utc'"
            ;;
        "compact"|"space")
            echo "Recommended format: compact-precise"
            echo "Reason: Minimal space usage with precision"
            echo "Usage: configure_logging 'compact-precise' 'utc'"
            ;;
        "general"|*)
            echo "Recommended format: readable"
            echo "Reason: Good balance of readability and functionality"
            echo "Usage: configure_logging 'readable' 'local'"
            ;;
    esac
}

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

# Pure function to generate timestamp in specified format
generate_timestamp() {
    local format="${1:-${TIMESTAMP_FORMAT:-default}}"
    local timezone="${2:-${TIMESTAMP_TIMEZONE:-local}}"
    
    # Handle timezone setting
    local tz_flag=""
    if [[ "$timezone" == "utc" ]]; then
        tz_flag="-u"
    elif [[ "$timezone" != "local" && -n "$timezone" ]]; then
        # Try to set specific timezone (requires TZ environment variable)
        export TZ="$timezone"
    fi
    
    case "$format" in
        "iso8601")
            if command -v date >/dev/null 2>&1; then
                if [[ "$timezone" == "utc" ]]; then
                    date $tz_flag '+%Y-%m-%dT%H:%M:%SZ'
                else
                    date $tz_flag '-Iseconds' 2>/dev/null || date $tz_flag '+%Y-%m-%dT%H:%M:%S%z'
                fi
            fi
            ;;
        "rfc3339")
            # RFC 3339 format (more strict than ISO 8601)
            if command -v date >/dev/null 2>&1; then
                if [[ "$timezone" == "utc" ]]; then
                    date $tz_flag '+%Y-%m-%dT%H:%M:%S.%3NZ'
                else
                    date $tz_flag '+%Y-%m-%dT%H:%M:%S.%3N%:z' 2>/dev/null || \
                    date $tz_flag '+%Y-%m-%dT%H:%M:%S%z'
                fi
            fi
            ;;
        "syslog")
            # Standard syslog format for system integration
            if command -v date >/dev/null 2>&1; then
                date $tz_flag '+%b %d %H:%M:%S'
            fi
            ;;
        "compact")
            date $tz_flag '+%Y%m%d_%H%M%S'
            ;;
        "compact-precise")
            # Compact format with milliseconds for high-frequency logging
            if command -v date >/dev/null 2>&1; then
                date $tz_flag '+%Y%m%d_%H%M%S.%3N' 2>/dev/null || \
                date $tz_flag '+%Y%m%d_%H%M%S'
            fi
            ;;
        "readable")
            date $tz_flag '+%Y-%m-%d %H:%M:%S'
            ;;
        "readable-precise")
            # Readable format with milliseconds
            if command -v date >/dev/null 2>&1; then
                date $tz_flag '+%Y-%m-%d %H:%M:%S.%3N' 2>/dev/null || \
                date $tz_flag '+%Y-%m-%d %H:%M:%S'
            fi
            ;;
        "debug"|"microseconds")
            if command -v date >/dev/null 2>&1; then
                # Try to get microseconds, fallback to milliseconds, then seconds
                date $tz_flag '+%Y-%m-%d %H:%M:%S.%6N' 2>/dev/null || \
                date $tz_flag '+%Y-%m-%d %H:%M:%S.%3N' 2>/dev/null || \
                date $tz_flag '+%Y-%m-%d %H:%M:%S'
            fi
            ;;
        "default"|*)
            date $tz_flag '+%Y-%m-%d %H:%M:%S'
            ;;
    esac
    
    # Reset TZ if we modified it
    if [[ "$timezone" != "local" && "$timezone" != "utc" && -n "$timezone" ]]; then
        unset TZ 2>/dev/null || true
    fi
}

# Pure function to validate timestamp format
validate_timestamp_format() {
    local format="$1"
    local valid_formats=(
        "default" "iso8601" "rfc3339" "syslog" 
        "compact" "compact-precise" "readable" "readable-precise"
        "debug" "microseconds"
    )
    
    for valid_format in "${valid_formats[@]}"; do
        if [[ "$format" == "$valid_format" ]]; then
            return 0
        fi
    done
    return 1
}

# Pure function to validate timezone format
validate_timezone() {
    local timezone="$1"
    
    # Accept common timezone identifiers
    case "$timezone" in
        "local"|"utc"|"UTC"|"+0000"|"-0000"|"Z")
            return 0
            ;;
        *)
            # Check if it looks like a timezone identifier (e.g., America/New_York)
            if [[ "$timezone" =~ ^[A-Za-z_]+/[A-Za-z_]+$ ]] || \
               [[ "$timezone" =~ ^[+-][0-9]{2}:?[0-9]{2}$ ]]; then
                return 0
            fi
            return 1
            ;;
    esac
}

# Pure function to get supported timestamp formats with descriptions
get_supported_timestamp_formats() {
    cat << 'EOF'
default: Standard format (2026-01-31 08:58:01)
iso8601: ISO 8601 with timezone (2026-01-31T08:58:01+00:00)
rfc3339: RFC 3339 with milliseconds (2026-01-31T08:58:01.123Z)
syslog: Syslog format (Jan 31 08:58:01)
compact: Compact format (20260131_085801)
compact-precise: Compact with milliseconds (20260131_085801.123)
readable: Human-readable (2026-01-31 08:58:01)
readable-precise: Readable with milliseconds (2026-01-31 08:58:01.123)
debug: Debug with microseconds (2026-01-31 08:58:01.123456)
microseconds: Alias for debug format
EOF
}

# Pure function to test timestamp performance
benchmark_timestamp_generation() {
    local format="${1:-default}"
    local iterations="${2:-100}"
    local timezone="${3:-local}"
    
    if ! command -v time >/dev/null 2>&1; then
        echo "time command not available, cannot benchmark"
        return 1
    fi
    
    # Warm up
    generate_timestamp "$format" "$timezone" >/dev/null
    
    # Benchmark
    local start_time=$(date +%s.%N 2>/dev/null || date +%s)
    for ((i=1; i<=iterations; i++)); do
        generate_timestamp "$format" "$timezone" >/dev/null
    done
    local end_time=$(date +%s.%N 2>/dev/null || date +%s)
    
    local duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")
    local avg_time=$(echo "scale=6; $duration / $iterations" | bc 2>/dev/null || echo "0")
    
    echo "Benchmark results for '$format' format ($iterations iterations):"
    echo "  Total time: ${duration}s"
    echo "  Average per call: ${avg_time}s"
    echo "  Calls per second: $(echo "scale=0; $iterations / $duration" | bc 2>/dev/null || echo "0")"
}

# Pure function to get script name with fallback
get_script_name() {
    local script_name="${SCRIPT_NAME:-$(basename "${BASH_SOURCE[2]:-${BASH_SOURCE[1]:-$0}}")}"
    echo "$script_name"
}

# Pure function to format log entry
format_log_entry() {
    local level="$1"
    local timestamp="$2"
    local script_name="$3"
    local message="$4"
    
    echo "[${level}] ${timestamp} ${script_name}: $message"
}

# Enhanced logging function with configurable timestamps
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp_format="${TIMESTAMP_FORMAT:-default}"
    local timezone="${TIMESTAMP_TIMEZONE:-local}"
    
    # Validate timestamp format
    if ! validate_timestamp_format "$timestamp_format"; then
        timestamp_format="default"
    fi
    
    # Generate timestamp using pure function
    local timestamp=$(generate_timestamp "$timestamp_format" "$timezone")
    local script_name=$(get_script_name)
    
    # Check if we should log this level
    if ! should_log "$level"; then
        return 0
    fi
    
    # Format log entry using pure function
    local log_entry=$(format_log_entry "$level" "$timestamp" "$script_name" "$message")
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
    
    # Send to Telegram if enabled and configured
    if [[ "${TELEGRAM_ENABLED:-false}" == "true" ]]; then
        # Load Telegram modules if not already loaded
        if ! declare -F send_log_to_telegram >/dev/null 2>&1; then
            local telegram_module_dir
            telegram_module_dir="$(dirname "${BASH_SOURCE[0]}")/core"
            if [[ -f "${telegram_module_dir}/telegram_logger.sh" ]]; then
                source "${telegram_module_dir}/telegram_logger.sh"
            fi
        fi
        
        # Send log to Telegram asynchronously
        if declare -F send_log_to_telegram >/dev/null 2>&1; then
            send_log_to_telegram "$level" "$message" "$script_name" &
        fi
    fi
}

# Specialized logging function for change detection events
log_change_detection() {
    local repo_name="$1"
    local changes_count="$2"
    local reboot_triggered="$3"
    
    if [[ "$reboot_triggered" == "true" ]]; then
        log "WARNING" "Change detection in $repo_name: $changes_count changes detected - REBOOT TRIGGERED"
    else
        log "INFO" "Change detection in $repo_name: $changes_count changes detected - no reboot needed"
    fi
}

# Specialized logging function for system health checks
log_system_health() {
    local check_type="$1"
    local status="$2"
    local details="$3"
    
    if [[ "$status" == "pass" ]]; then
        log "INFO" "System health check $check_type: PASSED"
    else
        log "ERROR" "System health check $check_type: FAILED - $details"
    fi
}

# Specialized logging function for reboot events
log_reboot_event() {
    local reason="$1"
    local scheduled_time="$2"
    
    log "WARNING" "REBOOT SCHEDULED: $reason"
    log "INFO" "Reboot will occur at: $scheduled_time"
    log_system_state_snapshot
}

# Function to capture system state snapshot before reboot
log_system_state_snapshot() {
    if [[ -z "${LOG_DIRECTORY}" || ! -d "${LOG_DIRECTORY}" ]]; then
        return 0
    fi
    
    local snapshot_file="${LOG_DIRECTORY}/system-state-$(date +%Y%m%d-%H%M%S).json"
    
    {
        echo "{"
        echo "  \"timestamp\": \"$(date -Iseconds)\","
        echo "  \"uptime\": \"$(uptime)\","
        echo "  \"disk_usage\": \"$(df -h / | tail -1 | awk '{print $5}')\","
        echo "  \"memory_usage\": \"$(free -h | grep '^Mem:' | awk '{print $3"/"$2}')\","
        echo "  \"load_average\": \"$(uptime | awk -F'load average:' '{print $2}')\","
        echo "  \"git_status\": \"$(git status --porcelain 2>/dev/null | wc -l) files modified\""
        echo "}"
    } > "$snapshot_file"
    
    log "INFO" "System state snapshot saved: $snapshot_file"
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

# Function to execute opencode calls with enhanced timeout handling
safe_execute_opencode() {
    local opencode_cmd="$*"
    local start_time=$(date +%s)
    local timeout_action="${OPENCODE_TIMEOUT_ACTION:-terminate}"
    
    log "INFO" "Executing OpenCode call with timeout monitoring"
    log "DEBUG" "OpenCode command: $opencode_cmd"
    
    # Check if this is an opencode call
    if [[ "$opencode_cmd" != *"opencode"* ]]; then
        log "WARNING" "safe_execute_opencode called with non-opencode command, using safe_execute"
        safe_execute "$opencode_cmd"
        return $?
    fi
    
    # Track the process for timeout handling
    local temp_pid_file="/tmp/opencode_pid_$$"
    local temp_timeout_file="/tmp/opencode_timeout_$$"
    
    # Set up timeout monitoring
    if [[ "${OPENCODE_TIMEOUT_ENABLED:-true}" == "true" ]]; then
        log "DEBUG" "OpenCode timeout enabled: ${OPENCODE_TIMEOUT_SECONDS:-7200}s"
        
        # Execute the opencode command and capture its exit code
        local exit_code=0
        local timed_out=false
        
        # Use the configured OPencode_CMD which already includes timeout
        if eval "$opencode_cmd"; then
            exit_code=0
            log "DEBUG" "OpenCode command completed successfully"
        else
            exit_code=$?
            
            # Check if this was a timeout
            if [[ $exit_code -eq 124 ]]; then  # timeout command exit code
                timed_out=true
                log "ERROR" "OpenCode call timed out after ${OPENCODE_TIMEOUT_SECONDS:-7200} seconds"
                
                # Log timeout event if enabled
                if [[ "${OPENCODE_LOG_TIMEOUTS:-true}" == "true" ]]; then
                    local end_time=$(date +%s)
                    local duration=$((end_time - start_time))
                    log_timeout_event "$opencode_cmd" "$duration" "$start_time"
                fi
                
                # Handle timeout based on configured action
                case "$timeout_action" in
                    "terminate")
                        log "ERROR" "OpenCode call terminated due to timeout"
                        ;;
                    "escalate")
                        log "ERROR" "OpenCode call timed out - escalation needed"
                        # Create escalation marker file
                        echo "{\"timestamp\": $(date +%s), \"command\": \"$opencode_cmd\", \"duration\": $duration, \"action\": \"escalate\"}" > "$temp_timeout_file"
                        ;;
                    "retry")
                        log "WARNING" "OpenCode call timed out - retry logic not implemented"
                        ;;
                    *)
                        log "ERROR" "Unknown timeout action: $timeout_action"
                        ;;
                esac
            else
                log "ERROR" "OpenCode command failed with exit code $exit_code"
            fi
        fi
        
        # Cleanup temporary files
        rm -f "$temp_pid_file" "$temp_timeout_file"
        
        return $exit_code
    else
        # Timeout disabled, use regular safe_execute
        log "DEBUG" "OpenCode timeout disabled, using regular execution"
        safe_execute "$opencode_cmd"
        return $?
    fi
}

# Function to log timeout events
log_timeout_event() {
    local command="$1"
    local duration="$2"
    local start_timestamp="$3"
    
    if [[ "${OPENCODE_LOG_TIMEOUTS:-true}" == "true" ]]; then
        local log_entry="{
            \"event_type\": \"opencode_timeout\",
            \"timestamp\": $(date +%s),
            \"start_timestamp\": $start_timestamp,
            \"duration_seconds\": $duration,
            \"command\": \"$command\",
            \"timeout_seconds\": ${OPENCODE_TIMEOUT_SECONDS:-7200},
            \"action\": \"${OPENCODE_TIMEOUT_ACTION:-terminate}\"
        }"
        
        # Log to both regular log and dedicated timeout log if available
        log "ERROR" "OpenCode timeout: $duration seconds exceeded limit of ${OPENCODE_TIMEOUT_SECONDS:-7200}s"
        
        # Write to timeout log file if log directory is configured
        if [[ -n "${LOG_DIRECTORY:-}" && -d "$LOG_DIRECTORY" ]]; then
            local timeout_log="$LOG_DIRECTORY/opencode_timeouts.log"
            echo "$log_entry" >> "$timeout_log"
            log "DEBUG" "Timeout event logged to: $timeout_log"
        fi
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

# Function to merge origin/main into current ai branch safely
merge_origin_main_to_ai() {
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    local current_branch
    
    log "INFO" "Starting merge of origin/main into ai branch"
    
    # Change to repository directory
    cd "$repo_dir" || {
        log "ERROR" "Cannot change to directory: $repo_dir"
        return 1
    }
    
    # Get current branch to verify we're on ai branch
    current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || {
        log "ERROR" "Failed to determine current branch"
        return 1
    }
    
    if [[ "$current_branch" != "ai" ]]; then
        log "ERROR" "Not on ai branch (current: $current_branch)"
        return 1
    fi
    
    # Fetch latest changes from origin
    log "DEBUG" "Fetching latest changes from origin"
    if ! safe_git "fetch origin"; then
        log "ERROR" "Failed to fetch from origin"
        return 1
    fi
    
    # Check if there are any changes to merge
    local ai_commit=$(git rev-parse HEAD 2>/dev/null)
    local main_commit=$(git rev-parse origin/main 2>/dev/null)
    
    if [[ "$ai_commit" == "$main_commit" ]]; then
        log "INFO" "ai branch is already up to date with origin/main"
        return 0
    fi
    
    # Check if merge would cause conflicts
    log "DEBUG" "Checking for potential merge conflicts"
    local merge_base=$(git merge-base HEAD origin/main 2>/dev/null)
    local ai_tree=$(git rev-parse "${merge_base}:." 2>/dev/null)
    local main_tree=$(git rev-parse "origin/main:." 2>/dev/null)
    
    if [[ "$ai_tree" != "$main_tree" ]]; then
        # Trees differ - check if merge would be clean
        local merge_result
        if ! merge_result=$(git merge-tree "$(git merge-base HEAD origin/main 2>/dev/null)" HEAD origin/main 2>&1); then
            if echo "$merge_result" | grep -q "<<<<<<< \|======= \|>>>>>>>"; then
                log "WARNING" "Potential merge conflicts detected between ai and origin/main"
                log "INFO" "Proceeding with merge attempt - conflicts will be resolved if needed"
            fi
        fi
    fi
    
    # Perform the merge
    log "INFO" "Merging origin/main into ai branch"
    if git merge origin/main -m "Merge origin/main into ai branch (automated)"; then
        log "SUCCESS" "Successfully merged origin/main into ai branch"
        return 0
    else
        local exit_code=$?
        log "ERROR" "Failed to merge origin/main into ai branch (exit code: $exit_code)"
        
        # Check if merge failed due to conflicts
        if git status --porcelain 2>/dev/null | grep -q "^UU\|^AA\|^DD"; then
            log "ERROR" "Merge conflicts detected - automatic resolution needed"
            log "INFO" "Conflict files: $(git diff --name-only --diff-filter=U 2>/dev/null | tr '\n' ' ')"
            
            # Abort the merge to clean up
            git merge --abort 2>/dev/null || true
        fi
        
        return $exit_code
    fi
}

# Function to detect merge conflicts and create structured report for opencode
detect_merge_conflicts() {
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    local conflict_report_file="/tmp/opencode_conflict_report.json"
    
    cd "$repo_dir" || return 1
    
    log "INFO" "Detecting merge conflicts for opencode escalation"
    
    # Check if we're in a merge state
    if ! git status --porcelain 2>/dev/null | grep -q "^UU\|^AA\|^DD\|^##"; then
        log "DEBUG" "No merge conflicts detected"
        return 0
    fi
    
    # Gather conflict information
    local conflicted_files=($(git diff --name-only --diff-filter=U 2>/dev/null))
    local conflict_count=${#conflicted_files[@]}
    
    if [[ $conflict_count -eq 0 ]]; then
        log "DEBUG" "No conflicted files found"
        return 0
    fi
    
    log "WARNING" "Found $conflict_count conflicted files: ${conflicted_files[*]}"
    
    # Create structured conflict report for opencode
    cat > "$conflict_report_file" << EOF
{
  "conflict_type": "merge_conflicts",
  "conflict_count": $conflict_count,
  "conflicted_files": [
$(for file in "${conflicted_files[@]}"; do
    echo "    \"$file\","
done | sed '$s/,$//')
  ],
  "merge_details": {
    "current_branch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)",
    "target_branch": "origin/main",
    "ai_head": "$(git rev-parse HEAD 2>/dev/null)",
    "main_head": "$(git rev-parse origin/main 2>/dev/null)",
    "merge_base": "$(git merge-base HEAD origin/main 2>/dev/null)"
  },
  "resolution_suggestions": [
    "Review conflicted files and resolve manually",
    "Consider using 'git merge --abort' to cancel merge",
    "Use 'git status' to see detailed conflict markers",
    "Apply appropriate resolution strategy for each conflict"
  ],
  "escalation_required": true,
  "timestamp": "$(date -Iseconds)"
}
EOF
    
    log "INFO" "Conflict report created: $conflict_report_file"
    echo "$conflict_report_file"
    return $conflict_count
}

# =============================================================================
# REPOSITORY STATE VALIDATION FUNCTIONS
# =============================================================================

# Function to validate repository state before merge operations
validate_repository_state() {
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    local operation_context="$1"
    
    log "DEBUG" "Validating repository state for operation: $operation_context"
    
    local validation_errors=()
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        validation_errors+=("Not in a git repository")
    fi
    
    # Check for lock files
    if [[ -f "$repo_dir/.git/index.lock" ]]; then
        validation_errors+=("Git index lock file exists")
    fi
    
    # Check if repository is in a valid state
    if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
        validation_errors+=("Invalid HEAD reference")
    fi
    
    # Check for detached HEAD (may be okay depending on context)
    local current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [[ "$current_branch" == "HEAD" ]]; then
        validation_errors+=("Repository in detached HEAD state")
    fi
    
    # Check git directory permissions
    if [[ ! -r "$repo_dir/.git" || ! -w "$repo_dir/.git" ]]; then
        validation_errors+=("Git directory permission issues")
    fi
    
    # Check disk space (basic check)
    local available_space=$(df "$repo_dir" | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 1024 ]]; then  # Less than 1MB
        validation_errors+=("Insufficient disk space")
    fi
    
    # Log validation results
    if [[ ${#validation_errors[@]} -eq 0 ]]; then
        log "DEBUG" "Repository state validation passed for: $operation_context"
        return 0
    else
        log "ERROR" "Repository state validation failed for: $operation_context"
        for error in "${validation_errors[@]}"; do
            log "ERROR" "  - $error"
        done
        return 1
    fi
}

# Function to get comprehensive repository health status
get_repository_health_status() {
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    
    local health_status="{
        \"repository\": \"$(basename "$repo_dir")\",
        \"timestamp\": \"$(date -Iseconds)\",
        \"git_status\": \"$(git status --porcelain 2>/dev/null | wc -l)\",
        \"current_branch\": \"$(git rev-parse --abbrev-ref HEAD 2>/dev/null)\",
        \"head_commit\": \"$(git rev-parse HEAD 2>/dev/null)\",
        \"origin_status\": \"$(git remote -v 2>/dev/null | grep -c origin || echo 0)\",
        \"staged_files\": \"$(git diff --cached --name-only 2>/dev/null | wc -l)\",
        \"modified_files\": \"$(git diff --name-only 2>/dev/null | wc -l)\",
        \"untracked_files\": \"$(git ls-files --others --exclude-standard 2>/dev/null | wc -l)\",
        \"last_commit_time\": \"$(git log -1 --format=%ci 2>/dev/null)\",
        \"lock_files\": \"$(find "$repo_dir/.git" -name "*.lock" 2>/dev/null | wc -l)\",
        \"disk_usage\": \"$(du -sh "$repo_dir" 2>/dev/null | cut -f1)\"
    }"
    
    echo "$health_status"
}

# =============================================================================
# MERGE ERROR HANDLING AND LOGGING SYSTEM
# =============================================================================

# Merge error type definitions
declare -A MERGE_ERROR_TYPES=(
    ["NETWORK_FAILURE"]="Network connectivity issues preventing git operations"
    ["PERMISSION_DENIED"]="Insufficient permissions to perform git operations"
    ["REPOSITORY_CORRUPT"]="Git repository in corrupted state, needs repair"
    ["MERGE_CONFLICT"]="Merge conflicts requiring manual resolution"
    ["FAST_FORWARD_FAILED"]="Fast-forward merge failed unexpectedly"
    ["BRANCH_NOT_FOUND"]="Target or source branch does not exist"
    ["DETACHED_HEAD"]="Repository in detached HEAD state"
    ["LOCK_FILE_EXISTS"]="Git lock files indicating concurrent operations"
    ["DISK_FULL"]="Insufficient disk space for git operations"
    ["TIMEOUT"]="Operation timed out during execution"
    ["UNKNOWN"]="Unknown or unexpected error during merge operation"
)

# Function to classify merge error type
classify_merge_error() {
    local exit_code="$1"
    local error_output="$2"
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    
    log "DEBUG" "Classifying merge error (exit code: $exit_code) in $repo_dir"
    
    # Check for specific error patterns
    if [[ "$error_output" =~ (connection|refused|timeout|network|unable to access) ]]; then
        echo "NETWORK_FAILURE"
    elif [[ "$error_output" =~ (permission|denied|access denied|read-only) ]]; then
        echo "PERMISSION_DENIED"
    elif [[ "$error_output" =~ (corrupt|broken|invalid|object not found) ]]; then
        echo "REPOSITORY_CORRUPT"
    elif [[ "$error_output" =~ (conflict|CONFLICT|merge|<<<<<<<<) ]]; then
        echo "MERGE_CONFLICT"
    elif [[ "$error_output" =~ (fast-forward|fast-forward only) ]]; then
        echo "FAST_FORWARD_FAILED"
    elif [[ "$error_output" =~ (not found|doesnt exist|branch.*not found) ]]; then
        echo "BRANCH_NOT_FOUND"
    elif [[ "$error_output" =~ (detached head|detached HEAD) ]]; then
        echo "DETACHED_HEAD"
    elif [[ "$error_output" =~ (lock file|index.lock|unable to create) ]]; then
        echo "LOCK_FILE_EXISTS"
    elif [[ "$error_output" =~ (no space left|disk full|insufficient space) ]]; then
        echo "DISK_FULL"
    elif [[ "$exit_code" -eq 124 ]]; then
        echo "TIMEOUT"
    else
        echo "UNKNOWN"
    fi
}

# Function to log merge attempt details
log_merge_attempt() {
    local operation="$1"
    local source_branch="$2"
    local target_branch="$3"
    local source_commit="$4"
    local target_commit="$5"
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    
    local timestamp=$(generate_timestamp "${TIMESTAMP_FORMAT:-default}" "${TIMESTAMP_TIMEZONE:-local}")
    local script_name=$(get_script_name)
    
    # Create structured merge event log
    local merge_event="{
    \"event_type\": \"merge_attempt\",
    \"operation\": \"$operation\",
    \"timestamp\": \"$timestamp\",
    \"repository\": \"$(basename "$repo_dir")\",
    \"source_branch\": \"$source_branch\",
    \"target_branch\": \"$target_branch\",
    \"source_commit\": \"$source_commit\",
    \"target_commit\": \"$target_commit\",
    \"working_directory\": \"$repo_dir\"
    }"
    
    log "INFO" "MERGE ATTEMPT: $operation - $source_branch -> $target_branch"
    log "DEBUG" "Merge event details: $merge_event"
    
    # Log to file if directory is configured
    if [[ -n "${LOG_DIRECTORY}" && -d "${LOG_DIRECTORY}" ]]; then
        local merge_log="${LOG_DIRECTORY}/merge_events.log"
        echo "$merge_event" >> "$merge_log"
    fi
}

# Function to log merge conflict detection results
log_merge_conflict_detection() {
    local conflicted_files=("$@")
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    local conflict_count=${#conflicted_files[@]}
    
    local timestamp=$(generate_timestamp "${TIMESTAMP_FORMAT:-default}" "${TIMESTAMP_TIMEZONE:-local}")
    
    log "WARNING" "MERGE CONFLICT DETECTED: $conflict_count conflicted files"
    
    # Create structured conflict detection log
    local conflict_event="{
    \"event_type\": \"merge_conflict_detected\",
    \"timestamp\": \"$timestamp\",
    \"repository\": \"$(basename "$repo_dir")\",
    \"conflict_count\": $conflict_count,
    \"conflicted_files\": [
        $(printf '"%s",' "${conflicted_files[@]}" | sed 's/,$//')
    ],
    \"ai_branch_head\": \"$(git rev-parse HEAD 2>/dev/null)\",
    \"main_branch_head\": \"$(git rev-parse origin/main 2>/dev/null)\",
    \"merge_base\": \"$(git merge-base HEAD origin/main 2>/dev/null)\"
    }"
    
    log "DEBUG" "Conflict detection details: $conflict_event"
    
    # Log to file if directory is configured
    if [[ -n "${LOG_DIRECTORY}" && -d "${LOG_DIRECTORY}" ]]; then
        local merge_log="${LOG_DIRECTORY}/merge_events.log"
        echo "$conflict_event" >> "$merge_log"
    fi
    
    # Log individual conflicted files
    for file in "${conflicted_files[@]}"; do
        log "DEBUG" "Conflicted file: $file"
    done
}

# Function to log opencode escalation trigger
log_opencode_escalation() {
    local escalation_reason="$1"
    local conflict_report_file="$2"
    local operation_context="$3"
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    
    local timestamp=$(generate_timestamp "${TIMESTAMP_FORMAT:-default}" "${TIMESTAMP_TIMEZONE:-local}")
    
    log "ERROR" "OPENCODE ESCALATION TRIGGERED: $escalation_reason"
    log "INFO" "Escalation context: $operation_context"
    
    if [[ -n "$conflict_report_file" && -f "$conflict_report_file" ]]; then
        log "INFO" "Conflict report generated: $conflict_report_file"
    fi
    
    # Create structured escalation log
    local escalation_event="{
    \"event_type\": \"opencode_escalation\",
    \"timestamp\": \"$timestamp\",
    \"repository\": \"$(basename "$repo_dir")\",
    \"escalation_reason\": \"$escalation_reason\",
    \"operation_context\": \"$operation_context\",
    \"conflict_report\": \"$conflict_report_file\",
    \"current_branch\": \"$(git rev-parse --abbrev-ref HEAD 2>/dev/null)\",
    \"working_tree_clean\": \"$(git status --porcelain 2>/dev/null | wc -l)\",
    \"git_status\": \"$(git status --porcelain 2>/dev/null | head -5 | tr '\n' ';')\"
    }"
    
    log "DEBUG" "Escalation details: $escalation_event"
    
    # Log to file if directory is configured
    if [[ -n "${LOG_DIRECTORY}" && -d "${LOG_DIRECTORY}" ]]; then
        local merge_log="${LOG_DIRECTORY}/merge_events.log"
        echo "$escalation_event" >> "$merge_log"
    fi
}

# Function to log merge resolution outcomes
log_merge_resolution_outcome() {
    local resolution_type="$1"
    local resolved_files_count="$2"
    local resolution_time_seconds="$3"
    local operation_context="$4"
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    
    local timestamp=$(generate_timestamp "${TIMESTAMP_FORMAT:-default}" "${TIMESTAMP_TIMEZONE:-local}")
    
    log "SUCCESS" "MERGE RESOLUTION: $resolution_type - $resolved_files_count files resolved"
    
    # Create structured resolution log
    local resolution_event="{
    \"event_type\": \"merge_resolution\",
    \"timestamp\": \"$timestamp\",
    \"repository\": \"$(basename "$repo_dir")\",
    \"resolution_type\": \"$resolution_type\",
    \"resolved_files_count\": $resolved_files_count,
    \"resolution_time_seconds\": $resolution_time_seconds,
    \"operation_context\": \"$operation_context\",
    \"final_branch_head\": \"$(git rev-parse HEAD 2>/dev/null)\",
    \"merge_successful\": \"$(git status --porcelain 2>/dev/null | grep -q "^UU" && echo "false" || echo "true")\"
    }"
    
    log "DEBUG" "Resolution details: $resolution_event"
    
    # Log to file if directory is configured
    if [[ -n "${LOG_DIRECTORY}" && -d "${LOG_DIRECTORY}" ]]; then
        local merge_log="${LOG_DIRECTORY}/merge_events.log"
        echo "$resolution_event" >> "$merge_log"
    fi
}

# Function to perform automatic rollback on merge failures
rollback_merge_on_failure() {
    local error_type="$1"
    local operation_context="$2"
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    
    log "WARNING" "Initiating rollback due to $error_type failure"
    log "DEBUG" "Rollback context: $operation_context"
    
    local rollback_successful=true
    local rollback_actions=()
    
    # Check if we're in a merge state and abort if necessary
    if git status --porcelain 2>/dev/null | grep -q "^UU\|^AA\|^DD"; then
        log "INFO" "Aborting merge to clean up conflict state"
        if git merge --abort 2>/dev/null; then
            rollback_actions+=("merge_aborted")
            log "DEBUG" "Merge successfully aborted"
        else
            rollback_successful=false
            rollback_actions+=("merge_abort_failed")
            log "ERROR" "Failed to abort merge"
        fi
    fi
    
    # Reset to known good state if needed
    if [[ "$error_type" == "REPOSITORY_CORRUPT" || "$rollback_successful" == false ]]; then
        log "INFO" "Resetting to HEAD to ensure clean state"
        if git reset --hard HEAD 2>/dev/null; then
            rollback_actions+=("reset_to_head")
            log "DEBUG" "Successfully reset to HEAD"
        else
            rollback_successful=false
            rollback_actions+=("reset_failed")
            log "ERROR" "Failed to reset to HEAD"
        fi
    fi
    
    # Clean up any stray lock files
    local lock_file="$repo_dir/.git/index.lock"
    if [[ -f "$lock_file" ]]; then
        log "INFO" "Removing git lock file: $lock_file"
        rm -f "$lock_file" 2>/dev/null && rollback_actions+=("lock_removed")
    fi
    
    # Log rollback outcome
    if [[ "$rollback_successful" == true ]]; then
        log "SUCCESS" "Rollback completed successfully: ${rollback_actions[*]}"
        return 0
    else
        log "ERROR" "Rollback partially failed: ${rollback_actions[*]}"
        return 1
    fi
}

# Function to preserve state for opencode intervention
preserve_state_for_opencode() {
    local operation_context="$1"
    local error_type="$2"
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    
    local state_dir="/tmp/opencode_state_$(basename "$repo_dir")_$(date +%s)"
    mkdir -p "$state_dir"
    
    log "INFO" "Preserving state for opencode intervention in: $state_dir"
    
    # Save current git state
    git status > "$state_dir/git_status.txt" 2>/dev/null
    git log --oneline -10 > "$state_dir/git_history.txt" 2>/dev/null
    git diff --cached > "$state_dir/staged_changes.diff" 2>/dev/null || true
    git diff > "$state_dir/working_changes.diff" 2>/dev/null || true
    
    # Save conflict files if any
    if git status --porcelain 2>/dev/null | grep -q "^UU"; then
        local conflicted_files=($(git diff --name-only --diff-filter=U 2>/dev/null))
        for file in "${conflicted_files[@]}"; do
            cp "$file" "$state_dir/" 2>/dev/null || true
        done
    fi
    
    # Create state metadata
    cat > "$state_dir/metadata.json" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "repository": "$(basename "$repo_dir")",
    "operation_context": "$operation_context",
    "error_type": "$error_type",
    "current_branch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)",
    "current_commit": "$(git rev-parse HEAD 2>/dev/null)",
    "origin_main_commit": "$(git rev-parse origin/main 2>/dev/null)",
    "merge_base": "$(git merge-base HEAD origin/main 2>/dev/null)",
    "working_tree_clean": $(git status --porcelain 2>/dev/null | wc -l),
    "preserved_files": $(ls "$state_dir" | wc -l)
}
EOF
    
    log "INFO" "State preservation completed: $state_dir"
    echo "$state_dir"
}

# Function to implement clean retry logic after opencode resolution
retry_merge_after_opencode_resolution() {
    local operation_context="$1"
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    local max_attempts="${2:-3}"
    
    log "INFO" "Attempting retry after opencode resolution: $operation_context"
    
    for ((attempt=1; attempt<=max_attempts; attempt++)); do
        log "INFO" "Retry attempt $attempt of $max_attempts"
        
        # Check if repository is in a clean state
        if git status --porcelain 2>/dev/null | grep -q "^UU\|^AA\|^DD"; then
            log "WARNING" "Still in conflict state, cannot retry (attempt $attempt)"
            return 2
        fi
        
        # Fetch latest changes
        if ! safe_git "fetch origin"; then
            log "ERROR" "Failed to fetch from origin during retry $attempt"
            continue
        fi
        
        # Attempt the merge
        if git merge origin/main -m "Merge origin/main into ai branch (retry after opencode resolution - attempt $attempt)"; then
            log "SUCCESS" "Retry successful on attempt $attempt"
            log_merge_resolution_outcome "automatic_retry" "0" "0" "$operation_context"
            return 0
        else
            local exit_code=$?
            log "WARNING" "Retry $attempt failed with exit code: $exit_code"
            
            # Clean up and continue to next attempt
            git merge --abort 2>/dev/null || true
        fi
    done
    
    log "ERROR" "All retry attempts failed after opencode resolution"
    return 1
}

# Enhanced merge function with opencode escalation support
merge_origin_main_to_ai_with_escalation() {
    local repo_dir="${GIT_REPO_DIR:-$(pwd)}"
    local current_branch
    local conflict_report_file
    local operation_start_time=$(date +%s)
    
    log "INFO" "Starting enhanced merge of origin/main into ai branch with comprehensive error handling"
    
    # Validate repository state before proceeding
    if ! validate_repository_state "pre_merge_validation"; then
        local error_type="REPOSITORY_CORRUPT"
        log "ERROR" "Repository state validation failed, cannot proceed with merge"
        
        # Attempt to get health status for debugging
        local health_status=$(get_repository_health_status)
        log "DEBUG" "Repository health status: $health_status"
        
        return 1
    fi
    
    # Change to repository directory
    cd "$repo_dir" || {
        local error_type="REPOSITORY_CORRUPT"
        log "ERROR" "Cannot change to directory: $repo_dir"
        log_merge_attempt "merge_origin_main_to_ai" "origin/main" "ai" "unknown" "unknown"
        return 1
    }
    
    # Get current branch to verify we're on ai branch
    current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || {
        local error_type="DETACHED_HEAD"
        log "ERROR" "Failed to determine current branch"
        log_merge_attempt "merge_origin_main_to_ai" "origin/main" "ai" "unknown" "unknown"
        return 1
    }
    
    if [[ "$current_branch" != "ai" ]]; then
        local error_type="BRANCH_NOT_FOUND"
        log "ERROR" "Not on ai branch (current: $current_branch)"
        log_merge_attempt "merge_origin_main_to_ai" "origin/main" "ai" "unknown" "unknown"
        return 1
    fi
    
    # Fetch latest changes from origin
    log "DEBUG" "Fetching latest changes from origin"
    if ! safe_git "fetch origin"; then
        local error_type="NETWORK_FAILURE"
        log "ERROR" "Failed to fetch from origin"
        log_merge_attempt "merge_origin_main_to_ai" "origin/main" "ai" "unknown" "unknown"
        return 1
    fi
    
    # Get commit information for logging
    local ai_commit=$(git rev-parse HEAD 2>/dev/null)
    local main_commit=$(git rev-parse origin/main 2>/dev/null)
    
    # Log the merge attempt
    log_merge_attempt "merge_origin_main_to_ai" "origin/main" "ai" "$main_commit" "$ai_commit"
    
    # Check if there are any changes to merge
    if [[ "$ai_commit" == "$main_commit" ]]; then
        log "INFO" "ai branch is already up to date with origin/main"
        log_merge_resolution_outcome "no_merge_needed" "0" "0" "up_to_date"
        return 0
    fi
    
    # Perform the merge with enhanced error handling
    log "INFO" "Attempting merge of origin/main into ai branch"
    local merge_output
    local merge_exit_code
    
    if merge_output=$(git merge origin/main -m "Merge origin/main into ai branch (automated)" 2>&1); then
        local operation_time=$(($(date +%s) - operation_start_time))
        log "SUCCESS" "Successfully merged origin/main into ai branch in ${operation_time}s"
        log_merge_resolution_outcome "automatic_merge" "0" "$operation_time" "initial_attempt"
        return 0
    else
        merge_exit_code=$?
        local error_type=$(classify_merge_error "$merge_exit_code" "$merge_output")
        local operation_time=$(($(date +%s) - operation_start_time))
        
        log "ERROR" "Merge failed with exit code: $merge_exit_code, error type: $error_type"
        log "DEBUG" "Merge error output: $merge_output"
        
        # Handle different error types appropriately
        case "$error_type" in
            "MERGE_CONFLICT")
                # Detect conflicts and create escalation report
                conflict_report_file=$(detect_merge_conflicts)
                local conflict_count=$?
                
                if [[ $conflict_count -gt 0 ]]; then
                    local conflicted_files=($(git diff --name-only --diff-filter=U 2>/dev/null))
                    log_merge_conflict_detection "${conflicted_files[@]}"
                    
                    log "ERROR" "Merge conflicts detected - escalating to opencode for resolution"
                    log_opencode_escalation "merge_conflicts_detected" "$conflict_report_file" "initial_merge_attempt"
                    
                    # Preserve state for opencode intervention
                    local state_dir=$(preserve_state_for_opencode "initial_merge_attempt" "$error_type")
                    
                    # Log to conflict report the state directory
                    if [[ -n "$conflict_report_file" && -f "$conflict_report_file" ]]; then
                        # Add state directory to conflict report
                        sed -i "s/}/,  \"state_directory\": \"$state_dir\"}/" "$conflict_report_file"
                    fi
                    
                    log "WARNING" "Merge state preserved - opencode intervention required"
                    return 2  # Special exit code for conflicts
                else
                    log "WARNING" "No conflicts found despite merge failure - treating as other error"
                fi
                ;;
                
            "NETWORK_FAILURE"|"TIMEOUT")
                log "ERROR" "Merge failed due to $error_type - will retry"
                rollback_merge_on_failure "$error_type" "merge_attempt"
                return $merge_exit_code
                ;;
                
            "LOCK_FILE_EXISTS")
                log "WARNING" "Git lock file detected - attempting cleanup"
                local lock_file="$repo_dir/.git/index.lock"
                if [[ -f "$lock_file" ]]; then
                    rm -f "$lock_file" && log "INFO" "Git lock file removed"
                    # Retry after cleanup
                    if git merge origin/main -m "Merge origin/main into ai branch (after lock cleanup)"; then
                        log "SUCCESS" "Merge succeeded after lock cleanup"
                        return 0
                    fi
                fi
                ;;
                
            *)
                log "ERROR" "Unhandled merge error type: $error_type"
                ;;
        esac
        
        # For non-conflict failures, attempt rollback and clean up
        rollback_merge_on_failure "$error_type" "merge_attempt"
        
        # Create error report for debugging
        local error_report_file="/tmp/merge_error_report_$(date +%s).json"
        cat > "$error_report_file" << EOF
{
    "error_type": "$error_type",
    "exit_code": $merge_exit_code,
    "operation_time_seconds": $operation_time,
    "error_output": "$merge_output",
    "repository": "$(basename "$repo_dir")",
    "current_branch": "$current_branch",
    "ai_commit": "$ai_commit",
    "main_commit": "$main_commit",
    "timestamp": "$(date -Iseconds)",
    "git_status": "$(git status --porcelain 2>/dev/null | tr '\n' ';')",
    "error_description": "${MERGE_ERROR_TYPES[$error_type]}"
}
EOF
        
        log "INFO" "Error report created: $error_report_file"
        log "ERROR" "Merge failed for $error_type reasons - cleanup completed"
        
        return $merge_exit_code
    fi
}

# =============================================================================
# BEADS QUERY FUNCTIONS
# =============================================================================

# Function to check if there are any open bead tasks for a repository
# Returns: 0 if open tasks exist, 1 if no open tasks, 2 if error occurred
has_open_bead_tasks() {
    local repo_dir="${1:-$(pwd)}"
    local timeout_seconds="${2:-30}"
    
    log "DEBUG" "Checking for open bead tasks in repository: $(basename "$repo_dir")"
    
    # Change to repository directory if specified
    if [[ -n "$1" ]]; then
        cd "$repo_dir" || {
            log "ERROR" "Cannot change to directory: $repo_dir"
            return 2
        }
    fi
    
    # Check if this is a beads-enabled repository
    if [[ ! -d ".beads" ]]; then
        log "DEBUG" "No .beads directory found - not a beads-enabled repository"
        return 1
    fi
    
    # Check if bd command is available
    if ! command_exists bd; then
        log "ERROR" "bd command not found - beads CLI is required"
        return 2
    fi
    
    # Query for open tasks with timeout
    local open_tasks_json
    local start_time=$(date +%s)
    
    log "DEBUG" "Querying beads for open tasks (timeout: ${timeout_seconds}s)"
    
    # Use timeout to prevent hanging
    if command -v timeout >/dev/null 2>&1; then
        open_tasks_json=$(timeout "$timeout_seconds" bd list --status=open --json 2>/dev/null) || {
            local exit_code=$?
            if [[ $exit_code -eq 124 ]]; then
                log "WARNING" "Beads query timed out after ${timeout_seconds}s"
            else
                log "ERROR" "Beads query failed with exit code: $exit_code"
            fi
            return 2
        }
    else
        # Fallback without timeout command
        open_tasks_json=$(bd list --status=open --json 2>/dev/null) || {
            local exit_code=$?
            log "ERROR" "Beads query failed with exit code: $exit_code"
            return 2
        }
    fi
    
    local query_time=$(($(date +%s) - start_time))
    log "DEBUG" "Beads query completed in ${query_time}s"
    
    # Parse JSON response to count open tasks
    local open_tasks_count=0
    if [[ -n "$open_tasks_json" ]]; then
        # Extract count from JSON array (simplified parsing)
        if echo "$open_tasks_json" | jq -e '. | length' >/dev/null 2>&1; then
            open_tasks_count=$(echo "$open_tasks_json" | jq '. | length' 2>/dev/null || echo 0)
        else
            # Fallback parsing without jq
            open_tasks_count=$(echo "$open_tasks_json" | grep -o '"id"' | wc -l)
        fi
    fi
    
    log "INFO" "Found $open_tasks_count open bead tasks in $(basename "$repo_dir")"
    
    # Return based on count
    if [[ $open_tasks_count -gt 0 ]]; then
        return 0  # Open tasks exist
    else
        return 1  # No open tasks
    fi
}

# Function to get count of open bead tasks
# Returns: number of open tasks, or -1 on error
get_open_bead_tasks_count() {
    local repo_dir="${1:-$(pwd)}"
    local timeout_seconds="${2:-30}"
    
    # Change to repository directory if specified
    if [[ -n "$1" ]]; then
        cd "$repo_dir" || {
            log "ERROR" "Cannot change to directory: $repo_dir"
            echo "-1"
            return 1
        }
    fi
    
    # Check if this is a beads-enabled repository
    if [[ ! -d ".beads" ]]; then
        log "DEBUG" "No .beads directory found - not a beads-enabled repository"
        echo "0"
        return 1
    fi
    
    # Check if bd command is available
    if ! command_exists bd; then
        log "ERROR" "bd command not found - beads CLI is required"
        echo "-1"
        return 2
    fi
    
    # Query for open tasks
    local open_tasks_json
    if command -v timeout >/dev/null 2>&1; then
        open_tasks_json=$(timeout "$timeout_seconds" bd list --status=open --json 2>/dev/null) || {
            echo "-1"
            return 2
        }
    else
        open_tasks_json=$(bd list --status=open --json 2>/dev/null) || {
            echo "-1"
            return 2
        }
    fi
    
    # Parse and return count
    if [[ -n "$open_tasks_json" ]]; then
        if echo "$open_tasks_json" | jq -e '. | length' >/dev/null 2>&1; then
            echo "$open_tasks_json" | jq '. | length' 2>/dev/null || echo "0"
        else
            # Fallback parsing
            echo "$open_tasks_json" | grep -o '"id"' | wc -l
        fi
    else
        echo "0"
    fi
}

# Function to log task availability decisions
log_task_availability_decision() {
    local repo_name="$1"
    local has_tasks="$2"
    local task_count="${3:-0}"
    local decision="${4:-proceed}"
    local reason="${5:-}"
    
    if [[ "$has_tasks" == "true" ]]; then
        log "INFO" "Task availability check for $repo_name: FOUND $task_count open tasks - decision: $decision"
    else
        log "INFO" "Task availability check for $repo_name: NO open tasks found - decision: $decision ${reason:+($reason)}"
    fi
}

export -f log strip_colors should_log rotate_log_if_needed cleanup_old_logs handle_error setup_error_handling script_success command_exists validate_env_vars check_directory safe_execute safe_execute_opencode safe_git setup_log_directory execute_with_capture merge_origin_main_to_ai detect_merge_conflicts merge_origin_main_to_ai_with_escalation
export -f log_change_detection log_system_health log_reboot_event log_system_state_snapshot
export -f generate_timestamp validate_timestamp_format validate_timezone get_script_name format_log_entry configure_logging
export -f get_supported_timestamp_formats benchmark_timestamp_generation recommend_timestamp_format
export -f classify_merge_error log_merge_attempt log_merge_conflict_detection log_opencode_escalation log_merge_resolution_outcome log_timeout_event
export -f rollback_merge_on_failure preserve_state_for_opencode retry_merge_after_opencode_resolution
export -f validate_repository_state get_repository_health_status
export -f has_open_bead_tasks get_open_bead_tasks_count log_task_availability_decision
export RED GREEN YELLOW BLUE NC DEBUG_MODE