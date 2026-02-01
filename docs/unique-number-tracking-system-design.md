# Unique Number Tracking System Design

## Overview

This document presents a comprehensive design for a robust unique number tracking system that ensures number uniqueness across concurrent operations while maintaining backward compatibility with the existing task file numbering system in `planner.sh`.

## Problem Statement

The current numbering system in `planner.sh` works correctly for single-threaded operations but has potential race conditions in concurrent environments:

1. **Race Condition Risk**: Multiple processes could read the same `max_num` simultaneously
2. **File Operation Failure**: If `mv` fails after number assignment, numbers could be skipped
3. **No Atomicity**: Number reading and assignment are separate operations
4. **Limited Scalability**: Current approach doesn't handle distributed scenarios

## Design Requirements

### Functional Requirements
1. **Uniqueness Guarantee**: Ensure no duplicate numbers are assigned
2. **Atomic Operations**: Number assignment must be atomic
3. **Concurrent Safety**: Support multiple processes operating simultaneously
4. **Backward Compatibility**: Work with existing `planner.sh` infrastructure
5. **Persistence**: Survive system restarts and crashes
6. **Performance**: Minimal overhead for numbering operations

### Non-Functional Requirements
1. **Reliability**: No single point of failure
2. **Maintainability**: Simple to understand and modify
3. **Debugging**: Clear logging and error reporting
4. **Recovery**: Graceful handling of failures and cleanup

## Proposed Solutions Analysis

### Option 1: State File with File Locking

**Description**: Maintain a state file with used numbers and use file locking for atomic operations.

**Advantages**:
- Simple to implement
- Atomic operations with file locks
- Persistent state
- Easy to debug and inspect

**Disadvantages**:
- Single point of contention
- File locking can be complex across systems
- Performance bottleneck under high concurrency

**Implementation**:
```bash
# State file format: JSON with used numbers and metadata
{
  "used_numbers": [1, 2, 3, 5, 8],
  "last_assigned": 8,
  "created_at": "2026-01-31T19:00:00Z",
  "updated_at": "2026-01-31T19:15:00Z"
}
```

### Option 2: Timestamp-Based Numbering

**Description**: Use timestamps (or timestamp-derived numbers) as unique identifiers.

**Advantages**:
- Naturally unique across time
- No state management required
- Works in distributed environments
- No coordination needed

**Disadvantages**:
- Not sequential (may be confusing for users)
- Large numbers (less human-readable)
- Clock synchronization issues possible
- Doesn't provide sequential ordering

**Implementation**:
```bash
# Format: YYYYMMDDHHMMSS or Unix timestamp
number=$(date +%Y%m%d%H%M%S)  # 20260131191500
# or
number=$(date +%s)           # 1706733300
```

### Option 3: Hash-Based Unique Identifiers

**Description**: Generate unique identifiers using cryptographic hashes of context + timestamp.

**Advantages**:
- Extremely low collision probability
- Distributed-friendly
- No state management
- Can embed context information

**Disadvantages**:
- Not human-readable or sequential
- Overkill for simple numbering needs
- Difficult to debug
- Changes the user experience significantly

**Implementation**:
```bash
number=$(echo "${task_dir}:${timestamp}" | sha256sum | cut -c1-8)
```

### Option 4: Atomic Directory Operations

**Description**: Use atomic directory creation operations to generate unique numbers.

**Advantages**:
- Truly atomic (OS-level)
- No external state files
- Works across systems
- Simple implementation

**Disadvantages**:
- Requires cleanup of temporary directories
- May not work on all filesystems
- Less intuitive than traditional numbering

**Implementation**:
```bash
# Create temporary directories atomically
temp_dir="${task_dir}/. numbering_$$"
mkdir "${temp_dir}" 2>/dev/null || handle_failure
```

## Recommended Solution: Hybrid Approach

**Selection**: **Option 1 (State File with File Locking)** with enhancements for robustness.

### Why This Approach?

