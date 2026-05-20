# vLLM-Ascend 知识库

## 📚 简介

这是我在学习 vLLM-Ascend 项目过程中积累的知识库，包含架构理解、开发经验、最佳实践等内容。

## 🎯 目标

从小白进化为资深 vLLM-Ascend 工程师，能够独立解决 Issue 并提交 PR。

## 📖 内容

### 核心知识

- [架构详解](architecture.md) - vLLM-Ascend 架构和工作原理
- [工作流程](workflow.md) - 完整的工作流程说明
- [继承关系](inheritance.md) - 关键的继承关系理解

### 开发指南

- [开发指南](development-guide.md) - 开发流程和最佳实践
- [测试指南](testing.md) - 如何编写和运行测试
- [性能优化](performance.md) - 性能优化技巧

### 实战经验

- [PR 示例](pr-examples.md) - 已完成的 PR 分析
- [问题排查](troubleshooting.md) - 常见问题和解决方案
- [经验教训](lessons-learned.md) - 踩坑记录和经验总结

### 快速开始

- [环境搭建](setup.md) - 如何搭建开发环境
- [运行服务](run-service.md) - 如何在 NPU 上运行服务

## 🏆 已完成的贡献

### PR 列表

1. **PR #9149** - BalanceScheduler 死锁修复
   - Issue: #8975
   - 类型: BugFix
   - 状态: ✅ CI 通过

2. **PR #9199** - 版本后缀比较修复
   - Issue: #9167
   - 类型: BugFix
   - 状态: ✅ CI 通过

3. **PR #9216** - shutdown 方法
   - Issue: #4112
   - 类型: Feature
   - 状态: ✅ 代码正确，CI 网络问题

## 🔑 关键学习

### 最重要的经验

1. **继承关系是第一位的**
   - 添加方法前必须检查基类是否已有
   - NPUPlatform 继承 Platform 基类
   - 不要重复实现基类的方法

2. **代码质量很重要**
   - 必须添加单元测试
   - 使用 ruff format 格式化
   - 根据 Gemini 反馈改进

3. **CI 失败不一定是代码问题**
   - 可能是网络问题
   - 可能是基础设施问题
   - 查看日志再判断

## 📚 参考资源

- [vLLM-Ascend 官方文档](https://docs.vllm.ai/projects/ascend/)
- [vLLM 文档](https://docs.vllm.ai/)
- [昇腾文档](https://www.hiascend.com/document/)
- [GitHub 仓库](https://github.com/vllm-project/vllm-ascend)

## 📝 更新日志

- 2026-05-18: 创建知识库，整理学习成果
