# Repository Automation System

A robust bash-based automation system for managing multiple Git repositories with dependency updates, task generation, and implementation.

## 🎯 Overview

This automation system provides comprehensive management of multiple repositories through sophisticated scripts that:

- **Dynamically discovers and runs scripts** from scripts directory
- **Uses YAML configuration** for flexible settings management
- **Automatically handles dependency updates** from Renovate branches
- **Creates structured task directories** for each repository
- **Processes numbered task files** with sequential ordering
- **Generates and implements bead tasks** using OpenCode CLI
- **Updates repositories** and merges branches safely
- **Provides comprehensive error handling** and colored logging
- **Runs continuously** in an endless loop

## 🔄 Recent Improvements

The system has been recently enhanced with:

### 🤖 OpenCode CLI Integration
- All opencode operations now use `opencode` CLI with `--agent OpenAgent`
- Direct integration with OpenCode for code generation and fixes
- Consistent interface through OpenCode CLI

### 📋 YAML Configuration System
- Replaced old config.sh with flexible `config.yaml`
- Centralized settings management with yaml_config.sh
- Environment variable validation and expansion

### 🔧 Comprehensive Error Handling
- Added utils.sh with robust error handling and logging
- Colored output with different log levels (INFO, SUCCESS, WARNING, ERROR, DEBUG)
- Safe command execution with detailed error reporting
- Git operation safety wrappers

### 📁 File Numbering System
- Automatic numbering of task files (0001-, 0002-, 0003-, etc.)
- Sequential processing order guaranteed
- Automatic assignment of numbers to unnumbered files
- Support for up to 10,000 tasks (0000-9999)

### 📁 Dynamic Script Discovery
- main.sh automatically discovers all `.sh` files in `scripts/` directory
- Scripts executed in alphabetical order
- Add new scripts without modifying main.sh

## 🚀 Features

- **🔄 Dynamic Script Discovery**: Automatically discovers and runs all .sh files in scripts/ directory
- **🤖 OpenCode CLI Integration**: Direct integration with opencode CLI and OpenAgent
- **📋 Task Processing**: Generates bead tasks from numbered text files
- **🔧 Code Generation**: Uses OpenCode CLI for implementation and fixes
- **📊 Task Management**: Delegates beads operations to opencode internally
- **📝 Comprehensive Logging**: Colored logging with multiple levels and error handling
- **📁 File Numbering**: Automatic sequential numbering and ordering of task files
- **📁 Proper Context**: Executes operations in correct repository directories
- **🎛️ YAML Configuration**: Flexible configuration system with validation
- **🔌 Modular Design**: Add new scripts without modifying main.sh
- **⚡ Error Recovery**: Robust error handling with safe command execution

## 📋 Prerequisites

Before using this system, ensure you have:
- [Opencode](https://opencode.ai/docs/#install)
- [Beads](https://github.com/steveyegge/beads)
- [OpenAgentsControl](https://github.com/darrenhinde/OpenAgentsControl) (I reccommend the full installation)
 
```bash
# Required tools
git                # Git version control
opencode           # OpenCode CLI for code generation
bd                # Beads CLI for task management
```

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Auto-slopp
```

### 2. Make Scripts Executable

```bash
chmod +x main.sh config.sh
chmod +x scripts/*.sh
```

### 3. Configure Repositories

Edit `config.yaml` to configure your repository automation:

```yaml
# config.yaml
sleep_duration: 1000
managed_repo_path: ~/git/managed
managed_repo_task_path: ~/git/repo_task_path
```

Create managed directories and add your repositories as subdirectories under `managed_repo_path`.

### 4. Configure Settings

Edit `config.yaml` to adjust settings:

```yaml
# Key settings
sleep_duration: 1000                # Sleep duration in seconds between cycles
managed_repo_path: ~/git/managed    # Path containing repository subdirectories
managed_repo_task_path: ~/git/repo_task_path  # Path for task description files
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
./scripts/update_fixer.sh    # Fix failed dependency updates
./scripts/creator.sh         # Setup directory structures
./scripts/planner.sh         # Process task files
./scripts/updater.sh         # Update repositories
./scripts/implementer.sh     # Implement bead tasks
```

### First Time Setup

1. **Configure repositories** in `config.yaml`
2. **Create managed directories** and add repositories as subdirectories
3. **Run creator.sh** to create task directories:
   ```bash
   ./scripts/creator.sh
   ```
4. **Start main system**:
   ```bash
   ./main.sh
   ```

## 📁 File Structure

```
Auto-slopp/
├── main.sh                    # Main orchestration script (dynamic discovery)
├── config.yaml                # YAML configuration file
├── config.sh                  # Configuration loader (uses yaml_config.sh)
├── scripts/                   # Core scripts (auto-discovered)
│   ├── utils.sh              # Error handling and logging utilities
│   ├── yaml_config.sh        # YAML configuration utilities
│   ├── update_fixer.sh       # Fix failed dependency updates
│   ├── creator.sh            # Create task directories
│   ├── planner.sh            # Process task files (with numbering)
│   ├── updater.sh            # Update repositories
│   ├── implementer.sh        # Implement bead tasks
│   └── [add new scripts here] # Automatically picked up!
├── managed_repo_path/         # Directory containing repositories
│   ├── repo1/               # Repository 1
│   ├── repo2/               # Repository 2
│   └── repo3/               # Repository 3
├── managed_repo_task_path/    # Directory for task files
│   ├── repo1/               # Task files for repo1
│   │   ├── .gitkeep
│   │   ├── 0001-task-name.txt
│   │   ├── 0002-another-task.txt
│   │   └── 0001-task-name.txt.used
│   ├── repo2/               # Task files for repo2
│   └── repo3/               # Task files for repo3
└── README.md                # This documentation
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
chmod +x main.sh scripts/*.sh
```

#### 2. Repository Not Found
```bash
# Check managed_repo_path in config.yaml
# Ensure repositories exist as subdirectories
# Verify paths are accessible
```

#### 3. OpenCode CLI Not Found
```bash
# Check if opencode is in PATH
which opencode

# Or update path in config.sh
OPencode_CLI="/path/to/opencode"
```

#### 4. Beads CLI Not Found
```bash
# Check if bd is in PATH
which bd

# Or update path in config.sh
BEADS_CLI="/path/to/bd"
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
if command_exists "$OPencode_CMD"; then
    safe_execute "$OPencode_CMD run \"Custom prompt\" --agent OpenAgent"
else
    log "ERROR" "OpenCode CLI not available"
    exit 1
fi
```

## 🤝 Contributing

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

## 📄 License

[Your License Information]

## 🔗 Related Tools

- **OpenCode CLI**: Code generation and automation with OpenAgent integration
- **OpenAgent**: Specialized agent for OpenCode operations
- **Beads CLI**: Task management (handled internally by OpenCode)
- **YAML Configuration**: Flexible settings management
- **Error Handling Utils**: Robust logging and error recovery
- **File Numbering System**: Sequential task processing

---

## 📞 Support

For issues and questions:

1. **Enable debug mode**: `export DEBUG_MODE=true`
2. **Check configuration**: Verify `config.yaml` settings
3. **Test scripts individually**: Run scripts with error handling
4. **Validate tools**: Check `opencode` and `bd` availability
5. **Consult troubleshooting** section above
6. **Create an issue** with relevant log files and debug output

---

*Generated by Repository Automation System*  
*Last updated: $(date)*
