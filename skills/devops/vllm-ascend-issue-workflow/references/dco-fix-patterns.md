# DCO (Developer Certificate of Origin) Fix Patterns

## Common DCO Failures

### 1. GitHub API Creates Commits with Noreply Email

**Problem**: Commits created via GitHub API use noreply email:
```
Author: nanxingMy <32252938+nanxingMy@users.noreply.github.com>
Signed-off-by: nanxing <1014662416@qq.com>
❌ DCO 失败 - 名字和邮箱都不匹配
```

**Root Cause**: GitHub API automatically uses noreply email for Author, which doesn't match Signed-off-by.

**Solution**: Use local git with correct config:
```bash
# Configure git
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"

# Rebase with --signoff
git rebase --signoff origin/main

# Force push
git push --force fork HEAD:<branch-name>
```

### 2. Missing Signed-off-by

**Problem**: Commit has no Signed-off-by line.

**Solution**: Add Signed-off-by using rebase:
```bash
git rebase --signoff origin/main
```

### 3. Author Name Mismatch

**Problem**: Author name doesn't match Signed-off-by name:
```
Author: nanxingMy
Signed-off-by: nanxing
❌ 名字不匹配
```

**Solution**: Ensure git config user.name matches the name in Signed-off-by:
```bash
git config user.name "nanxingMy"
git commit --amend --author="nanxingMy <1014662416@qq.com>" --no-edit
```

## Verification

After fixing, verify DCO:
```bash
# Check each commit
for sha in $(git log --format=%H origin/main..HEAD); do
    echo "Commit: ${sha:0:7}"
    git log -1 --format="Author: %an <%ae>" $sha
    git log -1 --format="%B" $sha | grep "Signed-off-by"
done
```

## Important Rules

⚠️ **CRITICAL**: DCO issues are NOT conflicts. Do NOT close PRs for DCO issues.

1. **Never close PR for DCO issues** - DCO issues can be fixed by rebasing
2. **Only close PR for conflicts** - When merge conflicts cannot be resolved
3. **One PR per issue** - Don't create multiple PRs for the same issue
4. **Force push is OK** - When fixing DCO, force push to update the branch

### Why DCO is Not a Conflict

- **DCO issue**: Commit metadata mismatch - fixable by rebase
- **Conflict**: Code changes incompatible - may require new PR
- **Lint issue**: Code style problem - fixable by modifying code

**User correction**: "This is not a conflict problem, just DCO problem, why close?" - DCO problems should be fixed in-place, not by closing and recreating PRs.

## Example: Fix PR #9383 DCO

```bash
# 1. Switch to branch
git checkout doc/add-minimax-m2.7-support-9291

# 2. Configure git
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"

# 3. Rebase with --signoff
git rebase --signoff origin/main

# 4. Force push
git push --force fork HEAD:doc/add-minimax-m2.7-support-9291
```

Result: All commits now have correct Signed-off-by that matches Author.

## Example: Fix PR #9216 DCO

PR #9216 had 4 commits with DCO failures:
- 3 commits created via GitHub API (noreply email)
- 1 commit missing Signed-off-by

Fix:
```bash
# 1. Switch to branch
git checkout feature/add-worker-shutdown-4112

# 2. Configure git
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"

# 3. Rebase all commits with --signoff
git rebase --signoff origin/main

# 4. Verify all commits
git log --oneline origin/main..HEAD

# 5. Force push
git push --force fork HEAD:feature/add-worker-shutdown-4112
```

Result: All 5 commits now have correct Signed-off-by.
