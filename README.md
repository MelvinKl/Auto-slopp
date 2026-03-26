# Auto-slopp

A Python-based automation framework for task execution with pluggable worker system. Auto-slopp provides a flexible foundation for creating automation workflows with support for configuration management, logging (including Telegram integration), and extensible worker implementations.

> **Warning: AI-Generated Code**
>
> This project contains a significant amount of AI-generated code. As a result, some features may be non-functional, incomplete, or behave unexpectedly now or in the future. AI-generated code can introduce "slop" — plausible-looking but incorrect or unreliable implementations. Please review and test thoroughly before relying on any functionality in production environments.

## Features

- **Pluggable Worker System**: Abstract base class for creating custom automation workers
- **Configuration Management**: Pydantic-based settings with environment variable support
- **Flexible Logging**: Built-in logging with optional Telegram integration for remote notifications
- **Task Execution**: Configurable execution of worker implementations
- **Modern Python**: Built with Python 3.14+ using uv package manager
- **Comprehensive Testing**: Full test suite with pytest and mocked dependencies
- **Real-time Monitoring**: Telegram bot integration for instant error notifications and status updates

## Important Setup Recommendation

It is recommended to set the coding machine to allow everything it requires for its job. It is **not** recommended to let it ask for permission as this will break the flow of the auto slopper.

### CLI Configuration

