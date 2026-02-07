"""Tests for Worker base class."""

from pathlib import Path

import pytest

from auto_slopp.worker import Worker


class TestWorkerBase:
    """Test cases for the Worker base class."""

    def test_worker_is_abstract(self):
        """Test that Worker cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Worker()

    def test_worker_subclass_can_be_instantiated(self):
        """Test that a concrete subclass of Worker can be instantiated."""

        class ConcreteWorker(Worker):
            def run(self, repo_path: Path, task_path: Path):
                return {"status": "completed"}

        worker = ConcreteWorker()
        assert worker is not None
        assert hasattr(worker, "run")

    def test_worker_run_method_signature(self):
        """Test that worker run method has correct signature."""

        class TestWorker(Worker):
            def run(self, repo_path: Path, task_path: Path):
                return {"repo": str(repo_path), "task": str(task_path)}

        worker = TestWorker()
        repo_path = Path("/test/repo")
        task_path = Path("/test/task")

        result = worker.run(repo_path, task_path)

        assert isinstance(result, dict)
        assert result["repo"] == str(repo_path)
        assert result["task"] == str(task_path)

    def test_worker_can_return_any_type(self):
        """Test that worker run method can return any type."""

        class StringWorker(Worker):
            def run(self, repo_path: Path, task_path: Path):
                return "string result"

        class NoneWorker(Worker):
            def run(self, repo_path: Path, task_path: Path):
                return None

        class ListWorker(Worker):
            def run(self, repo_path: Path, task_path: Path):
                return [1, 2, 3]

        repo_path = Path("/test/repo")
        task_path = Path("/test/task")

        string_worker = StringWorker()
        assert string_worker.run(repo_path, task_path) == "string result"

        none_worker = NoneWorker()
        assert none_worker.run(repo_path, task_path) is None

        list_worker = ListWorker()
        assert list_worker.run(repo_path, task_path) == [1, 2, 3]

    def test_worker_can_have_custom_init(self):
        """Test that workers can have custom initialization."""

        class ConfigurableWorker(Worker):
            def __init__(self, name: str, enabled: bool = True):
                self.name = name
                self.enabled = enabled

            def run(self, repo_path: Path, task_path: Path):
                if not self.enabled:
                    return {"status": "disabled"}
                return {"name": self.name, "status": "completed"}

        worker = ConfigurableWorker("test_worker", enabled=True)
        result = worker.run(Path("/test"), Path("/test"))

        assert result["name"] == "test_worker"
        assert result["status"] == "completed"

        disabled_worker = ConfigurableWorker("disabled_worker", enabled=False)
        result = disabled_worker.run(Path("/test"), Path("/test"))

        assert result["status"] == "disabled"

    def test_worker_can_handle_path_parameters(self, temp_repo_dir, temp_task_dir):
        """Test that workers can properly handle Path parameters."""

        class PathWorker(Worker):
            def run(self, repo_path: Path, task_path: Path):
                return {
                    "repo_exists": repo_path.exists(),
                    "task_exists": task_path.exists(),
                    "repo_is_dir": repo_path.is_dir(),
                    "task_is_dir": task_path.is_dir(),
                    "repo_name": repo_path.name,
                    "task_name": task_path.name,
                }

        worker = PathWorker()
        result = worker.run(temp_repo_dir, temp_task_dir)

        assert result["repo_exists"] is True
        assert result["task_exists"] is True
        assert result["repo_is_dir"] is True
        assert result["task_is_dir"] is True
        assert result["repo_name"] == temp_repo_dir.name
        assert result["task_name"] == temp_task_dir.name

    def test_worker_can_raise_exceptions(self):
        """Test that workers can raise exceptions during execution."""

        class ErrorWorker(Worker):
            def run(self, repo_path: Path, task_path: Path):
                raise ValueError("Test error")

        worker = ErrorWorker()

        with pytest.raises(ValueError, match="Test error"):
            worker.run(Path("/test"), Path("/test"))

    def test_worker_can_import_and_use_dependencies(self, temp_repo_dir, temp_task_dir):
        """Test that workers can import and use external dependencies."""

        class JsonWorker(Worker):
            def run(self, repo_path: Path, task_path: Path):
                import json

                # Create a JSON result
                result = {"repo_path": str(repo_path), "task_path": str(task_path), "timestamp": "2024-01-01T00:00:00Z"}

                # Serialize to JSON and back
                json_str = json.dumps(result)
                return json.loads(json_str)

        worker = JsonWorker()
        result = worker.run(temp_repo_dir, temp_task_dir)

        assert isinstance(result, dict)
        assert "repo_path" in result
        assert "task_path" in result
        assert "timestamp" in result
