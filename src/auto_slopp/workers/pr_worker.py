"""PR branch testing worker for auto-slopp automation system.

This worker iterates through all open PRs, updates each branch with latest main,
runs tests, and uses the configured CLI tool to fix any failing tests.
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from auto_slopp.utils.cli_executor import get_active_cli_command, run_cli_executor
from auto_slopp.utils.git_operations import (
    checkout_branch_resilient,
    merge_main_into_branch,
    push_branch,
)
from auto_slopp.utils.github_operations import get_open_pr_branches
from auto_slopp.utils.repository_utils import discover_repositories, validate_repository
from auto_slopp.worker import Worker
from settings.main import settings


class PRWorker(Worker):
    """Worker for testing open PR branches and fixing failures with the configured CLI tool."""

    def __init__(self, timeout: int | None = None):
        """Initialize PRWorker.

        Args:
            timeout: Timeout for test execution and OpenAgent fixes in seconds (default: from settings.slop_timeout)
        """
        self.timeout = timeout if timeout is not None else settings.slop_timeout
        self.logger = logging.getLogger("auto_slopp.workers.PRWorker")

    def run(self, repo_path: Path) -> Dict[str, Any]:
        """Execute PR branch testing workflow for a single repository.

        Args:
            repo_path: Path to a single repository directory

        Returns:
            Dictionary containing execution results and summary.
        """
        self.logger.info(f"PRWorker starting for {repo_path}")

        if not repo_path.exists():
            return {
                "worker_name": "PRWorker",
                "success": False,
                "error": f"Repository path does not exist: {repo_path}",
                "repositories_processed": 0,
                "repositories_tested": 0,
                "repositories_fixed": 0,
            }

        repo_info = validate_repository(repo_path)

        results = {
            "worker_name": "PRWorker",
            "success": True,
            "repositories_processed": 1,
            "repositories_tested": 0,
            "repositories_fixed": 0,
            "repositories_with_errors": 0,
            "repositories_invalid": 0,
            "repository_results": [],
            "errors": [],
        }

        self.logger.info(f"Processing repository: {repo_path.name}")

        if not repo_info.get("valid", False):
            self.logger.warning(
                f"Repository is invalid: {repo_path.name} - {repo_info.get('errors', ['Unknown error'])}"
            )
            results["repositories_invalid"] = 1
            results["repositories_with_errors"] = 1
            results["errors"].append(
                f"{repo_path.name}: Invalid repository - {repo_info.get('errors', ['Unknown error'])}"
            )
            results["success"] = False
        else:
            repo_result = self._process_repository(repo_path)
            results["repository_results"].append(repo_result)

            if repo_result["success"]:
                results["repositories_tested"] = 1
                if repo_result["tests_fixed"]:
                    results["repositories_fixed"] = 1
                if repo_result.get("error"):
                    results["repositories_with_errors"] = 1
                    results["errors"].append(f"{repo_path.name}: {repo_result.get('error', 'Unknown error')}")
            else:
                results["repositories_with_errors"] = 1
                results["errors"].append(f"{repo_path.name}: {repo_result.get('error', 'Unknown error')}")
                results["success"] = False

        self.logger.info(
            f"PRWorker completed for {repo_path.name}. "
            f"Tested: {results['repositories_tested']}, Fixed: {results['repositories_fixed']}, "
            f"Errors: {results['repositories_with_errors']}"
        )

        return results

    def _process_repository(self, repo_dir: Path) -> Dict[str, Any]:
        """Process a single repository directory.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Dictionary containing processing results for this repository.
        """
        result = {
            "repository": repo_dir.name,
            "path": str(repo_dir),
            "success": False,
            "branches_checked_out": [],
            "test_results": [],
            "tests_fixed": False,
            "error": None,
        }

        try:
            pr_branches = self._get_open_pr_branches(repo_dir)
            result["branches_checked_out"] = pr_branches

            if not pr_branches:
                self.logger.info(f"No open PR branches found in {repo_dir.name}, skipping")
                result["success"] = True
                result["error"] = None
                return result

            for branch in pr_branches:
                self.logger.info(f"Testing branch {branch} in {repo_dir.name}")

                if not self._checkout_branch(repo_dir, branch):
                    result["error"] = f"Failed to checkout branch {branch}"
                    continue

                if not self._update_branch_with_main(repo_dir, branch):
                    cli_tool = get_active_cli_command()
                    self.logger.info(f"Merge failed for {branch} in {repo_dir.name}, using {cli_tool} to fix")
                    fix_result = self._fix_merge_with_cli(repo_dir)
                    if fix_result["success"]:
                        if not self._update_branch_with_main(repo_dir, branch):
                            result["error"] = f"Failed to update branch {branch} with main after fix attempt"
                            continue
                    else:
                        result["error"] = f"Failed to fix merge conflicts: {fix_result.get('error', 'Unknown error')}"
                        continue

                test_result = self._run_tests(repo_dir)
                result["test_results"].append(
                    {
                        "branch": branch,
                        "success": test_result["success"],
                        "output": test_result.get("output", ""),
                        "error": test_result.get("error"),
                    }
                )

                tests_successful = test_result["success"]

                if not test_result["success"]:
                    cli_tool = get_active_cli_command()
                    self.logger.info(f"Tests failed for {branch} in {repo_dir.name}, using {cli_tool} to fix")
                    fix_result = self._fix_tests_with_cli(repo_dir)
                    if fix_result["success"]:
                        result["tests_fixed"] = True
                        verify_result = self._run_tests(repo_dir)
                        tests_successful = verify_result["success"]
                        result["test_results"][-1]["fix_success"] = verify_result["success"]
                        result["test_results"][-1]["fix_output"] = verify_result.get("output", "")
                    else:
                        tests_successful = False
                        result["test_results"][-1]["fix_success"] = False
                        result["test_results"][-1]["fix_error"] = fix_result.get("error", "Unknown fix error")
                else:
                    result["test_results"][-1]["fix_success"] = True

                if tests_successful and not self._push_branch(repo_dir, branch):
                    result["error"] = f"Failed to push branch {branch}"
                    continue

            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error processing repository {repo_dir.name}: {str(e)}")
            result["error"] = str(e)

        return result

    def _get_open_pr_branches(self, repo_dir: Path) -> List[str]:
        """Get list of branches from open PRs in the repository.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            List of branch names from open PRs
        """
        return get_open_pr_branches(repo_dir)

    def _checkout_branch(self, repo_dir: Path, branch: str) -> bool:
        """Checkout a specific branch in the repository.

        Args:
            repo_dir: Path to the repository directory
            branch: Branch name to checkout

        Returns:
            True if checkout successful, False otherwise
        """
        success = checkout_branch_resilient(repo_dir=repo_dir, branch=branch, fetch_first=True, timeout=60)

        if success:
            self.logger.info(f"Successfully checked out {branch} in {repo_dir.name}")
        else:
            self.logger.error(f"Failed to checkout {branch} in {repo_dir.name}")

        return success

    def _update_branch_with_main(self, repo_dir: Path, branch: str) -> bool:
        """Update branch with latest main by pulling and merging origin/main.

        Args:
            repo_dir: Path to the repository directory
            branch: Branch name being updated

        Returns:
            True if update successful, False otherwise
        """
        self.logger.info(f"Updating branch {branch} with latest main")

        success, message = merge_main_into_branch(repo_dir=repo_dir, branch=branch)

        if not success:
            self.logger.error(f"Failed to update branch {branch} with main: {message}")
            return False

        self.logger.info(f"Successfully merged origin/main into {branch}")
        return True

    def _push_branch(self, repo_dir: Path, branch: str) -> bool:
        """Push the updated branch to remote.

        Args:
            repo_dir: Path to the repository directory
            branch: Branch name to push

        Returns:
            True if push successful, False otherwise
        """
        self.logger.info(f"Pushing branch {branch} to remote")

        success = push_branch(repo_dir=repo_dir, branch=branch, force=True)

        if not success:
            self.logger.error(f"Failed to push branch {branch}")
            return False

        self.logger.info(f"Successfully pushed branch {branch}")
        return True

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

    def _fix_tests_with_cli(self, repo_dir: Path) -> Dict[str, Any]:
        """Use the configured CLI tool to fix failing tests.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Dictionary containing CLI execution results
        """
        additional_instructions = "'make test' is failing fix it and push the changes"

        result = run_cli_executor(
            additional_instructions=additional_instructions,
            working_directory=repo_dir,
            timeout=self.timeout,
            agent_args=[],
            capture_output=True,
        )

        return {
            "success": result["success"],
            "output": result.get("stdout", ""),
            "error": result.get("error") if not result["success"] else None,
            "return_code": result["return_code"],
        }

    def _fix_merge_with_cli(self, repo_dir: Path) -> Dict[str, Any]:
        """Use the configured CLI tool to fix merge conflicts.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Dictionary containing CLI execution results
        """
        additional_instructions = "Fix the merge conflicts and complete the merge, then push the changes"

        result = run_cli_executor(
            additional_instructions=additional_instructions,
            working_directory=repo_dir,
            timeout=self.timeout,
            agent_args=[],
            capture_output=True,
        )

        return {
            "success": result["success"],
            "output": result.get("stdout", ""),
            "error": result.get("error") if not result["success"] else None,
            "return_code": result["return_code"],
        }
