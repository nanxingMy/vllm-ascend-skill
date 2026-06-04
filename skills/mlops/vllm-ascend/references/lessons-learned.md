# vLLM-Ascend Lessons Learned

> 从实际贡献中提取的持久性经验教训，每日自动更新

---

## DCO (Developer Certificate of Origin)

### 核心规则
- Author 名字和邮箱必须与 Signed-off-by **完全匹配**（不仅是邮箱，名字也要匹配）
- Git user.email 必须与 Signed-off-by 邮箱一致
- merge commits 也需要 Signed-off-by（使用 `git merge --signoff`）

### 常见问题与修复

| 问题 | 原因 | 修复方法 |
|------|------|----------|
| GitHub API 提交 DCO 失败 | 使用 noreply 邮箱无法自定义 | 本地提交 + 强制推送 |
| GitHub 设置导致邮箱不匹配 | "Keep my email addresses private" 开启 | 取消该设置 |
| merge commit 缺少 Signed-off-by | git merge 不自动添加 signoff | `git merge --signoff` 或 rebase |
| 多个 commit DCO 失败 | 每个 commit 都需要 Signed-off-by | `git rebase --signoff origin/main` |

### 修复流程
```bash
git checkout <branch>
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"
git rebase --signoff origin/main
git push --force fork HEAD:<branch>
```

### ⚠️ 绝对不要
- **不要因为 DCO 问题关闭 PR** — DCO 可以通过 rebase 修复
- **不要使用 GitHub API 创建 commit** — 会导致 noreply 邮箱问题
- **不要忘记检查 git config** — 提交前验证 user.name 和 user.email

---

## Lint 和格式化

### 常见 Lint 问题
- **yaml sync lint**: 文档文件未在 pyproject.toml 的 exclude 列表中
- **F401**: 未使用的 import
- **SIM117**: 嵌套 with 语句
- **ruff format**: 代码格式不符合规范

### 修复方法
```bash
# 修复 lint
ruff check --fix vllm_ascend/ tests/

# 修复格式
ruff format vllm_ascend/ tests/

# 添加到 exclude 列表（pyproject.toml）
# 仅在确认需要排除时使用
```

### ⚠️ 绝对不要
- **不要因为 Lint 问题关闭 PR** — Lint 可以通过修改代码修复

---

## PR 工作流核心规则

1. **一个 Issue 只允许创建一个 PR** — 只有在冲突无法解决或 DCO 无法修复时才关闭旧 PR 创建新的
2. **同一 Issue 只用一个分支** — 禁止 v1/v2/v3 命名
3. **创建分支前必须先同步 fork main 到 upstream main** — 避免冲突
4. **PR 文件隔离** — 只推送当前 PR 文件
5. **GitHub 主分支是 main** — 推送时使用 main，不是 master

---

## 代码风格

- 类型注解混合使用（部分方法有完整类型注解，部分没有）
- 文档字符串可选
- 方法内导入模块
- 简洁实现
- **匹配现有风格比追求完美更重要**

### 风格匹配流程
1. 阅读目标文件中周围的代码（20-50 行）
2. 注意哪些元素有类型注解
3. 注意 docstring 风格
4. 复制大多数代码使用的模式

---

## CI 经验

### 网络失败是基础设施问题，不是代码问题

**症状**:
- `Connection broken, IncompleteRead`
- `Failed to connect to github.com port 443`
- `Connection was reset`
- pip download timeout

**解决**: 重试 CI，不要修改代码

### CI 状态解读

| mergeable_state | 含义 |
|----------------|------|
| clean | 可以合并 |
| unstable | CI 失败或等待中 |
| dirty | 合并冲突 |
| blocked | 分支保护规则 |
| behind | 落后于 base 分支 |
| draft | 草稿 PR |

---

## GitHub API 限制

- Personal Access Token 可以写入 fork 仓库
- 默认无法在上游仓库创建 PR（403 Forbidden）
- 这是 GitHub 安全机制

**解决方法**:
1. 手动在 Web 创建 PR
2. 使用 GitHub CLI (gh)
3. 需要 OAuth App 或特殊权限

---

## Gemini Code Assist 反馈处理

### 常见反馈类型
- 使用 `ValueError` 代替 `assert` 进行输入验证
- PR 标题格式: `[Module][Type] Description`
- PR 描述必须包含: What/Why, User-facing change, How tested
- 不可达代码检测
- 代码改进建议（更好的模式、缓存）

### 处理流程
1. 通过 GitHub API 获取反馈
2. 仔细审查建议
3. 如果正确则应用
4. 推送新 commit
5. CI 自动重新运行

### 关键学习
- Gemini 通常能发现人类忽略的问题
- 验证检查位置很重要（PR #9149: 检查放在了不可达位置）
- 始终等待并处理 Gemini 反馈

---

## 版本处理

- `vllm.__version__` 可能包含额外后缀（如 `"0.20.1+cpu"`）
- 使用 `Version.public` 属性代替手动剥离后缀
- 这比 `vllm_version.split('+')[0]` 更健壮

---

## 贡献记录

| PR | Issue | 类型 | 状态 |
|----|-------|------|------|
| #9149 | #8975 | 死锁检查 | 已合并 |
| #9199 | #9167 | 版本后缀修复 | 已合并 |
| #9205 | - | ViT backend 接口 | 已合并 |
| #9216 | #4112 | shutdown 方法 | 已合并 |
| #9369 | #9358 | DeepSeek-V3.2 参数修复 | DCO 修复后完成 |
| #9383 | #9291 | MiniMax-M2.7 文档 | 已完成 |
| #9493 | #9454 | pip install 清理 | 已创建 |

---

*最后更新: 2026-06-05*
