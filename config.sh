#!/bin/bash

# Configuration system for Repository Automation System
# Reads from config.yaml instead of repos.txt

# Function to read YAML configuration
read_yaml_config() {
    local config_file="$1"
    local key="$2"
    
    if [[ ! -f "$config_file" ]]; then
        echo "Error: Configuration file $config_file not found" >&2
        return 1
    fi
    
    # Simple YAML parsing using grep and sed
    # This handles basic key: value pairs
    grep "^[[:space:]]*$key:" "$config_file" | sed "s/^[[:space:]]*$key:[[:space:]]*//" | sed 's/^["'\'']//' | sed 's/["'\\'']$//'
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.yaml"

# Load configuration from YAML
SLEEP_DURATION=$(read_yaml_config "$CONFIG_FILE" "sleep_duration")
MANAGED_REPO_PATH=$(read_yaml_config "$CONFIG_FILE" "managed_repo_path")
MANAGED_REPO_TASK_PATH=$(read_yaml_config "$CONFIG_FILE" "managed_repo_task_path")

# Set defaults if values are empty
SLEEP_DURATION=${SLEEP_DURATION:-1000}
MANAGED_REPO_PATH=${MANAGED_REPO_PATH:-~/git/managed}
MANAGED_REPO_TASK_PATH=${MANAGED_REPO_TASK_PATH:-~/git/repo_task_path}

# Expand tilde paths
MANAGED_REPO_PATH="${MANAGED_REPO_PATH/#\~/$HOME}"
MANAGED_REPO_TASK_PATH="${MANAGED_REPO_TASK_PATH/#\~/$HOME}"

# CLI commands
OPencode_CMD="opencode"
BEADS_CMD="bd"

# Export variables for use by other scripts
export SLEEP_DURATION
export MANAGED_REPO_PATH
export MANAGED_REPO_TASK_PATH
export OPencode_CMD
export BEADS_CMD