Auto-slopp supports configurable CLI tools for automation. By default, it uses [opencode.ai](https://opencode.ai), but you can configure it to use other CLI tools like Claude Code.

#### opencode.json Example (for opencode.ai)

```json
{
  "permission": "allow",
  "$schema": "https://opencode.ai/config.json"
}
```

#### Environment Variables for CLI Configuration

Auto-slopp supports a tiered CLI configuration system with capability-based task matching. Each CLI tool has a capability rating (0-10), and tasks specify their requirements (min/max/recommended capabilities). The system automatically selects the most appropriate CLI tool for each task.

```bash
# Tiered CLI configurations (JSON array of objects)
# Each tool has a capability rating (0-10) indicating its sophistication level
AUTO_SLOPP_CLI_CONFIGURATIONS='[
  {
    "cli_command": "gemini",
    "cli_args": ["--yolo", "-p"],
    "capability": 8,
    "cooldown_seconds": 300
  },
  {
    "cli_command": "codex",
    "cli_args": ["--dangerously-bypass-approvals-and-sandbox", "exec"],
    "capability": 5,
    "cooldown_seconds": 300
  },
  {
    "cli_command": "opencode",
    "cli_args": ["--agent", "openagent", "--model", "zai-coding-plan/glm-4.7", "run"],
    "capability": 5,
    "cooldown_seconds": 300
  },
  {
    "cli_command": "opencode",
    "cli_args": ["--agent", "openagent", "--model", "zai-coding-plan/glm-4.7-flash", "run"],
    "capability": 2,
    "cooldown_seconds": 300
  }
]'

# Task difficulty ratings (JSON object)
# Each task specifies min/max/recommended capability requirements
AUTO_SLOPP_TASK_DIFFICULTIES='{
  "github_issue": { "min_rating": 0, "max_rating": 10, "recommended_rating": 5 },
  "vikunja_task": { "min_rating": 0, "max_rating": 10, "recommended_rating": 5 },
  "pr_review": { "min_rating": 0, "max_rating": 10, "recommended_rating": 5 },
  "git_checkout": { "min_rating": 0, "max_rating": 10, "recommended_rating": 2 },
  "default": { "min_rating": 0, "max_rating": 10, "recommended_rating": 5 }
}'

# Timeout for slopmachine execution in seconds (default: 7200, 2 hours)
AUTO_SLOPP_SLOP_TIMEOUT=7200
```

##### Understanding the Rating System

The capability rating system (0-10) helps match tasks with appropriate CLI tools:

**Low Rating (0-3):** 
- Suitable for simple, straightforward tasks
- Examples: Basic git operations, simple file modifications, straightforward code reviews
- These tools are faster but may struggle with complex logic or nuanced decisions

**Medium Rating (4-6):**
- Balanced capability for moderate complexity tasks
- Examples: Standard bug fixes, feature implementations, refactoring
- Good balance between speed and sophistication

**High Rating (7-10):**
- Advanced capability for complex, challenging tasks
- Examples: Complex architecture decisions, multi-file refactoring, intricate bug fixes
- More sophisticated but potentially slower

**How it works:**
1. Each task type has `min_rating`, `max_rating`, and `recommended_rating`
2. Each CLI tool has a single `capability` value
3. The system selects tools within the task's min/max range
4. Preference is given to tools closest to the task's recommended rating
5. If a tool encounters errors, it enters cooldown (configurable duration)

## Installation

### Prerequisites

- Python 3.14 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Auto-slopp
```

2. Install dependencies with uv:
```bash
uv sync
```

3. Activate the virtual environment:
```bash
source .venv/bin/activate
```

4. Configure your GitHub token:

> **🚨🚨🚨 CRITICAL SECURITY WARNING 🚨🚨🚨**
>
> **NEVER, EVER PUT YOUR GITHUB TOKEN IN .env FILE!**
>
> **⛔ DO NOT add `GH_TOKEN` or `GITHUB_TOKEN` to the `.env` file** in this project's root directory. The `.env` file is loaded by CLI tools spawned by auto-slopp, which will prevent them from interacting with GitHub directly and protect against unauthorized access.
>
> **⛔ DO NOT set `GH_TOKEN` or `GITHUB_TOKEN` in your shell environment variables** (bashrc, zshrc, etc.). This ensures CLI tools spawned by auto-slopp cannot access the GitHub token.
>
> **✅ INSTEAD:** Create a separate, dedicated `.gh.env` file **OUTSIDE** this project directory and only source it when **manually** using the `gh` CLI yourself.
>
> ---
>
> **Why this separation is critical:**
>
> When auto-slopp spawns CLI tools (like opencode, codex, gemini), it passes the entire `.env` file to them. If your GitHub token is in `.env`, these tools will gain access to your GitHub account and could make unauthorized changes. By keeping `GH_TOKEN` separate, you ensure that only YOU can interact with GitHub via the `gh` CLI, not the automated tools.
>
> ---

Auto-slopp uses the `gh` CLI for GitHub operations (issues, pull requests, etc.). The `gh` CLI requires a `GH_TOKEN` (or `GITHUB_TOKEN`) environment variable to authenticate with GitHub. This token must be provided **separately** from the main `.env` file — it is not an `AUTO_SLOPP_` prefixed variable.

To manually use `gh` CLI commands:

```bash
# Create a separate .gh.env file outside the project
cat > ~/.gh.env <<EOF
GH_TOKEN=ghp_your_github_personal_access_token
EOF

# Source it only when you need to use gh CLI manually
source ~/.gh.env
gh repo list
```

> **Note:** If `GITHUB_TOKEN` is set but `GH_TOKEN` is not, Auto-slopp will automatically map `GITHUB_TOKEN` to `GH_TOKEN` for `gh` CLI compatibility.

## Autostart with Systemd

To run auto-slopp automatically on system startup using systemd, follow these steps:

### Create a Systemd Service File

1. Create a service file at `/etc/systemd/system/auto-slopp.service`:

```ini
[Unit]
Description=Auto-slopp Automation Framework
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/Auto-slopp
Environment="PATH=/path/to/Auto-slopp/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=/path/to/Auto-slopp/.env
ExecStart=/path/to/Auto-slopp/.venv/bin/auto-slopp
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Important**: Replace:
- `your-username` with your actual username
- `/path/to/Auto-slopp` with the actual path to your installation

### Finding Your Paths

To determine the correct values for your system, run these commands:

```bash
# Get your current username
whoami

# Get the full path to your Auto-slopp installation
pwd

# Example: If you're in /home/username/Auto-slopp, your service file should use:
# User=username
# WorkingDirectory=/home/username/Auto-slopp
# Environment="PATH=/home/username/Auto-slopp/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
# EnvironmentFile=/home/username/Auto-slopp/.env
# ExecStart=/home/username/Auto-slopp/.venv/bin/auto-slopp
```
### Install and Enable the Service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable auto-slopp

# Start the service immediately
sudo systemctl start auto-slopp
```

### Service Management

```bash
# Check service status
sudo systemctl status auto-slopp

# View logs
sudo journalctl -u auto-slopp -f

# Stop the service
sudo systemctl stop auto-slopp

# Restart the service
sudo systemctl restart auto-slopp

# Disable autostart
sudo systemctl disable auto-slopp
```

### Configuration Notes

- Ensure your `.env` file contains all necessary configuration
- The service runs with the user specified in the service file, so ensure that user has proper permissions
- The `EnvironmentFile` directive loads environment variables from your `.env` file
- Adjust `RestartSec` as needed for your use case
- **Important**: The PATH environment variable must include both the virtual environment bin directory AND system paths (e.g., `/usr/bin`, `/usr/local/bin`) to ensure git and other system utilities are accessible

### Troubleshooting Autostart Issues

**Error: `[Errno 2] No such file or directory: 'git'`**

This error occurs when git is not in the PATH for the systemd service. The service file must include system paths in the PATH environment variable:

```ini
Environment="PATH=/path/to/Auto-slopp/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
```

**Other common issues:**

- Verify git is installed: `which git` should return a path (e.g., `/usr/bin/git`)
- Ensure the user has permission to access the repository directories
- Check service logs: `sudo journalctl -u auto-slopp -f`

## Docker

Auto-slopp can be run as a Docker container for easy deployment and isolation.

### Building the Docker Image

Build the Docker image from the project root:

```bash
docker build -t auto-slopp:latest .
```

### Running the Container

#### Basic Usage

Run auto-slopp with default configuration:

```bash
docker run -d \
  --name auto-slopp \
  -v /path/to/managed/repos:/repos \
  auto-slopp:latest
```

#### With Environment Variables

Configure auto-slopp using environment variables:

```bash
docker run -d \
  --name auto-slopp \
  -v /path/to/managed/repos:/repos \
  -e AUTO_SLOPP_DEBUG=false \
  -e AUTO_SLOPP_TELEGRAM_ENABLED=true \
  -e AUTO_SLOPP_TELEGRAM_BOT_TOKEN=your_bot_token \
  -e AUTO_SLOPP_TELEGRAM_CHAT_ID=your_chat_id \
  -e AUTO_SLOPP_WORKERS_DISABLED='[]' \
  auto-slopp:latest
```

> **⚠️ DO NOT pass GH_TOKEN as environment variable** - See the "Configure your GitHub token" section above for the critical security warning.

#### With CLI Configuration

Configure tiered CLI tools:

```bash
docker run -d \
  --name auto-slopp \
  -v /path/to/managed/repos:/repos \
  -e AUTO_SLOPP_CLI_CONFIGURATIONS='[
    {
      "cli_command": "gemini",
      "cli_args": ["--yolo", "-p"],
      "capability": 8,
      "cooldown_seconds": 300
    }
  ]' \
  auto-slopp:latest
