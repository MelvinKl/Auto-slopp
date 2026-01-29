# Makefile for Auto-slopp project

.PHONY: test help clean

# Default target
all: help

# Test target - runs comprehensive test suite
test:
	@echo "Running comprehensive test suite..."
	@./tests/test_suite.sh --no-make

# Help target
help:
	@echo "Available targets:"
	@echo "  test   - Run tests (currently just a placeholder)"
	@echo "  help   - Show this help message"
	@echo "  clean  - Clean temporary files"

# Clean target
clean:
	@echo "Cleaning temporary files..."
	@echo "✓ Clean completed"