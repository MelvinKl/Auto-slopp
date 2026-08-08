# 9 Design Decisions

## AD-01: Pluggable Worker Architecture

**Status**: Accepted
**Context**: The system needs to support multiple types of automation tasks (GitHub issues, PRs, branch cleanup, Vikunja tasks).
**Decision**: Use an abstract `Worker` base class with dynamic discovery from the `workers/` package.
**Consequences**:
- (+) New workers can be added without modifying core code
- (+) Workers are independently testable
- (+) Workers can fail independently without stopping the system
- (-) All workers share the same interface, limiting specialization

## AD-02: TaskSource Abstraction

**Status**: Accepted
**Context**: Tasks come from different sources (GitHub issues, Vikunja tasks) but need the same processing logic.
**Decision**: Abstract task loading behind the `TaskSource` interface. `IssueWorker` works with any `TaskSource` implementation.
**Consequences**:
- (+) Single `IssueWorker` handles all task sources
- (+) Easy to add new sources (e.g., Jira, GitLab)
- (-) Each source must implement many interface methods

## AD-03: Ralph Loop for Task Execution

**Status**: Accepted
**Context**: Tasks need structured execution with verification at each step.
**Decision**: Fixed 5-step loop (Analyze → Implement → Test → Document → Validate) with markdown plan files.
**Consequences**:
- (+) Predictable, repeatable execution
- (+) Clear checkpoints for verification
- (+) Human-readable plan files in `.ralph/`
- (-) Inflexible for tasks that don't fit the 5-step pattern

## AD-04: Tiered CLI Tool Configuration

**Status**: Accepted
**Context**: Different tasks have different complexity; a single CLI tool is insufficient.
**Decision**: Define multiple CLI tool configurations as a Pydantic `List[CLIConfiguration]` with capability ratings (0-10), automatic selection based on task difficulty.
**Consequences**:
- (+) Optimal tool selection for task complexity
- (+) Fallback to simpler tools for easy tasks
- (+) Type-safe configuration with validation
- (+) Sensible defaults baked into code
- (-) Adding new tools requires code changes (not just env vars)
- (-) Tool health must be monitored and managed

## AD-05: Pydantic Settings

**Status**: Accepted
**Context**: Configuration needs type safety, validation, and environment variable support.
**Decision**: Use Pydantic `BaseSettings` with `AUTO_SLOPP_` prefix for all settings.
**Consequences**:
- (+) Type-safe configuration
- (+) Automatic validation and defaults
- (+) Environment variable mapping is automatic
- (-) All settings must follow naming convention

## AD-06: Async Telegram Logging

**Status**: Accepted
**Context**: Telegram notifications must not block the main execution loop.
**Decision**: Use async httpx client with retry logic and exponential backoff.
**Consequences**:
- (+) Non-blocking log processing
- (+) Resilient to network failures
- (-) More complex error handling
- (-) Requires async runtime management

## AD-07: GitHub Token Isolation

**Status**: Accepted
**Context**: CLI tools spawned by auto-slopp must NOT have access to the GitHub token.
**Decision**: `GH_TOKEN` must be in a separate `.gh.env` file outside the project directory, never in `.env`.
**Consequences**:
- (+) CLI tools cannot access GitHub API
- (+) Security boundary between auto-slopp and external tools
- (-) Users must manage a separate token file

## AD-08: Branch-per-Task Isolation

**Status**: Accepted
**Context**: Each task should not interfere with other tasks or the main branch.
**Decision**: Create a dedicated git branch for each task, process on that branch, create PR.
**Consequences**:
- (+) Tasks are isolated from each other
- (+) Main branch stays clean
- (+) PRs provide review capability
- (-) More git operations per task
- (-) Branch cleanup required

## AD-09: Comment Condensation for GitHub Issues

**Status**: Accepted
**Context**: GitHub issues accumulate many comments that clutter the context for AI processing.
**Decision**: Condense comments from issue author and whitelisted user into a single summary, delete originals.
**Consequences**:
- (+) Cleaner issue context for AI tools
- (+) Reduced API calls (fewer comments to process)
- (-) Original comments are deleted (irreversible)

## AD-10: Hardcoded Worker List

**Status**: Accepted
**Context**: Workers need to be discoverable and configurable without dynamic file scanning.
**Decision**: Use a hardcoded `ALL_WORKERS` list in `executor.py` with filtering via `AUTO_SLOPP_WORKERS_DISABLED`.
**Consequences**:
- (+) Type-safe worker list
- (+) Explicit dependency between workers
- (+) Easy to disable specific workers via env var
- (-) Adding new workers requires code changes (import + list)
- (-) No auto-discovery from arbitrary paths

## AD-11: Branch-per-Task Isolation with Auto-Cleanup

**Status**: Accepted
**Context**: Multiple tasks processing the same repository must not interfere with each other.
**Decision**: Each task creates a dedicated git branch, processes on that branch, and creates a PR. The `StaleBranchCleanupWorker` handles cleanup of orphaned branches.
**Consequences**:
- (+) Tasks are fully isolated
- (+) Main branch stays clean
- (+) PRs provide natural review points
- (+) Automatic cleanup of orphaned branches
- (-) More git operations per task
- (-) Requires branch naming convention (`ai/issue-<number>-<title>`)

## AD-12: Resilient Git Operations

**Status**: Accepted
**Context**: Git operations can fail due to network issues, conflicts, or repository state problems.
**Decision**: Use resilient checkout with retry (reset + clean) and CLI fallback for complex failures.
**Consequences**:
- (+) Graceful handling of checkout failures
- (+] CLI tools can resolve complex merge conflicts
- (-) Added complexity in error handling
- (-] CLI fallback adds execution time

## AD-13: Task File Format in .ralph/

**Status**: Accepted
**Context**: Task plans need to be human-readable, machine-parsable, and survive restarts.
**Decision**: Use markdown files with checkbox syntax in `.ralph/` directories (gitignored).
**Consequences**:
- (+) Human-readable plan files
- (+) Checkboxes naturally track progress
- (+) Survives restarts (state in files)
- (+) `.ralph/` is gitignored (no clutter)
- (-) Requires markdown parsing logic
- (-) File format must be maintained across versions

## AD-14: No Dynamic Worker Discovery

**Status**: Accepted
**Context**: Dynamic discovery could load arbitrary code from unexpected paths.
**Decision**: Workers are explicitly imported in `workers/__init__.py` and listed in `ALL_WORKERS`.
**Consequences**:
- (+) Security: only known workers can run
- (+) Type safety via explicit imports
- (+) Easy to audit which workers exist
- (-) More boilerplate for new workers
- (-] Cannot add workers without code changes

## AD-15: GitHub Token Isolation via Additional Env File

**Status**: Accepted
**Context**: CLI tools spawned by auto-slopp should NOT have access to GitHub credentials.
**Decision**: `GH_TOKEN` goes in a separate `.gh.env` file outside the project, loaded only via `AUTO_SLOPP_ADDITIONAL_ENV_FILE` for GitHub API calls.
**Consequences**:
- (+) Security boundary between auto-slopp and CLI tools
- (+) CLI tools cannot access GitHub API
- (-) Users must manage a separate token file
- (-) Extra configuration step required
