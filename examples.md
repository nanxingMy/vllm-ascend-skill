# 使用示例

## 📖 目录

- [基础使用](#基础使用)
- [进阶使用](#进阶使用)
- [自动化](#自动化)
- [故障排查](#故障排查)

## 基础使用

### 示例 1: 分析并修复 Issue

```
用户: 帮我分析 Issue #8975

数字员工: 我来分析 Issue #8975...

【分析 Issue】
标题: BalanceScheduler + RecomputeScheduler 可能导致死锁
类型: BugFix
难度: ⭐⭐

【问题分析】
- BalanceScheduler 和 RecomputeScheduler 缺少互斥检查
- 可能同时启用导致死锁
- 需要添加互斥检查

【检查继承关系】
✅ BalanceScheduler 不继承其他类
✅ 可以直接修改

【修复方案】
在 schedule() 方法中添加互斥检查：
- 检查是否同时启用
- 抛出 ValueError

【实现修复】
✅ 创建分支: bugfix/scheduler-mutex-8975
✅ 修改代码: vllm_ascend/scheduler.py
✅ 添加测试: tests/ut/test_scheduler.py
✅ 格式化代码: ruff format

【提交 PR】
✅ 推送到 fork
✅ 创建 PR #9149
✅ 等待 CI

PR 链接: https://github.com/vllm-project/vllm-ascend/pull/9149
```

### 示例 2: 处理 Gemini 反馈

```
用户: 查看 PR #9199 的反馈

数字员工: 我来查看 PR #9199 的反馈...

【Gemini Code Assist 反馈】
反馈 1: 使用 Version.public 属性
位置: vllm_ascend/utils.py:45
建议: 使用 Version(vllm_version).public 代替手动剥离后缀

【处理反馈】
✅ 修改代码: 使用 Version.public
✅ 改进测试: 添加版本后缀测试
✅ 格式化: ruff format
✅ 提交: [Refactor] Use Version.public for robust comparison

【推送更新】
✅ 推送到 fork
✅ CI 重新运行

PR 已更新！
```

### 示例 3: 监控 CI 状态

```
用户: 查看 PR #9216 的 CI 状态

数字员工: 我来查看 PR #9216 的 CI 状态...

【CI 状态】
总计: 49 个检查
✅ 成功: 45 个
❌ 失败: 2 个
🔄 运行中: 2 个

【失败检查】
- e2e-light (v0.20.2) / 310p multicards 4cards
- e2e-light (v0.20.2) / 310p singlecard

【分析失败】
查看日志...
发现错误: IncompleteRead, Connection broken

✅ 这是网络问题，不是代码问题
建议: 重试 CI

【重试 CI】
✅ 已触发重试
```

## 进阶使用

### 示例 4: 批量处理 Issue

```
用户: 帮我处理所有 Good First Issue

数字员工: 我来查找所有 Good First Issue...

【查找 Issue】
搜索条件: label:"good first issue" state:open

找到 3 个 Issue:
1. #9151 - EPLB 精度问题
2. #9099 - 文档错误  
3. #5336 - 测试补充

【处理 Issue #9151】
分析中...
⚠️ 这是复杂问题，需要人类介入
原因: 涉及 EPLB 算法，需要深入理解

【处理 Issue #9099】
分析中...
✅ 这是文档错误
修复中...
✅ 已创建 PR #XXXX

【处理 Issue #5336】
分析中...
✅ 这是测试补充
修复中...
✅ 已创建 PR #XXXX

【总结】
✅ 成功: 2 个
⚠️ 需要人类: 1 个
```

### 示例 5: 自定义工作流

```
用户: 创建一个工作流：每天检查新 Issue 并尝试修复

数字员工: 我来创建工作流...

【创建 Cron Job】
名称: daily-issue-check
调度: 0 9 * * * (每天早上 9 点)
任务: 检查新 Issue 并尝试修复

【工作流内容】
1. 获取最近 24 小时的新 Issue
2. 筛选 Good First Issue 和 Help Wanted
3. 分析每个 Issue
4. 尝试修复简单 Issue
5. 复杂 Issue 发送通知

✅ Cron Job 已创建
下次运行: 明天 9:00 AM
```

## 自动化

### 示例 6: 自动监控 PR

```
用户: 自动监控我的所有 PR，失败时自动修复

数字员工: 我来设置自动监控...

【创建监控任务】
监控目标: 你的所有 PR
检查频率: 每 5 分钟
自动修复: 是

【监控逻辑】
1. 获取所有 open 的 PR
2. 检查 CI 状态
3. 如果失败:
   - 分析失败原因
   - 如果是代码问题，尝试修复
   - 如果是网络问题，重试 CI
4. 如果有新评论:
   - 分析评论内容
   - 如果需要回复，生成回复
   - 如果需要修改，执行修改

✅ 监控任务已创建
```

### 示例 7: 自动回复评论

```
用户: 自动回复维护者的评论

数字员工: 我来设置自动回复...

【PR #9149 新评论】
维护者 @shen-shanshan 评论:
"请添加更多测试用例"

【分析评论】
类型: 请求补充测试
优先级: 高

【处理评论】
✅ 添加测试用例:
   - test_scheduler_mutex_with_profiler
   - test_scheduler_mutex_concurrent
✅ 提交更新
✅ 回复评论:
   "已添加测试用例，请查看"

✅ 评论已处理
```

## 故障排查

### 示例 8: CI 失败分析

```
用户: PR #9216 CI 失败了，帮我看看

数字员工: 我来分析 CI 失败...

【获取 CI 日志】
Job: e2e-light (v0.20.2) / 310p singlecard
失败步骤: Install vllm-project/vllm-ascend

【分析错误】
错误类型: ProtocolError
错误信息: Connection broken: IncompleteRead(106897151 bytes read, 81554801 more expected)

【诊断】
✅ 这是网络问题
原因: pip 下载 mypy 时网络中断
不是代码问题

【解决方案】
方式 1: 重试 CI
方式 2: 等待网络恢复

【执行重试】
✅ 已触发 CI 重试
```

### 示例 9: 代码问题修复

```
用户: PR #9205 维护者说不需要，怎么办？

数字员工: 我来分析维护者的反馈...

【维护者评论】
@shen-shanshan:
"This change is redundant, since the logic here is totally 
the same as that of Platform base interface."

【分析反馈】
类型: 重复实现
原因: Platform 基类已有该方法

【检查继承关系】
✅ NPUPlatform 继承 Platform
✅ Platform 已有 get_vit_attn_backend 方法
✅ 我的实现与基类相同

【结论】
❌ 这个 PR 确实不需要
原因: 重复实现基类方法

【处理方案】
1. 关闭 PR #9205
2. 在 Issue #3489 说明情况
3. 学习经验: 添加方法前检查基类

【执行】
✅ 已关闭 PR #9205
✅ 已在 Issue #3489 评论说明
✅ 已记录经验教训
```

## 💡 提示

### 有效指令

```
✅ 好的指令:
"分析 Issue #8975，这是一个 BalanceScheduler 死锁问题"
"查看 PR #9149 的 CI 状态并分析失败原因"
"处理所有 Good First Issue，最多 5 个"

❌ 不好的指令:
"修复这个"  # 太模糊
"处理所有 Issue"  # 范围太大
"随便改改"  # 没有目标
```

### 分步骤工作

```
用户: 帮我处理 Issue #9151

数字员工: 这是一个复杂问题，建议分步骤处理：

【步骤 1】分析问题
我来分析 Issue #9151...

【步骤 2】设计方案
基于分析，我建议以下方案...

【步骤 3】实现修复
我来实现修复...

【步骤 4】验证结果
我来验证修复是否正确...

每完成一步，你可以检查结果，然后继续下一步。
是否开始步骤 1？
```

---

## 🎯 总结

**数字员工可以帮你**：
- ✅ 自动分析和修复 Issue
- ✅ 编写测试和格式化代码
- ✅ 提交 PR 和处理反馈
- ✅ 监控 CI 和自动修复
- ✅ 批量处理简单任务

**你需要做**：
- ✅ 提供清晰的指令
- ✅ 验证结果
- ✅ 处理复杂问题
- ✅ 做最终决策

**让数字员工成为你的得力助手！** 🚀
