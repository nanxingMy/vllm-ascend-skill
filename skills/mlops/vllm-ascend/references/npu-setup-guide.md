# NPU Development Environment Setup Guide

Session-generated guide for setting up vLLM-Ascend on Huawei Ascend NPU hardware.

## Hardware Requirements

### Supported NPU Models

| Series | SOC_VERSION | NPU Count | Use Case |
|--------|-------------|-----------|----------|
| Atlas A2 | ascend910b1/b2/b3/b4 | 8 | Mainstream inference |
| Atlas A3 | ascend910_9391/9381/9372 | 16 | High performance |
| Atlas A5 | ascend950_* | - | Latest generation |
| Atlas 310P | ascend310p1/p3/p5 | - | Inference dedicated |

### Hardware Verification

```bash
# Check NPU status
npu-smi info

# Check network connectivity (A2)
for i in {0..7}; do hccn_tool -i $i -link -g; done

# Check network connectivity (A3)
for i in {0..15}; do hccn_tool -i $i -link -g; done
```

## Software Dependencies

### Required Versions

| Software | Version | Notes |
|----------|---------|-------|
| CANN | 9.0.0 | Ascend Computing Architecture |
| PyTorch | 2.9.0 | Deep learning framework |
| torch-npu | 2.9.0 | PyTorch NPU extension |
| Python | 3.9-3.11 | Python interpreter |

### CANN Components

Three packages required:
- `Ascend-cann-toolkit_9.0.0` - Core toolkit
- `Ascend-cann-910b-ops_9.0.0` - 910B optimized operators
- `Ascend-cann-nnal_9.0.0` - NNAL (libatb.so)

## Installation Steps

### 1. Install CANN

```bash
# Download from: https://www.hiascend.com/software/cann

# Install toolkit
chmod +x Ascend-cann-toolkit_9.0.0_linux-aarch64.run
./Ascend-cann-toolkit_9.0.0_linux-aarch64.run --install

# Install 910B operators
chmod +x Ascend-cann-910b-ops_9.0.0_linux-aarch64.run
./Ascend-cann-910b-ops_9.0.0_linux-aarch64.run --install

# Install NNAL
chmod +x Ascend-cann-nnal_9.0.0_linux-aarch64.run
./Ascend-cann-nnal_9.0.0_linux-aarch64.run --install

# Set environment
source /usr/local/Ascend/ascend-toolkit/set_env.sh
source /usr/local/Ascend/nnal/atb/set_env.sh
```

### 2. Install PyTorch + torch-npu

```bash
# Create virtual environment
conda create -n vllm-ascend python=3.11 -y
conda activate vllm-ascend

# Install PyTorch
pip install torch==2.9.0

# Install torch-npu
pip install torch-npu==2.9.0
```

### 3. Install vLLM + vLLM-Ascend

```bash
# Clone and install vLLM
git clone https://github.com/vllm-project/vllm.git
cd vllm
pip install -e .[dev]

# Clone and install vLLM-Ascend
git clone https://github.com/vllm-project/vllm-ascend.git
cd vllm-ascend
pip install -e .[dev]
```

## Environment Configuration

### A3 Series (Required)

```bash
export ASCEND_ENABLE_USE_FABRIC_MEM=1
export ASCEND_BUFFER_POOL=4:8
export HCCL_OP_EXPANSION_MODE=AIV
```

### A2 Series (Required)

```bash
export HCCL_INTRA_ROCE_ENABLE=1
```

### Common Variables

```bash
export ASCEND_HOME_PATH=/usr/local/Ascend/ascend-toolkit/latest
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export VLLM_ASCEND_ENABLE_NZ=1
export HCCL_RDMA_TIMEOUT=17
export PYTHONHASHSEED=0
```

## Verification

```python
import torch
import torch_npu
import vllm
import vllm_ascend

print(f"PyTorch: {torch.__version__}")
print(f"torch-npu: {torch_npu.__version__}")
print(f"NPU available: {torch.npu.is_available()}")
print(f"NPU count: {torch.npu.device_count()}")
print(f"vLLM: {vllm.__version__}")
```

## Common Issues

### libatb.so: cannot open shared object file

```bash
source /usr/local/Ascend/nnal/atb/set_env.sh
```

### Failed to infer device type

```bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
```

### NPU not available

```bash
# Check NPU status
npu-smi info

# Check device permissions
ls -l /dev/davinci*

# Check environment
echo $ASCEND_RT_VISIBLE_DEVICES
```

## Quick Start

```python
from vllm import LLM, SamplingParams

llm = LLM(
    model="Qwen/Qwen2-7B",
    device="npu",
    tensor_parallel_size=1
)

sampling_params = SamplingParams(temperature=0.7, max_tokens=100)
outputs = llm.generate(["Hello, how are you?"], sampling_params)
print(outputs[0].outputs[0].text)
```

## References

- [vLLM-Ascend GitHub](https://github.com/vllm-project/vllm-ascend)
- [CANN Documentation](https://www.hiascend.com/document/detail/zh/canncommercial/)
- [vLLM Documentation](https://docs.vllm.ai/)
