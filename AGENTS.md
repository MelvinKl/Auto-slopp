# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Code Standards

**CRITICAL:** NEVER use relative imports in Python code. Always use absolute imports starting from the package root (`auto_slopp`). 

**Examples:**
- ✅ `from auto_slopp.worker import Worker`
- ❌ `from .worker import Worker`
- ❌ `from ..worker import Worker`

This ensures consistent import behavior, better readability, and follows security best practices.

**CRITICAL:** ALL imports must be at the top of the file. Do not place imports in the middle or end of files.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `make test` succeeds
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If 'make test' fails, resolve and retry until it succeeds
- If push fails, resolve and retry until it succeeds

