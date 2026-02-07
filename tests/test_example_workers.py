"""Tests for example Worker implementations."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from auto_slopp.example_workers import (
    BeadsTaskWorker,
    DirectoryScanner,
    FileMonitor,
    HeartbeatWorker,
    OpenAgentWorker,
    SimpleLogger,
    TaskProcessor,
)


class TestSimpleLogger:
    """Test cases for SimpleLogger worker."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        worker = SimpleLogger()
        assert worker.name == "SimpleLogger"
        assert worker.logger is not None

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        worker = SimpleLogger("CustomLogger")
        assert worker.name == "CustomLogger"

    def test_run_with_existing_paths(self, tmp_path):
        """Test running with existing repository and task paths."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        task_path = tmp_path / "task"
        task_path.mkdir()

        worker = SimpleLogger()
        result = worker.run(repo_path, task_path)

        assert result["worker_name"] == "SimpleLogger"
        assert result["repo_path"] == str(repo_path)
        assert result["task_path"] == str(task_path)
        assert result["repo_exists"] is True
        assert result["task_exists"] is True
        assert result["execution_time"] > 0
        assert "timestamp" in result

    def test_run_with_nonexistent_paths(self):
        """Test running with non-existent paths."""
        repo_path = Path("/nonexistent/repo")
        task_path = Path("/nonexistent/task")

        worker = SimpleLogger()
        result = worker.run(repo_path, task_path)

        assert result["repo_exists"] is False
        assert result["task_exists"] is False
        assert result["file_count"] == 0


class TestFileMonitor:
    """Test cases for FileMonitor worker."""

    def test_init_default(self):
        """Test initialization with default file patterns."""
        worker = FileMonitor()
        assert "*.py" in worker.file_patterns
        assert "*.md" in worker.file_patterns

    def test_init_custom_patterns(self):
        """Test initialization with custom file patterns."""
        patterns = ["*.txt", "*.log"]
        worker = FileMonitor(patterns)
        assert worker.file_patterns == patterns

    def test_run_with_files(self, tmp_path):
        """Test running with files in repository."""
        # Create test files
        (tmp_path / "test.py").write_text("print('hello')")
        (tmp_path / "readme.md").write_text("# Test")
        (tmp_path / "data.json").write_text('{"key": "value"}')

        worker = FileMonitor(["*.py", "*.md"])
        result = worker.run(tmp_path, Path("dummy_task"))

        assert result["worker_name"] == "FileMonitor"
        assert result["total_files_found"] == 2
        assert result["file_breakdown"]["*.py"]["count"] == 1
        assert result["file_breakdown"]["*.md"]["count"] == 1
        assert result["file_breakdown"]["*.py"]["size_bytes"] > 0

    def test_run_with_nonexistent_repo(self):
        """Test running with non-existent repository."""
        worker = FileMonitor()
        result = worker.run(Path("/nonexistent"), Path("dummy_task"))

        assert "error" in result
        assert result["repo_path"] == "/nonexistent"


class TestTaskProcessor:
    """Test cases for TaskProcessor worker."""

    def test_init_default(self):
        """Test initialization with default file size limit."""
        worker = TaskProcessor()
        assert worker.max_file_size == 10 * 1024 * 1024  # 10MB

    def test_init_custom_size(self):
        """Test initialization with custom file size limit."""
        worker = TaskProcessor(1024)  # 1KB
        assert worker.max_file_size == 1024

    def test_run_single_file(self, tmp_path):
        """Test processing a single file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!\nLine 2\nLine 3")

        worker = TaskProcessor()
        result = worker.run(tmp_path, test_file)

        assert result["worker_name"] == "TaskProcessor"
        assert result["total_files_processed"] == 1
        assert len(result["processed_files"]) == 1

        file_info = result["processed_files"][0]
        assert file_info["file_path"] == str(test_file)
        assert file_info["file_type"] == ".txt"
        assert file_info["line_count"] == 3
        assert "Hello, World!" in file_info["content_preview"]

    def test_run_directory(self, tmp_path):
        """Test processing a directory with multiple files."""
        (tmp_path / "file1.py").write_text("print('hello')")
        (tmp_path / "file2.md").write_text("# Title")

        worker = TaskProcessor()
        result = worker.run(tmp_path, tmp_path)

        assert result["total_files_processed"] == 2
        assert len(result["processed_files"]) == 2

    def test_run_with_large_file(self, tmp_path):
        """Test processing a file that exceeds size limit."""
        # Create a large file (smaller than our test limit)
        worker = TaskProcessor(100)  # 100 byte limit
        large_file = tmp_path / "large.txt"
        large_file.write_text("x" * 200)  # 200 bytes

        result = worker.run(tmp_path, large_file)

        file_info = result["processed_files"][0]
        assert "too large" in file_info["error"].lower()

    def test_run_nonexistent_task(self):
        """Test processing non-existent task path."""
        worker = TaskProcessor()
        result = worker.run(Path("/dummy/repo"), Path("/nonexistent/task"))

        assert "error" in result
        assert "does not exist" in result["error"]

    def test_binary_file_handling(self, tmp_path):
        """Test handling of binary files."""
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03\x04")

        worker = TaskProcessor()
        result = worker.run(tmp_path, binary_file)

        file_info = result["processed_files"][0]
        assert file_info["file_type"] == ".bin"
        # Binary files should either have line_count as None or 1 (since counting lines on binary content is unreliable)
        assert file_info["line_count"] in [None, 1]