```

#### Using an Environment File

For complex configurations, use an environment file:

```bash
# Create .env file with your configuration
cat > .env <<EOF
AUTO_SLOPP_DEBUG=false
AUTO_SLOPP_TELEGRAM_ENABLED=true
AUTO_SLOPP_TELEGRAM_BOT_TOKEN=your_bot_token
AUTO_SLOPP_TELEGRAM_CHAT_ID=your_chat_id
AUTO_SLOPP_WORKERS_DISABLED=[]
AUTO_SLOPP_SLOP_TIMEOUT=7200
EOF

# Run with environment file
docker run -d \
  --name auto-slopp \
  -v /path/to/managed/repos:/repos \
  --env-file .env \
  auto-slopp:latest
```

> **🚨 CRITICAL: DO NOT include GH_TOKEN in .env file** - See the "Configure your GitHub token" section above. Adding GH_TOKEN to this file will expose your GitHub token to CLI tools spawned by auto-slopp, creating a security vulnerability.

### Docker Compose

For easier management, use Docker Compose. Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  auto-slopp:
    image: auto-slopp:latest
    container_name: auto-slopp
    restart: unless-stopped
    volumes:
      - /path/to/managed/repos:/repos
    environment:
      - AUTO_SLOPP_DEBUG=false
      - AUTO_SLOPP_TELEGRAM_ENABLED=true
      - AUTO_SLOPP_TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - AUTO_SLOPP_TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
      - AUTO_SLOPP_WORKERS_DISABLED=[]
      - AUTO_SLOPP_SLOP_TIMEOUT=7200
    env_file:
      - .env
```

> **🚨 CRITICAL: DO NOT include GH_TOKEN in docker-compose.yml or .env file** - See the "Configure your GitHub token" section above. Adding GH_TOKEN here will expose your GitHub token to CLI tools spawned by auto-slopp, creating a security vulnerability.

Run with Docker Compose:

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Volume Mounting

The container requires access to your managed repositories:

- **`/repos`**: Directory containing git repositories to be managed by auto-slopp
  - Mount your repository directory: `-v /path/to/managed/repos:/repos`
  - Each subdirectory should be a git repository

### Container Management

```bash
# View container logs
docker logs -f auto-slopp

# Stop container
docker stop auto-slopp

# Start container
docker start auto-slopp

# Remove container
docker rm auto-slopp

# Execute shell inside container
docker exec -it auto-slopp /bin/bash
```

### Important Notes

- **Git Access**: The container includes git for repository operations
- **Network Access**: Ensure the container can access GitHub, Telegram API, and other required services
- **Volume Persistence**: Repository changes are persisted on the host through volume mounting
- **Environment Variables**: All `AUTO_SLOPP_*` environment variables are supported

### Troubleshooting Docker Issues

**Container exits immediately:**
- Check logs: `docker logs auto-slopp`
- Verify environment variables are set correctly
- Ensure volume mount path exists and has correct permissions

