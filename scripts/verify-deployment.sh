#!/bin/bash

# Auto-slopp Deployment Verification Script
# Validates deployment and provides diagnostic information

# Set script name for logging identification
SCRIPT_NAME="verify-deployment"

# Load utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Set up error handling
setup_error_handling

# Colors for output
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Verification results
VERIFICATION_PASSED=true
WARNINGS=()
ERRORS=()

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "  Auto-slopp Deployment Verification"
    echo "=================================================="
    echo -e "${NC}"
}

print_section() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "  ${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "  ${YELLOW}⚠${NC} $1"
    WARNINGS+=("$1")
}

print_error() {
    echo -e "  ${RED}✗${NC} $1"
    ERRORS+=("$1")
    VERIFICATION_PASSED=false
}

# System verification
verify_system() {
    print_section "System Requirements"
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_success "Operating System: Linux (compatible)"
    else
        print_warning "Operating System: $OSTYPE (Linux recommended)"
    fi
    
    # Bash version
    local bash_version="${BASH_VERSION%%.*}"
    if [[ "$bash_version" -ge 4 ]]; then
        print_success "Bash Version: $BASH_VERSION"
    else
        print_error "Bash Version: $BASH_VERSION (4.0+ required)"
    fi
    
    # Memory
    local available_mem=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [[ "$available_mem" -ge 512 ]]; then
        print_success "Available Memory: ${available_mem}MB"
    else
        print_warning "Available Memory: ${available_mem}MB (1GB+ recommended)"
    fi
    
    # Disk space
    local available_space=$(df -BG "$HOME" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ "$available_space" -ge 1 ]]; then
        print_success "Available Disk Space: ${available_space}GB"
    else
        print_error "Available Disk Space: ${available_space}GB (1GB+ required)"
    fi
}

# Dependency verification
verify_dependencies() {
    print_section "Dependencies"
    
    local commands=("git" "curl" "jq" "opencode" "bd")
    local descriptions=("Git Version Control" "HTTP Client" "JSON Processor" "OpenCode CLI" "Beads CLI")
    
    for i in "${!commands[@]}"; do
        local cmd="${commands[$i]}"
        local desc="${descriptions[$i]}"
        
        if command -v "$cmd" >/dev/null 2>&1; then
            local version=$("$cmd" --version 2>/dev/null || "$cmd" version 2>/dev/null || echo "unknown")
            print_success "$desc: $version"
        else
            print_error "$desc: Not found"
        fi
    done
}

# Directory structure verification
verify_directories() {
    print_section "Directory Structure"
    
    # Try to load config to get paths
    local managed_repo_path="$HOME/git/managed"
    local managed_repo_task_path="$HOME/git/repo_task_path"
    local log_dir="$HOME/git/Auto-logs"
    
    # Load actual config if possible
    if [[ -f "$SCRIPT_DIR/../config.yaml" ]]; then
        if source "$SCRIPT_DIR/yaml_config.sh" 2>/dev/null && load_config "$SCRIPT_DIR/../config.yaml" 2>/dev/null; then
            managed_repo_path="${MANAGED_REPO_PATH:-$managed_repo_path}"
            managed_repo_task_path="${MANAGED_REPO_TASK_PATH:-$managed_repo_task_path}"
            log_dir="${LOG_DIRECTORY:-$log_dir}"
        fi
    fi
    
    local directories=(
        "$SCRIPT_DIR/..:Installation Directory"
        "$managed_repo_path:Managed Repositories"
        "$managed_repo_task_path:Task Files"
        "$log_dir:Log Files"
    )
    
    for dir_info in "${directories[@]}"; do
        local dir="${dir_info%:*}"
        local desc="${dir_info#*:}"
        
        if [[ -d "$dir" ]]; then
            local file_count=$(find "$dir" -maxdepth 1 -type f 2>/dev/null | wc -l)
            print_success "$desc: $dir ($file_count files)"
        else
            print_error "$desc: $dir (not found)"
        fi
    done
}

