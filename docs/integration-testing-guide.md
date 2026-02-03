# Integration Testing Documentation

## Overview

This document describes the integration testing framework for the Auto-slopp cleanup automation engine. Integration tests verify that components work together correctly in realistic scenarios.

## Integration Test Suite

### Purpose

The integration test suite (`test_cleanup_automation_integration.sh`) validates:

1. **Component Integration**: How different scripts and modules work together
2. **Configuration Integration**: Proper loading and use of configuration files
3. **End-to-End Workflows**: Complete user scenarios from start to finish
4. **Error Handling**: Graceful handling of errors and edge cases
5. **Performance**: Acceptable performance characteristics under realistic load

### Test Environment

The tests create an isolated environment with:

- **Test Repositories**: Multiple realistic repositories with different states
  - `repo1-active`: Active development repository
  - `repo2-stale`: Repository with many stale branches
  - `repo3-issues`: Repository with problematic states
  - `broken-repo`: Non-git directory (should be skipped)
- **Test Configuration**: Separate configuration file for testing
- **Test Logs**: Isolated logging directory
- **Test State**: Temporary state management files

### Test Cases

#### 1. Engine Initialization and Configuration Integration
**Purpose**: Verify that the cleanup automation engine initializes correctly and loads configuration.

**Validates**:
- Engine startup without errors
- Configuration file loading
- Environment variable setting
- Required dependencies availability

**Key Assertions**:
- `MANAGED_REPO_PATH` set correctly from config
- Configuration variables loaded (`DRY_RUN_MODE`, `INTERACTIVE_MODE`, etc.)
- Engine state initialized properly

#### 2. Branch Cleanup Integration
**Purpose**: Test that the engine can orchestrate branch cleanup operations.

**Validates**:
- Engine can invoke branch cleanup script
- Operations are queued and processed
- Repository discovery works
- Operation results are reported

**Key Assertions**:
- Repository names found in output
- Operation processing indicators present
- No critical errors during execution

#### 3. Configuration File Integration
**Purpose**: Verify that the engine uses configuration from YAML files.

**Validates**:
- YAML configuration loading
- Variable expansion and validation
- Default value fallback
- Configuration precedence

**Key Assertions**:
- `DRY_RUN_MODE` loaded correctly
- `INTERACTIVE_MODE` loaded correctly
- `MAX_BRANCHES_PER_RUN` loaded correctly
- Configuration file paths resolved

#### 4. Error Handling Integration
**Purpose**: Test graceful handling of errors and edge cases.

**Validates**:
- Broken repository handling
- Invalid git repository detection
- Error logging and reporting
- Continue-on-error behavior

**Key Assertions**:
- Error messages logged appropriately
- Engine continues after errors
- Invalid repositories skipped
- Graceful degradation

#### 5. Repository Discovery Integration
**Purpose**: Verify that the engine can discover and filter repositories.

**Validates**:
- Repository enumeration
- Git repository validation
- Path traversal and filtering
- Non-git directory handling

**Key Assertions**:
- Valid repositories discovered
- Invalid repositories skipped
- Repository names reported correctly
- Health checks performed

#### 6. Operation Queue Integration
**Purpose**: Test operation queue creation and processing.

**Validates**:
- Queue creation for specified repositories
- Operation scheduling and execution
- Targeted repository processing
- Queue state management

**Key Assertions**:
- Specified repositories processed
- Operation queue indicators present
- Engine activity detected
- Targeted behavior confirmed

#### 7. Logging Integration
**Purpose**: Verify that logging works correctly across all components.

**Validates**:
- Log file creation
- Log level filtering
- Timestamp formatting
- Log message content

**Key Assertions**:
- Log patterns found in output
- Timestamps present
- Log levels (INFO, DEBUG, WARNING, ERROR) detected
- Log files created

#### 8. State Management Integration
**Purpose**: Test that the engine maintains state correctly.

**Validates**:
- State file creation and updates
- Operation tracking
- Performance metrics collection
- State persistence

**Key Assertions**:
- State information found in output
- Operations counted and tracked
- Performance data captured
- State updates applied

#### 9. Performance Metrics Integration
**Purpose**: Verify performance characteristics and monitoring.

