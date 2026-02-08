"""Auto-slopp package."""

__version__ = "0.1.0"

from .discovery import discover_workers
from .executor import Executor, run_executor
from .worker import Worker
from .workers import (
    OpenAgentWorker,
)

__all__ = [
    "Worker",
    "discover_workers",
    "Executor",
    "run_executor",
    "OpenAgentWorker",
]