1. **Best Balance**: Meets all requirements with reasonable complexity
2. **User Experience**: Maintains sequential, human-readable numbers
3. **Backward Compatibility**: Integrates smoothly with existing `planner.sh`
4. **Reliability**: Proven approach with well-understood failure modes
5. **Debugging**: State is inspectable and human-readable

## Detailed Design

### Core Components

#### 1. Number State Manager (`number_manager.sh`)

```bash
#!/bin/bash
# Number State Manager for Unique Number Tracking

SCRIPT_NAME="number_manager"
NUMBER_STATE_DIR="${MANAGED_REPO_PATH}/.number_state"
LOCK_TIMEOUT=30
MAX_RETRIES=5

# Initialize state directory
init_number_state() {
    mkdir -p "$NUMBER_STATE_DIR"
    
    # Create state file if doesn't exist
    if [ ! -f "$NUMBER_STATE_DIR/state.json" ]; then
        cat > "$NUMBER_STATE_DIR/state.json" << EOF
{
    "used_numbers": [],
    "last_assigned": 0,
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    fi
}

# Acquire exclusive lock on state
acquire_lock() {
    local lock_file="$NUMBER_STATE_DIR/.lock"
    local timeout=$LOCK_TIMEOUT
    local count=0
    
    while [ $count -lt $timeout ]; do
        if (set -C; echo $$ > "$lock_file") 2>/dev/null; then
            return 0
        fi
        
        # Check if lock is stale (process no longer exists)
        if [ -f "$lock_file" ]; then
            local lock_pid=$(cat "$lock_file")
            if ! kill -0 "$lock_pid" 2>/dev/null; then
                rm -f "$lock_file"
                continue
            fi
        fi
        
        sleep 1
        count=$((count + 1))
    done
    
    log "ERROR" "Failed to acquire lock after $timeout seconds"
    return 1
}

# Release exclusive lock
release_lock() {
    local lock_file="$NUMBER_STATE_DIR/.lock"
    rm -f "$lock_file"
}

# Get next unique number
get_next_number() {
    local task_context="$1"  # Optional context for tracking
    local state_file="$NUMBER_STATE_DIR/state.json"
    
    if ! acquire_lock; then
        return 1
    fi
    
    trap release_lock EXIT
    
    # Read current state
    local used_numbers last_assigned
    used_numbers=$(jq -r '.used_numbers[]' "$state_file" 2>/dev/null || echo "")
    last_assigned=$(jq -r '.last_assigned' "$state_file" 2>/dev/null || echo "0")
    
    # Find next available number
    local next_num=$((last_assigned + 1))
    while echo "$used_numbers" | grep -q "^${next_num}$"; do
        next_num=$((next_num + 1))
    done
    
    # Update state atomically
    local temp_file="${state_file}.tmp"
    jq \
        --argjson num "$next_num" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --arg context "$task_context" \
        '.used_numbers += [$num] | .last_assigned = $num | .updated_at = $timestamp | if .context_assignments == null then .context_assignments = {} end | .context_assignments[$context] = $num' \
        "$state_file" > "$temp_file"
    
    mv "$temp_file" "$state_file"
    
    echo "$next_num"
    return 0
}

# Release a number (for cleanup or rollback)
release_number() {
    local number="$1"
    local state_file="$NUMBER_STATE_DIR/state.json"
    
    if ! acquire_lock; then
        return 1
    fi
    
    trap release_lock EXIT
    
    # Remove number from used list
    local temp_file="${state_file}.tmp"
    jq \
        --argjson num "$number" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '.used_numbers -= [$num] | .updated_at = $timestamp' \
        "$state_file" > "$temp_file"
    
    mv "$temp_file" "$state_file"
    return 0
}

# Get current state statistics
get_state_stats() {
    local state_file="$NUMBER_STATE_DIR/state.json"
    
    if [ ! -f "$state_file" ]; then
        echo '{"status": "not_initialized"}'
        return
    fi
    
    jq \
        '{
            used_count: (.used_numbers | length),
            last_assigned: .last_assigned,
            created_at: .created_at,
            updated_at: .updated_at,
            context_assignments: (.context_assignments // {})
        }' \
        "$state_file"
}
```