class TestHeartbeatWorker:
    """Test cases for HeartbeatWorker."""

    def test_init_default(self):
        """Test initialization with default message."""
        worker = HeartbeatWorker()
        assert "Auto-slopp is running" in worker.message

    def test_init_custom_message(self):
        """Test initialization with custom message."""
        message = "Custom heartbeat"
        worker = HeartbeatWorker(message)
        assert worker.message == message

    def test_run(self, tmp_path):
        """Test running heartbeat worker."""
        worker = HeartbeatWorker("Test heartbeat")
        result = worker.run(tmp_path / "repo", tmp_path / "task")

        assert result["worker_name"] == "HeartbeatWorker"
        assert result["message"] == "Test heartbeat"
        assert result["repo_path"] == str(tmp_path / "repo")
        assert result["task_path"] == str(tmp_path / "task")
        assert "timestamp" in result
        assert result["timestamp"] is not None


class TestDirectoryScanner:
    """Test cases for DirectoryScanner worker."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        worker = DirectoryScanner()
        assert worker.include_hidden is False
        assert worker.max_depth is None
        assert worker.logger is not None

    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        worker = DirectoryScanner(include_hidden=True, max_depth=3)
        assert worker.include_hidden is True
        assert worker.max_depth == 3

    def test_run_with_directory_structure(self, tmp_path):
        """Test scanning a directory structure."""
        # Create test directory structure
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "docs").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')")
        (tmp_path / "src" / "utils.py").write_text("def helper(): pass")
        (tmp_path / "tests" / "test_main.py").write_text("def test(): pass")
        (tmp_path / "docs" / "readme.md").write_text("# Documentation")
        (tmp_path / ".git").mkdir()  # Hidden directory
        (tmp_path / ".git" / "config").write_text("git config")

        worker = DirectoryScanner(include_hidden=False)
        result = worker.run(tmp_path, Path("dummy_task"))

        assert result["worker_name"] == "DirectoryScanner"
        assert result["total_directories"] >= 3  # src, tests, docs
        assert result["total_files"] >= 4
        assert result["total_size_bytes"] > 0
        assert ".py" in result["file_types"]
        assert ".md" in result["file_types"]
        assert result["directory_analysis"]["root_subdirs"] >= 3

    def test_run_with_hidden_files(self, tmp_path):
        """Test scanning with hidden files included."""
        (tmp_path / "visible.txt").write_text("visible")
        (tmp_path / ".hidden").write_text("hidden")
        (tmp_path / ".git").mkdir()

        worker = DirectoryScanner(include_hidden=True)
        result = worker.run(tmp_path, Path("dummy_task"))

        assert result["total_files"] >= 2  # visible + hidden
        assert result["total_directories"] >= 1  # .git

    def test_run_with_depth_limit(self, tmp_path):
        """Test scanning with depth limit."""
        # Create nested structure
        (tmp_path / "level1").mkdir()
        (tmp_path / "level1" / "level2").mkdir()
        (tmp_path / "level1" / "level2" / "level3").mkdir()
        (tmp_path / "level1" / "file.txt").write_text("content")
        (tmp_path / "level1" / "level2" / "file2.txt").write_text("content2")
        (tmp_path / "level1" / "level2" / "level3" / "file3.txt").write_text("content3")

        worker = DirectoryScanner(max_depth=2)
        result = worker.run(tmp_path, Path("dummy_task"))

        # Should find level1 and level2 files but not level3
        file_paths = [f["path"] for f in result["files"]]
        assert "level1/file.txt" in file_paths
        assert "level1/level2/file2.txt" in file_paths
        assert "level1/level2/level3/file3.txt" not in file_paths

    def test_run_nonexistent_repo(self):
        """Test scanning non-existent repository."""
        worker = DirectoryScanner()
        result = worker.run(Path("/nonexistent"), Path("dummy_task"))

        assert "error" in result
        assert "does not exist" in result["error"]

    def test_run_file_instead_of_directory(self, tmp_path):
        """Test scanning when repo_path is a file."""
        test_file = tmp_path / "not_a_dir.txt"
        test_file.write_text("content")

        worker = DirectoryScanner()
        result = worker.run(test_file, Path("dummy_task"))

        assert "error" in result
        assert "not a directory" in result["error"]


class TestBeadsTaskWorker:
    """Test cases for BeadsTaskWorker worker."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        worker = BeadsTaskWorker()
        assert worker.include_in_progress is False
        assert worker.priority_filter is None
        assert worker.logger is not None

    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        worker = BeadsTaskWorker(include_in_progress=True, priority_filter=1)
        assert worker.include_in_progress is True
        assert worker.priority_filter == 1

    @patch("subprocess.run")
    def test_check_beads_availability_success(self, mock_run):
        """Test successful beads availability check."""
        mock_run.return_value.returncode = 0

        worker = BeadsTaskWorker()
        available = worker._check_beads_availability(Path("/tmp"))

        assert available is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_check_beads_availability_failure(self, mock_run):
        """Test failed beads availability check."""
        mock_run.return_value.returncode = 1

        worker = BeadsTaskWorker()
        available = worker._check_beads_availability(Path("/tmp"))

        assert available is False

    @patch("subprocess.run")
    def test_get_ready_tasks_success(self, mock_run):
        """Test successful ready tasks retrieval."""
        mock_response = [
            {"id": "task1", "title": "Test Task", "status": "open", "priority": 2},
            {"id": "task2", "title": "Another Task", "status": "open", "priority": 1},
        ]
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps(mock_response)

        worker = BeadsTaskWorker()
        tasks = worker._get_ready_tasks()

        assert len(tasks) == 2
        assert tasks[0]["id"] == "task1"
        assert tasks[1]["id"] == "task2"

    @patch("subprocess.run")
    def test_get_ready_tasks_with_filters(self, mock_run):
        """Test ready tasks retrieval with filters applied."""
        mock_response = [
            {"id": "task1", "title": "Test Task", "status": "open", "priority": 2},
            {"id": "task2", "title": "High Priority", "status": "open", "priority": 1},
            {"id": "task3", "title": "In Progress", "status": "in_progress", "priority": 2},
        ]
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps(mock_response)

        # Test priority filter
        worker = BeadsTaskWorker(priority_filter=1)
        tasks = worker._get_ready_tasks()

        assert len(tasks) == 1
        assert tasks[0]["id"] == "task2"

        # Test include_in_progress filter
        worker = BeadsTaskWorker(include_in_progress=True)
        tasks = worker._get_ready_tasks()

        assert len(tasks) == 3  # All tasks included

    @patch("subprocess.run")
    def test_get_ready_tasks_command_failure(self, mock_run):
        """Test ready tasks retrieval when command fails."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error occurred"

        worker = BeadsTaskWorker()
        tasks = worker._get_ready_tasks()

        assert len(tasks) == 0

    @patch("subprocess.run")
    def test_get_open_tasks_success(self, mock_run):
        """Test successful open tasks retrieval."""
        mock_response = [
            {"id": "open1", "title": "Open Task", "status": "open", "priority": 2},
            {"id": "open2", "title": "Another Open", "status": "open", "priority": 3},
        ]
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps(mock_response)

        worker = BeadsTaskWorker()
        tasks = worker._get_open_tasks()

        assert len(tasks) == 2
        assert tasks[0]["id"] == "open1"

    def test_analyze_tasks(self):
        """Test task analysis functionality."""
        all_tasks = [
            {"id": "task1", "status": "open", "priority": 2, "issue_type": "task"},
            {"id": "task2", "status": "in_progress", "priority": 1, "issue_type": "bug"},
            {"id": "task3", "status": "open", "priority": 1, "issue_type": "feature"},
        ]
        ready_tasks = [
            {"id": "task1", "status": "open", "priority": 2, "issue_type": "task"},
            {"id": "task3", "status": "open", "priority": 1, "issue_type": "feature"},
        ]

        worker = BeadsTaskWorker()
        analysis = worker._analyze_tasks(all_tasks, ready_tasks)

        assert analysis["status_breakdown"]["open"] == 2
        assert analysis["status_breakdown"]["in_progress"] == 1
        assert analysis["priority_breakdown"][1] == 2  # Two priority 1 tasks
        assert analysis["priority_breakdown"][2] == 1  # One priority 2 task
        assert analysis["type_breakdown"]["task"] == 1
        assert analysis["type_breakdown"]["bug"] == 1
        assert analysis["type_breakdown"]["feature"] == 1
        assert analysis["readiness_percentage"] == 66.67  # 2/3 * 100
        assert analysis["high_priority_ready_count"] == 1  # One priority 1 ready task

    @patch("subprocess.run")
    def test_run_with_beads_available(self, mock_run):
        """Test running worker when beads is available."""
        # Mock beads availability check
        mock_run.return_value.returncode = 0

        # Mock ready tasks response
        ready_tasks = [{"id": "task1", "title": "Test", "status": "open", "priority": 2}]
        mock_run.return_value.stdout = json.dumps(ready_tasks)

        worker = BeadsTaskWorker()
        result = worker.run(Path("/tmp"), Path("dummy_task"))

        assert result["worker_name"] == "BeadsTaskWorker"
        assert result["beads_available"] is True
        assert result["ready_tasks_count"] == 1
        assert result["total_open_tasks"] == 1

    @patch("subprocess.run")
    def test_run_without_beads_available(self, mock_run):
        """Test running worker when beads is not available."""
        # Mock beads availability check failure
        mock_run.return_value.returncode = 1

        worker = BeadsTaskWorker()
        result = worker.run(Path("/tmp"), Path("dummy_task"))

        assert result["worker_name"] == "BeadsTaskWorker"
        assert "error" in result
        assert "not available" in result["error"]


class TestOpenAgentWorker:
    """Test cases for OpenAgentWorker worker."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        worker = OpenAgentWorker()
        assert worker.agent_args == []
        assert worker.timeout == 300
        assert worker.capture_output is True
        assert worker.working_dir is None
        assert worker.logger is not None

    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        args = ["--help", "--verbose"]
        work_dir = Path("/custom/dir")
        worker = OpenAgentWorker(agent_args=args, timeout=60, capture_output=False, working_dir=work_dir)
        assert worker.agent_args == args
        assert worker.timeout == 60
        assert worker.capture_output is False
        assert worker.working_dir == work_dir

    @patch("subprocess.run")
    def test_run_success(self, mock_run):
        """Test successful OpenAgent execution."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "OpenAgent output"
        mock_run.return_value.stderr = ""

        worker = OpenAgentWorker(agent_args=["--version"])
        result = worker.run(Path("/tmp"), Path("dummy_task"))

        assert result["worker_name"] == "OpenAgentWorker"
        assert result["success"] is True
        assert result["return_code"] == 0
        assert result["stdout"] == "OpenAgent output"
        assert result["timeout"] is False
        assert "openagent --version" in result["command"]

    @patch("subprocess.run")
    def test_run_with_task_path(self, mock_run):
        """Test running with task path included in command."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Success"
        mock_run.return_value.stderr = ""

        task_path = Path("/tmp/task_file.txt")
        task_path.write_text("task content")  # Create the file

        worker = OpenAgentWorker(agent_args=["--process"])
        result = worker.run(Path("/tmp"), task_path)

        # Check that task path was added to command
        assert str(task_path) in result["command"]
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]  # Get the command list
        assert str(task_path) in call_args

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run):
        """Test OpenAgent execution with non-zero return code."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "Error message"

        worker = OpenAgentWorker()
        result = worker.run(Path("/tmp"), Path("dummy_task"))

        assert result["success"] is False
        assert result["return_code"] == 1
        assert result["stderr"] == "Error message"

    @patch("subprocess.run")
    def test_run_timeout(self, mock_run):
        """Test OpenAgent execution timeout."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("openagent", 300)

        worker = OpenAgentWorker(timeout=300)
        result = worker.run(Path("/tmp"), Path("dummy_task"))

        assert result["success"] is False
        assert result["timeout"] is True
        assert "timed out" in result["error"]

    @patch("subprocess.run")
    def test_run_command_not_found(self, mock_run):
        """Test OpenAgent execution when command is not found."""
        mock_run.side_effect = FileNotFoundError()

        worker = OpenAgentWorker()
        result = worker.run(Path("/tmp"), Path("dummy_task"))

        assert result["success"] is False
        assert result["return_code"] == -1
        assert "not found" in result["error"]

    @patch("subprocess.run")
    def test_run_with_custom_working_dir(self, mock_run):
        """Test OpenAgent execution with custom working directory."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Success"
        mock_run.return_value.stderr = ""

        custom_dir = Path("/custom/working/dir")
        worker = OpenAgentWorker(working_dir=custom_dir)
        result = worker.run(Path("/tmp"), Path("dummy_task"))

        assert result["working_directory"] == str(custom_dir)
        mock_run.assert_called_once()
        # Verify the working directory was passed correctly
        assert mock_run.call_args[1]["cwd"] == custom_dir

    @patch("subprocess.run")
    def test_run_without_output_capture(self, mock_run):
        """Test OpenAgent execution without output capture."""
        mock_run.return_value.returncode = 0

        worker = OpenAgentWorker(capture_output=False)
        result = worker.run(Path("/tmp"), Path("dummy_task"))

        assert result["success"] is True
        assert "stdout" not in result
        assert "stderr" not in result
        assert "stdout_lines" not in result
        assert "stderr_lines" not in result

    @patch("subprocess.run")
    def test_run_with_exception(self, mock_run):
        """Test OpenAgent execution with unexpected exception."""
        mock_run.side_effect = Exception("Unexpected error")

        worker = OpenAgentWorker()
        result = worker.run(Path("/tmp"), Path("dummy_task"))

        assert result["success"] is False
        assert result["return_code"] == -1
        assert "Unexpected error" in result["error"]
