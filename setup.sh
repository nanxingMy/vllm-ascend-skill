#!/bin/bash
# Hermes 配置脚本 - 将数字员工导入 Hermes

set -e

echo "========================================="
echo "vLLM-Ascend 数字员工 - Hermes 配置"
echo "========================================="
echo ""

# 检查 Hermes 是否安装
echo "【1/5】检查 Hermes..."
if ! command -v hermes &> /dev/null; then
    echo "❌ Hermes 未安装"
    echo ""
    echo "请先安装 Hermes:"
    echo "  pip install hermes-agent"
    echo ""
    exit 1
fi
echo "✅ Hermes 已安装"
echo ""

# 获取 Hermes 配置目录
HERMES_DIR="${HERMES_DIR:-$HOME/.hermes}"
SKILLS_DIR="$HERMES_DIR/skills"

echo "【2/5】创建 Hermes 配置目录..."
mkdir -p "$SKILLS_DIR"
mkdir -p "$HERMES_DIR/memory"
echo "✅ 配置目录已创建: $HERMES_DIR"
echo ""

# 获取当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SOURCE="$SCRIPT_DIR/skill"

echo "【3/5】安装 vLLM-Ascend 数字员工 skill..."
SKILL_TARGET="$SKILLS_DIR/vllm-ascend-digital-employee"

if [ -d "$SKILL_TARGET" ]; then
    echo "⚠️  Skill 已存在，更新中..."
    rm -rf "$SKILL_TARGET"
fi

cp -r "$SKILL_SOURCE" "$SKILL_TARGET"
echo "✅ Skill 已安装到: $SKILL_TARGET"
echo ""

# 导入知识到 Hermes memory
echo "【4/5】导入知识库到 Hermes memory..."

# 创建 memory 文件
MEMORY_FILE="$HERMES_DIR/memory/vllm_ascend_knowledge.md"

cat > "$MEMORY_FILE" << 'EOF'
# vLLM-Ascend 核心知识

## 继承关系（最重要！）

NPUPlatform 继承 Platform 基类，自动继承所有方法。

添加新接口前必须检查：
```bash
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/platforms/interface.py" | grep "def <method_name>"
```

## 开发流程

1. 分析 Issue → 2. 检查继承 → 3. 实现修复 → 4. 编写测试 → 5. 提交 PR → 6. 处理反馈

## 代码风格

- 使用 ValueError 而不是 assert
- ruff format 格式化
- 添加测试

## CI 问题

- IncompleteRead/Connection broken → 网络问题，重试 CI
- ruff check failed → 格式化代码
- pytest failed → 修复测试
EOF

echo "✅ 知识库已导入"
echo ""

# 创建 Hermes 配置文件
echo "【5/5】创建 Hermes 配置..."
CONFIG_FILE="$HERMES_DIR/config.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
# Hermes 配置

model: anthropic/claude-sonnet-4

memory:
  enabled: true
  max_entries: 100
  files:
    - vllm_ascend_knowledge.md

skills:
  enabled: true
  directories:
    - ~/.hermes/skills

# GitHub 配置（需要手动设置）
github:
  # username: your-username
  # token: your-token
  # email: your-email@example.com
EOF
    echo "✅ 配置文件已创建: $CONFIG_FILE"
else
    echo "⚠️  配置文件已存在，跳过"
fi

echo ""
echo "========================================="
echo "✅ 配置完成！"
echo "========================================="
echo ""
echo "下一步："
echo ""
echo "1. 配置 GitHub Token（如果还没有）:"
echo "   git config --global credential.helper store"
echo "   echo 'https://YOUR-USERNAME:YOUR-TOKEN@github.com' > ~/.git-credentials"
echo ""
echo "2. 克隆 vLLM-Ascend 仓库:"
echo "   git clone https://github.com/vllm-project/vllm-ascend.git"
echo "   cd vllm-ascend"
echo "   git remote add fork https://github.com/YOUR-USERNAME/vllm-ascend.git"
echo ""
echo "3. 启动 Hermes:"
echo "   hermes"
echo ""
echo "4. 加载 skill:"
echo "   /load-skill vllm-ascend-digital-employee"
echo ""
echo "5. 开始工作:"
echo "   帮我分析 Issue #8975"
echo ""
echo "========================================="
echo "详细文档: $SKILL_TARGET/references/"
echo "========================================="
