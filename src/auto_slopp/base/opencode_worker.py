"""OpenCode execution base class for running OpenCode with specific arguments.

This abstract base class provides the foundation for executing OpenCode commands
with configurable arguments, capturing output, and providing execution status
and results. It should be inherited by concrete worker implementations.
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from auto_slopp.utils.opencode import run_opencode
from auto_slopp.worker import Worker


class OpenCodeWorker(Worker, ABC):
    """OpenCode execution worker for running OpenCode with specific arguments.

    This worker executes OpenCode commands with configurable arguments,
    captures output, and provides execution status and results.
    """

    def __init__(
        self,
        agent_args: Optional[List[str]] = None,
        timeout: int = 7200,
        capture_output: bool = True,
        working_dir: Optional[Path] = None,
        process_all_repos: bool = False,
    ):
        """Initialize the OpenCode worker.

        Args:
            agent_args: List of arguments to pass to OpenCode
            timeout: Command execution timeout in seconds
            capture_output: Whether to capture stdout/stderr
            working_dir: Working directory for command execution (defaults to repo_path)
            process_all_repos: Whether to run OpenCode on all repositories in repo_path
        """
        self.agent_args = agent_args or []
        self.timeout = timeout
        self.capture_output = capture_output
        self.working_dir = working_dir
        self.process_all_repos = process_all_repos
        self.logger = logging.getLogger("auto_slopp.base.OpenCodeWorker")

    @abstractmethod
    def get_agent_instructions(self) -> str:
        """Get the specific instructions for this OpenCode worker.

        This method must be implemented by concrete subclasses to provide
        the specific instructions or context for the OpenCode execution.

        Returns:
            String containing the specific instructions for this worker.
        """
        pass

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute OpenCode with the configured arguments.

        Args:
            repo_path: Path to the directory containing repository subdirectories
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing execution results and output.
        """
        start_time = time.time()

        self.logger.info(f"OpenCodeWorker executing with args: {self.agent_args}")

        if not repo_path.exists():
            return {
                "worker_name": "OpenCodeWorker",
                "execution_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
                "repo_path": str(repo_path),
                "task_path": str(task_path),
                "success": False,
                "error": f"Repository path does not exist: {repo_path}",
                "repositories_processed": 0,
                "repositories_with_errors": 0,
                "repository_results": [],
            }

        # Always run on single repository now - orchestrator handles iteration
        return self._run_on_single_repository(repo_path, task_path, start_time)

    def _run_on_single_repository(self, repo_path: Path, task_path: Path, start_time: float) -> Dict[str, Any]:
        """Run OpenCode on a single repository (repo_path is the repository).

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file
            start_time: Start time for execution tracking

        Returns:
            Dictionary containing execution results for the single repository.
        """
        return self._execute_opencode(repo_path, task_path)

    def _execute_opencode(self, work_dir: Path, task_path: Path) -> Dict[str, Any]:
        """Execute OpenCode command in the specified working directory.

        Args:
            work_dir: Working directory for command execution
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing execution results.
        """
        # Determine working directory
        working_dir = self.working_dir or work_dir

        # Prepare additional instructions from task path if provided
        additional_instructions = None
        if task_path and task_path.exists():
            additional_instructions = str(task_path)

        # Use the centralized opencode utility
        result = run_opencode(
            additional_instructions=additional_instructions,
            working_directory=working_dir,
            timeout=self.timeout,
            agent_args=self.agent_args,
            capture_output=self.capture_output,
        )

        # Add worker name to result for consistency
        result["worker_name"] = "OpenCodeWorker"

        return result
