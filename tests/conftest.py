"""Pytest configuration and shared fixtures."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing.
    
    Returns:
        Path: Temporary directory path.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def temp_repo_dir(temp_dir):
    """Create a temporary repository directory with basic structure.
    
    Args:
        temp_dir: Temporary directory fixture.
        
    Returns:
        Path: Temporary repository directory path.
    """
    repo_dir = temp_dir / "test_repo"
    repo_dir.mkdir()
    
    # Create some basic files
    (repo_dir / "README.md").write_text("# Test Repository")
    (repo_dir / "src").mkdir()
    (repo_dir / "src" / "main.py").write_text("print('Hello, World!')")
    (repo_dir / "tests").mkdir()
    
    return repo_dir


@pytest.fixture
def temp_task_dir(temp_dir):
    """Create a temporary task directory with sample tasks.
    
    Args:
        temp_dir: Temporary directory fixture.
        
    Returns:
        Path: Temporary task directory path.
    """
    task_dir = temp_dir / "test_tasks"
    task_dir.mkdir()
    
    # Create some sample task files
    (task_dir / "task1.json").write_text('{"name": "task1", "type": "test"}')
    (task_dir / "task2.txt").write_text("This is a text task file")
    
    return task_dir


@pytest.fixture
def temp_workers_dir(temp_dir):
    """Create a temporary workers directory with sample worker files.
    
    Args:
        temp_dir: Temporary directory fixture.
        
    Returns:
        Path: Temporary workers directory path.
    """
    workers_dir = temp_dir / "workers"
    workers_dir.mkdir()
    (workers_dir / "__init__.py").write_text("")
    
    # Create sample worker file
    worker_code = '''
from pathlib import Path
from auto_slopp.worker import Worker

class TestWorker(Worker):
    """Test worker for testing purposes."""
    
    def run(self, repo_path: Path, task_path: Path) -> dict:
        return {"status": "completed", "repo": str(repo_path), "task": str(task_path)}
'''
    (workers_dir / "test_worker.py").write_text(worker_code)
    
    return workers_dir


@pytest.fixture
def mock_settings():
    """Create a mock settings object.
    
    Returns:
        MagicMock: Mock settings object with default values.
    """
    settings = MagicMock()
    settings.base_repo_path = Path("/test/repo")
    settings.base_task_path = Path("/test/tasks")
    settings.worker_search_path = Path("/test/workers")
    settings.executor_sleep_interval = 1.0
    settings.debug = False
    settings.telegram_enabled = False
    settings.telegram_bot_token = None
    settings.telegram_chat_id = None
    settings.telegram_timeout = 30.0
    settings.telegram_retry_attempts = 3
    settings.telegram_retry_delay = 1.0
    settings.telegram_parse_mode = "HTML"
    settings.telegram_disable_web_page_preview = True
    settings.telegram_disable_notification = False
    return settings


@pytest.fixture
def sample_log_record():
    """Create a sample log record for testing.
    
    Returns:
        logging.LogRecord: Sample log record.
    """
    import logging
    
    return logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="/test/file.py",
        lineno=42,
        msg="Test log message",
        args=(),
        exc_info=None
    )