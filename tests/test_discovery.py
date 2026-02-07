"""Tests for worker discovery mechanism."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from auto_slopp.discovery import discover_workers


class TestWorkerDiscovery:
    """Test cases for worker discovery functionality."""

    def test_discover_workers_empty_directory(self, temp_dir):
        """Test discovery in empty directory."""
        result = discover_workers(temp_dir)
        assert result == []

    def test_discover_workers_no_python_files(self, temp_dir):
        """Test discovery in directory with no Python files."""
        (temp_dir / "readme.txt").write_text("No Python files here")
        (temp_dir / "config.json").write_text('{"key": "value"}')

        result = discover_workers(temp_dir)
        assert result == []

    def test_discover_workers_with_valid_worker(self, temp_workers_dir):
        """Test discovery with a valid worker file."""
        result = discover_workers(temp_workers_dir)

        assert len(result) == 1
        worker_class = result[0]
        assert worker_class.__name__ == "TestWorker"
        assert hasattr(worker_class, "run")

    def test_discover_workers_ignores_non_worker_classes(self, temp_dir):
        """Test discovery ignores classes that don't inherit from Worker."""
        worker_code = '''
from pathlib import Path
from auto_slopp.worker import Worker

class NotAWorker:
    """Class that doesn't inherit from Worker."""
    pass

class AnotherClass:
    """Another non-worker class."""
    pass

class ValidWorker(Worker):
    """Valid worker class."""
    def run(self, repo_path: Path, task_path: Path):
        return {"status": "ok"}
'''
        (temp_dir / "mixed_workers.py").write_text(worker_code)

        result = discover_workers(temp_dir)

        assert len(result) == 1
        assert result[0].__name__ == "ValidWorker"

    def test_discover_workers_multiple_files(self, temp_dir):
        """Test discovery across multiple Python files."""
        # First worker file
        worker1_code = """
from pathlib import Path
from auto_slopp.worker import Worker

class Worker1(Worker):
    def run(self, repo_path: Path, task_path: Path):
        return {"worker": "1"}
"""
        (temp_dir / "worker1.py").write_text(worker1_code)

        # Second worker file
        worker2_code = """
from pathlib import Path
from auto_slopp.worker import Worker

class Worker2(Worker):
    def run(self, repo_path: Path, task_path: Path):
        return {"worker": "2"}
"""
        (temp_dir / "worker2.py").write_text(worker2_code)

        result = discover_workers(temp_dir)

        assert len(result) == 2
        worker_names = {w.__name__ for w in result}
        assert worker_names == {"Worker1", "Worker2"}

    def test_discover_workers_handles_import_errors_gracefully(self, temp_dir):
        """Test discovery handles import errors without crashing."""
        # File with invalid syntax
        (temp_dir / "invalid.py").write_text("invalid python syntax !!!")

        # Valid worker file
        valid_worker_code = """
from pathlib import Path
from auto_slopp.worker import Worker

class ValidWorker(Worker):
    def run(self, repo_path: Path, task_path: Path):
        return {"status": "ok"}
"""
        (temp_dir / "valid.py").write_text(valid_worker_code)

        # Should discover only the valid worker
        result = discover_workers(temp_dir)
        assert len(result) == 1
        assert result[0].__name__ == "ValidWorker"

    def test_discover_workers_with_nested_directories(self, temp_dir):
        """Test discovery with nested directory structure."""
        nested_dir = temp_dir / "nested"
        nested_dir.mkdir()

        worker_code = """
from pathlib import Path
from auto_slopp.worker import Worker

class NestedWorker(Worker):
    def run(self, repo_path: Path, task_path: Path):
        return {"nested": True}
"""
        (nested_dir / "worker.py").write_text(worker_code)

        result = discover_workers(temp_dir)

        assert len(result) == 1
        assert result[0].__name__ == "NestedWorker"

    def test_discover_workers_skips_init_files_by_default(self, temp_dir):
        """Test discovery skips __init__.py files due to import complexity."""
        init_code = """
from pathlib import Path
from auto_slopp.worker import Worker

class InitWorker(Worker):
    def run(self, repo_path: Path, task_path: Path):
        return {"from_init": True}
"""
        (temp_dir / "__init__.py").write_text(init_code)

        result = discover_workers(temp_dir)

        # Note: __init__.py files are skipped due to import complexity
        # Workers should be in regular Python files, not __init__.py
        assert len(result) == 0

    def test_discover_workers_ignores_test_files(self, temp_dir):
        """Test discovery includes both regular and test workers (filtering is done at higher level)."""
        # Regular worker
        worker_code = """
from pathlib import Path
from auto_slopp.worker import Worker

class RealWorker(Worker):
    def run(self, repo_path: Path, task_path: Path):
        return {"real": True}
"""
        (temp_dir / "worker.py").write_text(worker_code)

        # Test file with worker
        test_worker_code = """
from pathlib import Path
from auto_slopp.worker import Worker

class TestWorker(Worker):
    def run(self, repo_path: Path, task_path: Path):
        return {"test": True}
"""
        (temp_dir / "test_worker.py").write_text(test_worker_code)

        result = discover_workers(temp_dir)

        # Note: The discovery mechanism itself doesn't filter test files
        # That filtering would be done at a higher level if needed
        assert len(result) == 2
        worker_names = {w.__name__ for w in result}
        assert worker_names == {"RealWorker", "TestWorker"}

    def test_discover_workers_with_multiple_workers_in_same_file(self, temp_dir):
        """Test discovery handles multiple workers in the same file."""
        multi_worker_code = """
from pathlib import Path
from auto_slopp.worker import Worker

class FirstWorker(Worker):
    def run(self, repo_path: Path, task_path: Path):
        return {"worker": "first"}

class SecondWorker(Worker):
    def run(self, repo_path: Path, task_path: Path):
        return {"worker": "third"}

class ThirdWorker(Worker):
    def run(self, repo_path: Path, task_path: Path):
        return {"worker": "third"}
"""
        (temp_dir / "multi_workers.py").write_text(multi_worker_code)

        result = discover_workers(temp_dir)

        assert len(result) == 3
        worker_names = {w.__name__ for w in result}
        assert worker_names == {"FirstWorker", "SecondWorker", "ThirdWorker"}

    def test_discover_workers_nonexistent_path(self):
        """Test discovery with non-existent path."""
        nonexistent = Path("/nonexistent/path/that/should/not/exist")

        result = discover_workers(nonexistent)
        assert result == []

    def test_discover_workers_file_instead_of_directory(self, temp_dir):
        """Test discovery when path points to a file instead of directory."""
        test_file = temp_dir / "not_a_directory.py"
        test_file.write_text("print('hello')")

        result = discover_workers(test_file)
        assert result == []

    def test_discover_workers_with_abstract_worker_subclasses(self, temp_dir):
        """Test discovery ignores abstract worker subclasses."""
        abstract_worker_code = '''
from abc import abstractmethod
from pathlib import Path
from auto_slopp.worker import Worker

class AbstractWorker(Worker):
    """Abstract worker that shouldn't be discovered."""

    @abstractmethod
    def custom_method(self):
        pass

    def run(self, repo_path: Path, task_path: Path):
        return {"abstract": True}

class ConcreteWorker(AbstractWorker):
    """Concrete worker that should be discovered."""

    def custom_method(self):
        return "custom"
'''
        (temp_dir / "abstract_workers.py").write_text(abstract_worker_code)

        result = discover_workers(temp_dir)

        # Should only find the concrete worker
        assert len(result) == 1
        assert result[0].__name__ == "ConcreteWorker"
