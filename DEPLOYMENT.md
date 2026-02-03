# Auto-slopp Deployment Guide

This guide provides comprehensive deployment options for Auto-slopp, including local installation, system service, Docker containerization, and automated deployment scenarios.

## 🚀 Quick Deployment Options

### 1. Interactive Full Setup (Recommended)
```bash
./scripts/deploy-setup.sh
```
- Complete interactive installation with configuration
- Installs all dependencies
- Sets up environment variables
- Creates directory structure
- Validates installation

### 2. Quick Setup (Experienced Users)
```bash
./scripts/quick-setup.sh
```
- Fast, non-interactive installation
- Uses default settings
- Installs essential dependencies only

### 3. Docker Deployment
```bash
./scripts/docker-deploy.sh setup
cd docker
cp .env.template .env
# Edit .env with your settings
./build.sh && ./run.sh
```
- Containerized deployment
- Isolated environment
- Easy scaling and management

### 4. System Service (Production)
```bash
sudo ./scripts/install-service.sh
```
- Systemd service installation
- Auto-start on boot
- Log rotation
- Service management scripts

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+)
- **Shell**: Bash 4.4+
- **Memory**: Minimum 512MB RAM (1GB+ recommended)
- **Disk**: 100MB free space (plus space for repositories)
- **Network**: Internet access for git operations and optional Telegram integration

### Required Tools
- `git` - Version control
- `curl` - HTTP client for API calls
- `jq` - JSON processing
- `opencode` - OpenCode CLI for code generation
- `bd` - Beads CLI for task management

## 🏗️ Deployment Methods

### Method 1: Interactive Full Setup

The `deploy-setup.sh` script provides a comprehensive, guided installation:

```bash
./scripts/deploy-setup.sh
```

**Features:**
- Step-by-step wizard with validation
- System requirement checks
- Automatic dependency installation
- Custom path configuration
- Environment setup
- Installation verification
- Example repository creation

**Installation Steps:**
1. System requirements validation
2. Dependency installation (git, curl, jq)
3. OpenCode CLI installation
4. Beads CLI installation
5. Directory structure creation
6. Configuration setup
7. Script permissions
8. Environment variable setup
9. Installation verification
10. Initial setup creation

### Method 2: Quick Setup

For automated or experienced user installations:

```bash
# Interactive quick setup
./scripts/quick-setup.sh quick

# Silent installation
./scripts/quick-setup.sh silent

# Silent installation to custom directory
./scripts/quick-setup.sh silent /opt/auto-slopp
```

**Features:**
- Minimal prompts
- Default configuration
- Fast installation
- Automation-friendly

### Method 3: Docker Deployment

Containerized deployment for isolated environments:

```bash
# Setup Docker configuration
./scripts/docker-deploy.sh setup

cd docker

# Configure environment
cp .env.template .env
# Edit .env file with your settings

# Build and run
./build.sh
./run.sh

# Alternative: use docker-compose
docker-compose up -d
```

**Docker Features:**
- Isolated environment
- Version consistency
- Easy scaling
- Resource limits
- Health checks
- Volume persistence

**Directory Structure:**
```
docker/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Multi-container orchestration
├── .env.template           # Environment variables template
├── build.sh                # Build script
├── run.sh                  # Run script
├── stop.sh                 # Stop script
├── logs.sh                 # Log viewer
├── status.sh               # Status checker
└── volumes/                # Persistent data
    ├── config/             # Configuration files
    ├── logs/               # Log files
    ├── managed/            # Repository storage
    └── task-path/          # Task file storage
```

### Method 4: System Service

Production deployment with systemd:

```bash
# Install as system service
sudo ./scripts/install-service.sh install

# Management commands
sudo systemctl status auto-slopp
sudo systemctl restart auto-slopp
auto-slopp-status          # Convenience script
auto-slopp-logs -f         # Follow logs
```

**Service Features:**
- Auto-start on boot
- Process monitoring
- Automatic restarts
- Log rotation
- Security hardening
- Resource management

