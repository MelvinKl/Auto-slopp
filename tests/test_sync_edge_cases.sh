#!/bin/bash

# Test Edge Cases in File Synchronization
# Tests edge cases and boundary conditions in file synchronization operations
# Tests invalid filenames, permission issues, concurrent changes, and other edge cases

SCRIPT_NAME="test_sync_edge_cases"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_sync_edge_cases_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

# Test results tracking
TESTS_RUN=0
TESTS_PASSED=0

log "INFO" "Starting edge cases synchronization tests in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test helper functions
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo ""
    echo "=========================================="
    echo "Running Test: $test_name"
    echo "=========================================="
    
    if eval "$test_command"; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo "✅ $test_name PASSED"
        return 0
    else
        echo "❌ $test_name FAILED"
        return 1
    fi
}

# Helper to create test task files
create_task_file() {
    local number="$1"
    local title="$2"
    local task_dir="$3"
    
    # Pad number to 4 digits
    local padded_num=$(printf "%04d" "$number")
    local filename="${padded_num}-${title}.txt"
    local filepath="$task_dir/$filename"
    
    echo "Task content for $title" > "$filepath"
    echo "$filepath"
}

# Helper to initialize number state
init_test_state() {
    local context="$1"
    "$NUMBER_MANAGER_SCRIPT" init "$context" >/dev/null 2>&1
}

# Test 1: Invalid filename patterns
test_invalid_filenames() {
    log "INFO" "Test 1: Testing invalid filename patterns"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir="$TEST_STATE_DIR/tasks"
    mkdir -p "$task_dir"
    
    # Initialize state
    init_test_state "$context"
    
    # Create files with invalid patterns (should be ignored during sync)
    touch "$task_dir/123-invalid-prefix.txt"
    touch "$task_dir/12-three-digits.txt"
    touch "$task_dir/12345-five-digits.txt"
    touch "$task_dir/123-.txt"
    touch "$task_dir/not-numbered.txt"
    touch "$task_dir/abc-def.txt"
    touch "$task_dir/123-task.used"
    touch "$task_dir/123-task.md"
    touch "$task_dir/123-"
    touch "$task_dir/123-task.extra.txt"
    
    # Sync with invalid filenames (should result in empty state)
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Sync failed with invalid filenames"
        return 1
    fi
    
    # Verify state remains empty (no valid files found)
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    if [ "$used_count" -ne 0 ]; then
        log "ERROR" "Expected used_count=0 with invalid filenames, got $used_count"
        return 1
    fi
    
    # Now add a valid file and verify it's picked up
    create_task_file 1 "valid-task" "$task_dir"
    "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1
    
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    if [ "$used_count" -ne 1 ]; then
        log "ERROR" "Expected used_count=1 after adding valid file, got $used_count"
        return 1
    fi
    
    log "SUCCESS" "Invalid filename patterns handled correctly"
    return 0
}

# Test 2: Zero-padded number handling
test_zero_padded_numbers() {
    log "INFO" "Test 2: Testing zero-padded number handling"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir="$TEST_STATE_DIR/tasks"
    mkdir -p "$task_dir"
    
    # Initialize state
    init_test_state "$context"
    
    # Create files with various padding scenarios
    echo "content" > "$task_dir/0001-task.txt"
    echo "content" > "$task_dir/0010-task.txt"
    echo "content" > "$task_dir/0100-task.txt"
    echo "content" > "$task_dir/1000-task.txt"
    
    # Sync state
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Sync failed with zero-padded numbers"
        return 1
    fi
    
    # Verify all files are detected with correct numbers
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    local last_assigned
    last_assigned=$(echo "$stats" | jq -r '.last_assigned')
    
    if [ "$used_count" -ne 4 ]; then
        log "ERROR" "Expected used_count=4, got $used_count"
        return 1
    fi
    
    if [ "$last_assigned" -ne 1000 ]; then
        log "ERROR" "Expected last_assigned=1000, got $last_assigned"
        return 1
    fi
    
    log "SUCCESS" "Zero-padded number handling works correctly"
    return 0
}

