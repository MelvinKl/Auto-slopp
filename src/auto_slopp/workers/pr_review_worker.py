"""PR Review Worker for auto-slopp automation system.

This worker reviews pull requests with the "AI Review" label and provides
feedback using conventional comments format.
"""

import logging
from pathlib import Path
from typing import Any, Dict

from auto_slopp.utils.cli_executor import run_cli_executor
from auto_slopp.utils.github_operations import (
    get_open_prs_with_label,
    get_pr_files,
    remove_label_from_issue,
    submit_pr_review,
)
from auto_slopp.utils.pr_review import build_conservative_review_instructions
from auto_slopp.utils.repository_utils import validate_repository
from auto_slopp.worker import Worker
from settings.main import settings


def _build_review_instructions(title: str, body: str, diff: str) -> str:
    """Build instructions for the CLI tool to review a PR.

    Delegates to the shared conservative prompt in
    ``auto_slopp.utils.pr_review`` so both review call sites stay in sync.

    Args:
        title: PR title
        body: PR body description
        diff: PR diff content

    Returns:
        Instructions string for the CLI tool.
    """
    return build_conservative_review_instructions(title, body, diff)


class PrReviewWorker(Worker):
    """Worker for reviewing pull requests with conventional comments."""

    def __init__(self, timeout: int | None = None):
        """Initialize PrReviewWorker.

        Args:
            timeout: Timeout for CLI execution in seconds (default: from settings.slop_timeout)
        """
        self.timeout = timeout if timeout is not None else settings.slop_timeout
        self.logger = logging.getLogger("auto_slopp.workers.PrReviewWorker")

    def run(self, repo_path: Path) -> Dict[str, Any]:
        """Execute PR review workflow for a single repository.

        Args:
            repo_path: Path to the repository directory

        Returns:
            Dictionary containing execution results and summary.
        """
        self.logger.info(f"PrReviewWorker starting for {repo_path}")
        return self._process_repository(repo_path)

    def _process_repository(self, repo_dir: Path) -> Dict[str, Any]:
        """Process a single repository for PR reviews.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Dictionary containing execution results and summary.
        """
        if not repo_dir.exists():
            return {
                "worker_name": "PrReviewWorker",
                "success": False,
                "error": f"Repository path does not exist: {repo_dir}",
                "repositories_processed": 0,
                "pr_reviews_completed": 0,
                "errors": [],
            }

        results = {
            "worker_name": "PrReviewWorker",
            "success": True,
            "repositories_processed": 0,
            "pr_reviews_completed": 0,
            "errors": [],
        }

        # Validate the repository
        repo_info = validate_repository(repo_dir)
        if not repo_info.get("valid", False):
            self.logger.warning(
                f"Repository is invalid: {repo_dir.name} - {repo_info.get('errors', ['Unknown error'])}"
            )
            results["errors"].append(
                f"{repo_dir.name}: Invalid repository - {repo_info.get('errors', ['Unknown error'])}"
            )
            results["success"] = False
            results["error"] = f"Invalid repository - {repo_info.get('errors', ['Unknown error'])}"
            return results

        results["repositories_processed"] = 1
        self.logger.info(f"Processing repository: {repo_dir.name}")

        try:
            # Get the required label from settings
            required_label = settings.pr_review_worker_required_label

            # Get open PRs with the required label
            prs = get_open_prs_with_label(repo_dir, required_label)

            if not prs:
                self.logger.info(f"No open PRs with label '{required_label}' found in {repo_dir.name}")
                return results

            for pr in prs:
                pr_number = pr.get("number")
                pr_title = pr.get("title", "")

                self.logger.info(f"Reviewing PR #{pr_number}: {pr_title}")

                # Get the PR diff/files
                try:
                    diff = get_pr_files(repo_dir, pr_number)
                except Exception as e:
                    error_msg = f"Failed to get files for PR #{pr_number}: {str(e)}"
                    self.logger.error(error_msg)
                    results["errors"].append(error_msg)
                    continue

                # Prepare instructions for the CLI tool to review the PR
                instructions = _build_review_instructions(pr_title, pr.get("body", ""), diff)

                # Run the CLI tool to generate review comments
                review_result = run_cli_executor(
                    additional_instructions=instructions,
                    working_directory=repo_dir,
                    timeout=self.timeout,
                    capture_output=True,
                    task_name="pr_review",
                )

                if not review_result.get("success", False):
                    error_msg = (
                        f"CLI tool failed to review PR #{pr_number}: " f"{review_result.get('error', 'Unknown error')}"
                    )
                    self.logger.error(error_msg)
                    results["errors"].append(error_msg)
                    continue

                # Extract the review comments from the stdout
                review_output = review_result.get("stdout", "").strip()
                if not review_output:
                    self.logger.warning(f"No review output generated for PR #{pr_number}")
                    # Still remove the label to prevent infinite loop
                    remove_success = remove_label_from_issue(repo_dir, pr_number, required_label)
                    if not remove_success:
                        self.logger.warning(
                            f"Failed to remove '{required_label}' label from PR #{pr_number} after review"
                        )
                    results["pr_reviews_completed"] += 1
                    continue

                # Format the conventional comments
                formatted_comments = self._format_conventional_comments(review_output)

                # Submit the review
                review_success = submit_pr_review(repo_dir, pr_number, formatted_comments, event="COMMENT")

                if not review_success:
                    error_msg = f"Failed to submit review for PR #{pr_number}"
                    self.logger.error(error_msg)
                    results["errors"].append(error_msg)
                    # Still remove the label to prevent infinite loop on failure
                    remove_success = remove_label_from_issue(repo_dir, pr_number, required_label)
                    if not remove_success:
                        self.logger.warning(
                            f"Failed to remove '{required_label}' label from PR #{pr_number} after review failure"
                        )
                else:
                    self.logger.info(f"Successfully submitted review for PR #{pr_number}")

                # Remove the "AI Review" label to prevent re-review
                remove_success = remove_label_from_issue(repo_dir, pr_number, required_label)
                if not remove_success:
                    self.logger.warning(f"Failed to remove '{required_label}' label from PR #{pr_number} after review")

                results["pr_reviews_completed"] += 1

        except Exception as e:
            self.logger.error(f"Error processing repository {repo_dir.name}: {str(e)}")
            results["success"] = False
            results["error"] = str(e)
            results["errors"].append(str(e))

        self.logger.info(
            f"PrReviewWorker completed for {repo_dir.name}. "
            f"PRs reviewed: {results['pr_reviews_completed']}, "
            f"Errors: {len(results['errors'])}"
        )

        return results

    def _format_conventional_comments(self, raw_review: str) -> str:
        """Format the AI output into conventional comment syntax.

        Args:
            raw_review: Raw output from the AI CLI tool

        Returns:
            Formatted conventional comments string
        """
        # Split the input into lines
        lines = [line.strip() for line in raw_review.split("\n") if line.strip()]

        # Valid conventional comment prefixes
        valid_prefixes = [
            "suggestion:",
            "issue:",
            "nit:",
            "question:",
            "praise:",
            "chore:",
        ]

        formatted_lines = []
        for line in lines:
            # Check if the line already starts with a valid prefix (case-insensitive)
            line_lower = line.lower()
            has_valid_prefix = any(line_lower.startswith(prefix) for prefix in valid_prefixes)

            # Drop unprefixed lines: the prompt promises strictly prefixed
            # output, and prepending 'suggestion:' to stray prose would post
            # fake suggestions to the PR.
            if has_valid_prefix:
                formatted_lines.append(line)

        return "\n".join(formatted_lines)
