#!/bin/bash

# Telegram Message Queue Management Module
# Handles message queuing, rate limiting, and background processing
# Ensures reliable delivery of messages while respecting API limits

# Set script name for logging identification
SCRIPT_NAME="telegram_queue"

# Source utilities and modules
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../utils.sh"
source "${SCRIPT_DIR}/telegram_logger.sh"
source "${SCRIPT_DIR}/telegram_security.sh"

# Set up error handling
setup_error_handling

# Global queue configuration
declare -g TELEGRAM_QUEUE_DIR="/tmp/telegram_queue"
declare -g TELEGRAM_QUEUE_LOCK_FILE="${TELEGRAM_QUEUE_DIR}/.lock"
declare -g TELEGRAM_RATE_LIMIT_FILE="${TELEGRAM_QUEUE_DIR}/.rate_limit"
declare -g TELEGRAM_QUEUE_MAX_SIZE="${TELEGRAM_QUEUE_MAX_SIZE:-1000}"
declare -g TELEGRAM_QUEUE_RETENTION_HOURS="${TELEGRAM_QUEUE_RETENTION_HOURS:-24}"

# Rate limiting state
declare -g TELEGRAM_MESSAGES_SENT=0
declare -g TELEGRAM_WINDOW_START=0
declare -g TELEGRAM_LAST_RESET=0

# Function to initialize queue system
init_telegram_queue() {
    # Create queue directory with secure permissions
    mkdir -p "$TELEGRAM_QUEUE_DIR"
    chmod 700 "$TELEGRAM_QUEUE_DIR"
    
    # Initialize rate limiting window
    TELEGRAM_WINDOW_START=$(date +%s)
    TELEGRAM_LAST_RESET=$TELEGRAM_WINDOW_START
    
    # Clean up old queue files
    cleanup_old_queue_files
    
    log "DEBUG" "Telegram queue system initialized"
}

# Function to acquire queue lock
acquire_queue_lock() {
    local timeout="${1:-30}"
    local count=0
    
    while [[ $count -lt $timeout ]]; do
        if mkdir "$TELEGRAM_QUEUE_LOCK_FILE" 2>/dev/null; then
            # Lock acquired successfully
            echo $$ > "${TELEGRAM_QUEUE_LOCK_FILE}/pid"
            log "DEBUG" "Queue lock acquired by process $$"
            return 0
        fi
        
        # Check if lock is stale (process no longer exists)
        if [[ -f "${TELEGRAM_QUEUE_LOCK_FILE}/pid" ]]; then
            local lock_pid
            lock_pid=$(cat "${TELEGRAM_QUEUE_LOCK_FILE}/pid" 2>/dev/null)
            if [[ -n "$lock_pid" ]] && ! kill -0 "$lock_pid" 2>/dev/null; then
                log "WARNING" "Removing stale queue lock from process $lock_pid"
                rm -rf "$TELEGRAM_QUEUE_LOCK_FILE"
                continue
            fi
        fi
        
        sleep 1
        ((count++))
    done
    
    log "ERROR" "Failed to acquire queue lock after ${timeout}s"
    return 1
}

# Function to release queue lock
release_queue_lock() {
    if [[ -d "$TELEGRAM_QUEUE_LOCK_FILE" ]]; then
        local lock_pid
        lock_pid=$(cat "${TELEGRAM_QUEUE_LOCK_FILE}/pid" 2>/dev/null)
        if [[ "$lock_pid" == "$$" ]]; then
            rm -rf "$TELEGRAM_QUEUE_LOCK_FILE"
            log "DEBUG" "Queue lock released by process $$"
            return 0
        else
            log "WARNING" "Attempted to release lock owned by different process: $lock_pid"
            return 1
        fi
    fi
    return 0
}

# Function to generate unique queue entry ID
generate_queue_id() {
    local timestamp
    timestamp=$(date +%s%3N)  # Millisecond precision
    local random
    random=$((RANDOM % 1000))
    echo "${timestamp}_${random}_$$"
}

# Function to add message to queue
enqueue_telegram_message() {
    local message="$1"
    local chat_id="${2:-${TELEGRAM_CHAT_ID}}"
    local parse_mode="${3:-HTML}"
    local priority="${4:-normal}"  # high, normal, low
    
    if [[ -z "$message" ]]; then
        log "ERROR" "Cannot enqueue empty message"
        return 1
    fi
    
    # Check queue size limit
    if ! check_queue_size; then
        log "WARNING" "Queue is full, dropping message"
        return 1
    fi
    
    # Acquire lock for queue operation
    if ! acquire_queue_lock 5; then
        log "WARNING" "Failed to acquire lock for enqueue, dropping message"
        return 1
    fi
    
    local queue_id
    queue_id=$(generate_queue_id)
    local queue_file="${TELEGRAM_QUEUE_DIR}/${queue_id}.msg"
    
    # Create queue entry
    cat > "$queue_file" << EOF
queue_id: $queue_id
timestamp: $(date +%s)
chat_id: $chat_id
parse_mode: $parse_mode
priority: $priority
status: pending
retry_count: 0
created_by: $$
message:
$message
EOF
    
    local result=$?
    release_queue_lock
    
    if [[ $result -eq 0 ]]; then
        log "DEBUG" "Message enqueued successfully: $queue_id"
        
        # Trigger background processor
        trigger_queue_processor &
        
        return 0
    else
        log "ERROR" "Failed to enqueue message"
        return 1
    fi
}

# Function to check queue size
check_queue_size() {
    local queue_size
    queue_size=$(find "$TELEGRAM_QUEUE_DIR" -name "*.msg" -type f | wc -l)
    
    if [[ $queue_size -ge $TELEGRAM_QUEUE_MAX_SIZE ]]; then
        log "WARNING" "Queue size limit reached: $queue_size/$TELEGRAM_QUEUE_MAX_SIZE"
        
        # Try to clean up old messages first
        cleanup_old_queue_files
        queue_size=$(find "$TELEGRAM_QUEUE_DIR" -name "*.msg" -type f | wc -l)
        
        if [[ $queue_size -ge $TELEGRAM_QUEUE_MAX_SIZE ]]; then
            return 1
        fi
    fi
    
    return 0
}

# Function to get next message from queue
get_next_message() {
    local priority_filter="${1:-}"  # Optional: high, normal, low
    
    # Find messages sorted by priority and timestamp
    local next_msg
    case "$priority_filter" in
        "high")
            next_msg=$(find "$TELEGRAM_QUEUE_DIR" -name "*.msg" -type f -exec grep -l "^status: pending$" {} \; -exec grep -l "^priority: high$" {} \; | head -1)
            ;;
        "normal")
            next_msg=$(find "$TELEGRAM_QUEUE_DIR" -name "*.msg" -type f -exec grep -l "^status: pending$" {} \; -exec grep -l "^priority: normal$" {} \; | head -1)
            ;;
        "low")
            next_msg=$(find "$TELEGRAM_QUEUE_DIR" -name "*.msg" -type f -exec grep -l "^status: pending$" {} \; -exec grep -l "^priority: low$" {} \; | head -1)
            ;;
        *)
            # All priorities, sorted by priority order then timestamp
            next_msg=$(find "$TELEGRAM_QUEUE_DIR" -name "*.msg" -type f -exec grep -l "^status: pending$" {} \; | sort | head -1)
            ;;
    esac
    
    echo "$next_msg"
}

# Function to mark message as processed
mark_message_processed() {
    local queue_file="$1"
    local status="${2:-sent}"
    
    if [[ -f "$queue_file" ]]; then
        # Update status
        sed -i "s/^status: pending$/status: $status/" "$queue_file"
        
        # Move to processed directory
        local processed_dir="${TELEGRAM_QUEUE_DIR}/processed"
        mkdir -p "$processed_dir"
        
        local filename
        filename=$(basename "$queue_file")
        mv "$queue_file" "${processed_dir}/${filename}"
        
        log "DEBUG" "Message marked as $status: $filename"
        return 0
    fi
    
    return 1
}

# Function to mark message for retry
mark_message_for_retry() {
    local queue_file="$1"
    local retry_delay="${2:-60}"
    
    if [[ -f "$queue_file" ]]; then
        # Update retry count and status
        local retry_count
        retry_count=$(grep "^retry_count:" "$queue_file" | cut -d' ' -f2)
        ((retry_count++))
        
        sed -i "s/^retry_count:.*/retry_count: $retry_count/" "$queue_file"
        sed -i "s/^status: pending$/status: retry/" "$queue_file"
        
        # Schedule for retry
        local retry_time
        retry_time=$(($(date +%s) + retry_delay))
        echo "retry_after: $retry_time" >> "$queue_file"
        
        log "DEBUG" "Message scheduled for retry in ${retry_delay}s: $(basename "$queue_file")"
        return 0
    fi
    
    return 1
}

# Function to check if message is ready for retry
is_message_ready_for_retry() {
    local queue_file="$1"
    
    if [[ -f "$queue_file" ]]; then
        local status
        status=$(grep "^status:" "$queue_file" | cut -d' ' -f2)
        
        if [[ "$status" == "retry" ]]; then
            local retry_after
            retry_after=$(grep "^retry_after:" "$queue_file" | cut -d' ' -f2)
            
            if [[ -n "$retry_after" ]]; then
                local current_time
                current_time=$(date +%s)
                if [[ $current_time -ge $retry_after ]]; then
                    # Reset to pending
                    sed -i "s/^status: retry$/status: pending/" "$queue_file"
                    return 0
                fi
            fi
        fi
    fi
    
    return 1
}

# Function to check rate limiting
check_rate_limit_queue() {
    local messages_per_second="${TELEGRAM_RATE_LIMITING_MESSAGES_PER_SECOND:-5}"
    local burst_size="${TELEGRAM_RATE_LIMITING_BURST_SIZE:-20}"
    local current_time
    current_time=$(date +%s)
    
    # Reset window if needed
    if [[ $((current_time - TELEGRAM_WINDOW_START)) -ge 60 ]]; then
        TELEGRAM_MESSAGES_SENT=0
        TELEGRAM_WINDOW_START=$current_time
    fi
    
    # Check burst limit
    if [[ $TELEGRAM_MESSAGES_SENT -ge $burst_size ]]; then
        log "DEBUG" "Burst limit reached: $TELEGRAM_MESSAGES_SENT/$burst_size"
        return 1
    fi
    
    # Calculate time since last message
    local time_since_reset
    time_since_reset=$((current_time - TELEGRAM_LAST_RESET))
    local min_interval
    min_interval=$(echo "scale=2; 1 / $messages_per_second" | bc 2>/dev/null || echo "0.2")
    
    if [[ $time_since_reset -lt $(echo "$min_interval" | cut -d'.' -f1) ]]; then
        local sleep_time
        sleep_time=$(echo "$min_interval - $time_since_reset" | bc 2>/dev/null || echo "0.1")
        log "DEBUG" "Rate limiting: sleeping for ${sleep_time}s"
        sleep "$sleep_time"
    fi
    
    return 0
}

# Function to update rate limiting state
update_rate_limit_state() {
    TELEGRAM_MESSAGES_SENT=$((TELEGRAM_MESSAGES_SENT + 1))
    TELEGRAM_LAST_RESET=$(date +%s)
}

# Function to process a single message
process_queue_message() {
    local queue_file="$1"
    
    if [[ ! -f "$queue_file" ]]; then
        return 1
    fi
    
    # Check if message is ready for retry
    if ! is_message_ready_for_retry "$queue_file"; then
        return 0  # Skip, not ready yet
    fi
    
    # Extract message details
    local chat_id
    chat_id=$(grep "^chat_id:" "$queue_file" | cut -d' ' -f2)
    local parse_mode
    parse_mode=$(grep "^parse_mode:" "$queue_file" | cut -d' ' -f2)
    local priority
    priority=$(grep "^priority:" "$queue_file" | cut -d' ' -f2)
    local retry_count
    retry_count=$(grep "^retry_count:" "$queue_file" | cut -d' ' -f2)
    local message
    message=$(sed -n '/^message:$/,$p' "$queue_file" | tail -n +2)
    
    # Check rate limiting
    if ! check_rate_limit_queue; then
        return 0  # Rate limited, try again later
    fi
    
    # Send message
    local max_retries="${TELEGRAM_RETRY_MAX_ATTEMPTS:-3}"
    if send_telegram_message "$message" "$chat_id" "$parse_mode" "$max_retries"; then
        mark_message_processed "$queue_file" "sent"
        update_rate_limit_state
        return 0
    else
        if [[ $retry_count -lt $max_retries ]]; then
            # Calculate retry delay with exponential backoff
            local retry_delay
            retry_delay=$(echo "2 ^ $retry_count" | bc 2>/dev/null || echo "5")
            if [[ $retry_delay -gt 30 ]]; then
                retry_delay=30
            fi
            
            mark_message_for_retry "$queue_file" "$retry_delay"
            return 2  # Scheduled for retry
        else
            mark_message_processed "$queue_file" "failed"
            log "ERROR" "Message failed after $max_retries attempts: $(basename "$queue_file")"
            return 1
        fi
    fi
}

