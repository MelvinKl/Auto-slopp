"""Example Worker implementations for testing and demonstration."""

import json
import logging
import subprocess
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
            return {"worker_name": "DirectoryScanner", "error": "Repository path does not exist", "repo_path": str(repo_path)}

        if not repo_path.is_dir():
            return {"worker_name": "DirectoryScanner", "error": "Repository path is not a directory", "repo_path": str(repo_path)}

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
            **scan_results
        }

        self.logger.info(f"DirectoryScanner completed in {execution_time:.2f}s, found {result['total_directories']} directories and {result['total_files']} files")
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


class BeadsTaskWorker(Worker):
    """Beads task detection and management worker.

    This worker integrates with the beads task management system to
    detect available tasks, check ready states, and provide task
    management capabilities.
    """

    def __init__(self, include_in_progress: bool = False, priority_filter: Optional[int] = None):
        """Initialize the beads task worker.

        Args:
            include_in_progress: Whether to include tasks already in progress
            priority_filter: Filter tasks by priority (0-4, None for all)
        """
        self.include_in_progress = include_in_progress
        self.priority_filter = priority_filter
        self.logger = logging.getLogger("auto_slopp.workers.BeadsTaskWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Detect and analyze beads tasks in the repository.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file (not used in this worker)

        Returns:
            Dictionary containing beads task analysis and ready state information.
        """
        start_time = time.time()

        self.logger.info("BeadsTaskWorker detecting and analyzing beads tasks")

        # Check if beads is available in this repository
        beads_available = self._check_beads_availability(repo_path)

        if not beads_available:
            return {
                "worker_name": "BeadsTaskWorker",
                "error": "Beads task management system not available in this repository",
                "repo_path": str(repo_path),
                "execution_time": time.time() - start_time,
            }

        # Get ready tasks
        ready_tasks = self._get_ready_tasks()
        
        # Get all open tasks for analysis
        all_open_tasks = self._get_open_tasks()

        # Analyze task states and dependencies
        task_analysis = self._analyze_tasks(all_open_tasks, ready_tasks)

        execution_time = time.time() - start_time

        result = {
            "worker_name": "BeadsTaskWorker",
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "repo_path": str(repo_path),
            "beads_available": True,
            "ready_tasks_count": len(ready_tasks),
            "total_open_tasks": len(all_open_tasks),
            "ready_tasks": ready_tasks,
            "task_analysis": task_analysis,
        }

        self.logger.info(f"BeadsTaskWorker found {len(ready_tasks)} ready tasks out of {len(all_open_tasks)} total open tasks")
        return result

    def _check_beads_availability(self, repo_path: Path) -> bool:
        """Check if beads task management is available.

        Args:
            repo_path: Repository path to check

        Returns:
            True if beads is available, False otherwise.
        """
        try:
            # Try to run a simple beads command to check availability
            import subprocess
            result = subprocess.run(
                ["bd", "--help"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return False

    def _get_ready_tasks(self) -> List[Dict[str, Any]]:
        """Get list of ready tasks from beads.

        Returns:
            List of ready task dictionaries.
        """
        try:
            result = subprocess.run(
                ["bd", "ready", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                tasks = json.loads(result.stdout)
                
                # Apply filters
                filtered_tasks = []
                for task in tasks:
                    # Skip in-progress tasks if not included
                    if not self.include_in_progress and task.get("status") == "in_progress":
                        continue
                    
                    # Apply priority filter
                    if self.priority_filter is not None:
                        task_priority = task.get("priority", 2)
                        if task_priority != self.priority_filter:
                            continue
                    
                    filtered_tasks.append(task)
                
                return filtered_tasks
            else:
                self.logger.error(f"bd ready command failed: {result.stderr}")
                return []
                
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Error getting ready tasks: {str(e)}")
            return []

    def _get_open_tasks(self) -> List[Dict[str, Any]]:
        """Get list of all open tasks from beads.

        Returns:
            List of all open task dictionaries.
        """
        try:
            result = subprocess.run(
                ["bd", "list", "--status", "open", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                self.logger.error(f"bd list command failed: {result.stderr}")
                return []
                
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Error getting open tasks: {str(e)}")
            return []

    def _analyze_tasks(self, all_tasks: List[Dict[str, Any]], ready_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze tasks and provide insights.

        Args:
            all_tasks: List of all open tasks
            ready_tasks: List of ready tasks

        Returns:
            Dictionary containing task analysis.
        """
        # Count tasks by status
        status_counts = {}
        priority_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        type_counts = {}
        
        for task in all_tasks:
            # Count by status
            status = task.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by priority
            priority = task.get("priority", 2)
            if 0 <= priority <= 4:
                priority_counts[priority] += 1
            
            # Count by type
            task_type = task.get("issue_type", "unknown")
            type_counts[task_type] = type_counts.get(task_type, 0) + 1
        
        # Calculate readiness percentage
        ready_percentage = (len(ready_tasks) / len(all_tasks) * 100) if all_tasks else 0
        
        # Find high priority ready tasks
        high_priority_ready = [task for task in ready_tasks if task.get("priority", 2) <= 1]
        
        return {
            "status_breakdown": status_counts,
            "priority_breakdown": priority_counts,
            "type_breakdown": type_counts,
            "readiness_percentage": round(ready_percentage, 2),
            "high_priority_ready_count": len(high_priority_ready),
            "high_priority_ready_tasks": high_priority_ready,
            "blocked_tasks": status_counts.get("blocked", 0),
            "in_progress_tasks": status_counts.get("in_progress", 0),
        }


class OpenAgentWorker(Worker):
    """OpenAgent execution worker for running OpenAgent with specific arguments.

    This worker executes OpenAgent commands with configurable arguments,
    captures output, and provides execution status and results.
    """

    def __init__(self, 
                 agent_args: Optional[List[str]] = None,
                 timeout: int = 300,
                 capture_output: bool = True,
                 working_dir: Optional[Path] = None):
        """Initialize the OpenAgent worker.

        Args:
            agent_args: List of arguments to pass to OpenAgent
            timeout: Command execution timeout in seconds
            capture_output: Whether to capture stdout/stderr
            working_dir: Working directory for command execution (defaults to repo_path)
        """
        self.agent_args = agent_args or []
        self.timeout = timeout
        self.capture_output = capture_output
        self.working_dir = working_dir
        self.logger = logging.getLogger("auto_slopp.workers.OpenAgentWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute OpenAgent with the configured arguments.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing execution results and output.
        """
        start_time = time.time()

        self.logger.info(f"OpenAgentWorker executing with args: {self.agent_args}")

        # Determine working directory
        work_dir = self.working_dir or repo_path
        
        # Build command
        cmd = ["openagent"] + self.agent_args
        
        # Add task path to arguments if provided
        if task_path and task_path.exists():
            cmd.extend([str(task_path)])

        try:
            # Execute the command
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=self.capture_output,
                text=True,
                timeout=self.timeout
            )

            execution_time = time.time() - start_time

            # Prepare result
            execution_result = {
                "worker_name": "OpenAgentWorker",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "repo_path": str(repo_path),
                "task_path": str(task_path),
                "working_directory": str(work_dir),
                "command": " ".join(cmd),
                "return_code": result.returncode,
                "success": result.returncode == 0,
                "timeout": False,
            }

            # Add output if captured
            if self.capture_output:
                execution_result.update({
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "stdout_lines": result.stdout.splitlines() if result.stdout else [],
                    "stderr_lines": result.stderr.splitlines() if result.stderr else [],
                })

            self.logger.info(f"OpenAgentWorker completed in {execution_time:.2f}s with return code {result.returncode}")
            return execution_result

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            self.logger.error(f"OpenAgentWorker timed out after {self.timeout}s")
            
            return {
                "worker_name": "OpenAgentWorker",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "repo_path": str(repo_path),
                "task_path": str(task_path),
                "working_directory": str(work_dir),
                "command": " ".join(cmd),
                "return_code": -1,
                "success": False,
                "timeout": True,
                "error": f"Command timed out after {self.timeout} seconds",
            }

        except FileNotFoundError:
            execution_time = time.time() - start_time
            self.logger.error("OpenAgent command not found")
            
            return {
                "worker_name": "OpenAgentWorker",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "repo_path": str(repo_path),
                "task_path": str(task_path),
                "working_directory": str(work_dir),
                "command": " ".join(cmd),
                "return_code": -1,
                "success": False,
                "timeout": False,
                "error": "OpenAgent command not found - is it installed and in PATH?",
            }

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"OpenAgentWorker failed with error: {str(e)}")
            
            return {
                "worker_name": "OpenAgentWorker",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "repo_path": str(repo_path),
                "task_path": str(task_path),
                "working_directory": str(work_dir),
                "command": " ".join(cmd),
                "return_code": -1,
                "success": False,
                "timeout": False,
                "error": f"Unexpected error: {str(e)}",
            }


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
