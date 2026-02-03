#!/bin/bash

# Configuration validation script for auto-update-reboot
# Validates configuration values and provides warnings/errors for invalid settings

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/config.sh"

# Validation result tracking
VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0

log_validation_start() {
    echo "=== Auto-update-reboot Configuration Validation ==="
    echo "Starting validation of configuration options..."
    echo ""
}

log_validation_error() {
    local message="$1"
    echo "ERROR: $message"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
}

log_validation_warning() {
    local message="$1"
    echo "WARNING: $message"
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
}

log_validation_success() {
    local message="$1"
    echo "OK: $message"
}

validate_numeric_range() {
    local config_name="$1"
    local value="$2"
    local min="$3"
    local max="$4"
    local description="$5"
    
    # Check if value is numeric
    if ! [[ "$value" =~ ^[0-9]+$ ]]; then
        log_validation_error "$config_name ($description) must be a positive integer, got: $value"
        return 1
    fi
    
    # Check range
    if [[ $value -lt $min ]]; then
        log_validation_error "$config_name ($description) is too low: $value (minimum: $min)"
        return 1
    elif [[ $value -gt $max ]]; then
        log_validation_error "$config_name ($description) is too high: $value (maximum: $max)"
        return 1
    else
        log_validation_success "$config_name ($description): $value"
        return 0
    fi
}

validate_boolean() {
    local config_name="$1"
    local value="$2"
    local description="$3"
    
    if [[ "$value" == "true" || "$value" == "false" ]]; then
        log_validation_success "$config_name ($description): $value"
        return 0
    else
        log_validation_error "$config_name ($description) must be 'true' or 'false', got: $value"
        return 1
    fi
}

validate_string_in_list() {
    local config_name="$1"
    local value="$2"
    local valid_values="$3"
    local description="$4"
    
    for valid_value in $valid_values; do
        if [[ "$value" == "$valid_value" ]]; then
            log_validation_success "$config_name ($description): $value"
            return 0
        fi
    done
    
    log_validation_error "$config_name ($description) must be one of: $valid_values, got: $value"
    return 1
}

validate_time_format() {
    local config_name="$1"
    local value="$2"
    local description="$3"
    
    # Check HH:MM format (24-hour)
    if [[ "$value" =~ ^([01]?[0-9]|2[0-3]):[0-5][0-9]$ ]]; then
        log_validation_success "$config_name ($description): $value"
        return 0
    else
        log_validation_error "$config_name ($description) must be in HH:MM format (24-hour), got: $value"
        return 1
    fi
}

validate_email_address() {
    local email="$1"
    local config_name="$2"
    
    # Basic email validation regex
    if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        log_validation_error "$config_name: Invalid email address format: $email"
        return 1
    fi
}

