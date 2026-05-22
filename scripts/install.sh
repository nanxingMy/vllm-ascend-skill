#!/bin/bash

# vLLM-Ascend 数字助手安装脚本

set -e

echo "========================================="
echo "vLLM-Ascend 数字助手安装脚本"
echo "========================================="
echo ""

# 检测操作系统
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    HERMES_SKILLS="$HOME/AppData/Local/hermes/skills"
    HERMES_CONFIG="$HOME/AppData/Local/hermes"
else
    # Linux/Mac
    HERMES_SKILLS="$HOME/.hermes/skills"
    HERMES_CONFIG="$HOME/.hermes"
fi

echo "检测到 Hermes skills 目录: $HERMES_SKILLS"
echo ""

# 检查目录是否存在
if [ ! -d "$HERMES_SKILLS" ]; then
    echo "错误: Hermes skills 目录不存在"
    echo "请先安装 Hermes Agent"
    exit 1
fi

echo "步骤 1/5: 创建技能目录..."
mkdir -p "$HERMES_SKILLS/mlops/vllm-ascend"
mkdir -p "$HERMES_SKILLS/devops/vllm-ascend-issue-workflow"
mkdir -p "$HERMES_SKILLS/mlops/learn-from-merged-prs"
echo "✓ 目录创建完成"
echo ""

echo "步骤 2/5: 复制 vllm-ascend 技能..."
cp -r skills/mlops/vllm-ascend/* "$HERMES_SKILLS/mlops/vllm-ascend/"
echo "✓ vllm-ascend 技能已安装"
echo ""

echo "步骤 3/5: 复制 vllm-ascend-issue-workflow 技能..."
cp -r skills/devops/vllm-ascend-issue-workflow/* "$HERMES_SKILLS/devops/vllm-ascend-issue-workflow/"
echo "✓ vllm-ascend-issue-workflow 技能已安装"
echo ""

echo "步骤 4/5: 复制 learn-from-merged-prs 技能..."
cp -r skills/mlops/learn-from-merged-prs/* "$HERMES_SKILLS/mlops/learn-from-merged-prs/"
echo "✓ learn-from-merged-prs 技能已安装"
echo ""

echo "步骤 5/5: 显示配置说明..."
echo ""
echo "========================================="
echo "安装完成！"
echo "========================================="
echo ""
echo "接下来需要手动配置："
echo ""
echo "1. 导入 memory 配置:"
echo "   在 Hermes Agent 中使用 memory 工具添加 config/memory.md 中的内容"
echo ""
echo "2. 导入 fact_store 配置:"
echo "   在 Hermes Agent 中使用 fact_store 工具导入 config/fact_store.json"
echo ""
echo "3. 设置定时任务 (可选):"
echo "   参考 config/cronjobs.md 创建 cronjob"
echo ""
echo "4. 验证安装:"
echo "   在 Hermes Agent 中运行: skills_list"
echo "   应该看到 vllm-ascend, vllm-ascend-issue-workflow, learn-from-merged-prs"
echo ""
echo "详细说明请查看 README.md"
echo ""
