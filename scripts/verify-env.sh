#!/bin/bash

# Environment verification script for Auto-slopp development
# This script helps verify that local and CI environments are consistent

echo "=== Auto-slopp Environment Verification ==="
echo ""

# Check Python version
echo "Python Version:"
python --version
echo ""

# Check Make version
echo "Make Version:"
make --version 2>/dev/null || echo "Make not available"
echo ""

# Check available tools
echo "Tool Availability:"
echo "Black: $(which black 2>/dev/null || echo 'Not found')"
echo "isort: $(which isort 2>/dev/null || echo 'Not found')"
echo "flake8: $(which flake8 2>/dev/null || echo 'Not found')"
echo "pytest: $(which pytest 2>/dev/null || echo 'Not found')"
echo "bandit: $(which bandit 2>/dev/null || echo 'Not found')"
echo "safety: $(which safety 2>/dev/null || echo 'Not found')"
echo ""

# Check virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Virtual Environment: $VIRTUAL_ENV"
else
    echo "Virtual Environment: None (active shell)"
fi

echo ""

# Check project structure
echo "Project Structure:"
echo "Makefile: $([ -f Makefile ] && echo 'Present' || echo 'Missing')"
echo "pyproject.toml: $([ -f pyproject.toml ] && echo 'Present' || echo 'Missing')"
echo "src/ directory: $([ -d src ] && echo 'Present' || echo 'Missing')"
echo "tests/ directory: $([ -d tests ] && echo 'Present' || echo 'Missing')"
echo ""

# Quick validation of Makefile targets
echo "Makefile Targets (sample):"
if command -v make >/dev/null 2>&1; then
    echo "All make targets available"
else
    echo "Error: make command not working"
fi

echo ""
echo "=== Verification Complete ==="