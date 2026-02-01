#!/bin/bash

# Configuration Validation Module
# Provides comprehensive configuration validation, runtime checks, and dynamic validation
# Ensures system configuration consistency and integrity

# Set script name for logging identification
SCRIPT_NAME="configuration_validator"

# Source dependencies
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../utils.sh"
source "$SCRIPT_DIR/../core/system_state.sh"

# =============================================================================
# CONFIGURATION VALIDATION FRAMEWORK
# =============================================================================

# Validation result structure
declare -A VALIDATION_RESULTS=(
    ["errors"]=0
    ["warnings"]=0
    ["info_messages"]=0
    ["validation_timestamp"]=0
)

# Configuration field definitions with validation rules
declare -A CONFIG_FIELDS=(
    # System paths
    ["MANAGED_REPO_PATH"]="required:path:dir_exists:writable:non_empty"
    ["MANAGED_REPO_TASK_PATH"]="optional:path:dir_exists:writable"
    ["LOG_DIRECTORY"]="optional:path:dir_exists:writable:create_if_missing"
    
    # Timing and performance
    ["SLEEP_DURATION"]="required:integer:positive:max:3600"
    ["REBOOT_COOLDOWN_MINUTES"]="optional:integer:positive:max:1440"
    ["CHANGE_DETECTION_INTERVAL_MINUTES"]="optional:integer:positive:max:1440"
    ["REBOOT_DELAY_SECONDS"]="optional:integer:positive:max:300"
    
    # Limits and thresholds
    ["MAX_REBOOT_ATTEMPTS_PER_DAY"]="optional:integer:positive:max:24"
    ["LOG_MAX_SIZE_MB"]="optional:integer:positive:max:1000"
    ["LOG_MAX_FILES"]="optional:integer:positive:max:50"
    ["LOG_RETENTION_DAYS"]="optional:integer:positive:max:365"
    
    # Feature flags
    ["AUTO_UPDATE_REBOOT_ENABLED"]="optional:boolean"
    ["MAINTENANCE_MODE"]="optional:boolean"
    ["EMERGENCY_OVERRIDE"]="optional:boolean"
    ["DEBUG_MODE"]="optional:boolean"
    
    # Logging configuration
    ["LOG_LEVEL"]="optional:enum:DEBUG,INFO,SUCCESS,WARNING,ERROR"
    ["TIMESTAMP_FORMAT"]="optional:enum:default,iso8601,rfc3339,syslog,compact,readable,debug"
    ["TIMESTAMP_TIMEZONE"]="optional:enum:local,utc"
    
    # Beads configuration
    ["BEADS_DEFAULT_SYNC_MODE"]="optional:enum:incremental,full"
    ["BEADS_DEFAULT_CONFLICT_STRATEGY"]="optional:enum:newest,manual,keep_local,keep_remote"
    ["BEADS_DEFAULT_MAX_RETRIES"]="optional:integer:positive:max:10"
    ["BEADS_BACKUP_RETENTION_DAYS"]="optional:integer:positive:max:365"
    ["BEADS_LOCK_TIMEOUT_MINUTES"]="optional:integer:positive:max:1440"
)

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

# Main configuration validation function
validate_configuration() {
    local config_file="${1:-}"
    local validation_mode="${2:-strict}"  # strict, permissive, minimal
    local validation_results_file="${3:-/tmp/autoslopp_validation_results.json}"
    
    log "INFO" "Starting configuration validation (mode: $validation_mode)"
    
    # Reset validation results
    reset_validation_results
    
    # Validate configuration file existence and format
    validate_configuration_file "$config_file"
    
    # Load and validate YAML configuration if available
    if [[ -n "$config_file" && -f "$config_file" ]]; then
        validate_yaml_configuration "$config_file" "$validation_mode"
    fi
    
    # Validate environment variables
    validate_environment_variables "$validation_mode"
    
    # Validate configuration consistency
    validate_configuration_consistency "$validation_mode"
    
    # Validate runtime dependencies
    validate_runtime_dependencies "$validation_mode"
    
    # Validate security settings
    validate_security_settings "$validation_mode"
    
    # Generate validation report
    generate_validation_report "$validation_results_file"
    
    # Return validation status
    if [[ ${VALIDATION_RESULTS[errors]} -eq 0 ]]; then
        log "SUCCESS" "Configuration validation passed"
        return 0
    else
        log "ERROR" "Configuration validation failed with ${VALIDATION_RESULTS[errors]} errors"
        return 1
    fi
}

