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

### 技能 (Skills) - 5 个核心技能

| 技能名称 | 用途 | 位置 |
|---------|------|------|
| **vllm-ascend** | vLLM-Ascend 开发核心技能（架构、PR规范、陷阱、最佳实践） | `skills/mlops/vllm-ascend/` |
| **vllm-ascend-issue-workflow** | Issue 处理完整工作流（DCO修复、Lint修复、反馈处理） | `skills/devops/vllm-ascend-issue-workflow/` |
| **learn-from-merged-prs** | 从历史 PR 学习模式和最佳实践 | `skills/mlops/learn-from-merged-prs/` |
| **pr-feedback-handler** | 自动监控 PR 反馈并修复代码 | `skills/github/pr-feedback-handler/` |
| **continuous-learning** | 持续学习机制（每日更新、模块学习） | `skills/devops/continuous-learning/` |

### 配置文件 (Config) - 真实的 Hermes 配置

| 文件 | 用途 | 说明 |
|------|------|------|
| `config/MEMORY.md` | 系统记忆 | vLLM-Ascend 相关的经验和知识（36行） |
| `config/USER.md` | 用户配置 | GitHub 账号、偏好设置（28行） |
| `config/cronjobs.json` | 定时任务 | 5 个自动学习任务配置 |

### 脚本 (Scripts)

| 脚本 | 用途 |
|------|------|
| `scripts/install.sh` | 自动安装脚本 |

---

## 🚀 快速开始

### 前置要求

1. **Hermes Agent 已安装**
   ```bash
   hermes --version
   ```

2. **Git 配置正确**
   ```bash
   git config --global user.name "你的名字"
   git config --global user.email "你的邮箱"
   ```

3. **GitHub Token 已配置**

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

# 2. 设置 Hermes 目录（根据你的系统）
# Windows:
HERMES_DIR="$HOME/AppData/Local/hermes"
# Linux/Mac:
HERMES_DIR="$HOME/.hermes"

# 3. 复制技能
mkdir -p "$HERMES_DIR/skills/mlops/vllm-ascend"
mkdir -p "$HERMES_DIR/skills/devops/vllm-ascend-issue-workflow"
mkdir -p "$HERMES_DIR/skills/mlops/learn-from-merged-prs"
mkdir -p "$HERMES_DIR/skills/github/pr-feedback-handler"
mkdir -p "$HERMES_DIR/skills/devops/continuous-learning"

cp -r skills/mlops/vllm-ascend/* "$HERMES_DIR/skills/mlops/vllm-ascend/"
cp -r skills/devops/vllm-ascend-issue-workflow/* "$HERMES_DIR/skills/devops/vllm-ascend-issue-workflow/"
cp -r skills/mlops/learn-from-merged-prs/* "$HERMES_DIR/skills/mlops/learn-from-merged-prs/"
cp -r skills/github/pr-feedback-handler/* "$HERMES_DIR/skills/github/pr-feedback-handler/"
cp -r skills/devops/continuous-learning/* "$HERMES_DIR/skills/devops/continuous-learning/"

# 4. 导入 Memory 配置
mkdir -p "$HERMES_DIR/memories"
cp config/MEMORY.md "$HERMES_DIR/memories/MEMORY.md"
cp config/USER.md "$HERMES_DIR/memories/USER.md"

# 5. 导入 Cronjob 配置
mkdir -p "$HERMES_DIR/cron"
cp config/cronjobs.json "$HERMES_DIR/cron/jobs.json"

echo "✓ 安装完成！"
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

## ⚙️ 配置说明

### Memory 配置

**MEMORY.md** 包含：
- DCO 要求和规则
- PR 工作流规则
- 已完成的贡献记录
- 关键学习和陷阱
- 代码风格说明

**USER.md** 包含：
- GitHub 账号信息
- 用户偏好设置
- 工作流规则

### Cronjob 配置

**cronjobs.json** 包含 5 个定时任务：

1. **vllm-ascend-pr-monitor** (每 5 分钟)
   - 监控 PR 状态
   - 读取 review comments
   - 自动修复代码

2. **update-memory-to-vllm-ascend-skill** (每天凌晨)
   - 更新 memory 到仓库
   - 提取有价值的经验

3. **deep-learn-vllm-ascend** (每天凌晨)
   - 深度学习项目结构
   - 提取最佳实践

4. **module-learn-vllm-ascend** (每天凌晨)
   - 分模块学习
   - 生成学习文档

5. **learn-daily-merged-prs** (每天凌晨)
   - 学习新合入的 PR
   - 累积经验

---

## 🔧 高级配置

### 自定义 Git 配置

编辑 `config/USER.md`：

```markdown
GitHub 账号: 你的账号 (fork: https://github.com/你的账号/vllm-ascend.git)
邮箱: 你的邮箱
```

### 自定义定时任务

编辑 `config/cronjobs.json` 调整执行频率。

---

## 🎓 学习路径

安装完成后，建议按以下顺序学习：

### 第 1 天：理解架构

```bash
cat skills/mlops/vllm-ascend/references/architecture.md
cat skills/mlops/vllm-ascend/references/how-vllm-ascend-works.md
```

### 第 2-3 天：学习 PR 工作流

```bash
cat skills/mlops/vllm-ascend/references/pr-workflow-overview.md
cat skills/devops/vllm-ascend-issue-workflow/SKILL.md
```

### 第 4-7 天：学习历史 PR

```bash
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
Agent: [应该显示 vllm-ascend, vllm-ascend-issue-workflow, learn-from-merged-prs, pr-feedback-handler, continuous-learning]

用户: 查看 vllm-ascend 技能
Agent: [应该显示完整的技能内容]
```

---

## 📊 统计数据

- **技能数量**: 5 个核心技能
- **参考文档**: 40+ 个
- **脚本数量**: 5 个
- **已学习 PR**: 1370+ 个
- **已提交 PR**: 4 个
- **Memory 条目**: 36 条
- **定时任务**: 5 个

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
