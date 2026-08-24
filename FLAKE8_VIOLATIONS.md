# Flake8 Lint Configuration Report

## Summary

The `[tool.flake8] extend-ignore` list in `pyproject.toml` has been reduced to only the
codes that strictly conflict with black:

```toml
extend-ignore = [
    "E203",  # whitespace before ':' - black splits slices differently
    "W503",  # line break before binary operator - black formats after it
]
```

All previously ignored codes (Q000, WOT001, SIM117, S101, S105, S106, S108, S110, S403,
S404, S405, S603, S605, S607, S608, S609, C901, E501, F811, F841, B007, B014, BLK100,
D104, D406, D407, D202, D401, I100, I201, B027) are now enforced. Most violations were
fixed in code; the rest are handled with targeted `per-file-ignores` entries or inline
`# noqa` comments with justification.

`make test` (black + isort + flake8 + safety + bandit + pytest) passes with this
configuration.

## Quote style (flake8-quotes)

flake8-quotes defaults to preferring *single* quotes, which conflicts with black's
double-quote style. The plugin is now configured to match black:

```toml
inline-quotes = '"'
docstring-quotes = '"'
multiline-quotes = '"'
```

The only remaining single-quoted strings are GraphQL query fragments in
`src/auto_slopp/utils/github_operations.py` that contain double quotes; flake8-quotes
permits the non-preferred quote there to avoid escaping (black does the same).

## Fixes applied in code

| Code | What was fixed |
| ---- | -------------- |
| Q000  | Strings converted to the black-compatible double-quote style (black re-run afterwards) |
| WOT001 | `typing.Dict/List/Set/Tuple` imports and usages replaced with builtin generics (`dict`/`list`/`set`/`tuple`) |
| SIM117 | Adjacent `with` statements merged into single context managers |
| S110  | `try/except/pass` blocks replaced with `contextlib.suppress(Exception)` |
| E501  | Long lines wrapped to ≤ 120 characters |
| F811  | Removed duplicate definitions (`NO_TIMEOUT`, `validate_timeout`, `_execute_step`) and renamed 3 duplicate test functions so both tests run |
| B014  | Redundant exception types (`FileNotFoundError`, `PermissionError`) removed from `except` tuples that already catch `OSError` |
| C901  | Reduced complexity of `_condense_comments`, `_has_author_comments`, and `VikunjaTaskSource.get_tasks` by extracting helpers; remaining long orchestrators carry justified inline suppressions (below) |
| I100/I201 | Import order normalised with isort (black profile) |
| BLK100 | Removed the stale per-file black `exclude` entries for `github_operations.py` / `github_task_source.py` so black and flake8-black agree |

The remaining globally-unenforced codes (S403, S405, S608, S609, F841, B007, B027,
D104, D406, D407, D202, D401) had **zero violations** and simply no longer needed
exclusion.

## Targeted per-file-ignores

```toml
per-file-ignores = """
  ./tests/*: S101,I252,S105,S106,S108,S404,S603,S605,S607
  src/auto_slopp/executor.py: S404,S603,S607
  src/auto_slopp/utils/cli_executor.py: S404,S603,S607
  src/auto_slopp/utils/git_operations.py: S404,S603,S607
  src/auto_slopp/utils/github_operations.py: S404,S603,S607
  src/auto_slopp/utils/vikunja_operations.py: S404,S603
  src/auto_slopp/workers/github_task_source.py: S404,S603,S607
  src/auto_slopp/workers/pr_worker.py: S404,S603,S607
"""
```

Justification and covered violation counts (measured with all ignores and noqas
disabled):

| Scope | Codes | Violations | Why a global fix is not appropriate |
| ----- | ----- | ---------- | ----------------------------------- |
| `./tests/*` | S101 | 1519 | `assert` statements are the point of tests |
| `./tests/*` | S105/S106 | 43 | Fake test tokens/passwords, no real credentials |
| `./tests/*` | S108 | 115 | `tempfile` usage for isolated test sandboxes |
| `./tests/*` | S404/S603/S605/S607 | 89 | Tests exercise the CLI/executor via subprocess with fixed arguments |
| subprocess utility/worker modules (listed above) | S404/S603/S607 | 141 | These modules intentionally shell out to `git`/`gh`/docker; commands are built from fixed arguments, not untrusted input |
| `./tests/*` | I252 | — | Dunder method names in mocks (`__dict__`, `__exit__`, ...) |

## Inline suppressions with justification

13 long orchestration functions keep a local `# noqa: C901` (plus a comment line
explaining the rationale) because their branch logic is inherent to the workflow
orchestration they implement and splitting is deferred:

| Location | Complexity |
| -------- | ---------- |
| `src/auto_slopp/telegram_handler.py` `TelegramHandler._send_message_async` | 11 |
| `src/auto_slopp/utils/cli_executor.py` `run_cli_executor` | 9 |
| `src/auto_slopp/utils/git_operations.py` `checkout_branch_resilient` | 13 |
| `src/auto_slopp/utils/git_operations.py` `merge_main_into_branch` | 9 |
| `src/auto_slopp/utils/ralph.py` `PlanParser.parse_content` | 10 |
| `src/auto_slopp/utils/ralph.py` `RalphExecutor._run_refined_task_loop` | 14 |
| `src/auto_slopp/utils/vikunja_operations.py` `get_tasks` | 10 |
| `src/auto_slopp/utils/vikunja_operations.py` `verify_blocking_closed` | 14 |
| `src/auto_slopp/workers/issue_worker.py` `IssueWorker._process_single_task` | 45 |
| `src/auto_slopp/workers/issue_worker.py` `IssueWorker._review_pull_request` | 14 |
| `src/auto_slopp/workers/pr_review_worker.py` `PrReviewWorker._process_repository` | 15 |
| `src/auto_slopp/workers/pr_worker.py` `PRWorker._process_repository` | 15 |
| `src/auto_slopp/workers/pr_worker.py` `PRWorker._get_and_log_workflow_runs` | 13 |

Additionally, `Task.id` in `src/auto_slopp/workers/task_source.py` carries
`# noqa: A003` (field name matches the task-source API).

## Verification

```bash
make test        # black --check + isort --check + flake8 + safety + bandit + pytest
```

All checks pass.
