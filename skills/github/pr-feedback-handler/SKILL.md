---
name: pr-feedback-handler
description: 监控 GitHub PR 反馈并根据反馈自动修复代码
trigger: 当需要检查 PR 状态、处理审查反馈、或自动修复 PR 问题时调用
---

# PR Feedback Handler

监控 GitHub PR 的审查反馈，自动分析问题并修复代码。

## 使用场景

- 检查 PR 是否有新的审查反馈
- 根据代码审查意见自动修改代码
- 处理 CI 失败
- 更新 PR 描述和标题

## 工作流程

### 1. 获取 PR 状态

```bash
# 获取 PR 基本信息
curl -s "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'State: {data[\"state\"]}')
print(f'Head SHA: {data[\"head\"][\"sha\"]}')
print(f'Updated: {data[\"updated_at\"]}')
print(f'Mergeable: {data.get(\"mergeable\", \"unknown\")}')
"

# 获取 reviews
curl -s "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"

# 获取行内评论
curl -s "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"

# 获取 Issue 评论
curl -s "https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
```

### 2. 分析反馈类型

| 反馈类型 | 处理方式 |
|---------|---------|
| 代码位置错误 | 移动代码到正确位置 |
| 逻辑错误 | 修改代码逻辑 |
| 缺少测试 | 添加单元测试 |
| 文档问题 | 更新文档/PR 描述 |
| CI 失败 | 检查日志并修复 |
| 建议优化 | 评估后决定是否采纳 |

### 3. 常见修复模式

#### 移动代码位置
```python
# 使用 patch 工具移动代码
patch(mode='replace', path='file.py', old_string='...', new_string='...')
```

#### 添加测试
```python
# 参考现有测试模式添加新测试
# 位置: tests/ut/test_xxx.py
```

#### 更新 PR 描述
```bash
# 使用 GitHub API 更新 PR
curl -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d '{"title": "...", "body": "..."}' \
  "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
```

### 4. 提交并推送

```bash
git add .
git commit -m "[Fix] 根据审查反馈修复 xxx 问题"
git push fork {branch}
```

## 当前监控的 PR

- **PR #9149**: vllm-project/vllm-ascend
  - Issue: #8975 (BalanceScheduler + RecomputeScheduler 死锁)
  - 分支: bugfix/scheduler-mutex-check-8975
  - 文件: vllm_ascend/platform.py, tests/ut/test_platform.py

## References

- **[ci-network-issues.md](references/ci-network-issues.md)** - CI 网络问题诊断：如何区分代码问题和环境/网络问题，典型错误模式，处理流程

## 输出格式

```
## PR 监控报告

### 基本信息
- PR: #{number}
- 状态: {state}
- 最新 commit: {sha}

### 新反馈 ({count})
1. [{type}] {summary}
   - 文件: {file}
   - 行号: {line}
   - 建议: {suggestion}

### 已处理
- [x] {已处理的反馈}

### 待处理
- [ ] {需要人工干预的问题}

### 下一步
- {建议操作}
```

## 注意事项

1. **不要重复处理** - 记录已处理的反馈，避免重复修改
2. **保持 commit 历史** - 使用 `--amend` 或新 commit，不要 force push 除非必要
3. **测试验证** - 修改后验证语法和逻辑
4. **等待审查** - 修复后等待新一轮审查，不要频繁推送
5. **API 速率限制** - 监控 `X-RateLimit-Remaining`，避免频繁调用 API
6. **DCO 签名** - 确保 commit 有 `Signed-off-by`，否则 DCO 检查会失败
7. **ruff format** - 不仅检查 ruff check，还要检查 ruff format

## 常见陷阱

### 1. 只检查 ruff check 忽略 ruff format

```bash
# ❌ 错误：只检查 lint
python -m ruff check file.py  # 通过

# ✅ 正确：同时检查格式
python -m ruff check file.py
python -m ruff format --check file.py  # 可能失败！
```

### 2. 忘记 Signed-off-by

```bash
# ❌ 错误：直接提交
git commit -m "fix: xxx"

# ✅ 正确：添加 sign-off
git commit -s -m "fix: xxx"
# 或
git commit --amend --signoff
```

