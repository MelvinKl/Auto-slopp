# Contributing Guide

This guide provides comprehensive information for contributing to Auto-slopp, including development setup, contribution guidelines, and community practices.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Contribution Types](#contribution-types)
3. [Development Workflow](#development-workflow)
4. [Code Standards](#code-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation Standards](#documentation-standards)
7. [Pull Request Process](#pull-request-process)
8. [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

- Python 3.14 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Git
- GitHub account
- Code editor (VS Code recommended)

### Initial Setup

1. **Fork the Repository**
   ```bash
   # Fork the repository on GitHub, then clone your fork
   git clone https://github.com/your-username/Auto-slopp.git
   cd Auto-slopp
   ```

2. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/original-owner/Auto-slopp.git
   ```

3. **Set Up Development Environment**
   ```bash
   uv sync --dev
   source .venv/bin/activate
   ```

4. **Verify Setup**
   ```bash
   auto-slopp --version
   pytest --version
   ```

5. **Configure Git**
   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

### Development Environment

#### VS Code Setup

Install recommended extensions:
- Python
- Black Formatter
- isort
- Flake8
- GitLens

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
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

## Contribution Types

### 1. Bug Reports

Report bugs using GitHub Issues with the following template:

```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.14.0]
- Auto-slopp version: [e.g., 0.1.0]

## Additional Context
Any other relevant information
```

### 2. Feature Requests

Request features using GitHub Issues:

```markdown
## Feature Description
Brief description of the feature

## Problem Statement
What problem does this feature solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
What alternatives have you considered?

## Additional Context
Any other relevant information
```

### 3. Code Contributions

Code contributions include:
- New features
- Bug fixes
- Performance improvements
- Code refactoring
- Test improvements

### 4. Documentation Contributions

Documentation contributions include:
- README improvements
- API documentation updates
- Tutorial creation
- Example code
- Architecture documentation

## Development Workflow

### 1. Create Feature Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### 2. Make Changes

Follow the development workflow:

```bash
# Make your changes
# ... edit files ...

# Run tests
pytest

# Check code quality
black src/ tests/
isort src/ tests/
flake8 src/ tests/

# Run pre-commit hooks
pre-commit run --all-files
```

### 3. Commit Changes

Use conventional commit messages:

```bash
# Add changes
git add .

# Commit with conventional message
git commit -m "feat: add new worker type for XYZ processing"

# Examples:
# git commit -m "fix: resolve worker discovery issue with nested paths"
# git commit -m "docs: update API reference with new methods"
# git commit -m "test: add integration tests for executor"
# git commit -m "refactor: simplify worker discovery logic"
```

### 4. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Code Standards

### 1. Code Style

Follow the established code style:

```python
# Use Black formatting (120 character line length)
# Use isort for import sorting
# Follow PEP 8 guidelines
# Use type hints consistently

# Good example:
from pathlib import Path
from typing import Any, Dict, List

class ExampleWorker(Worker):
    """Example worker implementation."""
    
    def __init__(self, max_items: int = 100):
        self.max_items = max_items
        self.logger = logging.getLogger(__name__)
    
    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Process items with configurable limits."""
        self.logger.info(f"Processing up to {self.max_items} items")
        
        processed_items = self._process_items(repo_path)
        
        return {
            "worker_name": "ExampleWorker",
            "processed_items": processed_items,
            "limit_reached": processed_items >= self.max_items
        }
```

### 2. Documentation Standards

#### Docstrings

Use Google-style docstrings:

```python
def process_data(
    input_path: Path,
    config: Dict[str, Any],
    max_size: int = 1024 * 1024
) -> Dict[str, Any]:
    """Process data from input file with configuration.
    
    Args:
        input_path: Path to the input data file
        config: Configuration dictionary for processing
        max_size: Maximum file size in bytes (default: 1MB)
    
    Returns:
        Dictionary containing processing results and metadata
    
    Raises:
        FileNotFoundError: If input_path does not exist
        ValueError: If config contains invalid values
        PermissionError: If unable to read input file
    
    Example:
        >>> result = process_data(
        ...     Path("data.txt"),
        ...     {"mode": "fast", "output": "json"}
        ... )
        >>> print(result["status"])
        'completed'
    """
    pass
```

#### Comments

Use comments to explain complex logic:

```python
# Calculate worker discovery hash for caching
# This hash includes file paths, modification times, and file sizes
# to ensure cache invalidation when workers change
discovery_hash = hashlib.sha256()
for file_path in worker_files:
    discovery_hash.update(str(file_path).encode())
    discovery_hash.update(str(file_path.stat().st_mtime).encode())
    discovery_hash.update(str(file_path.stat().st_size).encode())
```

### 3. Type Hints

Use comprehensive type hints:

```python
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path

class WorkerResult:
    """Result from worker execution."""
    
    def __init__(
        self,
        status: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        execution_time: Optional[float] = None
    ):
        self.status = status
        self.data = data or {}
        self.error = error
        self.execution_time = execution_time

def execute_workers(
    workers: List[Type[Worker]],
    repo_path: Path,
    task_path: Path,
    progress_callback: Optional[Callable[[str], None]] = None
) -> Dict[str, WorkerResult]:
    """Execute workers and return results."""
    pass
```

### 4. Error Handling

Implement consistent error handling:

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class WorkerError(Exception):
    """Base exception for worker-related errors."""
    pass

class WorkerExecutionError(WorkerError):
    """Exception raised when worker execution fails."""
    
    def __init__(self, worker_name: str, cause: Exception):
        self.worker_name = worker_name
        self.cause = cause
        super().__init__(f"Worker {worker_name} failed: {cause}")

def safe_execute_worker(worker: Worker, repo_path: Path, task_path: Path) -> Optional[Any]:
    """Safely execute a worker with error handling."""
    try:
        return worker.run(repo_path, task_path)
    except Exception as e:
        logger.error(f"Worker {worker.__class__.__name__} failed: {e}", exc_info=True)
        return None
```

## Testing Guidelines

### 1. Test Structure

Organize tests by component:

```
tests/
├── unit/                    # Unit tests
│   ├── test_worker.py
│   ├── test_settings.py
│   └── test_discovery.py
├── integration/             # Integration tests
│   ├── test_executor.py
│   └── test_telegram_handler.py
├── e2e/                     # End-to-end tests
│   └── test_main.py
└── fixtures/                # Test data and utilities
    ├── sample_workers.py
    └── test_data.json
```

### 2. Test Writing Standards

#### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from auto_slopp.worker import Worker

class TestWorker:
    """Test the Worker base class."""
    
    def test_worker_is_abstract(self):
        """Test that Worker cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            Worker()
    
    def test_custom_worker_implementation(self, temp_repo_path):
        """Test custom worker implementation."""
        class TestWorker(Worker):
            def run(self, repo_path, task_path):
                return {"test": True, "repo": str(repo_path)}
        
        worker = TestWorker()
        result = worker.run(temp_repo_path, temp_repo_path / "task")
        
        assert result["test"] is True
        assert result["repo"] == str(temp_repo_path)
    
    @patch('auto_slopp.worker.logging.getLogger')
    def test_worker_logging(self, mock_getter):
        """Test worker logging setup."""
        mock_logger = Mock()
        mock_getter.return_value = mock_logger
        
        class LoggingWorker(Worker):
            def run(self, repo_path, task_path):
                self.logger.info("Test message")
                return {"logged": True}
        
        worker = LoggingWorker()
        worker.run(Path("/test"), Path("/test/task"))
        
        mock_logger.info.assert_called_once_with("Test message")
```

#### Integration Tests

```python
import pytest
from auto_slopp.executor import Executor

class TestExecutorIntegration:
    """Integration tests for Executor."""
    
    def test_full_worker_discovery_and_execution(self, tmp_path):
        """Test complete worker discovery and execution cycle."""
        # Create test worker file
        worker_file = tmp_path / "test_worker.py"
        worker_file.write_text("""
from auto_slopp.worker import Worker
from pathlib import Path

class TestWorker(Worker):
    def run(self, repo_path: Path, task_path: Path):
        return {
            "worker_name": "TestWorker",
            "repo_exists": repo_path.exists(),
            "task_exists": task_path.exists()
        }
""")
        
        # Test discovery and execution
        executor = Executor(tmp_path)
        workers = executor.discover_workers()
        
        assert len(workers) == 1
        assert workers[0].__name__ == "TestWorker"
        
        results = executor.execute_workers(tmp_path, tmp_path / "task")
        assert "TestWorker" in results
        assert results["TestWorker"]["worker_name"] == "TestWorker"
```

### 3. Test Fixtures

Create reusable fixtures:

```python
# conftest.py
import pytest
from pathlib import Path
from unittest.mock import Mock
import tempfile

@pytest.fixture
def temp_repo_path(tmp_path):
    """Create a temporary repository path."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    
    # Create basic repo structure
    (repo_path / "README.md").write_text("# Test Repo")
    (repo_path / "src").mkdir()
    
    return repo_path

@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = Mock()
    settings.base_repo_path = Path("/test/repo")
    settings.base_task_path = Path("/test/tasks")
    settings.worker_search_path = Path("/test/workers")
    settings.debug = True
    settings.telegram_enabled = False
    return settings

@pytest.fixture
def sample_worker_class():
    """Create a sample worker class for testing."""
    class SampleWorker(Worker):
        def run(self, repo_path, task_path):
            return {
                "worker_name": "SampleWorker",
                "repo_path": str(repo_path),
                "task_path": str(task_path)
            }
    return SampleWorker
```

### 4. Test Coverage

Maintain high test coverage:

```bash
# Check coverage
pytest --cov=src --cov-report=term-missing

# Generate HTML report
pytest --cov=src --cov-report=html

# Coverage requirements:
# - Overall coverage: > 90%
# - Core modules: > 95%
# - New features: 100%
```

## Documentation Standards

### 1. README Standards

Keep README comprehensive and up-to-date:

```markdown
# Project Name

Brief description of the project.

## Features
- Feature 1
- Feature 2

## Installation
Quick installation instructions.

## Usage
Basic usage examples.

## Configuration
Configuration options.

## Contributing
Link to contributing guide.

## License
License information.
```

### 2. API Documentation

Document all public APIs:

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """
    Brief description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: If param1 is invalid
    
    Example:
        >>> result = example_function("test", 5)
        >>> print(result)
        True
    """
    pass
```

### 3. Code Comments

Use comments for complex logic:

```python
# Complex algorithm explanation
# This implements the XYZ algorithm which:
# 1. Processes input data in chunks
# 2. Maintains a sliding window of size N
# 3. Applies transformation to each window
# 4. Aggregates results efficiently
```

## Pull Request Process

### 1. PR Requirements

Before submitting a PR:

- [ ] Tests pass locally
- [ ] Code coverage is maintained
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] PR description is comprehensive
- [ ] No breaking changes without discussion

### 2. PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] No merge conflicts

## Additional Context
Any additional information or context
```

### 3. Review Process

1. **Self-Review**: Review your own changes
2. **Automated Checks**: CI/CD pipeline runs tests
3. **Peer Review**: At least one maintainer reviews
4. **Approval**: PR approved and merged

### 4. Merge Guidelines

- **Squash Commits**: Use squash merge for clean history
- **Main Branch**: Merge to main branch
- **Version Bump**: Update version if needed
- **Release Notes**: Add to release notes

## Community Guidelines

### 1. Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Assume good intentions

### 2. Communication

- Use GitHub Issues for bugs and features
- Use Discussions for questions and ideas
- Be patient with response times
- Provide clear and concise information

### 3. Recognition

- Recognize valuable contributions
- Thank contributors for their work
- Highlight community members in releases
- Celebrate milestones together

### 4. Getting Help

- Check existing documentation first
- Search existing issues and discussions
- Provide minimal reproduction examples
- Be specific about your environment and use case

## Release Process

### 1. Version Management

Use semantic versioning:
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### 2. Release Checklist

Before releasing:
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version number updated
- [ ] Tag created
- [ ] Release notes prepared

### 3. Post-Release

- [ ] Announce release
- [ ] Monitor for issues
- [ ] Update documentation
- [ ] Plan next release

---

Thank you for contributing to Auto-slopp! Your contributions help make this project better for everyone.