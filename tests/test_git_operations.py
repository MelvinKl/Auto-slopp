"""Tests for git_operations module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from auto_slopp.utils.git_operations import (
    get_all_branches,
    get_current_branch,
    get_remote_branches,
)


class TestGetCurrentBranch:
    """Test cases for get_current_branch function."""

    def test_returns_branch_name(self, tmp_path):
        """Test that branch name is returned."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "main\n"

            result = get_current_branch(tmp_path)

            assert result == "main"
            mock_run.assert_called_once()


class TestGetAllBranches:
    """Test cases for get_all_branches function."""

    def test_returns_branch_list(self, tmp_path):
        """Test that branch list is returned."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "main\nfeature\nbugfix\n"

            result = get_all_branches(tmp_path)

            assert result == ["main", "feature", "bugfix"]


class TestGetRemoteBranches:
    """Test cases for get_remote_branches function."""

    def test_returns_remote_branch_list(self, tmp_path):
        """Test that remote branch list is returned."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "origin/main\norigin/feature\n"

            result = get_remote_branches(tmp_path)

            assert result == ["origin/main", "origin/feature"]
