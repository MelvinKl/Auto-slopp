# Auto-slopp Repository Structure and Update Mechanisms Research

## Executive Summary

This research document analyzes the current Auto-slopp repository structure, update mechanisms, and system architecture to inform the design of new auto-update-reboot functionality. The system demonstrates a sophisticated automation framework with YAML-based configuration, comprehensive logging, and robust error handling patterns.

## 1. Current Update Mechanisms

### 1.1 Primary Update Script (`scripts/updater.sh`)
- **Purpose**: Updates repositories and merges main into branches
- **Workflow**:
  1. Updates automation repository (`git pull`)
  2. Iterates through managed repositories
  3. For each repository: fetch, clean, update renovate and ai branches
  4. Merges origin/main into target branches
  5. Handles merge failures gracefully with abort

### 1.2 Auto-update-reboot Script (`scripts/auto-update-reboot.sh`)
- **Purpose**: Change detection and conditional system reboot
- **Current Status**: Fully implemented but disabled by default (`auto_update_reboot_enabled: false`)
- **Key Features**:
  - State management with JSON persistence
  - Cooldown periods and daily limits
  - System health checks (disk, memory, services)
  - Change detection with reboot triggers
  - Comprehensive logging and notifications

## 2. Git Workflow and Branching Strategy

### 2.1 Branch Architecture
- **main**: Primary development branch
- **ai**: Working branch for AI agent implementations
- **renovate***: Dependency update branches (pattern-matched)
- **ephemeral branches**: Short-lived task branches

### 2.2 Merge Strategy
- **Pre-work merge**: `origin/main` → `ai` before task implementation
- **Post-work merge**: `origin/main` → `ai` before pushing changes
- **Conflict detection**: Automated detection with opencode escalation
- **Conflict resolution**: Structured JSON reports for AI assistance

### 2.3 Integration Points
- **Implementer script** coordinates git operations with conflict detection
- **Merge functions** in utils.sh provide safe, logged git operations
- **Conflict escalation** creates structured reports for opencode resolution

## 3. Configuration System

### 3.1 YAML Configuration (`config.yaml`)
```yaml
# Core settings
sleep_duration: 100
managed_repo_path: '~/git/managed'
managed_repo_task_path: '~/git/repo_task_path'

# Logging configuration
log_directory: '~/git/Auto-logs'
log_max_size_mb: 10
log_max_files: 5
log_retention_days: 30
log_level: INFO
timestamp_format: default
timestamp_timezone: local

# Auto-update-reboot settings
auto_update_reboot_enabled: false
reboot_cooldown_minutes: 60
change_detection_interval_minutes: 5
reboot_delay_seconds: 30
max_reboot_attempts_per_day: 3
maintenance_mode: false
emergency_override: false
```

### 3.2 Configuration Loading (`scripts/yaml_config.sh`)
- **Parser**: Simple grep/sed-based YAML parsing
- **Environment variable mapping**: All YAML values exported as shell variables
- **Path expansion**: Tilde expansion for home directory paths
- **CLI command configuration**: OPencode_CMD and BEADS_CMD definitions

## 4. Error Handling Patterns

### 4.1 Centralized Error Management
- **Function**: `setup_error_handling()` in `utils.sh`
- **Mechanism**: `set -eE` with ERR trap
- **Handler**: `handle_error()` with line numbers and command context
- **Logging**: Structured error logging with timestamps

### 4.2 Safe Execution Patterns
- **Function**: `safe_execute()` with command logging
- **Git operations**: `safe_git()` with directory validation
- **Validation**: Pre-execution checks (directories, environment variables)

### 4.3 Error Recovery
- **Merge conflicts**: Automatic abort and escalation to opencode
- **Network failures**: Retry logic and graceful degradation
- **State preservation**: JSON state files for recovery scenarios

## 5. Logging Mechanisms

