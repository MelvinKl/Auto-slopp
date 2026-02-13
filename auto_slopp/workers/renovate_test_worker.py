from pathlib import Path

from auto_slopp.worker import Worker


class RenovateTestWorker(Worker):
    """Worker for testing renovate integration."""

    name = "renovate_test"

    def run(self, repo_path: Path, task_path: Path) -> dict:
        """Run renovate tests."""
        return {
            "status": "completed",
            "repo": str(repo_path),
            "task": str(task_path),
        }