### 3. 强制推送后 commit SHA 变化

强制推送会改变 commit SHA，导致：
- 旧的 CI 运行结果失效
- 需要等待新的 CI 运行
- PR 上的评论可能指向旧的代码位置

### 4. 网络问题导致推送失败

```bash
# 检查网络
curl -s --connect-timeout 10 https://api.github.com/

# 重试推送
git push fork {branch}
```

### 5. CI 安装步骤失败（网络问题，非代码问题）

当所有失败都在 "Install xxx" 步骤时，可能是网络问题而非代码问题：

**特征：**
- 错误信息包含 `IncompleteRead`、`Connection broken`、`ProtocolError`
- 失败发生在 pip/wget 下载阶段
- 多个任务在同一安装步骤失败

**典型错误：**
```
pip._vendor.urllib3.exceptions.ProtocolError: ('Connection broken: 
IncompleteRead(35766015 bytes read, 152685937 more expected)', 
IncompleteRead(35766015 bytes read, 152685937 more expected))
```

**处理方式：**
1. **确认不是代码问题**：本地检查语法 `python -m py_compile <file>`
2. **重新触发 CI**：
   - 在 GitHub PR 页面点击 "Re-run all jobs"
   - 或创建空提交：`git commit --allow-empty -m "[CI] Retry"`
3. **不要修改代码**：这是环境问题，修改代码无济于事

**判断流程：**
```python
# 如果所有失败步骤名称相同且包含 "Install"
failed_steps = get_failed_steps()
if len(failed_steps) == 1 and "Install" in list(failed_steps.keys())[0]:
    # 检查日志中是否有网络错误关键词
    if any(kw in log for kw in ["IncompleteRead", "Connection broken", "ProtocolError"]):
        print("网络问题，重新触发 CI")
    else:
        print("可能是依赖冲突或代码语法错误，检查安装日志")
```

### 5. JSON 解析错误

GitHub API 返回的 JSON 可能包含控制字符，需要清理：

```python
import re
clean_output = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw_output)
data = json.loads(clean_output)
```

## CI 失败模式分析

当多个 CI 任务失败时，分析失败模式可以快速定位根因：

### 失败模式分类

| 模式 | 特征 | 可能原因 | 优先检查 |
|------|------|---------|---------|
| **单一安装失败** | 所有失败都在安装步骤 | 依赖冲突、环境问题、代码语法错误 | 查看安装日志 |
| **单一测试失败** | 安装成功但测试失败 | 代码逻辑错误、测试环境问题 | 查看测试日志 |
| **随机失败** | 失败任务/步骤不一致 | 资源不足、网络抖动、时序问题 | 重试 CI |
| **平台特定失败** | 只在特定平台失败 | 平台兼容性问题、硬件限制 | 检查平台差异 |

### 快速诊断流程

```python
# 1. 获取所有失败任务的失败步骤
failed_jobs = [...]  # 从 check-runs API 获取
failed_steps = {}
for job in failed_jobs:
    job_detail = get_job_detail(job['id'])
    for step in job_detail['steps']:
        if step['conclusion'] == 'failure':
            step_name = step['name']
            failed_steps[step_name] = failed_steps.get(step_name, 0) + 1

# 2. 分析模式
if len(failed_steps) == 1:
    # 所有失败在同一步骤 -> 环境或依赖问题
    print(f"所有失败在: {list(failed_steps.keys())[0]}")
    print("优先检查: 依赖版本、环境配置、代码语法")
elif max(failed_steps.values()) / sum(failed_steps.values()) > 0.7:
    # 大部分失败在同一步骤 -> 该步骤有问题
    print(f"主要失败在: {max(failed_steps, key=failed_steps.get)}")
else:
    # 失败分散 -> 可能是随机问题
    print("失败分散，可能是资源或网络问题")
```

### 在浏览器中查看日志

当无法通过 API 获取日志（权限不足）时，打开浏览器：

```bash
# Windows
start "https://github.com/{owner}/{repo}/actions/runs/{run_id}"

# macOS
open "https://github.com/{owner}/{repo}/actions/runs/{run_id}"

# Linux
xdg-open "https://github.com/{owner}/{repo}/actions/runs/{run_id}"
```

