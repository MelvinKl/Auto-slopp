"""Task processing worker for handling text file instructions with OpenCode.

This worker processes repositories by:
1. Mapping repositories from repo_path to task_repo_path
2. Creating directories if they don't exist
3. Finding and processing .txt files with instructions
4. Using OpenCode to execute the instructions
5. Renaming processed files with 4-digit counters and .used suffix
6. Committing and pushing changes to task_repo_path
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from auto_slopp.base.opencode_worker import OpenCodeWorker
from auto_slopp.utils.file_operations import ensure_directory_exists
from auto_slopp.utils.repository_utils import discover_repositories
from auto_slopp.utils.task_processing import process_repository


class TaskProcessorWorker(OpenCodeWorker):
    """Worker for processing text file instructions with OpenCode.

    This worker maps repositories from repo_path to task_repo_path,
    processes .txt instruction files, and manages the complete workflow
    including file renaming, git operations, and OpenCode execution.
    """

    def __init__(
        self,
        task_repo_path: Path,
        counter_start: int = 1,
        timeout: int = 7200,
        agent_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ):
        """Initialize the TaskProcessorWorker.

        Args:
            task_repo_path: Path to the task repository directory
            counter_start: Starting number for 4-digit file counter
            timeout: Timeout for OpenCode execution in seconds
            agent_args: Additional arguments to pass to OpenCode
            dry_run: If True, skip actual OpenCode execution and git operations
        """
        super().__init__(agent_args=agent_args, timeout=timeout, process_all_repos=False)
        self.task_repo_path = task_repo_path
        self.counter_start = counter_start
        self.dry_run = dry_run
        self.logger = logging.getLogger("auto_slopp.workers.TaskProcessorWorker")

        # Ensure task_repo_path exists
        if not ensure_directory_exists(self.task_repo_path):
            raise RuntimeError(f"Failed to create task repository path: {self.task_repo_path}")

    def get_agent_instructions(self) -> str:
        """Get instructions for OpenCode execution.

        This method is called by the parent OpenCodeWorker class.
        For TaskProcessorWorker, instructions are dynamically loaded
        from text files in each repository.

        Returns:
            Empty string as instructions are provided per text file
        """
        return ""

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute the task processing workflow for a single repository.

        Args:
            repo_path: Path to a single repository subdirectory
            task_path: Path to the corresponding task subdirectory

        Returns:
            Dictionary containing execution results and statistics
        """
        start_time = self._get_current_time()
        self.logger.info(f"TaskProcessorWorker starting with repo_path: {repo_path}")

        # Validate input paths
        validation_result = self._validate_paths(repo_path, task_path, start_time)
        if validation_result:
            return validation_result

        # Initialize results for single repository
        results = self._create_results_dict(start_time, repo_path, task_path)

        # Process the single repository
        repo_result = self._process_single_repository(repo_path, task_path)
        results["repository_results"].append(repo_result)
        self._update_results_statistics(results, repo_result)

        # Finalize results
        results["execution_time"] = self._get_elapsed_time(start_time)
        self._log_completion_summary(results)

        return results

    def _validate_paths(self, repo_path: Path, task_path: Path, start_time: float) -> Optional[Dict[str, Any]]:
        """Validate input paths and return error result if invalid.

        Args:
            repo_path: Repository path to validate
            task_path: Task path (unused but kept for signature)
            start_time: Start time for error result

        Returns:
            Error result dictionary if validation fails, None otherwise
        """
        if not repo_path.exists():
            return self._create_error_result(
                start_time,
                repo_path,
                task_path,
                f"Repository path does not exist: {repo_path}",
            )

        if not self.task_repo_path.exists():
            return self._create_error_result(
                start_time,
                repo_path,
                task_path,
                f"Task repository path does not exist: {self.task_repo_path}",
            )

        return None

    def _create_results_dict(self, start_time: float, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Create the initial results dictionary.

        Args:
            start_time: Start time of execution
            repo_path: Repository path
            task_path: Task path

        Returns:
            Initialized results dictionary
        """
        return {
            "worker_name": "TaskProcessorWorker",
            "execution_time": 0,
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "task_path": str(task_path),
            "task_repo_path": str(self.task_repo_path),
            "dry_run": self.dry_run,
            "repositories_processed": 0,
            "repositories_with_errors": 0,
            "text_files_processed": 0,
            "openagent_executions": 0,
            "files_renamed": 0,
            "git_operations": 0,
            "repository_results": [],
            "success": True,
        }

    def _process_single_repository(self, repo_dir: Path, task_path: Path) -> Dict[str, Any]:
        """Process a single repository.

        Args:
            repo_dir: Path to the repository directory
            task_path: Path to the corresponding task directory

        Returns:
            Processing result for this repository
        """
        self.logger.info(f"Processing repository: {repo_dir.name}")

        # Use the provided task_path as the task repository directory
        if not task_path.exists():
            task_path.mkdir()
            # Create a .gitkeep file so the directory is recognized by git
            gitkeep_file = task_path / ".gitkeep"
            gitkeep_file.write_text("# Directory created by TaskProcessorWorker\n")

            # Initialize git repository and commit the .gitkeep file
            from auto_slopp.utils.git_operations import commit_and_push_changes

            commit_success, _ = commit_and_push_changes(
                task_path,
                f"Initialize directory for {repo_dir.name}",
                push_if_remote=False,
            )

            if commit_success:
                self.logger.info(f"Successfully initialized task directory: {task_path.name}")
            else:
                self.logger.warning(f"Failed to initialize git in task directory: {task_path.name}")

        return process_repository(
            repo_dir=repo_dir,
            task_repo_dir=task_path,
            dry_run=self.dry_run,
            agent_args=self.agent_args,
            timeout=self.timeout,
            counter_start=self.counter_start,
        )

    def _update_results_statistics(self, results: Dict[str, Any], repo_result: Dict[str, Any]) -> None:
        """Update results statistics with repository processing result.

        Args:
            results: Main results dictionary to update
            repo_result: Repository processing result
        """
        results["repositories_processed"] += 1

        if repo_result["success"]:
            results["text_files_processed"] += repo_result.get("text_files_processed", 0)
            results["openagent_executions"] += repo_result.get("openagent_executions", 0)
            results["files_renamed"] += repo_result.get("files_renamed", 0)
            results["git_operations"] += repo_result.get("git_operations", 0)
        else:
            results["repositories_with_errors"] += 1
            results["success"] = False

    def _log_completion_summary(self, results: Dict[str, Any]) -> None:
        """Log completion summary.

        Args:
            results: Final results dictionary
        """
        self.logger.info(
            f"TaskProcessorWorker completed. Processed: "
            f"{results['repositories_processed']}, "
            f"Text files: {results['text_files_processed']}, "
            f"OpenCode executions: {results['openagent_executions']}, "
            f"Files renamed: {results['files_renamed']}, "
            f"Git operations: {results['git_operations']}, "
            f"Errors: {results['repositories_with_errors']}"
        )

    def _create_error_result(
        self, start_time: float, repo_path: Path, task_path: Path, error_msg: str
    ) -> Dict[str, Any]:
        """Create an error result dictionary.

        Args:
            start_time: Start time of execution
            repo_path: Repository path
            task_path: Task path
            error_msg: Error message

        Returns:
            Error result dictionary
        """
        return {
            "worker_name": "TaskProcessorWorker",
            "execution_time": self._get_elapsed_time(start_time),
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "task_path": str(task_path),
            "task_repo_path": str(self.task_repo_path),
            "dry_run": self.dry_run,
            "success": False,
            "error": error_msg,
            "repositories_processed": 0,
            "repositories_with_errors": 0,
            "text_files_processed": 0,
            "openagent_executions": 0,
            "files_renamed": 0,
            "git_operations": 0,
            "repository_results": [],
        }

    def _get_current_time(self) -> float:
        """Get current time as float for consistent timing.

        Returns:
            Current time as float
        """
        return time.time()

    def _get_elapsed_time(self, start_time: float) -> float:
        """Get elapsed time from start time.

        Args:
            start_time: Start time as float

        Returns:
            Elapsed time in seconds
        """
        return time.time() - start_time
