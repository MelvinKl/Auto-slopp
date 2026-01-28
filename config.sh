#!/bin/bash

# Configuration system for Repository Automation System
# Uses YAML configuration instead of repos.txt

# Get script directory and load YAML configuration utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scripts/yaml_config.sh"

# Load all configuration from config.yaml
load_config "$SCRIPT_DIR/config.yaml"