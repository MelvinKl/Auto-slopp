#!/bin/bash

# Auto-slopp Docker Deployment Script
# Creates Docker configuration for containerized deployment

# Set script name for logging identification
SCRIPT_NAME="docker-deploy"

# Load utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Set up error handling
setup_error_handling

# Docker configuration
IMAGE_NAME="auto-slopp"
CONTAINER_NAME="auto-slopp-container"
DOCKER_DIR="$SCRIPT_DIR/../docker"

# Colors for output
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

print_status() {
    echo -e "${GREEN}[*]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check Docker installation
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker is not installed or not in PATH"
        echo "Please install Docker first: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running or user doesn't have permissions"
        echo "Start Docker daemon or add user to docker group"
        exit 1
    fi
    
    print_status "Docker is available"
}

# Create Docker directory structure
create_docker_structure() {
    print_status "Creating Docker directory structure..."
    
    mkdir -p "$DOCKER_DIR"
    
    # Create directories for volumes
    mkdir -p "$DOCKER_DIR/volumes/{logs,config,managed,task-path}"
    
    print_status "Docker directory structure created"
}

# Create Dockerfile
create_dockerfile() {
    print_status "Creating Dockerfile..."
    
    cat > "$DOCKER_DIR/Dockerfile" << 'EOF'
FROM ubuntu:22.04

# Set non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    jq \
    bash \
    golang-go \
    && rm -rf /var/lib/apt/lists/*

# Install OpenCode CLI
RUN curl -fsSL https://opencode.ai/install.sh | bash

# Install Beads CLI
RUN go install github.com/steveyegge/beads@latest

# Create application directory
WORKDIR /app

# Copy application files
COPY . /app/

# Set permissions
RUN chmod +x /app/main.sh \
    && chmod +x /app/config.sh \
    && chmod +x /app/scripts/*.sh \
    && chmod +x /app/scripts/core/*.sh

# Create directories
RUN mkdir -p /app/logs /app/managed /app/task-path

# Create auto-slopp user
RUN useradd -m -s /bin/bash auto-slopp \
    && chown -R auto-slopp:auto-slopp /app

# Switch to non-root user
USER auto-slopp

# Add Go bin to PATH
ENV PATH="$PATH:$(go env GOPATH)/bin"

# Expose volumes
VOLUME ["/app/logs", "/app/managed", "/app/task-path", "/app/config.yaml"]

# Set working directory
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep -f "main.sh" > /dev/null || exit 1

# Default command
CMD ["./main.sh"]
EOF

    print_status "Dockerfile created"
}

# Create docker-compose.yml
create_docker_compose() {
    print_status "Creating docker-compose.yml..."
    
    cat > "$DOCKER_DIR/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  auto-slopp:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    image: auto-slopp:latest
    container_name: auto-slopp-container
    restart: unless-stopped
    
    # Environment variables
    environment:
      - DEBUG_MODE=${DEBUG_MODE:-false}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
    
    # Volume mounts
    volumes:
      - ./volumes/logs:/app/logs
      - ./volumes/config:/app/config.yaml:ro
      - ./volumes/managed:/app/managed
      - ./volumes/task-path:/app/task-path
      - auto-slopp-state:/app/.number_state
      - auto-slopp-beads:/app/.beads
    
    # Network configuration
    networks:
      - auto-slopp-network
    
    # Resource limits
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
    
    # Health check
    healthcheck:
      test: ["CMD", "pgrep", "-f", "main.sh"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  auto-slopp-state:
    driver: local
  auto-slopp-beads:
    driver: local

networks:
  auto-slopp-network:
    driver: bridge
EOF

    print_status "docker-compose.yml created"
}

# Create .dockerignore file
create_dockerignore() {
    print_status "Creating .dockerignore file..."
    
    cat > "$DOCKER_DIR/../.dockerignore" << 'EOF'
# Git
.git
.gitignore

# Logs
*.log
logs/
Auto-logs/

# Temporary files
.tmp/
temp/
*.tmp

# Build artifacts
build/
dist/
node_modules/

# OS files
.DS_Store
Thumbs.db

# Editor files
.vscode/
.idea/
*.swp
*.swo
*~

# Test files
test/
tests/
*.test
coverage/

# Documentation (excluding README)
docs/
*.md
!README.md

# Backup files
*.backup
*.bak

# State files that should be mounted as volumes
.number_state/
.beads/

# Environment files
.env
.env.local
.env.*.local

# Docker files (to avoid recursion)
docker/
Dockerfile*
docker-compose*
.dockerignore

# CI/CD files
.github/
.gitlab-ci.yml
.travis.yml

# Package manager files
package-lock.json
yarn.lock
Gopkg.lock
go.sum

# IDE specific files
*.iml
.vscode/
.idea/
EOF

    print_status ".dockerignore file created"
}

# Create example configuration
create_example_config() {
    print_status "Creating example Docker configuration..."
    
    cat > "$DOCKER_DIR/volumes/config/config.yaml" << 'EOF'
# Auto-slopp Docker Configuration
# This file is mounted read-only into the container

# Duration between cycles in seconds
sleep_duration: 300

# Path where all repositories are located (inside container)
managed_repo_path: /app/managed

# Separate repository path for task descriptions
managed_repo_task_path: /app/task-path

# Logging configuration
log_directory: /app/logs
log_max_size_mb: 10
log_max_files: 5
log_retention_days: 30
log_level: INFO

# Timestamp configuration
timestamp_format: default
timestamp_timezone: local

# Auto-update-reboot (disabled in Docker)
auto_update_reboot_enabled: false

# Telegram Bot configuration
telegram:
  enabled: false
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  default_chat_id: "@logs_channel"
  api_timeout_seconds: 10
  connection_retries: 3

# Beads updater configuration
beads_updater:
  default_sync_mode: "incremental"
  default_conflict_strategy: "newest"
  default_max_retries: 3
  backup_retention_days: 30
  enable_detailed_reporting: true
  cleanup_temp_files: true
  lock_timeout_minutes: 30

# Branch protection configuration
branch_protection:
  enable_protection: true
  require_confirmation: true
  show_warnings: true
  protected_branches:
    - "main"
    - "master"
    - "develop"
    - "staging"
    - "production"
  protect_current_branch: true
  protection_patterns:
    - "keep-*"
    - "protected-*"
    - "temp-*"
    - "backup-*"

# Branch cleanup configuration
branch_cleanup:
  dry_run_mode: false
  interactive_mode: false
  confirm_before_delete: false
  show_dry_run_summary: true
  batch_confirmation: false
  confirmation_timeout: 60
  safety_mode: true
  backup_before_delete: true
  max_branches_per_run: 50
  show_branch_details: true
  show_safety_info: true
  show_skipped_branches: true
EOF

    print_status "Example configuration created"
}

# Create environment file template
create_env_template() {
    print_status "Creating environment file template..."
    
    cat > "$DOCKER_DIR/.env.template" << 'EOF'
# Auto-slopp Docker Environment Configuration
# Copy this file to .env and customize as needed

# Debug mode (true/false)
DEBUG_MODE=false

# Log level (DEBUG, INFO, WARNING, ERROR, SUCCESS)
LOG_LEVEL=INFO

# Telegram Bot Token (optional - for notifications)
# Get this from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=

# Resource limits
MEMORY_LIMIT=512M
CPU_LIMIT=0.5
MEMORY_RESERVATION=256M
CPU_RESERVATION=0.25

# Network settings
NETWORK_SUBNET=172.20.0.0/16
EOF

    print_status "Environment template created"
}

# Create deployment scripts
create_deployment_scripts() {
    print_status "Creating deployment scripts..."
    
    # Build script
    cat > "$DOCKER_DIR/build.sh" << 'EOF'
#!/bin/bash
set -e

echo "Building Auto-slopp Docker image..."

# Build the image
docker build -t auto-slopp:latest -f docker/Dockerfile .

echo "Image built successfully!"
echo ""
echo "To run: docker run -d --name auto-slopp auto-slopp:latest"
echo "Or use: ./docker/run.sh"
EOF

    # Run script
    cat > "$DOCKER_DIR/run.sh" << 'EOF'
#!/bin/bash
set -e

# Default container name
CONTAINER_NAME="auto-slopp-container"

# Stop existing container if running
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
    echo "Stopping existing container..."
    docker stop "$CONTAINER_NAME"
fi

# Remove existing container
if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
    echo "Removing existing container..."
    docker rm "$CONTAINER_NAME"
fi

# Run new container
echo "Starting Auto-slopp container..."
docker run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -v "$(pwd)/volumes/logs:/app/logs" \
    -v "$(pwd)/volumes/config/config.yaml:/app/config.yaml:ro" \
    -v "$(pwd)/volumes/managed:/app/managed" \
    -v "$(pwd)/volumes/task-path:/app/task-path" \
    --env-file .env \
    auto-slopp:latest

echo "Container started successfully!"
echo ""
echo "View logs: docker logs -f $CONTAINER_NAME"
echo "Check status: docker ps | grep $CONTAINER_NAME"
EOF

    # Stop script
    cat > "$DOCKER_DIR/stop.sh" << 'EOF'
#!/bin/bash

CONTAINER_NAME="auto-slopp-container"

echo "Stopping Auto-slopp container..."
docker stop "$CONTAINER_NAME" || true
docker rm "$CONTAINER_NAME" || true

echo "Container stopped and removed."
EOF

    # Logs script
    cat > "$DOCKER_DIR/logs.sh" << 'EOF'
#!/bin/bash

CONTAINER_NAME="auto-slopp-container"

if [[ "$1" == "-f" ]]; then
    echo "Following Auto-slopp logs (Ctrl+C to exit)..."
    docker logs -f "$CONTAINER_NAME"
else
    echo "Auto-slopp container logs:"
    docker logs "$CONTAINER_NAME"
fi
EOF

    # Status script
    cat > "$DOCKER_DIR/status.sh" << 'EOF'
#!/bin/bash

CONTAINER_NAME="auto-slopp-container"

echo "Auto-slopp Container Status"
echo "==========================="
docker ps -a --filter name="$CONTAINER_NAME"
echo ""
echo "Container information:"
docker inspect "$CONTAINER_NAME" --format='{{.State.Status}} - {{.State.StartedAt}}'
echo ""
echo "Recent logs:"
docker logs --tail 20 "$CONTAINER_NAME"
EOF

    # Make scripts executable
    chmod +x "$DOCKER_DIR"/*.sh
    
    print_status "Deployment scripts created"
}

# Show usage information
show_usage() {
    echo ""
    print_status "Docker deployment setup complete!"
    echo ""
    echo "Quick Start:"
    echo "  cd $DOCKER_DIR"
    echo "  cp .env.template .env"
    echo "  # Edit .env file with your settings"
    echo "  ./build.sh"
    echo "  ./run.sh"
    echo ""
    echo "Alternative with docker-compose:"
    echo "  cd $DOCKER_DIR"
    echo "  cp .env.template .env"
    echo "  docker-compose up -d"
    echo ""
    echo "Management Commands:"
    echo "  ./build.sh              Build Docker image"
    echo "  ./run.sh                Start container"
    echo "  ./stop.sh               Stop and remove container"
    echo "  ./logs.sh [-f]          View container logs"
    echo "  ./status.sh             Show container status"
    echo "  docker-compose ps       Show compose status"
    echo "  docker-compose logs -f  Follow logs"
    echo "  docker-compose down     Stop and remove containers"
    echo ""
    echo "Configuration:"
    echo "  Config file: $DOCKER_DIR/volumes/config/config.yaml"
    echo "  Environment: $DOCKER_DIR/.env"
    echo "  Logs directory: $DOCKER_DIR/volumes/logs"
    echo "  Repositories: $DOCKER_DIR/volumes/managed"
    echo "  Task files: $DOCKER_DIR/volumes/task-path"
    echo ""
    print_warning "Remember to add your repositories to the managed directory"
}

# Cleanup function
cleanup_docker() {
    print_status "Cleaning up Docker resources..."
    
    # Stop and remove container
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    
    # Remove image
    docker rmi "$IMAGE_NAME:latest" 2>/dev/null || true
    
    # Remove volumes
    docker volume rm auto-slopp-state 2>/dev/null || true
    docker volume rm auto-slopp-beads 2>/dev/null || true
    
    print_status "Docker cleanup complete"
}

# Main function
main() {
    echo "Auto-slopp Docker Deployment Setup"
    echo "=================================="
    echo ""
    
    case "${1:-setup}" in
        --help|-h)
            echo "Auto-slopp Docker Deployment Script"
            echo ""
            echo "Usage: $0 [action]"
            echo ""
            echo "Actions:"
            echo "  setup       Create Docker configuration (default)"
            echo "  build       Build Docker image"
            echo "  cleanup     Remove Docker resources"
            echo "  help        Show this help message"
            echo ""
            exit 0
            ;;
        setup)
            check_docker
            create_docker_structure
            create_dockerfile
            create_docker_compose
            create_dockerignore
            create_example_config
            create_env_template
            create_deployment_scripts
            show_usage
            ;;
        build)
            check_docker
            cd "$DOCKER_DIR"
            ./build.sh
            ;;
        cleanup)
            check_docker
            cleanup_docker
            ;;
        *)
            print_error "Unknown action: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"