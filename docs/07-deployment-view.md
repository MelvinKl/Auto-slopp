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
  auto-slopp:latest
```

## 7.2 Deployment Artifacts

| Artifact | Description | Location |
|----------|-------------|----------|
| `pyproject.toml` | Project metadata and dependencies | Root |
| `Dockerfile` | Container definition | Root |
| `.env.example` | Environment variable template | Root |
| `Makefile` | Development and CI commands | Root |
| `auto-slopp.service` | Systemd unit file | `/etc/systemd/system/` |

## 7.3 Environment Variables

All configuration is via environment variables with `AUTO_SLOPP_` prefix:

| Variable | Required | Description |
|----------|----------|-------------|
| `AUTO_SLOPP_BASE_REPO_PATH` | Yes | Directory containing git repositories |
| `AUTO_SLOPP_DEBUG` | No | Enable debug mode (default: false) |
| `AUTO_SLOPP_TELEGRAM_ENABLED` | No | Enable Telegram logging (default: false) |
| `AUTO_SLOPP_TELEGRAM_BOT_TOKEN` | No* | Telegram bot token |
| `AUTO_SLOPP_TELEGRAM_CHAT_ID` | No* | Telegram chat ID |
| `AUTO_SLOPP_CLI_CONFIGURATIONS` | No | JSON array of CLI tool configs |
| `AUTO_SLOPP_TASK_DIFFICULTIES` | No | JSON object of task difficulty ratings |
| `AUTO_SLOPP_SLOP_TIMEOUT` | No | Execution timeout in seconds (default: 7200) |
| `AUTO_SLOPP_LOG_FILE_DIR` | No | Directory for rotating log files |
| `AUTO_SLOPP_WORKERS_DISABLED` | No | JSON array of disabled worker names |

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
