#!/bin/bash

# Auto-slopp Quick Setup Script
# Fast installation for experienced users or automated deployments

# Set script name for logging identification
SCRIPT_NAME="quick-setup"

# Load utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Set up error handling
setup_error_handling

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

# Quick installation without prompts
quick_install() {
    print_status "Starting Auto-slopp quick setup..."
    
    # Create directories non-interactively
    local base_dir="$HOME/git"
    local managed_dir="$base_dir/managed"
    local task_dir="$base_dir/repo_task_path"
    local log_dir="$base_dir/Auto-logs"
    
    print_status "Creating directory structure..."
    mkdir -p "$managed_dir" "$task_dir" "$log_dir"
    
    # Install dependencies without prompts
    print_status "Installing dependencies..."
    
    # System packages
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update -qq
        sudo apt-get install -y git curl jq
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y git curl jq
    fi
    
    # OpenCode CLI
    if ! command -v opencode >/dev/null 2>&1; then
        print_status "Installing OpenCode CLI..."
        curl -fsSL https://opencode.ai/install.sh | bash >/dev/null 2>&1
    fi
    
    # Beads CLI (requires Go)
    if ! command -v bd >/dev/null 2>&1; then
        if command -v go >/dev/null 2>&1; then
            print_status "Installing Beads CLI..."
            go install github.com/steveyegge/beads@latest >/dev/null 2>&1
            
            # Add to PATH
            echo 'export PATH="$PATH:$(go env GOPATH)/bin"' >> "$HOME/.bashrc"
        else
            print_warning "Go not found, skipping Beads CLI installation"
        fi
    fi
    
    # Set script permissions
    print_status "Setting script permissions..."
    chmod +x "$SCRIPT_DIR/../main.sh"
    chmod +x "$SCRIPT_DIR/../config.sh"
    chmod +x "$SCRIPT_DIR"/*.sh
    chmod +x "$SCRIPT_DIR/core"/*.sh
    
    # Update config with default paths
    print_status "Updating configuration..."
    sed -i "s|managed_repo_path: '~/git/managed'|managed_repo_path: '$managed_dir'|" "$SCRIPT_DIR/../config.yaml"
    sed -i "s|managed_repo_task_path: '~/git/repo_task_path'|managed_repo_task_path: '$task_dir'|" "$SCRIPT_DIR/../config.yaml"
    sed -i "s|log_directory: '~/git/Auto-logs'|log_directory: '$log_dir'|" "$SCRIPT_DIR/../config.yaml"
    
    # Create minimal environment setup
    if ! grep -q "AUTO_SLOPP_HOME" "$HOME/.bashrc"; then
        cat >> "$HOME/.bashrc" << EOF

# Auto-slopp Environment
export AUTO_SLOPP_HOME="$SCRIPT_DIR/.."
export AUTO_SLOPP_CONFIG="$SCRIPT_DIR/../config.yaml"
export PATH="\$PATH:\$AUTO_SLOPP_HOME"
EOF
    fi
    
    print_status "Quick setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. source ~/.bashrc"
    echo "2. Add repositories to: $managed_dir"
    echo "3. Run: ./main.sh"
    echo ""
    echo "For full setup with configuration options, run: ./scripts/deploy-setup.sh"
}

# Silent installation for automation
silent_install() {
    local install_dir="${1:-$HOME/git}"
    
    # Suppress all output except errors
    exec 1>/dev/null
    
    mkdir -p "$install_dir/managed" "$install_dir/repo_task_path" "$install_dir/Auto-logs"
    
    # Install packages if available
    command -v apt-get >/dev/null 2>&1 && sudo apt-get update -qq && sudo apt-get install -y git curl jq >/dev/null 2>&1
    command -v yum >/dev/null 2>&1 && sudo yum install -y git curl jq >/dev/null 2>&1
    
    # Install CLIs
    command -v opencode >/dev/null 2>&1 || curl -fsSL https://opencode.ai/install.sh | bash >/dev/null 2>&1
    command -v go >/dev/null 2>&1 && command -v bd >/dev/null 2>&1 || go install github.com/steveyegge/beads@latest >/dev/null 2>&1
    
    # Set permissions
    chmod +x "$SCRIPT_DIR/../main.sh" "$SCRIPT_DIR/../config.sh" "$SCRIPT_DIR"/*.sh "$SCRIPT_DIR/core"/*.sh 2>/dev/null
    
    # Update config
    sed -i "s|~/git/managed|$install_dir/managed|g" "$SCRIPT_DIR/../config.yaml" 2>/dev/null
    sed -i "s|~/git/repo_task_path|$install_dir/repo_task_path|g" "$SCRIPT_DIR/../config.yaml" 2>/dev/null
    sed -i "s|~/git/Auto-logs|$install_dir/Auto-logs|g" "$SCRIPT_DIR/../config.yaml" 2>/dev/null
    
    # Restore output
    exec 1>&2
    echo "Auto-slopp installed to: $install_dir"
}

# Parse command line arguments
case "${1:-quick}" in
    --help|-h)
        echo "Auto-slopp Quick Setup Script"
        echo ""
        echo "Usage: $0 [mode] [options]"
        echo ""
        echo "Modes:"
        echo "  quick        Interactive quick setup (default)"
        echo "  silent       Silent installation for automation"
        echo ""
        echo "Options for silent mode:"
        echo "  [directory]  Installation directory (default: ~/git)"
        echo ""
        echo "Examples:"
        echo "  $0 quick                    # Interactive quick setup"
        echo "  $0 silent                   # Silent installation to ~/git"
        echo "  $0 silent /opt/auto-slopp   # Silent installation to /opt/auto-slopp"
        exit 0
        ;;
    quick)
        quick_install
        ;;
    silent)
        silent_install "${2:-$HOME/git}"
        ;;
    *)
        print_error "Unknown mode: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac