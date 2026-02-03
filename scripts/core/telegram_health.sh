#!/bin/bash

# Telegram Health Monitoring Module
# Monitors Telegram integration health, connectivity, and performance
# Provides comprehensive health checks and status reporting

# Set script name for logging identification
SCRIPT_NAME="telegram_health"

# Source utilities and modules
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../utils.sh"
source "${SCRIPT_DIR}/telegram_logger.sh"
source "${SCRIPT_DIR}/telegram_security.sh"
source "${SCRIPT_DIR}/telegram_queue.sh"

# Set up error handling
setup_error_handling

# Health check result codes
readonly HEALTH_STATUS_HEALTHY="healthy"
readonly HEALTH_STATUS_DEGRADED="degraded"
readonly HEALTH_STATUS_UNHEALTHY="unhealthy"

# Function to check Telegram API connectivity
check_api_connectivity() {
    local bot_token="${TELEGRAM_BOT_TOKEN:-}"
    local timeout="${TELEGRAM_API_TIMEOUT_SECONDS:-10}"
    
    if [[ -z "$bot_token" ]]; then
        echo "$HEALTH_STATUS_UNHEALTHY|No bot token configured"
        return 1
    fi
    
    if ! validate_bot_token_format "$bot_token"; then
        echo "$HEALTH_STATUS_UNHEALTHY|Invalid bot token format"
        return 1
    fi
    
    local test_url="https://api.telegram.org/bot${bot_token}/getMe"
    local response
    local start_time
    start_time=$(date +%s%3N)  # Millisecond precision
    
    if response=$(curl -s -w "%{http_code}" \
        --connect-timeout "$timeout" \
        --max-time "$timeout" \
        "$test_url" 2>/dev/null); then
        
        local end_time
        end_time=$(date +%s%3N)
        local response_time=$((end_time - start_time))
        
        local http_code="${response: -3}"
        local response_body="${response%???}"
        
        if [[ "$http_code" == "200" ]]; then
            local bot_info
            bot_info=$(echo "$response_body" | jq -r '.result.username // "unknown"' 2>/dev/null || echo "unknown")
            echo "$HEALTH_STATUS_HEALTHY|API OK (${response_time}ms) @$bot_info"
            return 0
        elif [[ "$http_code" == "401" ]]; then
            echo "$HEALTH_STATUS_UNHEALTHY|Authentication failed"
            return 1
        elif [[ "$http_code" =~ ^4[0-9][0-9]$ ]]; then
            echo "$HEALTH_STATUS_DEGRADED|Client error HTTP $http_code"
            return 2
        elif [[ "$http_code" =~ ^5[0-9][0-9]$ ]]; then
            echo "$HEALTH_STATUS_DEGRADED|Server error HTTP $http_code"
            return 2
        else
            echo "$HEALTH_STATUS_DEGRADED|Unexpected HTTP $http_code"
            return 2
        fi
    else
        echo "$HEALTH_STATUS_UNHEALTHY|Connection failed"
        return 1
    fi
}

# Function to check rate limiting status
check_rate_limiting() {
    local messages_per_second="${TELEGRAM_RATE_LIMITING_MESSAGES_PER_SECOND:-5}"
    local burst_size="${TELEGRAM_RATE_LIMITING_BURST_SIZE:-20}"
    local current_time
    current_time=$(date +%s)
    
    # Check if we're currently rate limited
    if [[ -f "/tmp/telegram_rate_limited" ]]; then
        local rate_limited_until
        rate_limited_until=$(cat "/tmp/telegram_rate_limited" 2>/dev/null || echo "0")
        if [[ $current_time -lt $rate_limited_until ]]; then
            local remaining_time=$((rate_limited_until - current_time))
            echo "$HEALTH_STATUS_DEGRADED|Currently rate limited (${remaining_time}s remaining)"
            return 2
        fi
    fi
    
    # Check recent message rate
    local recent_window=60  # Last 60 seconds
    local recent_count=0
    
    # This would need access to actual message logs or counters
    # For now, we'll simulate based on rate limiting state
    if [[ $TELEGRAM_MESSAGES_SENT -gt $((messages_per_second * recent_window / 2)) ]]; then
        echo "$HEALTH_STATUS_DEGRADED|High message rate ($TELEGRAM_MESSAGES_SENT messages in window)"
        return 2
    fi
    
    echo "$HEALTH_STATUS_HEALTHY|Rate limiting OK (${messages_per_second}/s limit)"
    return 0
}

