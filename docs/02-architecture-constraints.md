# 2 Architecture Constraints

## 2.1 Technical Constraints

### Runtime Environment

| Constraint | Detail |
|-----------|--------|
| Python Version | 3.14 or higher |
| Package Manager | `uv` (astral-sh/uv) |
| Virtual Environment | `.venv/` managed by uv |
| Entry Point | `auto-slopp` CLI command (from `pyproject.toml`) |
| OS Support | Linux (primary), macOS (development) |
| Git Required | Yes — all repository operations use git CLI |

### External Dependencies

| Dependency | Purpose | Constraint |
|-----------|---------|------------|
| `gh` CLI | GitHub API access | Requires `GH_TOKEN` environment variable |
| Telegram Bot API | Real-time notifications | Requires bot token and chat ID |
| Vikunja API | Task management (optional) | Requires Vikunja instance URL and token |
| CLI tools (pi, opencode) | AI task execution | Configurable in `settings/main.py` as `CLIConfiguration` list |
| httpx | Async HTTP client | Used for Telegram API and retry logic |
| pydantic / pydantic-settings | Configuration validation | Type-safe settings with env var mapping |
| python-dotenv | .env file loading | Loads `.env` for default values |

### Security Constraints

- **GitHub Token Isolation**: `GH_TOKEN` must NOT be in `.env` file. Use separate `.gh.env` file outside project directory.
- **Telegram Token Security**: Bot tokens treated as secrets, stored only in environment variables
- **HTTPS Only**: All network communication uses HTTPS
- **No Hardcoded Secrets**: All sensitive configuration via environment variables
- **PATH Security**: Systemd `PATH` must include `.venv/bin` first to use project dependencies
- **Docker Volumes**: Repo mounts must be read-write for git operations

## 2.2 Organizational Constraints

### Development Workflow

- Conventional commit messages (`feat:`, `fix:`, `docs:`, etc.)
- Code quality enforced by CI: black, isort, flake8, safety, bandit
- Test suite must pass (`make test`) before changes are considered complete

### Deployment Constraints

- Systemd service for autostart (optional)
- Docker containerization supported via `Dockerfile`
- Configuration via environment variables only (no config files)

## 2.3 Conventions

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Module names | snake_case | `github_operations.py` |
| Class names | PascalCase | `GitHubIssueWorker` |
| Environment variables | `AUTO_SLOPP_<SECTION>_<NAME>` | `AUTO_SLOPP_DEBUG` |
| Worker files | `<name>_worker.py` | `pr_worker.py` |
| Branch names | `ai/issue-<number>-<description>` | `ai/issue-404-update-documentation` |

### Code Style

- **Formatter**: Black (120 character line length)
- **Import Sorter**: isort with `--profile black`
- **Linter**: flake8
- **Type Hints**: Required for all public APIs
- **Docstrings**: Google-style

### Commit Message Convention

```
<type>: <description>

Types: feat, fix, docs, style, refactor, test, chore
```

## 2.4 Architectural Decisions Reference

Key decisions that constrain the architecture:

1. **Pydantic for Configuration** — All settings use Pydantic `BaseSettings` with `AUTO_SLOPP_` prefix
2. **Abstract Worker Interface** — All workers must inherit from `Worker` base class with `run(repo_path)` method
3. **TaskSource Abstraction** — Task loading is abstracted behind `TaskSource` interface
4. **Ralph Loop** — Task execution follows a fixed 5-step pattern (Analyze, Implement, Test, Document, Validate)
5. **Tiered CLI Selection** — CLI tools defined in code with capability ratings (0-10), automatically selected based on task difficulty
