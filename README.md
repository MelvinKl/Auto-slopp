# Auto-slopp

A Python-based automation framework for task execution with pluggable worker system. Auto-slopp provides a flexible foundation for creating automation workflows with support for configuration management, logging (including Telegram integration), and extensible worker implementations.

## Features

- **Pluggable Worker System**: Abstract base class for creating custom automation workers
- **Configuration Management**: Pydantic-based settings with environment variable support
- **Flexible Logging**: Built-in logging with optional Telegram integration for remote notifications
- **Task Execution**: Automated discovery and execution of worker implementations
- **Modern Python**: Built with Python 3.14+ using uv package manager
- **Comprehensive Testing**: Full test suite with pytest and mocked dependencies
- **Real-time Monitoring**: Telegram bot integration for instant error notifications and status updates

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

## Quick Start

### Basic Usage

Run Auto-slopp with default settings:
```bash
auto-slopp
```

Run with custom paths:
```bash
auto-slopp --repo-path /path/to/repo --task-path /path/to/tasks --search-path /path/to/workers
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
auto-slopp --repo-path /path/to/repo --task-path /path/to/tasks
```

Enable debug mode:
```bash
auto-slopp --debug
```

### Configuration

Create a `.env` file in the project root:

```bash
# Basic configuration
AUTO_SLOPP_BASE_REPO_PATH=/path/to/your/repo
AUTO_SLOPP_BASE_TASK_PATH=/path/to/your/tasks
AUTO_SLOPP_DEBUG=false

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

    def run(self, repo_path: Path, task_path: Path) -> Any:
        """
        Execute the worker's automation task.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Any result data from the worker execution
        """
        # Your automation logic here
        result = {
            "status": "completed",
            "repo": str(repo_path),
            "task": str(task_path),
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

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
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

### Worker Discovery

Auto-slopp automatically discovers worker implementations in the configured search path. Simply place your worker files in a directory that's included in `AUTO_SLOPP_WORKER_SEARCH_PATH` or the default search directory.

## Example Workers

The project includes several example workers:

### SimpleLogger
Logs basic information about repository and task paths.
```python
from auto_slopp.example_workers import SimpleLogger

# Usage is automatic through discovery
# Result includes: path info, existence checks, file counts
```

### FileMonitor
Scans repository for files matching specific patterns.
```python
from auto_slopp.example_workers import FileMonitor

# Configure with custom patterns
monitor = FileMonitor(file_patterns=["*.py", "*.md", "*.json"])
# Returns: file counts, sizes, breakdown by type
```

### TaskProcessor
Processes task files with size limits and content analysis.
```python
from auto_slopp.example_workers import TaskProcessor

# Configure maximum file size
processor = TaskProcessor(max_file_size=5*1024*1024)  # 5MB
# Returns: processed files, content previews, metadata
```

### HeartbeatWorker
Demonstrates periodic execution with status messages.
```python
from auto_slopp.example_workers import HeartbeatWorker

# Custom heartbeat message
heartbeat = HeartbeatWorker(message="Custom service is running")
# Returns: timestamp, message, path information
```

## API Reference

### Worker Base Class

```python
class Worker(ABC):
    """Abstract base class for all worker implementations."""

    @abstractmethod
    def run(self, repo_path: Path, task_path: Path) -> Any:
        """
        Execute the worker's automation task.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

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
    base_task_path: Path = Field(default_factory=lambda: Path.cwd() / "tasks")
    worker_search_path: Path = Field(default_factory=lambda: Path(__file__).parent.parent)

    # Execution
    executor_sleep_interval: float = Field(default=1.0)
    debug: bool = Field(default=False)

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
  --task-path PATH     Task directory or file (overrides AUTO_SLOPP_BASE_TASK_PATH)
  --search-path PATH   Worker search path (overrides AUTO_SLOPP_WORKER_SEARCH_PATH)
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
├── src/
│   ├── auto_slopp/
│   │   ├── __init__.py
│   │   ├── main.py              # Main entry point
│   │   ├── worker.py            # Base Worker class
│   │   ├── executor.py          # Worker discovery and execution
│   │   ├── example_workers.py    # Example implementations
│   │   └── telegram_handler.py  # Telegram logging integration
│   └── settings/
│       ├── __init__.py
│       └── main.py              # Configuration management
├── tests/
│   ├── conftest.py              # Test fixtures
│   ├── test_worker.py
│   ├── test_settings.py
│   └── test_telegram_handler.py
├── pyproject.toml               # Project configuration
└── README.md
```

## Configuration Examples

### Environment Variables

```bash
# Development environment
export AUTO_SLOPP_DEBUG=true
export AUTO_SLOPP_BASE_REPO_PATH=./dev-repo
export AUTO_SLOPP_BASE_TASK_PATH=./tasks

# Production environment
export AUTO_SLOPP_DEBUG=false
export AUTO_SLOPP_TELEGRAM_ENABLED=true
export AUTO_SLOPP_TELEGRAM_BOT_TOKEN=prod_bot_token
export AUTO_SLOPP_TELEGRAM_CHAT_ID=prod_chat_id
```

### .env File

```bash
# .env
AUTO_SLOPP_BASE_REPO_PATH=/home/user/projects/my-automation
AUTO_SLOPP_BASE_TASK_PATH=/home/user/tasks
AUTO_SLOPP_WORKER_SEARCH_PATH=/home/user/custom-workers
AUTO_SLOPP_EXECUTOR_SLEEP_INTERVAL=2.0
AUTO_SLOPP_DEBUG=false

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

- **Real-time notifications** for errors and warnings
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
- Worker discovery information
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

This project is licensed under the BSD 3-Clause License. See the [LICENSE](LICENSE) file for details.

## Version History

### 0.1.0
- Initial release
- Basic worker system with abstract base class
- Pydantic configuration management
- Telegram logging integration
- Example worker implementations
- Comprehensive test suite
