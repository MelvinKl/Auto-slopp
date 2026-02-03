# Auto-update-reboot Configuration Guide

This document describes the enhanced configuration options for the auto-update-reboot functionality in Auto-slopp.

## Overview

The auto-update-reboot feature provides automated git repository updates with conditional rebooting based on detected changes. It includes comprehensive safety mechanisms, notification systems, and configuration validation.

## Core Configuration

### Basic Settings

```yaml
auto_update_reboot_enabled: false        # Enable/disable the auto-update-reboot functionality
reboot_cooldown_minutes: 60             # Minimum time between reboots
change_detection_interval_minutes: 5   # How often to check for changes
reboot_delay_seconds: 30                # Grace period before reboot
max_reboot_attempts_per_day: 3          # Daily limit on reboot attempts
maintenance_mode: false                  # Manual override to disable all reboots
emergency_override: false               # Emergency override for forced reboots
```

**Important Notes:**
- Set `auto_update_reboot_enabled` to `true` to activate the feature
- `maintenance_mode` takes precedence over all other settings
- `emergency_override` should only be used in emergency situations

## Safety Mechanisms

### Safe Reboot Configuration

```yaml
safe_reboot:
  # Safety thresholds
  max_disk_usage_percent: 85            # Maximum disk usage before reboot is blocked
  max_memory_usage_percent: 85          # Maximum memory usage before reboot is blocked
  max_system_load_multiplier: 2         # Maximum load as multiplier of CPU count
  max_failed_services: 5                # Maximum failed services before reboot is blocked
  max_degraded_critical_services: 2     # Maximum degraded critical services before reboot is blocked
```

### Time-based Controls

```yaml
safe_reboot:
  # Reboot type determination
  maintenance_window_start: "02:00"    # Start time for maintenance window (24-hour format)
  maintenance_window_end: "04:00"      # End time for maintenance window (24-hour format)
  business_hours_start: "09:00"         # Start of business hours (may delay reboots)
  business_hours_end: "17:00"           # End of business hours (may delay reboots)
```

**Behavior:**
- Reboots are preferred during maintenance windows
- Reboots during business hours trigger additional warnings
- Outside business hours allows more flexible scheduling

## Notification System

### Basic Notifications

```yaml
safe_reboot:
  # Notification and alerting
  user_notifications_enabled: false      # Enable desktop/wall notifications
  monitoring_integration_enabled: false  # Enable integration with monitoring systems
  critical_endpoints: ""                 # Comma-separated list of critical endpoints to check
```

### Enhanced Notification Configuration

```yaml
notifications:
  # Reboot event notifications
  reboot_events_enabled: false         # Enable notifications for reboot events
  reboot_success_notifications: true   # Notify on successful reboots
  reboot_failure_notifications: true   # Notify on reboot failures
  reboot_cancelled_notifications: true # Notify when reboots are cancelled due to safety checks
  
  # Pre-reboot notifications
  pre_reboot_warning_enabled: true    # Send warning before scheduled reboots
  pre_reboot_warning_seconds: 300     # Seconds before reboot to send warning (5 min)
  pre_reboot_countdown_notifications: true # Send countdown notifications during reboot delay
```

### Email Notifications

```yaml
notifications:
  email_notifications:
    enabled: false                     # Enable email notifications
    smtp_server: ""                    # SMTP server address
    smtp_port: 587                     # SMTP port (typically 587 for TLS)
    smtp_username: ""                   # SMTP username
    smtp_password: ""                   # SMTP password (use environment variable)
    from_address: ""                    # From email address
    to_addresses: []                    # List of recipient email addresses
    use_tls: true                       # Use TLS encryption
```

**Security Notes:**
- Never store SMTP passwords directly in configuration files
- Use environment variables for sensitive credentials
- Ensure proper TLS/SSL settings for secure email transmission

### Webhook Notifications

