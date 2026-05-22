# DCO (Developer Certificate of Origin) 问题解决指南

## 📋 DCO 检查要求

---

## 1. Signed-off-by 邮箱必须匹配 GitHub 账号

### ❌ 常见错误

**问题**：Signed-off-by 的邮箱与 GitHub 账号不匹配

```
期望: nanxingMy <32252938+nanxingMy@users.noreply.github.com>
实际: nanxing <1014662416@qq.com>
结果: ❌ DCO 检查失败
```

### ✅ 正确做法

**Signed-off-by 必须使用 GitHub 账号的邮箱**：

```
Signed-off-by: nanxingMy <32252938+nanxingMy@users.noreply.github.com>
```

---

## 2. 如何获取正确的 GitHub 邮箱

### 方式 1: 查看 DCO 检查错误信息

DCO 检查失败时会显示期望的邮箱：

```
Expected "nanxingMy <32252938+nanxingMy@users.noreply.github.com>", 
but got "nanxing <1014662416@qq.com>"
```

### 方式 2: 通过 GitHub API 获取

```bash
curl -s -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/user | jq '.login, .id'
```

GitHub 分配的邮箱格式：
```
<user_id>+<username>@users.noreply.github.com
```

例如：
```
32252938+nanxingMy@users.noreply.github.com
```

### 方式 3: 在 GitHub 设置中查看

访问：https://github.com/settings/emails

---

## 3. 配置 Git 使用正确的邮箱

### 方式 1: 全局配置

```bash
git config --global user.name "nanxingMy"
git config --global user.email "32252938+nanxingMy@users.noreply.github.com"
```

### 方式 2: 仓库级配置

```bash
cd vllm-ascend
git config user.name "nanxingMy"
git config user.email "32252938+nanxingMy@users.noreply.github.com"
```

### 方式 3: 提交时指定

```bash
git commit -s --author="nanxingMy <32252938+nanxingMy@users.noreply.github.com>" -m "message"
```

---

## 4. 修复已有提交的 DCO 问题

### 方式 1: 重新提交（推荐）

```bash
# 1. 修改 Git 配置
git config user.name "nanxingMy"
git config user.email "32252938+nanxingMy@users.noreply.github.com"

# 2. 重置到修改前
git reset --soft HEAD~1

# 3. 重新提交
git commit -s -m "[Doc][BugFix] Fix parameter mismatch

Fixes #9358"

# 4. 推送
git push --force
```

### 方式 2: 使用 rebase

```bash
# 修改最近 N 个提交的 Signed-off-by
git rebase HEAD~N --signoff

# 推送
git push --force
```

### 方式 3: 通过 GitHub API 更新

如果 Git push 失败（网络问题），可以通过 GitHub API 更新文件：

```python
import requests
import base64

# 正确的 Signed-off-by
commit_message = """[Doc][BugFix] Fix parameter mismatch

Fixes #9358

Signed-off-by: nanxingMy <32252938+nanxingMy@users.noreply.github.com>"""

# 更新文件
response = requests.put(
    'https://api.github.com/repos/OWNER/REPO/contents/FILE_PATH',
    headers={'Authorization': f'token {TOKEN}'},
    json={
        'message': commit_message,
        'content': content_base64,
        'sha': current_sha,
        'branch': branch_name
    }
)
```

---

## 5. DCO 检查失败的原因

### 原因 1: 邮箱不匹配

```
❌ Signed-off-by 邮箱 ≠ GitHub 账号邮箱
```

**解决**：使用 GitHub 分配的邮箱

---

### 原因 2: 缺少 Signed-off-by

```
❌ commit message 中没有 Signed-off-by 行
```

**解决**：使用 `git commit -s` 自动添加

---

### 原因 3: Merge commit 缺少 Signed-off-by

```
❌ merge commit 没有 Signed-off-by
```

**解决**：
1. 避免在 PR 分支上 merge main
2. 如果必须 merge，使用 `git merge --signoff main`

---

## 6. 最佳实践

### ✅ DO

1. **配置 Git 使用 GitHub 邮箱**
   ```bash
   git config --global user.email "ID+USERNAME@users.noreply.github.com"
   ```

2. **始终使用 `-s` 参数提交**
   ```bash
   git commit -s -m "message"
   ```

3. **从 main 创建干净分支**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/new-feature
   ```

4. **避免在 PR 分支上 merge main**
   - 如果需要同步 main，使用 rebase
   - 或者重新从 main 创建分支

---

### ❌ DON'T

1. **不要使用个人邮箱**
   ```bash
   ❌ git config user.email "personal@example.com"
   ```

2. **不要忘记 `-s` 参数**
   ```bash
   ❌ git commit -m "message"  # 没有 Signed-off-by
   ```

3. **不要在 PR 分支上 merge main**
   ```bash
   ❌ git merge main  # 会创建 merge commit
   ```

---

## 7. 常见错误信息

### 错误 1: "There are N commits incorrectly signed off"

```
There are 2 commits incorrectly signed off.
Expected "nanxingMy <32252938+nanxingMy@users.noreply.github.com>", 
but got "nanxing <1014662416@qq.com>".
```

**原因**：邮箱不匹配

**解决**：重新提交，使用正确的邮箱

---

### 错误 2: "DCO: action_required"

```
DCO 检查状态: action_required
```

**原因**：需要用户操作

**解决**：
1. 查看 DCO 检查详情
2. 按照指示修复
3. 通常需要重新提交

---

## 8. 验证 Signed-off-by

### 检查最近提交

```bash
git log -1 --pretty=format:"%B"
```

应该看到：
```
[Doc][BugFix] Fix parameter mismatch

Fixes #9358

Signed-off-by: nanxingMy <32252938+nanxingMy@users.noreply.github.com>
```

### 检查所有提交

```bash
git log --pretty=format:"%h - %s%n%b%n---"
```

---

## 📚 参考

- [DCO](https://developercertificate.org/)
- [GitHub DCO App](https://probot.github.io/apps/dco/)
- [Git 配置](https://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration)

---

**记住：Signed-off-by 的邮箱必须与 GitHub 账号匹配！** 🎊
