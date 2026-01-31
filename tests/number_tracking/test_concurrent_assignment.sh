#!/bin/bash

# Test concurrent number assignment and race condition handling
# Part of Auto-9bu: Test unique number assignment and locking mechanism

set -e

SCRIPT_NAME="test_concurrent_assignment"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_concurrent_assignment_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting concurrent assignment test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Basic concurrent assignment with 5 processes
test_basic_concurrent_assignment() {
    log "INFO" "Test 1: Basic concurrent assignment with 5 processes"
    
    # Initialize
    if ! "$NUMBER_MANAGER_SCRIPT" init concurrent_test >/dev/null 2>&1; then
        log "ERROR" "Initialization failed"
        return 1
    fi
    
    # Start multiple background processes to get numbers concurrently
    local pids=()
    local output_files=()
    
    for i in {1..5}; do
        local output_file="$TEST_STATE_DIR/output_$i.txt"
        output_files+=("$output_file")
        
        (
            for j in {1..3}; do
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get concurrent_test 2>/dev/null | tail -1)
                if [ $? -eq 0 ]; then
                    echo "$num" >> "$output_file"
                fi
                sleep 0.1  # Small delay to increase concurrency
            done
        ) &
        
        pids+=($!)
    done
    
    # Wait for all processes to complete
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
    
    # Collect all assigned numbers
    local all_numbers=()
    for output_file in "${output_files[@]}"; do
        if [ -f "$output_file" ]; then
            while read -r num; do
                all_numbers+=("$num")
            done < "$output_file"
        fi
    done
    
    # Check we got the expected number of assignments
    if [ ${#all_numbers[@]} -ne 15 ]; then
        log "ERROR" "Expected 15 assignments, got ${#all_numbers[@]}"
        return 1
    fi
    
    # Check for duplicates
    local sorted_numbers
    sorted_numbers=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d)
    if [ -n "$sorted_numbers" ]; then
        log "ERROR" "Duplicate numbers found: $sorted_numbers"
        return 1
    fi
    
    # Check number range (should be 1-15)
    local min_num max_num
    min_num=$(printf '%s\n' "${all_numbers[@]}" | sort -n | head -1)
    max_num=$(printf '%s\n' "${all_numbers[@]}" | sort -n | tail -1)
    
    if [ "$min_num" != "1" ] || [ "$max_num" != "15" ]; then
        log "ERROR" "Number range incorrect: min=$min_num, max=$max_num"
        return 1
    fi
    
    log "SUCCESS" "Basic concurrent assignment: 15 unique numbers (1-15)"
    return 0
}

# Test 2: High-frequency concurrent assignment
test_high_frequency_concurrent() {
    log "INFO" "Test 2: High-frequency concurrent assignment"
    
    # Initialize fresh state
    rm -rf "$TEST_STATE_DIR/.number_state"
    "$NUMBER_MANAGER_SCRIPT" init freq_test >/dev/null 2>&1
    
    # Start more aggressive concurrent processes
    local pids=()
    local output_files=()
    local process_count=10
    local assignments_per_process=5
    
    for i in $(seq 1 $process_count); do
        local output_file="$TEST_STATE_DIR/freq_output_$i.txt"
        output_files+=("$output_file")
        
        (
            for j in $(seq 1 $assignments_per_process); do
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get freq_test 2>/dev/null | tail -1)
                if [ $? -eq 0 ]; then
                    echo "$num" >> "$output_file"
                fi
                # No delay for high frequency
            done
        ) &
        
        pids+=($!)
    done
    
    # Wait for all processes
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
    
    # Collect and verify results
    local all_numbers=()
    for output_file in "${output_files[@]}"; do
        if [ -f "$output_file" ]; then
            while read -r num; do
                all_numbers+=("$num")
            done < "$output_file"
        fi
    done
    
    local expected_count=$((process_count * assignments_per_process))
    if [ ${#all_numbers[@]} -ne $expected_count ]; then
        log "ERROR" "Expected $expected_count assignments, got ${#all_numbers[@]}"
        return 1
    fi
    
    # Check uniqueness
    local sorted_numbers
    sorted_numbers=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d)
    if [ -n "$sorted_numbers" ]; then
        log "ERROR" "Duplicates in high-frequency test: $sorted_numbers"
        return 1
    fi
    
    log "SUCCESS" "High-frequency concurrent assignment: $expected_count unique numbers"
    return 0
}

