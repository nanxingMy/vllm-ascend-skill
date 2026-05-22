# DCO Requirements and Fixes

## What is DCO?

DCO (Developer Certificate of Origin) is a lightweight way for contributors to certify that they wrote or otherwise have the right to submit the code they are contributing to the project.

**Requirement**: Every commit must have a `Signed-off-by: Name <email>` line in the commit message.

## Why DCO Matters for vLLM-Ascend

vLLM-Ascend uses DCO check on all PRs. If any commit lacks the sign-off line, the PR will be blocked from merging.

**DCO check bot**: Automatically checks every PR and will fail if:
- Any commit is missing `Signed-off-by`
- Merge commits don't have sign-off
- Sign-off doesn't match commit author

## Common DCO Failures

### 1. Regular Commits Without Sign-off

**Symptom**:
```
git commit -m "feat: add feature"
# Missing Signed-off-by!
```

**Fix**:
```bash
# Always use -s flag
git commit -s -m "feat: add feature"
```

### 2. Merge Commits Without Sign-off (Most Common!)

**Symptom**:
```bash
git merge main
# Creates merge commit without Signed-off-by
```

**Detection**:
```bash
# Check if merge commit has sign-off
git log --oneline --merges origin/main..HEAD
# For each merge commit:
git log -1 --pretty=format:"%B" <sha> | grep "Signed-off-by"
```

**Why this happens**: `git merge` doesn't automatically add sign-off.

**Fix**:
```bash
# Option 1: Use --signoff flag
git merge --signoff main

# Option 2: Use rebase instead
git rebase main
```

### 3. Cherry-pick Without Sign-off

**Symptom**:
```bash
git cherry-pick <sha>
# Preserves original commit message, may miss sign-off
```

**Fix**:
```bash
# Add sign-off after cherry-pick
git cherry-pick <sha>
git commit --amend -s --no-edit
```

## Complete Fix Workflow

### Scenario: PR Has Merge Commit Without Sign-off

**Example from PR #9369**:
- PR had 4 commits: 3 regular + 1 merge
- Regular commits had sign-off ✅
- Merge commit lacked sign-off ❌
- DCO check failed

**Solution 1: Create Clean Branch (Recommended for Simple Fixes)**

```bash
# Step 1: Create new clean branch from main
git checkout main
git pull origin main
git checkout -b fix-issue-X-clean

# Step 2: Apply only your changes
# Option A: Cherry-pick your commits
git cherry-pick <commit-sha-1>
git cherry-pick <commit-sha-2>

# Option B: Manually re-apply changes
# (Edit files, then commit)

# Step 3: Verify clean history
git log --oneline origin/main..HEAD
# Should only show YOUR commits, no merge commits

# Step 4: Verify all commits have sign-off
git log origin/main..HEAD --pretty=format:"%h %s" | while read sha msg; do
    if ! git log -1 --pretty=format:"%B" $sha | grep -q "Signed-off-by:"; then
        echo "❌ Missing: $sha"
    else
        echo "✅ OK: $sha"
    fi
done

# Step 5: Push to new branch
git push fork HEAD:fix-issue-X-clean --force

# Step 6: Create new PR from clean branch
# (Close old PR with comment about DCO issue)
```

**Solution 2: Rebase to Remove Merge Commit**

```bash
# Step 1: Interactive rebase
git rebase -i origin/main

# Step 2: In editor, mark merge commit as "drop"
# pick abc1234 Your first commit
# drop def5678 Merge branch 'main' into your-branch  <- DROP THIS
# pick ghi9012 Your second commit

# Step 3: Save and exit
# Git will replay commits without the merge

# Step 4: Force push
git push fork HEAD:your-branch --force
```

**Solution 3: Add Sign-off to Merge Commit**

```bash
# Step 1: Find the merge commit
git log --oneline --merges -1

# Step 2: Amend it with sign-off
git commit --amend -s --no-edit

# Step 3: Force push
git push fork HEAD:your-branch --force
```

## Prevention Best Practices

### 1. Always Use `-s` Flag

```bash
# ❌ Wrong
git commit -m "feat: add feature"

# ✅ Correct
git commit -s -m "feat: add feature"
```

### 2. Use Rebase Instead of Merge

```bash
# ❌ Risky - creates merge commit
git merge main

# ✅ Safer - no merge commit
git rebase main
```

### 3. If You Must Merge, Use --signoff

```bash
# ✅ Correct way to merge
git merge --signoff main
```

### 4. Check Before Pushing

```bash
# Pre-push check script
#!/bin/bash
echo "Checking DCO compliance..."
COMMITS=$(git log origin/main..HEAD --pretty=format:"%h")
FAIL=0

for sha in $COMMITS; do
    if ! git log -1 --pretty=format:"%B" $sha | grep -q "Signed-off-by:"; then
        echo "❌ Missing Signed-off-by: $sha"
        git log -1 --oneline $sha
        FAIL=1
    fi
done

if [ $FAIL -eq 1 ]; then
    echo ""
    echo "DCO check failed! Fix with:"
    echo "  git commit --amend -s --no-edit  # for last commit"
    echo "  git rebase -i origin/main^ --exec 'git commit --amend --signoff --no-edit'  # for all"
    exit 1
else
    echo "✅ All commits have Signed-off-by"
fi
```

