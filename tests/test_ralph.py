"""Tests for Ralph loop implementation."""

import tempfile
from pathlib import Path

import pytest

from auto_slopp.utils.ralph import (
    Plan,
    PlanParser,
    PlanWriter,
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
