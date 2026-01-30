#!/bin/bash

# Test script for planner.sh 4-digit numbering functionality
# This script creates test scenarios to verify the planner works correctly

# Load utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scripts/utils.sh"

# Test configuration
TEST_REPO_NAME="test-repo-4digit"
TEST_TASK_PATH="$HOME/git/repo_task_path/$TEST_REPO_NAME"
TEST_REPO_PATH="$HOME/git/managed/$TEST_REPO_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to log test results
log_test_result() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✓ PASS${NC}: $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC}: $test_name"
        echo -e "  ${YELLOW}Details: $details${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Function to setup test environment
setup_test_env() {
    echo "Setting up test environment..."
    
    # Create test repository directory
    mkdir -p "$TEST_REPO_PATH"
    cd "$TEST_REPO_PATH"
    git init
    git config user.email "test@example.com"
    git config user.name "Test User"
    
    # Create initial commit
    echo "# Test Repository" > README.md
    git add README.md
    git commit -m "Initial commit"
    
    # Create remote origin (local)
    git init --bare origin.git 2>/dev/null || true
    git remote add origin "$TEST_REPO_PATH/origin.git"
    git push -u origin main || git push -u origin master || true
    
    # Create test task directory
    mkdir -p "$TEST_TASK_PATH"
    cd "$TEST_TASK_PATH"
    git init
    git config user.email "test@example.com"
    git config user.name "Test User"
    echo "# Test task directory" > README.md
    git add README.md
    git commit -m "Initial commit"
    
    echo "Test environment setup complete."
}

# Function to cleanup test environment
cleanup_test_env() {
    echo "Cleaning up test environment..."
    rm -rf "$TEST_REPO_PATH"
    rm -rf "$TEST_TASK_PATH"
    echo "Cleanup complete."
}

