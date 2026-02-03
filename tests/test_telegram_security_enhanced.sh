#!/bin/bash

# Test script for Enhanced Telegram Bot Security Features
# Tests token encryption, rotation, audit logging, and revocation

# Set script name for logging
SCRIPT_NAME="telegram_security_test"

# Source utilities and security module
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../scripts/utils.sh"
source "${SCRIPT_DIR}/../scripts/core/telegram_security.sh"

# Set up error handling
setup_error_handling

# Test configuration (use user-accessible paths)
TEST_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890"
TEST_TOKEN_INVALID="invalid:token"
TEST_ENCRYPTION_KEY_FILE="$HOME/.test_telegram_encryption_key"
TEST_TOKEN_ENCRYPTED_FILE="$HOME/.test_telegram_token.enc"
TEST_REVOKE_LIST_FILE="$HOME/.test_telegram_revoke.json"
TEST_ROTATION_HISTORY_FILE="$HOME/.test_telegram_rotation.json"

# Override file locations for testing
TELEGRAM_TOKEN_ENCRYPTION_KEY_FILE="$TEST_ENCRYPTION_KEY_FILE"
TELEGRAM_TOKEN_ENCRYPTED_FILE="$TEST_TOKEN_ENCRYPTED_FILE"
TELEGRAM_TOKEN_REVOKE_LIST_FILE="$TEST_REVOKE_LIST_FILE"
TELEGRAM_TOKEN_ROTATION_HISTORY_FILE="$TEST_ROTATION_HISTORY_FILE"
TELEGRAM_DIR_PERMISSIONS=700

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test helper functions
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="${3:-0}"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo "Running test: $test_name"
    
    if eval "$test_command" >/dev/null 2>&1; then
        local actual_result=$?
        if [[ $actual_result -eq $expected_result ]]; then
            echo "  ✓ PASSED"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo "  ✗ FAILED (exit code: $actual_result, expected: $expected_result)"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        echo "  ✗ FAILED (command failed)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    echo ""
}

# Cleanup function
cleanup_test_files() {
    echo "Cleaning up test files..."
    rm -f "$TEST_ENCRYPTION_KEY_FILE" "$TEST_TOKEN_ENCRYPTED_FILE" "$TEST_REVOKE_LIST_FILE" "$TEST_ROTATION_HISTORY_FILE" "$HOME/.test_telegram_token"
    rm -rf "$HOME/.test_telegram_config"
    rm -f "$HOME/.telegram_audit.log" 2>/dev/null
}

echo "=================================================="
echo "Enhanced Telegram Bot Security Test Suite"
echo "=================================================="
echo ""

# Cleanup any existing test files
cleanup_test_files

echo "1. Testing Token Validation"
echo "----------------------------"

run_test "Valid token format" "validate_bot_token_format '$TEST_TOKEN'" 0
run_test "Invalid token format" "validate_bot_token_format '$TEST_TOKEN_INVALID'" 1
run_test "Empty token" "validate_bot_token_format ''" 1
run_test "Valid chat ID" "validate_chat_id '@test_channel'" 0
run_test "Invalid chat ID" "validate_chat_id 'invalid_chat'" 1

echo "2. Testing Encryption/Decryption"
echo "---------------------------------"

run_test "Generate encryption key" "get_encryption_key" 0
run_test "Encrypt valid token" "encrypt_token '$TEST_TOKEN'" 0
run_test "Decrypt encrypted token" "decrypt_token \$(encrypt_token '$TEST_TOKEN')" 0

# Test encryption round-trip
ENCRYPTED_TOKEN=$(encrypt_token "$TEST_TOKEN" 2>/dev/null)
DECRYPTED_TOKEN=$(decrypt_token "$ENCRYPTED_TOKEN" 2>/dev/null)
if [[ "$DECRYPTED_TOKEN" == "$TEST_TOKEN" ]]; then
    echo "Running test: Encryption round-trip"
    echo "  ✓ PASSED"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
else
    echo "Running test: Encryption round-trip"
    echo "  ✗ FAILED (tokens don't match)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
fi
echo ""

echo "3. Testing Token Revocation"
echo "---------------------------"

