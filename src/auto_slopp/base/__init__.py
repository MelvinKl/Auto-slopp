"""Base classes for auto-slopp workers.

This module contains abstract base classes and foundational components
that should be inherited by concrete worker implementations.
"""

from .openagent_worker import OpenAgentWorker

__all__ = ["OpenAgentWorker"]
