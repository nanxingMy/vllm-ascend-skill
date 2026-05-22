# CI 网络问题诊断

当 CI 失败时，如何区分代码问题和环境/网络问题。

## 网络问题特征

### 典型错误模式

```
pip._vendor.urllib3.exceptions.ProtocolError: ('Connection broken: 
IncompleteRead(35766015 bytes read, 152685937 more expected)', 
IncompleteRead(35766015 bytes read, 152685937 more expected))
```

**关键指标：**
- 错误类型：`ProtocolError`, `IncompleteRead`, `Connection broken`
- 发生位置：pip/wget/curl 下载阶段
- 上下文：正在安装依赖包

### 失败模式分析

当多个 CI 任务失败时，分析失败步骤：

| 模式 | 特征 | 原因 | 处理 |
|------|------|------|------|
| **全部安装失败** | 所有失败都在 "Install xxx" 步骤 | 网络问题或依赖冲突 | 检查日志关键词 |
| **同一安装步骤** | 失败步骤名称相同 | 可能是代码语法错误 | 本地验证语法 |
| **随机失败** | 失败步骤不一致 | 资源/网络抖动 | 重试 CI |
| **测试失败** | 安装成功但测试失败 | 代码逻辑问题 | 分析测试日志 |

## 诊断流程

### 1. 获取失败任务列表

```bash
curl -s "https://api.github.com/repos/{owner}/{repo}/commits/{sha}/check-runs" | python -c "
import sys, json
d = json.load(sys.stdin)
failed = [r for r in d.get('check_runs', []) if r.get('conclusion') == 'failure']
print(f'失败任务数: {len(failed)}')
for r in failed:
    print(f'  - {r.get(\"name\")}')
"
```

### 2. 获取失败步骤

```bash
curl -s "https://api.github.com/repos/{owner}/{repo}/actions/jobs/{job_id}" | python -c "
import sys, json
d = json.load(sys.stdin)
for step in d.get('steps', []):
    if step.get('conclusion') == 'failure':
        print(f'失败步骤: {step.get(\"name\")}')
"
```

### 3. 判断是否网络问题

```python
# 如果所有失败都在安装步骤
failed_steps = [...]  # 从 API 获取
if all("Install" in s for s in failed_steps):
    # 检查日志关键词
    network_keywords = ["IncompleteRead", "Connection broken", "ProtocolError", 
                        "timeout", "timed out", "network"]
    if any(kw in log for kw in network_keywords):
        print("网络问题，重新触发 CI")
    else:
        print("可能是代码问题，检查语法")
```

### 4. 本地验证代码

```bash
# 语法检查
python -m py_compile vllm_ascend/platform.py
python -m py_compile tests/ut/test_platform.py

# ruff 检查
ruff check vllm_ascend/
ruff format --check vllm_ascend/
```

## 处理方案

### 网络问题（非代码问题）

**不要修改代码！** 网络问题重试即可：

**方法 1：在 GitHub 网页上**
1. 打开 PR 页面
2. 点击 "Checks" 标签
3. 点击 "Re-run all jobs" 按钮

**方法 2：创建空提交**
```bash
git commit --allow-empty -m "[CI] Retry after network issue"
git push fork HEAD:<branch>
```

**方法 3：等待自动重试**
- CI 系统通常会自动重试失败的任务
- 等待几分钟观察是否自动恢复

### 代码问题

如果本地验证失败，说明代码有问题：

```bash
# 修复代码
# ...

# 提交修复
git add <files>
git commit -s -m "[Fix] Fix xxx issue"
git push fork HEAD:<branch>
```

## 案例：PR #9149 CI 网络失败

### 现象

3 个 CI 任务失败：
- `smart test (v0.20.1) / smart-ut (a2 x1)`
- `e2e-light (v0.20.1) / singlecard-light (0)`
- `e2e-light (c7aa186d...) / singlecard-light (0)`

### 分析

所有失败都在 "Install vllm-project/vllm-ascend" 步骤。

错误日志：
```
pip._vendor.urllib3.exceptions.ProtocolError: ('Connection broken: 
IncompleteRead(35766015 bytes read, 152685937 more expected)', ...)
```

正在下载 `mypy==1.11.1` 时连接中断：
- 已下载：35.7 MB
- 期望大小：152.7 MB
- 缺少：117 MB

### 结论

**网络问题，非代码问题。**

本地验证：
```bash
python -m py_compile vllm_ascend/platform.py  # 通过
python -m py_compile tests/ut/test_platform.py  # 通过
```

### 处理

重新触发 CI：
```bash
# 创建空提交
git commit --allow-empty -m "[CI] Retry after network issue"
git push fork HEAD:bugfix/scheduler-mutex-check-8975
```

结果：CI 重新运行，全部通过。

## 预防措施

### 1. 提交前本地验证

```bash
# 语法检查
python -m py_compile <modified_files>

# Lint 检查
ruff check vllm_ascend/
ruff format --check vllm_ascend/

# 本地测试（如有环境）
pytest tests/ut/ -v
```

### 2. 监控 CI 状态

设置自动监控：
```bash
# 创建 cron job
hermes cron create \
  --name "pr-monitor" \
  --schedule "every 10m" \
  --prompt "检查 PR 状态"
```

### 3. 快速响应

- 网络问题：立即重试
- 代码问题：快速修复并推送
- 不确定：先本地验证，再决定

## 常见错误关键词

| 关键词 | 含义 | 是否代码问题 |
|--------|------|-------------|
| `IncompleteRead` | 下载不完整 | 否 |
| `Connection broken` | 连接中断 | 否 |
| `ProtocolError` | 协议错误 | 否 |
| `timeout` / `timed out` | 超时 | 否 |
| `SyntaxError` | 语法错误 | 是 |
| `ImportError` | 导入错误 | 可能 |
| `AssertionError` | 断言失败 | 是 |
| `ModuleNotFoundError` | 模块未找到 | 可能 |

**"可能"** 的情况需要进一步分析：
- `ImportError` / `ModuleNotFoundError` 可能是：
  - 代码中导入了不存在的模块（代码问题）
  - 依赖未安装（环境问题）
