"""Tests for repository utilities."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from auto_slopp.utils.repository_utils import (
    discover_repositories,
    get_repository_status,
    is_git_repository,
    validate_repository,
)


class TestIsGitRepository:
    """Tests for is_git_repository function."""

    def test_is_git_repository_with_git_dir(self):
        """Test detection of git repository with .git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            git_dir = repo_dir / ".git"
            git_dir.mkdir()

            result = is_git_repository(repo_dir)
            assert result is True

    def test_is_git_repository_with_git_file(self):
        """Test detection of git repository with .git file (worktree)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            git_file = repo_dir / ".git"
            git_file.write_text("gitdir: /path/to/.git/worktrees")

            result = is_git_repository(repo_dir)
            assert result is True

    def test_is_git_repository_without_git(self):
        """Test detection of non-git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)

            result = is_git_repository(repo_dir)
            assert result is False

    def test_is_git_repository_with_exception(self):
        """Test is_git_repository handles exceptions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)

            with patch.object(Path, "is_dir", side_effect=PermissionError("Access denied")):
                result = is_git_repository(repo_dir)
                assert result is False


class TestValidateRepository:
    """Tests for validate_repository function."""

    def test_validate_repository_nonexistent(self):
        """Test validation of nonexistent directory."""
        repo_dir = Path("/nonexistent/repo")

        result = validate_repository(repo_dir)

        assert result["exists"] is False
        assert result["valid"] is False
        assert "Directory does not exist" in result["errors"]

    def test_validate_repository_not_a_directory(self):
        """Test validation of a file instead of directory."""
        with tempfile.NamedTemporaryFile() as temp_file:
            result = validate_repository(Path(temp_file.name))

            assert result["exists"] is True
            assert result["is_directory"] is False
            assert result["valid"] is False
            assert "Path is not a directory" in result["errors"]

    def test_validate_repository_not_git_repo(self):
        """Test validation of non-git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)

            result = validate_repository(repo_dir)

            assert result["exists"] is True
            assert result["is_git_repo"] is False
            assert result["valid"] is False
            assert any("Not a git repository" in err for err in result["errors"])

    def test_validate_repository_success(self):
        """Test successful repository validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            git_dir = repo_dir / ".git"
            git_dir.mkdir()

            with (
                patch(
                    "auto_slopp.utils.repository_utils.is_bare_repository",
                    return_value=False,
                ),
                patch(
                    "auto_slopp.utils.repository_utils.get_remotes",
                    return_value=["origin"],
                ),
                patch(
                    "auto_slopp.utils.repository_utils.get_default_branch",
                    return_value="main",
                ),
            ):
                result = validate_repository(repo_dir)

                assert result["exists"] is True
                assert result["is_git_repo"] is True
                assert result["has_remotes"] is True
                assert result["remotes"] == ["origin"]
                assert result["default_branch"] == "main"
                assert result["is_bare"] is False
                assert result["valid"] is True

    def test_validate_repository_exception(self):
        """Test validation handles exceptions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            git_dir = repo_dir / ".git"
            git_dir.mkdir()

            with patch(
                "auto_slopp.utils.repository_utils.is_bare_repository",
                side_effect=RuntimeError("Test error"),
            ):
                result = validate_repository(repo_dir)

                assert result["valid"] is False
                assert len(result["errors"]) > 0


