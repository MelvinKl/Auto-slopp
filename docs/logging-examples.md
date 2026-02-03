# Logging Examples and Usage Patterns

## Overview

This document provides practical examples of how to use the enhanced logging system effectively in different scenarios. Each example demonstrates best practices and common usage patterns.

## 🚀 Quick Start Examples

### Basic Script with Logging

```bash
#!/bin/bash

# Example: Basic script with enhanced logging
SCRIPT_NAME="example_basic"

# Load utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

# Set up error handling
setup_error_handling

main() {
    log "INFO" "Starting example script"
    
    # Example operations
    log "INFO" "Processing items"
    for i in {1..3}; do
        log "DEBUG" "Processing item $i"
        log "SUCCESS" "Item $i processed successfully"
    done
    
    log "SUCCESS" "Example script completed"
}

main "$@"
```

### Configuration-Driven Logging

```bash
#!/bin/bash

# Example: Logging with configuration
SCRIPT_NAME="example_config"

# Load utilities and configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

setup_error_handling

# Configure logging based on environment
configure_logging "${TIMESTAMP_FORMAT:-readable-precise}" "${TIMESTAMP_TIMEZONE:-local}"

main() {
    log "INFO" "Starting configuration-driven script"
    log "DEBUG" "Configuration loaded: format=$TIMESTAMP_FORMAT, timezone=$TIMESTAMP_TIMEZONE"
    
    # Your logic here
    log "SUCCESS" "Configuration-driven script completed"
}

main "$@"
```

## 📊 Real-World Usage Patterns

### Repository Management Script

```bash
#!/bin/bash

# Example: Repository management with comprehensive logging
SCRIPT_NAME="repo_manager"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/../config.sh"

setup_error_handling

# Function with detailed logging
update_repository() {
    local repo_path="$1"
    local repo_name=$(basename "$repo_path")
    local start_time=$(date +%s)
    
    log "INFO" "Starting repository update: $repo_name"
    log "DEBUG" "Repository path: $repo_path"
    
    # Check if repository exists
    if [[ ! -d "$repo_path" ]]; then
        log "ERROR" "Repository not found: $repo_path"
        return 1
    fi
    
    # Get current state
    local current_branch=$(git -C "$repo_path" branch --show-current)
    local current_commit=$(git -C "$repo_path" rev-parse HEAD)
    log "DEBUG" "Current state: branch=$current_branch, commit=$current_commit"
    
    # Fetch changes
    log "INFO" "Fetching changes from origin"
    if ! git -C "$repo_path" fetch origin; then
        log "ERROR" "Failed to fetch changes for $repo_name"
        return 1
    fi
    log "SUCCESS" "Successfully fetched changes for $repo_name"
    
    # Check for updates
    local upstream_commit=$(git -C "$repo_path" rev-parse origin/$current_branch)
    if [[ "$current_commit" == "$upstream_commit" ]]; then
        log "INFO" "Repository $repo_name is up to date"
        return 0
    fi
    
    # Pull updates
    log "INFO" "Pulling updates for $repo_name"
    if ! git -C "$repo_path" pull origin $current_branch; then
        log "ERROR" "Failed to pull updates for $repo_name"
        return 1
    fi
    
    # Calculate elapsed time
    local elapsed_time=$(($(date +%s) - start_time))
    log "SUCCESS" "Repository $repo_name updated successfully in ${elapsed_time}s"
    
    return 0
}

main() {
    log "INFO" "Starting repository manager"
    
    # Process each repository
    for repo_path in "$MANAGED_REPO_PATH"/*; do
        if [[ -d "$repo_path" && -d "$repo_path/.git" ]]; then
            update_repository "$repo_path"
        else
            log "WARNING" "Skipping non-git directory: $repo_path"
        fi
    done
    
    log "SUCCESS" "Repository manager completed"
}

main "$@"
```

### Task Processing Script

```bash
#!/bin/bash

# Example: Task processing with progress tracking
SCRIPT_NAME="task_processor"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

setup_error_handling

# Progress tracking functions
log_batch_start() {
    BATCH_START_TIME=$(date +%s)
    BATCH_COUNT=0
    log "INFO" "Starting batch processing"
}

log_batch_progress() {
    ((BATCH_COUNT++))
    if ((BATCH_COUNT % 10 == 0)); then
        local elapsed=$(($(date +%s) - BATCH_START_TIME))
        local rate=$(echo "scale=1; $BATCH_COUNT / $elapsed" | bc 2>/dev/null || echo "0")
        log "INFO" "Progress: $BATCH_COUNT items processed (${rate} items/sec)"
    fi
}

log_batch_end() {
    local elapsed=$(($(date +%s) - BATCH_START_TIME))
    local rate=$(echo "scale=1; $BATCH_COUNT / $elapsed" | bc 2>/dev/null || echo "0")
    log "SUCCESS" "Batch completed: $BATCH_COUNT items in ${elapsed}s (${rate} items/sec)"
}

# Task processing function
process_task() {
    local task_file="$1"
    local task_name=$(basename "$task_file")
    local start_time=$(date +%s)
    
    log "DEBUG" "Processing task: $task_name"
    
    # Simulate task processing
    sleep 1
    
    local elapsed=$(($(date +%s) - start_time))
    log "SUCCESS" "Task completed: $task_name (${elapsed}s)"
    
    log_batch_progress
}

main() {
    log "INFO" "Starting task processor"
    
    # Initialize batch tracking
    log_batch_start
    
    # Process all task files
    for task_file in tasks/*.txt; do
        if [[ -f "$task_file" ]]; then
            process_task "$task_file"
        else
            log "WARNING" "Task file not found: $task_file"
        fi
    done
    
    # Finalize batch
    log_batch_end
    log "SUCCESS" "Task processor completed"
}

main "$@"
```

### Error Handling and Recovery

```bash
#!/bin/bash

# Example: Robust error handling with logging
SCRIPT_NAME="robust_processor"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

setup_error_handling

# Retry mechanism with logging
retry_operation() {
    local max_attempts="$1"
    local delay="$2"
    shift 2
    local operation=("$@")
    
    local attempt=1
    while ((attempt <= max_attempts)); do
        log "INFO" "Attempting operation (attempt $attempt/$max_attempts)"
        
        if "${operation[@]}"; then
            log "SUCCESS" "Operation succeeded on attempt $attempt"
            return 0
        fi
        
        if ((attempt < max_attempts)); then
            log "WARNING" "Operation failed on attempt $attempt, retrying in ${delay}s"
            sleep "$delay"
        fi
        
        ((attempt++))
    done
    
    log "ERROR" "Operation failed after $max_attempts attempts"
    return 1
}

# Example operation that might fail
unreliable_operation() {
    local success_rate=70  # 70% success rate
    
    if (( RANDOM % 100 < success_rate )); then
        log "DEBUG" "Operation succeeded internally"
        return 0
    else
        log "DEBUG" "Operation failed internally"
        return 1
    fi
}

main() {
    log "INFO" "Starting robust processor"
    
    # Use retry mechanism
    if retry_operation 3 2 unreliable_operation; then
        log "SUCCESS" "Robust processor completed successfully"
    else
        log "ERROR" "Robust processor failed after retries"
        exit 1
    fi
}

main "$@"
```

## 🔍 Debugging Examples

### Debug Mode Usage

```bash
#!/bin/bash

# Example: Debug mode implementation
SCRIPT_NAME="debug_example"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

setup_error_handling

# Function with conditional debug logging
debug_function() {
    local data="$1"
    
    log "INFO" "Processing data"
    
    # Detailed debug information (only shown in debug mode)
    log "DEBUG" "Input data: $data"
    log "DEBUG" "Data length: ${#data} characters"
    log "DEBUG" "Data type: $(typeof "$data" 2>/dev/null || echo "unknown")"
    
    # Processing logic
    local processed_data=$(echo "$data" | tr '[:lower:]' '[:upper:]')
    
    log "DEBUG" "Processed data: $processed_data"
    log "SUCCESS" "Data processing completed"
}

# Type detection helper (optional)
typeof() {
    local var="$1"
    if [[ "$var" =~ ^[0-9]+$ ]]; then
        echo "integer"
    elif [[ "$var" =~ ^[0-9]+\.[0-9]+$ ]]; then
        echo "float"
    elif [[ -n "$var" ]]; then
        echo "string"
    else
        echo "empty"
    fi
}

main() {
    log "INFO" "Starting debug example"
    
    # Always enable debug mode for this example
    DEBUG_MODE=true
    
    # Test with different data types
    debug_function "hello world"
    debug_function "12345"
    debug_function "12.34"
    debug_function ""
    
    log "SUCCESS" "Debug example completed"
}

main "$@"
```

### Performance Monitoring

```bash
#!/bin/bash

# Example: Performance monitoring with logging
SCRIPT_NAME="perf_monitor"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

setup_error_handling

# Performance measurement function
measure_performance() {
    local operation_name="$1"
    shift
    local operation=("$@")
    
    log "INFO" "Starting performance measurement: $operation_name"
    
    # Start timing
    local start_time=$(date +%s.%N 2>/dev/null || date +%s)
    local start_cpu=$(ps -o %cpu= -p $$ 2>/dev/null || echo "0")
    
    # Execute operation
    local exit_code=0
    "${operation[@]}" || exit_code=$?
    
    # End timing
    local end_time=$(date +%s.%N 2>/dev/null || date +%s)
    local end_cpu=$(ps -o %cpu= -p $$ 2>/dev/null || echo "0")
    
    # Calculate metrics
    local elapsed=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")
    local cpu_usage=$(echo "$end_cpu - $start_cpu" | bc 2>/dev/null || echo "0")
    
    # Log results
    if [[ $exit_code -eq 0 ]]; then
        log "SUCCESS" "Operation '$operation_name' completed in ${elapsed}s (CPU: ${cpu_usage}%)"
    else
        log "ERROR" "Operation '$operation_name' failed in ${elapsed}s (exit code: $exit_code)"
    fi
    
    return $exit_code
}

# Example operations to measure
fast_operation() {
    # Simulate quick operation
    return 0
}

slow_operation() {
    # Simulate slow operation
    sleep 2
    return 0
}

failing_operation() {
    # Simulate failing operation
    return 1
}

main() {
    log "INFO" "Starting performance monitor"
    
    # Measure different operations
    measure_performance "fast_operation" fast_operation
    measure_performance "slow_operation" slow_operation
    measure_performance "failing_operation" failing_operation
    
    log "SUCCESS" "Performance monitor completed"
}

main "$@"
```

## 🔧 Advanced Logging Patterns

### Structured Logging for Complex Events

```bash
#!/bin/bash

# Example: Structured logging for complex operations
SCRIPT_NAME="structured_logger"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

setup_error_handling

# Structured logging function
log_structured() {
    local level="$1"
    local event_type="$2"
    shift 2
    local details=("$@")
    
    # Create structured message
    local message="Event: $event_type"
    for detail in "${details[@]}"; do
        message+=" | $detail"
    done
    
    log "$level" "$message"
}

# Database operation example
perform_database_operation() {
    local operation="$1"
    local table="$2"
    local record_id="$3"
    
    log_structured "INFO" "database_operation_start" \
        "operation=$operation" \
        "table=$table" \
        "record_id=$record_id" \
        "timestamp=$(date -Iseconds)"
    
    # Simulate database operation
    sleep 1
    
    log_structured "SUCCESS" "database_operation_complete" \
        "operation=$operation" \
        "table=$table" \
        "record_id=$record_id" \
        "duration=1.0s"
}

# API call example
make_api_call() {
    local endpoint="$1"
    local method="$2"
    local response_code="$3"
    
    log_structured "INFO" "api_call_start" \
        "endpoint=$endpoint" \
        "method=$method" \
        "user_id=12345"
    
    # Simulate API call
    sleep 0.5
    
    if [[ "$response_code" =~ ^2[0-9][0-9]$ ]]; then
        log_structured "SUCCESS" "api_call_success" \
            "endpoint=$endpoint" \
            "method=$method" \
            "response_code=$response_code" \
            "duration=0.5s"
    else
        log_structured "ERROR" "api_call_error" \
            "endpoint=$endpoint" \
            "method=$method" \
            "response_code=$response_code" \
            "duration=0.5s"
    fi
}

main() {
    log "INFO" "Starting structured logger example"
    
    # Example operations
    perform_database_operation "UPDATE" "users" "12345"
    make_api_call "/api/users/12345" "GET" "200"
    make_api_call "/api/users/99999" "GET" "404"
    
    log "SUCCESS" "Structured logger example completed"
}

main "$@"
```

### Multi-Level Progress Reporting