# Reset validation results
reset_validation_results() {
    VALIDATION_RESULTS[errors]=0
    VALIDATION_RESULTS[warnings]=0
    VALIDATION_RESULTS[info_messages]=0
    VALIDATION_RESULTS[validation_timestamp]=$(date +%s)
}

# Validate configuration file existence and format
validate_configuration_file() {
    local config_file="$1"
    
    if [[ -z "$config_file" ]]; then
        # Try to find default configuration files
        local script_dir="$(dirname "${BASH_SOURCE[0]}")/../"
        local possible_configs=(
            "$script_dir/config.yaml"
            "$script_dir/config.yml"
            "$script_dir/config.sh"
        )
        
        for config in "${possible_configs[@]}"; do
            if [[ -f "$config" ]]; then
                log "INFO" "Found configuration file: $config"
                return 0
            fi
        done
        
        add_validation_result "warning" "config_file" "No configuration file found, using defaults"
        return 0
    fi
    
    if [[ ! -f "$config_file" ]]; then
        add_validation_result "error" "config_file" "Configuration file not found: $config_file"
        return 1
    fi
    
    if [[ ! -r "$config_file" ]]; then
        add_validation_result "error" "config_file" "Configuration file not readable: $config_file"
        return 1
    fi
    
    # Check file format based on extension
    case "${config_file##*.}" in
        "yaml"|"yml")
            validate_yaml_syntax "$config_file"
            ;;
        "sh")
            validate_shell_syntax "$config_file"
            ;;
        *)
            add_validation_result "warning" "config_file" "Unknown configuration file format: ${config_file##*.}"
            ;;
    esac
    
    return 0
}

