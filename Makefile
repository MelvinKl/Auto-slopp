# Makefile for Auto-slopp project

.PHONY: test test-quick test-unit test-integration test-system test-performance test-security test-regression test-framework help clean install-deps validate

# Default target
all: help

# Test targets with comprehensive coverage
test: test-framework
	@echo "Running comprehensive test suite..."
	@./tests/test_suite_enhanced.sh

test-quick: test-framework
	@echo "Running quick test suite (critical tests only)..."
	@./tests/test_suite_enhanced.sh --quick

test-unit: test-framework
	@echo "Running unit tests..."
	@./tests/test_suite_enhanced.sh --category unit

test-integration: test-framework
	@echo "Running integration tests..."
	@./tests/test_suite_enhanced.sh --category integration

test-system: test-framework
	@echo "Running system tests..."
	@./tests/test_suite_enhanced.sh --category system

test-performance: test-framework
	@echo "Running performance tests..."
	@./tests/test_suite_enhanced.sh --category performance

test-security: test-framework
	@echo "Running security tests..."
	@./tests/test_suite_enhanced.sh --category security

test-regression: test-framework
	@echo "Running regression tests..."
	@./tests/test_suite_enhanced.sh --category regression

# Test framework validation
test-framework:
	@echo "Validating test framework..."
	@./tests/test_framework.sh

# Legacy test target (backwards compatibility)
test-legacy:
	@echo "Running legacy test suite..."
	@./tests/test_suite.sh --no-make

# Install test dependencies
install-deps:
	@echo "Installing test dependencies..."
	@if command -v apt-get >/dev/null 2>&1; then \
		sudo apt-get update && sudo apt-get install -y bc jq; \
	elif command -v yum >/dev/null 2>&1; then \
		sudo yum install -y bc jq; \
	elif command -v brew >/dev/null 2>&1; then \
		brew install bc jq; \
	else \
		echo "Please install bc and jq manually"; \
		exit 1; \
	fi

# Validate project structure
validate:
	@echo "Validating project structure..."
	@./tests/test_suite_enhanced.sh --quick --verbose

# Help target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Testing:"
	@echo "  test               Run comprehensive test suite"
	@echo "  test-quick         Run only critical tests"
	@echo "  test-unit          Run unit tests only"
	@echo "  test-integration   Run integration tests only"
	@echo "  test-system        Run system tests only"
	@echo "  test-performance   Run performance tests only"
	@echo "  test-security      Run security tests only"
	@echo "  test-regression    Run regression tests only"
	@echo "  test-legacy        Run legacy test suite"
	@echo "  test-framework     Validate test framework"
	@echo ""
	@echo "Development:"
	@echo "  install-deps       Install test dependencies"
	@echo "  validate          Quick project validation"
	@echo "  clean              Clean temporary files"
	@echo "  help               Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make test-quick              # Quick validation"
	@echo "  make test-unit test-system   # Specific test categories"
	@echo "  make validate                 # Fast project check"

# Clean target
clean:
	@echo "Cleaning temporary files..."
	@find /tmp -name "auto-slopp-test-*" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null || true
	@rm -f test_*.log
	@echo "✓ Clean completed"