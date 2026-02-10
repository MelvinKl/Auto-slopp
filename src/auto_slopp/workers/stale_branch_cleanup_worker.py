"""Stale branch cleanup worker for removing old local branches.

This worker identifies local branches that don't exist on the remote
and deletes them if their last commit is older than 5 days.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from auto_slopp.utils.branch_analysis import analyze_repository_branches
from auto_slopp.utils.git_operations import (
    get_local_branches,
    get_remote_branches,
    delete_branch,
)
from auto_slopp.utils.repository_utils import discover_repositories
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

        # Validate input path
        validation_result = self._validate_input_path(repo_path, task_path, start_time)
        if validation_result:
            return validation_result

        # Initialize results
        results = self._create_results_dict(start_time, repo_path, task_path)

        # Discover and validate repositories
        repositories = discover_repositories(repo_path, validate=True)

        # Process each repository
        for repo_info in repositories:
            repo_result = self._process_repository(repo_info)
            results["repository_results"].append(repo_result)
            self._update_results_statistics(results, repo_result)

        # Finalize results
        results["execution_time"] = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds()
        self._log_completion_summary(results)

        return results

    def _validate_input_path(
        self, repo_path: Path, task_path: Path, start_time: datetime
    ) -> Optional[Dict[str, Any]]:
        """Validate the input repository path.

        Args:
            repo_path: Path to validate
            task_path: Task path (for result structure)
            start_time: Start time for error result

        Returns:
            Error result if validation fails, None otherwise
        """
        if not repo_path.exists():
            return {
                "worker_name": "StaleBranchCleanupWorker",
                "execution_time": (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds(),
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
        return None

    def _create_results_dict(
        self, start_time: datetime, repo_path: Path, task_path: Path
    ) -> Dict[str, Any]:
        """Create the initial results dictionary.

        Args:
            start_time: Start time of execution
            repo_path: Repository path
            task_path: Task path

        Returns:
            Initialized results dictionary
        """
        return {
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

    def _process_repository(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single repository directory for stale branch cleanup.

        Args:
            repo_info: Repository information from discover_repositories

        Returns:
            Dictionary containing processing results for this repository.
        """
        repo_dir = Path(repo_info["path"])

        self.logger.info(f"Processing repository: {repo_info['name']}")

        # Handle invalid repositories
        if not repo_info.get("valid", False):
            self.logger.warning(
                f"Skipping invalid repository: {repo_info['name']} - "
                f"{repo_info.get('errors', ['Unknown error'])}"
            )
            return self._create_invalid_repo_result(repo_info)

        # Analyze and cleanup branches using utility function
        return analyze_repository_branches(
            repo_dir=repo_dir, days_threshold=self.days_threshold, dry_run=self.dry_run
        )

    def _create_invalid_repo_result(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create result for an invalid repository.

        Args:
            repo_info: Repository information

        Returns:
            Error result for invalid repository
        """
        return {
            "repository": repo_info["name"],
            "path": repo_info["path"],
            "success": False,
            "branches_deleted": 0,
            "branches_failed_to_delete": 0,
            "deleted_branches": [],
            "failed_deletions": [],
            "error": "; ".join(repo_info.get("errors", ["Repository is invalid"])),
        }

    def _update_results_statistics(
        self, results: Dict[str, Any], repo_result: Dict[str, Any]
    ) -> None:
        """Update results statistics with repository processing result.

        Args:
            results: Main results dictionary to update
            repo_result: Repository processing result
        """
        results["repositories_processed"] += 1

        if repo_result["success"]:
            results["total_branches_deleted"] += repo_result["branches_deleted"]
            results["total_branches_failed"] += repo_result["branches_failed_to_delete"]
        else:
            results["repositories_with_errors"] += 1
            results["success"] = False

    def _get_local_branches(self) -> List[Dict[str, Any]]:
        """Get local branches for testing purposes.

        Returns:
            List of local branch information.
        """
        return get_local_branches(Path.cwd())

    def _get_remote_branches(self) -> Set[str]:
        """Get remote branches for testing purposes.

        Returns:
            Set of remote branch names.
        """
        return get_remote_branches(Path.cwd())

    def _identify_stale_branches(
        self, local_branches: List[Dict[str, Any]], remote_branches: Set[str]
    ) -> List[Dict[str, Any]]:
        """Identify stale branches for testing purposes.

        Args:
            local_branches: List of local branch information
            remote_branches: Set of remote branch names

        Returns:
            List of stale branch information.
        """
        from auto_slopp.utils.branch_analysis import identify_stale_branches

        return identify_stale_branches(
            local_branches, remote_branches, self.days_threshold
        )

    def _delete_branch(self, branch_name: str) -> bool:
        """Delete a branch for testing purposes.

        Args:
            branch_name: Name of branch to delete

        Returns:
            True if deletion succeeded, False otherwise.
        """
        if self.dry_run:
            return True

        try:
            delete_branch(Path.cwd(), branch_name)
            return True
        except Exception:
            return False

    def _log_completion_summary(self, results: Dict[str, Any]) -> None:
        """Log completion summary.

        Args:
            results: Final results dictionary
        """
        self.logger.info(
            f"StaleBranchCleanupWorker completed. Processed: {results['repositories_processed']}, "
            f"Errors: {results['repositories_with_errors']}, "
            f"Total branches deleted: {results['total_branches_deleted']}, "
            f"Total failed: {results['total_branches_failed']}"
        )
