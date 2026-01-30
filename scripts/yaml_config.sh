#!/bin/bash

# YAML Configuration Parser for Repository Automation System
# Provides functions to read config.yaml values

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
        echo "Error: Configuration file $config_file not found" >&2
        echo "$default_value"
        return 1
    fi
    
    # Simple YAML parsing using grep and sed
    # This handles basic key: value pairs, ignoring comments
    local value=$(grep "^[[:space:]]*$key:" "$config_file" | grep -v "#" | sed "s/^[[:space:]]*$key:[[:space:]]*//" | sed 's/[[:space:]]*#.*//' | sed 's/^["'"'"']//' | sed 's/["'"'"']$//' | sed 's/[[:space:]]*$//')
    
    if [[ -z "$value" ]]; then
        echo "$default_value"
    else
        echo "$value"
    fi
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
    
    # Expand tilde paths
    MANAGED_REPO_PATH="${MANAGED_REPO_PATH/#\~/$HOME}"
    MANAGED_REPO_TASK_PATH="${MANAGED_REPO_TASK_PATH/#\~/$HOME}"
    LOG_DIRECTORY="${LOG_DIRECTORY/#\~/$HOME}"
    
    # CLI commands
    OPencode_CMD="opencode"
    BEADS_CMD="bd"
    
    # Export variables
    export SLEEP_DURATION MANAGED_REPO_PATH MANAGED_REPO_TASK_PATH LOG_DIRECTORY OPencode_CMD BEADS_CMD
    export AUTO_UPDATE_REBOOT_ENABLED REBOOT_COOLDOWN_MINUTES CHANGE_DETECTION_INTERVAL_MINUTES REBOOT_DELAY_SECONDS
    export MAX_REBOOT_ATTEMPTS_PER_DAY MAINTENANCE_MODE EMERGENCY_OVERRIDE
    export LOG_MAX_SIZE_MB LOG_MAX_FILES LOG_RETENTION_DAYS LOG_LEVEL
    export TIMESTAMP_FORMAT TIMESTAMP_TIMEZONE
}