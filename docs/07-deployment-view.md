# 7 Deployment View

## 7.1 Deployment Infrastructure

### Development Deployment

```
┌─────────────────────────────────────────────────┐
│              Developer Machine                    │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │  Auto-slopp (uv-managed .venv)              │ │
│  │  ┌─────────────────────────────────────────┐│ │
│  │  │  src/auto_slopp/                        ││ │
│  │  │  tests/                                 ││ │
│  │  │  docs/                                  ││ │
│  │  └─────────────────────────────────────────┘│ │
│  │                                             │ │
│  │  make test  ←  black + isort + flake8       │ │
│  │            +  pytest + safety + bandit      │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  Managed repos: /path/to/managed/                 │
│  Configuration: .env file + environment vars      │
└─────────────────────────────────────────────────┘
```

### Systemd Deployment

```
┌─────────────────────────────────────────────────┐
│              Production Server                    │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │  systemd service: auto-slopp.service        │ │
│  │                                             │ │
│  │  [Service]                                  │ │
│  │  Type=simple                                │ │
│  │  User=your-username                         │ │
│  │  WorkingDirectory=/path/to/Auto-slopp       │ │
│  │  Environment="PATH=.../.venv/bin:/usr/bin"  │ │
│  │  EnvironmentFile=/path/to/Auto-slopp/.env   │ │
│  │  ExecStart=/path/to/Auto-slopp/.venv/bin/   │ │
│  │            auto-slopp                        │ │
│  │  Restart=on-failure                          │ │
│  │  RestartSec=10                               │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │  /path/to/managed/                           │ │
│  │  ├── repository_a/  (git repo)              │ │
│  │  ├── repository_b/  (git repo)              │ │
│  │  └── repository_c/  (git repo)              │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

Install:
```bash
sudo systemctl daemon-reload
sudo systemctl enable auto-slopp
sudo systemctl start auto-slopp
```

### Systemd Service File Example

```ini
[Unit]
Description=Auto-slopp Automation Framework
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/auto-slopp
Environment="PATH=/opt/auto-slopp/.venv/bin:/usr/bin:/usr/local/bin"
EnvironmentFile=/opt/auto-slopp/.env
ExecStart=/opt/auto-slopp/.venv/bin/auto-slopp
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=auto-slopp

[Install]
WantedBy=multi-user.target
```

### Systemd Deployment Notes

- `EnvironmentFile` loads `.env` for configuration
- `PATH` must include both `.venv/bin` and system paths (`/usr/bin`, `/usr/local/bin`)
- CLI tools (pi, opencode) must be available in PATH
- Logs go to `journalctl -u auto-slopp`
- `GH_TOKEN` must be in a separate `.gh.env` file loaded via `AUTO_SLOPP_ADDITIONAL_ENV_FILE`
- The service runs in an endless loop — no separate cron needed
- `RestartSec=10` provides a 10-second delay before auto-restart on failure

### Docker Deployment

```
┌─────────────────────────────────────────────────┐
│              Docker Host                          │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │  Docker Container: auto-slopp               │ │
│  │  ┌─────────────────────────────────────────┐│ │
│  │  │  Auto-slopp (Python 3.14 + .venv)      ││ │
│  │  │  ┌───────────────────────────────────┐ ││ │
│  │  │  │  src/auto_slopp/                  │ ││ │
│  │  │  │  .venv/                           │ ││ │
│  │  │  └───────────────────────────────────┘ ││ │
│  │  └─────────────────────────────────────────┘│ │
│  │                                             │ │
│  │  Volumes:                                   │ │
│  │  /repos ← /path/to/managed/repos            │ │
│  │                                             │ │
│  │  Environment:                                 │ │
│  │  AUTO_SLOPP_TELEGRAM_ENABLED=true           │ │
│  │  AUTO_SLOPP_TELEGRAM_BOT_TOKEN=...          │ │
│  │  AUTO_SLOPP_TELEGRAM_CHAT_ID=...            │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

Build and run:
```bash
docker build -t auto-slopp:latest .
docker run -d \
  --name auto-slopp \
  -v /path/to/managed/repos:/repos \
  -e AUTO_SLOPP_TELEGRAM_ENABLED=true \
  -e AUTO_SLOPP_TELEGRAM_BOT_TOKEN=... \
  -e AUTO_SLOPP_TELEGRAM_CHAT_ID=... \
  auto-slopp:latest
```

### Docker Compose (Alternative)

```yaml
version: '3.8'
services:
  auto-slopp:
    build: .
    container_name: auto-slopp
    volumes:
      - /path/to/managed/repos:/repos
    environment:
      - AUTO_SLOPP_TELEGRAM_ENABLED=true
      - AUTO_SLOPP_TELEGRAM_BOT_TOKEN=${TG_BOT_TOKEN}
      - AUTO_SLOPP_TELEGRAM_CHAT_ID=${TG_CHAT_ID}
      - AUTO_SLOPP_BASE_REPO_PATH=/repos
    restart: unless-stopped
```

