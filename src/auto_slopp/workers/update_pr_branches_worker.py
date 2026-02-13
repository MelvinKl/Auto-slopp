"""PR branch update worker for auto-slopp automation system.

This worker iterates through all open PRs and updates each branch with the latest main.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from auto_slopp.utils.git_operations import checkout_branch_resilient
from auto_slopp.utils.repository_utils import validate_repository
from auto_slopp.worker import Worker


class UpdatePRBranchesWorker(Worker):
    """Worker for updating open PR branches with latest main."""

    def __init__(self):
        """Initialize UpdatePRBranchesWorker."""
        self.logger = logging.getLogger("auto_slopp.workers.UpdatePRBranchesWorker")
        # TODO: git operations belong into the git_operations file NOT into this file. If you add them here they arent't reusable. Also: There is error handling available in the git_operations.
        # TODO: create a new file for github_operations and move ALL operations for github there. Not only from this file, from all files.
        pass

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute PR branch update workflow for a single repository.

        Args:
            repo_path: Path to a single repository directory
            task_path: Path to task directory or file (not used in this worker)

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
            }

            if not self._checkout_branch(repo_path, branch):
                branch_result["error"] = "Failed to checkout branch"
                results["branches_failed"] += 1
            elif not self._merge_main(repo_path):
                branch_result["error"] = "Failed to merge origin/main"
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
        try:
            result = subprocess.run(
                ["gh", "pr", "list", "--state=open", "--json=headRefName"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                self.logger.error(f"Failed to list PRs in {repo_dir.name}: {result.stderr}")
                return []

            prs = json.loads(result.stdout)
            return [pr["headRefName"] for pr in prs]

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout getting PRs from {repo_dir.name}")
            return []
        except Exception as e:
            self.logger.error(f"Error getting PRs from {repo_dir.name}: {str(e)}")
            return []

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
        try:
            self.logger.info(f"Merging origin/main into current branch in {repo_dir.name}")

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
                subprocess.run(
                    ["git", "merge", "--abort"],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                return False

            self.logger.info("Successfully merged origin/main into current branch")
            return True

        except subprocess.TimeoutExpired:
            self.logger.error("Timeout merging main")
            return False
        except Exception as e:
            self.logger.error(f"Error merging main: {str(e)}")
            return False

    def _push_branch(self, repo_dir: Path, branch: str) -> bool:
        """Push the updated branch to remote."""
        try:
            self.logger.info(f"Pushing branch {branch} to remote")

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

            self.logger.info(f"Successfully pushed branch {branch}")
            return True

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout pushing branch {branch}")
            return False
        except Exception as e:
            self.logger.error(f"Error pushing branch {branch}: {str(e)}")
            return False
