# 阶段 1: Issue 发现与分析

## 🎯 目标

发现并分析 Issue，确认修复方案。

---

## 📋 步骤

### 1.1 发现 Issue

#### 方式 1: 浏览 Issues 列表
```bash
# 查看所有 open issues
gh issue list --repo vllm-project/vllm-ascend --state open

# 查看特定标签的 issues
gh issue list --repo vllm-project/vllm-ascend --label "bug"
gh issue list --repo vllm-project/vllm-ascend --label "good first issue"
```

#### 方式 2: 查看 Issue 详情
```bash
# 查看特定 issue
gh issue view <issue-number> --repo vllm-project/vllm-ascend

# 在浏览器中打开
gh issue view <issue-number> --repo vllm-project/vllm-ascend --web
```

#### 方式 3: 搜索 Issue
```bash
# 搜索关键词
gh issue list --repo vllm-project/vllm-ascend --search "deadlock"
gh issue list --repo vllm-project/vllm-ascend --search "scheduler"
```

---

### 1.2 分析 Issue

#### 分析内容
1. **Issue 标题和描述**
   - 问题是什么？
   - 影响范围？
   - 复现步骤？

2. **Issue 标签**
   - `bug`: Bug 修复
   - `enhancement`: 功能增强
   - `documentation`: 文档更新
   - `good first issue`: 适合新手

3. **Issue 评论**
   - 维护者的反馈
   - 其他用户的讨论
   - 已有的解决方案

4. **相关代码**
   - 定位问题代码位置
   - 理解代码逻辑
   - 确认修改范围

#### 分析工具
```bash
# 查看 Issue 的所有评论
gh api repos/vllm-project/vllm-ascend/issues/<issue-number>/comments

# 查看相关 PR
gh pr list --repo vllm-project/vllm-ascend --search "<issue-number>"
```

---

### 1.3 确认修复方案

#### 确认内容
1. **修复方案**
   - 需要修改哪些文件？
   - 需要添加哪些功能？
   - 需要删除哪些代码？

2. **测试方案**
   - 如何验证修复？
   - 需要添加哪些测试？
   - 测试覆盖范围？

3. **影响范围**
   - 是否影响其他功能？
   - 是否需要更新文档？
   - 是否有破坏性变更？

#### 记录方案
```markdown
## Issue #<number> 修复方案

### 问题描述
[简述问题]

### 修复方案
1. 修改文件: [文件列表]
2. 添加功能: [功能描述]
3. 删除代码: [代码描述]

### 测试方案
1. 单元测试: [测试描述]
2. 集成测试: [测试描述]

### 影响范围
- [影响描述]
```

---

## 🔍 案例分析

### 案例: Issue #8975

#### Issue 信息
```
标题: BalanceScheduler + RecomputeScheduler 导致 AlltoAll 死锁
标签: bug
状态: open
```

#### 问题分析
1. **问题**: 
   - BalanceScheduler 和 RecomputeScheduler 同时启用会导致死锁
   - 在 PD disaggregation mode with multi-DP MoE 场景下

2. **原因**:
   - MoE communication type mismatch across DP ranks
   - Some perform All2AllV, others MC2

3. **影响范围**:
   - PD disaggregation mode
   - Multi-DP MoE
   - BalanceScheduler 和 RecomputeScheduler

#### 修复方案
1. **修改文件**:
   - `vllm_ascend/platform.py`: 添加互斥检查
   - `tests/ut/test_platform.py`: 添加单元测试

2. **修复逻辑**:
   ```python
   # 添加互斥检查
   if ascend_config.enable_balance_scheduling and ascend_config.recompute_scheduler_enable:
       raise ValueError("cannot be enabled simultaneously")
   ```

3. **测试方案**:
   - 测试同时启用会抛出异常
   - 测试单独启用不抛出异常

---

## ✅ 检查清单

### Issue 分析完成检查
- [ ] 已阅读 Issue 描述
- [ ] 已查看 Issue 评论
- [ ] 已定位问题代码
- [ ] 已确认修复方案
- [ ] 已确认测试方案
- [ ] 已记录修复方案

### 准备进入下一阶段
- [ ] 知道需要修改哪些文件
- [ ] 知道如何测试修复
- [ ] 知道影响范围

---

## 📝 输出

完成本阶段后，应该有：

1. **Issue 编号**: `<issue-number>`
2. **修复方案**: 
   - 需要修改的文件列表
   - 修改内容描述
3. **测试方案**:
   - 测试方法
   - 测试用例
4. **影响范围**: 影响描述

---

## 🔄 下一阶段

准备完成后，进入 [阶段 2: 分支创建与代码修改](./workflow-02-branch-and-code.md)

---

**阶段**: 1/5  
**文档版本**: v1.0
