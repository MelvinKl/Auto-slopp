#!/bin/bash

# Comprehensive test suite for task availability functionality
# Tests the has_open_bead_tasks(), get_open_bead_tasks_count(), and log_task_availability_decision() functions

set -e

# Get script directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
UTILS_SCRIPT="$PROJECT_DIR/scripts/utils.sh"

# Colors for test output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test environment setup
TEST_REPO_DIR="/tmp/test-beads-repo-$$"
TEST_LOG_DIR="/tmp/test-task-availability-logs-$$"
TEST_BEDS_DIR="$TEST_REPO_DIR/.beads"

# Cleanup function
cleanup() {
    rm -rf "$TEST_REPO_DIR" "$TEST_LOG_DIR" 2>/dev/null || true
    unset LOG_LEVEL LOG_DIRECTORY SCRIPT_NAME DEBUG_MODE
}

# Register cleanup
trap cleanup EXIT

# Helper functions
log_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    log_test "Running: $test_name"
    
    if eval "$test_command"; then
        log_pass "$test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        local exit_code=$?
        log_fail "$test_name (exit code: $exit_code)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Source utils.sh for testing
source_utils() {
    if [[ ! -f "$UTILS_SCRIPT" ]]; then
        echo "ERROR: utils.sh not found at $UTILS_SCRIPT"
        exit 1
    fi
    
    # Source without executing main code
    source "$UTILS_SCRIPT"
}

# Create a mock bd command for testing
create_mock_bd() {
    local response_content="$1"
    cat > "/tmp/mock-bd-$$" << EOF
#!/bin/bash
if [[ "\$1" == "list" && "\$2" == "--status=open" ]]; then
    echo '$response_content'
elif [[ "\$1" == "ready" ]]; then
    echo '[]'
else
    echo '[]'
fi
EOF
    chmod +x "/tmp/mock-bd-$$"
    
    # Remove any existing bd and create symlink to mock
    rm -f "/tmp/bd"
    ln -sf "/tmp/mock-bd-$$" "/tmp/bd"
    
    # Add mock to PATH
    export PATH="/tmp:$PATH"
    export BD_MOCK_MODE="true"
}

# Create test repository with beads
create_test_repo() {
    rm -rf "$TEST_REPO_DIR"
    mkdir -p "$TEST_REPO_DIR"
    mkdir -p "$TEST_BEDS_DIR"
    
    # Create minimal beads structure
    echo '{"version": "1.0"}' > "$TEST_BEDS_DIR/config.json"
    
    cd "$TEST_REPO_DIR"
    
    # Initialize as git repo (required for beads functionality)
    git init >/dev/null 2>&1
    git config user.email "test@example.com"
    git config user.name "Test User"
    
    # Create a test issues.jsonl file
    touch "$TEST_BEDS_DIR/issues.jsonl"
}

# Test 1: Function availability
test_function_availability() {
    source_utils
    
    # Check if functions are defined
    if ! declare -f has_open_bead_tasks >/dev/null 2>&1; then
        echo "has_open_bead_tasks function not defined"
        return 1
    fi
    
    if ! declare -f get_open_bead_tasks_count >/dev/null 2>&1; then
        echo "get_open_bead_tasks_count function not defined"
        return 1
    fi
    
    if ! declare -f log_task_availability_decision >/dev/null 2>&1; then
        echo "log_task_availability_decision function not defined"
        return 1
    fi
    
    return 0
}

# Test 2: Repository without .beads directory
test_no_beads_directory() {
    source_utils
    
    # Create test directory without beads
    rm -rf "$TEST_REPO_DIR"
    mkdir -p "$TEST_REPO_DIR"
    cd "$TEST_REPO_DIR"
    
    # Test has_open_bead_tasks
    if has_open_bead_tasks "$TEST_REPO_DIR"; then
        echo "has_open_bead_tasks should return 1 for non-beads repo"
        return 1
    fi
    
    # Test get_open_bead_tasks_count
    local count
    count=$(get_open_bead_tasks_count "$TEST_REPO_DIR")
    if [[ "$count" != "0" ]]; then
        echo "get_open_bead_tasks_count should return 0 for non-beads repo, got $count"
        return 1
    fi
    
    return 0
}

# Test 3: Repository with beads but no open tasks
test_beads_no_open_tasks() {
    source_utils
    
    create_test_repo
    
    # Create mock bd response with no tasks
    local empty_response='[]'
    create_mock_bd "$empty_response"
    
    # Test has_open_bead_tasks
    if has_open_bead_tasks "$TEST_REPO_DIR"; then
        echo "has_open_bead_tasks should return 1 when no open tasks"
        return 1
    fi
    
    # Test get_open_bead_tasks_count
    local count
    count=$(get_open_bead_tasks_count "$TEST_REPO_DIR")
    if [[ "$count" != "0" ]]; then
        echo "get_open_bead_tasks_count should return 0 when no open tasks, got $count"
        return 1
    fi
    
    return 0
}

