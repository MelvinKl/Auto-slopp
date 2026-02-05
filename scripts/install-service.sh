#!/bin/bash

# Auto-slopp System Service Installer
# Creates systemd service for Auto-slopp daemon

# Set script name for logging identification
SCRIPT_NAME="install-service"

# Load utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Set up error handling
setup_error_handling

# Service configuration
SERVICE_NAME="auto-slopp"
SERVICE_USER="${SUDO_USER:-$USER}"
SERVICE_GROUP="$SERVICE_USER"
AUTO_SLOPP_HOME="$(cd "$SCRIPT_DIR/.." && pwd)"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Non-interactive mode flags
FORCE_INSTALL=false

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

# Check if running with sudo
check_sudo() {
    if [[ "$EUID" -ne 0 ]]; then
        print_error "This script requires sudo privileges to install system service"
        echo "Please run: sudo $0"
        exit 1
    fi
}

# Validate installation
validate_installation() {
    print_status "Validating Auto-slopp installation..."
    
    if [[ ! -f "$AUTO_SLOPP_HOME/main.sh" ]]; then
        print_error "Auto-slopp main.sh not found at: $AUTO_SLOPP_HOME/main.sh"
        exit 1
    fi
    
    if [[ ! -f "$AUTO_SLOPP_HOME/config.yaml" ]]; then
        print_error "Auto-slopp config.yaml not found at: $AUTO_SLOPP_HOME/config.yaml"
        exit 1
    fi
    
    # Test configuration loading
    if ! sudo -u "$SERVICE_USER" bash -c "cd '$AUTO_SLOPP_HOME' && source scripts/yaml_config.sh && load_config config.yaml" >/dev/null 2>&1; then
        print_warning "Configuration validation failed - service may not start properly"
        if [[ "$FORCE_INSTALL" != "true" ]]; then
            print_info "AUTO_CONFIRM mode: Continuing installation without prompt"
            # Auto-continue in hands-off mode
        else
            print_warning "Continuing anyway (--force-install flag set)"
        fi
    fi
    
    print_status "Installation validation passed"
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --force|-f)
                FORCE_INSTALL=true
                shift
                ;;
            --help|-h)
                echo "Auto-slopp System Service Installer"
                echo ""
                echo "Usage: $0 [action] [options]"
                echo ""
                echo "Actions:"
                echo "  install     Install and enable service (default)"
                echo "  uninstall   Remove service and configuration"
                echo "  status      Show service status"
                echo "  help        Show this help message"
                echo ""
                echo "Options:"
                echo "  --force, -f    Force installation even if validation fails"
                echo ""
                exit 0
                ;;
            *)
                # Not a flag, let main handle it
                break
                ;;
        esac
    done
}

# Main installation function
main() {
    echo "Auto-slopp System Service Installer"
    echo "==================================="
    echo ""
    
    case "${1:-install}" in
        --help|-h)
            echo "Auto-slopp System Service Installer"
            echo ""
            echo "Usage: $0 [action]"
            echo ""
            echo "Actions:"
            echo "  install     Install and enable service (default)"
            echo "  uninstall   Remove service and configuration"
            echo "  status      Show service status"
            echo "  help        Show this help message"
            echo ""
            exit 0
            ;;
        uninstall)
            check_sudo
            uninstall_service
            exit 0
            ;;
        status)
            if command -v systemctl >/dev/null 2>&1; then
                systemctl status "$SERVICE_NAME" --no-pager
            else
                print_error "systemctl not found"
                exit 1
            fi
            exit 0
            ;;
        install|"")
            check_sudo
            validate_installation
            create_service_file
            setup_log_rotation
            create_management_scripts
            enable_service
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown action: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
}

# Handle script execution
case "${1:-}" in
    --force|-f)
        FORCE_INSTALL=true
        shift
        main "$@"
        ;;
    --help|-h)
        echo "Auto-slopp System Service Installer"
        echo ""
        echo "Usage: $0 [action] [options]"
        echo ""
        echo "Actions:"
        echo "  install     Install and enable service (default)"
        echo "  uninstall   Remove service and configuration"
        echo "  status      Show service status"
        echo "  help        Show this help message"
        echo ""
        echo "Options:"
        echo "  --force, -f    Force installation even if validation fails"
        echo ""
        exit 0
        ;;
    uninstall|status)
        main "$@"
        ;;
    install|"")
        # Check if force flag was passed
        if [[ "$2" == "--force" ]] || [[ "$2" == "-f" ]]; then
            FORCE_INSTALL=true
        fi
        main "$@"
        ;;
    *)
        main "$@"
        ;;
esac