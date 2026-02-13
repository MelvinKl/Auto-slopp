"""AutoCommand worker for automatically running commands on repositories.

This worker executes specified shell commands on repository directories,
allowing for automated command execution across multiple repositories.
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from auto_slopp.worker import Worker


class AutoCommandWorker(Worker):
    """Worker that automatically runs specified commands on repositories.

    This worker executes a configured command in each repository directory,
    making it useful for running tests, builds, or other automated tasks.
    """

    def __init__(
        self,
        command: str = "echo 'No command configured'",
        shell: bool = True,
        capture_output: bool = True,
        timeout: Optional[int] = None,
    ):
        """Initialize the AutoCommandWorker.

        Args:
            command: Shell command to execute in each repository
            shell: Whether to run command through shell
            capture_output: Whether to capture stdout/stderr
            timeout: Optional timeout in seconds for command execution
        """
        self.command = command
        self.shell = shell
        self.capture_output = capture_output
        self.timeout = timeout
        self.logger = logging.getLogger("auto_slopp.workers.AutoCommandWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute the configured command on the repository.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file (unused)

        Returns:
            Dictionary containing execution results
        """
        if not repo_path.exists():
            return {
                "worker_name": "AutoCommandWorker",
                "success": False,
                "error": f"Repository path does not exist: {repo_path}",
                "command": self.command,
                "repo_path": str(repo_path),
            }

        self.logger.info(f"Executing command on {repo_path}: {self.command}")

        try:
            result = subprocess.run(
                self.command,
                shell=self.shell,
                cwd=str(repo_path),
                capture_output=self.capture_output,
                text=True,
                timeout=self.timeout,
            )

            return {
                "worker_name": "AutoCommandWorker",
                "success": result.returncode == 0,
                "command": self.command,
                "repo_path": str(repo_path),
                "returncode": result.returncode,
                "stdout": result.stdout if self.capture_output else None,
                "stderr": result.stderr if self.capture_output else None,
            }

        except subprocess.TimeoutExpired as e:
            self.logger.error(f"Command timed out on {repo_path}: {e}")
            return {
                "worker_name": "AutoCommandWorker",
                "success": False,
                "error": "Command timed out",
                "command": self.command,
                "repo_path": str(repo_path),
            }

        except Exception as e:
            self.logger.error(f"Error executing command on {repo_path}: {e}")
            return {
                "worker_name": "AutoCommandWorker",
                "success": False,
                "error": str(e),
                "command": self.command,
                "repo_path": str(repo_path),
            }