### 5.1 Enhanced Logging System (`scripts/utils.sh`)
- **Function**: `log()` with configurable levels (DEBUG, INFO, SUCCESS, WARNING, ERROR)
- **Timestamps**: Multiple formats (default, iso8601, compact, readable, debug, microseconds)
- **Colors**: ANSI color coding for different log levels
- **File rotation**: Size-based rotation with retention policies

### 5.2 Specialized Logging Functions
- **Change detection**: `log_change_detection()` for repository updates
- **System health**: `log_system_health()` for monitoring checks
- **Reboot events**: `log_reboot_event()` for system restarts
- **State snapshots**: `log_system_state_snapshot()` for debugging

### 5.3 Log Management
- **Rotation**: Size-based with configurable limits
- **Retention**: Age-based cleanup with configurable policies
- **Capture**: `execute_with_capture()` for script output logging
- **Cleanup**: `cleanup_old_logs()` for maintenance

## 6. Integration Points with main.sh Automation Cycle

### 6.1 Script Discovery and Execution
- **Discovery**: Dynamic script detection in `scripts/` directory
- **Execution**: All scripts executed alphabetically each cycle
- **Capture**: `execute_with_capture()` for comprehensive logging
- **Cycle**: Configurable sleep duration between cycles

### 6.2 Script Integration
1. **updater.sh**: Repository updates and merges
2. **planner.sh**: Task planning and management
3. **implementer.sh**: Task implementation with opencode
4. **creator.sh**: Repository creation and setup
5. **cleanup-branches.sh**: Branch maintenance
6. **auto-update-reboot.sh**: Change detection and reboots
7. **update_fixer.sh**: Update error resolution

### 6.3 Data Flow
- **Configuration**: YAML → shell variables → all scripts
- **State**: JSON files for persistent state management
- **Logging**: Centralized logging with rotation and retention
- **Error handling**: Structured error reporting and recovery

## 7. System Architecture Insights

### 7.1 Design Patterns
- **Modular architecture**: Individual scripts with specific responsibilities
- **Configuration-driven**: YAML configuration centralizes all settings
- **Logging-first**: Comprehensive logging for observability and debugging
- **Error resilience**: Graceful error handling with recovery mechanisms

### 7.2 Safety Mechanisms
- **Cooldown periods**: Prevents excessive reboots/operations
- **Health checks**: System validation before critical operations
- **State management**: Persistent state for recovery and debugging
- **Conflict detection**: Automated detection with AI-assisted resolution

### 7.3 Automation Philosophy
- **Conservative approach**: Fail-safe with manual override capabilities
- **Observability**: Comprehensive logging and state tracking
- **Scalability**: Multi-repository support with consistent patterns
- **Maintainability**: Modular design with shared utilities

## 8. Recommendations for Auto-update-reboot Enhancement

### 8.1 Integration Opportunities
- **Leverage existing patterns**: Use established logging and error handling
- **State management**: Build on existing JSON state file approach
- **Configuration**: Extend YAML configuration for new parameters
- **Health checks**: Utilize existing health check framework

### 8.2 Safety Considerations
- **Maintain conservative defaults**: Keep disabled by default
- **Preserve existing safeguards**: Cooldowns, limits, health checks
- **Enhanced logging**: Add specialized logging for new functionality
- **Testing framework**: Leverage existing test infrastructure

### 8.3 Architectural Alignment
- **Follow existing patterns**: Use established script structure and naming
- **Shared utilities**: Extend utils.sh with new functions
- **Configuration consistency**: Maintain YAML configuration approach
- **Error handling consistency**: Use established error handling patterns

## Conclusion

The Auto-slopp repository demonstrates a mature automation framework with robust patterns for configuration, logging, error handling, and git operations. The existing auto-update-reboot functionality is well-designed but conservative, featuring comprehensive safety mechanisms and state management. Any enhancements should leverage the established patterns while maintaining the system's safety-first approach and observability features.