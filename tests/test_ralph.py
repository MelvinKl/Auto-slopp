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
            file_prefix="github",
        )

    def test_initialization(self, ralph_executor, logger):
        """Test RalphExecutor initialization."""
        assert ralph_executor.logger is logger
        assert ralph_executor.agent_args == []
        assert ralph_executor.timeout == 60
        assert ralph_executor.max_iterations == 10

    def test_get_issue_task_path(self):
        """Test instance method _get_issue_task_path."""
        repo_dir = Path("/test/repo")
        ralph_executor = RalphExecutor(
            logger=logging.getLogger(__name__),
            agent_args=[],
            timeout=60,
            execute_fn=lambda *args, **kwargs: {"success": True},
            has_changes_fn=lambda x: False,
            commit_fn=lambda x, y, z: (True, True),
            max_iterations=5,
            file_prefix="github",
        )
        task_path = ralph_executor._get_issue_task_path(repo_dir, 123)
        expected = Path("/test/repo/.ralph/github-123.md")
        assert task_path == expected

    def test_configurable_file_prefix(self):
        """Test that file_prefix configures task file naming."""
        repo_dir = Path("/test/repo")

        github_executor = RalphExecutor(
            logger=logging.getLogger(__name__),
            agent_args=[],
            timeout=60,
            execute_fn=lambda *args, **kwargs: {"success": True},
            has_changes_fn=lambda x: False,
            commit_fn=lambda x, y, z: (True, True),
            max_iterations=5,
            file_prefix="github",
        )
        github_path = github_executor._get_issue_task_path(repo_dir, 123)
        assert github_path == Path("/test/repo/.ralph/github-123.md")

        vikunja_executor = RalphExecutor(
            logger=logging.getLogger(__name__),
            agent_args=[],
            timeout=60,
            execute_fn=lambda *args, **kwargs: {"success": True},
            has_changes_fn=lambda x: False,
            commit_fn=lambda x, y, z: (True, True),
            max_iterations=5,
            file_prefix="vikunja",
        )
        vikunja_path = vikunja_executor._get_issue_task_path(repo_dir, 456)
        assert vikunja_path == Path("/test/repo/.ralph/vikunja-456.md")

    def test_configurable_phase_names(self):
        """Test that per-phase task difficulty names are configurable."""
        executor = RalphExecutor(
            logger=logging.getLogger(__name__),
            agent_args=[],
            timeout=60,
            execute_fn=lambda *args, **kwargs: {"success": True},
            has_changes_fn=lambda x: False,
            commit_fn=lambda x, y, z: (True, True),
            max_iterations=5,
            file_prefix="github",
            task_planning_name="custom_planning",
            implementation_name="custom_impl",
            validation_name="custom_validation",
        )
        assert executor.task_planning_name == "custom_planning"
        assert executor.implementation_name == "custom_impl"
        assert executor.validation_name == "custom_validation"

    def test_default_phase_names(self):
        """Test that default phase names match settings keys."""
        executor = RalphExecutor(
            logger=logging.getLogger(__name__),
            agent_args=[],
            timeout=60,
            execute_fn=lambda *args, **kwargs: {"success": True},
            has_changes_fn=lambda x: False,
            commit_fn=lambda x, y, z: (True, True),
            max_iterations=5,
        )
        assert executor.task_planning_name == "task_planning"
        assert executor.implementation_name == "implementation"
        assert executor.validation_name == "task_implementation_validation"

    def test_update_issue_task_file_uses_task_planning_name(self):
        """Test that _update_issue_task_file passes task_planning_name as task_name."""
        captured = []

        def spy_execute_fn(*args, **kwargs):
            captured.append(kwargs)
            return {"success": True, "stdout": ""}

        executor = RalphExecutor(
            logger=logging.getLogger(__name__),
            agent_args=[],
            timeout=60,
            execute_fn=spy_execute_fn,
            has_changes_fn=lambda x: False,
            commit_fn=lambda x, y, z: (True, True),
            max_iterations=5,
            file_prefix="github",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-1.md"
            task_path.parent.mkdir(parents=True, exist_ok=True)
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. Step\n")

            executor._update_issue_task_file(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_number=1,
                issue_title="Test",
                issue_body="body",
                comment_texts=[],
                branch_name="ai/branch",
            )

        assert captured[0]["task_name"] == "task_planning"

    def test_refine_issue_task_file_uses_task_planning_name(self):
        """Test that _refine_issue_task_file passes task_planning_name as task_name."""
        captured = []

        def spy_execute_fn(*args, **kwargs):
            captured.append(kwargs)
            return {"success": True, "stdout": ""}

        executor = RalphExecutor(
            logger=logging.getLogger(__name__),
            agent_args=[],
            timeout=60,
            execute_fn=spy_execute_fn,
            has_changes_fn=lambda x: False,
            commit_fn=lambda x, y, z: (True, True),
            max_iterations=5,
            file_prefix="github",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-1.md"
            task_path.parent.mkdir(parents=True, exist_ok=True)
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. Step\n")

            executor._refine_issue_task_file(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test",
                issue_body="body",
                comment_texts=[],
                branch_name="ai/branch",
            )

        assert captured[0]["task_name"] == "task_planning"

    def test_execute_step_uses_implementation_name(self):
        """Test that _execute_step passes implementation_name as task_name."""
        captured = []

        def spy_execute_fn(*args, **kwargs):
            captured.append(kwargs)
            return {"success": True, "stdout": ""}

        executor = RalphExecutor(
            logger=logging.getLogger(__name__),
            agent_args=[],
            timeout=60,
            execute_fn=spy_execute_fn,
            has_changes_fn=lambda x: False,
            commit_fn=lambda x, y, z: (True, True),
            max_iterations=5,
            file_prefix="github",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            step = Step(number=1, description="Test step", is_closed=False)
            plan = Plan(title="Test", description="", steps=[step])

            executor._execute_step(
                step=step,
                plan=plan,
                repo_dir=repo_dir,
                issue_title="Test",
                issue_body="body",
                comment_texts=[],
                branch_name="ai/branch",
            )

        assert captured[0]["task_name"] == "implementation"

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

    def test_create_issue_task_file_has_all_five_steps(self, ralph_executor):
        """Test that the created task file contains all 5 required steps."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-123.md"

            ralph_executor._create_issue_task_file(
                task_path=task_path,
                issue_number=123,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch-123",
            )

            content = task_path.read_text()

            # Verify all 5 steps are present with correct descriptions
            assert "- [ ] 1. Analyze the required implementation changes for this issue." in content
            assert "- [ ] 2. Implement the required code changes." in content
            assert "- [ ] 3. Update or add tests for the implementation." in content
            assert (
                "- [ ] 4. If the change affects user-facing behavior or documentation, update README.md and any documentation affected by the changes."
                in content
            )
            assert "- [ ] 5. Run `make test` and confirm it succeeds." in content

    def test_create_issue_task_file_steps_have_acceptance_criteria(self, ralph_executor):
        """Test that each step has acceptance criteria directly beneath it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-123.md"

            ralph_executor._create_issue_task_file(
                task_path=task_path,
                issue_number=123,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch-123",
            )

            content = task_path.read_text()

            # Verify acceptance criteria for each step appear directly beneath the step
            # by checking the structure: step line followed by acceptance criteria indented
            lines = content.split("\n")

            # Step 1 and its criteria
            assert any("- [ ] 1. Analyze the required implementation changes" in line for line in lines)
            step1_idx = next(
                i for i, line in enumerate(lines) if "- [ ] 1. Analyze the required implementation changes" in line
            )
            assert "  - Acceptance Criteria:" in lines[step1_idx + 1]
            assert "    - The affected files and expected behavior are clearly identified." in lines[step1_idx + 2]

            # Step 2 and its criteria
            assert any("- [ ] 2. Implement the required code changes" in line for line in lines)
            step2_idx = next(
                i for i, line in enumerate(lines) if "- [ ] 2. Implement the required code changes" in line
            )
            assert "  - Acceptance Criteria:" in lines[step2_idx + 1]
            assert "    - Code changes are applied in the correct files." in lines[step2_idx + 2]

            # Step 3 and its criteria
            assert any("- [ ] 3. Update or add tests for the implementation" in line for line in lines)
            step3_idx = next(
                i for i, line in enumerate(lines) if "- [ ] 3. Update or add tests for the implementation" in line
            )
            assert "  - Acceptance Criteria:" in lines[step3_idx + 1]
            assert "    - Tests cover the implemented behavior." in lines[step3_idx + 2]

            # Step 4 and its criteria
            assert any(
                "- [ ] 4. If the change affects user-facing behavior or documentation, update README.md" in line
                for line in lines
            )
            step4_idx = next(
                i
                for i, line in enumerate(lines)
                if "- [ ] 4. If the change affects user-facing behavior or documentation, update README.md" in line
            )
            assert "  - Acceptance Criteria:" in lines[step4_idx + 1]
            assert "    - Documentation reflects the changes made (if applicable)." in lines[step4_idx + 2]

            # Step 5 and its criteria
            assert any("- [ ] 5. Run `make test` and confirm it succeeds" in line for line in lines)
            step5_idx = next(
                i for i, line in enumerate(lines) if "- [ ] 5. Run `make test` and confirm it succeeds" in line
            )
            assert "  - Acceptance Criteria:" in lines[step5_idx + 1]
            assert "    - `make test` exits successfully." in lines[step5_idx + 2]

    def test_create_issue_task_file_step_numbering_sequential(self, ralph_executor):
        """Test that step numbering is sequential from 1 to 5."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-123.md"

            ralph_executor._create_issue_task_file(
                task_path=task_path,
                issue_number=123,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch-123",
            )

            content = task_path.read_text()
            lines = content.split("\n")

            step_lines = [line for line in lines if line.strip().startswith("- [ ]") and ". " in line]
            assert len(step_lines) == 5

            # Verify sequential numbering
            for i, line in enumerate(step_lines, 1):
                assert f"- [ ] {i}. " in line

    def test_mark_step_completed_in_file(self, ralph_executor):
        """Test marking a step as completed in a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. Step 1\n- [ ] 2. Step 2\n")

            ralph_executor._mark_step_completed_in_file(task_path, 1)

            content = task_path.read_text()
            assert "- [x] 1. Step 1" in content
            assert "- [ ] 2. Step 2" in content

    def test_step_is_closed(self, ralph_executor):
        """Test checking if a step is closed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. First step\n- [ ] 2. Second step\n")

            assert ralph_executor._step_is_closed(task_path, 1) is True
            assert ralph_executor._step_is_closed(task_path, 2) is False
            assert ralph_executor._step_is_closed(task_path, 999) is False

    def test_ensure_last_step_is_make_test(self, ralph_executor):
        """Test ensuring last step is make test in various scenarios."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"

            # Scenario 1: Single step without make test
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n")
            ralph_executor._ensure_last_step_is_make_test(task_path)
            content = task_path.read_text()
            assert "make test" in content.lower()
            step_lines = [line for line in content.split("\n") if line.strip().startswith("- [ ]") and ". " in line]
            assert len(step_lines) == 2
            assert "make test" in step_lines[-1].lower()

            # Scenario 2: Full 5-step structure without make test as last step
            task_path.write_text(
                "# Test\n\n"
                "## Steps\n\n"
                "- [ ] 1. Analyze the required implementation changes\n"
                "- [ ] 2. Implement the required code changes\n"
                "- [ ] 3. Update or add tests for the implementation\n"
                "- [ ] 4. If the change affects user-facing behavior or documentation, update README.md and any documentation affected by the changes\n"
                "- [ ] 5. Some other final step\n"
            )
            ralph_executor._ensure_last_step_is_make_test(task_path)
            content = task_path.read_text()
            assert "make test" in content.lower()
            step_lines = [line for line in content.split("\n") if line.strip().startswith("- [ ]") and ". " in line]
            assert len(step_lines) == 6
            assert "make test" in step_lines[-1].lower()

            # Scenario 3: Make test already present as last step - should not duplicate
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n- [ ] 2. Run make test\n")
            original = task_path.read_text()
            ralph_executor._ensure_last_step_is_make_test(task_path)
            content = task_path.read_text()
            assert content == original

    def test_ensure_last_step_is_make_test_with_five_steps(self, ralph_executor):
        """Test ensuring last step is make test with full 5-step structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"

            # 5 steps without make test as last step
            content = (
                "# Test\n\n"
                "## Steps\n\n"
                "- [ ] 1. Analyze the required implementation changes\n"
                "- [ ] 2. Implement the required code changes\n"
                "- [ ] 3. Update or add tests for the implementation\n"
                "- [ ] 4. Update README.md and documentation\n"
                "- [ ] 5. Some other final step\n"
            )
            task_path.write_text(content)

            ralph_executor._ensure_last_step_is_make_test(task_path)

            updated_content = task_path.read_text()
            assert "make test" in updated_content.lower()
            # Should have 6 steps now (original 5 + make test)
            step_lines = [
                line for line in updated_content.split("\n") if line.strip().startswith("- [ ]") and ". " in line
            ]
            assert len(step_lines) == 6
            # Last step should be make test
            assert "make test" in step_lines[-1].lower()

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

    def test_build_refinement_instructions_includes_documentation_step(self, ralph_executor):
        """Test that refinement instructions require documentation update step."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"
            task_path.write_text("# Test")

            instructions = ralph_executor._build_refinement_instructions(
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
            )

            assert (
                "If the change affects user-facing behavior or documentation, include a step to update README.md and any documentation affected by the changes. This step must come before the final `make test` step"
                in instructions
            )
            assert "make test" in instructions
            assert "The last step must always verify" in instructions

    def test_update_issue_task_file_instructions_include_documentation_step(self, ralph_executor):
        """Test that update issue task file instructions require documentation update step."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-123.md"
            task_path.parent.mkdir(parents=True, exist_ok=True)
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. Completed step\n")

            captured = []

            def spy_execute_fn(*args, **kwargs):
                captured.append(kwargs.get("instructions", args[0] if args else ""))
                return {"success": True, "stdout": ""}

            ralph_executor.execute_fn = spy_execute_fn

            ralph_executor._update_issue_task_file(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_number=123,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch-123",
            )

            assert len(captured) == 1
            instructions = captured[0]
            assert (
                "If the change affects user-facing behavior or documentation, include a step to update README.md and any documentation affected by the changes. This step must come before the final `make test` step"
                in instructions
            )
            assert "make test" in instructions
            assert "The last step must always verify" in instructions

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

    def test_execute_final_acceptance_check(self, ralph_executor):
        """Test final acceptance check for all steps."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. First step\n- [x] 2. Second step\n")

            ralph_executor.execute_fn = lambda *args, **kwargs: {
                "success": True,
                "stdout": "ACCEPTANCE_STATUS: pass",
            }

            result = ralph_executor._execute_final_acceptance_check(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                branch_name="ai/branch",
            )

            assert result["success"] is True

    def test_execute_final_acceptance_check_failure(self, ralph_executor):
        """Test final acceptance check when criteria are not met."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. First step\n- [x] 2. Second step\n")

            ralph_executor.execute_fn = lambda *args, **kwargs: {
                "success": True,
                "stdout": "ACCEPTANCE_STATUS: fail",
            }

            result = ralph_executor._execute_final_acceptance_check(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                branch_name="ai/branch",
            )

            assert result["success"] is False

    def test_execute_final_acceptance_check_execute_failure(self, ralph_executor):
        """Test final acceptance check when execute_fn fails."""
        ralph_executor.execute_fn = lambda *args, **kwargs: {
            "success": False,
            "error": "CLI execution failed",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. First step\n")

            result = ralph_executor._execute_final_acceptance_check(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                branch_name="ai/branch",
            )

            assert result["success"] is False
            assert "error" in result

    def test_execute_final_acceptance_check_uses_validation_name(self):
        """Test that _execute_final_acceptance_check passes validation_name as task_name."""
        captured = []

        def spy_execute_fn(*args, **kwargs):
            captured.append(kwargs)
            return {"success": True, "stdout": "ACCEPTANCE_STATUS: pass"}

        executor = RalphExecutor(
            logger=logging.getLogger(__name__),
            agent_args=[],
            timeout=60,
            execute_fn=spy_execute_fn,
            has_changes_fn=lambda x: False,
            commit_fn=lambda x, y, z: (True, True),
            max_iterations=5,
            file_prefix="github",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. Step\n")

            executor._execute_final_acceptance_check(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test",
                issue_body="body",
                branch_name="ai/branch",
            )

        assert captured[0]["task_name"] == "task_implementation_validation"

    def test_execute_final_acceptance_check_missing_pass_token(self, ralph_executor):
        """Test that missing/empty acceptance output is treated as a failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. First step\n")

            ralph_executor.execute_fn = lambda *args, **kwargs: {"success": True, "stdout": ""}

            result = ralph_executor._execute_final_acceptance_check(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                branch_name="ai/branch",
            )

            assert result["success"] is False
            assert result["error"] == "Final acceptance criteria were not fulfilled"

    def test_execute_final_acceptance_check_unrelated_output_is_failure(self, ralph_executor):
        """Test that unrelated stdout without the pass token is treated as a failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. First step\n")

            ralph_executor.execute_fn = lambda *args, **kwargs: {"success": True, "stdout": "I don't know"}

            result = ralph_executor._execute_final_acceptance_check(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                branch_name="ai/branch",
            )

            assert result["success"] is False

    def test_execute_final_acceptance_check_missing_task_file(self, ralph_executor):
        """Test that a missing task file fails the final check without calling execute_fn."""
        execute_calls = [0]

        def spy_execute_fn(*args, **kwargs):
            execute_calls[0] += 1
            return {"success": True, "stdout": "ACCEPTANCE_STATUS: pass"}

        ralph_executor.execute_fn = spy_execute_fn

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"

            result = ralph_executor._execute_final_acceptance_check(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                branch_name="ai/branch",
            )

            assert result["success"] is False
            assert "Failed to build final acceptance check instructions" in result["error"]
            assert execute_calls[0] == 0

    def test_build_final_acceptance_check_instructions_includes_task_content(self, ralph_executor):
        """Test that final check instructions embed task content without status markers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.md"
            task_path.write_text(
                "# Test\n\n## Steps\n\n- [x] 1. First step\n" "  - Acceptance Criteria:\n" "    - Behavior verified\n"
            )

            instructions = ralph_executor._build_final_acceptance_check_instructions(
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                branch_name="ai/branch",
            )

            assert "Test Issue" in instructions
            assert "ACCEPTANCE_STATUS" in instructions
            assert "First step" in instructions
            assert "Behavior verified" in instructions
            assert "✓" not in instructions
            assert "○" not in instructions

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

            # Override execute_fn to return acceptance pass for final check
            ralph_executor.execute_fn = lambda *args, **kwargs: {
                "success": True,
                "stdout": "ACCEPTANCE_STATUS: pass",
            }

            result = ralph_executor._run_refined_task_loop(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
                issue_number=1,
            )

            assert result["success"] is True
            assert result["steps_completed"] == 2
            assert result["loops_executed"] == 0

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
                issue_number=1,
            )

            assert result["success"] is False
            assert result["max_loops_reached"] is True
            assert "loops_executed" in result

    def test_run_refined_task_loop_max_iterations_preserves_llm_unavailable_last_error(self, ralph_executor):
        """Test that the mid-loop LLM-unavailability reason is preserved as 'last_error' at max iterations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. Step that will never complete\n")

            ralph_executor.max_iterations = 3
            # Force every batch iteration to fail with an LLM-unavailability error
            ralph_executor.execute_fn = lambda *args, **kwargs: {
                "success": False,
                "error": "claude timed out after 7200 seconds",
            }

            result = ralph_executor._run_refined_task_loop(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
                issue_number=1,
            )

            assert result["success"] is False
            assert result["max_loops_reached"] is True
            assert result["loops_executed"] == 3
            assert "timed out" in result["last_error"], "last_error must keep the mid-loop LLM timeout reason"

    def test_run_refined_task_loop_final_check_failure_sets_error(self, ralph_executor):
        """Test that a final acceptance check failure is reported via 'error', not just 'last_error'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. Completed step\n")

            ralph_executor.max_iterations = 1
            ralph_executor.execute_fn = lambda *args, **kwargs: {
                "success": True,
                "stdout": "ACCEPTANCE_STATUS: fail",
            }

            result = ralph_executor._run_refined_task_loop(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
                issue_number=1,
            )

            assert result["success"] is False
            assert result["error"] == "Final acceptance criteria were not fulfilled"
            assert result["max_loops_reached"] is False
            assert result["loops_executed"] == 0

    def test_run_refined_task_loop_final_check_deletes_task_file_on_failure(self, ralph_executor):
        """Test that a failed final check deletes the task file so it is recreated next time."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-1.md"
            task_path.parent.mkdir(parents=True, exist_ok=True)
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. Completed step\n")

            ralph_executor.max_iterations = 3
            ralph_executor.execute_fn = lambda *args, **kwargs: {
                "success": True,
                "stdout": "ACCEPTANCE_STATUS: fail",
            }

            result = ralph_executor._run_refined_task_loop(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
                issue_number=1,
            )

            assert result["success"] is False
            assert result["error"] == "Final acceptance criteria were not fulfilled"
            assert not task_path.exists(), "Task file should be deleted on failed evaluation"
            assert result["loops_executed"] == 0

    def test_run_refined_task_loop_max_iterations_partial_work_runs_final_check(self, ralph_executor):
        """Test that the final acceptance check runs on partial work at max iterations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n- [ ] 2. Second step\n")

            ralph_executor.max_iterations = 2
            ralph_executor.has_changes_fn = lambda path: False

            validation_calls = [0]
            implementation_calls = [0]

            def tracking_execute_fn(*args, **kwargs):
                task_name = kwargs.get("task_name", "unknown")
                if task_name == "task_implementation_validation":
                    validation_calls[0] += 1
                    return {"success": True, "stdout": "ACCEPTANCE_STATUS: fail"}
                if task_name == "implementation":
                    implementation_calls[0] += 1
                    # Simulate the CLI marking all steps as closed in the task file
                    task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. First step\n- [x] 2. Second step\n")
                    return {"success": True}
                return {"success": True, "stdout": "Done"}

            ralph_executor.execute_fn = tracking_execute_fn

            result = ralph_executor._run_refined_task_loop(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
                issue_number=1,
            )

            # With batch execution, all steps are executed in one CLI call
            assert result["success"] is False
            assert result["max_loops_reached"] is False, "Batch execution completes in 1 iteration"
            assert result["steps_completed"] == 2
            assert result["loops_executed"] == 1
            assert implementation_calls[0] == 1, "Expected 1 batched implementation call"
            assert validation_calls[0] == 1
            assert result["last_error"] == "Final acceptance criteria were not fulfilled"

    def test_run_refined_task_loop_max_iterations_deletes_task_file_on_failed_check(self, ralph_executor):
        """Test that the task file is deleted when final acceptance check fails at max iterations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / ".ralph" / "github-1.md"
            task_path.parent.mkdir(parents=True, exist_ok=True)
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n- [ ] 2. Second step\n")

            ralph_executor.max_iterations = 2
            ralph_executor.has_changes_fn = lambda path: False

            validation_calls = [0]

            def tracking_execute_fn(*args, **kwargs):
                task_name = kwargs.get("task_name", "unknown")
                if task_name == "task_implementation_validation":
                    validation_calls[0] += 1
                    return {"success": True, "stdout": "ACCEPTANCE_STATUS: fail"}
                # Implementation call - mark all steps as closed
                task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. First step\n- [x] 2. Second step\n")
                return {"success": True}

            ralph_executor.execute_fn = tracking_execute_fn

            result = ralph_executor._run_refined_task_loop(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
                issue_number=1,
            )

            assert result["success"] is False
            assert result["max_loops_reached"] is False, "Batch execution completes in 1 iteration"
            assert result["loops_executed"] == 1
            assert not task_path.exists(), "Task file should be deleted on failed evaluation at max iterations"
            assert validation_calls[0] == 1

    def test_run_refined_task_loop_max_iterations_final_check_failure_recorded_in_error_state(self, ralph_executor):
        """Test that a final acceptance check failure at max iterations is recorded in the error state.

        If the last step iteration succeeded (clearing ``_last_error`` and
        ``_last_iteration_failure_reason``) and the final acceptance check
        then fails, ``get_skip_reason()`` must still be able to surface the
        failure so an LLM timeout during the final check skips the issue for
        retry instead of dropping it via ``on_max_iterations_reached``.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n- [ ] 2. Second step\n")

            ralph_executor.max_iterations = 2
            ralph_executor.has_changes_fn = lambda path: False

            def tracking_execute_fn(*args, **kwargs):
                task_name = kwargs.get("task_name", "unknown")
                if task_name == "task_implementation_validation":
                    return {"success": False, "error": "LLM timed out waiting for response"}
                # Implementation call: close only step 1, leaving step 2 open
                task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. First step\n- [ ] 2. Second step\n")
                return {"success": True}

            ralph_executor.execute_fn = tracking_execute_fn

            result = ralph_executor._run_refined_task_loop(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
                issue_number=1,
            )

            assert result["success"] is False
            assert result["max_loops_reached"] is True
            assert result["last_error"] == "LLM timed out waiting for response"
            # The failure must also be recorded in the executor's error state
            # (the successful step iterations cleared it).
            assert ralph_executor._last_error == "LLM timed out waiting for response"
            assert ralph_executor._last_iteration_failure_reason == "LLM timed out waiting for response"
            assert ralph_executor.get_skip_reason() == "LLM timed out waiting for response"

    def test_run_refined_task_loop_no_intermediate_checks(self, ralph_executor):
        """Test that refined task loop executes steps in a single batch call with final validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text(
                "# Test\n"
                "\n"
                "## Steps\n"
                "\n"
                "- [ ] 1. First step\n"
                "- [ ] 2. Second step\n"
                "- [ ] 3. Run make test\n"
            )

            ralph_executor.max_iterations = 10
            ralph_executor.has_changes_fn = lambda path: True

            call_log = []

            def tracking_execute_fn(*args, **kwargs):
                task_name = kwargs.get("task_name", "unknown")
                call_log.append(task_name)
                if task_name == "task_implementation_validation":
                    return {"success": True, "stdout": "ACCEPTANCE_STATUS: pass"}
                # Implementation call - mark all steps as closed
                task_path.write_text(
                    "# Test\n"
                    "\n"
                    "## Steps\n"
                    "\n"
                    "- [x] 1. First step\n"
                    "- [x] 2. Second step\n"
                    "- [x] 3. Run make test\n"
                )
                return {"success": True}

            ralph_executor.execute_fn = tracking_execute_fn
            ralph_executor.commit_fn = lambda path, msg, push: (True, None)

            result = ralph_executor._run_refined_task_loop(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
                issue_number=1,
            )

            assert result["success"] is True
            assert result["steps_completed"] == 3

            implementation_calls = [c for c in call_log if c == "implementation"]
            validation_calls = [c for c in call_log if c == "task_implementation_validation"]
            remaining_steps_calls = [c for c in call_log if c == "remaining_steps_update"]

            # With batch execution, all steps are implemented in a single CLI call
            assert (
                len(implementation_calls) == 1
            ), f"Expected 1 batched implementation call, got {len(implementation_calls)}"
            assert len(validation_calls) == 1, f"Expected 1 final validation call, got {len(validation_calls)}"
            assert (
                len(remaining_steps_calls) == 0
            ), f"Expected 0 remaining_steps_update calls, got {len(remaining_steps_calls)}"

    def test_is_llm_unavailable_no_error(self, ralph_executor):
        """Test _is_llm_unavailable returns False when no error is set."""
        assert ralph_executor._is_llm_unavailable() is False

    def test_is_llm_unavailable_timeout(self, ralph_executor):
        """Test _is_llm_unavailable detects timeout errors."""
        ralph_executor._last_error = "claude timed out after 7200 seconds"
        assert ralph_executor._is_llm_unavailable() is True

    def test_is_llm_unavailable_rate_limit(self, ralph_executor):
        """Test _is_llm_unavailable detects rate limit errors."""
        ralph_executor._last_error = "Rate limit exceeded: too many requests"
        assert ralph_executor._is_llm_unavailable() is True

    def test_is_llm_unavailable_connection_refused(self, ralph_executor):
        """Test _is_llm_unavailable detects connection refused errors."""
        ralph_executor._last_error = "Connection refused to API endpoint"
        assert ralph_executor._is_llm_unavailable() is True

    def test_is_llm_unavailable_503(self, ralph_executor):
        """Test _is_llm_unavailable detects 503 service unavailable errors."""
        ralph_executor._last_error = "503 Service Unavailable"
        assert ralph_executor._is_llm_unavailable() is True

    def test_is_llm_unavailable_step_failure_not_unavailable(self, ralph_executor):
        """Test _is_llm_unavailable returns False for non-LLM failures."""
        ralph_executor._last_error = "Step implementation failed: syntax error in code"
        assert ralph_executor._is_llm_unavailable() is False

    def test_is_llm_unavailable_parse_failure_not_unavailable(self, ralph_executor):
        """Test _is_llm_unavailable returns False for parse failures."""
        ralph_executor._last_error = "Failed to parse updated task file: invalid format"
        assert ralph_executor._is_llm_unavailable() is False

    def test_is_llm_unavailable_llm_down(self, ralph_executor):
        """Test _is_llm_unavailable detects explicit LLM down indicators."""
        ralph_executor._last_error = "LLM is down, please try again later"
        assert ralph_executor._is_llm_unavailable() is True

    def test_is_llm_unavailable_service_unavailable(self, ralph_executor):
        """Test _is_llm_unavailable detects service unavailable errors."""
        ralph_executor._last_error = "Service unavailable: API endpoint not responding"
        assert ralph_executor._is_llm_unavailable() is True

    def test_is_llm_unavailable_prefers_last_iteration_failure_reason(self, ralph_executor):
        """Test _is_llm_unavailable prefers _last_iteration_failure_reason over _last_error."""
        # Set a stale non-LLM error from earlier in the run
        ralph_executor._last_error = "Step implementation failed: syntax error"
        # Set the current iteration error that indicates LLM unavailability
        ralph_executor._last_iteration_failure_reason = "timed out waiting for response"
        assert ralph_executor._is_llm_unavailable() is True

    def test_is_llm_unavailable_last_iteration_failure_reason_fallback(self, ralph_executor):
        """Test _is_llm_unavailable falls back to _last_error when _last_iteration_failure_reason is None."""
        ralph_executor._last_iteration_failure_reason = None
        ralph_executor._last_error = "timed out after 7200 seconds"
        assert ralph_executor._is_llm_unavailable() is True

    def test_is_llm_unavailable_last_iteration_failure_reason_clears_on_success(self, ralph_executor):
        """Test that _last_iteration_failure_reason is cleared after a successful iteration."""
        ralph_executor._last_iteration_failure_reason = "timed out waiting for response"
        assert ralph_executor._is_llm_unavailable() is True

        # Simulate a successful iteration clearing the error
        ralph_executor._last_iteration_failure_reason = None
        assert ralph_executor._is_llm_unavailable() is False

    def test_get_skip_reason_no_error(self, ralph_executor):
        """Test get_skip_reason returns None when no error is set."""
        assert ralph_executor.get_skip_reason() is None

    def test_get_skip_reason_returns_reason_when_unavailable(self, ralph_executor):
        """Test get_skip_reason returns the error message when it indicates LLM unavailability."""
        ralph_executor._last_error = "LLM timed out waiting for response"
        assert ralph_executor.get_skip_reason() == "LLM timed out waiting for response"

    def test_get_skip_reason_prefers_last_iteration_failure_reason(self, ralph_executor):
        """Test get_skip_reason prefers _last_iteration_failure_reason over _last_error."""
        ralph_executor._last_error = "stale error from earlier phase"
        ralph_executor._last_iteration_failure_reason = "connection refused"
        assert ralph_executor.get_skip_reason() == "connection refused"

    def test_get_skip_reason_none_for_non_unavailable_error(self, ralph_executor):
        """Test get_skip_reason returns None for errors that do not indicate LLM unavailability."""
        ralph_executor._last_error = "Step implementation failed: syntax error"
        assert ralph_executor.get_skip_reason() is None

    def test_run_refined_task_loop_sets_last_iteration_failure_reason_on_failure(self, ralph_executor):
        """Test that _last_iteration_failure_reason is set during the loop on step failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. Step that will fail\n")

            ralph_executor.max_iterations = 2
            call_count = [0]

            def failing_execute_fn(*args, **kwargs):
                call_count[0] += 1
                return {"success": False, "error": "timed out waiting for response"}

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
            # Verify _last_iteration_failure_reason was set during the loop
            assert ralph_executor._last_iteration_failure_reason is not None
            assert "timed out" in ralph_executor._last_iteration_failure_reason

    def test_run_refined_task_loop_last_iteration_failure_reason_cleared_on_success(self, ralph_executor):
        """Test that _last_iteration_failure_reason is cleared after a successful iteration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n- [ ] 2. Second step that fails\n")

            ralph_executor.max_iterations = 5
            call_count = [0]

            def success_then_fail(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return {"success": True, "stdout": "Done"}
                return {"success": False, "error": "timed out waiting for response"}

            ralph_executor.execute_fn = success_then_fail
            ralph_executor.has_changes_fn = lambda path: True
            ralph_executor.commit_fn = lambda path, msg, push: (True, None)

            result = ralph_executor._run_refined_task_loop(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
            )

            assert result["success"] is False
            # After the first successful iteration, _last_iteration_failure_reason should be None
            # (it was cleared), then set again on the second failure
            assert ralph_executor._last_iteration_failure_reason is not None
            assert "timed out" in ralph_executor._last_iteration_failure_reason

    def test_run_refined_task_loop_clears_last_error_after_successful_iteration(self, ralph_executor):
        """Test that a stale _last_error is cleared after a successful iteration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [ ] 1. First step\n- [ ] 2. Second step that fails\n")

            ralph_executor.max_iterations = 5
            # Simulate a transient timeout from an earlier phase of the run.
            ralph_executor._last_error = "timed out waiting for response"
            call_count = [0]
            error_after_success = []

            def success_then_fail(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return {"success": True, "stdout": "Done"}
                # The stale error must have been cleared by the successful
                # first iteration before the second iteration runs.
                error_after_success.append(ralph_executor._last_error)
                return {"success": False, "error": "timed out waiting for response"}

            ralph_executor.execute_fn = success_then_fail
            ralph_executor.has_changes_fn = lambda path: True
            ralph_executor.commit_fn = lambda path, msg, push: (True, None)

            result = ralph_executor._run_refined_task_loop(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
            )

            assert result["success"] is False
            # The first call after the successful iteration must see a cleared
            # _last_error (later failures set it again).
            assert error_after_success[0] is None

    def test_run_refined_task_loop_clears_error_state_on_successful_completion(self, ralph_executor):
        """Test that both error fields are cleared when the run completes successfully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            task_path = repo_dir / "task.md"
            task_path.write_text("# Test\n\n## Steps\n\n- [x] 1. Completed step\n- [x] 2. Also completed\n")

            # Simulate a transient timeout that occurred in an earlier run/phase.
            ralph_executor._last_error = "timed out waiting for response"
            ralph_executor._last_iteration_failure_reason = "timed out waiting for response"

            ralph_executor.execute_fn = lambda *args, **kwargs: {
                "success": True,
                "stdout": "acceptance_status: pass",
            }

            result = ralph_executor._run_refined_task_loop(
                repo_dir=repo_dir,
                task_path=task_path,
                issue_title="Test Issue",
                issue_body="Test body",
                comment_texts=[],
                branch_name="ai/branch",
                issue_number=1,
            )

            assert result["success"] is True
            assert ralph_executor._last_error is None
            assert ralph_executor._last_iteration_failure_reason is None
            # A successful completion must not be misclassified as LLM-unavailable.
            assert ralph_executor.get_skip_reason() is None
