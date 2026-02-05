# Merge Conflict Detection and Escalation Strategy for OpenCode

## Executive Summary

This document describes the comprehensive merge conflict detection and escalation strategy implemented in the Auto-slopp repository automation system. The system provides automated detection, classification, logging, and escalation of merge conflicts during repository operations, with seamless integration with OpenCode for automated resolution.

## System Architecture

### Core Components

1. **Merge Conflict Detection Layer** - Identifies and classifies merge conflicts
2. **Escalation Engine** - Routes conflicts to appropriate resolution mechanisms  
3. **State Preservation System** - Maintains context for resolution attempts
4. **Comprehensive Logging Framework** - Tracks all merge operations and outcomes
5. **OpenCode Integration** - Automated AI-powered conflict resolution

### Workflow Overview

```
Repository Change Detected
        ↓
    Merge Attempt
        ↓
┌───────────────────┐
│  Success?         │── Yes ──→ ✅ Log success, continue operations
└───────────────────┘
        ↓ No
┌───────────────────┐
│  Classify Error   │── Network ──→ 🔄 Retry with timeout
│  Type             │── Permission ──→ 🚫 Halt with error
│                   │── Corruption ──→ 💾 Preserve state, alert
└───────────────────┘
        ↓ Conflict
┌───────────────────┐
│  Detect Conflicts │── Get conflicted files list
│  Create Report    │── Save conflict details
│  Log Event        │── Comprehensive audit trail
└───────────────────┘
        ↓
┌───────────────────┐
│  Escalate to      │── Generate detailed prompt
│  OpenCode         │── Provide conflict context
│                   │── Include resolution instructions
└───────────────────┘
        ↓
┌───────────────────┐
│  Resolution       │── Success ──→ ✅ Log outcome, continue
│  Attempt          │── Failed ──→ ⚠️ Manual intervention required
└───────────────────┘
```

## Implementation Details

### 1. Error Classification System

**Function**: `classify_merge_error(exit_code, error_output)`

Classifies merge errors into actionable categories:

| Error Type | Pattern Match | Action |
|------------|---------------|---------|
| `NETWORK_FAILURE` | connection, refused, timeout, network | Retry with exponential backoff |
| `PERMISSION_DENIED` | permission, denied, access denied | Halt, alert administrator |
| `REPOSITORY_CORRUPT` | corrupt, broken, invalid | Preserve state, full diagnostic |
| `MERGE_CONFLICT` | conflict, CONFLICT, merge, <<<<<<< | Escalate to OpenCode |
| `FAST_FORWARD_FAILED` | fast-forward | Abort, force push required |
| `BRANCH_NOT_FOUND` | not found, doesnt exist, branch not found | Validate branch names |
| `DETACHED_HEAD` | detached head | Abort, switch to branch |
| `LOCK_FILE_EXISTS` | lock file, index.lock | Wait and retry |
| `DISK_FULL` | no space left, disk full | Cleanup required |
| `TIMEOUT` | Exit code 124 | Retry with longer timeout |

### 2. Conflict Detection Engine

**Function**: `detect_merge_conflicts()`

Detects and catalogs merge conflicts:

1. **Identify Conflicted Files**: `git diff --name-only --diff-filter=U`
2. **Extract Conflict Markers**: Parse <<<<<<< HEAD, =======, >>>>>>> origin/main
3. **Generate Conflict Report**: JSON-formatted conflict details
4. **Calculate Conflict Count**: Number of files with conflicts

**Conflict Report Structure**:
```json
{
  "event_type": "merge_conflict_detected",
  "timestamp": "2026-02-05 10:30:00",
  "repository": "my-repo",
  "conflict_count": 3,
  "conflicted_files": [
    "src/utils/helper.js",
    "tests/test_helper.js", 
    "docs/README.md"
  ],
  "ai_branch_head": "abc123def",
  "main_branch_head": "456789ghi",
  "merge_base": "xyz789abc"
}
```

### 3. Comprehensive Logging Framework

**Functions**:
- `log_merge_attempt(operation, source, target, source_commit, target_commit)`
- `log_merge_conflict_detection(conflicted_files_array)`
- `log_opencode_escalation(conflict_type, report_file, context)`
- `log_merge_resolution_outcome(outcome, error_count, operation_time, context)`

