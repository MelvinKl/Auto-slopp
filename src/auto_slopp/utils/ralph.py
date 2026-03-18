"""Ralph loop implementation for step-based task execution.

This module provides a mechanism for:
1. Creating and parsing markdown-based plan files
2. Tracking step status (open/closed) in the plan
3. Executing steps in a loop until completion or max iterations
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Step:
    """Represents a single step in the plan."""

    number: int
    description: str
    is_closed: bool = False
    indent_level: int = 0

    def to_markdown_line(self) -> str:
        """Convert step to markdown line."""
        checkbox = "[x]" if self.is_closed else "[ ]"
        indent = "  " * self.indent_level
        return f"{indent}- {checkbox} {self.number}. {self.description}"

    @classmethod
    def from_markdown_line(cls, line: str) -> Optional["Step"]:
        """Parse a step from a markdown line.

        Args:
            line: Markdown line to parse

        Returns:
            Step object if line matches step pattern, None otherwise
        """
        stripped = line.strip()
        if not stripped.startswith("-"):
            return None

        indent_level = (len(line) - len(line.lstrip())) // 2

        closed_pattern = r"- \[x\]\s*(\d+)\.\s*(.+)"
        open_pattern = r"- \[ \]\s*(\d+)\.\s*(.+)"

        match = re.match(closed_pattern, stripped)
        if match:
            return cls(
                number=int(match.group(1)),
                description=match.group(2).strip(),
                is_closed=True,
                indent_level=indent_level,
            )

        match = re.match(open_pattern, stripped)
        if match:
            return cls(
                number=int(match.group(1)),
                description=match.group(2).strip(),
                is_closed=False,
                indent_level=indent_level,
            )

        return None


@dataclass
class Plan:
    """Represents a plan with steps."""

    title: str
    description: str
    steps: List[Step] = field(default_factory=list)
    header_content: str = ""
    footer_content: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_open_steps(self) -> List[Step]:
        """Get all open (not closed) steps."""
        return [s for s in self.steps if not s.is_closed]

    def get_next_open_step(self) -> Optional[Step]:
        """Get the next open step."""
        open_steps = self.get_open_steps()
        return open_steps[0] if open_steps else None

    def mark_step_closed(self, step_number: int) -> bool:
        """Mark a step as closed.

        Args:
            step_number: Step number to mark closed

        Returns:
            True if step was found and updated, False otherwise
        """
        for step in self.steps:
            if step.number == step_number:
                step.is_closed = True
                return True
        return False

    def all_steps_closed(self) -> bool:
        """Check if all steps are closed."""
        return len(self.get_open_steps()) == 0

    def to_markdown(self) -> str:
        """Convert plan to markdown format."""
        lines = []

        if self.header_content:
            lines.append(self.header_content)
            lines.append("")

        lines.append(f"# {self.title}")
        lines.append("")
        lines.append(self.description)
        lines.append("")
        lines.append("## Steps")
        lines.append("")

        for step in self.steps:
            lines.append(step.to_markdown_line())

        lines.append("")

        if self.footer_content:
            lines.append(self.footer_content)

        return "\n".join(lines)


class PlanParser:
    """Parser for plan markdown files."""

    @staticmethod
    def parse_file(file_path: Path) -> Plan:
        """Parse a plan from a markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            Parsed Plan object
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Plan file not found: {file_path}")

        content = file_path.read_text()
        return PlanParser.parse_content(content)

    @staticmethod
    def parse_content(content: str) -> Plan:
        """Parse a plan from markdown content.

        Args:
            content: Markdown content to parse

        Returns:
            Parsed Plan object
        """
        lines = content.split("\n")
        title = "Plan"
        description = ""
        steps: List[Step] = []
        header_lines: List[str] = []
        footer_lines: List[str] = []
        in_header = True
        in_steps = False
        found_title = False
        description_lines: List[str] = []

        for line in lines:
            if line.strip().startswith("# ") and not found_title:
                title = line.strip()[2:].strip()
                found_title = True
                in_header = False
                continue

            if line.strip().lower() == "## steps":
                in_steps = True
                continue

            if in_header and not found_title:
                header_lines.append(line)
                continue

            if in_steps:
                step = Step.from_markdown_line(line)
                if step:
                    steps.append(step)
                elif steps and not line.strip():
                    pass
                elif steps:
                    footer_lines.append(line)
            elif found_title and not in_steps:
                description_lines.append(line)

        description = "\n".join(description_lines).strip()

        return Plan(
            title=title,
            description=description,
            steps=steps,
            header_content="\n".join(header_lines).strip(),
            footer_content="\n".join(footer_lines).strip(),
        )


class PlanWriter:
    """Writer for plan markdown files."""

    @staticmethod
    def write_file(plan: Plan, file_path: Path) -> None:
        """Write a plan to a markdown file.

        Args:
            plan: Plan object to write
            file_path: Path to write the file to
        """
        content = plan.to_markdown()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        logger.info(f"Plan written to {file_path}")


class RalphLoop:
    """Ralph loop executor for step-based task execution.

    This class implements the ralph-loop pattern:
    1. Load or create a plan with steps
    2. Loop through steps, executing each via a callback
    3. Mark steps as closed on success
    4. Continue until all steps are closed or max loops reached
    """

    def __init__(
        self,
        plan_path: Path,
        max_loops: int = 20,
        step_executor: Optional[Callable[[Step, Plan], Dict[str, Any]]] = None,
    ):
        """Initialize the Ralph loop.

        Args:
            plan_path: Path to the plan markdown file
            max_loops: Maximum number of loop iterations (default: 20)
            step_executor: Callback function to execute each step
        """
        self.plan_path = plan_path
        self.max_loops = max_loops
        self.step_executor = step_executor
        self.plan: Optional[Plan] = None
        self.current_loop = 0
        self.logger = logging.getLogger("auto_slopp.ralph.RalphLoop")

    def load_plan(self) -> Plan:
        """Load the plan from file.

        Returns:
            Loaded Plan object
        """
        self.plan = PlanParser.parse_file(self.plan_path)
        return self.plan

    def save_plan(self) -> None:
        """Save the current plan to file."""
        if self.plan:
            PlanWriter.write_file(self.plan, self.plan_path)

    def create_plan(self, title: str, description: str, step_descriptions: List[str]) -> Plan:
        """Create a new plan with the given steps.

        Args:
            title: Plan title
            description: Plan description
            step_descriptions: List of step descriptions

        Returns:
            Created Plan object
        """
        steps = [Step(number=i + 1, description=desc, is_closed=False) for i, desc in enumerate(step_descriptions)]
        self.plan = Plan(title=title, description=description, steps=steps)
        self.save_plan()
        return self.plan

    def execute_step(self, step: Step) -> Dict[str, Any]:
        """Execute a single step.

        Args:
            step: Step to execute

        Returns:
            Execution result dictionary
        """
        if self.step_executor and self.plan:
            return self.step_executor(step, self.plan)

        self.logger.info(f"Executing step {step.number}: {step.description}")
        return {"success": True, "message": "Step executed (no executor provided)"}

    def run(self) -> Dict[str, Any]:
        """Run the ralph loop.

        Returns:
            Result dictionary with loop execution details
        """
        if not self.plan:
            try:
                self.load_plan()
            except FileNotFoundError:
                return {
                    "success": False,
                    "error": "Plan file not found",
                    "loops_executed": 0,
                }

        plan = self.plan
        if not plan:
            return {
                "success": False,
                "error": "Failed to load plan",
                "loops_executed": 0,
            }

        result = {
            "success": False,
            "loops_executed": 0,
            "steps_completed": 0,
            "total_steps": len(plan.steps),
            "max_loops_reached": False,
        }

        for loop_num in range(1, self.max_loops + 1):
            self.current_loop = loop_num
            self.logger.info(f"Ralph loop iteration {loop_num}/{self.max_loops}")

            next_step = plan.get_next_open_step()
            if not next_step:
                result["success"] = True
                result["loops_executed"] = loop_num - 1
                result["steps_completed"] = len([s for s in plan.steps if s.is_closed])
                self.logger.info("All steps completed!")
                break

            self.logger.info(f"Executing step {next_step.number}: {next_step.description}")
            step_result = self.execute_step(next_step)

            if step_result.get("success", False):
                plan.mark_step_closed(next_step.number)
                self.plan = plan
                self.save_plan()
                result["steps_completed"] = len([s for s in plan.steps if s.is_closed])
                self.logger.info(f"Step {next_step.number} completed successfully")
            else:
                self.logger.warning(f"Step {next_step.number} failed: {step_result.get('error', 'Unknown error')}")
                result["last_error"] = step_result.get("error", "Unknown error")

            result["loops_executed"] = loop_num

            if plan.all_steps_closed():
                result["success"] = True
                self.logger.info("All steps completed!")
                break
        else:
            result["max_loops_reached"] = True
            self.logger.warning(f"Max loops ({self.max_loops}) reached without completing all steps")

        return result


def create_default_plan_steps() -> List[str]:
    """Create default plan steps for issue processing.

    Returns:
        List of default step descriptions
    """
    return [
        "Understand the requirements by analyzing the issue title and description",
        "Explore the codebase to understand the current implementation",
        "Design a solution that is simple and focused",
        "Identify components that can be reused",
        "Implement the solution for the problem. Ensure to re-use existing code if possible",
        "Write or update tests for the changes",
        "Run 'make lint' to ensure code quality",
        "Run 'make test' to verify all tests pass",
        "Check if the README.md needs to be updated. Ensure the README.md contains an up-todate tree-view of the repository (max-depth=3) with a one-line description for each directory",
        "Commit the changes with a clear commit message",
        "Push the changes to the remote branch",
    ]