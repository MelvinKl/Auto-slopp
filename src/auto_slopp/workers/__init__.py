"""Auto-slopp workers package.

This package contains all worker implementations organized by functionality:
- integration: External system integrations
"""

from auto_slopp.workers.github_issue_worker import GitHubIssueWorker
from auto_slopp.workers.openproject_worker import OpenProjectWorker
from auto_slopp.workers.pr_worker import PRWorker
from auto_slopp.workers.stale_branch_cleanup_worker import StaleBranchCleanupWorker

__all__ = [
    "GitHubIssueWorker",
    "OpenProjectWorker",
    "PRWorker",
    "StaleBranchCleanupWorker",
]
