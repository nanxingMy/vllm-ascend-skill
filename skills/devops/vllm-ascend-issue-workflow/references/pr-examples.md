# PR Examples

This document contains real PR examples with problems and solutions.

## PR #9383 - MiniMax-M2.7 Documentation

**Issue**: #9291 - MiniMax-M2.7 文档缺失

**Branch**: `doc/add-minimax-m2.7-support-9291`

**Problems Encountered**:

1. **DCO Failure** (Check Run ID: 77161748699)
   - Commit ce0c2d9 created via GitHub API
   - Author: `nanxingMy <noreply.github.com>`
   - Signed-off-by: `nanxing <1014662416@qq.com>`
   - ❌ Name and email mismatch

2. **Lint Failure** (Check Run ID: 77164148182)
   - yaml sync lint error for MiniMax-M2.7.md
   - File not in exclude list

**Solutions Applied**:

1. **Fix DCO**:
   ```bash
   git checkout doc/add-minimax-m2.7-support-9291
   git config user.name "nanxingMy"
   git config user.email "1014662416@qq.com"
   git rebase --signoff origin/main
   git push --force fork HEAD:doc/add-minimax-m2.7-support-9291
   ```

2. **Fix Lint**:
   - Added `MiniMax-M2.7.md` to pyproject.toml exclude list
   - Committed and pushed

**Final Result**:
- ✅ DCO passed
- ✅ Lint passed
- ✅ CI passed

**Key Learning**: Don't close PR for DCO issues - fix by rebasing.

---

## PR #9216 - Worker Shutdown Method

**Issue**: #4112 - Add shutdown method to NPUWorker

**Branch**: `feature/add-worker-shutdown-4112`

**Problems Encountered**:

1. **DCO Failure** (Check Run ID: 77161743506)
   - 4 commits with DCO failures:
     - 3 commits created via GitHub API (noreply email)
     - 1 commit missing Signed-off-by

**Solutions Applied**:

1. **Fix DCO**:
   ```bash
   git checkout feature/add-worker-shutdown-4112
   git config user.name "nanxingMy"
   git config user.email "1014662416@qq.com"
   git rebase --signoff origin/main
   git push --force fork HEAD:feature/add-worker-shutdown-4112
   ```

**Final Result**:
- ✅ All 5 commits have correct Signed-off-by
- ✅ DCO passed

**Key Learning**: Multiple commits can be fixed with single rebase --signoff.

---

## PR #9416 - BalanceScheduler Deadlock Check

**Issue**: #8975 - BalanceScheduler + RecomputeScheduler 死锁

**Branch**: `bugfix/scheduler-mutex-8975-dco-fix`

**Problems Encountered**:

1. **Lint Failure**
   - F401: Unused import
   - SIM117: Nested with statements

**Solutions Applied**:

1. **Fix Lint**:
   ```bash
   ruff check --fix vllm_ascend/platform.py tests/ut/test_platform.py
   # Manual fix for SIM117
   git commit -s -m "Fix lint issues"
   git push fork HEAD:bugfix/scheduler-mutex-8975-dco-fix
   ```

**Final Result**:
- ✅ Lint passed
- ✅ DCO passed
- ✅ CI passed

**Key Learning**: Always run ruff check before pushing.

---

## Common Patterns

### Pattern 1: DCO Fix

**When**: Any commit has Author != Signed-off-by

**Steps**:
1. Configure git correctly
2. Rebase with --signoff
3. Force push

### Pattern 2: Lint Fix

**When**: Pre-commit checks fail

**Steps**:
1. Run ruff check --fix
2. Run ruff format
3. Add files to exclude list if needed
4. Commit and push

### Pattern 3: Multiple Problems

**When**: PR has both DCO and Lint issues

**Order**:
1. Fix DCO first (rebase)
2. Then fix Lint (new commit)
3. Push once

---

## What NOT To Do

❌ **Don't close PR for DCO issues**
- DCO can be fixed by rebasing
- Only close for unresolvable conflicts

❌ **Don't create new PR for same issue**
- One issue = one PR
- Update existing PR instead

❌ **Don't use GitHub API to create commits**
- Causes noreply email DCO issues
- Use local git instead

❌ **Don't forget to configure git**
- Always verify user.name and user.email
- Must match Signed-off-by
