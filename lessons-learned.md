# 经验教训

## 📝 踩坑记录

### 1. Issue #3489 - 重复实现基类方法

**错误**：没有检查继承关系就实现方法

**问题**：
- Platform 基类已有 `get_vit_attn_backend` 方法
- 我的实现与基类完全相同
- NPUPlatform 会自动继承基类的方法
- 重复实现没有任何意义

**教训**：
- ⚠️ **添加方法前必须检查基类是否已有**
- ⚠️ **理解继承关系，避免重复实现**

**正确做法**：
```bash
# 检查基类
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/platforms/interface.py" | grep "def get_vit_attn_backend"

# 如果基类已有，判断是否需要覆盖
# 如果不需要覆盖，关闭 Issue
```

---

### 2. PR #9149 - CI 网络问题

**错误**：看到 CI 失败就认为代码有问题

**问题**：
- CI 失败是因为 pip 下载时网络中断
- 错误信息：`IncompleteRead`, `Connection broken`
- 这是基础设施问题，不是代码问题

**教训**：
- ⚠️ **CI 失败不一定是代码问题**
- ⚠️ **查看日志再判断**

**正确做法**：
```
1. 查看错误日志
2. 识别网络问题关键词：IncompleteRead, Connection broken, ProtocolError
3. 重试 CI
```

---

### 3. PR #9205 - 多次 merge main

**错误**：多次 merge main 分支导致提交历史混乱

**问题**：
- PR 有 5 个 merge commit
- 提交历史不清晰
- 可能引入依赖冲突

**教训**：
- ⚠️ **避免多次 merge main**
- ⚠️ **使用 rebase 保持历史干净**

**正确做法**：
```bash
# 方式 1: 创建干净分支
git checkout main
git checkout -b feature/new-branch
git cherry-pick <commits>

# 方式 2: 使用 rebase
git checkout feature/branch
git rebase main
```

---

### 4. 忘记添加测试

**错误**：没有添加单元测试就提交 PR

**问题**：
- PR 应该包含测试
- 没有测试无法验证修复
- 维护者会要求添加测试

**教训**：
- ⚠️ **每个 PR 都应该有测试**
- ⚠️ **测试正常、边界、错误情况**

**正确做法**：
```python
class TestMyFeature(unittest.TestCase):
    def test_normal_case(self):
        # 正常情况
        pass
    
    def test_error_case(self):
        # 错误情况
        with self.assertRaises(ValueError):
            my_function(invalid_input)
```

---

### 5. 格式化问题

**错误**：忘记运行 ruff format

**问题**：
- CI 的 lint 检查失败
- 代码格式不符合要求

**教训**：
- ⚠️ **提交前必须运行 ruff format**
- ⚠️ **本地验证格式**

**正确做法**：
```bash
# 格式化
ruff format .

# 检查
ruff check .

# 提交
git add .
git commit -m "[Style] Fix ruff formatting"
```

---

### 6. 修改不相关代码

**错误**：修改了不相关的代码

**问题**：
- PR 应该只修改必要的代码
- 修改不相关代码会增加 review 难度
- 可能引入新问题

**教训**：
- ⚠️ **最小化修改**
- ⚠️ **只修改必要的代码**

**正确做法**：
```bash
# 查看修改
git diff --stat

# 确认只修改了必要的文件
# 例如：2 files changed, 35 insertions(+)
```

---

## ✅ 成功经验

### 1. Issue #8975 - BalanceScheduler 死锁

**成功因素**：
- ✅ 问题分析清晰
- ✅ 有明确的修复目标
- ✅ 添加了单元测试
- ✅ 处理了 Gemini 反馈
- ✅ 监控了 CI 状态

**关键步骤**：
1. 理解问题：两个 scheduler 互斥检查缺失
2. 定位代码：找到需要添加检查的位置
3. 实现修复：添加互斥检查
4. 添加测试：验证检查生效
5. 处理反馈：根据 Gemini 改进

---

### 2. Issue #9167 - 版本后缀比较

**成功因素**：
- ✅ 问题定位准确
- ✅ 使用了正确的方法（Version.public）
- ✅ 添加了完整的测试
- ✅ 根据 Gemini 反馈改进

**关键学习**：
- 使用 `Version.public` 属性处理版本后缀
- 添加多种测试用例覆盖不同情况

---

### 3. Issue #4112 - shutdown 方法

**成功因素**：
- ✅ 检查了基类没有该方法
- ✅ 实现了 NPU 特定的逻辑
- ✅ 添加了完整的测试
- ✅ 处理了 Gemini 反馈

**关键学习**：
- 基类没有 shutdown 方法，需要实现
- NPU 需要特定的清理逻辑（torch.npu.synchronize）
- 检查属性存在性避免 AttributeError

---

## 🎯 核心原则

### 开发原则

1. **继承关系是第一位的**
   - 添加方法前检查基类
   - 理解是否需要覆盖
   - 避免重复实现

2. **最小化修改**
   - 只修改必要的代码
   - 不修改不相关代码
   - 匹配现有风格

3. **测试很重要**
   - 每个 PR 都要有测试
   - 测试多种情况
   - 本地验证

4. **格式化不能忘**
   - 提交前运行 ruff format
   - 检查代码风格
   - 本地验证

5. **CI 失败要看日志**
   - 不一定是代码问题
   - 可能是网络问题
   - 查看日志再判断

### Git 原则

1. **从 main 创建干净分支**
   - 不从其他分支创建
   - 避免 merge commit
   - 保持历史清晰

2. **提交信息要规范**
   - 格式：[Module][Type] Description
   - 包含 Signed-off-by
   - 说明修复的 Issue

3. **避免多次 merge**
   - 使用 rebase 代替 merge
   - 保持提交历史线性
   - 减少冲突

---

## 📊 问题分类

### 代码问题

- ❌ 重复实现基类方法
- ❌ 逻辑错误
- ❌ 边界情况未处理
- ❌ 缺少错误处理

### 流程问题

- ❌ 没有添加测试
- ❌ 没有格式化
- ❌ 提交信息不规范
- ❌ 多次 merge main

### 理解问题

- ❌ 不理解继承关系
- ❌ 不理解问题本质
- ❌ 不理解代码逻辑

---

## 🔍 问题排查

### CI 失败

**步骤**：
1. 查看错误日志
2. 识别错误类型
3. 判断是否代码问题
4. 相应处理

**常见错误类型**：

| 错误类型 | 症状 | 原因 | 解决 |
|---------|------|------|------|
| 网络问题 | IncompleteRead | pip 下载失败 | 重试 CI |
| 格式问题 | ruff check failed | 代码格式不对 | ruff format |
| 测试失败 | pytest failed | 测试未通过 | 修复代码 |
| 语法错误 | SyntaxError | 代码语法错误 | 修复语法 |

### 代码问题

**步骤**：
1. 理解错误信息
2. 定位问题代码
3. 分析问题原因
4. 实现修复
5. 添加测试

---

## 💡 最佳实践总结

### DO ✅

- 检查继承关系
- 最小化修改
- 添加测试
- 格式化代码
- 查看日志
- 处理反馈
- 监控 CI

### DON'T ❌

- 重复实现基类方法
- 修改不相关代码
- 没有测试就提交
- 忘记格式化
- 不看日志就修改
- 忽略反馈
- 多次 merge main

---

## 🎓 学习建议

### 学习顺序

1. **理解架构**
   - 阅读架构文档
   - 理解继承关系
   - 理解工作流程

2. **学习代码风格**
   - 阅读现有代码
   - 理解格式规范
   - 使用 ruff

3. **实践**
   - 修复简单 Issue
   - 添加测试
   - 提交 PR

4. **总结**
   - 记录经验教训
   - 避免重复错误
   - 持续改进

---

## 📝 记住

**经验是最好的老师，但教训更深刻！**

- ✅ 从错误中学习
- ✅ 记录经验教训
- ✅ 避免重复错误
- ✅ 持续改进
