# Configuration Documentation

## Overview

The Repository Automation System uses a centralized YAML configuration system for flexible settings management.

## Configuration Files

### `config.yaml`

Main configuration file containing all system settings.

```yaml
# Repository automation configuration
sleep_duration: 1000                # Duration between cycles (seconds)
managed_repo_path: ~/git/managed    # Path containing repository subdirectories
managed_repo_task_path: ~/git/repo_task_path  # Path for task description files
```

### `config.sh`

Legacy configuration loader (now uses `yaml_config.sh` internally).

### `scripts/yaml_config.sh`

YAML configuration utilities that:
- Load and parse YAML configuration
- Validate required settings
- Expand tilde paths (~) to full paths
- Export configuration as environment variables
- Provide configuration validation functions

## Configuration Variables

### Core System Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SLEEP_DURATION` | Time between automation cycles (seconds) | 1000 | Yes |
| `MANAGED_REPO_PATH` | Path containing repository subdirectories | ~/git/managed | Yes |
| `MANAGED_REPO_TASK_PATH` | Path for task description files | ~/git/repo_task_path | Yes |
| `OPencode_CMD` | Path to OpenCode CLI executable | opencode | No |
| `BEADS_CMD` | Path to Beads CLI executable | bd | No |

### Enhanced Logging Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TIMESTAMP_FORMAT` | Timestamp format for logs | readable-precise | No |
| `TIMESTAMP_TIMEZONE` | Timezone for timestamps | local | No |

### Branch Cleanup Configuration Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DRY_RUN_MODE` | Enable dry-run mode by default | false | No |
| `INTERACTIVE_MODE` | Enable interactive prompts | true | No |
| `CONFIRM_BEFORE_DELETE` | Confirm before each branch deletion | true | No |
| `SHOW_DRY_RUN_SUMMARY` | Show detailed summary in dry-run mode | true | No |
| `BATCH_CONFIRMATION` | Confirm all operations at once vs individual | false | No |
| `CONFIRMATION_TIMEOUT` | Timeout for confirmation prompts (seconds) | 60 | No |
| `SAFETY_MODE` | Enable all safety checks by default | true | No |
| `BACKUP_BEFORE_DELETE` | Create backup patches before deletion | true | No |
| `MAX_BRANCHES_PER_RUN` | Maximum branches to delete in one run | 50 | No |
| `SHOW_BRANCH_DETAILS` | Show detailed branch info in dry-run | true | No |
| `SHOW_SAFETY_INFO` | Show safety configuration in dry-run | true | No |
| `SHOW_SKIPPED_BRANCHES` | Show why branches are skipped in dry-run | true | No |
| `LOG_LEVEL` | Minimum log level to output | INFO | No |
| `LOG_DIRECTORY` | Directory for log files | ~/git/Auto-logs | No |
| `LOG_MAX_SIZE_MB` | Maximum log file size before rotation | 10 | No |
| `LOG_MAX_FILES` | Number of rotated log files to keep | 5 | No |
| `LOG_RETENTION_DAYS` | Days to keep old log files | 30 | No |
| `DEBUG_MODE` | Enable debug messages regardless of log level | false | No |

## Path Expansion

The configuration system automatically expands tilde (~) paths:

```yaml
# These are automatically expanded:
managed_repo_path: ~/git/managed        # → /home/user/git/managed
managed_repo_task_path: ~/git/tasks      # → /home/user/git/tasks
```

## Environment Variables

You can override configuration settings using environment variables:

```bash
# Override sleep duration
export SLEEP_DURATION=3600

# Override repository paths
export MANAGED_REPO_PATH=/custom/path/to/repos
export MANAGED_REPO_TASK_PATH=/custom/path/to/tasks

# Override CLI commands
export OPencode_CMD=/path/to/custom/opencode
export BEADS_CMD=/path/to/custom/bd

# Override logging settings
export TIMESTAMP_FORMAT="iso8601"
export TIMESTAMP_TIMEZONE="utc"
export LOG_LEVEL="DEBUG"
export DEBUG_MODE="true"
export LOG_DIRECTORY="/custom/log/path"
```

## Enhanced Logging Configuration

### Timestamp Formats

Available timestamp formats and their use cases:

| Format | Example | Best For |
|--------|---------|----------|
| `default` | `2026-01-31 09:00:01` | General logging |
| `iso8601` | `2026-01-31T09:00:01+00:00` | Production, API integration |
| `rfc3339` | `2026-01-31T09:00:01.123Z` | Web services, JSON logs |
| `syslog` | `Jan 31 09:00:01` | System integration |
| `compact` | `20260131_090001` | Filenames, space-constrained |
| `compact-precise` | `20260131_090001.123` | High-frequency logging |
| `readable` | `2026-01-31 09:00:01` | Human-readable logs |
| `readable-precise` | `2026-01-31 09:00:01.123` | Development (recommended) |
| `debug` | `2026-01-31 09:00:01.123456` | Debugging, performance analysis |
| `microseconds` | `2026-01-31 09:00:01.123456` | Microsecond precision |