## ⚙️ Configuration

### Basic Configuration

Edit `config.yaml` for your environment:

```yaml
# Repository paths
managed_repo_path: '~/git/managed'
managed_repo_task_path: '~/git/repo_task_path'

# Logging
log_directory: '~/git/Auto-logs'
log_level: INFO

# Automation settings
sleep_duration: 300  # 5 minutes between cycles
```

### Environment Variables

Set these in your shell or `.env` file:

```bash
# Auto-slopp environment
export AUTO_SLOPP_HOME="/path/to/auto-slopp"
export AUTO_SLOPP_CONFIG="/path/to/config.yaml"

# Optional: Debug mode
export DEBUG_MODE=true

# Optional: Telegram integration
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

### Advanced Configuration

See `config.yaml` for advanced options:
- Auto-update-reboot settings
- Telegram bot configuration
- Branch protection rules
- Beads synchronization
- Logging levels and formats

## 🗂️ Directory Structure

After deployment, your directory structure should look like:

```
auto-slopp/                    # Installation directory
├── main.sh                    # Main orchestration script
├── config.yaml                # Configuration file
├── scripts/                   # Core scripts
│   ├── deploy-setup.sh        # Full deployment script
│   ├── quick-setup.sh         # Quick deployment script
│   ├── install-service.sh     # System service installer
│   ├── docker-deploy.sh       # Docker deployment script
│   └── ...                    # Other system scripts
├── docker/                    # Docker configuration (if used)
└── .beads/                    # Beads state (if initialized)

~/git/                         # Data directory
├── managed/                   # Repository storage
│   ├── repo1/                 # Repository 1
│   ├── repo2/                 # Repository 2
│   └── repo3/                 # Repository 3
├── repo_task_path/            # Task file storage
│   ├── repo1/                 # Tasks for repo1
│   ├── repo2/                 # Tasks for repo2
│   └── repo3/                 # Tasks for repo3
└── Auto-logs/                 # Log files
    ├── 2026-02-03.log         # Today's logs
    ├── 2026-02-02.log         # Yesterday's logs
    └── ...                    # Rotated logs
```

## 🚦 Running the System

### Starting Auto-slopp

**Method 1: Direct execution**
```bash
cd /path/to/auto-slopp
./main.sh
```

**Method 2: System service**
```bash
sudo systemctl start auto-slopp
sudo systemctl enable auto-slopp  # Start on boot
```

**Method 3: Docker**
```bash
cd docker
docker-compose up -d
```

### Monitoring the System

**Check status:**
```bash
# Direct execution
ps aux | grep main.sh

# System service
systemctl status auto-slopp
auto-slopp-status

# Docker
docker ps
docker-compose ps
```

**View logs:**
```bash
# Log files
tail -f ~/git/Auto-logs/$(date +%Y-%m-%d).log

# System service
journalctl -u auto-slopp -f
auto-slopp-logs -f

# Docker
docker logs -f auto-slopp-container
docker-compose logs -f
```

## 🔧 Management Operations

### Adding Repositories

```bash
# Navigate to managed directory
cd ~/git/managed

# Clone repositories
git clone https://github.com/user/repo1.git repo1
git clone https://github.com/user/repo2.git repo2

# Auto-slopp will automatically detect and process them
```

### Managing Tasks

Tasks are automatically created in task directories:

```bash
# View tasks
ls -la ~/git/repo_task_path/repo1/

# Add manual task
echo "Implement new feature X" > ~/git/repo_task_path/repo1/0001-feature-x.txt

# Auto-slopp will process and implement the task
```

### Configuration Updates

```bash
# Edit configuration
nano config.yaml

# Reload service (if running as service)
sudo systemctl reload auto-slopp

