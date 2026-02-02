#!/bin/bash

# Simple test for basic Telegram security functions

echo "Testing basic Telegram security functionality..."

# Source the security module
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../scripts/utils.sh"
source "${SCRIPT_DIR}/../scripts/core/telegram_security.sh"

# Test 1: Token format validation
echo "1. Testing token validation..."
TEST_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz-12345abc"
if validate_bot_token_format "$TEST_TOKEN"; then
    echo "   ✓ Token validation passed"
else
    echo "   ✗ Token validation failed"
fi

# Test 2: Chat ID validation
echo "2. Testing chat ID validation..."
if validate_chat_id "@test_channel"; then
    echo "   ✓ Chat ID validation passed"
else
    echo "   ✗ Chat ID validation failed"
fi

# Test 3: Token redaction
echo "3. Testing token redaction..."
TEST_MESSAGE="This contains a token 123456789:ABCdefGHIjklMNOpqrsTUVwxyz-12345abc in the message"
REDACTED_MESSAGE=$(redact_token_in_output "$TEST_MESSAGE")
if [[ "$REDACTED_MESSAGE" == *"This contains a token [REDACTED_TOKEN] in the message" ]]; then
    echo "   ✓ Token redaction passed"
else
    echo "   ✗ Token redaction failed"
    echo "   Original: $TEST_MESSAGE"
    echo "   Redacted: $REDACTED_MESSAGE"
fi

# Test 4: Audit logging
echo "4. Testing audit logging..."
AUDIT_FILE="$HOME/.telegram_audit.log"
if audit_token_access "TEST_OPERATION" "SUCCESS" "Test audit message"; then
    echo "   ✓ Audit logging executed"
    if [[ -f "$AUDIT_FILE" ]]; then
        echo "   ✓ Audit file created"
    else
        echo "   ⚠ Audit file not found (may be permission issue)"
    fi
else
    echo "   ✗ Audit logging failed"
fi

# Test 5: Revoked token checking
echo "5. Testing revoked token checking..."
# Initially should not be revoked
if ! is_token_revoked "$TEST_TOKEN"; then
    echo "   ✓ New token not marked as revoked"
else
    echo "   ⚠ New token unexpectedly marked as revoked"
fi

echo ""
echo "Basic security functionality test completed."
echo "For full testing, run with proper permissions to test encryption features."