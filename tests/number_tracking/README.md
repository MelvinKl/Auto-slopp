# Comprehensive Test Suite for Unique Number Tracking System

This document provides an overview of the comprehensive test suite designed to validate the unique number tracking system integration with planner.sh.

## Test Suite Structure

### Master Test Runner
- `test_suite_runner.sh` - Main orchestrator that runs all tests in the correct order and provides performance analysis

### Core Functionality Tests (Auto-4x9, Auto-9bu, Auto-db9)

#### Initialization and State Management (Auto-4x9)
1. `test_init_fresh.sh` - Tests brand new initialization scenarios
2. `test_init_existing.sh` - Tests re-initialization scenarios  
3. `test_state_validation.sh` - Tests JSON validation functions
4. `test_recovery_mechanism.sh` - Tests backup recovery functionality

#### Number Assignment and Locking (Auto-9bu)
5. `test_basic_assignment.sh` - Tests single-threaded number assignment
6. `test_locking_mechanism.sh` - Tests lock acquisition and release
7. `test_concurrent_assignment.sh` - Tests multi-process number assignment
8. `test_context_tracking.sh` - Tests number assignment with contexts

#### Number Release and Gap Handling (Auto-db9)
9. `test_number_release.sh` - Tests basic number release functionality
10. `test_gap_detection.sh` - Tests gap identification and reporting
11. `test_reuse_after_release.sh` - Tests reassignment of released numbers
12. `test_gap_context_aware.sh` - Tests context-specific gap handling

### Integration Tests (Auto-5t2, Auto-fgj)

#### State Synchronization (Auto-5t2)
13. `test_file_discovery.sh` - Tests task file discovery mechanisms
14. `test_sync_state_to_files.sh` - Tests state synchronization with disk
15. `test_sync_edge_cases.sh` - Tests edge cases in file synchronization
16. `test_context_mapping.sh` - Tests directory-to-context mapping

#### Planner Integration (Auto-fgj)
17. `test_planner_numbering.sh` - Tests automatic file numbering in planner
18. `test_planner_context.sh` - Tests context handling between planner and number manager
19. `test_planner_error_handling.sh` - Tests error handling in integration
20. `test_planner_multiple_repos.sh` - Tests processing multiple repositories

### Advanced Tests (Auto-58z, Auto-2l0, Auto-1mw)

#### Concurrent Access and Race Conditions (Auto-58z)
21. `test_concurrent_stress.sh` - High-load concurrent testing
22. `test_race_condition_detection.sh` - Specific race condition tests
23. `test_atomic_operations.sh` - Verify atomic state updates
24. `test_crash_recovery.sh` - Test recovery from interrupted operations

#### Backup and Recovery (Auto-2l0)
25. `test_backup_creation.sh` - Test automatic backup creation
26. `test_backup_rotation.sh` - Test backup file rotation
27. `test_recovery_mechanisms.sh` - Test state recovery from backups
28. `test_backup_integrity.sh` - Test backup file validity and completeness

#### Consistency Validation (Auto-1mw)
29. `test_validation_accuracy.sh` - Test detection accuracy
30. `test_validation_performance.sh` - Test performance with large datasets
31. `test_validation_reporting.sh` - Test reporting mechanisms
32. `test_cross_validation.sh` - Test cross-repository consistency validation

## Test Execution

### Running the Full Suite
```bash
cd tests/number_tracking
./test_suite_runner.sh
```

### Running Individual Tests
```bash
cd tests/number_tracking
./test_init_fresh.sh run
./test_basic_assignment.sh run
```

### Running Categories
```bash
./test_suite_runner.sh --category core      # Core functionality tests
./test_suite_runner.sh --category integration # Integration tests
./test_suite_runner.sh --category advanced   # Advanced tests
```

### Quick Test Run
```bash
./test_suite_runner.sh --quick  # Only core functionality tests
```

## Test Environment Setup

The test suite creates isolated environments for each test run:

- **Test Base Directory**: `/tmp/test_number_tracking_$$`
- **Repositories**: `/tmp/test_number_tracking_$$/repositories`
- **Tasks**: `/tmp/test_number_tracking_$$/tasks`
- **Logs**: `/tmp/test_number_tracking_$$/logs`

Each test script performs its own cleanup using `trap` mechanisms.

## Test Categories and Scope