**Logging Features**:
- Structured JSON logging to file
- Console output with colors and timestamps
- Log level filtering (DEBUG, INFO, WARNING, ERROR, SUCCESS)
- Centralized log directory with rotation

### 4. Escalation Engine

**Function**: `merge_origin_main_to_ai_with_escalation()`

Automated escalation workflow:

1. **Pre-merge Validation**
   - Repository state validation
   - Branch verification
   - Network connectivity check

2. **Merge Execution**
   - Attempt automated merge
   - Capture exit code and output
   - Classify result

3. **Conflict Response** (if conflicts detected)
   - Generate detailed conflict report
   - Log comprehensive conflict details
   - Create escalation context
   - Invoke OpenCode with enhanced prompt

4. **Resolution Verification**
   - Check OpenCode exit code
   - Validate merge success
   - Log resolution outcome
   - Continue or abort based on result

### 5. OpenCode Integration

**Enhanced Resolution Prompt Template**:

```
Resolve merge conflicts in the current repository.

CONTEXT:
- Operation: {operation_context}
- Conflict Type: {conflict_type}
- Conflicted Files: {file_list}
- Branch: ai (current), origin/main (incoming)

REQUIRED ACTIONS:
1. Analyze conflict markers in each file
2. Resolve conflicts using appropriate strategy:
   - ours: Keep ai branch changes
   - theirs: Keep origin/main changes  
   - union: Combine both changes
   - manual: Carefully merge changes

3. After resolving all conflicts:
   - Test changes if applicable
   - Commit resolution: "Merge conflict resolution by OpenCode"
   - Push to origin/ai branch

4. Use logging functions:
   - log_merge_resolution_outcome() on completion
   - log("INFO"/"ERROR") for status updates

DELIVERABLES:
- All conflicts resolved
- Tests passing
- Changes committed and pushed
- Resolution logged appropriately

Begin conflict resolution now.
```

### 6. State Preservation System

**Function**: `preserve_state_for_opencode(context, error_type)`

Preserves critical state for resolution attempts:

- Current branch state (HEAD commits)
- Conflict markers and diffs
- Working directory changes
- Recent git history
- Error context and classification

## Configuration Options

### Environment Variables

```bash
# Merge behavior
GIT_MERGE_STRATEGY=recursive
GIT_CONFLICT_STYLE=merge
GIT_NO_VERIFY=false

# Timeout configuration  
GIT_OPERATION_TIMEOUT=120
GIT_RETRY_COUNT=3
GIT_RETRY_DELAY=5

# Escalation settings
OPENCODE_ESCALATION_ENABLED=true
OPENCODE_AUTO_RESOLVE=true
MANUAL_INTERVENTION_THRESHOLD=5

# Logging configuration
LOG_MERGE_EVENTS=true
LOG_DIRECTORY=/var/log/auto-slopp
LOG_MAX_SIZE_MB=100
LOG_RETENTION_DAYS=30
```

## Usage Examples

### Basic Merge with Auto-Escalation

```bash
# Automatic conflict detection and escalation
source utils.sh
merge_result=$(merge_origin_main_to_ai_with_escalation)
exit_code=$?

if [[ $exit_code -eq 0 ]]; then
    log "SUCCESS" "Merge completed successfully"
elif [[ $exit_code -eq 2 ]]; then
    log "WARNING" "Conflicts escalated to OpenCode"
else
    log "ERROR" "Merge failed, manual intervention required"
fi
```

### Manual Conflict Analysis

```bash
# Detect and log conflicts without escalation
source utils.sh
conflicted_files=$(detect_merge_conflicts)
conflict_count=$?

if [[ $conflict_count -gt 0 ]]; then
    log_merge_conflict_detection "${conflicted_files[@]}"
    
    # Generate detailed report
    conflict_report=$(generate_conflict_report)
    log "INFO" "Conflict report: $conflict_report"
fi
```

### Custom Escalation Trigger

