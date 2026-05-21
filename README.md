# vLLM-Ascend 数字员工

## 🤖 一键拥有你的数字员工

**克隆这个项目，运行一个命令，你就拥有了一个 24/7 不知疲倦的数字员工！**

```bash
# 克隆项目
git clone https://github.com/nanxingMy/vllm-ascend-skill.git
cd vllm-ascend-skill

# 一键配置
bash setup.sh

# 启动 Hermes
hermes

# 开始工作
帮我分析 Issue #8975
```

## ✨ 能做什么

这个数字员工可以自动：

- ✅ 分析 vLLM-Ascend GitHub Issue
- ✅ 检查继承关系，避免重复实现
- ✅ 修复代码问题
- ✅ 编写单元测试
- ✅ 提交 Pull Request
- ✅ 处理 Gemini Code Assist 反馈
- ✅ 监控 CI 状态并自动修复

### 已完成的工作

| PR | Issue | 类型 | 状态 |
|----|-------|------|------|
| #9149 | #8975 | BugFix | ✅ 已合并 |
| #9199 | #9167 | BugFix | ✅ 已合并 |
| #9216 | #4112 | Feature | ✅ 代码正确 |

## 🚀 快速开始

### 前置条件

1. **Python 3.10-3.11**
2. **Git**
3. **GitHub Account**

### 安装步骤

```bash
# 1. 安装 Hermes Agent
pip install hermes-agent

# 2. 克隆这个项目
git clone https://github.com/nanxingMy/vllm-ascend-skill.git
cd vllm-ascend-skill

# 3. 运行配置脚本（自动完成所有配置）
bash setup.sh

# 4. 配置 GitHub Token
git config --global credential.helper store
echo 'https://YOUR-USERNAME:YOUR-TOKEN@github.com' > ~/.git-credentials

# 5. 克隆 vLLM-Ascend 仓库
git clone https://github.com/vllm-project/vllm-ascend.git
cd vllm-ascend
git remote add fork https://github.com/YOUR-USERNAME/vllm-ascend.git

# 6. 启动 Hermes
hermes

# 7. 加载 skill
/load-skill vllm-ascend-digital-employee

# 8. 开始工作
帮我分析 Issue #8975
```

## 📖 使用方法

### 基础使用

```
用户: 帮我分析 Issue #8975

数字员工: 我来分析 Issue #8975...
【分析】BalanceScheduler 死锁问题
【检查】继承关系 ✅
【修复】添加互斥检查
【测试】编写测试用例
【提交】创建 PR #9149
【状态】✅ CI 通过
```

### 自动监控

```
用户: 自动监控我的所有 PR

数字员工: 我来设置监控...
【监控】每 5 分钟检查一次
【自动修复】CI 失败时自动处理
✅ 监控已启动
```

### 批量处理

```
用户: 处理所有 Good First Issue

数字员工: 找到 3 个 Issue...
【处理】Issue #9151
【处理】Issue #9099
【处理】Issue #5336
✅ 已创建 3 个 PR
```

## 🎓 核心知识

### 继承关系（最重要！）

**添加新接口前必须检查**：

```bash
# 检查 Platform 基类是否有某方法
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/platforms/interface.py" | grep "def <method_name>"
```

**判断规则**：
- ✅ 基类没有 → 可以实现
- ✅ 基类有，但需要不同逻辑 → 可以覆盖
- ❌ 基类有，逻辑相同 → 不需要实现

### 开发流程

```
1. 分析 Issue
2. 检查继承关系
3. 实现修复
4. 编写测试
5. 格式化代码
6. 提交 PR
7. 处理反馈
8. 监控 CI
```

### 代码风格

- 使用 `ValueError` 而不是 `assert`
- 使用 `ruff format` 格式化
- 添加单元测试
- 处理所有 Gemini 反馈

## 📚 知识库

数字员工包含完整的知识库：

