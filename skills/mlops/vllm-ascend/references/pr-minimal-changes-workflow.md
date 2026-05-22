# PR Minimal Changes Workflow

## Principle

**Always make minimal, focused changes.** Do not modify files for formatting reasons unless formatting is broken and prevents CI from passing.

## Why This Matters

1. **Review efficiency**: Large diffs with formatting changes make code review difficult
2. **Git history**: Clean git history shows only meaningful changes
3. **CI performance**: Fewer changed files = faster CI
4. **Merge conflicts**: Less chance of conflicts with other PRs

## Techniques

### 1. Preserving File Formatting When Adding Code

When adding tests or code to existing files, preserve original formatting:

```bash
# Step 1: Check file line endings
file tests/ut/test_utils.py
# Output: "with CRLF line terminators" or "with LF line terminators"

# Step 2: Append with correct line endings
# For CRLF files (Windows):
printf '\r\n    def test_new_feature(self):\r\n        ...\r\n' >> file.py

# For LF files (Linux/Mac):
cat >> file.py << 'EOF'

    def test_new_feature(self):
        ...
EOF

# Step 3: Verify minimal change
git diff --stat
# Should show small numbers like:
#  tests/ut/test_utils.py | 38 +++++++++++++++++++++++++
# NOT:
#  tests/ut/test_utils.py | 838 ++++++++++++++++++++++++++-----------------------
```

### 2. What NOT to Do

❌ **Never use `write_file` to completely overwrite files** - it changes line endings and formatting

❌ **Never run formatters on files you didn't meaningfully change**

❌ **Never "fix" whitespace or line breaks in existing code unless it's broken**

### 3. What TO Do

✅ **Check `git diff --stat` before every commit**

✅ **Aim for: additions only, minimal deletions**

✅ **If you see massive line changes (400+/400-), stop and fix it**

## Example: PR #9195 (Good)

```
 tests/ut/test_utils.py | 38 +++++++++++++++++++++++++
 vllm_ascend/utils.py   |  5 +++++
 2 files changed, 43 insertions(+)
```

- 2 files changed
- 43 insertions
- 0 deletions
- **No formatting changes**

## Example: PR #9195 (Bad - Initial Attempt)

```
 tests/ut/test_utils.py | 838 ++++++++++++++++++++++++++-----------------------
 vllm_ascend/utils.py   |   5 +++++
 2 files changed, 443 insertions(+), 400 deletions(-)
```

- 838 lines changed in test file
- 400 deletions (formatting changes)
- **This is what we want to avoid**

## Clean Branch Creation

When working on multiple PRs, always create clean branches from main to avoid including previous PR commits.

### Wrong Approach

```bash
# Creates branch from current branch with ALL history
git checkout -b new-feature
# Result: New PR includes 36 files, 1800+ lines from previous PR
```

### Correct Approach

```bash
# Creates clean branch from main
git checkout -b new-feature origin/main

# Or from fork main
git checkout -b new-feature fork/main

# Apply only the fix for the new issue
# ...

# Verify clean diff
git diff origin/main...HEAD --stat
# Should show only YOUR changes
```

### Workflow for Clean PR

1. Create branch from main: `git checkout -b fix-issue-X origin/main`
2. Apply only the fix for issue X
3. Verify with `git diff origin/main...HEAD --stat`
4. Push to new branch name (never reuse existing branch names)

### Example: PR #9195

- **Wrong**: Created branch from `bugfix/scheduler-mutex-check-8975` → 36 files changed
- **Correct**: Created clean branch from `fork/main` → 2 files, +43 lines

## Verification Checklist

Before pushing:

- [ ] `git diff --stat` shows reasonable numbers
- [ ] No unexpected file format changes (check with `git diff`)
- [ ] Only files you intended to modify are changed
- [ ] No whitespace-only or formatting-only changes
- [ ] CI will pass (lint, format checks)
- [ ] Branch is clean (not based on previous PR branch)

## Related

- See `debugging-patterns.md` for debugging workflow
- See `pr-patterns.md` for PR patterns and examples
- See Issue #9167, PR #9195 for real example
- See Issue #3489 for interface addition example
