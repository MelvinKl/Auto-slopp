# Non-Interactive Mode Configuration Guide

This document describes how to run all Auto-slopp scripts completely hands-off (non-interactive mode).

## Overview

All user interaction prompts have been replaced with command-line flags and environment variables, allowing completely automated execution.

## Quick Start

### Complete hands-off deployment:
```bash
./scripts/deploy-setup.sh --force --install-packages --auto-configure
```

### Complete hands-off service installation:
```bash
sudo ./scripts/install-service.sh install --force
```

## deploy-setup.sh - Complete Non-Interactive Deployment

### Command-Line Flags

| Flag | Description |
|------|-------------|
| `--force` | Continue even if running as root (skip root warning) |
| `--install-packages` | Automatically install missing system packages |
| `--skip-packages` | Skip package installation entirely |
| `--managed-path PATH` | Set managed repositories path (non-interactive) |
| `--task-path PATH` | Set task path (non-interactive) |
| `--log-dir PATH` | Set log directory (non-interactive) |
| `--auto-configure` | Use default values for all configuration prompts |
| `--help` | Show help message |

### Environment Variables (Alternative to Flags)

| Variable | Description |
|----------|-------------|
| `AUTO_SLOPP_FORCE_ROOT=true` | Equivalent to `--force` |
| `AUTO_SLOPP_AUTO_INSTALL=true` | Equivalent to `--install-packages` |
| `AUTO_SLOPP_SKIP_PACKAGES=true` | Equivalent to `--skip-packages` |
| `AUTO_SLOPP_MANAGED_REPO_PATH` | Set managed repositories path |
| `AUTO_SLOPP_TASK_PATH` | Set task path |
| `AUTO_SLOPP_LOG_DIR` | Set log directory |

### Usage Examples

**Basic non-interactive deployment:**
```bash
./scripts/deploy-setup.sh --auto-configure
```

**Deployment with automatic package installation:**
```bash
./scripts/deploy-setup.sh --install-packages --auto-configure
```

**Deployment with custom paths:**
```bash
./scripts/deploy-setup.sh \
  --managed-path "/opt/auto-slopp/managed" \
  --task-path "/opt/auto-slopp/tasks" \
  --log-dir "/var/log/auto-slopp"
```

**Deployment as root (hands-off):**
```bash
sudo ./scripts/deploy-setup.sh --force --install-packages --auto-configure
```

**Using environment variables:**
```bash
export AUTO_SLOPP_AUTO_INSTALL=true
export AUTO_SLOPP_MANAGED_REPO_PATH="/custom/path"
./scripts/deploy-setup.sh --auto-configure
```

## install-service.sh - Complete Non-Interactive Service Installation

### Command-Line Flags

| Flag | Description |
|------|-------------|
| `--force, -f` | Force installation even if configuration validation fails |
| `--help, -h` | Show help message |

### Usage Examples

**Basic service installation:**
```bash
sudo ./scripts/install-service.sh install
```

**Force installation despite validation warnings:**
```bash
sudo ./scripts/install-service.sh install --force
```

**Or using short flag:**
```bash
sudo ./scripts/install-service.sh install -f
```

## telegram_security.sh - Non-Interactive Token Input

### Non-Interactive Methods

The `secure_token_input()` function now supports non-interactive token input in the following priority order:

1. **Environment Variable** (highest priority):
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"
   ```

2. **Token File** (second priority):
   - Default location: `/etc/telegram/token`
   - Custom location: `TELEGRAM_TOKEN_FILE=/path/to/token ./script.sh`

3. **Interactive Input** (fallback):
   - Only used if no environment variable or token file is found

### Usage Examples

**Set token via environment variable:**
```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
./scripts/your-script.sh
```

**Set custom token file location:**
```bash
TELEGRAM_TOKEN_FILE="/home/user/.telegram_token" ./scripts/your-script.sh
```

**Complete hands-off Telegram setup:**
```bash
#!/bin/bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export AUTO_SLOPP_AUTO_INSTALL=true
export AUTO_SLOPP_MANAGED_REPO_PATH="/opt/auto-slopp/managed"

./scripts/deploy-setup.sh --auto-configure
sudo ./scripts/install-service.sh install --force
```

## Migration from Interactive to Non-Interactive

### Before (Interactive Mode):
```bash
# User had to respond to prompts:
./scripts/deploy-setup.sh
# > "Install missing packages? (y/N):" → User types "y"
# > "Managed repositories path [...]: " → User types path
# > "Continue anyway? (y/N):" → User types "y" (if root)
```

### After (Non-Interactive Mode):
```bash
# Completely automated:
./scripts/deploy-setup.sh --force --install-packages --auto-configure
```

## Error Handling in Non-Interactive Mode

All scripts maintain proper error handling even in non-interactive mode:

- **Validation errors** will still cause script exit (e.g., missing required files)
- **Configuration errors** will log warnings but continue if `--force` is set
- **Package installation failures** will be logged and may cause exit if critical

## Best Practices

1. **Always use `--auto-configure`** for completely hands-off execution
2. **Set environment variables** for sensitive information (tokens) rather than command-line arguments
3. **Use `--force`** when running as root or in CI/CD environments
4. **Test in non-interactive mode** before deployment to production
5. **Review logs** at `~/.auto-slopp-deploy.log` for deployment details

## Complete CI/CD Example

```bash
#!/bin/bash
set -e  # Exit on error

# Configure environment
export AUTO_SLOPP_FORCE_ROOT=true
export AUTO_SLOPP_AUTO_INSTALL=true
export AUTO_SLOPP_MANAGED_REPO_PATH="/opt/auto-slopp/managed"
export AUTO_SLOPP_TASK_PATH="/opt/auto-slopp/tasks"
export AUTO_SLOPP_LOG_DIR="/var/log/auto-slopp"

# Deploy Auto-slopp
./scripts/deploy-setup.sh --auto-configure

# Install service
sudo ./scripts/install-service.sh install --force

echo "Auto-slopp deployment completed successfully!"
```

## Troubleshooting

### Issue: Script still prompts for input
**Solution:** Ensure all required flags or environment variables are set. Check for typos in flag names.

### Issue: Configuration validation fails
**Solution:** Use `--force` flag to bypass validation warnings, or fix the underlying configuration issues.

### Issue: Token input still required
**Solution:** Set `TELEGRAM_BOT_TOKEN` environment variable before running the script.

### Issue: Running as root but script exits
**Solution:** Use `--force` flag or set `AUTO_SLOPP_FORCE_ROOT=true` environment variable.

## Support

For issues or questions about non-interactive mode, review the script help:
```bash
./scripts/deploy-setup.sh --help
./scripts/install-service.sh --help
```
