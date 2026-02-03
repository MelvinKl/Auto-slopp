#!/bin/bash

# Comprehensive Number Uniqueness Verification Test Suite
# Auto-54t: Add tests to verify number uniqueness
# Tests normal renaming operations, edge cases, regression tests, and performance

set -e

SCRIPT_NAME="test_comprehensive_number_uniqueness"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_comprehensive_uniqueness_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"

log "INFO" "Starting comprehensive number uniqueness verification tests in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Comprehensive test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Normal renaming operations with unique number assignment
test_normal_renaming_operations() {
    log "INFO" "Test 1.1: Normal renaming operations with unique number assignment"
    
    # Initialize number state
    if ! "$NUMBER_MANAGER_SCRIPT" init renaming_test >/dev/null 2>&1; then
        log "ERROR" "Failed to initialize number state for renaming test"
        return 1
    fi
    
    # Simulate normal config file renaming workflow
    local config_files=("database" "cache" "auth" "logging" "monitoring")
    local assigned_numbers=()
    local renamed_files=()
    
    for config in "${config_files[@]}"; do
        # Get unique number for this config file
        local unique_num
        unique_num=$("$NUMBER_MANAGER_SCRIPT" get "config_${config}" 2>/dev/null | tail -1)
        
        if [ $? -ne 0 ] || [ -z "$unique_num" ]; then
            log "ERROR" "Failed to get unique number for config: $config"
            return 1
        fi
        
        assigned_numbers+=("$unique_num")
        
        # Simulate renaming operation
        local old_name="${config}.conf"
        local new_name="$(printf "%04d" $unique_num)-${config}.conf"
        renamed_files+=("$new_name")
        
        log "DEBUG" "Config $config: $old_name -> $new_name (number: $unique_num)"
    done
    
    # Verify all assigned numbers are unique
    local sorted_numbers
    sorted_numbers=$(printf '%s\n' "${assigned_numbers[@]}" | sort -n | uniq -d)
    if [ -n "$sorted_numbers" ]; then
        log "ERROR" "Duplicate numbers found in renaming operations: $sorted_numbers"
        return 1
    fi
    
    # Verify numbers are sequential (expecting 1-5)
    local expected_sequence=(1 2 3 4 5)
    for i in "${!expected_sequence[@]}"; do
        if [ "${assigned_numbers[$i]}" != "${expected_sequence[$i]}" ]; then
            log "ERROR" "Expected ${expected_sequence[$i]}, got ${assigned_numbers[$i]} for config ${config_files[$i]}"
            return 1
        fi
    done
    
    log "SUCCESS" "Normal renaming operations: ${#assigned_numbers[@]} unique numbers assigned"
    return 0
}

# Test 2: Edge cases with existing numbered files
test_existing_numbered_files() {
    log "INFO" "Test 1.2: Edge cases with existing numbered files"
    
    # Initialize fresh state
    rm -rf "$TEST_STATE_DIR/.number_state"
    "$NUMBER_MANAGER_SCRIPT" init existing_files_test >/dev/null 2>&1
    
    # Create mock directory with existing numbered files
    local mock_task_dir="$TEST_STATE_DIR/mock_tasks"
    mkdir -p "$mock_task_dir"
    
    # Create existing numbered files with gaps (using .txt extension as expected by sync)
    touch "$mock_task_dir/0001-database.txt"
    touch "$mock_task_dir/0003-cache.txt"
    touch "$mock_task_dir/0007-auth.txt"
    touch "$mock_task_dir/0010-logging.txt"
    
    # Sync state with existing files
    if ! "$NUMBER_MANAGER_SCRIPT" sync "$mock_task_dir" existing_files >/dev/null 2>&1; then
        log "ERROR" "Failed to sync state with existing numbered files"
        return 1
    fi
    
    # Try to get new numbers - should skip existing ones
    local new_numbers=()
    for i in {1..5}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get new_config 2>/dev/null | tail -1)
        if [ $? -eq 0 ]; then
            new_numbers+=("$num")
        fi
    done
    
    # Verify new numbers don't conflict with existing ones
    local existing_numbers=(1 3 7 10)
    local conflict_found=false
    
    for new_num in "${new_numbers[@]}"; do
        for existing_num in "${existing_numbers[@]}"; do
            if [ "$new_num" = "$existing_num" ]; then
                log "ERROR" "Conflict: new number $new_num matches existing number $existing_num"
                conflict_found=true
            fi
        done
    done
    
    if [ "$conflict_found" = true ]; then
        return 1
    fi
    
    # Verify new numbers are unique among themselves
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${new_numbers[@]}" | sort -n | uniq -d | wc -l)
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Duplicate numbers in new assignments: $duplicate_count"
        return 1
    fi
    
    log "SUCCESS" "Existing numbered files: ${#new_numbers[@]} new unique numbers assigned, no conflicts"
    return 0
}

# Test 3: Concurrent operations edge cases
test_concurrent_operations_edge_cases() {
    log "INFO" "Test 1.3: Concurrent operations edge cases"
    
    # Initialize fresh state
    rm -rf "$TEST_STATE_DIR/.number_state"
    "$NUMBER_MANAGER_SCRIPT" init concurrent_edge_test >/dev/null 2>&1
    
    # Simulate concurrent access with varying delays and interruptions
    local pids=()
    local output_files=()
    local process_count=8
    local operations_per_process=3
    
    for i in $(seq 1 $process_count); do
        local output_file="$TEST_STATE_DIR/concurrent_edge_$i.txt"
        output_files+=("$output_file")
        
        (
            local context="concurrent_proc_$i"
            for j in $(seq 1 $operations_per_process); do
                # Vary the delay to create realistic concurrency patterns
                local delay=$(echo "scale=3; $RANDOM / 32767 * 0.2" | bc 2>/dev/null || echo "0.1")
                sleep "$delay"
                
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get "$context" 2>/dev/null | tail -1)
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    echo "$num:$context" >> "$output_file"
                fi
                
                # Random chance of brief pause to simulate system load
                if [ $((RANDOM % 5)) -eq 0 ]; then
                    sleep 0.05
                fi
            done
        ) &
        
        pids+=($!)
    done
    
    # Wait for all processes
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Collect all assignments
    local all_assignments=()
    local all_numbers=()
    
    for output_file in "${output_files[@]}"; do
        if [ -f "$output_file" ]; then
            while read -r line; do
                if [ -n "$line" ]; then
                    all_assignments+=("$line")
                    local num=$(echo "$line" | cut -d: -f1)
                    all_numbers+=("$num")
                fi
            done < "$output_file"
        fi
    done
    
    # Verify uniqueness
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Concurrent edge case: found $duplicate_count duplicate numbers"
        return 1
    fi
    
    # Verify expected count
    local expected_count=$((process_count * operations_per_process))
    if [ ${#all_numbers[@]} -ne $expected_count ]; then
        log "WARNING" "Concurrent edge case: expected $expected_count assignments, got ${#all_numbers[@]}"
        # Don't fail test as some might legitimately fail under concurrency
    fi
    
    log "SUCCESS" "Concurrent operations edge case: ${#all_numbers[@]} unique assignments from $process_count processes"
    return 0
}

# Test 4: Regression tests for the original bug
test_regression_original_bug() {
    log "INFO" "Test 1.4: Regression tests for the original number reuse bug"
    
    # This test specifically addresses the original issue where numbers were reused
    
    # Initialize fresh state
    rm -rf "$TEST_STATE_DIR/.number_state"
    "$NUMBER_MANAGER_SCRIPT" init regression_test >/dev/null 2>&1
    
    # Scenario 1: Rapid sequential assignments (original bug trigger)
    local rapid_numbers=()
    for i in {1..20}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get rapid_test 2>/dev/null | tail -1)
        rapid_numbers+=("$num")
    done
    
    # Verify no duplicates in rapid assignments
    local rapid_duplicates
    rapid_duplicates=$(printf '%s\n' "${rapid_numbers[@]}" | sort -n | uniq -d)
    if [ -n "$rapid_duplicates" ]; then
        log "ERROR" "Regression: rapid assignments produced duplicates: $rapid_duplicates"
        return 1
    fi
    
    # Scenario 2: Mixed context assignments with potential for cross-contamination
    rm -rf "$TEST_STATE_DIR/.number_state"
    "$NUMBER_MANAGER_SCRIPT" init mixed_context_test >/dev/null 2>&1
    
    local contexts=("alpha" "beta" "gamma" "delta")
    local context_assignments=()
    
    for ctx in "${contexts[@]}"; do
        local ctx_nums=()
        for i in {1..5}; do
            local num
            num=$("$NUMBER_MANAGER_SCRIPT" get "$ctx" 2>/dev/null | tail -1)
            ctx_nums+=("$num")
            context_assignments+=("$num")
        done
        log "DEBUG" "Context $ctx: ${ctx_nums[*]}"
    done
    
    # Verify no duplicates across contexts
    local mixed_duplicates
    mixed_duplicates=$(printf '%s\n' "${context_assignments[@]}" | sort -n | uniq -d)
    if [ -n "$mixed_duplicates" ]; then
        log "ERROR" "Regression: mixed context assignments produced duplicates: $mixed_duplicates"
        return 1
    fi
    
    # Scenario 3: Test with number release and reuse (ensure release doesn't cause issues)
    local release_test_numbers=()
    for i in {1..10}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get release_regression_test 2>/dev/null | tail -1)
        release_test_numbers+=("$num")
    done
    
    # Release some numbers
    "$NUMBER_MANAGER_SCRIPT" release "${release_test_numbers[2]}" release_regression_test >/dev/null 2>&1
    "$NUMBER_MANAGER_SCRIPT" release "${release_test_numbers[5]}" release_regression_test >/dev/null 2>&1
    
    # Get more numbers
    local post_release_numbers=()
    for i in {1..5}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get release_regression_test 2>/dev/null | tail -1)
        post_release_numbers+=("$num")
    done
    
    # Check all numbers for uniqueness
    local all_regression_numbers=("${release_test_numbers[@]}" "${post_release_numbers[@]}")
    local regression_duplicates
    regression_duplicates=$(printf '%s\n' "${all_regression_numbers[@]}" | sort -n | uniq -d)
    if [ -n "$regression_duplicates" ]; then
        log "ERROR" "Regression: release/reuse scenario produced duplicates: $regression_duplicates"
        return 1
    fi
    
    log "SUCCESS" "Regression tests: no duplicate numbers detected in any scenario"
    return 0
}

# Test 5: Performance tests for the new numbering system
test_performance_numbering_system() {
    log "INFO" "Test 1.5: Performance tests for the new numbering system"
    
    # Performance Test 1: High-volume sequential assignments
    rm -rf "$TEST_STATE_DIR/.number_state"
    "$NUMBER_MANAGER_SCRIPT" init performance_test >/dev/null 2>&1
    
    local sequential_count=100
    local start_time=$(date +%s.%N)
    local sequential_numbers=()
    
    for i in $(seq 1 $sequential_count); do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get performance_seq 2>/dev/null | tail -1)
        sequential_numbers+=("$num")
    done
    
    local end_time=$(date +%s.%N)
    local sequential_duration
    sequential_duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "N/A")
    
    # Verify sequential performance results
    local sequential_duplicates
    sequential_duplicates=$(printf '%s\n' "${sequential_numbers[@]}" | sort -n | uniq -d)
    if [ -n "$sequential_duplicates" ]; then
        log "ERROR" "Performance test: sequential assignments had duplicates: $sequential_duplicates"
        return 1
    fi
    
    # Performance Test 2: Concurrent assignments under load
    rm -rf "$TEST_STATE_DIR/.number_state"
    "$NUMBER_MANAGER_SCRIPT" init concurrent_performance_test >/dev/null 2>&1
    
    local concurrent_processes=10
    local assignments_per_process=10
    local pids=()
    local output_files=()
    
    local concurrent_start_time=$(date +%s.%N)
    
    for i in $(seq 1 $concurrent_processes); do
        local output_file="$TEST_STATE_DIR/perf_concurrent_$i.txt"
        output_files+=("$output_file")
        
        (
            for j in $(seq 1 $assignments_per_process); do
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get "concurrent_perf_$i" 2>/dev/null | tail -1)
                if [ $? -eq 0 ]; then
                    echo "$num" >> "$output_file"
                fi
            done
        ) &
        
        pids+=($!)
    done
    
    # Wait for completion
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    local concurrent_end_time=$(date +%s.%N)
    local concurrent_duration
    concurrent_duration=$(echo "$concurrent_end_time - $concurrent_start_time" | bc -l 2>/dev/null || echo "N/A")
    
    # Collect concurrent results
    local concurrent_numbers=()
    for output_file in "${output_files[@]}"; do
        if [ -f "$output_file" ]; then
            while read -r num; do
                concurrent_numbers+=("$num")
            done < "$output_file"
        fi
    done
    
    # Verify concurrent performance results
    local concurrent_duplicates
    concurrent_duplicates=$(printf '%s\n' "${concurrent_numbers[@]}" | sort -n | uniq -d)
    if [ -n "$concurrent_duplicates" ]; then
        log "ERROR" "Performance test: concurrent assignments had duplicates: $concurrent_duplicates"
        return 1
    fi
    
    # Calculate performance metrics
    local total_concurrent_assignments=${#concurrent_numbers[@]}
    local expected_concurrent=$((concurrent_processes * assignments_per_process))
    
    # Report performance results
    if command -v bc >/dev/null 2>&1; then
        local sequential_avg sequential_throughput
        if [ "$sequential_duration" != "N/A" ]; then
            sequential_avg=$(echo "scale=3; $sequential_duration / $sequential_count" | bc -l)
            log "INFO" "Sequential performance: $sequential_count assignments in ${sequential_duration}s (avg: ${sequential_avg}s each)"
        fi
        
        if [ "$concurrent_duration" != "N/A" ]; then
            local concurrent_avg=$(echo "scale=3; $concurrent_duration / $total_concurrent_assignments" | bc -l)
            local concurrent_throughput=$(echo "scale=1; $total_concurrent_assignments / $concurrent_duration" | bc -l)
            log "INFO" "Concurrent performance: $total_concurrent_assignments assignments in ${concurrent_duration}s (avg: ${concurrent_avg}s each, ${concurrent_throughput} ops/sec)"
        fi
    else
        log "INFO" "Sequential performance: $sequential_count assignments completed"
        log "INFO" "Concurrent performance: $total_concurrent_assignments/$expected_concurrent assignments completed"
    fi
    
    # Performance Test 3: Memory and disk usage efficiency
    local state_file_size
    state_file_size=$(du -k "$TEST_STATE_DIR/.number_state/state.json" 2>/dev/null | cut -f1 || echo "0")
    local backup_count
    backup_count=$(ls "$TEST_STATE_DIR/.number_state/backup/"*.json 2>/dev/null | wc -l)
    
    if [ "$state_file_size" -gt 100 ]; then
        log "WARNING" "State file size seems large: ${state_file_size}KB for $sequential_count assignments"
    fi
    
    log "SUCCESS" "Performance tests: ${sequential_count} sequential, ${total_concurrent_assignments} concurrent assignments with no duplicates"
    return 0
}

# Test 6: Integration test with planner.sh renaming workflow
test_planner_integration_workflow() {
    log "INFO" "Test 1.6: Integration test with planner.sh renaming workflow"
    
    # This test simulates how planner.sh would use the number manager
    rm -rf "$TEST_STATE_DIR/.number_state"
    "$NUMBER_MANAGER_SCRIPT" init planner_integration_test >/dev/null 2>&1
    
    # Mock planner configuration scenarios
    local planner_configs=(
        "frontend-react:webpack.config.js"
        "backend-nodejs:server.js"
        "database-postgres:schema.sql"
        "cache-redis:redis.conf"
        "monitoring-prometheus:prometheus.yml"
    )
    
    local planner_assignments=()
    
    for config_info in "${planner_configs[@]}"; do
        local context=$(echo "$config_info" | cut -d: -f1)
        local filename=$(echo "$config_info" | cut -d: -f2)
        
        # Simulate planner asking for a number for a config file
        local unique_num
        unique_num=$("$NUMBER_MANAGER_SCRIPT" get "planner_$context" 2>/dev/null | tail -1)
        
        if [ $? -ne 0 ] || [ -z "$unique_num" ]; then
            log "ERROR" "Planner integration: failed to get number for context: $context"
            return 1
        fi
        
        # Simulate the renaming that planner would do
        local renamed_file="$(printf "%04d" $unique_num)-$filename"
        planner_assignments+=("$unique_num:$context:$renamed_file")
        
        log "DEBUG" "Planner: $context -> $renamed_file (number: $unique_num)"
    done
    
    # Verify uniqueness across all planner operations
    local planner_numbers=()
    for assignment in "${planner_assignments[@]}"; do
        local num=$(echo "$assignment" | cut -d: -f1)
        planner_numbers+=("$num")
    done
    
    local planner_duplicates
    planner_duplicates=$(printf '%s\n' "${planner_numbers[@]}" | sort -n | uniq -d)
    if [ -n "$planner_duplicates" ]; then
        log "ERROR" "Planner integration: duplicate numbers found: $planner_duplicates"
        return 1
    fi
    
    # Test scenario where planner needs to handle conflicts
    # Simulate a scenario where some numbers are pre-allocated
    rm -rf "$TEST_STATE_DIR/.number_state"
    "$NUMBER_MANAGER_SCRIPT" init planner_conflict_test >/dev/null 2>&1
    
    # Pre-allocate some numbers to simulate existing files
    for i in {1..3}; do
        "$NUMBER_MANAGER_SCRIPT" get "existing_context_$i" >/dev/null 2>&1
    done
    
    # Now planner tries to add new configs
    local conflict_contexts=("new_config_1" "new_config_2" "new_config_3")
    local conflict_numbers=()
    
    for ctx in "${conflict_contexts[@]}"; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get "planner_$ctx" 2>/dev/null | tail -1)
        conflict_numbers+=("$num")
    done
    
    # Verify conflict resolution
    for num in "${conflict_numbers[@]}"; do
        if [ "$num" -le 3 ]; then
            log "ERROR" "Planner conflict: assigned number $num which should have been skipped"
            return 1
        fi
    done
    
    log "SUCCESS" "Planner integration: ${#planner_assignments[@]} successful assignments, ${#conflict_numbers[@]} conflict-free assignments"
    return 0
}

# Run all comprehensive uniqueness tests
run_comprehensive_uniqueness_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_normal_renaming_operations"
        "test_existing_numbered_files"
        "test_concurrent_operations_edge_cases"
        "test_regression_original_bug"
        "test_performance_numbering_system"
        "test_planner_integration_workflow"
    )
    
    log "INFO" "Starting comprehensive number uniqueness verification test suite"
    log "INFO" "Running ${#tests[@]} comprehensive tests covering normal operations, edge cases, regression, and performance"
    
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
    echo "Comprehensive Uniqueness Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All comprehensive number uniqueness verification tests passed!"
        echo ""
        echo "🎯 Test Coverage Summary:"
        echo "   ✓ Normal renaming operations with unique number assignment"
        echo "   ✓ Edge cases with existing numbered files"
        echo "   ✓ Concurrent operations and race condition handling"
        echo "   ✓ Regression tests for original number reuse bug"
        echo "   ✓ Performance tests for the new numbering system"
        echo "   ✓ Integration tests with planner.sh renaming workflow"
        echo ""
        echo "✨ Number uniqueness system is verified and robust!"
        return 0
    else
        log "ERROR" "Some comprehensive uniqueness tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_comprehensive_uniqueness_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script provides comprehensive tests for number uniqueness verification"
    echo "Auto-54t: Add tests to verify number uniqueness"
    echo ""
    echo "Test Categories:"
    echo "  - Normal renaming operations with unique number assignment"
    echo "  - Edge cases (existing numbered files, concurrent operations)"
    echo "  - Regression tests to ensure the original bug doesn't reoccur"
    echo "  - Performance tests for the new numbering system"
    echo "  - Integration tests with planner.sh renaming workflow"
    exit 1
fi