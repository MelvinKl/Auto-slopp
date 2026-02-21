"""Endless loop executor for running Worker instances."""

import sys
import time
import traceback
from pathlib import Path
from typing import Any, Optional, Type

from auto_slopp.discovery import discover_workers
from auto_slopp.utils.git_operations import (
    commit_all_changes,
    pull_from_remote,
    push_to_remote,
)
from auto_slopp.worker import Worker
from settings.main import settings


class Executor:
    """Main executor that continuously runs discovered workers.

    The executor runs in an endless loop, discovering workers,
    instantiating them with the provided paths, and executing
    their run methods while handling exceptions gracefully.
    """

    def __init__(self, search_path: Path, repo_path: Path, task_path: Path):
        """Initialize the executor.

        Args:
            search_path: Path to search for worker implementations
            repo_path: Path to the repository directory
            task_path: Path to the task directory or file
        """
        self.search_path = search_path
        self.repo_path = repo_path
        self.task_path = task_path
        self.running = False

    def start(self) -> None:
        """Start the endless execution loop."""
        print("Starting Auto-slopp executor...")
        self.running = True

        try:
            while self.running:
                self._run_iteration()
                time.sleep(settings.executor_sleep_interval)  # Prevent tight loop
        except KeyboardInterrupt:
            print("\\nReceived interrupt signal, shutting down...")
        except Exception as e:
            print(f"Fatal error in executor: {e}")
            traceback.print_exc()
        finally:
            self.running = False
            print("Executor stopped.")

    def stop(self) -> None:
        """Stop the execution loop."""
        self.running = False

    def _run_iteration(self) -> None:
        """Run a single iteration of worker discovery and execution."""
        try:
            # Update task_repo before running workers
            self._update_task_repo()

            # Discover worker classes
            workers = discover_workers(self.search_path)

            if not workers:
                print("No workers found in this iteration")
                return

            print(f"Found {len(workers)} workers: {[w.__name__ for w in workers]}")

            # Execute each worker
            for worker_class in workers:
                self._execute_worker(worker_class)

        except Exception as e:
            print(f"Error in iteration: {e}")
            traceback.print_exc()

    def _update_task_repo(self) -> None:
        """Pull and push changes in the task_repo."""
        try:
            task_repo_path = settings.task_repo_path
            if not task_repo_path.exists():
                print(f"Task repo path does not exist: {task_repo_path}")
                return

            if not (task_repo_path / ".git").exists():
                print(f"Task repo path is not a git repository: {task_repo_path}")
                return

            commit_success, commit_msg = commit_all_changes(task_repo_path, "Auto-slopp: auto-commit changes")
            if commit_success:
                print(f"Committed changes in task_repo: {commit_msg}")
            else:
                print(f"No changes or commit failed in task_repo: {commit_msg}")

            pull_success, pull_msg = pull_from_remote(task_repo_path, "origin", "main")
            if pull_success:
                print("Pulled latest changes from origin/main in task_repo")
            else:
                print(f"Failed to pull from origin/main in task_repo: {pull_msg}")

            push_success, push_msg = push_to_remote(task_repo_path, "origin", "main")
            if push_success:
                print("Pushed changes to origin/main in task_repo")
            else:
                print(f"Failed to push to origin/main in task_repo: {push_msg}")

        except Exception as e:
            print(f"Error updating task_repo: {e}")

    def _instantiate_worker(self, worker_class: Type[Worker]) -> Worker:
        """Instantiate a worker with appropriate arguments.

        Args:
            worker_class: Worker class to instantiate

        Returns:
            Instantiated worker instance
        """
        # Special handling for TaskProcessorWorker which requires task_repo_path
        if worker_class.__name__ == "TaskProcessorWorker":
            from settings.main import settings

            return worker_class(task_repo_path=settings.task_repo_path)

        # Default instantiation for simple workers
        return worker_class()

    def _execute_worker(self, worker_class: Type[Worker]) -> None:
        """Execute a single worker instance.

        Args:
            worker_class: Worker class to instantiate and execute
        """
        try:
            print(f"Executing worker: {worker_class.__name__}")

            # Check if this worker needs directory iteration (orchestrator-level)
            if self._worker_needs_directory_iteration(worker_class):
                self._execute_worker_with_directories(worker_class)
            else:
                self._execute_worker_single(worker_class)

        except Exception as e:
            print(f"Error executing worker {worker_class.__name__}: {e}")
            traceback.print_exc()

    def _worker_needs_directory_iteration(self, worker_class: Type[Worker]) -> bool:
        """Check if worker needs directory iteration at orchestrator level.

        Args:
            worker_class: Worker class to check

        Returns:
            True if worker should be executed for each subdirectory
        """
        return True

    def _execute_worker_with_directories(self, worker_class: Type[Worker]) -> None:
        """Execute worker for each subdirectory in repo_path.

        Args:
            worker_class: Worker class to instantiate and execute
        """
        if not self.repo_path.exists():
            print(f"Repository path does not exist: {self.repo_path}")
            return

        # Get all subdirectories in repo_path
        subdirectories = [d for d in self.repo_path.iterdir() if d.is_dir()]

        if not subdirectories:
            print(f"No subdirectories found in {self.repo_path}")
            return

        print(f"Found {len(subdirectories)} subdirectories to process")

        # Execute worker for each subdirectory
        for subdirectory in subdirectories:
            try:
                print(f"Processing subdirectory: {subdirectory.name}")

                # Instantiate worker
                worker = self._instantiate_worker(worker_class)

                # Map repo_task_path to corresponding subdirectory
                repo_task_path = self.task_path / subdirectory.name if self.task_path else None

                # Execute worker on single subdirectory
                start_time = time.time()
                result = worker.run(subdirectory, repo_task_path)
                execution_time = time.time() - start_time

                print(f"Worker {worker_class.__name__} on {subdirectory.name} completed in {execution_time:.2f}s")
                if result is not None:
                    print(f"Result: {result}")

            except Exception as e:
                print(f"Error executing worker {worker_class.__name__} on {subdirectory.name}: {e}")
                traceback.print_exc()

    def _execute_worker_single(self, worker_class: Type[Worker]) -> None:
        """Execute worker once on entire repo_path (for workers that don't need iteration).

        Args:
            worker_class: Worker class to instantiate and execute
        """
        # Instantiate worker with appropriate arguments
        worker = self._instantiate_worker(worker_class)

        # Execute worker
        start_time = time.time()
        result = worker.run(self.repo_path, self.task_path)
        execution_time = time.time() - start_time

        print(f"Worker {worker_class.__name__} completed in {execution_time:.2f}s")
        if result is not None:
            print(f"Result: {result}")


def run_executor(
    search_path: Optional[Path] = None,
    repo_path: Optional[Path] = None,
    task_path: Optional[Path] = None,
) -> None:
    """Run the executor with the given parameters or settings defaults.

    Args:
        search_path: Path to search for worker implementations (optional)
        repo_path: Path to the repository directory (optional)
        task_path: Path to the task directory or file (optional)
    """
    executor = Executor(
        search_path=search_path or settings.worker_search_path,
        repo_path=repo_path or settings.base_repo_path,
        task_path=task_path or settings.base_task_path,
    )
    executor.start()
