# Repository Automation System

A simple bash-based automation system for managing multiple Git repositories with dependency updates, task generation, and implementation.

## 🎯 Overview

This automation system provides straightforward management of multiple repositories through simple scripts that:

- **Dynamically discovers and runs scripts** from scripts directory
- **Automatically handles dependency updates** from Renovate branches
- **Creates directories** for each repository
- **Processes task files** and generates bead tasks
- **Implements ready tasks** using OpenAgent delegation
- **Updates repositories** and merges branches
- **Runs continuously** in an endless loop

## 🔄 Recent Improvements

The system has been recently enhanced with:

### 🤖 OpenAgent Integration
- All opencode operations now use `task` tool with `subagent_type='OpenAgent'`
- Proper delegation pattern for code generation and fixes
- Centralized interface through specialized OpenAgent

### 📁 Dynamic Script Discovery
- main.sh automatically discovers all `.sh` files in `scripts/` directory
- Scripts executed in alphabetical order
- Add new scripts without modifying main.sh

### 📤 Simplified Task Management
- Removed direct beads CLI calls from all scripts
- Beads operations delegated to opencode internally
- Single interface through OpenAgent

### 🎯 Proper Working Directory
- All operations execute in correct repository context
- OpenAgent calls use proper `workdir` parameter
- Maintains directory context throughout execution

## 🚀 Features

- **🔄 Dynamic Script Discovery**: Automatically discovers and runs all .sh files in scripts/ directory
- **🤖 OpenAgent Integration**: Uses proper agent delegation for all opencode operations
- **📋 Task Processing**: Generates bead tasks from text files
- **🔧 Code Generation**: Uses OpenAgent with opencode for implementation
- **📊 Task Management**: Delegates beads operations to opencode
- **📝 Simple Logging**: Basic echo output for easy debugging
- **📁 Proper Context**: Executes operations in correct repository directories
- **🎛️ Easy Configuration**: Simple config file
- **🔌 Modular Design**: Add new scripts without modifying main.sh

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

Edit `repos.txt` to list your repositories:

```bash
# repos.txt
# Add one repository path per line
$HOME/projects/project1
$HOME/projects/project2
/opt/repos/important-app
```

### 4. Configure Settings

Edit `config.sh` to adjust settings:

```bash
# Key settings
SLEEP_DURATION=1800        # Sleep duration in seconds (30 min)
OPencode_CMD="opencode"    # OpenCode CLI command
BEADS_CMD="bd"            # Beads CLI command (now handled by opencode)
```

### 5. Verify OpenAgent Integration

The system uses OpenAgent delegation for all opencode operations. Ensure OpenAgent is available:

```bash
# Test OpenAgent delegation
task subagent_type="OpenAgent" description="Test" prompt="Test message" workdir="."
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

1. **Configure repositories** in `repos.txt`
2. **Adjust settings** in `config.sh`
3. **Run creator.sh** to create directory structures:
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
├── config.sh                  # Simple configuration file
├── repos.txt                  # Repository list
├── logs/                      # Log files
├── scripts/                   # Core scripts (auto-discovered)
│   ├── update_fixer.sh       # Fix failed dependency updates
│   ├── creator.sh            # Create directory structures
│   ├── planner.sh            # Process task files
│   ├── updater.sh            # Update repositories
│   ├── implementer.sh        # Implement bead tasks
│   └── [add new scripts here] # Automatically picked up!
├── <repo-name>/              # Auto-created per repository
│   ├── tasks/               # Task files to process
│   ├── logs/                # Repository-specific logs
│   └── state/               # State tracking files
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
    ├── git fetch, reset, clean
    ├── Run `make test`
    ├── If test fails → OpenCode CLI to fix
    └── Push fixes
```

#### creator.sh
```bash
For each repository in repos.txt:
    ├── Create directory <repo-name>/
    ├── Create subdirectories: tasks/, logs/, state/
    └── Generate README.md with repository info
```