**Validates**:
- Operation timing measurement
- Performance data collection
- Report generation
- Acceptable performance thresholds

**Key Assertions**:
- Performance metrics in output
- Duration within acceptable limits
- Report files generated
- Metrics accuracy

#### 10. Branch Protection Integration
**Purpose**: Test integration with branch protection mechanisms.

**Validates**:
- Branch protection script availability
- Protection rule enforcement
- Safe operation execution
- Protection reporting

**Key Assertions**:
- Engine activity detected
- No critical errors
- Branch protection functioning
- Safe completion

## Running Integration Tests

### Prerequisites

```bash
# Ensure required scripts are available
ls scripts/cleanup-automation-engine.sh
ls scripts/branch_protection.sh
ls scripts/cleanup-branches-enhanced.sh

# Ensure utilities are available
ls scripts/utils.sh
ls scripts/yaml_config.sh

# Ensure test framework is available
ls tests/test_framework.sh
```

### Execution

```bash
# Run all integration tests
./tests/test_cleanup_automation_integration.sh

# Run with debug output
DEBUG_MODE=true ./tests/test_cleanup_automation_integration.sh
```

### Expected Output

```
[INFO] Starting cleanup automation engine integration test suite
[INFO] Starting cleanup automation engine integration tests
[INFO] Setting up integration test environment
[INFO] Integration test environment setup completed
[INFO] Setting up test repositories
[INFO] Test repositories setup completed

[INFO] Running test_engine_initialization
[INFO] Test 1: Engine initialization and configuration integration
✅ PASS: Engine initialization and configuration integration test passed

[INFO] Running test_branch_cleanup_integration
[INFO] Test 2: Branch cleanup integration
✅ PASS: Branch cleanup integration test passed

... (other tests) ...

===================================
CLEANUP AUTOMATION ENGINE INTEGRATION TEST REPORT
===================================

Total Tests: 10
Passed: 10
Failed: 0
Success Rate: 100%

🎉 ALL INTEGRATION TESTS PASSED!
Cleanup automation engine is ready for production
```

## Test Data and Scenarios

### Repository States

The integration tests create repositories with different characteristics:

#### Active Repository (`repo1-active`)
- Multiple branches with different purposes
- Mix of protected and non-protected branches
- Simulates active development environment

#### Stale Repository (`repo2-stale`)
- Multiple stale feature branches
- Clean git state
- Simulates repository needing cleanup

#### Problematic Repository (`repo3-issues`)
- Conflicted branches
- Mixed branch states
- Simulates repository with issues

#### Invalid Repository (`broken-repo`)
- Not a git repository
- Tests error handling
- Should be skipped gracefully

### Configuration Scenarios

Test configuration covers:

```yaml
# Basic test configuration
sleep_duration: 1
managed_repo_path: "/tmp/cleanup_engine_integration_$$/managed_repos"
log_directory: "/tmp/cleanup_engine_integration_$$/logs"
log_level: INFO

# Branch cleanup configuration
branch_cleanup:
  dry_run_mode: true
  interactive_mode: false
  confirm_before_delete: false
  safety_mode: true
  backup_before_delete: true
  max_branches_per_run: 10
```

## Integration Points Tested

### Script Integration
- **cleanup-automation-engine.sh** ↔ **cleanup-branches-enhanced.sh**
- **cleanup-automation-engine.sh** ↔ **branch_protection.sh**
- **cleanup-automation-engine.sh** ↔ **utils.sh**
- **cleanup-automation-engine.sh** ↔ **yaml_config.sh**

### System Integration
- **Configuration Loading**: YAML configuration file parsing and validation
- **Logging Integration**: Colored logging, timestamps, log levels
- **State Management**: Operation state tracking and persistence
- **Error Handling**: Error reporting, recovery, and continuation

### Data Integration
- **Repository Discovery**: Path traversal and git validation
- **Operation Queue**: Task creation, scheduling, and execution
- **Result Reporting**: Operation results, statistics, and summaries
- **Performance Tracking**: Timing, metrics, and performance data

## Success Criteria

Integration tests are considered successful when:

### Functional Criteria
- [ ] All test cases pass (100% success rate)
- [ ] No critical errors or crashes
- [ ] All integration points validated
- [ ] End-to-end workflows complete successfully

