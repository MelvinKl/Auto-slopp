"""Endless loop executor for running Worker instances."""

import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Optional, Type

from auto_slopp.discovery import discover_workers
from auto_slopp.plugin_manager import PluginManager
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
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugins_from_path(search_path)

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
            # Discover worker classes using plugin system
            workers = discover_workers(self.search_path)

            if not workers:
                print("No workers found in this iteration")
                return

            print(f"Found {len(workers)} workers: {[w.__name__ for w in workers]}")

            # Apply plugin filtering
            hook = self.plugin_manager.get_hook()
            try:
                filtered_results = hook.auto_slopp_filter_workers(workers=workers)
                if filtered_results:
                    # Use the last non-empty result from filters
                    for filtered in reversed(filtered_results):
                        if filtered is not None:
                            workers = filtered
                            break
            except Exception as e:
                print(f"Warning: Plugin filtering failed: {e}")

            # Execute each worker
            for worker_class in workers:
                self._execute_worker(worker_class)

        except Exception as e:
            print(f"Error in iteration: {e}")
            traceback.print_exc()

    def _instantiate_worker(self, worker_class: Type[Worker]) -> Worker:
        """Instantiate a worker with appropriate arguments.

        Args:
            worker_class: Worker class to instantiate

        Returns:
            Instantiated worker instance
        """
        # Default kwargs
        kwargs = {}

        # Special handling for workers that need extra parameters
        if worker_class.__name__ == "TaskProcessorWorker":
            from settings.main import settings

            kwargs = {"task_repo_path": settings.task_repo_path}

        # Apply plugin modification hooks
        hook = self.plugin_manager.get_hook()
        try:
            modified_kwargs_list = hook.auto_slopp_modify_worker_kwargs(worker_class=worker_class, kwargs=kwargs)
            if modified_kwargs_list:
                # Use the last non-empty result from modifiers
                for modified in reversed(modified_kwargs_list):
                    if modified is not None:
                        kwargs = modified
                        break
        except Exception as e:
            print(f"Warning: Plugin kwargs modification failed: {e}")

        # Instantiate worker with modified kwargs
        return worker_class(**kwargs)

    def _execute_worker(self, worker_class: Type[Worker]) -> None:
        """Execute a single worker instance.

        Args:
            worker_class: Worker class to instantiate and execute
        """
        try:
            print(f"Executing worker: {worker_class.__name__}")

            # Check if worker should execute using plugin hooks
            should_execute = None
            hook = self.plugin_manager.get_hook()
            try:
                should_execute_results = hook.auto_slopp_should_execute_worker(
                    worker_class=worker_class,
                    repo_path=str(self.repo_path),
                    task_path=str(self.task_path),
                )
                if should_execute_results:
                    # Use the last non-None result
                    for result in reversed(should_execute_results):
                        if result is not None:
                            should_execute = result
                            break
            except Exception as e:
                print(f"Warning: Plugin should_execute check failed: {e}")

            # Skip execution if plugins say so
            if should_execute is False:
                print(f"Skipping worker {worker_class.__name__} (plugin decision)")
                return

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
        # Workers that currently handle their own directory iteration
        # should be handled by the orchestrator instead
        workers_requiring_iteration = {
            "TaskProcessorWorker",
            "RenovateTestWorker",
            "StaleBranchCleanupWorker",
        }

        return worker_class.__name__ in workers_requiring_iteration

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
                # Ensure task_path is not None
                task_path = repo_task_path or self.task_path
                result = worker.run(subdirectory, task_path)
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
        hook = self.plugin_manager.get_hook()
        before_context = None

        # Call before execution hooks
        try:
            before_results = hook.auto_slopp_worker_before_execution(
                worker_class=worker_class,
                repo_path=str(self.repo_path),
                task_path=str(self.task_path),
            )
            if before_results:
                # Use the last non-None result
                for result in reversed(before_results):
                    if result is not None:
                        before_context = result
                        break
        except Exception as e:
            print(f"Warning: Plugin before_execution hook failed: {e}")

        try:
            # Instantiate worker with appropriate arguments
            worker = self._instantiate_worker(worker_class)

            # Execute worker
            start_time = time.time()
            result = worker.run(self.repo_path, self.task_path)
            execution_time = time.time() - start_time

            print(f"Worker {worker_class.__name__} completed in {execution_time:.2f}s")
            if result is not None:
                print(f"Result: {result}")

            # Call after execution hooks
            try:
                hook.auto_slopp_worker_after_execution(
                    worker_class=worker_class,
                    repo_path=str(self.repo_path),
                    task_path=str(self.task_path),
                    result=result,
                    execution_time=execution_time,
                    before_context=before_context,
                )
            except Exception as e:
                print(f"Warning: Plugin after_execution hook failed: {e}")

        except Exception as e:
            # Call execution failed hooks
            try:
                hook.auto_slopp_worker_execution_failed(
                    worker_class=worker_class,
                    repo_path=str(self.repo_path),
                    task_path=str(self.task_path),
                    exception=e,
                    before_context=before_context,
                )
            except Exception as hook_e:
                print(f"Warning: Plugin execution_failed hook failed: {hook_e}")

            raise


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
