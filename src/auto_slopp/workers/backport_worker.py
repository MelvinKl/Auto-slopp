"""Backport worker for cherry-picking commits to release branches.

This worker identifies commits from a source branch (typically main)
and backports them to target release branches.
"""

import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from auto_slopp.worker import Worker


class BackportWorker(Worker):
    """Worker for backporting commits to release branches.

    This worker cherry-picks commits from a source branch to one or more
    target branches for creating backports.
    """

    def __init__(
        self,
        source_branch: str = "main",
        target_branches: Optional[List[str]] = None,
        commits: Optional[List[str]] = None,
        dry_run: bool = False,
    ):
        """Initialize the backport worker.

        Args:
            source_branch: Source branch to cherry-pick from (default: main)
            target_branches: List of target branches to backport to
            commits: List of commit hashes to backport (default: all recent)
            dry_run: If True, only simulate backport without making changes
        """
        self.source_branch = source_branch
        self.target_branches = target_branches or []
        self.commits = commits or []
        self.dry_run = dry_run
        self.logger = logging.getLogger("auto_slopp.workers.BackportWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute backport operation for a repository.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file (unused in worker)

        Returns:
            Dictionary containing backport results and statistics.
        """
        start_time = datetime.now(timezone.utc)
        self.logger.info(f"Starting backport worker for {repo_path}")

        validation_result = self._validate_input(repo_path, task_path, start_time)
        if validation_result:
            return validation_result

        results = self._create_results_dict(start_time, repo_path, task_path)

        backport_results = self._process_backports(repo_path)
        results["backport_results"].append(backport_results)
        self._update_results_statistics(results, backport_results)

        results["execution_time"] = (datetime.now(timezone.utc) - start_time).total_seconds()
        self._log_completion_summary(results)

        return results

    def _validate_input(self, repo_path: Path, task_path: Path, start_time: datetime) -> Optional[Dict[str, Any]]:
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
                "worker_name": "BackportWorker",
                "execution_time": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "timestamp": start_time.isoformat(),
                "repo_path": str(repo_path),
                "task_path": str(task_path),
                "dry_run": self.dry_run,
                "source_branch": self.source_branch,
                "target_branches": self.target_branches,
                "success": False,
                "error": f"Repository path does not exist: {repo_path}",
                "commits_backported": 0,
                "commits_failed": 0,
                "backport_results": [],
            }
        return None

    def _create_results_dict(self, start_time: datetime, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Create the initial results dictionary.

        Args:
            start_time: Start time of execution
            repo_path: Repository path
            task_path: Task path

        Returns:
            Initialized results dictionary
        """
        return {
            "worker_name": "BackportWorker",
            "execution_time": 0,
            "timestamp": start_time.isoformat(),
            "repo_path": str(repo_path),
            "task_path": str(task_path),
            "dry_run": self.dry_run,
            "source_branch": self.source_branch,
            "target_branches": self.target_branches,
            "commits": self.commits,
            "commits_backported": 0,
            "commits_failed": 0,
            "backport_results": [],
            "success": True,
        }

    def _process_backports(self, repo_dir: Path) -> Dict[str, Any]:
        """Process backports for a repository.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Dictionary containing backport results for this repository.
        """
        self.logger.info(f"Processing backports for repository: {repo_dir.name}")

        result = {
            "repository": repo_dir.name,
            "path": str(repo_dir),
            "source_branch": self.source_branch,
            "target_branches": self.target_branches,
            "commits_processed": 0,
            "commits_backported": 0,
            "commits_failed": 0,
            "backported_commits": [],
            "failed_commits": [],
            "success": True,
            "error": None,
        }

        try:
            original_cwd = os.getcwd()
        except OSError:
            original_cwd = str(repo_dir)

        try:
            os.chdir(repo_dir)

            commits_to_backport = self._get_commits_to_backport(repo_dir)
            result["commits_processed"] = len(commits_to_backport)

            for target_branch in self.target_branches:
                for commit in commits_to_backport:
                    success = self._cherry_pick_commit(repo_dir, commit, target_branch)
                    if success:
                        result["commits_backported"] += 1
                        result["backported_commits"].append(
                            {
                                "commit": commit,
                                "target_branch": target_branch,
                            }
                        )
                    else:
                        result["commits_failed"] += 1
                        result["failed_commits"].append(
                            {
                                "commit": commit,
                                "target_branch": target_branch,
                            }
                        )

            self.logger.info(
                f"Backport complete for {repo_dir.name}: "
                f"{result['commits_backported']} backported, "
                f"{result['commits_failed']} failed"
            )

        except Exception as e:
            self.logger.error(f"Backport failed for {repo_dir.name}: {str(e)}")
            result["success"] = False
            result["error"] = str(e)

        finally:
            try:
                os.chdir(original_cwd)
            except OSError:
                pass

        return result

    def _get_commits_to_backport(self, repo_dir: Path) -> List[str]:
        """Get list of commits to backport.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            List of commit hashes to backport
        """
        if self.commits:
            return self.commits

        try:
            result = subprocess.run(
                ["git", "log", self.source_branch, "--format=%H", "-n", "10"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            commits = result.stdout.strip().split("\n")
            return [c for c in commits if c]
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get commits: {e}")
            return []

    def _cherry_pick_commit(self, repo_dir: Path, commit: str, target_branch: str) -> bool:
        """Cherry-pick a commit to a target branch.

        Args:
            repo_dir: Path to the repository directory
            commit: Commit hash to cherry-pick
            target_branch: Target branch name

        Returns:
            True if cherry-pick succeeded, False otherwise
        """
        if self.dry_run:
            self.logger.info(f"DRY RUN: Would cherry-pick {commit} to {target_branch}")
            return True

        try:
            subprocess.run(
                ["git", "checkout", target_branch],
                cwd=repo_dir,
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                ["git", "cherry-pick", commit, "--no-commit"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                subprocess.run(
                    ["git", "cherry-pick", "--abort"],
                    cwd=repo_dir,
                    capture_output=True,
                )
                self.logger.warning(f"Cherry-pick failed for {commit} to {target_branch}: {result.stderr}")
                return False

            subprocess.run(
                ["git", "commit", "-m", f"Backport: {commit}"],
                cwd=repo_dir,
                capture_output=True,
                check=True,
            )

            self.logger.info(f"Successfully cherry-picked {commit} to {target_branch}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git error during cherry-pick: {e}")
            return False

    def _update_results_statistics(self, results: Dict[str, Any], backport_result: Dict[str, Any]) -> None:
        """Update results statistics with backport result.

        Args:
            results: Main results dictionary to update
            backport_result: Backport processing result
        """
        results["commits_backported"] += backport_result["commits_backported"]
        results["commits_failed"] += backport_result["commits_failed"]

        if not backport_result["success"]:
            results["success"] = False

    def _log_completion_summary(self, results: Dict[str, Any]) -> None:
        """Log completion summary.

        Args:
            results: Final results dictionary
        """
        self.logger.info(
            f"BackportWorker completed. Commits backported: {results['commits_backported']}, "
            f"Commits failed: {results['commits_failed']}"
        )
