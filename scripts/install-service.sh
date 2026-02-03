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
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_status "Installation validation passed"
}

# Create systemd service file
create_service_file() {
    print_status "Creating systemd service file..."
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Auto-slopp Repository Automation System
Documentation=https://github.com/auto-slopp/auto-slopp
After=network.target
Wants=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$AUTO_SLOPP_HOME
ExecStart=/bin/bash $AUTO_SLOPP_HOME/main.sh
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=auto-slopp

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$AUTO_SLOPP_HOME

# Environment
Environment=AUTO_SLOPP_HOME=$AUTO_SLOPP_HOME
Environment=AUTO_SLOPP_CONFIG=$AUTO_SLOPP_HOME/config.yaml

[Install]
WantedBy=multi-user.target
EOF
    
    print_status "Service file created: $SERVICE_FILE"
}

# Set up log rotation
setup_log_rotation() {
    print_status "Setting up log rotation..."
    
    local logrotate_file="/etc/logrotate.d/auto-slopp"
    
    # Get log directory from config
    local log_dir=$(sudo -u "$SERVICE_USER" bash -c "cd '$AUTO_SLOPP_HOME' && source scripts/yaml_config.sh && load_config config.yaml && echo \$LOG_DIRECTORY" 2>/dev/null)
    log_dir="${log_dir:-$HOME/git/Auto-logs}"
    
    cat > "$logrotate_file" << EOF
$log_dir/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $SERVICE_USER $SERVICE_GROUP
    postrotate
        # Send USR1 signal to main.sh to reopen log files
        systemctl reload auto-slopp 2>/dev/null || true
    endscript
}
EOF
    
    print_status "Log rotation configured for: $log_dir"
}

# Enable and start service
enable_service() {
    print_status "Enabling and starting service..."
    
    # Reload systemd to recognize new service
    systemctl daemon-reload
    
    # Enable service to start on boot
    systemctl enable "$SERVICE_NAME"
    
    # Start service immediately
    systemctl start "$SERVICE_NAME"
    
    # Check status
    sleep 2
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_status "Service is running successfully"
        systemctl status "$SERVICE_NAME" --no-pager
    else
        print_error "Service failed to start"
        systemctl status "$SERVICE_NAME" --no-pager
        print_error "Check logs with: journalctl -u $SERVICE_NAME -f"
        exit 1
    fi
}

# Create management scripts
create_management_scripts() {
    print_status "Creating management scripts..."
    
    local bin_dir="/usr/local/bin"
    
    # Service status script
    cat > "$bin_dir/auto-slopp-status" << EOF
#!/bin/bash
echo "Auto-slopp Service Status"
echo "========================="
systemctl status auto-slopp --no-pager
echo ""
echo "Recent logs:"
journalctl -u auto-slopp --since "1 hour ago" -n 20
EOF

    # Service restart script
    cat > "$bin_dir/auto-slopp-restart" << EOF
#!/bin/bash
echo "Restarting Auto-slopp service..."
sudo systemctl restart auto-slopp
echo "Service status after restart:"
systemctl status auto-slopp --no-pager
EOF

    # Service stop script
    cat > "$bin_dir/auto-slopp-stop" << EOF
#!/bin/bash
echo "Stopping Auto-slopp service..."
sudo systemctl stop auto-slopp
echo "Service status:"
systemctl status auto-slopp --no-pager
EOF

    # Service logs script
    cat > "$bin_dir/auto-slopp-logs" << EOF
#!/bin/bash
if [[ "\$1" == "-f" ]]; then
    echo "Following Auto-slopp logs (Ctrl+C to exit)..."
    sudo journalctl -u auto-slopp -f
else
    echo "Auto-slopp logs:"
    sudo journalctl -u auto-slopp --since "1 hour ago"
fi
EOF

    # Make scripts executable
    chmod +x "$bin_dir/auto-slopp-status"
    chmod +x "$bin_dir/auto-slopp-restart"
    chmod +x "$bin_dir/auto-slopp-stop"
    chmod +x "$bin_dir/auto-slopp-logs"
    
    print_status "Management scripts created in /usr/local/bin/"
}

# Show usage information
show_usage() {
    echo ""
    print_status "Auto-slopp service installation complete!"
    echo ""
    echo "Service Management Commands:"
    echo "  sudo systemctl status auto-slopp     # Check service status"
    echo "  sudo systemctl restart auto-slopp   # Restart service"
    echo "  sudo systemctl stop auto-slopp      # Stop service"
    echo "  sudo systemctl start auto-slopp     # Start service"
    echo "  sudo systemctl disable auto-slopp   # Disable on boot"
    echo ""
    echo "Convenience Scripts:"
    echo "  auto-slopp-status                  # Show status and recent logs"
    echo "  auto-slopp-restart                  # Restart service"
    echo "  auto-slopp-stop                     # Stop service"
    echo "  auto-slopp-logs [-f]                # View logs (add -f to follow)"
    echo ""
    echo "Log Commands:"
    echo "  journalctl -u auto-slopp -f         # Follow service logs"
    echo "  journalctl -u auto-slopp -b         # Logs since boot"
    echo "  journalctl -u auto-slopp --since '1 hour ago'  # Recent logs"
    echo ""
    echo "Configuration:"
    echo "  Service file: $SERVICE_FILE"
    echo "  Working directory: $AUTO_SLOPP_HOME"
    echo "  Config file: $AUTO_SLOPP_HOME/config.yaml"
    echo ""
    print_warning "Remember to reload configuration with: sudo systemctl reload auto-slopp"
}

# Uninstall function
uninstall_service() {
    print_status "Uninstalling Auto-slopp service..."
    
    # Stop and disable service
    systemctl stop "$SERVICE_NAME" 2>/dev/null || true
    systemctl disable "$SERVICE_NAME" 2>/dev/null || true
    
    # Remove service file
    if [[ -f "$SERVICE_FILE" ]]; then
        rm -f "$SERVICE_FILE"
        print_status "Removed service file: $SERVICE_FILE"
    fi
    
    # Remove logrotate config
    if [[ -f "/etc/logrotate.d/auto-slopp" ]]; then
        rm -f "/etc/logrotate.d/auto-slopp"
        print_status "Removed logrotate configuration"
    fi
    
    # Remove management scripts
    rm -f /usr/local/bin/auto-slopp-*
    print_status "Removed management scripts"
    
    # Reload systemd
    systemctl daemon-reload
    
    print_status "Auto-slopp service uninstalled successfully"
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

# Run main function
main "$@"