validate_url() {
    local url="$1"
    local config_name="$2"
    
    # Basic URL validation
    if [[ "$url" =~ ^https?://[a-zA-Z0-9.-]+[a-zA-Z0-9._/-]*$ ]]; then
        return 0
    else
        log_validation_error "$config_name: Invalid URL format: $url"
        return 1
    fi
}

validate_config_file() {
    if [[ ! -f "$SCRIPT_DIR/../config.yaml" ]]; then
        log_validation_error "Configuration file not found: $SCRIPT_DIR/../config.yaml"
        return 1
    fi
    
    log_validation_success "Configuration file found: $SCRIPT_DIR/../config.yaml"
    return 0
}

validate_log_levels() {
    echo "Validating log level configurations..."
    
    # Validate main log level
    validate_string_in_list "log_level" "${LOG_LEVEL:-INFO}" "DEBUG INFO WARNING ERROR SUCCESS" "Main log level"
    
    # Validate auto-update-reboot specific log levels
    local aur_log_levels="DEBUG INFO WARNING ERROR SUCCESS"
    
    # Check if YAML config loader supports these new config keys
    if command -v yaml_get >/dev/null 2>&1; then
        # Use yaml_get if available
        local git_ops_level=$(yaml_get "auto_update_reboot_logging.git_operations_log_level" "INFO" 2>/dev/null)
        local safety_checks_level=$(yaml_get "auto_update_reboot_logging.safety_checks_log_level" "INFO" 2>/dev/null)
        local change_detection_level=$(yaml_get "auto_update_reboot_logging.change_detection_log_level" "INFO" 2>/dev/null)
        local notifications_level=$(yaml_get "auto_update_reboot_logging.notifications_log_level" "WARNING" 2>/dev/null)
        local system_health_level=$(yaml_get "auto_update_reboot_logging.system_health_log_level" "INFO" 2>/dev/null)
        
        validate_string_in_list "git_operations_log_level" "$git_ops_level" "$aur_log_levels" "Git operations log level"
        validate_string_in_list "safety_checks_log_level" "$safety_checks_level" "$aur_log_levels" "Safety checks log level"
        validate_string_in_list "change_detection_log_level" "$change_detection_level" "$aur_log_levels" "Change detection log level"
        validate_string_in_list "notifications_log_level" "$notifications_level" "$aur_log_levels" "Notifications log level"
        validate_string_in_list "system_health_log_level" "$system_health_level" "$aur_log_levels" "System health log level"
    else
        log_validation_warning "yaml_get command not available, skipping detailed log level validation"
    fi
}

validate_notification_settings() {
    echo "Validating notification settings..."
    
    # Validate email settings if enabled
    local email_enabled=$(yaml_get "notifications.email_notifications.enabled" "false" 2>/dev/null || echo "false")
    validate_boolean "email_notifications.enabled" "$email_enabled" "Email notifications enabled"
    
    if [[ "$email_enabled" == "true" ]]; then
        local smtp_server=$(yaml_get "notifications.email_notifications.smtp_server" "" 2>/dev/null || echo "")
        local smtp_port=$(yaml_get "notifications.email_notifications.smtp_port" "587" 2>/dev/null || echo "587")
        local from_address=$(yaml_get "notifications.email_notifications.from_address" "" 2>/dev/null || echo "")
        local to_addresses=$(yaml_get "notifications.email_notifications.to_addresses" "[]" 2>/dev/null || echo "[]")
        
        if [[ -z "$smtp_server" ]]; then
            log_validation_error "SMTP server is required when email notifications are enabled"
        fi
        
        validate_numeric_range "smtp_port" "$smtp_port" 1 65535 "SMTP port"
        
        if [[ -n "$from_address" ]]; then
            validate_email_address "$from_address" "email_notifications.from_address"
        fi
        
        # Simple validation for to_addresses array
        if [[ "$to_addresses" != "[]" && "$to_addresses" != "" ]]; then
            log_validation_success "Email recipients configured"
        else
            log_validation_error "No email recipients configured when email notifications are enabled"
        fi
    fi
    
    # Validate webhook settings if enabled
    local webhook_enabled=$(yaml_get "notifications.webhook_notifications.enabled" "false" 2>/dev/null || echo "false")
    validate_boolean "webhook_notifications.enabled" "$webhook_enabled" "Webhook notifications enabled"
    
    if [[ "$webhook_enabled" == "true" ]]; then
        local webhook_url=$(yaml_get "notifications.webhook_notifications.webhook_url" "" 2>/dev/null || echo "")
        local webhook_timeout=$(yaml_get "notifications.webhook_notifications.webhook_timeout_seconds" "10" 2>/dev/null || echo "10")
        
        if [[ -z "$webhook_url" ]]; then
            log_validation_error "Webhook URL is required when webhook notifications are enabled"
        else
            validate_url "$webhook_url" "webhook_notifications.webhook_url"
        fi
        
        validate_numeric_range "webhook_timeout_seconds" "$webhook_timeout" 1 300 "Webhook timeout"
    fi
}

validate_safety_overrides() {
    echo "Validating safety override configurations..."
    
    # Validate that force reboot settings make sense
    local force_reboot_enabled=$(yaml_get "emergency_overrides.force_reboot_enabled" "false" 2>/dev/null || echo "false")
    validate_boolean "force_reboot_enabled" "$force_reboot_enabled" "Force reboot enabled"
    
    if [[ "$force_reboot_enabled" == "true" ]]; then
        local force_password=$(yaml_get "emergency_overrides.force_reboot_password" "" 2>/dev/null || echo "")
        local emergency_key=$(yaml_get "emergency_overrides.emergency_reboot_key" "" 2>/dev/null || echo "")
        
        if [[ -z "$force_password" && -z "$emergency_key" ]]; then
            log_validation_warning "Force reboot is enabled but no password or key is configured - this may be a security risk"
        fi
        
        log_validation_warning "Force reboot is enabled - this bypasses all safety checks"
    fi
    
    # Validate emergency stop file path
    local stop_file=$(yaml_get "emergency_overrides.emergency_stop_file" "/tmp/auto-update-reboot.stop" 2>/dev/null || echo "/tmp/auto-update-reboot.stop")
    if [[ ! -d "$(dirname "$stop_file")" ]]; then
        log_validation_warning "Emergency stop file directory does not exist: $(dirname "$stop_file")"
    fi
}

validate_time_settings() {
    echo "Validating time-based configurations..."
    
    # Validate maintenance window
    local window_start=$(yaml_get "safe_reboot.maintenance_window_start" "02:00" 2>/dev/null || echo "02:00")
    local window_end=$(yaml_get "safe_reboot.maintenance_window_end" "04:00" 2>/dev/null || echo "04:00")
    local business_start=$(yaml_get "safe_reboot.business_hours_start" "09:00" 2>/dev/null || echo "09:00")
    local business_end=$(yaml_get "safe_reboot.business_hours_end" "17:00" 2>/dev/null || echo "17:00")
    
    validate_time_format "maintenance_window_start" "$window_start" "Maintenance window start"
    validate_time_format "maintenance_window_end" "$window_end" "Maintenance window end"
    validate_time_format "business_hours_start" "$business_start" "Business hours start"
    validate_time_format "business_hours_end" "$business_end" "Business hours end"
}

validate_resource_thresholds() {
    echo "Validating resource threshold configurations..."
    
    # Validate safe_reboot thresholds
    validate_numeric_range "max_disk_usage_percent" "${SAFE_REBOOT_MAX_DISK_USAGE:-85}" 1 99 "Maximum disk usage percent"
    validate_numeric_range "max_memory_usage_percent" "${SAFE_REBOOT_MAX_MEMORY_USAGE:-85}" 1 99 "Maximum memory usage percent"
    validate_numeric_range "max_system_load_multiplier" "${SAFE_REBOOT_MAX_LOAD_MULTIPLIER:-2}" 1 10 "Maximum system load multiplier"
    validate_numeric_range "max_failed_services" "${SAFE_REBOOT_MAX_FAILED_SERVICES:-5}" 0 50 "Maximum failed services"
    validate_numeric_range "max_degraded_critical_services" "${SAFE_REBOOT_MAX_DEGRADED_CRITICAL_SERVICES:-2}" 0 20 "Maximum degraded critical services"
}

validate_git_settings() {
    echo "Validating git operation configurations..."
    
    validate_numeric_range "git_timeout_seconds" "${GIT_TIMEOUT_SECONDS:-30}" 5 300 "Git timeout seconds"
    validate_numeric_range "git_retry_attempts" "${GIT_RETRY_ATTEMPTS:-3}" 1 10 "Git retry attempts"
    validate_numeric_range "git_retry_delay_seconds" "${GIT_RETRY_DELAY_SECONDS:-5}" 1 60 "Git retry delay seconds"
    validate_numeric_range "network_timeout_seconds" "${NETWORK_TIMEOUT_SECONDS:-60}" 10 600 "Network timeout seconds"
}

validate_core_settings() {
    echo "Validating core auto-update-reboot settings..."
    
    validate_boolean "auto_update_reboot_enabled" "${AUTO_UPDATE_REBOOT_ENABLED:-false}" "Auto-update-reboot enabled"
    validate_numeric_range "reboot_cooldown_minutes" "${REBOOT_COOLDOWN_MINUTES:-60}" 5 1440 "Reboot cooldown minutes"
    validate_numeric_range "reboot_delay_seconds" "${REBOOT_DELAY_SECONDS:-30}" 10 3600 "Reboot delay seconds"
    validate_numeric_range "max_reboot_attempts_per_day" "${MAX_REBOOT_ATTEMPTS_PER_DAY:-3}" 1 24 "Maximum reboot attempts per day"
    validate_boolean "maintenance_mode" "${MAINTENANCE_MODE:-false}" "Maintenance mode"
    validate_boolean "emergency_override" "${EMERGENCY_OVERRIDE:-false}" "Emergency override"
}

validate_validation_settings() {
    echo "Validating configuration validation settings..."
    
    # Validate validation bounds
    local min_cooldown=$(yaml_get "validation.min_reboot_cooldown_minutes" "5" 2>/dev/null || echo "5")
    local max_cooldown=$(yaml_get "validation.max_reboot_cooldown_minutes" "1440" 2>/dev/null || echo "1440")
    local min_delay=$(yaml_get "validation.min_reboot_delay_seconds" "10" 2>/dev/null || echo "10")
    local max_delay=$(yaml_get "validation.max_reboot_delay_seconds" "3600" 2>/dev/null || echo "3600")
    
    validate_numeric_range "validation.min_reboot_cooldown_minutes" "$min_cooldown" 1 1440 "Minimum cooldown validation"
    validate_numeric_range "validation.max_reboot_cooldown_minutes" "$max_cooldown" 60 1440 "Maximum cooldown validation"
    validate_numeric_range "validation.min_reboot_delay_seconds" "$min_delay" 1 300 "Minimum delay validation"
    validate_numeric_range "validation.max_reboot_delay_seconds" "$max_delay" 60 7200 "Maximum delay validation"
}

# Main validation function
main() {
    log_validation_start
    
    # Validate configuration file exists
    validate_config_file
    
    # Core settings validation
    validate_core_settings
    
    # Resource thresholds
    validate_resource_thresholds
    
    # Git settings
    validate_git_settings
    
    # Time settings
    validate_time_settings
    
    # Log levels
    validate_log_levels
    
    # Notification settings
    validate_notification_settings
    
    # Safety overrides
    validate_safety_overrides
    
    # Validation settings
    validate_validation_settings
    
    # Summary
    echo ""
    echo "=== Validation Summary ==="
    echo "Errors: $VALIDATION_ERRORS"
    echo "Warnings: $VALIDATION_WARNINGS"
    
    if [[ $VALIDATION_ERRORS -eq 0 ]]; then
        if [[ $VALIDATION_WARNINGS -eq 0 ]]; then
            echo "✓ All configuration options are valid!"
            return 0
        else
            echo "⚠ Configuration is valid but has $VALIDATION_WARNINGS warnings"
            return 0
        fi
    else
        echo "✗ Configuration has $VALIDATION_ERRORS errors that must be fixed"
        echo "Please address the errors before using auto-update-reboot functionality"
        return 1
    fi
}

# Run validation if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi