"""Simple logging worker that demonstrates basic functionality.

This worker logs information about the repository and task paths
and reports basic statistics.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from ...worker import Worker


class SimpleLogger(Worker):
    """Simple logging worker that demonstrates basic functionality.

    This worker logs information about the repository and task paths
    and reports basic statistics.
    """

    def __init__(self, name: str = "SimpleLogger"):
        """Initialize the simple logger worker.

        Args:
            name: Name identifier for this worker instance.
        """
        self.name = name
        self.logger = logging.getLogger(f"auto_slopp.workers.{name}")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Log information about paths and return statistics.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing execution statistics and path info.
        """
        start_time = time.time()

        self.logger.info(f"{self.name} starting execution")
        self.logger.info(f"Repository path: {repo_path}")
        self.logger.info(f"Task path: {task_path}")

        # Check if paths exist
        repo_exists = repo_path.exists()
        task_exists = task_path.exists()

        self.logger.info(f"Repository exists: {repo_exists}")
        self.logger.info(f"Task path exists: {task_exists}")

        # Count files in repository if it exists
        file_count = 0
        if repo_exists and repo_path.is_dir():
            file_count = len(list(repo_path.rglob("*")))
            self.logger.info(f"Files in repository: {file_count}")

        execution_time = time.time() - start_time

        result = {
            "worker_name": self.name,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "repo_path": str(repo_path),
            "task_path": str(task_path),
            "repo_exists": repo_exists,
            "task_exists": task_exists,
            "file_count": file_count,
        }

        self.logger.info(f"{self.name} completed in {execution_time:.2f}s")
        return result