# 11 Technical Risks

## Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R1 | AI-generated code contains bugs ("slop") | High | Medium | Comprehensive test suite, `make test` validation step, code review |
| R2 | GitHub API rate limiting | Medium | High | Rate limit monitoring, cooldown for CLI tools, retry logic |
| R3 | CLI tool failures (network, API changes) | Medium | Medium | Tiered tool selection with fallback, cooldown mechanism, health probing |
| R4 | Telegram API changes or downtime | Low | Medium | Retry logic with backoff, graceful degradation (logs still go to console/file) |
| R5 | Vikunja API changes or downtime | Low | Low | TaskSource abstraction allows swapping implementations |
| R6 | Git branch conflicts (multiple workers on same repo) | Medium | Medium | Branch-per-task isolation, each worker processes repos independently |
| R7 | Environment variable misconfiguration | Medium | Medium | Pydantic validation, sensible defaults, `--debug` mode for troubleshooting |
| R8 | Security vulnerability in dependencies | Low | High | `make security` (safety + bandit) in CI, regular dependency updates |
| R9 | GitHub token exposure | Medium | Critical | Token isolation design (`.gh.env` outside project), documented warnings |
| R10 | Python 3.14 compatibility issues with dependencies | Low | Medium | Pin dependency versions in `pyproject.toml`, test with `make test` |

## Detailed Risk Analysis

### R1: AI-Generated Code Quality

**Description**: Auto-slopp itself contains and processes AI-generated code. This code may contain subtle bugs, incorrect assumptions, or "slop" patterns.

**Mitigation**:
- Each task processed by auto-slopp includes a `Validate` step that runs `make test`
- The project's own test suite must pass before changes are committed
- Code quality checks (black, isort, flake8) enforce consistent style

**Residual Risk**: Some edge cases may not be covered by tests. Manual review recommended for critical paths.

### R2: GitHub API Rate Limiting

**Description**: GitHub API has rate limits (5000 requests/hour for authenticated users). Processing many issues across multiple repositories could exceed limits.

**Mitigation**:
- Use `gh` CLI which handles rate limiting gracefully
- Monitor rate limit in logs
- Process repositories sequentially within a single run

**Residual Risk**: Large-scale processing across many repositories may require rate limit awareness.

### R3: CLI Tool Failures

**Description**: Configured CLI tools (opencode, gemini, codex) may fail due to network issues, API changes, or rate limits.

**Mitigation**:
- Tiered tool selection provides fallback options
- Cooldown mechanism prevents repeated failures
- Health probing on startup identifies unhealthy tools
- Task blacklist prevents unsuitable tools for certain task types

**Residual Risk**: If all tools are unavailable, task processing will fail.

### R9: GitHub Token Exposure

**Description**: If `GH_TOKEN` is accidentally placed in `.env`, it would be passed to CLI tools spawned by auto-slopp, potentially granting them GitHub access.

**Mitigation**:
- Design enforces token isolation (`.gh.env` outside project)
- Documentation contains prominent warnings
- `.env` is not committed to version control

**Residual Risk**: User error in configuration. Mitigated by documentation and warnings.

## Risk Monitoring

| Risk | Monitoring Method | Review Frequency |
|------|------------------|-----------------|
| R1 | Test coverage reports, code review | Per PR |
| R2 | GitHub API rate limit headers in logs | Per run |
| R3 | CLI tool error rates, cooldown events | Per run |
| R8 | `make security` in CI | Per PR |
| R9 | Audit `.env` and `.gitignore` | Per deployment |
