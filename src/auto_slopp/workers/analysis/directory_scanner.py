"""Directory scanning worker that analyzes repository structure.

This worker performs comprehensive directory scanning on repo_path,
analyzing directory structure, file types, and providing detailed
repository metadata.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...worker import Worker


class DirectoryScanner(Worker):
    """Directory scanning worker that analyzes repository structure.

    This worker performs comprehensive directory scanning on repo_path,
    analyzing directory structure, file types, and providing detailed
    repository metadata.
    """

    def __init__(self, include_hidden: bool = False, max_depth: Optional[int] = None):
        """Initialize the directory scanner worker.

        Args:
            include_hidden: Whether to include hidden files/directories (.git, .vscode, etc.)
            max_depth: Maximum directory depth to scan (None for unlimited).
        """
        self.include_hidden = include_hidden
        self.max_depth = max_depth
        self.logger = logging.getLogger("auto_slopp.workers.DirectoryScanner")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Scan repository directory and analyze structure.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file (not used in this worker)

        Returns:
            Dictionary containing comprehensive directory analysis.
        """
        start_time = time.time()

        self.logger.info(f"DirectoryScanner scanning repository: {repo_path}")

        if not repo_path.exists():
            return {
                "worker_name": "DirectoryScanner",
                "error": "Repository path does not exist",
                "repo_path": str(repo_path),
            }

        if not repo_path.is_dir():
            return {
                "worker_name": "DirectoryScanner",
                "error": "Repository path is not a directory",
                "repo_path": str(repo_path),
            }

        # Perform directory scanning
        scan_results = self._scan_directory(repo_path)

        execution_time = time.time() - start_time

        result = {
            "worker_name": "DirectoryScanner",
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "repo_path": str(repo_path),
            "scan_config": {
                "include_hidden": self.include_hidden,
                "max_depth": self.max_depth,
            },
            **scan_results,
        }

        self.logger.info(
            f"DirectoryScanner completed in {execution_time:.2f}s, found {result['total_directories']} directories and {result['total_files']} files"
        )
        return result

    def _scan_directory(self, root_path: Path) -> Dict[str, Any]:
        """Perform the actual directory scanning.

        Args:
            root_path: Root directory to scan

        Returns:
            Dictionary containing scan results.
        """
        directories = []
        files = []
        file_types = {}
        total_size = 0

        # Scan the directory structure
        for item in root_path.rglob("*"):
            # Skip hidden items if not included
            if not self.include_hidden and item.name.startswith("."):
                continue

            # Check depth limit
            if self.max_depth is not None:
                relative_path = item.relative_to(root_path)
                depth = len(relative_path.parts) - 1
                if depth > self.max_depth:
                    continue

            if item.is_dir():
                directories.append(str(item.relative_to(root_path)))
            elif item.is_file():
                file_info = {
                    "path": str(item.relative_to(root_path)),
                    "size_bytes": item.stat().st_size,
                    "size_kb": round(item.stat().st_size / 1024, 2),
                    "extension": item.suffix.lower(),
                    "modified_time": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                }
                files.append(file_info)
                total_size += item.stat().st_size

                # Track file types
                ext = item.suffix.lower()
                if ext:
                    file_types[ext] = file_types.get(ext, 0) + 1
                else:
                    file_types["(no extension)"] = file_types.get("(no extension)", 0) + 1

        # Analyze directory structure
        directory_analysis = self._analyze_directory_structure(directories, root_path)

        return {
            "total_directories": len(directories),
            "total_files": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)),
            "directories": directories,
            "files": files,
            "directory_analysis": directory_analysis,
        }

    def _analyze_directory_structure(self, directories: List[str], root_path: Path) -> Dict[str, Any]:
        """Analyze directory structure and provide insights.

        Args:
            directories: List of directory paths relative to root
            root_path: Root directory path

        Returns:
            Dictionary containing directory structure analysis.
        """
        if not directories:
            return {"max_depth": 0, "avg_depth": 0, "root_subdirs": 0}

        # Calculate directory depths
        depths = [len(dir_path.split("/")) for dir_path in directories]
        max_depth = max(depths)
        avg_depth = sum(depths) / len(depths)

        # Count immediate subdirectories of root
        root_subdirs = len([d for d in directories if "/" not in d])

        # Look for common directory patterns
        common_dirs = {}
        for dir_path in directories:
            parts = dir_path.split("/")
            for part in parts:
                if part in ["src", "tests", "docs", "lib", "bin", "config", "scripts", "examples"]:
                    common_dirs[part] = common_dirs.get(part, 0) + 1

        return {
            "max_depth": max_depth,
            "avg_depth": round(avg_depth, 2),
            "root_subdirs": root_subdirs,
            "common_directories": dict(sorted(common_dirs.items(), key=lambda x: x[1], reverse=True)),
        }