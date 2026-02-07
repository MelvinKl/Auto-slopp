"""File monitoring worker that tracks changes in the repository.

This worker scans for files and reports basic statistics about
different file types and sizes.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...worker import Worker


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