# Function to check queue health
check_queue_health() {
    local queue_dir="/tmp/telegram_queue"
    
    if [[ ! -d "$queue_dir" ]]; then
        echo "$HEALTH_STATUS_DEGRADED|Queue directory not found"
        return 2
    fi
    
    # Count queue status
    local pending
    pending=$(find "$queue_dir" -name "*.msg" -exec grep -l "^status: pending$" {} \; 2>/dev/null | wc -l)
    local retry
    retry=$(find "$queue_dir" -name "*.msg" -exec grep -l "^status: retry$" {} \; 2>/dev/null | wc -l)
    local failed
    failed=$(find "${queue_dir}/processed" -name "*.msg" -exec grep -l "^status: failed$" {} \; 2>/dev/null | wc -l)
    
    local total_pending=$((pending + retry))
    local total_processed=$((failed))
    
    # Check for queue size issues
    if [[ $total_pending -gt 100 ]]; then
        echo "$HEALTH_STATUS_DEGRADED|Large queue backlog: $total_pending pending"
        return 2
    fi
    
    # Check for high failure rate
    if [[ $total_processed -gt 0 ]]; then
        local failure_rate=$((total_processed * 100 / (total_processed + pending + retry)))
        if [[ $failure_rate -gt 50 ]]; then
            echo "$HEALTH_STATUS_DEGRADED|High failure rate: ${failure_rate}%"
            return 2
        fi
    fi
    
    echo "$HEALTH_STATUS_HEALTHY|Queue OK ($pending pending, $retry retry, $failed failed)"
    return 0
}

