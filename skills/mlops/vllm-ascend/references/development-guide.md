# vLLM-Ascend Development Guide

> 基于实际贡献经验总结的开发指南

---

## 环境配置

### Git 配置
```bash
git config --global user.name "nanxingMy"
git config --global user.email "1014662416@qq.com"
```

### 项目路径
- vLLM-Ascend: `C:/Users/HuaWei/vllm-ascend`
- Fork: `https://github.com/nanxingMy/vllm-ascend.git`
- 上游: `https://github.com/vllm-project/vllm-ascend.git`

### GitHub Token
- 需要 `repo` scope 推送 fork
- 需要 `public_repo` scope 更新 PR 标题/描述
- 读取公开仓库 PR 信息不需要认证

---

## 完整 PR 工作流

### Step 1: 分析 Issue
```bash
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/issues/NUMBER"
```

### Step 2: 同步并创建干净分支
```bash
# 同步 fork main 到 upstream main
git fetch origin
git checkout main
git merge origin/main
git push fork main

# 创建干净分支（必须从 main 创建）
git checkout -b fix-issue-NUMBER origin/main
```

### Step 3: 实现修复
- 只修改必要的文件
- 保留文件格式（使用 `patch` 或 `cat >>`）
- 添加单元测试
- 检查方法依赖是否存在

### Step 4: 验证最小变更
```bash
git diff --stat
# 应匹配预期：如 2 files, +43 lines
```

### Step 5: 提交
```bash
git add specific_files_only
git commit -s -m "[BugFix] Description

What this PR does / why we need it:
[解释问题和解决方案]

Fixes #NUMBER"
```

### Step 6: 推送
```bash
git push fork HEAD:fix-issue-NUMBER
```

### Step 7: 创建 PR
- 通过 GitHub Web UI 或 API
- 标题格式: `[Type][Module] Description`
- 描述包含: What/Why, User-facing change, How tested

### Step 8: 监控 CI
- 每 60-90 秒轮询
- 检测网络失败（重试，不修改代码）
- 等待所有检查通过

### Step 9: 处理 Gemini 反馈
- 通过 API 获取 bot 评论
- 审查建议
- 如果有效则应用
- 推送新 commit
- CI 自动重新运行

### Step 10: 等待合并
- 所有 CI 检查通过
- DCO 检查通过
- 等待维护者审查

---

## 测试要求

### 测试位置
- 单元测试: `tests/ut/`
- 集成测试: `tests/e2e/`

### 测试模式

**Platform 接口方法** (`tests/ut/test_platform.py`):
```python
def test_new_method(self):
    result = NPUPlatform.new_method()
    self.assertIsInstance(result, expected_type)
```

**Worker 方法** (`tests/ut/worker/test_worker_v1.py`):
```python
@patch("vllm_ascend.utils.adapt_patch")
def test_new_worker_method(self, mock_adapt_patch):
    from vllm_ascend.worker.worker import NPUWorker
    with patch.object(NPUWorker, "__init__", lambda x, **kwargs: None):
        worker = NPUWorker()
        # 测试逻辑
```

### 测试注意事项
- Mock 外部依赖使用 `@patch`
- 使用 `importlib.reload(platform)` 拾取 mock 值
- 异常匹配使用 `pytest.raises(ValueError, match=r"pattern")`
- 环境变量 mock 使用 `patch("module.envs.VAR", value, create=True)`

---

## 方法依赖检查

在实现调用其他对象方法的接口时：

1. **先检查方法是否存在**
```bash
grep -n "def method_name" target_file.py
# 如果没有输出，需要先添加该方法
```

2. **按正确顺序添加**
- 先在被调用对象上添加方法
- 然后在调用者上添加调用代码

3. **验证实现正确性**
- 参考 vLLM 的实现
- 确保所有必要的方法都已存在

---

## 分支管理

### ⚠️ 关键规则
- **始终从 main 创建分支**，不要从其他 PR 分支创建
- **一个 Issue 只用一个分支**，禁止 v1/v2/v3 命名
- **创建前同步 main**，避免冲突

### 如果已经从错误分支创建
```bash
# 选项 1: 创建干净分支 + cherry-pick
git checkout -b feature/new-pr-clean origin/main
git cherry-pick <commit-hash>

# 选项 2: 创建干净分支 + 重新应用修改
git checkout -b feature/new-pr-clean origin/main
# 手动重新应用修改

# 验证
git log --oneline origin/main..HEAD  # 应只显示你的 commits
git diff --stat origin/main...HEAD   # 应匹配预期变更
```

---

## 提交前检查清单

```bash
# 1. 检查分支来源
git log --oneline origin/main..HEAD
# 应只显示你的 commits，不包含其他 PR 的 commits

# 2. 检查 diff 大小
git diff --stat origin/main...HEAD
# 应匹配预期变更（如 2 files, +90 lines）

# 3. 检查测试存在
ls tests/ut/test_*.py

# 4. 运行测试
pytest tests/ut/test_xxx.py -v

# 5. 检查格式
ruff format --check vllm_ascend/ tests/

# 6. 检查 lint
ruff check vllm_ascend/ tests/
```

---

## 常见错误避免

1. ❌ 为格式化原因修改文件（行尾、空白）
2. ❌ 从另一个分支创建分支（包含所有历史）
3. ❌ 使用 `write_file` 完全覆盖（改变行尾）
4. ❌ 忽略 Gemini Code Assist 反馈
5. ❌ 将网络失败当作代码问题
6. ❌ 提交前不验证 `git diff --stat`
7. ❌ 为不同 PR 重用分支名
8. ❌ 在 PR 中包含不相关的变更
9. ❌ 因为 DCO 问题关闭 PR（应 rebase 修复）
10. ❌ 因为 Lint 问题关闭 PR（应修改代码修复）

---

*最后更新: 2026-06-05*
