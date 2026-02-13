"""Python file worker for handling .py files."""

import logging
from pathlib import Path
from typing import Any, Dict

from auto_slopp.worker import Worker


class PyWorker(Worker):
    """Worker for handling Python (.py) files.

    This worker scans the repository for Python files.
    """

    def __init__(self, exclude_patterns: list[str] | None = None):
        """Initialize the PyWorker.

        Args:
            exclude_patterns: List of patterns to exclude from results
        """
        self.exclude_patterns = exclude_patterns or [
            "__pycache__",
            ".venv",
            "pytest_cache",
            "venv",
            ".git",
        ]
        self.logger = logging.getLogger("auto_slopp.workers.PyWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute the Python file worker task.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing information about found Python files
        """
        self.logger.info(f"PyWorker starting with repo_path: {repo_path}")

        if not repo_path.exists():
            return {
                "worker_name": "PyWorker",
                "success": False,
                "error": f"Repository path does not exist: {repo_path}",
                "files_found": 0,
            }

        py_files = []
        for f in repo_path.rglob("*.py"):
            if not any(excl in f.parts for excl in self.exclude_patterns):
                py_files.append(f)

        py_files = sorted(set(py_files))

        total_lines = 0
        file_types = {"test": 0, "module": 0, "other": 0}
        for f in py_files:
            if f.is_file():
                try:
                    lines = len(f.read_text().splitlines())
                    total_lines += lines
                    if "test" in f.name:
                        file_types["test"] += 1
                    elif "__init__" in f.name:
                        file_types["module"] += 1
                    else:
                        file_types["other"] += 1
                except Exception:
                    pass

        return {
            "worker_name": "PyWorker",
            "success": True,
            "repo_path": str(repo_path),
            "task_path": str(task_path),
            "files_found": len(py_files),
            "total_lines": total_lines,
            "file_types": file_types,
            "py_files": [str(f.relative_to(repo_path)) for f in py_files[:10]],
        }
