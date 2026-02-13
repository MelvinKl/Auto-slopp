from pathlib import Path

from auto_slopp.worker import Worker


class TaskProcessorWorker(Worker):
    """Worker for processing tasks."""

    name = "task_processor"

    def run(self, repo_path: Path, task_path: Path) -> dict:
        """Process tasks in the repository."""
        return {
            "status": "completed",
            "repo": str(repo_path),
            "task": str(task_path),
        }
