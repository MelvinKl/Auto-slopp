"""Heartbeat worker that demonstrates periodic execution.

This worker simply sends a heartbeat message to show that
the executor is running properly.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from ...worker import Worker


class HeartbeatWorker(Worker):
    """Heartbeat worker that demonstrates periodic execution.

    This worker simply sends a heartbeat message to show that
    the executor is running properly.
    """

    def __init__(self, message: str = "Auto-slopp is running"):
        """Initialize the heartbeat worker.

        Args:
            message: Custom heartbeat message.
        """
        self.message = message
        self.logger = logging.getLogger("auto_slopp.workers.Heartbeat")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Send a heartbeat message.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing heartbeat information.
        """
        timestamp = datetime.now().isoformat()

        heartbeat_msg = f"{self.message} at {timestamp}"
        self.logger.info(heartbeat_msg)

        return {
            "worker_name": "HeartbeatWorker",
            "message": self.message,
            "timestamp": timestamp,
            "repo_path": str(repo_path),
            "task_path": str(task_path),
        }