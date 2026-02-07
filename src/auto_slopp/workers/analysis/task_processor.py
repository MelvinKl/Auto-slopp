"""Task processing worker that handles task files.

This worker processes task files and can perform various operations
like reading, parsing, and basic validation.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from ...worker import Worker


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