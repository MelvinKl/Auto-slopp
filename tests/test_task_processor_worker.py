"""Tests for the TaskProcessorWorker.

This module contains comprehensive tests for the TaskProcessorWorker,
including unit tests for individual methods and integration tests
for the complete workflow.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from auto_slopp.workers.task_processor_worker import TaskProcessorWorker


class TestTaskProcessorWorker:
    """Test suite for TaskProcessorWorker."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.repo_path = self.temp_dir / "repos"
        self.task_repo_path = self.temp_dir / "task_repos"

        self.repo_path.mkdir()
        self.task_repo_path.mkdir()

        self.worker = TaskProcessorWorker(
            task_repo_path=self.task_repo_path,
            counter_start=1,
            timeout=300,
            dry_run=True,  # Use dry run for tests
        )

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_init(self):
        """Test TaskProcessorWorker initialization."""
        worker = TaskProcessorWorker(
            task_repo_path=self.task_repo_path,
            counter_start=10,
            timeout=600,
            agent_args=["--verbose"],
            dry_run=False,
        )

        assert worker.task_repo_path == self.task_repo_path
        assert worker.counter_start == 10
        assert worker.timeout == 600
        assert worker.agent_args == ["--verbose"]
        assert worker.dry_run is False
        assert worker.process_all_repos is True

    def test_get_agent_instructions(self):
        """Test get_agent_instructions method."""
        instructions = self.worker.get_agent_instructions()
        assert instructions == ""

    def test_run_with_nonexistent_repo_path(self):
        """Test run method with nonexistent repo_path."""
        nonexistent_path = self.temp_dir / "nonexistent"
        result = self.worker.run(nonexistent_path, self.temp_dir / "task")

        assert result["success"] is False
        assert "Repository path does not exist" in result["error"]
        assert result["repositories_processed"] == 0

    def test_run_with_nonexistent_task_repo_path(self):
        """Test run method with nonexistent task_repo_path."""
        nonexistent_task_path = self.temp_dir / "nonexistent_task"
        # TaskProcessorWorker creates the directory in __init__, so we need to test differently
        with patch("pathlib.Path.mkdir", side_effect=OSError("Permission denied")):
            with pytest.raises(OSError):
                TaskProcessorWorker(nonexistent_task_path)

    def test_process_repository_success(self):
        """Test successful repository processing."""
        # Create a test repository with a text file
        test_repo = self.repo_path / "test_repo"
        test_repo.mkdir()
        # Initialize as git repository to be considered valid
        (test_repo / ".git").mkdir()
        (test_repo / ".git" / "config").write_text("[core]\n\trepositoryformatversion = 0\n")

        text_file = test_repo / "instructions.txt"
        text_file.write_text("Test instruction content")

        result = self.worker._process_repository(test_repo)

        assert result["success"] is True
        assert result["repository"] == "test_repo"
        assert result["text_files_processed"] == 1
        assert result["files_renamed"] == 1
        assert len(result["processed_files"]) == 1
        assert len(result["errors"]) == 0

    def test_process_repository_no_text_files(self):
        """Test repository processing with no text files."""
        test_repo = self.repo_path / "test_repo"
        test_repo.mkdir()

        # Create a non-text file
        (test_repo / "README.md").write_text("# Test README")

        result = self.worker._process_repository(test_repo)

        assert result["success"] is True
        assert result["text_files_processed"] == 0
        assert result["files_renamed"] == 0
        assert len(result["processed_files"]) == 0

    def test_process_repository_empty_text_file(self):
        """Test repository processing with empty text file."""
        test_repo = self.repo_path / "test_repo"
        test_repo.mkdir()
        # Initialize as git repository to be considered valid
        (test_repo / ".git").mkdir()
        (test_repo / ".git" / "config").write_text("[core]\n\trepositoryformatversion = 0\n")

        # Create empty text file
        text_file = test_repo / "empty.txt"
        text_file.write_text("")

        result = self.worker._process_repository(test_repo)

        # Repository processing fails due to empty file error
        assert result["success"] is False
        assert len(result["processed_files"]) == 1
        assert result["processed_files"][0]["success"] is False
        assert "empty" in result["processed_files"][0]["error"].lower()

    def test_find_text_files(self):
        """Test text file discovery."""
        test_repo = self.repo_path / "test_repo"
        test_repo.mkdir()

        # Create test files
        (test_repo / "file1.txt").write_text("Content 1")
        (test_repo / "file2.txt").write_text("Content 2")
        (test_repo / "not_txt.md").write_text("Markdown")

        # Create subdirectory with text file
        subdir = test_repo / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("Content 3")

        text_files = self.worker._find_text_files(test_repo)

        assert len(text_files) == 3
        assert any(f.name == "file1.txt" for f in text_files)
        assert any(f.name == "file2.txt" for f in text_files)
        assert any(f.name == "file3.txt" for f in text_files)

    def test_process_text_file_success(self):
        """Test successful text file processing."""
        test_repo = self.repo_path / "test_repo"
        test_repo.mkdir()

        task_repo_dir = self.task_repo_path / "test_repo"
        task_repo_dir.mkdir()

        text_file = test_repo / "instructions.txt"
        text_file.write_text("Test instruction content")

        result = self.worker._process_text_file(text_file, task_repo_dir)

        assert result["success"] is True
        assert result["instructions"] == "Test instruction content"
        assert result["openagent_executed"] is True  # dry run
        assert result["file_renamed"] is True
        assert result["git_operations"] is True  # dry run

    def test_process_text_file_openagent_failure(self):
        """Test text file processing when OpenAgent fails."""
        # Create worker without dry run to mock actual failure
        worker = TaskProcessorWorker(
            task_repo_path=self.task_repo_path,
            dry_run=False,
        )

        test_repo = self.repo_path / "test_repo"
        test_repo.mkdir()

        task_repo_dir = self.task_repo_path / "test_repo"
        task_repo_dir.mkdir()

        text_file = test_repo / "instructions.txt"
        text_file.write_text("Test instruction content")

        # Mock OpenAgent execution to fail
        with patch.object(worker, "_execute_openagent_with_instructions") as mock_execute:
            mock_execute.return_value = {"success": False, "error": "OpenAgent failed"}

            result = worker._process_text_file(text_file, task_repo_dir)

            assert result["success"] is False
            assert "OpenAgent failed" in result["error"]
            assert result["openagent_executed"] is False

    def test_rename_processed_file(self):
        """Test file renaming with counter."""
        test_repo = self.repo_path / "test_repo"
        test_repo.mkdir()

        original_file = test_repo / "original.txt"
        original_file.write_text("Content")

        renamed_file = self.worker._rename_processed_file(original_file)

        assert renamed_file is not None
        assert renamed_file.name.startswith("0001_")
        assert renamed_file.name.endswith(".used.txt")
        assert "original" in renamed_file.name
        assert not original_file.exists()
        assert renamed_file.exists()

    def test_get_next_counter_no_existing_files(self):
        """Test counter generation when no existing files."""
        counter = self.worker._get_next_counter(self.repo_path)
        assert counter == 1

    def test_get_next_counter_with_existing_files(self):
        """Test counter generation with existing files."""
        test_repo = self.repo_path / "test_repo"
        test_repo.mkdir()

        # Create existing used files
        (test_repo / "0001_file1.used.txt").write_text("Content 1")
        (test_repo / "0003_file2.used.txt").write_text("Content 2")

        counter = self.worker._get_next_counter(test_repo)
        assert counter == 4  # Should be max existing + 1

    def test_commit_and_push_changes_success(self):
        """Test successful git commit and push operations."""
        # Create worker without dry run
        worker = TaskProcessorWorker(
            task_repo_path=self.task_repo_path,
            dry_run=False,
        )

        task_repo_dir = self.task_repo_path / "test_repo"
        task_repo_dir.mkdir()

        # Mock git operations
        with patch("subprocess.run") as mock_run:
            # Mock git status to show changes
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "M file.txt"

            result = worker._commit_and_push_changes(task_repo_dir, "test.txt")

            assert result is True
            # Verify git commands were called
            assert mock_run.call_count >= 3  # add, status, commit

    def test_commit_and_push_changes_no_changes(self):
        """Test git commit when no changes exist."""
        # Create worker without dry run
        worker = TaskProcessorWorker(
            task_repo_path=self.task_repo_path,
            dry_run=False,
        )

        task_repo_dir = self.task_repo_path / "test_repo"
        task_repo_dir.mkdir()

        # Mock git operations - no changes to commit
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""  # No changes

            result = worker._commit_and_push_changes(task_repo_dir, "test.txt")

            assert result is True
            # Should not call commit command
            commit_calls = [call for call in mock_run.call_args_list if "commit" in str(call)]
            assert len(commit_calls) == 0

    def test_commit_and_push_changes_git_failure(self):
        """Test git commit and push operations when git fails."""
        # Create worker without dry run
        worker = TaskProcessorWorker(
            task_repo_path=self.task_repo_path,
            dry_run=False,
        )

        task_repo_dir = self.task_repo_path / "test_repo"
        task_repo_dir.mkdir()

        # Mock git operations to fail
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "git")

            result = worker._commit_and_push_changes(task_repo_dir, "test.txt")

            assert result is False

    def test_run_integration(self):
        """Test complete integration run with multiple repositories."""
        # Create test repositories as git repos
        repo1 = self.repo_path / "repo1"
        repo2 = self.repo_path / "repo2"
        repo3 = self.repo_path / "repo3"

        for repo in [repo1, repo2, repo3]:
            repo.mkdir()
            # Initialize as git repository
            (repo / ".git").mkdir()
            (repo / ".git" / "config").write_text("[core]\n\trepositoryformatversion = 0\n")

        # Add text files to some repos
        (repo1 / "instructions1.txt").write_text("Instruction 1")
        (repo2 / "instructions2.txt").write_text("Instruction 2")
        # repo3 has no text files

        result = self.worker.run(self.repo_path, self.temp_dir / "task")

        assert result["success"] is True
        assert result["repositories_processed"] == 3
        assert result["text_files_processed"] == 2
        assert result["files_renamed"] == 2
        assert len(result["repository_results"]) == 3

    def test_create_error_result(self):
        """Test error result creation."""
        start_time = 1.0
        result = self.worker._create_error_result(start_time, self.repo_path, self.temp_dir / "task", "Test error")

        assert result["success"] is False
        assert result["error"] == "Test error"
        assert result["repositories_processed"] == 0
        assert result["execution_time"] >= 0

    def test_timing_functions(self):
        """Test timing helper functions."""
        start_time = self.worker._get_current_time()
        assert isinstance(start_time, float)

        # Small delay
        import time

        time.sleep(0.01)

        elapsed = self.worker._get_elapsed_time(start_time)
        assert elapsed > 0
        assert elapsed < 1.0  # Should be very short

    @patch("auto_slopp.workers.task_processor_worker.discover_repositories")
    def test_run_with_repository_discovery_failure(self, mock_discover):
        """Test run method when repository discovery fails."""
        mock_discover.side_effect = Exception("Discovery failed")

        with pytest.raises(Exception, match="Discovery failed"):
            self.worker.run(self.repo_path, self.temp_dir / "task")

    def test_process_text_file_with_large_instructions(self):
        """Test processing text file with very large instructions."""
        test_repo = self.repo_path / "test_repo"
        test_repo.mkdir()

        task_repo_dir = self.task_repo_path / "test_repo"
        task_repo_dir.mkdir()

        # Create large instruction file
        large_content = "Large instruction " * 10000  # Large content
        text_file = test_repo / "large_instructions.txt"
        text_file.write_text(large_content)

        result = self.worker._process_text_file(text_file, task_repo_dir)

        assert result["success"] is True
        # Note: .strip() removes trailing whitespace, so content length may differ
        assert len(result["instructions"]) > 0
        assert result["instructions"].startswith("Large instruction")
