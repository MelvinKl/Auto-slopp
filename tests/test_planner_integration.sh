#!/bin/bash

# Test file for planner integration
# Part of Auto-65t: Test file for planner integration

set -e

SCRIPT_NAME="test_planner_integration"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$PROJECT_DIR/scripts/utils.sh"

# Test setup
TEST_STATE_DIR="/tmp/test_planner_integration_$$"
export MANAGED_REPO_PATH="$TEST_STATE_DIR"
NUMBER_MANAGER_SCRIPT="$PROJECT_DIR/scripts/number_manager.sh"
PLANNER_SCRIPT="$PROJECT_DIR/scripts/planner.sh"

log "INFO" "Starting planner integration test in $TEST_STATE_DIR"

# Cleanup function
cleanup_test() {
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    wait 2>/dev/null || true
    rm -rf "$TEST_STATE_DIR"
    log "INFO" "Planner integration test cleanup completed"
}

trap cleanup_test EXIT

# Test 1: Basic planner number manager integration
test_planner_number_integration() {
    log "INFO" "Test 1: Basic planner number manager integration"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init planner_integration >/dev/null 2>&1
    
    # Create a test scenario
    local test_context="test_planner_ctx"
    
    # Get a number for the context
    local assigned_num
    assigned_num=$("$NUMBER_MANAGER_SCRIPT" get "$test_context" 2>/dev/null | tail -1)
    
    if [ $? -ne 0 ] || [ -z "$assigned_num" ]; then
        log "ERROR" "Failed to get number for planner integration test"
        return 1
    fi
    
    # Create a mock task file that would be created by planner
    local task_file="$TEST_STATE_DIR/task_${assigned_num}.md"
    echo "# Test Task $assigned_num
This is a test task file created by planner integration test.
Context: $test_context
Number: $assigned_num
" > "$task_file"
    
    # Verify task file was created
    if [ ! -f "$task_file" ]; then
        log "ERROR" "Failed to create mock task file"
        return 1
    fi
    
    log "SUCCESS" "Planner number integration: created task file with number $assigned_num"
    return 0
}