class TestDiscoverRepositories:
    """Tests for discover_repositories function."""

    def test_discover_repositories_nonexistent_path(self):
        """Test discovery with nonexistent path."""
        result = discover_repositories(Path("/nonexistent"))

        assert result == []

    def test_discover_repositories_no_directories(self):
        """Test discovery with no subdirectories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            result = discover_repositories(repo_path)

            assert result == []

    def test_discover_repositories_with_files(self):
        """Test discovery with files (not directories)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            file_path = repo_path / "test_file.txt"
            file_path.write_text("content")

            result = discover_repositories(repo_path)

            assert len(result) == 0

    def test_discover_repositories_with_non_git_dirs(self):
        """Test discovery with non-git directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            subdir = repo_path / "subdir"
            subdir.mkdir()

            result = discover_repositories(repo_path, validate=False)

            assert len(result) == 1
            assert result[0]["name"] == "subdir"
            assert result[0]["is_git_repo"] is False

    def test_discover_repositories_with_git_dirs(self):
        """Test discovery with git directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            subdir = repo_path / "my_repo"
            subdir.mkdir()
            git_dir = subdir / ".git"
            git_dir.mkdir()

            result = discover_repositories(repo_path, validate=False)

            assert len(result) == 1
            assert result[0]["name"] == "my_repo"
            assert result[0]["is_git_repo"] is True

    def test_discover_repositories_with_validation(self):
        """Test discovery with validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            subdir = repo_path / "my_repo"
            subdir.mkdir()
            git_dir = subdir / ".git"
            git_dir.mkdir()

            with (
                patch(
                    "auto_slopp.utils.repository_utils.is_git_repository",
                    return_value=True,
                ),
                patch(
                    "auto_slopp.utils.repository_utils.validate_repository",
                    return_value={"valid": True, "is_git_repo": True},
                ),
            ):
                result = discover_repositories(repo_path, validate=True)

                assert len(result) == 1
                assert result[0]["valid"] is True


class TestGetRepositoryStatus:
    """Tests for get_repository_status function."""

    def test_get_repository_status_not_git_repo(self):
        """Test status for non-git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)

            result = get_repository_status(repo_dir)

            assert result["valid"] is False
            assert "Not a git repository" in result["error"]

    def test_get_repository_status_success(self):
        """Test successful status retrieval."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            git_dir = repo_dir / ".git"
            git_dir.mkdir()

            with (
                patch(
                    "auto_slopp.utils.repository_utils.is_git_repository",
                    return_value=True,
                ),
                patch(
                    "auto_slopp.utils.repository_utils.get_current_branch",
                    return_value="main",
                ),
                patch(
                    "auto_slopp.utils.repository_utils.has_changes",
                    return_value=False,
                ),
                patch(
                    "auto_slopp.utils.repository_utils.get_ahead_behind",
                    return_value=(0, 0),
                ),
            ):
                result = get_repository_status(repo_dir)

                assert result["valid"] is True
                assert result["current_branch"] == "main"
                assert result["is_clean"] is True
                assert result["ahead"] == 0
                assert result["behind"] == 0

    def test_get_repository_status_with_changes(self):
        """Test status with uncommitted changes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            git_dir = repo_dir / ".git"
            git_dir.mkdir()

            with (
                patch(
                    "auto_slopp.utils.repository_utils.is_git_repository",
                    return_value=True,
                ),
                patch(
                    "auto_slopp.utils.repository_utils.get_current_branch",
                    return_value="feature",
                ),
                patch(
                    "auto_slopp.utils.repository_utils.has_changes",
                    return_value=True,
                ),
                patch(
                    "auto_slopp.utils.repository_utils.get_ahead_behind",
                    return_value=(1, 2),
                ),
            ):
                result = get_repository_status(repo_dir)

                assert result["valid"] is True
                assert result["current_branch"] == "feature"
                assert result["is_clean"] is False
                assert result["ahead"] == 2
                assert result["behind"] == 1

    def test_get_repository_status_exception(self):
        """Test status handles exceptions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            git_dir = repo_dir / ".git"
            git_dir.mkdir()

            with (
                patch(
                    "auto_slopp.utils.repository_utils.is_git_repository",
                    return_value=True,
                ),
                patch(
                    "auto_slopp.utils.repository_utils.get_current_branch",
                    side_effect=RuntimeError("Git error"),
                ),
            ):
                result = get_repository_status(repo_dir)

                assert result["valid"] is False
                assert "Error getting repository status" in result["error"]