```bash
#!/bin/bash

# Example: Multi-level progress reporting
SCRIPT_NAME="progress_reporter"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

setup_error_handling

# Progress tracking with hierarchy
declare -A PROGRESS_LEVELS=(
    ["main"]="Main Process"
    ["phase"]="Phase"
    ["step"]="Step"
    ["substep"]="Sub-step"
)

progress_start() {
    local level="$1"
    local name="$2"
    local total="$3"
    
    PROGRESS_${level}_START=$(date +%s)
    PROGRESS_${level}_TOTAL="$total"
    PROGRESS_${level}_CURRENT=0
    
    log "INFO" "${PROGRESS_LEVELS[$level]} started: $name${total:+ ($total items)}"
}

progress_update() {
    local level="$1"
    local increment="${2:-1}"
    
    local current_var="PROGRESS_${level}_CURRENT"
    local total_var="PROGRESS_${level}_TOTAL"
    local start_var="PROGRESS_${level}_START"
    
    local current=${!current_var}
    local total=${!total_var}
    local start=${!start_var}
    
    ((current += increment))
    printf -v "$current_var" "%d" "$current"
    
    if [[ -n "$total" && "$total" -gt 0 ]]; then
        local percent=$((current * 100 / total))
        local elapsed=$(($(date +%s) - start))
        local eta=$((elapsed * (total - current) / current))
        
        log "INFO" "${PROGRESS_LEVELS[$level]} progress: $current/$total (${percent}%) - ETA: ${eta}s"
    fi
}

progress_end() {
    local level="$1"
    local name="$2"
    
    local current_var="PROGRESS_${level}_CURRENT"
    local total_var="PROGRESS_${level}_TOTAL"
    local start_var="PROGRESS_${level}_START"
    
    local current=${!current_var}
    local total=${!total_var}
    local start=${!start_var}
    
    local elapsed=$(($(date +%s) - start))
    
    log "SUCCESS" "${PROGRESS_LEVELS[$level]} completed: $name ($current/$total items in ${elapsed}s)"
}

# Example usage
process_project() {
    local project_name="$1"
    
    progress_start "phase" "Processing $project_name" 3
    
    # Phase 1: Setup
    progress_start "step" "Setup" 2
    progress_update "step" 1
    sleep 1
    progress_update "step" 1
    progress_end "step" "Setup"
    progress_update "phase"
    
    # Phase 2: Analysis
    progress_start "step" "Analysis" 5
    for i in {1..5}; do
        progress_update "step" 1
        sleep 0.5
    done
    progress_end "step" "Analysis"
    progress_update "phase"
    
    # Phase 3: Deployment
    progress_start "step" "Deployment" 3
    for i in {1..3}; do
        progress_start "substep" "Deploy component $i" 2
        progress_update "substep" 1
        sleep 0.3
        progress_update "substep" 1
        progress_end "substep" "Deploy component $i"
        progress_update "step" 1
    done
    progress_end "step" "Deployment"
    progress_update "phase"
    
    progress_end "phase" "Processing $project_name"
}

main() {
    log "INFO" "Starting progress reporter example"
    
    progress_start "main" "Project Processing" 2
    
    process_project "Project Alpha"
    progress_update "main"
    
    process_project "Project Beta"
    progress_update "main"
    
    progress_end "main" "Project Processing"
    log "SUCCESS" "Progress reporter example completed"
}

main "$@"
```

## 🌐 Integration Examples

### Integration with External Tools

```bash
#!/bin/bash

# Example: Integration with external monitoring tools
SCRIPT_NAME="external_integration"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

setup_error_handling

# Send structured logs to external monitoring
send_to_monitoring() {
    local level="$1"
    local message="$2"
    local script_name="$3"
    
    # Create JSON payload
    local payload=$(cat << EOF
{
    "timestamp": "$(date -Iseconds)",
    "level": "$level",
    "message": "$message",
    "script": "$script_name",
    "host": "$(hostname)",
    "user": "$USER"
}
EOF
)
    
    # Send to monitoring service (example)
    if command -v curl >/dev/null; then
        curl -s -X POST \
            -H "Content-Type: application/json" \
            -d "$payload" \
            "https://monitoring.example.com/logs" \
            >/dev/null 2>&1 || log "WARNING" "Failed to send to monitoring service"
    fi
}

# Enhanced log function with external integration
log_with_integration() {
    local level="$1"
    shift
    local message="$*"
    
    # Standard logging
    log "$level" "$message"
    
    # External integration for certain levels
    if [[ "$level" =~ ^(ERROR|WARNING)$ ]]; then
        send_to_monitoring "$level" "$message" "$SCRIPT_NAME"
    fi
}

# Example usage
main() {
    log_with_integration "INFO" "Starting external integration example"
    
    # Normal operations
    log_with_integration "INFO" "Processing data"
    log_with_integration "SUCCESS" "Data processed successfully"
    
    # Error conditions (will be sent to monitoring)
    log_with_integration "WARNING" "High memory usage detected"
    log_with_integration "ERROR" "Connection to database failed"
    
    log_with_integration "SUCCESS" "External integration example completed"
}

main "$@"
```

---

**Examples last updated**: 2026-01-31  
**Compatible with**: Auto-slopp v2.0+  
**Maintained by**: Repository Automation System