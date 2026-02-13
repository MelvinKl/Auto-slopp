"""Auto-slopp workers package.

This package contains all worker implementations organized by functionality:
- integration: External system integrations
"""

# Import all workers to make them available for discovery
from auto_slopp.workers.pr_worker import PRWorker
from auto_slopp.workers.stale_branch_cleanup_worker import StaleBranchCleanupWorker
from auto_slopp.workers.task_processor_worker import TaskProcessorWorker
from auto_slopp.workers.update_pr_branches_worker import UpdatePRBranchesWorker

__all__ = [
    "PRWorker",
    "StaleBranchCleanupWorker",
    "TaskProcessorWorker",
    "UpdatePRBranchesWorker",
]