### Docker Deployment Notes

- The container expects repos mounted at `/repos`
- `GH_TOKEN` must be provided via `additional_env_file` setting (e.g., `/host/.gh.env`)
- No database or persistent state — stateless per execution
- Container runs in an endless loop with configurable sleep interval
- Logs go to console (all levels) and optionally to file/Telegram

## 7.2 Deployment Artifacts

| Artifact | Description | Location |
|----------|-------------|----------|
| `pyproject.toml` | Project metadata, dependencies, and entry points | Root |
| `Dockerfile` | Multi-stage container definition | Root |
| `.dockerignore` | Files to exclude from Docker build | Root |
| `.env.example` | Environment variable template | Root |
| `Makefile` | Development and CI commands | Root |
| `auto-slopp.service` | Systemd unit file (manual setup) | `/etc/systemd/system/` |
| `.pre-commit-config.yaml` | Pre-commit hooks configuration | Root |

### pyproject.toml Structure

```toml
[project]
name = "auto-slopp"
version = "0.1.0"
entry-points:
  auto-slopp = "auto_slopp.main:main"

[project.dependencies]
# Core dependencies: pydantic, pydantic-settings, httpx, python-dotenv

[project.optional-dependencies]
dev = ["pytest", "black", "isort", "flake8", "safety", "bandit"]
```

### Dockerfile Structure

```dockerfile
FROM python:3.14-slim
WORKDIR /app
# Install git, uv
# Copy pyproject.toml and src/
# uv sync --no-dev
ENV AUTO_SLOPP_BASE_REPO_PATH=/repos
VOLUME ["/repos"]
ENTRYPOINT ["uv", "run", "auto-slopp"]
```

### .dockerignore

Excludes: `.venv/`, `__pycache__/`, `.pytest_cache/`, `logs/`, `.git/`, `*.egg-info/`

## 7.3 Environment Variables

All configuration is via environment variables with `AUTO_SLOPP_` prefix:

| Variable | Required | Description |
|----------|----------|-------------|
| `AUTO_SLOPP_BASE_REPO_PATH` | No | Directory containing git repositories (default: cwd) |
| `AUTO_SLOPP_DEBUG` | No | Enable debug mode (default: false) |
| `AUTO_SLOPP_TELEGRAM_ENABLED` | No | Enable Telegram logging (default: false) |
| `AUTO_SLOPP_TELEGRAM_BOT_TOKEN` | No* | Telegram bot token |
| `AUTO_SLOPP_TELEGRAM_CHAT_ID` | No* | Telegram chat ID |
| `AUTO_SLOPP_LOG_FILE_DIR` | No | Directory for rotating log files |
| `AUTO_SLOPP_WORKERS_DISABLED` | No | Comma-separated list of disabled worker names |
| `AUTO_SLOPP_RALPH_MAX_LOOPS` | No | Max Ralph loop iterations (default: 500) |
| `AUTO_SLOPP_GITHUB_ISSUE_STEP_MAX_ITERATIONS` | No | Max step iterations per issue (default: 50) |
| `AUTO_SLOPP_RALPH_ENABLED` | No | Enable Ralph loop (default: true) |
| `AUTO_SLOPP_ADDITIONAL_ENV_FILE` | No | Path to additional .env file for subprocess calls |
| `AUTO_SLOPP_STALE_BRANCH_DAYS_THRESHOLD` | No | Days before branch is stale (default: 1) |
| `AUTO_SLOPP_AUTO_UPDATE_REBOOT_DELAY` | No | Seconds before reboot after update (default: 300) |
| `AUTO_SLOPP_EXECUTOR_SLEEP_INTERVAL` | No | Seconds between executor iterations (default: 600) |

*Only required when `AUTO_SLOPP_TELEGRAM_ENABLED=true`

## 7.4 Network Requirements

| Destination | Protocol | Port | Purpose |
|-------------|----------|------|---------|
| `api.github.com` | HTTPS | 443 | GitHub API (issues, PRs) |
| `api.telegram.org` | HTTPS | 443 | Telegram bot API |
| Vikunja instance | HTTPS | 443 | Vikunja API (optional) |
| CLI tool endpoints | HTTPS | 443 | AI tool APIs (opencode, gemini, etc.) |

## 7.5 Security Considerations

- **GitHub Token**: Never in `.env` — use separate `.gh.env` file outside project
- **Telegram Token**: Only in environment variables
- **Log Files**: Added to `.gitignore`, stored locally
- **PATH in Systemd**: Must include both `.venv/bin` and system paths (`/usr/bin`, `/usr/local/bin`)
