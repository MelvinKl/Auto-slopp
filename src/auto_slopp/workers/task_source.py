"""TaskSource base class for abstracting task/issue loading.

Provides a common interface for loading tasks from different sources
(e.g., GitHub Issues, Vikunja) so that a unified IssueWorker can
process them identically regardless of origin.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class Task:
    """Normalized task representation from any source."""

    id: int  # noqa: A003
    title: str
    body: str
    comments: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)


class TaskSource(ABC):
    """Abstract base class for loading tasks from different sources.

    Implementations provide source-specific logic for fetching tasks,
    generating branch names, and handling task lifecycle events
    (start, complete, failure, no changes).
    """

    @abstractmethod
    def get_tasks(self, repo_path: Path) -> List[Task]:
        """Fetch and filter tasks from the source.

        Args:
            repo_path: Path to the repository directory

        Returns:
            List of normalized Task objects ready for processing
        """

    @abstractmethod
    def get_branch_name(self, task: Task) -> str:
        """Generate the branch name for a task.

        Args:
            task: The task to generate a branch name for

        Returns:
            Branch name string (e.g., 'ai/issue-42-fix-bug')
        """

    @abstractmethod
    def get_ralph_file_prefix(self) -> str:
        """Return the prefix for ralph task files.

        Returns:
            Prefix string (e.g., 'github' or 'vikunja')
        """

    @abstractmethod
    def get_default_pr_body(self, task: Task) -> str:
        """Generate the default PR body for a task.

        Args:
            task: The task to generate a PR body for

        Returns:
            PR body string in markdown
        """

    @abstractmethod
    def on_task_start(self, task: Task, branch_name: str) -> None:
        """Called when task processing begins.

        Args:
            task: The task being started
            branch_name: The branch created for this task
        """

    @abstractmethod
    def on_task_complete(self, task: Task, branch_name: str, pr_url: str) -> None:
        """Called when a task completes successfully.

        Args:
            task: The completed task
            branch_name: The branch used for this task
            pr_url: URL of the created pull request
        """

    @abstractmethod
    def on_task_failure(self, task: Task, error: str) -> None:
        """Called when a task fails.

        Args:
            task: The failed task
            error: Error description
        """

    @abstractmethod
    def on_no_changes(self, task: Task) -> None:
        """Called when no changes were needed for a task.

        Args:
            task: The task that required no changes
        """

    @abstractmethod
    def on_max_iterations_reached(self, task: Task, steps_completed: int, total_steps: int, error: str) -> None:
        """Called when the ralph loop reaches max iterations without completing.

        Args:
            task: The task that hit the iteration limit
            steps_completed: Number of steps completed
            total_steps: Total number of steps
            error: Last error message
        """