# Validate YAML syntax
validate_yaml_syntax() {
    local yaml_file="$1"
    
    if command -v yamllint >/dev/null 2>&1; then
        if yamllint "$yaml_file" >/dev/null 2>&1; then
            add_validation_result "info" "yaml_syntax" "YAML syntax is valid"
        else
            add_validation_result "error" "yaml_syntax" "YAML syntax validation failed"
        fi
    elif command -v python3 >/dev/null 2>&1; then
        # Try basic YAML parsing with python
        if python3 -c "
import yaml
import sys
try:
    with open('$yaml_file') as f:
        yaml.safe_load(f)
    print('YAML syntax valid')
except Exception as e:
    print(f'YAML error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
            add_validation_result "info" "yaml_syntax" "YAML syntax is valid"
        else
            add_validation_result "error" "yaml_syntax" "YAML parsing failed"
        fi
    else
        add_validation_result "warning" "yaml_syntax" "No YAML validator available (yamllint or python3)"
    fi
}

# Validate shell script syntax
validate_shell_syntax() {
    local shell_file="$1"
    
    if bash -n "$shell_file" 2>/dev/null; then
        add_validation_result "info" "shell_syntax" "Shell script syntax is valid"
    else
        add_validation_result "error" "shell_syntax" "Shell script syntax validation failed"
    fi
}

# Validate YAML configuration content
validate_yaml_configuration() {
    local yaml_file="$1"
    local validation_mode="$2"
    
    # Extract YAML values using python or fallback methods
    if command -v python3 >/dev/null 2>&1; then
        validate_yaml_with_python "$yaml_file" "$validation_mode"
    else
        add_validation_result "warning" "yaml_content" "Python3 not available, limited YAML validation"
        validate_yaml_with_grep "$yaml_file" "$validation_mode"
    fi
}

# Validate YAML using Python
validate_yaml_with_python() {
    local yaml_file="$1"
    local validation_mode="$2"
    
    python3 -c "
import yaml
import os
import re

try:
    with open('$yaml_file') as f:
        config = yaml.safe_load(f)
    
    # Validate key configuration fields
    validations = []
    
    # Check managed_repo_path
    if 'managed_repo_path' in config:
        path = config['managed_repo_path']
        expanded_path = os.path.expanduser(path)
        if not os.path.exists(expanded_path):
            validations.append(('error', 'managed_repo_path', f'Path does not exist: {expanded_path}'))
        elif not os.path.isdir(expanded_path):
            validations.append(('error', 'managed_repo_path', f'Path is not a directory: {expanded_path}'))
        elif not os.access(expanded_path, os.R_OK):
            validations.append(('error', 'managed_repo_path', f'Path is not readable: {expanded_path}'))
    
    # Check log_directory
    if 'log_directory' in config:
        path = config['log_directory']
        expanded_path = os.path.expanduser(path)
        if not os.path.exists(expanded_path):
            # Try to create it
            try:
                os.makedirs(expanded_path, exist_ok=True)
                validations.append(('info', 'log_directory', f'Created log directory: {expanded_path}'))
            except Exception as e:
                validations.append(('warning', 'log_directory', f'Cannot create log directory: {expanded_path} ({e})'))
    
    # Check sleep_duration
    if 'sleep_duration' in config:
        duration = config['sleep_duration']
        if not isinstance(duration, (int, float)) or duration <= 0:
            validations.append(('error', 'sleep_duration', f'Invalid sleep duration: {duration}'))
        elif duration > 3600:
            validations.append(('warning', 'sleep_duration', f'Sleep duration very high: {duration}s'))
    
    # Print validation results
    for level, field, message in validations:
        print(f'{level}:{field}:{message}')
        
except Exception as e:
    print(f'error:yaml_parsing:Failed to parse YAML: {e}')
" | while IFS=: read -r level field message; do
        add_validation_result "$level" "$field" "$message"
    done
}

# Validate YAML using grep (fallback method)
validate_yaml_with_grep() {
    local yaml_file="$1"
    local validation_mode="$2"
    
    # Basic grep-based validation
    if grep -q "managed_repo_path:" "$yaml_file"; then
        local path=$(grep "managed_repo_path:" "$yaml_file" | cut -d: -f2- | xargs)
        add_validation_result "info" "managed_repo_path" "Found managed_repo_path: $path"
    else
        add_validation_result "warning" "managed_repo_path" "managed_repo_path not found in configuration"
    fi
    
    if grep -q "sleep_duration:" "$yaml_file"; then
        local duration=$(grep "sleep_duration:" "$yaml_file" | cut -d: -f2- | xargs)
        if [[ "$duration" =~ ^[0-9]+$ ]] && [[ $duration -gt 0 ]]; then
            add_validation_result "info" "sleep_duration" "Valid sleep duration: $duration"
        else
            add_validation_result "error" "sleep_duration" "Invalid sleep duration: $duration"
        fi
    fi
}

# Validate environment variables
validate_environment_variables() {
    local validation_mode="$1"
    
    # Check critical environment variables
    local critical_vars=(
        "HOME"
        "PATH"
        "PWD"
    )
    
    for var in "${critical_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            add_validation_result "error" "environment" "Critical environment variable not set: $var"
        fi
    done
    
    # Check Auto-slopp specific variables
    if [[ -z "${MANAGED_REPO_PATH:-}" ]]; then
        add_validation_result "warning" "environment" "MANAGED_REPO_PATH not set"
    elif [[ ! -d "$MANAGED_REPO_PATH" ]]; then
        add_validation_result "error" "environment" "MANAGED_REPO_PATH directory not found: $MANAGED_REPO_PATH"
    else
        add_validation_result "info" "environment" "MANAGED_REPO_PATH is valid: $MANAGED_REPO_PATH"
    fi
    
    if [[ -n "${LOG_DIRECTORY:-}" && ! -d "$LOG_DIRECTORY" ]]; then
        add_validation_result "warning" "environment" "LOG_DIRECTORY not found: $LOG_DIRECTORY"
    fi
}

# Validate configuration consistency
validate_configuration_consistency() {
    local validation_mode="$1"
    
    # Check path consistency
    if [[ -n "${MANAGED_REPO_PATH:-}" && -n "${MANAGED_REPO_TASK_PATH:-}" ]]; then
        if [[ "$MANAGED_REPO_PATH" == "$MANAGED_REPO_TASK_PATH" ]]; then
            add_validation_result "warning" "consistency" "MANAGED_REPO_PATH and MANAGED_REPO_TASK_PATH are the same"
        fi
    fi
    
    # Check timing consistency
    if [[ -n "${CHANGE_DETECTION_INTERVAL_MINUTES:-}" && -n "${SLEEP_DURATION:-}" ]]; then
        # Convert sleep_duration to minutes for comparison
        local sleep_minutes=$((SLEEP_DURATION / 60))
        if [[ $sleep_minutes -lt $CHANGE_DETECTION_INTERVAL_MINUTES ]]; then
            add_validation_result "warning" "consistency" "Sleep duration may be too short for change detection interval"
        fi
    fi
    
    # Check log level consistency
    if [[ -n "${LOG_LEVEL:-}" ]]; then
        if ! echo "DEBUG INFO SUCCESS WARNING ERROR" | grep -q -w "$LOG_LEVEL"; then
            add_validation_result "error" "consistency" "Invalid LOG_LEVEL: $LOG_LEVEL"
        fi
    fi
    
    # Check feature flag consistency
    if [[ "${AUTO_UPDATE_REBOOT_ENABLED:-false}" == "true" ]]; then
        if [[ -z "${REBOOT_COOLDOWN_MINUTES:-}" ]]; then
            add_validation_result "warning" "consistency" "Auto-update-reboot enabled but no cooldown period set"
        fi
        if [[ -z "${MAX_REBOOT_ATTEMPTS_PER_DAY:-}" ]]; then
            add_validation_result "warning" "consistency" "Auto-update-reboot enabled but no daily limit set"
        fi
    fi
}

# Validate runtime dependencies
validate_runtime_dependencies() {
    local validation_mode="$1"
    
    # Required commands
    local required_commands=(
        "git"
        "bash"
        "find"
        "grep"
        "sed"
        "awk"
    )
    
    local missing_required=()
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_required+=("$cmd")
        fi
    done
    
    if [[ ${#missing_required[@]} -gt 0 ]]; then
        add_validation_result "error" "dependencies" "Missing required commands: ${missing_required[*]}"
    else
        add_validation_result "info" "dependencies" "All required commands available"
    fi
    
    # Optional but recommended commands
    local optional_commands=(
        "jq"
        "yamllint"
        "python3"
        "notify-send"
        "bc"
    )
    
    local missing_optional=()
    for cmd in "${optional_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_optional+=("$cmd")
        fi
    done
    
    if [[ ${#missing_optional[@]} -gt 0 ]]; then
        add_validation_result "warning" "dependencies" "Missing optional commands: ${missing_optional[*]}"
    fi
    
    # Git version check
    if command -v git >/dev/null 2>&1; then
        local git_version=$(git --version 2>/dev/null | cut -d' ' -f3)
        if [[ -n "$git_version" ]]; then
            add_validation_result "info" "dependencies" "Git version: $git_version"
        fi
    fi
}

# Validate security settings
validate_security_settings() {
    local validation_mode="$1"
    
    # Check file permissions for critical files
    local script_dir="$(dirname "${BASH_SOURCE[0]}")/.."
    local critical_files=(
        "$script_dir/config.sh"
        "$script_dir/config.yaml"
        "$script_dir/main.sh"
        "$script_dir/scripts/utils.sh"
    )
    
    for file in "${critical_files[@]}"; do
        if [[ -f "$file" ]]; then
            local perms=$(stat -c "%a" "$file" 2>/dev/null)
            if [[ -n "$perms" ]]; then
                # Check if world-writable (security risk)
                if [[ "${perms: -1}" =~ [2367] ]]; then
                    add_validation_result "warning" "security" "File is world-writable: $file ($perms)"
                fi
            fi
        fi
    done
    
    # Check for sensitive information in configuration
    if [[ -f "$script_dir/config.yaml" ]]; then
        # Look for potential passwords or keys (basic pattern matching)
        if grep -qi "password\|secret\|key\|token" "$script_dir/config.yaml"; then
            add_validation_result "warning" "security" "Potential sensitive information found in configuration file"
        fi
    fi
    
    # Check log directory permissions
    if [[ -n "${LOG_DIRECTORY:-}" && -d "$LOG_DIRECTORY" ]]; then
        if [[ ! -w "$LOG_DIRECTORY" ]]; then
            add_validation_result "error" "security" "Log directory is not writable: $LOG_DIRECTORY"
        fi
    fi
}

# =============================================================================
# VALIDATION RESULT MANAGEMENT
# =============================================================================

# Add validation result
add_validation_result() {
    local level="$1"
    local field="$2"
    local message="$3"
    local timestamp=$(date +%s)
    
    case "$level" in
        "error")
            ((VALIDATION_RESULTS[errors]++))
            log "ERROR" "Validation error [$field]: $message"
            ;;
        "warning")
            ((VALIDATION_RESULTS[warnings]++))
            log "WARNING" "Validation warning [$field]: $message"
            ;;
        "info")
            ((VALIDATION_RESULTS[info_messages]++))
            log "INFO" "Validation info [$field]: $message"
            ;;
    esac
    
    # Store result for report generation
    local result_entry="{\"timestamp\": $timestamp, \"level\": \"$level\", \"field\": \"$field\", \"message\": \"$message\"}"
    echo "$result_entry" >> "/tmp/autoslopp_validation_entries.tmp"
}

# Generate validation report
generate_validation_report() {
    local output_file="$1"
    
    local report_content=$(cat << EOF
{
    "validation_summary": {
        "timestamp": ${VALIDATION_RESULTS[validation_timestamp]},
        "errors": ${VALIDATION_RESULTS[errors]},
        "warnings": ${VALIDATION_RESULTS[warnings]},
        "info_messages": ${VALIDATION_RESULTS[info_messages]},
        "status": "$([ ${VALIDATION_RESULTS[errors]} -eq 0 ] && echo "passed" || echo "failed")"
    },
    "validation_details": [
$(cat "/tmp/autoslopp_validation_entries.tmp" 2>/dev/null | sed 's/^/        /' | sed '$s/^        //' | tr '\n' ',' | sed 's/,$//')
    ],
    "recommendations": [
$(generate_recommendations)
    ]
}
EOF
)
    
    echo "$report_content" > "$output_file"
    rm -f "/tmp/autoslopp_validation_entries.tmp"
    
    log "INFO" "Validation report generated: $output_file"
}

# Generate recommendations based on validation results
generate_recommendations() {
    local recommendations=()
    
    if [[ ${VALIDATION_RESULTS[errors]} -gt 0 ]]; then
        recommendations+=("\"Fix all validation errors before proceeding\"")
    fi
    
    if [[ ${VALIDATION_RESULTS[warnings]} -gt 0 ]]; then
        recommendations+=("\"Review and address validation warnings\"")
    fi
    
    if [[ ${VALIDATION_RESULTS[errors]} -eq 0 && ${VALIDATION_RESULTS[warnings]} -eq 0 ]]; then
        recommendations+=("\"Configuration validation passed successfully\"")
    fi
    
    printf '"%s"' "${recommendations[@]}" | tr '\n' ',' | sed 's/,$//'
}

# =============================================================================
# RUNTIME VALIDATION UTILITIES
# =============================================================================

# Validate configuration at runtime
validate_runtime_configuration() {
    local operation="$1"
    
    log "DEBUG" "Runtime validation for operation: $operation"
    
    case "$operation" in
        "git_operation")
            validate_git_operation_config
            ;;
        "log_write")
            validate_logging_config
            ;;
        "cleanup")
            validate_cleanup_config
            ;;
        *)
            validate_basic_config
            ;;
    esac
}

