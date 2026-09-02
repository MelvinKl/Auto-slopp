# Changelog

All notable changes to Auto-slopp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **`auto_slopp.utils.linking`**: New module with `ensure_issue_link_in_pr_body()` function and `CLOSING_KEYWORDS` constant for reliable PR-to-issue linking
- **`tests/test_linking.py`**: Comprehensive test suite for the linking utilities (82 tests)
- **`auto_slopp.utils.linking`**: Supports `owner/repo#123` format (including nested paths like `org/subteam/repo#123`) in existing-link detection
- **`auto_slopp.utils.github_operations.get_failed_workflow_logs()`**: Fetches the failed logs of a single completed, non-successful workflow run
### Changed
- **GitHubTaskSource**: Error details are no longer posted as comments on GitHub issues. The skip comment (`on_skip`) is now generic (the raw skip reason is an error message and is only logged locally), and the max-iterations failure comment (`on_max_iterations_reached`) no longer includes the last error. Both comments previously embedded raw error text in the issue.
- **PRWorker**: Branches with non-successful GitHub Actions runs are no longer skipped; the failure logs are fetched and passed to the CLI tool (`_fix_workflows_with_cli`) to fix them before continuing
- **PRWorker._get_and_log_workflow_runs**: Now returns a tuple of (failed runs, failure logs) instead of only the failed runs
- **`AUTO_SLOPP_GITHUB_ISSUE_PR_REVIEW_MAX_ITERATIONS`**: Default changed from 5 to 3 for maximum PR review/fix iterations before giving up
- **IssueWorker/RalphExecutor**: Removed intermediate per-step acceptance checks; now only a single final acceptance check runs after all steps complete
- **RalphExecutor**: Removed `remaining_steps_update_name` constructor parameter and associated dead code (`_execute_step_acceptance_check`, `_update_remaining_steps`, `_build_acceptance_check_instructions`, `_build_remaining_steps_update_instructions`, `_extract_step_block`, `_find_step_description`)
- **Final acceptance check**: Now requires explicit `acceptance_status: pass` in output; empty/unknown output is treated as failure
- **Loop behavior**: `loops_executed` now consistently reports `iteration - 1` on both success and final-check failure paths; final check runs on max-iterations with partial work and result recorded in `last_error`
- **`checkout_branch_resilient`**: Replaced `git reset --hard` fallback with `git stash`/`git stash pop` to preserve uncommitted local changes when branch checkout fails due to conflicting modifications

### Fixed
- **Git checkout**: Uncommitted local changes are no longer silently discarded when switching branches. Changes are now stashed before checkout and restored afterward, preventing data loss from previous worker operations leaving temporary files in the working directory

### Removed
- Per-step acceptance criteria validation after each step
- Per-step remaining steps update after each step
- `remaining_steps_update_name` parameter from `RalphExecutor` constructor and `IssueWorker` call site
- **`AUTO_SLOPP_PR_REVIEW_WORKER_MIN_COMMENTS`** (breaking): the conservative review prompt no longer enforces a minimum comment count, so this setting was removed from `Settings`. Existing `.env` files containing `AUTO_SLOPP_PR_REVIEW_WORKER_MIN_COMMENTS` will have the value silently ignored (pydantic `extra="ignore"`); remove it from your `.env`. Users who previously relied on a minimum comment count should note that reviews may now contain fewer comments (or a single `praise:` line)
- **`AUTO_SLOPP_PR_REVIEW_WORKER_MAX_COMMENTS`**: the old per-worker review prompts interpolated this value into the instruction text ("Generate between {min} and {max} comments"), but the new shared conservative review prompt no longer enforces a comment count, so the setting had no effect and was removed from `Settings`, `README.md`, `.env.example`, and `docs/08-concepts.md`. Existing `.env` files containing it are silently ignored; remove it from your `.env`
- Duplicated conservative review prompt: the prompt previously copy-pasted in `PrReviewWorker._build_review_instructions` and `IssueWorker._build_review_instructions` now lives in a single shared helper, `build_conservative_review_instructions()` in `auto_slopp.utils.pr_review`

### Documentation
- Updated README.md to reflect removal of intermediate checks and new final acceptance check behavior

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