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
	pip install -e .

# Install development dependencies
dev-install:
	pip install -e .[dev]

# Main target: run all tests and linting checks
test: lint security test-unit
	@echo "✅ All checks passed!"

# Run linting checks (fails if any issue found)
lint:
	@echo "🔍 Running linting checks..."
	@echo "Running black..."
	black --check --diff src/ tests/ || (echo "❌ Black formatting check failed" && exit 1)
	@echo "✅ Black formatting check passed"
	@echo "Running isort..."
	isort --check-only --diff src/ tests/ || (echo "❌ isort import sorting check failed" && exit 1)
	@echo "✅ isort import sorting check passed"
	@echo "Running flake8..."
	flake8 --max-line-length=120 --max-complexity=8 --extend-ignore=E203,W503,D104,F401,D401,I201,F841,F811,B014,C901,B007,E501,I100,D202 src/ tests/ || (echo "❌ flake8 linting failed" && exit 1)
	@echo "✅ flake8 linting passed"

# Format code
format:
	@echo "🎨 Formatting code..."
	black src/ tests/
	isort src/ tests/
	@echo "✅ Code formatting completed"

# Run unit tests
test-unit:
	@echo "🧪 Running unit tests..."
	. .venv/bin/activate && python -m pytest tests/ -v --tb=short || (echo "❌ Tests failed" && exit 1)
	@echo "✅ All tests passed"

# Run tests with coverage
coverage:
	@echo "📊 Running tests with coverage..."
	. .venv/bin/activate && python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html || (echo "❌ Tests failed" && exit 1)
	@echo "✅ Coverage report generated"
	@echo "📁 HTML coverage report available at htmlcov/index.html"

# Run security vulnerability scans
security:
	@echo "🔒 Running security scans..."
	@echo "Running safety check..."
	. .venv/bin/activate && safety check || (echo "❌ Safety security check failed" && exit 1)
	@echo "✅ Safety security check passed"
	@echo "Running bandit security linter..."
	. .venv/bin/activate && bandit -r src/ --severity-level=medium || (echo "❌ Bandit security linter failed" && exit 1)
	@echo "✅ Bandit security linter passed"

# Run performance tests specifically
test-performance:
	@echo "⚡ Running performance tests..."
	. .venv/bin/activate && python -m pytest -m performance -v --tb=short || (echo "❌ Performance tests failed" && exit 1)
	@echo "✅ Performance tests passed"

# Run integration tests specifically
test-integration:
	@echo "🔗 Running integration tests..."
	. .venv/bin/activate && python -m pytest -m integration -v --tb=short || (echo "❌ Integration tests failed" && exit 1)
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