# Test 3: Very large numbers (near limit)
test_large_numbers() {
    log "INFO" "Test 3: Testing very large numbers near limits"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir="$TEST_STATE_DIR/tasks"
    mkdir -p "$task_dir"
    
    # Initialize state
    init_test_state "$context"
    
    # Create files with large numbers
    echo "content" > "$task_dir/9995-task.txt"
    echo "content" > "$task_dir/9998-task.txt"
    echo "content" > "$task_dir/9999-task.txt"
    
    # Sync state
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Sync failed with large numbers"
        return 1
    fi
    
    # Verify large numbers are handled correctly
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    local last_assigned
    last_assigned=$(echo "$stats" | jq -r '.last_assigned')
    
    if [ "$used_count" -ne 3 ]; then
        log "ERROR" "Expected used_count=3, got $used_count"
        return 1
    fi
    
    if [ "$last_assigned" -ne 9999 ]; then
        log "ERROR" "Expected last_assigned=9999, got $last_assigned"
        return 1
    fi
    
    # Test getting next number (should work as there are gaps)
    local next_num
    if next_num=$("$NUMBER_MANAGER_SCRIPT" get "$context" 2>/dev/null); then
        if [ "$next_num" -lt 1 ] || [ "$next_num" -gt 9999 ]; then
            log "ERROR" "Next number out of range: $next_num"
            return 1
        fi
    else
        log "ERROR" "Failed to get next number after large numbers"
        return 1
    fi
    
    log "SUCCESS" "Large number handling works correctly"
    return 0
}

# Test 4: Files with special characters in names
test_special_characters() {
    log "INFO" "Test 4: Testing files with special characters in names"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir="$TEST_STATE_DIR/tasks"
    mkdir -p "$task_dir"
    
    # Initialize state
    init_test_state "$context"
    
    # Create files with various special characters
    echo "content" > "$task_dir/0001-task-with-dashes.txt"
    echo "content" > "$task_dir/0002-task_with_underscores.txt"
    echo "content" > "$task_dir/0003-task.with.dots.txt"
    echo "content" > "$task_dir/0004-task+with+plus.txt"
    echo "content" > "$task_dir/0005-task with spaces.txt"
    echo "content" > "$task_dir/0006/task-with-slash.txt"  # Invalid: contains slash
    echo "content" > "$task_dir/0007-task@at.txt"
    echo "content" > "$task_dir/0008/task:colon.txt"  # Invalid: contains colon
    
    # Sync state
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Sync failed with special characters"
        return 1
    fi
    
    # Should only find valid files (excluding those with forbidden characters)
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    # Expected: 0001, 0002, 0003, 0004, 0007 (5 valid files)
    # 0005 has space (might be valid), 0006 and 0008 have slash/colon (invalid)
    if [ "$used_count" -lt 5 ] || [ "$used_count" -gt 6 ]; then
        log "ERROR" "Expected 5-6 valid files with special characters, got $used_count"
        return 1
    fi
    
    log "SUCCESS" "Special character handling works correctly"
    return 0
}

# Test 5: Files with read-only permissions
test_readonly_files() {
    log "INFO" "Test 5: Testing files with read-only permissions"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir="$TEST_STATE_DIR/tasks"
    mkdir -p "$task_dir"
    
    # Initialize state
    init_test_state "$context"
    
    # Create files with read-only permissions
    local file1="$task_dir/0001-readonly-task.txt"
    local file2="$task_dir/0002-normal-task.txt"
    
    echo "readonly content" > "$file1"
    echo "normal content" > "$file2"
    
    # Make first file read-only
    chmod 444 "$file1"
    
    # Sync state (should work fine as we only need to read files)
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Sync failed with read-only files"
        return 1
    fi
    
    # Verify both files are detected
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    if [ "$used_count" -ne 2 ]; then
        log "ERROR" "Expected used_count=2 with read-only files, got $used_count"
        return 1
    fi
    
    # Restore permissions for cleanup
    chmod 644 "$file1"
    
    log "SUCCESS" "Read-only file handling works correctly"
    return 0
}

