"""Performance benchmarking tests for Auto-slopp components."""

import time
from pathlib import Path
from typing import Any, Dict, List

import pytest

from auto_slopp.example_workers import (
    BeadsTaskWorker,
    DirectoryScanner,
    FileMonitor,
    SimpleLogger,
    TaskProcessor,
)
from auto_slopp.executor import Executor


class TestPerformanceBenchmarks:
    """Performance benchmarking tests for worker components."""

    @pytest.mark.performance
    def test_simple_logger_performance(self, temp_repo_dir, temp_task_dir):
        """Benchmark SimpleLogger worker performance."""
        worker = SimpleLogger()

        start_time = time.perf_counter()
        result = worker.run(temp_repo_dir, temp_task_dir)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        result_time = result["execution_time"]

        # Performance assertions
        assert execution_time < 1.0, f"SimpleLogger took {execution_time:.3f}s, should be < 1.0s"
        assert result_time < 1.0, f"SimpleLogger reported {result_time:.3f}s, should be < 1.0s"
        assert abs(execution_time - result_time) < 0.1, "Reported time should match actual time"

    @pytest.mark.performance
    def test_file_monitor_performance(self, temp_repo_dir, temp_task_dir):
        """Benchmark FileMonitor worker performance."""
        # Create more files to test with
        for i in range(100):
            (temp_repo_dir / f"test_{i}.py").write_text(f"print('test {i}')")
            (temp_repo_dir / f"doc_{i}.md").write_text(f"# Document {i}")

        worker = FileMonitor()

        start_time = time.perf_counter()
        result = worker.run(temp_repo_dir, temp_task_dir)
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Performance assertions - should handle 200+ files quickly
        assert execution_time < 2.0, f"FileMonitor took {execution_time:.3f}s for 200+ files, should be < 2.0s"
        assert result["total_files_found"] >= 200, f"Expected >=200 files, found {result['total_files_found']}"

    @pytest.mark.performance
    def test_directory_scanner_performance(self, temp_repo_dir, temp_task_dir):
        """Benchmark DirectoryScanner worker performance."""
        # Create nested directory structure
        for i in range(10):
            subdir = temp_repo_dir / f"subdir_{i}"
            subdir.mkdir()
            for j in range(10):
                (subdir / f"file_{j}.txt").write_text(f"Content {i}_{j}")
                subsubdir = subdir / f"nested_{j}"
                subsubdir.mkdir()
                for k in range(5):
                    (subsubdir / f"deep_{k}.py").write_text(f"# Deep file {i}_{j}_{k}")

        worker = DirectoryScanner()

        start_time = time.perf_counter()
        result = worker.run(temp_repo_dir, temp_task_dir)
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Performance assertions - should handle 600+ files across 100+ directories
        assert (
            execution_time < 3.0
        ), f"DirectoryScanner took {execution_time:.3f}s for complex structure, should be < 3.0s"
        assert result["total_files"] >= 600, f"Expected >=600 files, found {result['total_files']}"
        assert result["total_directories"] >= 100, f"Expected >=100 directories, found {result['total_directories']}"

    @pytest.mark.performance
    def test_task_processor_performance(self, temp_repo_dir, temp_task_dir):
        """Benchmark TaskProcessor worker performance."""
        # Create many task files
        for i in range(50):
            (temp_task_dir / f"task_{i}.json").write_text('{{"task": "{}", "data": "x" * 1000}}'.format(i))
            (temp_task_dir / f"note_{i}.txt").write_text(f"Note {i}: " + "y" * 500)

        worker = TaskProcessor(max_file_size=10 * 1024)  # 10KB limit

        start_time = time.perf_counter()
        result = worker.run(temp_repo_dir, temp_task_dir)
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Performance assertions
        assert execution_time < 2.0, f"TaskProcessor took {execution_time:.3f}s for 100+ files, should be < 2.0s"
        assert (
            result["total_files_processed"] >= 100
        ), f"Expected >=100 files, processed {result['total_files_processed']}"

    @pytest.mark.performance
    def test_executor_performance(self, temp_repo_dir, temp_task_dir, temp_workers_dir):
        """Benchmark Executor performance with multiple workers."""
        executor = Executor(
            search_path=temp_workers_dir,
            repo_path=temp_repo_dir,
            task_path=temp_task_dir,
        )

        start_time = time.perf_counter()
        executor._run_iteration()  # Run single iteration
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Performance assertions - single iteration should be fast
        assert execution_time < 1.0, f"Executor iteration took {execution_time:.3f}s, should be < 1.0s"

    @pytest.mark.performance
    def test_beads_task_worker_performance(self, temp_repo_dir, temp_task_dir):
        """Benchmark BeadsTaskWorker performance."""
        worker = BeadsTaskWorker()

        start_time = time.perf_counter()
        result = worker.run(temp_repo_dir, temp_task_dir)
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Performance assertions - should complete quickly even if beads unavailable
        assert execution_time < 2.0, f"BeadsTaskWorker took {execution_time:.3f}s, should be < 2.0s"

    @pytest.mark.performance
    def test_memory_usage_large_file_processing(self, temp_repo_dir, temp_task_dir):
        """Test memory efficiency with large files."""
        # Create a large file (but within our processing limits)
        large_content = "x" * (5 * 1024 * 1024)  # 5MB
        large_file = temp_task_dir / "large_file.txt"
        large_file.write_text(large_content)

        worker = TaskProcessor(max_file_size=10 * 1024 * 1024)  # 10MB limit

        start_time = time.perf_counter()
        result = worker.run(temp_repo_dir, temp_task_dir)
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Should handle large files efficiently
        assert execution_time < 1.0, f"Large file processing took {execution_time:.3f}s, should be < 1.0s"
        assert result["total_size_mb"] >= 5, f"Expected >=5MB, found {result['total_size_mb']}MB"

    def test_concurrent_worker_simulation(self, temp_repo_dir, temp_task_dir):
        """Simulate concurrent worker execution to test for race conditions."""
        workers = [
            SimpleLogger("Logger_1"),
            FileMonitor(),
            DirectoryScanner(),
        ]

        results = []
        start_time = time.perf_counter()

        # Simulate concurrent execution (in series since we can't easily test true concurrency)
        for worker in workers:
            result = worker.run(temp_repo_dir, temp_task_dir)
            results.append(result)

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # All workers should complete successfully
        assert len(results) == 3
        for result in results:
            assert result.get("worker_name") is not None
            assert result.get("execution_time", 0) > 0

        # Total time should be reasonable
        assert total_time < 5.0, f"Concurrent simulation took {total_time:.3f}s, should be < 5.0s"

    def test_scalability_deep_directory_structure(self, temp_repo_dir, temp_task_dir):
        """Test performance with very deep directory structures."""
        # Create a deeply nested structure
        current = temp_repo_dir
        max_depth = 20

        for i in range(max_depth):
            current = current / f"level_{i}"
            current.mkdir()
            (current / f"file_{i}.py").write_text(f"# File at level {i}")

        worker = DirectoryScanner(max_depth=None)

        start_time = time.perf_counter()
        result = worker.run(temp_repo_dir, temp_task_dir)
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Should handle deep structures efficiently
        assert execution_time < 2.0, f"Deep structure scan took {execution_time:.3f}s, should be < 2.0s"
        assert result["directory_analysis"]["max_depth"] >= max_depth

    def test_error_handling_performance(self, temp_repo_dir, temp_task_dir):
        """Test that error handling doesn't significantly impact performance."""
        # Create some problematic files
        (temp_task_dir / "bad_json.json").write_text("{invalid json}")
        (temp_task_dir / "binary_file.bin").write_bytes(b"\x00\x01\x02\x03\x04")

        # Also create a file that's too large
        (temp_task_dir / "huge_file.txt").write_text("x" * (15 * 1024 * 1024))  # 15MB

        worker = TaskProcessor(max_file_size=10 * 1024 * 1024)  # 10MB limit

        start_time = time.perf_counter()
        result = worker.run(temp_repo_dir, temp_task_dir)
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Should handle errors gracefully without major performance impact
        assert execution_time < 1.0, f"Error handling took {execution_time:.3f}s, should be < 1.0s"

        # Should report errors properly
        processed_files = result.get("processed_files", [])
        error_files = [f for f in processed_files if "error" in f]
        assert len(error_files) > 0, "Should have detected and reported errors"
