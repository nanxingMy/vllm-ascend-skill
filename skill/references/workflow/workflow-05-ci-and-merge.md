# 阶段 5: CI 监控与合并

## 🎯 目标

监控 CI 状态，处理失败，等待合并。

---

## 📋 步骤

### 5.1 监控 CI 状态

#### 查看 CI 状态
```bash
# 使用 GitHub CLI
gh pr checks <pr-number> --repo vllm-project/vllm-ascend

# 使用 GitHub API
gh api repos/vllm-project/vllm-ascend/pulls/<pr-number> | \
  jq -r '.head.sha' | \
  xargs -I {} gh api repos/vllm-project/vllm-ascend/commits/{}/check-runs
```

#### CI 检查类型
| Check | 说明 | 处理 |
|-------|------|------|
| DCO | Developer Certificate of Origin | 确保所有 commits 有正确的 Signed-off-by |
| lint | 代码格式检查 | 运行 `ruff format` |
| test | 单元测试 | 修复失败的测试 |
| e2e | 端到端测试 | 检查是否是基础设施问题 |

#### CI 状态
- ✅ **success**: 通过
- ❌ **failure**: 失败
- ⏳ **in_progress**: 运行中
- ⏸️ **queued**: 排队中

---

### 5.2 处理 CI 失败

#### 分析失败原因

##### 1. DCO 失败
```
Check: DCO
Status: action_required
Message: There are commits incorrectly signed off
```

**处理**: 返回 [阶段 3: PR 创建与 DCO 处理](./workflow-03-pr-and-dco.md)

##### 2. Lint 失败
```
Check: lint
Status: failure
Message: Code format issues
```

**处理**:
```bash
# 格式化代码
ruff format vllm_ascend/ tests/

# 提交
git add .
git commit -s -m "Fix lint issues"
git push origin <branch-name>
```

##### 3. 测试失败
```
Check: test
Status: failure
Message: Some tests failed
```

**处理**:
```bash
# 查看失败详情
gh run view <run-id> --repo vllm-project/vllm-ascend

# 本地运行失败的测试
pytest tests/ut/test_platform.py -v

# 修复测试
# 编辑代码

# 提交
git add .
git commit -s -m "Fix test failures"
git push origin <branch-name>
```

##### 4. E2E 测试失败
```
Check: e2e
Status: failure
Message: E2E tests failed
```

**分析**:
- 是否是代码问题？
- 是否是基础设施问题？（网络、环境等）
- 是否是已知问题？

**处理**:
- 代码问题: 修复并提交
- 基础设施问题: 重试 CI 或联系维护者
- 已知问题: 在 PR 中说明

---

### 5.3 重试 CI

#### 何时重试？
- 网络超时
- 临时环境问题
- 非代码相关的失败

#### 重试方法

##### 方法 1: 空提交
```bash
git commit --allow-empty -s -m "CI: Trigger CI retry"
git push origin <branch-name>
```

##### 方法 2: 重新运行 Check
```bash
# 使用 GitHub CLI
gh run rerun <run-id> --repo vllm-project/vllm-ascend

# 使用 GitHub API
gh api -X POST repos/vllm-project/vllm-ascend/actions/runs/<run-id>/rerun
```

---

### 5.4 等待合并

#### 合并条件
- [ ] DCO 通过
- [ ] 所有 CI 通过
- [ ] 无冲突
- [ ] 检视意见已处理
- [ ] 至少一个 Reviewer 批准

#### 查看合并状态
```bash
# 查看 PR 状态
gh pr view <pr-number> --repo vllm-project/vllm-ascend

# 查看是否可以合并
gh pr view <pr-number> --repo vllm-project/vllm-ascend --json mergeable,mergeStateStatus
```

#### 合并状态
- **MERGEABLE**: 可以合并
- **CONFLICTING**: 有冲突
- **UNKNOWN**: 正在计算
- **BLOCKED**: 被阻止（CI 失败、缺少审批等）

---

### 5.5 处理合并冲突

#### 检测冲突
```bash
gh pr view <pr-number> --repo vllm-project/vllm-ascend --json mergeable

# mergeable: false → 有冲突
```

#### 解决冲突

