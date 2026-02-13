"""Pre-commit hook worker for running pre-commit checks on repositories.

This worker runs pre-commit hooks on repositories to ensure code quality
and consistency by checking for issues like trailing whitespace, large files,
merge conflicts, and more.
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from auto_slopp.worker import Worker


class PreCommitWorker(Worker):
    """Worker for running pre-commit hooks on repositories.

    This worker executes pre-commit hooks on a repository to perform
    automated code quality checks including formatting, linting, and
    security scans.
    """

    def __init__(
        self,
        files: Optional[List[str]] = None,
        hook_ids: Optional[List[str]] = None,
        all_files: bool = False,
        show_diff_on_failure: bool = False,
    ):
        """Initialize the PreCommitWorker.

        Args:
            files: List of specific files to run hooks on (default: all staged files)
            hook_ids: List of specific hook IDs to run (e.g., 'trailing-whitespace', 'black')
            all_files: If True, run on all files instead of just staged files
            show_diff_on_failure: If True, show diff when hooks fail
        """
        self.files = files or []
        self.hook_ids = hook_ids or []
        self.all_files = all_files
        self.show_diff_on_failure = show_diff_on_failure
        self.logger = logging.getLogger("auto_slopp.workers.PreCommitWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute pre-commit hooks on the repository.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file (unused)

        Returns:
            Dictionary containing execution results and statistics
        """
        start_time = self._get_current_time()
        self.logger.info(f"PreCommitWorker starting with repo_path: {repo_path}")

        if not repo_path.exists():
            return self._create_error_result(
                start_time,
                repo_path,
                "Repository path does not exist",
            )

        pre_commit_config = repo_path / ".pre-commit-config.yaml"
        if not pre_commit_config.exists():
            return self._create_error_result(
                start_time,
                repo_path,
                "No .pre-commit-config.yaml found in repository",
            )

        result = self._run_pre_commit(repo_path)
        result["execution_time"] = self._get_elapsed_time(start_time)
        result["repo_path"] = str(repo_path)
        result["timestamp"] = start_time

        self._log_completion_summary(result)
        return result

    def _run_pre_commit(self, repo_path: Path) -> Dict[str, Any]:
        """Run pre-commit hooks on the repository.

        Args:
            repo_path: Path to the repository directory

        Returns:
            Dictionary containing execution results
        """
        cmd = ["pre-commit", "run"]

        if self.all_files:
            cmd.append("--all-files")
        elif self.files:
            cmd.extend(self.files)
        else:
            cmd.append("--staged")

        if self.hook_ids:
            cmd.extend(["--hooks", ",".join(self.hook_ids)])

        if self.show_diff_on_failure:
            cmd.append("--show-diff-on-failure")

        self.logger.info(f"Running pre-commit command: {' '.join(cmd)}")

        try:
            process = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=300,
            )

            return {
                "worker_name": "PreCommitWorker",
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "command": " ".join(cmd),
            }
        except subprocess.TimeoutExpired:
            return {
                "worker_name": "PreCommitWorker",
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": "Pre-commit hook timed out after 300 seconds",
                "command": " ".join(cmd),
                "error": "timeout",
            }
        except FileNotFoundError:
            return {
                "worker_name": "PreCommitWorker",
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": "pre-commit command not found. Is pre-commit installed?",
                "command": " ".join(cmd),
                "error": "pre-commit not found",
            }
        except Exception as e:
            return {
                "worker_name": "PreCommitWorker",
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "command": " ".join(cmd),
                "error": str(e),
            }

    def _create_error_result(self, start_time: float, repo_path: Path, error_msg: str) -> Dict[str, Any]:
        """Create an error result dictionary.

        Args:
            start_time: Start time of execution
            repo_path: Repository path
            error_msg: Error message

        Returns:
            Error result dictionary
        """
        return {
            "worker_name": "PreCommitWorker",
            "execution_time": self._get_elapsed_time(start_time),
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "success": False,
            "error": error_msg,
            "return_code": -1,
            "stdout": "",
            "stderr": error_msg,
        }

    def _log_completion_summary(self, result: Dict[str, Any]) -> None:
        """Log completion summary.

        Args:
            result: Results dictionary
        """
        status = "succeeded" if result["success"] else "failed"
        self.logger.info(
            f"PreCommitWorker {status}. "
            f"Repo: {result.get('repo_path', 'unknown')}, "
            f"Return code: {result.get('return_code', -1)}"
        )

    def _get_current_time(self) -> float:
        """Get current time as float for consistent timing.

        Returns:
            Current time as float
        """
        import time

        return time.time()

    def _get_elapsed_time(self, start_time: float) -> float:
        """Get elapsed time from start time.

        Args:
            start_time: Start time as float

        Returns:
            Elapsed time in seconds
        """
        import time

        return time.time() - start_time
