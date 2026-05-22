# GitHub PR Creation Limitation with Personal Access Token

## The Problem

**Personal Access Tokens (PAT) cannot create Pull Requests in upstream repositories (repos you don't own), even with full `repo` scope.**

This is a GitHub security design, not a permission issue.

## Symptoms

```bash
POST /repos/vllm-project/vllm-ascend/pulls
→ 403 Forbidden: "Resource not accessible by personal access token"
```

## Root Cause

### Token Permission Scope

| Repository Type | Permission Level | Can Create PR? |
|----------------|------------------|----------------|
| Your own repos (fork) | admin, push, pull | ✅ Yes |
| Others' repos (upstream) | pull (read-only) | ❌ No |

**Why?**
- PAT has full permissions for YOUR repositories
- PAT only has READ permissions for OTHERS' repositories
- Creating PR in upstream requires write permission on upstream
- This is intentional security design to prevent unauthorized PR creation

## Token Permission Check

```bash
# Check fork permissions (will show admin=True, push=True)
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/YOUR-USER/vllm-ascend" | \
  python -c "import sys,json; r=json.load(sys.stdin); print(r.get('permissions'))"

# Output: {'admin': True, 'maintain': True, 'push': True, 'pull': True}

# Check upstream permissions (will show push=False)
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/vllm-project/vllm-ascend" | \
  python -c "import sys,json; r=json.load(sys.stdin); print(r.get('permissions'))"

# Output: {'admin': False, 'maintain': False, 'push': False, 'pull': True}
```

## Standard Workflow

**What ALL open source contributors do**:

```
1. Fork upstream repo         ✅
2. Push code to fork          ✅ (PAT can do this)
3. Create PR in upstream      ❌ (PAT cannot do this)
   → Use GitHub Web UI        ⭐ (easiest, 30 seconds)
   → Or use GitHub CLI (gh)   (requires installation)
```

## Solutions

### Solution 1: GitHub Web UI (Recommended) ⭐

**Link format**:
```
https://github.com/vllm-project/vllm-ascend/compare/main...YOUR-USER:branch-name?expand=1
```

**Steps**:
1. Click the link
2. PR title and branch are auto-filled
3. Paste PR description
4. Click "Create pull request"

**Time**: 30 seconds

**Pros**:
- No installation needed
- Works from any browser
- Visual preview of changes
- Can add labels, reviewers, milestones

### Solution 2: GitHub CLI (gh)

**Installation**:
```bash
# Windows
winget install GitHub.cli

# macOS
brew install gh

# Linux
sudo apt install gh  # Debian/Ubuntu
```

**Usage**:
```bash
# Login (one-time)
gh auth login

# Create PR
cd /path/to/vllm-ascend
gh pr create --repo vllm-project/vllm-ascend

# Or with options
gh pr create \
  --repo vllm-project/vllm-ascend \
  --title "[Doc][BugFix] Fix parameter mismatch" \
  --body "Fixes #9358" \
  --base main
```

**Pros**:
- Can be scripted
- Works from terminal
- Can create PRs for multiple repos

**Cons**:
- Requires installation
- Need to configure authentication

### Solution 3: Become Upstream Collaborator

**Not recommended for most contributors**.

If you're added as a collaborator to the upstream repository:
- You get write permissions
- PAT can create PRs directly
- But this requires maintainer approval

## Why This Is NOT a Problem

### It's the Standard Workflow

**ALL open source contributors use this workflow**:
- Linux Kernel contributors
- Kubernetes contributors
- React contributors
- vLLM-Ascend contributors
- Everyone

### Manual PR Creation Is Fast

- Takes 30 seconds
- No installation needed
- Works reliably
- Safe and secure

### It's a Security Feature

Prevents:
- Unauthorized PR creation
- Malicious users spamming repos with PRs
- Bots creating PRs without proper authentication

## Common Misconceptions

### ❌ "My token doesn't have enough permissions"

**Reality**: Even with full `repo` scope, PAT cannot create PRs in upstream.

### ❌ "I need to generate a special token"

**Reality**: No token can do this. It's a GitHub design, not a token issue.

### ❌ "This is a bug in GitHub"

**Reality**: This is intentional security design.

### ❌ "I should be able to automate PR creation"

**Reality**: You can, but you need:
- GitHub App (requires upstream installation)
- OAuth App (requires upstream configuration)
- Or just use the Web UI (simplest)

## Real Example

**Scenario**: Attempting to auto-create PR for Issue #9358

**Token**: Had full `repo` scope

**Attempt**:
```bash
curl -X POST \
  -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/vllm-project/vllm-ascend/pulls" \
  -d '{"title":"...","head":"nanxingMy:branch","base":"main"}'
```

**Result**: `403 Forbidden`

**Solution**: Used Web UI link:
```
https://github.com/vllm-project/vllm-ascend/compare/main...nanxingMy:doc/fix-deepseek-v3.2-parameter-9358?expand=1
```

**Time**: 30 seconds

## Best Practices

### For Regular Contributors

1. Accept the workflow: Fork → Push → Web UI PR
2. Bookmark the PR creation link template
3. Keep PR description template ready
4. Use GitHub CLI if you prefer terminal

### For Automation

If you need automated PR creation:
1. Use GitHub Apps (requires upstream installation)
2. Use GitHub Actions (can create PRs in same repo)
3. Use bots with proper authentication

### For Organizations

If your organization needs automated PRs:
1. Create a GitHub App
2. Install it on upstream repos (requires maintainer approval)
3. Use App authentication instead of PAT

## Reference

- Attempted: May 2026, Issue #9358
- Token scope: Full `repo`
- Result: 403 Forbidden (expected)
- Solution: Web UI PR creation
- Time: 30 seconds
- Status: ✅ PR created successfully via Web UI
