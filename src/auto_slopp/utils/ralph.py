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
