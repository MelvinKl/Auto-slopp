# Changelog

All notable changes to Auto-slopp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **`auto_slopp.utils.linking`**: New module with `ensure_issue_link_in_pr_body()` function and `CLOSING_KEYWORDS` constant for reliable PR-to-issue linking
- **`tests/test_linking.py`**: Comprehensive test suite for the linking utilities (82 tests)
- **`auto_slopp.utils.linking`**: Supports `owner/repo#123` format (including nested paths like `org/subteam/repo#123`) in existing-link detection
- **TaskSource**: New `on_skip()` lifecycle callback for skipping issues that should be retried later (e.g., LLM unavailability). `GitHubTaskSource` implements it by posting a skip comment on the issue (the required label is intentionally kept so the issue stays eligible for retry), while `VikunjaTaskSource` commits a skip comment but intentionally leaves the task status unchanged (Vikunja statuses are per-project and user-defined, and `get_tasks` only fetches non-`done` tasks, so the unchanged status keeps the task eligible for retry).
- **`RalphExecutor.get_skip_reason()`**: New public accessor returning the last failure reason when it indicates LLM unavailability (`None` otherwise), so callers no longer need to reach into the executor's private error-tracking fields.
- **`is_any_cli_available` / cooldown helpers** in `auto_slopp.utils.cli_executor`: New `has_cli_configurations()` and `are_all_clis_in_cooldown()` to distinguish "no CLI configured" (misconfiguration) from "all configured CLIs are in cooldown" (transient outage). The LLM-unavailability classification and the IssueWorker skip/close routing now key off `are_all_clis_in_cooldown()`, so a deployment with zero configured CLIs is no longer treated as an outage (e.g. weak-pattern errors are no longer classified as LLM-unavailable and "no changes" tasks are closed instead of skipped forever)
- **`error_indicates_llm_unavailability()`**: New optional `cli_available: bool | None = None` parameter so the weak-pattern corroboration can use an explicit CLI-availability state instead of reading global state (defaults to the live check), keeping the core matching pure and easier to unit test
- **`GitHubTaskSource.on_skip` / `VikunjaTaskSource.on_skip`**: Now check whether the latest comment on the issue/task is already a skip comment and, if so, do not post another (and, for Vikunja, do not create another commit), preventing a prolonged outage from spamming the issue/task with identical skip comments on every retry cycle

### Changed
- **`AUTO_SLOPP_GITHUB_ISSUE_PR_REVIEW_MAX_ITERATIONS`**: Default changed from 5 to 3 for maximum PR review/fix iterations before giving up
- **IssueWorker/RalphExecutor**: Removed intermediate per-step acceptance checks; now only a single final acceptance check runs after all steps complete
- **RalphExecutor**: Removed `remaining_steps_update_name` constructor parameter and associated dead code (`_execute_step_acceptance_check`, `_update_remaining_steps`, `_build_acceptance_check_instructions`, `_build_remaining_steps_update_instructions`, `_extract_step_block`, `_find_step_description`)
- **Final acceptance check**: Now requires explicit `acceptance_status: pass` in output; empty/unknown output is treated as failure
- **Loop behavior**: `loops_executed` now consistently reports `iteration - 1` on both success and final-check failure paths; final check runs on max-iterations with partial work and its failure is recorded in `last_error` and in the executor's error state (`_last_error`/`_last_iteration_failure_reason`), so `get_skip_reason()` can surface an LLM outage during the final check instead of the issue being dropped via `on_max_iterations_reached`
- **`checkout_branch_resilient`**: Replaced `git reset --hard` fallback with `git stash`/`git stash pop` to preserve uncommitted local changes when branch checkout fails due to conflicting modifications