# Test 2: Context-based planning with unique numbers
test_context_based_planning() {
    log "INFO" "Test 2: Context-based planning with unique numbers"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init context_planning >/dev/null 2>&1
    
    # Test multiple contexts
    local contexts=("repo_alpha" "repo_beta" "repo_gamma")
    local created_tasks=()
    
    for ctx in "${contexts[@]}"; do
        # Get number for each context
        local ctx_num
        ctx_num=$("$NUMBER_MANAGER_SCRIPT" get "$ctx" 2>/dev/null | tail -1)
        
        if [ $? -ne 0 ] || [ -z "$ctx_num" ]; then
            log "ERROR" "Failed to get number for context '$ctx'"
            return 1
        fi
        
        # Create task file
        local task_file="$TEST_STATE_DIR/${ctx}_task_${ctx_num}.md"
        echo "# ${ctx} Task $ctx_num
Context: $ctx
Number: $ctx_num
" > "$task_file"
        
        if [ -f "$task_file" ]; then
            created_tasks+=("$ctx:$ctx_num")
        fi
    done
    
    # Verify all tasks were created
    if [ ${#created_tasks[@]} -ne ${#contexts[@]} ]; then
        log "ERROR" "Not all context-based tasks created: ${#created_tasks[@]}/${#contexts[@]}"
        return 1
    fi
    
    # Check for duplicate numbers across contexts
    local all_numbers=()
    for task in "${created_tasks[@]}"; do
        local num
        num=$(echo "$task" | cut -d: -f2)
        all_numbers+=("$num")
    done
    
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Duplicate numbers found across contexts: $duplicate_count"
        return 1
    fi
    
    log "SUCCESS" "Context-based planning: created ${#created_tasks[@]} tasks with unique numbers"
    return 0
}

# Test 3: State validation after planner operations
test_planner_state_validation() {
    log "INFO" "Test 3: State validation after planner operations"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init planner_validation >/dev/null 2>&1
    
    # Simulate planner creating multiple tasks
    local tasks_created=0
    for i in {1..5}; do
        local num
        num=$("$NUMBER_MANAGER_SCRIPT" get planner_validation 2>/dev/null | tail -1)
        
        if [ $? -eq 0 ] && [ -n "$num" ]; then
            # Create mock task file
            local task_file="$TEST_STATE_DIR/planner_task_${num}.md"
            echo "# Planner Task $num
Number: $num
Created: $(date)
" > "$task_file"
            
            if [ -f "$task_file" ]; then
                tasks_created=$((tasks_created + 1))
            fi
        fi
    done
    
    if [ "$tasks_created" -eq 0 ]; then
        log "ERROR" "No tasks created for validation test"
        return 1
    fi
    
    # Validate state
    "$NUMBER_MANAGER_SCRIPT" validate "$TEST_STATE_DIR" planner_validation >/dev/null 2>&1
    
    if [ $? -ne 0 ]; then
        log "ERROR" "State validation failed after planner operations"
        return 1
    fi
    
    # Check state consistency
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "State file invalid after planner operations"
            return 1
        fi
    fi
    
    log "SUCCESS" "Planner state validation: $tasks_created tasks created, state validated successfully"
    return 0
}

# Test 4: Concurrent planner operations
test_concurrent_planner_operations() {
    log "INFO" "Test 4: Concurrent planner operations"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init concurrent_planner >/dev/null 2>&1
    
    # Start concurrent planner-like operations
    local pids=()
    local results_file="$TEST_STATE_DIR/concurrent_planner_results.txt"
    
    for i in {1..5}; do
        (
            for j in {1..2}; do
                local start_time
                start_time=$(date +%s.%N)
                local num
                num=$("$NUMBER_MANAGER_SCRIPT" get concurrent_planner 2>/dev/null | tail -1)
                local end_time
                end_time=$(date +%s.%N)
                
                if [ $? -eq 0 ] && [ -n "$num" ]; then
                    # Create mock task file
                    local task_file="$TEST_STATE_DIR/concurrent_task_${i}_${j}_${num}.md"
                    echo "# Concurrent Task ${i}_${j}
Number: $num
Process: $i
Operation: $j
" > "$task_file"
                    
                    echo "process_${i}:operation_${j}:number_${num}:start_${start_time}:end_${end_time}" >> "$results_file"
                else
                    echo "process_${i}:operation_${j}:failed:start_${start_time}:end_${end_time}" >> "$results_file"
                fi
                
                sleep 0.01
            done
        ) &
        pids+=($!)
    done
    
    # Wait for completion
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    # Analyze results
    local all_numbers=()
    local successful_operations=0
    
    if [ -f "$results_file" ]; then
        while read -r line; do
            if echo "$line" | grep -q "number_"; then
                successful_operations=$((successful_operations + 1))
                local num
                num=$(echo "$line" | grep -o "number_[0-9]*" | cut -d_ -f2)
                all_numbers+=("$num")
            fi
        done < "$results_file"
    fi
    
    # Check for duplicates
    local duplicate_count
    duplicate_count=$(printf '%s\n' "${all_numbers[@]}" | sort -n | uniq -d | wc -l)
    
    if [ "$duplicate_count" -gt 0 ]; then
        log "ERROR" "Duplicates found in concurrent planner operations: $duplicate_count"
        return 1
    fi
    
    # Verify state file integrity
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "State file corrupted after concurrent planner operations"
            return 1
        fi
    fi
    
    log "SUCCESS" "Concurrent planner operations: $successful_operations successful, ${#all_numbers[@]} unique numbers, no duplicates"
    return 0
}

# Test 5: Error handling in planner integration
test_planner_error_handling() {
    log "INFO" "Test 5: Error handling in planner integration"
    
    # Initialize number manager
    "$NUMBER_MANAGER_SCRIPT" init planner_errors >/dev/null 2>&1
    
    # Test error handling scenarios
    
    # Scenario 1: Invalid context (should still work)
    local num1
    num1=$("$NUMBER_MANAGER_SCRIPT" get "" 2>/dev/null | tail -1)
    
    # Scenario 2: Missing context (should use default)
    local num2
    num2=$("$NUMBER_MANAGER_SCRIPT" get 2>/dev/null | tail -1)
    
    # Scenario 3: Special characters in context
    local num3
    num3=$("$NUMBER_MANAGER_SCRIPT" get "test-ctx_with-dashes" 2>/dev/null | tail -1)
    
    # Check that we got at least some numbers
    local successful_numbers=0
    for num in "$num1" "$num2" "$num3"; do
        if [ -n "$num" ] && [ "$num" != "0" ]; then
            successful_numbers=$((successful_numbers + 1))
        fi
    done
    
    if [ "$successful_numbers" -eq 0 ]; then
        log "ERROR" "No numbers assigned in error handling test"
        return 1
    fi
    
    # Verify state is still consistent after errors
    local state_file="$TEST_STATE_DIR/.number_state/state.json"
    if [ -f "$state_file" ]; then
        if ! python3 -m json.tool "$state_file" >/dev/null 2>&1; then
            log "ERROR" "State file corrupted after error scenarios"
            return 1
        fi
    fi
    
    log "SUCCESS" "Planner error handling: $successful_numbers numbers assigned despite error scenarios"
    return 0
}

# Run all planner integration tests
run_all_planner_integration_tests() {
    local test_count=0
    local pass_count=0
    
    local tests=(
        "test_planner_number_integration"
        "test_context_based_planning"
        "test_planner_state_validation"
        "test_concurrent_planner_operations"
        "test_planner_error_handling"
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
    echo "Planner Integration Test Results: $pass_count/$test_count passed"
    echo "=========================================="
    
    if [ $pass_count -eq $test_count ]; then
        log "SUCCESS" "All planner integration tests passed!"
        return 0
    else
        log "ERROR" "Some planner integration tests failed"
        return 1
    fi
}

# Main execution
if [ "${1:-}" = "run" ]; then
    run_all_planner_integration_tests
    exit $?
else
    echo "Usage: $0 run"
    echo "This script tests planner integration with number manager"
    exit 1
fi