## GitHub API Push When Git Push Fails

### Scenario

```bash
git push origin branch
# fatal: unable to access '...': Failed to connect to github.com port 443
# fatal: unable to access '...': Connection was reset

# But curl works:
curl https://api.github.com
# {"current_user_url": ...}  # ✅ Works!
```

### Why This Happens

- Git uses different connection method than curl
- Network/firewall may block Git's HTTPS but allow API
- Git's SSL/TLS handling differs from Python requests

### Solution: Use GitHub REST API

**Python script to update file via API**:

```python
import requests
import base64
import sys

def push_file_via_api(token, owner, repo, branch, file_path, content, commit_message):
    """
    Update a file on GitHub via REST API when git push fails.
    
    Args:
        token: GitHub personal access token
        owner: Repository owner
        repo: Repository name
        branch: Branch name
        file_path: Path to file in repo
        content: New file content (string)
        commit_message: Commit message (include Signed-off-by!)
    
    Returns:
        True if successful, False otherwise
    """
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # 1. Get current file SHA (required for update)
    print(f"1. Getting current file SHA...")
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}'
    resp = requests.get(url, headers=headers)
    
    if resp.status_code == 404:
        print(f"   File doesn't exist on branch, will create new")
        current_sha = None
    elif resp.status_code != 200:
        print(f"   Error: {resp.status_code} - {resp.text}")
        return False
    else:
        current_sha = resp.json()['sha']
        print(f"   Current SHA: {current_sha[:7]}")
    
    # 2. Base64 encode content
    content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    # 3. Update file
    print(f"2. Updating file...")
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{file_path}'
    
    data = {
        'message': commit_message,
        'content': content_b64,
        'branch': branch
    }
    
    if current_sha:
        data['sha'] = current_sha
    
    resp = requests.put(url, headers=headers, json=data)
    
    if resp.status_code in [200, 201]:
        result = resp.json()
        print(f"✅ File updated successfully!")
        print(f"   Commit: {result['commit']['sha'][:7]}")
        print(f"   URL: {result['content']['html_url']}")
        return True
    else:
        print(f"❌ Error: {resp.status_code} - {resp.text}")
        return False

# Usage example
if __name__ == '__main__':
    # Read token
    with open('/tmp/github_token.txt', 'r') as f:
        token = f.read().strip()
    
    # Read file content
    with open('docs/source/tutorials/models/DeepSeek-V3.2.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Commit message MUST include Signed-off-by
    commit_msg = """[Doc][BugFix] Fix parameter mismatch in DeepSeek-V3.2.md

- Fix served-model-name: 'dsv3' -> 'deepseek_v3.2'
- Fix port number: 7000 -> 8000
- Keep placeholders in curl command

Fixes #9358

Signed-off-by: nanxing <1014662416@qq.com>"""
    
    # Push via API
    push_file_via_api(
        token=token,
        owner='nanxingMy',
        repo='vllm-ascend',
        branch='doc/fix-deepseek-v3.2-parameter-9358',
        file_path='docs/source/tutorials/models/DeepSeek-V3.2.md',
        content=content,
        commit_message=commit_msg
    )
```

### Limitations

- **Single file only**: Each API call updates one file
- **No complex git operations**: Can't merge, rebase, etc.
- **No binary files**: Works best for text files
- **Rate limits**: GitHub API has rate limits (5000 requests/hour for auth)

### When to Use

- ✅ Git push fails but API works
- ✅ Simple documentation/config updates
- ✅ Emergency fixes when network unstable
- ❌ Complex multi-file changes (use git when possible)
- ❌ Binary files (use git when possible)

## Real Example: PR #9369

### Timeline

1. **Created PR #9369** with 4 commits
2. **DCO check failed** - merge commit lacked Signed-off-by
3. **Git push failed** - network connection issues
4. **Used GitHub API** to push file update
5. **Still had DCO issue** - merge commit still in history
6. **Created clean branch** `doc/fix-deepseek-v3.2-parameter-9358-v2`
7. **Pushed via API** to clean branch
8. **DCO check passed** ✅

### Key Learnings

1. **Merge commits need Signed-off-by too** - most common DCO failure
2. **Clean branch is often easiest fix** - avoid complex rebase
3. **GitHub API works when Git push fails** - useful workaround
4. **Always check DCO before pushing** - save time

### Commands Used

```bash
# Check DCO compliance
git log origin/main..HEAD --pretty=format:"%h %s" | while read sha msg; do
    if ! git log -1 --pretty=format:"%B" $sha | grep -q "Signed-off-by:"; then
        echo "❌ Missing: $sha $msg"
    fi
done

# Create clean branch
git checkout main
git pull origin main
git checkout -b doc/fix-deepseek-v3.2-parameter-9358-v2

# Apply changes and commit with sign-off
git commit -s -m "[Doc][BugFix] Fix parameter mismatch..."

# Push via API (when git push fails)
python push_via_api.py
```

## References

- DCO Definition: https://developercertificate.org/
- GitHub DCO Check: https://github.com/apps/dco
- PR #9369: https://github.com/vllm-project/vllm-ascend/pull/9369
- Issue #9358: https://github.com/vllm-project/vllm-ascend/issues/9358
