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
    # This handles basic key: value pairs
    local value=$(grep "^[[:space:]]*$key:" "$config_file" | sed "s/^[[:space:]]*$key:[[:space:]]*//" | sed 's/^["'"'"']//' | sed 's/["'"'"']$//')
    
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
    
    # Expand tilde paths
    MANAGED_REPO_PATH="${MANAGED_REPO_PATH/#\~/$HOME}"
    MANAGED_REPO_TASK_PATH="${MANAGED_REPO_TASK_PATH/#\~/$HOME}"
    LOG_DIRECTORY="${LOG_DIRECTORY/#\~/$HOME}"
    
    # CLI commands
    OPencode_CMD="timeout -v -k 1m 2h opencode"
    BEADS_CMD="bd"
    
    # Export variables
    export SLEEP_DURATION MANAGED_REPO_PATH MANAGED_REPO_TASK_PATH LOG_DIRECTORY OPencode_CMD BEADS_CMD
}
