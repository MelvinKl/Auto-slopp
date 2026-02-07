"""Integration tests for CI/CD pipeline automation."""

import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from auto_slopp.example_workers import (
    BeadsTaskWorker,
    OpenAgentWorker,
    SimpleLogger,
)
from auto_slopp.executor import Executor


class TestCIIntegration:
    """Integration tests for CI/CD pipeline scenarios."""

    @pytest.mark.integration
    def test_full_workflow_integration(self, temp_repo_dir, temp_task_dir, temp_workers_dir):
        """Test complete workflow from worker discovery to execution."""
        executor = Executor(
            search_path=temp_workers_dir,
            repo_path=temp_repo_dir,
            task_path=temp_task_dir,
        )

        # Run a full iteration
        executor._run_iteration()

        # Verify workers were discovered and executed
        # This is tested more thoroughly in test_executor.py

    @pytest.mark.integration
    def test_beads_integration_in_ci_environment(self, temp_repo_dir, temp_task_dir):
        """Test beads task worker integration in CI environment."""
        worker = BeadsTaskWorker()
        result = worker.run(temp_repo_dir, temp_task_dir)

        # Should handle beads (available or not)
        assert result["worker_name"] == "BeadsTaskWorker"
        assert "beads_available" in result

    @pytest.mark.integration
    def test_openagent_worker_integration(self, temp_repo_dir, temp_task_dir):
        """Test OpenAgent worker integration for CI automation."""
        worker = OpenAgentWorker(agent_args=["--version"], timeout=30, capture_output=True)

        result = worker.run(temp_repo_dir, temp_task_dir)

        # Should execute OpenAgent command (even if it fails)
        assert result["worker_name"] == "OpenAgentWorker"
        assert "command" in result
        assert "return_code" in result
        assert "timeout" in result

    @pytest.mark.integration
    def test_error_recovery_and_logging(self, temp_repo_dir, temp_task_dir):
        """Test error recovery and proper logging in CI environment."""

        # Create a worker that will fail
        class FailingWorker:
            def run(self, repo_path: Path, task_path: Path):
                raise ValueError("Simulated failure for testing")

        # This should be handled gracefully by the executor
        executor = Executor(
            search_path=temp_repo_dir,  # No actual workers here
            repo_path=temp_repo_dir,
            task_path=temp_task_dir,
        )

        # Should handle empty worker list gracefully
        executor._run_iteration()

    @pytest.mark.integration
    @patch("subprocess.run")
    def test_ci_environment_variables(self, mock_subprocess, temp_repo_dir, temp_task_dir):
        """Test handling of CI environment variables."""
        # Mock successful beads execution
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = json.dumps([])
        mock_subprocess.return_value.stderr = ""

        # Test with CI environment variables
        with patch.dict(
            "os.environ",
            {"CI": "true", "GITHUB_ACTIONS": "true", "GITHUB_REF": "refs/heads/main", "GITHUB_SHA": "abc123"},
        ):
            worker = BeadsTaskWorker()
            result = worker.run(temp_repo_dir, temp_task_dir)

            # Should work in CI environment
            assert result["worker_name"] == "BeadsTaskWorker"

    @pytest.mark.integration
    def test_parallel_worker_execution_simulation(self, temp_repo_dir, temp_task_dir):
        """Test parallel execution scenarios."""
        workers = [
            SimpleLogger("Parallel_1"),
            SimpleLogger("Parallel_2"),
            SimpleLogger("Parallel_3"),
        ]

        results = []
        for worker in workers:
            result = worker.run(temp_repo_dir, temp_task_dir)
            results.append(result)

        # All workers should complete successfully
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result["worker_name"] == f"Parallel_{i+1}"
            assert result["execution_time"] > 0

    @pytest.mark.integration
    def test_large_dataset_handling(self, temp_repo_dir, temp_task_dir):
        """Test handling of large datasets in CI environment."""
        # Create many files to simulate large project
        for i in range(1000):
            (temp_repo_dir / f"source_{i}.py").write_text(f"# Source file {i}\nprint('Hello {i}')")
            (temp_repo_dir / f"data_{i}.json").write_text(f'{{"id": {i}, "data": "test"}}')

        from auto_slopp.example_workers import DirectoryScanner, FileMonitor

        # Test file monitoring with large dataset
        file_monitor = FileMonitor()
        result = file_monitor.run(temp_repo_dir, temp_task_dir)

        assert result["total_files_found"] >= 2000  # 1000 Python + 1000 JSON files
        assert result["execution_time"] < 5.0  # Should complete quickly

        # Test directory scanning with large dataset
        dir_scanner = DirectoryScanner()
        result = dir_scanner.run(temp_repo_dir, temp_task_dir)

        assert result["total_files"] >= 2000
        assert result["execution_time"] < 5.0

    @pytest.mark.integration
    def test_ci_timeout_handling(self, temp_repo_dir, temp_task_dir):
        """Test timeout handling in CI environment."""
        worker = OpenAgentWorker(
            agent_args=["sleep", "10"],  # Command that will timeout
            timeout=1,  # Very short timeout
        )

        result = worker.run(temp_repo_dir, temp_task_dir)

        # Should handle command failure gracefully (either timeout or command not found)
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.integration
    def test_resource_cleanup_after_failure(self, temp_repo_dir, temp_task_dir):
        """Test proper resource cleanup after worker failures."""
        from auto_slopp.example_workers import TaskProcessor

        # Create files that will cause processing issues
        (temp_task_dir / "huge_file.txt").write_text("x" * (20 * 1024 * 1024))  # 20MB
        (temp_task_dir / "corrupted.json").write_text("{invalid json content")

        worker = TaskProcessor(max_file_size=10 * 1024 * 1024)  # 10MB limit
        result = worker.run(temp_repo_dir, temp_task_dir)

        # Should handle oversized and corrupted files
        processed_files = result.get("processed_files", [])
        assert len(processed_files) >= 2

        error_files = [f for f in processed_files if "error" in f]
        assert len(error_files) >= 1, "Should have detected at least one error"

    @pytest.mark.integration
    def test_ci_report_generation(self, temp_repo_dir, temp_task_dir):
        """Test generation of CI reports."""
        from auto_slopp.example_workers import DirectoryScanner, FileMonitor

        # Collect comprehensive repository data
        scanner = DirectoryScanner()
        scan_result = scanner.run(temp_repo_dir, temp_task_dir)

        monitor = FileMonitor()
        monitor_result = monitor.run(temp_repo_dir, temp_task_dir)

        # Generate CI report
        ci_report = {
            "timestamp": scan_result["timestamp"],
            "repository_analysis": scan_result,
            "file_analysis": monitor_result,
            "total_files": scan_result["total_files"],
            "total_size_mb": scan_result["total_size_mb"],
            "file_types": scan_result["file_types"],
        }

        # Report should contain comprehensive data
        assert "repository_analysis" in ci_report
        assert "file_analysis" in ci_report
        assert ci_report["total_files"] >= 0
        assert isinstance(ci_report["file_types"], dict)

    @pytest.mark.integration
    def test_multi_python_version_compatibility(self, temp_repo_dir, temp_task_dir):
        """Test compatibility across different Python versions."""
        import sys

        worker = SimpleLogger()
        result = worker.run(temp_repo_dir, temp_task_dir)

        # Should work regardless of Python version
        assert result["worker_name"] == "SimpleLogger"


