# DCO Debugging Guide for vLLM-Ascend

## What is DCO?

DCO (Developer Certificate of Origin) is a legal requirement that ensures every commit has a Signed-off-by line indicating the author certifies they have the right to submit the code.

## DCO Requirements

The Author name AND email must **exactly match** the Signed-off-by:

```
✅ CORRECT:
Author: John Doe <john@example.com>
Signed-off-by: John Doe <john@example.com>

❌ WRONG (name mismatch):
Author: John Doe <john@example.com>
Signed-off-by: johndoe <john@example.com>

❌ WRONG (email mismatch):
Author: John Doe <john@company.com>
Signed-off-by: John Doe <john@personal.com>
```

## Common DCO Failure Patterns

### Pattern 1: GitHub API/Web Commits

**Symptom**: Commit created via GitHub API or web interface has noreply email

```
Author: nanxingMy <32252938+nanxingMy@users.noreply.github.com>
Signed-off-by: nanxing <1014662416@qq.com>
```

**Root cause**: GitHub automatically uses noreply email for API/web commits

**Solution**:
1. Don't close the PR - this is fixable
2. Create clean local commit:
   ```bash
   git config user.name "nanxingMy"
   git config user.email "1014662416@qq.com"
   git checkout main
   git checkout -b fix-branch
   # Apply your changes
   git add .
   git commit -s -m "Your message"
   git push --force fork HEAD:original-branch
   ```

### Pattern 2: Missing Signed-off-by

**Symptom**: Commit has no Signed-off-by line

**Solution**: Amend the commit with `-s` flag:
```bash
git commit --amend -s --no-edit
```

### Pattern 3: Multiple Signed-off-by Lines

**Symptom**: Multiple Signed-off-by lines, none matching Author

```
Author: nanxingMy <1014662416@qq.com>
Signed-off-by: nanxing <1014662416@qq.com>
Signed-off-by: nanxingMy <1014662416@qq.com>
```

**Note**: This actually passes DCO if one of them matches!

## How to Check DCO Status

### Via GitHub API

```python
import requests

# Get PR commits
response = requests.get(
    f'https://api.github.com/repos/vllm-project/vllm-ascend/pulls/{pr_number}/commits',
    headers={'Authorization': f'token {token}'}
)

for commit in response.json():
    author = commit['commit']['author']
    message = commit['commit']['message']
    
    # Check for Signed-off-by
    if 'Signed-off-by:' in message:
        signed_offs = [line.strip() for line in message.split('\n') 
                       if 'Signed-off-by:' in line]
        
        # Check if any Signed-off-by matches Author
        matched = any(
            author['name'] in s and author['email'] in s 
            for s in signed_offs
        )
        
        if matched:
            print(f"✅ {commit['sha'][:7]} DCO passes")
        else:
            print(f"❌ {commit['sha'][:7]} DCO fails")
```

### Via DCO Check Run

```python
# Get check runs for a commit
response = requests.get(
    f'https://api.github.com/repos/vllm-project/vllm-ascend/commits/{sha}/check-runs',
    headers={'Authorization': f'token {token}'}
)

# Find DCO check
dco_check = next(
    (c for c in response.json()['check_runs'] if c['name'] == 'DCO'),
    None
)

if dco_check:
    print(f"DCO status: {dco_check['conclusion']}")
    if dco_check['output'].get('text'):
        print(dco_check['output']['text'])
```

## Preventing DCO Issues

### 1. Configure Git Correctly

```bash
git config user.name "YourGitHubUsername"
git config user.email "your-real-email@example.com"
```

### 2. Always Use `-s` Flag

```bash
git commit -s -m "Your message"
```

This automatically adds:
```
Signed-off-by: YourGitHubUsername <your-real-email@example.com>
```

### 3. Avoid GitHub Web/API Edits

- Don't edit files via GitHub web interface
- Don't use GitHub API to create commits
- Always commit locally and push

### 4. Verify Before Pushing

```bash
# Check last commit
git log -1 --format=full

# Should show:
# Author: YourName <your@email.com>
# Signed-off-by: YourName <your@email.com>
```

## What NOT to Do

❌ **Don't close a PR for DCO issues** - They are fixable in place

❌ **Don't create a new PR for DCO issues** - Fix the existing one

❌ **Don't use GitHub web interface for commits** - It uses noreply email

❌ **Don't forget to configure Git** - Set user.name and user.email

## Summary

- DCO requires exact match of Author name AND email with Signed-off-by
- GitHub API/web commits use noreply email - avoid them
- Always commit locally with `-s` flag
- Fix DCO issues by force pushing clean commits, not by closing PRs
- One PR per Issue - don't create multiple PRs for DCO issues