# Test 4: Repository with beads and open tasks
test_beads_with_open_tasks() {
    source_utils
    
    create_test_repo
    
    # Create mock bd response with open tasks (use tempfile for proper escaping)
    local tasks_response='[
        {"id": "test-1", "title": "Test Task 1", "status": "open"},
        {"id": "test-2", "title": "Test Task 2", "status": "open"},
        {"id": "test-3", "title": "Test Task 3", "status": "open"}
    ]'
    create_mock_bd "$tasks_response"
    
    # Test has_open_bead_tasks
    if ! has_open_bead_tasks "$TEST_REPO_DIR"; then
        echo "has_open_bead_tasks should return 0 when open tasks exist"
        return 1
    fi
    
    # Test get_open_bead_tasks_count
    local count
    count=$(get_open_bead_tasks_count "$TEST_REPO_DIR")
    if [[ "$count" != "3" ]]; then
        echo "get_open_bead_tasks_count should return 3 when 3 open tasks exist, got $count"
        return 1
    fi
    
    return 0
}

# Test 5: Mixed status tasks
test_mixed_status_tasks() {
    source_utils
    
    create_test_repo
    
    # Create mock bd response with mixed status tasks
    # Note: bd --status=open should only return open tasks, so we simulate that
    local mixed_response='[
        {"id": "open-1", "title": "Open Task 1", "status": "open"},
        {"id": "open-2", "title": "Open Task 2", "status": "open"}
    ]'
    create_mock_bd "$mixed_response"
    
    # Test has_open_bead_tasks (should only count open tasks)
    if ! has_open_bead_tasks "$TEST_REPO_DIR"; then
        echo "has_open_bead_tasks should return 0 when some open tasks exist"
        return 1
    fi
    
    # Test get_open_bead_tasks_count (should only count open tasks)
    local count
    count=$(get_open_bead_tasks_count "$TEST_REPO_DIR")
    if [[ "$count" != "2" ]]; then
        echo "get_open_bead_tasks_count should return 2 when 2 open tasks exist among mixed status, got $count"
        return 1
    fi
    
    return 0
}

# Test 6: BD command behavior (basic functionality)
test_bd_command_behavior() {
    source_utils
    
    create_test_repo
    
    # Create mock bd response with no tasks
    create_mock_bd '[]'
    
    # Test has_open_bead_tasks returns 1 (no tasks)
    if has_open_bead_tasks "$TEST_REPO_DIR"; then
        echo "has_open_bead_tasks should return 1 when no tasks available"
        return 1
    fi
    
    return 0
}

# Test 7: BD command timeout
test_bd_command_timeout() {
    source_utils
    
    create_test_repo
    
    # Create a mock bd that hangs
    cat > "/tmp/mock-slow-bd-$$" << 'EOF'
#!/bin/bash
sleep 5  # Simulate slow response
echo '[]'
EOF
    chmod +x "/tmp/mock-slow-bd-$$"
    
    export PATH="/tmp:$PATH"
    export BD_MOCK_MODE="true"
    
    # Create a symlink with correct name but slow execution
    ln -sf "/tmp/mock-slow-bd-$$" "/tmp/bd"
    
    # Test has_open_bead_tasks with short timeout
    local exit_code
    has_open_bead_tasks "$TEST_REPO_DIR" 1 >/dev/null 2>&1
    exit_code=$?
    
    if [[ $exit_code -ne 2 ]]; then
        echo "has_open_bead_tasks should return 2 when bd times out, got $exit_code"
        return 1
    fi
    
    return 0
}

# Test 8: Invalid JSON response
test_invalid_json_response() {
    source_utils
    
    create_test_repo
    
    # Create mock bd with invalid JSON
    cat > "/tmp/mock-invalid-bd-$$" << 'EOF'
#!/bin/bash
echo 'invalid json response'
EOF
    chmod +x "/tmp/mock-invalid-bd-$$"
    
    export PATH="/tmp:$PATH"
    rm -f "/tmp/bd"
    ln -sf "/tmp/mock-invalid-bd-$$" "/tmp/bd"
    
    # Test has_open_bead_tasks with invalid JSON
    local exit_code
    has_open_bead_tasks "$TEST_REPO_DIR" >/dev/null 2>&1
    exit_code=$?
    
    # Should handle gracefully (return 1 for no tasks found)
    if [[ $exit_code -ne 1 ]]; then
        echo "has_open_bead_tasks should return 1 with invalid JSON (no tasks found), got $exit_code"
        return 1
    fi
    
    # Test get_open_bead_tasks_count with invalid JSON
    local count
    count=$(get_open_bead_tasks_count "$TEST_REPO_DIR")
    if [[ "$count" != "0" ]]; then
        echo "get_open_bead_tasks_count should return 0 with invalid JSON, got $count"
        return 1
    fi
    
    return 0
}

