"""Underscore pytest worker for handling _pytest* files."""

import logging
from pathlib import Path
from typing import Any, Dict

from auto_slopp.worker import Worker


class UnderscorePytestWorker(Worker):
    """Worker for handling files starting with _pytest.

    This worker scans the repository for files matching _pytest* pattern.
    """

    def __init__(self, file_pattern: str = "_pytest*"):
        """Initialize the UnderscorePytestWorker.

        Args:
            file_pattern: Pattern to match _pytest files
        """
        self.file_pattern = file_pattern
        self.logger = logging.getLogger("auto_slopp.workers.UnderscorePytestWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute the _pytest worker task.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing information about found _pytest files
        """
        self.logger.info(f"UnderscorePytestWorker starting with repo_path: {repo_path}")

        if not repo_path.exists():
            return {
                "worker_name": "UnderscorePytestWorker",
                "success": False,
                "error": f"Repository path does not exist: {repo_path}",
                "files_found": 0,
            }

        test_files = list(repo_path.rglob(self.file_pattern))
        test_files = sorted(set(test_files))

        total_lines = 0
        for f in test_files:
            if f.is_file():
                try:
                    total_lines += len(f.read_text().splitlines())
                except Exception:
                    pass

        return {
            "worker_name": "UnderscorePytestWorker",
            "success": True,
            "repo_path": str(repo_path),
            "task_path": str(task_path),
            "file_pattern": self.file_pattern,
            "files_found": len(test_files),
            "total_lines": total_lines,
            "test_files": [str(f.relative_to(repo_path)) for f in test_files[:10]],
        }
