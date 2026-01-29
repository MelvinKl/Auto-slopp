# Test Suite Documentation

## Overview

The Repository Automation System includes a comprehensive test suite that validates all scripts, configuration, and functionality.

## Test Suite Structure

```
tests/
├── test_suite.sh           # Main test runner
├── test_scripts.sh          # Individual script tests
├── test_config.sh           # Configuration tests
└── test_integration.sh      # Integration tests
```

## Running Tests

### Quick Test

```bash
# Run all tests
./tests/test_suite.sh

# Run via Makefile
make test
```

### Individual Test Categories

```bash
# Test script syntax and existence
./tests/test_scripts.sh

# Test configuration loading
./tests/test_config.sh

# Test integration scenarios
./tests/test_integration.sh
```

## Test Categories

### 1. Script Existence Tests

Validates that all required scripts exist:
- `main.sh`
- `config.sh`
- `scripts/*.sh` (all scripts in scripts directory)

### 2. Script Executability Tests

Ensures all scripts have proper execute permissions:
- Checks `+x` permission on all script files
- Validates scripts can be executed

### 3. Script Syntax Tests

Validates bash syntax for all scripts:
- Uses `bash -n` for syntax checking
- Catches syntax errors before execution

### 4. Configuration Tests

Validates configuration system:
- `config.yaml` exists and is valid YAML
- Configuration loads successfully
- Required variables are set
- Paths are accessible

### 5. Makefile Tests

Validates Makefile functionality:
- Makefile exists
- Test target executes successfully
- Exit code is 0 (success)

### 6. Integration Tests

Tests end-to-end functionality:
- Configuration loading in scripts
- Script discovery and execution
- Error handling and logging

## Test Output

The test suite provides colored output:

```
=== Auto-slopp Test Suite ===
Testing directory: /root/git/Auto-slopp

[INFO] Running test: main.sh exists
[PASS] main.sh exists
[INFO] Running test: main.sh is executable
[PASS] main.sh is executable
[INFO] Running test: main.sh has valid syntax
[PASS] main.sh has valid syntax
...

=== Test Results ===
Total tests: 31
Passed: 31
Failed: 0
✓ All tests passed!
```

### Color Legend

- **[INFO]** (Yellow): Test execution information
- **[PASS]** (Green): Test passed successfully
- **[FAIL]** (Red): Test failed

## Test Functions

The test suite provides reusable test functions:

### `run_test()`

Execute a test with proper logging and result tracking.

```bash
run_test "test name" "test command"
```

### `test_script_exists()`

Check if a script file exists.

```bash
test_script_exists "main.sh"
test_script_exists "scripts/utils.sh"
```

### `test_script_executable()`

Check if a script has execute permissions.

```bash
test_script_executable "main.sh"
test_script_executable "scripts/creator.sh"
```

### `test_script_syntax()`

Validate bash syntax of a script.

```bash
test_script_syntax "main.sh"
test_script_syntax "scripts/planner.sh"
```

## Adding New Tests

To add tests for new functionality:

### 1. Add Test Functions

Create new test functions in `test_suite.sh`:

```bash
# Test new functionality
test_new_feature() {
    local feature="$1"
    # Your test logic here
    [[ -f "$PROJECT_DIR/$feature" ]]
}

# Test new script integration
test_new_script_integration() {
    local script="$1"
    # Test script loads and runs correctly
    cd "$PROJECT_DIR" && "./$script" --test
}
```

### 2. Add Test Cases

Add new test cases to the `main()` function:

```bash
# Test new script
run_test "new_script.sh exists" "test_script_exists 'scripts/new_script.sh'"
run_test "new_script.sh is executable" "test_script_executable 'scripts/new_script.sh'"
run_test "new_script.sh has valid syntax" "test_script_syntax 'scripts/new_script.sh'"
run_test "new_script.sh integration" "test_new_script_integration 'scripts/new_script.sh'"
```

### 3. Update Test Counters

The test suite automatically tracks:
- `TESTS_TOTAL`: Total number of tests run
- `TESTS_PASSED`: Number of tests passed
- `TESTS_FAILED`: Number of tests failed

## Continuous Integration

Add tests to your CI pipeline:

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          chmod +x tests/test_suite.sh
          ./tests/test_suite.sh
      - name: Run Makefile tests
        run: make test
```

## Test Coverage

The current test suite covers:

- ✅ All script files (existence, permissions, syntax)
- ✅ Configuration files (YAML validation, loading)
- ✅ Makefile functionality
- ✅ Directory structure
- ✅ Basic integration scenarios

### Future Test Enhancements

- Mock external dependencies (opencode, bd)
- Test error handling scenarios
- Performance and load testing
- Security vulnerability scanning
- End-to-end automation testing

## Troubleshooting Tests

### Common Test Failures

1. **Permission Denied**:
   ```bash
   # Fix script permissions
   chmod +x main.sh scripts/*.sh
   ```

2. **Syntax Errors**:
   ```bash
   # Check script syntax manually
   bash -n script_with_error.sh
   ```

3. **Missing Files**:
   ```bash
   # Check what files are missing
   ls -la main.sh scripts/ config.yaml
   ```

4. **Configuration Issues**:
   ```bash
   # Test configuration loading
   source scripts/yaml_config.sh && load_config
   ```

### Debug Mode

Enable debug mode for verbose test output:

```bash
# Enable debug mode
export DEBUG_MODE=true

# Run tests with debug output
./tests/test_suite.sh
```

### Manual Testing

Test individual components manually:

```bash
# Test script loading
source scripts/utils.sh
source scripts/yaml_config.sh

# Test configuration
load_config config.yaml
echo "Configuration loaded: $SLEEP_DURATION"

# Test script execution
./scripts/creator.sh --dry-run
```

## Best Practices

1. **Run tests before changes**: Ensure baseline passes
2. **Test after modifications**: Catch regressions early
3. **Use CI/CD**: Automate testing in pipeline
4. **Add tests for new features**: Maintain coverage
5. **Update documentation**: Keep test docs current
6. **Mock external dependencies**: Ensure reliable tests

## Test Metrics

Track test metrics over time:

- Test execution time
- Pass/fail rates
- Code coverage percentage
- Number of tests per feature
- Test flakiness (intermittent failures)

Use these metrics to improve test quality and reliability.