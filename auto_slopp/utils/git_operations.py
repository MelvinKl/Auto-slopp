import subprocess
from pathlib import Path


def get_current_branch(repo_path: Path) -> str:
    """Get the current branch name of a git repository.

    Args:
        repo_path: Path to the git repository.

    Returns:
        Name of the current branch.
    """
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_all_branches(repo_path: Path) -> list[str]:
    """Get all branch names in a git repository.

    Args:
        repo_path: Path to the git repository.

    Returns:
        List of branch names.
    """
    result = subprocess.run(
        ["git", "branch", "--format=%(refname:short)"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    return [b.strip() for b in result.stdout.strip().split("\n") if b.strip()]


def get_remote_branches(repo_path: Path) -> list[str]:
    """Get all remote branch names in a git repository.

    Args:
        repo_path: Path to the git repository.

    Returns:
        List of remote branch names.
    """
    result = subprocess.run(
        ["git", "branch", "-r", "--format=%(refname:short)"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    return [b.strip() for b in result.stdout.strip().split("\n") if b.strip()]
