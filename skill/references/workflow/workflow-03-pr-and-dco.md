# 阶段 3: PR 创建与 DCO 处理

## 🎯 目标

提交代码、创建 PR，并确保 DCO 通过。

---

## 📋 步骤

### 3.1 配置 Git 用户信息

#### 为什么重要？
- DCO 要求 Author 名字和邮箱必须与 Signed-off-by 完全匹配
- 配置错误会导致 DCO 失败

#### 配置方法
```bash
# 配置用户名和邮箱
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"

# 验证配置
git config user.name   # 应该输出: nanxingMy
git config user.email  # 应该输出: 1014662416@qq.com
```

#### 常见错误
```
❌ 错误示例:
Author: nanxingMy <1014662416@qq.com>
Signed-off-by: nanxing <1014662416@qq.com>
→ 名字不匹配，DCO 失败

✅ 正确示例:
Author: nanxingMy <1014662416@qq.com>
Signed-off-by: nanxingMy <1014662416@qq.com>
→ 名字和邮箱都匹配，DCO 通过
```

---

### 3.2 提交代码

#### 提交命令
```bash
# 添加修改的文件
git add <files>

# 提交（使用 -s 自动添加 Signed-off-by）
git commit -s -m "<commit-message>"

# 示例
git commit -s -m "[Ops][BugFix] Add mutual exclusion check for BalanceScheduler and RecomputeScheduler

- Add mutex check to prevent deadlock
- Add unit tests

Fixes #8975"
```

#### Commit Message 规范
```
<type>[<scope>] <subject>

<body>

<footer>

type:
  - feat: 新功能
  - fix: Bug 修复
  - docs: 文档
  - style: 格式
  - refactor: 重构
  - test: 测试
  - chore: 构建/工具

scope: 可选，影响范围

示例:
[Ops][BugFix] Add mutual exclusion check for BalanceScheduler
[Test] Add unit tests for scheduler mutex check
```

#### 验证提交
```bash
# 查看提交信息
git log -1 --format=full

# 查看 Signed-off-by
git log -1 --format="%B" | grep "Signed-off-by"

# 应该输出:
# Signed-off-by: nanxingMy <1014662416@qq.com>
```

---

### 3.3 推送到 Fork

#### 推送命令
```bash
# 推送到 fork
git push origin <branch-name>

# 示例
git push origin bugfix/scheduler-mutex-8975

# 如果分支已存在，使用强制推送
git push origin <branch-name> --force-with-lease
```

#### 使用 GitHub API 推送（可选）
```python
import requests
import base64

# 读取文件内容
with open('vllm_ascend/platform.py', 'r') as f:
    content = f.read()

content_base64 = base64.b64encode(content.encode()).decode()

# 更新文件
response = requests.put(
    'https://api.github.com/repos/nanxingMy/vllm-ascend/contents/vllm_ascend/platform.py',
    headers={'Authorization': f'token {token}'},
    json={
        'message': 'commit message\n\nSigned-off-by: nanxingMy <1014662416@qq.com>',
        'content': content_base64,
        'sha': file_sha,
        'branch': branch_name
    }
)
```

---

### 3.4 创建 PR

#### 使用 GitHub CLI
```bash
gh pr create \
  --repo vllm-project/vllm-ascend \
  --title "[Ops][BugFix] Add mutual exclusion check for BalanceScheduler and RecomputeScheduler" \
  --body "### What this PR does / why we need it?

This PR adds a mutual exclusion check between BalanceScheduler and RecomputeScheduler.

Fixes #8975

### Does this PR introduce _any_ user-facing change?

Yes. The system will now raise a ValueError if both schedulers are enabled.

### How was this patch tested?

- Added unit tests in tests/ut/test_platform.py
- Verified that each scheduler can be enabled individually"
```

#### 使用 GitHub API
```python
response = requests.post(
    'https://api.github.com/repos/vllm-project/vllm-ascend/pulls',
    headers={'Authorization': f'token {token}'},
    json={
        'title': 'PR Title',
        'head': 'nanxingMy:branch-name',
        'base': 'main',
        'body': 'PR Description'
    }
)
pr_number = response.json()['number']
```

---

### 3.5 验证 DCO

