# vLLM-Ascend PR Workflow Overview

Complete 5-stage workflow for contributing to vLLM-Ascend.

---

## Core Rules

### 1. One Issue = One PR

A single Issue must only have ONE PR. Only create a new PR if:
- Unresolvable merge conflicts occur
- DCO issues cannot be fixed on the existing PR

**Violations**:
- ❌ Creating multiple PRs for the same Issue
- ❌ Creating v1/v2/v3 branches for the same Issue

**Correct approach**:
- ✅ Update existing PR with new commits
- ✅ Rebase and force push to update
- ✅ Only close and create new PR when conflicts are unresolvable

---

### 2. DCO Requirements

Developer Certificate of Origin requires Author **NAME** and **EMAIL** to match Signed-off-by **exactly**.

#### Correct Example
```
Author: nanxingMy <1014662416@qq.com>
Signed-off-by: nanxingMy <1014662416@qq.com>
✅ Name and email both match
```

#### Common Errors

**Error 1: Name mismatch**
```
Author: nanxingMy <1014662416@qq.com>
Signed-off-by: nanxing <1014662416@qq.com>
❌ Name doesn't match: "nanxingMy" vs "nanxing"
```

**Error 2: Email mismatch (GitHub noreply)**
```
Author: nanxingMy <32252938+nanxingMy@users.noreply.github.com>
Signed-off-by: nanxingMy <1014662416@qq.com>
❌ Email doesn't match
```

#### Solution

```bash
# Configure Git BEFORE committing
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"

# Always use -s flag to auto-add Signed-off-by
git commit -s -m "commit message"

# Verify before pushing
git log -1 --format=full
git log -1 --format="%B" | grep "Signed-off-by"
```

#### GitHub API Limitation

When using GitHub API to update files, GitHub automatically uses noreply email, causing DCO failure.