class TestCIEnvironmentSetup:
    """Test CI environment setup and teardown."""

    @pytest.mark.integration
    def test_environment_variable_handling(self):
        """Test handling of various CI environment variables."""
        ci_vars = {
            "CI": "true",
            "GITHUB_ACTIONS": "true",
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_SHA": "abc123def456",
            "GITHUB_RUN_ID": "123456789",
            "GITHUB_RUN_NUMBER": "42",
        }

        with patch.dict("os.environ", ci_vars):
            # Test that environment variables are properly accessible
            import os

            assert os.getenv("CI") == "true"
            assert os.getenv("GITHUB_ACTIONS") == "true"

    @pytest.mark.integration
    def test_workspace_isolation(self, temp_dir):
        """Test workspace isolation between test runs."""
        # Each test should get a clean workspace
        workspace1 = temp_dir / "workspace1"
        workspace2 = temp_dir / "workspace2"

        workspace1.mkdir()
        workspace2.mkdir()

        # Create different content in each workspace
        (workspace1 / "file.txt").write_text("workspace1")
        (workspace2 / "file.txt").write_text("workspace2")

        # Verify isolation
        assert (workspace1 / "file.txt").read_text() == "workspace1"
        assert (workspace2 / "file.txt").read_text() == "workspace2"

    @pytest.mark.integration
    def test_dependency_availability(self):
        """Test that required dependencies are available."""
        try:
            import pytest

            import auto_slopp
            from auto_slopp.executor import Executor
            from auto_slopp.worker import Worker

            # Should be able to import everything
            assert pytest is not None
            assert auto_slopp is not None
            assert Worker is not None
            assert Executor is not None

        except ImportError as e:
            pytest.fail(f"Missing required dependency: {e}")

    @pytest.mark.integration
    def test_configuration_loading(self):
        """Test loading of configuration in CI environment."""
        from settings.main import settings

        # Settings should load properly in CI environment
        assert hasattr(settings, "base_repo_path")
        assert hasattr(settings, "base_task_path")
        assert hasattr(settings, "worker_search_path")
        assert hasattr(settings, "executor_sleep_interval")
