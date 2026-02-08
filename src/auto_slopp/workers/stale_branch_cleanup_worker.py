"""Stale branch cleanup worker for removing old local branches.

This worker identifies local branches that don't exist on the remote
and deletes them if their last commit is older than 5 days.
"""

import logging
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from ..worker import Worker


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
        self.logger = logging.getLogger(
            "auto_slopp.workers.StaleBranchCleanupWorker"
        )

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute stale branch cleanup.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file (unused in worker)

        Returns:
            Dictionary containing cleanup results and statistics.
        """
        start_time = datetime.now(timezone.utc)
        self.logger.info(f"Starting stale branch cleanup in {repo_path}")

        import os

        try:
            original_cwd = os.getcwd()
        except OSError:
            # If we can't get current directory, use repo_path as fallback
            original_cwd = str(repo_path)

        try:
            # Change to repository directory
            os.chdir(repo_path)

            # Get all branches information
            local_branches = self._get_local_branches()
            remote_branches = self._get_remote_branches()

            # Find stale branches
            stale_branches = self._identify_stale_branches(
                local_branches, remote_branches
            )

            # Delete stale branches
            deleted_branches = []
            failed_deletions = []

            for branch_info in stale_branches:
                branch_name = branch_info["name"]
                if self.dry_run:
                    self.logger.info(
                        f"DRY RUN: Would delete branch '{branch_name}' "
                        f"(last commit: {branch_info['last_commit_date']})"
                    )
                    deleted_branches.append(branch_info)
                else:
                    if self._delete_branch(branch_name):
                        deleted_branches.append(branch_info)
                    else:
                        failed_deletions.append(branch_info)

            # Restore working directory
            os.chdir(original_cwd)

            execution_time = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds()

            result = {
                "worker_name": "StaleBranchCleanupWorker",
                "execution_time": execution_time,
                "timestamp": start_time.isoformat(),
                "repo_path": str(repo_path),
                "task_path": str(task_path),
                "dry_run": self.dry_run,
                "days_threshold": self.days_threshold,
                "total_local_branches": len(local_branches),
                "total_remote_branches": len(remote_branches),
                "stale_branches_found": len(stale_branches),
                "branches_deleted": len(deleted_branches),
                "branches_failed_to_delete": len(failed_deletions),
                "success": len(failed_deletions) == 0,
                "deleted_branches": deleted_branches,
                "failed_deletions": failed_deletions,
            }

            self.logger.info(
                f"Completed stale branch cleanup: {len(deleted_branches)} "
                f"deleted, {len(failed_deletions)} failed"
            )
            return result

        except Exception as e:
            # Restore working directory on error
            try:
                os.chdir(original_cwd)
            except OSError:
                pass

            execution_time = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds()
            self.logger.error(f"Stale branch cleanup failed: {str(e)}")

            return {
                "worker_name": "StaleBranchCleanupWorker",
                "execution_time": execution_time,
                "timestamp": start_time.isoformat(),
                "repo_path": str(repo_path),
                "task_path": str(task_path),
                "dry_run": self.dry_run,
                "days_threshold": self.days_threshold,
                "success": False,
                "error": str(e),
                "branches_deleted": [],
                "failed_deletions": [],
            }

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
                    "--format=%(refname:short)%00%(committerdate:iso-strict)"
                    "%00%(objectname)",
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
                        name = (
                            parts[0].strip("* ").strip()
                        )  # Remove '* ' prefix for current branch
                        # Using iso-strict format from git, should be parseable
                        date_str = parts[1]
                        try:
                            commit_date = datetime.fromisoformat(date_str)
                        except ValueError:
                            # Fallback to handling git's regular iso format
                            # Handle format like '2026-02-08 11:06:41 +0000'
                            date_str = date_str.replace(" ", "T", 1).replace(
                                " ", ""
                            )
                            commit_date = datetime.fromisoformat(date_str)
                        commit_hash = parts[2]

                        # Skip main/master branches by default
                        if name not in ["main", "master"]:
                            branches.append(
                                {
                                    "name": name,
                                    "last_commit_date": commit_date,
                                    "last_commit_hash": commit_hash,
                                    "days_old": (
                                        datetime.now(timezone.utc)
                                        - commit_date
                                    ).days,
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
        cutoff_date = datetime.now(timezone.utc) - timedelta(
            days=self.days_threshold
        )

        for branch in local_branches:
            branch_name = branch["name"]

            # Check if branch not on remote and is older than threshold
            if (
                branch_name not in remote_branches
                and branch["last_commit_date"] < cutoff_date
            ):
                stale_branches.append(branch)

        self.logger.info(
            f"Found {len(stale_branches)} stale branches out of "
            f"{len(local_branches)} local branches"
        )
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
                self.logger.warning(
                    f"Cannot delete current branch '{branch_name}'"
                )
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
