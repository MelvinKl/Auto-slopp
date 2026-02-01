# Beads Updater Integration Guide

## Overview

The **Beads Updater Script** (`scripts/beads_updater.sh`) provides automated repository synchronization and beads state management for the Repository Automation System. This is a critical P0 component that ensures beads state consistency across multiple repositories.

## Features

### Core Functionality
- **Automated Sync Engine**: Automatically syncs beads state across repositories
- **Conflict Resolution**: Handles merge conflicts in beads files with configurable strategies  
- **State Validation**: Verifies beads integrity before and after sync operations
- **Rollback Capability**: Safe rollback mechanism when sync operations fail
- **Comprehensive Reporting**: Detailed JSON reports for audit and monitoring

### Integration Points
- **Configuration System**: Reads from `config.yaml` for settings
- **Logging Integration**: Uses the enhanced timestamped logging system
- **Error Handling**: Integrates with `utils.sh` error handling utilities
- **Git Workflow**: Compatible with existing git automation

## Configuration

### Environment Variables
```bash
# Logging
LOG_LEVEL="INFO"                    # DEBUG, INFO, WARNING, ERROR
LOG_DIRECTORY="~/git/Auto-logs"     # Directory for log files
TIMESTAMP_FORMAT="readable"         # Timestamp format
TIMESTAMP_TIMEZONE="local"          # Timezone setting

# Beads Updater Specific
BEADS_UPDATER_VERSION="1.0.0"      # Script version
DEBUG_MODE="false"                  # Enable debug logging
```

### Configuration File (config.yaml)
```yaml
# Beads updater specific settings can be added here
beads_updater:
  default_sync_mode: "incremental"  # "incremental" or "full"
  default_conflict_strategy: "newest"  # "newest", "manual", "keep_local", "keep_remote"
  default_max_retries: 3
  backup_retention_days: 30
```

## Usage

### Command Line Interface
```bash
# Basic usage - uses defaults
./scripts/beads_updater.sh

# Specify sync mode and conflict strategy
./scripts/beads_updater.sh --mode full --strategy keep_local

# Validation only
./scripts/beads_updater.sh --validate-only

# List available backups
./scripts/beads_updater.sh --list-backups

# Restore from backup
./scripts/beads_updater.sh --restore /path/to/backup

# Show help
./scripts/beads_updater.sh --help
```

### Integration with Main Automation

The beads updater is automatically executed by `main.sh` as part of the script discovery system. No additional configuration is required - it will run on each automation cycle.

## Conflict Resolution Strategies

### 1. Newest (Default)
- **Behavior**: Uses beads' default "newest" conflict resolution
- **Use Case**: Standard automated operation
- **Risk Level**: Low

### 2. Manual
- **Behavior**: Requires manual intervention for conflicts
- **Use Case**: When you need to review every conflict
- **Risk Level**: Low (but requires human intervention)

### 3. Keep Local
- **Behavior**: Always preserves local changes during conflicts
- **Use Case**: When local changes take priority
- **Risk Level**: Medium (potential data loss on remote)

### 4. Keep Remote
- **Behavior**: Always preserves remote changes during conflicts  
- **Use Case**: When remote changes take priority
- **Risk Level**: Medium (potential data loss locally)

## Backup and Restore

### Automatic Backups
The script automatically creates backups before each sync attempt:
- **Location**: `~/.beads_updater_backups/`
- **Naming**: `operation_name_timestamp/`
- **Contents**: `.beads/issues.jsonl`, `.beads/interactions.jsonl`, `.beads/metadata.json`, `.beads/config.yaml`
- **Metadata**: `backup_info.json` with detailed backup information

### Manual Restore
```bash
# List available backups
./scripts/beads_updater.sh --list-backups

# Restore from specific backup
./scripts/beads_updater.sh --restore ~/.beads_updater_backups/pre_sync_20260131_120000
```

## Monitoring and Troubleshooting