##### 方案 A: Rebase（推荐）
```bash
# 1. 切换到 PR 分支
git checkout <branch-name>

# 2. 获取最新 main
git fetch origin main

# 3. Rebase
git rebase origin/main

# 4. 解决冲突
# 编辑冲突文件
git add <conflicted-files>
git rebase --continue

# 5. 强制推送
git push origin <branch-name> --force-with-lease
```

##### 方案 B: 关闭旧 PR，创建新 PR（最后手段）
```bash
# 1. 关闭旧 PR
gh pr close <old-pr-number>

# 2. 返回阶段 2，创建新分支
# 参考: workflow-02-branch-and-code.md
```

---

## 🔧 自动化监控

### 设置 Cron Job 监控 PR
```python
import requests

def monitor_pr(pr_number, token):
    # 获取 PR 状态
    response = requests.get(
        f'https://api.github.com/repos/vllm-project/vllm-ascend/pulls/{pr_number}',
        headers={'Authorization': f'token {token}'}
    )
    pr = response.json()
    
    # 检查状态
    mergeable = pr.get('mergeable')
    mergeable_state = pr.get('mergeable_state')
    
    # 获取 CI 状态
    sha = pr['head']['sha']
    response = requests.get(
        f'https://api.github.com/repos/vllm-project/vllm-ascend/commits/{sha}/check-runs',
        headers={'Authorization': f'token {token}'}
    )
    checks = response.json()['check_runs']
    
    # 分析状态
    all_passed = all(c['conclusion'] == 'success' for c in checks if c['status'] == 'completed')
    
    if mergeable and all_passed:
        print(f'✅ PR #{pr_number} ready to merge')
    elif not mergeable:
        print(f'❌ PR #{pr_number} has conflicts')
        # 处理冲突
    else:
        failed_checks = [c for c in checks if c.get('conclusion') == 'failure']
        print(f'⚠️ PR #{pr_number} has {len(failed_checks)} failed checks')
        # 处理失败
```

### 创建 Cron Job
```bash
# 每 10 分钟检查一次
*/10 * * * * python monitor_pr.py 9416
```

---

## 📝 案例: PR #9416

### 监控 CI
```bash
# 查看 CI 状态
gh pr checks 9416 --repo vllm-project/vllm-ascend

# 输出示例:
# DCO              ✅ SUCCESS
# lint             ✅ SUCCESS
# test             ⏳ IN PROGRESS
# e2e-light        ⏳ IN PROGRESS
```

### 处理失败
```
假设 e2e-light 失败:

1. 查看失败详情
   gh run view <run-id>

2. 分析原因
   - 网络超时 → 重试 CI
   - 代码问题 → 修复并提交

3. 重试 CI
   git commit --allow-empty -s -m "CI: Retry"
   git push origin bugfix/scheduler-mutex-8975
```

### 等待合并
```bash
# 查看合并状态
gh pr view 9416 --repo vllm-project/vllm-ascend

# 等待所有检查通过
# 等待 Reviewer 审批
# 等待维护者合并
```

---

## ✅ 检查清单

### CI 监控检查
- [ ] 已查看 CI 状态
- [ ] 已处理所有失败的 CI
- [ ] 所有 CI 通过
- [ ] 无冲突
- [ ] 检视意见已处理

### 合并准备检查
- [ ] DCO: ✅ success
- [ ] Lint: ✅ success
- [ ] Test: ✅ success
- [ ] E2E: ✅ success
- [ ] Mergeable: ✅ True
- [ ] Reviews: ✅ Approved

---

## 📝 输出

完成本阶段后，应该有：

1. **PR 状态**: Ready to merge
2. **CI 状态**: ✅ All passed
3. **合并状态**: ✅ Mergeable
4. **等待**: 维护者合并

---

## 🎉 完成！

恭喜！Issue 处理工作流全部完成！

### 最终状态
- ✅ Issue 已修复
- ✅ PR 已创建
- ✅ DCO 通过
- ✅ CI 通过
- ✅ 检视意见已处理
- ✅ 等待合并

### 下一步
- 等待维护者合并 PR
- 合并后关闭 Issue
- 开始处理下一个 Issue

---

**阶段**: 5/5  
**文档版本**: v1.0