# Script permissions verification
verify_scripts() {
    print_section "Script Permissions"
    
    local scripts=(
        "$SCRIPT_DIR/../main.sh:Main Script"
        "$SCRIPT_DIR/../config.sh:Configuration Loader"
        "$SCRIPT_DIR/utils.sh:Utilities"
        "$SCRIPT_DIR/yaml_config.sh:YAML Configuration"
    )
    
    # Add all .sh files in scripts directory
    for script in "$SCRIPT_DIR"/*.sh; do
        if [[ -f "$script" ]]; then
            scripts+=("$script:$(basename "$script")")
        fi
    done
    
    # Add core scripts
    for script in "$SCRIPT_DIR/core"/*.sh; do
        if [[ -f "$script" ]]; then
            scripts+=("$script:core/$(basename "$script")")
        fi
    done
    
    for script_info in "${scripts[@]}"; do
        local script="${script_info%:*}"
        local desc="${script_info#*:}"
        
        if [[ -f "$script" ]]; then
            if [[ -x "$script" ]]; then
                print_success "$desc: Executable"
            else
                print_warning "$desc: Not executable"
            fi
        else
            print_warning "$desc: Not found"
        fi
    done
}

# Configuration verification
verify_configuration() {
    print_section "Configuration"
    
    local config_file="$SCRIPT_DIR/../config.yaml"
    
    if [[ -f "$config_file" ]]; then
        print_success "Configuration file exists: $config_file"
        
        # Validate YAML syntax
        if command -v python3 >/dev/null 2>&1; then
            if python3 -c "import yaml; yaml.safe_load(open('$config_file'))" 2>/dev/null; then
                print_success "YAML syntax: Valid"
            else
                print_error "YAML syntax: Invalid"
            fi
        else
            print_warning "YAML syntax: Cannot validate (python3 not available)"
        fi
        
        # Test configuration loading
        if source "$SCRIPT_DIR/yaml_config.sh" 2>/dev/null; then
            if load_config "$config_file" 2>/dev/null; then
                print_success "Configuration loading: Success"
                
                # Check key variables
                local key_vars=("SLEEP_DURATION" "MANAGED_REPO_PATH" "MANAGED_REPO_TASK_PATH" "LOG_DIRECTORY")
                for var in "${key_vars[@]}"; do
                    if [[ -n "${!var:-}" ]]; then
                        print_success "Variable $var: Set"
                    else
                        print_warning "Variable $var: Not set"
                    fi
                done
            else
                print_error "Configuration loading: Failed"
            fi
        else
            print_error "YAML config loader: Not found"
        fi
    else
        print_error "Configuration file: Not found"
    fi
}

# Environment verification
verify_environment() {
    print_section "Environment"
    
    # Check environment variables
    local env_vars=("AUTO_SLOPP_HOME" "AUTO_SLOPP_CONFIG" "DEBUG_MODE" "TELEGRAM_BOT_TOKEN")
    
    for var in "${env_vars[@]}"; do
        if [[ -n "${!var:-}" ]]; then
            if [[ "$var" == "TELEGRAM_BOT_TOKEN" ]]; then
                print_success "$var: Set (hidden for security)"
            else
                print_success "$var: ${!var}"
            fi
        else
            print_warning "$var: Not set"
        fi
    done
    
    # Check PATH includes auto-slopp
    if [[ ":$PATH:" == *":$SCRIPT_DIR/..:"* ]]; then
        print_success "PATH: Includes Auto-slopp directory"
    else
        print_warning "PATH: Does not include Auto-slopp directory"
    fi
}

# Service verification
verify_service() {
    print_section "System Service"
    
    if command -v systemctl >/dev/null 2>&1; then
        if systemctl list-unit-files | grep -q "auto-slopp.service"; then
            print_success "Service file: Installed"
            
            if systemctl is-enabled auto-slopp >/dev/null 2>&1; then
                print_success "Service: Enabled on boot"
            else
                print_warning "Service: Not enabled on boot"
            fi
            
            if systemctl is-active --quiet auto-slopp 2>/dev/null; then
                print_success "Service: Running"
            else
                print_warning "Service: Not running"
            fi
        else
            print_warning "Service: Not installed"
        fi
    else
        print_warning "systemctl: Not available (systemd not found)"
    fi
}

# Docker verification
verify_docker() {
    print_section "Docker (if applicable)"
    
    if command -v docker >/dev/null 2>&1; then
        print_success "Docker: Available"
        
        if docker info >/dev/null 2>&1; then
            print_success "Docker daemon: Running"
            
            # Check for Auto-slopp container/image
            if docker images | grep -q "auto-slopp"; then
                print_success "Docker image: Available"
            else
                print_warning "Docker image: Not found"
            fi
            
            if docker ps -a | grep -q "auto-slopp"; then
                print_success "Docker container: Created"
            else
                print_warning "Docker container: Not found"
            fi
        else
            print_warning "Docker daemon: Not running"
        fi
    else
        print_warning "Docker: Not installed"
    fi
}

# Functional testing
verify_functionality() {
    print_section "Functionality Tests"
    
    # Test basic utilities
    if source "$SCRIPT_DIR/utils.sh" 2>/dev/null; then
        print_success "Utils.sh: Loads successfully"
        
        # Test logging function
        if log "INFO" "Test message" 2>/dev/null; then
            print_success "Logging function: Works"
        else
            print_warning "Logging function: Issue detected"
        fi
    else
        print_error "Utils.sh: Failed to load"
    fi
    
    # Test number manager
    if "$SCRIPT_DIR/number_manager.sh" --help >/dev/null 2>&1; then
        print_success "Number manager: Available"
    else
        print_warning "Number manager: Not testable"
    fi
    
    # Test beads if available
    if command -v bd >/dev/null 2>&1; then
        if bd --version >/dev/null 2>&1; then
            print_success "Beads CLI: Functional"
        else
            print_warning "Beads CLI: Issue detected"
        fi
    fi
}

# Generate report
generate_report() {
    echo ""
    print_section "Verification Summary"
    
    echo "Results:"
    echo "  Total Checks: $((${#WARNINGS[@]} + ${#ERRORS[@]}))"
    echo "  Errors: ${#ERRORS[@]}"
    echo "  Warnings: ${#WARNINGS[@]}"
    echo ""
    
    if [[ ${#ERRORS[@]} -gt 0 ]]; then
        echo -e "${RED}Errors found:${NC}"
        for error in "${ERRORS[@]}"; do
            echo "  • $error"
        done
        echo ""
    fi
    
    if [[ ${#WARNINGS[@]} -gt 0 ]]; then
        echo -e "${YELLOW}Warnings:${NC}"
        for warning in "${WARNINGS[@]}"; do
            echo "  • $warning"
        done
        echo ""
    fi
    
    if [[ "$VERIFICATION_PASSED" == true ]]; then
        echo -e "${GREEN}✓ Deployment verification PASSED${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Add repositories to: $HOME/git/managed"
        echo "2. Run Auto-slopp: ./main.sh"
        echo "3. Monitor logs: tail -f $HOME/git/Auto-logs/\$(date +%Y-%m-%d).log"
    else
        echo -e "${RED}✗ Deployment verification FAILED${NC}"
        echo ""
        echo "Please resolve the errors above before running Auto-slopp."
        echo "For help, see: DEPLOYMENT.md"
    fi
}

# Main verification function
main() {
    print_header
    
    verify_system
    verify_dependencies
    verify_directories
    verify_scripts
    verify_configuration
    verify_environment
    verify_service
    verify_docker
    verify_functionality
    
    generate_report
    
    # Exit with appropriate code
    if [[ "$VERIFICATION_PASSED" == true ]]; then
        exit 0
    else
        exit 1
    fi
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Auto-slopp Deployment Verification Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --quiet        Suppress warnings, only show errors"
        echo ""
        exit 0
        ;;
    --quiet)
        # Suppress warnings (simple implementation)
        exec 1>/dev/null
        main
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac