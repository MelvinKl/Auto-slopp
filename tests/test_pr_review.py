"""Tests for the shared conservative PR review prompt."""

from auto_slopp.utils.pr_review import build_conservative_review_instructions


class TestBuildConservativeReviewInstructions:
    """Tests for build_conservative_review_instructions."""

    def test_includes_title_body_and_diff(self):
        """The prompt contains the PR title, body, and diff."""
        result = build_conservative_review_instructions("Fix bug", "Details here", "diff --git a/b c")
        assert "Fix bug" in result
        assert "Details here" in result
        assert "diff --git a/b c" in result

    def test_empty_body_has_no_description_text(self):
        """An empty body leaves the Description section blank without stray newlines."""
        empty = build_conservative_review_instructions("Fix bug", "", "diff")
        with_body = build_conservative_review_instructions("Fix bug", "Details", "diff")
        assert "Title: Fix bug\nDescription:\n\nDiff:" in empty
        assert "Description:\nDetails\n\nDiff:" in with_body

    def test_is_conservative(self):
        """The prompt instructs conservative, high-confidence reviews."""
        result = build_conservative_review_instructions("t", "b", "d")
        assert "conservative" in result.lower()
        assert "Do not invent problems" in result

    def test_uses_conventional_comment_prefixes(self):
        """The prompt uses the conventional comment prefixes."""
        result = build_conservative_review_instructions("t", "b", "d")
        for prefix in ("issue:", "suggestion:", "nit:", "chore:", "question:", "praise:"):
            assert prefix in result

    def test_same_prompt_for_all_call_sites(self):
        """Both review call sites delegate to this shared builder."""
        from unittest.mock import patch

        from auto_slopp.workers.issue_worker import IssueWorker
        from auto_slopp.workers.pr_review_worker import _build_review_instructions

        with (
            patch(
                "auto_slopp.workers.pr_review_worker.build_conservative_review_instructions",
                wraps=build_conservative_review_instructions,
            ) as pr_mock,
            patch(
                "auto_slopp.workers.issue_worker.build_conservative_review_instructions",
                wraps=build_conservative_review_instructions,
            ) as issue_mock,
        ):
            assert _build_review_instructions("t", "b", "d") == build_conservative_review_instructions("t", "b", "d")
            assert IssueWorker._build_review_instructions("t", "b", "d") == build_conservative_review_instructions(
                "t", "b", "d"
            )
            pr_mock.assert_called_once_with("t", "b", "d")
            issue_mock.assert_called_once_with("t", "b", "d")