**Permission denied errors:**
- Ensure the mounted directory has proper permissions
- On Linux, you may need to adjust ownership: `chown -R 1000:1000 /path/to/repos`

**Network connectivity issues:**
- Verify the container can reach external services
- Check firewall rules if applicable

## Helm Chart

Auto-slopp can be deployed to Kubernetes using the provided Helm chart.

### Installing the Chart

```bash
# Install from local chart
helm install auto-slopp ./charts/auto-slopp

# Install with custom values
helm install auto-slopp ./charts/auto-slopp -f my-values.yaml

# Install with specific namespace
helm install auto-slopp ./charts/auto-slopp -n auto-slopp --create-namespace
```

### Configuration

The Helm chart supports extensive configuration through `values.yaml`. Key configurations include:

#### Basic Configuration

```yaml
# Number of replicas
replicaCount: 1

# Image configuration
image:
  repository: auto-slopp
  pullPolicy: IfNotPresent
  tag: "latest"

# Persistence for /repos volume
persistence:
  enabled: true
  size: 10Gi
  storageClass: ""
  accessMode: ReadWriteOnce
```

#### Environment Variables

```yaml
env:
  AUTO_SLOPP_DEBUG: "false"
  AUTO_SLOPP_TELEGRAM_ENABLED: "false"
  AUTO_SLOPP_TELEGRAM_BOT_TOKEN: ""
  AUTO_SLOPP_TELEGRAM_CHAT_ID: ""
  AUTO_SLOPP_WORKERS_DISABLED: "[]"
  AUTO_SLOPP_SLOP_TIMEOUT: "7200"
```

#### Installing Additional Programs

The Helm chart supports installing additional programs during container startup using an init container. This is useful for adding development tools like Android build tools:

```yaml
# Install additional packages
additionalPrograms:
  - android-sdk
  - android-sdk-build-tools
  - openjdk-11-jdk
```

The init container will run `apt-get install` with the specified packages before the main application starts.

#### Secrets

For sensitive configuration like API tokens, use the secrets configuration:

```yaml
secrets:
  TELEGRAM_BOT_TOKEN: "your-secret-token"
  API_KEY: "your-api-key"
```

Secrets are automatically base64 encoded and mounted as environment variables.

#### Custom Environment Sources

You can also load environment variables from external sources:

```yaml
envFrom:
  - secretRef:
      name: my-existing-secret
  - configMapRef:
      name: my-config-map
```

### Example: Deploy with Android Build Tools

```bash
# Create values file for Android development
cat > android-values.yaml <<EOF
additionalPrograms:
  - android-sdk
  - android-sdk-build-tools
  - openjdk-11-jdk

env:
  AUTO_SLOPP_DEBUG: "false"
  AUTO_SLOPP_BASE_REPO_PATH: "/repos"

persistence:
  enabled: true
  size: 20Gi
EOF

# Install with Android build tools
helm install auto-slopp ./charts/auto-slopp -f android-values.yaml
```

### Upgrading

```bash
# Upgrade with new values
helm upgrade auto-slopp ./charts/auto-slopp -f my-values.yaml

# Upgrade to new version
helm upgrade auto-slopp ./charts/auto-slopp
```

### Uninstalling

```bash
helm uninstall auto-slopp
```

### Chart Reference

For a complete list of configurable parameters, see the [values.yaml](charts/auto-slopp/values.yaml) file.

## Quick Start

### Basic Usage

Run Auto-slopp with default settings:
```bash
auto-slopp
```

### Development

The project includes a comprehensive Makefile for streamlined development and testing:

#### Installation and Setup
```bash
# Install dependencies
make dev-install

# Format code
make format

# Run all tests and checks
make test

# Run tests with coverage
make coverage

# Run security scans
make security
```

#### Available Makefile Targets

| Target | Description |
|---------|-------------|
| `make help` | Show all available targets |
| `make install` | Install production dependencies |
| `make dev-install` | Install development dependencies |
| `make test` | Run all tests and linting checks |
| `make test-unit` | Run unit tests only |
| `make test-performance` | Run performance tests |
| `make test-integration` | Run integration tests |
| `make lint` | Run formatting and linting checks |
| `make format` | Format code with black and isort |
| `make security` | Run security vulnerability scans |
| `make coverage` | Generate test coverage report |
| `make clean` | Clean temporary files and caches |
| `make ci` | Full CI simulation |

#### CI/CD Integration

The same `make test` command is used in GitHub Actions CI/CD pipelines, ensuring consistency between local development and CI environments. All pipeline steps use the Makefile as the single source of truth for build and test operations.

#### Quality Checks

The `make test` target includes comprehensive validation:

