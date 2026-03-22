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

    @staticmethod
    def _get_issue_task_path(repo_dir: Path, issue_number: int) -> Path:
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

    def _build_refinement_instructions(
        self,
        task_path: Path,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> str:
        """Build instructions for refining the issue task file."""
        comments_text = ""
        if comment_texts:
            comments_text = "\nComments:\n" + "\n".join(f"- {comment}" for comment in comment_texts if comment)

        return (
            f"You are already on branch '{branch_name}'. "
            f"Refine the GitHub issue task file at '{task_path}'.\n"
            f"Issue title: {issue_title}\n"
            f"Issue description:\n{issue_body}\n"
            f"{comments_text}\n\n"
            "Rewrite the file into concrete implementation steps with explicit acceptance criteria.\n"
            "Requirements for the file format:\n"
            "- Keep a section named '## Steps'.\n"
            "- Each step must use this exact format: '- [ ] <number>. <step description>'.\n"
            "- Every step must include acceptance criteria directly below it as bullets.\n"
            "- Keep step numbering sequential and stable.\n"
            "- The last step must always verify that `make test` succeeds.\n"
            "- Do not commit, do not push, and do not create a PR.\n"
        )

    def _execute_step(
        self,
        step: Step,
        plan: Plan,
        repo_dir: Path,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> Dict[str, Any]:
        """Execute a single step from the plan.

        Args:
            step: Step to execute
            plan: The full plan containing all steps
            repo_dir: Repository directory
            issue_title: GitHub issue title
            issue_body: GitHub issue body
            comment_texts: List of comment texts from the issue
            branch_name: Git branch name

        Returns:
            Execution result dictionary
        """
        step_instructions = self._build_step_instructions(
            step=step,
            plan=plan,
            issue_title=issue_title,
            issue_body=issue_body,
            comment_texts=comment_texts,
            branch_name=branch_name,
        )

        self.logger.info(f"Executing step {step.number}: {step.description}")

        result = self.execute_fn(
            step_instructions,
            repo_dir,
            self.agent_args,
            self.timeout,
            task_name="github_issue",
        )

        if result.get("success", False):
            self.logger.info(f"Step {step.number} completed successfully")
        else:
            self.logger.warning(f"Step {step.number} failed: {result.get('error', 'Unknown error')}")

        return result

    def _execute_step_acceptance_check(
        self,
        repo_dir: Path,
        task_path: Path,
        step: Step,
        issue_title: str,
        issue_body: str,
        branch_name: str,
    ) -> Dict[str, Any]:
        """Run acceptance criteria validation for a step.

        Args:
            repo_dir: Repository directory
            task_path: Path to the task file
            step: Step to validate
            issue_title: GitHub issue title
            issue_body: GitHub issue body
            branch_name: Git branch name

        Returns:
            Dictionary with 'success' key and optional 'error'
        """
        instructions = self._build_acceptance_check_instructions(
            task_path=task_path,
            step=step,
            issue_title=issue_title,
            issue_body=issue_body,
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
                "error": result.get("error", "Acceptance criteria check command failed"),
            }

        stdout_lower = (result.get("stdout") or "").lower()
        if "acceptance_status: fail" in stdout_lower or "acceptance status: fail" in stdout_lower:
            return {
                "success": False,
                "error": "Acceptance criteria were not fulfilled",
            }

        return {"success": True}

    def _update_remaining_steps(
        self,
        repo_dir: Path,
        task_path: Path,
        step: Step,
        issue_title: str,
        issue_body: str,
        branch_name: str,
    ) -> Dict[str, Any]:
        """Update future steps with details learned from a completed step.

        Args:
            repo_dir: Repository directory
            task_path: Path to the task file
            step: Step whose completion triggered the update
            issue_title: GitHub issue title
            issue_body: GitHub issue body
            branch_name: Git branch name

        Returns:
            Dictionary with 'success' key and optional 'error'
        """
        instructions = self._build_remaining_steps_update_instructions(
            task_path=task_path,
            step=step,
            issue_title=issue_title,
            issue_body=issue_body,
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
                "error": result.get("error", "Failed to update remaining steps"),
            }

        return {"success": True}

    def _build_step_instructions(
        self,
        step: Step,
        plan: Plan,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> str:
        """Build instructions for a single step.

        Args:
            step: Step to build instructions for
            plan: Current plan
            issue_title: Issue title
            issue_body: Issue body
            comment_texts: Comment texts
            branch_name: Branch name

        Returns:
            Instructions string for the step
        """
        body_text = f"\n{issue_body}" if issue_body else ""
        comments_text = ""
        if comment_texts:
            comments_text = "\nComments:\n" + "\n".join(f"- {comment}" for comment in comment_texts if comment)

        progress_info = self._build_progress_info(plan)

        return (
            f"You are already on branch '{branch_name}'. "
            f"Work on this branch, implement the changes, commit them, and push.\n"
            f"Implement the following:\n"
            f"Title: {issue_title}\n"
            f"Description:{body_text}\n"
            f"{comments_text}\n\n"
            f"Current Progress:\n{progress_info}\n\n"
            f"Your current task is Step {step.number}: {step.description}\n\n"
            f"Focus only on completing this step. Once done, mark it as complete in your work. "
            f"Keep your implementation simple. Only implement what is required. "
            f"Check if there are components you can reuse. "
            f"Ensure that 'make test' runs successful. Only push if ALL tests are successful. "
            f"Check if you need to update the README.md."
        )

    def _build_progress_info(self, plan: Plan) -> str:
        """Build progress information string.

        Args:
            plan: Current plan

        Returns:
            Progress information string
        """
        lines = []
        for step in plan.steps:
            status = "\u2713" if step.is_closed else "\u25cb"
            lines.append(f"{status} Step {step.number}: {step.description}")
        return "\n".join(lines)

    def _build_acceptance_check_instructions(
        self,
        task_path: Path,
        step: Step,
        issue_title: str,
        issue_body: str,
        branch_name: str,
    ) -> str:
        """Build instructions for acceptance criteria checks."""
        step_block = self._extract_step_block(task_path, step.number)
        return (
            f"You are already on branch '{branch_name}'. "
            f"Check acceptance criteria for Step {step.number} in '{task_path}'.\n"
            f"Issue title: {issue_title}\n"
            f"Issue description:\n{issue_body}\n\n"
            f"Step details:\n{step_block}\n\n"
            "Validate that all acceptance criteria are fulfilled.\n"
            "If all criteria are fulfilled, mark the step as completed in the task file.\n"
            "If criteria are not fulfilled, keep the step open.\n"
            "Do not commit, do not push, and do not create a PR.\n"
            "At the end, output exactly one line: ACCEPTANCE_STATUS: pass or ACCEPTANCE_STATUS: fail"
        )

    def _build_remaining_steps_update_instructions(
        self,
        task_path: Path,
        step: Step,
        issue_title: str,
        issue_body: str,
        branch_name: str,
    ) -> str:
        """Build instructions for updating remaining steps after a successful step."""
        step_block = self._extract_step_block(task_path, step.number)
        return (
            f"You are already on branch '{branch_name}'. "
            f"Update remaining open steps in '{task_path}' after completion of Step {step.number}.\n"
            f"Issue title: {issue_title}\n"
            f"Issue description:\n{issue_body}\n\n"
            f"Completed step details:\n{step_block}\n\n"
            "Update only unchecked steps to include concrete details learned from the completed step.\n"
            "Do not alter numbering, and do not modify completed steps.\n"
            "Do not commit, do not push, and do not create a PR."
        )

    def _extract_step_block(self, task_path: Path, step_number: int) -> str:
        """Extract a step block (step line plus child lines) from the task markdown file."""
        content = task_path.read_text()
        lines = content.splitlines()
        step_pattern = re.compile(r"^\s*-\s\[[ x]\]\s*\d+\.\s+")
        target_pattern = re.compile(rf"^\s*-\s\[[ x]\]\s*{step_number}\.\s+")

        start_idx: Optional[int] = None
        end_idx = len(lines)

        for idx, line in enumerate(lines):
            if target_pattern.match(line):
                start_idx = idx
                break

        if start_idx is None:
            return f"- [ ] {step_number}. {self._find_step_description(task_path, step_number)}"

        for idx in range(start_idx + 1, len(lines)):
            if step_pattern.match(lines[idx]):
                end_idx = idx
                break

        return "\n".join(lines[start_idx:end_idx]).strip()

    def _find_step_description(self, task_path: Path, step_number: int) -> str:
        """Fallback helper to retrieve the step description for a given step number."""
        try:
            plan = PlanParser.parse_file(task_path)
        except Exception:
            return "Unknown step"
        for step in plan.steps:
            if step.number == step_number:
                return step.description
        return "Unknown step"

    def _step_is_closed(self, task_path: Path, step_number: int) -> bool:
        """Check whether a step is marked as completed in the task file."""
        try:
            plan = PlanParser.parse_file(task_path)
        except Exception:
            return False
        for step in plan.steps:
            if step.number == step_number:
                return step.is_closed
        return False

    def _mark_step_completed_in_file(self, task_path: Path, step_number: int) -> None:
        """Mark a step as completed directly in markdown without rewriting the full file."""
        content = task_path.read_text()
        pattern = re.compile(rf"^(\s*-\s)\[\s\](\s*{step_number}\.\s+)", re.MULTILINE)
        updated_content, replacements = pattern.subn(r"\1[x]\2", content, count=1)
        if replacements > 0:
            task_path.write_text(updated_content)

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
