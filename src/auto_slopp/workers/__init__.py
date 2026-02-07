"""Auto-slopp workers package.

This package contains all worker implementations organized by functionality:
- core: Basic utility workers
- analysis: Analysis and inspection workers  
- integration: External system integrations
"""

# Import all workers to make them available for discovery
from .core.heartbeat import HeartbeatWorker
from .core.file_monitor import FileMonitor
from .core.simple_logger import SimpleLogger
from .analysis.directory_scanner import DirectoryScanner
from .analysis.task_processor import TaskProcessor
from .integration.beads_worker import BeadsTaskWorker
from .integration.openagent_worker import OpenAgentWorker

__all__ = [
    "HeartbeatWorker",
    "FileMonitor", 
    "SimpleLogger",
    "DirectoryScanner",
    "TaskProcessor",
    "BeadsTaskWorker",
    "OpenAgentWorker",
]