### Log Files
- **Main Log**: `~/git/Auto-logs/beads_updater.log`
- **Sync Reports**: `~/git/Auto-logs/beads_updater_report_*.json`
- **Debug Logs**: When `DEBUG_MODE=true`, additional detail is logged

### Sync Report Format
Each sync operation generates a detailed JSON report:
```json
{
  "sync_report": {
    "timestamp": "2026-01-31T11:41:07+00:00",
    "script_version": "1.0.0", 
    "exit_code": 0,
    "success": true,
    "sync_operation": {
      "mode": "incremental",
      "conflict_strategy": "newest",
      "max_retries": 3,
      "backups_created": 1
    },
    "beads_status": {
      "pending_changes": 0,
      "last_export": "2026-01-31 11:37:12",
      "conflicts": "none"
    },
    "git_status": {
      "modified_files": 3,
      "current_commit": "44acb55c388a74d2faedeb7066865fe79b8ce4ea",
      "current_branch": "ai"
    },
    "system_info": {
      "hostname": "server",
      "user": "automation",
      "working_directory": "/path/to/repo"
    }
  }
}
```

### Common Issues and Solutions

#### 1. Sync Conflicts
```bash
# Check current sync status
bd sync --status

# Manual conflict resolution
bd sync

# Force strategy selection
./scripts/beads_updater.sh --strategy keep_local
```

#### 2. Lock File Issues
```bash
# Remove stale lock file
rm -f /tmp/beads_updater.lock
```

#### 3. Backup Space Issues
```bash
# Clean old backups
find ~/.beads_updater_backups -name "*" -type d -mtime +30 -exec rm -rf {} \;
```

## Performance Considerations

### Sync Modes
- **Incremental**: Faster, only syncs changes (recommended)
- **Full**: Slower, complete sync (use for troubleshooting)

### Optimization Tips
1. **Use incremental sync** for regular operations
2. **Monitor backup directory size** and clean old backups
3. **Set appropriate log rotation** in config.yaml
4. **Use appropriate conflict strategy** to minimize manual intervention

## Security Considerations

### Access Control
- Script runs with permissions of the executing user
- Backups are stored in user home directory
- Log files may contain sensitive beads data

### Recommendations
1. **Restrict access** to `~/.beads_updater_backups/`
2. **Regular cleanup** of old backups and logs
3. **Monitor log files** for sensitive data exposure
4. **Use secure file permissions** for bead repositories

## Testing

### Test Suite
Run the comprehensive test suite:
```bash
./tests/test_beads_updater.sh
```

### Test Coverage
- ✅ Script existence and execution
- ✅ Help functionality  
- ✅ Validate-only mode
- ✅ Backup creation and restoration
- ✅ Sync report generation
- ✅ Conflict resolution
- ✅ Error handling
- ✅ Logging integration
- ✅ Lock file mechanism

## Integration with Existing Systems

### Main Automation
- Automatically discovered and executed by `main.sh`
- Uses existing logging configuration from `config.yaml`
- Integrates with error handling from `utils.sh`

### Git Workflow
- Works with existing git automation (implementer.sh, updater.sh, etc.)
- Respects git branch structure (ai/main workflow)
- Compatible with existing git hooks and automation

### Beads System
- Uses standard `bd` CLI commands
- Compatible with existing beads configuration
- Works with beads sync (git-portable mode)

## Version History

### v1.0.0 (2026-01-31)
- Initial release
- Core sync functionality
- Backup/restore system
- Conflict resolution strategies
- Comprehensive reporting
- Integration with existing automation systems

## Support and Maintenance

### Regular Maintenance
1. **Monitor backup directory size**
2. **Review log retention policies**
3. **Update test suite with new features**
4. **Monitor sync success rates**

### Troubleshooting Checklist
1. ✅ Check `bd sync --status` for current state
2. ✅ Review latest sync report for error details
3. ✅ Check log files for detailed error information  
4. ✅ Verify beads data integrity with `--validate-only`
5. ✅ Consider restore from backup if needed

### Contact and Support
Refer to the main project documentation or create a bead issue for bugs and feature requests.