#!/bin/bash

# Test File Discovery Mechanisms
# Tests detection of numbered task files (####-*.txt pattern) in task directories
# Tests file discovery, pattern matching, and number extraction functionality

SCRIPT_NAME="test_file_discovery"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_file_discovery_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

# Test results tracking
TESTS_RUN=0
TESTS_PASSED=0

log "INFO" "Starting file discovery tests in $TEST_STATE_DIR"

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

# Helper to find numbered task files (simulate discovery)
discover_task_files() {
    local task_dir="$1"
    if [ ! -d "$task_dir" ]; then
        return 0
    fi
    find "$task_dir" -maxdepth 1 -type f -name "[0-9][0-9][0-9][0-9]-*.txt" ! -name "*.used" 2>/dev/null | sort
}

# Helper to count discovered files
count_discovered_files() {
    local file_list="$1"
    if [ -z "$file_list" ]; then
        echo 0
    else
        echo "$file_list" | wc -l
    fi
}

# Helper to extract numbers from discovered files
extract_numbers_from_files() {
    local file_list="$1"
    local numbers=()
    
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            basename_num=$(basename "$file" | sed 's/^\([0-9][0-9][0-9][0-9]\)-.*/\1/')
            if [[ "$basename_num" =~ ^[0-9][0-9][0-9][0-9]$ ]]; then
                numbers+=("$((10#$basename_num))")
            fi
        fi
    done <<< "$file_list"
    
    printf '%s\n' "${numbers[@]}" | sort -n
}

# Test 1: Basic numbered file discovery
test_basic_file_discovery() {
    log "INFO" "Test 1: Testing basic numbered file discovery"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$TEST_STATE_DIR/tasks"
    
    # Create test task files
    local task_dir="$TEST_STATE_DIR/tasks"
    create_task_file 1 "first-task" "$task_dir"
    create_task_file 5 "fifth-task" "$task_dir"
    create_task_file 10 "tenth-task" "$task_dir"
    
    # Discover files
    local discovered_files
    discovered_files=$(discover_task_files "$task_dir")
    
    # Check if we found all 3 files
    local file_count
    file_count=$(echo "$discovered_files" | wc -l)
    if [ "$file_count" -ne 3 ]; then
        log "ERROR" "Expected 3 files, found $file_count"
        echo "Discovered files:"
        echo "$discovered_files"
        return 1
    fi
    
    # Check if specific files are found
    if ! echo "$discovered_files" | grep -q "0001-first-task.txt"; then
        log "ERROR" "Failed to discover 0001-first-task.txt"
        return 1
    fi
    
    if ! echo "$discovered_files" | grep -q "0005-fifth-task.txt"; then
        log "ERROR" "Failed to discover 0005-fifth-task.txt"
        return 1
    fi
    
    if ! echo "$discovered_files" | grep -q "0010-tenth-task.txt"; then
        log "ERROR" "Failed to discover 0010-tenth-task.txt"
        return 1
    fi
    
    log "SUCCESS" "Basic file discovery works correctly"
    return 0
}

# Test 2: Pattern matching accuracy
test_pattern_matching() {
    log "INFO" "Test 2: Testing pattern matching accuracy"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$TEST_STATE_DIR/tasks"
    
    local task_dir="$TEST_STATE_DIR/tasks"
    
    # Create files with various patterns
    create_task_file 1 "valid-task" "$task_dir"
    create_task_file 100 "another-valid" "$task_dir"
    
    # Create files that should NOT be discovered
    touch "$task_dir/not-numbered.txt"
    touch "$task_dir/123-invalid-prefix.txt"
    touch "$task_dir/123-NO-TXT.md"
    touch "$task_dir/123-task.used"
    touch "$task_dir/12-three-digits.txt"
    touch "$task_dir/12345-five-digits.txt"
    touch "$task_dir/123-.txt"
    touch "$task_dir/abc-def.txt"
    
    # Discover files
    local discovered_files
    discovered_files=$(discover_task_files "$task_dir")
    
    # Should only find the 2 valid files
    local file_count
    file_count=$(echo "$discovered_files" | wc -l)
    if [ "$file_count" -ne 2 ]; then
        log "ERROR" "Expected 2 files, found $file_count"
        echo "Discovered files:"
        echo "$discovered_files"
        return 1
    fi
    
    # Verify the correct files are found
    if ! echo "$discovered_files" | grep -q "0001-valid-task.txt"; then
        log "ERROR" "Failed to discover valid 0001-valid-task.txt"
        return 1
    fi
    
    if ! echo "$discovered_files" | grep -q "0100-another-valid.txt"; then
        log "ERROR" "Failed to discover valid 0100-another-valid.txt"
        return 1
    fi
    
    log "SUCCESS" "Pattern matching works correctly"
    return 0
}

