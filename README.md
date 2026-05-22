# vLLM-Ascend 数字助手技能包

> 让你的 Hermes Agent 拥有与训练有素的 vLLM-Ascend 数字助手相同的能力

---

## 🎯 这个仓库是什么？

这个仓库包含了训练 vLLM-Ascend 数字助手的所有技能、配置和知识。按照本 README 安装后，你的 Hermes Agent 将能够：

- ✅ 自动分析 vLLM-Ascend Issue 并修复
- ✅ 自动创建符合 DCO 要求的 PR
- ✅ 自动处理 Gemini Code Assist 反馈
- ✅ 自动监控 PR 状态并响应
- ✅ 持续学习 vLLM-Ascend 历史 PR 积累经验
- ✅ 掌握 vLLM-Ascend 架构、陷阱和最佳实践

---

## 📦 包含内容

### 技能 (Skills)

| 技能名称 | 用途 | 位置 |
|---------|------|------|
| **vllm-ascend** | vLLM-Ascend 开发核心技能（架构、PR规范、陷阱、最佳实践） | `skills/mlops/vllm-ascend/` |
| **vllm-ascend-issue-workflow** | Issue 处理完整工作流（DCO修复、Lint修复、反馈处理） | `skills/devops/vllm-ascend-issue-workflow/` |
| **learn-from-merged-prs** | 从历史 PR 学习模式和最佳实践 | `skills/mlops/learn-from-merged-prs/` |

### 配置 (Config)

| 文件 | 用途 |
|------|------|
| `config/memory.md` | 关键经验和知识（DCO规则、PR工作流、陷阱等） |
| `config/fact_store.json` | 结构化事实存储 |
| `config/cronjobs.md` | 定时任务配置（PR监控、每日学习等） |

### 脚本 (Scripts)

| 脚本 | 用途 |
|------|------|
| `learn_all_prs.py` | 批量学习所有历史 PR |
| `learn_daily_prs.py` | 每日学习新合入的 PR |
| `check_npu_env.sh` | NPU 环境检查 |

---

## 🚀 快速开始

### 前置要求

1. **Hermes Agent 已安装**
   ```bash
   # 检查 hermes 是否安装
   hermes --version
   ```

2. **Git 配置正确**
   ```bash
   # 配置 Git（必须与你的 GitHub 账号匹配）
   git config --global user.name "你的名字"
   git config --global user.email "你的邮箱"
   ```

3. **GitHub Token 已配置**
   ```bash
   # 检查 GitHub 认证
   git ls-remote https://github.com/vllm-project/vllm-ascend.git
   ```

### 安装步骤

#### 方法 1: 自动安装（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/nanxingMy/vllm-ascend-skill.git
cd vllm-ascend-skill

# 2. 运行安装脚本
bash scripts/install.sh
```

#### 方法 2: 手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/nanxingMy/vllm-ascend-skill.git
cd vllm-ascend-skill

# 2. 复制技能到 Hermes skills 目录
HERMES_SKILLS=~/.hermes/skills  # 或 ~/AppData/Local/hermes/skills (Windows)

# 复制 vllm-ascend 技能
mkdir -p $HERMES_SKILLS/mlops/vllm-ascend
cp -r skills/mlops/vllm-ascend/* $HERMES_SKILLS/mlops/vllm-ascend/

# 复制 vllm-ascend-issue-workflow 技能
mkdir -p $HERMES_SKILLS/devops/vllm-ascend-issue-workflow
cp -r skills/devops/vllm-ascend-issue-workflow/* $HERMES_SKILLS/devops/vllm-ascend-issue-workflow/

# 复制 learn-from-merged-prs 技能
mkdir -p $HERMES_SKILLS/mlops/learn-from-merged-prs
cp -r skills/mlops/learn-from-merged-prs/* $HERMES_SKILLS/mlops/learn-from-merged-prs/

# 3. 导入 memory 配置
# 方法 A: 手动添加到 Hermes memory
# 打开 Hermes Agent，使用 memory 工具添加 config/memory.md 中的内容

# 方法 B: 直接编辑 memory 文件（高级用户）
# 找到 Hermes memory 文件位置，追加 config/memory.md 内容

# 4. 导入 fact_store 配置
# 使用 fact_store 工具导入 config/fact_store.json 中的事实

# 5. 设置定时任务（可选）
# 参考 config/cronjobs.md 创建 cronjob
```