1. **Code Formatting**: Black code formatting validation
2. **Import Sorting**: isort import organization checks  
3. **Linting**: flake8 code quality checks
4. **Security**: Safety dependency scan + Bandit security linter
5. **Testing**: Full pytest test suite execution

All checks must pass for the command to succeed, ensuring code quality and reliability before deployment.

### Repository Tree View (max depth: 3)

```text
Auto-slopp/                               # Repository root for the auto-slopp automation framework
├── .github/                              # GitHub repository configuration
│   └── workflows/                        # CI workflow definitions
├── .ralph/                               # Ralph task-planning and execution notes
├── docs/                                 # Project documentation files
├── src/                                  # Python source tree
│   ├── auto_slopp/                       # Main auto-slopp package
│   │   ├── utils/                        # Shared utility helpers
│   │   └── workers/                      # Worker implementations
│   └── settings/                         # Configuration/settings package
└── tests/                                # Automated test suite
```

### Managed Repositories Directory Structure

Auto-slopp operates on managed repositories using a specific directory structure:

```
AUTO_SLOPP_BASE_REPO_PATH/          # Directory containing git repositories
├── repository_a/                    # Each subdirectory is a git repository
├── repository_b/
└── repository_c/
```

- **`AUTO_SLOPP_BASE_REPO_PATH`** (or `--repo-path`): Directory containing multiple git repositories. Auto-slopp iterates over each subdirectory and processes it as a separate repository.

**Example:**
```bash
# Your managed repositories (each is a git repo)
AUTO_SLOPP_BASE_REPO_PATH=/root/git/managed
# /root/git/managed/warhammer_battle_calculator
# /root/git/managed/Auto-slopp
```

### Configuration

Create a `.env` file in the project root:

```bash
# Basic configuration
AUTO_SLOPP_BASE_REPO_PATH=/path/to/your/repo
AUTO_SLOPP_DEBUG=false

# Worker configuration (all workers enabled by default)
# JSON list of disabled workers. Available: GitHubIssueWorker, PRWorker, StaleBranchCleanupWorker, VikunjaWorker
# Leave empty to enable all workers, or specify workers to disable:
AUTO_SLOPP_WORKERS_DISABLED='[]'
# Example: AUTO_SLOPP_WORKERS_DISABLED='["GitHubIssueWorker"]'

# CLI configuration (optional)
export AUTO_SLOPP_CLI_CONFIGURATIONS='[
  {
    "cli_command": "gemini",
    "cli_args": ["--yolo", "-p"],
    "capability": 8,
    "cooldown_seconds": 300
  },
  {
    "cli_command": "codex",
    "cli_args": ["--dangerously-bypass-approvals-and-sandbox", "exec"],
    "capability": 5,
    "cooldown_seconds": 300
  },
  {
    "cli_command": "opencode",
    "cli_args": ["--agent", "openagent", "--model", "zai-coding-plan/glm-4.7", "run"],
    "capability": 5,
    "cooldown_seconds": 300
  },
  {
    "cli_command": "opencode",
    "cli_args": ["--agent", "openagent", "--model", "zai-coding-plan/glm-4.7-flash", "run"],
    "capability": 2,
    "cooldown_seconds": 300
  }
]'

# Task difficulty ratings (optional)
AUTO_SLOPP_TASK_DIFFICULTIES='{
  "github_issue": { "min_rating": 0, "max_rating": 10, "recommended_rating": 5 },
  "vikunja_task": { "min_rating": 0, "max_rating": 10, "recommended_rating": 5 },
  "pr_review": { "min_rating": 0, "max_rating": 10, "recommended_rating": 5 },
  "git_checkout": { "min_rating": 0, "max_rating": 10, "recommended_rating": 2 },
  "default": { "min_rating": 0, "max_rating": 10, "recommended_rating": 5 }
}'

# Timeout for slopmachine execution in seconds (default: 7200, 2 hours)
AUTO_SLOPP_SLOP_TIMEOUT=7200

# Telegram logging (optional)
AUTO_SLOPP_TELEGRAM_ENABLED=true
AUTO_SLOPP_TELEGRAM_BOT_TOKEN=your_bot_token
AUTO_SLOPP_TELEGRAM_CHAT_ID=your_chat_id

# Advanced Telegram settings
AUTO_SLOPP_TELEGRAM_TIMEOUT=60.0
AUTO_SLOPP_TELEGRAM_RETRY_ATTEMPTS=5
AUTO_SLOPP_TELEGRAM_PARSE_MODE=HTML
```

## Creating Worker Implementations

### Basic Worker

All workers inherit from the `Worker` base class and implement the `run` method:

```python
from pathlib import Path
from auto_slopp.worker import Worker
from typing import Any

class MyCustomWorker(Worker):
    """Custom worker for my specific automation task."""

    def run(self, repo_path: Path) -> Any:
        """
        Execute the worker's automation task.

        Args:
            repo_path: Path to the repository directory

        Returns:
            Any result data from the worker execution
        """
        # Your automation logic here
        result = {
            "status": "completed",
            "repo": str(repo_path),
            "processed_items": 42
        }

        return result
```

### Worker with Initialization

```python
import logging
from pathlib import Path
from auto_slopp.worker import Worker
from typing import Any, Dict

class ConfigurableWorker(Worker):
    """Worker that accepts configuration during initialization."""

    def __init__(self, max_items: int = 100, enable_logging: bool = True):
        """
        Initialize the configurable worker.

        Args:
            max_items: Maximum number of items to process
            enable_logging: Whether to enable detailed logging
        """
        self.max_items = max_items
        self.enable_logging = enable_logging
        self.logger = logging.getLogger("auto_slopp.workers.ConfigurableWorker")

    def run(self, repo_path: Path) -> Dict[str, Any]:
        """Process items with configurable limits."""
        if self.enable_logging:
            self.logger.info(f"Processing up to {self.max_items} items")

        # Implementation logic here
        processed_items = min(42, self.max_items)  # Example processing

        return {
            "worker_name": "ConfigurableWorker",
            "processed_items": processed_items,
            "limit_reached": processed_items == self.max_items
        }
```

### Worker Configuration

Workers are explicitly defined and can be disabled using the `AUTO_SLOPP_WORKERS_DISABLED` environment variable. By default, all workers are enabled.

#### Disabling Specific Workers

To disable specific workers, set the `AUTO_SLOPP_WORKERS_DISABLED` variable in your `.env` file:

```bash
# Disable specific workers
AUTO_SLOPP_WORKERS_DISABLED='["GitHubIssueWorker", "PRWorker"]'

# Disable all workers
AUTO_SLOPP_WORKERS_DISABLED='["GitHubIssueWorker", "PRWorker", "StaleBranchCleanupWorker", "VikunjaWorker"]'
```

## Available Workers

The project includes several workers for automation tasks:

### PRWorker
Manages pull request operations.
```python
from auto_slopp.workers import PRWorker

# Disable in AUTO_SLOPP_WORKERS_DISABLED
# Returns: PR status, merge results, branch information
```

### IssueWorker
A unified worker class that processes tasks/issues using the Ralph execution logic. It accepts a TaskSource (base class) that abstracts the task loading mechanism, allowing it to work with different task sources (GitHub issues, Vikunja tasks, etc.).
```python
from auto_slopp.workers import IssueWorker
from auto_slopp.workers import GitHubTaskSource, VikunjaTaskSource

# Create with GitHub task source
github_worker = IssueWorker(task_source=GitHubTaskSource())

# Create with Vikunja task source
vikunja_worker = IssueWorker(task_source=VikunjaTaskSource())
```

### GitHubIssueWorker
Convenience wrapper around IssueWorker configured with GitHubTaskSource. Handles GitHub issue operations.
```python
from auto_slopp.workers import GitHubIssueWorker

# Disable in AUTO_SLOPP_WORKERS_DISABLED
# Returns: issue status, updates, management results
```

### StaleBranchCleanupWorker
Cleans up stale git branches.
```python
from auto_slopp.workers import StaleBranchCleanupWorker

# Disable in AUTO_SLOPP_WORKERS_DISABLED
# Returns: cleaned branches, deletion status
```

### VikunjaWorker
Convenience wrapper around IssueWorker configured with VikunjaTaskSource. Processes Vikunja tasks as instructions. Searches open tasks in a Vikunja project (creating it if needed), filters tasks to only those tagged with "ai" and having no open dependencies, uses task title/description as instructions for the configured CLI tool, creates a new branch, executes the instructions, and updates the task status. Works on tasks indiscriminately regardless of assignment or creator. Additionally creates subtasks in Vikunja and pull requests in GitHub based on processing results.
```python
from auto_slopp.workers import VikunjaWorker

# Disable in AUTO_SLOPP_WORKERS_DISABLED
# Returns: task processing results, branch information, task status updates, subtask creation results, PR creation results
```

### TaskSource Classes
Base class and implementations for loading tasks from different sources:
- `TaskSource`: Abstract base class for task loading
- `GitHubTaskSource`: Loads tasks from GitHub issues
- `VikunjaTaskSource`: Loads tasks from Vikunja project

## API Reference

### Worker Base Class

```python
class Worker(ABC):
    """Abstract base class for all worker implementations."""

    @abstractmethod
    def run(self, repo_path: Path) -> Any:
        """
        Execute the worker's automation task.

        Args:
            repo_path: Path to the repository directory

        Returns:
            Any result data from the worker execution
        """
        pass
```

### Settings

