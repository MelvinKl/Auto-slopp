"""Verify that the pre-commit flake8 hook's ignore list matches pyproject.toml.

The flake8 hook in .pre-commit-config.yaml must ignore exactly the codes listed
in [tool.flake8] extend-ignore of pyproject.toml; otherwise pre-commit would
either miss violations or block valid code.
"""

import re
import sys
import tomllib
from pathlib import Path


def main() -> int:
    """Compare both ignore lists and exit non-zero if they differ."""
    root = Path(__file__).resolve().parent.parent
    pre_commit_path = root / ".pre-commit-config.yaml"
    pyproject_path = root / "pyproject.toml"

    with pyproject_path.open("rb") as f:
        pyproject = tomllib.load(f)
    pyproject_ignore = set(pyproject.get("tool", {}).get("flake8", {}).get("extend-ignore", []))

    pre_commit = pre_commit_path.read_text()
    hook_match = re.search(r"id:\s*flake8\b(?!\s*[-:])[\s\S]*?args:\s*\[([^\]]*)\]", pre_commit)
    if not hook_match:
        print("❌ Could not find the flake8 hook args in .pre-commit-config.yaml")
        return 1
    extend_ignore = re.search(r"--extend-ignore=([A-Za-z0-9,]+)", hook_match.group(1))
    if not extend_ignore:
        print("❌ flake8 hook in .pre-commit-config.yaml has no --extend-ignore argument")
        return 1
    hook_ignore = {code for code in extend_ignore.group(1).split(",") if code}

    if pyproject_ignore != hook_ignore:
        print(
            "❌ flake8 ignore lists are out of sync:\n"
            f"   .pre-commit-config.yaml: {sorted(hook_ignore)}\n"
            f"   pyproject.toml:          {sorted(pyproject_ignore)}"
        )
        return 1
    print(f"✅ flake8 ignore lists are in sync: {sorted(pyproject_ignore)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
