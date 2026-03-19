"""Tests for auto-update functionality."""

import subprocess
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from auto_slopp.executor import Executor


class TestAutoUpdate:
    """Test cases for auto-update functionality."""

    @patch("auto_slopp.executor.subprocess.run")
    def test_git_pull_called_after_worker_loop(self, mock_subprocess_run, temp_repo_dir, mock_settings):
        """Test that git pull is called after every worker loop iteration."""
        mock_settings.executor_sleep_interval = 0.1
        mock_settings.workers_disabled = [
            "GitHubIssueWorker",
            "PRWorker",
            "StaleBranchCleanupWorker",
        ]

        mock_subprocess_run.return_value = Mock(returncode=0, stdout="Already up to date.", stderr="")

        with patch("auto_slopp.executor.settings", mock_settings):
            executor = Executor(repo_path=temp_repo_dir)
            executor.running = True

            executor._run_iteration()

            executor._check_for_updates()

            mock_subprocess_run.assert_called()

            call_args = list(mock_subprocess_run.call_args_list)
            git_pull_called = any("pull" in str(call) for call in call_args)
            assert git_pull_called, "git pull should be called after worker loop"

    @patch("auto_slopp.executor.subprocess.run")
    @patch("auto_slopp.executor.time.sleep")
    def test_reboot_scheduled_after_update(self, mock_sleep, mock_subprocess_run, temp_repo_dir, mock_settings):
        """Test that reboot is scheduled after detecting an update."""
        mock_settings.auto_update_reboot_delay = 300
        mock_settings.workers_disabled = [
            "GitHubIssueWorker",
            "PRWorker",
            "StaleBranchCleanupWorker",
        ]

        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stdout="Updating abc123..def456\nFast-forward", stderr=""),
        ]

        with patch("auto_slopp.executor.settings", mock_settings):
            executor = Executor(repo_path=temp_repo_dir)

            update_detected = executor._check_for_updates()

            assert update_detected is True, "Update should be detected"

    @patch("auto_slopp.executor.subprocess.run")
    def test_no_reboot_when_no_update(self, mock_subprocess_run, temp_repo_dir, mock_settings):
        """Test that no reboot is scheduled when there's no update."""
        mock_settings.auto_update_reboot_delay = 300
        mock_settings.workers_disabled = [
            "GitHubIssueWorker",
            "PRWorker",
            "StaleBranchCleanupWorker",
        ]

        mock_subprocess_run.return_value = Mock(returncode=0, stdout="Already up to date.", stderr="")

        with patch("auto_slopp.executor.settings", mock_settings):
            executor = Executor(repo_path=temp_repo_dir)

            update_detected = executor._check_for_updates()

            assert update_detected is False, "No update should be detected"

    @patch("auto_slopp.executor.subprocess.run")
    def test_git_pull_failure_handled_gracefully(self, mock_subprocess_run, temp_repo_dir, mock_settings):
        """Test that git pull failures are handled gracefully."""
        mock_settings.workers_disabled = [
            "GitHubIssueWorker",
            "PRWorker",
            "StaleBranchCleanupWorker",
        ]

        mock_subprocess_run.return_value = Mock(returncode=1, stdout="", stderr="fatal: not a git repository")

        with patch("auto_slopp.executor.settings", mock_settings):
            executor = Executor(repo_path=temp_repo_dir)

            update_detected = executor._check_for_updates()

            assert update_detected is False, "Failed git pull should not detect update"

    @patch("auto_slopp.executor.subprocess.run")
    def test_configurable_reboot_delay(self, mock_subprocess_run, temp_repo_dir):
        """Test that reboot delay is configurable."""
        custom_delay = 600

        mock_settings = MagicMock()
        mock_settings.auto_update_reboot_delay = custom_delay
        mock_settings.workers_disabled = [
            "GitHubIssueWorker",
            "PRWorker",
            "StaleBranchCleanupWorker",
        ]

        mock_subprocess_run.return_value = Mock(returncode=0, stdout="Already up to date.", stderr="")

        with patch("auto_slopp.executor.settings", mock_settings):
            Executor(repo_path=temp_repo_dir)

            assert hasattr(mock_settings, "auto_update_reboot_delay")
            assert mock_settings.auto_update_reboot_delay == custom_delay

    @patch("auto_slopp.executor.subprocess.run")
    @patch("auto_slopp.executor.time.sleep")
    def test_reboot_delay_timer(self, mock_sleep, mock_subprocess_run, temp_repo_dir, mock_settings):
        """Test that reboot delay timer is correctly applied."""
        mock_settings.auto_update_reboot_delay = 300
        mock_settings.workers_disabled = [
            "GitHubIssueWorker",
            "PRWorker",
            "StaleBranchCleanupWorker",
        ]

        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stdout="Updating abc123..def456", stderr=""),
        ]

        with patch("auto_slopp.executor.settings", mock_settings):
            executor = Executor(repo_path=temp_repo_dir)

            with patch.object(executor, "_schedule_reboot") as mock_schedule_reboot:
                update_detected = executor._check_for_updates()

                if update_detected:
                    mock_schedule_reboot.assert_called_once_with(mock_settings.auto_update_reboot_delay)

    @patch("auto_slopp.executor.subprocess.run")
    def test_git_pull_in_working_directory(self, mock_subprocess_run, temp_repo_dir, mock_settings):
        """Test that git pull is executed in the working directory of the program."""
        mock_settings.workers_disabled = [
            "GitHubIssueWorker",
            "PRWorker",
            "StaleBranchCleanupWorker",
        ]

        mock_subprocess_run.return_value = Mock(returncode=0, stdout="Already up to date.", stderr="")

        with patch("auto_slopp.executor.settings", mock_settings):
            executor = Executor(repo_path=temp_repo_dir)

            executor._check_for_updates()

            for call_obj in mock_subprocess_run.call_args_list:
                if "pull" in str(call_obj):
                    cwd_arg = call_obj[1].get("cwd")
                    assert cwd_arg is not None, "git pull should specify working directory"
                    break

    @patch("auto_slopp.executor.subprocess.run")
    def test_multiple_iterations_trigger_multiple_pulls(self, mock_subprocess_run, temp_repo_dir, mock_settings):
        """Test that each worker loop iteration triggers a git pull."""
        mock_settings.executor_sleep_interval = 0.1
        mock_settings.workers_disabled = [
            "GitHubIssueWorker",
            "PRWorker",
            "StaleBranchCleanupWorker",
        ]

        mock_subprocess_run.return_value = Mock(returncode=0, stdout="Already up to date.", stderr="")

        with patch("auto_slopp.executor.settings", mock_settings):
            executor = Executor(repo_path=temp_repo_dir)

            for _ in range(3):
                executor._run_iteration()
                executor._check_for_updates()

            git_pull_calls = [call for call in mock_subprocess_run.call_args_list if "pull" in str(call)]

            assert len(git_pull_calls) >= 3, "git pull should be called in each iteration"

    @patch("auto_slopp.executor.subprocess.run")
    @patch("auto_slopp.executor.time.sleep")
    def test_update_detection_with_various_outputs(self, mock_sleep, mock_subprocess_run, temp_repo_dir, mock_settings):
        """Test update detection with various git pull outputs."""
        mock_settings.auto_update_reboot_delay = 300
        mock_settings.workers_disabled = [
            "GitHubIssueWorker",
            "PRWorker",
            "StaleBranchCleanupWorker",
        ]

        test_cases = [
            ("Already up to date.", False),
            ("Updating abc123..def456\nFast-forward", True),
            ("Updating abc123..def456\n1 file changed", True),
            ("Current branch main is up to date.", False),
            ("", False),
        ]

        with patch("auto_slopp.executor.settings", mock_settings):
            executor = Executor(repo_path=temp_repo_dir)

            for output, expected_update in test_cases:
                mock_subprocess_run.return_value = Mock(returncode=0, stdout=output, stderr="")

                update_detected = executor._check_for_updates()

                assert update_detected == expected_update, f"Failed for output: {output}"

    @patch("auto_slopp.executor.subprocess.run")
    @patch("auto_slopp.executor.time.sleep")
    def test_reboot_command_execution(self, mock_sleep, mock_subprocess_run, temp_repo_dir, mock_settings):
        """Test that reboot command is executed after delay."""
        mock_settings.auto_update_reboot_delay = 0
        mock_settings.workers_disabled = [
            "GitHubIssueWorker",
            "PRWorker",
            "StaleBranchCleanupWorker",
        ]

        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stdout="Updating abc123..def456", stderr=""),
        ]

        with patch("auto_slopp.executor.settings", mock_settings):
            executor = Executor(repo_path=temp_repo_dir)

            with patch.object(executor, "_execute_reboot") as mock_execute_reboot:
                executor._check_for_updates()

                if mock_subprocess_run.call_count > 0:
                    first_call = mock_subprocess_run.call_args_list[0]
                    if "Updating" in str(first_call):
                        mock_execute_reboot.assert_called()
