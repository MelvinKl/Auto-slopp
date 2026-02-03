# Branch Cleanup Documentation

## Overview

The Auto-slopp system provides two branch cleanup scripts with different levels of sophistication:

1. **`cleanup-branches.sh`** - Basic branch cleanup for simple operations
2. **`cleanup-branches-enhanced.sh`** - Advanced branch cleanup with comprehensive safety features

This guide focuses on the enhanced version, which provides enterprise-grade safety mechanisms, detailed analysis, and flexible operation modes.

## Features

### Core Functionality
- **Automatic Detection**: Identifies local branches that no longer exist on remote
- **Safe Deletion**: Multi-stage safety verification before any deletion
- **Backup Creation**: Automatic patch backups before deletion (configurable)
- **Comprehensive Logging**: Detailed operation logging with performance tracking
- **Interactive Confirmation**: Flexible confirmation options for different use cases

### Advanced Features
- **Dry Run Mode**: Preview exactly what would be deleted without making changes
- **Batch Processing**: Handle multiple repositories efficiently
- **Safety Limits**: Prevent accidental mass deletions
- **Branch Analysis**: Detailed branch state analysis with conflict detection
- **Configuration Integration**: Full integration with Auto-slopp configuration system
- **Error Recovery**: Robust error handling with retry mechanisms

## Quick Start

### Basic Usage

```bash
# Run with default configuration (interactive mode)
./scripts/cleanup-branches-enhanced.sh

# Preview what would be deleted (recommended first step)
./scripts/cleanup-branches-enhanced.sh --dry-run

# Run automatically without prompts (for automation)
./scripts/cleanup-branches-enhanced.sh --no-confirmation
```

### Recommended Workflow

1. **First Time Setup**:
   ```bash
   # Test with dry-run to see what would be deleted
   ./scripts/cleanup-branches-enhanced.sh --dry-run --show-details
   ```

2. **Review Results**:
   - Check the dry-run output carefully
   - Verify that important branches are protected
   - Confirm backup settings are appropriate

3. **Execute Cleanup**:
   ```bash
   # Run with interactive confirmations
   ./scripts/cleanup-branches-enhanced.sh
   ```

## Command Line Options

### Basic Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--help` | `-h` | Show help message and exit | `-h` |
| `--dry-run` | `-d` | Enable dry-run mode (simulation only) | `-d` |
| `--no-confirmation` | `-y` | Skip all confirmation prompts | `-y` |
| `--interactive` | `-i` | Enable interactive prompts for each operation | `-i` |
| `--batch-confirmation` | `-b` | Enable batch confirmation vs individual | `-b` |

### Advanced Options

| Option | Description | Type | Default | Example |
|--------|-------------|-------|---------|---------|
| `--timeout SECONDS` | Set confirmation prompt timeout | integer | 60 | `--timeout 120` |
| `--max-branches COUNT` | Maximum branches to delete in one run | integer | 50 | `--max-branches 10` |
| `--no-backup` | Disable creating backup patches | flag | enabled | `--no-backup` |
| `--no-safety` | Disable safety checks (dangerous) | flag | enabled | `--no-safety` |
| `--show-details` | Show detailed branch information | flag | enabled | `--show-details` |
| `--hide-summary` | Hide detailed summary in dry-run mode | flag | enabled | `--hide-summary` |

### Usage Examples

#### Safe Interactive Usage
```bash
# Run with full interactivity and details
./scripts/cleanup-branches-enhanced.sh --interactive --show-details --max-branches 10
```

#### Automated Usage
```bash
# Run automatically for CI/CD
./scripts/cleanup-branches-enhanced.sh --no-confirmation --batch-confirmation --max-branches 100
```

#### Testing and Validation
```bash
# Comprehensive dry-run analysis
./scripts/cleanup-branches-enhanced.sh --dry-run --show-details --show-safety-info
```

#### Production Safety
```bash
# Conservative production run
./scripts/cleanup-branches-enhanced.sh --interactive --max-branches 5 --timeout 120
```

## Configuration

### Configuration File Section

Add the following to your `config.yaml`:

```yaml
# Enhanced branch cleanup configuration
branch_cleanup:
  # Dry-run and interactive mode settings
  dry_run_mode: false                  # Enable dry-run mode by default
  interactive_mode: true               # Enable interactive prompts
  confirm_before_delete: true          # Confirm before each branch deletion
  show_dry_run_summary: true           # Show detailed summary in dry-run mode
  batch_confirmation: false            # Confirm all operations at once vs individual
  confirmation_timeout: 60            # Timeout for confirmation prompts (seconds)
  
  # Safety and operational settings
  safety_mode: true                    # Enable all safety checks by default
  backup_before_delete: true           # Create backup patches before deletion
  max_branches_per_run: 50            # Maximum branches to delete in one run
  
  # Dry-run specific settings
  show_branch_details: true            # Show detailed branch info in dry-run
  show_safety_info: true               # Show safety configuration in dry-run
  show_skipped_branches: true          # Show why branches are skipped in dry-run
```

