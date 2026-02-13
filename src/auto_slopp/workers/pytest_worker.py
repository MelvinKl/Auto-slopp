"""Pytest worker for handling pytest-related files."""

import logging
from pathlib import Path
from typing import Any, Dict

from auto_slopp.worker import Worker


class PytestWorker(Worker):
    """Worker for handling pytest-related files and test execution.

    This worker scans the repository for pytest-related files and
    provides information about them.
    """

    def __init__(self, file_pattern: str = "test_*.py"):
        """Initialize the PytestWorker.

        Args:
            file_pattern: Pattern to match pytest test files
        """
        self.file_pattern = file_pattern
        self.logger = logging.getLogger("auto_slopp.workers.PytestWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute the pytest worker task.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing information about found pytest files
        """
        self.logger.info(f"PytestWorker starting with repo_path: {repo_path}")

        if not repo_path.exists():
            return {
                "worker_name": "PytestWorker",
                "success": False,
                "error": f"Repository path does not exist: {repo_path}",
                "files_found": 0,
            }

        test_files = list(repo_path.rglob(self.file_pattern))
        test_files.extend(list(repo_path.rglob("*_test.py")))

        test_files = sorted(set(test_files))

        total_lines = 0
        for f in test_files:
            if f.is_file():
                try:
                    total_lines += len(f.read_text().splitlines())
                except Exception:
                    pass

        return {
            "worker_name": "PytestWorker",
            "success": True,
            "repo_path": str(repo_path),
            "task_path": str(task_path),
            "file_pattern": self.file_pattern,
            "files_found": len(test_files),
            "total_lines": total_lines,
            "test_files": [str(f.relative_to(repo_path)) for f in test_files[:10]],
        }
