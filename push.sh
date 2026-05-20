#!/bin/bash
# 推送脚本

echo "========================================="
echo "推送 vLLM-Ascend 知识库到 GitHub"
echo "========================================="

cd /c/Users/HuaWei/vllm-ascend-skill

# 检查网络
echo "检查网络连接..."
if ping -c 1 github.com > /dev/null 2>&1; then
    echo "✅ 网络连接正常"
else
    echo "❌ 无法连接到 GitHub"
    echo "请检查网络连接后重试"
    exit 1
fi

# 推送
echo ""
echo "推送到远程仓库..."
git push -u origin master

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 推送成功！"
    echo ""
    echo "访问: https://github.com/nanxingMy/vllm-ascend-skill"
else
    echo ""
    echo "❌ 推送失败"
    echo "请检查错误信息并重试"
fi