### Environment Variable Overrides

You can override configuration using environment variables:

```bash
# Override specific settings
export branch_cleanup_dry_run_mode=true
export branch_cleanup_max_branches_per_run=10
export branch_cleanup_interactive_mode=false

./scripts/cleanup-branches-enhanced.sh
```

### Priority Order

1. **Command Line Arguments** (highest priority)
2. **Environment Variables**
3. **Configuration File** (`config.yaml`)
4. **Default Values** (lowest priority)

## Safety Features

### Multi-Stage Protection

#### Stage 1: Basic Safety Checks
- Never delete current branch
- Never delete protected branches (main, master, develop, etc.)
- Validate repository access and git health
- Check file permissions

#### Stage 2: Advanced Safety Analysis
- Check for unmerged changes
- Detect dependent branches
- Verify no stashed changes
- Analyze branch relationships

#### Stage 3: Contextual Safety Checks
- Check for configuration file references
- Look for branch-specific files/directories
- Validate branch age and activity
- Assess potential impact

#### Stage 4: Temporal Safety Checks
- Don't delete very recent branches (< 7 days)
- Be cautious with recently active branches (< 24 hours)
- Consider branch lifecycle patterns

### Protection Mechanisms

#### Protected Branches
The following branches are never deleted:
- `main`, `master`, `develop`, `HEAD`
- `staging`, `production`
- Currently checked-out branch
- Branches matching protection patterns: `keep-*`, `protected-*`, `temp-*`, `backup-*`

#### Safety Limits
- `max_branches_per_run`: Prevents mass deletions
- Confirmation timeouts prevent hanging operations
- Interactive mode provides human oversight
- Dry-run mode enables safe testing

#### Backup System
```bash
# Automatic backup creation
backup_dir="${BACKUP_DIR:-/tmp/autoslopp_branch_backups}"
backup_file="$backup_dir/${branch}_$(date +%Y%m%d_%H%M%S).patch"

# Backup creation process
git format-patch --stdout "$branch" > "$backup_file"
```

## Dry Run Mode

### What Dry Run Shows

```bash
🔍 DRY RUN ANALYSIS
═══════════════════════════════════════════════════════════════

Repository: my-repo
Operation: Branch Cleanup (SIMULATION)
Date: 2026-02-03 08:45:12

🗑️  Branches that would be DELETED:

 1. feature-old-api
     Last commit: abc123 | Fix authentication bug
     Age: 45 days old
     Status: ✅ Merged | ✅ No untracked changes
     📦 Backup: Would create patch backup before deletion

 2. hotfix-temp-patch
     Last commit: def456 | Temporary fix
     Age: 12 days old
     Status: ✅ Merged | ⚠️  Has untracked changes
     📦 Backup: Would create patch backup before deletion

Total branches to delete: 2

🛡️  Branches that would be SKIPPED:

  • main (protected branch)
  • keep-backup-branch (protection pattern)
  • current-feature (current branch)

Total branches skipped: 3

🔒 Safety Information:
  • Backup before delete: true
  • Safety mode: true
  • Max branches per run: 50
  • Interactive mode: true
  • Confirm before delete: true
  • Confirmation timeout: 60s
```

### Dry Run Benefits

1. **Risk Assessment**: See exactly what would be affected
2. **Safety Verification**: Confirm protection rules are working
3. **Impact Analysis**: Understand the scope of changes
4. **Planning**: Plan maintenance windows appropriately
5. **Training**: Learn system behavior safely

## Interactive Mode

### Individual Branch Confirmation

```bash
🔄 BRANCH DELETION CONFIRMATION
═══════════════════════════════════════════════════════════════

About to delete branch: feature-old-api
Repository: my-repo
Last commit: abc123 | Fix authentication bug

Options:
  ✅ yes     - Delete this branch
  ⏭️  skip    - Skip this branch
  ℹ️  info    - Show detailed branch information
  ❌ cancel  - Cancel all operations

Your choice [yes]: 
```

### Batch Confirmation

```bash
🔄 BATCH CONFIRMATION REQUIRED
═══════════════════════════════════════════════════════════════

You are about to delete 5 branches
Repository: my-repo

This will:
  • Create backup patches for each branch
  • Delete 5 local branches
  • This operation cannot be undone!

Proceed with cleanup operation? [no]: yes
```