Configuration is managed through the `Settings` class using Pydantic:

```python
class Settings(BaseSettings):
    # Paths
    base_repo_path: Path = Field(default_factory=lambda: Path.cwd())

    # Workers - all enabled by default
    workers_disabled: List[str] = Field(default_factory=list)

    # Execution
    executor_sleep_interval: float = Field(default=1.0)
    debug: bool = Field(default=False)

    # CLI Configuration
    cli_configurations: List[CLIConfiguration] = Field(default_factory=list)
    slop_timeout: int = Field(default=7200, description="Timeout for slopmachine execution in seconds (default: 2 hours)")

    # Telegram integration
    telegram_enabled: bool = Field(default=False)
    telegram_bot_token: Optional[str] = Field(default=None)
    telegram_chat_id: Optional[str] = Field(default=None)
    telegram_timeout: float = Field(default=30.0)
    telegram_retry_attempts: int = Field(default=3)
    telegram_parse_mode: str = Field(default="HTML")
```

### Command Line Interface

```bash
auto-slopp [OPTIONS]

Options:
  --repo-path PATH      Repository directory (overrides AUTO_SLOPP_BASE_REPO_PATH)
  --debug              Enable debug mode (overrides AUTO_SLOPP_DEBUG)
  --version            Show version and exit
  --help               Show help message
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_worker.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/
```

### Project Structure

```
Auto-slopp/
├── .github/                      # GitHub configuration and automation files
│   └── workflows/                # CI workflow definitions
├── docs/                         # Documentation files (guides, API references)
├── src/                          # Source code
│   ├── auto_slopp/               # Main package with core modules and workers
│   │   ├── utils/                # Utility modules (git, github operations)
│   │   └── workers/              # Worker implementations (IssueWorker, PR, StaleBranchCleanup)
│   │       # TaskSource implementations: GitHubTaskSource, VikunjaTaskSource
│   └── settings/                 # Configuration management with Pydantic settings
└── tests/                        # Test suite with pytest tests
```

## Configuration Examples

### Environment Variables

```bash
# Development environment
export AUTO_SLOPP_DEBUG=true
export AUTO_SLOPP_BASE_REPO_PATH=./dev-repo

# Worker configuration - disable specific workers (JSON list format)
export AUTO_SLOPP_WORKERS_DISABLED='[]'

# Production environment
export AUTO_SLOPP_DEBUG=false
export AUTO_SLOPP_TELEGRAM_ENABLED=true
export AUTO_SLOPP_TELEGRAM_BOT_TOKEN=prod_bot_token
export AUTO_SLOPP_TELEGRAM_CHAT_ID=prod_chat_id

# CLI configuration (optional)
export AUTO_SLOPP_CLI_CONFIGURATIONS='[
  {
    "cli_command": "gemini",
    "cli_args": ["--yolo", "-p"],
    "rating": { "min_rating": 0, "max_rating": 10, "recommend_rating": 8 },
    "cooldown_seconds": 300
  },
  {
    "cli_command": "codex",
    "cli_args": ["--dangerously-bypass-approvals-and-sandbox", "exec"],
    "rating": { "min_rating": 0, "max_rating": 10, "recommend_rating": 5 },
    "cooldown_seconds": 300
  },
  {
    "cli_command": "opencode",
    "cli_args": ["--agent", "openagent", "--model", "zai-coding-plan/glm-4.7", "run"],
    "rating": { "min_rating": 0, "max_rating": 10, "recommend_rating": 5 },
    "cooldown_seconds": 300
  },
  {
    "cli_command": "opencode",
    "cli_args": ["--agent", "openagent", "--model", "zai-coding-plan/glm-4.7-flash", "run"],
    "rating": { "min_rating": 0, "max_rating": 10, "recommend_rating": 2 },
    "cooldown_seconds": 300
  }
]'

# Timeout for slopmachine execution in seconds (default: 7200, 2 hours)
export AUTO_SLOPP_SLOP_TIMEOUT=7200
```

### .env File