### Fixed
- **IssueWorker `max_loops_reached` handling (Ralph path)**: An LLM outage inside the Ralph step loop previously surfaced only as `max_loops_reached` after exhausting all iterations, which was handled by `on_max_iterations_reached` and permanently dropped the issue. The worker now consults `RalphExecutor.get_skip_reason()` in the `max_loops_reached` branch (which returns the executor's preserved mid-loop failure reason, demoting stale run-level errors) and calls `on_skip` (with the actual iteration failure reason) when the LLM was unavailable **during** the Ralph step loop, so the issue is preserved for retry. Genuine iteration exhaustion still goes through `on_max_iterations_reached`, and the two cases are logged distinctly ("LLM unavailable during Ralph loop" vs "Ralph loop reached max iterations").
- **`VikunjaTaskSource.on_skip`**: Posts a skip comment (and commits it) but intentionally leaves the task status unchanged. Vikunja statuses are per-project and user-defined, so a project may not have a status named "skipped" (making a status update fail on every skip), and `get_tasks` only fetches tasks that are not `done`, so an unchanged status keeps the task eligible for retry once the LLM is available again
- **IssueWorker skip detection**: The "no changes made" and "no commits ahead" skip paths key off the all-CLIs-in-cooldown state (`are_all_clis_in_cooldown()`) rather than the executor's preserved failure reason: a run that reaches those paths has succeeded, which clears the executor's error state, so `get_skip_reason()` can only ever return `None` there and would be dead code. A deployment with zero configured CLIs is treated as a misconfiguration (not an outage): such tasks are closed via `on_no_changes()` instead of being skipped forever
- **README**: Merged the duplicated `PR-to-Issue Linking` sections into a single section
- **`UNAVAILABILITY_PATTERNS`**: Removed the redundant `"503 service unavailable"` and `"502 bad gateway"` entries, already covered by the word-boundary status-code match and the standalone `"service unavailable"` pattern
- **Git checkout**: Uncommitted local changes are no longer silently discarded when switching branches. Changes are now stashed before checkout and restored afterward, preventing data loss from previous worker operations leaving temporary files in the working directory
- **PR-to-issue linking**: Pull requests now always contain a valid GitHub closing keyword (`Closes`, `Fixes`, or `Resolves`) linking to the source issue. The `ensure_issue_link_in_pr_body` helper function guarantees at least one closing keyword is present in the PR body, preventing issues from remaining open after PR creation.
- **`validate_issue_link`**: Now validates `issue_id` (raises `TypeError` for non-integers and `ValueError` for non-positive values), matching the documented contract and the behavior of `ensure_issue_link_in_pr_body`
- **Linking pattern**: Cross-repo references now require at least one slash (e.g. `owner/repo#123`). A single segment like `Closes docs#123` is not a valid GitHub issue reference and is no longer treated as an existing link, so a closing keyword is reliably prepended
- **IssueWorker class structure**: Moved orphaned class methods (`_generate_pr_body_from_task_file`, `_build_review_instructions`, `_review_pull_request`, `_build_pr_description_instructions`, `_create_error_result`, `_get_current_time`, `_get_elapsed_time`, `_log_completion_summary`) back inside the `IssueWorker` class where they were incorrectly defined outside the class.

### Removed
- Per-step acceptance criteria validation after each step
- Per-step remaining steps update after each step
- `remaining_steps_update_name` parameter from `RalphExecutor` constructor and `IssueWorker` call site
- **`AUTO_SLOPP_PR_REVIEW_WORKER_MIN_COMMENTS`** (breaking): the conservative review prompt no longer enforces a minimum comment count, so this setting was removed from `Settings`. Existing `.env` files containing `AUTO_SLOPP_PR_REVIEW_WORKER_MIN_COMMENTS` will have the value silently ignored (pydantic `extra="ignore"`); remove it from your `.env`. Users who previously relied on a minimum comment count should note that reviews may now contain fewer comments (or a single `praise:` line)
- **`AUTO_SLOPP_PR_REVIEW_WORKER_MAX_COMMENTS`**: the old per-worker review prompts interpolated this value into the instruction text ("Generate between {min} and {max} comments"), but the new shared conservative review prompt no longer enforces a comment count, so the setting had no effect and was removed from `Settings`, `README.md`, `.env.example`, and `docs/08-concepts.md`. Existing `.env` files containing it are silently ignored; remove it from your `.env`
- Duplicated conservative review prompt: the prompt previously copy-pasted in `PrReviewWorker._build_review_instructions` and `IssueWorker._build_review_instructions` now lives in a single shared helper, `build_conservative_review_instructions()` in `auto_slopp.utils.pr_review`

### Migration Notes
- **TaskSource.on_skip()**: New optional lifecycle callback for skipping tasks that should be retried later (e.g., LLM unavailability). The method has a default no-op implementation, so this is **NOT a breaking change** for custom `TaskSource` implementations. Sources that track skip state (GitHub, Vikunja) override this method to add a skip comment while leaving the task/issue in a state that remains eligible for future processing.
- **IssueWorker skipped-task results (behavioral change)**: Tasks skipped due to LLM unavailability report `success=True` alongside a new `skipped=True` flag and a `skip_reason` (the underlying failure is also carried in `result["error"]` when the skip came from a failed execution). `success=True` here means "handled without error" (the top-level `worker.run()` result likewise reports `success=True`), not "task completed". Downstream consumers that use `success` to decide whether a task was fully processed should also check the `skipped` flag (e.g. count a task as completed only when `result["success"] and not result.get("skipped")`).
- **LLM-unavailability detection (behavioral change)**: Bare HTTP status codes (`429`, `502`, `503`, `504`) are now matched with word boundaries instead of as plain substrings. This only excludes codes embedded in longer tokens (e.g. `5034`, `x503y`); a code appearing as a standalone number — including incidental numbers in an error message such as a file path (`/tmp/503/file`) or a line number (`line 503: ...`) — still matches and can still cause a false positive. Additionally, all-configured-CLIs-in-cooldown is now only a secondary confirmation and no longer independently classifies an error as "LLM unavailable"; the error message must also match an unavailability pattern.
- **Weak unavailability patterns (behavioral change)**: The broad patterns `"exhausted"`, `"no response"`, `"not responding"`, `"unreachable"`, and `"all cli"` moved from `UNAVAILABILITY_PATTERNS` to a new `WEAK_UNAVAILABILITY_PATTERNS` in `auto_slopp.constants`. A match on one of these alone no longer classifies an error as LLM unavailability; the match must be corroborated by an unavailability status code in the message or by all configured CLIs currently being in cooldown (`are_all_clis_in_cooldown()` returning `True`; a deployment with zero configured CLIs is a misconfiguration, not an outage), so genuine step/CLI-output failures containing these words are no longer skipped-and-retried indefinitely.
- **TaskSource.on_no_changes()**: Changed from abstract to non-abstract with a default no-op implementation. Custom `TaskSource` implementations no longer need to override this method unless they want custom behavior.
- **RalphExecutor._last_iteration_failure_reason**: Renamed from `_last_iteration_error` for clarity. The field captures the failure reason from the last loop iteration so `_is_llm_unavailable()` can inspect it.
- **UNAVAILABILITY_PATTERNS**: Extracted to shared constant in `auto_slopp.constants`. Both `IssueWorker` and `RalphExecutor` now use the same source of truth for LLM unavailability detection. The pattern set is the union of both previous sets.

### Documentation
- Updated README.md to reflect removal of intermediate checks and new final acceptance check behavior
- Updated README.md `LLM Unavailability Handling` section to document the `max_loops_reached` distinction between genuine iteration exhaustion (failed via `on_max_iterations_reached`) and mid-loop LLM unavailability (skipped via `on_skip` for retry)

## [0.1.0] - 2024-01-01

### Added
- Initial release of Auto-slopp automation framework
- Pluggable worker system with abstract base class
- Configuration management using Pydantic settings
- Flexible logging with optional Telegram integration
- Task execution with automated worker discovery
- Modern Python support (3.14+)
- Comprehensive test suite with pytest
- Example worker implementations
- Command-line interface with argument parsing
- Environment variable configuration support
- Error handling and graceful degradation
- Async Telegram logging with retry logic

### Features
- **Worker System**: Abstract base class for creating custom automation workers
- **Configuration**: Pydantic-based settings with environment variable support
- **Logging**: Built-in logging with optional Telegram integration
- **Discovery**: Automated discovery and execution of worker implementations
- **CLI**: Command-line interface with comprehensive options
- **Testing**: Full test suite with mocked dependencies

### Documentation
- Basic README with installation and usage instructions
- Telegram logging setup guide
- API documentation in docstrings
- Example configurations and use cases

---

## Version History

### Future Plans

#### [0.2.0] - Planned
- Enhanced worker discovery with caching
- Performance monitoring and metrics
- Additional example workers
- Plugin system for dynamic loading
- Configuration validation and schemas
- Enhanced error reporting
- Worker execution timeouts
- Parallel worker execution

#### [0.3.0] - Planned
- Workflow engine for complex task orchestration
- Web interface for monitoring and management
- Database integration for state management
- Advanced logging with structured output
- Worker dependency management
- Conditional worker execution
- Result aggregation and reporting
- Integration with external systems

#### [1.0.0] - Planned
- Production-ready stability
- Comprehensive test coverage (>95%)
- Performance optimizations
- Security hardening
- Complete documentation suite
- Community contribution guidelines
- Long-term support commitment

---

## Release Process

### Version Numbers
- **Major (X.0.0)**: Breaking changes, new architecture
- **Minor (X.Y.0)**: New features, backward compatible
- **Patch (X.Y.Z)**: Bug fixes, documentation updates

### Release Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version number updated
- [ ] Git tag created
- [ ] Release published
- [ ] Documentation deployed

### Release Types

#### Patch Release
- Bug fixes
- Documentation improvements
- Typos and formatting
- Dependency updates

#### Minor Release
- New features
- Performance improvements
- Enhanced functionality
- Backward-compatible changes

#### Major Release
- Breaking changes
- New architecture
- Significant redesign
- Incompatible changes

---

## Contributing to Changelog

When contributing to the project:

1. **Document your changes** - Add entries to the "Unreleased" section
2. **Use proper format** - Follow the established changelog format
3. **Categorize changes** - Use appropriate categories (Added, Changed, Deprecated, etc.)
4. **Be specific** - Provide clear, concise descriptions of changes
5. **Reference issues** - Link to related GitHub issues when applicable

### Categories

- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Features marked for future removal
- **Removed** - Features removed in this version
- **Fixed** - Bug fixes
- **Security** - Security-related changes
- **Documentation** - Documentation improvements

---

For more information about contributing, see the [Contributing Guide](docs/contributing.md).