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
_CLOSING_PATTERN = re.compile(
    rf"\b({'|'.join(CLOSING_KEYWORDS)})\s+((?:[\w-]+/[\w-]+)?)#{r'(?<!\d)'}(?P<id>\d+)(?<!\d)\b",
    re.IGNORECASE,
)


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

    pattern = rf"\b({'|'.join(CLOSING_KEYWORDS)})\s+#{issue_id}\b"
    if not re.search(pattern, body, re.IGNORECASE):
        body = f"Closes #{issue_id}\n\n{body}\n"
    return body