### 核心文档
- [架构详解](skill/references/architecture.md) - 工作原理
- [继承关系](skill/references/inheritance.md) - **最重要！**
- [开发指南](skill/references/development-guide.md) - 最佳实践
- [经验教训](skill/references/lessons-learned.md) - 踩坑记录
- [PR 示例](skill/references/pr-examples.md) - 实战案例
- [使用示例](skill/references/examples.md) - 详细示例

### Issue 处理工作流 ⭐ **新增！**
完整的 5 阶段工作流文档：
- [工作流总览](skill/references/workflow/README.md)
- [快速参考](skill/references/workflow/QUICK-REFERENCE.md) - **常用命令速查**
- [阶段 1: Issue 发现与分析](skill/references/workflow/workflow-01-issue-discovery.md)
- [阶段 2: 分支创建与代码修改](skill/references/workflow/workflow-02-branch-and-code.md)
- [阶段 3: PR 创建与 DCO 处理](skill/references/workflow/workflow-03-pr-and-dco.md)
- [阶段 4: 检视意见处理](skill/references/workflow/workflow-04-review-feedback.md)
- [阶段 5: CI 监控与合并](skill/references/workflow/workflow-05-ci-and-merge.md)

## 🛠️ 配置

### 环境变量（可选）

```bash
export GITHUB_USERNAME="your-username"
export GITHUB_TOKEN="your-token"
export HERMES_MODEL="claude-sonnet-4"
```

### Hermes 配置

配置文件位于 `~/.hermes/config.yaml`，setup.sh 会自动创建。

## 📊 性能

### 效率对比

| 任务 | 人类 | 数字员工 | 加速 |
|------|------|---------|------|
| 分析 Issue | 1-2h | 5-10m | 6-12x |
| 修复代码 | 2-4h | 10-30m | 4-8x |
| 编写测试 | 1-2h | 5-10m | 6-12x |
| 提交 PR | 30m | 2-5m | 6-15x |
| **总计** | **5-9h** | **20-55m** | **6-10x** |

### 成功率

- ✅ 简单 BugFix: 100%
- ✅ 简单 Feature: 100%
- ⚠️ 复杂问题: 需要人类介入

## 🎯 最佳实践

### DO ✅

- 选择合适的 Issue（Good First Issue, Help Wanted）
- 提供清晰的指令
- 验证结果

### DON'T ❌

- 处理复杂的架构问题
- 盲目信任结果
- 忽略反馈

## 🐛 故障排查

### 常见问题

**Q: Git 推送失败？**
```bash
# 检查网络
ping github.com

# 重新配置 token
git config --global credential.helper store
```

**Q: CI 一直失败？**
```
用户: 查看 PR #XXX 的 CI 日志

数字员工: [分析]
发现是网络问题（IncompleteRead），不是代码问题。
建议重试 CI。
```

**Q: 找不到相关代码？**
```
用户: Issue #XXX 涉及哪些文件？

数字员工: [搜索]
找到相关文件：
- vllm_ascend/platform.py
- tests/ut/test_platform.py
```

## 📈 进阶使用

### 自定义工作流

创建 `.hermes/workflows/my-workflow.yaml` 自定义工作流。

### 批量处理

```bash
hermes run-batch --issues "good-first-issue" --max 5
```

### 监控和报警

```bash
hermes create-cron --name "monitor-prs" --schedule "*/5 * * * *"
```

## 🤝 贡献

欢迎贡献！可以添加：

- 新的知识文档
- 新的工作流程
- Bug 修复
- 文档改进

## 📄 许可证

MIT License

## 🙏 致谢

- [Hermes Agent](https://github.com/nousresearch/hermes)
- [vLLM-Ascend](https://github.com/vllm-project/vllm-ascend)

---

## 🎉 立即开始

```bash
git clone https://github.com/nanxingMy/vllm-ascend-skill.git
cd vllm-ascend-skill
bash setup.sh
hermes
```

**拥有你的数字员工，让开发效率提升 10 倍！** 🚀
