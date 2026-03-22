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
from typing import Any, Callable, Dict, List, Optional, Tuple

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


class RalphExecutor:
    """Executes step-based task plans using the Ralph loop.

    This class encapsulates the logic for creating, refining, and executing
    task plans defined in markdown files with step-by-step checkboxes.
    """

    def __init__(
        self,
        logger: logging.Logger,
        agent_args: List[str],
        timeout: int,
        execute_fn: Callable[..., Dict[str, Any]],
        has_changes_fn: Callable[[Path], bool],
        commit_fn: Callable[[Path, str, bool], Tuple[bool, Optional[bool]]],
    ):
        """Initialize the RalphExecutor.

        Args:
            logger: Logger instance for logging messages.
            agent_args: Additional arguments to pass to the CLI tool.
            timeout: Timeout for CLI execution in seconds.
            execute_fn: Callable matching the signature of
                ``execute_with_instructions(instructions, work_dir, agent_args, timeout, task_name)``.
            has_changes_fn: Callable that checks if a repo directory has uncommitted changes.
            commit_fn: Callable that commits (and optionally pushes) changes.
                Signature: ``(repo_dir, commit_message, push_if_remote) -> (commit_ok, push_ok)``.
        """
        self.logger = logger
        self.agent_args = agent_args
        self.timeout = timeout
        self.execute_fn = execute_fn
        self.has_changes_fn = has_changes_fn
        self.commit_fn = commit_fn

    def _get_issue_task_path(self, repo_dir: Path, issue_number: int) -> Path:
        """Get the canonical task file path for a GitHub issue."""
        return repo_dir / ".ralph" / f"github-{issue_number}.md"

    def _create_issue_task_file(
        self,
        task_path: Path,
        issue_number: int,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> None:
        """Create the initial GitHub issue task file in .ralph."""
        comments_text = ""
        if comment_texts:
            comments_text = "Comments:\n" + "\n".join(f"- {comment}" for comment in comment_texts if comment) + "\n\n"

        content = (
            f"# GitHub Issue Task: {issue_title}\n\n"
            f"Issue Number: {issue_number}\n"
            f"Branch: {branch_name}\n\n"
            f"## Required Task\n\n"
            f"{issue_body}\n\n"
            f"{comments_text}"
            "## Steps\n\n"
            "- [ ] 1. Analyze the required implementation changes for this issue.\n"
            "  - Acceptance Criteria:\n"
            "    - The affected files and expected behavior are clearly identified.\n"
            "- [ ] 2. Implement the required code changes.\n"
            "  - Acceptance Criteria:\n"
            "    - Code changes are applied in the correct files.\n"
            "- [ ] 3. Update or add tests for the implementation.\n"
            "  - Acceptance Criteria:\n"
            "    - Tests cover the implemented behavior.\n"
            "- [ ] 4. Run `make test` and confirm it succeeds.\n"
            "  - Acceptance Criteria:\n"
            "    - `make test` exits successfully.\n"
        )

        task_path.parent.mkdir(parents=True, exist_ok=True)
        task_path.write_text(content)
        self.logger.info(f"Created issue task file: {task_path}")

    def _update_issue_task_file(
        self,
        repo_dir: Path,
        task_path: Path,
        issue_number: int,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> Dict[str, Any]:
        """Update an existing task file via the CLI instead of overwriting it."""
        comments_text = ""
        if comment_texts:
            comments_text = "\nComments:\n" + "\n".join(f"- {comment}" for comment in comment_texts if comment)

        instructions = (
            f"You are already on branch '{branch_name}'. "
            f"Update the existing task file at '{task_path}' for GitHub issue #{issue_number}.\n"
            f"Issue title: {issue_title}\n"
            f"Issue description:\n{issue_body}\n"
            f"{comments_text}\n\n"
            "The task file already exists and may contain completed steps from prior work.\n"
            "Requirements:\n"
            "- Preserve all completed (checked) steps exactly as they are.\n"
            "- Update only the open (unchecked) steps to reflect the latest issue description and comments.\n"
            "- Add new steps if the issue description or comments require additional work.\n"
            "- Remove open steps that are no longer relevant.\n"
            "- Keep the '## Steps' section and the existing file format.\n"
            "- Keep step numbering sequential and stable.\n"
            "- The last step must always verify that `make test` succeeds.\n"
            "- Do not commit, do not push, and do not create a PR.\n"
        )

        result = self.execute_fn(
            instructions,
            repo_dir,
            self.agent_args,
            self.timeout,
            task_name="github_issue",
        )

        if not result.get("success", False):
            return {
                "success": False,
                "error": result.get("error", "Failed to update task file via CLI"),
            }

        try:
            updated_plan = PlanParser.parse_file(task_path)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse updated task file: {str(e)}",
            }

        if not updated_plan.steps:
            return {
                "success": False,
                "error": "Updated task file does not contain any executable steps",
            }

        return {"success": True}

    def _refine_issue_task_file(
        self,
        repo_dir: Path,
        task_path: Path,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> Dict[str, Any]:
        """Ask slopmachine to refine the task into concrete steps with acceptance criteria."""
        instructions = self._build_refinement_instructions(
            task_path=task_path,
            issue_title=issue_title,
            issue_body=issue_body,
            comment_texts=comment_texts,
            branch_name=branch_name,
        )
        result = self.execute_fn(
            instructions,
            repo_dir,
            self.agent_args,
            self.timeout,
            task_name="github_issue",
        )

        if not result.get("success", False):
            return {
                "success": False,
                "error": result.get("error", "Task refinement failed"),
            }

        try:
            refined_plan = PlanParser.parse_file(task_path)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse refined task file: {str(e)}",
            }

        if not refined_plan.steps:
            return {
                "success": False,
                "error": "Refined task file does not contain any executable steps",
            }

        return {"success": True}

    def _ensure_last_step_is_make_test(self, task_path: Path) -> None:
        """Ensure the last task step always verifies that make test succeeds."""
        try:
            plan = PlanParser.parse_file(task_path)
        except Exception:
            return

        if not plan.steps:
            return

        last_step = plan.steps[-1]
        if "make test" in last_step.description.lower():
            return

        next_step_number = last_step.number + 1
        append_content = (
            f"\n- [ ] {next_step_number}. Run `make test` and confirm it succeeds.\n"
            "  - Acceptance Criteria:\n"
            "    - `make test` exits successfully.\n"
        )
        with task_path.open("a") as task_file:
            task_file.write(append_content)


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
