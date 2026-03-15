"""Endless loop executor for running Worker instances."""

import subprocess
import time
import traceback
from pathlib import Path
from typing import Any, Optional, Type

from auto_slopp.worker import Worker
from auto_slopp.workers import (
    GitHubIssueWorker,
    PRWorker,
    StaleBranchCleanupWorker,
)
from settings.main import settings

ALL_WORKERS: list[Type[Worker]] = [
    GitHubIssueWorker,
    PRWorker,
    StaleBranchCleanupWorker,
]


class Executor:
    """Main executor that continuously runs enabled workers.

    The executor runs in an endless loop, selecting enabled workers
    from the predefined list, instantiating them with the provided paths,
    and executing their run methods while handling exceptions gracefully.
    """

    def __init__(self, repo_path: Path):
        """Initialize the executor.

        Args:
            repo_path: Path to the repository directory
        """
        self.repo_path = repo_path
        self.running = False

    def start(self) -> None:
        """Start the endless execution loop."""
        print("Starting Auto-slopp executor...")
        self.running = True

        try:
            while self.running:
                self._run_iteration()
                self._check_for_updates()
                time.sleep(settings.executor_sleep_interval)
        except KeyboardInterrupt:
            print("\nReceived interrupt signal, shutting down...")
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
        """Run a single iteration of worker execution."""
        try:
            enabled_workers = [w for w in ALL_WORKERS if w.__name__ not in settings.workers_disabled]

            if not enabled_workers:
                print("No workers enabled")
                return

            print(f"Running {len(enabled_workers)} workers: {[w.__name__ for w in enabled_workers]}")

            for worker_class in enabled_workers:
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
        return worker_class()

    def _execute_worker(self, worker_class: Type[Worker]) -> None:
        """Execute a single worker instance.

        Args:
            worker_class: Worker class to instantiate and execute
        """
        try:
            print(f"Executing worker: {worker_class.__name__}")
            self._execute_worker_with_directories(worker_class)

        except Exception as e:
            print(f"Error executing worker {worker_class.__name__}: {e}")
            traceback.print_exc()

    def _execute_worker_with_directories(self, worker_class: Type[Worker]) -> None:
        """Execute worker for each subdirectory in repo_path.

        Args:
            worker_class: Worker class to instantiate and execute
        """
        if not self.repo_path.exists():
            print(f"Repository path does not exist: {self.repo_path}")
            return

        subdirectories = [d for d in self.repo_path.iterdir() if d.is_dir()]

        if not subdirectories:
            print(f"No subdirectories found in {self.repo_path}")
            return

        print(f"Found {len(subdirectories)} subdirectories to process")

        for subdirectory in subdirectories:
            try:
                print(f"Processing subdirectory: {subdirectory.name}")

                worker = self._instantiate_worker(worker_class)

                start_time = time.time()
                result = worker.run(subdirectory)
                execution_time = time.time() - start_time

                print(f"Worker {worker_class.__name__} on {subdirectory.name} completed in {execution_time:.2f}s")
                if result is not None:
                    print(f"Result: {result}")

            except Exception as e:
                print(f"Error executing worker {worker_class.__name__} on {subdirectory.name}: {e}")
                traceback.print_exc()

    def _check_for_updates(self) -> bool:
        """Execute git pull in the working directory and detect if updates were downloaded.

        Returns:
            True if an update was detected, False otherwise.
        """
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"Git pull failed: {result.stderr}")
                return False

            output = result.stdout
            update_detected = "Updating" in output or "Fast-forward" in output and "Already up to date" not in output

            if update_detected:
                print(f"Update detected: {output.strip()}")
                self._schedule_reboot(settings.auto_update_reboot_delay)
                return True

            return False

        except Exception as e:
            print(f"Error checking for updates: {e}")
            traceback.print_exc()
            return False

    def _schedule_reboot(self, delay: int) -> None:
        """Schedule a reboot after the specified delay.

        Args:
            delay: Delay in seconds before rebooting.
        """
        print(f"Update detected. Rebooting in {delay} seconds...")

        if delay > 0:
            time.sleep(delay)

        self._execute_reboot()

    def _execute_reboot(self) -> None:
        """Execute the reboot command."""
        print("Executing reboot...")
        try:
            subprocess.run(["reboot"], check=True)
        except Exception as e:
            print(f"Failed to execute reboot: {e}")
            traceback.print_exc()


def run_executor(
    repo_path: Optional[Path] = None,
) -> None:
    """Run the executor with the given parameters or settings defaults.

    Args:
        repo_path: Path to the repository directory (optional)
    """
    executor = Executor(
        repo_path=repo_path or settings.base_repo_path,
    )
    executor.start()
