#!/bin/bash

# Test concurrent stress testing with high-load scenarios
# Part of Auto-58z: Test concurrent access and race condition handling

set -e

SCRIPT_NAME="test_concurrent_stress"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_concurrent_stress_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting concurrent stress test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Stress test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Extreme load test - 100+ concurrent processes
test_extreme_load() {
    log "INFO" "Test 1: Extreme load test - 100+ concurrent processes"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init extreme_load >/dev/null 2>&1
    
    # Start 100 concurrent processes
    local pids=()
    local output_files=()
    local process_count=100
    local assignments_per_process=5
    local expected_total=$((process_count * assignments_per_process))
    
    log "INFO" "Starting $process_count processes with $assignments_per_process assignments each"
    
    for i in $(seq 1 $process_count); do
        local output_file="$TEST_STATE_DIR/extreme_$i.txt"
        output_files+=("$output_file")
        
        (
            for j in $(seq 1 $assignments_per_process); do
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get extreme_load 2>/dev/null | tail -1)
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "$num" >> "$output_file"
                fi
                # Minimal delay to maximize contention
                sleep 0.001
            done
        ) &
        
        pids+=($!)
        
        # Batch process starts to avoid overwhelming the system
        if [ $((i % 10)) -eq 0 ]; then
            sleep 0.01
        fi
    done
    
    # Wait for all processes with timeout
    local timeout=60
    local elapsed=0
    local remaining_pids=${#pids[@]}
    
    while [ $remaining_pids -gt 0 ] && [ $elapsed -lt $timeout ]; do
        sleep 1
        elapsed=$((elapsed + 1))
        
        # Check completed processes
        local completed=0
        for pid in "${pids[@]}"; do
            if ! kill -0 "$pid" 2>/dev/null; then
                completed=$((completed + 1))
            fi
        done
        remaining_pids=$((remaining_pids - completed))
        
        log "INFO" "Progress: $((process_count - remaining_pids))/$process_count completed"
    done
    
    # Force kill any remaining processes
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done
    wait 2>/dev/null || true
    
    # Collect results
    local all_numbers=()
    local total_files=0
    
    for output_file in "${output_files[@]}"; do
        if [ -f "$output_file" ]; then
            total_files=$((total_files + 1))
            while read -r num; do
                if [ -n "$num" ]; then
                    all_numbers+=("$num")
                fi
            done < "$output_file"
        fi
    done
    
    log "INFO" "Collected ${#all_numbers[@]} numbers from $total_files files"
    
    # Verify results
    if [ ${#all_numbers[@]} -lt $((expected_total / 2)) ]; then
        log "ERROR" "Too few assignments: ${#all_numbers[@]} (expected at least $((expected_total / 2)))"
        return 1
    fi
    
    # Check for duplicates (critical test)
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "EXTREME LOAD TEST FAILED: $duplicate_count duplicates found!"
        printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | head -10
        return 1
    fi
    
    log "SUCCESS" "Extreme load test: ${#all_numbers[@]} unique numbers, 0 duplicates"
    return 0
}

# Test 2: Resource exhaustion testing
test_resource_exhaustion() {
    log "INFO" "Test 2: Resource exhaustion testing"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init resource_exhaustion >/dev/null 2>&1
    
    # Consume file descriptors
    local temp_files=()
    for i in {1..50}; do
        local temp_file="$TEST_STATE_DIR/temp_$i.tmp"
        exec 3<"$temp_file" 2>/dev/null || true
        temp_files+=("$temp_file")
    done
    
    # Try concurrent operations under resource pressure
    local pids=()
    local process_count=20
    
    for i in $(seq 1 $process_count); do
        (
            for j in {1..3}; do
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get resource_exhaustion 2>/dev/null | tail -1)
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "$num" >> "$TEST_STATE_DIR/exhaustion_$i.txt"
                fi
                sleep 0.1
            done
        ) &
        pids+=($!)
    done
    
    # Wait for completion
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Clean up file descriptors
    for i in {1..50}; do
        exec 3<&- 2>/dev/null || true
    done
    
    # Verify results
    local all_numbers=()
    for i in $(seq 1 $process_count); do
        local file="$TEST_STATE_DIR/exhaustion_$i.txt"
        if [ -f "$file" ]; then
            while read -r num; do
                all_numbers+=("$num")
            done < "$file"
        fi
    done
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Resource exhaustion test failed: $duplicate_count duplicates"
        return 1
    fi
    
    log "SUCCESS" "Resource exhaustion test: ${#all_numbers[@]} unique numbers under resource pressure"
    return 0
}

# Test 3: Long-running operations with lock holding
test_long_running_operations() {
    log "INFO" "Test 3: Long-running operations with lock holding"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init long_running >/dev/null 2>&1
    
    # Start a process that will hold locks longer
    (
        for i in {1..5}; do
            # Simulate long operation
            "$NUMBER_MANAGER_SCRIPT" get long_running >/dev/null 2>&1
            sleep 0.5  # Hold state longer than usual
        done
    ) &
    local long_pid=$!
    
    # Start other processes that should wait or timeout
    local pids=()
    for i in {1..10}; do
        (
            for j in {1..2}; do
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get long_running 2>/dev/null | tail -1)
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "$num" >> "$TEST_STATE_DIR/long_$i.txt"
                fi
                sleep 0.1
            done
        ) &
        pids+=($!)
    done
    
    # Wait for all processes
    wait "$long_pid" 2>/dev/null || true
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Verify no duplicates despite long operations
    local all_numbers=()
    for i in {1..10}; do
        local file="$TEST_STATE_DIR/long_$i.txt"
        if [ -f "$file" ]; then
            while read -r num; do
                all_numbers+=("$num")
            done < "$file"
        fi
    done
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Long-running operations test failed: $duplicate_count duplicates"
        return 1
    fi
    
    log "SUCCESS" "Long-running operations test: ${#all_numbers[@]} unique numbers"
    return 0
}

# Test 4: Memory pressure testing
test_memory_pressure() {
    log "INFO" "Test 4: Memory pressure testing"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init memory_pressure >/dev/null 2>&1
    
    # Create memory pressure
    (
        # Allocate some memory
        local mem_hog=()
        for i in {1..1000}; do
            mem_hog+=("$(printf '%80s' '' | tr ' ' 'X')")
        done
        
        # Run concurrent operations under memory pressure
        for j in {1..3}; do
            local num
            num=$("$NUMBER_MANAGER_SCRIPT" get memory_pressure 2>/dev/null | tail -1)
            if [ $? -eq 0 ] && [ -n "$num" ]; then
                echo "$num" >> "$TEST_STATE_DIR/memory_$$.txt"
            fi
            sleep 0.1
        done
    ) &
    local mem_pid=$!
    
    # Start other concurrent processes
    local pids=()
    for i in {1..15}; do
        (
            for j in {1..2}; do
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get memory_pressure 2>/dev/null | tail -1)
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "$num" >> "$TEST_STATE_DIR/mem_pressure_$i.txt"
                fi
                sleep 0.05
            done
        ) &
        pids+=($!)
    done
    
    # Wait for completion
    wait "$mem_pid" 2>/dev/null || true
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Verify results
    local all_numbers=()
    for i in {1..15}; do
        local file="$TEST_STATE_DIR/mem_pressure_$i.txt"
        if [ -f "$file" ]; then
            while read -r num; do
                all_numbers+=("$num")
            done < "$file"
        fi
    done
    
    # Add memory process results
    if [ -f "$TEST_STATE_DIR/memory_$$.txt" ]; then
        while read -r num; do
            all_numbers+=("$num")
        done < "$TEST_STATE_DIR/memory_$$.txt"
    fi
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Memory pressure test failed: $duplicate_count duplicates"
        return 1
    fi
    
    log "SUCCESS" "Memory pressure test: ${#all_numbers[@]} unique numbers under memory pressure"
    return 0
}

# Test 5: Performance benchmark under stress
test_performance_benchmark() {
    log "INFO" "Test 5: Performance benchmark under stress"
    
    # Initialize
    "$NUMBER_MANAGER_SCRIPT" init performance >/dev/null 2>&1
    
    # Benchmark with increasing load
    local loads=(10 25 50 75)
    
    for load in "${loads[@]}"; do
        log "INFO" "Benchmarking with $load concurrent processes"
        
        local start_time=$(date +%s.%N)
        local pids=()
        
        for i in $(seq 1 $load); do
            (
                for j in {1..2}; do
                    "$NUMBER_MANAGER_SCRIPT" get performance >/dev/null 2>&1
                done
            ) &
            pids+=($!)
        done
        
        # Wait for completion
        for pid in "${pids[@]}"; do
            wait "$pid" 2>/dev/null || true
        done
        
        local end_time=$(date +%s.%N)
        local duration
        duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "N/A")
        
        local total_operations=$((load * 2))
        
        if command -v bc >/dev/null 2>&1 && [ "$duration" != "N/A" ]; then
            local ops_per_sec
            ops_per_sec=$(echo "scale=2; $total_operations / $duration" | bc -l)
            log "INFO" "Load $load: $total_operations ops in ${duration}s (${ops_per_sec} ops/sec)"
        else
            log "INFO" "Load $load: $total_operations operations completed"
        fi
        
        # Brief pause between benchmarks
        sleep 1
    done
    
    log "SUCCESS" "Performance benchmark completed"
    return 0
}

# Run all stress tests
run_all_stress_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_extreme_load"
        "test_resource_exhaustion"
        "test_long_running_operations"
        "test_memory_pressure"
        "test_performance_benchmark"
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
    echo "Concurrent Stress Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All concurrent stress tests passed!"
        return 0
    else
        log "ERROR" "Some concurrent stress tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_stress_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests concurrent stress scenarios with high load"
    exit 1
fi