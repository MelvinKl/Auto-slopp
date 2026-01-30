# Merge Conflict Handling Test Scenarios

This document describes the comprehensive test scenarios implemented for merge conflict handling in the Auto-slopp repository automation system.

## Test Coverage Overview

The enhanced test suite provides 17 test scenarios covering:

- **Basic merge functionality**: 2 tests
- **Conflict detection and reporting**: 3 tests  
- **Complex conflict scenarios**: 4 tests
- **Edge cases and robustness**: 5 tests
- **Validation and error handling**: 3 tests

## Test Scenarios

### Basic Merge Scenarios

1. **Successful merge with no conflicts**
   - Tests clean merge when branches have non-overlapping changes
   - Validates proper merge completion and logging

2. **No changes to merge**
   - Tests behavior when branches are already up-to-date
   - Ensures no unnecessary operations are performed

### Basic Conflict Scenarios

3. **File-level conflicts detection**
   - Creates simple file conflicts between ai and main branches
   - Validates that conflicts are properly detected and handled

4. **Conflict detection and reporting**
   - Tests the `detect_merge_conflicts()` function
   - Validates JSON report generation for opencode escalation

5. **Conflict report structure validation**
   - Verifies JSON report contains all required fields
   - Ensures proper data structure for opencode integration

### Complex Conflict Scenarios

6. **Complex multi-file conflicts**
   - Tests scenarios with multiple conflicted files
   - Validates escalation report with multiple conflict entries

7. **Nested directory conflicts**
   - Tests conflicts in nested directory structures (src/components/, src/utils.js)
   - Ensures path handling works correctly for complex project structures

8. **Binary file conflicts**
   - Tests handling of binary-like files during conflicts
   - Validates graceful handling without corruption

9. **Deletion vs modification conflicts**
   - Tests edge case where one branch deletes a file modified in another
   - Ensures proper handling of delete/modify conflicts

### Edge Cases and Robustness

10. **Whitespace and formatting conflicts**
    - Tests conflicts arising from different whitespace/formatting
    - Ensures such conflicts are detectable and handled

11. **Large file conflicts**
    - Tests performance with large files (1000+ lines)
    - Ensures system handles large conflict scenarios without timeouts

12. **Merge with uncommitted changes**
    - Tests merge behavior when there are uncommitted changes
    - Validates proper handling of dirty working directory states

13. **Concurrent merge scenarios**
    - Tests behavior with divergent changes in both branches
    - Ensures merge completes without hanging or corruption

14. **Merge rollback on failure**
    - Tests that failed merges leave repository in clean state
    - Validates proper cleanup and state preservation

### Validation and Error Handling

15. **Branch validation**
    - Tests that merge functions fail when not on ai branch
    - Ensures proper branch validation

16. **Merge function existence**
    - Tests that all required merge functions are available
    - Validates function export and availability

17. **Logging integration**
    - Tests that merge functions properly integrate with logging system
    - Ensures consistent log output across merge operations

## Test Infrastructure

### Repository Setup
- Each test creates isolated repositories in `/tmp/merge_test_repos_$$`
- Automatic cleanup after each test and on exit
- Remote setup using bare repositories for realistic testing

### Helper Functions
- `create_test_repo()`: Sets up git repository with ai/main branches
- `setup_remote()`: Configures remote for testing
- `run_test()`: Provides standardized test execution with pass/fail tracking

### Test Data
- Varied content types (text, config, binary-like data)
- Different file sizes and structures
- Realistic conflict scenarios based on common development patterns

## Opencode Integration

The tests specifically validate the opencode escalation workflow:

- **Conflict Detection**: Proper identification of merge conflicts
- **Report Generation**: Structured JSON reports with all required metadata
- **State Preservation**: Clean state preservation for opencode intervention
- **Escalation Triggers**: Proper exit codes and logging for escalation

## Coverage Areas

### Conflict Types Tested
- Simple text conflicts
- Multi-file conflicts
- Nested directory conflicts
- Binary file conflicts
- Delete/modify conflicts
- Whitespace/formatting conflicts

### System Robustness
- Large file handling
- Uncommitted changes
- Branch validation
- Error recovery and cleanup
- Performance under load

### Integration Points
- Logging system integration
- Opencode escalation workflow
- Git state management
- Configuration handling

## Running Tests

Execute the test suite with:
```bash
./tests/test_merge_functionality.sh
```

The test suite provides colored output showing:
- Blue: Test execution
- Green: Passed tests
- Red: Failed tests
- Yellow: Information messages

Each test runs in isolation with proper cleanup to ensure no interference between tests.

## Expected Outcomes

All 17 tests should pass consistently. Any test failure indicates:

1. **Code Regression**: Changes to merge logic that broke existing functionality
2. **Environment Issues**: Git configuration or permission problems
3. **Test Infrastructure**: Issues with repository setup or cleanup

## Future Enhancements

Potential areas for additional test coverage:
- Network connectivity issues during merge
- Permission/access denied scenarios
- Corrupted repository state handling
- Concurrent merge operations in parallel
- Integration with specific git server configurations