#!/bin/bash
# vLLM-Ascend NPU 环境检查脚本

echo "========================================="
echo "vLLM-Ascend 环境检查"
echo "========================================="

# 1. 检查 NPU 硬件
echo -e "\n[1] NPU 硬件检查"
if command -v npu-smi &> /dev/null; then
    npu-smi info
else
    echo "❌ npu-smi 未安装"
fi

# 2. 检查 CANN 环境
echo -e "\n[2] CANN 环境检查"
if [ -n "$ASCEND_HOME_PATH" ]; then
    echo "✅ ASCEND_HOME_PATH: $ASCEND_HOME_PATH"
else
    echo "❌ ASCEND_HOME_PATH 未设置"
fi

# 3. 检查 PyTorch 和 torch-npu
echo -e "\n[3] PyTorch 检查"
python3 -c "
import torch
print(f'PyTorch 版本: {torch.__version__}')
try:
    import torch_npu
    print(f'torch-npu 版本: {torch_npu.__version__}')
    print(f'NPU 可用: {torch.npu.is_available()}')
    if torch.npu.is_available():
        print(f'NPU 数量: {torch.npu.device_count()}')
        for i in range(torch.npu.device_count()):
            print(f'  NPU {i}: {torch.npu.get_device_name(i)}')
except ImportError:
    print('❌ torch-npu 未安装')
"

# 4. 检查 vLLM
echo -e "\n[4] vLLM 检查"
python3 -c "
try:
    import vllm
    print(f'vLLM 版本: {vllm.__version__}')
except ImportError:
    print('❌ vLLM 未安装')
"

# 5. 检查 vLLM-Ascend
echo -e "\n[5] vLLM-Ascend 检查"
python3 -c "
try:
    import vllm_ascend
    print('✅ vLLM-Ascend 已安装')
    from vllm_ascend.platform import NPUPlatform
    print('✅ NPUPlatform 可导入')
except ImportError as e:
    print(f'❌ vLLM-Ascend 未安装: {e}')
"

echo -e "\n========================================="
echo "检查完成"
echo "========================================="