#### 2. Enhanced Planner Integration

Modify `planner.sh` to use the number manager:

```bash
# In planner.sh, replace the numbering logic with:

# Source the number manager
source "$SCRIPT_DIR/number_manager.sh"

# Initialize number state
init_number_state

# For each unnumbered file:
for unnumbered_file in "${unnumbered_files[@]}"; do
    # Get next unique number for this task directory
    task_context="$repo_name/$(basename "$task_dir")"
    next_num=$(get_next_number "$task_context")
    
    if [ $? -ne 0 ]; then
        log "ERROR" "Failed to get unique number for $task_context"
        continue
    fi
    
    filename=$(basename "$unnumbered_file" .txt)
    new_filename=$(printf "%04d-%s.txt" "$next_num" "$filename")
    
    log "INFO" "Assigning unique number $next_num: $(basename "$unnumbered_file") to $new_filename"
    
    if mv "$unnumbered_file" "$task_dir/$new_filename"; then
        log "SUCCESS" "Successfully renamed to $new_filename"
    else
        log "ERROR" "Failed to rename $unnumbered_file to $new_filename"
        # Release the number back to pool
        release_number "$next_num"
    fi
done
```

#### 3. State Cleanup and Maintenance

```bash
# cleanup_number_state.sh - Periodic maintenance

cleanup_number_state() {
    local state_file="$NUMBER_STATE_DIR/state.json"
    local task_dir="$1"
    
    if ! acquire_lock; then
        return 1
    fi
    
    trap release_lock EXIT
    
    # Find actual files in task directory
    local actual_files actual_numbers
    actual_files=($(find "$task_dir" -maxdepth 1 -type f -name "[0-9][0-9][0-9][0-9]-*.txt" ! -name "*.used"))
    
    # Extract numbers from actual files
    actual_numbers=()
    for file in "${actual_files[@]}"; do
        basename_num=$(basename "$file" | sed 's/^\([0-9][0-9][0-9][0-9]\)-.*/\1/')
        if [[ "$basename_num" =~ ^[0-9][0-9][0-9][0-9]$ ]]; then
            actual_numbers+=("$((10#$basename_num))")
        fi
    done
    
    # Update state to match reality
    local temp_file="${state_file}.tmp"
    jq \
        --argjson actual "$(printf '%s\n' "${actual_numbers[@]}" | jq -R . | jq -s .)" \
        --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '.used_numbers = $actual | .updated_at = $timestamp' \
        "$state_file" > "$temp_file"
    
    mv "$temp_file" "$state_file"
}
```

### File Structure

```
managed_repo_path/
├── .number_state/
│   ├── state.json          # Main state file
│   ├── .lock              # Process lock file
│   └── backup/            # State backups
│       ├── state_20260131_190000.json
│       └── state_20260131_180000.json
├── scripts/
│   ├── number_manager.sh   # Core number management
│   ├── planner.sh         # Enhanced with number manager
│   └── cleanup_number_state.sh  # Maintenance script
└── managed_repo_task_path/
    └── repo_name/
        ├── 0001-task.txt
        ├── 0002-task.txt
        └── 0003-task.txt.used
```

### Error Handling and Recovery

#### Lock Timeout Handling
```bash
# Enhanced lock acquisition with exponential backoff
acquire_lock_with_backoff() {
    local max_attempts=$MAX_RETRIES
    local base_delay=1
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if acquire_lock; then
            return 0
        fi
        
        # Exponential backoff
        delay=$((base_delay * 2 ** attempt))
        sleep "$delay"
        attempt=$((attempt + 1))
    done
    
    return 1
}
```

#### State Corruption Recovery
```bash
# Detect and repair corrupted state
validate_and_repair_state() {
    local state_file="$NUMBER_STATE_DIR/state.json"
    
    # Check if state file is valid JSON
    if ! jq empty "$state_file" 2>/dev/null; then
        log "WARNING" "State file corrupted, attempting recovery from backup"
        
        # Try latest backup
        local latest_backup=$(ls -t "$NUMBER_STATE_DIR/backup/"*.json 2>/dev/null | head -1)
        if [ -f "$latest_backup" ]; then
            cp "$latest_backup" "$state_file"
            log "INFO" "Recovered state from backup: $(basename "$latest_backup")"
        else
            # Fallback to reinitialization
            init_number_state
            log "INFO" "Reinitialized state file due to corruption"
        fi
    fi
}
```

