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

---

## PR #9493 - Issue #9454 pip install Cleanup

**Issue**: #9454 - 移除不必要的 pip install

**Key Decision**: 只删除 pip install，保留 `export VLLM_USE_MODELSCOPE=True`

**Learning**: 修改前仔细理解 Issue 的真正需求，不要过度修改。

---

## PR #9369 → Clean Branch - Issue #9358 DeepSeek-V3.2 Parameter Fix

**Issue**: #9358 - DeepSeek-V3.2.md 参数不匹配

**Problems Encountered**:

1. **DCO Failure** - merge commit 缺少 Signed-off-by
2. **Git push 失败** - 需要使用 GitHub API 推送

**Solutions Applied**:

1. **创建干净分支** `doc/fix-deepseek-v3.2-parameter-9358-v2` 解决 DCO 问题

**Key Learnings**:
- merge commits 也需要 Signed-off-by
- Git push 失败时可用 GitHub API 推送
- 创建干净分支是解决 DCO 问题的最简单方法

---

## PR #9199 - Issue #9167 Version Suffix Fix

**Issue**: #9167 - vllm_version_is 版本后缀问题

**Problem**: `vllm.__version__` 包含额外后缀（如 `"0.20.1+cpu"`）导致版本比较失败

**Solution**: 使用 `Version.public` 属性代替手动剥离后缀

**Before**:
```python
vllm_version = vllm_version.split('+')[0]
return Version(vllm_version) == Version(target_vllm_version)
```

**After**:
```python
return Version(vllm_version).public == Version(target_vllm_version).public
```

**Key Learning**: 使用标准库提供的属性处理版本后缀，比手动字符串操作更健壮。