# Test 3: Mixed contexts concurrently
test_mixed_contexts_concurrent() {
    log "INFO" "Test 3: Mixed contexts concurrently"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init mixed_test >/dev/null 2>&1
    
    local pids=()
    local output_files=()
    local contexts=("repo_A" "repo_B" "repo_C")
    
    for ctx in "${contexts[@]}"; do
        local output_file="$TEST_STATE_DIR/mixed_${ctx}.txt"
        output_files+=("$output_file")
        
        (
            for i in {1..5}; do
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get "$ctx" 2>/dev/null | tail -1)
                if [ $? -eq 0 ]; then
                    echo "$num" >> "$output_file"
                fi
                sleep 0.05
            done
        ) &
        
        pids+=($!)
    done
    
    # Wait for completion
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
    
    # Collect all numbers
    local all_numbers=()
    for output_file in "${output_files[@]}"; do
        if [ -f "$output_file" ]; then
            while read -r num; do
                all_numbers+=("$num")
            done < "$output_file"
        fi
    done
    
    # Verify uniqueness across contexts
    local sorted_numbers
    sorted_numbers=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d)
    if [ -n "$sorted_numbers" ]; then
        log "ERROR" "Cross-context duplicates found: $sorted_numbers"
        return 1
    fi
    
    # Verify total count
    if [ ${#all_numbers[@]} -ne 15 ]; then
        log "ERROR" "Expected 15 assignments, got ${#all_numbers[@]}"
        return 1
    fi
    
    log "SUCCESS" "Mixed contexts concurrent: 15 unique numbers across 3 contexts"
    return 0
}

# Test 4: Stress test with many concurrent processes
test_stress_concurrent() {
    log "INFO" "Test 4: Stress test with many concurrent processes"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init stress_test >/dev/null 2>&1
    
    # Start many concurrent processes
    local pids=()
    local output_files=()
    local process_count=20
    local assignments_per_process=3
    
    for i in $(seq 1 $process_count); do
        local output_file="$TEST_STATE_DIR/stress_$i.txt"
        output_files+=("$output_file")
        
        (
            for j in $(seq 1 $assignments_per_process); do
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get stress_test 2>/dev/null | tail -1)
                if [ $? -eq 0 ]; then
                    echo "$num" >> "$output_file"
                fi
                # Minimal delay to increase contention
                sleep 0.01
            done
        ) &
        
        pids+=($!)
    done
    
    # Wait for all processes
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
    
    # Collect results
    local all_numbers=()
    for output_file in "${output_files[@]}"; do
        if [ -f "$output_file" ]; then
            while read -r num; do
                all_numbers+=("$num")
            done < "$output_file"
        fi
    done
    
    local expected_count=$((process_count * assignments_per_process))
    if [ ${#all_numbers[@]} -ne $expected_count ]; then
        log "ERROR" "Stress test: expected $expected_count, got ${#all_numbers[@]}"
        return 1
    fi
    
    # Critical check for duplicates in stress test
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Stress test found $duplicate_count duplicates"
        return 1
    fi
    
    log "SUCCESS" "Stress test: $expected_count unique numbers from $process_count concurrent processes"
    return 0
}

# Test 5: Lock timeout behavior
test_lock_timeout() {
    log "INFO" "Test 5: Lock timeout behavior"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init timeout_test >/dev/null 2>&1
    
    # Start a process that holds a lock for a while
    (
        # This process will try to get a number but get interrupted
        "$NUMBER_MANAGER_SCRIPT" get timeout_test >/dev/null 2>&1 &
        sleep 2  # Hold for 2 seconds
        kill $! 2>/dev/null || true
    ) &
    local holder_pid=$!
    
    # Immediately try another process (should wait or timeout)
    local start_time=$(date +%s)
    local num
    num=$("$NUMBER_MANAGER_SCRIPT" get timeout_test 2>/dev/null | tail -1)
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Wait for holder process
    wait "$holder_pid" 2>/dev/null || true
    
    # Check behavior
    if [ $? -eq 0 ] && [ -n "$num" ]; then
        log "SUCCESS" "Lock timeout handled gracefully, got number $num in ${duration}s"
    else
        log "WARNING" "Lock may have timed out (duration: ${duration}s)"
    fi
    
    return 0
}

# Test 6: Process interruption during assignment
test_process_interruption() {
    log "INFO" "Test 6: Process interruption during assignment"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init interrupt_test >/dev/null 2>&1
    
    # Start multiple processes and interrupt some
    local pids=()
    for i in {1..10}; do
        (
            for j in {1..5}; do
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get interrupt_test 2>/dev/null | tail -1)
                if [ $? -eq 0 ]; then
                    echo "$num" >> "$TEST_STATE_DIR/interrupt_success.txt"
                fi
                
                # Randomly interrupt some processes
                if [ $((RANDOM % 10)) -eq 0 ]; then
                    break
                fi
                sleep 0.1
            done
        ) &
        pids+=($!)
    done
    
    # Let them run for a bit, then interrupt some
    sleep 0.5
    for i in {1..3}; do
        if [ ${#pids[@]} -gt $i ]; then
            kill "${pids[$i]}" 2>/dev/null || true
        fi
    done
    
    # Wait for remaining processes
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Collect successful assignments
    local all_numbers=()
    if [ -f "$TEST_STATE_DIR/interrupt_success.txt" ]; then
        while read -r num; do
            all_numbers+=("$num")
        done < "$TEST_STATE_DIR/interrupt_success.txt"
    fi
    
    # Verify uniqueness despite interruptions
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Duplicates found after interruption: $duplicate_count"
        return 1
    fi
    
    log "SUCCESS" "Process interruption handled: ${#all_numbers[@]} successful assignments"
    return 0
}

# Test 7: Lock file cleanup after crash
test_lock_cleanup() {
    log "INFO" "Test 7: Lock file cleanup after crash"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init cleanup_test >/dev/null 2>&1
    
    # Create a stale lock file
    local lock_file="$TEST_STATE_DIR/.number_state/.lock"
    echo "99999:$(($(date +%s) - 3600))" > "$lock_file"  # Old timestamp
    
    # Try to get a number (should clean up stale lock)
    local num
    num=$("$NUMBER_MANAGER_SCRIPT" get cleanup_test 2>/dev/null | tail -1)
    if [ $? -eq 0 ] && [ -n "$num" ]; then
        log "SUCCESS" "Stale lock cleaned up successfully, got number $num"
    else
        log "ERROR" "Failed to clean up stale lock"
        return 1
    fi
    
    return 0
}

# Test 8: Performance under concurrency
test_concurrent_performance() {
    log "INFO" "Test 8: Performance under concurrency"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init perf_test >/dev/null 2>&1
    
    # Measure performance with concurrent access
    local start_time=$(date +%s.%N)
    local pids=()
    local process_count=15
    local assignments_per_process=4
    
    for i in $(seq 1 $process_count); do
        (
            for j in $(seq 1 $assignments_per_process); do
                "$NUMBER_MANAGER_SCRIPT" get perf_test >/dev/null 2>&1
            done
        ) &
        pids+=($!)
    done
    
    # Wait for completion
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
    
    local end_time=$(date +%s.%N)
    local duration
    duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "N/A")
    
    local total_assignments=$((process_count * assignments_per_process))
    
    if command -v bc >/dev/null 2>&1 && [ "$duration" != "N/A" ]; then
        local avg_time
        avg_time=$(echo "scale=3; $duration / $total_assignments" | bc -l)
        log "SUCCESS" "Performance: $total_assignments assignments in ${duration}s (avg: ${avg_time}s per assignment)"
    else
        log "SUCCESS" "Performance: $total_assignments assignments completed"
    fi
    
    return 0
}

# Run all tests
run_all_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_basic_concurrent_assignment"
        "test_high_frequency_concurrent"
        "test_mixed_contexts_concurrent"
        "test_stress_concurrent"
        "test_lock_timeout"
        "test_process_interruption"
        "test_lock_cleanup"
        "test_concurrent_performance"
    )
    
    for test_func in "${tests[@]}"; do
        test_count=$((test_count + 1))
        echo ""
        echo "=========================================="
        echo "Running $test_func"
        echo "=========================================="
        
        if $test_func; then
            pass_count=$((pass_count + 1))
            echo "✅ $test_func PASSED"
        else
            echo "❌ $test_func FAILED"
        fi
    done
    
    echo ""
    echo "=========================================="
    echo "Concurrent Assignment Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All concurrent assignment tests passed!"
        return 0
    else
        log "ERROR" "Some concurrent assignment tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests concurrent number assignment functionality"
    exit 1
fi