## CI 状态检查 (无 gh CLI)

当 `gh` CLI 不可用时，使用 curl + GitHub REST API：

```bash
# 获取 PR 信息
curl -s "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

# 获取 commit 的 check runs
curl -s -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/{owner}/{repo}/commits/{sha}/check-runs"

# 获取 job 详情 (包含步骤状态)
curl -s "https://api.github.com/repos/{owner}/{repo}/actions/jobs/{job_id}"

# 获取 check run annotations (错误详情)
curl -s -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/{owner}/{repo}/check-runs/{check_id}/annotations"
```

### 分析 CI 失败步骤

```python
import re
import json

# 获取 job 详情
job_result = terminal(f"curl -s 'https://api.github.com/repos/{owner}/{repo}/actions/jobs/{job_id}'")

# 提取步骤状态
steps_pattern = r'"name":\s*"([^"]+)".*?"conclusion":\s*"([^"]*)"'
steps = re.findall(steps_pattern, job_result['output'], re.DOTALL)

for step_name, conclusion in steps:
    if conclusion == 'failure':
        print(f"❌ {step_name}")
```

## CI Lint 错误处理

### 获取 Lint 错误详情

```bash
# 获取 check run ID
CHECK_ID=$(curl -s "https://api.github.com/repos/{owner}/{repo}/commits/$SHA/check-runs" | \
  python3 -c "import sys,json; [print(r['id']) for r in json.load(sys.stdin).get('check_runs',[]) if r['name']=='lint / pre-commit']")

# 获取错误 annotations
curl -s "https://api.github.com/repos/{owner}/{repo}/check-runs/$CHECK_ID/annotations" | \
  python3 -c "import sys,json; [print(f\"{a['path']}:{a['start_line']}: {a['message']}\") for a in json.load(sys.stdin)]"
```

### 常见 Lint 错误修复

| 错误 | 修复方法 |
|------|---------|
| E501 Line too long | 将长行拆分为多行，使用括号续行 |
| F401 Import unused | 删除未使用的导入 |
| E502 Blank line | 检查行尾空白 |
| ruff format | 运行 `python -m ruff format <file>` 自动修复 |

### ruff format 检查失败

```bash
# 检查格式问题
python -m ruff format --check <file>

# 自动修复
python -m ruff format <file>
```

常见格式问题：
- docstring 末尾多余空格
- 函数调用参数换行格式
- 括号内多余空格

### E501 修复示例

```python
# 错误 (141 > 120)
pytest.raises(ValueError, match=r"VLLM_ASCEND_BALANCE_SCHEDULING.*recompute_scheduler_enable.*cannot be enabled simultaneously"),

# 修复 - 拆分为多行
pytest.raises(
    ValueError,
    match=r"VLLM_ASCEND_BALANCE_SCHEDULING.*recompute_scheduler_enable"
          r".*cannot be enabled simultaneously"),
```

## Git Push 失败时的替代方案

当 `git push` 因网络问题失败时，使用 GitHub API 推送文件：

```python
import base64
import json
import urllib.request
import ssl

# 读取文件
with open("path/to/file.py", "r", encoding="utf-8") as f:
    content = f.read()
content_base64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')

# 获取当前文件 SHA
req = urllib.request.Request(
    f"https://api.github.com/repos/{owner}/{repo}/contents/path/to/file.py?ref={branch}"
)
req.add_header("Authorization", f"token {token}")
resp = urllib.request.urlopen(req)
file_sha = json.loads(resp.read())["sha"]

# 更新文件
data = {
    "message": "commit message",
    "content": content_base64,
    "sha": file_sha,
    "branch": branch
}
req = urllib.request.Request(
    f"https://api.github.com/repos/{owner}/{repo}/contents/path/to/file.py",
    data=json.dumps(data).encode('utf-8'),
    method="PUT"
)
req.add_header("Authorization", f"token {token}")
resp = urllib.request.urlopen(req)
```

## API 速率限制处理

```bash
# 检查速率限制
curl -s -I "https://api.github.com/..." | grep "X-RateLimit"

# 输出:
# X-RateLimit-Limit: 60
# X-RateLimit-Remaining: 45
# X-RateLimit-Reset: 1778743695  # Unix timestamp
```

