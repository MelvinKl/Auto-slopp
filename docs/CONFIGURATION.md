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

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SLEEP_DURATION` | Time between automation cycles (seconds) | 1000 | Yes |
| `MANAGED_REPO_PATH` | Path containing repository subdirectories | ~/git/managed | Yes |
| `MANAGED_REPO_TASK_PATH` | Path for task description files | ~/git/repo_task_path | Yes |
| `OPencode_CMD` | Path to OpenCode CLI executable | opencode | No |
| `BEADS_CMD` | Path to Beads CLI executable | bd | No |

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