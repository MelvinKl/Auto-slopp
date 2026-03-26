"""Vikunja Worker for processing tasks as instructions.

This worker is a thin wrapper around IssueWorker that uses VikunjaTaskSource.
"""

from pathlib import Path
from typing import Any, Dict

from auto_slopp.worker import Worker
from auto_slopp.workers.issue_worker import IssueWorker
from auto_slopp.workers.vikunja_task_source import VikunjaTaskSource


class VikunjaWorker(Worker):
    """Worker for processing Vikunja tasks as instructions.

    This worker is a thin wrapper that delegates to IssueWorker
    with VikunjaTaskSource for task loading and lifecycle management.
    """

    def __init__(
        self,
        timeout: int | None = None,
        agent_args: list[str] | None = None,
        dry_run: bool = False,
    ):
        """Initialize the VikunjaWorker.

        Args:
            timeout: Timeout for CLI execution in seconds (default: from settings.slop_timeout)
            agent_args: Additional arguments to pass to the CLI tool
            dry_run: If True, skip actual CLI execution and git operations
        """
        task_source = VikunjaTaskSource()
        self._worker = IssueWorker(
            task_source=task_source,
            timeout=timeout,
            agent_args=agent_args,
            dry_run=dry_run,
        )

    def run(self, repo_path: Path) -> Dict[str, Any]:
        """Execute the Vikunja task processing workflow for a single repository.

        Args:
            repo_path: Path to the repository directory

        Returns:
            Dictionary containing execution results and statistics
        """
        return self._worker.run(repo_path)