#### planner.sh
```bash
For each repository with directory:
    ├── Find task files (numbered .txt files)
    ├── Switch to ai branch
    ├── OpenCode CLI to generate bead tasks
    ├── Increment file number
    └── Commit and push changes
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
    ├── Switch to ai branch
    ├── Get next ready bead task
    ├── OpenCode CLI to implement task
    ├── Commit and push changes
    └── Close completed task
```

## 📝 Task File Format

Create task files in `<repo-name>/tasks/` with numbered naming:

```bash
# Example task files
project1/tasks/add-user-authentication.1.txt
project1/tasks/improve-error-handling.2.txt
project1/tasks/optimze-database-queries.3.txt
```

Task file content:
```
Add user authentication to the application with login, logout, and session management.
Include proper error handling and security measures.
```

The planner will process files with numbers ≤ MAX_FILE_NUMBER and increment them after processing.

## ⚙️ Configuration

### config.sh Settings

```bash
# Repository Configuration
REPO_DIRECTORY="$HOME/repositories"     # Directory containing repos
AUTOMATION_ROOT="$(pwd)"                # This repository root
SCRIPTS_DIR="$AUTOMATION_ROOT/scripts"   # Scripts directory
LOGS_DIR="$AUTOMATION_ROOT/logs"        # Logs directory

# Processing Limits
MAX_FILE_NUMBER="999"                   # Max file number to process
MAIN_SLEEP_DURATION="1800"              # Sleep between cycles (seconds)

# Git Configuration
GIT_AUTHOR_NAME="Automation Bot"
GIT_AUTHOR_EMAIL="automation@example.com"

# CLI Paths
OPencode_CLI="opencode"                 # OpenCode CLI path
BEADS_CLI="bd"                          # Beads CLI path

# Logging
LOG_LEVEL="INFO"                        # DEBUG/INFO/WARN/ERROR
```

### repos.txt Format

```bash
# Repository list - one path per line
# Use absolute paths or $HOME, $USER variables

# Examples:
$HOME/projects/my-app
$HOME/work/important-service
/opt/git/repo-to-automate

# Comments are ignored
# Blank lines are ignored
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
# Check repos.txt paths
# Ensure repositories exist and are accessible
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

The scripts use simple echo statements for output. To debug:

```bash
# Run scripts individually to see output
./scripts/update_fixer.sh

# Check what commands are being run
bash -x ./main.sh

# Test OpenAgent delegation
task subagent_type="OpenAgent" description="Debug test" prompt="Test message" workdir="."
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
# Test configuration
./scripts/common.sh  # Should load without errors

# Test repository processing
./scripts/creator.sh

# Test task processing
./scripts/planner.sh
```

## 📚 Advanced Usage

### Custom Sleep Duration

```bash
# Run every hour
SLEEP_DURATION="3600" ./main.sh

# Run every 10 minutes
SLEEP_DURATION="600" ./main.sh
```

### Adding New Scripts

Simply add new `.sh` files to the `scripts/` directory:

```bash
# Create a new script
cat > scripts/new_script.sh << 'EOF'
#!/bin/bash
echo "Running new script"
# Your code here
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

### OpenAgent Customization

Customize OpenAgent prompts by modifying the scripts:

```bash
# Example: Custom implementer prompt
task \
  subagent_type="OpenAgent" \
  description="Custom task implementation" \
  prompt="Implement with specific coding standards and testing requirements" \
  workdir="$repo"
```

## 🤝 Contributing

When adding new functionality:

1. **Follow existing patterns** in scripts
2. **Use common.sh** for shared functions
3. **Add proper logging** with appropriate levels
4. **Update this README** with new features
5. **Test thoroughly** before deployment

## 📄 License

[Your License Information]

## 🔗 Related Tools

- **OpenAgent**: Specialized agent for OpenCode operations
- **OpenCode CLI**: Code generation and automation
- **Beads CLI**: Task management (handled internally by OpenCode)
- **Renovate**: Dependency update automation

---

## 📞 Support

For issues and questions:

1. **Check logs** in the `logs/` directory
2. **Review configuration** in `config.sh`
3. **Consult troubleshooting** section above
4. **Create an issue** with relevant log files

---

*Generated by Repository Automation System*  
*Last updated: $(date)*
