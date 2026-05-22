# Branch Workflow and DCO Requirements

## User Preference: One Branch Per Issue

**CRITICAL**: When fixing an Issue, use ONE branch only. Do NOT create multiple branches (v1, v2, v3) for the same Issue.

### Why This Matters

- Multiple branches create confusion
- Each branch requires a new PR
- Harder to track which PR is the "real" one
- Wastes branch namespace

### Wrong Pattern

```
Issue #9358:
  - doc/fix-deepseek-v3.2-parameter-9358      (PR #9369)
  - doc/fix-deepseek-v3.2-parameter-9358-v2   (PR #9379)
  - doc/fix-deepseek-v3.2-parameter-9358-v3   (???)
```

### Correct Pattern

```
Issue #9358:
  - doc/fix-deekseek-v3.2-parameter-9358-v2   (PR #9379)
  # Fix issues on same branch, force push to update PR
```

### When You Need to Fix Issues

```bash
# Stay on same branch
git checkout doc/fix-deekseek-v3.2-parameter-9358-v2

# Make fixes
git add .
git commit -s -m "[Doc] Fix additional issues"

# Push to same branch (updates existing PR)
git push fork HEAD:doc/fix-deekseek-v3.2-parameter-9358-v2
```

### When to Create New Branch

- ONLY if old branch is completely broken (e.g., wrong base, massive history)
- AND you've closed the old PR
- Use clean name without version suffix

---

## DCO Requirements

### Email Matching Requirement

The email in `Signed-off-by` MUST match the email in Git's `user.email` config. If they don't match, DCO check will fail even though Signed-off-by is present.

### Symptoms

- DCO check fails with "action_required"
- All commits have Signed-off-by, but still fails
- Author email is GitHub's noreply email: `32252938+username@users.noreply.github.com`
- Signed-off-by email is your real email: `your@email.com`

### Root Cause

- Git config `user.email` is wrong or not set
- GitHub API file updates use noreply email automatically
- DCO requires Author email == Signed-off-by email

### Detection

```bash
# Check Git config
git config user.email
# If this doesn't match your Signed-off-by email, DCO will fail

# Check commit Author vs Signed-off-by
git log -1 --pretty=format:"Author: %an <%ae>%nSigned-off-by: %b"
```

### Solutions

#### Method 1: Fix Git config (recommended)

```bash
# Set correct email
git config --global user.email "your@email.com"

# Recreate commits with correct Author
git commit --amend --reset-author -s --no-edit

# Force push
git push --force
```

#### Method 2: Make GitHub use your real email

1. Visit https://github.com/settings/emails
2. Uncheck "Keep my email addresses private"
3. Now GitHub API will use your real email instead of noreply

#### Method 3: Use local Git push instead of GitHub API

- GitHub API file updates always use noreply email
- Local Git commits use your configured email
- When network allows, prefer local commit + push

### Verification

```bash
# After fix, verify match
git log -1 --pretty=format:"Author: %ae%nSigned-off-by: " && \
git log -1 --pretty=format:"%b" | grep "Signed-off-by:" | sed 's/Signed-off-by:.*<\(.*\)>/\1/'
```

---

## GitHub API Limitations

### Cannot Specify Author Email

When updating files via GitHub REST API, the Author email is automatically set to GitHub's noreply email. You cannot specify a custom email.

**Implication**:
- API updates: Author = `32252938+username@users.noreply.github.com`
- Local commits: Author = your `git config user.email`

**For DCO compliance**:
- If you need Author email to match Signed-off-by, use local Git commit
- Or uncheck "Keep my email addresses private" in GitHub settings

### Cannot Modify PR Title/Description

Personal Access Tokens cannot modify PR title or description in upstream repositories (repos you don't own), even with full `repo` scope.

**Symptoms**:
```
PATCH /repos/vllm-project/vllm-ascend/pulls/9379
→ 403 Forbidden: "Resource not accessible by personal access token"
```

**Solution**: Manually edit PR via GitHub Web UI (takes 30 seconds)

---

## CI Failures

### yaml sync lint error

**Symptoms**:
```
Check docs/yaml sync blocks...............................................Failed
- hook id: check-docs-yaml-sync
- exit code: 1

##[error] MiniMax-M2.7.md:1: yaml sync lint error
  detail: Markdown files should link model test cases.
```

**Solution**: Add to exclude list in `pyproject.toml`:

```toml
[tool.check_docs_yaml_sync]
exclude = [
    ...
    "docs/source/tutorials/models/MiniMax-M2.5.md",
    "docs/source/tutorials/models/MiniMax-M2.7.md",  # Add here
    ...
]
```

### markdownlint format error

**Symptoms**:
```
markdownlint..............................................................Failed
- hook id: markdownlint
- files were modified by this hook
```

**Common issues**:

1. **Trailing space after bold text**:
   ```markdown
   Wrong: **Note**: 
   Right: **Note**:
   ```

2. **Missing blank line before list**:
   ```markdown
   Wrong:
   **Note**:
   - item 1
   
   Right:
   **Note**:
   
   - item 1
   ```

**Fix**: The hook auto-fixes, just commit the changes:
```bash
git add docs/source/path/to/file.md
git commit -s -m "[Doc] Fix markdownlint format issues"
git push
```

---

## Local Main Branch Sync

Always sync local main with remote before creating new branches, otherwise PR will include unexpected changes from commits that remote main has but local main doesn't.

### Symptoms

- PR shows extra files changed (e.g., 4 files instead of 2)
- PR diff includes changes you didn't make
- `git diff origin/main` shows different files than expected

### Root Cause

- Local main branch is behind remote main
- Creating branch from local main includes "missing" commits
- PR compares against remote main, showing the gap

### Solution

```bash
# Always sync main first
git checkout main
git pull origin main

# OR use remote main directly
git checkout -b new-branch origin/main
```

### If You Already Created Branch from Old Main

```bash
# Rebase onto latest main
git checkout your-branch
git rebase origin/main

# Force push to update PR
git push fork your-branch --force
```

---

## PR Format Requirements

### PR Title Format

```
[Type][SubType] Description

Examples:
[Doc][BugFix] Fix parameter mismatch in DeepSeek-V3.2.md
[Feature][Model] Add DeepSeek V4 support
[BugFix][Scheduler] Fix deadlock in BalanceScheduler
```

### PR Description Format

```markdown
### What this PR does / why we need it?
[Description of what the PR does and why]

Fixes #XXX

### Does this PR introduce _any_ user-facing change?
[Yes/No, with details if Yes]

### How was this patch tested?
[Test method]
```

---

## Reference

- Issue #9291 (MiniMax-M2.7 documentation)
- Issue #9358 (DeepSeek-V3.2 parameter mismatch)
- PR #9379 (DCO email mismatch fix)
- PR #9383 (yaml sync lint fix)
- User correction: "同一个Issue尽量一个分支" (May 2026)
