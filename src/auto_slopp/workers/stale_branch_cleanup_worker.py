"""Stale branch cleanup worker for removing old local branches.

This worker identifies local branches that don't exist on the remote
and deletes them if their last commit is older than 5 days.
"""

import logging
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from auto_slopp.utils.repository_utils import discover_repositories, validate_repository
from auto_slopp.worker import Worker


class StaleBranchCleanupWorker(Worker):
    """Worker for cleaning up stale local branches.

    Identifies local branches that are not present on the remote repository
    and deletes them if their last commit is older than 5 days.
    """

    def __init__(self, days_threshold: int = 5, dry_run: bool = False):
        """Initialize the stale branch cleanup worker.

        Args:
            days_threshold: Days after which a branch is considered stale
            dry_run: Only report deletions without actually deleting
        """
        self.days_threshold = days_threshold
        self.dry_run = dry_run
        self.logger = logging.getLogger("auto_slopp.workers.StaleBranchCleanupWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute stale branch cleanup.

        Args:
            repo_path: Path to the directory containing repository subdirectories
            task_path: Path to the task directory or file (unused in worker)

        Returns:
            Dictionary containing cleanup results and statistics.
        """
        start_time = datetime.now(timezone.utc)
        self.logger.info(f"Starting stale branch cleanup in {repo_path}")

        if not repo_path.exists():
            return {
                "worker_name": "StaleBranchCleanupWorker",
                "execution_time": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "timestamp": start_time.isoformat(),
                "repo_path": str(repo_path),
                "task_path": str(task_path),
                "dry_run": self.dry_run,
                "days_threshold": self.days_threshold,
                "success": False,
                "error": f"Repository path does not exist: {repo_path}",
                "repositories_processed": 0,
                "repositories_with_errors": 0,
                "total_branches_deleted": 0,
                "total_branches_failed": 0,
                "repository_results": [],
            }

        results = {
            "worker_name": "StaleBranchCleanupWorker",
            "execution_time": 0,
            "timestamp": start_time.isoformat(),
            "repo_path": str(repo_path),
            "task_path": str(task_path),
            "dry_run": self.dry_run,
            "days_threshold": self.days_threshold,
            "repositories_processed": 0,
            "repositories_with_errors": 0,
            "total_branches_deleted": 0,
            "total_branches_failed": 0,
            "repository_results": [],
            "success": True,
        }

        # Discover and validate repositories
        repositories = discover_repositories(repo_path, validate=True)

        # Process only valid git repositories
        for repo_info in repositories:
            repo_dir = Path(repo_info["path"])

            self.logger.info(f"Processing repository: {repo_info['name']}")
            results["repositories_processed"] += 1

            if not repo_info.get("valid", False):
                self.logger.warning(
                    f"Skipping invalid repository: {repo_info['name']} - {repo_info.get('errors', ['Unknown error'])}"
                )
                results["repositories_with_errors"] += 1
                results["success"] = False
                continue

            repo_result = self._process_repository(repo_dir)
            results["repository_results"].append(repo_result)

            if repo_result["success"]:
                results["total_branches_deleted"] += repo_result["branches_deleted"]
                results["total_branches_failed"] += repo_result["branches_failed_to_delete"]
            else:
                results["repositories_with_errors"] += 1
                results["success"] = False

        # Update final execution time
        results["execution_time"] = (datetime.now(timezone.utc) - start_time).total_seconds()

        self.logger.info(
            f"StaleBranchCleanupWorker completed. Processed: {results['repositories_processed']}, "
            f"Errors: {results['repositories_with_errors']}, "
            f"Total branches deleted: {results['total_branches_deleted']}, "
            f"Total failed: {results['total_branches_failed']}"
        )

        return results

    def _process_repository(self, repo_dir: Path) -> Dict[str, Any]:
        """Process a single repository directory for stale branch cleanup.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Dictionary containing processing results for this repository.
        """
        import os

        result = {
            "repository": repo_dir.name,
            "path": str(repo_dir),
            "success": False,
            "branches_deleted": 0,
            "branches_failed_to_delete": 0,
            "deleted_branches": [],
            "failed_deletions": [],
            "error": None,
        }

        try:
            original_cwd = os.getcwd()
        except OSError:
            # If we can't get current directory, use repo_dir as fallback
            original_cwd = str(repo_dir)

        try:
            # Change to repository directory
            os.chdir(repo_dir)

            # Get all branches information
            local_branches = self._get_local_branches()
            remote_branches = self._get_remote_branches()

            # Find stale branches
            stale_branches = self._identify_stale_branches(local_branches, remote_branches)

            # Delete stale branches
            deleted_branches = []
            failed_deletions = []

            for branch_info in stale_branches:
                branch_name = branch_info["name"]
                if self.dry_run:
                    self.logger.info(
                        f"DRY RUN: Would delete branch '{branch_name}' "
                        f"(last commit: {branch_info['last_commit_date']}) in {repo_dir.name}"
                    )
                    deleted_branches.append(branch_info)
                else:
                    if self._delete_branch(branch_name):
                        deleted_branches.append(branch_info)
                    else:
                        failed_deletions.append(branch_info)

            # Restore working directory
            os.chdir(original_cwd)

            result.update(
                {
                    "success": True,
                    "branches_deleted": len(deleted_branches),
                    "branches_failed_to_delete": len(failed_deletions),
                    "deleted_branches": deleted_branches,
                    "failed_deletions": failed_deletions,
                    "total_local_branches": len(local_branches),
                    "total_remote_branches": len(remote_branches),
                    "stale_branches_found": len(stale_branches),
                }
            )

            self.logger.info(
                f"Completed stale branch cleanup for {repo_dir.name}: "
                f"{len(deleted_branches)} deleted, {len(failed_deletions)} failed"
            )

        except Exception as e:
            # Restore working directory on error
            try:
                os.chdir(original_cwd)
            except OSError:
                pass

            self.logger.error(f"Stale branch cleanup failed for {repo_dir.name}: {str(e)}")
            result["error"] = str(e)

        return result

    def _get_local_branches(self) -> List[Dict[str, Any]]:
        """Get all local branches with their last commit dates.

        Returns:
            List of dictionaries containing branch information.
        """
        try:
            # Get local branches and their last commit dates
            result = subprocess.run(
                [
                    "git",
                    "branch",
                    "-v",
                    "--format=%(refname:short)%00%(committerdate:iso-strict)" "%00%(objectname)",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            branches = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    parts = line.split("\x00")
                    if len(parts) >= 3:
                        name = parts[0].strip("* ").strip()  # Remove '* ' prefix for current branch
                        # Using iso-strict format from git, should be parseable
                        date_str = parts[1]
                        try:
                            commit_date = datetime.fromisoformat(date_str)
                        except ValueError:
                            # Fallback to handling git's regular iso format
                            # Handle format like '2026-02-08 11:06:41 +0000'
                            date_str = date_str.replace(" ", "T", 1).replace(" ", "")
                            commit_date = datetime.fromisoformat(date_str)
                        commit_hash = parts[2]

                        # Skip main/master branches by default
                        if name not in ["main", "master"]:
                            branches.append(
                                {
                                    "name": name,
                                    "last_commit_date": commit_date,
                                    "last_commit_hash": commit_hash,
                                    "days_old": (datetime.now(timezone.utc) - commit_date).days,
                                }
                            )

            return branches

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get local branches: {e}")
            raise

    def _get_remote_branches(self) -> set:
        """Get all branches that exist on the remote.

        Returns:
            Set of remote branch names (without 'origin/' prefix).
        """
        try:
            result = subprocess.run(
                ["git", "branch", "-r", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                check=True,
            )

            remote_branches = set()
            for line in result.stdout.strip().split("\n"):
                if line.strip() and "HEAD" not in line:
                    # Remove 'origin/' prefix and clean up
                    branch_name = line.strip().replace("origin/", "")
                    if branch_name:
                        remote_branches.add(branch_name)

            return remote_branches

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get remote branches: {e}")
            raise

    def _identify_stale_branches(
        self, local_branches: List[Dict[str, Any]], remote_branches: set
    ) -> List[Dict[str, Any]]:
        """Identify branches that are stale and should be deleted.

        Args:
            local_branches: List of local branch information
            remote_branches: Set of remote branch names

        Returns:
            List of stale branch information.
        """
        stale_branches = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.days_threshold)

        for branch in local_branches:
            branch_name = branch["name"]

            # Check if branch not on remote and is older than threshold
            if branch_name not in remote_branches and branch["last_commit_date"] < cutoff_date:
                stale_branches.append(branch)

        self.logger.info(f"Found {len(stale_branches)} stale branches out of " f"{len(local_branches)} local branches")
        return stale_branches

    def _delete_branch(self, branch_name: str) -> bool:
        """Delete a local branch.

        Args:
            branch_name: Name of the branch to delete

        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            # Don't delete current branch
            result = subprocess.run(
                [
                    "git",
                    "rev-parse",
                    "--abbrev-ref",
                    "HEAD",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            current_branch = result.stdout.strip()

            if branch_name == current_branch:
                self.logger.warning(f"Cannot delete current branch '{branch_name}'")
                return False

            # Delete the branch
            subprocess.run(
                ["git", "branch", "-D", branch_name],
                capture_output=True,
                text=True,
                check=True,
            )

            self.logger.info(f"Successfully deleted branch '{branch_name}'")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to delete branch '{branch_name}': {e}")
            return False
