"""Auto-slopp workers package.

This package contains all worker implementations organized by functionality:
- integration: External system integrations
"""

# Import all workers to make them available for discovery
from auto_slopp.workers.renovate_test_worker import RenovateTestWorker
from auto_slopp.workers.stale_branch_cleanup_worker import StaleBranchCleanupWorker
from auto_slopp.workers.test_fix_worker import TestFixWorker

__all__ = [
    "RenovateTestWorker",
    "StaleBranchCleanupWorker",
    "TestFixWorker",
]
