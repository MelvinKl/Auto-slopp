# Auto-Update-Reboot Implementation Guide

## Overview

The auto-update-reboot functionality has been implemented to safely detect repository changes and conditionally reboot the system when significant updates are detected. This guide covers the implementation details, configuration options, and operational procedures.

## Architecture Summary

### Core Components

1. **auto-update-reboot.sh** - Main script located in `scripts/` directory
2. **Configuration Integration** - Extended `config.yaml` with new settings
3. **Enhanced Logging** - Specialized logging functions for auto-update events
4. **State Management** - Persistent state tracking for safety mechanisms

### Safety Mechanisms

- **Cooldown Period**: Prevents reboot loops (configurable, default 60 minutes)
- **Daily Limits**: Maximum reboots per day (configurable, default 3)
- **System Health Checks**: Validates disk space and memory before reboot
- **Maintenance Mode**: Manual override to prevent reboots during maintenance
- **State Persistence**: Tracks reboot history and system status

## Configuration

### Basic Configuration (config.yaml)

```yaml
# Auto-update-reboot configuration
auto_update_reboot_enabled: false        # Master switch (recommended: false initially)
reboot_cooldown_minutes: 60             # Minimum time between reboots
reboot_delay_seconds: 30                # Grace period before reboot
max_reboot_attempts_per_day: 3          # Daily limit on reboot attempts
maintenance_mode: false                  # Manual override for maintenance
emergency_override: false               # Emergency override (use with caution)
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `auto_update_reboot_enabled` | boolean | false | Master switch for functionality |
| `reboot_cooldown_minutes` | integer | 60 | Minimum time between reboots |
| `reboot_delay_seconds` | integer | 30 | Grace period before actual reboot |
| `max_reboot_attempts_per_day` | integer | 3 | Daily reboot limit |
| `maintenance_mode` | boolean | false | Prevent all reboots when true |
| `emergency_override` | boolean | false | Override safety checks (dangerous) |

## Operation

### How It Works

1. **Discovery**: Script automatically discovered and executed by `main.sh`
2. **Change Detection**: Monitors Auto-slopp repository for changes
3. **Trigger Analysis**: Identifies changes that require reboot (scripts, config, main components)
4. **Safety Validation**: Runs system health checks and validates cooldown periods
5. **Reboot Execution**: Performs graceful reboot with notifications

### Change Detection Rules

The following file changes trigger reboot consideration:
- `scripts/*.sh` - Any script changes
- `config.yaml` - Configuration changes
- `main.sh` - Main orchestrator changes
- `scripts/utils.sh` - Core utilities changes

**Excluded changes:**
- `logs/*` - Log files
- `*.tmp` - Temporary files
- `.git/*` - Git metadata

### State Management

State is maintained in `{LOG_DIRECTORY}/auto-update-reboot.state`:
```json
{
  "last_reboot_timestamp": "2026-01-30T17:00:00Z",
  "reboot_attempts_today": 2,
  "current_date": "2026-01-30",
  "last_known_heads": {
    "/path/to/repo": "abc123..."
  },
  "system_health_status": "healthy"
}
```

## Safety Features

### Cooldown Protection

Prevents reboot loops by enforcing minimum time between reboots:
```bash
# Example: 60-minute cooldown prevents rapid reboots
reboot_cooldown_minutes: 60
```

### Daily Limits

Restricts total reboots per day to prevent system instability:
```bash
# Maximum 3 reboots per day
max_reboot_attempts_per_day: 3
```

### System Health Checks

Validates system state before reboot:
- **Disk Space**: Must have >10% free space
- **Memory Usage**: Must have >10% free memory
- **Critical Services**: Checks for failed systemd services

### Maintenance Mode

Manual override to prevent reboots during maintenance:
```yaml
# Set to true to disable all auto-reboots
maintenance_mode: true
```

## Logging and Monitoring

### Enhanced Logging

Specialized logging functions provide detailed insight:
- `log_change_detection()` - Repository change events
- `log_system_health()` - Health check results
- `log_reboot_event()` - Reboot scheduling and execution
- `log_system_state_snapshot()` - Pre-reboot system state

### System State Snapshots

Before reboot, captures system state to `{LOG_DIRECTORY}/system-state-{timestamp}.json`:
```json
{
  "timestamp": "2026-01-30T17:00:00Z",
  "uptime": " 17:00:00 up 2 days,  3:45,  1 user,  load average: 0.15, 0.12, 0.10",
  "disk_usage": "15%",
  "memory_usage": "2.1G/8.0G",
  "load_average": " 0.15, 0.12, 0.10",
  "git_status": "0 files modified"
}
```

## Integration with Existing System

### Main.sh Integration

The script follows established patterns:
- Located in `scripts/auto-update-reboot.sh`
- Automatically discovered by `main.sh`
- Uses standard loading sequence (config.sh → utils.sh → error handling)

### Configuration System

- Extended existing `config.yaml` with new section
- Uses established YAML parsing in `yaml_config.sh`
- Maintains backward compatibility

### Logging Integration

- Uses existing `log()` function from `utils.sh`
- Follows established log level hierarchy
- Integrates with log rotation and retention

## Testing

### Test Suite

Comprehensive test suite available at `tests/test_auto-update-reboot.sh`:
- Configuration loading validation
- Script discovery and execution
- Logging function availability
- State management testing
- Integration testing

### Running Tests

```bash
# Run the complete test suite
./tests/test_auto-update-reboot.sh

# Expected output: 13/13 tests passing
```

## Deployment and Operation

### Initial Setup

1. **Configuration**: Review and update `config.yaml` settings
2. **Validation**: Run test suite to verify implementation
3. **Dry Run**: Start with `auto_update_reboot_enabled: false`
4. **Monitoring**: Check logs and validate behavior
5. **Production**: Enable when confident in configuration

### Monitoring Procedures

1. **Daily**: Check log files for unusual patterns
2. **Weekly**: Review state files and system snapshots
3. **Monthly**: Validate configuration and safety limits
4. **After Changes**: Monitor behavior after system updates

### Troubleshooting

#### Common Issues

**Script not executing:**
- Check file permissions: `chmod +x scripts/auto-update-reboot.sh`
- Verify main.sh discovery: `find scripts/ -name "*.sh"`
- Check configuration: `auto_update_reboot_enabled`

**Unexpected reboots:**
- Review log files for change detection events
- Validate cooldown and daily limits
- Check maintenance mode setting
- Review system state snapshots

**Configuration issues:**
- Run test suite: `./tests/test_auto-update-reboot.sh`
- Check YAML syntax: `bash -n scripts/yaml_config.sh`
- Validate config loading: `grep AUTO_UPDATE_REBOOT_ENABLED config.yaml`

## Security Considerations

### Access Control

- Script runs with same permissions as main.sh
- State files stored in configured log directory
- No external dependencies beyond standard Linux utilities

### Fail-Safe Design

- All safety checks must pass before reboot
- Multiple reboot methods with fallbacks
- Comprehensive error handling and logging
- Emergency override available for critical situations

### Audit Trail

- All operations logged with timestamps
- System state preserved before reboots
- Configuration changes tracked through git
- State files provide operational history

## Maintenance

### Regular Tasks

1. **Log Rotation**: Automatically handled by existing system
2. **State Cleanup**: State files maintained automatically
3. **Configuration Review**: Monthly validation of settings
4. **Test Validation**: Run test suite after changes

### Updates and Changes

- All modifications should follow established patterns
- Update documentation when changing behavior
- Test thoroughly in non-production environment
- Commit changes following project workflow

## Support and Escalation

For issues or questions about the auto-update-reboot functionality:

1. **Check Logs**: Review relevant log files in `{LOG_DIRECTORY}`
2. **Run Tests**: Execute test suite for validation
3. **Review State**: Check state file for operational history
4. **System Status**: Verify system health and configuration
5. **Emergency**: Use `maintenance_mode: true` to disable if needed

This implementation provides a robust, safe, and maintainable auto-update-reboot system that integrates seamlessly with the existing Auto-slopp automation infrastructure.