### Response Options

| Option | Action | Use Case |
|--------|--------|----------|
| `yes` | Delete the branch | Normal operation |
| `skip` | Skip this branch only | Want to continue but save this branch |
| `info` | Show detailed branch information | Need more context before deciding |
| `cancel` | Cancel all operations | Something looks wrong, stop everything |

## Integration with Auto-slopp

### System Integration Points

1. **Configuration System**: Uses `yaml_config.sh` for settings
2. **Logging System**: Integrates with colored logging and rotation
3. **Error Handling**: Uses `utils.sh` error handling functions
4. **Branch Protection**: Integrates with `branch_protection.sh`
5. **State Management**: Tracks operation state and performance

### Main System Integration

The branch cleanup script can be called from the main automation loop:

```bash
# In main.sh or custom automation
./scripts/cleanup-branches-enhanced.sh --batch-confirmation --max-branches 10
```

### Beads Integration

Branch cleanup operations can be tracked through beads:

```bash
# Create task for branch cleanup
bd create "Perform branch cleanup maintenance" --type=task --priority=2

# Complete after successful cleanup
bd close <task-id> --reason="Branch cleanup completed successfully"
```

## Performance and Monitoring

### Performance Metrics

The script automatically tracks:
- Operation duration
- Branches processed per repository
- Success/failure rates
- Backup creation time
- Confirmation response time

### Monitoring Commands

```bash
# Check recent cleanup operations
grep "cleanup-branches-enhanced" ~/git/Auto-logs/*.log | tail -20

# Performance analysis
grep "elapsed_time" ~/git/Auto-logs/*.log | grep "cleanup"

# Error analysis
grep "ERROR.*cleanup-branches" ~/git/Auto-logs/*.log
```

### Health Monitoring

```bash
# Check backup directory usage
du -sh /tmp/autoslopp_branch_backups/

# Verify recent backups
ls -la /tmp/autoslopp_branch_backups/ | tail -10

# Check for orphaned locks
find /tmp -name "*cleanup*lock*" -ls
```

## Troubleshooting

### Common Issues

#### 1. Script Won't Run

```bash
# Check permissions
ls -la scripts/cleanup-branches-enhanced.sh

# Make executable
chmod +x scripts/cleanup-branches-enhanced.sh
```

#### 2. Configuration Not Loading

```bash
# Check configuration syntax
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Test configuration loading
source scripts/yaml_config.sh && load_config
echo "DRY_RUN_MODE: $DRY_RUN_MODE"
```

#### 3. Branch Protection Not Working

```bash
# Check branch protection configuration
grep -A 10 "branch_protection:" config.yaml

# Test protection manually
./scripts/branch_protection.sh --test
```

#### 4. Backup Creation Failing

```bash
# Check backup directory permissions
ls -la /tmp/autoslopp_branch_backups/

# Create backup directory
mkdir -p /tmp/autoslopp_branch_backups/
chmod 755 /tmp/autoslopp_branch_backups/
```

#### 5. Network Issues

```bash
# Test remote connectivity
cd ~/git/managed/your-repo
git ls-remote --heads origin

# Check network settings
git config --get remote.origin.url
```

### Debug Mode

Enable comprehensive debugging:

```bash
# Enable debug mode
export DEBUG_MODE=true

# Run with maximum output
./scripts/cleanup-branches-enhanced.sh --dry-run --show-details --debug
```

### Log Analysis

```bash
# Recent cleanup logs
tail -f ~/git/Auto-logs/$(date +%Y-%m-%d).log | grep "cleanup-branches"

# Error analysis
grep -i "error.*cleanup" ~/git/Auto-logs/*.log

# Performance analysis
grep "operation.*cleanup.*completed" ~/git/Auto-logs/*.log
```

## Best Practices

### Production Environment

1. **Always use dry-run first** to preview changes
2. **Enable interactive mode** for human oversight
3. **Set conservative limits** for `max_branches_per_run`
4. **Enable backup creation** for recovery options
5. **Monitor logs regularly** for issues or patterns
6. **Test in development** before production deployment

### Automation/CI/CD

1. **Use batch confirmation** for efficiency
2. **Set appropriate timeouts** to prevent hanging
3. **Configure monitoring** for operation tracking
4. **Implement alerting** for failed operations
5. **Regular backup maintenance** for storage management
6. **Performance monitoring** to identify bottlenecks

### Development Environment

