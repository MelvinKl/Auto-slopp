# Enhanced Testing Framework Documentation

## Overview

The Auto-slopp project uses an enhanced testing framework that follows modern testing standards and best practices. The framework is designed to provide comprehensive coverage, maintainability, and ease of use while following the AAA pattern (Arrange → Act → Assert).

## Framework Components

### 1. Test Framework (`tests/test_framework.sh`)

The core testing framework provides:

- **AAA Pattern Implementation**: Arrange → Act → Assert
- **Comprehensive Coverage Tracking**: Critical, High, Medium, Low levels
- **Performance Analysis**: Execution time tracking and analysis
- **Mocking and Stubbing**: Test isolation capabilities
- **Rich Reporting**: Detailed test results with recommendations

### 2. Enhanced Test Suite (`tests/test_suite_enhanced.sh`)

The main test runner includes:

- **Unit Tests**: Isolated function testing
- **Integration Tests**: Component interaction testing
- **System Tests**: End-to-end workflow testing
- **Performance Tests**: Speed and resource usage testing
- **Security Tests**: Input validation and security testing
- **Regression Tests**: Backward compatibility testing

### 3. Legacy Test Suite (`tests/test_suite.sh`)

Maintained for backward compatibility with existing test scripts.

## Test Categories

### Unit Tests
- **Purpose**: Test individual functions and components in isolation
- **Coverage**: Critical and High priority
- **Examples**: Script syntax validation, configuration loading, utility functions

### Integration Tests
- **Purpose**: Test interaction between components
- **Coverage**: High and Medium priority
- **Examples**: Main script integration, planner integration, repository discovery

### System Tests
- **Purpose**: Test complete workflows end-to-end
- **Coverage**: High priority
- **Examples**: Complete automation cycles, system state consistency

### Performance Tests
- **Purpose**: Ensure acceptable performance characteristics
- **Coverage**: Medium priority
- **Examples**: Script loading time, number manager performance

### Security Tests
- **Purpose**: Validate security measures and input handling
- **Coverage**: High priority
- **Examples**: Input validation, file permissions, malicious input handling

### Regression Tests
- **Purpose**: Ensure backward compatibility and prevent regressions
- **Coverage**: High priority
- **Examples**: Legacy configuration support, migration scenarios

## Coverage Levels

### Critical (100% required)
- Business logic
- Data transformations
- Core functionality
- Error handling

### High (90%+ required)
- Public APIs
- User-facing features
- Integration points
- Security functions

### Medium (80%+ recommended)
- Utility functions
- Helper functions
- Configuration management
- Logging functions

### Low (optional)
- Simple wrappers
- Configuration files
- Static data
- Documentation

## Running Tests

### Quick Test (Critical Only)
```bash
make test-quick
# or
./tests/test_suite_enhanced.sh --quick
```

### Comprehensive Test Suite
```bash
make test
# or
./tests/test_suite_enhanced.sh
```

### Specific Test Categories
```bash
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-system        # System tests only
make test-performance   # Performance tests only
make test-security      # Security tests only
make test-regression    # Regression tests only
```

### Verbose Output
```bash
./tests/test_suite_enhanced.sh --verbose
```

### Help and Options
```bash
./tests/test_suite_enhanced.sh --help
```

### Legacy Tests
```bash
make test-legacy
# or
./tests/test_suite.sh
```

## Writing Tests

### Test Structure

Follow the AAA pattern in your test functions:

```bash
test_my_function() {
    arrange "Setup test data and mocks" "
        local test_input='test_value'
        local expected_output='expected_value'
        create_mock 'dependency_function' 0 'mock_output'
    "
    
    act "Execute the function under test" "
        local actual_output
        actual_output=\$(my_function \"\$test_input\")
    "
    
    assert "Verify the results" "
        assert_equals \"\$actual_output\" \"\$expected_value\" \"Function should return expected value\"
        assert_contains \"\$(cat mock_log_file)\" 'dependency_function called' \"Dependency should be called\"
    "
}
```

### Using Assertions

The framework provides comprehensive assertion helpers:

```bash
# Equality assertions
assert_equals "$actual" "$expected" "Custom message"
assert_not_equals "$actual" "$unexpected" "Custom message"

# String assertions
assert_contains "$haystack" "$needle" "Custom message"
assert_not_contains "$haystack" "$needle" "Custom message"

# File assertions
assert_file_exists "$file_path" "Custom message"
assert_file_not_exists "$file_path" "Custom message"

# Command assertions
assert_command_success "command to run" "Custom message"
assert_command_failure "command to run" "Custom message"
assert_exit_code "command to run" expected_code "Custom message"
```

### Performance Testing

```bash
test_performance_critical_function() {
    arrange "Setup performance test" "
        local test_data=\$(generate_large_dataset)
    "
    
    act "Measure performance" "
        local execution_time
        execution_time=\$(measure_time "critical_function '\$test_data'" 10)
    "
    
    assert "Performance within acceptable limits" "
        assert_performance "critical_function '\$test_data'" 100  # Max 100ms
    "
}
```

### Mocking and Stubbing

