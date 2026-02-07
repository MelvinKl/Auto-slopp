"""Example Worker implementations for testing and demonstration."""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .worker import Worker


class SimpleLogger(Worker):
    """Simple logging worker that demonstrates basic functionality.

    This worker logs information about the repository and task paths
    and reports basic statistics.
    """

    def __init__(self, name: str = "SimpleLogger"):
        """Initialize the simple logger worker.

        Args:
            name: Name identifier for this worker instance.
        """
        self.name = name
        self.logger = logging.getLogger(f"auto_slopp.workers.{name}")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Log information about paths and return statistics.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing execution statistics and path info.
        """
        start_time = time.time()

        self.logger.info(f"{self.name} starting execution")
        self.logger.info(f"Repository path: {repo_path}")
        self.logger.info(f"Task path: {task_path}")

        # Check if paths exist
        repo_exists = repo_path.exists()
        task_exists = task_path.exists()

        self.logger.info(f"Repository exists: {repo_exists}")
        self.logger.info(f"Task path exists: {task_exists}")

        # Count files in repository if it exists
        file_count = 0
        if repo_exists and repo_path.is_dir():
            file_count = len(list(repo_path.rglob("*")))
            self.logger.info(f"Files in repository: {file_count}")

        execution_time = time.time() - start_time

        result = {
            "worker_name": self.name,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "repo_path": str(repo_path),
            "task_path": str(task_path),
            "repo_exists": repo_exists,
            "task_exists": task_exists,
            "file_count": file_count,
        }

        self.logger.info(f"{self.name} completed in {execution_time:.2f}s")
        return result


class FileMonitor(Worker):
    """File monitoring worker that tracks changes in the repository.

    This worker scans for files and reports basic statistics about
    different file types and sizes.
    """

    def __init__(self, file_patterns: Optional[List[str]] = None):
        """Initialize the file monitor worker.

        Args:
            file_patterns: List of file patterns to monitor (default: common code files).
        """
        self.file_patterns = file_patterns or ["*.py", "*.md", "*.txt", "*.json", "*.yaml", "*.yml"]
        self.logger = logging.getLogger("auto_slopp.workers.FileMonitor")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Scan repository and report file statistics.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing file statistics and analysis.
        """
        start_time = time.time()

        self.logger.info("FileMonitor scanning repository")

        if not repo_path.exists() or not repo_path.is_dir():
            return {"error": "Repository path does not exist or is not a directory", "repo_path": str(repo_path)}

        # Scan for files
        file_stats = {}
        total_files = 0
        total_size = 0

        for pattern in self.file_patterns:
            pattern_files = list(repo_path.rglob(pattern))
            pattern_count = len(pattern_files)
            pattern_size = sum(f.stat().st_size for f in pattern_files if f.is_file())

            file_stats[pattern] = {
                "count": pattern_count,
                "size_bytes": pattern_size,
                "size_mb": round(pattern_size / (1024 * 1024), 2),
            }

            total_files += pattern_count
            total_size += pattern_size

        execution_time = time.time() - start_time

        result = {
            "worker_name": "FileMonitor",
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "repo_path": str(repo_path),
            "monitored_patterns": self.file_patterns,
            "total_files_found": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_breakdown": file_stats,
        }

        self.logger.info(f"FileMonitor found {total_files} files totaling {result['total_size_mb']} MB")
        return result


class TaskProcessor(Worker):
    """Task processing worker that handles task files.

    This worker processes task files and can perform various operations
    like reading, parsing, and basic validation.
    """

    def __init__(self, max_file_size: int = 10 * 1024 * 1024):  # 10MB
        """Initialize the task processor worker.

        Args:
            max_file_size: Maximum file size to process in bytes.
        """
        self.max_file_size = max_file_size
        self.logger = logging.getLogger("auto_slopp.workers.TaskProcessor")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Process task files and report findings.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing task processing results.
        """
        start_time = time.time()

        self.logger.info(f"TaskProcessor processing: {task_path}")

        if not task_path.exists():
            return {"worker_name": "TaskProcessor", "error": "Task path does not exist", "task_path": str(task_path)}

        processed_tasks = []
        total_size = 0

        if task_path.is_file():
            # Process single file
            result = self._process_single_file(task_path)
            processed_tasks.append(result)
            if result.get("size_bytes", 0):
                total_size += result["size_bytes"]
        elif task_path.is_dir():
            # Process all files in directory
            for file_path in task_path.rglob("*"):
                if file_path.is_file():
                    result = self._process_single_file(file_path)
                    processed_tasks.append(result)
                    if result.get("size_bytes", 0):
                        total_size += result["size_bytes"]

        execution_time = time.time() - start_time

        result = {
            "worker_name": "TaskProcessor",
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "task_path": str(task_path),
            "total_files_processed": len(processed_tasks),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "processed_files": processed_tasks,
        }

        self.logger.info(f"TaskProcessor processed {len(processed_tasks)} files")
        return result

    def _process_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file and return metadata.

        Args:
            file_path: Path to the file to process.

        Returns:
            Dictionary with file metadata and content analysis.
        """
        try:
            stat = file_path.stat()
            size_bytes = stat.st_size

            # Skip if file is too large
            if size_bytes > self.max_file_size:
                return {
                    "file_path": str(file_path),
                    "error": f"File too large ({size_bytes} bytes > {self.max_file_size} bytes limit)",
                    "size_bytes": size_bytes,
                }

            # Determine file type
            file_type = file_path.suffix.lower()

            # Try to read content for small files
            content_preview = None
            line_count = None

            if size_bytes < 1024:  # Only read files smaller than 1KB for preview
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        line_count = len(content.splitlines())
                        content_preview = content[:200] + "..." if len(content) > 200 else content
                except UnicodeDecodeError:
                    content_preview = "[Binary file]"
            else:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        line_count = sum(1 for _ in f)
                except UnicodeDecodeError:
                    line_count = None

            return {
                "file_path": str(file_path),
                "file_type": file_type,
                "size_bytes": size_bytes,
                "size_kb": round(size_bytes / 1024, 2),
                "line_count": line_count,
                "content_preview": content_preview,
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }

        except Exception as e:
            return {"file_path": str(file_path), "error": f"Processing failed: {str(e)}"}


class HeartbeatWorker(Worker):
    """Heartbeat worker that demonstrates periodic execution.

    This worker simply sends a heartbeat message to show that
    the executor is running properly.
    """

    def __init__(self, message: str = "Auto-slopp is running"):
        """Initialize the heartbeat worker.

        Args:
            message: Custom heartbeat message.
        """
        self.message = message
        self.logger = logging.getLogger("auto_slopp.workers.Heartbeat")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Send a heartbeat message.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing heartbeat information.
        """
        timestamp = datetime.now().isoformat()

        heartbeat_msg = f"{self.message} at {timestamp}"
        self.logger.info(heartbeat_msg)

        return {
            "worker_name": "HeartbeatWorker",
            "message": self.message,
            "timestamp": timestamp,
            "repo_path": str(repo_path),
            "task_path": str(task_path),
        }
