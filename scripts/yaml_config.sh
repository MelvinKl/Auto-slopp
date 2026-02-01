#!/bin/bash

# YAML Configuration Parser for Repository Automation System
# Provides functions to read config.yaml values

# Set script name for logging identification
SCRIPT_NAME="yaml_config"

# Load utilities first - use existing SCRIPT_DIR or compute relative to this file
if [[ -z "$SCRIPT_DIR" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
# Since utils.sh is in the same directory as this script, we can source it directly
source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

# Set up error handling
setup_error_handling

# Function to get script directory
get_script_dir() {
    cd "$(dirname "${BASH_SOURCE[1]}")" && pwd
}

# Function to read YAML configuration
read_yaml_config() {
    local config_file="$1"
    local key="$2"
    local default_value="$3"
    
    if [[ ! -f "$config_file" ]]; then
        log "ERROR" "Configuration file $config_file not found"
        echo "$default_value"
        return 1
    fi
    
    # Simple YAML parsing using grep and sed
    # This handles basic key: value pairs, ignoring comments
    local value=$(grep "^[[:space:]]*$key:" "$config_file" | grep -v "#" | sed "s/^[[:space:]]*$key:[[:space:]]*//" | sed 's/[[:space:]]*#.*//' | sed 's/^["'"'"']//' | sed 's/["'"'"']$//' | sed 's/[[:space:]]*$//')
    
    if [[ -z "$value" ]]; then
        log "DEBUG" "Using default value for key: $key"
        echo "$default_value"
    else
        log "DEBUG" "Found configuration value: $key = $value"
        echo "$value"
    fi
}

# Function to read YAML array with a simpler direct approach
read_yaml_array() {
    local config_file="$1"
    local key="$2"
    local -n array_ref=$3
    
    if [[ ! -f "$config_file" ]]; then
        log "ERROR" "Configuration file $config_file not found"
        return 1
    fi
    
    # Use mapfile to avoid subshell issues
    local temp_array=()
    
    # Simple approach: find the array section and extract items
    # This works for the specific structure in config.yaml
    case "$key" in
        "branch_protection.protected_branches")
            # Extract lines after "protected_branches:" and before the next key
            mapfile -t temp_array < <(awk '
            /^#/ { next }
            /protected_branches:/ { 
                in_array = 1
                next 
            }
            in_array && /^[[:space:]]+[a-zA-Z_]/ { 
                in_array = 0
                next 
            }
            in_array && /^[[:space:]]+-/ {
                gsub(/^[[:space:]]+-[[:space:]]*["'"'"']/, "")
                gsub(/["'"'"'][[:space:]]*$/, "")
                gsub(/^[[:space:]]+-[[:space:]]*/, "")
                gsub(/[[:space:]]+$/, "")
                if (length($0) > 0) print $0
            }
            ' "$config_file")
            ;;
        "branch_protection.protection_patterns")
            mapfile -t temp_array < <(awk '
            /^#/ { next }
            /protection_patterns:/ { 
                in_array = 1
                next 
            }
            in_array && /^[[:space:]]+[a-zA-Z_]/ { 
                in_array = 0
                next 
            }
            in_array && /^[[:space:]]+-/ {
                gsub(/^[[:space:]]+-[[:space:]]*["'"'"']/, "")
                gsub(/["'"'"'][[:space:]]*$/, "")
                gsub(/^[[:space:]]+-[[:space:]]*/, "")
                gsub(/[[:space:]]+$/, "")
                if (length($0) > 0) print $0
            }
            ' "$config_file")
            ;;
        "branch_protection.require_explicit_confirmation_for")
            mapfile -t temp_array < <(awk '
            /^#/ { next }
            /require_explicit_confirmation_for:/ { 
                in_array = 1
                next 
            }
            in_array && /^[[:space:]]+[a-zA-Z_]/ { 
                in_array = 0
                next 
            }
            in_array && /^[[:space:]]+-/ {
                gsub(/^[[:space:]]+-[[:space:]]*["'"'"']/, "")
                gsub(/["'"'"'][[:space:]]*$/, "")
                gsub(/^[[:space:]]+-[[:space:]]*/, "")
                gsub(/[[:space:]]+$/, "")
                if (length($0) > 0) print $0
            }
            ' "$config_file")
            ;;
        *)
            log "WARNING" "Unknown array key: $key"
            ;;
    esac
    
    # Copy temp array to reference array
    for item in "${temp_array[@]}"; do
        [[ -n "$item" ]] && array_ref+=("$item")
    done
    
    log "DEBUG" "Loaded ${#array_ref[@]} items for array: $key"
}

# Function to load all configuration
load_config() {
    local config_file="${1:-$(get_script_dir)/config.yaml}"
    
    # Load configuration values
    SLEEP_DURATION=$(read_yaml_config "$config_file" "sleep_duration" "1000")
    MANAGED_REPO_PATH=$(read_yaml_config "$config_file" "managed_repo_path" "~/git/managed")
    MANAGED_REPO_TASK_PATH=$(read_yaml_config "$config_file" "managed_repo_task_path" "~/git/repo_task_path")
    LOG_DIRECTORY=$(read_yaml_config "$config_file" "log_directory" "")
    LOG_MAX_SIZE_MB=$(read_yaml_config "$config_file" "log_max_size_mb" "10")
    LOG_MAX_FILES=$(read_yaml_config "$config_file" "log_max_files" "5")
    LOG_RETENTION_DAYS=$(read_yaml_config "$config_file" "log_retention_days" "30")
    LOG_LEVEL=$(read_yaml_config "$config_file" "log_level" "INFO")
    
    # Enhanced timestamp configuration
    TIMESTAMP_FORMAT=$(read_yaml_config "$config_file" "timestamp_format" "default")
    TIMESTAMP_TIMEZONE=$(read_yaml_config "$config_file" "timestamp_timezone" "local")
    
    # Auto-update-reboot configuration
    AUTO_UPDATE_REBOOT_ENABLED=$(read_yaml_config "$config_file" "auto_update_reboot_enabled" "false")
    REBOOT_COOLDOWN_MINUTES=$(read_yaml_config "$config_file" "reboot_cooldown_minutes" "60")
    CHANGE_DETECTION_INTERVAL_MINUTES=$(read_yaml_config "$config_file" "change_detection_interval_minutes" "5")
    REBOOT_DELAY_SECONDS=$(read_yaml_config "$config_file" "reboot_delay_seconds" "30")
    MAX_REBOOT_ATTEMPTS_PER_DAY=$(read_yaml_config "$config_file" "max_reboot_attempts_per_day" "3")
    MAINTENANCE_MODE=$(read_yaml_config "$config_file" "maintenance_mode" "false")
    EMERGENCY_OVERRIDE=$(read_yaml_config "$config_file" "emergency_override" "false")
    
    # Branch protection configuration
    branch_protection_enable_protection=$(read_yaml_config "$config_file" "branch_protection.enable_protection" "true")
    branch_protection_require_confirmation=$(read_yaml_config "$config_file" "branch_protection.require_confirmation" "true")
    branch_protection_show_warnings=$(read_yaml_config "$config_file" "branch_protection.show_warnings" "true")
    branch_protection_protect_current_branch=$(read_yaml_config "$config_file" "branch_protection.protect_current_branch" "true")
    
    # Load branch protection arrays
    declare -g -a branch_protection_protected_branches=()
    read_yaml_array "$config_file" "branch_protection.protected_branches" branch_protection_protected_branches
    
    declare -g -a branch_protection_protection_patterns=()
    read_yaml_array "$config_file" "branch_protection.protection_patterns" branch_protection_protection_patterns
    
    declare -g -a branch_protection_require_explicit_confirmation_for=()
    read_yaml_array "$config_file" "branch_protection.require_explicit_confirmation_for" branch_protection_require_explicit_confirmation_for
    
    # Expand tilde paths
    MANAGED_REPO_PATH="${MANAGED_REPO_PATH/#\~/$HOME}"
    MANAGED_REPO_TASK_PATH="${MANAGED_REPO_TASK_PATH/#\~/$HOME}"
    LOG_DIRECTORY="${LOG_DIRECTORY/#\~/$HOME}"
    
    # CLI commands
    OPencode_CMD="timeout -v -k 1m 2h opencode"
    BEADS_CMD="bd"
    
    # Export variables
    export SLEEP_DURATION MANAGED_REPO_PATH MANAGED_REPO_TASK_PATH LOG_DIRECTORY OPencode_CMD BEADS_CMD
    export AUTO_UPDATE_REBOOT_ENABLED REBOOT_COOLDOWN_MINUTES CHANGE_DETECTION_INTERVAL_MINUTES REBOOT_DELAY_SECONDS
    export MAX_REBOOT_ATTEMPTS_PER_DAY MAINTENANCE_MODE EMERGENCY_OVERRIDE
    export LOG_MAX_SIZE_MB LOG_MAX_FILES LOG_RETENTION_DAYS LOG_LEVEL
    export TIMESTAMP_FORMAT TIMESTAMP_TIMEZONE
    
    # Export branch protection variables
    export branch_protection_enable_protection branch_protection_require_confirmation branch_protection_show_warnings
    export branch_protection_protect_current_branch
    export branch_protection_protected_branches branch_protection_protection_patterns
    export branch_protection_require_explicit_confirmation_for
}
