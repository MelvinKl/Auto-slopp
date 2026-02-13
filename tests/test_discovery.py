"""Tests for discovery module."""

from pathlib import Path

import pytest

from auto_slopp.discovery import discover_workers, get_worker_by_name


class TestDiscoverWorkers:
    """Test cases for discover_workers function."""

    def test_returns_empty_list_for_nonexistent_path(self, tmp_path):
        """Test that nonexistent path returns empty list."""
        result = discover_workers(tmp_path / "nonexistent")
        assert result == []

    def test_returns_empty_list_for_empty_directory(self, tmp_path):
        """Test that empty directory returns empty list."""
        result = discover_workers(tmp_path)
        assert result == []


class TestGetWorkerByName:
    """Test cases for get_worker_by_name function."""

    def test_finds_worker_by_name(self):
        """Test that worker is found by name."""
        from auto_slopp.worker import Worker

        class TestWorker(Worker):
            name = "test"

            def run(self, repo_path: Path, task_path: Path) -> dict:
                return {}

        workers = [TestWorker]
        result = get_worker_by_name("test", workers)

        assert result == TestWorker

    def test_returns_none_for_unknown_name(self):
        """Test that unknown name returns None."""
        from auto_slopp.worker import Worker

        class TestWorker(Worker):
            name = "test"

            def run(self, repo_path: Path, task_path: Path) -> dict:
                return {}

        workers = [TestWorker]
        result = get_worker_by_name("unknown", workers)

        assert result is None
