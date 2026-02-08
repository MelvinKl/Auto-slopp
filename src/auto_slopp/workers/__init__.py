"""Auto-slopp workers package.

This package contains all worker implementations organized by functionality:
- integration: External system integrations
"""

# Import all workers to make them available for discovery
from .openagent_worker import OpenAgentWorker
from .renovate_test_worker import RenovateTestWorker
from .stale_branch_cleanup_worker import StaleBranchCleanupWorker

__all__ = [
    "OpenAgentWorker",
    "RenovateTestWorker",
    "StaleBranchCleanupWorker",
]