run_test "Revoke valid token" "revoke_token '$TEST_TOKEN' 'Test revocation'" 0
run_test "Check token is revoked" "is_token_revoked '$TEST_TOKEN'" 0
run_test "Attempt to revoke invalid token" "revoke_token '$TEST_TOKEN_INVALID' 'Test revocation'" 1

echo "4. Testing Token Rotation"
echo "-------------------------"

NEW_TEST_TOKEN="987654321:ZYXwvuTSRqpoNMLkJIHgfeDCBA-9876543210"
run_test "Rotate to new token" "rotate_token '$TEST_TOKEN' '$NEW_TEST_TOKEN'" 0
run_test "Check old token is revoked" "is_token_revoked '$TEST_TOKEN'" 0
run_test "Check new token is not revoked" "is_token_revoked '$NEW_TEST_TOKEN'" 1

echo "5. Testing Secure Token Storage"
echo "--------------------------------"

run_test "Setup encrypted storage" "setup_secure_token_storage '$NEW_TEST_TOKEN' '$HOME/.test_telegram_token' 'true'" 0
run_test "Load from encrypted storage" "load_token_from_storage '$HOME/.test_telegram_token' '$TEST_TOKEN_ENCRYPTED_FILE'" 0
run_test "Check token is loaded correctly" "[[ \"\$TELEGRAM_BOT_TOKEN\" == \"$NEW_TEST_TOKEN\" ]]" 0

echo "6. Testing Token Redaction"
echo "--------------------------"

TEST_MESSAGE="This message contains a token 123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890 and should be redacted"
REDACTED_MESSAGE=$(redact_token_in_output "$TEST_MESSAGE")
if [[ "$REDACTED_MESSAGE" == *"This message contains a token [REDACTED_TOKEN] and should be redacted" ]]; then
    echo "Running test: Token redaction"
    echo "  ✓ PASSED"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
else
    echo "Running test: Token redaction"
    echo "  ✗ FAILED (redaction failed)"
    echo "  Original: $TEST_MESSAGE"
    echo "  Redacted: $REDACTED_MESSAGE"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
fi
echo ""

echo "7. Testing Audit Logging"
echo "------------------------"

run_test "Audit token access" "audit_token_access 'TEST_OPERATION' 'SUCCESS' 'Test message'" 0

# Check if audit log was created
AUDIT_FILE="/var/log/telegram_audit.log"
if [[ ! -f "$AUDIT_FILE" ]]; then
    AUDIT_FILE="$HOME/.telegram_audit.log"
fi

if [[ -f "$AUDIT_FILE" ]]; then
    echo "Running test: Audit log creation"
    echo "  ✓ PASSED"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
else
    echo "Running test: Audit log creation"
    echo "  ✗ FAILED (audit log not found)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
fi
echo ""

echo "8. Testing Rotation Check"
echo "-------------------------"

# Test with a token that has no rotation history
TEMP_TOKEN="111111111:tempTestTokenABCdefGHIjklMNOpqrsTUVwxyz"
run_test "Check rotation needed for new token" "check_token_rotation_needed '$TEMP_TOKEN'" 0

echo "9. Testing Security Health Check"
echo "--------------------------------"

run_test "Perform security health check" "perform_security_health_check" 0

echo "10. Testing Cleanup Functions"
echo "-----------------------------"

run_test "Cleanup revoked tokens" "cleanup_revoked_tokens" 0

echo "=================================================="
echo "Test Results Summary"
echo "=================================================="
echo "Total Tests: $TESTS_TOTAL"
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo "✓ ALL TESTS PASSED!"
    echo "Enhanced Telegram security features are working correctly."
else
    echo "✗ SOME TESTS FAILED!"
    echo "Please review the failed tests and fix any issues."
fi
echo ""

# Generate security report
echo "Generating security report..."
generate_security_report "config.yaml" "/tmp/test_telegram_security_report.txt"
echo "Security report saved to: /tmp/test_telegram_security_report.txt"
echo ""

# Cleanup test files
cleanup_test_files

echo "=================================================="
echo "Test completed"
echo "=================================================="

exit $([[ $TESTS_FAILED -eq 0 ]] && echo 0 || echo 1)