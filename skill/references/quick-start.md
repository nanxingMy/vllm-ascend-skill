# 快速开始

## 🚀 5 分钟上手

### 前置条件

- ✅ 有 NPU 机器访问权限
- ✅ 已安装 CANN 9.0.0
- ✅ Python 3.10-3.11

### 步骤 1: 验证环境（1 分钟）

```bash
# 检查 NPU
npu-smi info

# 检查 Python
python --version

# 检查 torch-npu
python -c "import torch; import torch_npu; print('OK')"
```

### 步骤 2: 安装（2 分钟）

```bash
# 安装 vLLM-Ascend
pip install vllm-ascend

# 验证安装
python -c "import vllm_ascend; print('OK')"
```

### 步骤 3: 测试（2 分钟）

创建 `test.py`:

```python
from vllm import LLM, SamplingParams

# 初始化模型
llm = LLM(
    model="Qwen/Qwen2.5-7B-Instruct",
    trust_remote_code=True,
)

# 生成文本
outputs = llm.generate(
    ["你好，请介绍一下你自己。"],
    SamplingParams(max_tokens=50)
)

# 打印结果
print(outputs[0].outputs[0].text)
```

运行：

```bash
python test.py
```

### 预期结果

```
我是通义千问，由阿里云开发的大语言模型...
```

---

## 📦 详细安装

### 方式 1: Docker（推荐）

```bash
# 1. 拉取镜像
docker pull swr.cn-southwest-2.myhuaweicloud.com/base_image/ascend-ci/cann:9.0.0-910b-ubuntu22.04-py3.11

# 2. 启动容器
docker run -it \
  --device=/dev/davinci0 \
  --device=/dev/davinci_manager \
  --device=/dev/devmm_svm \
  --device=/dev/hisi_hdev \
  -v /usr/local/Ascend:/usr/local/Ascend \
  -v $(pwd):/workspace \
  -p 8000:8000 \
  swr.cn-southwest-2.myhuaweicloud.com/base_image/ascend-ci/cann:9.0.0-910b-ubuntu22.04-py3.11 \
  /bin/bash

# 3. 在容器内安装
pip install vllm-ascend
```

### 方式 2: 本地环境

```bash
# 1. 激活 CANN 环境
source /usr/local/Ascend/ascend-toolkit/set_env.sh

# 2. 安装 vLLM-Ascend
pip install vllm-ascend
```

### 方式 3: 从源码安装

```bash
# 1. 克隆仓库
git clone https://github.com/vllm-project/vllm-ascend.git
cd vllm-ascend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装
pip install -e .
```

---

## 🎯 使用方式

### 方式 1: Python API（离线推理）

```python
from vllm import LLM, SamplingParams

# 初始化
llm = LLM(
    model="Qwen/Qwen2.5-7B-Instruct",
    trust_remote_code=True,
    tensor_parallel_size=1,  # 单卡
)

# 采样参数
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=128,
)

# 生成
prompts = [
    "你好，请介绍一下你自己。",
    "What is the capital of France?",
]

outputs = llm.generate(prompts, sampling_params)

# 打印结果
for output in outputs:
    print(f"Prompt: {output.prompt}")
    print(f"Generated: {output.outputs[0].text}")
```

### 方式 2: OpenAI API（在线服务）

#### 启动服务

```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --trust-remote-code
```

#### 测试服务

```bash
# Completions API
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "prompt": "你好，请介绍一下你自己。",
    "max_tokens": 128,
    "temperature": 0.7
  }'

# Chat API
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "messages": [
      {"role": "user", "content": "你好，请介绍一下你自己。"}
    ],
    "max_tokens": 128,
    "temperature": 0.7
  }'
```

#### Python 客户端

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy",
)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-7B-Instruct",
    messages=[
        {"role": "user", "content": "你好，请介绍一下你自己。"}
    ],
    max_tokens=128,
    temperature=0.7,
)

print(response.choices[0].message.content)
```

---

## 📊 性能测试

### Benchmark 脚本

```python
import time
from vllm import LLM, SamplingParams

# 初始化
print("Loading model...")
start = time.time()
llm = LLM(
    model="Qwen/Qwen2.5-7B-Instruct",
    trust_remote_code=True,
)
print(f"Model loaded in {time.time() - start:.2f}s")

# 测试不同 batch size
for batch_size in [1, 8, 16, 32]:
    prompts = ["你好"] * batch_size
    
    sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.9,
        max_tokens=128,
    )
    
    # 预热
    llm.generate(prompts[:1], sampling_params)
    
    # 测试
    start = time.time()
    outputs = llm.generate(prompts, sampling_params)
    elapsed = time.time() - start
    
    # 计算性能
    total_tokens = sum(len(o.outputs[0].token_ids) for o in outputs)
    throughput = total_tokens / elapsed
    
    print(f"Batch size: {batch_size}")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Throughput: {throughput:.2f} tokens/s")
    print(f"  Per request: {throughput/batch_size:.2f} tokens/s")
```

### 预期性能

**Qwen2.5-7B 在 Atlas A2 上**：
- 首token延迟: ~100-200ms
- 生成速度: ~50-100 tokens/s
- 内存占用: ~15GB

---

## 🔧 高级配置

### 量化

```bash
# INT8 量化
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --quantization w8a8

# FP8 量化
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --quantization fp8
```

### 多卡推理

```bash
# 2 卡张量并行
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-14B-Instruct \
    --tensor-parallel-size 2
```

### KV Cache 优化

```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --gpu-memory-utilization 0.9 \
    --max-model-len 4096 \
    --block-size 16
```

---

## 🐛 常见问题

### 1. 内存不足

**症状**: OOM (Out of Memory)

**解决**:
- 减小 batch size
- 使用量化模型
- 减小 max_model_len

### 2. 模型加载失败

**症状**: Model not found

**解决**:
- 检查模型路径
- 下载模型到本地
- 使用 trust_remote_code=True

### 3. NPU 不可用

**症状**: No NPU device found

**解决**:
- 检查 NPU 驱动：`npu-smi info`
- 检查 CANN 环境：`source /usr/local/Ascend/ascend-toolkit/set_env.sh`
- 检查 torch-npu：`python -c "import torch_npu"`

---

## 📚 下一步

- [架构详解](architecture.md) - 理解工作原理
- [开发指南](development-guide.md) - 开始贡献代码
- [性能优化](performance.md) - 优化性能

---

## 📖 参考资源

- [vLLM-Ascend 文档](https://docs.vllm.ai/projects/ascend/)
- [vLLM 文档](https://docs.vllm.ai/)
- [昇腾文档](https://www.hiascend.com/document/)
- [GitHub](https://github.com/vllm-project/vllm-ascend)
