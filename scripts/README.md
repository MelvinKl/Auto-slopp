# Scripts Documentation

This directory contains all the core automation scripts for the Repository Automation System.

## Script Overview

| Script | Purpose | Dependencies |
|--------|---------|--------------|
| `utils.sh` | Error handling, logging, and utility functions | None |
| `yaml_config.sh` | YAML configuration loading and validation | `utils.sh` |
| `update_fixer.sh` | Fix failed dependency updates from Renovate | `utils.sh`, `yaml_config.sh` |
| `creator.sh` | Create and maintain task directory structures | `utils.sh`, `yaml_config.sh` |
| `planner.sh` | Process task files and generate bead tasks | `utils.sh`, `yaml_config.sh` |
| `updater.sh` | Update repositories and merge branches | `utils.sh`, `yaml_config.sh` |
| `implementer.sh` | Implement bead tasks using OpenCode CLI | `utils.sh`, `yaml_config.sh` |

## Script Dependencies

```
utils.sh (base utilities)
├── yaml_config.sh (configuration management)
│   ├── update_fixer.sh
│   ├── creator.sh
│   ├── planner.sh
│   ├── updater.sh
│   └── implementer.sh
```

## Execution Order

The `main.sh` script executes all scripts in alphabetical order:

1. `creator.sh` - Ensure directory structures exist
2. `implementer.sh` - Implement existing tasks
3. `planner.sh` - Process new task files
4. `update_fixer.sh` - Fix dependency issues
5. `updater.sh` - Update repositories

## Common Patterns

All scripts follow these patterns:

1. **Load dependencies**:
   ```bash
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   source "$SCRIPT_DIR/utils.sh"
   source "$SCRIPT_DIR/yaml_config.sh"
   ```

2. **Setup error handling**:
   ```bash
   setup_error_handling
   ```

3. **Load configuration**:
   ```bash
   load_config "$SCRIPT_DIR/../config.yaml"
   ```

4. **Logging with colors**:
   ```bash
   log "INFO" "Information message"
   log "SUCCESS" "Success message"
   log "WARNING" "Warning message"
   log "ERROR" "Error message"
   log "DEBUG" "Debug message"
   ```

5. **Safe command execution**:
   ```bash
   safe_execute "command with arguments"
   ```

6. **Safe git operations**:
   ```bash
   safe_git "git command"
   ```

## Adding New Scripts

To add a new automation script:

1. Create the script file in this directory
2. Follow the common patterns above
3. Make it executable: `chmod +x new_script.sh`
4. The script will be automatically discovered by `main.sh`

Example new script:
```bash
#!/bin/bash

# Load utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/yaml_config.sh"

# Set up error handling
setup_error_handling

# Load configuration
load_config "$SCRIPT_DIR/../config.yaml"

# Your automation logic here
log "INFO" "Starting new automation script"
# ... your code ...
log "SUCCESS" "New automation script completed"
```

## Configuration

All scripts use the centralized `config.yaml` file for settings. The `yaml_config.sh` script loads and validates these settings, making them available as environment variables.

Key configuration variables:
- `SLEEP_DURATION`: Time between automation cycles
- `MANAGED_REPO_PATH`: Path to managed repositories
- `MANAGED_REPO_TASK_PATH`: Path for task files
- `OPencode_CMD`: Path to OpenCode CLI
- `BEADS_CMD`: Path to Beads CLI

## Error Handling

All scripts use the robust error handling from `utils.sh`:

- Automatic script termination on errors
- Colored log output with different levels
- Safe command execution with error checking
- Safe git operations with proper error reporting
- Debug mode for troubleshooting

For detailed information about each script, see their individual documentation or inline comments.