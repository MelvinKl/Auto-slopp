# 4 Solution Strategy

## 4.1 Technical Decisions

### Pluggable Worker Architecture

**Decision**: Use an abstract base class (`Worker`) with dynamic discovery.

**Rationale**: Allows adding new automation tasks without modifying core code. Workers are discovered from the `workers/` package at runtime.

**Alternatives Considered**:
- Static worker registration — Rejected: requires code changes for new workers
- Configuration-driven workers — Rejected: less type-safe, harder to test

### TaskSource Abstraction

**Decision**: Separate task loading logic from task processing logic via `TaskSource` interface.

**Rationale**: The `IssueWorker` can process tasks from any source (GitHub, Vikunja, future sources) without modification. Each source only needs to implement the `TaskSource` interface.

**Alternatives Considered**:
- Source-specific workers — Rejected: code duplication between GitHub and Vikunja processing
- Monolithic task processor — Rejected: tightly coupled to specific sources

### Ralph Loop Execution

**Decision**: Process each task through a fixed 5-step loop (Analyze → Implement → Test → Document → Validate).

**Rationale**: Provides structured, repeatable task processing with clear checkpoints. Each step can be verified independently.

**Alternatives Considered**:
- Single-pass execution — Rejected: no verification step
- Fully open-ended execution — Rejected: no quality gates

### Tiered CLI Tool Selection

**Decision**: Configure multiple CLI tools with capability ratings (0-10) and automatically select based on task difficulty.

**Rationale**: Matches task complexity with appropriate tool sophistication. Simpler tasks use faster/cheaper tools; complex tasks use more capable ones.

**Alternatives Considered**:
- Single CLI tool — Rejected: not flexible enough for varying task complexity
- Manual tool selection — Rejected: requires human intervention

## 4.2 Key Technical Decisions

### Pydantic Settings

All configuration uses Pydantic `BaseSettings` with `AUTO_SLOPP_` environment variable prefix. This provides:
- Type-safe configuration
- Automatic validation
- Environment variable mapping
- `.env` file support

### Async Logging

Telegram notifications use async HTTP (httpx) with retry logic and exponential backoff. This ensures:
- Non-blocking log processing
- Resilience to network failures
- Rate limit compliance

### Rotating File Logging

Logs at WARNING level and above are written to a rotating file (`RotatingFileHandler`):
- 10 MB per file
- 5 backup files
- Automatic rotation

### Branch-per-Task Workflow

Each task creates a dedicated git branch:
1. Create branch from current state
2. Process task on branch
3. Create PR if changes exist
4. Clean up branch after merge

## 4.3 Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.14+ |
| Package Manager | uv |
| Configuration | Pydantic BaseSettings |
| HTTP Client | httpx (async) |
| Logging | Python logging + Telegram handler |
| Testing | pytest |
| Code Quality | black, isort, flake8, safety, bandit |
| CI/CD | GitHub Actions |
| Deployment | Docker, systemd |
