"""OpenAgent execution worker for running OpenAgent with specific arguments.

This worker executes OpenAgent commands with configurable arguments,
captures output, and provides execution status and results.
"""

import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from auto_slopp.worker import Worker


class OpenAgentWorker(Worker):
    """OpenAgent execution worker for running OpenAgent with specific arguments.

    This worker executes OpenAgent commands with configurable arguments,
    captures output, and provides execution status and results.
    """

    def __init__(
        self,
        agent_args: Optional[List[str]] = None,
        timeout: int = 300,
        capture_output: bool = True,
        working_dir: Optional[Path] = None,
        process_all_repos: bool = False,
    ):
        """Initialize the OpenAgent worker.

        Args:
            agent_args: List of arguments to pass to OpenAgent
            timeout: Command execution timeout in seconds
            capture_output: Whether to capture stdout/stderr
            working_dir: Working directory for command execution (defaults to repo_path)
            process_all_repos: Whether to run OpenAgent on all repositories in repo_path
        """
        self.agent_args = agent_args or []
        self.timeout = timeout
        self.capture_output = capture_output
        self.working_dir = working_dir
        self.process_all_repos = process_all_repos
        self.logger = logging.getLogger("auto_slopp.workers.OpenAgentWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute OpenAgent with the configured arguments.

        Args:
            repo_path: Path to the directory containing repository subdirectories
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing execution results and output.
        """
        start_time = time.time()

        self.logger.info(f"OpenAgentWorker executing with args: {self.agent_args}")

        if not repo_path.exists():
            return {
                "worker_name": "OpenAgentWorker",
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

        if self.process_all_repos:
            return self._run_on_all_repositories(repo_path, task_path, start_time)
        else:
            return self._run_on_single_repository(repo_path, task_path, start_time)

    def _run_on_all_repositories(
        self, repo_path: Path, task_path: Path, start_time: float
    ) -> Dict[str, Any]:
        """Run OpenAgent on all repositories in repo_path.

        Args:
            repo_path: Path to the directory containing repository subdirectories
            task_path: Path to the task directory or file
            start_time: Start time for execution tracking

        Returns:
            Dictionary containing execution results for all repositories.
        """
        results = {
            "worker_name": "OpenAgentWorker",
            "execution_time": 0,
            "timestamp": datetime.now().isoformat(),
            "repo_path": str(repo_path),
            "task_path": str(task_path),
            "process_all_repos": True,
            "repositories_processed": 0,
            "repositories_with_errors": 0,
            "repository_results": [],
            "success": True,
        }

        # Process all subdirectories in repo_path
        for repo_dir in repo_path.iterdir():
            if not repo_dir.is_dir():
                continue

            self.logger.info(f"Processing repository: {repo_dir.name}")
            results["repositories_processed"] += 1

            repo_result = self._execute_openagent(repo_dir, task_path)
            results["repository_results"].append(repo_result)

            if not repo_result["success"]:
                results["repositories_with_errors"] += 1
                results["success"] = False

        # Update final execution time
        results["execution_time"] = time.time() - start_time

        self.logger.info(
            f"OpenAgentWorker completed. Processed: {results['repositories_processed']}, "
            f"Errors: {results['repositories_with_errors']}"
        )

        return results

    def _run_on_single_repository(
        self, repo_path: Path, task_path: Path, start_time: float
    ) -> Dict[str, Any]:
        """Run OpenAgent on a single repository (repo_path is the repository).

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file
            start_time: Start time for execution tracking

        Returns:
            Dictionary containing execution results for the single repository.
        """
        return self._execute_openagent(repo_path, task_path)

    def _execute_openagent(self, work_dir: Path, task_path: Path) -> Dict[str, Any]:
        """Execute OpenAgent command in the specified working directory.

        Args:
            work_dir: Working directory for command execution
            task_path: Path to the task directory or file

        Returns:
            Dictionary containing execution results.
        """
        start_time = time.time()

        # Determine working directory
        working_dir = self.working_dir or work_dir

        # Build command
        cmd = ["openagent"] + self.agent_args

        # Add task path to arguments if provided
        if task_path and task_path.exists():
            cmd.extend([str(task_path)])

        try:
            # Execute the command
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=self.capture_output,
                text=True,
                timeout=self.timeout,
            )

            execution_time = time.time() - start_time

            # Prepare result
            execution_result = {
                "worker_name": "OpenAgentWorker",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "working_directory": str(working_dir),
                "command": " ".join(cmd),
                "return_code": result.returncode,
                "success": result.returncode == 0,
                "timeout": False,
            }

            # Add output if captured
            if self.capture_output:
                execution_result.update(
                    {
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "stdout_lines": result.stdout.splitlines()
                        if result.stdout
                        else [],
                        "stderr_lines": result.stderr.splitlines()
                        if result.stderr
                        else [],
                    }
                )

            self.logger.info(
                f"OpenAgentWorker completed in {execution_time:.2f}s with return code {result.returncode}"
            )
            return execution_result

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            self.logger.error(f"OpenAgentWorker timed out after {self.timeout}s")

            return {
                "worker_name": "OpenAgentWorker",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "working_directory": str(working_dir),
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
                "working_directory": str(working_dir),
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
                "working_directory": str(working_dir),
                "command": " ".join(cmd),
                "return_code": -1,
                "success": False,
                "timeout": False,
                "error": f"Unexpected error: {str(e)}",
            }