### Performance Considerations

1. **Lock Contention**: Use exponential backoff to reduce contention
2. **State Size**: Keep state file small and efficient with jq operations
3. **Backup Strategy**: Rotate backups to prevent disk usage growth
4. **Caching**: Consider in-memory caching for frequently accessed state

### Monitoring and Debugging

#### State Inspection Commands
```bash
# View current state
get_state_stats | jq '.'

# Show number usage by context
jq '.context_assignments' "$NUMBER_STATE_DIR/state.json"

# Check for gaps in numbering
check_number_gaps() {
    local task_dir="$1"
    local max_num=$(jq '.last_assigned' "$NUMBER_STATE_DIR/state.json")
    
    for ((i=1; i<=max_num; i++)); do
        if ! find "$task_dir" -name "$(printf "%04d-*" "$i")" -type f | grep -q .; then
            echo "Gap found: number $i not used in any file"
        fi
    done
}
```

#### Logging Integration
```bash
# Enhanced logging for number operations
log_number_assignment() {
    local number="$1"
    local old_name="$2"
    local new_name="$3"
    local context="$4"
    
    log "INFO" "Number assigned: $number | Context: $context | $old_name → $new_name"
}
```

## Implementation Plan

### Phase 1: Core Infrastructure
1. Create `number_manager.sh` with basic functionality
2. Implement file locking and state management
3. Add comprehensive error handling
4. Create unit tests

### Phase 2: Integration
1. Modify `planner.sh` to use number manager
2. Ensure backward compatibility
3. Add migration path for existing numbered files
4. Test integration thoroughly

### Phase 3: Enhancement
1. Add maintenance and cleanup scripts
2. Implement monitoring and debugging tools
3. Add performance optimizations
4. Create comprehensive documentation

### Phase 4: Production Deployment
1. Gradual rollout with monitoring
2. Performance validation
3. User training and documentation
4. Establish maintenance procedures

## Migration Strategy

### Step 1: Backward Compatibility
- Existing numbered files remain unchanged
- New files use the enhanced system
- Gradual migration of existing files on next access

### Step 2: State Initialization
- Scan existing directories to build initial state
- Map existing numbers to state file
- Validate consistency with actual files

### Step 3: Rollback Plan
- Keep original `planner.sh` as backup
- Ability to disable new system via configuration
- Clear rollback procedures documented

## Testing Strategy

### Unit Tests
- Lock acquisition and release
- State file operations (read, write, update)
- Number assignment and release
- Error conditions and recovery

### Integration Tests
- `planner.sh` integration
- Concurrent execution scenarios
- File system failure simulation
- State corruption recovery

### Performance Tests
- High concurrency scenarios
- Large directory handling
- Lock contention behavior
- Memory and disk usage

## Security Considerations

1. **File Permissions**: Ensure proper access controls on state directory
2. **Lock Security**: Validate lock file ownership and process IDs
3. **Path Security**: Validate all file paths to prevent traversal
4. **Input Validation**: Sanitize all inputs to state operations

## Conclusion

The proposed hybrid approach using a state file with file locking provides the best balance of:

- **Reliability**: Proven approach with clear failure modes
- **Performance**: Efficient for the expected workload
- **Maintainability**: Simple to understand and modify
- **User Experience**: Maintains sequential, human-readable numbers
- **Backward Compatibility**: Integrates smoothly with existing systems

This design addresses the core requirements while providing a robust foundation for future enhancements and scaling.

---

**Document Status**: Ready for Implementation  
**Next Steps**: Begin Phase 1 development of `number_manager.sh`  
**Dependencies**: None (standalone system)  
**Backward Compatibility**: Full support for existing `planner.sh` workflow