```yaml
notifications:
  webhook_notifications:
    enabled: false                     # Enable webhook notifications
    webhook_url: ""                    # Webhook endpoint URL
    webhook_timeout_seconds: 10        # Timeout for webhook requests
    webhook_retry_attempts: 2          # Retry attempts for failed webhooks
    webhook_headers: {}                 # Custom headers for webhook requests
```

**Webhook Format:**
The webhook receives POST requests with JSON payload containing:
- `event_type`: Type of event (reboot_success, reboot_failure, etc.)
- `timestamp`: Event timestamp in ISO8601 format
- `details`: Event-specific details
- `system_state`: Current system state information

## Logging Configuration

### Component-specific Log Levels

```yaml
auto_update_reboot_logging:
  # Log level controls for different components
  log_level: "INFO"                      # Overall log level: DEBUG, INFO, WARNING, ERROR, SUCCESS
  git_operations_log_level: "INFO"      # Log level for git operations
  safety_checks_log_level: "INFO"       # Log level for safety checks
  change_detection_log_level: "INFO"    # Log level for change detection
  notifications_log_level: "WARNING"     # Log level for notification system
  system_health_log_level: "INFO"        # Log level for system health checks
```

### Detailed Logging Controls

```yaml
auto_update_reboot_logging:
  # Component-specific logging toggles
  log_git_commands: false               # Log actual git commands being executed
  log_safety_check_details: true         # Log detailed safety check results
  log_change_analysis: true              # Log change significance analysis
  log_state_changes: true                # Log state file modifications
  log_retry_attempts: true               # Log retry attempts for failed operations
  log_network_operations: false         # Log detailed network operations
  log_system_state_snapshots: false     # Log when system state snapshots are created
  
  # Performance logging
  log_operation_timings: true            # Log timing information for operations
  log_resource_usage: false             # Log CPU/memory usage during operations
  log_performance_metrics: false         # Log detailed performance metrics
```

### Debug Mode

```yaml
auto_update_reboot_logging:
  # Debug and troubleshooting logging
  debug_mode: false                     # Enable comprehensive debug logging
  verbose_change_detection: false       # Log detailed change detection process
  trace_git_operations: false           # Trace every git operation step
  log_configuration_loading: false      # Log configuration loading process
```

**Debug Mode Effects:**
- Enables all detailed logging options
- Increases log verbosity significantly
- May impact performance (use only for troubleshooting)

## Emergency Overrides

### Emergency Reboot Settings

```yaml
emergency_overrides:
  # Emergency reboot settings
  force_reboot_enabled: false            # Allow forced reboots bypassing safety checks
  force_reboot_password: ""               # Password required for forced reboots
  emergency_reboot_key: ""               # SSH key or emergency access method
```

**Security Warning:**
- Force reboot bypasses ALL safety mechanisms
- Use only in critical emergency situations
- Always require strong authentication
- Log all force reboot attempts

### Emergency Stop Mechanisms

```yaml
emergency_overrides:
  # Emergency stop mechanisms
  emergency_stop_file: "/tmp/auto-update-reboot.stop" # File existence prevents all reboots
  emergency_stop_timeout: 3600           # Timeout for emergency stop file (seconds)
  emergency_recovery_mode: false         # Enable emergency recovery procedures
```

**Using Emergency Stop:**
```bash
# Create emergency stop file to prevent all reboots
touch /tmp/auto-update-reboot.stop

# Remove emergency stop file to allow reboots again
rm /tmp/auto-update-reboot.stop
```

### System Condition Overrides

```yaml
emergency_overrides:
  # System condition overrides
  override_high_load: false              # Allow reboot despite high system load
  override_low_disk: false               # Allow reboot despite low disk space
  override_failed_services: false        # Allow reboot despite failed services
  override_network_issues: false          # Allow reboot despite network problems
```

## Configuration Validation

### Safety Bounds Validation

