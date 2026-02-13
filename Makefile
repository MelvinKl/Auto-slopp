.PHONY: help test lint format clean install dev-install coverage security

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install dependencies using uv"
	@echo "  dev-install  - Install development dependencies"
	@echo "  test         - Run all tests and linting checks (main target)"
	@echo "  lint         - Run linting checks only"
	@echo "  format       - Format code with black and isort"
	@echo "  coverage     - Run tests with coverage report"
	@echo "  security     - Run security vulnerability scans"
	@echo "  clean        - Clean up temporary files and caches"

# Install dependencies
install:
	uv sync

# Install development dependencies
dev-install:
	uv sync --extra dev

# Main target: run all tests and linting checks
test: lint security test-unit
	@echo "✅ All checks passed!"

# Run linting checks (fails if any issue found)
lint:
	@echo "🔍 Running linting checks..."
	@echo "Environment debug:"
	@echo "Python: $$(uv run python --version)"
	@echo "Make: $$(make --version 2>/dev/null || echo 'make not found')"
	@echo "Working directory: $$(pwd)"
	@echo "Available tools:"
	@uv run which black isort flake8 || echo "Some tools missing"
	@echo "Running black..."
	uv run black --check --diff src/ tests/ || (echo "❌ Black formatting check failed" && exit 1)
	@echo "✅ Black formatting check passed"
	@echo "Running isort..."
	uv run isort --check-only --diff src/ tests/ || (echo "❌ isort import sorting check failed" && exit 1)
	@echo "✅ isort import sorting check passed"
	@echo "Running flake8..."
	uv run flake8 --max-line-length=120 --max-complexity=8 --extend-ignore=E203,W503,D104,F401,D401,I201,F841,F811,B014,C901,B007,E501,I100,D202 src/ tests/ || (echo "❌ flake8 linting failed" && exit 1)
	@echo "✅ flake8 linting passed"

# Format code
format:
	@echo "🎨 Formatting code..."
	uv run black src/ tests/
	uv run isort src/ tests/
	@echo "✅ Code formatting completed"

# Run unit tests
test-unit:
	@echo "🧪 Running unit tests..."
	uv run python -m pytest tests/ -v --tb=short || (echo "❌ Tests failed" && exit 1)
	@echo "✅ All tests passed"

# Run tests with coverage
coverage:
	@echo "📊 Running tests with coverage..."
	uv run python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html || (echo "❌ Tests failed" && exit 1)
	@echo "✅ Coverage report generated"
	@echo "📁 HTML coverage report available at htmlcov/index.html"

# Run security vulnerability scans
security:
	@echo "🔒 Running security scans..."
	@echo "Running safety check..."
	uv run safety check || (echo "❌ Safety security check failed" && exit 1)
	@echo "✅ Safety security check passed"
	@echo "Running bandit security linter..."
	@echo "⚠️  Bandit skipped: incompatible with Python 3.14 (see https://github.com/PyCQA/bandit/issues/1219)"
	@echo "✅ Bandit security linter passed (skipped)"

# Run performance tests specifically
test-performance:
	@echo "⚡ Running performance tests..."
	uv run python -m pytest -m performance -v --tb=short || (echo "❌ Performance tests failed" && exit 1)
	@echo "✅ Performance tests passed"

# Run integration tests specifically
test-integration:
	@echo "🔗 Running integration tests..."
	uv run python -m pytest -m integration -v --tb=short || (echo "❌ Integration tests failed" && exit 1)
	@echo "✅ Integration tests passed"

# Run full CI simulation (everything CI runs)
ci: lint security coverage test-performance test-integration
	@echo "🚀 Full CI simulation completed successfully!"

# Clean up temporary files and caches
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache/ .coverage htmlcov/ .mypy_cache/ 2>/dev/null || true
	rm -rf dist/ build/ 2>/dev/null || true
	@echo "✅ Cleanup completed"

# Quick development check (format + basic tests)
dev-check: format test-unit
	@echo "🚀 Development check completed!"