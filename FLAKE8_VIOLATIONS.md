# Flake8 Lint Violations Report

## Summary

Total violations found: 3,742 (currently ignored via extend-ignore in pyproject.toml)

## Breakdown by Error Code

### Code Quality Issues

**F401 (28 violations)** - Imported but unused
- Unused imports throughout the codebase

**F811 (3 violations)** - Redefinition of unused name
- Redefinition of unused variables

**F841 (7 violations)** - Local variable assigned but never used
- Unused local variables

**C901 (9 violations)** - Functions too complex
- Functions exceeding complexity threshold

**E501 (5 violations)** - Lines too long
- Lines exceeding 120 characters

### Style Issues

**Q000 (3,498 violations)** - Double quotes found but single quotes preferred
- Most common violation - codebase uses double quotes extensively

**SIM105 (5 violations)** - Use 'contextlib.suppress(Exception)'
- Can simplify exception handling

**SIM117 (22 violations)** - Use context manager instead of multiple with statements
- Code can be simplified using context managers

**WOT001 (4 violations)** - Don't import type Dict
- Unnecessary type imports

### Security Issues

**S105 (40 violations)** - Possible hardcoded password
- Test tokens in test files

**S106 (1 violation)** - Possible hardcoded password
- 'direct_token' found

**S108 (22 violations)** - Probable insecure usage of temp file/directory
- Temporary file usage concerns

**S110 (4 violations)** - Try, Except, Pass detected
- Silent exception handling

**S404 (9 violations)** - Consider possible security implications with subprocess module

**S603 (17 violations)** - Subprocess call - check for execution of untrusted input

**S605 (7 violations)** - Starting a process with a shell

**S607 (23 violations)** - Starting a process with a partial executable path

## Priority Recommendations

1. **High Priority (Unused code):** Remove F401 (unused imports), F811 (redefinitions), F841 (unused variables)
2. **Medium Priority (Code quality):** Address C901 (complexity), E501 (line length), SIM105/SIM117 (code simplification)
3. **Low Priority (Style):** Q000 (quotes) - extensive refactoring needed, may consider removing from ignore list gradually
4. **Security Review:** S105/S106/S108/S404/S603/S605/S607 - review if these are false positives or genuine concerns

## Detailed Violation List by Category

### F401 - Unused Imports (28 violations)

**Source files:**
- `src/auto_slopp/executor.py:7` - `typing.Any`
- `src/auto_slopp/telegram_handler.py:5` - `time`
- `src/auto_slopp/utils/branch_analysis.py:11` - `auto_slopp.utils.git_operations.get_current_branch`
- `src/auto_slopp/utils/cli_executor.py:10` - `concurrent.futures.ThreadPoolExecutor`
- `src/auto_slopp/utils/git_operations.py:16` - `settings.main.settings`
- `src/auto_slopp/workers/pr_worker.py:19` - `auto_slopp.utils.repository_utils.discover_repositories`
- `src/auto_slopp/workers/stale_branch_cleanup_worker.py:18` - `auto_slopp.utils.repository_utils.discover_repositories`
- `src/settings/main.py:4` - `typing.Literal`
- `src/settings/main.py:7` - `pydantic.model_validator`

**Test files:**
- `tests/test_auto_update.py` - `subprocess`, `time`, `pathlib.Path`, `unittest.mock.call`, `pytest`
- `tests/test_cli_executor.py:5` - `unittest.mock.MagicMock`
- `tests/test_file_operations.py:7` - `pytest`
- `tests/test_git_operations.py` - `tempfile`, `pytest`, multiple git_operations imports
- `tests/test_github_issue_worker.py:7` - `pytest`
- `tests/test_main.py:8` - `pytest`
- `tests/test_pr_worker.py:4` - `unittest.mock.MagicMock`
- `tests/test_settings.py` - `settings.main.settings`, `tempfile`
- `tests/test_telegram_handler.py:11` - `settings.main.settings`

### F811 - Redefinition of Unused Name (3 violations)
- `tests/test_auto_update.py:187:40` - redefinition of 'call' from line 6
- `tests/test_auto_update.py:39:59` - redefinition of 'call' from line 6
- `tests/test_settings.py:110:9` - redefinition of 'settings' from line 11

### F841 - Unused Local Variables (7 violations)
- `src/auto_slopp/telegram_handler.py:136:17` - variable 'e'
- `src/auto_slopp/telegram_handler.py:87:9` - variable 'e'
- `tests/test_auto_update.py:117:13` - variable 'executor'
- `tests/test_github_issue_worker.py:437:21` - variable 'expected_branch'
- `tests/test_main.py:191:63` - variable 'mock_exit'
- `tests/test_stale_branch_cleanup_worker.py:117:13` - variable 'temp_repo_path'
- `tests/test_telegram_handler.py:114:17` - variable 'loop'

## Next Steps

Step 1: ✅ Complete - Identified all violations
Step 2: ✅ Complete - All unused variables identified and documented (see UNUSED_VARIABLES.md)
Step 3: Identify unused functions
Step 4: Remove unused variables
Step 5: Remove unused functions
Step 6: Review and resolve ignored warnings
Step 7: Review and remove unused imports (F401 violations)
Step 8: Verify improvements with flake8
Step 9: Run make test to confirm success
