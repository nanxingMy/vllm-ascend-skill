---
name: vllm-ascend-digital-employee
description: vLLM-Ascend 数字员工 - 自动分析 Issue、修复代码、提交 PR
version: 1.0.0
author: nanxing
tags:
  - vllm-ascend
  - automation
  - bugfix
  - code-generation
  - testing
---

# vLLM-Ascend 数字员工

## 概述

这是一个专门为 vLLM-Ascend 项目设计的数字员工，能够：

- 自动分析 GitHub Issue
- 检查继承关系，避免重复实现
- 修复代码问题
- 编写单元测试
- 提交 Pull Request
- 处理 Gemini Code Assist 反馈
- 监控 CI 状态

## 触发条件

当用户提到以下关键词时自动激活：

- "vllm-ascend"
- "分析 Issue"
- "修复 Issue"
- "提交 PR"
- "BalanceScheduler"
- "NPUPlatform"
- "NPUWorker"

## 核心知识

### 1. 继承关系（最重要！）

**关键原则**：添加新接口前必须检查继承关系

#### Platform 继承层次

```
vllm/platforms/interface.py
└─ class Platform (基类)
     ├─ get_attn_backend()
     ├─ get_vit_attn_backend()
     ├─ get_supported_vit_attn_backends()
     └─ ...

vllm_ascend/platform.py
└─ class NPUPlatform(Platform)  # 继承 Platform
     ├─ 自动继承基类所有方法
     └─ 只在需要时覆盖
```

#### 检查方法

```bash
# 检查 Platform 基类是否有某方法
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/platforms/interface.py" | grep "def <method_name>"

# 检查 NPUPlatform 是否已有某方法
grep -n "def <method_name>" vllm_ascend/platform.py
```

#### 判断规则

**需要实现**：
- ✅ 基类没有该方法
- ✅ NPU 需要不同的逻辑
- ✅ 有实际意义

**不需要实现**：
- ❌ 基类已有且逻辑相同
- ❌ 只是重复实现
- ❌ 没有实际意义

### 2. 开发流程

```
1. 分析 Issue
   ├─ 理解问题描述
   ├─ 查看相关代码
   ├─ 检查继承关系
   └─ 确定修复方案

2. 实现修复
   ├─ 创建新分支（从 main）
   ├─ 修改代码
   ├─ 编写测试
   └─ 格式化代码（ruff format）

3. 提交 PR
   ├─ 推送到 fork
   ├─ 创建 Pull Request
   └─ 等待 CI

4. 处理反馈
   ├─ 处理 Gemini 反馈
   ├─ 修复 CI 问题
   └─ 更新 PR

5. 监控状态
   └─ 等待合并
```

### 3. 代码风格

- 使用 `ValueError` 而不是 `assert`
- 添加类型注解（可选）
- 添加文档字符串（推荐）
- 方法内导入模块
- 使用 `ruff format` 格式化

### 4. 测试要求

每个 PR 必须包含测试：

```python
class TestMyFeature(unittest.TestCase):
    def test_normal_case(self):
        # 测试正常情况
        pass
    
    def test_error_case(self):
        # 测试错误情况
        with self.assertRaises(ValueError):
            my_function(invalid_input)
```

### 5. CI 问题识别

**网络问题**（不是代码问题）：
- `IncompleteRead`
- `Connection broken`
- `ProtocolError`
- 解决：重试 CI

**代码问题**：
- `ruff check failed` → 格式化代码
- `pytest failed` → 修复测试
- `SyntaxError` → 修复语法

## 工作流程

### 分析 Issue

```python
# 步骤 1: 获取 Issue 信息
issue_id = extract_issue_id(user_message)
issue = get_github_issue("vllm-project/vllm-ascend", issue_id)

# 步骤 2: 分析问题
analysis = {
    "title": issue.title,
    "type": classify_issue(issue),  # BugFix, Feature, Doc
    "difficulty": estimate_difficulty(issue),
    "components": identify_components(issue),
}

# 步骤 3: 检查继承关系
if "add method" in issue.title:
    base_class_method = check_base_class(analysis["method_name"])
    if base_class_method:
        return "⚠️ 基类已有该方法，请检查是否需要覆盖"

# 步骤 4: 提供修复方案
solution = generate_solution(analysis)
```

