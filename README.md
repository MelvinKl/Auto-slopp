# Auto-slopp: Advanced Repository Automation System

A sophisticated bash-based automation system for managing multiple Git repositories with intelligent task processing, dependency updates, and comprehensive monitoring capabilities.

## 🎯 Overview

Auto-slopp is an enterprise-grade automation system that provides comprehensive management of multiple repositories through intelligent scripts that:

### 🔄 Core Automation
- **Dynamic Script Discovery**: Automatically discovers and executes all `.sh` files in `scripts/` directory
- **YAML Configuration System**: Flexible, validated configuration with environment variable support
- **Dependency Update Management**: Automated handling of Renovate branch updates with conflict resolution
- **Structured Task Processing**: Intelligent task directory creation and sequential file processing
- **Beads Integration**: Native task management through beads CLI with OpenCode automation
- **Safe Git Operations**: Atomic operations with comprehensive error handling and rollback

### 🚀 Advanced Features
- **Number State Management**: Atomic, concurrent-safe number assignment for unique tracking
- **Auto-Update-Reboot**: Intelligent system reboot management with comprehensive safety mechanisms
- **Telegram Bot Integration**: Real-time monitoring and alerting with rate limiting and security
- **Branch Protection**: Advanced branch safety with configurable protection rules
- **Beads Synchronization**: Cross-repository state synchronization with conflict resolution
- **Comprehensive Logging**: Multi-level colored logging with rotation and archival
- **Health Monitoring**: System health checks with automated recovery mechanisms

### 🏗️ Architecture
The system operates as a distributed automation engine with:
- **Modular Design**: Each component operates independently with clear interfaces
- **State Management**: Persistent state tracking across restarts and failures
- **Concurrent Safety**: Atomic operations with proper locking mechanisms
- **Error Recovery**: Comprehensive error handling with retry logic and fallback strategies

## 🚀 Key Features

### 🔄 Core Automation Engine
- **Dynamic Script Discovery**: Automatically discovers and runs all `.sh` files in `scripts/` directory
- **Sequential Processing**: Scripts executed in alphabetical order with dependency tracking
- **Modular Architecture**: Add new functionality without modifying core components

### 🤖 Intelligent Task Management
- **OpenCode CLI Integration**: Direct integration with OpenAgent for code generation and fixes
- **Beads Task Processing**: Native task management with automated workflow
- **File Numbering System**: Automatic sequential numbering (0001-9999) with conflict resolution
- **Task State Tracking**: Persistent task state across system restarts

### 📊 Advanced Configuration
- **YAML Configuration System**: Flexible, validated configuration with environment variables
- **Multi-environment Support**: Environment-specific settings with inheritance
- **Runtime Validation**: Configuration validation with detailed error reporting
- **Hot Reloading**: Configuration changes without system restart

### 🔧 Comprehensive Tooling
- **Number State Manager**: Atomic, concurrent-safe number assignment and tracking
- **Auto-Update-Reboot**: Intelligent system reboot management with safety mechanisms
- **Branch Protection**: Advanced branch safety with configurable rules and validation
- **Beads Synchronization**: Cross-repository state sync with conflict resolution

### 📡 Monitoring & Alerting
- **Telegram Bot Integration**: Real-time monitoring with rate limiting and security
- **Comprehensive Logging**: Multi-level colored logging with rotation and archival
- **Health Monitoring**: System health checks with automated recovery
- **Performance Metrics**: Detailed reporting and performance tracking

### 🛡️ Enterprise Features
- **Error Recovery**: Robust error handling with retry logic and fallback strategies
- **Concurrent Safety**: Atomic operations with proper locking mechanisms
- **Audit Trail**: Complete audit logging for compliance and debugging
- **Security Hardening**: Token encryption, access validation, and secure storage

## 📋 Prerequisites

### Required Tools
```bash
# Core dependencies
git                # Git version control (v2.25+)
opencode           # OpenCode CLI for code generation
bd                # Beads CLI for task management

# Optional but recommended
jq                 # JSON processing for configuration validation
curl               # HTTP client for API integrations
```

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+)
- **Shell**: Bash 4.4+ with extended globbing
- **Memory**: Minimum 512MB RAM (1GB+ recommended)
- **Disk**: 100MB free space for logs and state management
- **Network**: Internet access for git operations and optional Telegram integration

### Environment Setup
```bash
# Set up environment (optional)
export DEBUG_MODE=true                    # Enable verbose logging
export TELEGRAM_BOT_TOKEN="your_token"    # Telegram bot token
export OPencode_CMD="/usr/local/bin/opencode"  # Custom OpenCode path
export BEADS_CMD="/usr/local/bin/bd"      # Custom beads path
```

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Auto-slopp
```

### 2. Install Dependencies

```bash
# Install required tools (Ubuntu/Debian)
sudo apt update
sudo apt install -y git curl jq

# Install OpenCode CLI (if not already installed)
curl -fsSL https://opencode.ai/install.sh | bash

