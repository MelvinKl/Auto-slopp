"""Shared constants for auto_slopp."""

import re

# Lowercase substrings that indicate the LLM/CLI tool is unavailable.
# Patterns are matched case-insensitively via .lower() on the error message.
# Used by :class:`IssueWorker` and :class:`RalphExecutor` to distinguish
# temporary outages (which should trigger a skip for retry) from genuine
# iteration exhaustion (which should drop the task).
#
# Note: bare HTTP status codes are intentionally NOT listed here as plain
# substrings. They live in :data:`UNAVAILABILITY_STATUS_CODES` below and are
# matched with word boundaries so that incidental numbers in a message (a file
# path like ``/tmp/503/``, a line number in a stack trace, or a variable name
# containing ``429``) do not cause a false positive.
UNAVAILABILITY_PATTERNS: tuple[str, ...] = (
    "llm unavailable",
    "llm is unavailable",
    "llm is down",
    "service unavailable",
    "api unavailable",
    "api is down",
    "rate limit",
    "too many requests",
    "connection refused",
    "connection reset",
    "connection timeout",
    "econnrefused",
    "econnreset",
    "etimedout",
    "timed out",
    "no response",
    "not responding",
    "unreachable",
    "gateway timeout",
    "internal server error",
    # CLI-configuration-level outages reported by the CLI executor (e.g.
    # "No active CLI configuration", "All CLI configurations are in cooldown",
    # "No configuration meets the requirements").
    "no active cli",
    "all cli",
    "exhausted",
    "cooldown",
    "no configuration meets",
)

# Bare HTTP status codes that indicate unavailability. These are matched with
# word boundaries (e.g. ``re.search(r"\b503\b", ...)``) rather than as plain
# substrings, so that unrelated numbers embedded in an error message do not
# trigger a false positive.
UNAVAILABILITY_STATUS_CODES: tuple[str, ...] = (
    "429",
    "502",
    "503",
    "504",
)

_STATUS_CODE_PATTERNS = tuple(re.compile(rf"\b{code}\b") for code in UNAVAILABILITY_STATUS_CODES)


def error_indicates_llm_unavailability(error_msg: str) -> bool:
    """Return ``True`` if *error_msg* indicates the LLM/CLI tool is unavailable.

    Substring patterns in :data:`UNAVAILABILITY_PATTERNS` are matched
    case-insensitively. Bare HTTP status codes in
    :data:`UNAVAILABILITY_STATUS_CODES` are matched with word boundaries so that
    incidental numbers in the message (file paths, line numbers, identifiers)
    do not trigger a false positive.
    """
    error_lower = error_msg.lower()
    if any(pattern in error_lower for pattern in UNAVAILABILITY_PATTERNS):
        return True
    return any(pattern.search(error_lower) for pattern in _STATUS_CODE_PATTERNS)
