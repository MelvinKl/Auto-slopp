"""Pre-commit utilities package."""

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List


def get_staged_files(repo_dir: Path = Path.cwd()) -> List[str]:
    """Get list of staged files in the repository.

    Args:
        repo_dir: Path to the git repository (default: current directory)

    Returns:
        List of staged file paths
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except subprocess.CalledProcessError as e:
        return []


def get_staged_python_files(repo_dir: Path = Path.cwd()) -> List[str]:
    """Get list of staged Python files in the repository.

    Args:
        repo_dir: Path to the git repository (default: current directory)

    Returns:
        List of staged Python file paths
    """
    staged = get_staged_files(repo_dir)
    return [f for f in staged if f.endswith(".py")]


def check_pre_commit_hooks(repo_dir: Path = Path.cwd()) -> Dict[str, Any]:
    """Check if pre-commit hooks are configured.

    Args:
        repo_dir: Path to the git repository (default: current directory)

    Returns:
        Dictionary with pre-commit hook information
    """
    hooks_dir = repo_dir / ".git" / "hooks"
    pre_commit_hook = hooks_dir / "pre-commit"

    hooks_path = str(pre_commit_hook) if pre_commit_hook.exists() else None
    return {
        "pre_commit_hook_exists": pre_commit_hook.exists(),
        "pre_commit_hook_path": hooks_path,
    }


def main():
    """Main entry point for pre-commit CLI."""
    staged_files = get_staged_python_files()
    print(f"Staged Python files: {len(staged_files)}")
    for f in staged_files:
        print(f"  - {f}")

    hook_info = check_pre_commit_hooks()
    print(f"\nPre-commit hook configured: {hook_info['pre_commit_hook_exists']}")


if __name__ == "__main__":
    main()
