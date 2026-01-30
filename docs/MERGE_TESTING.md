# Merge-Before-Push Test Strategy and Implementation

## Overview

This document outlines the comprehensive test strategy for the merge-before-push functionality implemented in the Auto-slopp system. The test suite covers all scenarios required by issue Auto-jth.

## Test Coverage Areas

### 1. Successful Merge Scenarios

#### Tests:
- **`test_successful_merge_no_conflicts()`**: Verifies clean merge when main has new changes that don't conflict with ai branch
- **`test_no_changes_to_merge()`**: Tests behavior when there are no changes to merge (branches are already in sync)

#### Expected Behavior:
- Merge completes successfully
- No conflicts detected
- Branch state remains consistent

### 2. Conflict Scenarios

#### Tests:
- **`test_file_level_conflicts()`**: Same file modified differently in both branches
- **`test_directory_structure_conflicts()`**: Directory structure conflicts
- **`test_binary_file_conflicts()`**: Binary file conflicts (different data in same file)
- **`test_delete_vs_modify_conflicts()`**: File deleted in one branch, modified in another

#### Expected Behavior:
- Merge fails with appropriate exit codes
- Conflicts are properly detected
- System gracefully handles conflict scenarios

### 3. OpenCode Escalation Workflow

#### Tests:
- **`test_conflict_report_creation()`**: Verifies JSON conflict report generation
- **`test_merge_with_escalation_function()`**: Tests enhanced merge function with escalation support

#### Expected Behavior:
- Structured conflict reports generated in JSON format
- Proper escalation exit codes (exit code 2 for conflicts)
- Merge state preserved for OpenCode intervention

### 4. Edge Cases

#### Tests:
- **`test_network_failure_simulation()`**: Handles fetch failures gracefully
- **`test_empty_branch_scenario()`**: Handles empty or minimal branches
- **`test_large_merge_operation()`**: Tests performance with many files
- **`test_concurrent_modifications()`**: Handles concurrent changes scenarios

#### Expected Behavior:
- Graceful error handling
- System stability under various conditions
- Appropriate error codes and logging

## Test Implementation Details

### Test Repository Creation
Each test creates isolated Git repositories to ensure:
- **Isolation**: Tests don't interfere with each other
- **Realism**: Tests use actual Git operations
- **Reproducibility**: Consistent test environments

### Merge Functions Tested
1. **`merge_origin_main_to_ai()`**: Basic merge functionality
2. **`detect_merge_conflicts()`**: Conflict detection and JSON reporting
3. **`merge_origin_main_to_ai_with_escalation()`**: Enhanced merge with OpenCode escalation

### Exit Code Validation
- **Exit Code 0**: Successful merge
- **Exit Code 1**: Merge failure (non-conflict reasons)
- **Exit Code 2**: Merge conflicts detected (escalation required)

## Running the Tests

### Individual Test Suite
```bash
cd /root/git/managed/Auto-slopp/tests
./test_merge_functionality.sh
```

### Full Test Suite (includes merge tests)
```bash
cd /root/git/managed/Auto-slopp/tests
./test_suite.sh
```

### Skip Merge Tests (for faster CI)
```bash
cd /root/git/managed/Auto-slopp/tests
./test_suite.sh --no-merge
```

## Test Environment Requirements

### Required Tools
- **Git**: For repository operations
- **Bash**: Test execution environment
- **jq**: Optional, for JSON validation in conflict reports

### Test Directory Structure
```
/tmp/merge_test_repos_$$/     # Temporary test repositories
├── no_conflicts/             # Test repository for clean merges
├── file_conflicts/           # Test repository for file conflicts
├── dir_conflicts/           # Test repository for directory conflicts
└── ...                      # Other test scenarios
```

## Integration Points

### Main Test Suite Integration
The merge tests are integrated into the main test suite (`test_suite.sh`) and can be:
- **Included**: Default behavior in full test runs
- **Skipped**: Using `--no-merge` flag for faster CI cycles

### Continuous Integration
The tests are designed to be:
- **Fast**: Each test runs independently with minimal setup
- **Reliable**: Deterministic results with proper cleanup
- **Isolated**: No side effects between tests

## Validation Criteria

### Success Criteria
- All tests pass consistently
- Proper exit code handling
- Complete cleanup of test environments
- No false positives or negatives

### Failure Handling
- Clear error messages for debugging
- Proper test isolation to prevent cascading failures
- Detailed logs for failed test scenarios

## Future Enhancements

### Potential Additions
- **Performance benchmarking**: Large merge operation timing
- **Network simulation**: More sophisticated network failure scenarios
- **Concurrent testing**: Multi-threaded merge operation testing
- **Integration testing**: End-to-end testing with actual OpenCode calls

### Maintenance Considerations
- **Regular updates**: As merge functionality evolves
- **Scenario expansion**: Add new conflict types as discovered
- **Performance monitoring**: Track test execution times

## Conclusion

This comprehensive test suite ensures the merge-before-push functionality is robust, reliable, and properly integrated with the OpenCode escalation workflow. The tests cover all required scenarios from the original task specification and provide a solid foundation for ongoing development and maintenance.