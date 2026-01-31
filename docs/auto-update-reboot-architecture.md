# Auto-Update-Reboot Architecture Design

## Overview

This document outlines the architecture for the auto-update-reboot functionality that will safely detect repository changes and conditionally reboot the system when significant updates are detected.

## 1. Script Placement and Naming Convention

Following the established pattern, the script will be:

- **File**: `scripts/auto-update-reboot.sh`
- **Executable**: Standard bash script with execute permissions
- **Discovery**: Automatically discovered and executed by `main.sh` in alphabetical order

## 2. Integration with Existing config.yaml System

### Configuration Schema Extensions

```yaml
# Auto-update-reboot configuration (add to existing config.yaml)
auto_update_reboot:
  # Enable/disable the auto-update-reboot functionality
  enabled: false
  
  # Repository monitoring settings
  repositories:
    - path: '~/git/managed/Auto-slopp'
      name: 'automation-system'
      reboot_triggers:
        - 'scripts/*.sh'
        - 'config.yaml'
        - 'main.sh'
        - 'scripts/utils.sh'
      exclusion_patterns:
        - 'logs/*'
        - '*.tmp'
        - '.git/*'
  
  # Timing and safety settings
  reboot_cooldown_minutes: 60          # Minimum time between reboots
  change_detection_interval_minutes: 5 # How often to check for changes
  reboot_delay_seconds: 30             # Grace period before reboot
  
  # Safety mechanisms
  max_reboot_attempts_per_day: 3
  system_health_checks:
    - 'disk_space'
    - 'memory_usage'
    - 'critical_processes'
  
  # Notification settings
  notifications:
    enabled: true
    pre_reboot_minutes: 5
    methods: ['log', 'systemd']
  
  # Logging configuration
  log_level: 'INFO'
  log_system_state: true
  
  # Override settings
  maintenance_mode: false
  emergency_override: false
```

## 3. Decision Flow Architecture

```
┌─────────────────┐
│ Start Script    │
└─────┬───────────┘
      │
      ▼
┌─────────────────┐     NO     ┌─────────────────┐
│ Check if        │────────────▶│ Exit gracefully │
│ Enabled         │             └─────────────────┘
└─────┬───────────┘
      │ YES
      ▼
┌─────────────────┐     YES    ┌─────────────────┐
│ Check Maintenance│────────────▶│ Skip cycle      │
│ Mode             │             └─────────────────┘
└─────┬───────────┘
      │ NO
      ▼
┌─────────────────┐     YES    ┌─────────────────┐
│ Check Cooldown  │────────────▶│ Log & Skip      │
│ Period          │             └─────────────────┘
└─────┬───────────┘
      │ NO
      ▼
┌─────────────────┐
│ For Each Repo:  │
│ - Git Pull      │
│ - Detect Changes│
└─────┬───────────┘
      │
      ▼
┌─────────────────┐     NO     ┌─────────────────┐
│ Changes Match   │────────────▶│ Log "No changes"│
│ Reboot Triggers?│             └─────────────────┘
└─────┬───────────┘
      │ YES
      ▼
┌─────────────────┐
│ System Health   │
│ Checks          │
└─────┬───────────┘
      │
      ▼
┌─────────────────┐     FAIL    ┌─────────────────┐
│ Health OK?      │────────────▶│ Log "Health fail│
│                 │             │ - Skipping"     │
└─────┬───────────┘      │
      │ PASS              │
      ▼                   │
┌─────────────────┐       │
│ Send Pre-reboot │       │
│ Notifications   │       │
└─────┬───────────┘       │
      │                   │
      ▼                   │
┌─────────────────┐       │
│ Wait Delay      │       │
│ Period          │       │
└─────┬───────────┘       │
      │                   │
      ▼                   │
┌─────────────────┐       │
│ Update State    │       │
│ Files           │       │
└─────┬───────────┘       │
      │                   ▼
      │         ┌─────────────────┐
      │         │ Log & Continue  │
      │         │ Next Cycle      │
      │         └─────────────────┘
      ▼
┌─────────────────┐
│ System Reboot   │
└─────────────────┘
```

## 4. Safety Mechanisms to Prevent Reboot Loops

### 4.1. Multi-layered Protection

