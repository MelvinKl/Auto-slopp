# Testing Guide for Auto-slopp

This guide covers how to run tests locally, understand test coverage, and integrate with CI/CD pipelines.

> **Note:** This project contains a significant amount of AI-generated code. Some tests may cover features that are non-functional or behave unexpectedly due to LLM-generated "slop." When writing or modifying tests, verify the underlying implementation is correct.

## Table of Contents

- [Local Testing](#local-testing)
- [Test Structure](#test-structure)
- [Performance Testing](#performance-testing)
- [Integration Testing](#integration-testing)
- [Coverage Reports](#coverage-reports)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## Local Testing

### Prerequisites

Ensure you have the development dependencies installed:

```bash
# Using uv (recommended)
uv pip install -e .[dev]

# Or using pip
pip install -e .[dev]
```

### Running All Tests

```bash
# Basic test run
pytest

# Verbose output
pytest -v

# With coverage
pytest --cov=src --cov-report=term-missing

# Stop on first failure
pytest -x

# Run specific test file
pytest tests/test_worker.py

  # Run specific test class
  pytest tests/test_worker.py::TestWorkerBase

  # Run specific test method
  pytest tests/test_worker.py::TestWorker::test_worker_is_abstract
```

### Running Specific Test Categories

```bash
# Performance tests (marked with @pytest.mark.performance)
pytest -m performance

# Integration tests (marked with @pytest.mark.integration)
pytest -m integration

# All tests except performance (useful for quick checks)
pytest -m "not performance"
```

## Test Structure

### Test Organization

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── test_discovery.py         # Worker discovery tests
├── test_main.py             # Main entry point tests
├── test_settings.py         # Configuration tests
├── test_telegram_handler.py # Telegram integration tests
├── test_worker.py           # Base worker class tests
├── test_github_issue_worker.py  # GitHubIssueWorker tests
├── test_git_operations.py    # Git operations tests
├── test_file_operations.py   # File operations tests
└── test_*_worker.py         # Other worker tests
```

### Key Fixtures

- `temp_dir`: Temporary directory for testing
- `temp_repo_dir`: Temporary repository with basic structure
- `temp_task_dir`: Temporary task directory with sample files
- `temp_workers_dir`: Temporary workers directory with sample workers
- `mock_settings`: Mock settings object for testing

### Test Categories

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions and CI/CD scenarios
3. **Performance Tests**: Benchmark critical operations and identify bottlenecks

## Performance Testing

Performance tests are marked with `@pytest.mark.performance` and can be run separately:

```bash
# Run all performance tests
pytest -m performance -v

# Run with detailed timing
pytest -m performance -v --tb=short
```

### Performance Benchmarks

The performance tests include:

- **SimpleLogger**: Basic worker execution speed
- **FileMonitor**: File scanning performance with large datasets
- **DirectoryScanner**: Directory traversal performance
- **GitHubIssueWorker**: Issue processing performance
- **Executor**: Overall executor performance
- **Memory Usage**: Efficiency with large files
- **Concurrency**: Race condition detection
- **Scalability**: Deep directory structure handling

### Performance Assertions

Each performance test includes specific assertions:
- Maximum execution time limits
- Minimum throughput requirements
- Memory efficiency checks
- Error handling performance impact

## Integration Testing

Integration tests verify the system works correctly in CI/CD environments:

```bash
# Run all integration tests
pytest -m integration -v

# Run specific integration test scenarios
pytest tests/test_integration.py::TestCIEnvironmentSetup -v
```

### Integration Test Scenarios

1. **Full Workflow Integration**: End-to-end workflow testing
2. **OpenAgent Integration**: External tool integration
3. **CI Environment Variables**: Environment-specific behavior
4. **Error Recovery**: Failure handling and recovery
5. **Resource Cleanup**: Proper resource management
6. **Large Dataset Handling**: Performance with real-world data sizes

## Coverage Reports

### Generating Coverage Reports

```bash
# Terminal coverage report with missing lines
pytest --cov=src --cov-report=term-missing

# HTML coverage report (detailed, browser-based)
pytest --cov=src --cov-report=html
open htmlcov/index.html

# XML coverage report (for CI systems)
pytest --cov=src --cov-report=xml

# Coverage with multiple formats
pytest --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml
```

### Coverage Goals

- **Overall Coverage**: Target 90%+ coverage
- **Critical Components**: 95%+ coverage for core worker system
- **Example Workers**: 90%+ coverage for demonstration code
- **Error Paths**: Ensure all error conditions are tested

### Coverage Exclusions

The following are excluded from coverage calculations:
- Test files (obviously)
- Debug/development code paths
- Exception handling that's difficult to test realistically

## CI/CD Integration

### GitHub Actions

The project includes comprehensive CI/CD workflows in `.github/workflows/`:

1. **ci.yml**: Main CI pipeline with testing and coverage
2. **lint.yml**: Code quality checks (black, isort, flake8)

### Local CI Simulation

You can simulate the CI environment locally:

```bash
# Run the full CI test matrix
docker-compose -f .github/docker-compose.test.yml up

# Or manually run the CI steps
uv venv
source .venv/bin/activate
uv pip install -e .[dev]
pytest --cov=src --cov-report=xml
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/
```

### Environment Variables

The tests respect these CI environment variables:

```bash
# Standard CI detection
CI=true

# GitHub Actions specific
GITHUB_ACTIONS=true
GITHUB_REF=refs/heads/main
GITHUB_SHA=abc123def456
GITHUB_RUN_ID=123456789
GITHUB_RUN_NUMBER=42
```

### Pre-commit Hooks

The project includes pre-commit configuration for local quality checks:

```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure dependencies are installed with `uv pip install -e .[dev]`
2. **Test Timeouts**: Performance tests may timeout on slow systems; increase timeout values
3. **Missing Fixtures**: Ensure conftest.py is in the tests directory
4. **Coverage Not Working**: Install pytest-cov: `pip install pytest-cov`

### Performance Test Failures

Performance tests have strict timing requirements. If they fail:

1. **System Load**: Close other applications and re-run
2. **Disk Speed**: Slow disk I/O can affect file-based tests
3. **Memory Pressure**: Ensure sufficient RAM is available
4. **Adjust Thresholds**: If consistently failing, adjust performance thresholds in the tests

### Debug Mode

Run tests with debug output for troubleshooting:

```bash
# Verbose pytest output
pytest -v -s

# Show local variables in tracebacks
pytest --tb=long

# Debug specific test
pytest -s -v tests/test_worker.py::TestWorker::test_init

# Use Python debugger
pytest --pdb
```

### Test Data Cleanup

Tests use temporary directories that are automatically cleaned up. If cleanup fails:

```bash
# Clean pytest cache manually
pytest --cache-clear

# Remove temporary files
rm -rf /tmp/tmp*
```

## Best Practices

### Writing Tests

1. **Use Fixtures**: Leverage existing fixtures for consistency
2. **Test Edges**: Don't just test happy paths; test error conditions
3. **Mock External Dependencies**: Use unittest.mock for external services
4. **Clear Naming**: Use descriptive test method names
5. **One Assertion Per Test**: When possible, keep tests focused

### Performance Testing

1. **Baseline First**: Establish performance baselines before optimization
2. **Consistent Environment**: Run performance tests in consistent environments
3. **Measure Multiple Runs**: Performance can vary; consider statistical significance
4. **Document Benchmarks**: Update documentation when changing performance targets

### CI/CD Integration

1. **Fail Fast**: Configure CI to fail on first test failure for fast feedback
2. **Parallel Execution**: Use test parallelization for faster CI runs
3. **Coverage Gates**: Set minimum coverage thresholds in CI
4. **Artifact Retention**: Keep test artifacts (coverage reports) for analysis

## Continuous Improvement

### Adding New Tests

When adding new features:

1. Add corresponding unit tests
2. Add integration tests if the feature affects system behavior
3. Add performance tests if the feature impacts performance
4. Update documentation

### Monitoring

Regularly monitor:

- Test execution time trends
- Coverage percentage changes
- Test flakiness/reliability
- CI pipeline duration

This comprehensive testing approach ensures Auto-slopp remains reliable, performant, and maintainable across different environments and use cases.