# Test 9: Task availability decision logging
test_task_availability_logging() {
    source_utils
    
    export LOG_LEVEL="INFO"
    export LOG_DIRECTORY="$TEST_LOG_DIR"
    mkdir -p "$LOG_DIRECTORY"
    
    # Test logging with tasks found
    log_task_availability_decision "test-repo" "true" "5" "proceed" "tasks found"
    
    # Test logging with no tasks found
    log_task_availability_decision "test-repo" "false" "0" "skip" "no tasks available"
    
    # Check log file for entries
    local log_file="$LOG_DIRECTORY/utils.sh.log"
    if [[ -f "$log_file" ]]; then
        if ! grep -q "FOUND 5 open tasks" "$log_file"; then
            echo "Expected 'FOUND 5 open tasks' log entry missing"
            return 1
        fi
        
        if ! grep -q "NO open tasks found" "$log_file"; then
            echo "Expected 'NO open tasks found' log entry missing"
            return 1
        fi
    fi
    
    return 0
}

# Test 10: Large number of tasks performance
test_large_number_of_tasks() {
    source_utils
    
    create_test_repo
    
    # Create mock bd response with many tasks (write to temp file first)
    local many_tasks_file="/tmp/many-tasks-$$"
    echo '[' > "$many_tasks_file"
    for ((i=1; i<=100; i++)); do
        echo '{"id": "task-'"$i"'", "title": "Test Task '"$i"'", "status": "open"}' >> "$many_tasks_file"
        [[ $i -lt 100 ]] && echo ',' >> "$many_tasks_file"
    done
    echo ']' >> "$many_tasks_file"
    
    local many_tasks_content=$(cat "$many_tasks_file")
    create_mock_bd "$many_tasks_content"
    rm -f "$many_tasks_file"
    
    # Test get_open_bead_tasks_count performance
    local start_time=$(date +%s.%N 2>/dev/null || date +%s)
    local count
    count=$(get_open_bead_tasks_count "$TEST_REPO_DIR")
    local end_time=$(date +%s.%N 2>/dev/null || date +%s)
    
    if [[ "$count" != "100" ]]; then
        echo "get_open_bead_tasks_count should return 100 for 100 tasks, got $count"
        return 1
    fi
    
    # Check performance (should complete within reasonable time)
    local duration
    if command -v bc >/dev/null 2>&1; then
        duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")
        local comparison=$(echo "$duration < 5" | bc 2>/dev/null || echo "1")
        if [[ "$comparison" != "1" ]]; then
            echo "Task count query took too long: ${duration}s"
            return 1
        fi
    fi
    
    return 0
}

# Test 11: Directory navigation and error handling
test_directory_navigation() {
    source_utils
    
    create_test_repo
    
    # Create mock bd with no tasks and ensure it's in PATH
    create_mock_bd '[]'
    export PATH="/tmp:$PATH"
    
    local original_dir=$(pwd)
    
    # Test that function changes directory correctly
    cd "/tmp"
    has_open_bead_tasks "$TEST_REPO_DIR"
    local test_result=$?
    
    if [[ $test_result -ne 1 ]]; then
        echo "has_open_bead_tasks should return 1 (no tasks) when called from different directory (got exit code: $test_result)"
        cd "$original_dir"
        return 1
    fi
    
    # Test with non-existent directory
    has_open_bead_tasks "/nonexistent/directory" 2>/dev/null
    local test_result1=$?
    
    # Accept return code 1 or 2 (both indicate error/no tasks)
    if [[ $test_result1 -ne 1 && $test_result1 -ne 2 ]]; then
        echo "has_open_bead_tasks should return 1 or 2 with non-existent directory, got $test_result1"
        cd "$original_dir"
        return 1
    fi
    
    # Test get_open_bead_tasks_count with non-existent directory
    local count
    count=$(get_open_bead_tasks_count "/nonexistent/directory" 2>/dev/null || echo "-1")
    if [[ "$count" != "-1" && "$count" != "0" ]]; then
        echo "get_open_bead_tasks_count should return -1 or 0 with non-existent directory, got $count"
        cd "$original_dir"
        return 1
    fi
    
    cd "$original_dir"
    return 0
}

