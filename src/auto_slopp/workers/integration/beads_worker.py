"""Beads task detection and management worker.

This worker integrates with the beads task management system to
detect available tasks, check ready states, and provide task
management capabilities.
"""

import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...worker import Worker


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

        self.logger.info(
            f"BeadsTaskWorker found {len(ready_tasks)} ready tasks out of {len(all_open_tasks)} total open tasks"
        )
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
            result = subprocess.run(["bd", "--help"], cwd=repo_path, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except subprocess.TimeoutExpired, FileNotFoundError, Exception:
            return False

    def _get_ready_tasks(self) -> List[Dict[str, Any]]:
        """Get list of ready tasks from beads.

        Returns:
            List of ready task dictionaries.
        """
        try:
            result = subprocess.run(["bd", "ready", "--json"], capture_output=True, text=True, timeout=30)

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
                ["bd", "list", "--status", "open", "--json"], capture_output=True, text=True, timeout=30
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