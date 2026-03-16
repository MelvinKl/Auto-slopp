"""Auto-slopp package."""

__version__ = "0.1.0"

from auto_slopp.executor import Executor, run_executor
from auto_slopp.worker import Worker
from auto_slopp.workers import StaleBranchCleanupWorker

__all__ = [
    "Worker",
    "Executor",
    "run_executor",
    "StaleBranchCleanupWorker",
    "TestFixWorker",
]