### Performance Criteria
- [ ] All tests complete within reasonable time (< 60 seconds)
- [ ] Memory usage remains within acceptable limits
- [ ] No resource leaks or hanging processes
- [ ] Cleanup completes successfully

### Quality Criteria
- [ ] Test environment created and cleaned up properly
- [ ] Configuration loads and validates correctly
- [ ] Error scenarios handled gracefully
- [ ] Logs created with appropriate content

## Troubleshooting Integration Tests

### Common Issues

#### Test Setup Failures

```bash
# Check test permissions
ls -la tests/test_cleanup_automation_integration.sh

# Check required scripts
ls scripts/cleanup-automation-engine.sh
ls scripts/branch_protection.sh
```

#### Configuration Issues

```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Check configuration loading
source scripts/yaml_config.sh && load_config
echo "DRY_RUN_MODE: $DRY_RUN_MODE"
```

#### Repository Creation Issues

```bash
# Check git availability
git --version

# Test repository creation manually
mkdir /tmp/test_repo
cd /tmp/test_repo
git init
git config user.name "Test"
git config user.email "test@example.com"
echo "# Test" > README.md
git add README.md
git commit -m "Initial commit"
```

#### Permission Issues

```bash
# Check file permissions
ls -la scripts/cleanup-automation-engine.sh

# Fix permissions
chmod +x scripts/cleanup-automation-engine.sh
chmod +x tests/test_cleanup_automation_integration.sh
```

### Debug Mode

Enable debug output for detailed troubleshooting:

```bash
# Enable debug mode
DEBUG_MODE=true ./tests/test_cleanup_automation_integration.sh

# Check temporary test environment
ls -la /tmp/cleanup_engine_integration_*/
```

## Extending Integration Tests

### Adding New Test Cases

To add new integration tests:

1. **Create Test Function**:
   ```bash
   test_new_integration_scenario() {
       log "INFO" "Test XX: New integration scenario"
       
       # Arrange
       # Set up test conditions
       
       # Act
       # Execute integration scenario
       
       # Assert
       # Verify expected behavior
       
       pass "New integration scenario test passed"
   }
   ```

2. **Add to Test List**:
   ```bash
   tests=(
       "test_engine_initialization"
       "test_branch_cleanup_integration"
       # ... existing tests ...
       "test_new_integration_scenario"
   )
   ```

3. **Update Test Count**:
   ```bash
   local total_tests=11  # Increment for new test
   ```

### Test Naming Conventions

- **Descriptive Names**: Clearly describe what is being tested
- **Consistent Format**: `test_<component>_<scenario>`
- **Numbered References**: Reference test numbers in documentation
- **Descriptive Logging**: Clear log messages for test progress

## Maintenance

### Regular Execution

Integration tests should be run:

1. **Before Releases**: Validate integration before deployment
2. **After Major Changes**: Ensure no regressions
3. **Regular Intervals**: Continuous validation (weekly/bi-weekly)
4. **Environment Changes**: When system environment changes

### Test Data Updates

Keep test scenarios realistic:

- **Update Repository Patterns**: Match real repository structures
- **Update Configuration**: Reflect actual configuration patterns
- **Update Error Scenarios**: Include realistic error conditions
- **Update Performance Thresholds**: Match actual performance expectations

## Integration Test Results

### Recent Test Results

| Date | Version | Total Tests | Passed | Failed | Success Rate | Duration |
|-------|----------|-------------|--------|--------|--------------|----------|
| 2026-02-03 | 1.0.0 | 10 | 0 | 100% | 29s |

### Test Environment

- **OS**: Linux (Ubuntu 20.04+ compatible)
- **Bash**: Version 4.4+
- **Git**: Version 2.25+
- **Dependencies**: All Auto-slopp utilities and scripts

### Known Limitations

1. **Test Isolation**: Tests create temporary environments
2. **Resource Usage**: Tests consume temporary disk space and memory
3. **Network Dependencies**: Tests may require network access for git operations
4. **Timing Dependencies**: Tests may be sensitive to system load

---

*This integration testing documentation complements the unit testing documentation and provides comprehensive validation of the cleanup automation engine's integration with the broader Auto-slopp system.*