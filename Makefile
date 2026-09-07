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
	uv sync --extra dev

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
	@uv run --extra dev which black isort flake8 || echo "Some tools missing"
	@echo "Running black..."
	uv run --extra dev black --check --diff src/ tests/ || (echo "❌ Black formatting check failed" && exit 1)
	@echo "✅ Black formatting check passed"
	@echo "Running isort..."
	uv run --extra dev isort --check-only --diff src/ tests/ || (echo "❌ isort import sorting check failed" && exit 1)
	@echo "✅ isort import sorting check passed"
	@echo "Running flake8..."
	uv run --extra dev flake8 src/ tests/ || (echo "❌ flake8 linting failed" && exit 1)
	@echo "✅ flake8 linting passed"

# Format code
format:
	@echo "🎨 Formatting code..."
	uv run --extra dev black src/ tests/
	uv run --extra dev isort src/ tests/
	@echo "✅ Code formatting completed"

# Run unit tests
test-unit:
	@echo "🧪 Running unit tests..."
	uv run --extra dev python -m pytest tests/ -v --tb=short -m "not integration" || (echo "❌ Tests failed" && exit 1)
	@echo "✅ All tests passed"

# Run tests with coverage
coverage:
	@echo "📊 Running tests with coverage..."
	uv run --extra dev python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html -m "not integration" || (echo "❌ Tests failed" && exit 1)
	@echo "✅ Coverage report generated"
	@echo "📁 HTML coverage report available at htmlcov/index.html"

# Run security vulnerability scans
security:
	@echo "🔒 Running security scans..."
	@echo "Running pip-audit..."
	uv run --extra dev pip-audit --ignore-vuln PYSEC-2026-25 --ignore-vuln PYSEC-2026-188 --ignore-vuln PYSEC-2026-2119 --ignore-vuln PYSEC-2026-2121 --ignore-vuln PYSEC-2026-2120 --ignore-vuln PYSEC-2026-2132 --ignore-vuln PYSEC-2026-35 --ignore-vuln PYSEC-2026-36 --ignore-vuln GHSA-537c-gmf6-5ccf --ignore-vuln PYSEC-2026-2475 --ignore-vuln PYSEC-2026-2476 --ignore-vuln PYSEC-2026-215 --ignore-vuln CVE-2026-52870 --ignore-vuln CVE-2026-52869 --ignore-vuln CVE-2026-59950 --ignore-vuln GHSA-4xgf-cpjx-pc3j --ignore-vuln PYSEC-2026-2987 --ignore-vuln PYSEC-2026-120 --ignore-vuln PYSEC-2026-179 --ignore-vuln PYSEC-2026-175 --ignore-vuln PYSEC-2026-178 --ignore-vuln PYSEC-2026-176 --ignore-vuln PYSEC-2026-177 --ignore-vuln PYSEC-2026-1845 --ignore-vuln PYSEC-2026-2270 --ignore-vuln PYSEC-2026-3038 --ignore-vuln PYSEC-2026-3037 --ignore-vuln PYSEC-2026-3036 --ignore-vuln PYSEC-2026-3040 --ignore-vuln PYSEC-2026-3039 --ignore-vuln PYSEC-2026-2275 --ignore-vuln PYSEC-2026-3447 --ignore-vuln PYSEC-2026-161 --ignore-vuln PYSEC-2026-248 --ignore-vuln PYSEC-2026-249 --ignore-vuln PYSEC-2026-2281 --ignore-vuln PYSEC-2026-2280 --ignore-vuln PYSEC-2026-142 --ignore-vuln PYSEC-2026-141 --ignore-vuln PYSEC-2026-2192 --ignore-vuln PYSEC-2026-2573 --ignore-vuln PYSEC-2026-2575 --ignore-vuln GHSA-f4xh-w4cj-qxq8 --ignore-vuln GHSA-6v7p-g79w-8964 --ignore-vuln PYSEC-2026-196 --ignore-vuln PYSEC-2026-2875 --ignore-vuln PYSEC-2026-2876 --ignore-vuln PYSEC-2026-3072 --ignore-vuln PYSEC-2026-3071 --ignore-vuln GHSA-4gg8-gxpx-9rph --ignore-vuln PYSEC-2026-3552 --ignore-vuln PYSEC-2026-3721 || (echo "❌ pip-audit security check failed" && exit 1)
	@echo "✅ pip-audit security check passed"
	@echo "Running bandit security linter..."
	uv run --extra dev bandit -r src/ --severity-level=medium || (echo "❌ Bandit security linter failed" && exit 1)
	@echo "✅ Bandit security linter passed"

# Run performance tests specifically
test-performance:
	@echo "⚡ Running performance tests..."
	uv run --extra dev python -m pytest -m performance -v --tb=short || (echo "❌ Performance tests failed" && exit 1)
	@echo "✅ Performance tests passed"

# Run integration tests specifically
test-integration:
	@echo "🔗 Running integration tests..."
	uv run --extra dev python -m pytest -m integration -v --tb=short || (echo "❌ Integration tests failed" && exit 1)
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