# Validate git operation configuration
validate_git_operation_config() {
    if [[ ! -d "${GIT_REPO_DIR:-$MANAGED_REPO_PATH}" ]]; then
        add_validation_result "error" "runtime" "Git repository directory not found"
        return 1
    fi
    
    if ! command -v git >/dev/null 2>&1; then
        add_validation_result "error" "runtime" "Git command not available"
        return 1
    fi
    
    return 0
}

# Validate logging configuration
validate_logging_config() {
    if [[ -n "${LOG_DIRECTORY:-}" ]]; then
        if [[ ! -d "$LOG_DIRECTORY" ]]; then
            mkdir -p "$LOG_DIRECTORY" 2>/dev/null || {
                add_validation_result "error" "runtime" "Cannot create log directory: $LOG_DIRECTORY"
                return 1
            }
        fi
        
        if [[ ! -w "$LOG_DIRECTORY" ]]; then
            add_validation_result "error" "runtime" "Log directory not writable: $LOG_DIRECTORY"
            return 1
        fi
    fi
    
    return 0
}

# Validate cleanup operation configuration
validate_cleanup_config() {
    if [[ -z "${MANAGED_REPO_PATH:-}" ]]; then
        add_validation_result "error" "runtime" "MANAGED_REPO_PATH not configured for cleanup"
        return 1
    fi
    
    if [[ ! -r "$MANAGED_REPO_PATH" ]]; then
        add_validation_result "error" "runtime" "MANAGED_REPO_PATH not readable: $MANAGED_REPO_PATH"
        return 1
    fi
    
    return 0
}

