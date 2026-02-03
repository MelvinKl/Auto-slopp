# Auto-slopp Test Suite Documentation

This directory contains comprehensive test suites for all Auto-slopp scripts, providing multiple layers of testing from basic syntax validation to complex integration scenarios.

## Test Suite Overview

### Available Test Suites

1. **Basic Test Suite** (`test_suite.sh`)
   - Validates script existence, executability, and syntax
   - Tests basic configuration files
   - Covers logging, merge, and number tracking functionality

2. **Enhanced Test Suite** (`test_suite_enhanced.sh`)
   - Uses AAA (Arrange-Act-Assert) pattern
   - Provides coverage analysis and performance metrics
   - Organized by test categories: unit, integration, system, performance, security, regression

3. **Comprehensive Test Suite** (`test_comprehensive_suite.sh`)
   - Tests all scripts with detailed functionality verification
   - Categorized testing: core, automation, utilities, telegram, main scripts
   - Includes performance and stress testing

4. **Master Test Runner** (`run_all_tests.sh`)
   - Single entry point for running all test suites
   - Provides comprehensive reporting and quality gates
   - Supports selective suite execution and quick mode

### Specialized Test Suites

- **Number Tracking Tests** (`number_tracking/`)
- **Telegram Integration Tests** (`test_telegram_*.sh`)
- **Planner Tests** (`test_planner_*.sh`)
- **Validation Tests** (`test_validation_*.sh`)
- **Backup Tests** (`test_backup_*.sh`)
- **Performance Tests** (`test_*.sh` with performance focus)

## Quick Start

### Run All Tests
```bash
# Run all test suites
./tests/run_all_tests.sh

# Run quick version (essential tests only)
./tests/run_all_tests.sh --quick

# Run with verbose output
./tests/run_all_tests.sh --verbose
```

### Run Specific Test Suites
```bash
# Run only basic tests
./tests/run_all_tests.sh --suites basic

# Run comprehensive and enhanced tests
./tests/run_all_tests.sh --suites comprehensive enhanced

# Run telegram-specific tests
./tests/run_all_tests.sh --suites telegram
```

### Direct Test Execution
```bash
# Run basic test suite directly
./tests/test_suite.sh

# Run enhanced test suite
./tests/test_suite_enhanced.sh --quick

# Run comprehensive suite for specific scripts
./tests/test_comprehensive_suite.sh --script number_manager
```

## Test Categories

### Coverage Levels
- **Critical**: Business logic, data transformations (100% required)
- **High**: Public APIs, user-facing features (90%+ required)
- **Medium**: Utilities, helpers (80%+ required)
- **Low**: Simple wrappers, configs (optional)

### Test Types
- **Unit Tests**: Isolated function testing
- **Integration Tests**: Component interaction
- **System Tests**: End-to-end workflows
- **Performance Tests**: Speed and resource usage
- **Security Tests**: Input validation and permissions
- **Regression Tests**: Prevent functionality loss

## Quality Gates

The test suite enforces quality gates:
- No test failures allowed
- Minimum 85% coverage (configurable)
- Performance thresholds must be met
- Security validations must pass

## Test Framework Features

### AAA Pattern
All enhanced tests follow Arrange-Act-Assert pattern:
```bash
# Arrange: Setup test data and environment
arrange "Setup test data" "
    # Setup commands here
"

# Act: Execute code under test
act "Execute function" "
    # Test execution here
"

# Assert: Verify results
assert "Expected behavior" "
    # Assertions here
"
```

### Coverage Analysis
- Tracks test coverage by priority level
- Provides recommendations for improvement
- Generates detailed coverage reports

### Performance Monitoring
- Measures execution time for tests
- Identifies performance regressions
- Provides optimization insights

## Configuration

### Environment Variables
- `DEBUG=true`: Enable debug output
- `TEST_TMP_DIR`: Override temporary directory
- `COVERAGE_TARGET`: Set coverage threshold

### Test Configuration
Tests can be configured with command-line options:
- `--quick`: Run only critical tests
- `--category`: Filter by test category
- `--script`: Test specific scripts
- `--coverage`: Set coverage target
- `--verbose`: Show detailed output

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   chmod +x tests/*.sh scripts/*.sh
   ```

2. **Missing Dependencies**
   ```bash
   # Install required tools
   apt-get update && apt-get install -y bc jq
   ```

3. **Test Isolation Failures**
   - Ensure test temporary directories are properly cleaned
   - Check for conflicting environment variables

### Debug Mode
Run tests with debug output:
```bash
DEBUG=true ./tests/run_all_tests.sh --verbose --suites basic
```

## Adding New Tests

### Test Structure
1. Create test functions following AAA pattern
2. Use the test framework utilities
3. Add appropriate coverage level
4. Include error handling and edge cases

### Example New Test
```bash
test_new_functionality() {
    arrange "Setup test environment" "
        # Setup commands
    "
    
    act "Execute test" "
        # Test commands
    "
    
    assert "Expected result" "
        # Assertion commands
    "
}

# Register the test
run_test "New functionality" "test_new_functionality" "unit" "high" "Test description"
```

## Continuous Integration

### CI Integration
Add to CI pipeline:
```yaml
test:
  script:
    - ./tests/run_all_tests.sh --coverage 90 --fail-fast
  artifacts:
    reports:
      junit: tests/results.xml
```

### Pre-commit Hooks
```bash
#!/bin/sh
# Run quick tests before commit
./tests/run_all_tests.sh --quick --suites basic
```

## Test Metrics

The test suite tracks:
- Total test count and pass rate
- Execution time and performance
- Coverage levels by priority
- Quality gate compliance

## Contributing

When adding new scripts:
1. Create corresponding tests
2. Update script metadata in comprehensive suite
3. Verify coverage targets are met
4. Update documentation

## Support

For test-related issues:
1. Check test output for specific error messages
2. Run with `--verbose` for detailed information
3. Verify dependencies are installed
4. Check script permissions and syntax

---

**Test Suite Version**: 2.0  
**Framework**: Auto-slopp Enhanced Test Framework  
**Last Updated**: 2026-02-02