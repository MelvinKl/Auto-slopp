"""Tests for Ralph loop implementation."""

import logging
import tempfile
from pathlib import Path

import pytest

from auto_slopp.utils.ralph import (
    Plan,
    PlanParser,
    PlanWriter,
    RalphExecutor,
    Step,
)


class TestStep:
    """Tests for Step class."""

    def test_step_creation(self):
        """Test creating a step."""
        step = Step(number=1, description="Test step", is_closed=False)
        assert step.number == 1
        assert step.description == "Test step"
        assert step.is_closed is False

    def test_step_to_markdown_line_open(self):
        """Test converting open step to markdown."""
        step = Step(number=1, description="Test step", is_closed=False)
        line = step.to_markdown_line()
        assert line == "- [ ] 1. Test step"

    def test_step_to_markdown_line_closed(self):
        """Test converting closed step to markdown."""
        step = Step(number=1, description="Test step", is_closed=True)
        line = step.to_markdown_line()
        assert line == "- [x] 1. Test step"

    def test_step_to_markdown_line_with_indent(self):
        """Test converting step with indent to markdown."""
        step = Step(number=1, description="Test step", is_closed=False, indent_level=2)
        line = step.to_markdown_line()
        assert line == "    - [ ] 1. Test step"

    def test_step_from_markdown_line_open(self):
        """Test parsing open step from markdown."""
        line = "- [ ] 1. Test step"
        step = Step.from_markdown_line(line)
        assert step is not None
        assert step.number == 1
        assert step.description == "Test step"
        assert step.is_closed is False

    def test_step_from_markdown_line_closed(self):
        """Test parsing closed step from markdown."""
        line = "- [x] 1. Test step"
        step = Step.from_markdown_line(line)
        assert step is not None
        assert step.number == 1
        assert step.description == "Test step"
        assert step.is_closed is True

    def test_step_from_markdown_line_with_indent(self):
        """Test parsing step with indent from markdown."""
        line = "  - [ ] 2. Nested step"
        step = Step.from_markdown_line(line)
        assert step is not None
        assert step.number == 2
        assert step.description == "Nested step"
        assert step.indent_level == 1

    def test_step_from_markdown_line_invalid(self):
        """Test parsing invalid markdown line."""
        assert Step.from_markdown_line("not a step") is None
        assert Step.from_markdown_line("") is None
        assert Step.from_markdown_line("- [ ] invalid") is None


class TestPlan:
    """Tests for Plan class."""

    def test_plan_creation(self):
        """Test creating a plan."""
        steps = [
            Step(number=1, description="Step 1"),
            Step(number=2, description="Step 2"),
        ]
        plan = Plan(title="Test Plan", description="A test plan", steps=steps)

        assert plan.title == "Test Plan"
        assert plan.description == "A test plan"
        assert len(plan.steps) == 2

    def test_get_open_steps(self):
        """Test getting open steps."""
        steps = [
            Step(number=1, description="Step 1", is_closed=True),
            Step(number=2, description="Step 2", is_closed=False),
            Step(number=3, description="Step 3", is_closed=False),
        ]
        plan = Plan(title="Test", description="", steps=steps)

        open_steps = plan.get_open_steps()
        assert len(open_steps) == 2
        assert open_steps[0].number == 2
        assert open_steps[1].number == 3

    def test_get_next_open_step(self):
        """Test getting next open step."""
        steps = [
            Step(number=1, description="Step 1", is_closed=True),
            Step(number=2, description="Step 2", is_closed=False),
        ]
        plan = Plan(title="Test", description="", steps=steps)

        next_step = plan.get_next_open_step()
        assert next_step is not None
        assert next_step.number == 2

    def test_get_next_open_step_all_closed(self):
        """Test getting next open step when all are closed."""
        steps = [
            Step(number=1, description="Step 1", is_closed=True),
            Step(number=2, description="Step 2", is_closed=True),
        ]
        plan = Plan(title="Test", description="", steps=steps)

        assert plan.get_next_open_step() is None

    def test_mark_step_closed(self):
        """Test marking a step as closed."""
        steps = [
            Step(number=1, description="Step 1", is_closed=False),
            Step(number=2, description="Step 2", is_closed=False),
        ]
        plan = Plan(title="Test", description="", steps=steps)

        result = plan.mark_step_closed(1)
        assert result is True
        assert plan.steps[0].is_closed is True
        assert plan.steps[1].is_closed is False

    def test_mark_step_closed_not_found(self):
        """Test marking a non-existent step as closed."""
        steps = [Step(number=1, description="Step 1")]
        plan = Plan(title="Test", description="", steps=steps)

        result = plan.mark_step_closed(99)
        assert result is False

    def test_all_steps_closed(self):
        """Test checking if all steps are closed."""
        steps = [
            Step(number=1, description="Step 1", is_closed=True),
            Step(number=2, description="Step 2", is_closed=True),
        ]
        plan = Plan(title="Test", description="", steps=steps)

        assert plan.all_steps_closed() is True

    def test_all_steps_closed_false(self):
        """Test checking if all steps are closed when some are open."""
        steps = [
            Step(number=1, description="Step 1", is_closed=True),
            Step(number=2, description="Step 2", is_closed=False),
        ]
        plan = Plan(title="Test", description="", steps=steps)

        assert plan.all_steps_closed() is False

    def test_to_markdown(self):
        """Test converting plan to markdown."""
        steps = [
            Step(number=1, description="Step 1", is_closed=True),
            Step(number=2, description="Step 2", is_closed=False),
        ]
        plan = Plan(title="Test Plan", description="A test plan", steps=steps)

        md = plan.to_markdown()

        assert "# Test Plan" in md
        assert "A test plan" in md
        assert "## Steps" in md
        assert "- [x] 1. Step 1" in md
        assert "- [ ] 2. Step 2" in md


