import re

with open(".ralph/github-291.md", "r") as f:
    content = f.read()

# Step 3
content = re.sub(
    r'(- \[ \] 3\. Fix unused variables.*?)(?=\n  - Acceptance Criteria)',
    r'\1 (Current status: 0 errors reported.)',
    content,
    flags=re.DOTALL
)

# Step 4
content = re.sub(
    r'(- \[ \] 4\. Analyze and eliminate duplicated code.*?)(?=\n  - Acceptance Criteria)',
    r'\1 (Current status: 0 duplicated code found.)',
    content,
    flags=re.DOTALL
)

# Step 5
content = re.sub(
    r'(- \[ \] 5\. Add missing unit tests.*?)(?=\n  - Acceptance Criteria)',
    r'\1 (Current status: Total coverage is 67%.)',
    content,
    flags=re.DOTALL
)

# Step 6
content = re.sub(
    r'(- \[ \] 6\. Run `make test`.*?)(?=\n  - Acceptance Criteria)',
    r'\1 (Current status: 207 tests pass, including 9 in tests/test_stale_branch_cleanup_worker.py.)',
    content,
    flags=re.DOTALL
)

with open(".ralph/github-291.md", "w") as f:
    f.write(content)
