"""PR Test Worker for auto-slopp automation system.

This worker merges origin/main into the current PR branch, pushes changes,
runs tests, and only pushes if all tests are successful.
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict

from auto_slopp.utils.git_operations import checkout_branch_resilient
from auto_slopp.utils.repository_utils import validate_repository
from auto_slopp.worker import Worker


class PRTestWorker(Worker):
    """Worker for testing PR branches with latest main merged in."""

    def __init__(self, timeout: int = 600):
        """Initialize PRTestWorker.

        Args:
            timeout: Timeout for test execution in seconds
        """
        self.timeout = timeout
        self.logger = logging.getLogger("auto_slopp.workers.PRTestWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute PR test workflow for a single repository.

        Args:
            repo_path: Path to a single repository directory
            task_path: Path to task directory or file (not used in this worker)

        Returns:
            Dictionary containing execution results and summary.
        """
        self.logger.info(f"PRTestWorker starting for {repo_path}")

        if not repo_path.exists():
            return {
                "worker_name": "PRTestWorker",
                "success": False,
                "error": f"Repository path does not exist: {repo_path}",
            }

        repo_info = validate_repository(repo_path)

        if not repo_info.get("valid", False):
            return {
                "worker_name": "PRTestWorker",
                "success": False,
                "error": f"Invalid repository: {repo_info.get('errors', ['Unknown error'])}",
            }

        result = self._process_repository(repo_path)
        return {
            "worker_name": "PRTestWorker",
            "success": result["success"],
            "branch": result.get("branch"),
            "merged_main": result.get("merged_main", False),
            "pushed_before_test": result.get("pushed_before_test", False),
            "test_success": result.get("test_success", False),
            "pushed_after_test": result.get("pushed_after_test", False),
            "error": result.get("error"),
        }

    def _process_repository(self, repo_dir: Path) -> Dict[str, Any]:
        """Process a single repository directory.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Dictionary containing processing results.
        """
        result = {
            "success": False,
            "branch": None,
            "merged_main": False,
            "pushed_before_test": False,
            "test_success": False,
            "pushed_after_test": False,
            "error": None,
        }

        try:
            current_branch = self._get_current_branch(repo_dir)
            if not current_branch:
                result["error"] = "Could not determine current branch"
                return result

            result["branch"] = current_branch
            self.logger.info(f"Processing branch {current_branch} in {repo_dir.name}")

            if not self._merge_main(repo_dir):
                result["error"] = "Failed to merge origin/main into branch"
                return result

            result["merged_main"] = True
            self.logger.info(f"Successfully merged origin/main into {current_branch}")

            if not self._push_branch(repo_dir, current_branch):
                result["error"] = "Failed to push branch before tests"
                return result

            result["pushed_before_test"] = True
            self.logger.info(f"Pushed branch {current_branch} before running tests")

            test_result = self._run_tests(repo_dir)
            result["test_success"] = test_result["success"]

            if test_result["success"]:
                if self._push_branch(repo_dir, current_branch):
                    result["pushed_after_test"] = True
                    self.logger.info(f"Tests passed, pushed branch {current_branch}")
                else:
                    result["error"] = "Tests passed but failed to push after tests"
                    return result
            else:
                self.logger.warning(f"Tests failed for {current_branch}, not pushing after test")
                result["error"] = f"Tests failed: {test_result.get('error', 'Unknown error')}"
                return result

            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error processing repository {repo_dir.name}: {str(e)}")
            result["error"] = str(e)

        return result

    def _get_current_branch(self, repo_dir: Path) -> str:
        """Get the current branch name.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Current branch name or None if not on a branch
        """
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                self.logger.error(f"Failed to get current branch: {result.stderr}")
                return None

            branch = result.stdout.strip()
            if not branch:
                self.logger.error("Not on a branch (detached HEAD)")
                return None

            return branch

        except Exception as e:
            self.logger.error(f"Error getting current branch: {str(e)}")
            return None

    def _merge_main(self, repo_dir: Path) -> bool:
        """Merge origin/main into the current branch.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            True if merge successful, False otherwise
        """
        try:
            fetch_result = subprocess.run(
                ["git", "fetch", "origin", "main:main"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if fetch_result.returncode != 0:
                self.logger.error(f"Failed to fetch main: {fetch_result.stderr}")
                return False

            merge_result = subprocess.run(
                ["git", "merge", "origin/main", "--no-edit"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if merge_result.returncode != 0:
                self.logger.warning(f"Merge had conflicts or failed: {merge_result.stderr}")
                abort_result = subprocess.run(
                    ["git", "merge", "--abort"],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if abort_result.returncode != 0:
                    self.logger.error(f"Failed to abort merge: {abort_result.stderr}")
                return False

            return True

        except subprocess.TimeoutExpired:
            self.logger.error("Timeout during merge")
            return False
        except Exception as e:
            self.logger.error(f"Error during merge: {str(e)}")
            return False

    def _push_branch(self, repo_dir: Path, branch: str) -> bool:
        """Push the branch to remote.

        Args:
            repo_dir: Path to the repository directory
            branch: Branch name to push

        Returns:
            True if push successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "push", "origin", branch, "--force"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                self.logger.error(f"Failed to push branch {branch}: {result.stderr}")
                return False

            return True

        except subprocess.TimeoutExpired:
            self.logger.error("Timeout during push")
            return False
        except Exception as e:
            self.logger.error(f"Error during push: {str(e)}")
            return False

    def _run_tests(self, repo_dir: Path) -> Dict[str, Any]:
        """Run make test in the repository.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Dictionary containing test execution results
        """
        try:
            result = subprocess.run(
                ["make", "test"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Test execution timed out after {self.timeout} seconds",
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Error running tests: {str(e)}",
            }