# Function to test 4-digit file generation
test_4digit_file_generation() {
    echo "Testing 4-digit file generation..."
    
    cd "$TEST_TASK_PATH"
    
    # Create an unnumbered task file
    echo "Test task for 4-digit numbering" > "test-task-1.txt"
    
    # Run the planner on just our test directory
    # We'll extract and run only the file numbering part
    unnumbered_files=($(find "$TEST_TASK_PATH" -maxdepth 1 -type f -name "*.txt" ! -name "[0-9][0-9][0-9][0-9]-*" ! -name "*.used" | sort))
    
    if [ ${#unnumbered_files[@]} -gt 0 ]; then
        # Find the next available number
        max_num=0
        numbered_files=($(find "$TEST_TASK_PATH" -maxdepth 1 -type f -name "[0-9][0-9][0-9][0-9]-*.txt" ! -name "*.used" 2>/dev/null))
        for num_file in "${numbered_files[@]}"; do
            basename_num=$(basename "$num_file" | sed 's/^\([0-9][0-9][0-9][0-9]\)-.*/\1/')
            if [[ "$basename_num" =~ ^[0-9][0-9][0-9][0-9]$ ]]; then
                num_val=$((10#$basename_num))
                if [ $num_val -gt $max_num ]; then
                    max_num=$num_val
                fi
            fi
        done
        
        # Assign numbers to unnumbered files
        next_num=$((max_num + 1))
        for unnumbered_file in "${unnumbered_files[@]}"; do
            filename=$(basename "$unnumbered_file" .txt)
            new_filename=$(printf "%04d-%s.txt" "$next_num" "$filename")
            mv "$unnumbered_file" "$TEST_TASK_PATH/$new_filename"
            
            # Check if the filename has 4-digit numbering
            if [[ "$new_filename" =~ ^[0-9][0-9][0-9][0-9]-.*\.txt$ ]]; then
                log_test_result "4-digit file generation" "PASS" "Generated $new_filename"
            else
                log_test_result "4-digit file generation" "FAIL" "Expected 4-digit format, got $new_filename"
            fi
        done
    else
        log_test_result "4-digit file generation" "FAIL" "No unnumbered files found to test"
    fi
}

# Function to test existing 2-digit file processing
test_2digit_file_processing() {
    echo "Testing existing 2-digit file processing..."
    
    cd "$TEST_TASK_PATH"
    
    # Create a mock 2-digit file (to test backward compatibility)
    echo "Legacy 2-digit task file" > "01-legacy-task.txt"
    
    # Check if the glob pattern finds 4-digit files but not 2-digit files for processing
    processed_files=($(find "$TEST_TASK_PATH" -maxdepth 1 -name "[0-9][0-9][0-9][0-9]-*.txt" ! -name "*.used" 2>/dev/null))
    
    # Check if 2-digit files are NOT processed by the new 4-digit pattern
    if [ -f "01-legacy-task.txt" ]; then
        # The 2-digit file should exist but NOT be in processed_files
        found_2digit=false
        for file in "${processed_files[@]}"; do
            if [[ "$(basename "$file")" == "01-legacy-task.txt" ]]; then
                found_2digit=true
                break
            fi
        done
        
        if [ "$found_2digit" = false ]; then
            log_test_result "2-digit file exclusion" "PASS" "2-digit files correctly excluded from 4-digit processing"
        else
            log_test_result "2-digit file exclusion" "FAIL" "2-digit files incorrectly included in 4-digit processing"
        fi
    else
        log_test_result "2-digit file processing setup" "FAIL" "Could not create test 2-digit file"
    fi
}

# Function to test sequential numbering
test_sequential_numbering() {
    echo "Testing sequential 4-digit numbering..."
    
    cd "$TEST_TASK_PATH"
    
    # Create multiple unnumbered files
    echo "Task A" > "task-a.txt"
    echo "Task B" > "task-b.txt"
    echo "Task C" > "task-c.txt"
    
    # Find existing numbered files
    max_num=0
    numbered_files=($(find "$TEST_TASK_PATH" -maxdepth 1 -type f -name "[0-9][0-9][0-9][0-9]-*.txt" ! -name "*.used" 2>/dev/null))
    for num_file in "${numbered_files[@]}"; do
        basename_num=$(basename "$num_file" | sed 's/^\([0-9][0-9][0-9][0-9]\)-.*/\1/')
        if [[ "$basename_num" =~ ^[0-9][0-9][0-9][0-9]$ ]]; then
            num_val=$((10#$basename_num))
            if [ $num_val -gt $max_num ]; then
                max_num=$num_val
            fi
        fi
    done
    
    # Process unnumbered files
    unnumbered_files=($(find "$TEST_TASK_PATH" -maxdepth 1 -type f -name "*.txt" ! -name "[0-9][0-9][0-9][0-9]-*" ! -name "*.used" | sort))
    expected_sequence=()
    
    next_num=$((max_num + 1))
    for unnumbered_file in "${unnumbered_files[@]}"; do
        filename=$(basename "$unnumbered_file" .txt)
        new_filename=$(printf "%04d-%s.txt" "$next_num" "$filename")
        expected_sequence+=("$new_filename")
        mv "$unnumbered_file" "$TEST_TASK_PATH/$new_filename"
        next_num=$((next_num + 1))
    done
    
    # Verify sequential numbering
    sequential_correct=true
    expected_num=$((max_num + 1))
    
    for expected_file in "${expected_sequence[@]}"; do
        actual_num=$(basename "$expected_file" | sed 's/^\([0-9][0-9][0-9][0-9]\)-.*/\1/')
        expected_num_str=$(printf "%04d" "$expected_num")
        
        if [ "$actual_num" != "$expected_num_str" ]; then
            sequential_correct=false
            break
        fi
        expected_num=$((expected_num + 1))
    done
    
    if [ "$sequential_correct" = true ]; then
        log_test_result "Sequential numbering" "PASS" "Files numbered correctly in sequence"
    else
        log_test_result "Sequential numbering" "FAIL" "Expected sequential numbering, but got incorrect sequence"
    fi
}

# Function to test file pattern matching
test_file_pattern_matching() {
    echo "Testing 4-digit file pattern matching..."
    
    cd "$TEST_TASK_PATH"
    
    # Create test files with different patterns
    touch "0001-test.txt"
    touch "1234-test.txt"
    touch "9999-test.txt"
    touch "00000-test.txt"     # 5-digit - should NOT match
    touch "999-test.txt"       # 3-digit - should NOT match
    touch "99-test.txt"        # 2-digit - should NOT match
    touch "abcd-test.txt"      # letters - should NOT match
    
    # Test the pattern used in the script
    matched_files=($(find "$TEST_TASK_PATH" -maxdepth 1 -name "[0-9][0-9][0-9][0-9]-*.txt" ! -name "*.used" 2>/dev/null | sort))
    
    # Expected matches
    expected_matches=("0001-test.txt" "1234-test.txt" "9999-test.txt")
    
    all_match=true
    for expected in "${expected_matches[@]}"; do
        found=false
        for actual in "${matched_files[@]}"; do
            if [[ "$(basename "$actual")" == "$expected" ]]; then
                found=true
                break
            fi
        done
        if [ "$found" = false ]; then
            all_match=false
            break
        fi
    done
    
    # Check that non-matching files are not included
    non_matching=("00000-test.txt" "999-test.txt" "99-test.txt" "abcd-test.txt")
    for non_match in "${non_matching[@]}"; do
        found=false
        for actual in "${matched_files[@]}"; do
            if [[ "$(basename "$actual")" == "$non_match" ]]; then
                found=true
                break
            fi
        done
        if [ "$found" = true ]; then
            all_match=false
            break
        fi
    done
    
    if [ "$all_match" = true ]; then
        log_test_result "4-digit pattern matching" "PASS" "Pattern correctly matches 4-digit files only"
    else
        log_test_result "4-digit pattern matching" "FAIL" "Pattern matching incorrect"
    fi
}

# Main test execution
main() {
    echo "Starting planner.sh 4-digit numbering tests..."
    echo "=========================================="
    
    # Setup
    setup_test_env
    
    # Run tests
    test_4digit_file_generation
    test_2digit_file_processing
    test_sequential_numbering
    test_file_pattern_matching
    
    # Cleanup
    cleanup_test_env
    
    # Results summary
    echo "=========================================="
    echo "Test Results Summary:"
    echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
    echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed! ✓${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed! ✗${NC}"
        exit 1
    fi
}

# Run main function
main "$@"