#### 检查 DCO 状态
```bash
# 获取 PR 的 check runs
gh api repos/vllm-project/vllm-ascend/pulls/<pr-number> | \
  jq -r '.head.sha' | \
  xargs -I {} gh api repos/vllm-project/vllm-ascend/commits/{}/check-runs

# 查找 DCO check
# 应该看到: conclusion: "success"
```

#### 检查 Commits
```bash
# 获取 PR 的所有 commits
gh api repos/vllm-project/vllm-ascend/pulls/<pr-number>/commits

# 验证每个 commit 的:
# - Author 名字和邮箱
# - Signed-off-by 名字和邮箱
# - 两者是否匹配
```

---

## 🚨 DCO 问题处理

### 问题 1: 名字不匹配

#### 错误信息
```
Expected "nanxingMy <1014662416@qq.com>"
but got "nanxing <1014662416@qq.com>"
```

#### 解决方法
```bash
# 1. 配置正确的用户名
git config user.name "nanxingMy"

# 2. 修改最后一次提交
git commit --amend -s --no-edit

# 3. 强制推送
git push --force-with-lease
```

---

### 问题 2: 邮箱不匹配

#### 错误信息
```
Expected "nanxingMy <1014662416@qq.com>"
but got "nanxingMy <32252938+nanxingMy@users.noreply.github.com>"
```

#### 原因
- GitHub API 更新文件会自动使用 noreply 邮箱
- GitHub 设置了 "Keep my email addresses private"

#### 解决方法
```bash
# 方法 1: 取消 GitHub 邮箱隐私设置
# 访问: https://github.com/settings/emails
# 取消勾选 "Keep my email addresses private"

# 方法 2: 使用本地 Git 推送
git push origin <branch-name>
```

---

### 问题 3: 缺少 Signed-off-by

#### 错误信息
```
The commit is missing a Signed-off-by line
```

#### 解决方法
```bash
# 添加 Signed-off-by
git commit --amend -s --no-edit

# 或重新提交
git reset HEAD~1
git commit -s -m "message"
```

---

## 📝 案例: Issue #8975

### 配置 Git
```bash
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"
```

### 提交代码
```bash
git add vllm_ascend/platform.py tests/ut/test_platform.py

git commit -s -m "[Ops][BugFix] Add mutual exclusion check for BalanceScheduler and RecomputeScheduler

- Add mutex check to prevent deadlock when both schedulers are enabled
- BalanceScheduler and RecomputeScheduler must not be enabled simultaneously
- Add unit tests

Fixes #8975"
```

### 推送并创建 PR
```bash
git push origin bugfix/scheduler-mutex-8975

gh pr create \
  --repo vllm-project/vllm-ascend \
  --title "[Ops][BugFix] Add mutual exclusion check for BalanceScheduler and RecomputeScheduler" \
  --body "..."
```

### 验证 DCO
```
Commit: e304fcdf
Author: nanxingMy <1014662416@qq.com>
Signed-off-by: nanxingMy <1014662416@qq.com>
✅ DCO 通过（名字和邮箱都匹配）
```

---

## ✅ 检查清单

### 提交前检查
- [ ] Git user.name 正确
- [ ] Git user.email 正确
- [ ] 使用 `git commit -s` 提交
- [ ] Commit message 符合规范
- [ ] Signed-off-by 已添加

### PR 创建后检查
- [ ] PR 已创建
- [ ] DCO check 通过
- [ ] 无冲突 (Mergeable: True)
- [ ] CI 开始运行

### DCO 验证检查
- [ ] Author 名字与 Signed-off-by 名字匹配
- [ ] Author 邮箱与 Signed-off-by 邮箱匹配
- [ ] 所有 commits 都有 Signed-off-by
- [ ] DCO check 显示 success

---

## 📝 输出

完成本阶段后，应该有：

1. **PR 编号**: `<pr-number>`
2. **PR 链接**: `https://github.com/vllm-project/vllm-ascend/pull/<pr-number>`
3. **DCO 状态**: ✅ 通过
4. **Mergeable**: ✅ True

---

## 🔄 下一阶段

准备完成后，进入 [阶段 4: 检视意见处理](./workflow-04-review-feedback.md)

---

**阶段**: 3/5  
**文档版本**: v1.0
