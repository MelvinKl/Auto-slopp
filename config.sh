#!/bin/bash

# Configuration for Repository Automation System
# This file contains all configurable paths and settings

# Directory containing all repositories to process
REPO_DIRECTORY="${REPO_DIRECTORY:-$HOME/repositories}"

# Directory for this automation repository
AUTOMATION_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Scripts directory
SCRIPTS_DIR="$AUTOMATION_ROOT/scripts"

# Logs directory
LOGS_DIR="$AUTOMATION_ROOT/logs"

# Maximum file number to process in planner.sh (files with higher numbers are skipped)
MAX_FILE_NUMBER="${MAX_FILE_NUMBER:-999}"

# Sleep duration between main.sh cycles (in seconds)
MAIN_SLEEP_DURATION="${MAIN_SLEEP_DURATION:-1800}"  # 30 minutes

# Git settings
GIT_AUTHOR_NAME="${GIT_AUTHOR_NAME:-Automation Bot}"
GIT_AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-automation@example.com}"

# OpenCode CLI path (adjust if needed)
OPencode_CLI="${OPencode_CLI:-opencode}"

# Beads CLI path (adjust if needed)
BEADS_CLI="${BEADS_CLI:-bd}"

# Log level (DEBUG, INFO, WARN, ERROR)
LOG_LEVEL="${LOG_LEVEL:-INFO}"