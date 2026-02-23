# API Reference

This document provides comprehensive API reference for Auto-slopp classes, functions, and interfaces.

## Table of Contents

- [Core Classes](#core-classes)
  - [Worker](#worker)
  - [Executor](#executor)
- [Discovery Functions](#discovery-functions)
  - [discover_workers](#discover_workers)
- [Settings](#settings)
- [Telegram Integration](#telegram-integration)
  - [TelegramHandler](#telegramhandler)
  - [setup_telegram_logging](#setup_telegram_logging)
- [Example Workers](#example-workers)

## Core Classes

### Worker

Abstract base class for all worker implementations.

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

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

        Raises:
            Exception: If the worker execution fails
        """
        pass
```

#### Usage Example

```python
from pathlib import Path
from auto_slopp.worker import Worker
from typing import Dict, Any

class MyWorker(Worker):
    """Custom worker implementation."""
    
    def run(self, repo_path: Path) -> Dict[str, Any]:
        """Execute custom automation logic."""
        result = {
            "status": "completed",
            "repo_path": str(repo_path),
            "processed_items": 42
        }
        return result
```

### Executor

Discovers and executes worker implementations.

```python
from pathlib import Path
from typing import List, Type, Dict, Any
import importlib.util
import logging

class Executor:
    """Discovers and executes worker implementations."""
    
    def __init__(self, search_path: Path):
        """
        Initialize the executor.

        Args:
            search_path: Path to search for worker implementations
        """
        self.search_path = search_path
        self.logger = logging.getLogger("auto_slopp.executor")
        self.workers: List[Type[Worker]] = []
    
    def discover_workers(self) -> List[Type[Worker]]:
        """
        Discover worker implementations in the search path.

        Returns:
            List of discovered worker classes

        Raises:
            ImportError: If worker modules cannot be imported
        """
        pass
    
    def execute_workers(self, repo_path: Path) -> Dict[str, Any]:
        """
        Execute all discovered workers.

        Args:
            repo_path: Path to the repository directory

        Returns:
            Dictionary containing execution results from all workers

        Raises:
            Exception: If worker execution fails
        """
        pass
```

## Discovery Functions

### discover_workers

```python
from pathlib import Path
from typing import List, Type

def discover_workers(search_path: Path) -> List[Type[Worker]]:
    """
    Discover worker implementations in the given search path.

    Args:
        search_path: Path to search for worker implementations

    Returns:
        List of discovered worker classes

    Example:
        >>> workers = discover_workers(Path("/path/to/workers"))
        >>> print(f"Found {len(workers)} workers")
    """
    pass
```

## Settings

Configuration management using Pydantic settings.

```python
from pathlib import Path
from typing import Optional
from pydantic import Field, BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Path Configuration
    base_repo_path: Path = Field(
        default_factory=lambda: Path.cwd(),
        description="Base path for repository operations"
    )
    
    worker_search_path: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent,
        description="Path to search for worker implementations"
    )
    
    # Execution Configuration
    executor_sleep_interval: float = Field(
        default=1.0,
        description="Sleep interval between worker executions in seconds"
    )
    
    debug: bool = Field(
        default=False,
        description="Enable debug mode with verbose logging"
    )
    
    # Telegram Configuration
    telegram_enabled: bool = Field(
        default=False,
        description="Enable Telegram logging integration"
    )
    
    telegram_bot_token: Optional[str] = Field(
        default=None,
        description="Telegram bot token for logging"
    )
    
    telegram_chat_id: Optional[str] = Field(
        default=None,
        description="Telegram chat ID for notifications"
    )
    
    telegram_timeout: float = Field(
        default=30.0,
        description="Telegram API request timeout in seconds"
    )
    
    telegram_retry_attempts: int = Field(
        default=3,
        description="Number of retry attempts for failed Telegram requests"
    )
    
    telegram_retry_delay: float = Field(
        default=1.0,
        description="Delay between retry attempts in seconds"
    )
    
    telegram_parse_mode: str = Field(
        default="HTML",
        description="Message parse mode (HTML, Markdown, or empty)"
    )
    
    telegram_disable_web_page_preview: bool = Field(
        default=True,
        description="Disable link previews in Telegram messages"
    )
    
    telegram_disable_notification: bool = Field(
        default=False,
        description="Send Telegram messages silently"
    )
    
    class Config:
        env_prefix = "AUTO_SLOPP_"
        env_file = ".env"
        case_sensitive = False
```

## Telegram Integration

### TelegramHandler

Logging handler for sending log messages to Telegram.

```python
import logging
import asyncio
from typing import Optional
import httpx

class TelegramHandler(logging.Handler):
    """Async logging handler for Telegram bot integration."""
    
    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        timeout: float = 30.0,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = True,
        disable_notification: bool = False,
    ):
        """
        Initialize Telegram handler.

        Args:
            bot_token: Telegram bot token (overrides settings)
            chat_id: Target chat ID (overrides settings)
            timeout: HTTP request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
            retry_delay: Delay between retry attempts in seconds
            parse_mode: Message format (HTML, Markdown, or empty)
            disable_web_page_preview: Disable link previews in messages
            disable_notification: Send messages silently
        """
        pass
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Send a log record to Telegram.

        Args:
            record: Log record to send
        """
        pass
    
    def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        pass
```

### setup_telegram_logging

```python
import logging
from typing import Optional

def setup_telegram_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    **handler_kwargs
) -> Optional[logging.Handler]:
    """
    Set up Telegram logging with sensible defaults.

    Args:
        level: Logging level for the handler
        format_string: Custom message format string
        **handler_kwargs: Additional arguments for TelegramHandler

    Returns:
        Configured TelegramHandler or None if disabled

    Example:
        >>> handler = setup_telegram_logging(level=logging.WARNING)
        >>> logger = logging.getLogger("my_app")
        >>> logger.addHandler(handler)
        >>> logger.warning("This will go to Telegram")
    """
    pass
```

## Example Workers

### SimpleLogger

```python
class SimpleLogger(Worker):
    """Logs basic information about repository path."""
    
    def run(self, repo_path: Path) -> Dict[str, Any]:
        """
        Log path information and return basic details.

        Returns:
            Dictionary with path information and existence checks
        """
        pass
```

### FileMonitor

```python
class FileMonitor(Worker):
    """Scans repository for files matching specific patterns."""
    
    def __init__(self, file_patterns: List[str] = None):
        """
        Initialize file monitor.

        Args:
            file_patterns: List of file patterns to match (default: ["*"])
        """
        self.file_patterns = file_patterns or ["*"]
    
    def run(self, repo_path: Path) -> Dict[str, Any]:
        """
        Scan repository and return file statistics.

        Returns:
            Dictionary with file counts, sizes, and pattern matches
        """
        pass
```

### TaskProcessor

```python
class TaskProcessor(Worker):
    """Processes task files with size limits and content analysis."""
    
    def __init__(self, max_file_size: int = 5 * 1024 * 1024):
        """
        Initialize task processor.

        Args:
            max_file_size: Maximum file size to process in bytes
        """
        self.max_file_size = max_file_size
    
    def run(self, repo_path: Path) -> Dict[str, Any]:
        """
        Process task files and return analysis results.

        Returns:
            Dictionary with processed files, content previews, and metadata
        """
        pass
```

### HeartbeatWorker

```python
class HeartbeatWorker(Worker):
    """Demonstrates periodic execution with status messages."""
    
    def __init__(self, message: str = "Auto-slopp heartbeat"):
        """
        Initialize heartbeat worker.

        Args:
            message: Custom heartbeat message
        """
        self.message = message
    
    def run(self, repo_path: Path) -> Dict[str, Any]:
        """
        Generate heartbeat status message.

        Returns:
            Dictionary with timestamp, message, and path information
        """
        pass
```

## Error Handling

### Common Exceptions

- **ImportError**: Raised when worker modules cannot be imported
- **ValueError**: Raised for invalid configuration values
- **RuntimeError**: Raised for execution failures
- **ConnectionError**: Raised for Telegram API connection issues

### Error Recovery

The executor implements graceful error handling:

```python
try:
    result = executor.execute_workers(repo_path)
except ImportError as e:
    logger.error(f"Failed to import workers: {e}")
    # Handle import errors
except Exception as e:
    logger.error(f"Worker execution failed: {e}")
    # Handle execution errors
```

## Type Hints

Auto-slopp uses comprehensive type hints throughout the codebase:

```python
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Function signatures with type hints
def process_data(
    input_path: Path,
    config: Dict[str, Any],
    options: Optional[List[str]] = None
) -> Dict[str, Union[str, int, float]]:
    """Process data with type-annotated parameters and return value."""
    pass
```

## Constants

```python
# Version information
__version__ = "0.1.0"

# Default values
DEFAULT_TIMEOUT = 30.0
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY = 1.0

# Log levels
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"
```

---

For more examples and usage patterns, see the [Development Guide](development-guide.md) and refer to the source code in the `src/auto_slopp/` directory.