1. **Time-based Cooldown**: Configurable minimum time between reboots
2. **Daily Attempt Limit**: Maximum reboots per day (default: 3)
3. **State Tracking**: Persistent tracking of last reboot time and attempts
4. **Health Gates**: System health validation before reboot
5. **Maintenance Mode**: Manual override to prevent reboots during maintenance

### 4.2. State Management

```bash
# State file location
STATE_FILE="${LOG_DIRECTORY}/auto-update-reboot.state"

# State structure
{
  "last_reboot_timestamp": "2026-01-30T17:00:00Z",
  "reboot_attempts_today": 2,
  "current_date": "2026-01-30",
  "last_known_heads": {
    "/path/to/repo1": "abc123...",
    "/path/to/repo2": "def456..."
  },
  "system_health_status": "healthy"
}
```

### 4.3. Cooldown Enforcement

```bash
check_cooldown() {
    local last_reboot=$(get_state_value "last_reboot_timestamp")
    local cooldown_minutes=$(get_config_value "reboot_cooldown_minutes")
    
    if [[ -n "$last_reboot" ]]; then
        local seconds_since_reboot=$(($(date +%s) - $(date -d "$last_reboot" +%s)))
        local cooldown_seconds=$((cooldown_minutes * 60))
        
        if [[ $seconds_since_reboot -lt $cooldown_seconds ]]; then
            local remaining_minutes=$(((cooldown_seconds - seconds_since_reboot) / 60))
            log "WARNING" "Reboot cooldown active. ${remaining_minutes} minutes remaining."
            return 1
        fi
    fi
    return 0
}
```

## 5. Logging Strategy

### 5.1. Integration with Existing Logging System

- Use existing `log()` function from `utils.sh`
- Leverage current log directory and rotation settings
- Follow established log level hierarchy (DEBUG, INFO, WARNING, ERROR, SUCCESS)

### 5.2. Enhanced Logging for Auto-Update-Reboot

```bash
# Specialized logging functions
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

log_reboot_event() {
    local reason="$1"
    local scheduled_time="$2"
    
    log "WARNING" "REBOOT SCHEDULED: $reason"
    log "INFO" "Reboot will occur at: $scheduled_time"
    log_system_state_snapshot
}
```

### 5.3. System State Snapshots

```bash
log_system_state_snapshot() {
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
```

## 6. Error Recovery Procedures

### 6.1. Git Operation Failures

```bash
handle_git_failure() {
    local repo_path="$1"
    local operation="$2"
    local error_output="$3"
    
    log "ERROR" "Git operation '$operation' failed for $repo_path"
    log "DEBUG" "Error details: $error_output"
    
    # Attempt recovery
    case "$operation" in
        "pull")
            log "INFO" "Attempting git recovery: fetch and reset"
            cd "$repo_path"
            git fetch --all || log "ERROR" "Git fetch failed during recovery"
            git reset --hard HEAD || log "ERROR" "Git reset failed during recovery"
            ;;
        "status")
            log "WARNING" "Git status failed, repository may be in corrupted state"
            ;;
    esac
    
    return 1  # Signal failure to caller
}
```

### 6.2. System Health Failures

```bash
handle_health_check_failure() {
    local failed_check="$1"
    local failure_details="$2"
    
    log "ERROR" "System health check failed: $failed_check"
    log "INFO" "Failure details: $failure_details"
    log "WARNING" "Reboot aborted due to system health issues"
    
    # Attempt remediation based on failure type
    case "$failed_check" in
        "disk_space")
            log "INFO" "Attempting basic disk cleanup"
            cleanup_temp_files
            ;;
        "memory_usage")
            log "INFO" "Memory usage too high, consider manual intervention"
            ;;
        "critical_processes")
            log "INFO" "Checking critical process status"
            check_critical_processes
            ;;
    esac
    
    return 1  # Signal reboot should be aborted
}
```

### 6.3. Reboot Failure Handling

```bash
handle_reboot_failure() {
    local reboot_command="$1"
    local error_output="$2"
    
    log "ERROR" "Reboot command failed: $reboot_command"
    log "ERROR" "Error output: $error_output"
    
    # Log system state for debugging
    log_system_state_snapshot
    
    # Try alternative reboot methods
    if command -v systemctl >/dev/null 2>&1; then
        log "INFO" "Attempting alternative reboot via systemctl"
        systemctl reboot || log "ERROR" "systemctl reboot also failed"
    elif command -v shutdown >/dev/null 2>&1; then
        log "INFO" "Attempting alternative reboot via shutdown"
        shutdown -r now || log "ERROR" "shutdown reboot also failed"
    fi
    
    return 1
}
```

