# 开发指南

## 🚀 开发流程

### 完整流程

```
1. 选择 Issue
   ↓
2. 分析问题
   ↓
3. 检查继承关系
   ↓
4. 实现修复
   ↓
5. 编写测试
   ↓
6. 格式化代码
   ↓
7. 提交 PR
   ↓
8. 处理反馈
   ↓
9. 监控 CI
```

## 1️⃣ 选择 Issue

### 推荐顺序

1. **Good First Issue**
   - 标签：`good first issue`
   - 难度：⭐
   - 适合：新手

2. **Help Wanted**
   - 标签：`help wanted`
   - 难度：⭐⭐
   - 适合：有一定经验

3. **Bug Fix**
   - 标签：`bug`
   - 难度：⭐⭐⭐
   - 适合：理解代码后

4. **Feature**
   - 标签：`feature`
   - 难度：⭐⭐⭐⭐
   - 适合：有经验后

### 避免的 Issue 类型

- ❌ 复杂的架构问题（内存分配、分布式通信）
- ❌ 需要深入理解硬件的 Issue
- ❌ 没有明确目标的 Issue
- ❌ 需要大量依赖的 Issue

## 2️⃣ 分析问题

### 检查清单

- [ ] 理解 Issue 的描述
- [ ] 查看相关代码
- [ ] 找到问题根源
- [ ] 确定修复方案
- [ ] 检查是否有类似 Issue

### 分析步骤

```bash
# 1. 查看相关代码
grep -r "关键词" vllm_ascend/

# 2. 查看相关 Issue
# 在 GitHub 上搜索类似 Issue

# 3. 查看相关 PR
# 看看是否有人已经尝试修复

# 4. 查看测试
grep -r "关键词" tests/
```

## 3️⃣ 检查继承关系

### ⚠️ 最重要的一步

**添加新接口前必须检查**：

```bash
# 检查 Platform 基类
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/platforms/interface.py" | grep "def <method_name>"

# 检查 NPUPlatform 是否已有
grep -n "def <method_name>" vllm_ascend/platform.py
```

### 判断是否需要实现

**需要实现**：
- ✅ 基类没有该方法
- ✅ NPU 需要不同的逻辑
- ✅ 有实际意义

**不需要实现**：
- ❌ 基类已有且逻辑相同
- ❌ 只是重复实现
- ❌ 没有实际意义

## 4️⃣ 实现修复

### 分支管理

```bash
# 1. 从 main 创建新分支
git checkout main
git pull origin main
git checkout -b feature/fix-issue-XXX

# 2. 避免从其他分支创建
# ❌ 错误：git checkout -b feature/new from feature/old
```

### 代码风格

```python
# ✅ 匹配现有风格
def my_function(self, arg1: int, arg2: str) -> None:
    """简短的文档字符串"""
    # 方法内导入
    from vllm import something
    
    # 简洁实现
    result = self._helper(arg1, arg2)
    return result

# ❌ 不要过度格式化
# ❌ 不要改变不相关的代码
# ❌ 不要添加不必要的类型注解
```

### 实现原则

- ✅ 最小化修改
- ✅ 只修改必要的代码
- ✅ 匹配现有风格
- ✅ 添加必要的注释
- ❌ 不要修改不相关的代码
- ❌ 不要过度优化

## 5️⃣ 编写测试

### 测试类型

```python
# 单元测试
class TestMyFeature(unittest.TestCase):
    def test_normal_case(self):
        # 测试正常情况
        pass
    
    def test_edge_case(self):
        # 测试边界情况
        pass
    
    def test_error_case(self):
        # 测试错误情况
        with self.assertRaises(ValueError):
            my_function(invalid_input)
```

### 测试原则

- ✅ 测试正常情况
- ✅ 测试边界情况
- ✅ 测试错误情况
- ✅ 使用 mock 隔离依赖
- ❌ 不要依赖外部资源
- ❌ 不要有随机性