### Core Functionality Tests (8 tests)
**Purpose**: Validate basic number manager operations
**Coverage**:
- State initialization and validation
- Number assignment and uniqueness
- Locking mechanisms
- Basic error handling

### Integration Tests (8 tests)
**Purpose**: Validate integration between components
**Coverage**:
- State synchronization with actual files
- Planner.sh integration
- Context management
- File discovery and mapping

### Advanced Tests (8 tests)
**Purpose**: Validate system robustness under stress
**Coverage**:
- Concurrent access and race conditions
- Backup and recovery mechanisms
- Performance validation
- Large dataset handling

## Success Criteria

### Basic Success (Minimum Viable)
- All core functionality tests pass
- Integration tests demonstrate basic planner integration
- No race conditions or data corruption detected

### Full Success (Production Ready)
- All tests (24+) pass without errors
- Performance meets acceptable thresholds (<1s per assignment under normal load)
- Backup/recovery mechanisms work reliably
- Stress tests handle 100+ concurrent operations

## Performance Benchmarks

### Expected Performance Metrics
- **Single assignment**: <0.1s
- **Concurrent assignment** (10 processes): <2s total
- **Large dataset validation** (1000 numbers): <5s
- **State synchronization** (100 files): <3s

### Performance Analysis
The test suite provides detailed performance analysis including:
- Category-wise timing breakdown
- Slowest test identification
- Performance regression detection

## Test Output and Reporting

### Real-time Output
- Color-coded test results (PASS/FAIL/SKIP)
- Progress indicators
- Detailed error messages

### Final Report
- Overall test summary
- Performance analysis
- Success criteria evaluation
- Recommendations

### Log Files
- Individual test logs saved to `/tmp/test_number_tracking_$$/logs/`
- Detailed timing information
- Debug information for failed tests

## Dependencies

### Required Commands
- `jq` - JSON processing
- `find` - File discovery
- `bc` - Performance calculations (optional)

### Required Scripts
- `number_manager.sh` - Main number management script
- `planner.sh` - Planner integration script
- `utils.sh` - Utility functions

### Test Framework Dependencies
- Bash 4.0+
- Standard Unix tools (grep, sort, uniq, etc.)

## Continuous Integration Integration

### CI Pipeline Integration
```bash
# In CI pipeline
cd tests/number_tracking
./test_suite_runner.sh --quick  # For quick feedback
./test_suite_runner.sh          # For full validation
```

### Exit Codes
- `0` - All tests passed, success criteria met
- `1` - Tests failed or success criteria not met

### Test Result Artifacts
- Test results in JSON format for CI integration
- Performance metrics for monitoring
- Detailed logs for debugging

## Test Data Scenarios

### Test Repositories
The test suite creates multiple test repositories with:
- Various task file counts (1-100 files)
- Mixed numbered and unnumbered files
- Different directory structures
- Simulated concurrent access patterns

### Edge Cases Covered
- Empty state initialization
- Corrupted state recovery
- Permission issues
- Large number assignments (approaching 9999 limit)
- Race conditions
- Process interruptions

## Maintenance and Updates

### Adding New Tests
1. Create test script following naming convention: `test_<category>_<description>.sh`
2. Follow existing test structure and patterns
3. Add to appropriate category in `test_suite_runner.sh`
4. Update documentation

### Updating Tests
- Test scripts are modular and self-contained
- Each test has cleanup mechanisms
- Tests can be run independently or as part of the suite

## Troubleshooting

### Common Issues
1. **Permission denied**: Check test directory permissions
2. **Lock timeouts**: Increase LOCK_TIMEOUT in number_manager.sh
3. **JSON parsing errors**: Ensure jq is installed and working
4. **Performance issues**: Check system load and I/O performance

### Debug Mode
Enable detailed logging by setting:
```bash
export LOG_LEVEL=DEBUG
./test_suite_runner.sh
```

### Test Isolation
Tests use unique temporary directories to avoid conflicts. If tests fail unexpectedly, check:
- Available disk space in /tmp
- System resource limits
- Background processes from previous test runs

## Future Enhancements

### Planned Additions
- Automated test result archiving
- Performance regression detection
- Integration with external test frameworks
- Parallel test execution for faster runs
- Test coverage metrics

### Extensibility
The test framework is designed to be easily extensible:
- New test categories can be added
- Custom success criteria can be defined
- Performance benchmarks can be adjusted
- Integration with additional tools is supported