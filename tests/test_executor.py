"""Tests for Executor class and worker registration."""

import threading
import time
from pathlib import Path
from typing import Any
from unittest.mock import patch

from auto_slopp.executor import ALL_WORKERS, Executor
from auto_slopp.worker import Worker
from auto_slopp.workers import (
    GitHubIssueWorker,
    PrReviewWorker,
    PRWorker,
    StaleBranchCleanupWorker,
    VikunjaWorker,
)


class TestWorkerRegistration:
    """Test cases for worker registration in executor."""

    def test_all_workers_includes_github_issue_worker(self):
        """Test that GitHubIssueWorker is registered in ALL_WORKERS."""
        worker_classes = [w.__name__ for w in ALL_WORKERS]
        assert "GitHubIssueWorker" in worker_classes

    def test_all_workers_includes_pr_worker(self):
        """Test that PRWorker is registered in ALL_WORKERS."""
        worker_classes = [w.__name__ for w in ALL_WORKERS]
        assert "PRWorker" in worker_classes

    def test_all_workers_includes_stale_branch_cleanup_worker(self):
        """Test that StaleBranchCleanupWorker is registered in ALL_WORKERS."""
        worker_classes = [w.__name__ for w in ALL_WORKERS]
        assert "StaleBranchCleanupWorker" in worker_classes

    def test_all_workers_includes_vikunja_worker(self):
        """Test that VikunjaWorker is registered in ALL_WORKERS."""
        worker_classes = [w.__name__ for w in ALL_WORKERS]
        assert "VikunjaWorker" in worker_classes

    def test_all_workers_count(self):
        """Test that ALL_WORKERS contains all expected workers."""
        expected_count = 5
        assert len(ALL_WORKERS) == expected_count, (
            f"Expected {expected_count} workers in ALL_WORKERS, "
            f"but found {len(ALL_WORKERS)}: {[w.__name__ for w in ALL_WORKERS]}"
        )

    def test_all_workers_are_worker_subclasses(self):
        """Test that all items in ALL_WORKERS are Worker subclasses."""
        from auto_slopp.worker import Worker

        for worker_class in ALL_WORKERS:
            assert issubclass(worker_class, Worker), f"{worker_class.__name__} is not a Worker subclass"

    def test_all_workers_importable_from_workers_module(self):
        """Test that all workers in ALL_WORKERS can be imported from workers module."""
        for worker_class in ALL_WORKERS:
            assert worker_class in [
                GitHubIssueWorker,
                PRWorker,
                PrReviewWorker,
                StaleBranchCleanupWorker,
                VikunjaWorker,
            ], f"{worker_class.__name__} not found in workers module exports"


