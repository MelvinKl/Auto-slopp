#!/bin/bash

# Auto-slopp Deployment and Setup Script
# Comprehensive installation and configuration script for Auto-slopp automation system

# Set script name for logging identification
SCRIPT_NAME="deploy-setup"

# Load utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

# Set up error handling
setup_error_handling

# Default configuration
DEFAULT_INSTALL_DIR="$HOME/git"
DEFAULT_MANAGED_REPO_PATH="$DEFAULT_INSTALL_DIR/managed"
DEFAULT_MANAGED_REPO_TASK_PATH="$DEFAULT_INSTALL_DIR/repo_task_path"
DEFAULT_LOG_DIR="$HOME/git/Auto-logs"
DEFAULT_CONFIG_FILE="$SCRIPT_DIR/../config.yaml"

# Non-interactive mode flags
FORCE_ROOT=false
AUTO_INSTALL_PACKAGES=false
SKIP_PACKAGES=false
AUTO_CONFIGURE=true
MANAGED_REPO_PATH=""
MANAGED_REPO_TASK_PATH=""
LOG_DIR=""

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Deployment tracking
DEPLOYMENT_LOG="$HOME/.auto-slopp-deploy.log"
STEP_COUNT=0
TOTAL_STEPS=10

# Utility functions
print_step() {
    ((STEP_COUNT++))
    echo -e "${BLUE}[${STEP_COUNT}/${TOTAL_STEPS}]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "  Auto-slopp Deployment and Setup Script"
    echo "=================================================="
    echo -e "${NC}"
}

log_deployment() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" >> "$DEPLOYMENT_LOG"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "  Auto-slopp Deployment and Setup Script"
    echo "=================================================="
    echo -e "${NC}"
}

log_deployment() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" >> "$DEPLOYMENT_LOG"
}

# System validation functions
check_system_requirements() {
    print_step "Checking system requirements"
    
    local requirements_met=true
    
    # Check operating system
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_warning "Auto-slopp is optimized for Linux. Other systems may require manual adjustments."
    fi
    
    # Check bash version
    local bash_version="${BASH_VERSION%%.*}"
    if [[ "$bash_version" -lt 4 ]]; then
        print_error "Bash 4.0+ is required. Current version: $BASH_VERSION"
        requirements_met=false
    else
        print_success "Bash version: $BASH_VERSION"
    fi
    
    # Check minimum memory
    local available_mem=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [[ "$available_mem" -lt 512 ]]; then
        print_warning "Low memory detected: ${available_mem}MB available. 1GB+ recommended."
    else
        print_success "Memory available: ${available_mem}MB"
    fi
    
    # Check disk space
    local available_space=$(df -BG "$HOME" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ "$available_space" -lt 1 ]]; then
        print_error "Insufficient disk space: ${available_space}GB available. 1GB+ required."
        requirements_met=false
    else
        print_success "Disk space available: ${available_space}GB"
    fi
    
    if [[ "$requirements_met" != true ]]; then
        log_deployment "System requirements check failed"
        exit 1
    fi
    
    print_success "System requirements check passed"
    log_deployment "System requirements check passed"
}