```bash
# Custom escalation with specific context
classify_merge_error $exit_code "$error_output"
error_type=$(echo "$?")

if [[ "$error_type" == "MERGE_CONFLICT" ]]; then
    preserve_state_for_opencode "custom_operation" "$error_type"
    log_opencode_escalation "$error_type" "$report_file" "custom_context"
    
    # Custom OpenCode prompt
    opencode_prompt="Resolve conflicts from custom operation..."
    safe_execute_opencode "$OPencode_CMD run \"$opencode_prompt\" --agent OpenAgent"
fi
```

## Monitoring and Observability

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| Conflict Rate | % of merges with conflicts | > 25% |
| Resolution Time | Average time to resolve conflicts | > 5 minutes |
| Escalation Rate | % conflicts requiring OpenCode | > 80% |
| Manual Intervention | % conflicts not auto-resolved | > 10% |
| Merge Success Rate | % successful merges | < 95% |

### Log Analysis Queries

**Find recent conflicts**:
```bash
grep "MERGE_CONFLICT_DETECTED" /var/log/auto-slopp/merge_events.log
```

**Analyze conflict patterns**:
```bash
jq '.conflicted_files | length' /var/log/auto-slopp/merge_events.log | sort | uniq -c
```

**Track OpenCode resolution success**:
```bash
grep "opencode_resolved" /var/log/auto-slopp/merge_events.log | jq '.outcome' | sort | uniq -c
```

## Best Practices

### 1. Proactive Conflict Prevention

- **Frequent Integration**: Merge small changes frequently
- **Feature Branching**: Isolate work to minimize conflicts
- **Communication**: Team coordination on shared files

### 2. Conflict Resolution Strategies

- **Automated First**: Use OpenCode for routine conflicts
- **Manual Review**: Human review for critical systems
- **Testing Required**: Always test after conflict resolution

### 3. Logging and Audit

- **Complete Audit Trail**: Log all merge operations
- **Context Preservation**: Save state before escalation
- **Resolution Documentation**: Track resolution methods and outcomes

### 4. Performance Optimization

- **Timeout Management**: Prevent infinite escalation loops
- **Retry Logic**: Exponential backoff for transient failures
- **Resource Cleanup**: Remove temporary conflict files

## Troubleshooting Guide

### Common Issues

**Issue**: OpenCode escalation timeout
```
Cause: Complex conflicts requiring extensive resolution
Solution: Manual intervention, break into smaller merges
```

**Issue**: Recurring conflicts on same files
```
Cause: Multiple developers editing same files frequently
Solution: File ownership assignment, merge strategies
```

**Issue**: Merge leaves residual conflict markers
```
Cause: Incomplete conflict resolution
Solution: Post-merge validation, automated marker removal
```

**Issue**: Permission denied during merge
```
Cause: Branch protection rules, read-only repository
Solution: Adjust permissions, bypass rules for automation
```

## Future Enhancements

### Planned Improvements

1. **AI-Powered Conflict Prediction**
   - Predict likely conflicts before merge
   - Proactive notification to developers
   - Suggested resolution strategies

2. **Advanced Resolution Strategies**
   - 3-way merge with semantic understanding
   - Language-specific conflict resolution
   - Test-aware resolution validation

3. **Enhanced Monitoring**
   - Real-time conflict dashboards
   - Trend analysis and predictions
   - Automated performance recommendations

4. **Integration Improvements**
   - Better GitHub/GitLab conflict detection
   - IDE integration for manual resolution
   - CI/CD pipeline conflict handling

## Conclusion

The merge conflict detection and escalation system provides a robust, automated approach to handling merge conflicts in the Auto-slopp repository automation system. Key benefits include:

- **Automated Detection**: Instant identification of merge conflicts
- **Intelligent Classification**: Categorization of error types for appropriate response
- **Seamless Escalation**: Automatic routing to OpenCode for resolution
- **Comprehensive Logging**: Complete audit trail of all operations
- **State Preservation**: Context maintenance for resolution attempts
- **Performance Monitoring**: Metrics and alerts for system health

The system successfully balances automation with human oversight, providing efficient conflict resolution while maintaining system reliability and audit capabilities.

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-05  
**Status**: ✅ Implemented and Operational
