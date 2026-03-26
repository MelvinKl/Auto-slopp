"""Tests for VikunjaWorker thin wrapper."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from auto_slopp.workers.issue_worker import IssueWorker
from auto_slopp.workers.vikunja_task_source import VikunjaTaskSource
from auto_slopp.workers.vikunja_worker import VikunjaWorker


class TestVikunjaWorker:
    """Tests for VikunjaWorker."""

    def test_initialization_creates_internal_worker(self):
        """Test that initialization creates internal IssueWorker with VikunjaTaskSource."""
        worker = VikunjaWorker(
            timeout=7200,
            agent_args=["--verbose"],
            dry_run=True,
        )

        assert hasattr(worker, "_worker")
        assert isinstance(worker._worker, IssueWorker)
        assert isinstance(worker._worker.task_source, VikunjaTaskSource)

    def test_run_delegates_to_internal_worker(self):
        """Test that run() delegates to internal IssueWorker."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            worker = VikunjaWorker(dry_run=True)

            with patch.object(
                worker._worker,
                "run",
                return_value={"success": True, "tasks_processed": 1},
            ) as mock_run:
                result = worker.run(repo_path)

                mock_run.assert_called_once_with(repo_path)
                assert result == {"success": True, "tasks_processed": 1}

    def test_initialization_with_defaults(self):
        """Test that initialization uses default values."""
        worker = VikunjaWorker()

        assert hasattr(worker, "_worker")
        assert isinstance(worker._worker, IssueWorker)
        assert isinstance(worker._worker.task_source, VikunjaTaskSource)

    def test_dry_run_passed_to_internal_worker(self):
        """Test that dry_run is passed to internal IssueWorker."""
        worker = VikunjaWorker(dry_run=True)

        assert worker._worker.dry_run is True

    def test_timeout_passed_to_internal_worker(self):
        """Test that timeout is passed to internal IssueWorker."""
        worker = VikunjaWorker(timeout=7200)

        assert worker._worker.timeout == 7200

    def test_agent_args_passed_to_internal_worker(self):
        """Test that agent_args are passed to internal IssueWorker."""
        worker = VikunjaWorker(agent_args=["--verbose", "--debug"])

        assert worker._worker.agent_args == ["--verbose", "--debug"]
