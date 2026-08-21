# Changelog

All notable changes to Auto-slopp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **`auto_slopp.utils.linking`**: New module with `ensure_issue_link_in_pr_body()` function and `CLOSING_KEYWORDS` constant for reliable PR-to-issue linking
- **`tests/test_linking.py`**: Comprehensive test suite for the linking utilities (82 tests)
- **`auto_slopp.utils.linking`**: Supports `owner/repo#123` format (including nested paths like `org/subteam/repo#123`) in existing-link detection
- **TaskSource**: New `on_skip()` lifecycle callback for skipping issues that should be retried later (e.g., LLM unavailability). `GitHubTaskSource` implements it by posting a skip comment on the issue (the required label is intentionally kept so the issue stays eligible for retry), while `VikunjaTaskSource` commits a skip comment and updates the task status to 'skipped'.
- **`RalphExecutor.get_skip_reason()`**: New public accessor returning the last failure reason when it indicates LLM unavailability (`None` otherwise), so callers no longer need to reach into the executor's private error-tracking fields.

### Changed
- **IssueWorker/RalphExecutor**: Removed intermediate per-step acceptance checks; now only a single final acceptance check runs after all steps complete
- **RalphExecutor**: Removed `remaining_steps_update_name` constructor parameter and associated dead code (`_execute_step_acceptance_check`, `_update_remaining_steps`, `_build_acceptance_check_instructions`, `_build_remaining_steps_update_instructions`, `_extract_step_block`, `_find_step_description`)
- **Final acceptance check**: Now requires explicit `acceptance_status: pass` in output; empty/unknown output is treated as failure
- **Loop behavior**: `loops_executed` now consistently reports `iteration - 1` on both success and final-check failure paths; final check runs on max-iterations with partial work and result recorded in `last_error`
- **`checkout_branch_resilient`**: Replaced `git reset --hard` fallback with `git stash`/`git stash pop` to preserve uncommitted local changes when branch checkout fails due to conflicting modifications

### Fixed
- **IssueWorker `max_loops_reached` handling (Ralph path)**: An LLM outage inside the Ralph step loop previously surfaced only as `max_loops_reached` after exhausting all iterations, which was handled by `on_max_iterations_reached` and permanently dropped the issue. The worker now checks `ralph_executor.get_skip_reason()` in the `max_loops_reached` branch and calls `on_skip` (with the actual iteration failure reason) when the LLM was unavailable during the loop, so the issue is preserved for retry. Genuine iteration exhaustion still goes through `on_max_iterations_reached`, and the two cases are logged distinctly.
- **`VikunjaTaskSource.on_skip`**: Now uses the shared `_update_task_with_comment_and_status` helper like the other lifecycle hooks, giving it the same error-handling behavior
- **IssueWorker skip detection**: The "no changes made" and "no commits ahead" skip paths now use `ralph_executor.get_skip_reason()` (the actual last failure reason) instead of a check on an empty error string that could never fire
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

### Migration Notes
- **TaskSource.on_skip()**: New optional lifecycle callback for skipping tasks that should be retried later (e.g., LLM unavailability). The method has a default no-op implementation, so this is **NOT a breaking change** for custom `TaskSource` implementations. Sources that track skip state (GitHub, Vikunja) override this method to add a skip comment (and, for Vikunja, update the task status).
- **IssueWorker skipped-task results (behavioral change)**: Tasks skipped due to LLM unavailability now report `success=False` (previously `True`) alongside a new `skipped=True` flag and a `skip_reason`. The top-level `worker.run()` result still reports `success=True`, but per-task results now disagree for skipped tasks. Downstream consumers that use `success` to decide whether a task was "processed" should instead check the `skipped` flag (e.g. count a task as processed when `result["skipped"] or result["success"]`).
- **LLM-unavailability detection (behavioral change)**: Bare HTTP status codes (`429`, `502`, `503`, `504`) are now matched with word boundaries instead of as plain substrings, so incidental numbers in an error message (file paths, line numbers, identifiers) no longer cause a false positive. Additionally, all-CLIs-inactive is now only a secondary confirmation and no longer independently classifies an error as "LLM unavailable"; the error message must also match an unavailability pattern.
- **TaskSource.on_no_changes()**: Changed from abstract to non-abstract with a default no-op implementation. Custom `TaskSource` implementations no longer need to override this method unless they want custom behavior.
- **RalphExecutor._last_iteration_failure_reason**: Renamed from `_last_iteration_error` for clarity. The field captures the failure reason from the last loop iteration so `_is_llm_unavailable()` can inspect it.
- **UNAVAILABILITY_PATTERNS**: Extracted to shared constant in `auto_slopp.constants`. Both `IssueWorker` and `RalphExecutor` now use the same source of truth for LLM unavailability detection. The pattern set is the union of both previous sets.

### Documentation
- Updated README.md to reflect removal of intermediate checks and new final acceptance check behavior
- Updated README.md `LLM Unavailability Handling` section to document the `max_loops_reached` distinction between genuine iteration exhaustion (failed via `on_max_iterations_reached`) and mid-loop LLM unavailability (skipped via `on_skip` for retry)

### Fixed
- **PR-to-issue linking**: Pull requests now always contain a valid GitHub closing keyword (`Closes`, `Fixes`, or `Resolves`) linking to the source issue. The `ensure_issue_link_in_pr_body` helper function guarantees at least one closing keyword is present in the PR body, preventing issues from remaining open after PR creation.
- **`validate_issue_link`**: Now validates `issue_id` (raises `TypeError` for non-integers and `ValueError` for non-positive values), matching the documented contract and the behavior of `ensure_issue_link_in_pr_body`
- **Linking pattern**: Cross-repo references now require at least one slash (e.g. `owner/repo#123`). A single segment like `Closes docs#123` is not a valid GitHub issue reference and is no longer treated as an existing link, so a closing keyword is reliably prepended
- **IssueWorker class structure**: Moved orphaned class methods (`_generate_pr_body_from_task_file`, `_build_review_instructions`, `_review_pull_request`, `_build_pr_description_instructions`, `_create_error_result`, `_get_current_time`, `_get_elapsed_time`, `_log_completion_summary`) back inside the `IssueWorker` class where they were incorrectly defined outside the class.

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