**Solutions**:
1. Disable "Keep my email addresses private" in GitHub settings (https://github.com/settings/emails)
2. Use local git push instead of GitHub API

---

### 3. Review Feedback Processing

Automatically process all review feedback:

1. **Detect** review comments via GitHub API
2. **Analyze** feedback type (code, format, test, documentation)
3. **Modify** code/PR as suggested
4. **Commit** and push changes
5. **Reply** to each comment
6. **Create** summary comment when all addressed

---

## 5-Stage Workflow

### Stage 1: Issue Discovery & Analysis

**Goal**: Understand the problem and plan the fix.

**Steps**:
1. Find Issue (browse, search, or direct link)
2. Read Issue description and comments
3. Identify problem and affected components
4. Determine fix approach
5. Identify files to modify
6. Plan test strategy

**Output**: Issue number + fix plan + files to modify

---

### Stage 2: Branch Creation & Code Modification

**Goal**: Create clean branch and implement fix.

**Critical Step**: **Sync fork main from upstream BEFORE creating branch**

```bash
# Using GitHub API (recommended)
# Get upstream main SHA
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/vllm-project/vllm-ascend/git/refs/heads/main"

# Update fork main
curl -s -X PATCH -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/nanxingMy/vllm-ascend/git/refs/heads/main" \
  -d '{"sha": "<upstream-sha>", "force": true}'
```

**Branch Naming**:
```
<type>/<description>-<issue-number>

Types: feature, bugfix, doc, refactor, test

Examples:
  bugfix/scheduler-mutex-8975
  feature/add-new-api-1234
  doc/update-readme-5678
```

**Steps**:
1. Sync fork main from upstream
2. Create new branch from main
3. Modify code
4. Add/update tests
5. Run local tests
6. Format code (ruff format)

**Output**: Branch name + modified files + test results

---

### Stage 3: PR Creation & DCO Handling

**Goal**: Create PR with correct DCO.

**Git Configuration** (CRITICAL):
```bash
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"
```

**Commit**:
```bash
# Add files
git add <files>

# Commit with -s flag
git commit -s -m "[<Type>][<Scope>] <subject>

<body>

Fixes #<issue-number>"

# Verify
git log -1 --format=full
```

**Push & Create PR**:
```bash
# Push to fork
git push origin <branch-name>

# Create PR
gh pr create --repo vllm-project/vllm-ascend \
  --title "[<Type>][<Scope>] <subject>" \
  --body "### What this PR does / why we need it?

...

### Does this PR introduce _any_ user-facing change?

...

### How was this patch tested?

..."
```

**Verify DCO**:
```bash
# Check commits
gh api repos/vllm-project/vllm-ascend/pulls/<pr-number>/commits

# All commits should have:
# - Author name == Signed-off-by name
# - Author email == Signed-off-by email
```

**Output**: PR number + DCO status

---

### Stage 4: Review Feedback Processing

**Goal**: Address all review comments.

**Steps**:
1. Get review comments
   ```bash
   gh api repos/vllm-project/vllm-ascend/pulls/<pr-number>/comments
   ```

2. For each comment:
   - Analyze feedback type
   - Modify code/PR as needed
   - Commit and push
   - Reply to comment

3. Create summary comment
   ```markdown
   ## ✅ Review Feedback Addressed
   
   All review comments have been addressed:
   - [x] Comment 1: ...
   - [x] Comment 2: ...
   
   Thank you for the feedback! 🎉
   ```

**Feedback Types**:
| Type | Action |
|------|--------|
| Code modification | Edit code → commit → push |
| PR format | Update PR title/body |
| Test suggestion | Add/modify tests → commit → push |
| Documentation | Update docs → commit → push |

**Output**: Number of comments processed

---

### Stage 5: CI Monitoring & Merge

**Goal**: Ensure all CI passes and wait for merge.

**Monitor CI**:
```bash
# View CI status
gh pr checks <pr-number> --repo vllm-project/vllm-ascend

# Get detailed status
gh api repos/vllm-project/vllm-ascend/pulls/<pr-number> | \
  jq -r '.head.sha' | \
  xargs -I {} gh api repos/vllm-project/vllm-ascend/commits/{}/check-runs
```

**Handle CI Failures**:

| Check | Failure Cause | Solution |
|-------|---------------|----------|
| DCO | Name/email mismatch | Fix Git config, amend commit |
| lint | Format issues | `ruff format`, commit |
| test | Test failures | Fix tests, commit |
| e2e | Code or infra issue | Analyze, fix or retry |

**Retry CI**:
```bash
# Empty commit to trigger CI
git commit --allow-empty -s -m "CI: Retry"
git push origin <branch-name>

# Or rerun specific check
gh run rerun <run-id>
```

**Handle Conflicts**:
```bash
# Rebase onto latest main
git fetch origin main
git rebase origin/main

# Resolve conflicts
# Edit conflicted files
git add <files>
git rebase --continue

# Force push
git push --force-with-lease
```

**Wait for Merge**:
- All CI checks pass
- No conflicts
- Review approved
- Maintainer merges

**Output**: PR ready to merge

---

## Common Pitfalls

### Pitfall 1: Creating Branch Without Syncing Fork Main

**Problem**: Branch is based on outdated fork main, leads to conflicts.

**Solution**: Always sync fork main from upstream BEFORE creating branch.

---

### Pitfall 2: DCO Failure Due to Name Mismatch

**Problem**: Author name doesn't match Signed-off-by name.

**Example**:
```
Expected: "nanxingMy <1014662416@qq.com>"
Got: "nanxing <1014662416@qq.com>"
```

**Solution**:
```bash
git config user.name "nanxingMy"
git commit --amend -s --no-edit
git push --force-with-lease
```

---

### Pitfall 3: GitHub API Updates with Noreply Email

**Problem**: GitHub API automatically uses noreply email, breaking DCO.

**Solution**:
1. Disable "Keep my email addresses private" in GitHub settings
2. Or use local git push instead of API

---

### Pitfall 4: Creating Multiple PRs for Same Issue

**Problem**: Violates "One Issue = One PR" rule.

**Solution**: Update existing PR, don't create new one.

---

### Pitfall 5: Not Using -s Flag for Commit

**Problem**: Commit missing Signed-off-by line.

**Solution**: Always use `git commit -s` to auto-add Signed-off-by.

---

## Success Example: Issue #8975 → PR #9416

### Issue
- **Number**: #8975
- **Problem**: BalanceScheduler + RecomputeScheduler causes AlltoAll deadlock
- **Type**: BugFix

### Workflow

**Stage 1**: Analyzed Issue, identified fix location (platform.py)

**Stage 2**: 
- Synced fork main from upstream
- Created branch: `bugfix/scheduler-mutex-8975`
- Added mutex check in platform.py
- Added unit tests

**Stage 3**:
- Configured Git: user.name="nanxingMy", user.email="1014662416@qq.com"
- Committed with `-s` flag
- Pushed to fork
- Created PR #9416
- Verified DCO passed

**Stage 4**:
- Detected Gemini Code Assist review comments
- Updated PR title and summary as suggested
- Replied to comments
- Created summary comment

**Stage 5**:
- Monitored CI status
- All checks passed
- Waiting for merge

### Result
- ✅ DCO: passed
- ✅ Mergeable: True
- ✅ Reviews: processed
- ✅ CI: passed

---

## Quick Reference

### Git Commands
```bash
# Configure
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"

# Commit with DCO
git commit -s -m "message"

# View commit
git log -1 --format=full

# Rebase
git rebase origin/main

# Force push
git push --force-with-lease
```

### GitHub CLI Commands
```bash
# View PR
gh pr view <number>

# Create PR
gh pr create --title "..." --body "..."

# View CI
gh pr checks <number>

# Close PR
gh pr close <number>
```

---

**Version**: 1.0  
**Last Updated**: 2026-05-21  
**Source**: Issue #8975 → PR #9416 workflow