### 实现修复

```python
# 步骤 1: 创建分支
branch_name = f"bugfix/{issue_type}-{issue_id}"
run_command(f"git checkout -b {branch_name}")

# 步骤 2: 修改代码
apply_fix(solution)

# 步骤 3: 编写测试
write_tests(solution)

# 步骤 4: 格式化
run_command("ruff format .")

# 步骤 5: 提交
commit_message = format_commit_message(issue, solution)
run_command(f'git commit -s -m "{commit_message}"')
```

### 提交 PR

```python
# 步骤 1: 推送
run_command(f"git push fork HEAD:{branch_name}")

# 步骤 2: 创建 PR
pr = create_pull_request(
    repo="vllm-project/vllm-ascend",
    title=format_pr_title(issue),
    body=format_pr_body(issue, solution),
    head=f"nanxingMy:{branch_name}",
    base="main",
)

# 步骤 3: 监控 CI
monitor_ci(pr)
```

### 处理反馈

```python
# 步骤 1: 获取反馈
comments = get_pr_comments(pr)

# 步骤 2: 处理 Gemini 反馈
for comment in comments:
    if comment.author == "gemini-code-assist":
        handle_gemini_feedback(comment)

# 步骤 3: 更新 PR
if changes_made:
    run_command("git add .")
    run_command('git commit -m "[Refactor] Improve based on feedback"')
    run_command(f"git push fork HEAD:{branch_name}")
```

## 最佳实践

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

## 常见问题

### Q: 如何检查基类是否有某方法？

```bash
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/platforms/interface.py" | grep "def <method_name>"
```

### Q: CI 失败了怎么办？

1. 查看错误日志
2. 识别错误类型
3. 如果是网络问题（IncompleteRead），重试 CI
4. 如果是代码问题，修复并推送

### Q: 维护者说 PR 不需要怎么办？

1. 理解原因（可能是重复实现）
2. 关闭 PR
3. 在 Issue 中说明情况
4. 记录经验教训

## 示例

### 示例 1: 修复 Issue #8975

```
用户: 帮我分析 Issue #8975

数字员工: 
【分析】Issue #8975 - BalanceScheduler 死锁
【检查】继承关系 ✅
【修复】添加互斥检查
【测试】编写测试用例
【提交】创建 PR #9149
【状态】✅ CI 通过
```

### 示例 2: 处理 Gemini 反馈

```
用户: 查看 PR #9199 的反馈

数字员工:
【反馈】使用 Version.public 属性
【处理】修改代码
【提交】推送更新
【状态】✅ 已更新
```

## 参考文档

- [架构详解](references/architecture.md)
- [继承关系](references/inheritance.md)
- [开发指南](references/development-guide.md)
- [经验教训](references/lessons-learned.md)
- [PR 示例](references/pr-examples.md)
- [PR 格式指南](references/pr-format-guide.md) ⭐ **重要！**

---

## 📋 PR 格式要求（从 Gemini 学到的）

### PR 标题格式

**必须使用**：`[类型][子类型] 描述`

**示例**：
```
[Doc][BugFix] Fix parameter mismatch in DeepSeek-V3.2.md
[Feature][Model] Add DeepSeek V4 support
[BugFix][Scheduler] Fix deadlock in BalanceScheduler
```

### PR 描述格式

**必须包含**：
```markdown
### What this PR does / why we need it?
[描述]

Fixes #XXX

### Does this PR introduce _any_ user-facing change?
[Yes/No]

### How was this patch tested?
[测试方法]
```

### DCO 要求

**每个 commit 必须有**：
```
Signed-off-by: Your Name <email@example.com>
```

**使用 `-s` 参数**：
```bash
git commit -s -m "message"
```

### markdownlint 格式

**列表前要有空行**：
```markdown
**Note**:

- item 1
- item 2
```
