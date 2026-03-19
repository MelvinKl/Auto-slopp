"""Tests for Executor class and worker registration."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from auto_slopp.executor import ALL_WORKERS, Executor
from auto_slopp.workers import (
    GitHubIssueWorker,
    PRWorker,
    StaleBranchCleanupWorker,
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

    def test_all_workers_count(self):
        """Test that ALL_WORKERS contains all expected workers."""
        expected_count = 3
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
                StaleBranchCleanupWorker,
            ], f"{worker_class.__name__} not found in workers module exports"


class TestExecutor:
    """Tests for Executor class."""

    def test_executor_initialization(self):
        """Test executor initialization."""
        repo_path = Path("/tmp/repo")
        executor = Executor(repo_path)

        assert executor.repo_path == repo_path
        assert executor.running is False

    def test_stop_executor(self):
        """Test stopping the executor."""
        executor = Executor(Path("/tmp/repo"))
        executor.running = True

        executor.stop()

        assert executor.running is False

    def test_run_iteration_with_enabled_workers(self, mock_settings):
        """Test running an iteration with enabled workers."""
        executor = Executor(Path("/tmp/repo"))

        mock_worker_instance = MagicMock()
        mock_worker_class = MagicMock(return_value=mock_worker_instance)
        mock_worker_class.__name__ = "TestWorker"

        with patch("auto_slopp.executor.settings", mock_settings):
            with patch.object(executor, "_execute_worker"):
                with patch.object(executor, "_check_for_updates", return_value=False):
                    with patch.object(
                        executor,
                        "_instantiate_worker",
                        return_value=mock_worker_instance,
                    ):
                        executor._run_iteration()

    def test_run_iteration_with_disabled_workers(self, mock_settings):
        """Test running an iteration when all workers are disabled."""
        executor = Executor(Path("/tmp/repo"))
        mock_settings.workers_disabled = [
            "GitHubIssueWorker",
            "PRWorker",
            "StaleBranchCleanupWorker",
        ]

        with patch("auto_slopp.executor.settings", mock_settings):
            with patch.object(executor, "_check_for_updates", return_value=False):
                with patch("builtins.print") as mock_print:
                    executor._run_iteration()

                    mock_print.assert_any_call("No workers enabled")

    def test_run_iteration_exception(self, mock_settings):
        """Test running an iteration handles exceptions."""
        executor = Executor(Path("/tmp/repo"))

        with patch("auto_slopp.executor.settings", mock_settings):
            with patch.object(
                executor,
                "_execute_worker",
                side_effect=RuntimeError("Test error"),
            ):
                with patch.object(executor, "_check_for_updates", return_value=False):
                    with patch("builtins.print"):
                        executor._run_iteration()

    def test_execute_worker_success(self, mock_settings):
        """Test successful worker execution."""
        executor = Executor(Path("/tmp/repo"))

        mock_worker_class = MagicMock()
        mock_worker_class.__name__ = "TestWorker"
        mock_worker_instance = MagicMock()

        with patch("auto_slopp.executor.settings", mock_settings):
            with patch.object(executor, "_execute_worker_with_directories"):
                with patch.object(executor, "_instantiate_worker", return_value=mock_worker_instance):
                    with patch("builtins.print"):
                        executor._execute_worker(mock_worker_class)

    def test_execute_worker_exception(self, mock_settings):
        """Test worker execution handles exceptions."""
        executor = Executor(Path("/tmp/repo"))

        mock_worker_class = MagicMock()
        mock_worker_class.__name__ = "TestWorker"

        with patch.object(
            executor,
            "_execute_worker_with_directories",
            side_effect=RuntimeError("Test error"),
        ):
            with patch("builtins.print"):
                executor._execute_worker(mock_worker_class)

    def test_execute_worker_with_directories_no_subdirectories(self, mock_settings):
        """Test executing worker with no subdirectories."""
        executor = Executor(Path("/tmp/repo"))

        mock_subdir = MagicMock()
        mock_subdir.is_dir.return_value = False

        mock_repo_path = MagicMock()
        mock_repo_path.exists.return_value = True
        mock_repo_path.iterdir.return_value = [mock_subdir]

        executor.repo_path = mock_repo_path

        mock_worker_class = MagicMock()

        with patch("auto_slopp.executor.settings", mock_settings):
            with patch("builtins.print") as mock_print:
                executor._execute_worker_with_directories(mock_worker_class)

                mock_print.assert_any_call(f"No subdirectories found in {mock_repo_path}")

    def test_execute_worker_with_directories_nonexistent_path(self, mock_settings):
        """Test executing worker with nonexistent repository path."""
        executor = Executor(Path("/nonexistent"))

        mock_repo_path = MagicMock()
        mock_repo_path.exists.return_value = False

        executor.repo_path = mock_repo_path

        mock_worker_class = MagicMock()

        with patch("auto_slopp.executor.settings", mock_settings):
            with patch("builtins.print") as mock_print:
                executor._execute_worker_with_directories(mock_worker_class)

                mock_print.assert_any_call(f"Repository path does not exist: {mock_repo_path}")

    def test_execute_worker_with_directories_success(self, mock_settings):
        """Test successful worker execution with directories."""
        executor = Executor(Path("/tmp/repo"))

        mock_subdir = MagicMock()
        mock_subdir.is_dir.return_value = True
        mock_subdir.name = "test_repo"

        mock_repo_path = MagicMock()
        mock_repo_path.exists.return_value = True
        mock_repo_path.iterdir.return_value = [mock_subdir]
        mock_repo_path.__str__ = lambda self: "/tmp/repo"

        executor.repo_path = mock_repo_path

        mock_worker_class = MagicMock()
        mock_worker_class.__name__ = "TestWorker"
        mock_worker_instance = MagicMock()
        mock_worker_instance.run.return_value = {"success": True}

        with patch("auto_slopp.executor.settings", mock_settings):
            with patch.object(executor, "_instantiate_worker", return_value=mock_worker_instance):
                with patch("builtins.print"):
                    executor._execute_worker_with_directories(mock_worker_class)

                    mock_worker_instance.run.assert_called_once()

    def test_execute_worker_with_directories_worker_exception(self, mock_settings):
        """Test worker execution handles worker exceptions."""
        executor = Executor(Path("/tmp/repo"))

        mock_subdir = MagicMock()
        mock_subdir.is_dir.return_value = True
        mock_subdir.name = "test_repo"

        mock_repo_path = MagicMock()
        mock_repo_path.exists.return_value = True
        mock_repo_path.iterdir.return_value = [mock_subdir]
        mock_repo_path.__str__ = lambda self: "/tmp/repo"

        executor.repo_path = mock_repo_path

        mock_worker_class = MagicMock()
        mock_worker_class.__name__ = "TestWorker"
        mock_worker_instance = MagicMock()
        mock_worker_instance.run.side_effect = RuntimeError("Worker error")

        with patch("auto_slopp.executor.settings", mock_settings):
            with patch.object(executor, "_instantiate_worker", return_value=mock_worker_instance):
                with patch("builtins.print"):
                    executor._execute_worker_with_directories(mock_worker_class)

    def test_check_for_updates_update_detected(self, mock_settings):
        """Test update detection when update is available."""
        executor = Executor(Path("/tmp/repo"))

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Updating 123..456"

        with patch("subprocess.run", return_value=mock_result):
            with patch.object(executor, "_schedule_reboot") as mock_reboot:
                result = executor._check_for_updates()

                assert result is True
                mock_reboot.assert_called_once()

    def test_check_for_updates_fast_forward(self, mock_settings):
        """Test update detection with fast-forward."""
        executor = Executor(Path("/tmp/repo"))

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Fast-forward"

        with patch("subprocess.run", return_value=mock_result):
            with patch.object(executor, "_schedule_reboot"):
                result = executor._check_for_updates()

                assert result is True

    def test_check_for_updates_already_up_to_date(self, mock_settings):
        """Test update detection when already up to date."""
        executor = Executor(Path("/tmp/repo"))

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Already up to date."

        with patch("subprocess.run", return_value=mock_result):
            result = executor._check_for_updates()

            assert result is False

    def test_check_for_updates_git_pull_failed(self, mock_settings):
        """Test update detection when git pull fails."""
        executor = Executor(Path("/tmp/repo"))

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error"

        with patch("subprocess.run", return_value=mock_result):
            result = executor._check_for_updates()

            assert result is False

    def test_check_for_updates_exception(self, mock_settings):
        """Test update detection handles exceptions."""
        executor = Executor(Path("/tmp/repo"))

        with patch("subprocess.run", side_effect=OSError("Test error")):
            result = executor._check_for_updates()

            assert result is False

    def test_schedule_reboot(self, mock_settings):
        """Test scheduling a reboot."""
        executor = Executor(Path("/tmp/repo"))

        with patch.object(executor, "_execute_reboot") as mock_reboot:
            with patch("time.sleep"):
                executor._schedule_reboot(1)

                mock_reboot.assert_called_once()

    def test_schedule_reboot_zero_delay(self, mock_settings):
        """Test scheduling a reboot with zero delay."""
        executor = Executor(Path("/tmp/repo"))

        with patch.object(executor, "_execute_reboot") as mock_reboot:
            executor._schedule_reboot(0)

            mock_reboot.assert_called_once()

    def test_execute_reboot(self, mock_settings):
        """Test executing reboot."""
        executor = Executor(Path("/tmp/repo"))

        with patch("subprocess.run") as mock_run:
            executor._execute_reboot()

            mock_run.assert_called_once_with(["reboot"], check=True)

    def test_execute_reboot_exception(self, mock_settings):
        """Test executing reboot handles exceptions."""
        executor = Executor(Path("/tmp/repo"))

        with patch("subprocess.run", side_effect=RuntimeError("Reboot failed")):
            with patch("traceback.print_exc"):
                executor._execute_reboot()

    def test_instantiate_worker(self, mock_settings):
        """Test worker instantiation."""
        executor = Executor(Path("/tmp/repo"))

        mock_worker_class = MagicMock()

        with patch("auto_slopp.executor.settings", mock_settings):
            executor._instantiate_worker(mock_worker_class)

            mock_worker_class.assert_called_once()

    def test_start_method_keyboard_interrupt(self, mock_settings):
        """Test start method handles KeyboardInterrupt."""
        executor = Executor(Path("/tmp/repo"))

        call_count = 0

        def first_success_then_interrupt():
            nonlocal call_count
            call_count += 1
            if call_count > 1:
                raise KeyboardInterrupt()

        with patch("auto_slopp.executor.settings", mock_settings):
            with patch.object(executor, "_run_iteration", side_effect=first_success_then_interrupt):
                with patch.object(executor, "_check_for_updates", return_value=False):
                    with patch("builtins.print") as mock_print:
                        with patch("time.sleep"):
                            executor.start()

                            assert executor.running is False
                            mock_print.assert_any_call("\nReceived interrupt signal, shutting down...")

    def test_start_method_exception(self, mock_settings):
        """Test start method handles exceptions."""
        executor = Executor(Path("/tmp/repo"))

        with patch("auto_slopp.executor.settings", mock_settings):
            with patch.object(
                executor,
                "_run_iteration",
                side_effect=RuntimeError("Fatal error"),
            ):
                with patch("builtins.print"):
                    with patch("traceback.print_exc"):
                        executor.start()

                        assert executor.running is False


class TestRunExecutor:
    """Tests for run_executor function."""

    def test_run_executor_default_path(self, mock_settings):
        """Test run_executor uses default repo path from settings."""
        from auto_slopp.executor import run_executor

        mock_settings.base_repo_path = Path("/default/repo")
        mock_settings.workers_disabled = []
        mock_settings.executor_sleep_interval = 3600

        executor_instance = MagicMock()

        with patch("auto_slopp.executor.Executor", return_value=executor_instance) as mock_executor_class:
            with patch.object(executor_instance, "start", side_effect=KeyboardInterrupt):
                with patch("auto_slopp.executor.settings", mock_settings):
                    try:
                        run_executor()
                    except KeyboardInterrupt:
                        pass

                    mock_executor_class.assert_called_once_with(repo_path=Path("/default/repo"))

    def test_run_executor_custom_path(self, mock_settings):
        """Test run_executor uses custom repo path."""
        from auto_slopp.executor import run_executor

        mock_settings.workers_disabled = []
        mock_settings.executor_sleep_interval = 3600

        executor_instance = MagicMock()

        with patch("auto_slopp.executor.Executor", return_value=executor_instance) as mock_executor_class:
            with patch.object(executor_instance, "start", side_effect=KeyboardInterrupt):
                try:
                    run_executor(repo_path=Path("/custom/repo"))
                except KeyboardInterrupt:
                    pass

                mock_executor_class.assert_called_once_with(repo_path=Path("/custom/repo"))