1. **Use dry-run mode** extensively for testing
2. **Enable detailed output** for learning and debugging
3. **Test safety features** with various scenarios
4. **Verify configuration** changes before deployment
5. **Document custom settings** for team knowledge
6. **Regular cleanup testing** to maintain familiarity

## Advanced Usage

### Custom Protection Patterns

Add custom protection patterns to your configuration:

```yaml
branch_protection:
  protection_patterns:
    - "keep-*"           # Keep branches
    - "protected-*"      # Protected branches
    - "temp-*"           # Temporary branches
    - "backup-*"         # Backup branches
    - "release-*"        # Release branches
    - "hotfix-*"         # Hotfix branches
    - "feature-wip-*"    # Work in progress
```

### Custom Backup Location

Override backup directory:

```bash
export BACKUP_DIR="/mnt/backups/branch_cleanup"
./scripts/cleanup-branches-enhanced.sh
```

### Integration with Monitoring Systems

Create custom monitoring hooks:

```bash
#!/bin/bash
# cleanup-monitoring-hook.sh

# Pre-cleanup monitoring
./scripts/monitoring/collect-metrics.sh --before-cleanup

# Run cleanup
./scripts/cleanup-branches-enhanced.sh "$@"

# Post-cleanup monitoring
./scripts/monitoring/collect-metrics.sh --after-cleanup
./scripts/monitoring/send-alerts.sh
```

### Scheduled Maintenance

Set up cron jobs for regular cleanup:

```bash
# Weekly branch cleanup (Sundays at 2 AM)
0 2 * * 0 /path/to/Auto-slopp/scripts/cleanup-branches-enhanced.sh --batch-confirmation --max-branches 20

# Monthly backup cleanup
0 3 1 * * /path/to/Auto-slopp/scripts/cleanup-backups.sh
```

## Recovery Procedures

### Restoring from Backups

```bash
# List available backups
ls -la /tmp/autoslopp_branch_backups/

# Restore a specific branch
cd ~/git/managed/your-repo
git checkout -b restored-feature-abc
git apply /tmp/autoslopp_branch_backups/feature-abc_20260203_084512.patch

# Push restored branch if needed
git push origin restored-feature-abc
```

### Emergency Procedures

```bash
# Stop all cleanup operations
pkill -f cleanup-branches-enhanced

# Check for active locks
find /tmp -name "*cleanup*lock*" -ls

# Force cleanup (dangerous)
./scripts/cleanup-branches-enhanced.sh --no-safety --no-confirmation
```

## Security Considerations

### Access Control

1. **File Permissions**: Ensure proper permissions on scripts and configuration
2. **Backup Security**: Secure backup directory with appropriate permissions
3. **Git Credentials**: Protect remote access credentials
4. **Audit Trail**: Maintain logs for compliance and debugging

### Risk Mitigation

1. **Defense in Depth**: Multiple safety layers prevent accidents
2. **Configuration Validation**: Validate settings before execution
3. **Timeout Protection**: Prevent hanging operations
4. **Rollback Capability**: Backup system enables recovery

### Compliance

1. **Audit Logging**: All operations are logged with timestamps
2. **Change Tracking**: Git operations maintain audit trails
3. **Backup Retention**: Configure appropriate backup retention policies
4. **Access Logging**: Monitor who runs cleanup operations

## API Reference

### Script Functions

#### Core Functions
- `cleanup_repository_enhanced()` - Main cleanup workflow
- `analyze_branches_comprehensive()` - Branch analysis
- `safe_delete_branch_enhanced()` - Safe branch deletion
- `show_dry_run_analysis()` - Dry-run analysis display

#### Safety Functions
- `verify_branch_safety_comprehensive()` - Multi-stage safety checks
- `verify_basic_safety()` - Basic safety validation
- `verify_advanced_safety()` - Advanced safety analysis
- `verify_contextual_safety()` - Contextual safety checks

#### Utility Functions
- `create_branch_backup()` - Backup creation
- `request_user_confirmation()` - User prompts
- `show_configuration()` - Configuration display
- `validate_configuration_values()` - Configuration validation

### Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Operation completed successfully |
| 1 | General Error | Check logs for details |
| 2 | User Cancelled | Operation cancelled by user |
| 3 | Configuration Error | Fix configuration issues |
| 4 | Safety Check Failed | Review safety settings |

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `DEBUG_MODE` | Enable debug output | false |
| `BACKUP_DIR` | Backup directory location | `/tmp/autoslopp_branch_backups` |
| `CLEANUP_OPERATION_ID` | Unique operation identifier | Auto-generated |

---

*This documentation covers the enhanced branch cleanup script. For basic cleanup operations, see `cleanup-branches.sh`. For related branch protection features, see the branch protection documentation.*