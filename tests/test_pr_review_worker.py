"""Tests for PRReviewWorker."""

from pathlib import Path
from unittest.mock import patch

from auto_slopp.workers.pr_review_worker import PrReviewWorker


class TestPRReviewWorker:
    """Tests for PRReviewWorker."""

    def test_no_open_prs_with_label(self):
        """Test that worker returns early when no PRs have the required label."""
        worker = PrReviewWorker()
        repo_dir = Path("/tmp/repo")

        with patch("auto_slopp.workers.pr_review_worker.validate_repository") as mock_validate:
            mock_validate.return_value = {"valid": True}
            with patch("auto_slopp.workers.pr_review_worker.get_open_prs_with_label") as mock_get_prs:
                mock_get_prs.return_value = []
                with patch("auto_slopp.workers.pr_review_worker.settings") as mock_settings:
                    mock_settings.pr_review_worker_required_label = "AI Review"
                    result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert result["repositories_processed"] == 1
        assert result["pr_reviews_completed"] == 0
        assert result["errors"] == []
        mock_get_prs.assert_called_once_with(repo_dir, "AI Review")

    def test_review_pr_success(self):
        """Test reviewing a PR with successful CLI execution and comment posting."""
        worker = PrReviewWorker()
        repo_dir = Path("/tmp/repo")

        mock_pr = {
            "number": 123,
            "title": "Add feature",
            "body": "This is a PR",
        }

        mock_diff = "diff --git a/file.txt b/file.txt\n+new line"
        mock_instructions = "review instructions"
        mock_review_output = "suggestion: improve code\nissue: potential bug"
        mock_formatted_comments = "suggestion: improve code\nissue: potential bug"

        with patch("auto_slopp.workers.pr_review_worker.validate_repository") as mock_validate:
            mock_validate.return_value = {"valid": True}
            with patch("auto_slopp.workers.pr_review_worker.get_open_prs_with_label") as mock_get_prs:
                mock_get_prs.return_value = [mock_pr]
                with patch("auto_slopp.workers.pr_review_worker.get_pr_files") as mock_get_files:
                    mock_get_files.return_value = mock_diff
                    with patch("auto_slopp.workers.pr_review_worker.settings") as mock_settings:
                        mock_settings.pr_review_worker_required_label = "AI Review"
                        mock_settings.pr_review_worker_min_comments = 1
                        mock_settings.pr_review_worker_max_comments = 5
                        with patch("auto_slopp.workers.pr_review_worker._build_review_instructions") as mock_build:
                            mock_build.return_value = mock_instructions
                            with patch("auto_slopp.workers.pr_review_worker.run_cli_executor") as mock_run_cli:
                                mock_run_cli.return_value = {
                                    "success": True,
                                    "stdout": mock_review_output,
                                }
                                with patch("auto_slopp.workers.pr_review_worker.submit_pr_review") as mock_submit:
                                    mock_submit.return_value = True
                                    with patch("auto_slopp.workers.pr_review_worker.remove_label_from_issue") as mock_remove:
                                        mock_remove.return_value = True
                                        with patch("auto_slopp.workers.pr_review_worker.PRReviewWorker._format_conventional_comments") as mock_format:
                                            mock_format.return_value = mock_formatted_comments
                                            result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert result["repositories_processed"] == 1
        assert result["pr_reviews_completed"] == 1
        assert result["errors"] == []
        mock_get_prs.assert_called_once_with(repo_dir, "AI Review")
        mock_get_files.assert_called_once_with(repo_dir, 123)
        mock_build.assert_called_once_with("Add feature", "This is a PR", mock_diff)
        mock_run_cli.assert_called_once()
        mock_submit.assert_called_once_with(repo_dir, 123, mock_formatted_comments, event="COMMENT")
        mock_remove.assert_called_once_with(repo_dir, 123, "AI Review")

    def test_review_pr_cli_failure(self):
        """Test handling when the CLI tool fails to review the PR."""
        worker = PrReviewWorker()
        repo_dir = Path("/tmp/repo")

        mock_pr = {
            "number": 456,
            "title": "Fix bug",
            "body": "",
        }

        mock_diff = "diff"
        mock_instructions = "review instructions"

        with patch("auto_slopp.workers.pr_review_worker.validate_repository") as mock_validate:
            mock_validate.return_value = {"valid": True}
            with patch("auto_slopp.workers.pr_review_worker.get_open_prs_with_label") as mock_get_prs:
                mock_get_prs.return_value = [mock_pr]
                with patch("auto_slopp.workers.pr_review_worker.get_pr_files") as mock_get_files:
                    mock_get_files.return_value = mock_diff
                    with patch("auto_slopp.workers.pr_review_worker.settings") as mock_settings:
                        mock_settings.pr_review_worker_required_label = "AI Review"
                        mock_settings.pr_review_worker_min_comments = 1
                        mock_settings.pr_review_worker_max_comments = 5
                        with patch("auto_slopp.workers.pr_review_worker._build_review_instructions") as mock_build:
                            mock_build.return_value = mock_instructions
                            with patch("auto_slopp.workers.pr_review_worker.run_cli_executor") as mock_run_cli:
                                mock_run_cli.return_value = {
                                    "success": False,
                                    "error": "CLI tool error",
                                }
                                with patch("auto_slopp.workers.pr_review_worker.remove_label_from_issue") as mock_remove:
                                    result = worker._process_repository(repo_dir)

        assert result["success"] is True  # The worker itself doesn't fail, it just records errors
        assert result["repositories_processed"] == 1
        assert result["pr_reviews_completed"] == 0
        assert len(result["errors"]) == 1
        assert "CLI tool failed to review PR #456" in result["errors"][0]
        mock_get_prs.assert_called_once_with(repo_dir, "AI Review")
        mock_get_files.assert_called_once_with(repo_dir, 456)
        mock_build.assert_called_once_with("Fix bug", "", mock_diff)
        mock_run_cli.assert_called_once()
        # Even if CLI fails, we still attempt to remove the label? No, we skip to the next PR without removing the label.
        mock_remove.assert_not_called()

    def test_review_pr_empty_output(self):
        """Test handling when the CLI tool returns no review output."""
        worker = PrReviewWorker()
        repo_dir = Path("/tmp/repo")

        mock_pr = {
            "number": 789,
            "title": "Docs update",
            "body": "Update README",
        }

        mock_diff = "diff"
        mock_instructions = "review instructions"

        with patch("auto_slopp.workers.pr_review_worker.validate_repository") as mock_validate:
            mock_validate.return_value = {"valid": True}
            with patch("auto_slopp.workers.pr_review_worker.get_open_prs_with_label") as mock_get_prs:
                mock_get_prs.return_value = [mock_pr]
                with patch("auto_slopp.workers.pr_review_worker.get_pr_files") as mock_get_files:
                    mock_get_files.return_value = mock_diff
                    with patch("auto_slopp.workers.pr_review_worker.settings") as mock_settings:
                        mock_settings.pr_review_worker_required_label = "AI Review"
                        mock_settings.pr_review_worker_min_comments = 1
                        mock_settings.pr_review_worker_max_comments = 5
                        with patch("auto_slopp.workers.pr_review_worker._build_review_instructions") as mock_build:
                            mock_build.return_value = mock_instructions
                            with patch("auto_slopp.workers.pr_review_worker.run_cli_executor") as mock_run_cli:
                                mock_run_cli.return_value = {
                                    "success": True,
                                    "stdout": "",  # Empty output
                                }
                                with patch("auto_slopp.workers.pr_review_worker.remove_label_from_issue") as mock_remove:
                                    result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert result["repositories_processed"] == 1
        assert result["pr_reviews_completed"] == 1  # Still counted as reviewed? Yes, the code increments prs_reviewed even if output is empty.
        assert result["errors"] == []
        mock_get_prs.assert_called_once_with(repo_dir, "AI Review")
        mock_get_files.assert_called_once_with(repo_dir, 789)
        mock_build.assert_called_once_with("Docs update", "Update README", mock_diff)
        mock_run_cli.assert_called_once()
        # In the empty output case, we call remove_label_from_issue once (inside the if not review_output block) and then we do NOT call it again after? Let's see:
        #   if not review_output:
        #       ... 
        #       remove_success = remove_label_from_issue(...)   # <-- first call
        #       if not remove_success: ...
        #       results["prs_reviewed"] += 1
        #       continue   # <-- skips the rest of the loop for this PR
        # So we do not reach the code after the continue. Therefore, we expect exactly one call to remove_label_from_issue.
        mock_remove.assert_called_once_with(repo_dir, 789, "AI Review")

    def test_review_pr_submit_failure(self):
        """Test handling when submitting the review fails."""
        worker = PrReviewWorker()
        repo_dir = Path("/tmp/repo")

        mock_pr = {
            "number": 101,
            "title": "Chore",
            "body": "",
        }

        mock_diff = "diff"
        mock_instructions = "review instructions"
        mock_review_output = "suggestion: fix typo"
        mock_formatted_comments = "suggestion: fix typo"

        with patch("auto_slopp.workers.pr_review_worker.validate_repository") as mock_validate:
            mock_validate.return_value = {"valid": True}
            with patch("auto_slopp.workers.pr_review_worker.get_open_prs_with_label") as mock_get_prs:
                mock_get_prs.return_value = [mock_pr]
                with patch("auto_slopp.workers.pr_review_worker.get_pr_files") as mock_get_files:
                    mock_get_files.return_value = mock_diff
                    with patch("auto_slopp.workers.pr_review_worker.settings") as mock_settings:
                        mock_settings.pr_review_worker_required_label = "AI Review"
                        mock_settings.pr_review_worker_min_comments = 1
                        mock_settings.pr_review_worker_max_comments = 5
                        with patch("auto_slopp.workers.pr_review_worker._build_review_instructions") as mock_build:
                            mock_build.return_value = mock_instructions
                            with patch("auto_slopp.workers.pr_review_worker.run_cli_executor") as mock_run_cli:
                                mock_run_cli.return_value = {
                                    "success": True,
                                    "stdout": mock_review_output,
                                }
                                with patch("auto_slopp.workers.pr_review_worker.submit_pr_review") as mock_submit:
                                    mock_submit.return_value = False  # Simulate failure
                                    with patch("auto_slopp.workers.pr_review_worker.remove_label_from_issue") as mock_remove:
                                        result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert result["repositories_processed"] == 1
        assert result["pr_reviews_completed"] == 1  # Still counted as reviewed? Yes, the code increments prs_reviewed after removing label, regardless of submit success.
        assert len(result["errors"]) == 1
        assert "Failed to submit review for PR #101" in result["errors"][0]
        mock_get_prs.assert_called_once_with(repo_dir, "AI Review")
        mock_get_files.assert_called_once_with(repo_dir, 101)
        mock_build.assert_called_once_with("Chore", "", mock_diff)
        mock_run_cli.assert_called_once()
        mock_submit.assert_called_once_with(repo_dir, 101, mock_formatted_comments, event="COMMENT")
        # In the submit failure case, we call remove_label_from_issue twice? Let's see:
        #   if not review_success:
        #       ... 
        #       remove_success = remove_label_from_issue(...)   # <-- first call (inside the if block)
        #   else:
        #       ... 
        #   # Remove the "AI Review" label to prevent re-review
        #   remove_success = remove_label_from_issue(...)   # <-- second call (outside the if-else)
        # So we expect two calls to remove_label_from_issue.
        assert mock_remove.call_count == 2
        mock_remove.assert_any_call(repo_dir, 101, "AI Review")

    def test_review_pr_remove_label_failure(self):
        """Test handling when removing the label fails (but we still count as reviewed)."""
        worker = PrReviewWorker()
        repo_dir = Path("/tmp/repo")

        mock_pr = {
            "number": 202,
            "title": "Feature",
            "body": "",
        }

        mock_diff = "diff"
        mock_instructions = "review instructions"
        mock_review_output = "praise: great job"
        mock_formatted_comments = "praise: great job"

        with patch("auto_slopp.workers.pr_review_worker.validate_repository") as mock_validate:
            mock_validate.return_value = {"valid": True}
            with patch("auto_slopp.workers.pr_review_worker.get_open_prs_with_label") as mock_get_prs:
                mock_get_prs.return_value = [mock_pr]
                with patch("auto_slopp.workers.pr_review_worker.get_pr_files") as mock_get_files:
                    mock_get_files.return_value = mock_diff
                    with patch("auto_slopp.workers.pr_review_worker.settings") as mock_settings:
                        mock_settings.pr_review_worker_required_label = "AI Review"
                        mock_settings.pr_review_worker_min_comments = 1
                        mock_settings.pr_review_worker_max_comments = 5
                        with patch("auto_slopp.workers.pr_review_worker._build_review_instructions") as mock_build:
                            mock_build.return_value = mock_instructions
                            with patch("auto_slopp.workers.pr_review_worker.run_cli_executor") as mock_run_cli:
                                mock_run_cli.return_value = {
                                    "success": True,
                                    "stdout": mock_review_output,
                                }
                                with patch("auto_slopp.workers.pr_review_worker.submit_pr_review") as mock_submit:
                                    mock_submit.return_value = True
                                    with patch("auto_slopp.workers.pr_review_worker.remove_label_from_issue") as mock_remove:
                                        # First call (after submit) succeeds, second call (final removal) fails
                                        mock_remove.side_effect = [True, False]
                                        result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert result["repositories_processed"] == 1
        assert result["pr_reviews_completed"] == 1  # Still counted as reviewed
        assert result["errors"] == []  # No errors logged because the worker doesn't treat removal failure as an error? It logs a warning but doesn't add to errors.
        mock_get_prs.assert_called_once_with(repo_dir, "AI Review")
        mock_get_files.assert_called_once_with(repo_dir, 202)
        mock_build.assert_called_once_with("Feature", "", mock_diff)
        mock_run_cli.assert_called_once()
        mock_submit.assert_called_once_with(repo_dir, 202, mock_formatted_comments, event="COMMENT")
        assert mock_remove.call_count == 2
        mock_remove.assert_any_call(repo_dir, 202, "AI Review")

    def test_review_pr_exception_handling(self):
        """Test that unexpected exceptions are caught and reported."""
        worker = PrReviewWorker()
        repo_dir = Path("/tmp/repo")

        with patch("auto_slopp.workers.pr_review_worker.validate_repository") as mock_validate:
            mock_validate.return_value = {"valid": True}
            with patch("auto_slopp.workers.pr_review_worker.get_open_prs_with_label") as mock_get_prs:
                mock_get_prs.side_effect = Exception("Unexpected error")
                result = worker._process_repository(repo_dir)

        assert result["success"] is False
        assert "Unexpected error" in result["error"]
        assert result["repositories_processed"] == 0
        assert result["pr_reviews_completed"] == 0
        assert len(result["errors"]) == 1
        assert "Unexpected error" in result["errors"][0]

    def test_invalid_repository(self):
        """Test handling of an invalid repository."""
        worker = PrReviewWorker()
        repo_dir = Path("/tmp/repo")

        with patch("auto_slopp.workers.pr_review_worker.validate_repository") as mock_validate:
            mock_validate.return_value = {"valid": False, "errors": ["invalid repo"]}
            result = worker._process_repository(repo_dir)

        assert result["success"] is False
        assert "Invalid repository" in result["error"]
        assert result["repositories_processed"] == 0
        assert result["pr_reviews_completed"] == 0
        assert len(result["errors"]) == 1
        assert "invalid repo" in result["errors"][0]

    def test_repository_does_not_exist(self):
        """Test handling when the repository path does not exist."""
        worker = PrReviewWorker()
        repo_dir = Path("/non/existent/path")

        # No need to mock validate_repository because the early exit checks for existence
        result = worker._process_repository(repo_dir)

        assert result["success"] is False
        assert "Repository path does not exist" in result["error"]
        assert result["repositories_processed"] == 0
        assert result["pr_reviews_completed"] == 0
        assert result["errors"] == []


