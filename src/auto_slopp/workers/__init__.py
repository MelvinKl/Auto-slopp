"""Auto-slopp workers package.

This package contains all worker implementations organized by functionality:
- integration: External system integrations
"""

# Import all workers to make them available for discovery
from .openagent_worker import OpenAgentWorker

__all__ = [
    "OpenAgentWorker",
]
