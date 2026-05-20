#!/bin/bash
# 推送到 GitHub 指南

echo "========================================="
echo "推送 vLLM-Ascend 数字员工到 GitHub"
echo "========================================="
echo ""

# 检查网络
echo "【步骤 1】检查网络连接..."
echo ""

if ping -c 1 github.com > /dev/null 2>&1; then
    echo "✅ 网络连接正常"
else
    echo "❌ 无法连接到 GitHub"
    echo ""
    echo "可能的原因："
    echo "1. 网络问题"
    echo "2. 防火墙阻止"
    echo "3. DNS 解析失败"
    echo ""
    echo "解决方法："
    echo "1. 检查网络连接"
    echo "2. 尝试使用 VPN"
    echo "3. 等待网络恢复后重试"
    echo ""
    exit 1
fi

echo ""

# 检查 Git 配置
echo "【步骤 2】检查 Git 配置..."
echo ""

if git config --global user.name > /dev/null 2>&1; then
    echo "✅ Git 用户名: $(git config --global user.name)"
else
    echo "⚠️  Git 用户名未配置"
    echo "请运行: git config --global user.name 'Your Name'"
fi

if git config --global user.email > /dev/null 2>&1; then
    echo "✅ Git 邮箱: $(git config --global user.email)"
else
    echo "⚠️  Git 邮箱未配置"
    echo "请运行: git config --global user.email 'your@email.com'"
fi

echo ""

# 检查远程仓库
echo "【步骤 3】检查远程仓库..."
echo ""

cd /c/Users/HuaWei/vllm-ascend-skill

if git remote | grep -q "origin"; then
    echo "✅ 远程仓库已配置:"
    git remote -v
else
    echo "⚠️  远程仓库未配置"
    echo ""
    echo "请选择推送方式:"
    echo "1. HTTPS (推荐)"
    echo "2. SSH"
    echo ""
    read -p "选择 (1/2): " choice
    
    if [ "$choice" = "1" ]; then
        git remote add origin https://github.com/nanxingMy/vllm-ascend-skill.git
        echo "✅ 已添加 HTTPS 远程"
    else
        git remote add origin git@github.com:nanxingMy/vllm-ascend-skill.git
        echo "✅ 已添加 SSH 远程"
    fi
fi

echo ""

# 推送
echo "【步骤 4】推送到 GitHub..."
echo ""

git push -u origin master

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✅ 推送成功！"
    echo "========================================="
    echo ""
    echo "访问你的项目:"
    echo "https://github.com/nanxingMy/vllm-ascend-skill"
    echo ""
    echo "其他人可以使用:"
    echo "git clone https://github.com/nanxingMy/vllm-ascend-skill.git"
    echo "cd vllm-ascend-skill"
    echo "bash setup.sh"
    echo "hermes"
    echo ""
else
    echo ""
    echo "========================================="
    echo "❌ 推送失败"
    echo "========================================="
    echo ""
    echo "可能的原因:"
    echo "1. GitHub 认证失败"
    echo "   - 配置 token: git config --global credential.helper store"
    echo "   - 或使用 SSH: ssh-keygen -t ed25519 -C 'your@email.com'"
    echo ""
    echo "2. 仓库不存在"
    echo "   - 先在 GitHub 创建仓库: https://github.com/new"
    echo ""
    echo "3. 网络问题"
    echo "   - 检查网络连接"
    echo "   - 尝试使用 VPN"
    echo ""
fi
