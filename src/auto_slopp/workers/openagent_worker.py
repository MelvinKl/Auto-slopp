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

from ...worker import Worker


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
    ):
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
                cmd, cwd=work_dir, capture_output=self.capture_output, text=True, timeout=self.timeout
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
                execution_result.update(
                    {
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "stdout_lines": result.stdout.splitlines() if result.stdout else [],
                        "stderr_lines": result.stderr.splitlines() if result.stderr else [],
                    }
                )

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
