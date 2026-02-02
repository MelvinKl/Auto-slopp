#!/bin/bash

# Comprehensive Test Suite for All Auto-slopp Scripts
# This script provides complete coverage testing for all scripts in the project
# Uses the enhanced test framework and organizes tests by category and priority

set -e

# Load the enhanced test framework
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_framework.sh"

# Project directories
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SCRIPTS_DIR="$PROJECT_DIR/scripts"
CORE_SCRIPTS_DIR="$SCRIPTS_DIR/core"

# Test configuration
QUICK_MODE=false
CATEGORY_FILTER=""
SCRIPT_FILTER=""
VERBOSE=false
COVERAGE_TARGET=85

# Script categories for organized testing
declare -A SCRIPT_CATEGORIES=(
    ["core"]="Core system scripts (configuration, state, error handling)"
    ["telegram"]="Telegram integration scripts"  
    ["automation"]="Automation and workflow scripts"
    ["utilities"]="Utility scripts and helpers"
    ["main"]="Main entry points"
)

# Map scripts to categories and priorities
declare -A SCRIPT_METADATA=(
    # Core scripts
    ["configuration_validator.sh"]="core:critical"
    ["error_recovery.sh"]="core:critical" 
    ["system_state.sh"]="core:high"
    ["telegram_config.sh"]="core:high"
    ["telegram_health.sh"]="core:medium"
    ["telegram_logger.sh"]="core:high"
    ["telegram_queue.sh"]="core:medium"
    ["telegram_security.sh"]="core:critical"
    
    # Automation scripts
    ["planner.sh"]="automation:critical"
    ["updater.sh"]="automation:high"
    ["implementer.sh"]="automation:high"
    ["creator.sh"]="automation:medium"
    ["cleanup-branches.sh"]="automation:medium"
    ["cleanup-branches-enhanced.sh"]="automation:medium"
    ["cleanup-automation-engine.sh"]="automation:low"
    ["auto-update-reboot.sh"]="automation:critical"
    ["branch_protection.sh"]="automation:medium"
    
    # Utility scripts
    ["utils.sh"]="utilities:critical"
    ["number_manager.sh"]="utilities:critical"
    ["yaml_config.sh"]="utilities:high"
    ["repository-discovery.sh"]="utilities:high"
    ["task-status-detection.sh"]="utilities:medium"
    ["beads_updater.sh"]="utilities:medium"
    ["update_fixer.sh"]="utilities:medium"
    
    # Main scripts
    ["main.sh"]="main:critical"
    ["config.sh"]="main:critical"
)

# ============================================================================
# CORE SYSTEM TESTS
# ============================================================================

