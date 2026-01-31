# Detailed Echo Statement Inventory

## Files Requiring Logging Migration

### Critical Priority Files
1. **main.sh** - 13 echo statements
   - All need migration to log() function
   - Critical for system-wide consistency

2. **planner.sh** - 13 echo statements  
   - Mix of error messages and status updates
   - Needs comprehensive migration

3. **updater.sh** - 5 echo statements
   - Status updates and error messages
   - Needs migration to log() function

4. **update_fixer.sh** - 4 echo statements
   - Status and error messages
   - Needs migration to log() function

### Lower Priority Files
5. **Other scripts** - 12 echo statements total
   - Mostly in yaml_config.sh (configuration parsing)
   - Some in implementer.sh (variable assignments)
   - auto-update-reboot.sh (utility functions)

## Migration Strategy

### Phase 1: Core System Files
- main.sh (13 statements) - HIGHEST PRIORITY
- planner.sh (13 statements) - HIGH PRIORITY  
- updater.sh (5 statements) - HIGH PRIORITY
- update_fixer.sh (4 statements) - MEDIUM PRIORITY

### Phase 2: Utility Files
- Remaining scripts with echo statements - LOWER PRIORITY

## Total Migration Effort
- **35 echo statements** in core files requiring immediate attention
- **12 echo statements** in utility files for later cleanup
- **47 total echo statements** to be migrated across the system

## Recommended Log Level Mapping
- Error messages → `log "ERROR"`
- Status updates → `log "INFO"`  
- Processing details → `log "DEBUG"`
- Success messages → `log "SUCCESS"`
- Warnings → `log "WARNING"`

## Estimated Effort
- **main.sh**: 30 minutes (complete logging overhaul)
- **planner.sh**: 20 minutes (multiple log levels needed)
- **updater.sh**: 15 minutes (straightforward migration)
- **update_fixer.sh**: 10 minutes (minimal changes)
- **Total**: ~75 minutes for core files

## Success Criteria
1. All core scripts use unified log() function
2. Proper log levels applied consistently
3. SCRIPT_NAME variables set where missing
4. No functional regressions
5. Enhanced debugging and monitoring capabilities