class TestPlanParser:
    """Tests for PlanParser class."""

    def test_parse_content(self):
        """Test parsing plan content."""
        content = """# Test Plan

A test plan

## Steps

- [ ] 1. Step 1
- [x] 2. Step 2
- [ ] 3. Step 3
"""
        plan = PlanParser.parse_content(content)

        assert plan.title == "Test Plan"
        assert plan.description == "A test plan"
        assert len(plan.steps) == 3
        assert plan.steps[0].is_closed is False
        assert plan.steps[1].is_closed is True
        assert plan.steps[2].is_closed is False

    def test_parse_file(self):
        """Test parsing plan from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Plan\n\nDescription\n\n## Steps\n\n- [ ] 1. Step 1\n")
            f.flush()

            plan = PlanParser.parse_file(Path(f.name))
            assert plan.title == "Test Plan"
            assert len(plan.steps) == 1

    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        with pytest.raises(FileNotFoundError):
            PlanParser.parse_file(Path("/nonexistent/plan.md"))


class TestPlanWriter:
    """Tests for PlanWriter class."""

    def test_write_file(self):
        """Test writing plan to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_path = Path(tmpdir) / "plan.md"

            steps = [Step(number=1, description="Step 1")]
            plan = Plan(title="Test", description="Desc", steps=steps)

            PlanWriter.write_file(plan, plan_path)

            assert plan_path.exists()
            content = plan_path.read_text()
            assert "# Test" in content
            assert "Step 1" in content

    def test_write_file_creates_directories(self):
        """Test that write_file creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_path = Path(tmpdir) / "subdir" / "plan.md"

            steps = [Step(number=1, description="Step 1")]
            plan = Plan(title="Test", description="Desc", steps=steps)

            PlanWriter.write_file(plan, plan_path)

            assert plan_path.exists()
            assert plan_path.parent.is_dir()


class TestRalphExecutor:
    """Tests for RalphExecutor class."""

    @pytest.fixture
    def logger(self):
        """Create a test logger."""
        return logging.getLogger("test_ralph_executor")

    @pytest.fixture
    def mock_execute_fn(self):
        """Mock execute function."""
        return lambda *args, **kwargs: {"success": True, "stdout": "test output"}

    @pytest.fixture
    def mock_has_changes_fn(self):
        """Mock has_changes function."""
        return lambda path: False

    @pytest.fixture
    def mock_commit_fn(self):
        """Mock commit function."""
        return lambda path, msg, push: (True, None)

    @pytest.fixture
    def ralph_executor(
        self,
        logger,
        mock_execute_fn,
        mock_has_changes_fn,
        mock_commit_fn,
    ):
        """Create a RalphExecutor instance for testing."""
        return RalphExecutor(
            logger=logger,
            agent_args=[],
            timeout=60,
            execute_fn=mock_execute_fn,
            has_changes_fn=mock_has_changes_fn,
            commit_fn=mock_commit_fn,
            max_iterations=10,
        )

    def test_initialization(self, ralph_executor, logger):
        """Test RalphExecutor initialization."""
        assert ralph_executor.logger is logger
        assert ralph_executor.agent_args == []
        assert ralph_executor.timeout == 60
        assert ralph_executor.max_iterations == 10

    def test_get_issue_task_path(self):
        """Test static method _get_issue_task_path."""
        repo_dir = Path("/test/repo")
        task_path = RalphExecutor._get_issue_task_path(repo_dir, 123)
        expected = Path("/test/repo/.ralph/github-123.md")
        assert task_path == expected

    def test_create_issue_task_file(self, ralph_executor):
        """Test creating an issue task file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-123.md"

            ralph_executor._create_issue_task_file(
                task_path=task_path,
                issue_number=123,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=["Comment 1", "Comment 2"],
                branch_name="ai/branch-123",
            )

            assert task_path.exists()
            content = task_path.read_text()
            assert "Test Issue" in content
            assert "123" in content
            assert "ai/branch-123" in content
            assert "Test body" in content
            assert "Comment 1" in content
            assert "Comment 2" in content

    def test_mark_step_completed_in_file(self, ralph_executor):
        """Test marking a step as completed in a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. Step 1\n- [ ] 2. Step 2\n")

            ralph_executor._mark_step_completed_in_file(task_path, 1)

            content = task_path.read_text()
            assert "- [x] 1. Step 1" in content
            assert "- [ ] 2. Step 2" in content

    def test_extract_step_block(self, ralph_executor):
        """Test extracting a step block from task file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n- [ ] 2. Second step\n")

            block = ralph_executor._extract_step_block(task_path, 1)
            assert "- [ ] 1. First step" in block
            assert "Second step" not in block

    def test_find_step_description(self, ralph_executor):
        """Test finding step description."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n- [ ] 2. Second step\n")

            desc = ralph_executor._find_step_description(task_path, 1)
            assert desc == "First step"

            desc = ralph_executor._find_step_description(task_path, 999)
            assert desc == "Unknown step"

    def test_step_is_closed(self, ralph_executor):
        """Test checking if a step is closed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. First step\n- [ ] 2. Second step\n")

            assert ralph_executor._step_is_closed(task_path, 1) is True
            assert ralph_executor._step_is_closed(task_path, 2) is False
            assert ralph_executor._step_is_closed(task_path, 999) is False

    def test_ensure_last_step_is_make_test(self, ralph_executor):
        """Test ensuring last step is make test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"

            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n")

            ralph_executor._ensure_last_step_is_make_test(task_path)

            content = task_path.read_text()
            assert "make test" in content.lower()

    def test_ensure_last_step_is_make_test_already_present(self, ralph_executor):
        """Test ensuring last step is make test when already present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"

            original = "# Test\n\n## Steps\n\n- [ ] 1. First step\n- [ ] 2. Run make test\n"
            task_path.write_text(original)

            ralph_executor._ensure_last_step_is_make_test(task_path)

            content = task_path.read_text()
            assert content == original

    def test_build_progress_info(self, ralph_executor):
        """Test building progress info."""
        steps = [
            Step(number=1, description="Step 1", is_closed=True),
            Step(number=2, description="Step 2", is_closed=False),
        ]
        plan = Plan(title="Test", description="", steps=steps)

        progress = ralph_executor._build_progress_info(plan)

        assert "✓ Step 1: Step 1" in progress or "\u2713 Step 1: Step 1" in progress
        assert "○ Step 2: Step 2" in progress or "\u25cb Step 2: Step 2" in progress

    def test_build_refinement_instructions(self, ralph_executor):
        """Test building refinement instructions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"
            task_path.write_text("# Test")

            instructions = ralph_executor._build_refinement_instructions(
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=["Comment 1"],
                branch_name="ai/branch",
            )

            assert "Test Issue" in instructions
            assert "Test body" in instructions
            assert "Comment 1" in instructions
            assert "ai/branch" in instructions
            assert "## Steps" in instructions
            assert "make test" in instructions

    def test_build_step_instructions(self, ralph_executor):
        """Test building step instructions."""
        step = Step(number=1, description="Test step", is_closed=False)
        plan = Plan(title="Test", description="", steps=[step])

        instructions = ralph_executor._build_step_instructions(
            step=step,
            plan=plan,
            issue_title="Test Issue",
            issue_body="Test body",
            comment_texts=["Comment 1"],
            branch_name="ai/branch",
        )

        assert "Test Issue" in instructions
        assert "Test body" in instructions
        assert "Comment 1" in instructions
        assert "ai/branch" in instructions
        assert "Step 1: Test step" in instructions

    def test_build_acceptance_check_instructions(self, ralph_executor):
        """Test building acceptance check instructions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n")

            instructions = ralph_executor._build_acceptance_check_instructions(
                task_path=task_path,
                step=Step(number=1, description="First step"),
                issue_title="Test Issue",
                issue_body="Test body",
                branch_name="ai/branch",
            )

            assert "Test Issue" in instructions
            assert "ACCEPTANCE_STATUS" in instructions
            assert "First step" in instructions

    def test_build_remaining_steps_update_instructions(self, ralph_executor):
        """Test building remaining steps update instructions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n")

            instructions = ralph_executor._build_remaining_steps_update_instructions(
                task_path=task_path,
                step=Step(number=1, description="First step"),
                issue_title="Test Issue",
                issue_body="Test body",
                branch_name="ai/branch",
            )

            assert "Test Issue" in instructions
            assert "First step" in instructions
            assert "Update only unchecked steps" in instructions

    def test_update_issue_task_file(self, ralph_executor):
        """Test updating an existing issue task file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-123.md"
            task_path.parent.mkdir(parents=True, exist_ok=True)

            initial_content = "# Test\n\n## Steps\n\n- [x] 1. Completed step\n- [ ] 2. Old step\n"
            task_path.write_text(initial_content)

            result = ralph_executor._update_issue_task_file(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_number=123,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=["Comment 1"],
                branch_name="ai/branch-123",
            )

            assert result["success"] is True

    def test_update_issue_task_file_execute_failure(self, ralph_executor):
        """Test updating issue task file when execute_fn fails."""
        ralph_executor.execute_fn = lambda *args, **kwargs: {
            "success": False,
            "error": "CLI execution failed",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-123.md"
            task_path.parent.mkdir(parents=True, exist_ok=True)
            task_path.write_text("# Test")

            result = ralph_executor._update_issue_task_file(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_number=123,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch-123",
            )

            assert result["success"] is False
            assert "error" in result

    def test_refine_issue_task_file(self, ralph_executor):
        """Test refining an issue task file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-123.md"
            task_path.parent.mkdir(parents=True, exist_ok=True)

            initial_content = "# Test\n\n## Steps\n\n- [ ] 1. First step\n"
            task_path.write_text(initial_content)

            result = ralph_executor._refine_issue_task_file(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=["Comment 1"],
                branch_name="ai/branch-123",
            )

            assert result["success"] is True

    def test_refine_issue_task_file_execute_failure(self, ralph_executor):
        """Test refining issue task file when execute_fn fails."""
        ralph_executor.execute_fn = lambda *args, **kwargs: {
            "success": False,
            "error": "CLI execution failed",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-123.md"
            task_path.parent.mkdir(parents=True, exist_ok=True)
            task_path.write_text("# Test")

            result = ralph_executor._refine_issue_task_file(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch-123",
            )

            assert result["success"] is False
            assert "error" in result

    def test_execute_step(self, ralph_executor):
        """Test executing a single step."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            step = Step(number=1, description="Test step", is_closed=False)
            plan = Plan(title="Test", description="", steps=[step])

            result = ralph_executor._execute_step(
                step=step,
                plan=plan,
                repo_dir=repo_dir,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
            )

            assert result["success"] is True

    def test_execute_step_failure(self, ralph_executor):
        """Test executing a step that fails."""
        ralph_executor.execute_fn = lambda *args, **kwargs: {
            "success": False,
            "error": "Step execution failed",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            step = Step(number=1, description="Test step", is_closed=False)
            plan = Plan(title="Test", description="", steps=[step])

            result = ralph_executor._execute_step(
                step=step,
                plan=plan,
                repo_dir=repo_dir,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
            )

            assert result["success"] is False

    def test_execute_step_acceptance_check(self, ralph_executor):
        """Test acceptance check for a step."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n")

            ralph_executor.execute_fn = lambda *args, **kwargs: {
                "success": True,
                "stdout": "ACCEPTANCE_STATUS: pass",
            }

            result = ralph_executor._execute_step_acceptance_check(
                repo_dir=repo_dir,
                task_path=task_path,
                step=Step(number=1, description="First step"),
                issue_title="Test Issue",
                issue_body="Test body",
                branch_name="ai/branch",
            )

            assert result["success"] is True

    def test_execute_step_acceptance_check_failure(self, ralph_executor):
        """Test acceptance check when criteria are not met."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n")

            ralph_executor.execute_fn = lambda *args, **kwargs: {
                "success": True,
                "stdout": "ACCEPTANCE_STATUS: fail",
            }

            result = ralph_executor._execute_step_acceptance_check(
                repo_dir=repo_dir,
                task_path=task_path,
                step=Step(number=1, description="First step"),
                issue_title="Test Issue",
                issue_body="Test body",
                branch_name="ai/branch",
            )

            assert result["success"] is False

    def test_update_remaining_steps(self, ralph_executor):
        """Test updating remaining steps after a completed step."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n- [ ] 2. Second step\n")

            result = ralph_executor._update_remaining_steps(
                repo_dir=repo_dir,
                task_path=task_path,
                step=Step(number=1, description="First step"),
                issue_title="Test Issue",
                issue_body="Test body",
                branch_name="ai/branch",
            )

            assert result["success"] is True

    def test_update_remaining_steps_failure(self, ralph_executor):
        """Test updating remaining steps when execution fails."""
        ralph_executor.execute_fn = lambda *args, **kwargs: {
            "success": False,
            "error": "Update failed",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n")

            result = ralph_executor._update_remaining_steps(
                repo_dir=repo_dir,
                task_path=task_path,
                step=Step(number=1, description="First step"),
                issue_title="Test Issue",
                issue_body="Test body",
                branch_name="ai/branch",
            )

            assert result["success"] is False

    def test_execute_new_issue(self, ralph_executor):
        """Test execute method for a new issue (no existing task file)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)

            result = ralph_executor.execute(
                repo_dir=repo_dir,
                issue_number=123,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=["Comment 1"],
                branch_name="ai/branch-123",
            )

            assert "success" in result
            assert "task_path" in result
            assert result["task_path"] == str(repo_dir / ".ralph" / "github-123.md")

    def test_execute_existing_issue(self, ralph_executor):
        """Test execute method for an existing issue (task file exists)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-123.md"
            task_path.parent.mkdir(parents=True, exist_ok=True)
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. Completed step\n")

            result = ralph_executor.execute(
                repo_dir=repo_dir,
                issue_number=123,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch-123",
            )

            assert "success" in result
            assert "task_path" in result

    def test_run_refined_task_loop_all_steps_completed(self, ralph_executor):
        """Test refined task loop when all steps are already completed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. Completed step\n- [x] 2. Also completed\n")

            result = ralph_executor._run_refined_task_loop(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
            )

            assert result["success"] is True
            assert result["steps_completed"] == 2

    def test_run_refined_task_loop_max_iterations(self, ralph_executor):
        """Test refined task loop reaching max iterations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. Step that will never complete\n")

            ralph_executor.max_iterations = 2

            execute_count = [0]

            def failing_execute_fn(*args, **kwargs):
                execute_count[0] += 1
                return {"success": False, "error": "Step execution failed"}

            ralph_executor.execute_fn = failing_execute_fn

            result = ralph_executor._run_refined_task_loop(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
            )

            assert result["success"] is False
            assert result["max_loops_reached"] is True
            assert "loops_executed" in result