# Restart if needed
sudo systemctl restart auto-slopp
```

## 🐚 Deployment Scripts Reference

### deploy-setup.sh

**Usage:**
```bash
./scripts/deploy-setup.sh          # Interactive setup
./scripts/deploy-setup.sh --help   # Show help
```

**Features:**
- System requirement validation
- Dependency installation
- Path configuration
- Environment setup
- Verification testing

### quick-setup.sh

**Usage:**
```bash
./scripts/quick-setup.sh quick              # Interactive quick setup
./scripts/quick-setup.sh silent              # Silent installation
./scripts/quick-setup.sh silent /path/to/dir # Custom directory
```

**Features:**
- Fast installation
- Default settings
- Automation-friendly
- Custom directory support

### install-service.sh

**Usage:**
```bash
sudo ./scripts/install-service.sh install   # Install service
sudo ./scripts/install-service.sh status    # Check status
sudo ./scripts/install-service.sh uninstall # Remove service
```

**Features:**
- Systemd service creation
- Auto-start configuration
- Log rotation setup
- Management scripts

### docker-deploy.sh

**Usage:**
```bash
./scripts/docker-deploy.sh setup     # Setup Docker config
./scripts/docker-deploy.sh build     # Build image
./scripts/docker-deploy.sh cleanup   # Remove resources
```

**Features:**
- Docker image creation
- Multi-container orchestration
- Volume management
- Environment isolation

## 🛡️ Security Considerations

### Token Security

**Telegram Bot Token:**
- Never store in plain text in config files
- Use environment variables: `export TELEGRAM_BOT_TOKEN="..."`
- Set file permissions: `chmod 600 ~/.bashrc`

**System Security:**
- Run as non-root user when possible
- Use systemd service with `NoNewPrivileges=true`
- Limit container capabilities in Docker
- Regular security updates

### File Permissions

```bash
# Secure configuration files
chmod 600 config.yaml
chmod 700 ~/.bashrc

# Secure scripts
chmod 755 scripts/*.sh
chmod 644 scripts/*.md

# Secure data directories
chmod 755 ~/git/managed
chmod 755 ~/git/repo_task_path
chmod 755 ~/git/Auto-logs
```

### Network Security

- Use HTTPS for git operations
- Validate SSL certificates
- Use VPN for remote repositories
- Configure firewall rules

## 🔍 Troubleshooting

### Common Issues

**1. Permission Denied**
```bash
# Fix script permissions
chmod +x main.sh scripts/*.sh

# Fix directory permissions
chmod 755 ~/git/managed ~/git/repo_task_path
```

**2. Dependencies Missing**
```bash
# Reinstall dependencies
./scripts/deploy-setup.sh

# Manual installation
sudo apt-get install git curl jq
```

**3. Configuration Errors**
```bash
# Validate configuration
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Test loading
source scripts/yaml_config.sh && load_config
```

**4. Service Not Starting**
```bash
# Check service status
systemctl status auto-slopp

# View logs
journalctl -u auto-slopp -n 50

# Check configuration
sudo -u auto-slopp ./main.sh --test
```

### Debug Mode

Enable comprehensive debugging:

```bash
# Enable debug mode
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG

# Run with debug output
DEBUG_MODE=true ./main.sh

# Service debug
sudo systemctl edit auto-slopp
# Add: Environment=DEBUG_MODE=true
sudo systemctl daemon-reload
sudo systemctl restart auto-slopp
```

### Log Analysis

```bash
# Recent errors
grep -i error ~/git/Auto-logs/*.log

# Performance analysis
grep "elapsed_time" ~/git/Auto-logs/*.log

# Full trace
bash -x ./main.sh
```

## 📚 Additional Resources

- **Main Documentation**: [README.md](../README.md)
- **Configuration Guide**: See config.yaml comments
- **Architecture**: [Auto-Update-Reboot Architecture](AUTO_UPDATE_REBOOT_ARCHITECTURE.md)
- **Troubleshooting**: See main README troubleshooting section

## 🤝 Support

For deployment issues:

1. Check this guide first
2. Review main README troubleshooting
3. Check log files for specific errors
4. Run with debug mode enabled
5. Verify system requirements met

Remember to replace placeholder paths and configurations with your actual environment settings.