当 `X-RateLimit-Remaining: 0` 时，等待重置：

```python
import datetime
reset_time = 1778743695
wait_seconds = datetime.datetime.fromtimestamp(reset_time) - datetime.datetime.now()
print(f"等待 {wait_seconds.seconds} 秒")
```

## Cron Job 自动监控

创建定时任务自动监控 PR：

```bash
# 创建 cron job (每 10 分钟检查)
hermes cron create \
  --name "pr-monitor" \
  --schedule "every 10m" \
  --prompt "检查 PR 状态并处理反馈"
```

Cron job 会自动：
1. 检查 PR 状态和 CI 结果
2. 获取新的审查评论
3. 分析并执行修复
4. 推送修改

## Token 权限要求

更新 PR 标题/描述需要 Token 有 `public_repo` 或 `repo` scope。

```bash
# 检查当前 token 用户
curl -s -H "Authorization: token $TOKEN" "https://api.github.com/user"

# 更新 PR（使用 Issues API）
curl -X PATCH \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{"title": "...", "body": "..."}' \
  "https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}"
```

## Git Credential 管理 (Windows)

```bash
# 列出已存储的 GitHub credentials
git credential-manager github list

# 获取 credential
echo "protocol=https
host=github.com" | git credential-manager get

# 存储 credential
echo "protocol=https
host=github.com
username=<USER>
password=<TOKEN>" | git credential-manager store

# 删除 credential
echo "protocol=https
host=github.com
username=<USER>" | git credential-manager erase
```

## DCO (Developer Certificate of Origin) 检查

vLLM-Ascend 项目要求每个 commit 都有 `Signed-off-by` 签名。

### 检查 DCO 状态

```bash
# 检查 commit 是否有 sign-off
git log -1 --format=full

# 应该看到:
# Signed-off-by: Your Name <your@email.com>
```

### 添加 Signed-off-by

```bash
# 修改最后一个 commit 添加 sign-off
git commit --amend --signoff --no-edit

# 或者在提交时就加上
git commit -s -m "your message"
```

### DCO 检查失败处理

当 DCO 检查显示 `action_required` 时：

1. **检查当前 commit**:
   ```bash
   git log -1 --format="%B"
   ```

2. **添加 sign-off 并强制推送**:
   ```bash
   git commit --amend --signoff --no-edit
   git push fork {branch} --force
   ```

3. **注意**: 强制推送会改变 commit SHA，触发新的 CI 运行

### pre-commit 配置中的 signoff

vLLM-Ascend 的 `.pre-commit-config.yaml` 包含 `signoff-commit` hook，会自动添加 sign-off：

```yaml
- id: signoff-commit
  name: Sign-off Commit
  entry: bash
  args:
    - -c
    - |
      if ! grep -q "^Signed-off-by: $(git config user.name) <$(git config user.email)>" "$(git rev-parse --git-path COMMIT_EDITMSG)"; then
        printf "\nSigned-off-by: $(git config user.name) <$(git config user.email)>\n" >> "$(git rev-parse --git-path COMMIT_EDITMSG)"
      fi
  stages: [commit-msg]
```

但这只在本地 commit 时生效，如果 commit 已经推送，需要手动添加。

## mergeable_state 含义

| 状态 | 含义 |
|------|------|
| clean | 可以合并 |
| unstable | CI 失败或等待中 |
| dirty | 有冲突 |
| blocked | 被分支保护规则阻止 |
| behind | 落后于 base 分支 |
| draft | 草稿状态 |

## 检查 Review 状态

```bash
# 获取请求的审查者
curl -s "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/requested_reviewers"

# 分析 review 状态
curl -s "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews" | python3 -c "
import sys, json
reviews = json.load(sys.stdin)
states = {}
for r in reviews:
    state = r.get('state', 'UNKNOWN')
    states[state] = states.get(state, 0) + 1
print(f'状态统计: {states}')
# APPROVED: 可合并
# CHANGES_REQUESTED: 需要修改
# COMMENTED: 仅评论，可能需要 APPROVED
"
```