# Install Beads CLI (if not already installed)
go install github.com/steveyegge/beads@latest
```

### 3. Make Scripts Executable

```bash
chmod +x main.sh config.sh
chmod +x scripts/*.sh
chmod +x scripts/core/*.sh
```

### 4. Configure Repository Structure

```bash
# Create managed directories
mkdir -p ~/git/managed
mkdir -p ~/git/repo_task_path

# Add your repositories as subdirectories
cd ~/git/managed
git clone <repo1-url> repo1
git clone <repo2-url> repo2
# Add more repositories as needed
```

### 5. Configure System

Edit `config.yaml` with your settings:

```yaml
# Basic configuration
sleep_duration: 100                  # Duration between cycles (seconds)
managed_repo_path: '~/git/managed'  # Path containing repository subdirectories
managed_repo_task_path: '~/git/repo_task_path'  # Path for task description files

# Logging configuration
log_level: INFO                     # DEBUG, INFO, WARNING, ERROR, SUCCESS
log_directory: '~/git/Auto-logs'     # Log file location
log_max_size_mb: 10                 # Maximum log file size before rotation
log_retention_days: 30              # Maximum age of log files before cleanup
```

### 6. First Time Setup

```bash
# Test configuration loading
source scripts/yaml_config.sh && load_config

# Initialize number management system
./scripts/number_manager.sh init

# Create task directories
./scripts/creator.sh

# Test individual components
./scripts/updater.sh
./scripts/planner.sh
```

## ⚙️ Configuration

### Core Configuration

```yaml
# Repository automation configuration
sleep_duration: 100                  # Duration between cycles (seconds)
managed_repo_path: '~/git/managed'  # Path containing repository subdirectories
managed_repo_task_path: '~/git/repo_task_path'  # Path for task description files
```

### Auto-Update-Reboot Configuration

The auto-update-reboot functionality monitors repository changes and triggers conditional system reboots with comprehensive safety mechanisms:

```yaml
# Auto-update-reboot configuration
auto_update_reboot_enabled: false        # Enable/disable the functionality
reboot_cooldown_minutes: 60             # Minimum time between reboots
change_detection_interval_minutes: 5   # How often to check for changes
reboot_delay_seconds: 30                # Grace period before reboot
max_reboot_attempts_per_day: 3          # Daily limit on reboot attempts
maintenance_mode: false                  # Manual override to disable reboots
emergency_override: false               # Emergency override for forced reboots
```

**Key Safety Features:**
- **Cooldown Protection**: Prevents reboot loops with configurable minimum intervals
- **Daily Limits**: Caps the number of reboots per day to prevent excessive reboots
- **Health Checks**: Validates system health (disk space, memory) before rebooting
- **Maintenance Mode**: Manual override to disable all reboots during maintenance
- **Change Detection**: Only reboots for critical file changes (scripts, configuration)

### Beads Updater Configuration (CRITICAL P0)

Advanced configuration for automated repository synchronization:

```yaml
# Beads updater configuration (CRITICAL P0 - Automated Repository Synchronization)
beads_updater:
  default_sync_mode: "incremental"      # "incremental" or "full" - sync mode preference
  default_conflict_strategy: "newest"   # "newest", "manual", "keep_local", "keep_remote"
  default_max_retries: 3               # Maximum retry attempts for failed syncs
  backup_retention_days: 30            # Days to keep automatic backups
  enable_detailed_reporting: true       # Generate detailed JSON sync reports
  cleanup_temp_files: true             # Clean up temporary files after sync
  lock_timeout_minutes: 30            # Lock file timeout to prevent deadlocks
```

### Branch Protection Configuration

Advanced branch protection and safety mechanisms:

```yaml
# Enhanced branch protection configuration
branch_protection:
  enable_protection: true              # Enable branch protection mechanisms
  require_confirmation: true           # Require explicit confirmation for protected branches
  show_warnings: true                  # Show warnings before deleting any branch
  protected_branches:                  # List of branches that are always protected
    - "main"
    - "master"
    - "develop"
    - "staging"
    - "production"
  protect_current_branch: true        # Always protect the currently checked-out branch
  protection_patterns:                 # Branch name patterns that are protected
    - "keep-*"
    - "protected-*"
    - "temp-*"
    - "backup-*"
  require_explicit_confirmation_for:   # Branch types requiring explicit confirmation
    - "main"
    - "master"
    - "develop"
    - "staging"
    - "production"
```

### Branch Cleanup Configuration

Enhanced branch cleanup with comprehensive safety mechanisms:

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

**Key Safety Features:**
- **Dry Run Mode**: Preview operations before executing changes
- **Interactive Confirmation**: Confirm each deletion or use batch mode
- **Backup Creation**: Automatic patch backups before deletion
- **Safety Limits**: Maximum branches per run to prevent accidents
- **Comprehensive Protection**: Multiple layers of branch safety checks
- **Detailed Analysis**: Branch state analysis with conflict detection
- **Configurable Timeouts**: Prevent hanging operations
```

### Telegram Bot Configuration (P0 Critical)

Real-time monitoring and alerting through Telegram:

```yaml
# Telegram Bot logging configuration (P0 Critical)
telegram:
  enabled: false                        # Enable/disable Telegram logging globally
  bot_token: "${TELEGRAM_BOT_TOKEN}"    # Environment variable for bot token (NEVER store in plain text)
  default_chat_id: "@logs_channel"      # Default target for sending messages (see below for options)
  api_timeout_seconds: 10               # Timeout for Telegram API requests
  connection_retries: 3                 # Maximum retry attempts for failed connections
  
  # Rate limiting configuration
  rate_limiting:
    messages_per_second: 5              # Conservative rate limit (far below Telegram's 30/sec)
    burst_size: 20                     # Burst capacity for handling logs
    rate_limit_window_seconds: 60      # Time window for rate limiting calculations
    backoff_multiplier: 2              # Multiplier for exponential backoff
    max_backoff_seconds: 30             # Maximum backoff delay
  
  # Message formatting configuration
  formatting:
    parse_mode: "HTML"                  # Message format: "HTML", "Markdown", or "plain"
    max_message_length: 4000            # Safe message length (below Telegram's 4096 limit)
    include_timestamp: true             # Include timestamps in messages
    include_log_level: true             # Include log level indicators
    include_script_name: true           # Include script name for context
    use_emoji_indicators: true          # Use emoji for log levels (🔴🟡🟢🔵)
```

#### Configuring Log Destination (User, Channel, or Group)

The `default_chat_id` setting determines where Telegram logs are sent. You can configure it to send logs to:

**1. Send to a specific user (by numeric ID)**
```yaml
telegram:
  enabled: true
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  default_chat_id: "123456789"         # Replace with your numeric Telegram user ID
```

**2. Send to a public channel**
```yaml
telegram:
  enabled: true
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  default_chat_id: "@my_logs_channel"    # Public channel username (must start with @)
```

**3. Send to a private group**
```yaml
telegram:
  enabled: true
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  default_chat_id: "-1001234567890"    # Private group ID (negative number)
```

#### How to Find Your Telegram User ID

To send logs to your personal account, you need your numeric Telegram user ID:

**Method 1: Using a bot**
1. Start a conversation with `@userinfobot` on Telegram
2. Send `/start`
3. The bot will reply with your numeric user ID

**Method 2: Using another bot**
1. Start a conversation with `@MyTelegramID_bot` or `@JsonDumpBot`
2. Send any message
3. The bot will reply with your user ID

**Method 3: Using curl and bot token**
```bash
# Get bot info (verifies token works)
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"

# Get updates to find chat IDs
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates"
# Look for "chat":{"id":123456789,"type":"private"} in the response
```

#### Testing Telegram Configuration

After configuring, test your setup:

```bash
# Test with current configuration
source scripts/core/telegram_logger.sh
send_log_to_telegram "INFO" "Test message from Auto-slopp"

# Test with a specific user (temporary override)
TELEGRAM_CHAT_ID="123456789" send_log_to_telegram "INFO" "Test message"

# Test via main script
DEBUG_MODE=true ./main.sh  # Watch for Telegram errors in logs
```

#### Important Notes

- **User IDs are numeric** (e.g., `123456789`) - do not use `@username`
- **Channel usernames** start with `@` (e.g., `@my_channel`)
- **Private groups** have negative IDs (e.g., `-1001234567890`)
- The bot must be a member of any channel or group you want to send logs to
- Environment variable `TELEGRAM_CHAT_ID` overrides `default_chat_id` if set
- Store bot token in environment variable, never in plain text config

### Logging Configuration

Comprehensive logging with rotation, archival, and enhanced timestamp support:

```yaml
# Logging configuration
log_directory: '~/git/Auto-logs'         # Log file location
log_max_size_mb: 10                     # Maximum log file size before rotation (MB)
log_max_files: 5                        # Maximum number of rotated log files to keep
log_retention_days: 30                  # Maximum age of log files before cleanup (days)
log_level: INFO                         # Default log level (DEBUG, INFO, WARNING, ERROR, SUCCESS)

# Enhanced timestamp configuration
timestamp_format: readable-precise       # Timestamp format: "default", "iso8601", "rfc3339", "syslog", "compact", "compact-precise", "readable", "readable-precise", "debug", "microseconds"
timestamp_timezone: local                # Timezone for timestamps: "local", "utc", or specific timezone (e.g., "America/New_York")
```

#### Available Timestamp Formats

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
| `microseconds` | `2026-01-31 09:00:01.123456` | Microsecond precision (alias for debug) |

#### Log Levels and Filtering

- **DEBUG**: Detailed information for debugging (only shown when `DEBUG_MODE=true`)
- **INFO**: General informational messages
- **SUCCESS**: Successful operations
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations

#### Environment Variables

Override logging configuration via environment variables:

```bash
export TIMESTAMP_FORMAT="iso8601"       # Override timestamp format
export TIMESTAMP_TIMEZONE="utc"          # Override timezone
export LOG_LEVEL="DEBUG"                 # Override log level filtering
export DEBUG_MODE="true"                 # Enable debug messages
```

The configuration system uses `yaml_config.sh` to automatically load and validate these values for all scripts. Tilde paths (~) are automatically expanded to your home directory.

### 5. Verify OpenCode CLI Integration

The system uses OpenCode CLI with OpenAgent for all opencode operations. Ensure they are available:

```bash
# Test OpenCode CLI with OpenAgent
opencode run "Test message" --agent OpenAgent

# Test configuration loading
source scripts/yaml_config.sh && load_config
echo "Configuration loaded successfully"
```

## 🎯 Quick Start

### Basic Usage

```bash
# Start the full automation system
./main.sh

# Or run individual components
./scripts/update_fixer.sh          # Fix failed dependency updates
./scripts/creator.sh               # Setup directory structures
./scripts/planner.sh               # Process task files with numbering
./scripts/updater.sh               # Update repositories
./scripts/implementer.sh           # Implement bead tasks
./scripts/auto-update-reboot.sh    # Monitor changes and trigger conditional reboots
./scripts/beads_updater.sh         # Synchronize beads across repositories
./scripts/number_manager.sh        # Manage unique number assignments
```

### Advanced Components

```bash
# Branch management and protection
./scripts/branch_protection.sh    # Advanced branch safety rules
./scripts/cleanup-branches.sh     # Clean up old branches (basic version)
./scripts/cleanup-branches-enhanced.sh  # Enhanced branch cleanup with safety features
./scripts/cleanup-automation-engine.sh  # System cleanup operations

# Monitoring and alerting
./scripts/core/telegram_logger.sh  # Telegram bot integration
./scripts/repository-discovery.sh  # Discover and analyze repositories
./scripts/task-status-detection.sh # Monitor task completion status
```

### First Time Setup

1. **Configure repositories** in `config.yaml`
2. **Create managed directories** and add repositories as subdirectories
3. **Initialize advanced features**:
   ```bash
   ./scripts/number_manager.sh init    # Initialize number tracking
   ./scripts/creator.sh                 # Create task directories
   ./scripts/beads_updater.sh init      # Initialize beads sync
   ```
4. **Start main system**:
   ```bash
   ./main.sh
   ```

### Branch Cleanup Usage

The enhanced branch cleanup script provides comprehensive safety features and flexible operation modes:

#### Basic Usage

```bash
# Run with default configuration (interactive mode)
./scripts/cleanup-branches-enhanced.sh

# Dry run to see what would be deleted
./scripts/cleanup-branches-enhanced.sh --dry-run

# Run automatically without confirmations
./scripts/cleanup-branches-enhanced.sh --no-confirmation
```

#### Advanced Options

```bash
# Interactive mode with detailed information
./scripts/cleanup-branches-enhanced.sh --interactive --show-details

# Limit number of branches deleted
./scripts/cleanup-branches-enhanced.sh --max-branches 10

# Batch confirmation vs individual confirmations
./scripts/cleanup-branches-enhanced.sh --batch-confirmation

# Skip backup creation (faster but less safe)
./scripts/cleanup-branches-enhanced.sh --no-backup

# Disable safety checks (DANGEROUS - use with caution)
./scripts/cleanup-branches-enhanced.sh --no-safety
```

#### Command-Line Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help message and exit |
| `-d, --dry-run` | Enable dry-run mode (simulation only) |
| `-y, --no-confirmation` | Skip all confirmation prompts |
| `-i, --interactive` | Enable interactive prompts for each operation |
| `-b, --batch-confirmation` | Enable batch confirmation |
| `-t, --timeout SECONDS` | Set confirmation prompt timeout |
| `-m, --max-branches COUNT` | Maximum branches to delete in one run |
| `--no-backup` | Disable creating backup patches |
| `--no-safety` | Disable safety checks (dangerous) |
| `--show-details` | Show detailed branch information |
| `--hide-summary` | Hide detailed summary in dry-run mode |

#### Safety Features

- **Protected Branches**: Never deletes main, master, develop, staging, production
- **Current Branch Protection**: Cannot delete the currently checked-out branch
- **Backup Creation**: Automatic patch backups before deletion (configurable)
- **Safety Limits**: Maximum branches per run prevents accidental mass deletion
- **Multi-stage Verification**: Comprehensive safety checks before deletion
- **Interactive Prompts**: Confirm each operation or use batch mode
- **Dry Run Mode**: Preview exactly what would be deleted
- **Timeout Protection**: Prevents hanging operations

#### Integration with Main System

The branch cleanup script integrates seamlessly with the Auto-slopp system:

```yaml
# Configuration in config.yaml
branch_cleanup:
  dry_run_mode: false      # Set to true for safety testing
  interactive_mode: true    # Require human confirmation
  safety_mode: true        # Enable all safety checks
  backup_before_delete: true # Create automatic backups
```

The script automatically uses the system's logging, error handling, and configuration management facilities.
```

## 📁 File Structure

```
Auto-slopp/
├── main.sh                           # Main orchestration script (dynamic discovery)
├── config.yaml                       # YAML configuration file
├── config.sh                         # Configuration loader (uses yaml_config.sh)
├── scripts/                          # Core scripts (auto-discovered)
│   ├── utils.sh                     # Error handling and logging utilities
│   ├── yaml_config.sh               # YAML configuration utilities
│   │
│   ├── Core Automation Scripts/
│   ├── auto-update-reboot.sh        # Monitor changes and trigger conditional reboots
│   ├── update_fixer.sh              # Fix failed dependency updates
│   ├── creator.sh                   # Create task directories
│   ├── planner.sh                   # Process task files (with numbering)
│   ├── updater.sh                   # Update repositories
│   ├── implementer.sh               # Implement bead tasks
│   │
│   ├── Advanced Management Scripts/
│   ├── number_manager.sh             # Atomic number assignment and tracking
│   ├── beads_updater.sh             # Cross-repository beads synchronization
│   ├── branch_protection.sh         # Advanced branch safety rules
│   ├── cleanup-branches.sh          # Clean up old branches (basic version)
│   ├── cleanup-branches-enhanced.sh # Enhanced branch cleanup with safety features
│   ├── cleanup-automation-engine.sh # System cleanup operations
│   │
│   ├── Monitoring & Discovery Scripts/
│   ├── repository-discovery.sh      # Discover and analyze repositories
│   ├── task-status-detection.sh     # Monitor task completion status
│   ├── test_merge_error_handling.sh # Test merge conflict handling
│   │
│   └── core/                         # Core system modules
│       ├── telegram_logger.sh        # Telegram bot integration
│       ├── telegram_config.sh        # Telegram configuration management
│       ├── telegram_health.sh        # Telegram health monitoring
│       ├── telegram_queue.sh         # Telegram message queuing
│       ├── telegram_security.sh      # Telegram security features
│       ├── configuration_validator.sh # Configuration validation
│       ├── error_recovery.sh         # Error recovery mechanisms
│       └── system_state.sh           # System state management
│
├── managed_repo_path/                # Directory containing repositories
│   ├── repo1/                       # Repository 1
│   ├── repo2/                       # Repository 2
│   └── repo3/                       # Repository 3
│
├── managed_repo_task_path/           # Directory for task files
│   ├── repo1/                       # Task files for repo1
│   │   ├── .gitkeep
│   │   ├── 0001-task-name.txt
│   │   ├── 0002-another-task.txt
│   │   └── 0001-task-name.txt.used
│   ├── repo2/                       # Task files for repo2
│   └── repo3/                       # Task files for repo3
│
├── logs/                            # System logs (auto-created)
├── docs/                            # Additional documentation
├── tests/                           # Test scripts and suites
└── README.md                        # This documentation
```

## 🔄 Workflow

### 1. Main Orchestration Loop

The `main.sh` script runs continuously:

```bash
while true; do
    update_fixer.sh    # Fix dependency updates
    creator.sh         # Create/maintain directories
    planner.sh         # Process task files
    updater.sh         # Update repositories
    implementer.sh     # Implement tasks
    sleep 1800        # Wait 30 minutes
done
```

### 2. Individual Script Workflows

#### update_fixer.sh
```bash
For each repository:
    ├── Find renovate branches
    ├── git fetch, reset, clean (safe operations)
    ├── Run `make test`
    ├── If test fails → OpenCode CLI with OpenAgent to fix
    ├── Comprehensive error handling and logging
    └── Push fixes
```

#### creator.sh
```bash
For each repository in managed_repo_path:
    ├── Create corresponding directory in managed_repo_task_path
    ├── Initialize git repository if needed
    ├── Add .gitkeep file for tracking
    ├── Generate README.md with task directory info
    └── Commit and push changes with error handling
```

#### planner.sh
```bash
For each repository with directory:
    ├── Auto-number unnumbered task files (0001-, 0002-, etc.)
    ├── Process files in numerical order
    ├── Switch to ai branch (safe git operations)
    ├── OpenCode CLI with OpenAgent to generate bead tasks
    ├── Rename processed files with .used suffix
    └── Commit and push changes with error handling
```

#### updater.sh
```bash
1. Update automation repository
2. For each repository:
    ├── git clean, reset, fetch
    ├── Merge main into renovate branches
    ├── Merge main into ai branch
    └── Push updates
```

#### implementer.sh
```bash
For each repository:
    ├── Switch to ai branch (safe git operations)
    ├── Validate OpenCode CLI availability
    ├── Get next ready bead task
    ├── OpenCode CLI with OpenAgent to implement task
    ├── Comprehensive error handling and logging
    ├── Commit and push changes
    └── Close completed task
```

#### auto-update-reboot.sh
```bash
# Comprehensive safety checks before any operations
├── Check if auto-update-reboot is enabled in config
├── Verify maintenance mode status
├── Validate reboot cooldown period
└── Check daily reboot limits

# System health validation
├── Disk space check (must have < 90% usage)
├── Memory usage check (must have < 90% usage)
└── Critical services status check

# Repository change detection
├── Store current HEAD commit
├── git pull latest changes
├── Compare HEAD before/after pull
├── Analyze changed files for triggers
└── Update state tracking

# Conditional reboot execution
├── Send pre-reboot notifications
├── Capture system state snapshot
├── Wait configured delay period
├── Execute reboot with fallback methods
└── Update reboot state and history
```

#### number_manager.sh
```bash
# Initialize number state management
├── Create state directory structure (.number_state/)
├── Initialize JSON state file with metadata
├── Set up locking mechanisms for concurrent access
└── Validate existing state integrity

# Atomic number assignment
├── Acquire exclusive lock on state file
├── Read current state and calculate next available number
├── Update state with new assignment and timestamp
├── Create backup of previous state
├── Release lock and return assigned number
└── Handle concurrent access conflicts gracefully

# State management and cleanup
├── Backup state files with rotation
├── Cleanup stale locks and temporary files
├── Validate state consistency on startup
└── Generate state reports and statistics
```

#### beads_updater.sh
```bash
# Initialize beads synchronization
├── Validate beads CLI availability and configuration
├── Create temporary working directory
├── Set up backup retention policies
└── Initialize conflict resolution strategy

# Cross-repository synchronization
├── Discover all managed repositories
├── Pull latest beads state from each repository
├── Detect conflicts and apply resolution strategy
├── Merge changes according to sync mode (incremental/full)
├── Generate detailed sync reports (JSON format)
├── Update repositories with synchronized state
└── Cleanup temporary files and locks

# Error handling and recovery
├── Retry failed operations with exponential backoff
├── Rollback changes on sync failure
├── Maintain backup of previous states
└── Log detailed error information for debugging
```

#### branch_protection.sh
```bash
# Initialize branch protection
├── Load protection configuration from config.yaml
├── Validate current git repository state
├── Identify protected branches and patterns
└── Set up protection rules and warnings

# Branch operation validation
├── Check if branch matches protection patterns
├── Verify current branch protection status
├── Request explicit confirmation for protected operations
├── Log all protection decisions and actions
└── Prevent accidental deletion of critical branches

# Advanced protection features
├── Pattern-based protection (wildcard matching)
├── Current branch automatic protection
├── Configurable confirmation requirements
└── Detailed protection logging and audit trail
```

#### telegram_logger.sh
```bash
# Initialize Telegram integration
├── Validate Telegram configuration and credentials
├── Set up rate limiting and message queuing
├── Initialize security features and token validation
└── Test API connectivity and permissions

# Message processing and delivery
├── Filter messages by log level and script name
├── Apply rate limiting with exponential backoff
├── Format messages according to configuration (HTML/Markdown/Plain)
├── Queue messages for batch delivery
├── Handle API errors and retry failed deliveries
└── Maintain message delivery statistics

# Security and monitoring
├── Encrypt sensitive configuration data
├── Audit all token access attempts
├── Monitor rate limiting status and queue size
├── Perform periodic health checks
└── Generate security and delivery reports
```

#### cleanup-branches-enhanced.sh
```bash
# Enhanced branch cleanup initialization
├── Parse command-line arguments and configuration
├── Initialize branch protection system
├── Load enhanced error handling and state management
└── Validate configuration and perform health checks

# Comprehensive branch analysis
├── Collect local and remote branch information
├── Analyze branch states and relationships
├── Detect potential conflicts and safety issues
├── Generate safety assessments and recommendations
└── Create detailed analysis reports

# Safe branch deletion operations
├── Multi-stage safety verification
├── Interactive confirmation prompts
├── Backup creation before deletion
├── Enhanced deletion with monitoring
└── Performance tracking and error recovery

# Dry-run and simulation capabilities
├── Comprehensive dry-run analysis
├── Detailed branch deletion previews
├── Safety information display
└── Batch and individual confirmation options
```

## 📝 Task File Format

Create task files in `managed_repo_task_path/<repo-name>/` with automatic numbering:

```bash
# Example task files (automatically numbered by planner.sh)
managed_repo_task_path/repo1/0001-add-user-authentication.txt
managed_repo_task_path/repo1/0002-improve-error-handling.txt
managed_repo_task_path/repo1/0003-optimize-database-queries.txt

# Unnumbered files are automatically numbered:
managed_repo_task_path/repo1/add-feature.txt  →  0004-add-feature.txt
```

Task file content:
```
Add user authentication to the application with login, logout, and session management.
Include proper error handling and security measures.
```

**File Numbering System:**
- Files are automatically numbered with four-digit prefixes (0001-, 0002-, 0003-, etc.)
- Unnumbered files are automatically assigned the next available number
- Files are processed in numerical order
- Processed files are renamed with `.used` suffix
- Supports up to 10,000 tasks (0000-9999)
- Ensures predictable and sequential task processing

## ⚙️ Configuration

### config.yaml Format

```yaml
# Repository automation configuration
sleep_duration: 1000                # Duration between cycles (seconds)
managed_repo_path: ~/git/managed    # Path containing repository subdirectories
managed_repo_task_path: ~/git/repo_task_path  # Path for task description files
```

### Configuration Loading

The system uses `yaml_config.sh` to load and validate configuration:

```bash
# Configuration loading in scripts
source "$SCRIPT_DIR/yaml_config.sh"
load_config "$SCRIPT_DIR/../config.yaml"

# Variables are automatically exported:
# - SLEEP_DURATION
# - MANAGED_REPO_PATH (tilde expanded)
# - MANAGED_REPO_TASK_PATH (tilde expanded)
# - OPencode_CMD (opencode)
# - BEADS_CMD (bd)
```

### Environment Variables

```bash
# Enable debug mode (optional)
export DEBUG_MODE=true

# Override CLI paths (optional)
export OPencode_CMD="/path/to/opencode"
export BEADS_CMD="/path/to/bd"
```

### Directory Structure

```
managed_repo_path/
├── repo1/           # Repository 1
├── repo2/           # Repository 2
└── repo3/           # Repository 3

managed_repo_task_path/
├── repo1/           # Task files for repo1
│   ├── .gitkeep
│   ├── task1.txt
│   └── task1.txt.used
├── repo2/           # Task files for repo2
│   └── .gitkeep
└── repo3/           # Task files for repo3
    └── .gitkeep
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Permission Denied
```bash
# Fix: Make scripts executable
chmod +x main.sh scripts/*.sh scripts/core/*.sh
```

#### 2. Repository Not Found
```bash
# Check managed_repo_path in config.yaml
# Ensure repositories exist as subdirectories
# Verify paths are accessible
grep -E "(managed_repo_path|managed_repo_task_path)" config.yaml
```

#### 3. OpenCode CLI Not Found
```bash
# Check if opencode is in PATH
which opencode

# Test OpenCode integration
opencode run "Test message" --agent OpenAgent

# Or update path in config.yaml
export OPencode_CMD="/path/to/opencode"
```

#### 4. Beads CLI Not Found
```bash
# Check if bd is in PATH
which bd

# Test beads functionality
bd ready

# Or update path in config.yaml
export BEADS_CMD="/path/to/bd"
```

#### 5. Logging Issues

For comprehensive logging troubleshooting, see the **[Logging Troubleshooting Guide](docs/logging-troubleshooting.md)**.

**Quick Logging Diagnostics:**
```bash
# Test basic logging
source scripts/utils.sh && log "INFO" "Test message"

# Check timestamp format
validate_timestamp_format "$TIMESTAMP_FORMAT"

# Test timestamp generation
generate_timestamp "$TIMESTAMP_FORMAT" "$TIMESTAMP_TIMEZONE"
```

**Common Logging Problems:**
- **No timestamps**: Ensure `utils.sh` is sourced before calling `log()`
- **No colors**: Check terminal support with `echo -e "${RED}Red${NC}"`
- **No log files**: Verify `LOG_DIRECTORY` permissions and accessibility
- **Debug messages missing**: Set `DEBUG_MODE=true` and `LOG_LEVEL=DEBUG`

### Advanced Troubleshooting

#### Number Manager Issues

**Problem**: Number assignment conflicts or state corruption
```bash
# Check number manager state
ls -la .number_state/
cat .number_state/state.json

# Reset number manager state (CAUTION: This will lose current numbering)
rm -rf .number_state/
./scripts/number_manager.sh init

# Check for stale locks
find /tmp -name "*number_manager*" -type f
```

**Problem**: Concurrent access conflicts
```bash
# Check active locks
lsof | grep number_manager

# Force release stale locks
find /tmp -name "*number_manager*lock*" -delete
```

#### Beads Updater Issues

**Problem**: Sync conflicts or failed synchronization
```bash
# Check sync status
./scripts/beads_updater.sh status

# Force full sync
./scripts/beads_updater.sh full

# Check sync logs
grep "beads_updater" ~/git/Auto-logs/*.log

# Reset sync state
rm -rf ~/.beads_updater_backups/
./scripts/beads_updater.sh init
```

#### Telegram Integration Issues

**Problem**: Messages not being sent
```bash
# Check Telegram configuration
./scripts/core/telegram_config.sh validate

# Test Telegram connectivity
./scripts/core/telegram_health.sh test

# Check rate limiting status
./scripts/core/telegram_logger.sh status

# Verify bot token format
echo "$TELEGRAM_BOT_TOKEN" | grep -E '^[0-9]+:[a-zA-Z0-9_-]{35}$'
```

**Problem**: API rate limiting
```bash
# Check current rate limit status
./scripts/core/telegram_logger.sh rate-limit-status

# Clear rate limit cache (emergency only)
rm -f /tmp/telegram_rate_limit_*
```

#### Auto-Update-Reboot Issues

**Problem**: Unexpected reboots
```bash
# Check reboot state
cat ~/.auto_update_reboot_state.json

# Check reboot history
cat ~/.auto_update_reboot_history.json

# Disable auto-reboot temporarily
sed -i 's/auto_update_reboot_enabled: true/auto_update_reboot_enabled: false/' config.yaml

# Put system in maintenance mode
sed -i 's/maintenance_mode: false/maintenance_mode: true/' config.yaml
```

#### Configuration Issues

**Problem**: Invalid YAML configuration
```bash
# Validate configuration syntax
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Check configuration loading
source scripts/yaml_config.sh && load_config && echo "Configuration loaded successfully"

# Check for missing required variables
set | grep -E "(SLEEP_DURATION|MANAGED_REPO_PATH)"
```

### Debug Mode

Enable comprehensive debugging:

```bash
# Enable debug mode for verbose logging
export DEBUG_MODE=true

# Run scripts with detailed output
DEBUG_MODE=true ./main.sh

# Check what commands are being run
bash -x ./main.sh

# Test configuration loading with debug
DEBUG_MODE=true source scripts/yaml_config.sh && load_config
```

### Log Analysis

Analyze system logs for issues:

```bash
# Recent log entries
tail -f ~/git/Auto-logs/$(date +%Y-%m-%d).log

# Search for errors
grep -i error ~/git/Auto-logs/*.log

# Check specific script logs
grep "script_name=number_manager" ~/git/Auto-logs/*.log

# Analyze performance
grep "elapsed_time" ~/git/Auto-logs/*.log | tail -20
```

### Debug Mode

The scripts use comprehensive logging with colored output. To debug:

```bash
# Run scripts individually to see detailed output
./scripts/update_fixer.sh

# Enable debug mode for verbose logging
export DEBUG_MODE=true
./scripts/creator.sh

# Check what commands are being run
bash -x ./main.sh

# Test OpenCode CLI integration
opencode run "Debug test" --agent OpenAgent

# Test configuration loading
source scripts/yaml_config.sh && load_config
echo "SLEEP_DURATION: $SLEEP_DURATION"
echo "MANAGED_REPO_PATH: $MANAGED_REPO_PATH"
```

### Troubleshooting OpenAgent

If OpenAgent operations fail:

1. **Check OpenAgent availability**:
   ```bash
   task subagent_type="OpenAgent" description="Test" prompt="Test" workdir="."
   ```

2. **Verify workdir parameter**: Ensure the working directory is correct

3. **Check prompts**: Verify OpenAgent can understand the instructions

4. **Repository access**: Ensure the script can access target repositories

### Manual Testing

Test individual scripts:

```bash
# Test configuration loading
source scripts/yaml_config.sh && load_config

# Test repository processing
./scripts/creator.sh

# Test task processing with numbering
./scripts/planner.sh

# Test error handling utilities
source scripts/utils.sh
log "INFO" "Test message"
```

## 📚 Advanced Usage

### Custom Sleep Duration

```bash
# Run every hour (modify config.yaml)
sleep_duration: 3600

# Or override via environment variable
SLEEP_DURATION=600 ./main.sh

# Enable debug mode
DEBUG_MODE=true ./main.sh
```

### Adding New Scripts

Simply add new `.sh` files to the `scripts/` directory:

```bash
# Create a new script with proper error handling
cat > scripts/new_script.sh << 'EOF'
#!/bin/bash

# Load utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# Set up error handling
setup_error_handling

log "INFO" "Starting new script"
# Your code here with error handling
log "SUCCESS" "New script completed"
EOF

# Make it executable
chmod +x scripts/new_script.sh

# It will be automatically picked up by main.sh!
```

### Selective Script Execution

```bash
# Only update repositories
./scripts/updater.sh

# Only implement tasks
./scripts/implementer.sh

# Create directories and plan tasks
./scripts/creator.sh && ./scripts/planner.sh
```

### Integration with CI/CD

Add to your CI pipeline:

```yaml
# .github/workflows/automation.yml
name: Repository Automation
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  automation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run automation
        run: |
          chmod +x main.sh scripts/*.sh
          ./main.sh
```

### OpenCode CLI Customization

Customize OpenCode CLI prompts by modifying scripts:

```bash
# Example: Custom implementer prompt
$OPencode_CMD run "Implement with specific coding standards and testing requirements" --agent OpenAgent

# Custom error handling
if command_exists "${OPencode_CMD##* }"; then
    safe_execute "$OPencode_CMD run \"Custom prompt\" --agent OpenAgent"
else
    log "ERROR" "OpenCode CLI not available"
    exit 1
fi
```

## 🏗️ Architecture Documentation

### Core Architecture

Auto-slopp follows a **microservices architecture** with loosely coupled components that communicate through standardized interfaces:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   main.sh       │    │  Configuration  │    │   State Store   │
│  (Orchestrator) │◄──►│    Manager      │◄──►│  (JSON Files)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Script Engine │    │   Logging Core  │    │  Error Recovery │
│ (Dynamic Loader) │    │ (Colored Out)   │    │   Manager       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Advanced Modules Layer                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │Number Mgr   │ │Beads Updater│ │Telegram Bot │ │Auto-Reboot│ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Component Communication

**Synchronous Communication:**
- Direct function calls between core utilities
- Configuration access through `yaml_config.sh`
- Error handling through `utils.sh`

**Asynchronous Communication:**
- State management through JSON files
- Message queuing for Telegram integration
- Lock files for concurrent access control

### Data Flow

```
1. Configuration Load
   ↓
2. Script Discovery & Loading
   ↓
3. State Initialization
   ↓
4. Component Execution Loop
   ↓
5. Error Recovery & Cleanup
   ↓
6. State Persistence & Logging
```

### Security Model

**Token Management:**
- Environment variable storage for sensitive data
- In-memory encryption for runtime protection
- Audit logging for all token access

**Access Control:**
- File permission checks before operations
- Branch protection rules for Git operations
- Rate limiting for external API calls

### Concurrency Model

**Locking Strategy:**
- File-based locks for critical sections
- Timeout-based lock acquisition
- Deadlock detection and recovery

**State Synchronization:**
- Atomic operations for state updates
- Version tracking for change detection
- Backup and rollback mechanisms

### Design Patterns

**Observer Pattern:**
- Logging system observes all script activities
- Telegram integration subscribes to log events

**State Pattern:**
- Number manager maintains assignment state
- Auto-reboot tracks system reboot state

**Strategy Pattern:**
- Configurable conflict resolution strategies
- Multiple sync modes for beads updater

### Technical Specifications

For detailed technical specifications and design decisions, see:

- **[Auto-Update-Reboot Architecture](AUTO_UPDATE_REBOOT_ARCHITECTURE.md)** - Comprehensive design documentation for the auto-update-reboot functionality, including safety mechanisms, state management, and integration patterns
- **[Repository Cleanup Architecture](REPOSITORY_CLEANUP_ARCHITECTURE.md)** - Design documentation for repository cleanup operations

These documents provide in-depth technical details for developers and system administrators who need to understand the internal architecture, security considerations, and extensibility of the system components.

## 🧪 Testing

### Running Tests

```bash
# Test individual components
./test_logging_system.sh              # Test logging functionality
./test_planner_4digit.sh               # Test 4-digit numbering system
./test_telegram_integration.sh        # Test Telegram bot integration

# Test error handling
./scripts/test_merge_error_handling.sh # Test merge conflict resolution

# Run all tests
make test  # If Makefile is configured
```

### Test Coverage

The system includes comprehensive test coverage for:
- **Logging System**: Multi-level logging with rotation and formatting
- **Number Management**: Concurrent-safe number assignment and state management
- **Git Operations**: Merge conflict handling and branch management
- **Telegram Integration**: Bot API communication with rate limiting
- **Configuration Validation**: YAML parsing and validation logic
- **Error Recovery**: System resilience and recovery mechanisms

## 🤝 Contributing

### Development Guidelines

When adding new functionality:

1. **Follow existing patterns** in scripts
2. **Use utils.sh** for shared error handling and logging
3. **Load yaml_config.sh** for configuration
4. **Add proper error handling** with setup_error_handling()
5. **Use log() function** with appropriate levels (INFO, SUCCESS, WARNING, ERROR, DEBUG)
6. **Use safe_execute()** for command execution
7. **Use safe_git()** for git operations
8. **Update this README** with new features
9. **Test thoroughly** before deployment

### Adding New Scripts

Create new scripts with the standard template:

```bash
#!/bin/bash

# Your Script Description
# Brief one-line description of the script's purpose

# Set script name for logging identification
SCRIPT_NAME="your_script_name"

# Load utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# Set up error handling
setup_error_handling

# Your script functions here
main() {
    log "INFO" "Starting your_script_name"
    
    # Your logic here
    
    log "SUCCESS" "your_script_name completed successfully"
}

# Run main function
main "$@"
```

### Configuration Integration

Add new configuration options to `config.yaml`:

```yaml
# Your new configuration section
your_feature:
  enabled: true
  setting_one: "value"
  setting_two: 123
  
# Optional: Add to core configuration for validation
```

Update `yaml_config.sh` if validation is needed:

```bash
# Add validation for your configuration section
validate_your_feature_config() {
    local config="$1"
    
    # Validate required fields
    if [[ -z "${your_feature_enabled:-}" ]]; then
        log "ERROR" "your_feature.enabled is required"
        return 1
    fi
    
    # Add custom validation logic
    return 0
}
```

### Testing Your Changes

1. **Unit Tests**: Create test scripts for individual functions
2. **Integration Tests**: Test with full system workflows
3. **Error Handling**: Test failure scenarios and recovery
4. **Configuration**: Test with various configuration combinations
5. **Performance**: Test with realistic workloads

### Code Review Checklist

Before submitting changes:

- [ ] Script follows standard template and error handling patterns
- [ ] Configuration options are documented and validated
- [ ] Logging is appropriate and uses consistent formatting
- [ ] Error conditions are handled gracefully
- [ ] Documentation is updated (README, config examples)
- [ ] Tests are added for new functionality
- [ ] Security implications are considered
- [ ] Performance impact is assessed

## 📊 Performance & Monitoring

### Performance Metrics

The system automatically tracks performance metrics for all operations:

```bash
# View performance statistics
grep "elapsed_time" ~/git/Auto-logs/*.log | tail -20

# Generate performance report
./scripts/repository-discovery.sh --performance-report

# Check system resource usage
./scripts/core/system_state.sh --resource-usage
```

### Key Performance Indicators

**Script Execution Time:**
- Target: < 60 seconds for individual scripts
- Warning: > 300 seconds for complex operations
- Critical: > 900 seconds for any operation

**Memory Usage:**
- Target: < 100MB for core processes
- Warning: 100-500MB for intensive operations
- Critical: > 500MB memory consumption

**Disk I/O:**
- Target: < 10MB/s for normal operations
- Warning: 10-50MB/s for bulk operations
- Critical: > 50MBs sustained I/O

### Monitoring Commands

```bash
# Real-time system monitoring
watch -n 5 'ps aux | grep -E "(main\.sh|number_manager|beads_updater)"'

# Monitor log file growth
watch -n 10 'du -sh ~/git/Auto-logs/'

# Check lock file status
find /tmp -name "*Auto-slopp*" -ls

# Monitor queue sizes
ls -la /tmp/telegram_queue_*
```

### Health Checks

The system includes comprehensive health monitoring:

```bash
# Run complete health check
./scripts/core/system_state.sh --full-health-check

# Check individual components
./scripts/core/telegram_health.sh --check-all
./scripts/beads_updater.sh --health-check
./scripts/number_manager.sh --validate-state
```

### Performance Optimization

**Configuration Tuning:**
```yaml
# Optimize for performance
sleep_duration: 60                    # Reduce cycle time for faster response
log_level: WARNING                    # Reduce logging overhead
telegram:
  enabled: false                      # Disable for maximum performance
  rate_limiting:
    messages_per_second: 10           # Increase for high-volume systems
```

**Resource Limits:**
```bash
# Set process limits
ulimit -u 1024    # Max user processes
ulimit -f 100    # Max file size (MB)
ulimit -n 4096   # Max open files
```

## 🔒 Security Considerations

### Data Protection

**Sensitive Information:**
- Bot tokens stored in environment variables only
- Configuration encryption in memory
- Audit logging for all sensitive operations
- Token redaction in log files

**Access Control:**
- File permission validation before operations
- Branch protection for critical Git operations
- Rate limiting for external API calls
- Input validation for all user inputs

### Security Best Practices

```bash
# Regular security checks
./scripts/core/telegram_security.sh --audit

# Validate configuration security
./scripts/core/configuration_validator.sh --security-check

# Monitor for unauthorized access
grep -i "access_denied\|permission_denied" ~/git/Auto-logs/*.log
```

### Network Security

**API Communication:**
- HTTPS enforcement for all external calls
- Certificate validation for Telegram API
- Timeout configuration for network operations
- Retry limits to prevent abuse

## 📄 License

[Your License Information]

## 🔗 Related Tools

- **OpenCode CLI**: Code generation and automation with OpenAgent integration
- **OpenAgent**: Specialized agent for OpenCode operations
- **Beads CLI**: Task management (handled internally by OpenCode)
- **YAML Configuration**: Flexible settings management
- **Error Handling Utils**: Robust logging and error recovery
- **File Numbering System**: Sequential task processing

## 📚 Documentation

### Logging Documentation
- **[Logging Best Practices](docs/logging-best-practices.md)** - Comprehensive usage guidelines
- **[Logging Troubleshooting](docs/logging-troubleshooting.md)** - Diagnostic steps and solutions
- **[Logging Examples](docs/logging-examples.md)** - Practical implementation examples
- **[Enhanced Logging Features](docs/enhanced_logging.md)** - Feature documentation
- **[Logging System Documentation](LOGGING_SYSTEM_DOCUMENTATION.md)** - Technical architecture

### Branch Management Documentation
- **[Branch Cleanup Usage Guide](docs/branch-cleanup-usage-guide.md)** - Comprehensive branch cleanup documentation
- **[Configuration Documentation](docs/CONFIGURATION.md)** - Complete configuration reference including branch cleanup settings

## 📞 Support

For issues and questions:

1. **Enable debug mode**: `export DEBUG_MODE=true`
2. **Check configuration**: Verify `config.yaml` settings
3. **Test scripts individually**: Run scripts with error handling
4. **Validate tools**: Check `opencode` and `bd` availability
5. **Consult troubleshooting** section above
6. **Create an issue** with relevant log files and debug output

### Reporting Issues

When creating issues, please include:

- **System Information**: OS version, Bash version, available memory
- **Configuration**: Sanitized `config.yaml` (remove tokens/passwords)
- **Logs**: Relevant log entries from `~/git/Auto-logs/`
- **Steps to Reproduce**: Clear reproduction steps
- **Expected vs Actual Behavior**: Detailed description of the issue

### Community Resources

- **Documentation**: Check this README and architecture documents
- **Troubleshooting**: Use the comprehensive troubleshooting section
- **Examples**: Review configuration examples in the repository
- **Tests**: Examine test scripts for usage patterns

---

*Generated by Repository Automation System*  
*Last updated: $(date)*  
*Version: 2.0*
