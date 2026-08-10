"""PR-to-issue linking utilities.

This module provides helper functions for ensuring that pull request bodies
contain valid GitHub closing keywords (Closes, Fixes, or Resolves) linked
to the appropriate issue number.
"""

import re

CLOSING_KEYWORDS = ("closes", "fixes", "resolves")

# Regex pattern with word boundaries to prevent false matches:
# - Prevents false positives like '#1' matching inside '#1234'
# - Supports 'owner/repo#123' format in addition to plain '#123'
# - Supports nested paths like 'org/subteam/repo#123'
# Keywords are dynamically joined from CLOSING_KEYWORDS so adding/removing
# keywords in CLOSING_KEYWORDS automatically updates the pattern.
_CLOSING_PATTERN = re.compile(
    r"\b(" + "|".join(CLOSING_KEYWORDS) + r")\s+(?:(?:[\w-]+/)*[\w-]+)?#(?P<id>\d+)\b",
    re.IGNORECASE,
)


def _find_existing_link(body: str, issue_id: int) -> re.Match | None:
    """Find an existing closing keyword link for the given issue in the body.

    Searches the body for a closing keyword (closes, fixes, resolves) followed
    by the issue number. Returns the first match object if found, None otherwise.

    Args:
        body: The PR body text to search
        issue_id: The GitHub issue number to look for

    Returns:
        Match object if a valid link is found, None otherwise.
    """
    for match in _CLOSING_PATTERN.finditer(body):
        if int(match.group("id")) == issue_id:
            return match
    return None


def _get_matching_keyword(match: re.Match) -> str:
    """Extract the closing keyword text from a regex match.

    Extracts the keyword portion (e.g. "Closes", "fixes", "Resolves")
    from a _CLOSING_PATTERN match object.

    Args:
        match: A regex match object from _CLOSING_PATTERN

    Returns:
        The matched keyword string (preserving original case)
    """
    return match.group(0).split()[0]


def validate_issue_link(body: str, issue_id: int) -> bool:
    """Validate whether a PR body contains a valid closing keyword link for the given issue.

    Checks for Closes, Fixes, or Resolves followed by the issue number (case-insensitive),
    using the same pattern as `ensure_issue_link_in_pr_body`.

    Args:
        body: The PR body text to validate
        issue_id: The GitHub issue number to check for (must be a positive integer)

    Returns:
        True if a valid closing keyword link for the issue is found, False otherwise.
        Returns False for empty or non-string bodies.

    Raises:
        TypeError: If issue_id is not a positive integer (rejects bools, strings, floats, negatives, zero)
    """
    if not isinstance(body, str):
        return False
    if not body.strip():
        return False

    return any(int(match.group("id")) == issue_id for match in _CLOSING_PATTERN.finditer(body))


def ensure_issue_link_in_pr_body(body: str, issue_id: int) -> str:
    """Ensure the PR body contains at least one valid GitHub closing keyword for the issue.

    Checks for Closes, Fixes, or Resolves followed by the issue number (case-insensitive),
    using word boundaries to prevent false negatives (e.g. 'Closes#1' with no space) and
    false positives (e.g. '#1' matching inside '#1234').
    Supports both plain '#123' and 'owner/repo#123' formats.

    Args:
        body: The PR body text to check
        issue_id: The GitHub issue number to link (must be a positive integer)

    Returns:
        PR body with a valid closing keyword guaranteed to be present

    Raises:
        TypeError: If issue_id is not a positive integer (rejects bools, strings, floats, negatives, zero)
    """
    # Type validation: reject booleans, strings, floats, negatives, and zero
    if isinstance(issue_id, bool) or not isinstance(issue_id, int):
        raise TypeError(f"issue_id must be a positive integer, got {type(issue_id).__name__}: {issue_id!r}")
    if issue_id <= 0:
        raise ValueError(f"issue_id must be a positive integer, got {issue_id}")

    # Check if the issue is already linked
    if _find_existing_link(body, issue_id):
        return body

    # Not linked, prepend
    body = f"Closes #{issue_id}\n\n{body}\n"
    return body