```bash
# .env
AUTO_SLOPP_BASE_REPO_PATH=/home/user/projects/my-automation
AUTO_SLOPP_WORKERS_DISABLED='[]'
AUTO_SLOPP_EXECUTOR_SLEEP_INTERVAL=2.0
AUTO_SLOPP_DEBUG=false

# CLI configuration (optional)
export AUTO_SLOPP_CLI_CONFIGURATIONS='[
  {
    "cli_command": "gemini",
    "cli_args": ["--yolo", "-p"],
    "rating": { "min_rating": 0, "max_rating": 10, "recommend_rating": 8 },
    "cooldown_seconds": 300
  },
  {
    "cli_command": "codex",
    "cli_args": ["--dangerously-bypass-approvals-and-sandbox", "exec"],
    "rating": { "min_rating": 0, "max_rating": 10, "recommend_rating": 5 },
    "cooldown_seconds": 300
  },
  {
    "cli_command": "opencode",
    "cli_args": ["--agent", "openagent", "--model", "zai-coding-plan/glm-4.7", "run"],
    "rating": { "min_rating": 0, "max_rating": 10, "recommend_rating": 5 },
    "cooldown_seconds": 300
  },
  {
    "cli_command": "opencode",
    "cli_args": ["--agent", "openagent", "--model", "zai-coding-plan/glm-4.7-flash", "run"],
    "rating": { "min_rating": 0, "max_rating": 10, "recommend_rating": 2 },
    "cooldown_seconds": 300
  }
]'

# Timeout for slopmachine execution in seconds (default: 7200, 2 hours)
export AUTO_SLOPP_SLOP_TIMEOUT=7200

# Telegram settings
AUTO_SLOPP_TELEGRAM_ENABLED=true
AUTO_SLOPP_TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
AUTO_SLOPP_TELEGRAM_CHAT_ID=123456789
AUTO_SLOPP_TELEGRAM_TIMEOUT=60.0
AUTO_SLOPP_TELEGRAM_RETRY_ATTEMPTS=5
AUTO_SLOPP_TELEGRAM_RETRY_DELAY=2.0
AUTO_SLOPP_TELEGRAM_PARSE_MODE=HTML
```

## Documentation

For comprehensive documentation, see the [docs/](docs/) directory:

### User Documentation
- **[Telegram Logging Guide](docs/telegram-logging.md)** - Complete setup and configuration guide

### Developer Documentation
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Development Guide](docs/development-guide.md)** - Development setup and workflow
- **[Architecture Overview](docs/architecture.md)** - System architecture and design
- **[Contributing Guide](docs/contributing.md)** - Contribution guidelines

## Telegram Logging

For comprehensive Telegram logging setup and configuration, see the [Telegram Logging Guide](docs/telegram-logging.md).

### Quick Setup

1. **Create Telegram Bot**
   ```bash
   # Talk to @BotFather on Telegram
   /newbot
   # Follow prompts to get your bot token
   ```

2. **Get Chat ID**
   ```bash
   # Send a message to your bot, then visit:
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   # Look for "chat.id" in the response
   ```

3. **Configure Environment**
   ```bash
   AUTO_SLOPP_TELEGRAM_ENABLED=true
   AUTO_SLOPP_TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   AUTO_SLOPP_TELEGRAM_CHAT_ID=123456789
   ```

4. **Test Configuration**
   ```bash
   auto-slopp --debug
   # Check for Telegram connection logs
   ```

### Features

- **Real-time notifications** for errors and warnings (WARNING level and above by default)
- **Configurable log levels** and message formatting
- **Retry logic** for network failures and rate limiting
- **HTML/Markdown formatting** support
- **Group and channel notifications** support
- **Secure token management** through environment variables

### Security

- **Never share bot tokens** - treat them as passwords
- **Use environment variables** for sensitive configuration
- **Enable bot privacy settings** in BotFather
- **Regular token rotation** recommended for production

## Troubleshooting

### Common Issues

**Workers not discovered:**
- Ensure worker files are in the search path
- Check that workers inherit from `Worker` class
- Verify the `run` method is properly implemented

**Configuration not loading:**
- Check environment variable names have `AUTO_SLOPP_` prefix
- Verify `.env` file is in the project root
- Ensure boolean values use `true`/`false` (case-insensitive)

**Telegram integration not working:**
- 📖 **See complete guide:** [Telegram Logging Guide](docs/telegram-logging.md#troubleshooting)
- Verify bot token and chat ID are correct
- Check network connectivity to Telegram API
- Enable debug mode to see API error details
- Test with curl: `curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe`

**Path issues:**
- Use absolute paths for reliable configuration
- Ensure paths exist and have proper permissions
- Check that repo path contains the expected structure

### Debug Mode

Enable debug mode for detailed logging:

```bash
auto-slopp --debug
```

Or via environment:
```bash
AUTO_SLOPP_DEBUG=true auto-slopp
```

This provides:
- Detailed execution logs
- Worker execution details
- Configuration loading details
- Telegram API error messages

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Check code quality: `black src/ tests/ && isort src/ tests/ && flake8 src/ tests/`
6. Commit your changes: `git commit -m "Add feature description"`
7. Push to your branch: `git push origin feature-name`
8. Open a pull request

## License

[License information to be added]

## Version History

### 0.1.0
- Initial release
- Basic worker system with abstract base class
- Pydantic configuration management
- Telegram logging integration
- Example worker implementations
- Comprehensive test suite
