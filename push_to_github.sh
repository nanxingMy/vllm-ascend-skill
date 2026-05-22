#!/bin/bash

# 推送到 GitHub 脚本

set -e

echo "========================================="
echo "推送到 vllm-ascend-skill 仓库"
echo "========================================="
echo ""

cd ~/vllm-ascend-skill

echo "当前分支："
git branch
echo ""

echo "最新提交："
git log --oneline -3
echo ""

echo "步骤 1/2: 推送到 main 分支..."
git push origin main

echo ""
echo "步骤 2/2: 推送到 master 分支..."
git push origin master

echo ""
echo "========================================="
echo "✓ 推送完成！"
echo "========================================="
echo ""
echo "访问仓库："
echo "https://github.com/nanxingMy/vllm-ascend-skill"