```bash
test_with_dependency() {
    arrange "Setup mocks" "
        local call_log_file='$TEST_TMP_DIR/calls.log'
        create_mock 'external_api_call' 0 'success_response'
        create_stub 'logger_function' '$call_log_file'
    "
    
    act "Test function that uses mocked dependencies" "
        local result
        result=\$(function_with_dependencies 'test_input')
    "
    
    assert "Function works correctly with mocks" "
        assert_equals \"\$result\" 'expected_result'
        assert_file_contains '$call_log_file' 'logger_function called'
    "
}
```

## Test Standards

### Naming Conventions
- Test functions: `test_<feature>_<scenario>`
- Test files: `test_<component>.sh`
- Descriptive names explaining what is being tested and the expected outcome

### Test Independence
- Each test should be independent
- No shared state between tests
- Tests should run in any order
- Cleanup after each test

### Error Handling
- Tests should handle expected errors gracefully
- Use proper assertions for error conditions
- Test both success and failure paths

### Coverage Requirements
- Critical functionality: 100% coverage
- Public APIs: 90%+ coverage
- Utilities: 80%+ coverage
- Simple wrappers: optional coverage

## Continuous Integration

### Quality Gates
The test framework enforces quality gates:

1. **No Test Failures**: All tests must pass
2. **Minimum Coverage**: Critical + High coverage must be ≥ 60%
3. **Performance**: Total test time must be < 5 minutes
4. **Dependencies**: All required dependencies must be available

### CI Integration

Add to your CI pipeline:

```yaml
# Example CI configuration
test:
  stage: test
  script:
    - make install-deps
    - make test-quick  # Fast feedback
    - make test         # Full validation
  coverage: '/Coverage: \d+\.\d+%/'
  artifacts:
    reports:
      junit: test-results.xml
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure test scripts are executable
   ```bash
   chmod +x tests/test_suite_enhanced.sh
   ```

2. **Missing Dependencies**: Install required tools
   ```bash
   make install-deps
   ```

3. **Test Failures**: Check logs for detailed error messages
   ```bash
   ./tests/test_suite_enhanced.sh --verbose
   ```

4. **Performance Issues**: Run performance tests to identify bottlenecks
   ```bash
   make test-performance
   ```

### Debug Mode

Enable debug output for troubleshooting:

```bash
DEBUG=true ./tests/test_suite_enhanced.sh --verbose
```

### Test Isolation

If tests interfere with each other:

1. Check for shared state in test variables
2. Ensure proper cleanup in `cleanup_test_environment()`
3. Use separate test data directories

## Maintenance

### Adding New Tests

1. Choose appropriate category (unit/integration/system)
2. Follow AAA pattern
3. Use appropriate coverage level
4. Add to test suite execution
5. Update documentation

### Updating Framework

1. Test framework changes with existing tests
2. Maintain backward compatibility
3. Update documentation
4. Communicate changes to team

### Test Data Management

1. Use temporary directories for test data
2. Clean up test artifacts
3. Use deterministic test data
4. Version test fixtures if needed

## Best Practices

1. **Test Early**: Write tests alongside code
2. **Test Often**: Run tests frequently during development
3. **Keep Tests Simple**: One assertion per test when possible
4. **Use Descriptive Names**: Test names should explain what they test
5. **Mock External Dependencies**: Isolate code from external systems
6. **Test Edge Cases**: Don't just test happy path
7. **Maintain Coverage**: Keep test coverage at required levels
8. **Review Test Code**: Apply same quality standards to test code

## Framework Features

### Test Environment Isolation
- Automatic setup/cleanup of test directories
- Isolated environment variables
- Temporary file management
- Process cleanup

### Performance Monitoring
- Individual test timing
- Category-wise performance analysis
- Slow test identification
- Performance trend tracking

### Coverage Analysis
- Coverage level distribution
- Gap identification
- Recommendations for improvement
- Quality gate enforcement

### Rich Reporting
- Colored output with categories
- Detailed failure analysis
- Performance metrics
- Actionable recommendations

## Migration from Legacy Tests

To migrate from the legacy test suite:

1. **Start with Enhanced Framework**: Use `test_suite_enhanced.sh` for new tests
2. **Gradual Migration**: Port existing tests one by one
3. **Maintain Compatibility**: Keep legacy tests during transition
4. **Update CI**: Switch to enhanced test suite when ready

### Example Migration

**Legacy Test**:
```bash
test_script_exists() {
    [[ -f "$PROJECT_DIR/$script" ]]
}
```

**Enhanced Test**:
```bash
test_script_exists_enhanced() {
    arrange "Setup script paths" "
        local scripts=('$SCRIPTS_DIR'/*.sh)
        local failed_scripts=()
    "
    
    act "Check script existence" "
        for script in \"${scripts[@]}\"; do
            if [[ ! -f \"\$script\" ]]; then
                failed_scripts+=(\"\$(basename \"\$script\")\")
            fi
        done
    "
    
    assert "All scripts exist" "
        [[ \${#failed_scripts[@]} -eq 0 ]]
    "
}
```

## Resources

- [Testing Standards](/root/.config/opencode/context/core/standards/test-coverage.md)
- [Makefile Targets](#running-tests)
- [Assertion Helpers](#using-assertions)
- [Mock Framework](#mocking-and-stubbing)

For questions or issues with the testing framework, consult the test files or run `./tests/test_suite_enhanced.sh --help`.