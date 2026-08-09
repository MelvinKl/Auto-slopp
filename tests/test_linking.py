"""Tests for PR-to-issue linking utilities.

This module tests the `ensure_issue_link_in_pr_body` function and the
`CLOSING_KEYWORDS` constant from `auto_slopp.utils.linking`.
"""

import pytest

from auto_slopp.utils.linking import CLOSING_KEYWORDS, ensure_issue_link_in_pr_body


class TestClosingKeywords:
    """Tests for the CLOSING_KEYWORDS constant."""

    def test_closing_keywords_is_tuple(self):
        """Test that CLOSING_KEYWORDS is a tuple."""
        assert isinstance(CLOSING_KEYWORDS, tuple)

    def test_closing_keywords_contains_expected_values(self):
        """Test that CLOSING_KEYWORDS contains closes, fixes, resolves."""
        assert "closes" in CLOSING_KEYWORDS
        assert "fixes" in CLOSING_KEYWORDS
        assert "resolves" in CLOSING_KEYWORDS

    def test_closing_keywords_lowercase(self):
        """Test that all keywords are lowercase."""
        for keyword in CLOSING_KEYWORDS:
            assert keyword == keyword.lower()


class TestEnsureIssueLinkInPRBody:
    """Tests for the ensure_issue_link_in_pr_body function."""

    # --- Cases where link already exists (no prepend needed) ---

    def test_already_has_closes_link(self):
        """Test that body with 'Closes #1' is returned unchanged."""
        body = "Closes #1\n\nThis is the PR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_already_has_fixes_link(self):
        """Test that body with 'Fixes #1' is returned unchanged."""
        body = "Fixes #1\n\nThis is the PR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_already_has_resolves_link(self):
        """Test that body with 'Resolves #1' is returned unchanged."""
        body = "Resolves #1\n\nThis is the PR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_case_insensitive_closes(self):
        """Test that 'closes #1' (lowercase) is recognized."""
        body = "closes #1\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_case_insensitive_fixes(self):
        """Test that 'FIXES #1' (uppercase) is recognized."""
        body = "FIXES #1\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_case_insensitive_resolves(self):
        """Test that 'Resolves #1' (mixed case) is recognized."""
        body = "Resolves #1\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_link_in_middle_of_body(self):
        """Test that link anywhere in body is recognized."""
        body = "Some text\n\nFixes #42\n\nMore text here."
        result = ensure_issue_link_in_pr_body(body, 42)
        assert result == body

    def test_link_with_extra_whitespace_before_hash(self):
        """Test that 'Fixes  #1' (multiple spaces) is recognized."""
        body = "Fixes  #1\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_link_with_newline_between_keyword_and_hash(self):
        """Test that 'Fixes\n#1' (newline) is recognized."""
        body = "Fixes\n#1\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    # --- Cases where link is missing (prepend needed) ---

    def test_no_link_at_all(self):
        """Test that body without any link gets 'Closes #1' prepended."""
        body = "This is the PR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result.startswith("Closes #1\n\n")
        assert result.endswith(body + "\n")

    def test_empty_body(self):
        """Test that empty body gets 'Closes #1' prepended."""
        result = ensure_issue_link_in_pr_body("", 1)
        assert result == "Closes #1\n\n\n"

    def test_different_issue_number(self):
        """Test that body mentioning a different issue gets current issue prepended."""
        body = "Closes #99\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result.startswith("Closes #1\n\n")
        assert "Closes #99" in result

    # --- Edge cases from PR review ---

    def test_no_space_between_keyword_and_hash(self):
        """Test that 'Closes#1' (no space) does NOT match and gets prepended."""
        body = "Closes#1\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        # Should prepend because 'Closes#1' has no space
        assert result != body
        assert result.startswith("Closes #1\n\n")

    def test_hash_number_inside_larger_number(self):
        """Test that '#1' inside '#1234' does NOT match."""
        body = "Closes #1234\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        # Should prepend because #1 is not a separate token in #1234
        assert result != body
        assert result.startswith("Closes #1\n\n")

    def test_keyword_as_part_of_larger_word(self):
        """Test that 'Discloses #1' does NOT match (keyword is part of larger word)."""
        body = "Discloses #1\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        # Should prepend because 'Discloses' is not exactly 'Closes'
        assert result != body
        assert result.startswith("Closes #1\n\n")

    def test_keyword_as_part_of_larger_word_fixes(self):
        """Test that 'Refixes #1' does NOT match."""
        body = "Refixes #1\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result != body
        assert result.startswith("Closes #1\n\n")

    def test_keyword_as_part_of_larger_word_resolves(self):
        """Test that 'Unresolves #1' does NOT match."""
        body = "Unresolves #1\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result != body
        assert result.startswith("Closes #1\n\n")

    def test_hash_number_as_part_of_larger_number_multi_keyword(self):
        """Test that '#42' inside '#420' does NOT match for any keyword."""
        body = "Fixes #420\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 42)
        assert result != body
        assert result.startswith("Closes #42\n\n")

    def test_multi_digit_issue_id(self):
        """Test that multi-digit issue IDs work correctly."""
        body = "Fixes #123\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 123)
        assert result == body

    def test_multi_digit_issue_id_no_match(self):
        """Test that multi-digit issue ID doesn't match a substring."""
        body = "Fixes #1234\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 123)
        assert result != body
        assert result.startswith("Closes #123\n\n")

    def test_prepended_body_has_trailing_newline(self):
        """Test that the prepended link string ends with a trailing newline."""
        body = "PR content."
        result = ensure_issue_link_in_pr_body(body, 42)
        # The full result should end with a newline
        assert result.endswith("\n")

    def test_pr_body_ends_with_newline_on_prepend(self):
        """Test that the full prepended result ends with exactly one trailing newline."""
        body = "PR content."
        result = ensure_issue_link_in_pr_body(body, 42)
        # After the body text, there should be a trailing newline
        assert result.endswith("PR content.\n")

    def test_multiple_existing_links(self):
        """Test that body with multiple valid links is returned unchanged."""
        body = "Closes #1\n\nFixes #2\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_link_with_special_characters_after_issue_number(self):
        """Test that '#' followed by issue number and then punctuation still matches."""
        body = "Closes #1.\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_link_with_parentheses(self):
        """Test that '#1)' still matches the issue number."""
        body = "Closes #1) this fixes the bug."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_issue_id_as_word_boundary(self):
        """Test that '#1' at end of line (followed by newline) matches."""
        body = "Closes #1\n\nBody text."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    # --- Type validation tests ---

    def test_issue_id_bool_raises_type_error(self):
        """Test that passing a boolean for issue_id raises TypeError."""
        body = "PR body."
        with pytest.raises(TypeError):
            ensure_issue_link_in_pr_body(body, True)

    def test_issue_id_string_raises_type_error(self):
        """Test that passing a string for issue_id raises TypeError."""
        body = "PR body."
        with pytest.raises(TypeError):
            ensure_issue_link_in_pr_body(body, "1")

    def test_issue_id_float_raises_type_error(self):
        """Test that passing a float for issue_id raises TypeError."""
        body = "PR body."
        with pytest.raises(TypeError):
            ensure_issue_link_in_pr_body(body, 1.5)

    def test_issue_id_negative_raises_value_error(self):
        """Test that passing a negative integer for issue_id raises ValueError."""
        body = "PR body."
        with pytest.raises(ValueError, match="must be a positive integer"):
            ensure_issue_link_in_pr_body(body, -1)

    def test_issue_id_zero_raises_value_error(self):
        """Test that passing zero for issue_id raises ValueError."""
        body = "PR body."
        with pytest.raises(ValueError, match="must be a positive integer"):
            ensure_issue_link_in_pr_body(body, 0)

    # --- owner/repo#123 format tests ---

    def test_owner_repo_format_not_recognized(self):
        """Test that 'owner/repo#1' format is NOT recognized by the simple pattern."""
        body = "Closes owner/repo#1\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        # The simple pattern only matches plain #123, not owner/repo#123
        assert result != body
        assert result.startswith("Closes #1\n\n")

    def test_owner_repo_format_missing_link(self):
        """Test that body without owner/repo#1 link gets one prepended."""
        body = "PR body without link."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result.startswith("Closes #1\n\n")

    def test_owner_repo_format_different_repo(self):
        """Test that 'owner/repo#99' does not match issue_id=1."""
        body = "Closes owner/repo#99\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result != body
        assert result.startswith("Closes #1\n\n")

    def test_owner_repo_format_fixes_not_recognized(self):
        """Test that 'Fixes myorg/myrepo#42' is NOT recognized by the simple pattern."""
        body = "Fixes myorg/myrepo#42\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 42)
        assert result != body
        assert result.startswith("Closes #42\n\n")

    def test_owner_repo_format_resolves_not_recognized(self):
        """Test that 'Resolves some-org/some-repo#7' is NOT recognized by the simple pattern."""
        body = "Resolves some-org/some-repo#7\n\nPR body."
        result = ensure_issue_link_in_pr_body(body, 7)
        assert result != body
        assert result.startswith("Closes #7\n\n")

    # --- None body test ---

    def test_none_body_raises_type_error(self):
        """Test that passing None for body raises TypeError."""
        with pytest.raises(TypeError):
            ensure_issue_link_in_pr_body(None, 1)
