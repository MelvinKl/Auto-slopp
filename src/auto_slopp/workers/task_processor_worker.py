"""Task processing worker for handling text file instructions with OpenAgent.

This worker processes repositories by:
1. Mapping repositories from repo_path to task_repo_path
2. Creating directories if they don't exist
3. Finding and processing .txt files with instructions
4. Using OpenAgent to execute the instructions
5. Renaming processed files with 4-digit counters and .used suffix
6. Committing and pushing changes to task_repo_path
"""

import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from auto_slopp.base.openagent_worker import OpenAgentWorker
from auto_slopp.utils.repository_utils import discover_repositories


class TaskProcessorWorker(OpenAgentWorker):
    """Worker for processing text file instructions with OpenAgent.

    This worker maps repositories from repo_path to task_repo_path,
    processes .txt instruction files, and manages the complete workflow
    including file renaming, git operations, and OpenAgent execution.
    """

    def __init__(
        self,
        task_repo_path: Path,
        counter_start: int = 1,
        timeout: int = 600,
        agent_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ):
        """Initialize the TaskProcessorWorker.

        Args:
            task_repo_path: Path to the task repository directory
            counter_start: Starting number for 4-digit file counter
            timeout: Timeout for OpenAgent execution in seconds
            agent_args: Additional arguments to pass to OpenAgent
            dry_run: If True, skip actual OpenAgent execution and git operations
        """
        super().__init__(agent_args=agent_args, timeout=timeout, process_all_repos=True)
        self.task_repo_path = task_repo_path
        self.counter_start = counter_start
        self.dry_run = dry_run
        self.logger = logging.getLogger("auto_slopp.workers.TaskProcessorWorker")

        # Ensure task_repo_path exists
        self.task_repo_path.mkdir(parents=True, exist_ok=True)

    def get_agent_instructions(self) -> str:
        """Get instructions for OpenAgent execution.

        This method is called by the parent OpenAgentWorker class.
        For TaskProcessorWorker, instructions are dynamically loaded
        from text files in each repository.

        Returns:
            Empty string as instructions are provided per text file
        """
        return ""

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute the task processing workflow.

        Args:
            repo_path: Path to the directory containing repository subdirectories
            task_path: Path to the task directory or file (unused in this worker)

        Returns:
            Dictionary containing execution results and statistics
        """
        start_time = self._get_current_time()
        self.logger.info(f"TaskProcessorWorker starting with repo_path: {repo_path}")

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

        results = {
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

        # Discover repositories in repo_path
        repositories = discover_repositories(repo_path, validate=True)

        for repo_info in repositories:
            repo_dir = Path(repo_info["path"])

            self.logger.info(f"Processing repository: {repo_info['name']}")
            results["repositories_processed"] += 1

            if not repo_info.get("valid", False):
                self.logger.warning(
                    f"Skipping invalid repository: {repo_info['name']} - "
                    f"{repo_info.get('errors', ['Unknown error'])}"
                )
                results["repositories_with_errors"] += 1
                results["success"] = False
                continue

            repo_result = self._process_repository(repo_dir)
            results["repository_results"].append(repo_result)

            # Update statistics
            if repo_result["success"]:
                results["text_files_processed"] += repo_result.get("text_files_processed", 0)
                results["openagent_executions"] += repo_result.get("openagent_executions", 0)
                results["files_renamed"] += repo_result.get("files_renamed", 0)
                results["git_operations"] += repo_result.get("git_operations", 0)
            else:
                results["repositories_with_errors"] += 1
                results["success"] = False

        results["execution_time"] = self._get_elapsed_time(start_time)

        self.logger.info(
            f"TaskProcessorWorker completed. Processed: "
            f"{results['repositories_processed']}, "
            f"Text files: {results['text_files_processed']}, "
            f"OpenAgent executions: {results['openagent_executions']}, "
            f"Files renamed: {results['files_renamed']}, "
            f"Git operations: {results['git_operations']}, "
            f"Errors: {results['repositories_with_errors']}"
        )

        return results

    def _process_repository(self, repo_dir: Path) -> Dict[str, Any]:
        """Process a single repository directory.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Dictionary containing processing results for this repository
        """
        result = {
            "repository": repo_dir.name,
            "path": str(repo_dir),
            "success": False,
            "text_files_processed": 0,
            "openagent_executions": 0,
            "files_renamed": 0,
            "git_operations": 0,
            "processed_files": [],
            "errors": [],
        }

        try:
            # Create corresponding directory in task_repo_path
            task_repo_dir = self.task_repo_path / repo_dir.name
            task_repo_dir.mkdir(exist_ok=True)
            self.logger.info(f"Ensured task directory exists: {task_repo_dir}")

            # Find .txt files in the repository
            text_files = self._find_text_files(repo_dir)

            if not text_files:
                self.logger.info(f"No .txt files found in {repo_dir.name}")
                result["success"] = True
                return result

            # Process each text file
            for text_file in text_files:
                file_result = self._process_text_file(text_file, task_repo_dir)
                result["processed_files"].append(file_result)

                if file_result["success"]:
                    result["text_files_processed"] += 1
                    if file_result.get("openagent_executed", False):
                        result["openagent_executions"] += 1
                    if file_result.get("file_renamed", False):
                        result["files_renamed"] += 1
                    if file_result.get("git_operations", False):
                        result["git_operations"] += 1
                else:
                    result["errors"].append(file_result.get("error", "Unknown processing error"))

            result["success"] = len(result["errors"]) == 0

        except Exception as e:
            self.logger.error(f"Error processing repository {repo_dir.name}: {str(e)}")
            result["errors"].append(str(e))

        return result

    def _find_text_files(self, repo_dir: Path) -> List[Path]:
        """Find all .txt files in the repository directory.

        Args:
            repo_dir: Path to search for .txt files

        Returns:
            List of paths to .txt files, sorted by name
        """
        try:
            text_files = []
            for file_path in repo_dir.rglob("*.txt"):
                if file_path.is_file():
                    text_files.append(file_path)

            # Sort by modification time (oldest first) or by name
            text_files.sort(key=lambda f: f.stat().st_mtime)

            self.logger.info(f"Found {len(text_files)} .txt files in {repo_dir.name}")
            return text_files

        except Exception as e:
            self.logger.error(f"Error finding .txt files in {repo_dir.name}: {str(e)}")
            return []

    def _process_text_file(self, text_file: Path, task_repo_dir: Path) -> Dict[str, Any]:
        """Process a single text file with instructions.

        Args:
            text_file: Path to the text file
            task_repo_dir: Directory in task_repo_path for this repository

        Returns:
            Dictionary containing processing results for this file
        """
        result = {
            "file": str(text_file),
            "success": False,
            "instructions": "",
            "openagent_executed": False,
            "file_renamed": False,
            "git_operations": False,
            "error": None,
        }

        try:
            # Read file content as instructions
            instructions = text_file.read_text(encoding="utf-8").strip()

            if not instructions:
                result["error"] = "Text file is empty"
                return result

            result["instructions"] = instructions
            self.logger.info(f"Loaded instructions from {text_file.name}")

            # Execute OpenAgent with the instructions
            if not self.dry_run:
                openagent_result = self._execute_openagent_with_instructions(instructions, task_repo_dir)
                result["openagent_executed"] = openagent_result["success"]

                if not openagent_result["success"]:
                    result["error"] = (
                        f"OpenAgent execution failed: " f"{openagent_result.get('error', 'Unknown error')}"
                    )
                    return result
            else:
                self.logger.info(f"DRY RUN: Would execute OpenAgent with instructions from " f"{text_file.name}")
                result["openagent_executed"] = True

            # Rename the file with counter and .used suffix
            new_file_path = self._rename_processed_file(text_file)
            result["file_renamed"] = new_file_path is not None

            if new_file_path:
                self.logger.info(f"Renamed {text_file.name} to {new_file_path.name}")

            # Commit and push changes in task_repo_path
            if not self.dry_run:
                git_success = self._commit_and_push_changes(task_repo_dir, text_file.name)
                result["git_operations"] = git_success

                if not git_success:
                    result["error"] = "Git commit/push operations failed"
                    return result
            else:
                self.logger.info(f"DRY RUN: Would commit and push changes for {text_file.name}")
                result["git_operations"] = True

            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error processing text file {text_file.name}: {str(e)}")
            result["error"] = str(e)

        return result

    def _execute_openagent_with_instructions(self, instructions: str, work_dir: Path) -> Dict[str, Any]:
        """Execute OpenAgent with specific instructions.

        Args:
            instructions: Text instructions to pass to OpenAgent
            work_dir: Working directory for OpenAgent execution

        Returns:
            Dictionary containing OpenAgent execution results
        """
        try:
            self.logger.info(f"Executing OpenAgent with instructions length: {len(instructions)}")

            # Create a temporary instruction file
            instruction_file = work_dir / ".agent_instructions.txt"
            instruction_file.write_text(instructions, encoding="utf-8")

            try:
                # Build OpenAgent command
                cmd = ["openagent"] + self.agent_args

                # Add the instruction file as argument
                cmd.append(str(instruction_file))

                # Execute OpenAgent
                result = subprocess.run(
                    cmd,
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )

                self.logger.info(f"OpenAgent execution completed with return code: " f"{result.returncode}")

                return {
                    "success": result.returncode == 0,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "timeout": False,
                }

            finally:
                # Clean up instruction file
                try:
                    instruction_file.unlink(missing_ok=True)
                except Exception:
                    pass

        except subprocess.TimeoutExpired:
            self.logger.error(f"OpenAgent execution timed out after {self.timeout} seconds")
            return {
                "success": False,
                "timeout": True,
                "error": f"OpenAgent execution timed out after {self.timeout} seconds",
            }

        except Exception as e:
            self.logger.error(f"Error executing OpenAgent: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing OpenAgent: {str(e)}",
            }

    def _rename_processed_file(self, original_file: Path) -> Optional[Path]:
        """Rename a processed file with 4-digit counter and .used suffix.

        Args:
            original_file: Path to the original file

        Returns:
            Path to the renamed file, or None if renaming failed
        """
        try:
            # Find next available counter
            counter = self._get_next_counter(original_file.parent)
            counter_str = f"{counter:04d}"

            # Create new filename: counter_original_name.used.txt
            new_name = f"{counter_str}_{original_file.stem}.used{original_file.suffix}"
            new_path = original_file.parent / new_name

            # Rename the file
            original_file.rename(new_path)

            self.logger.info(f"Renamed {original_file.name} to {new_name}")
            return new_path

        except Exception as e:
            self.logger.error(f"Error renaming file {original_file.name}: {str(e)}")
            return None

    def _get_next_counter(self, directory: Path) -> int:
        """Get the next available 4-digit counter for file naming.

        Args:
            directory: Directory to search for existing counters

        Returns:
            Next available counter number
        """
        try:
            # Find all files with counter prefix pattern
            counter_pattern = re.compile(r"^(\d{4})_.*\.used\.txt$")
            existing_counters = []

            for file_path in directory.iterdir():
                if file_path.is_file() and file_path.suffix == ".txt":
                    match = counter_pattern.match(file_path.name)
                    if match:
                        existing_counters.append(int(match.group(1)))

            # Find next available counter
            if existing_counters:
                max_counter = max(existing_counters)
                return max(self.counter_start, max_counter + 1)
            else:
                return self.counter_start

        except Exception:
            return self.counter_start

    def _commit_and_push_changes(self, task_repo_dir: Path, processed_file: str) -> bool:
        """Commit and push changes in the task repository directory.

        Args:
            task_repo_dir: Directory to commit and push changes
            processed_file: Name of the processed file for commit message

        Returns:
            True if commit and push were successful, False otherwise
        """
        try:
            original_cwd = os.getcwd()

            try:
                # Change to task repository directory
                os.chdir(task_repo_dir)

                # Check if this is a git repository
                if not (task_repo_dir / ".git").exists():
                    self.logger.info(f"Initializing git repository in {task_repo_dir}")
                    subprocess.run(["git", "init"], check=True, capture_output=True)

                # Add all changes
                subprocess.run(["git", "add", "."], check=True, capture_output=True)

                # Check if there are changes to commit
                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                if not status_result.stdout.strip():
                    self.logger.info("No changes to commit in task repository")
                    return True

                # Commit changes
                commit_message = f"Process instructions from {processed_file}"
                subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    check=True,
                    capture_output=True,
                )

                # Check if there's a remote to push to
                remote_result = subprocess.run(
                    ["git", "remote", "-v"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                if remote_result.stdout.strip():
                    # Push changes if remote exists
                    subprocess.run(["git", "push"], check=True, capture_output=True)
                    self.logger.info(f"Committed and pushed changes for {processed_file}")
                else:
                    self.logger.info(f"Committed changes for {processed_file} (no remote to push)")

                return True

            finally:
                os.chdir(original_cwd)

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git operations failed for {processed_file}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error during git operations for {processed_file}: {str(e)}")
            return False

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
