"""Auto-slopp package."""

__version__ = "0.1.0"

from auto_slopp.discovery import discover_workers
from auto_slopp.executor import Executor, run_executor
from auto_slopp.worker import Worker
from auto_slopp.workers import (
    RenovateTestWorker,
    StaleBranchCleanupWorker,
)
from auto_slopp.plugin_manager import PluginManager

__all__ = [
    "Worker",
    "discover_workers",
    "PluginManager",
    "Executor",
    "run_executor",
    "RenovateTestWorker",
    "StaleBranchCleanupWorker",
    "TestFixWorker",
]
