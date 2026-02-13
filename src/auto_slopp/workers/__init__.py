"""Auto-slopp workers package.

This package contains all worker implementations organized by functionality:
- integration: External system integrations
"""

# Import all workers to make them available for discovery
from auto_slopp.workers.http11_worker import HTTP11Worker
from auto_slopp.workers.renovate_test_worker import RenovateTestWorker
from auto_slopp.workers.stale_branch_cleanup_worker import StaleBranchCleanupWorker
from auto_slopp.workers.task_processor_worker import TaskProcessorWorker

__all__ = [
    "HTTP11Worker",
    "RenovateTestWorker",
    "StaleBranchCleanupWorker",
    "TaskProcessorWorker",
]
