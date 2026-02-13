"""Tests for PyWorker."""

import tempfile
from pathlib import Path

import pytest

from auto_slopp.workers.py_worker import PyWorker


class TestPyWorker:
    """Tests for PyWorker."""

    def test_initialization(self):
        """Test worker initialization."""
        worker = PyWorker()
        assert "__pycache__" in worker.exclude_patterns

    def test_run_with_existing_path(self):
        """Test run with existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "test_file.py").write_text("print('hello')")
            (repo_path / "__init__.py").write_text("")
            (repo_path / "module.py").write_text("def foo(): pass")

            worker = PyWorker()
            result = worker.run(repo_path, repo_path)

            assert result["success"] is True
            assert result["files_found"] >= 3

    def test_run_with_nonexistent_path(self):
        """Test run with non-existent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "nonexistent"

            worker = PyWorker()
            result = worker.run(repo_path, repo_path)

            assert result["success"] is False
            assert "error" in result

    def test_run_excludes_venv(self):
        """Test that venv directories are excluded."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "main.py").write_text("print('hello')")

            venv_dir = repo_path / ".venv"
            venv_dir.mkdir()
            (venv_dir / "script.py").write_text("print('venv')")

            worker = PyWorker()
            result = worker.run(repo_path, repo_path)

            assert result["success"] is True
            py_files = result["py_files"]
            assert all(".venv" not in f for f in py_files)