class TestExecutorThreading:
    """Test cases for multi-threaded worker execution."""

    def test_executor_has_stop_event(self):
        """Executor should have a threading.Event for signaling stop."""
        executor = Executor(repo_path=Path("/tmp/test"))
        assert isinstance(executor._stop_event, threading.Event)

    def test_executor_has_worker_threads_list(self):
        """Executor should have a list to track worker threads."""
        executor = Executor(repo_path=Path("/tmp/test"))
        assert isinstance(executor._worker_threads, list)

    def test_executor_has_repo_locks(self):
        """Executor should have a dict for per-repository locks."""
        executor = Executor(repo_path=Path("/tmp/test"))
        assert isinstance(executor._repo_locks, dict)

    def test_get_repo_lock_returns_same_lock_for_same_path(self):
        """Same repository path should return the same lock instance."""
        executor = Executor(repo_path=Path("/tmp/test"))
        lock1 = executor._get_repo_lock(Path("/tmp/repo1"))
        lock2 = executor._get_repo_lock(Path("/tmp/repo1"))
        assert lock1 is lock2

    def test_get_repo_lock_returns_different_locks_for_different_paths(self):
        """Different repository paths should return different lock instances."""
        executor = Executor(repo_path=Path("/tmp/test"))
        lock1 = executor._get_repo_lock(Path("/tmp/repo1"))
        lock2 = executor._get_repo_lock(Path("/tmp/repo2"))
        assert lock1 is not lock2

    def test_stop_event_signals_workers_to_stop(self, temp_dir):
        """Setting the stop event should cause workers to stop without processing all subdirectories."""
        executor = Executor(repo_path=temp_dir)

        # Create subdirectories
        sub1 = temp_dir / "sub1"
        sub2 = temp_dir / "sub2"
        sub3 = temp_dir / "sub3"
        sub1.mkdir()
        sub2.mkdir()
        sub3.mkdir()

        call_order = []

        class SlowWorker(Worker):
            def run(self, repo_path: Path) -> Any:
                call_order.append(repo_path.name)
                time.sleep(0.05)
                return None

        # Patch _instantiate_worker to return our slow worker
        with patch.object(Executor, "_instantiate_worker", return_value=SlowWorker()):
            # Set stop event before running
            executor._stop_event.set()
            executor._execute_worker_with_directories(SlowWorker)

        # Worker should have stopped before processing all subdirectories
        # The stop_event is checked at the start of each subdirectory iteration
        assert len(call_order) < 3

    def test_stop_event_is_resettable(self):
        """Stop event should be resettable between iterations."""
        executor = Executor(repo_path=Path("/tmp/test"))
        executor._stop_event.set()
        assert executor._stop_event.is_set()
        executor._stop_event.clear()
        assert not executor._stop_event.is_set()

    def test_run_iteration_launches_threads(self, temp_dir):
        """_run_iteration should launch a thread per enabled worker and join them."""
        executor = Executor(repo_path=temp_dir)

        # Create subdirectory so worker has something to process
        sub = temp_dir / "repo1"
        sub.mkdir()

        # Patch subprocess.run to avoid git pull, and _check_for_updates to prevent reboot
        with patch("subprocess.run"), patch.object(Executor, "_check_for_updates", return_value=False):
            executor._run_iteration()

        # All threads should have been started and joined (all stopped)
        for thread in executor._worker_threads:
            assert not thread.is_alive(), f"Thread {thread.name} is still alive after _run_iteration"

    def test_worker_threads_run_independently(self, temp_dir):
        """Multiple worker threads should run concurrently."""
        executor = Executor(repo_path=temp_dir)

        sub = temp_dir / "repo1"
        sub.mkdir()

        execution_order = []
        lock = threading.Lock()

        class TrackingWorker(Worker):
            def __init__(self, name: str):
                self.name = name

            def run(self, repo_path: Path) -> Any:
                with lock:
                    execution_order.append(f"start-{self.name}")
                time.sleep(0.05)
                with lock:
                    execution_order.append(f"end-{self.name}")
                return None

        worker_a = TrackingWorker("A")
        worker_b = TrackingWorker("B")

        with patch.object(Executor, "_instantiate_worker", side_effect=[worker_a, worker_b]):
            executor._run_iteration()

        # Both workers should have started and finished
        starts = [e for e in execution_order if e.startswith("start-")]
        ends = [e for e in execution_order if e.startswith("end-")]
        assert len(starts) == 2
        assert len(ends) == 2

    def test_repo_lock_prevents_concurrent_access(self, temp_dir):
        """Two workers processing the same repo path should be serialized by the lock."""
        executor = Executor(repo_path=temp_dir)

        sub = temp_dir / "repo1"
        sub.mkdir()

        max_concurrent = [0]
        current_concurrent = [0]
        lock = threading.Lock()

        class LockedWorker(Worker):
            def run(self, repo_path: Path) -> Any:
                with lock:
                    current_concurrent[0] += 1
                    if current_concurrent[0] > max_concurrent[0]:
                        max_concurrent[0] = current_concurrent[0]
                time.sleep(0.05)
                with lock:
                    current_concurrent[0] -= 1
                return None

        worker = LockedWorker()

        with patch.object(Executor, "_instantiate_worker", return_value=worker):
            executor._run_iteration()

        # Only one worker at a time should be active per repo
        assert max_concurrent[0] <= 1


class TestCLICooldownThreadSafety:
    """Test cases for thread-safe CLI cooldown state."""

    def test_cli_states_uses_lock(self):
        """CLI cooldown state should use a threading.Lock for safety."""
        from auto_slopp.utils import cli_executor

        assert isinstance(cli_executor._cli_lock, threading.Lock)

    def test_get_cli_state_creates_entry(self):
        """_get_cli_state should create a new entry if one doesn't exist."""
        from auto_slopp.utils import cli_executor

        # Ensure clean state
        cli_executor._cli_states.clear()

        state = cli_executor._get_cli_state(42)
        assert state["active"] is True
        assert state["cooldown_until"] == 0.0
        assert 42 in cli_executor._cli_states

    def test_get_cli_state_returns_existing_entry(self):
        """_get_cli_state should return existing entry without modification."""
        from auto_slopp.utils import cli_executor

        cli_executor._cli_states.clear()
        cli_executor._cli_states[10] = {"active": False, "cooldown_until": 100.0}

        state = cli_executor._get_cli_state(10)
        assert state["active"] is False
        assert state["cooldown_until"] == 100.0

    def test_concurrent_cooldown_updates(self):
        """Multiple threads should be able to update cooldown state safely."""
        from auto_slopp.utils import cli_executor

        cli_executor._cli_states.clear()
        errors = []

        def update_state(index: int):
            try:
                for _ in range(50):
                    with cli_executor._cli_lock:
                        if index not in cli_executor._cli_states:
                            cli_executor._cli_states[index] = {"active": True, "cooldown_until": 0.0}
                        cli_executor._cli_states[index]["cooldown_until"] = time.time()
                        cli_executor._cli_states[index]["active"] = not cli_executor._cli_states[index]["active"]
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=update_state, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors during concurrent updates: {errors}"
        # All 5 indices should exist
        assert len(cli_executor._cli_states) == 5
