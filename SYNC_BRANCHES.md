# 同步 master 到 main 分支指南

## 问题

- master 分支：包含所有 16 个文件
- main 分支：只有 2 个文件（GitHub 默认创建）
- 目标：让 main 分支也有所有文件

## 解决方法

### 方法 1: 在 GitHub 网页操作（推荐）

1. **访问仓库设置**
   https://github.com/nanxingMy/vllm-ascend-skill/settings

2. **修改默认分支**
   - 点击左侧 "Branches"
   - 在 "Default branch" 部分，点击切换按钮
   - 选择 "master" 作为默认分支
   - 点击 "Update"

3. **删除 main 分支（可选）**
   - 回到 Branches 页面
   - 找到 main 分支
   - 点击垃圾桶图标删除

### 方法 2: 本地命令行（网络稳定后）

```bash
cd /c/Users/HuaWei/vllm-ascend-skill

# 1. 切换到 master
git checkout master

# 2. 创建新的 main 分支（从 master）
git branch -D main  # 删除本地 main
git checkout -b main

# 3. 推送并覆盖远程 main
TOKEN=$(cat /tmp/github_token.txt)
git remote set-url origin "https://${TOKEN}@github.com/nanxingMy/vllm-ascend-skill.git"
git push origin main --force

# 4. 切换回 master
git checkout master
```

### 方法 3: 使用 GitHub API（需要权限）

```bash
# 将 master 设为默认分支
TOKEN=$(cat /tmp/github_token.txt)

curl -X PATCH \
  -H "Authorization: token ${TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/nanxingMy/vllm-ascend-skill" \
  -d '{"default_branch": "master"}'
```

注意：需要 token 有 repo 权限。

### 方法 4: 在 GitHub Desktop 操作

1. 打开 GitHub Desktop
2. 添加本地仓库：`C:\Users\HuaWei\vllm-ascend-skill`
3. 切换到 master 分支
4. 点击 "Branch" → "Rename Branch"
5. 将 master 重命名为 main
6. 推送

## 推荐：方法 1（网页操作）

最简单，不需要网络推送，直接在 GitHub 网页修改设置。

## 当前状态

- ✅ master 分支：16 个文件（完整）
- ⚠️ main 分支：2 个文件（默认）
- 📌 建议：将 master 设为默认分支

## 访问链接

- 仓库主页：https://github.com/nanxingMy/vllm-ascend-skill
- master 分支：https://github.com/nanxingMy/vllm-ascend-skill/tree/master
- 设置页面：https://github.com/nanxingMy/vllm-ascend-skill/settings
- Branches 设置：https://github.com/nanxingMy/vllm-ascend-skill/settings/branches
