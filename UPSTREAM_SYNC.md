# Upstream Sync Tracking

**Purpose**: Track which commits from upstream (dobbelina/repository.dobbelina) have been integrated into this fork.

**Last Updated**: 2026-01-04

---

## How to Use This File

1. **Before cherry-picking**: Check this file to see if a commit is already integrated
2. **After cherry-picking**: Add the new entry to the appropriate section below
3. **Format for new entries**:
   ```
   | `upstream-hash` | Commit message | `fork-hash` | YYYY-MM-DD | Notes |
   ```

---

## Already Integrated Commits

These upstream commits have been integrated into the fork (possibly with modifications):

| Upstream Hash | Message | Fork Hash | Date Integrated | Notes |
|---------------|---------|-----------|-----------------|-------|
| `673fe9b` | fix module load error on TvOS #1724 | `07aafdc` | 2025-12-28 | Manual integration |
| `8eae561` | fullxcinema | `ef3a914` | 2025-12-28 | Manual integration |
| `3a98f37` | Python 2 fixes #1722 fixes #1663 | `f9e4c51` | 2025-12-28 | Manual integration |
| `c11caeb` | pornhoarder fixes #1713 | `b4a998e` | 2025-12-28 | Manual integration |
| `31644dc` | pornhub fixes #1712 | `1888b76` | 2025-12-28 | Manual integration |
| `53a9dfe` | whoreshub fixes #1715 | `ab66f4f` | 2025-12-28 | Manual integration |
| `0509d5b` | premiumporn - fixes #1714 | `8ee8f7f` | 2025-12-28 | Manual integration |
| `51c39fb` | porntn fixes #1720 | `5e1458b` | 2025-12-28 | Manual integration |
| `afe1ff0` | celebsroulette, awmnet | `dfbc225` | 2025-12-28 | Manual integration |
| `b4daafc` | fixes (cumlouder, justporn, porndig, porno1hu) | `unknown` | 2025-11-30 | Manual integration |

---

## Pending Upstream Commits

See `CHERRY_PICK_ANALYSIS.md` for detailed list of commits not yet integrated.

---

## Integration Commands

When cherry-picking from upstream, use the `-x` flag to automatically track the source:

```bash
# Cherry-pick with tracking
git cherry-pick -x <upstream-commit-hash>

# This adds a line to the commit message:
# (cherry picked from commit <upstream-commit-hash>)
```

After cherry-picking, update this file:

```bash
# Get the new commit hash in your fork
git log -1 --oneline

# Add entry to this file under 'Already Integrated Commits':
# | `<upstream-hash>` | Commit message | `<fork-hash>` | YYYY-MM-DD | Cherry-picked with -x |
```

---

## Checking Sync Status

To see what new commits are in upstream:

```bash
# Fetch latest from upstream
git fetch upstream

# View commits in upstream not in fork (excluding version bumps)
git log upstream/master --not origin/master --oneline --no-merges | grep -v 'Bumped to v.'

# View detailed changes
git log upstream/master --not origin/master --stat

# Check if a specific upstream commit is in fork
git log --all --grep='cherry picked from commit <hash>'
```

---

## Future Integration Strategy

**Recommended workflow:**

1. **Weekly/Monthly sync check**:
   ```bash
   git fetch upstream
   git log upstream/master --not origin/master --oneline --no-merges | grep -v 'Bumped to v.' > /tmp/new_commits.txt
   ```

2. **Review new commits**:
   - Read commit messages and changes
   - Categorize by priority (critical/high/medium/low)
   - Check for conflicts with fork-specific changes

3. **Cherry-pick with tracking**:
   ```bash
   git cherry-pick -x <hash>  # Automatically adds source reference
   ```

4. **Update this file**:
   - Add entry to 'Already Integrated Commits' table
   - Include any notes about conflicts or modifications

5. **Test**:
   ```bash
   python run_tests.py
   python run_tests.py --coverage
   ```

---

## Notes

- **Manual integrations**: Some commits were manually applied before this tracking system existed
- **Modified integrations**: If a commit was cherry-picked but modified, note it in the 'Notes' column
- **Skipped commits**: If you intentionally skip an upstream commit, document why
- **Version bumps**: Generally skip upstream version bumps and manage versions independently