## 7. Configuration Parameters Detailed

### 7.1. Enable/Disable Auto-Reboot

- **Purpose**: Master switch for the entire auto-update-reboot functionality
- **Type**: Boolean (true/false)
- **Default**: false (conservative default)
- **Validation**: Must be boolean

### 7.2. Reboot Delay/Timing

- **reboot_cooldown_minutes**: Minimum time between automatic reboots
- **change_detection_interval_minutes**: How often to poll repositories for changes
- **reboot_delay_seconds**: Grace period between reboot decision and actual reboot
- **max_reboot_attempts_per_day**: Daily limit on reboot attempts

### 7.3. Exclusion Conditions

- **exclusion_patterns**: File patterns that should never trigger reboots
- **maintenance_mode**: Manual override to disable all reboots
- **system_health_checks**: Health checks that must pass before reboot

### 7.4. Notification Requirements

- **pre_reboot_minutes**: Warning time before scheduled reboot
- **notification_methods**: How to send notifications (log, systemd, email)
- **log_system_state**: Whether to capture system state before reboot

## 8. Integration Points

### 8.1. Main.sh Integration

The script will be automatically discovered and executed by `main.sh` following the established pattern:
- Located in `scripts/` directory
- Named `auto-update-reboot.sh`
- Executable permissions (755)
- Uses standard script header and loading sequence

### 8.2. Configuration Loading

```bash
# Standard script header following existing patterns
#!/bin/bash

# Auto-update-reboot script with change detection and conditional reboot
# Load utilities and configuration first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# Set up error handling
setup_error_handling

# Configure script-specific variables
SCRIPT_NAME="auto-update-reboot"
```

### 8.3. State Management Integration

- State files stored in configured `LOG_DIRECTORY`
- Rotation follows existing log retention policies
- Integration with existing log rotation mechanisms

## 9. Testing Strategy

### 9.1. Unit Testing Components

1. **Change Detection Logic**: Test with various git scenarios
2. **Configuration Validation**: Test with valid/invalid config values
3. **Health Check Functions**: Test with simulated system states
4. **Cooldown Logic**: Test time-based restrictions
5. **State Management**: Test state file operations

### 9.2. Integration Testing

1. **End-to-End Workflow**: Full cycle without actual reboot
2. **Configuration Integration**: Test with real config.yaml
3. **Main.sh Integration**: Test discovery and execution
4. **Git Repository Integration**: Test with real repository changes

### 9.3. Safety Testing

1. **Reboot Loop Prevention**: Test cooldown and daily limits
2. **System Health Failures**: Test reboot abortion on health failures
3. **Configuration Errors**: Test graceful handling of invalid configs
4. **Network Failures**: Test git operation failure handling

## 10. Maintenance and Modification Guidelines

### 10.1. Configuration Changes

- All configuration changes should be made via `config.yaml`
- Use semantic versioning for configuration schema changes
- Maintain backward compatibility when possible

### 10.2. Script Modifications

- Follow existing code patterns and conventions
- Use established error handling and logging mechanisms
- Update this design document for architectural changes

### 10.3. Monitoring and Debugging

- Monitor log files for unusual reboot patterns
- Check state files for persistent issues
- Use system state snapshots for debugging failed reboots
- Validate configuration changes in test environment first

## 11. Implementation Phases

### Phase 1: Core Infrastructure
- Configuration schema and validation
- Basic change detection logic
- State management system
- Logging integration

### Phase 2: Safety Mechanisms
- Cooldown and daily limits
- System health checks
- Error recovery procedures
- State persistence

### Phase 3: Advanced Features
- Multi-repository support
- Advanced pattern matching
- Notification system
- Comprehensive testing

### Phase 4: Production Readiness
- Performance optimization
- Security hardening
- Documentation completion
- Integration testing

This architecture provides a robust, safe, and maintainable auto-update-reboot system that integrates seamlessly with the existing Auto-slopp automation infrastructure.