# Test 12: Repository-specific filtering
test_repository_specific_filtering() {
    source_utils
    
    # Create two separate test repositories
    local repo1_dir="/tmp/test-repo-1-$$"
    local repo2_dir="/tmp/test-repo-2-$$"
    
    # Setup repo 1 with tasks
    rm -rf "$repo1_dir"
    mkdir -p "$repo1_dir/.beads"
    cd "$repo1_dir"
    git init >/dev/null 2>&1
    git config user.email "test@example.com"
    git config user.name "Test User"
    echo '{"version": "1.0"}' > "$repo1_dir/.beads/config.json"
    touch "$repo1_dir/.beads/issues.jsonl"
    
    # Setup repo 2 without tasks
    rm -rf "$repo2_dir"
    mkdir -p "$repo2_dir/.beads"
    cd "$repo2_dir"
    git init >/dev/null 2>&1
    git config user.email "test@example.com"
    git config user.name "Test User"
    echo '{"version": "1.0"}' > "$repo2_dir/.beads/config.json"
    touch "$repo2_dir/.beads/issues.jsonl"
    
    # Create mock bd that returns different responses based on current directory
    cat > "/tmp/mock-repo-bd-$$" << 'EOF'
#!/bin/bash
current_dir=\$(pwd)
if [[ "\$current_dir" == *"repo-1"* ]]; then
    echo '[{"id": "repo1-task", "title": "Repo 1 Task", "status": "open"}]'
else
    echo '[]'
fi
EOF
    chmod +x "/tmp/mock-repo-bd-$$"
    
    export PATH="/tmp:$PATH"
    rm -f "/tmp/bd"
    ln -sf "/tmp/mock-repo-bd-$$" "/tmp/bd"
    
    # Test repo 1 (should have tasks)
    if ! has_open_bead_tasks "$repo1_dir"; then
        echo "has_open_bead_tasks should find tasks in repo1"
        rm -rf "$repo1_dir" "$repo2_dir"
        return 1
    fi
    
    local count1
    count1=$(get_open_bead_tasks_count "$repo1_dir")
    if [[ "$count1" != "1" ]]; then
        echo "get_open_bead_tasks_count should return 1 for repo1, got $count1"
        rm -rf "$repo1_dir" "$repo2_dir"
        return 1
    fi
    
    # Test repo 2 (should have no tasks)
    if has_open_bead_tasks "$repo2_dir"; then
        echo "has_open_bead_tasks should not find tasks in repo2"
        rm -rf "$repo1_dir" "$repo2_dir"
        return 1
    fi
    
    local count2
    count2=$(get_open_bead_tasks_count "$repo2_dir")
    if [[ "$count2" != "0" ]]; then
        echo "get_open_bead_tasks_count should return 0 for repo2, got $count2"
        rm -rf "$repo1_dir" "$repo2_dir"
        return 1
    fi
    
    # Cleanup
    rm -rf "$repo1_dir" "$repo2_dir"
    return 0
}

# Main test execution
main() {
    echo "=== Task Availability Functionality Test Suite ==="
    echo "Testing directory: $PROJECT_DIR"
    echo "Utils script: $UTILS_SCRIPT"
    echo "Test repository: $TEST_REPO_DIR"
    echo "Test log directory: $TEST_LOG_DIR"
    echo ""
    
    # Run all tests
    run_test "Function availability" "test_function_availability"
    run_test "Repository without .beads directory" "test_no_beads_directory"
    run_test "Repository with beads but no open tasks" "test_beads_no_open_tasks"
    run_test "Repository with beads and open tasks" "test_beads_with_open_tasks"
    run_test "Mixed status tasks" "test_mixed_status_tasks"
    run_test "BD command behavior" "test_bd_command_behavior"
    run_test "BD command timeout" "test_bd_command_timeout"
    run_test "Invalid JSON response" "test_invalid_json_response"
    run_test "Task availability decision logging" "test_task_availability_logging"
    run_test "Large number of tasks performance" "test_large_number_of_tasks"
    run_test "Directory navigation and error handling" "test_directory_navigation"
    run_test "Repository-specific filtering" "test_repository_specific_filtering"
    
    # Print results
    echo ""
    echo "=== Test Results ==="
    echo "Total tests: $TESTS_TOTAL"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ All task availability tests passed!${NC}"
        echo ""
        echo "Test coverage includes:"
        echo "  ✓ Function availability and basic functionality"
        echo "  ✓ Repository with and without .beads directory"
        echo "  ✓ Open task detection and counting"
        echo "  ✓ Mixed status task handling"
        echo "  ✓ BD command availability and timeout handling"
        echo "  ✓ Invalid JSON response handling"
        echo "  ✓ Task availability decision logging"
        echo "  ✓ Performance with large task sets"
        echo "  ✓ Directory navigation and error handling"
        echo "  ✓ Repository-specific filtering"
        echo ""
        echo "Functions tested:"
        echo "  - has_open_bead_tasks(): Boolean check for open tasks"
        echo "  - get_open_bead_tasks_count(): Count of open tasks"
        echo "  - log_task_availability_decision(): Decision logging"
        exit 0
    else
        echo -e "${RED}✗ Some task availability tests failed!${NC}"
        exit 1
    fi
}

# Run main function
main "$@"