# Test 3: Number extraction from filenames
test_number_extraction() {
    log "INFO" "Test 3: Testing number extraction from filenames"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$TEST_STATE_DIR/tasks"
    
    local task_dir="$TEST_STATE_DIR/tasks"
    
    # Create files with various numbers
    create_task_file 1 "task-one" "$task_dir"
    create_task_file 42 "task-forty-two" "$task_dir"
    create_task_file 9999 "max-number" "$task_dir"
    create_task_file 0 "zero-task" "$task_dir"
    
    # Discover files and extract numbers
    local discovered_files
    discovered_files=$(discover_task_files "$task_dir")
    local extracted_numbers
    extracted_numbers=$(extract_numbers_from_files "$discovered_files")
    
    # Expected numbers: 0, 1, 42, 9999
    local expected_numbers="0
1
42
9999"
    
    if [ "$extracted_numbers" != "$expected_numbers" ]; then
        log "ERROR" "Number extraction failed"
        echo "Expected: $expected_numbers"
        echo "Got: $extracted_numbers"
        return 1
    fi
    
    log "SUCCESS" "Number extraction works correctly"
    return 0
}

# Test 4: Empty directory discovery
test_empty_directory() {
    log "INFO" "Test 4: Testing empty directory discovery"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$TEST_STATE_DIR/tasks"
    
    local task_dir="$TEST_STATE_DIR/tasks"
    
    # Discover files in empty directory
    local discovered_files
    discovered_files=$(discover_task_files "$task_dir")
    
    # Should find no files
    local file_count
    if [ -z "$discovered_files" ]; then
        file_count=0
    else
        file_count=$(echo "$discovered_files" | wc -l)
    fi
    if [ "$file_count" -ne 0 ]; then
        log "ERROR" "Expected 0 files in empty directory, found $file_count"
        return 1
    fi
    
    # Extracted numbers should also be empty
    local extracted_numbers
    extracted_numbers=$(extract_numbers_from_files "$discovered_files")
    if [ -n "$extracted_numbers" ]; then
        log "ERROR" "Expected no numbers from empty directory, got: $extracted_numbers"
        return 1
    fi
    
    log "SUCCESS" "Empty directory discovery works correctly"
    return 0
}

# Test 5: Large number of files discovery
test_large_file_count() {
    log "INFO" "Test 5: Testing discovery with many files"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$TEST_STATE_DIR/tasks"
    
    local task_dir="$TEST_STATE_DIR/tasks"
    
    # Create 100 test files
    for i in {1..100}; do
        create_task_file "$i" "task-$i" "$task_dir"
    done
    
    # Discover files
    local discovered_files
    discovered_files=$(discover_task_files "$task_dir")
    
    # Should find all 100 files
    local file_count
    file_count=$(echo "$discovered_files" | wc -l)
    if [ "$file_count" -ne 100 ]; then
        log "ERROR" "Expected 100 files, found $file_count"
        return 1
    fi
    
    # Extract numbers and verify range
    local extracted_numbers
    extracted_numbers=$(extract_numbers_from_files "$discovered_files")
    local min_num
    local max_num
    min_num=$(echo "$extracted_numbers" | head -1)
    max_num=$(echo "$extracted_numbers" | tail -1)
    
    if [ "$min_num" != "1" ] || [ "$max_num" != "100" ]; then
        log "ERROR" "Number range incorrect. Expected min=1, max=100. Got min=$min_num, max=$max_num"
        return 1
    fi
    
    log "SUCCESS" "Large file count discovery works correctly"
    return 0
}

