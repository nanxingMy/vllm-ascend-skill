# vLLM-Ascend 学习系统

> 让每个人都能快速了解 vLLM-Ascend 项目

## 📚 学习模块

### 1. 架构概览 (Monday)
- 项目简介
- 目录结构
- 核心模块
- 数据流

**文件**: `learned/01-architecture.md`

---

### 2. 核心组件 (Tuesday)
- NPUWorker
- NPUModelRunner
- Platform
- 配置管理

**文件**: `learned/02-core-components.md`

---

### 3. 平台适配 (Wednesday)
- 平台检测
- 设备特性
- 平台配置
- 性能调优

**文件**: `learned/03-platform-adaptation.md`

---

### 4. 算子实现 (Thursday)
- 注意力算子
- MoE 算子
- 量化算子
- 自定义算子

**文件**: `learned/04-operators.md`

---

### 5. 分布式系统 (Friday)
- 并行策略
- 通信机制
- KV 传输
- 负载均衡

**文件**: `learned/05-distributed.md`

---

### 6. 测试体系 (Saturday)
- 单元测试
- 端到端测试
- 性能测试
- 测试覆盖率

**文件**: `learned/06-testing.md`

---

### 7. 最佳实践 (Sunday)
- 代码风格
- 错误处理
- 性能优化
- 调试技巧

**文件**: `learned/07-best-practices.md`

---

## 🎯 学习目标

通过这个学习系统，你将：

✅ **理解架构**: 掌握 vLLM-Ascend 的整体设计

✅ **熟悉组件**: 了解各个核心组件的职责和实现

✅ **掌握平台**: 理解 NPU 平台适配机制

✅ **深入算子**: 学习关键算子的实现细节

✅ **了解分布**: 掌握分布式推理的原理

✅ **学会测试**: 理解测试体系和方法

✅ **应用实践**: 掌握最佳实践和优化技巧

---

## 📅 学习计划

| 星期 | 模块 | 时间 |
|------|------|------|
| Monday | 架构概览 | 00:00 |
| Tuesday | 核心组件 | 00:00 |
| Wednesday | 平台适配 | 00:00 |
| Thursday | 算子实现 | 00:00 |
| Friday | 分布式系统 | 00:00 |
| Saturday | 测试体系 | 00:00 |
| Sunday | 最佳实践 | 00:00 |

---

## 🚀 快速开始

### 查看所有模块

```bash
ls skill/references/learned/
```

### 阅读特定模块

```bash
cat skill/references/learned/01-architecture.md
```

### 查看学习进度

```bash
# 查看已学习的模块
ls -la skill/references/learned/
```

---

## 📖 文档结构

```
skill/references/learned/
├── 01-architecture.md        # 架构概览
├── 02-core-components.md     # 核心组件
├── 03-platform-adaptation.md # 平台适配
├── 04-operators.md           # 算子实现
├── 05-distributed.md         # 分布式系统
├── 06-testing.md             # 测试体系
└── 07-best-practices.md      # 最佳实践
```

---

## 🔄 自动更新

**Cron Job**: `module-learn-vllm-ascend`

**执行时间**: 每天 00:00

**执行脚本**: `scripts/module_learn.py`

**自动流程**:
1. 根据星期几选择学习模块
2. 学习并生成文档
3. 提交到 Git
4. 推送到 GitHub

---

## 💡 学习建议

### 对于新手

1. 从 **架构概览** 开始
2. 理解 **核心组件** 的职责
3. 学习 **平台适配** 机制
4. 逐步深入其他模块

### 对于开发者

1. 关注 **最佳实践**
2. 学习 **算子实现**
3. 理解 **分布式系统**
4. 参考 **测试体系**

### 对于运维人员

1. 重点阅读 **平台适配**
2. 学习 **分布式系统**
3. 了解 **测试体系**
4. 掌握 **最佳实践**

---

## 📊 学习效果

通过持续学习，你将：

- 🎯 **快速上手**: 30 分钟了解项目
- 📈 **深入理解**: 1 周掌握核心概念
- 🚀 **熟练应用**: 1 月成为贡献者
- 🏆 **专家级别**: 3 月成为专家

---

## 🔗 相关链接

- **vLLM-Ascend**: https://github.com/vllm-project/vllm-ascend
- **vLLM-Ascend-Skill**: https://github.com/nanxingMy/vllm-ascend-skill
- **vLLM 文档**: https://vllm.readthedocs.io/

---

**每天学习一个模块，一周掌握 vLLM-Ascend！** 🎓