# Test 6: Empty files
test_empty_files() {
    log "INFO" "Test 6: Testing empty files"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir="$TEST_STATE_DIR/tasks"
    mkdir -p "$task_dir"
    
    # Initialize state
    init_test_state "$context"
    
    # Create empty files
    touch "$task_dir/0001-empty-task.txt"
    touch "$task_dir/0002-another-empty.txt"
    
    # Also create a file with content
    echo "has content" > "$task_dir/0003-has-content.txt"
    
    # Sync state
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Sync failed with empty files"
        return 1
    fi
    
    # Verify all files are detected regardless of content
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    if [ "$used_count" -ne 3 ]; then
        log "ERROR" "Expected used_count=3 with empty files, got $used_count"
        return 1
    fi
    
    log "SUCCESS" "Empty file handling works correctly"
    return 0
}

# Test 7: Symlink handling
test_symlink_handling() {
    log "INFO" "Test 7: Testing symlink handling"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir="$TEST_STATE_DIR/tasks"
    mkdir -p "$task_dir"
    
    # Initialize state
    init_test_state "$context"
    
    # Create regular file
    echo "regular content" > "$task_dir/0001-regular.txt"
    
    # Create symlink to regular file (should be ignored or handled gracefully)
    ln -s "0001-regular.txt" "$task_dir/0002-symlink.txt"
    
    # Create broken symlink
    ln -s "nonexistent.txt" "$task_dir/0003-broken-symlink.txt"
    
    # Sync state
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Sync failed with symlinks"
        return 1
    fi
    
    # Should find regular file but not symlinks (depending on implementation)
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    # At minimum, should find the regular file
    if [ "$used_count" -lt 1 ]; then
        log "ERROR" "Expected at least used_count=1 with regular file, got $used_count"
        return 1
    fi
    
    # Should not crash on broken symlinks
    log "SUCCESS" "Symlink handling works correctly"
    return 0
}

# Test 8: Files with binary content
test_binary_files() {
    log "INFO" "Test 8: Testing files with binary content"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir="$TEST_STATE_DIR/tasks"
    mkdir -p "$task_dir"
    
    # Initialize state
    init_test_state "$context"
    
    # Create regular text file
    echo "text content" > "$task_dir/0001-text-file.txt"
    
    # Create binary file
    echo -e "\x00\x01\x02\x03\x04\x05" > "$task_dir/0002-binary-file.txt"
    
    # Create mixed content file
    echo "text start" > "$task_dir/0003-mixed-file.txt"
    echo -e "\x00\x01" >> "$task_dir/0003-mixed-file.txt"
    echo "text end" >> "$task_dir/0003-mixed-file.txt"
    
    # Sync state (should work as we only read filenames, not content)
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Sync failed with binary files"
        return 1
    fi
    
    # Verify all files are detected
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    if [ "$used_count" -ne 3 ]; then
        log "ERROR" "Expected used_count=3 with binary files, got $used_count"
        return 1
    fi
    
    log "SUCCESS" "Binary file handling works correctly"
    return 0
}

# Test 9: Files in hidden directories
test_hidden_directories() {
    log "INFO" "Test 9: Testing files in hidden directories"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir="$TEST_STATE_DIR/tasks"
    mkdir -p "$task_dir"
    mkdir -p "$task_dir/.hidden"
    mkdir -p "$task_dir/.hidden/subdir"
    
    # Initialize state
    init_test_state "$context"
    
    # Create files in various locations
    echo "content" > "$task_dir/0001-visible-file.txt"
    echo "content" > "$task_dir/.hidden/0002-hidden-file.txt"
    echo "content" > "$task_dir/.hidden/subdir/0003-subdir-file.txt"
    
    # Sync state (should only find files in main directory due to maxdepth 1)
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Sync failed with hidden directories"
        return 1
    fi
    
    # Should only find the visible file
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    if [ "$used_count" -ne 1 ]; then
        log "ERROR" "Expected used_count=1 (excluding hidden dirs), got $used_count"
        return 1
    fi
    
    log "SUCCESS" "Hidden directory handling works correctly"
    return 0
}

# Test 10: Very long filenames
test_long_filenames() {
    log "INFO" "Test 10: Testing very long filenames"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir="$TEST_STATE_DIR/tasks"
    mkdir -p "$task_dir"
    
    # Initialize state
    init_test_state "$context"
    
    # Create files with very long names
    local long_name=$(printf "a%.0s" {1..200})  # 200 characters
    echo "content" > "$task_dir/0001-${long_name}.txt"
    
    # Create file with maximum typical filename length (255 chars total)
    local max_name=$(printf "b%.0s" {1..245})  # 245 chars + "0004-" + ".txt" = 255
    echo "content" > "$task_dir/0002-${max_name}.txt"
    
    # Sync state
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Sync failed with long filenames"
        return 1
    fi
    
    # Verify long files are detected
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    if [ "$used_count" -ne 2 ]; then
        log "ERROR" "Expected used_count=2 with long filenames, got $used_count"
        return 1
    fi
    
    log "SUCCESS" "Long filename handling works correctly"
    return 0
}