```yaml
validation:
  # Safety bounds validation
  min_reboot_cooldown_minutes: 5         # Minimum allowed cooldown period
  max_reboot_cooldown_minutes: 1440      # Maximum allowed cooldown period (24 hours)
  min_reboot_delay_seconds: 10           # Minimum allowed reboot delay
  max_reboot_delay_seconds: 3600         # Maximum allowed reboot delay (1 hour)
  max_reboot_attempts_per_day: 10        # Maximum daily reboot attempts
```

### Resource Threshold Validation

```yaml
validation:
  # Resource threshold validation
  min_disk_usage_threshold: 50           # Minimum disk usage threshold (percent)
  max_disk_usage_threshold: 95           # Maximum disk usage threshold (percent)
  min_memory_usage_threshold: 50         # Minimum memory usage threshold (percent)
  max_memory_usage_threshold: 95         # Maximum memory usage threshold (percent)
```

### Configuration Change Validation

```yaml
validation:
  # Configuration change validation
  require_restart_on_config_change: true # Restart script when config changes
  validate_config_on_load: true          # Validate configuration when loading
  backup_config_before_changes: true     # Backup configuration before changes
```

## Change Detection Configuration

### File Pattern Matching

```yaml
# Change significance filtering
reboot_trigger_patterns: "scripts/*.sh|config.yaml|main.sh|scripts/utils.sh|scripts/core/*.sh"  # File patterns that trigger reboot
ignore_change_patterns: "*.md|*.txt|*.log|tests/*.sh|.*"  # File patterns to ignore
min_changed_files_for_reboot: 1          # Minimum number of significant changes to trigger reboot
max_change_count_for_reboot: 100         # Maximum number of changes before manual review is required
```

**Pattern Matching Rules:**
- Use `|` to separate multiple patterns
- Supports shell glob patterns (`*`, `?`, `[]`)
- Case-sensitive matching
- Paths are relative to repository root

### Git Operation Settings

```yaml
# Enhanced git change detection configuration
git_timeout_seconds: 30                  # Timeout for individual git operations
git_retry_attempts: 3                    # Number of retry attempts for failed git operations
git_retry_delay_seconds: 5               # Delay between retry attempts (exponential backoff)
network_timeout_seconds: 60              # Network operation timeout
```

## Configuration Validation Script

Use the provided validation script to check configuration validity:

```bash
# Run configuration validation
./scripts/validate-auto-update-reboot-config.sh
```

The script will:
- Check all configuration values are in valid ranges
- Validate boolean settings are true/false
- Ensure time formats are correct
- Verify email addresses and URLs
- Check for security best practices
- Report errors and warnings

## Best Practices

### Security
1. Never store passwords directly in config.yaml
2. Use environment variables for sensitive credentials
3. Enable configuration validation
4. Regularly review emergency override settings
5. Monitor force reboot usage

### Performance
1. Set appropriate log levels for production
2. Disable debug logging in production
3. Use reasonable timeout values
4. Monitor system resource usage

### Reliability
1. Configure proper notification channels
2. Set conservative safety thresholds
3. Use maintenance windows for critical reboots
4. Enable comprehensive logging
5. Regularly test emergency procedures

### Monitoring
1. Enable notifications for critical events
2. Monitor reboot attempt patterns
3. Track system health over time
4. Review change detection accuracy
5. Audit emergency override usage

## Troubleshooting

### Common Issues

1. **Configuration not loading**
   - Check config.yaml syntax
   - Verify file permissions
   - Run validation script

2. **Notifications not working**
   - Verify notification settings are enabled
   - Check network connectivity
   - Validate email/webhook configurations

3. **Reboots not triggering**
   - Check file pattern matching
   - Verify change detection is working
   - Review safety check logs

4. **Emergency overrides not working**
   - Verify authentication credentials
   - Check file permissions for emergency stop file
   - Review override logs

### Debug Mode

Enable debug mode for comprehensive troubleshooting:

```yaml
auto_update_reboot_logging:
  debug_mode: true
  verbose_change_detection: true
  trace_git_operations: true
```

Remember to disable debug mode after troubleshooting is complete.