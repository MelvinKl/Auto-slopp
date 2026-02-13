"""Tests for UnderscorePytestWorker."""

import tempfile
from pathlib import Path

import pytest

from auto_slopp.workers.underscore_pytest_worker import UnderscorePytestWorker


class TestUnderscorePytestWorker:
    """Tests for UnderscorePytestWorker."""

    def test_initialization(self):
        """Test worker initialization."""
        worker = UnderscorePytestWorker()
        assert worker.file_pattern == "_pytest*"

    def test_run_with_existing_path(self):
        """Test run with existing directory containing _pytest files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "_pytest_example.py").write_text("# pytest config")
            (repo_path / "conftest.py").write_text("import pytest")

            worker = UnderscorePytestWorker()
            result = worker.run(repo_path, repo_path)

            assert result["success"] is True

    def test_run_with_nonexistent_path(self):
        """Test run with non-existent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "nonexistent"

            worker = UnderscorePytestWorker()
            result = worker.run(repo_path, repo_path)

            assert result["success"] is False
            assert "error" in result

    def test_run_empty_directory(self):
        """Test run with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            worker = UnderscorePytestWorker()
            result = worker.run(repo_path, repo_path)

            assert result["success"] is True
            assert result["files_found"] == 0
