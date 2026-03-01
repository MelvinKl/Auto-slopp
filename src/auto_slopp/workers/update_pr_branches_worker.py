"""PR branch update worker for auto-slopp automation system.

This worker iterates through all open PRs and updates each branch with the latest main.
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from auto_slopp.utils.cli_executor import run_cli_executor
from auto_slopp.utils.git_operations import (
    checkout_branch_resilient,
    merge_main_into_branch,
    push_branch,
)
from auto_slopp.utils.github_operations import get_open_pr_branches
from auto_slopp.utils.repository_utils import validate_repository
from auto_slopp.worker import Worker
from settings.main import settings


class UpdatePRBranchesWorker(Worker):
    """Worker for updating open PR branches with latest main."""

    def __init__(self, timeout: int | None = None):
        """Initialize UpdatePRBranchesWorker.

        Args:
            timeout: Timeout for slopmachine execution in seconds (default: from settings.slop_timeout)
        """
        self.timeout = timeout if timeout is not None else settings.slop_timeout
        self.logger = logging.getLogger("auto_slopp.workers.UpdatePRBranchesWorker")

    def run(self, repo_path: Path) -> Dict[str, Any]:
        """Execute PR branch update workflow for a single repository.

        Args:
            repo_path: Path to a single repository directory

        Returns:
            Dictionary containing execution results and summary.
        """
        self.logger.info(f"UpdatePRBranchesWorker starting for {repo_path}")

        if not repo_path.exists():
            return {
                "worker_name": "UpdatePRBranchesWorker",
                "success": False,
                "error": f"Repository path does not exist: {repo_path}",
                "branches_updated": 0,
            }

        repo_info = validate_repository(repo_path)

        results = {
            "worker_name": "UpdatePRBranchesWorker",
            "success": True,
            "branches_updated": 0,
            "branches_failed": 0,
            "branch_results": [],
        }

        if not repo_info.get("valid", False):
            self.logger.warning(
                f"Repository is invalid: {repo_path.name} - {repo_info.get('errors', ['Unknown error'])}"
            )
            results["success"] = False
            results["error"] = f"Invalid repository: {repo_info.get('errors', ['Unknown error'])}"
            return results

        pr_branches = self._get_open_pr_branches(repo_path)

        if not pr_branches:
            self.logger.info(f"No open PR branches found in {repo_path.name}")
            return results

        for branch in pr_branches:
            self.logger.info(f"Updating branch {branch} in {repo_path.name}")

            branch_result = {
                "branch": branch,
                "success": False,
                "error": None,
                "fix_attempted": False,
                "fix_success": False,
            }

            if not self._checkout_branch(repo_path, branch):
                branch_result["error"] = "Failed to checkout branch"
                results["branches_failed"] += 1
            elif not self._merge_main(repo_path):
                cli_tool = settings.cli_command
                self.logger.info(f"Merge failed for {branch} in {repo_path.name}, using {cli_tool} to fix")
                fix_result = self._fix_merge_with_cli(repo_path)
                branch_result["fix_attempted"] = True

                if fix_result["success"]:
                    branch_result["fix_success"] = True
                    if not self._merge_main(repo_path):
                        branch_result["error"] = "Failed to merge origin/main after fix attempt"
                        results["branches_failed"] += 1
                    elif not self._push_branch(repo_path, branch):
                        branch_result["error"] = "Failed to push branch after fix"
                        results["branches_failed"] += 1
                    else:
                        branch_result["success"] = True
                        results["branches_updated"] += 1
                else:
                    branch_result["fix_success"] = False
                    branch_result["error"] = (
                        f"Failed to fix merge conflicts: {fix_result.get('error', 'Unknown error')}"
                    )
                    results["branches_failed"] += 1
            elif not self._push_branch(repo_path, branch):
                branch_result["error"] = "Failed to push branch"
                results["branches_failed"] += 1
            else:
                branch_result["success"] = True
                results["branches_updated"] += 1

            results["branch_results"].append(branch_result)

        if results["branches_failed"] > 0:
            results["success"] = False

        self.logger.info(
            f"UpdatePRBranchesWorker completed for {repo_path.name}. "
            f"Updated: {results['branches_updated']}, Failed: {results['branches_failed']}"
        )

        return results

    def _get_open_pr_branches(self, repo_dir: Path) -> List[str]:
        """Get list of branches from open PRs in the repository."""
        return get_open_pr_branches(repo_dir)

    def _checkout_branch(self, repo_dir: Path, branch: str) -> bool:
        """Checkout a specific branch in the repository."""
        success = checkout_branch_resilient(repo_dir=repo_dir, branch=branch, fetch_first=True, timeout=60)

        if success:
            self.logger.info(f"Successfully checked out {branch} in {repo_dir.name}")
        else:
            self.logger.error(f"Failed to checkout {branch} in {repo_dir.name}")

        return success

    def _merge_main(self, repo_dir: Path) -> bool:
        """Merge origin/main into the current branch."""
        self.logger.info(f"Merging origin/main into current branch in {repo_dir.name}")

        success, message = merge_main_into_branch(repo_dir=repo_dir, branch="current")

        if not success:
            self.logger.warning(f"Merge failed: {message}")
            return False

        self.logger.info("Successfully merged origin/main into current branch")
        return True

    def _push_branch(self, repo_dir: Path, branch: str) -> bool:
        """Push the updated branch to remote."""
        try:
            self.logger.info(f"Pushing branch {branch} to remote")

            success = push_branch(repo_dir=repo_dir, branch=branch, force=True)

            if not success:
                self.logger.error(f"Failed to push branch {branch}")
                return False

            self.logger.info(f"Successfully pushed branch {branch}")
            return True
        except Exception as e:
            self.logger.error(f"Error pushing branch {branch}: {str(e)}")
            return False

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
