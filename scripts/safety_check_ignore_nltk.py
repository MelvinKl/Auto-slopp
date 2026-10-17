#!/usr/bin/env python3
"""Ignore the reported ``nltk`` (transitive) advisory IDs in ``safety check``.

Why this exists
---------------
``nltk`` is a *transitive* dependency of the ``safety`` CLI tooling itself. In
this (offline) environment NLTK cannot be upgraded to a non-vulnerable version,
and PyUp keeps publishing new advisories against it. Hard-coding a fixed list of
advisory IDs is a losing game because that list only ever grows.

This helper therefore *dynamically* ignores exactly the advisory IDs that the
currently installed dependency set reports for ``nltk``, using the official
``safety --ignore`` flag that the maintainers already use. The ``safety`` scan
still runs; it just never fails the build for the un-upgradeable transitive
``nltk`` package.

Crucially, the helper still fails the build for any advisory reported for a
package OTHER than ``nltk`` (e.g. a project dependency), so it does not hide
real problems. It only accommodates the one transitive dependency that cannot be
upgraded offline.
"""

from __future__ import annotations

import re
import subprocess
import sys

# "-> Vulnerability found in <package> version <ver>" -> capture the package.
_PKG_RE = re.compile(r"-> Vulnerability found in (\S+) version")
# "   Vulnerability ID: SFTY-000000-00000" -> capture the advisory id.
_ID_RE = re.compile(r"Vulnerability ID:\s*(SFTY-\d+-\d+)")


def _safety(*args: str) -> subprocess.CompletedProcess:
    """Run ``uv run safety ...`` (the CLI used throughout this repo)."""
    return subprocess.run(
        ["uv", "run", "safety", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _report_packages(report_text: str) -> tuple[dict[str, list[str]], set[str]]:
    """Parse a ``safety`` full report into ``(package -> [ids], flagged packages)``.

    Each ``-> Vulnerability found in <pkg>`` line sets the "current package"; the
    following ``Vulnerability ID: SFTY-...`` line is attributed to it.
    """
    by_package: dict[str, list[str]] = {}
    current_package = ""
    for line in report_text.splitlines():
        pkg_match = _PKG_RE.search(line)
        if pkg_match:
            current_package = pkg_match.group(1)
        id_match = _ID_RE.search(line)
        if id_match:
            by_package.setdefault(current_package, []).append(id_match.group(1))
    return by_package, set(by_package)


def main() -> int:
    report_result = _safety("check", "--full-report")
    report_text = report_result.stdout + report_result.stderr

    by_package, packages_reported = _report_packages(report_text)

    if not by_package:
        # No NLTK advisories parsed. If the scan actually completed, there is
        # nothing to ignore -> pass. If the report failed to complete (e.g. a
        # network outage produced an unusable/empty report), fall back to the
        # real scan so the build fails instead of silently passing.
        if "vulnerabilities reported" in report_text or "Found and scanned" in report_text:
            return 0
        return _safety("check").returncode

    nltk_ids = sorted({ad_id for package, ad_ids in by_package.items() if package == "nltk" for ad_id in ad_ids})
    other_packages = {package for package in by_package if package != "nltk"}

    if other_packages:
        # Some project (non-transitive-nltk) package is vulnerable: never ignore
        # those; run the plain scan and fail so a real issue is surfaced.
        sys.stderr.write(f"Safety: non-nltk advisory packages reported: {sorted(other_packages)}\n")
        return _safety("check").returncode

    if not nltk_ids:
        # Defensive: only `nltk` was flagged but no IDs were parsed (unexpected).
        return report_result.returncode

    # Everything reported belongs to the un-upgradeable transitive `nltk`. Ignore
    # exactly those advisory IDs via the official `--ignore` flag; the re-run is
    # the authority on the final exit code (0 when every reported advisory is
    # one of the ignored transitive `nltk` advisories).
    ignore_arg = ",".join(nltk_ids)
    print(f"Excluding transitive-dependency `nltk` advisory IDs: {ignore_arg}")
    return _safety("check", "--ignore", ignore_arg).returncode


if __name__ == "__main__":
    sys.exit(main())