### Timezone Options

- `local`: Use system's local timezone (default)
- `utc`: Use UTC timezone for consistent logs across systems
- Specific timezone: `America/New_York`, `Europe/London`, etc.
- Offset format: `+05:30`, `-08:00`, etc.

### Log Levels

Log levels in order of priority (higher numbers = more filtering):

| Level | Priority | Use Case |
|-------|----------|----------|
| `DEBUG` | 0 | Detailed debugging information |
| `INFO` | 1 | General informational messages |
| `SUCCESS` | 1 | Successful operations |
| `WARNING` | 2 | Warning messages for potential issues |
| `ERROR` | 3 | Error messages for failed operations |

Only messages at or above the configured `LOG_LEVEL` will be displayed.

### Example Logging Configurations

#### Production Environment
```yaml
# Production logging configuration
timestamp_format: iso8601
timestamp_timezone: utc
log_level: INFO
log_directory: /var/log/auto-slopp
log_max_size_mb: 50
log_max_files: 10
log_retention_days: 90
debug_mode: false
```

#### Development Environment
```yaml
# Development logging configuration
timestamp_format: readable-precise
timestamp_timezone: local
log_level: DEBUG
log_directory: ~/git/Auto-logs
log_max_size_mb: 10
log_max_files: 5
log_retention_days: 7
debug_mode: true
```

#### High-Performance Environment
```yaml
# High-performance logging configuration
timestamp_format: compact-precise
timestamp_timezone: utc
log_level: WARNING
log_directory: /var/log/auto-slopp
log_max_size_mb: 100
log_max_files: 3
log_retention_days: 30
debug_mode: false
```

## Configuration Loading

Scripts automatically load configuration using:

```bash
# Load configuration utilities
source "$SCRIPT_DIR/yaml_config.sh"

# Load and validate configuration
load_config "$SCRIPT_DIR/../config.yaml"

# Configuration variables are now available as:
# - $SLEEP_DURATION
# - $MANAGED_REPO_PATH
# - $MANAGED_REPO_TASK_PATH
# - $OPencode_CMD
# - $BEADS_CMD
```

## Configuration Validation

The `yaml_config.sh` script provides validation functions:

```bash
# Validate all required configuration
validate_config

# Check if a specific variable is set
if [[ -z "$SLEEP_DURATION" ]]; then
    log "ERROR" "SLEEP_DURATION not configured"
    exit 1
fi

# Validate paths exist
if [[ ! -d "$MANAGED_REPO_PATH" ]]; then
    log "ERROR" "Managed repository path not found: $MANAGED_REPO_PATH"
    exit 1
fi
```

## Debug Mode

Enable debug mode for verbose configuration output:

```bash
export DEBUG_MODE=true
./main.sh
```

This will show:
- Configuration file being loaded
- Variables being set
- Path expansion results
- Validation status

## Configuration Best Practices

1. **Use absolute paths** when possible to avoid ambiguity
2. **Keep paths consistent** between `MANAGED_REPO_PATH` and `MANAGED_REPO_TASK_PATH`
3. **Test configuration** before running automation:
   ```bash
   source scripts/yaml_config.sh && load_config
   echo "Configuration loaded successfully"
   ```
4. **Use environment variables** for temporary overrides
5. **Keep backup** of working configuration

## Troubleshooting Configuration

### Common Issues

1. **Missing configuration file**:
   ```bash
   # Check if config.yaml exists
   ls -la config.yaml
   
   # Create default configuration if missing
   cp config.yaml.example config.yaml
   ```

2. **Invalid YAML syntax**:
   ```bash
   # Validate YAML syntax
   python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

3. **Missing required variables**:
   ```bash
   # Check configuration loading
   source scripts/yaml_config.sh && load_config
   echo "SLEEP_DURATION: $SLEEP_DURATION"
   echo "MANAGED_REPO_PATH: $MANAGED_REPO_PATH"
   ```

4. **Path not found**:
   ```bash
   # Verify paths exist
   ls -la "$MANAGED_REPO_PATH"
   ls -la "$MANAGED_REPO_TASK_PATH"
   ```

### Debug Configuration Loading

```bash
# Enable debug mode and test configuration
export DEBUG_MODE=true
source scripts/yaml_config.sh
load_config config.yaml