# Test 6: Non-existent directory handling
test_nonexistent_directory() {
    log "INFO" "Test 6: Testing non-existent directory handling"
    
    # Ensure clean state (don't create tasks directory)
    rm -rf "$TEST_STATE_DIR"
    
    local task_dir="$TEST_STATE_DIR/tasks"
    
    # Try to discover files in non-existent directory
    local discovered_files
    discovered_files=$(discover_task_files "$task_dir" 2>/dev/null || true)
    
    # Should return empty (find should handle non-existent directory gracefully)
    local file_count
    if [ -z "$discovered_files" ]; then
        file_count=0
    else
        file_count=$(echo "$discovered_files" | wc -l)
    fi
    if [ "$file_count" -ne 0 ]; then
        log "ERROR" "Expected 0 files for non-existent directory, found $file_count"
        return 1
    fi
    
    log "SUCCESS" "Non-existent directory handling works correctly"
    return 0
}

# Test 7: Special characters in filenames
test_special_characters() {
    log "INFO" "Test 7: Testing filenames with special characters"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$TEST_STATE_DIR/tasks"
    
    local task_dir="$TEST_STATE_DIR/tasks"
    
    # Create files with special characters (but valid pattern)
    create_task_file 1 "task-with-dashes" "$task_dir"
    create_task_file 2 "task_with_underscores" "$task_dir"
    create_task_file 3 "task-with.dots" "$task_dir"
    create_task_file 4 "task-with-numbers-123" "$task_dir"
    create_task_file 5 "task-MIXED-Case" "$task_dir"
    
    # Discover files
    local discovered_files
    discovered_files=$(discover_task_files "$task_dir")
    
    # Should find all 5 files
    local file_count
    file_count=$(echo "$discovered_files" | wc -l)
    if [ "$file_count" -ne 5 ]; then
        log "ERROR" "Expected 5 files with special characters, found $file_count"
        return 1
    fi
    
    # Verify specific files are found
    if ! echo "$discovered_files" | grep -q "0001-task-with-dashes.txt"; then
        log "ERROR" "Failed to discover file with dashes"
        return 1
    fi
    
    if ! echo "$discovered_files" | grep -q "0002-task_with_underscores.txt"; then
        log "ERROR" "Failed to discover file with underscores"
        return 1
    fi
    
    if ! echo "$discovered_files" | grep -q "0003-task-with.dots.txt"; then
        log "ERROR" "Failed to discover file with dots"
        return 1
    fi
    
    log "SUCCESS" "Special characters in filenames handled correctly"
    return 0
}

# Test 8: Subdirectory exclusion
test_subdirectory_exclusion() {
    log "INFO" "Test 8: Testing subdirectory exclusion"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$TEST_STATE_DIR/tasks/subdir"
    
    local task_dir="$TEST_STATE_DIR/tasks"
    
    # Create files in main directory and subdirectory
    create_task_file 1 "main-task" "$task_dir"
    create_task_file 2 "sub-task" "$task_dir/subdir"
    
    # Discover files (should only find files in main directory due to maxdepth 1)
    local discovered_files
    discovered_files=$(discover_task_files "$task_dir")
    
    # Should only find 1 file (not the one in subdir)
    local file_count
    file_count=$(echo "$discovered_files" | wc -l)
    if [ "$file_count" -ne 1 ]; then
        log "ERROR" "Expected 1 file (excluding subdirectory), found $file_count"
        return 1
    fi
    
    # Verify it's the main directory file
    if ! echo "$discovered_files" | grep -q "0001-main-task.txt"; then
        log "ERROR" "Failed to discover main directory file"
        return 1
    fi
    
    # Should not find the subdirectory file
    if echo "$discovered_files" | grep -q "0002-sub-task.txt"; then
        log "ERROR" "Incorrectly discovered subdirectory file"
        return 1
    fi
    
    log "SUCCESS" "Subdirectory exclusion works correctly"
    return 0
}

