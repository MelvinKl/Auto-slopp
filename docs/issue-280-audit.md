# Issue 280 Step 1 Audit: Remove beads

Date: 2026-03-18
Branch: `ai/issue-280-remove-beads`

## Audit method
- `git ls-files | sed 's#^#./#' | xargs -r grep -nHiE "bead|beads|BEAD"`
- `find . -path ./.git -prune -o -type d | grep -Ei "bead|beads"`
- `find . -path ./.git -prune -o -type f | grep -Ei "bead|beads"`

## Bead-related artifacts in scope
- `README.md`: repository tree lists `.beads/` with beads description.
- `docs/testing.md`: contains "Beads Integration" scenario text.
- `tests/test_ralph.py`: contains explicit `"beads"` wording in assertion text.
- Local untracked `.beads/` directory exists in the repository root.

## Out-of-scope matches
- `uv.lock` contains unrelated package URL fragments with `bead` as part of hashes/paths.
- `.venv/` contains third-party package content unrelated to repository implementation.

## Exact removal scope for subsequent steps
1. Remove bead-specific references from `README.md` and `docs/testing.md`.
2. Remove or rewrite bead-specific wording in `tests/test_ralph.py`.
3. Remove local `.beads/` runtime artifacts and ensure no tracked bead assets remain.
4. Keep `src/auto_slopp/utils/ralph.py` unchanged for this issue.
