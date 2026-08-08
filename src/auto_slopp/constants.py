"""Shared constants for auto_slopp."""

# Lowercase substrings that indicate the LLM/CLI tool is unavailable.
# Used by :class:`IssueWorker` and :class:`RalphExecutor` to distinguish
# temporary outages (which should trigger a skip for retry) from genuine
# iteration exhaustion (which should drop the task).
UNAVAILABILITY_PATTERNS: tuple[str, ...] = (
    "llm unavailable",
    "llm is unavailable",
    "llm is down",
    "service unavailable",
    "api unavailable",
    "api is down",
    "rate limit",
    "too many requests",
    "429",
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
    "503 service unavailable",
    "503",
    "502 bad gateway",
    "502",
    "504",
    "gateway timeout",
    "internal server error",
)