# Validate basic configuration
validate_basic_config() {
    # Basic checks that apply to most operations
    if [[ -z "${MANAGED_REPO_PATH:-}" ]]; then
        add_validation_result "warning" "runtime" "MANAGED_REPO_PATH not configured"
    fi
    
    return 0
}

# =============================================================================
# CONFIGURATION REPAIR UTILITIES
# =============================================================================

# Attempt to repair configuration issues
attempt_configuration_repair() {
    local repair_mode="${1:-safe}"  # safe, aggressive
    
    log "INFO" "Attempting configuration repair (mode: $repair_mode)"
    
    local repairs_made=0
    
    # Try to create missing directories
    if [[ -n "${LOG_DIRECTORY:-}" && ! -d "$LOG_DIRECTORY" ]]; then
        if mkdir -p "$LOG_DIRECTORY" 2>/dev/null; then
            log "INFO" "Created missing log directory: $LOG_DIRECTORY"
            ((repairs_made++))
        fi
    fi
    
    if [[ -n "${MANAGED_REPO_PATH:-}" && ! -d "$MANAGED_REPO_PATH" ]]; then
        if [[ "$repair_mode" == "aggressive" ]]; then
            if mkdir -p "$MANAGED_REPO_PATH" 2>/dev/null; then
                log "INFO" "Created missing repository path: $MANAGED_REPO_PATH"
                ((repairs_made++))
            fi
        fi
    fi
    
    # Set sensible defaults for missing values
    if [[ -z "${SLEEP_DURATION:-}" ]]; then
        export SLEEP_DURATION=100
        log "INFO" "Set default sleep duration: $SLEEP_DURATION"
        ((repairs_made++))
    fi
    
    if [[ -z "${LOG_LEVEL:-}" ]]; then
        export LOG_LEVEL="INFO"
        log "INFO" "Set default log level: $LOG_LEVEL"
        ((repairs_made++))
    fi
    
    log "INFO" "Configuration repair completed: $repairs_made repairs made"
    return $repairs_made
}

# Export key functions
export -f validate_configuration
export -f validate_runtime_configuration
export -f attempt_configuration_repair

# Auto-validate configuration if this script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    validate_configuration
fi