# Test 11: Files with Unicode characters
test_unicode_filenames() {
    log "INFO" "Test 11: Testing files with Unicode characters"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir="$TEST_STATE_DIR/tasks"
    mkdir -p "$task_dir"
    
    # Initialize state
    init_test_state "$context"
    
    # Create files with Unicode characters
    echo "content" > "$task_dir/0001-ñiño.txt"
    echo "content" > "$task_dir/0002-中文.txt"
    echo "content" > "$task_dir/0003-русский.txt"
    echo "content" > "$task_dir/0004-العربية.txt"
    echo "content" > "$task_dir/0005-🚀emoji.txt"
    
    # Sync state
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Sync failed with Unicode filenames"
        return 1
    fi
    
    # Verify Unicode files are detected
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    if [ "$used_count" -ne 5 ]; then
        log "ERROR" "Expected used_count=5 with Unicode filenames, got $used_count"
        return 1
    fi
    
    log "SUCCESS" "Unicode filename handling works correctly"
    return 0
}

# Test 12: Directory with mixed valid/invalid patterns
test_mixed_patterns() {
    log "INFO" "Test 12: Testing directory with mixed valid/invalid patterns"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    
    # Setup
    local context="test-repo"
    local task_dir="$TEST_STATE_DIR/tasks"
    mkdir -p "$task_dir"
    
    # Initialize state
    init_test_state "$context"
    
    # Create mix of valid and invalid files
    echo "content" > "$task_dir/0001-valid-task.txt"
    echo "content" > "$task_dir/0002-valid-task.txt"
    touch "$task_dir/invalid.txt"
    touch "$task_dir/123-invalid-prefix.txt"
    echo "content" > "$task_dir/0003-valid-task.txt"
    touch "$task_dir/12-three-digits.txt"
    echo "content" > "$task_dir/0004-valid-task.txt"
    touch "$task_dir/not-numbered.md"
    
    # Sync state
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$task_dir" "$context" >/dev/null 2>&1; then
        log "ERROR" "Sync failed with mixed patterns"
        return 1
    fi
    
    # Should only find the 4 valid files
    local stats
    stats=$("$NUMBER_MANAGER_SCRIPT" stats 2>/dev/null)
    local used_count
    used_count=$(echo "$stats" | jq -r '.used_count')
    
    if [ "$used_count" -ne 4 ]; then
        log "ERROR" "Expected used_count=4 in mixed patterns, got $used_count"
        return 1
    fi
    
    log "SUCCESS" "Mixed pattern handling works correctly"
    return 0
}

# Main test execution
run_all_tests() {
    echo ""
    echo "=========================================="
    echo "Edge Cases Synchronization Tests"
    echo "=========================================="
    
    run_test "Invalid Filenames" "test_invalid_filenames"
    run_test "Zero-padded Numbers" "test_zero_padded_numbers"
    run_test "Large Numbers" "test_large_numbers"
    run_test "Special Characters" "test_special_characters"
    run_test "Read-only Files" "test_readonly_files"
    run_test "Empty Files" "test_empty_files"
    run_test "Symlink Handling" "test_symlink_handling"
    run_test "Binary Files" "test_binary_files"
    run_test "Hidden Directories" "test_hidden_directories"
    run_test "Long Filenames" "test_long_filenames"
    run_test "Unicode Filenames" "test_unicode_filenames"
    run_test "Mixed Patterns" "test_mixed_patterns"
    
    echo ""
    echo "=========================================="
    echo "Test Results: $TESTS_PASSED/$TESTS_RUN passed"
    echo "=========================================="
    
    if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
        log "SUCCESS" "All edge cases synchronization tests passed!"
        return 0
    else
        log "ERROR" "Some edge cases synchronization tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests edge cases in file synchronization"
    exit 1
fi