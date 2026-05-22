# Cronjob 配置

此文件定义了 vLLM-Ascend 数字助手的定时任务配置。

---

## 定时任务列表

### 1. PR 监控 (vllm-ascend-pr-monitor)

**用途**: 监控 PR 状态，读取反馈，自动修复代码

**配置**:
```yaml
name: vllm-ascend-pr-monitor
schedule: "every 5m"
repeat: forever
deliver: origin
enabled_toolsets:
  - web
  - terminal
  - file
```

**功能**:
- 检查 PR 状态
- 读取 review comments
- 根据 Gemini Code Assist 反馈自动修复代码
- 回复并关闭 review comments

---

### 2. Memory 更新 (update-memory-to-vllm-ascend-skill)

**用途**: 每天凌晨自动更新 memory 到 vllm-ascend-skill 仓库

**配置**:
```yaml
name: update-memory-to-vllm-ascend-skill
schedule: "0 0 * * *"
repeat: forever
deliver: local
script: scripts/update_memory.py
enabled_toolsets:
  - terminal
  - file
```

**功能**:
- 读取当前的 memory 文件
- 提取有价值的经验教训和知识点
- 更新到 vllm-ascend-skill 仓库
- 提交并推送

---

### 3. 深度学习 (deep-learn-vllm-ascend)

**用途**: 每天凌晨自动深入学习 vllm-ascend 项目

**配置**:
```yaml
name: deep-learn-vllm-ascend
schedule: "0 0 * * *"
repeat: forever
deliver: local
script: scripts/comprehensive_learn.py
enabled_toolsets:
  - terminal
  - file
```

**功能**:
- 分析项目结构和架构
- 学习关键模块和类
- 提取最佳实践和设计模式
- 理解代码继承关系
- 分析测试覆盖和性能优化

---

### 4. 模块学习 (module-learn-vllm-ascend)

**用途**: 每天凌晨分模块学习 vllm-ascend

**配置**:
```yaml
name: module-learn-vllm-ascend
schedule: "0 0 * * *"
repeat: forever
deliver: local
script: scripts/module_learn.py
enabled_toolsets:
  - terminal
  - file
```

**学习计划**:
- Monday: 架构概述
- Tuesday: 核心组件
- Wednesday: 平台适配
- Thursday: 分布式通信
- Friday: 性能优化
- Saturday: 测试方法
- Sunday: 总结复习

---

### 5. PR 学习 (learn-daily-merged-prs)

**用途**: 每天凌晨学习当天合入的 PR

**配置**:
```yaml
name: learn-daily-merged-prs
schedule: "0 0 * * *"
repeat: forever
deliver: local
script: scripts/learn_daily_prs.py
enabled_toolsets:
  - terminal
  - file
  - web
```

**功能**:
- 获取今天合入的 PR
- 分析每个 PR 的解决方案
- 查找对应的 Issue
- 提取经验和最佳实践
- 累积到已有知识库

---

## 安装说明

将这些 cronjob 配置导入到 Hermes Agent:

```bash
# 方法 1: 使用 hermes CLI
hermes cronjob import config/cronjobs.yaml

# 方法 2: 手动创建每个 cronjob
hermes cronjob create --name "vllm-ascend-pr-monitor" --schedule "every 5m" --prompt "..."
hermes cronjob create --name "learn-daily-merged-prs" --schedule "0 0 * * *" --script scripts/learn_daily_prs.py
```

---

## 注意事项

1. **时区**: 所有时间使用本地时区 (UTC+8)
2. **并发**: 多个 cronjob 可以并发执行
3. **失败重试**: 网络失败会自动重试
4. **日志**: 所有执行日志保存在 ~/.hermes/logs/cronjobs/
