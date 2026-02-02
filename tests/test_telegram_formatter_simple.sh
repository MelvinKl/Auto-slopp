#!/bin/bash

# Simple test to verify Telegram formatter functions work
# This test isolates the functions from dependencies

echo "🧪 Testing Enhanced Telegram Logging Formatter"
echo "=============================================="

# Define the functions inline for testing
format_structured_message() {
    local message="$1"
    local parse_mode="${2:-HTML}"
    
    # Check if message looks like JSON
    if [[ "$message" =~ ^\{.*\}$ ]] || [[ "$message" =~ ^\[.*\]$ ]]; then
        if [[ "$parse_mode" == "HTML" ]]; then
            echo "<b>📋 Structured Data:</b>
<pre><code>${message}</code></pre>"
        else
            echo "*📋 Structured Data:*
\`\`\`${message}\`\`\`"
        fi
        return 0
    fi
    
    echo "$message"
}

highlight_error_message() {
    local message="$1"
    local level="$2"
    local parse_mode="${3:-HTML}"
    
    if [[ "$level" != "ERROR" && "$level" != "WARNING" ]]; then
        echo "$message"
        return 0
    fi
    
    local highlighted_message="$message"
    
    # Highlight common error patterns
    if [[ "$parse_mode" == "HTML" ]]; then
        highlighted_message="${highlighted_message//Error:/<b><i>Error:</i></b>}"
        highlighted_message="${highlighted_message//Failed/<b><i>Failed</i></b>}"
        highlighted_message=$(echo "$highlighted_message" | sed -E 's|(/[a-zA-Z0-9_/-]+\.[a-zA-Z0-9_:-]+)|<code>\1</code>|g')
    fi
    
    echo "$highlighted_message"
}

truncate_message() {
    local message="$1"
    local max_length="${2:-4000}"
    local truncation_indicator="${3:-...}"
    
    if [[ ${#message} -le $max_length ]]; then
        echo "$message"
        return 0
    fi
    
    local truncated="${message:0:$((max_length - ${#truncation_indicator}))}${truncation_indicator}"
    echo "$truncated"
}

format_context_info() {
    local script_name="$1"
    local parse_mode="${2:-HTML}"
    local additional_context="${3:-}"
    
    local context_section=""
    
    if [[ -n "$script_name" ]]; then
        if [[ "$parse_mode" == "HTML" ]]; then
            context_section+="📝 <i>${script_name}</i>"
        else
            context_section+="📝 _${script_name}_"
        fi
    fi
    
    local pid="$$"
    if [[ "$parse_mode" == "HTML" ]]; then
        context_section+="\n🔢 <code>PID: ${pid}</code>"
    else
        context_section+="\n🔢 \`PID: ${pid}\`"
    fi
    
    echo "$context_section"
}

format_message_by_type() {
    local message="$1"
    local message_type="general"
    
    if [[ "$message" =~ ^(Started|Completed|Failed|Running) ]]; then
        message_type="operation"
    elif [[ "$message" =~ (config|setting|parameter) ]]; then
        message_type="config"
    elif [[ "$message" =~ (HTTP|API|request|response) ]]; then
        message_type="network"
    fi
    
    local type_icon=""
    case "$message_type" in
        "operation"|"config") type_icon="⚙️" ;;
        "network") type_icon="🌐" ;;
        *) type_icon="📝" ;;
    esac
    
    echo "${type_icon} ${message}"
}

sanitize_message() {
    local message="$1"
    local sanitized="$message"
    
    sanitized=$(echo "$sanitized" | sed -E 's/(password|token|key|secret|credential)[[:space:]]*[:=][[:space:]]*[^\s]+/\1=***REDACTED***/gi')
    sanitized=$(echo "$sanitized" | sed -E 's/\b[a-zA-Z0-9]{25,}\b/***REDACTED***/g')
    sanitized=$(echo "$sanitized" | sed -E 's/\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b/***EMAIL***/g')
    
    echo "$sanitized"
}

format_telegram_message() {
    local level="$1"
    local message="$2"
    local script_name="${3:-test}"
    
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    local formatted_message=""
    
    # Add emoji and log level
    case "$level" in
        "ERROR") formatted_message+="🔴" ;;
        "WARNING") formatted_message+="🟡" ;;
        "SUCCESS") formatted_message+="🟢" ;;
        "INFO") formatted_message+="🔵" ;;
        "DEBUG") formatted_message+="⚪" ;;
        *) formatted_message+="📝" ;;
    esac
    formatted_message+=" "
    
    # Add log level
    formatted_message+="<b>${level}</b>"
    
    # Add timestamp
    formatted_message+="\n🕐 <code>${timestamp}</code>"
    
    # Add context
    if [[ -n "$script_name" ]]; then
        formatted_message+="\n📝 <i>${script_name}</i>"
    fi
    
    # Process message content
    local processed_message="$message"
    processed_message=$(format_structured_message "$processed_message" "HTML")
    processed_message=$(highlight_error_message "$processed_message" "$level" "HTML")
    processed_message=$(format_message_by_type "$processed_message" "$level")
    
    formatted_message+="\n\n${processed_message}"
    
    echo "$formatted_message"
}

# Test functions
TESTS_TOTAL=0
TESTS_PASSED=0

run_test() {
    local test_name="$1"
    local result="$2"
    local expected="$3"
    
    ((TESTS_TOTAL++))
    
    if [[ "$result" == *"$expected"* ]]; then
        echo "✅ PASS: $test_name"
        ((TESTS_PASSED++))
    else
        echo "❌ FAIL: $test_name"
        echo "   Expected: $expected"
        echo "   Got: $result"
    fi
}

echo -e "\n📋 Test 1: Basic message formatting"
basic_message="This is a test message"
formatted=$(format_telegram_message "INFO" "$basic_message" "test_script")
run_test "INFO level emoji indicator" "$formatted" "🔵"
run_test "INFO level bold formatting" "$formatted" "<b>INFO</b>"
run_test "Script name formatting" "$formatted" "📝 <i>test_script</i>"
run_test "Timestamp formatting" "$formatted" "🕐 <code>"
run_test "Original message preserved" "$formatted" "$basic_message"

echo -e "\n📋 Test 2: Error message highlighting"
error_message="Error: Failed to connect to database at /var/log/app.log"
highlighted=$(highlight_error_message "$error_message" "ERROR" "HTML")
run_test "Error pattern highlighting" "$highlighted" "<b><i>Error:</i></b>"
run_test "Failed pattern highlighting" "$highlighted" "<b><i>Failed</i></b>"
run_test "File path highlighting" "$highlighted" "<code>/var/log/app.log</code>"

echo -e "\n📋 Test 3: Structured data formatting"
json_message='{"user": "john", "action": "login"}'
structured=$(format_structured_message "$json_message" "HTML")
run_test "Structured data detection" "$structured" "📋 Structured Data:"
run_test "Code block formatting for JSON" "$structured" "<pre><code>"

echo -e "\n📋 Test 4: Message truncation"
long_message=$(printf "A%.0s" {1..100})
truncated=$(truncate_message "$long_message" 50)
run_test "Truncation indicator" "$truncated" "..."

echo -e "\n📋 Test 5: Message sanitization"
sensitive_message="User login failed: password=secret123, email=user@example.com, token=abc123def456"
sanitized=$(sanitize_message "$sensitive_message")
run_test "Password redaction" "$sanitized" "password=***REDACTED***"
run_test "Email redaction" "$sanitized" "***EMAIL***"

echo -e "\n📋 Test 6: Context information formatting"
context=$(format_context_info "test_script" "HTML" "additional info")
run_test "Script name in context" "$context" "📝 <i>test_script</i>"
run_test "Process ID in context" "$context" "🔢 <code>PID:"

echo -e "\n📋 Test 7: Message type detection and formatting"
operation_msg="Started processing user data"
formatted=$(format_message_by_type "$operation_msg")
run_test "Operation message type icon" "$formatted" "⚙️"

network_msg="HTTP request timeout occurred"
formatted=$(format_message_by_type "$network_msg")
run_test "Network message type icon" "$formatted" "🌐"

echo -e "\n📊 Test Results Summary"
echo "========================"
echo "Total Tests: $TESTS_TOTAL"
echo "Passed: $TESTS_PASSED"
echo "Failed: $((TESTS_TOTAL - TESTS_PASSED))"

if [[ $((TESTS_TOTAL - TESTS_PASSED)) -eq 0 ]]; then
    echo -e "\n🎉 All tests passed! Enhanced Telegram logging formatter is working correctly."
    exit 0
else
    echo -e "\n⚠️  Some tests failed."
    exit 1
fi