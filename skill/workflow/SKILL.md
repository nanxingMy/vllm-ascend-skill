---
name: vllm-ascend-issue-workflow
description: vLLM-Ascend Issue 处理工作流 - 从 Issue 发现到 PR 合并的完整流程
version: 1.0.0
author: nanxing
tags:
  - vllm-ascend
  - workflow
  - automation
  - issue-handling
---

# vLLM-Ascend Issue 处理工作流

## 触发条件

当用户提到以下关键词时自动激活：

- "处理 Issue"
- "分析 Issue"
- "修复 Issue"
- "创建 PR"
- "workflow"
- "工作流"

---

## 🎯 核心规则

### 1. PR 工作流规则
- **一个 Issue 只允许创建一个 PR**
- 只有在出现**冲突无法解决**时，才允许关闭旧 PR 并创建新的
- 禁止为同一个 Issue 创建多个并行的 PR

### 2. DCO 要求
- **Author 名字和邮箱必须与 Signed-off-by 完全匹配**
- 示例：
  ```
  Author: nanxingMy <1014662416@qq.com>
  Signed-off-by: nanxingMy <1014662416@qq.com>
  ✅ 名字和邮箱都匹配
  ```

### 3. Git 配置
```bash
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"
```

---

## 🔄 完整工作流程（5 个阶段）

### 阶段 1: Issue 发现与分析

**目标**: 发现并分析 Issue，确认修复方案

**步骤**:

1. **发现 Issue**
   ```bash
   # 查看所有 open issues
   gh issue list --repo vllm-project/vllm-ascend --state open
   
   # 查看特定 issue
   gh issue view <issue-number> --repo vllm-project/vllm-ascend
   ```

2. **分析 Issue**
   - Issue 标题和描述
   - Issue 标签（bug, enhancement, documentation）
   - Issue 评论
   - 相关代码

3. **确认修复方案**
   - 需要修改哪些文件？
   - 需要添加哪些功能？
   - 如何测试修复？

**输出**: Issue 编号 + 修复方案

---

### 阶段 2: 分支创建与代码修改

**目标**: 创建分支并修改代码，完成本地测试

**步骤**:

1. **同步 Fork Main**
   ```python
   # 使用 GitHub API 同步 fork main
   # 获取主仓库 main 的最新 SHA
   # 更新 fork main
   ```

2. **创建新分支**
   ```bash
   git checkout main
   git checkout -b <type>/<description>-<issue-number>
   
   # 示例
   git checkout -b bugfix/scheduler-mutex-8975
   ```

3. **修改代码**
   - 定位代码位置
   - 修改代码
   - 验证修改

4. **本地测试**
   ```bash
   pytest tests/ut/test_xxx.py -v
   ruff format vllm_ascend/
   ```

**输出**: 分支名称 + 修改的文件

---

### 阶段 3: PR 创建与 DCO 处理

**目标**: 提交代码、创建 PR，并确保 DCO 通过

**步骤**:

1. **配置 Git 用户信息**
   ```bash
   git config user.name "nanxingMy"
   git config user.email "1014662416@qq.com"
   ```

2. **提交代码（使用 -s）**
   ```bash
   git add <files>
   git commit -s -m "<type>[<scope>] <subject>
   
   Fixes #<issue-number>"
   ```

3. **推送到 Fork**
   ```bash
   git push origin <branch-name>
   ```

4. **创建 PR**
   ```bash
   gh pr create --repo vllm-project/vllm-ascend \
     --title "..." --body "..."
   ```

5. **验证 DCO**
   ```bash
   git log -1 --format="%B" | grep "Signed-off-by"
   ```

**输出**: PR 编号 + DCO 状态

---

### 阶段 4: 检视意见处理

**目标**: 检测、处理并关闭检视意见

**步骤**:

1. **检测检视意见**
   ```bash
   gh api repos/vllm-project/vllm-ascend/pulls/<pr-number>/comments
   ```

2. **分析检视意见类型**
   - 代码修改建议 → 修改代码
   - PR 格式建议 → 更新 PR 描述
   - 测试建议 → 添加测试

3. **自动修改**
   - 修改代码/PR 描述
   - 提交并推送

4. **回复并关闭**
   ```python
   # 回复检视意见
   # 创建总结评论
   ```

