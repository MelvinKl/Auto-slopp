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
