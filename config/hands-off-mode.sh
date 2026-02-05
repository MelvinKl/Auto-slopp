#!/bin/bash
# Auto-slopp Hands-off Configuration
# This file configures the system to run completely without user interaction

# Core auto-confirmation settings
export AUTO_CONFIRM="true"
export INTERACTIVE_MODE="false"

# Package management
export AUTO_INSTALL_PACKAGES="true"

# Service management
export FORCE_INSTALL="true"
export FORCE_ROOT="true"

# Branch management
export CONFIRM_BEFORE_DELETE="false"
export CONFIRMATION_TIMEOUT="0"

# Telegram security
export SKIP_TOKEN_CONFIRMATION="true"

# Logging level for hands-off mode
export LOG_LEVEL="INFO"

# Safety settings (can be overridden if needed)
# export SAFE_MODE="false"  # Uncomment to disable all safety checks

echo "Hands-off mode configured: All user interactions disabled"
echo "Set AUTO_CONFIRM=false to re-enable interactive prompts"