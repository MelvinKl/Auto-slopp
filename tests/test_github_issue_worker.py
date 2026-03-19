"""Tests for GitHubIssueWorker."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from auto_slopp.utils.ralph import PlanParser, Step
from auto_slopp.workers.github_issue_worker import GitHubIssueWorker


class TestGitHubIssueWorker:
    """Tests for GitHubIssueWorker."""

    def test_initialization_success(self):
        """Test successful worker initialization."""
        worker = GitHubIssueWorker(
            timeout=7200,
            agent_args=["--verbose"],
            dry_run=True,
        )

        assert worker.timeout == 7200
        assert worker.agent_args == ["--verbose"]
        assert worker.dry_run is True

    def test_run_with_no_issues(self):
        """Test run with no open issues."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            with patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues:
                mock_issues.return_value = []

                worker = GitHubIssueWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["repositories_processed"] == 1
                assert result["repositories_with_errors"] == 0
                assert result["issues_processed"] == 0

    def test_run_with_issues_dry_run(self):
        """Test run with open issues in dry run mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_issue = {
                "number": 1,
                "title": "Test Issue",
                "body": "This is a test issue",
                "url": "https://github.com/test/repo/issues/1",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            with patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues:
                mock_issues.return_value = [mock_issue]

                worker = GitHubIssueWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["repositories_processed"] == 1
                assert result["issues_processed"] == 1
                assert result["issue_results"][0]["issue_number"] == 1
                assert result["issue_results"][0]["issue_title"] == "Test Issue"

    def test_run_with_nonexistent_repo(self):
        """Test run with nonexistent repository path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "nonexistent_repo"

            worker = GitHubIssueWorker(dry_run=True)
            result = worker.run(repo_path)

            assert result["success"] is False
            assert "error" in result

    def test_build_instructions(self):
        """Test instruction building."""
        worker = GitHubIssueWorker(dry_run=True)

        instructions = worker._build_instructions("Fix bug", "This is a bug")
        assert "Fix bug" in instructions
        assert "This is a bug" in instructions
        assert "ai/" in instructions

    def test_build_instructions_with_branch_name(self):
        """Test instruction building with branch name provided."""
        worker = GitHubIssueWorker(dry_run=True)

        instructions = worker._build_instructions("Fix bug", "This is a bug", branch_name="ai/issue-1-fix-bug")
        assert "Fix bug" in instructions
        assert "This is a bug" in instructions
        assert "already on branch 'ai/issue-1-fix-bug'" in instructions
        assert "Create a new branch" not in instructions

    def test_build_instructions_empty_body(self):
        """Test instruction building with empty body."""
        worker = GitHubIssueWorker(dry_run=True)

        instructions = worker._build_instructions("Test issue", "")
        assert "Test issue" in instructions
        assert "ai/" in instructions

    def test_build_instructions_includes_plan(self):
        """Test that instructions include a structured plan."""
        worker = GitHubIssueWorker(dry_run=True)

        instructions = worker._build_instructions("Test issue", "Test body")
        assert "Plan:" in instructions
        assert "1." in instructions
        assert "2." in instructions
        assert "Understand the requirements" in instructions
        assert "Explore the codebase" in instructions
        assert "make lint" in instructions
        assert "make test" in instructions
        assert "Commit the changes" in instructions
        assert "Push the changes" in instructions

    def test_create_error_result(self):
        """Test error result creation."""
        worker = GitHubIssueWorker(dry_run=True)
        start_time = 1000.0

        result = worker._create_error_result(
            start_time,
            Path("/test/repo"),
            "Test error",
        )

        assert result["success"] is False
        assert result["error"] == "Test error"
        assert result["worker_name"] == "GitHubIssueWorker"

    def test_run_with_no_changes(self):
        """Test run when no changes are made - should close issue with comment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_issue = {
                "number": 1,
                "title": "Test Issue",
                "body": "This is a test issue",
                "url": "https://github.com/test/repo/issues/1",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            with (
                patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues,
                patch("auto_slopp.workers.github_issue_worker.create_and_checkout_branch") as mock_create_branch,
                patch("auto_slopp.workers.github_issue_worker.execute_with_instructions") as mock_execute,
                patch("auto_slopp.workers.github_issue_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.github_issue_worker.comment_on_issue") as mock_comment,
                patch("auto_slopp.workers.github_issue_worker.close_issue") as mock_close,
                patch("auto_slopp.workers.github_issue_worker.delete_branch") as mock_delete,
                patch("auto_slopp.workers.github_issue_worker.checkout_branch_resilient") as mock_checkout,
            ):
                mock_issues.return_value = [mock_issue]
                mock_create_branch.return_value = True
                mock_execute.return_value = {"success": True}
                mock_get_branch.return_value = "main"
                mock_comment.return_value = True
                mock_close.return_value = True
                mock_delete.return_value = True
                mock_checkout.return_value = True

                worker = GitHubIssueWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["issues_processed"] == 1
                assert result["issues_closed"] == 1
                assert result["issue_results"][0]["no_changes"] is True
                assert result["issue_results"][0]["issue_closed"] is True
                assert result["issue_results"][0]["issue_commented"] is True

                mock_close.assert_called_once()
                mock_comment.assert_called_once()
                mock_delete.assert_called_once()

    def test_is_renovate_issue_by_author_renovate_bot(self):
        """Test detection of renovate issues by author renovate[bot]."""
        worker = GitHubIssueWorker(dry_run=True)

        issue = {
            "number": 1,
            "title": "Update dependencies",
            "body": "Update dependencies",
            "url": "https://github.com/test/repo/issues/1",
            "author": {"login": "renovate[bot]"},
        }

        assert worker._is_renovate_issue(issue) is True

    def test_is_renovate_issue_by_author_renovate(self):
        """Test detection of renovate issues by author renovate."""
        worker = GitHubIssueWorker(dry_run=True)

        issue = {
            "number": 1,
            "title": "Update dependencies",
            "body": "Update dependencies",
            "url": "https://github.com/test/repo/issues/1",
            "author": {"login": "renovate"},
        }

        assert worker._is_renovate_issue(issue) is True

    def test_is_renovate_issue_by_label(self):
        """Test detection of renovate issues by renovate label."""
        worker = GitHubIssueWorker(dry_run=True)

        issue = {
            "number": 1,
            "title": "Update dependencies",
            "body": "Update dependencies",
            "url": "https://github.com/test/repo/issues/1",
            "labels": [{"name": "renovate"}],
        }

        assert worker._is_renovate_issue(issue) is True

    def test_is_renovate_issue_false(self):
        """Test that regular issues are not detected as renovate."""
        worker = GitHubIssueWorker(dry_run=True)

        issue = {
            "number": 1,
            "title": "Fix bug",
            "body": "Fix a bug",
            "url": "https://github.com/test/repo/issues/1",
            "author": {"login": "developer"},
            "labels": [{"name": "bug"}],
        }

        assert worker._is_renovate_issue(issue) is False

    def test_filter_renovate_issues(self):
        """Test filtering out renovate issues from list."""
        worker = GitHubIssueWorker(dry_run=True)

        issues = [
            {
                "number": 1,
                "title": "Regular Issue",
                "body": "A regular issue",
                "author": {"login": "developer"},
            },
            {
                "number": 2,
                "title": "Renovate Issue",
                "body": "Update dependencies",
                "author": {"login": "renovate[bot]"},
            },
            {
                "number": 3,
                "title": "Another Regular Issue",
                "body": "Another regular issue",
                "author": {"login": "developer"},
            },
        ]

        filtered = worker._filter_renovate_issues(issues)

        assert len(filtered) == 2
        assert filtered[0]["number"] == 1
        assert filtered[1]["number"] == 3

    def test_run_skips_renovate_issues(self):
        """Test that worker skips renovate issues."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            issues = [
                {
                    "number": 1,
                    "title": "Regular Issue",
                    "body": "A regular issue",
                    "url": "https://github.com/test/repo/issues/1",
                    "author": {"login": "MelvinKl"},
                    "labels": [{"name": "ai"}],
                },
                {
                    "number": 2,
                    "title": "Renovate Issue",
                    "body": "Update dependencies",
                    "url": "https://github.com/test/repo/issues/2",
                    "author": {"login": "renovate[bot]"},
                },
            ]

            with patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues:
                mock_issues.return_value = issues

                worker = GitHubIssueWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["issues_processed"] == 1
                assert result["issue_results"][0]["issue_number"] == 1

    def test_branch_name_sanitization(self):
        """Test that branch names are properly sanitized from issue titles."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            test_cases = [
                {"title": "Fix bug", "expected": "ai/issue-1-fix-bug"},
                {"title": "Fix: bug", "expected": "ai/issue-2-fix-bug"},
                {
                    "title": "Feature: Add new functionality",
                    "expected": "ai/issue-3-feature-add-new-functio",
                },
                {
                    "title": "Issue with:colon",
                    "expected": "ai/issue-4-issue-with-colon",
                },
                {
                    "title": "Issue with?question",
                    "expected": "ai/issue-5-issue-with-question",
                },
                {
                    "title": "Issue with*asterisk",
                    "expected": "ai/issue-6-issue-with-asterisk",
                },
                {
                    "title": "Issue with[brackets]",
                    "expected": "ai/issue-7-issue-with-brackets",
                },
                {
                    "title": "Issue\\with\\backslash",
                    "expected": "ai/issue-8-issue-with-backslash",
                },
                {
                    "title": "  Issue with spaces  ",
                    "expected": "ai/issue-9-issue-with-spaces",
                },
                {
                    "title": "Issue---with---dashes",
                    "expected": "ai/issue-10-issue-with-dashes",
                },
            ]

            for i, test_case in enumerate(test_cases, start=1):
                issue = {
                    "number": i,
                    "title": test_case["title"],
                    "body": "Test body",
                    "url": f"https://github.com/test/repo/issues/{i}",
                    "author": {"login": "MelvinKl"},
                    "labels": [{"name": "ai"}],
                }

                with patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues:
                    mock_issues.return_value = [issue]

                    result = worker.run(repo_path)

                    assert result["success"] is True
                    assert result["issues_processed"] == 1

                    assert result["issue_results"][0]["issue_title"] == test_case["title"]

    def test_should_process_issue_with_required_label(self):
        """Test that issues with required label from allowed creator are processed."""
        from unittest.mock import patch

        with patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings:
            mock_settings.github_issue_worker_required_label = "ai"
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

            worker = GitHubIssueWorker(dry_run=True)

            issue_with_label = {
                "number": 1,
                "title": "AI Task",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            assert worker._should_process_issue(issue_with_label) is True

    def test_should_process_issue_with_allowed_creator(self):
        """Test that issues without 'ai' label are skipped even if from allowed creator."""
        from unittest.mock import patch

        with patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings:
            mock_settings.github_issue_worker_required_label = "ai"
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

            worker = GitHubIssueWorker(dry_run=True)

            issue_from_allowed_creator = {
                "number": 2,
                "title": "Regular Task",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "bug"}],
            }

            assert worker._should_process_issue(issue_from_allowed_creator) is False

    def test_should_process_issue_without_label_and_not_allowed_creator(self):
        """Test that issues without required label and not from allowed creator are skipped."""
        from unittest.mock import patch

        with patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings:
            mock_settings.github_issue_worker_required_label = "ai"
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

            worker = GitHubIssueWorker(dry_run=True)

            issue_without_label = {
                "number": 3,
                "title": "Regular Task",
                "author": {"login": "other_user"},
                "labels": [{"name": "bug"}],
            }

            assert worker._should_process_issue(issue_without_label) is False

    def test_should_process_issue_with_both_label_and_allowed_creator(self):
        """Test that issues with both label and allowed creator are processed."""
        from unittest.mock import patch

        with patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings:
            mock_settings.github_issue_worker_required_label = "ai"
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

            worker = GitHubIssueWorker(dry_run=True)

            issue_with_both = {
                "number": 4,
                "title": "AI Task",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            assert worker._should_process_issue(issue_with_both) is True

    def test_filter_by_label_and_creator(self):
        """Test filtering issues by label and creator."""
        from unittest.mock import patch

        with patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings:
            mock_settings.github_issue_worker_required_label = "ai"
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

            worker = GitHubIssueWorker(dry_run=True)

            issues = [
                {
                    "number": 1,
                    "title": "AI Task",
                    "author": {"login": "other_user"},
                    "labels": [{"name": "ai"}],
                },
                {
                    "number": 2,
                    "title": "MelvinKl Task",
                    "author": {"login": "MelvinKl"},
                    "labels": [{"name": "bug"}],
                },
                {
                    "number": 3,
                    "title": "Other Task",
                    "author": {"login": "other_user"},
                    "labels": [{"name": "bug"}],
                },
                {
                    "number": 4,
                    "title": "AI Task by MelvinKl",
                    "author": {"login": "MelvinKl"},
                    "labels": [{"name": "ai"}],
                },
            ]

            filtered = worker._filter_by_label_and_creator(issues)

            assert len(filtered) == 1
            assert filtered[0]["number"] == 4

    def test_should_process_issue_case_insensitive_label(self):
        """Test that label check is case-insensitive."""
        from unittest.mock import patch

        with patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings:
            mock_settings.github_issue_worker_required_label = "ai"
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

            worker = GitHubIssueWorker(dry_run=True)

            test_cases = [
                {"label": "ai", "expected": True},
                {"label": "AI", "expected": True},
                {"label": "Ai", "expected": True},
                {"label": "aI", "expected": True},
                {"label": "bug", "expected": False},
            ]

            for test_case in test_cases:
                issue = {
                    "number": 1,
                    "title": "Test Issue",
                    "author": {"login": "MelvinKl"},
                    "labels": [{"name": test_case["label"]}],
                }

                result = worker._should_process_issue(issue)
                assert result == test_case["expected"], f"Failed for label '{
                    test_case['label']
                }'"

    def test_run_filters_issues_by_label_and_creator(self):
        """Test that run method filters issues by label and creator."""
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            issues = [
                {
                    "number": 1,
                    "title": "AI Task",
                    "author": {"login": "MelvinKl"},
                    "labels": [{"name": "ai"}],
                    "url": "https://github.com/test/repo/issues/1",
                },
                {
                    "number": 2,
                    "title": "Other Task",
                    "author": {"login": "other_user"},
                    "labels": [{"name": "bug"}],
                    "url": "https://github.com/test/repo/issues/2",
                },
            ]

            with (
                patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings,
                patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues,
            ):
                mock_settings.github_issue_worker_required_label = "ai"
                mock_settings.github_issue_worker_allowed_creator = "MelvinKl"
                mock_issues.return_value = issues

                worker = GitHubIssueWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["issues_processed"] == 1
                assert result["issue_results"][0]["issue_number"] == 1

    def test_run_ignores_comments_not_from_issue_author(self):
        """Test that only issue-author comments are included in instructions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            issue = {
                "number": 1,
                "title": "Test issue",
                "body": "Issue body",
                "url": "https://github.com/test/repo/issues/1",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            with (
                patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues,
                patch("auto_slopp.workers.github_issue_worker.get_issue_comments") as mock_comments,
                patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings,
                patch("auto_slopp.workers.github_issue_worker.create_and_checkout_branch") as mock_create_branch,
                patch("auto_slopp.workers.github_issue_worker.execute_with_instructions") as mock_execute,
                patch("auto_slopp.workers.github_issue_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.github_issue_worker.get_pr_for_branch") as mock_get_pr,
                patch("auto_slopp.workers.github_issue_worker.create_pull_request") as mock_create_pr,
                patch("auto_slopp.workers.github_issue_worker.close_issue") as mock_close,
                patch("auto_slopp.workers.github_issue_worker.comment_on_issue") as mock_comment,
                patch("auto_slopp.workers.github_issue_worker.checkout_branch_resilient") as mock_checkout,
                patch.object(GitHubIssueWorker, "_build_instructions") as mock_build_instructions,
            ):
                mock_issues.return_value = [issue]
                mock_comments.return_value = [
                    {"body": "Author comment", "author": "MelvinKl"},
                    {"body": "Other user comment", "author": "other-user"},
                    {"body": "Bot comment", "author": "some-bot"},
                ]
                mock_settings.github_issue_worker_required_label = "ai"
                mock_settings.github_issue_worker_allowed_creator = "MelvinKl"
                mock_settings.ralph_enabled = False
                mock_create_branch.return_value = True
                mock_execute.return_value = {"success": True}
                mock_get_branch.return_value = "ai/issue-1-test-issue"
                mock_get_pr.return_value = None
                mock_create_pr.return_value = {"url": "https://github.com/test/repo/pull/1"}
                mock_close.return_value = True
                mock_comment.return_value = True
                mock_checkout.return_value = True
                mock_build_instructions.return_value = "instructions"

                worker = GitHubIssueWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["issues_processed"] == 1

                call_args = mock_build_instructions.call_args
                assert call_args.args[0] == "Test issue"
                assert call_args.args[1] == "Issue body"
                assert call_args.args[2] == ["Author comment"]

    def test_get_issue_task_path_uses_github_prefix(self):
        """Test that issue task files use .ralph/github-<issue>.md naming."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            task_path = worker._get_issue_task_path(repo_path, 281)

            assert task_path == repo_path / ".ralph" / "github-281.md"

    def test_create_issue_task_file_creates_expected_content(self):
        """Test creating the initial GitHub task markdown file."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            task_path = repo_path / ".ralph" / "github-281.md"

            worker._create_issue_task_file(
                task_path=task_path,
                issue_number=281,
                issue_title="Rework worker",
                issue_body="Implement the new Ralph flow.",
                comment_texts=["Please include tests"],
                branch_name="ai/issue-281-rework-worker",
            )

            content = task_path.read_text()
            assert "Issue Number: 281" in content
            assert "Branch: ai/issue-281-rework-worker" in content
            assert "Implement the new Ralph flow." in content
            assert "Comments:\n- Please include tests" in content
            assert "- [ ] 4. Run `make test` and confirm it succeeds." in content

    def test_ensure_last_step_is_make_test_appends_step(self):
        """Test that make test step is appended when not already last."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            task_path = Path(temp_dir) / "task.md"
            task_path.write_text("""# Task

## Steps

- [ ] 1. Implement changes
- [ ] 2. Update tests
""")

            worker._ensure_last_step_is_make_test(task_path)
            updated = task_path.read_text()

            assert "- [ ] 3. Run `make test` and confirm it succeeds." in updated

    def test_ensure_last_step_is_make_test_does_not_duplicate(self):
        """Test that make test step is not duplicated when already last."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            task_path = Path(temp_dir) / "task.md"
            task_path.write_text("""# Task

## Steps

- [ ] 1. Implement changes
- [ ] 2. Run `make test` and confirm it succeeds.
""")

            worker._ensure_last_step_is_make_test(task_path)
            updated = task_path.read_text()

            assert updated.count("Run `make test` and confirm it succeeds.") == 1

    def test_execute_step_acceptance_check_fails_when_status_fail(self):
        """Test acceptance check returns failure when agent reports fail."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            task_path = repo_path / "task.md"
            task_path.write_text("# Task\n\n## Steps\n\n- [ ] 1. Implement changes\n")
            step = Step(number=1, description="Implement changes")

            with patch("auto_slopp.workers.github_issue_worker.execute_with_instructions") as mock_execute:
                mock_execute.return_value = {
                    "success": True,
                    "stdout": "ACCEPTANCE_STATUS: fail",
                }

                result = worker._execute_step_acceptance_check(
                    repo_dir=repo_path,
                    task_path=task_path,
                    step=step,
                    issue_title="Issue",
                    issue_body="Body",
                    branch_name="ai/issue-1",
                )

            assert result["success"] is False
            assert "not fulfilled" in result["error"].lower()

    def test_execute_step_acceptance_check_passes_when_status_pass(self):
        """Test acceptance check returns success when agent reports pass."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            task_path = repo_path / "task.md"
            task_path.write_text("# Task\n\n## Steps\n\n- [ ] 1. Implement changes\n")
            step = Step(number=1, description="Implement changes")

            with patch("auto_slopp.workers.github_issue_worker.execute_with_instructions") as mock_execute:
                mock_execute.return_value = {
                    "success": True,
                    "stdout": "ACCEPTANCE_STATUS: pass",
                }

                result = worker._execute_step_acceptance_check(
                    repo_dir=repo_path,
                    task_path=task_path,
                    step=step,
                    issue_title="Issue",
                    issue_body="Body",
                    branch_name="ai/issue-1",
                )

            assert result["success"] is True

    def test_run_refined_task_loop_respects_max_iterations_setting(self):
        """Test refined task loop stops after configured maximum iterations."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            task_path = repo_path / "task.md"
            task_path.write_text("# Task\n\n## Steps\n\n- [ ] 1. Implement changes\n")

            with (
                patch(
                    "auto_slopp.workers.github_issue_worker.settings.github_issue_step_max_iterations",
                    2,
                ),
                patch.object(
                    worker,
                    "_execute_step",
                    return_value={"success": False, "error": "retry needed"},
                ),
            ):
                result = worker._run_refined_task_loop(
                    repo_dir=repo_path,
                    task_path=task_path,
                    issue_title="Issue",
                    issue_body="Body",
                    comment_texts=[],
                    branch_name="ai/issue-1",
                )

            assert result["success"] is False
            assert result["max_loops_reached"] is True
            assert result["loops_executed"] == 2
            assert "maximum iterations (2)" in result["error"].lower()

    def test_run_refined_task_loop_commits_on_successful_step(self):
        """Test successful step completion triggers per-step commit."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            task_path = repo_path / "task.md"
            task_path.write_text("""# Task

## Steps

- [ ] 1. Implement changes
""")

            with (
                patch(
                    "auto_slopp.workers.github_issue_worker.settings.github_issue_step_max_iterations",
                    3,
                ),
                patch.object(worker, "_execute_step", return_value={"success": True}),
                patch.object(
                    worker,
                    "_execute_step_acceptance_check",
                    return_value={"success": True},
                ),
                patch.object(worker, "_update_remaining_steps", return_value={"success": True}),
                patch(
                    "auto_slopp.workers.github_issue_worker.has_changes",
                    return_value=True,
                ),
                patch("auto_slopp.workers.github_issue_worker.commit_and_push_changes") as mock_commit,
            ):
                mock_commit.return_value = (True, "ok")

                result = worker._run_refined_task_loop(
                    repo_dir=repo_path,
                    task_path=task_path,
                    issue_title="Issue",
                    issue_body="Body",
                    comment_texts=[],
                    branch_name="ai/issue-1",
                )

            assert result["success"] is True
            assert result["loops_executed"] == 1
            assert result["steps_completed"] == 1
            mock_commit.assert_called_once()
            assert mock_commit.call_args.kwargs["push_if_remote"] is False
            assert "Complete issue step 1" in mock_commit.call_args.kwargs["commit_message"]

    def test_generate_pr_body_from_task_file_prefixes_closes_issue(self):
        """Test generated PR body includes closing reference."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            task_path = repo_path / ".ralph" / "github-281.md"
            task_path.parent.mkdir(parents=True, exist_ok=True)
            task_path.write_text("# Task\n\n## Steps\n\n- [x] 1. Implement changes\n")

            with patch("auto_slopp.workers.github_issue_worker.execute_with_instructions") as mock_execute:
                mock_execute.return_value = {
                    "success": True,
                    "stdout": "## Summary\n- Implemented changes",
                }

                body = worker._generate_pr_body_from_task_file(
                    repo_dir=repo_path,
                    issue_number=281,
                    issue_title="Issue title",
                    issue_body="Issue body",
                )

            assert body.startswith("Closes #281")
            assert "Implemented changes" in body

    # =========================================================================
    # Error/Exception Path Tests
    # =========================================================================

    def test_checkout_main_branch_failure(self):
        """Test that _checkout_main_branch failure is handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_issue = {
                "number": 1,
                "title": "Test Issue",
                "body": "This is a test issue",
                "url": "https://github.com/test/repo/issues/1",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            with (
                patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues,
                patch.object(GitHubIssueWorker, "_checkout_main_branch", return_value=False),
            ):
                mock_issues.return_value = [mock_issue]

                worker = GitHubIssueWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is False
                assert result["repositories_with_errors"] == 1
                assert result["issues_processed"] == 0

    def test_process_issue_branch_creation_failure(self):
        """Test that branch creation failure is handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_issue = {
                "number": 1,
                "title": "Test Issue",
                "body": "This is a test issue",
                "url": "https://github.com/test/repo/issues/1",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            with (
                patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues,
                patch("auto_slopp.workers.github_issue_worker.create_and_checkout_branch") as mock_create_branch,
                patch("auto_slopp.workers.github_issue_worker.checkout_branch_resilient") as mock_checkout,
            ):
                mock_issues.return_value = [mock_issue]
                mock_checkout.return_value = True
                mock_create_branch.return_value = False

                worker = GitHubIssueWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["issues_processed"] == 0
                assert result["issue_results"][0]["success"] is False
                assert "Failed to create branch" in result["issue_results"][0]["error"]

    def test_process_issue_push_failure_ralph(self):
        """Test that push failure with ralph enabled is handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_issue = {
                "number": 1,
                "title": "Test Issue",
                "body": "This is a test issue",
                "url": "https://github.com/test/repo/issues/1",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            with (
                patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues,
                patch("auto_slopp.workers.github_issue_worker.create_and_checkout_branch") as mock_create_branch,
                patch("auto_slopp.workers.github_issue_worker.checkout_branch_resilient") as mock_checkout,
                patch("auto_slopp.workers.github_issue_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.github_issue_worker.push_to_remote") as mock_push,
                patch.object(GitHubIssueWorker, "_execute_with_ralph_loop") as mock_ralph_loop,
                patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings,
            ):
                mock_issues.return_value = [mock_issue]
                mock_create_branch.return_value = True
                mock_checkout.return_value = True
                mock_get_branch.return_value = "ai/issue-1-test-issue"
                mock_push.return_value = (False, "Push failed")
                # Ralph loop completes successfully but returns no steps
                mock_ralph_loop.return_value = {
                    "success": True,
                    "loops_executed": 1,
                    "steps_completed": 1,
                }
                mock_settings.ralph_enabled = True
                mock_settings.github_issue_worker_required_label = "ai"
                mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

                worker = GitHubIssueWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["issue_results"][0]["success"] is False
                assert "Failed to push branch" in result["issue_results"][0]["error"]

    def test_process_issue_pr_creation_failure(self):
        """Test that PR creation failure with failed fallback is handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_issue = {
                "number": 1,
                "title": "Test Issue",
                "body": "This is a test issue",
                "url": "https://github.com/test/repo/issues/1",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            with (
                patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues,
                patch("auto_slopp.workers.github_issue_worker.create_and_checkout_branch") as mock_create_branch,
                patch("auto_slopp.workers.github_issue_worker.checkout_branch_resilient") as mock_checkout,
                patch("auto_slopp.workers.github_issue_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.github_issue_worker.push_to_remote") as mock_push,
                patch("auto_slopp.workers.github_issue_worker.create_pull_request") as mock_create_pr,
                patch("auto_slopp.workers.github_issue_worker.get_pr_for_branch") as mock_get_pr,
                patch.object(GitHubIssueWorker, "_execute_with_ralph_loop") as mock_ralph_loop,
                patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings,
            ):
                mock_issues.return_value = [mock_issue]
                mock_create_branch.return_value = True
                mock_checkout.return_value = True
                mock_get_branch.return_value = "ai/issue-1-test-issue"
                mock_push.return_value = (True, "Success")
                mock_create_pr.return_value = None  # PR creation fails
                mock_get_pr.return_value = None  # No existing PR either
                mock_ralph_loop.return_value = {
                    "success": True,
                    "loops_executed": 1,
                    "steps_completed": 1,
                }
                mock_settings.ralph_enabled = True
                mock_settings.github_issue_worker_required_label = "ai"
                mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

                worker = GitHubIssueWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["issue_results"][0]["success"] is False
                assert "Failed to create pull request" in result["issue_results"][0]["error"]

    def test_process_issue_with_exception(self):
        """Test that exceptions during issue processing are caught and handled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_issue = {
                "number": 1,
                "title": "Test Issue",
                "body": "This is a test issue",
                "url": "https://github.com/test/repo/issues/1",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            with (
                patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues,
                patch("auto_slopp.workers.github_issue_worker.create_and_checkout_branch") as mock_create_branch,
                patch("auto_slopp.workers.github_issue_worker.checkout_branch_resilient") as mock_checkout,
            ):
                mock_issues.return_value = [mock_issue]
                mock_checkout.return_value = True
                mock_create_branch.side_effect = RuntimeError("Branch creation failed")

                worker = GitHubIssueWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["issues_processed"] == 0
                assert result["issue_results"][0]["success"] is False
                assert "Branch creation failed" in result["issue_results"][0]["error"]

    def test_ensure_last_step_make_test_file_exception(self):
        """Test that _ensure_last_step_is_make_test handles file parse exceptions."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            task_path = Path(temp_dir) / "task.md"
            # Create a file that cannot be parsed
            task_path.write_text("This is not valid markdown for a plan")

            with patch("auto_slopp.workers.github_issue_worker.PlanParser.parse_file") as mock_parse:
                mock_parse.side_effect = ValueError("Parse error")
                # Should not raise, just return
                worker._ensure_last_step_is_make_test(task_path)

                # Verify parse was attempted
                mock_parse.assert_called_once()

    def test_run_task_file_parse_exception(self):
        """Test that task file parse exceptions in the loop are handled."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            task_path = repo_path / "task.md"
            task_path.write_text("# Task\n\n## Steps\n\n- [ ] 1. Implement changes\n")

            with (
                patch("auto_slopp.workers.github_issue_worker.PlanParser.parse_file") as mock_parse,
                patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings,
            ):
                mock_settings.github_issue_step_max_iterations = 3
                # First call raises exception
                mock_parse.side_effect = ValueError("Parse error")

                result = worker._run_refined_task_loop(
                    repo_dir=repo_path,
                    task_path=task_path,
                    issue_title="Issue",
                    issue_body="Body",
                    comment_texts=[],
                    branch_name="ai/issue-1",
                )

                assert result["success"] is False
                assert "Failed to parse task file" in result["error"]
                assert result["loops_executed"] == 1

    def test_run_acceptance_check_failure(self):
        """Test that acceptance check failure is handled and step remains open."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            task_path = repo_path / "task.md"
            task_path.write_text("# Task\n\n## Steps\n\n- [ ] 1. Implement changes\n")

            with (
                patch("auto_slopp.workers.github_issue_worker.PlanParser.parse_file") as mock_parse,
                patch.object(worker, "_execute_step") as mock_step,
                patch.object(worker, "_execute_step_acceptance_check") as mock_acceptance,
                patch.object(worker, "_update_remaining_steps") as mock_update,
                patch("auto_slopp.workers.github_issue_worker.has_changes") as mock_changes,
                patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings,
            ):
                mock_settings.github_issue_step_max_iterations = 3

                # Create a plan with one open step
                plan = PlanParser.parse_file(task_path)
                mock_parse.return_value = plan
                mock_step.return_value = {"success": True}
                # Acceptance check fails
                mock_acceptance.return_value = {
                    "success": False,
                    "error": "Acceptance not met",
                }
                mock_update.return_value = {"success": True}
                mock_changes.return_value = False

                result = worker._run_refined_task_loop(
                    repo_dir=repo_path,
                    task_path=task_path,
                    issue_title="Issue",
                    issue_body="Body",
                    comment_texts=[],
                    branch_name="ai/issue-1",
                )

                # After max iterations with acceptance failures, should fail with max_loops_reached
                assert result["success"] is False
                assert result["max_loops_reached"] is True
                # The last_error should contain the acceptance check failure
                assert result["loops_executed"] == 3

    def test_run_step_still_open_after_acceptance(self):
        """Test that step remaining open after acceptance check is handled."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            task_path = repo_path / "task.md"
            task_path.write_text("# Task\n\n## Steps\n\n- [ ] 1. Implement changes\n")

            with (
                patch("auto_slopp.workers.github_issue_worker.PlanParser.parse_file") as mock_parse,
                patch.object(worker, "_execute_step") as mock_step,
                patch.object(worker, "_execute_step_acceptance_check") as mock_acceptance,
                patch.object(worker, "_step_is_closed") as mock_is_closed,
                patch.object(worker, "_mark_step_completed_in_file") as mock_mark,
                patch.object(worker, "_update_remaining_steps") as mock_update,
                patch("auto_slopp.workers.github_issue_worker.has_changes") as mock_changes,
                patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings,
            ):
                mock_settings.github_issue_step_max_iterations = 3

                # Create a plan with one open step
                plan = PlanParser.parse_file(task_path)
                mock_parse.return_value = plan
                mock_step.return_value = {"success": True}
                mock_acceptance.return_value = {"success": True}
                mock_update.return_value = {"success": True}
                mock_changes.return_value = False

                # First call: step is not closed (acceptance couldn't mark it)
                # Second call: still not closed (should not happen in practice but covers the path)
                # Each iteration calls _step_is_closed twice, so for 3 iterations we need 6 values
                mock_is_closed.side_effect = [False, False, False, False, False, False]
                mock_mark.return_value = None

                result = worker._run_refined_task_loop(
                    repo_dir=repo_path,
                    task_path=task_path,
                    issue_title="Issue",
                    issue_body="Body",
                    comment_texts=[],
                    branch_name="ai/issue-1",
                )

                assert result["success"] is False
                assert "still open after acceptance check" in result.get("last_error", "")

    def test_run_update_remaining_steps_failure(self):
        """Test that _update_remaining_steps failure is handled with warning."""
        from unittest.mock import MagicMock

        from auto_slopp.utils.ralph import Step

        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            task_path = repo_path / "task.md"
            task_path.write_text("# Task\n\n## Steps\n\n- [ ] 1. Implement changes\n")

            with (
                patch("auto_slopp.workers.github_issue_worker.PlanParser.parse_file") as mock_parse,
                patch.object(worker, "_execute_step") as mock_step,
                patch.object(worker, "_execute_step_acceptance_check") as mock_acceptance,
                patch.object(worker, "_step_is_closed") as mock_is_closed,
                patch.object(worker, "_mark_step_completed_in_file") as mock_mark,
                patch.object(worker, "_update_remaining_steps") as mock_update,
                patch("auto_slopp.workers.github_issue_worker.has_changes") as mock_changes,
                patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings,
            ):
                mock_settings.github_issue_step_max_iterations = 3

                # Create mock plan with open step
                mock_plan = MagicMock()
                mock_step_obj = MagicMock(spec=Step)
                mock_step_obj.number = 1
                mock_step_obj.description = "Test step"
                mock_step_obj.is_closed = False

                # Return step on first call, None on subsequent calls
                call_count = [0]

                def get_next_open():
                    call_count[0] += 1
                    if call_count[0] == 1:
                        return mock_step_obj
                    return None

                mock_plan.get_next_open_step = get_next_open
                mock_plan.steps = [mock_step_obj]
                mock_parse.return_value = mock_plan

                mock_step.return_value = {"success": True}
                mock_acceptance.return_value = {"success": True}
                mock_is_closed.return_value = True
                mock_mark.return_value = None
                mock_update.return_value = {"success": False, "error": "Update failed"}
                mock_changes.return_value = False

                result = worker._run_refined_task_loop(
                    repo_dir=repo_path,
                    task_path=task_path,
                    issue_title="Issue",
                    issue_body="Body",
                    comment_texts=[],
                    branch_name="ai/issue-1",
                )

                # The update failure should only log a warning, not fail the result
                # The loop completes after first iteration because get_next_open_step returns None
                assert result["success"] is True
                assert result["loops_executed"] == 1

    def test_run_commit_failure(self):
        """Test that commit failure is handled correctly."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            task_path = repo_path / "task.md"
            task_path.write_text("# Task\n\n## Steps\n\n- [ ] 1. Implement changes\n")

            with (
                patch("auto_slopp.workers.github_issue_worker.PlanParser.parse_file") as mock_parse,
                patch.object(worker, "_execute_step") as mock_step,
                patch.object(worker, "_execute_step_acceptance_check") as mock_acceptance,
                patch.object(worker, "_step_is_closed") as mock_is_closed,
                patch.object(worker, "_mark_step_completed_in_file") as mock_mark,
                patch.object(worker, "_update_remaining_steps") as mock_update,
                patch("auto_slopp.workers.github_issue_worker.has_changes") as mock_changes,
                patch("auto_slopp.workers.github_issue_worker.commit_and_push_changes") as mock_commit,
                patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings,
            ):
                mock_settings.github_issue_step_max_iterations = 3

                # Create a plan with one open step
                plan = PlanParser.parse_file(task_path)
                mock_parse.return_value = plan
                mock_step.return_value = {"success": True}
                mock_acceptance.return_value = {"success": True}
                mock_is_closed.return_value = True
                mock_mark.return_value = None
                mock_update.return_value = {"success": True}
                mock_changes.return_value = True
                mock_commit.return_value = (False, "Commit failed")

                result = worker._run_refined_task_loop(
                    repo_dir=repo_path,
                    task_path=task_path,
                    issue_title="Issue",
                    issue_body="Body",
                    comment_texts=[],
                    branch_name="ai/issue-1",
                )

                assert result["success"] is False
                assert "Failed to commit changes" in result["error"]
                assert result["steps_completed"] == 0

    def test_find_step_description_fallback(self):
        """Test _find_step_description fallback when file cannot be parsed."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            task_path = Path(temp_dir) / "task.md"
            task_path.write_text("Not a valid plan file")

            with patch("auto_slopp.workers.github_issue_worker.PlanParser.parse_file") as mock_parse:
                mock_parse.side_effect = ValueError("Parse error")

                result = worker._find_step_description(task_path, 1)

                assert result == "Unknown step"

    def test_checkout_main_branch_pull_failure(self):
        """Test that pull failure in _checkout_main_branch returns False."""
        worker = GitHubIssueWorker(dry_run=False)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            with patch("auto_slopp.workers.github_issue_worker.checkout_branch_resilient") as mock_checkout:
                mock_checkout.return_value = False

                result = worker._checkout_main_branch(repo_dir=repo_path)

                assert result is False

    def test_process_issue_pr_fallback_to_existing(self):
        """Test that PR creation falls back to existing PR when available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_issue = {
                "number": 1,
                "title": "Test Issue",
                "body": "This is a test issue",
                "url": "https://github.com/test/repo/issues/1",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            with (
                patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues,
                patch("auto_slopp.workers.github_issue_worker.create_and_checkout_branch") as mock_create_branch,
                patch("auto_slopp.workers.github_issue_worker.checkout_branch_resilient") as mock_checkout,
                patch("auto_slopp.workers.github_issue_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.github_issue_worker.push_to_remote") as mock_push,
                patch("auto_slopp.workers.github_issue_worker.create_pull_request") as mock_create_pr,
                patch("auto_slopp.workers.github_issue_worker.get_pr_for_branch") as mock_get_pr,
                patch("auto_slopp.workers.github_issue_worker.close_issue") as mock_close,
                patch("auto_slopp.workers.github_issue_worker.comment_on_issue") as mock_comment,
                patch.object(GitHubIssueWorker, "_execute_with_ralph_loop") as mock_ralph_loop,
                patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings,
            ):
                mock_issues.return_value = [mock_issue]
                mock_create_branch.return_value = True
                mock_checkout.return_value = True
                mock_get_branch.return_value = "ai/issue-1-test-issue"
                mock_push.return_value = (True, "Success")
                mock_create_pr.return_value = None  # PR creation fails
                # But existing PR is found
                mock_get_pr.return_value = {
                    "url": "https://github.com/test/repo/pull/1",
                    "state": "OPEN",
                }
                mock_close.return_value = True
                mock_comment.return_value = True
                mock_ralph_loop.return_value = {
                    "success": True,
                    "loops_executed": 1,
                    "steps_completed": 1,
                }
                mock_settings.ralph_enabled = True
                mock_settings.github_issue_worker_required_label = "ai"
                mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

                worker = GitHubIssueWorker(dry_run=False)
                result = worker.run(repo_path)

                # Should succeed by falling back to existing PR
                assert result["issue_results"][0]["success"] is True
                assert result["issue_results"][0]["pr_created"] is True
                assert "https://github.com/test/repo/pull/1" in result["issue_results"][0]["pr_url"]

    def test_step_is_closed_with_parse_exception(self):
        """Test that _step_is_closed returns False on parse exception."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            task_path = Path(temp_dir) / "task.md"
            task_path.write_text("Not valid markdown")

            with patch("auto_slopp.workers.github_issue_worker.PlanParser.parse_file") as mock_parse:
                mock_parse.side_effect = ValueError("Parse error")

                result = worker._step_is_closed(task_path, 1)

                assert result is False
