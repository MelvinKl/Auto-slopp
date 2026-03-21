# Development Guide

This guide provides comprehensive information for developers working on Auto-slopp, including setup, architecture, testing, and contribution guidelines.

> **Note:** This project contains a significant amount of AI-generated code. Some features may be non-functional or behave unexpectedly due to LLM-generated "slop." Please review and test thoroughly.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Architecture](#project-architecture)
3. [Development Workflow](#development-workflow)
4. [Testing](#testing)
5. [Code Quality](#code-quality)
6. [Debugging](#debugging)
7. [Performance Considerations](#performance-considerations)
8. [Common Patterns](#common-patterns)

## Getting Started

### Prerequisites

- Python 3.14 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Git
- Code editor (VS Code recommended)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Auto-slopp
   ```

2. **Create development environment**
   ```bash
   uv sync --dev
   source .venv/bin/activate
   ```

3. **Verify installation**
   ```bash
   auto-slopp --version
   pytest --version
   ```

4. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

### IDE Configuration

#### VS Code

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Auto-slopp",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/auto_slopp/main.py",
            "args": ["--debug"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Run Tests",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/.venv/bin/pytest",
            "args": ["${workspaceFolder}/tests", "-v"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

## Project Architecture

### Directory Structure

```
Auto-slopp/
├── src/
│   ├── auto_slopp/
│   │   ├── __init__.py              # Package initialization
│   │   ├── main.py                  # CLI entry point
│   │   ├── worker.py                # Abstract base worker class
│   │   ├── executor.py              # Worker discovery and execution
│   │   ├── discovery.py             # Worker discovery utilities
│   │   ├── telegram_handler.py      # Telegram logging integration
│   │   ├── workers/                 # Worker implementations
│   │   │   ├── pr_worker.py
│   │   │   ├── github_issue_worker.py
│   │   │   ├── stale_branch_cleanup_worker.py
│   │   │   └── update_pr_branches_worker.py
│   │   └── utils/                   # Utility modules
│   │       ├── git_operations.py
│   │       ├── github_operations.py
│   │       ├── branch_analysis.py
│   │       ├── file_operations.py
│   │       ├── repository_utils.py
│   │       └── cli_executor.py
│   └── settings/
│       ├── __init__.py
│       └── main.py                  # Configuration management
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Test fixtures and configuration
│   ├── test_main.py
│   ├── test_worker.py
│   ├── test_discovery.py
│   ├── test_settings.py
│   ├── test_telegram_handler.py
│   └── test_*_worker.py            # Worker tests
├── docs/
│   ├── README.md                    # Documentation index
│   ├── api-reference.md             # API documentation
│   ├── development-guide.md         # This file
│   ├── telegram-logging.md          # Telegram integration guide
│   └── architecture.md              # Architecture overview
├── .github/
│   └── workflows/                    # CI/CD workflows
├── pyproject.toml                   # Project configuration
├── README.md                        # Main project documentation
└── .env.example                     # Environment variables template
```

### Core Components

#### Worker System

The worker system is built around an abstract base class:

```python
# worker.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class Worker(ABC):
    """Abstract base class for all worker implementations."""
    
    @abstractmethod
    def run(self, repo_path: Path) -> Any:
        """Execute the worker's automation task."""
        pass
```

#### Discovery System

Workers are discovered dynamically using Python's importlib:

```python
# discovery.py
def discover_workers(search_path: Path) -> List[Type[Worker]]:
    """Discover worker implementations in the search path."""
    workers = []
    
    for file_path in search_path.rglob("*.py"):
        if file_path.name.startswith("test_"):
            continue
            
        # Import module and find Worker subclasses
        module = import_module_from_path(file_path)
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, Worker) and 
                obj is not Worker):
                workers.append(obj)
    
    return workers
```

#### Configuration System

Settings are managed using Pydantic with environment variable support:

```python
# settings/main.py
from pydantic import BaseSettings, Field
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    base_repo_path: Path = Field(default_factory=lambda: Path.cwd())
    debug: bool = Field(default=False)
    
    class Config:
        env_prefix = "AUTO_SLOPP_"
        env_file = ".env"
```

## Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-worker-type

# Make changes
# ... edit files ...

# Run tests
pytest

# Check code quality
black src/ tests/
isort src/ tests/
flake8 src/ tests/

# Commit changes
git add .
git commit -m "feat: add new worker type with XYZ functionality"

# Push and create PR
git push origin feature/new-worker-type
```

### 2. Bug Fixes

```bash
# Create bug fix branch
git checkout -b fix/worker-discovery-issue

# Add tests for the bug first (TDD)
# ... write failing tests ...

# Fix the issue
# ... edit code ...

# Verify tests pass
pytest

# Commit with fix prefix
git commit -m "fix: resolve worker discovery issue with nested directories"
```

### 3. Documentation Updates

```bash
# Update documentation
# ... edit docs ...

# Test documentation examples
# ... run examples ...

# Commit with docs prefix
git commit -m "docs: update API reference with new methods"
```

### Commit Message Convention

Use conventional commits:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

## Testing

### Test Structure

Tests are organized by component:

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_worker.py
│   ├── test_settings.py
│   └── test_discovery.py
├── integration/             # Integration tests
│   ├── test_executor.py
│   └── test_telegram_handler.py
└── e2e/                     # End-to-end tests
    └── test_main.py
```

### Test Fixtures

```python
# conftest.py
import pytest
from pathlib import Path
from unittest.mock import Mock

@pytest.fixture
def temp_repo_path(tmp_path):
    """Create a temporary repository path."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    return repo_path

@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = Mock()
    settings.base_repo_path = Path("/test/repo")
    settings.debug = True
    return settings

@pytest.fixture
def sample_worker():
    """Create a sample worker for testing."""
    class SampleWorker(Worker):
        def run(self, repo_path):
            return {"status": "test", "repo": str(repo_path)}
    return SampleWorker()
```

### Writing Tests

#### Unit Tests

```python
# test_worker.py
import pytest
from auto_slopp.worker import Worker

class TestWorker:
    """Test the Worker base class."""
    
    def test_worker_is_abstract(self):
        """Test that Worker cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Worker()
    
    def test_custom_worker_implementation(self, temp_repo_path):
        """Test custom worker implementation."""
        class TestWorker(Worker):
            def run(self, repo_path):
                return {"test": True}
        
        worker = TestWorker()
        result = worker.run(temp_repo_path)
        
        assert result["test"] is True
```

#### Integration Tests

```python
# test_executor.py
import pytest
from auto_slopp.executor import Executor

class TestExecutor:
    """Test the Executor class."""
    
    def test_worker_discovery(self, temp_repo_path):
        """Test worker discovery functionality."""
        # Create test worker file
        worker_file = temp_repo_path / "test_worker.py"
        worker_file.write_text("""
from auto_slopp.worker import Worker

class TestWorker(Worker):
    def run(self, repo_path):
        return {"discovered": True}
""")
        
        executor = Executor(temp_repo_path)
        workers = executor.discover_workers()
        
        assert len(workers) > 0
        assert any("TestWorker" in w.__name__ for w in workers)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_worker.py

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run with markers
pytest -m "not slow"
```

### Test Coverage

Aim for high test coverage:

```bash
# Check coverage
pytest --cov=src --cov-report=term-missing

# Generate HTML report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html to view
```

## Code Quality

### Code Formatting

Use Black for code formatting:

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/
```

### Import Sorting

Use isort for import sorting:

```bash
# Sort imports
isort src/ tests/

# Check import sorting
isort --check-only src/ tests/
```

### Linting

Use flake8 for linting:

```bash
# Lint code
flake8 src/ tests/

# Lint with specific configuration
flake8 --config=.flake8 src/ tests/
```

### Type Checking

Use mypy for static type checking:

```bash
# Type check
mypy src/

# Type check with specific configuration
mypy --config-file=mypy.ini src/
```

### Pre-commit Hooks

Configure pre-commit hooks in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.14

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

## Debugging

### Debug Mode

Enable debug mode for verbose logging:

```bash
# Command line
auto-slopp --debug

# Environment variable
AUTO_SLOPP_DEBUG=true auto-slopp

# In .env file
AUTO_SLOPP_DEBUG=true
```

### Logging Configuration

Configure logging for development:

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Configure specific loggers
logging.getLogger("auto_slopp").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)
```

### Debugging Workers

Add debug logging to workers:

```python
import logging

class DebugWorker(Worker):
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DebugWorker")
    
    def run(self, repo_path):
        self.logger.debug(f"Starting worker with repo={repo_path}")
        
        try:
            result = self._do_work(repo_path)
            self.logger.debug(f"Worker completed successfully: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Worker failed: {e}", exc_info=True)
            raise
```

### Using pdb

Add breakpoints for debugging:

```python
import pdb

class DebugWorker(Worker):
    def run(self, repo_path):
        pdb.set_trace()  # Breakpoint
        # ... rest of the code
```

## Performance Considerations

### Worker Discovery

Optimize worker discovery:

```python
# Cache discovered workers
class Executor:
    def __init__(self, search_path: Path):
        self.search_path = search_path
        self._workers_cache: Optional[List[Type[Worker]]] = None
    
    def discover_workers(self) -> List[Type[Worker]]:
        if self._workers_cache is None:
            self._workers_cache = self._load_workers()
        return self._workers_cache
```

### Async Operations

Use async for I/O-bound operations:

```python
import asyncio
import aiofiles

async def process_files_async(file_paths: List[Path]):
    """Process files asynchronously."""
    tasks = []
    for file_path in file_paths:
        task = asyncio.create_task(process_file_async(file_path))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### Memory Management

Manage memory for large operations:

```python
def process_large_file(file_path: Path, chunk_size: int = 8192):
    """Process large file in chunks."""
    with open(file_path, 'r') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield process_chunk(chunk)
```

## Common Patterns

### Error Handling

Implement consistent error handling:

```python
from typing import Optional, Any
import logging

class WorkerBase(Worker):
    """Base worker with error handling."""
    
    def run(self, repo_path: Path) -> Any:
        try:
            return self._execute(repo_path)
        except Exception as e:
            self.logger.error(f"Worker {self.__class__.__name__} failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _execute(self, repo_path: Path) -> Any:
        """Override this method in subclasses."""
        raise NotImplementedError
```

### Configuration Validation

Validate configuration:

```python
from pydantic import validator

class Settings(BaseSettings):
    max_file_size: int = Field(default=5 * 1024 * 1024)
    
    @validator('max_file_size')
    def validate_max_file_size(cls, v):
        if v <= 0:
            raise ValueError('max_file_size must be positive')
        if v > 100 * 1024 * 1024:  # 100MB
            raise ValueError('max_file_size too large (max 100MB)')
        return v
```

### Resource Management

Use context managers for resources:

```python
from contextlib import contextmanager

@contextmanager
def temporary_directory():
    """Create and clean up temporary directory."""
    import tempfile
    temp_dir = tempfile.mkdtemp()
    try:
        yield Path(temp_dir)
    finally:
        import shutil
        shutil.rmtree(temp_dir)
```

### Plugin Architecture

Implement plugin system:

```python
class PluginRegistry:
    """Registry for worker plugins."""
    
    def __init__(self):
        self._plugins = {}
    
    def register(self, name: str, worker_class: Type[Worker]):
        """Register a worker plugin."""
        self._plugins[name] = worker_class
    
    def get(self, name: str) -> Optional[Type[Worker]]:
        """Get a registered worker plugin."""
        return self._plugins.get(name)
    
    def list_all(self) -> List[str]:
        """List all registered plugin names."""
        return list(self._plugins.keys())

# Global registry
registry = PluginRegistry()

# Decorator for registration
def register_worker(name: str):
    def decorator(cls):
        registry.register(name, cls)
        return cls
    return decorator
```

---

For more information, see the [API Reference](api-reference.md) and [Architecture Overview](architecture.md).