# Function to check configuration consistency
check_configuration() {
    local issues=()
    
    # Check essential configuration
    if [[ "${TELEGRAM_ENABLED:-false}" != "true" ]]; then
        issues+=("Telegram logging disabled")
    fi
    
    if [[ -z "$TELEGRAM_BOT_TOKEN" ]]; then
        issues+=("Bot token not configured")
    fi
    
    if [[ -z "$TELEGRAM_CHAT_ID" ]]; then
        issues+=("Chat ID not configured")
    fi
    
    # Check configuration format
    if [[ -n "$TELEGRAM_BOT_TOKEN" ]] && ! validate_bot_token_format "$TELEGRAM_BOT_TOKEN"; then
        issues+=("Invalid bot token format")
    fi
    
    if [[ -n "$TELEGRAM_CHAT_ID" ]] && ! validate_chat_id "$TELEGRAM_CHAT_ID"; then
        issues+=("Invalid chat ID format")
    fi
    
    # Check rate limiting configuration
    local messages_per_second="${TELEGRAM_RATE_LIMITING_MESSAGES_PER_SECOND:-5}"
    if [[ $messages_per_second -lt 1 ]] || [[ $messages_per_second -gt 30 ]]; then
        issues+=("Rate limit setting may be problematic: $messages_per_second/s")
    fi
    
    # Check message length configuration
    local max_length="${TELEGRAM_FORMATTING_MAX_MESSAGE_LENGTH:-4000}"
    if [[ $max_length -gt 4096 ]] || [[ $max_length -lt 100 ]]; then
        issues+=("Message length may be problematic: $max_length chars")
    fi
    
    if [[ ${#issues[@]} -eq 0 ]]; then
        echo "$HEALTH_STATUS_HEALTHY|Configuration valid"
        return 0
    elif [[ ${#issues[@]} -le 2 ]]; then
        echo "$HEALTH_STATUS_DEGRADED|Configuration issues: ${issues[*]}"
        return 2
    else
        echo "$HEALTH_STATUS_UNHEALTHY|Multiple configuration issues: ${issues[*]}"
        return 1
    fi
}

# Function to check security configuration
check_security() {
    local issues=()
    
    # Check for hardcoded tokens
    if ! check_hardcoded_tokens "$(dirname "${SCRIPT_DIR}")" 2>/dev/null; then
        issues+=("Potential security issues detected")
    fi
    
    # Check token storage security
    if [[ -f "/etc/telegram/token" ]]; then
        if ! validate_token_file_permissions "/etc/telegram/token" 2>/dev/null; then
            issues+=("Token file permission issues")
        fi
    fi
    
    # Check environment security
    if [[ "${TELEGRAM_SECURITY_HIDE_TOKENS_IN_LOGS:-true}" != "true" ]]; then
        issues+=("Token hiding in logs disabled")
    fi
    
    if [[ "${TELEGRAM_SECURITY_REQUIRE_HTTPS:-true}" != "true" ]]; then
        issues+=("HTTPS requirement disabled")
    fi
    
    if [[ ${#issues[@]} -eq 0 ]]; then
        echo "$HEALTH_STATUS_HEALTHY|Security configuration OK"
        return 0
    elif [[ ${#issues[@]} -eq 1 ]]; then
        echo "$HEALTH_STATUS_DEGRADED|Security issue: ${issues[0]}"
        return 2
    else
        echo "$HEALTH_STATUS_UNHEALTHY|Multiple security issues: ${issues[*]}"
        return 1
    fi
}

# Function to check performance metrics
check_performance() {
    local issues=()
    local metrics=()
    
    # Check API response times
    local api_result
    api_result=$(check_api_connectivity)
    local api_status="${api_result%%|*}"
    
    if [[ "$api_status" != "$HEALTH_STATUS_HEALTHY" ]]; then
        issues+=("API connectivity issues")
    else
        local api_details="${api_result#*|}"
        if [[ "$api_details" =~ \(([0-9]+)ms\) ]]; then
            local response_time="${BASH_REMATCH[1]}"
            metrics+=("API response: ${response_time}ms")
            
            if [[ $response_time -gt 5000 ]]; then
                issues+=("Slow API response time")
            fi
        fi
    fi
    
    # Check queue processing rate
    local queue_result
    queue_result=$(check_queue_health)
    local queue_status="${queue_result%%|*}"
    
    if [[ "$queue_status" != "$HEALTH_STATUS_HEALTHY" ]]; then
        issues+=("Queue performance issues")
    fi
    
    if [[ ${#issues[@]} -eq 0 ]]; then
        local metric_string
        metric_string=$(IFS=", "; echo "${metrics[*]}")
        echo "$HEALTH_STATUS_HEALTHY|Performance OK ($metric_string)"
        return 0
    else
        echo "$HEALTH_STATUS_DEGRADED|Performance issues: ${issues[*]}"
        return 2
    fi
}

# Function to run comprehensive health check
run_telegram_health_check() {
    local detailed="${1:-false}"
    local overall_status="$HEALTH_STATUS_HEALTHY"
    local checks=()
    local failed_checks=()
    local degraded_checks=()
    
    log "INFO" "Running Telegram integration health check..."
    
    # Run all health checks
    local api_check
    api_check=$(check_api_connectivity)
    checks+=("API: $api_check")
    
    local rate_limit_check
    rate_limit_check=$(check_rate_limiting)
    checks+=("Rate Limiting: $rate_limit_check")
    
    local queue_check
    queue_check=$(check_queue_health)
    checks+=("Queue: $queue_check")
    
    local config_check
    config_check=$(check_configuration)
    checks+=("Configuration: $config_check")
    
    local security_check
    security_check=$(check_security)
    checks+=("Security: $security_check")
    
    if [[ "$detailed" == "true" ]]; then
        local performance_check
        performance_check=$(check_performance)
        checks+=("Performance: $performance_check")
    fi
    
    # Determine overall status
    for check in "${checks[@]}"; do
        local status="${check%%|*}"
        case "$status" in
            "$HEALTH_STATUS_UNHEALTHY")
                failed_checks+=("$check")
                overall_status="$HEALTH_STATUS_UNHEALTHY"
                ;;
            "$HEALTH_STATUS_DEGRADED")
                if [[ "$overall_status" != "$HEALTH_STATUS_UNHEALTHY" ]]; then
                    overall_status="$HEALTH_STATUS_DEGRADED"
                fi
                degraded_checks+=("$check")
                ;;
        esac
    done
    
    # Report results
    local timestamp
    timestamp=$(generate_timestamp "${TIMESTAMP_FORMAT:-default}" "${TIMESTAMP_TIMEZONE:-local}")
    
    case "$overall_status" in
        "$HEALTH_STATUS_HEALTHY")
            log "SUCCESS" "Telegram health check: $overall_status"
            if [[ "$detailed" == "true" ]]; then
                for check in "${checks[@]}"; do
                    log "INFO" "  ${check#*|}"
                done
            fi
            ;;
        "$HEALTH_STATUS_DEGRADED")
            log "WARNING" "Telegram health check: $overall_status"
            for check in "${degraded_checks[@]}"; do
                log "WARNING" "  ${check#*|}"
            done
            ;;
        "$HEALTH_STATUS_UNHEALTHY")
            log "ERROR" "Telegram health check: $overall_status"
            for check in "${failed_checks[@]}"; do
                log "ERROR" "  ${check#*|}"
            done
            ;;
    esac
    
    echo "$overall_status"
    return 0
}

# Function to get health check summary
get_telegram_health_summary() {
    local health_result
    health_result=$(run_telegram_health_check "false")
    local status="${health_result%%|*}"
    
    local timestamp
    timestamp=$(generate_timestamp "${TIMESTAMP_FORMAT:-default}" "${TIMESTAMP_TIMEZONE:-local}")
    
    cat << EOF
Telegram Integration Health Summary
Generated: $timestamp
Overall Status: $status

Quick Checks:
$(run_telegram_health_check "true" | grep "  " | sed 's/^  /- /')

For detailed diagnostics, run: run_telegram_health_check true
EOF
}

# Function to set up periodic health checks
setup_health_monitoring() {
    local interval_minutes="${TELEGRAM_HEALTH_HEALTH_CHECK_INTERVAL_MINUTES:-15}"
    
    if [[ "${TELEGRAM_HEALTH_ENABLE_HEALTH_CHECKS:-true}" != "true" ]]; then
        log "INFO" "Telegram health monitoring is disabled"
        return 0
    fi
    
    log "INFO" "Setting up Telegram health monitoring (interval: ${interval_minutes}min)"
    
    # Create health check script that will be called periodically
    cat > "/tmp/telegram_health_monitor.sh" << 'EOF'
#!/bin/bash
# Telegram Health Monitor - called periodically

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../scripts/core" && pwd)"
source "$SCRIPT_DIR/telegram_health.sh"

result=$(run_telegram_health_check "false")
status="${result%%|*}"

if [[ "$status" != "healthy" ]]; then
    # Send health alert to logs (will be forwarded to Telegram if configured)
    log "WARNING" "Telegram health alert: $status"
fi
EOF
    
    chmod +x "/tmp/telegram_health_monitor.sh"
    
    # Note: In a real implementation, you'd set this up with cron or systemd
    # For now, we'll just log that it's configured
    log "INFO" "Health monitoring configured. Consider adding to crontab:"
    log "INFO" "*/${interval_minutes} * * * * /tmp/telegram_health_monitor.sh"
}

# Function to cleanup health monitoring
cleanup_health_monitoring() {
    rm -f "/tmp/telegram_health_monitor.sh"
    log "DEBUG" "Health monitoring cleanup completed"
}

# Cleanup on exit
trap cleanup_health_monitoring EXIT

log "DEBUG" "Telegram health monitoring module loaded"