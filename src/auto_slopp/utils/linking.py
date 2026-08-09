"""PR-to-issue linking utilities.

This module provides helper functions for ensuring that pull request bodies
contain valid GitHub closing keywords (Closes, Fixes, or Resolves) linked
to the appropriate issue number.
"""

import re

CLOSING_KEYWORDS = ("closes", "fixes", "resolves")


def ensure_issue_link_in_pr_body(body: str, issue_id: int) -> str:
    """Ensure the PR body contains at least one valid GitHub closing keyword for the issue.

    Checks for Closes, Fixes, or Resolves followed by the issue number (case-insensitive),
    using word boundaries to prevent false negatives (e.g. 'Closes#1' with no space) and
    false positives (e.g. '#1' matching inside '#1234').
    If none are found, prepends "Closes #{issue_id}" to the body.

    Args:
        body: The PR body text to check
        issue_id: The GitHub issue number to link

    Returns:
        PR body with a valid closing keyword guaranteed to be present
    """
    pattern = rf"\b({'|'.join(CLOSING_KEYWORDS)})\s+#{issue_id}\b"
    if not re.search(pattern, body, re.IGNORECASE):
        body = f"Closes #{issue_id}\n\n{body}"
    return body