# Dependency installation functions
install_system_dependencies() {
    print_step "Installing system dependencies"
    
    local packages=("git" "curl" "jq")
    local missing_packages=()
    
    # Check for missing packages
    for package in "${packages[@]}"; do
        if ! command -v "$package" >/dev/null 2>&1; then
            missing_packages+=("$package")
        fi
    done
    
    if [[ ${#missing_packages[@]} -eq 0 ]]; then
        print_success "All system dependencies are already installed"
        return 0
    fi
    
    echo "Missing packages: ${missing_packages[*]}"
    
    # Auto-install if flag set, skip if flag set, otherwise ask
    if [[ "$SKIP_PACKAGES" == "true" ]]; then
        print_warning "Skipping system dependency installation (--skip-packages flag set)"
        return 0
    elif [[ "$AUTO_INSTALL_PACKAGES" != "true" ]]; then
        read -p "Install missing packages? (y/N): " -n 1 -r
        echo
        
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_warning "Skipping system dependency installation"
            return 0
        fi
    fi
    
    # Install based on package manager
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y "${missing_packages[@]}"
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y "${missing_packages[@]}"
    elif command -v brew >/dev/null 2>&1; then
        brew install "${missing_packages[@]}"
    else
        print_error "No supported package manager found. Please install manually: ${missing_packages[*]}"
        return 1
    fi
    
    # Verify installation
    local install_failed=false
    for package in "${missing_packages[@]}"; do
        if ! command -v "$package" >/dev/null 2>&1; then
            print_error "Failed to install $package"
            install_failed=true
        fi
    done
    
    if [[ "$install_failed" == true ]]; then
        return 1
    fi
    
    print_success "System dependencies installed successfully"
    log_deployment "System dependencies installed: ${missing_packages[*]}"
}

# OpenCode CLI installation
install_opencode_cli() {
    print_step "Installing OpenCode CLI"
    
    if command -v opencode >/dev/null 2>&1; then
        local opencode_version=$(opencode --version 2>/dev/null || echo "unknown")
        print_success "OpenCode CLI already installed: $opencode_version"
        return 0
    fi
    
    echo "OpenCode CLI not found. Installing..."
    
    # Check if curl is available
    if ! command -v curl >/dev/null 2>&1; then
        print_error "curl is required for OpenCode CLI installation"
        return 1
    fi
    
    # Attempt installation
    if curl -fsSL https://opencode.ai/install.sh | bash; then
        # Add to PATH if not already there
        if ! command -v opencode >/dev/null 2>&1; then
            export PATH="$PATH:/usr/local/bin"
            echo 'export PATH="$PATH:/usr/local/bin"' >> "$HOME/.bashrc"
        fi
        
        # Verify installation
        if command -v opencode >/dev/null 2>&1; then
            local version=$(opencode --version 2>/dev/null || echo "unknown")
            print_success "OpenCode CLI installed: $version"
            log_deployment "OpenCode CLI installed: $version"
        else
            print_error "OpenCode CLI installation failed"
            return 1
        fi
    else
        print_error "OpenCode CLI installation script failed"
        return 1
    fi
}

# Beads CLI installation
install_beads_cli() {
    print_step "Installing Beads CLI"
    
    if command -v bd >/dev/null 2>&1; then
        local beads_version=$(bd --version 2>/dev/null || echo "unknown")
        print_success "Beads CLI already installed: $beads_version"
        return 0
    fi
    
    echo "Beads CLI not found. Installing..."
    
    # Check if Go is available
    if ! command -v go >/dev/null 2>&1; then
        print_warning "Go is required for Beads CLI. Attempting to install Go..."
        
        # Try to install Go
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update
            sudo apt-get install -y golang-go
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y golang
        elif command -v brew >/dev/null 2>&1; then
            brew install go
        else
            print_error "Go is required for Beads CLI installation. Please install Go manually."
            return 1
        fi
    fi
    
    # Install Beads CLI
    if go install github.com/steveyegge/beads@latest; then
        # Add to PATH if not already there
        if ! command -v bd >/dev/null 2>&1; then
            export PATH="$PATH:$(go env GOPATH)/bin"
            echo 'export PATH="$PATH:$(go env GOPATH)/bin"' >> "$HOME/.bashrc"
        fi
        
        # Verify installation
        if command -v bd >/dev/null 2>&1; then
            local version=$(bd --version 2>/dev/null || echo "unknown")
            print_success "Beads CLI installed: $version"
            log_deployment "Beads CLI installed: $version"
        else
            print_error "Beads CLI installation failed"
            return 1
        fi
    else
        print_error "Beads CLI installation failed"
        return 1
    fi
}

# Directory structure creation
create_directory_structure() {
    print_step "Creating directory structure"
    
    local directories=(
        "$DEFAULT_INSTALL_DIR"
        "$DEFAULT_MANAGED_REPO_PATH"
        "$DEFAULT_MANAGED_REPO_TASK_PATH"
        "$DEFAULT_LOG_DIR"
    )
    
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
            log_deployment "Created directory: $dir"
        else
            print_success "Directory exists: $dir"
        fi
    done
    
    # Set proper permissions
    chmod 755 "${directories[@]}"
    print_success "Directory permissions set"
}

# Configuration setup
setup_configuration() {
    print_step "Setting up configuration"
    
    local config_file="$DEFAULT_CONFIG_FILE"
    local config_backup=""
    
    if [[ -f "$config_file" ]]; then
        # Create backup of existing config
        config_backup="${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$config_file" "$config_backup"
        print_success "Backed up existing config to: $config_backup"
    fi
    
    # Use environment variables or defaults if in non-interactive mode
    if [[ "$AUTO_CONFIGURE" == "true" ]]; then
        MANAGED_REPO_PATH="${MANAGED_REPO_PATH:-$DEFAULT_MANAGED_REPO_PATH}"
        MANAGED_REPO_TASK_PATH="${MANAGED_REPO_TASK_PATH:-$DEFAULT_MANAGED_REPO_TASK_PATH}"
        LOG_DIR="${LOG_DIR:-$DEFAULT_LOG_DIR}"
    else
        # Interactive mode - ask for user input
        read -p "Managed repositories path [$DEFAULT_MANAGED_REPO_PATH]: " managed_path
        MANAGED_REPO_PATH="${managed_path:-$DEFAULT_MANAGED_REPO_PATH}"
        
        read -p "Task path [$DEFAULT_MANAGED_REPO_TASK_PATH]: " task_path
        MANAGED_REPO_TASK_PATH="${task_path:-$DEFAULT_MANAGED_REPO_TASK_PATH}"
        
        read -p "Log directory [$DEFAULT_LOG_DIR]: " log_dir
        LOG_DIR="${log_dir:-$DEFAULT_LOG_DIR}"
    fi
    
    # Update config file with paths
    sed -i "s|managed_repo_path: '~/.*/managed'|managed_repo_path: '$MANAGED_REPO_PATH'|" "$config_file"
    sed -i "s|managed_repo_task_path: '~/.*/repo_task_path'|managed_repo_task_path: '$MANAGED_REPO_TASK_PATH'|" "$config_file"
    sed -i "s|log_directory: '~/.*/Auto-logs'|log_directory: '$LOG_DIR'|" "$config_file"
    
    print_success "Configuration updated"
    log_deployment "Configuration updated: managed_repo_path=$MANAGED_REPO_PATH, task_path=$MANAGED_REPO_TASK_PATH, log_dir=$LOG_DIR"
}

# Script permissions
set_script_permissions() {
    print_step "Setting script permissions"
    
    local scripts=(
        "$SCRIPT_DIR/../main.sh"
        "$SCRIPT_DIR/../config.sh"
        "$SCRIPT_DIR"/*.sh
        "$SCRIPT_DIR/core"/*.sh
    )
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            chmod +x "$script"
            print_success "Made executable: $(basename "$script")"
        fi
    done
    
    print_success "Script permissions set"
    log_deployment "Script permissions set for $(ls -1 "${scripts[@]}" 2>/dev/null | wc -l) scripts"
}

# Environment setup
setup_environment() {
    print_step "Setting up environment"
    
    local bashrc="$HOME/.bashrc"
    local env_block="# Auto-slopp Environment"
    
    # Remove existing Auto-slopp environment block
    if grep -q "$env_block" "$bashrc"; then
        sed -i "/$env_block/,/^$/d" "$bashrc"
    fi
    
    # Add environment variables
    cat >> "$bashrc" << EOF

$env_block
export AUTO_SLOPP_HOME="$SCRIPT_DIR/.."
export AUTO_SLOPP_CONFIG="$SCRIPT_DIR/../config.yaml"
export PATH="\$PATH:\$AUTO_SLOPP_HOME"

# Optional: Enable debug mode
# export DEBUG_MODE=true

# Optional: Telegram bot token (set this manually for security)
# export TELEGRAM_BOT_TOKEN="your_bot_token_here"

EOF
    
    print_success "Environment variables added to ~/.bashrc"
    print_warning "Run 'source ~/.bashrc' or restart your shell to apply changes"
    log_deployment "Environment setup completed"
}

# Verification functions
verify_installation() {
    print_step "Verifying installation"
    
    local verification_failed=false
    
    # Check directories
    local directories=("$MANAGED_REPO_PATH" "$MANAGED_REPO_TASK_PATH" "$LOG_DIR")
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            print_error "Missing directory: $dir"
            verification_failed=true
        fi
    done
    
    # Check scripts
    local critical_scripts=("$SCRIPT_DIR/../main.sh" "$SCRIPT_DIR/utils.sh" "$SCRIPT_DIR/yaml_config.sh")
    for script in "${critical_scripts[@]}"; do
        if [[ ! -f "$script" ]]; then
            print_error "Missing script: $(basename "$script")"
            verification_failed=true
        elif [[ ! -x "$script" ]]; then
            print_error "Script not executable: $(basename "$script")"
            verification_failed=true
        fi
    done
    
    # Check dependencies
    local commands=("git" "curl" "jq" "opencode" "bd")
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            print_error "Missing command: $cmd"
            verification_failed=true
        fi
    done
    
    # Test configuration loading
    if ! source "$SCRIPT_DIR/yaml_config.sh" 2>/dev/null || ! load_config "$DEFAULT_CONFIG_FILE" 2>/dev/null; then
        print_error "Configuration loading test failed"
        verification_failed=true
    else
        print_success "Configuration loading test passed"
    fi
    
    if [[ "$verification_failed" == true ]]; then
        print_error "Installation verification failed"
        log_deployment "Installation verification failed"
        return 1
    fi
    
    print_success "Installation verification passed"
    log_deployment "Installation verification passed"
}

# Create initial setup
create_initial_setup() {
    print_step "Creating initial setup"
    
    # Initialize beads if not already done
    if command -v bd >/dev/null 2>&1 && [[ -d "$SCRIPT/../.beads" ]]; then
        cd "$SCRIPT_DIR/.."
        if ! bd status >/dev/null 2>&1; then
            bd init
            print_success "Beads initialized"
        else
            print_success "Beads already initialized"
        fi
    fi
    
    # Create example repository structure
    if [[ ! -d "$MANAGED_REPO_PATH/example-repo" ]]; then
        mkdir -p "$MANAGED_REPO_PATH/example-repo"
        cd "$MANAGED_REPO_PATH/example-repo"
        git init
        echo "# Example Repository" > README.md
        git add README.md
        git commit -m "Initial commit"
        print_success "Created example repository"
    fi
    
    # Create corresponding task directory
    if [[ ! -d "$MANAGED_REPO_TASK_PATH/example-repo" ]]; then
        mkdir -p "$MANAGED_REPO_TASK_PATH/example-repo"
        echo "# Example Repository Tasks" > "$MANAGED_REPO_TASK_PATH/example-repo/README.md"
        touch "$MANAGED_REPO_TASK_PATH/example-repo/.gitkeep"
        print_success "Created example task directory"
    fi
    
    log_deployment "Initial setup completed"
}

# Final setup and next steps
show_next_steps() {
    print_step "Deployment complete!"
    
    echo -e "${GREEN}"
    echo "=================================================="
    echo "  Auto-slopp Deployment Complete!"
    echo "=================================================="
    echo -e "${NC}"
    
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Reload your shell environment:"
    echo "   source ~/.bashrc"
    echo ""
    echo "2. Add your repositories to: $MANAGED_REPO_PATH"
    echo "   cd $MANAGED_REPO_PATH"
    echo "   git clone <your-repo-url> repo-name"
    echo ""
    echo "3. Test the configuration:"
    echo "   cd $SCRIPT_DIR/.."
    echo "   source scripts/yaml_config.sh && load_config"
    echo ""
    echo "4. Run the system:"
    echo "   ./main.sh"
    echo ""
    echo "5. (Optional) Configure Telegram logging:"
    echo "   export TELEGRAM_BOT_TOKEN=\"your_bot_token\""
    echo "   # Edit config.yaml to enable telegram.enabled: true"
    echo ""
    
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "- View logs: tail -f $LOG_DIR/\$(date +%Y-%m-%d).log"
    echo "- Test individual scripts: ./scripts/script-name.sh"
    echo "- Check status: bd status (if beads initialized)"
    echo ""
    
    echo -e "${BLUE}Documentation:${NC}"
    echo "- Full documentation: $SCRIPT_DIR/../README.md"
    echo "- Configuration: $DEFAULT_CONFIG_FILE"
    echo "- Deployment log: $DEPLOYMENT_LOG"
    echo ""
    
    echo -e "${GREEN}✓ Auto-slopp is ready to use!${NC}"
    log_deployment "Deployment completed successfully"
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --force)
                FORCE_ROOT=true
                shift
                ;;
            --install-packages)
                AUTO_INSTALL_PACKAGES=true
                shift
                ;;
            --skip-packages)
                SKIP_PACKAGES=true
                shift
                ;;
            --managed-path)
                MANAGED_REPO_PATH="$2"
                AUTO_CONFIGURE=true
                shift 2
                ;;
            --task-path)
                MANAGED_REPO_TASK_PATH="$2"
                AUTO_CONFIGURE=true
                shift 2
                ;;
            --log-dir)
                LOG_DIR="$2"
                AUTO_CONFIGURE=true
                shift 2
                ;;
            --auto-configure)
                AUTO_CONFIGURE=true
                shift
                ;;
            --help|-h)
                echo "Auto-slopp Deployment and Setup Script"
                echo ""
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --help, -h           Show this help message"
                echo "  --force              Continue even if running as root"
                echo "  --install-packages    Automatically install missing packages"
                echo "  --skip-packages      Skip package installation entirely"
                echo "  --managed-path PATH   Set managed repositories path"
                echo "  --task-path PATH     Set task path"
                echo "  --log-dir PATH       Set log directory"
                echo "  --auto-configure     Use default values for all prompts"
                echo ""
                echo "Environment Variables (alternative to flags):"
                echo "  AUTO_SLOPP_FORCE_ROOT=true"
                echo "  AUTO_SLOPP_AUTO_INSTALL=true"
                echo "  AUTO_SLOPP_SKIP_PACKAGES=true"
                echo "  AUTO_SLOPP_MANAGED_REPO_PATH"
                echo "  AUTO_SLOPP_TASK_PATH"
                echo "  AUTO_SLOPP_LOG_DIR"
                echo ""
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Check for environment variables as fallback
    if [[ "$AUTO_SLOPP_FORCE_ROOT" == "true" ]]; then
        FORCE_ROOT=true
    fi
    if [[ "$AUTO_SLOPP_AUTO_INSTALL" == "true" ]]; then
        AUTO_INSTALL_PACKAGES=true
    fi
    if [[ "$AUTO_SLOPP_SKIP_PACKAGES" == "true" ]]; then
        SKIP_PACKAGES=true
    fi
    if [[ -n "$AUTO_SLOPP_MANAGED_REPO_PATH" ]]; then
        MANAGED_REPO_PATH="$AUTO_SLOPP_MANAGED_REPO_PATH"
        AUTO_CONFIGURE=true
    fi
    if [[ -n "$AUTO_SLOPP_TASK_PATH" ]]; then
        MANAGED_REPO_TASK_PATH="$AUTO_SLOPP_TASK_PATH"
        AUTO_CONFIGURE=true
    fi
    if [[ -n "$AUTO_SLOPP_LOG_DIR" ]]; then
        LOG_DIR="$AUTO_SLOPP_LOG_DIR"
        AUTO_CONFIGURE=true
    fi
}

# Main execution function
main() {
    print_header
    
    # Check if running as root (not recommended)
    if [[ "$EUID" -eq 0 ]]; then
        print_warning "Running as root is not recommended. Please run as a regular user."
        if [[ "$FORCE_ROOT" != "true" ]]; then
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            print_warning "Continuing as root (--force flag set)"
        fi
    fi
    
    # Create deployment log
    touch "$DEPLOYMENT_LOG"
    log_deployment "Starting Auto-slopp deployment"
    
    # Run deployment steps
    check_system_requirements || exit 1
    install_system_dependencies || exit 1
    install_opencode_cli || exit 1
    install_beads_cli || exit 1
    create_directory_structure || exit 1
    setup_configuration || exit 1
    set_script_permissions || exit 1
    setup_environment || exit 1
    verify_installation || exit 1
    create_initial_setup || exit 1
    show_next_steps
    
    log_deployment "Auto-slopp deployment completed successfully"
}

# Handle script execution
case "${1:-}" in
    --help|-h|--force|--install-packages|--skip-packages|--managed-path|--task-path|--log-dir|--auto-configure)
        parse_arguments "$@"
        main "$@"
        ;;
    --uninstall)
        echo "Uninstall feature not yet implemented"
        exit 1
        ;;
    "")
        # Default behavior - still parse args in case env vars are set
        parse_arguments "$@"
        main "$@"
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac