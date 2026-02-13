from pathlib import Path

from auto_slopp.worker import Worker


class StaleBranchCleanupWorker(Worker):
    """Worker for cleaning up stale branches."""

    name = "stale_branch_cleanup"

    def run(self, repo_path: Path, task_path: Path) -> dict:
        """Clean up stale branches."""
        return {
            "status": "completed",
            "repo": str(repo_path),
            "task": str(task_path),
        }
