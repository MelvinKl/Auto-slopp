"""Auto-slopp workers package.

This package contains all worker implementations organized by functionality:
- integration: External system integrations
"""

from auto_slopp.workers.github_issue_worker import GitHubIssueWorker
from auto_slopp.workers.github_task_source import GitHubTaskSource
from auto_slopp.workers.pr_worker import PRWorker
from auto_slopp.workers.stale_branch_cleanup_worker import StaleBranchCleanupWorker
from auto_slopp.workers.task_source import Task, TaskSource
from auto_slopp.workers.vikunja_worker import VikunjaWorker

__all__ = [
    "GitHubIssueWorker",
    "GitHubTaskSource",
    "PRWorker",
    "StaleBranchCleanupWorker",
    "Task",
    "TaskSource",
    "VikunjaWorker",
]
