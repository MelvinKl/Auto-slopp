"""Shared constants for auto_slopp."""

import re
from typing import Optional

# Lowercase substrings that indicate the LLM/CLI tool is unavailable.
# Patterns are matched case-insensitively via .lower() on the error message.
# Used by :class:`IssueWorker` and :class:`RalphExecutor` to distinguish
# temporary outages (which should trigger a skip for retry) from genuine
# iteration exhaustion (which should drop the task).
#
# Note: bare HTTP status codes are intentionally NOT listed here as plain
# substrings. They live in :data:`UNAVAILABILITY_STATUS_CODES` below and are
# matched with word boundaries so that a code embedded in a longer token
# (e.g. ``5034`` or ``x503y``) does not cause a false positive. A code
# appearing as a standalone number (e.g. in a file path like ``/tmp/503/file``
# or a line number) still matches.
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
    "gateway timeout",
    "internal server error",
    # CLI-configuration-level outages reported by the CLI executor (e.g.
    # "No active CLI configuration", "All CLI configurations are in cooldown",
    # "No configuration meets the requirements").
    "no active cli",
    "cooldown",
    "no configuration meets",
)

# Broad substrings that can also appear in genuine step/CLI-output failures
# (e.g. "retry limit exhausted" or "all clients disconnected" printed by a tool
# that actually ran). Matching one of these alone does NOT classify the error
# as LLM unavailability: the match must be corroborated by evidence that the
# LLM/CLI layer is actually down, i.e. an unavailability status code in the
# message, or all configured CLIs in cooldown (:func:`are_all_clis_in_cooldown`
# is True; a deployment with zero configured CLIs is a misconfiguration, not
# an outage).
WEAK_UNAVAILABILITY_PATTERNS: tuple[str, ...] = (
    "exhausted",
    "no response",
    "not responding",
    "unreachable",
    "all cli",
)

# Bare HTTP status codes that indicate unavailability. These are matched with
# word boundaries (e.g. ``re.search(r"\b503\b", ...)``) rather than as plain
# substrings, so that a code embedded in a longer token (e.g. ``5034``,
# ``x503y``) does not trigger a false positive. This only narrows the
# substring match to longer tokens: a code appearing as a standalone number
# (e.g. in a file path like ``/tmp/503/file`` or a line number such as
# ``line 503: ...``) still matches and can still cause a false positive.
UNAVAILABILITY_STATUS_CODES: tuple[str, ...] = (
    "429",
    "502",
    "503",
    "504",
)

_STATUS_CODE_PATTERNS = tuple(re.compile(rf"\b{code}\b") for code in UNAVAILABILITY_STATUS_CODES)


def error_indicates_llm_unavailability(error_msg: str, cli_available: Optional[bool] = None) -> bool:
    """Return ``True`` if *error_msg* indicates the LLM/CLI tool is unavailable.

    Substring patterns in :data:`UNAVAILABILITY_PATTERNS` are matched
    case-insensitively. Bare HTTP status codes in
    :data:`UNAVAILABILITY_STATUS_CODES` are matched with word boundaries so that
    a code embedded in a longer token (e.g. ``5034`` or ``x503y``) does not
    trigger a false positive; a code appearing as a standalone number (file
    paths, line numbers) still matches.

    Broad patterns in :data:`WEAK_UNAVAILABILITY_PATTERNS` can also appear in
    genuine step/CLI-output failures, so a match on them alone is not
    sufficient: it must be corroborated by an unavailability status code in
    the message or by all configured CLIs currently being in cooldown
    (:func:`are_all_clis_in_cooldown` returning ``True``; a deployment with
    zero configured CLIs is a misconfiguration, not an outage).

    Args:
        error_msg: The error message to inspect.
        cli_available: Optional explicit CLI-availability state used to
            corroborate weak patterns. The value mirrors the negation of
            :func:`are_all_clis_in_cooldown`: ``False`` means all *configured*
            CLIs are currently in cooldown, not merely that no CLI is
            available. A deployment with zero configured CLIs is a
            misconfiguration, not an outage, so callers must not pass
            ``False`` for one (in particular, do not derive the value from
            :func:`is_any_cli_available`, which is also ``False`` there). When
            ``None`` (the default), the live state is checked via
            :func:`are_all_clis_in_cooldown`. Passing an explicit value keeps
            the matching pure (no global state is read), which is also easier
            to unit test.
    """
    error_lower = error_msg.lower()
    if any(pattern in error_lower for pattern in UNAVAILABILITY_PATTERNS):
        return True
    if any(pattern.search(error_lower) for pattern in _STATUS_CODE_PATTERNS):
        return True
    if any(pattern in error_lower for pattern in WEAK_UNAVAILABILITY_PATTERNS):
        if cli_available is None:
            # Lazy import: keeps this module free of the CLI-execution/settings
            # machinery by default (and avoids a circular import if
            # cli_executor ever needs a constant).
            from auto_slopp.utils.cli_executor import are_all_clis_in_cooldown

            return are_all_clis_in_cooldown()
        return not cli_available
    return False