# Test 9: File sorting and ordering
test_file_sorting() {
    log "INFO" "Test 9: Testing file sorting and ordering"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$TEST_STATE_DIR/tasks"
    
    local task_dir="$TEST_STATE_DIR/tasks"
    
    # Create files in non-sequential order
    create_task_file 100 "hundredth" "$task_dir"
    create_task_file 1 "first" "$task_dir"
    create_task_file 50 "fiftieth" "$task_dir"
    create_task_file 25 "twenty-fifth" "$task_dir"
    create_task_file 10 "tenth" "$task_dir"
    
    # Discover files
    local discovered_files
    discovered_files=$(discover_task_files "$task_dir")
    
    # Extract numbers and verify they are sorted
    local extracted_numbers
    extracted_numbers=$(extract_numbers_from_files "$discovered_files")
    
    local expected_order="1
10
25
50
100"
    
    if [ "$extracted_numbers" != "$expected_order" ]; then
        log "ERROR" "Files not sorted correctly"
        echo "Expected order: $expected_order"
        echo "Got order: $extracted_numbers"
        return 1
    fi
    
    log "SUCCESS" "File sorting and ordering works correctly"
    return 0
}

# Test 10: Edge case number patterns
test_edge_case_numbers() {
    log "INFO" "Test 10: Testing edge case number patterns"
    
    # Ensure clean state
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$TEST_STATE_DIR/tasks"
    
    local task_dir="$TEST_STATE_DIR/tasks"
    
    # Create files with edge case numbers
    create_task_file 0 "zero" "$task_dir"
    create_task_file 1 "min" "$task_dir"
    create_task_file 9999 "max" "$task_dir"
    create_task_file 1000 "thousand" "$task_dir"
    
    # Discover files and extract numbers
    local discovered_files
    discovered_files=$(discover_task_files "$task_dir")
    local extracted_numbers
    extracted_numbers=$(extract_numbers_from_files "$discovered_files")
    
    # Expected numbers in order
    local expected="0
1
1000
9999"
    
    if [ "$extracted_numbers" != "$expected" ]; then
        log "ERROR" "Edge case numbers not handled correctly"
        echo "Expected: $expected"
        echo "Got: $extracted_numbers"
        return 1
    fi
    
    log "SUCCESS" "Edge case number patterns handled correctly"
    return 0
}

# Main test execution
run_all_tests() {
    echo ""
    echo "=========================================="
    echo "File Discovery Tests"
    echo "=========================================="
    
    run_test "Basic File Discovery" "test_basic_file_discovery"
    run_test "Pattern Matching Accuracy" "test_pattern_matching"
    run_test "Number Extraction" "test_number_extraction"
    run_test "Empty Directory" "test_empty_directory"
    run_test "Large File Count" "test_large_file_count"
    run_test "Non-existent Directory" "test_nonexistent_directory"
    run_test "Special Characters" "test_special_characters"
    run_test "Subdirectory Exclusion" "test_subdirectory_exclusion"
    run_test "File Sorting" "test_file_sorting"
    run_test "Edge Case Numbers" "test_edge_case_numbers"
    
    echo ""
    echo "=========================================="
    echo "Test Results: $TESTS_PASSED/$TESTS_RUN passed"
    echo "=========================================="
    
    if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
        log "SUCCESS" "All file discovery tests passed!"
        return 0
    else
        log "ERROR" "Some file discovery tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests file discovery mechanisms for numbered task files"
    exit 1
fi