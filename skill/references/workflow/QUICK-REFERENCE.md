# vLLM-Ascend Issue 处理 - 快速参考

## 🚀 快速开始

### 完整流程（5 个阶段）
```
1. Issue 发现与分析 → 2. 分支创建与代码修改 → 3. PR 创建与 DCO 处理 → 4. 检视意见处理 → 5. CI 监控与合并
```

---

## 📋 阶段 1: Issue 发现与分析

```bash
# 查看所有 open issues
gh issue list --repo vllm-project/vllm-ascend --state open

# 查看特定 issue
gh issue view <issue-number> --repo vllm-project/vllm-ascend

# 搜索 issue
gh issue list --repo vllm-project/vllm-ascend --search "keyword"
```

**输出**: Issue 编号 + 修复方案

---

## 📋 阶段 2: 分支创建与代码修改

```bash
# 同步 fork main（使用 GitHub API）
# ...

# 创建分支
git checkout main
git checkout -b <type>/<description>-<issue-number>

# 修改代码
# ...

# 本地测试
pytest tests/ut/test_xxx.py -v
ruff format vllm_ascend/
```

**输出**: 分支名称 + 修改的文件

---

## 📋 阶段 3: PR 创建与 DCO 处理

```bash
# 配置 Git
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"

# 提交代码（使用 -s）
git add <files>
git commit -s -m "<type>[<scope>] <subject>

Fixes #<issue-number>"

# 推送
git push origin <branch-name>

# 创建 PR
gh pr create --repo vllm-project/vllm-ascend \
  --title "..." --body "..."

# 验证 DCO
git log -1 --format="%B" | grep "Signed-off-by"
```

**输出**: PR 编号 + DCO 状态

---

## 📋 阶段 4: 检视意见处理

```bash
# 获取检视意见
gh api repos/vllm-project/vllm-ascend/pulls/<pr-number>/comments

# 处理检视意见
# - 代码建议: 修改代码 → 提交 → 推送
# - 格式建议: 更新 PR 描述
# - 测试建议: 添加测试 → 提交 → 推送

# 回复检视意见
gh api repos/vllm-project/vllm-ascend/pulls/<pr-number>/comments \
  -f body="✅ Thank you for the feedback!"
```

**输出**: 已处理的检视意见数量

---

## 📋 阶段 5: CI 监控与合并

```bash
# 查看 CI 状态
gh pr checks <pr-number> --repo vllm-project/vllm-ascend

# 处理 CI 失败
# - DCO 失败: 返回阶段 3
# - Lint 失败: ruff format → 提交
# - Test 失败: 修复测试 → 提交
# - E2E 失败: 分析原因 → 修复或重试

# 重试 CI
git commit --allow-empty -s -m "CI: Retry"
git push origin <branch-name>

# 查看合并状态
gh pr view <pr-number> --repo vllm-project/vllm-ascend
```

**输出**: PR ready to merge

---

## 🔧 常用命令

### Git 命令
```bash
# 配置用户
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"

# 提交（自动添加 Signed-off-by）
git commit -s -m "message"

# 查看提交
git log -1 --format=full

# Rebase
git rebase origin/main

# 强制推送
git push --force-with-lease
```

### GitHub CLI 命令
```bash
# 查看 PR
gh pr view <number>

# 创建 PR
gh pr create --title "..." --body "..."

# 查看 CI
gh pr checks <number>

# 关闭 PR
gh pr close <number>
```

---

## 🚨 常见问题

### DCO 失败 - 名字不匹配
```bash
# 配置正确的用户名
git config user.name "nanxingMy"

# 修改提交
git commit --amend -s --no-edit
git push --force-with-lease
```

### DCO 失败 - 邮箱不匹配
```bash
# 取消 GitHub 邮箱隐私设置
# 访问: https://github.com/settings/emails
# 取消勾选 "Keep my email addresses private"
```

### 分支冲突
```bash
# Rebase
git rebase origin/main
# 解决冲突
git add <files>
git rebase --continue
git push --force-with-lease
```

### CI 失败
```bash
# 查看失败详情
gh run view <run-id>

# 重试 CI
gh run rerun <run-id>
```

---

## ✅ 检查清单

### 提交前
- [ ] Git user.name: nanxingMy
- [ ] Git user.email: 1014662416@qq.com
- [ ] 使用 `git commit -s`
- [ ] Signed-off-by 与 Author 匹配

### PR 创建后
- [ ] DCO: ✅ success
- [ ] Mergeable: ✅ True
- [ ] CI: ✅ success
- [ ] Reviews: ✅ 已处理

---

## 📚 完整文档

- [总览](./README.md)
- [阶段 1: Issue 发现与分析](./workflow-01-issue-discovery.md)
- [阶段 2: 分支创建与代码修改](./workflow-02-branch-and-code.md)
- [阶段 3: PR 创建与 DCO 处理](./workflow-03-pr-and-dco.md)
- [阶段 4: 检视意见处理](./workflow-04-review-feedback.md)
- [阶段 5: CI 监控与合并](./workflow-05-ci-and-merge.md)

---

**版本**: v2.0  
**最后更新**: 2026-05-21