**输出**: 已处理的检视意见数量

---

### 阶段 5: CI 监控与合并

**目标**: 监控 CI 状态，处理失败，等待合并

**步骤**:

1. **监控 CI 状态**
   ```bash
   gh pr checks <pr-number> --repo vllm-project/vllm-ascend
   ```

2. **处理 CI 失败**
   - DCO 失败 → 返回阶段 3
   - Lint 失败 → `ruff format` → 提交
   - Test 失败 → 修复测试 → 提交
   - E2E 失败 → 分析原因 → 修复或重试

3. **重试 CI**
   ```bash
   git commit --allow-empty -s -m "CI: Retry"
   git push origin <branch-name>
   ```

4. **等待合并**
   - DCO 通过
   - 所有 CI 通过
   - 无冲突
   - 检视意见已处理

**输出**: PR ready to merge

---

## 🚨 常见问题及解决

### 问题 1: DCO 失败 - 名字不匹配

**错误信息**:
```
Expected "nanxingMy <1014662416@qq.com>"
but got "nanxing <1014662416@qq.com>"
```

**解决方法**:
```bash
git config user.name "nanxingMy"
git commit --amend -s --no-edit
git push --force-with-lease
```

---

### 问题 2: DCO 失败 - 邮箱不匹配

**错误信息**:
```
Expected "nanxingMy <1014662416@qq.com>"
but got "nanxingMy <32252938+nanxingMy@users.noreply.github.com>"
```

**解决方法**:
1. 在 GitHub 设置中取消 "Keep my email addresses private"
2. 或使用本地 Git 推送

---

### 问题 3: 分支冲突

**解决方法**:
```bash
git rebase origin/main
# 解决冲突
git add <files>
git rebase --continue
git push --force-with-lease
```

---

### 问题 4: CI 失败（网络问题）

**识别**:
- IncompleteRead
- Connection broken
- ProtocolError

**解决方法**: 重试 CI

---

## ✅ 检查清单

### 提交前检查
- [ ] Git user.name: nanxingMy
- [ ] Git user.email: 1014662416@qq.com
- [ ] 使用 `git commit -s`
- [ ] Signed-off-by 与 Author 匹配

### PR 创建后检查
- [ ] DCO: ✅ success
- [ ] Mergeable: ✅ True
- [ ] CI: ✅ success
- [ ] Reviews: ✅ 已处理

---

## 📚 参考文档

- [工作流总览](references/workflow/README.md)
- [快速参考](references/workflow/QUICK-REFERENCE.md)
- [阶段 1: Issue 发现与分析](references/workflow/workflow-01-issue-discovery.md)
- [阶段 2: 分支创建与代码修改](references/workflow/workflow-02-branch-and-code.md)
- [阶段 3: PR 创建与 DCO 处理](references/workflow/workflow-03-pr-and-dco.md)
- [阶段 4: 检视意见处理](references/workflow/workflow-04-review-feedback.md)
- [阶段 5: CI 监控与合并](references/workflow/workflow-05-ci-and-merge.md)

---

## 🎓 最佳实践

### DO ✅

- 从 main 创建干净分支
- 检查继承关系
- 最小化修改
- 添加测试
- 格式化代码
- 处理所有反馈
- 监控 CI 状态

### DON'T ❌

- 从其他分支创建
- 不检查基类就实现方法
- 修改不相关代码
- 没有测试就提交
- 忘记格式化
- 忽略反馈
- 多次 merge main

---

## 📝 示例

### 示例: 处理 Issue #8975

```
用户: 帮我处理 Issue #8975

数字员工:
【阶段 1】Issue 分析
- 问题: BalanceScheduler + RecomputeScheduler 死锁
- 类型: BugFix
- 修复方案: 添加互斥检查

【阶段 2】创建分支并修改代码
- 分支: bugfix/scheduler-mutex-8975
- 修改: vllm_ascend/platform.py, tests/ut/test_platform.py
- 测试: ✅ 通过

【阶段 3】创建 PR
- PR: #9416
- DCO: ✅ 通过

【阶段 4】处理检视意见
- 更新 PR 格式
- ✅ 已处理

【阶段 5】监控 CI
- CI: ⏳ 运行中
- 等待完成...
```

---

**工作流版本**: v1.0  
**最后更新**: 2026-05-21
