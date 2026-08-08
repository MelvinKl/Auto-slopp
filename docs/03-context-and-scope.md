# 3 Context and Scope

## 3.1 System Context

Auto-slopp operates within a broader ecosystem of tools and services:

```
┌─────────────────────────────────────────────────────────────────────┐
│                           External World                             │
│                                                                     │
│  ┌──────────┐    ┌──────────────┐    ┌──────────┐    ┌──────────┐  │
│  │ GitHub   │    │   Telegram   │    │ Vikunja  │    │ CLI Tools│  │
│  │ (Issues) │    │   (Logging)  │    │  (Tasks) │    │ (opencode│  │
│  │          │    │              │    │          │    │  gemini  │  │
│  │          │    │              │    │          │    │  codex)  │  │
│  └────┬─────┘    └──────┬───────┘    └────┬─────┘    └────┬─────┘  │
│       │                 │                  │               │        │
│       ▼                 ▼                  ▼               ▼        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     Auto-slopp                               │   │
│  │  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────────┐  │   │
│  │  │  CLI    │  │ Executor │  │ Workers │  │ Task Sources │  │   │
│  │  │  Main   │  │          │  │         │  │              │  │   │
│  │  └────┬────┘  └────┬─────┘  └────┬────┘  └──────┬───────┘  │   │
│  │       │             │              │              │          │   │
│  │       ▼             ▼              ▼              ▼          │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │              Managed Repositories                     │   │   │
│  │  │  repo_a/  repo_b/  repo_c/  ...                       │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### External Systems

| System | Interaction | Direction |
|--------|-------------|-----------|
| GitHub | Read issues, create branches/PRs, manage labels | Auto-slopp → GitHub |
| Telegram | Send log notifications | Auto-slopp → Telegram |
| Vikunja | Read tasks, update task status, create subtasks/PRs | Auto-slopp ↔ Vikunja |
| CLI Tools | Execute AI-powered task instructions | Auto-slopp → CLI tools |
| Git | Repository operations (clone, branch, commit, push) | Auto-slopp ↔ Git |

## 3.2 Software Scope

### In Scope

- Task discovery from configured sources (GitHub issues, Vikunja tasks)
- Task processing via Ralph loop (5-step execution pattern)
- Worker discovery and execution across multiple repositories
- Configuration management via environment variables
- Logging and monitoring (console, file, Telegram)
- CLI tool selection based on task difficulty ratings
- Branch management (create, checkout, push, cleanup)

### Out of Scope

- Direct code editing (delegated to configured CLI tools)
- Manual issue/task triage
- Human review/approval workflows
- Database or persistent storage (stateless per execution)
- Web interface or dashboard

## 3.3 Running Environments

| Environment | Description |
|------------|-------------|
| Development | Local machine with `.venv`, `make test` for validation |
| Production (Systemd) | Linux server with systemd service autostart |
| Production (Docker) | Containerized deployment with volume-mounted repos |

## 3.4 Scope Constraints

- All repositories must be git repositories in subdirectories of `AUTO_SLOPP_BASE_REPO_PATH`
- Each repository is processed independently
- Workers are explicitly enabled/disabled (not auto-discovered from arbitrary paths)
- Task sources are limited to implemented `TaskSource` subclasses (GitHub, Vikunja)
