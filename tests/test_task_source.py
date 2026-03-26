"""Tests for TaskSource ABC and Task dataclass."""

from pathlib import Path
from typing import List

from auto_slopp.workers.task_source import Task, TaskSource


class ConcreteTaskSource(TaskSource):
    """Concrete implementation for testing the ABC."""

    def get_tasks(self, repo_path: Path) -> List[Task]:
        return [Task(id=1, title="Test", body="body")]

    def get_branch_name(self, task: Task) -> str:
        return f"ai/test-{task.id}"

    def get_ralph_file_prefix(self) -> str:
        return "test"

    def get_task_difficulty_name(self) -> str:
        return "test_task"

    def get_default_pr_body(self, task: Task) -> str:
        return f"PR for {task.title}"

    def on_task_start(self, task: Task, branch_name: str) -> None:
        pass

    def on_task_complete(self, task: Task, branch_name: str, pr_url: str) -> None:
        pass

    def on_task_failure(self, task: Task, error: str) -> None:
        pass

    def on_no_changes(self, task: Task) -> None:
        pass

    def on_max_iterations_reached(self, task: Task, steps_completed: int, total_steps: int, error: str) -> None:
        pass


class TestTask:
    """Tests for the Task dataclass."""

    def test_task_creation_with_all_fields(self):
        task = Task(
            id=42,
            title="Fix bug",
            body="There is a bug",
            comments=["comment1", "comment2"],
            raw={"number": 42, "extra": "data"},
        )
        assert task.id == 42
        assert task.title == "Fix bug"
        assert task.body == "There is a bug"
        assert task.comments == ["comment1", "comment2"]
        assert task.raw == {"number": 42, "extra": "data"}

    def test_task_creation_with_defaults(self):
        task = Task(id=1, title="Test", body="body")
        assert task.id == 1
        assert task.title == "Test"
        assert task.body == "body"
        assert task.comments == []
        assert task.raw == {}

    def test_task_default_lists_are_independent(self):
        task1 = Task(id=1, title="A", body="a")
        task2 = Task(id=2, title="B", body="b")
        task1.comments.append("x")
        assert task2.comments == []
        task1.raw["key"] = "val"
        assert task2.raw == {}


class TestTaskSource:
    """Tests for the TaskSource ABC."""

    def test_concrete_implementation_can_be_instantiated(self):
        source = ConcreteTaskSource()
        assert isinstance(source, TaskSource)

    def test_get_tasks_returns_list(self):
        source = ConcreteTaskSource()
        tasks = source.get_tasks(Path("/tmp"))
        assert len(tasks) == 1
        assert tasks[0].id == 1

    def test_get_branch_name(self):
        source = ConcreteTaskSource()
        task = Task(id=5, title="My Task", body="")
        assert source.get_branch_name(task) == "ai/test-5"

    def test_get_ralph_file_prefix(self):
        source = ConcreteTaskSource()
        assert source.get_ralph_file_prefix() == "test"

    def test_get_task_difficulty_name(self):
        source = ConcreteTaskSource()
        assert source.get_task_difficulty_name() == "test_task"

    def test_get_default_pr_body(self):
        source = ConcreteTaskSource()
        task = Task(id=1, title="Fix it", body="")
        assert source.get_default_pr_body(task) == "PR for Fix it"

    def test_cannot_instantiate_abc_directly(self):
        import pytest

        with pytest.raises(TypeError):
            TaskSource()  # type: ignore[abstract]

    def test_incomplete_implementation_cannot_be_instantiated(self):
        import pytest

        class IncompleteSource(TaskSource):
            def get_tasks(self, repo_path: Path) -> List[Task]:
                return []

        with pytest.raises(TypeError):
            IncompleteSource()  # type: ignore[abstract]