# Show all configuration variables
env | grep -E "(SLEEP_DURATION|MANAGED_REPO_PATH|OPencode_CMD|BEADS_CMD)"
```

## Migration from Old Configuration

If upgrading from an old `config.sh` system:

1. **Backup old configuration**:
   ```bash
   cp config.sh config.sh.backup
   ```

2. **Create new `config.yaml`**:
   ```yaml
   sleep_duration: 1000
   managed_repo_path: ~/git/managed
   managed_repo_task_path: ~/git/repo_task_path
   ```

3. **Test new configuration**:
   ```bash
   source scripts/yaml_config.sh && load_config
   ```

4. **Remove old `config.sh`** (optional):
   ```bash
   rm config.sh
   ```

The new system provides better validation, path expansion, and error handling.

## Branch Cleanup Configuration

The enhanced branch cleanup script (`cleanup-branches-enhanced.sh`) provides comprehensive configuration options for safe and flexible branch management.

### Configuration Section

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

### Configuration Options Explained

#### Dry-run and Interactive Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dry_run_mode` | boolean | false | Run in simulation mode without making changes |
| `interactive_mode` | boolean | true | Enable interactive prompts for user decisions |
| `confirm_before_delete` | boolean | true | Require confirmation for each branch deletion |
| `show_dry_run_summary` | boolean | true | Show detailed summary in dry-run mode |
| `batch_confirmation` | boolean | false | Confirm all operations at once vs individual confirmations |
| `confirmation_timeout` | integer | 60 | Timeout for confirmation prompts in seconds |

#### Safety and Operational Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `safety_mode` | boolean | true | Enable all safety checks by default |
| `backup_before_delete` | boolean | true | Create backup patches before deletion |
| `max_branches_per_run` | integer | 50 | Maximum branches to delete in one run |

#### Dry-run Display Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_branch_details` | boolean | true | Show detailed branch information in dry-run |
| `show_safety_info` | boolean | true | Show safety configuration in dry-run |
| `show_skipped_branches` | boolean | true | Show reasons for skipped branches in dry-run |

### Configuration Examples

#### Safe Production Setup

```yaml
branch_cleanup:
  dry_run_mode: true                  # Always preview first
  interactive_mode: true               # Require human oversight
  confirm_before_delete: true          # Confirm each deletion
  safety_mode: true                   # All safety checks enabled
  backup_before_delete: true           # Create backups
  max_branches_per_run: 10            # Conservative limit
  confirmation_timeout: 120            # Longer timeout for careful review
```

#### Automated CI/CD Setup

```yaml
branch_cleanup:
  dry_run_mode: false                 # Execute directly
  interactive_mode: false              # No human interaction
  confirm_before_delete: false         # Auto-confirm deletions
  batch_confirmation: true            # Single confirmation for all
  safety_mode: true                   # Keep safety checks
  backup_before_delete: true           # Maintain backups
  max_branches_per_run: 100           # Higher limit for automation
  confirmation_timeout: 30            # Shorter timeout
```

#### Development/Testing Setup

```yaml
branch_cleanup:
  dry_run_mode: true                  # Always simulate
  interactive_mode: true               # Interactive learning
  confirm_before_delete: true          # Educational confirmations
  show_dry_run_summary: true          # Detailed feedback
  show_branch_details: true            # Maximum information
  show_safety_info: true              # Show safety workings
  show_skipped_branches: true         # Explain skips
  max_branches_per_run: 5             # Small test batches
```

### Safety Configuration Guidelines

1. **Always enable `safety_mode`** in production environments
2. **Use `dry_run_mode: true`** for initial testing and verification
3. **Set appropriate `max_branches_per_run`** to prevent accidental mass deletions
4. **Enable `backup_before_delete`** unless you have other backup strategies
5. **Configure `confirmation_timeout`** based on your operational needs
6. **Use `interactive_mode: true`** for manual operations
7. **Set `batch_confirmation: true`** for trusted automated operations

### Integration with Other Systems

The branch cleanup configuration integrates with:

- **Branch Protection System**: Uses `branch_protection` configuration for protected branches
- **Logging System**: Logs operations according to `log_level` and `timestamp_format` settings
- **Error Handling**: Uses system error handling and recovery mechanisms
- **Backup System**: Integrates with system backup and archival settings

### Environment Variable Overrides

You can override configuration using environment variables:

```bash
# Temporary override for testing
export branch_cleanup_dry_run_mode=true
export branch_cleanup_interactive_mode=false
export branch_cleanup_max_branches_per_run=5

./scripts/cleanup-branches-enhanced.sh
```

### Command Line Priority

Command line arguments take precedence over configuration file settings:

```bash
# This will run in dry-run mode even if config.yaml has dry_run_mode: false
./scripts/cleanup-branches-enhanced.sh --dry-run --max-branches 10
```

### Troubleshooting Branch Cleanup Configuration

1. **Configuration not loading**:
   ```bash
   # Check if branch_cleanup section exists
   grep -A 20 "branch_cleanup:" config.yaml
   
   # Verify YAML syntax
   python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

2. **Settings not taking effect**:
   ```bash
   # Check environment variables
   env | grep branch_cleanup
   
   # Test configuration loading
   source scripts/yaml_config.sh && load_config
   echo "DRY_RUN_MODE: $DRY_RUN_MODE"
   ```

3. **Safety mode issues**:
   ```bash
   # Check safety configuration
   ./scripts/cleanup-branches-enhanced.sh --help
   
   # Test with minimal safety
   ./scripts/cleanup-branches-enhanced.sh --dry-run --no-safety
   ```