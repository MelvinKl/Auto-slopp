"""Tests for PytestWorker."""

import tempfile
from pathlib import Path

import pytest

from auto_slopp.workers.pytest_worker import PytestWorker


class TestPytestWorker:
    """Tests for PytestWorker."""

    def test_initialization(self):
        """Test worker initialization."""
        worker = PytestWorker()
        assert worker.file_pattern == "test_*.py"

    def test_run_with_existing_path(self):
        """Test run with existing directory containing test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "test_example.py").write_text("def test_one(): pass\ndef test_two(): pass")
            (repo_path / "example_test.py").write_text("def test_three(): pass")
            (repo_path / "regular.py").write_text("def foo(): pass")

            worker = PytestWorker()
            result = worker.run(repo_path, repo_path)

            assert result["success"] is True
            assert result["files_found"] >= 2

    def test_run_with_nonexistent_path(self):
        """Test run with non-existent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "nonexistent"

            worker = PytestWorker()
            result = worker.run(repo_path, repo_path)

            assert result["success"] is False
            assert "error" in result

    def test_run_empty_directory(self):
        """Test run with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            worker = PytestWorker()
            result = worker.run(repo_path, repo_path)

            assert result["success"] is True
            assert result["files_found"] == 0
