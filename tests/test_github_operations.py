"""Tests for GitHub operations utilities."""

from pathlib import Path
from unittest.mock import Mock, patch

from auto_slopp.utils.github_operations import get_open_issues


class TestGetOpenIssues:
    """Tests for GitHub issue listing behavior."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    @patch("auto_slopp.utils.github_operations.logger")
    def test_disabled_issues_are_skipped_without_error(self, mock_logger, mock_run_gh_command):
        """Test repositories with disabled issues are treated as a normal skip."""
        repo_dir = Path("/tmp/test_repo")
        mock_run_gh_command.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="the 'owner/repo' repository has disabled issues",
        )

        issues = get_open_issues(repo_dir)

        assert issues == []
        mock_logger.info.assert_called_once()
        mock_logger.error.assert_not_called()