---

## 📚 使用指南

### 1. 分析 Issue

```
用户: 分析 vLLM-Ascend Issue #8975
Agent: [自动加载 vllm-ascend 技能，分析问题，提供解决方案]
```

### 2. 创建 PR

```
用户: 为 Issue #8975 创建 PR
Agent: [自动创建分支、修改代码、提交、推送、创建 PR]
```

### 3. 处理反馈

```
用户: 检查 PR #9149 的反馈
Agent: [自动读取 review comments，修复代码，回复]
```

### 4. 学习历史 PR

```
用户: 学习 vLLM-Ascend 历史 PR
Agent: [运行 learn_all_prs.py，提取模式和最佳实践]
```

---

## 🔧 高级配置

### 自定义 Git 配置

编辑 `config/memory.md` 中的 Git 配置：

```markdown
## DCO 要求

Git 配置: user.name="你的名字", user.email="你的邮箱"
```

### 自定义定时任务

编辑 `config/cronjobs.md` 调整执行频率：

```yaml
# PR 监控（默认每 5 分钟）
schedule: "every 10m"

# 每日学习（默认凌晨 0 点）
schedule: "0 6 * * *"  # 改为早上 6 点
```

### 添加自定义技能

在 `skills/` 目录下创建新技能：

```bash
mkdir -p skills/custom/my-skill
# 创建 SKILL.md 文件
```

---

## 🎓 学习路径

安装完成后，建议按以下顺序学习：

### 第 1 天：理解架构

```bash
# 阅读架构文档
cat skills/mlops/vllm-ascend/references/architecture.md
cat skills/mlops/vllm-ascend/references/how-vllm-ascend-works.md
```

### 第 2-3 天：学习 PR 工作流

```bash
# 阅读 PR 工作流文档
cat skills/mlops/vllm-ascend/references/pr-workflow-overview.md
cat skills/devops/vllm-ascend-issue-workflow/SKILL.md
```

### 第 4-7 天：学习历史 PR

```bash
# 学习所有历史 PR（约 1900 个）
python skills/mlops/learn-from-merged-prs/scripts/learn_all_prs.py
```

### 持续学习

定时任务会自动：
- 每天学习新合入的 PR
- 每天深入学习项目模块
- 每 5 分钟监控你的 PR 状态

---

## 🐛 常见问题

### Q: DCO 检查失败怎么办？

A: 参考 `skills/devops/vllm-ascend-issue-workflow/references/dco-fix-patterns.md`

关键：**不要关闭 PR**，使用 `git rebase --signoff origin/main` 修复。

### Q: Lint 检查失败怎么办？

A: 参考 `skills/devops/vllm-ascend-issue-workflow/references/lint-fix-patterns.md`

通常需要添加文件到 `pyproject.toml` 的 exclude 列表。

### Q: 如何验证安装成功？

A: 在 Hermes Agent 中运行：

```
用户: 列出所有技能
Agent: [应该显示 vllm-ascend, vllm-ascend-issue-workflow, learn-from-merged-prs]

用户: 查看 vllm-ascend 技能
Agent: [应该显示完整的技能内容]
```

---

## 📊 统计数据

- **技能数量**: 3 个核心技能
- **参考文档**: 40+ 个
- **脚本数量**: 3 个
- **已学习 PR**: 1370+ 个
- **已提交 PR**: 4 个
- **知识条目**: 10+ 条

---

## 🤝 贡献

欢迎贡献！你可以：

1. **添加新技能** - 在 `skills/` 目录下创建
2. **更新文档** - 改进参考文档和陷阱说明
3. **分享经验** - 添加新的学习案例

---

## 📄 许可证

Apache-2.0

---

## 🙏 致谢

- vLLM-Ascend 项目团队
- Hermes Agent 框架
- 所有贡献者

---

## 📞 支持

遇到问题？

1. 查看 `skills/mlops/vllm-ascend/SKILL.md` 中的陷阱部分
2. 查看 `skills/devops/vllm-ascend-issue-workflow/references/` 中的示例
3. 提交 Issue 到本仓库

---

**祝你成为 vLLM-Ascend 贡献者！** 🎉
