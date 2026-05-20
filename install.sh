#!/bin/bash
# 快速安装脚本

set -e

echo "========================================="
echo "vLLM-Ascend 数字员工安装脚本"
echo "========================================="
echo ""

# 检查 Python
echo "【1/6】检查 Python..."
if ! command -v python &> /dev/null; then
    echo "❌ Python 未安装"
    echo "请先安装 Python 3.10-3.11"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "✅ Python 版本: $PYTHON_VERSION"
echo ""

# 检查 Git
echo "【2/6】检查 Git..."
if ! command -v git &> /dev/null; then
    echo "❌ Git 未安装"
    echo "请先安装 Git"
    exit 1
fi
echo "✅ Git 已安装"
echo ""

# 安装 Hermes
echo "【3/6】安装 Hermes Agent..."
if ! python -c "import hermes" 2>/dev/null; then
    echo "正在安装 Hermes..."
    pip install hermes-agent
else
    echo "✅ Hermes 已安装"
fi
echo ""

# 克隆 vLLM-Ascend Skill
echo "【4/6】克隆 vLLM-Ascend Skill..."
if [ ! -d "vllm-ascend-skill" ]; then
    echo "正在克隆..."
    git clone https://github.com/nanxingMy/vllm-ascend-skill.git
else
    echo "✅ vllm-ascend-skill 已存在"
fi
echo ""

# 克隆 vLLM-Ascend
echo "【5/6】克隆 vLLM-Ascend..."
if [ ! -d "vllm-ascend" ]; then
    echo "正在克隆..."
    git clone https://github.com/vllm-project/vllm-ascend.git
    cd vllm-ascend
    
    # 询问 GitHub 用户名
    echo ""
    echo "请输入你的 GitHub 用户名："
    read -r GITHUB_USERNAME
    
    # 配置 fork 远程仓库
    echo "配置 fork 远程仓库..."
    git remote add fork "https://github.com/$GITHUB_USERNAME/vllm-ascend.git"
    
    cd ..
else
    echo "✅ vllm-ascend 已存在"
fi
echo ""

# 配置 Git
echo "【6/6】配置 Git..."
echo ""
echo "请输入你的 Git 配置信息："
echo "用户名 (默认: $(git config --global user.name 2>/dev/null || echo '未设置')):"
read -r GIT_NAME
if [ -n "$GIT_NAME" ]; then
    git config --global user.name "$GIT_NAME"
fi

echo "邮箱 (默认: $(git config --global user.email 2>/dev/null || echo '未设置')):"
read -r GIT_EMAIL
if [ -n "$GIT_EMAIL" ]; then
    git config --global user.email "$GIT_EMAIL"
fi

echo ""
echo "========================================="
echo "✅ 安装完成！"
echo "========================================="
echo ""
echo "下一步："
echo ""
echo "1. 配置 GitHub Token:"
echo "   访问 https://github.com/settings/tokens 创建 token"
echo "   然后运行："
echo "   git config --global credential.helper store"
echo "   echo 'https://YOUR-USERNAME:YOUR-TOKEN@github.com' > ~/.git-credentials"
echo ""
echo "2. 启动数字员工:"
echo "   hermes"
echo ""
echo "3. 加载技能:"
echo "   /load-skill vllm-ascend-skill"
echo ""
echo "4. 开始工作:"
echo "   帮我分析 Issue #8975"
echo ""
echo "========================================="
echo "详细文档: vllm-ascend-skill/README.md"
echo "========================================="