### 运行测试

```bash
# 运行单个测试
pytest tests/ut/test_file.py::TestClass::test_method -v

# 运行所有测试
pytest tests/ut/ -v
```

## 6️⃣ 格式化代码

### 使用 ruff

```bash
# 格式化代码
ruff format .

# 检查代码风格
ruff check .

# 自动修复
ruff check . --fix
```

### 检查修改

```bash
# 查看修改
git diff

# 确认只修改了必要的文件
git diff --stat
```

## 7️⃣ 提交 PR

### 提交信息格式

```
[Module][Type] Brief description

What this PR does / why we need it:
- 详细说明

Fixes #XXX

Signed-off-by: Your Name <email@example.com>
```

### 示例

```
[Worker][Feature] Add shutdown method to NPUWorker

What this PR does / why we need it:
- Add shutdown() method to NPUWorker
- Release NPU resources properly
- Follow vLLM gpu_worker implementation

Fixes #4112

Signed-off-by: nanxing <1014662416@qq.com>
```

### 提交步骤

```bash
# 1. 添加文件
git add <files>

# 2. 提交
git commit -s -m "..."

# 3. 推送
git push fork HEAD:feature/branch-name

# 4. 创建 PR
# 在 GitHub 上创建 Pull Request
```

## 8️⃣ 处理反馈

### Gemini Code Assist 反馈

**常见反馈类型**：

1. **代码风格**
   - 使用 ValueError 而不是 assert
   - 添加类型注解
   - 改进文档字符串

2. **逻辑问题**
   - 检查边界情况
   - 避免冗余代码
   - 优化性能

3. **PR 格式**
   - 标题格式
   - 描述格式
   - 测试覆盖

### 处理步骤

```bash
# 1. 根据反馈修改代码
# 2. 格式化
ruff format .

# 3. 提交
git add .
git commit -s -m "[Refactor] Improve based on Gemini feedback"

# 4. 推送
git push fork HEAD:feature/branch-name
```

## 9️⃣ 监控 CI

### CI 类型

```
CI 流程：
├─ Lint 检查
│  ├─ ruff format
│  ├─ ruff check
│  └─ mypy
│
├─ 单元测试
│  └─ pytest tests/ut/
│
└─ 端到端测试
   ├─ e2e-light (轻量级)
   └─ e2e-full (完整)
```

### 常见 CI 问题

#### 1. 网络问题

**症状**：
```
ProtocolError: ('Connection broken: IncompleteRead(...)')
```

**解决**：
- 重试 CI
- 不是代码问题

#### 2. 格式问题

**症状**：
```
ruff format check failed
```

**解决**：
```bash
ruff format .
git add .
git commit -m "[Style] Fix ruff formatting"
```

#### 3. 测试失败

**症状**：
```
pytest failed
```

**解决**：
- 查看错误日志
- 修复测试
- 本地验证

### 监控方法

```bash
# 查看最新提交
git log --oneline -1

# 查看 CI 状态
# 在 GitHub PR 页面查看

# 或使用 API
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/commits/<sha>/check-runs"
```

## 📋 检查清单

### 提交 PR 前

- [ ] 从 main 创建新分支
- [ ] 检查继承关系
- [ ] 实现正确
- [ ] 添加测试
- [ ] ruff format
- [ ] 本地测试通过
- [ ] 提交信息正确
- [ ] Signed-off-by

### PR 创建后

- [ ] 等待 CI 运行
- [ ] 处理 Gemini 反馈
- [ ] 监控 CI 状态
- [ ] 回复评论

## 🎯 最佳实践

### DO ✅

- 从 main 创建干净分支
- 最小化修改
- 添加测试
- 匹配现有风格
- 处理反馈
- 监控 CI

### DON'T ❌

- 从其他分支创建
- 修改不相关代码
- 没有测试就提交
- 改变代码风格
- 忽略反馈
- 不看日志就修改
