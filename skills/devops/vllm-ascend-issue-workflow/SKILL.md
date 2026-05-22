---
name: vllm-ascend-issue-workflow
description: Complete workflow for handling vLLM-Ascend issues - from discovery to PR merge. Includes DCO fixes, lint fixes, and review feedback handling.
version: 1.0.0
author: nanxing
tags:
  - vllm-ascend
  - workflow
  - dco
  - git
  - github
  - pr
triggers:
  - "vllm-ascend"
  - "分析 Issue"
  - "修复 Issue"
  - "提交 PR"
  - "处理 Issue"
  - "workflow"
  - "工作流"
  - "DCO"
---

# vLLM-Ascend Issue 处理工作流

完整的 Issue 处理流程，从 Issue 发现到 PR 合并。

## 核心规则

### 1. PR 工作流规则

⚠️ **最重要的规则**：

- **一个 Issue 只允许创建一个 PR**
- **只有在出现冲突无法解决时，才允许关闭旧 PR 并创建新的**
- **DCO 问题不是冲突，不要关闭 PR**
- **Lint 问题不是冲突，不要关闭 PR**

### 2. DCO 要求

DCO (Developer Certificate of Origin) 要求：
- **Author 名字和邮箱必须与 Signed-off-by 完全匹配**
- 使用 `git commit -s` 自动添加 Signed-off-by
- Git 配置必须正确：
  ```bash
  git config user.name "nanxingMy"
  git config user.email "1014662416@qq.com"
  ```

### 3. Git 配置

**必须使用以下配置**：
```bash
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"
```

⚠️ **不要使用**：
- `user.name = "nanxing"` (名字不匹配)
- GitHub noreply 邮箱

### 4. 分支命名

**GitHub 主分支是 main，不是 master**：
```bash
# 正确
git push origin main
git push fork main

# 错误
git push origin master  # ❌
```

## 工作流程

### 阶段 1: Issue 发现与分析

1. 发现 Issue
2. 分析问题根源
3. 确认修复方案
4. 检查是否已有相关 PR

### 阶段 2: 分支创建与代码修改

1. **同步 fork main 到上游最新**：
   ```bash
   # 获取上游 main 最新 SHA
   curl -s https://api.github.com/repos/vllm-project/vllm-ascend/git/refs/heads/main
   
   # 更新 fork main
   git fetch origin
   git checkout main
   git reset --hard origin/main
   git push fork main --force
   ```

2. **创建新分支**：
   ```bash
   git checkout -b <branch-name>
   ```

3. **修改代码**

4. **本地测试**：
   ```bash
   ruff check <files>
   ruff format <files>
   pytest <test-files>
   ```

### 阶段 3: PR 创建与 DCO 处理

1. **配置 Git**：
   ```bash
   git config user.name "nanxingMy"
   git config user.email "1014662416@qq.com"
   ```

2. **提交代码**：
   ```bash
   git commit -s -m "message"
   ```

3. **推送到 fork**：
   ```bash
   git push fork <branch-name>
   ```

4. **创建 PR**：
   - 使用正确的 PR 格式
   - 包含 Fixes #<issue-number>

5. **验证 DCO**：
   - 检查所有 commits 的 Author 和 Signed-off-by 是否匹配

### 阶段 4: 检视意见处理

1. **检测检视意见**：
   ```bash
   curl -s https://api.github.com/repos/vllm-project/vllm-ascend/pulls/<pr>/comments
   ```

2. **自动修改**：根据检视意见修改代码

3. **回复并关闭**：回复检视意见并标记为已解决

### 阶段 5: CI 监控与合并

1. **监控 CI 状态**
2. **处理 CI 失败**
3. **等待合并**

## 常见问题处理

### DCO 失败

**问题**: Commit 的 Author 和 Signed-off-by 不匹配

**解决方案**：
```bash
# Rebase 并添加正确的 Signed-off-by
git rebase --signoff origin/main

# 强制推送
git push --force fork HEAD:<branch-name>
```

详见: `references/dco-fix-patterns.md`

### Lint 失败

**问题**: yaml sync lint error

**解决方案**：
在 `pyproject.toml` 中添加文件到排除列表：
```toml
[tool.check_docs_yaml_sync]
exclude = [
    ...,
    "docs/source/tutorials/models/<filename>.md"
]
```

### 网络问题

**问题**: git push 失败

**解决方案**：使用 GitHub API 推送：
```python
import requests
response = requests.patch(
    f'https://api.github.com/repos/{repo}/git/refs/heads/{branch}',
    headers=headers,
    json={'sha': commit_sha}
)
```

## 检查清单

### 提交前检查

- [ ] Git user.name = "nanxingMy"
- [ ] Git user.email = "1014662416@qq.com"
- [ ] 使用 `git commit -s` 提交
- [ ] 运行 `ruff check` 通过
- [ ] 运行 `ruff format` 通过

### 创建 PR 后检查

- [ ] DCO 检查通过
- [ ] 无冲突 (Mergeable: True)
- [ ] CI 开始运行

### 更新 PR 时检查

- [ ] 在原分支上修改
- [ ] 不要创建新分支
- [ ] 不要创建新 PR

## 最佳实践

### DO

- ✅ 使用正确的 Git 配置
- ✅ 使用 `git commit -s` 提交
- ✅ 在原分支上修改并强制推送
- ✅ 一个 Issue 只创建一个 PR
- ✅ 先同步 fork main 再创建分支

### DON'T

- ❌ 不要使用 GitHub API 创建 commits (会导致 noreply 邮箱)
- ❌ 不要为同一个 Issue 创建多个 PR
- ❌ **不要因为 DCO 问题关闭 PR** - DCO 可以通过 `git rebase --signoff` 修复
- ❌ **不要因为 Lint 问题关闭 PR** - Lint 可以通过修改代码修复
- ❌ 不要使用错误的 Git user.name
- ❌ 不要混淆"冲突"和"问题" - DCO/Lint 是问题，不是冲突，只有无法解决的冲突才应关闭 PR

## 参考文档

- [DCO Fix Patterns](references/dco-fix-patterns.md) - DCO 问题修复模式
- [Lint Fix Patterns](references/lint-fix-patterns.md) - Lint 问题修复模式
- [PR Examples](references/pr-examples.md) - PR 示例

## 相关 Skills

- `github-pr-workflow` - GitHub PR 工作流
- `systematic-debugging` - 系统化调试
