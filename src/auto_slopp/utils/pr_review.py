"""Shared helpers for PR review prompts."""


def build_conservative_review_instructions(title: str, body: str, diff: str) -> str:
    """Build the conservative code review prompt shared by all PR review call sites.

    Keeping this prompt in one place prevents the instructions used by
    ``PrReviewWorker`` and ``IssueWorker`` from drifting apart.

    Args:
        title: PR title
        body: PR body description
        diff: PR diff content

    Returns:
        Instructions string for the CLI tool.
    """
    body_section = f"\n{body}" if body else ""

    return (
        f"You are a conservative code review assistant. Review the following pull request:\n"
        f"Title: {title}\n"
        f"Description:{body_section}\n\n"
        f"Diff:\n{diff}\n\n"
        f"Only report concrete, verified problems: code that is broken, causes a real bug, "
        f"or breaks the project's tests or lint. Do NOT report style preferences, "
        f"hypothetical improvements, or speculative issues. Prefer fewer, high-confidence "
        f"comments over many. If the code is fine, output a single 'praise:' line and stop. "
        f"Do not invent problems to reach a comment count. "
        f"Each comment should be on a new line and start with one of the following:\n"
        f"- 'issue:' for a concrete, verified problem that must be fixed (bug, correctness, security)\n"
        f"- 'suggestion:' for a meaningful improvement that is not required\n"
        f"- 'nit:' for minor style points\n"
        f"- 'chore:' for maintenance suggestions\n"
        f"- 'question:' for asking clarifying questions\n"
        f"- 'praise:' for positive feedback when there is nothing wrong\n"
        f"Only output the comments, one per line, without any additional text or explanation."
    )