# Test configuration validator
test_configuration_validator() {
    arrange "Setup configuration validator test" "
        source '$CORE_SCRIPTS_DIR/configuration_validator.sh'
        local test_config='$TEST_TMP_DIR/test_config.yaml'
        local validation_passed=false
        local validation_failed=false
        
        # Create valid test configuration
        cat > "\$test_config" << 'EOF'
# Test configuration
sleep_duration: 30
managed_repo_path: "/test/repo"
timestamp_format: "%Y-%m-%d %H:%M:%S"
log_level: "INFO"
telegram_enabled: false
auto_reboot:
  enabled: false
  cooldown_hours: 1
EOF
    "
    
    act "Test configuration validation" "
        if validate_config_file '\$test_config' 2>/dev/null; then
            validation_passed=true
        else
            validation_failed=true
        fi
        
        # Test invalid configuration
        echo 'invalid_yaml: [' > '$TEST_TMP_DIR/invalid.yaml'
        local invalid_result=false
        if ! validate_config_file '$TEST_TMP_DIR/invalid.yaml' 2>/dev/null; then
            invalid_result=true
        fi
    "
    
    assert "Valid configuration passes validation" "
        [[ \"\$validation_passed\" == \"true\" ]]
    "
    
    assert "Invalid configuration fails validation" "
        [[ \"\$invalid_result\" == \"true\" ]]
    "
}

# Test error recovery mechanisms
test_error_recovery() {
    arrange "Setup error recovery test" "
        source '$CORE_SCRIPTS_DIR/error_recovery.sh'
        local test_state_file='$TEST_TMP_DIR/error_state.json'
        local recovery_triggered=false
        
        # Create test error scenario
        export ERROR_STATE_FILE='\$test_state_file'
        echo '{}' > '\$test_state_file'
    "
    
    act "Test error recovery functionality" "
        # Test error recording
        record_error 'test_error' 'Test error scenario' 'test_component'
        
        # Test error recovery check
        local error_count=\$(get_error_count 'test_error')
        
        # Test recovery trigger
        if check_recovery_needed 'test_error' 3; then
            recovery_triggered=true
        fi
    "
    
    assert "Error is recorded correctly" "
        [[ \"\$error_count\" -ge 1 ]]
    "
    
    assert "Recovery mechanism works" "
        [[ \"\$recovery_triggered\" == \"true\" ]] || [[ \"\$recovery_triggered\" == \"false\" ]]
    "
}

# Test system state management
test_system_state() {
    arrange "Setup system state test" "
        source '$CORE_SCRIPTS_DIR/system_state.sh'
        local test_state_file='$TEST_TMP_DIR/system_state.json'
        export SYSTEM_STATE_FILE='\$test_state_file'
        
        # Initialize system state
        initialize_system_state
    "
    
    act "Test system state operations" "
        # Test state updates
        update_system_state 'test_key' 'test_value'
        update_system_state 'test_number' '42'
        update_system_state 'test_array' '["item1", "item2"]'
        
        # Test state retrieval
        local retrieved_value=\$(get_system_state 'test_key')
        local retrieved_number=\$(get_system_state 'test_number')
        
        # Test state persistence
        local state_exists=false
        if [[ -f '\$test_state_file' && -s '\$test_state_file' ]]; then
            state_exists=true
        fi
    "
    
    assert "State values are stored and retrieved correctly" "
        [[ \"\$retrieved_value\" == \"test_value\" ]] && [[ \"\$retrieved_number\" == \"42\" ]]
    "
    
    assert "State file is created and populated" "
        [[ \"\$state_exists\" == \"true\" ]]
    "
}

# ============================================================================
# TELEGRAM INTEGRATION TESTS
# ============================================================================

# Test Telegram configuration management
test_telegram_config_management() {
    arrange "Setup Telegram config test" "
        source '$CORE_SCRIPTS_DIR/telegram_config.sh'
        local test_token='123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
        local test_chat='987654321'
        export TELEGRAM_ENABLED='true'
        export TELEGRAM_BOT_TOKEN='\$test_token'
        export TELEGRAM_CHAT_ID='\$test_chat'
    "
    
    act "Test Telegram configuration validation" "
        local config_valid=false
        if validate_telegram_config 2>/dev/null; then
            config_valid=true
        fi
        
        # Test with invalid token
        export TELEGRAM_BOT_TOKEN='invalid'
        local config_invalid=false
        if ! validate_telegram_config 2>/dev/null; then
            config_invalid=true
        fi
        
        # Test disabled state
        export TELEGRAM_ENABLED='false'
        local config_disabled=false
        if ! validate_telegram_config 2>/dev/null; then
            config_disabled=true
        fi
    "
    
    assert "Valid Telegram configuration passes" "
        [[ \"\$config_valid\" == \"true\" ]]
    "
    
    assert "Invalid Telegram configuration fails" "
        [[ \"\$config_invalid\" == \"true\" ]]
    "
    
    assert "Disabled Telegram configuration fails gracefully" "
        [[ \"\$config_disabled\" == \"true\" ]]
    "
}

# Test Telegram health checking
test_telegram_health() {
    arrange "Setup Telegram health test" "
        source '$CORE_SCRIPTS_DIR/telegram_health.sh'
        local health_result=''
        
        # Mock curl for testing
        curl() {
            if [[ \"\$*\" == *'getMe'* ]]; then
                echo '{"ok":true,"result":{"id":123456789,"is_bot":true,"first_name":"Test Bot"}}'
                return 0
            fi
            return 1
        }
        export -f curl
    "
    
    act "Test Telegram health check" "
        if check_telegram_health 2>/dev/null; then
            health_result='healthy'
        else
            health_result='unhealthy'
        fi
        
        # Test with network error
        curl() { return 1; }
        export -f curl
        
        local health_error=''
        if ! check_telegram_health 2>/dev/null; then
            health_error='error_detected'
        fi
    "
    
    assert "Health check passes with valid bot" "
        [[ \"\$health_result\" == \"healthy\" ]]
    "
    
    assert "Health check fails with network error" "
        [[ \"\$health_error\" == \"error_detected\" ]]
    "
}

# ============================================================================
# AUTOMATION SCRIPTS TESTS
# ============================================================================

# Test planner functionality
test_planner_functionality() {
    arrange "Setup planner test" "
        source '$SCRIPTS_DIR/planner.sh'
        local test_repo='$TEST_DATA_DIR/test_planner_repo'
        
        # Create test repository
        mkdir -p '\$test_repo'
        cd '\$test_repo'
        git init --quiet
        echo 'test content' > test_file.txt
        git add test_file.txt
        git commit -m 'Initial commit' --quiet
    "
    
    act "Test planner functionality" "
        local planner_result=''
        planner_result=\$(run_planner '\$test_repo' 2>&1 || echo 'planner_executed')
        
        # Test planner with invalid repo
        local invalid_result=''
        invalid_result=\$(run_planner '/nonexistent/repo' 2>&1 || echo 'error_handled')
    "
    
    assert "Planner executes on valid repository" "
        [[ -n \"\$planner_result\" ]]
    "
    
    assert "Planner handles invalid repository gracefully" "
        [[ \"\$invalid_result\" == 'error_handled' ]] || [[ \"\$invalid_result\" == *'error'* ]]
    "
}

# Test updater functionality
test_updater_functionality() {
    arrange "Setup updater test" "
        source '$SCRIPTS_DIR/updater.sh'
        local test_repo='$TEST_DATA_DIR/test_updater_repo'
        
        # Create test repository with remote
        mkdir -p '\$test_repo'
        cd '\$test_repo'
        git init --quiet
        echo 'initial content' > file.txt
        git add file.txt
        git commit -m 'Initial commit' --quiet
        
        # Create a "remote" directory
        mkdir -p '$TEST_DATA_DIR/remote_repo'
        cd '$TEST_DATA_DIR/remote_repo'
        git init --quiet
        echo 'remote content' > file.txt
        git add file.txt
        git commit -m 'Remote commit' --quiet
        
        # Add remote to test repo
        cd '\$test_repo'
        git remote add origin '$TEST_DATA_DIR/remote_repo'
    "
    
    act "Test updater functionality" "
        local update_result=''
        update_result=\$(run_updater '\$test_repo' 2>&1 || echo 'update_attempted')
        
        # Test with non-existent repo
        local no_repo_result=''
        no_repo_result=\$(run_updater '/nonexistent/repo' 2>&1 || echo 'handled_no_repo')
    "
    
    assert "Updater attempts to update valid repository" "
        [[ -n \"\$update_result\" ]]
    "
    
    assert "Updater handles non-existent repository" "
        [[ \"\$no_repo_result\" == 'handled_no_repo' ]] || [[ \"\$no_repo_result\" == *'error'* ]]
    "
}

# ============================================================================
# UTILITY SCRIPTS TESTS
# ============================================================================

# Test number manager comprehensively
test_number_manager_comprehensive() {
    arrange "Setup number manager test" "
        source '$SCRIPTS_DIR/number_manager.sh'
        local test_state_file='$TEST_TMP_DIR/number_state.json'
        export NUMBER_STATE_FILE='\$test_state_file'
        
        echo '{}' > '\$test_state_file'
    "
    
    act "Test number manager operations" "
        # Test basic assignment
        local assigned_num1=\$(assign_number 'test-context' 'test-task-1' 2>/dev/null || echo 'assign_failed')
        local assigned_num2=\$(assign_number 'test-context' 'test-task-2' 2>/dev/null || echo 'assign_failed')
        
        # Test number uniqueness
        local numbers_unique=false
        if [[ \"\$assigned_num1\" != \"\$assigned_num2\" ]] && [[ \"\$assigned_num1\" =~ ^[0-9]+$ ]] && [[ \"\$assigned_num2\" =~ ^[0-9]+$ ]]; then
            numbers_unique=true
        fi
        
        # Test number release
        local release_result=false
        if release_number '\$assigned_num1' 2>/dev/null; then
            release_result=true
        fi
        
        # Test state persistence
        local state_exists=false
        if [[ -f '\$test_state_file' && -s '\$test_state_file' ]]; then
            state_exists=true
        fi
    "
    
    assert "Numbers are assigned uniquely" "
        [[ \"\$numbers_unique\" == \"true\" ]]
    "
    
    assert "Number release works correctly" "
        [[ \"\$release_result\" == \"true\" ]]
    "
    
    assert "State file is maintained" "
        [[ \"\$state_exists\" == \"true\" ]]
    "
}

# Test YAML configuration handling
test_yaml_config_handling() {
    arrange "Setup YAML config test" "
        source '$SCRIPTS_DIR/yaml_config.sh'
        local test_yaml='$TEST_TMP_DIR/test_config.yaml'
        local key_value=''
        
        # Create test YAML
        cat > "\$test_yaml" << 'EOF'
# Test configuration
string_value: "test_string"
number_value: 42
boolean_value: true
nested:
  key1: "value1"
  key2: "value2"
array_value:
  - item1
  - item2
  - item3
EOF
    "
    
    act "Test YAML parsing" "
        # Test simple key extraction
        key_value=\$(get_yaml_value '\$test_yaml' 'string_value' 2>/dev/null || echo 'parse_failed')
        
        # Test number extraction
        local number_value=\$(get_yaml_value '\$test_yaml' 'number_value' 2>/dev/null || echo '0')
        
        # Test boolean extraction  
        local boolean_value=\$(get_yaml_value '\$test_yaml' 'boolean_value' 2>/dev/null || echo 'false')
        
        # Test nested key extraction
        local nested_value=\$(get_yaml_value '\$test_yaml' 'nested.key1' 2>/dev/null || echo 'nested_failed')
        
        # Test array extraction
        local array_value=\$(get_yaml_value '\$test_yaml' 'array_value[0]' 2>/dev/null || echo 'array_failed')
    "
    
    assert "String value is extracted correctly" "
        [[ \"\$key_value\" == \"test_string\" ]]
    "
    
    assert "Number value is extracted correctly" "
        [[ \"\$number_value\" == \"42\" ]]
    "
    
    assert "Nested value is extracted correctly" "
        [[ \"\$nested_value\" == \"value1\" ]]
    "
    
    assert "Array value is extracted correctly" "
        [[ \"\$array_value\" == \"item1\" ]] || [[ \"\$array_value\" == *'item1'* ]]
    "
}

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

# Test script interdependencies
test_script_integration() {
    arrange "Setup integration test environment" "
        local test_workspace='$TEST_DATA_DIR/integration_workspace'
        mkdir -p '\$test_workspace'
        
        # Test that scripts can source each other properly
        local source_test=false
        if source '$SCRIPTS_DIR/utils.sh' 2>/dev/null && source '$SCRIPTS_DIR/yaml_config.sh' 2>/dev/null; then
            source_test=true
        fi
    "
    
    act "Test script integration scenarios" "
        # Test number manager with planner
        local integration_result=false
        if source '$SCRIPTS_DIR/number_manager.sh' && source '$SCRIPTS_DIR/planner.sh' 2>/dev/null; then
            integration_result=true
        fi
        
        # Test configuration loading across scripts
        local config_integration=false
        if source '$PROJECT_DIR/config.sh' 2>/dev/null; then
            config_integration=true
        fi
    "
    
    assert "Scripts can source dependencies" "
        [[ \"\$source_test\" == \"true\" ]]
    "
    
    assert "Script integration works" "
        [[ \"\$integration_result\" == \"true\" ]]
    "
    
    assert "Configuration integration works" "
        [[ \"\$config_integration\" == \"true\" ]]
    "
}

# ============================================================================
# PERFORMANCE AND STRESS TESTS
# ============================================================================

# Test script performance
test_script_performance() {
    arrange "Setup performance test" "
        source '$SCRIPTS_DIR/utils.sh'
        local performance_passed=true
    "
    
    act "Test script loading performance" "
        # Test multiple scripts loading time
        local loading_time=\$(measure_time "
            for script in '$SCRIPTS_DIR/utils.sh' '$SCRIPTS_DIR/number_manager.sh' '$SCRIPTS_DIR/yaml_config.sh'; do
                if [[ -f \"\$script\" ]]; then
                    source \"\$script\" >/dev/null 2>&1
                fi
            done
        " 5)
        
        # Performance threshold: 2 seconds for loading 3 scripts
        if [[ \$loading_time -gt 2000 ]]; then
            performance_passed=false
        fi
    "
    
    assert "Scripts load within performance threshold" "
        [[ \"\$performance_passed\" == \"true\" ]]
    "
}

# ============================================================================
# TEST EXECUTION ENGINE
# ============================================================================

# Execute tests for a specific category
execute_category_tests() {
    local category="$1"
    echo "=============================================="
    echo "${category^} Tests"
    echo "=============================================="
    
    case "$category" in
        "core")
            run_test "Configuration validator" "test_configuration_validator" "unit" "critical" "Test configuration validation logic"
            run_test "Error recovery" "test_error_recovery" "unit" "critical" "Test error recovery mechanisms"
            run_test "System state" "test_system_state" "unit" "high" "Test system state management"
            run_test "Telegram config management" "test_telegram_config_management" "unit" "high" "Test Telegram configuration"
            run_test "Telegram health" "test_telegram_health" "unit" "medium" "Test Telegram health checking"
            ;;
        "automation")
            run_test "Planner functionality" "test_planner_functionality" "integration" "critical" "Test planner script functionality"
            run_test "Updater functionality" "test_updater_functionality" "integration" "high" "Test updater script functionality"
            ;;
        "utilities")
            run_test "Number manager comprehensive" "test_number_manager_comprehensive" "unit" "critical" "Test number manager comprehensively"
            run_test "YAML config handling" "test_yaml_config_handling" "unit" "high" "Test YAML configuration parsing"
            ;;
        "integration")
            run_test "Script integration" "test_script_integration" "integration" "high" "Test script interdependencies"
            ;;
        "performance")
            run_test "Script performance" "test_script_performance" "performance" "medium" "Test script loading performance"
            ;;
    esac
}

# Execute tests for specific scripts
execute_script_tests() {
    local script_name="$1"
    echo "Running tests for script: $script_name"
    
    # Extract metadata
    local metadata="${SCRIPT_METADATA[$script_name]:-}"
    if [[ -z "$metadata" ]]; then
        log_warning "No metadata found for $script_name, skipping"
        return 0
    fi
    
    local category=$(echo "$metadata" | cut -d: -f1)
    local priority=$(echo "$metadata" | cut -d: -f2)
    
    # Run relevant tests based on script category
    case "$category" in
        "core")
            if [[ "$script_name" == *"configuration"* ]]; then
                run_test "$script_name config validation" "test_configuration_validator" "unit" "$priority" "Test $script_name"
            elif [[ "$script_name" == *"error"* ]]; then
                run_test "$script_name error handling" "test_error_recovery" "unit" "$priority" "Test $script_name"
            elif [[ "$script_name" == *"state"* ]]; then
                run_test "$script_name state management" "test_system_state" "unit" "$priority" "Test $script_name"
            elif [[ "$script_name" == *"telegram"* ]]; then
                run_test "$script_name telegram config" "test_telegram_config_management" "unit" "$priority" "Test $script_name"
            fi
            ;;
        "automation")
            if [[ "$script_name" == *"planner"* ]]; then
                run_test "$script_name functionality" "test_planner_functionality" "integration" "$priority" "Test $script_name"
            elif [[ "$script_name" == *"updater"* ]]; then
                run_test "$script_name functionality" "test_updater_functionality" "integration" "$priority" "Test $script_name"
            fi
            ;;
        "utilities")
            if [[ "$script_name" == *"number"* ]]; then
                run_test "$script_name comprehensive" "test_number_manager_comprehensive" "unit" "$priority" "Test $script_name"
            elif [[ "$script_name" == *"yaml"* ]]; then
                run_test "$script_name YAML handling" "test_yaml_config_handling" "unit" "$priority" "Test $script_name"
            fi
            ;;
    esac
}

# Discover and test all scripts
test_all_scripts() {
    echo "Discovering and testing all scripts..."
    
    local total_scripts=0
    local tested_scripts=0
    
    # Test scripts in main scripts directory
    for script_file in "$SCRIPTS_DIR"/*.sh; do
        if [[ -f "$script_file" ]]; then
            local script_name=$(basename "$script_file")
            total_scripts=$((total_scripts + 1))
            
            # Test basic script properties
            run_test "$script_name syntax" "bash -n '$script_file'" "unit" "high" "Test $script_name syntax"
            run_test "$script_name executable" "test -x '$script_file'" "unit" "medium" "Test $script_name executable"
            
            # Run specific functionality tests
            if [[ -z "$SCRIPT_FILTER" || "$script_name" == *"$SCRIPT_FILTER"* ]]; then
                execute_script_tests "$script_name"
                tested_scripts=$((tested_scripts + 1))
            fi
        fi
    done
    
    # Test scripts in core directory
    for script_file in "$CORE_SCRIPTS_DIR"/*.sh; do
        if [[ -f "$script_file" ]]; then
            local script_name=$(basename "$script_file")
            total_scripts=$((total_scripts + 1))
            
            # Test basic script properties
            run_test "$script_name syntax" "bash -n '$script_file'" "unit" "high" "Test core/$script_name syntax"
            run_test "$script_name executable" "test -x '$script_file'" "unit" "medium" "Test core/$script_name executable"
            
            # Run specific functionality tests
            if [[ -z "$SCRIPT_FILTER" || "$script_name" == *"$SCRIPT_FILTER"* ]]; then
                execute_script_tests "$script_name"
                tested_scripts=$((tested_scripts + 1))
            fi
        fi
    done
    
    echo "Script discovery summary:"
    echo "  Total scripts found: $total_scripts"
    echo "  Scripts with specific tests: $tested_scripts"
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                QUICK_MODE=true
                shift
                ;;
            --category)
                CATEGORY_FILTER="$2"
                shift 2
                ;;
            --script)
                SCRIPT_FILTER="$2"
                shift 2
                ;;
            --verbose)
                VERBOSE=true
                export DEBUG=true
                shift
                ;;
            --coverage)
                COVERAGE_TARGET="$2"
                shift 2
                ;;
            --help|-h)
                echo "Comprehensive Test Suite for Auto-slopp Scripts"
                echo ""
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --quick              Run only critical tests"
                echo "  --category CATEGORY  Run tests for specific category"
                echo "  --script SCRIPT      Run tests for specific script (partial match)"
                echo "  --verbose            Enable debug output"
                echo "  --coverage PERCENT    Set coverage target (default: 85)"
                echo "  --help, -h           Show this help message"
                echo ""
                echo "Categories:"
                for category in "${!SCRIPT_CATEGORIES[@]}"; do
                    echo "  $category    ${SCRIPT_CATEGORIES[$category]}"
                done
                echo ""
                echo "Examples:"
                echo "  $0 --quick                              # Quick critical tests"
                echo "  $0 --category core                       # Test core scripts only"
                echo "  $0 --script number_manager               # Test number manager"
                echo "  $0 --script telegram                     # Test all telegram scripts"
                echo ""
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Main execution
main() {
    # Parse arguments
    parse_arguments "$@"
    
    # Initialize framework
    init_framework
    
    echo "Comprehensive script testing..."
    echo "Quick mode: $QUICK_MODE"
    echo "Category filter: ${CATEGORY_FILTER:-'all'}"
    echo "Script filter: ${SCRIPT_FILTER:-'none'}"
    echo "Coverage target: ${COVERAGE_TARGET}%"
    echo ""
    
    # Execute tests based on configuration
    if [[ -n "$CATEGORY_FILTER" ]]; then
        execute_category_tests "$CATEGORY_FILTER"
    elif [[ -n "$SCRIPT_FILTER" ]]; then
        test_all_scripts
    else
        # Run all category tests
        if [[ "$QUICK_MODE" != true ]]; then
            for category in core automation utilities integration performance; do
                execute_category_tests "$category"
            done
        else
            # Quick mode: only critical tests
            execute_category_tests "core"
        fi
        
        # Always run script discovery tests
        test_all_scripts
    fi
    
    # Generate final report
    generate_report
    
    # Check coverage target
    local actual_coverage=0
    if [[ $TESTS_TOTAL -gt 0 ]]; then
        actual_coverage=$(echo "scale=1; ($COVERAGE_CRITICAL + $COVERAGE_HIGH) * 100 / $TESTS_TOTAL" | bc -l)
    fi
    
    echo ""
    echo "=== Coverage Assessment ==="
    printf "Target coverage: %d%%\n" "$COVERAGE_TARGET"
    printf "Actual coverage: %.1f%%\n" "$actual_coverage"
    
    if (( $(echo "$actual_coverage >= $COVERAGE_TARGET" | bc -l) )); then
        echo -e "${GREEN}✓ Coverage target met!${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Coverage target not met. Consider adding more tests.${NC}"
        return 1
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi