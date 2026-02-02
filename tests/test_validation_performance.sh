#!/bin/bash

# Test Validation Performance with Large Datasets
# Tests the performance characteristics of validation operations
# Includes timing analysis and memory usage monitoring

SCRIPT_NAME="test_validation_performance"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_validation_performance_$$"
TEST_TASK_DIR="$TEST_STATE_DIR/tasks"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$BASE_DIR/scripts/number_manager.sh"

# Performance tracking
TESTS_RUN=0
TESTS_PASSED=0
PERFORMANCE_RESULTS=()

# Performance thresholds (in seconds)
SMALL_DATASET_THRESHOLD=1.0     # 100 files
MEDIUM_DATASET_THRESHOLD=5.0    # 1000 files  
LARGE_DATASET_THRESHOLD=20.0   # 5000 files
HUGE_DATASET_THRESHOLD=60.0     # 10000 files

log "INFO" "Starting validation performance tests in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Test cleanup completed"
}

trap cleanup_test EXIT

# Performance measurement helper
measure_performance() {
    local test_name="$1"
    local dataset_size="$2"
    local setup_command="$3"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo ""
    echo "=========================================="
    echo "Performance Test: $test_name ($dataset_size files)"
    echo "=========================================="
    
    # Setup test data
    eval "$setup_command"
    
    # Measure validation time
    local start_time=$(date +%s.%N)
    local validation_output
    validation_output=$("$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" 2>&1)
    local end_time=$(date +%s.%N)
    
    # Calculate duration
    local duration=$(echo "$end_time - $start_time" | bc -l)
    local duration_rounded=$(printf "%.2f" "$duration")
    
    echo "Dataset size: $dataset_size files"
    echo "Validation time: ${duration_rounded}s"
    echo "Validation result: $(echo "$validation_output" | tail -1)"
    
    # Store performance result
    PERFORMANCE_RESULTS+=("$test_name:$dataset_size:$duration_rounded")
    
    # Check against thresholds
    local threshold
    case $dataset_size in
        100) threshold=$SMALL_DATASET_THRESHOLD ;;
        1000) threshold=$MEDIUM_DATASET_THRESHOLD ;;
        5000) threshold=$LARGE_DATASET_THRESHOLD ;;
        10000) threshold=$HUGE_DATASET_THRESHOLD ;;
        *) threshold=999999 ;;
    esac
    
    local comparison=$(echo "$duration <= $threshold" | bc -l)
    if [ "$comparison" = "1" ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo "✅ $test_name PASSED (within ${threshold}s threshold)"
        return 0
    else
        echo "❌ $test_name FAILED (exceeded ${threshold}s threshold)"
        return 1
    fi
}

# Setup test environment
setup_test_env() {
    rm -rf "$TEST_STATE_DIR"
    mkdir -p "$TEST_TASK_DIR"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init "test_context" >/dev/null 2>&1
}

# Create dataset with specified size
create_dataset() {
    local size="$1"
    local inconsistency_ratio="${2:-0.0}"  # 0.0 = perfect consistency, 0.1 = 10% inconsistencies
    
    log "INFO" "Creating dataset with $size files (inconsistency ratio: $inconsistency_ratio)"
    
    # Create numbered files
    for i in $(seq 1 "$size"); do
        local num=$(printf "%04d" $i)
        touch "$TEST_TASK_DIR/${num}-task${i}.txt"
    done
    
    # Assign numbers in state (with some inconsistencies if specified)
    local state_count
    state_count=$(echo "$size * (1 - $inconsistency_ratio)" | bc -l)
    state_count=${state_count%.*}  # Convert to integer
    
    for i in $(seq 1 "$state_count"); do
        "$NUMBER_MANAGER_SCRIPT" get "test_context" >/dev/null 2>&1
    done
    
    echo "Created $size files, assigned $state_count numbers in state"
}

# Performance Test 1: Small dataset (100 files, perfect consistency)
test_small_dataset_perfect() {
    setup_test_env
    measure_performance "Small Dataset Perfect" 100 "create_dataset 100 0.0"
}

# Performance Test 2: Medium dataset (1000 files, perfect consistency)
test_medium_dataset_perfect() {
    setup_test_env
    measure_performance "Medium Dataset Perfect" 1000 "create_dataset 1000 0.0"
}

# Performance Test 3: Large dataset (5000 files, perfect consistency)
test_large_dataset_perfect() {
    setup_test_env
    measure_performance "Large Dataset Perfect" 5000 "create_dataset 5000 0.0"
}

# Performance Test 4: Huge dataset (10000 files, perfect consistency)
test_huge_dataset_perfect() {
    setup_test_env
    measure_performance "Huge Dataset Perfect" 10000 "create_dataset 10000 0.0"
}

# Performance Test 5: Medium dataset with inconsistencies (1000 files, 10% inconsistencies)
test_medium_dataset_inconsistencies() {
    setup_test_env
    measure_performance "Medium Dataset with Inconsistencies" 1000 "create_dataset 1000 0.1"
}

# Performance Test 6: Large dataset with inconsistencies (5000 files, 20% inconsistencies)
test_large_dataset_inconsistencies() {
    setup_test_env
    measure_performance "Large Dataset with Inconsistencies" 5000 "create_dataset 5000 0.2"
}

# Performance Test 7: Memory usage test (monitor peak memory)
test_memory_usage() {
    setup_test_env
    echo "Memory Usage Test: Medium Dataset (1000 files)"
    
    # Create dataset
    create_dataset 1000 0.1
    
    # Monitor memory usage during validation
    local memory_before=$(free -m | awk 'NR==2{print $3}')
    
    local start_time=$(date +%s.%N)
    "$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" >/dev/null 2>&1
    local end_time=$(date +%s.%N)
    
    local memory_after=$(free -m | awk 'NR==2{print $3}')
    local memory_used=$((memory_after - memory_before))
    local duration=$(echo "$end_time - $start_time" | bc -l)
    
    echo "Memory used: ${memory_used}MB"
    echo "Duration: $(printf "%.2f" $duration)s"
    
    # Check if memory usage is reasonable (less than 50MB for 1000 files)
    if [ $memory_used -lt 50 ]; then
        TESTS_RUN=$((TESTS_RUN + 1))
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo "✅ Memory Usage Test PASSED (${memory_used}MB < 50MB threshold)"
        return 0
    else
        TESTS_RUN=$((TESTS_RUN + 1))
        echo "❌ Memory Usage Test FAILED (${memory_used}MB >= 50MB threshold)"
        return 1
    fi
}

# Performance Test 8: Scalability analysis (compare performance ratios)
test_scalability() {
    setup_test_env
    
    echo "Scalability Analysis Test"
    
    # Test multiple dataset sizes
    local sizes=(100 500 1000 2000)
    local times=()
    
    for size in "${sizes[@]}"; do
        create_dataset "$size" 0.0
        
        local start_time=$(date +%s.%N)
        "$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" >/dev/null 2>&1
        local end_time=$(date +%s.%N)
        
        local duration=$(echo "$end_time - $start_time" | bc -l)
        times+=("$duration")
        
        echo "Dataset size $size: $(printf "%.3f" $duration)s"
        
        # Cleanup for next iteration
        rm -f "$TEST_TASK_DIR"/*.txt
        "$NUMBER_MANAGER_SCRIPT" init "test_context" >/dev/null 2>&1
    done
    
    # Check if scaling is reasonable (should not be exponential)
    local ratio_500_100=$(echo "scale=2; ${times[1]} / ${times[0]}" | bc -l)
    local ratio_1000_500=$(echo "scale=2; ${times[2]} / ${times[1]}" | bc -l)
    local ratio_2000_1000=$(echo "scale=2; ${times[3]} / ${times[2]}" | bc -l)
    
    echo "Scaling ratios:"
    echo "  500/100: $ratio_500_100"
    echo "  1000/500: $ratio_1000_500"
    echo "  2000/1000: $ratio_2000_1000"
    
    # Check if ratios are reasonable (should be somewhat linear, not exponential)
    local max_ratio=$(echo "if ($ratio_500_100 > $ratio_1000_500) $ratio_500_100 else $ratio_1000_500" | bc -l)
    max_ratio=$(echo "if ($max_ratio > $ratio_2000_1000) $max_ratio else $ratio_2000_1000" | bc -l)
    
    # Allow up to 3x scaling (worst case should be much better)
    if (( $(echo "$max_ratio < 3.0" | bc -l) )); then
        TESTS_RUN=$((TESTS_RUN + 1))
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo "✅ Scalability Test PASSED (max ratio: $max_ratio < 3.0)"
        return 0
    else
        TESTS_RUN=$((TESTS_RUN + 1))
        echo "❌ Scalability Test FAILED (max ratio: $max_ratio >= 3.0)"
        return 1
    fi
}

# Performance Test 9: Concurrency performance (multiple validations)
test_concurrency_performance() {
    setup_test_env
    
    echo "Concurrency Performance Test"
    
    # Create medium dataset
    create_dataset 1000 0.1
    
    # Run multiple validations in parallel to test system behavior
    local start_time=$(date +%s.%N)
    
    for i in {1..3}; do
        "$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" >/dev/null 2>&1 &
    done
    
    wait  # Wait for all background processes
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)
    
    echo "3 parallel validations completed in: $(printf "%.2f" $duration)s"
    
    # Should complete in reasonable time (less than 2x single validation time)
    local single_start=$(date +%s.%N)
    "$NUMBER_MANAGER_SCRIPT" validate "$TEST_TASK_DIR" "test_context" >/dev/null 2>&1
    local single_end=$(date +%s.%N)
    local single_duration=$(echo "$single_end - $single_start" | bc -l)
    
    local efficiency=$(echo "scale=2; (3 * $single_duration) / $duration" | bc -l)
    echo "Concurrency efficiency: $efficiency (1.0 = perfect parallelism, >1.0 = overhead)"
    
    # Allow some overhead but not excessive (efficiency should be > 0.5)
    if (( $(echo "$efficiency > 0.5" | bc -l) )); then
        TESTS_RUN=$((TESTS_RUN + 1))
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo "✅ Concurrency Performance Test PASSED (efficiency: $efficiency > 0.5)"
        return 0
    else
        TESTS_RUN=$((TESTS_RUN + 1))
        echo "❌ Concurrency Performance Test FAILED (efficiency: $efficiency <= 0.5)"
        return 1
    fi
}

# Run all performance tests
echo "Starting Validation Performance Tests..."

# Check if bc is available for calculations
if ! command -v bc >/dev/null 2>&1; then
    echo "❌ 'bc' command not found, required for performance calculations"
    exit 1
fi

run_test "Small Dataset (100 files)" "test_small_dataset_perfect"
run_test "Medium Dataset (1000 files)" "test_medium_dataset_perfect"
run_test "Large Dataset (5000 files)" "test_large_dataset_perfect"
run_test "Huge Dataset (10000 files)" "test_huge_dataset_perfect"
run_test "Medium Dataset with Inconsistencies" "test_medium_dataset_inconsistencies"
run_test "Large Dataset with Inconsistencies" "test_large_dataset_inconsistencies"
run_test "Memory Usage Analysis" "test_memory_usage"
run_test "Scalability Analysis" "test_scalability"
run_test "Concurrency Performance" "test_concurrency_performance"

# Performance Summary
echo ""
echo "=========================================="
echo "PERFORMANCE TEST SUMMARY"
echo "=========================================="
echo "Tests Run: $TESTS_RUN"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $((TESTS_RUN - TESTS_PASSED))"

echo ""
echo "Performance Results:"
for result in "${PERFORMANCE_RESULTS[@]}"; do
    IFS=':' read -r name size duration <<< "$result"
    printf "  %-35s: %6s files, %6ss\n" "$name" "$size" "$duration"
done

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    echo "🎉 ALL PERFORMANCE TESTS PASSED!"
    exit 0
else
    echo "❌ SOME PERFORMANCE TESTS FAILED!"
    exit 1
fi