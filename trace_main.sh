#!/bin/bash
echo "1. Initial state:"
echo "   BASH_SOURCE[0] = ${BASH_SOURCE[0]}"
echo "   PWD = $(pwd)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "2. After setting SCRIPT_DIR:"
echo "   SCRIPT_DIR = $SCRIPT_DIR"

echo "3. About to source config.sh from: $SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/config.sh"
echo "4. After sourcing config.sh:"
echo "   SCRIPT_DIR = $SCRIPT_DIR"

source "$SCRIPT_DIR/scripts/utils.sh"
echo "5. After sourcing utils.sh:"
echo "   SCRIPT_DIR = $SCRIPT_DIR"

SCRIPTS_DIR="$SCRIPT_DIR/scripts"
echo "6. After setting SCRIPTS_DIR:"
echo "   SCRIPTS_DIR = $SCRIPTS_DIR"
