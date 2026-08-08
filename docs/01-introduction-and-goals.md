# 1 Introduction and Goals

## 1.1 Purpose

Auto-slopp is a Python-based automation framework for task execution with a pluggable worker system. It provides a flexible foundation for creating automation workflows that process tasks from various sources (GitHub issues, Vikunja tasks, etc.) using configurable AI-powered CLI tools.

The framework enables:
- Automated processing of GitHub issues and Vikunja tasks
- Dynamic worker discovery and execution
- Multi-source task processing through a unified interface
- Real-time monitoring via Telegram notifications
- Tiered CLI tool selection based on task complexity

## 1.2 Vision

Auto-slopp aims to be a general-purpose automation framework that can handle diverse task sources through a pluggable architecture. The system should be:
- **Extensible**: New workers and task sources can be added without modifying core code
- **Configurable**: Behavior is driven by environment variables and configuration files
- **Observable**: Comprehensive logging with Telegram integration for real-time monitoring
- **Modern**: Built with Python 3.14+ using modern tooling (uv, pydantic, type hints)

## 1.3 Quality Goals

### Quality Tree

```
Auto-slopp Quality Goals
├── Extensibility
│   ├── Easy to add new worker types (inherit from Worker base class)
│   ├── Easy to add new task sources (implement TaskSource interface)
│   └── Plugin-like worker discovery
├── Configurability
│   ├── All settings via environment variables
│   ├── Pydantic-based validation
│   └── Tiered CLI tool configuration
├── Observability
│   ├── Structured console logging
│   ├── Rotating file logging (WARNING+)
│   └── Telegram real-time notifications
├── Reliability
│   ├── Graceful worker failure handling
│   ├── Retry logic for external APIs
│   └── Cooldown mechanism for failing CLI tools
└── Maintainability
    ├── Comprehensive type hints
    ├── Full test suite with pytest
    └── Code quality checks (black, isort, flake8)
```

### Quality Scenarios

| Scenario | Response |
|----------|----------|
| Add a new worker type | Inherit from `Worker` base class, implement `run()` method, place in `workers/` directory |
| Add a new task source | Implement `TaskSource` abstract class, register with `IssueWorker` |
| Change CLI tool configuration | Update `AUTO_SLOPP_CLI_CONFIGURATIONS` environment variable (JSON) |
| Monitor system remotely | Configure Telegram bot token and chat ID via environment variables |
| Scale to multiple repositories | Set `AUTO_SLOPP_BASE_REPO_PATH` to directory containing repos |

## 1.4 Stakeholders

| Stakeholder | Interest |
|-------------|----------|
| Project Maintainer (MelvinKl) | Automation of issue/task processing across repositories |
| Developers | Extending the framework with custom workers |
| DevOps/SRE | Monitoring via Telegram, deployment via Docker/systemd |

## 1.5 Constraints

- Python 3.14+ required
- Uses `uv` package manager
- GitHub operations require `gh` CLI
- External services: GitHub API, Telegram API, Vikunja API (optional)

## 1.6 Terminology and Acronyms

See [Chapter 12: Glossary](12-glossary.md) for full terminology.

Key terms:
- **Worker**: A pluggable automation unit that processes repositories
- **TaskSource**: Abstraction for loading tasks from different sources (GitHub, Vikunja)
- **Ralph**: The step-based execution loop for processing tasks
- **Slop**: AI-generated code that may be plausible but unreliable