# Function to process queue (main processor)
process_telegram_queue() {
    log "DEBUG" "Starting queue processor"
    
    # Initialize queue system
    init_telegram_queue
    
    # Acquire lock for processing
    if ! acquire_queue_lock 10; then
        log "WARNING" "Failed to acquire lock for queue processing"
        return 1
    fi
    
    local processed=0
    local failed=0
    local retried=0
    
    # Process messages in priority order
    local priorities=("high" "normal" "low")
    for priority in "${priorities[@]}"; do
        while true; do
            local next_msg
            next_msg=$(get_next_message "$priority")
            
            if [[ -z "$next_msg" ]]; then
                break  # No more messages with this priority
            fi
            
            process_queue_message "$next_msg"
            local result=$?
            
            case $result in
                0) ((processed++)) ;;
                1) ((failed++)) ;;
                2) ((retried++)) ;;
            esac
            
            # Small delay between messages to avoid overwhelming the API
            sleep 0.5
        done
    done
    
    release_queue_lock
    
    log "DEBUG" "Queue processing completed: $processed sent, $failed failed, $retried retried"
    
    return 0
}

# Function to trigger background queue processor
trigger_queue_processor() {
    # Check if processor is already running
    if pgrep -f "process_telegram_queue" >/dev/null 2>&1; then
        return 0  # Already running
    fi
    
    # Start background processor
    {
        process_telegram_queue >/dev/null 2>&1
    } &
    
    log "DEBUG" "Background queue processor triggered"
}

# Function to get queue statistics
get_queue_statistics() {
    local pending
    pending=$(find "$TELEGRAM_QUEUE_DIR" -name "*.msg" -exec grep -l "^status: pending$" {} \; | wc -l)
    local retry
    retry=$(find "$TELEGRAM_QUEUE_DIR" -name "*.msg" -exec grep -l "^status: retry$" {} \; | wc -l)
    local sent
    sent=$(find "${TELEGRAM_QUEUE_DIR}/processed" -name "*.msg" -exec grep -l "^status: sent$" {} \; 2>/dev/null | wc -l)
    local failed
    failed=$(find "${TELEGRAM_QUEUE_DIR}/processed" -name "*.msg" -exec grep -l "^status: failed$" {} \; 2>/dev/null | wc -l)
    
    cat << EOF
Telegram Queue Statistics:
  Pending: $pending
  Retry: $retry
  Sent: $sent
  Failed: $failed
  Rate Limit: $TELEGRAM_MESSAGES_SENT/60s window
EOF
}

# Function to clean up old queue files
cleanup_old_queue_files() {
    local retention_seconds
    retention_seconds=$((TELEGRAM_QUEUE_RETENTION_HOURS * 3600))
    local cutoff_time
    cutoff_time=$(($(date +%s) - retention_seconds))
    
    # Clean up old processed files
    find "${TELEGRAM_QUEUE_DIR}/processed" -name "*.msg" -type f -mtime +${TELEGRAM_QUEUE_RETENTION_HOURS} -delete 2>/dev/null
    
    # Clean up old failed files
    find "$TELEGRAM_QUEUE_DIR" -name "*.msg" -exec grep -l "^status: failed$" {} \; -mtime +${TELEGRAM_QUEUE_RETENTION_HOURS} -delete 2>/dev/null
    
    # Clean up very old pending files (probably stuck)
    find "$TELEGRAM_QUEUE_DIR" -name "*.msg" -type f -mtime +${TELEGRAM_QUEUE_RETENTION_HOURS} -exec grep -l "^status: pending$" {} \; -mtime +${TELEGRAM_QUEUE_RETENTION_HOURS} -delete 2>/dev/null
    
    log "DEBUG" "Queue cleanup completed"
}

# Function to cleanup queue on exit
cleanup_queue_on_exit() {
    release_queue_lock 2>/dev/null
    cleanup_old_queue_files
}

# Cleanup on exit
trap cleanup_queue_on_exit EXIT

log "DEBUG" "Telegram queue module loaded"