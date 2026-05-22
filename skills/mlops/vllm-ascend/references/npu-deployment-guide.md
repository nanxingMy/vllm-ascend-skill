# NPU Deployment and Testing Guide

## Environment Requirements

### Hardware
- Ascend NPU (Atlas A2/A3/A5/310P)
- Driver installed
- CANN installed

### Software
- Python >= 3.10, < 3.12
- CANN 9.0.0
- PyTorch 2.10.0
- torch-npu 2.10.0

## Step 1: Environment Setup

### Option 1: Use Docker (Recommended)

```bash
# 1. Pull official image
docker pull swr.cn-southwest-2.myhuaweicloud.com/base_image/ascend-ci/cann:9.0.0-910b-ubuntu22.04-py3.11

# 2. Start container
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

# 3. Verify NPU inside container
npu-smi info
```

### Option 2: Local Environment (requires CANN installed)

```bash
# 1. Activate CANN environment
source /usr/local/Ascend/ascend-toolkit/set_env.sh

# 2. Verify NPU
npu-smi info

# 3. Verify Python and PyTorch
python --version
python -c "import torch; import torch_npu; print(torch_npu.__version__)"
```

## Step 2: Install vLLM-Ascend

### Option 1: From PyPI (Stable)

```bash
pip install vllm-ascend

# Verify
python -c "import vllm_ascend; print(vllm_ascend.__version__)"
```

### Option 2: From Source (Development)

```bash
# 1. Clone repository
git clone https://github.com/vllm-project/vllm-ascend.git
cd vllm-ascend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install in development mode
pip install -e .

# 4. Verify
python -c "import vllm_ascend; print('vLLM-Ascend installed successfully!')"
```

## Step 3: Start Service

### Option 1: Python API (Offline Inference)

Create `test_offline.py`:
```python
from vllm import LLM, SamplingParams

# Initialize model
llm = LLM(
    model="Qwen/Qwen2.5-7B-Instruct",
    trust_remote_code=True,
    tensor_parallel_size=1,  # Single card
)

# Set sampling parameters
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=128,
)

# Generate text
prompts = [
    "Hello, please introduce yourself.",
    "What is the capital of France?",
]

outputs = llm.generate(prompts, sampling_params)

# Print results
for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}")
    print(f"Generated: {generated_text!r}")
    print("-" * 50)
```

Run:
```bash
python test_offline.py
```

### Option 2: OpenAI Compatible API (Online Service)

Start service:
```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --trust-remote-code
```

Test service:
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "messages": [
      {"role": "user", "content": "Hello, please introduce yourself."}
    ],
    "max_tokens": 128,
    "temperature": 0.7
  }'
```

### Option 3: Using Python Client

Create `test_api.py`:
```python
import requests
import json
import time

url = "http://localhost:8000/v1/chat/completions"

# Test request
data = {
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "messages": [
        {"role": "user", "content": "Hello, please introduce yourself."}
    ],
    "max_tokens": 128,
    "temperature": 0.7,
}

# Send request
start = time.time()
response = requests.post(url, json=data)
elapsed = time.time() - start

# Print result
print(f"Status: {response.status_code}")
print(f"Time: {elapsed:.2f}s")
print(f"Response:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

Run:
```bash
python test_api.py
```

## Step 4: Performance Testing

### Benchmark Script

Create `benchmark.py`:
```python
import time
from vllm import LLM, SamplingParams

# Initialize model
print("Loading model...")
start = time.time()
llm = LLM(
    model="Qwen/Qwen2.5-7B-Instruct",
    trust_remote_code=True,
    tensor_parallel_size=1,
)
print(f"Model loaded in {time.time() - start:.2f}s")

# Test different batch sizes
for batch_size in [1, 8, 16, 32]:
    prompts = ["Hello"] * batch_size
    
    sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.9,
        max_tokens=128,
    )
    
    # Warmup
    llm.generate(prompts[:1], sampling_params)
    
    # Test
    start = time.time()
    outputs = llm.generate(prompts, sampling_params)
    elapsed = time.time() - start
    
    # Calculate performance
    total_tokens = sum(len(o.outputs[0].token_ids) for o in outputs)
    throughput = total_tokens / elapsed
    
    print(f"Batch size: {batch_size}")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Throughput: {throughput:.2f} tokens/s")
    print(f"  Per request: {throughput/batch_size:.2f} tokens/s")
```

Run:
```bash
python benchmark.py
```

## Step 5: Monitoring and Debugging

### Monitor NPU Usage

```bash
# Real-time monitoring
watch -n 1 npu-smi info

# View NPU memory usage
npu-smi info -t board -i 0

# View NPU utilization
npu-smi info -t utilization -i 0
```

### Monitor vLLM Performance

Start service with performance logging:
```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --trust-remote-code \
    --enable-log-request
```

View logs:
```bash
tail -f vllm.log
```

### Debug Mode

```bash
# Enable verbose logging
export VLLM_LOGGING_LEVEL=DEBUG

# Run
python test_offline.py
```

## Step 6: Advanced Configuration

### Quantization

```bash
# INT8 quantization
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --quantization w8a8 \
    --host 0.0.0.0 \
    --port 8000

# FP8 quantization
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --quantization fp8 \
    --host 0.0.0.0 \
    --port 8000

# AWQ quantization
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct-AWQ \
    --quantization awq \
    --host 0.0.0.0 \
    --port 8000
```

### Multi-Card Inference

```bash
# 2-card tensor parallelism
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-14B-Instruct \
    --tensor-parallel-size 2 \
    --host 0.0.0.0 \
    --port 8000

# 4-card tensor parallelism
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-72B-Instruct \
    --tensor-parallel-size 4 \
    --host 0.0.0.0 \
    --port 8000
```

### KV Cache Optimization

```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --gpu-memory-utilization 0.9 \
    --max-model-len 4096 \
    --block-size 16 \
    --host 0.0.0.0 \
    --port 8000
```

## Common Issues and Solutions

### 1. Memory Insufficient

**Symptom**: OOM (Out of Memory)

**Solutions**:
- Reduce batch size
- Use quantized model
- Reduce max_model_len

### 2. Model Loading Failed

**Symptom**: Model not found

**Solutions**:
- Check model path
- Download model to local
- Use trust_remote_code=True

### 3. NPU Unavailable

**Symptom**: No NPU device found

**Solutions**:
- Check NPU driver: `npu-smi info`
- Check CANN environment: `source /usr/local/Ascend/ascend-toolkit/set_env.sh`
- Check torch-npu: `python -c "import torch_npu"`

### 4. CI Network Failure

**Symptom**: `ProtocolError: ('Connection broken: IncompleteRead(...)')`

**Diagnosis**: This is infrastructure issue, NOT code problem

**Solution**: Retry CI (click "Re-run all jobs")

## Expected Performance

### Qwen2.5-7B on Atlas A2

- First token latency: ~100-200ms
- Generation speed: ~50-100 tokens/s
- Memory usage: ~15GB

### Qwen2.5-14B on Atlas A2 (2 cards)

- First token latency: ~150-300ms
- Generation speed: ~40-80 tokens/s
- Memory usage: ~25GB per card

## Quick Start (5 minutes)

```bash
# Step 1: Verify environment (1 min)
npu-smi info
python --version
python -c "import torch; import torch_npu; print('OK')"

# Step 2: Install (2 min)
pip install vllm-ascend
python -c "import vllm_ascend; print('OK')"

# Step 3: Test (2 min)
python -c "
from vllm import LLM, SamplingParams
llm = LLM(model='Qwen/Qwen2.5-7B-Instruct', trust_remote_code=True)
outputs = llm.generate(['Hello'], SamplingParams(max_tokens=50))
print(outputs[0].outputs[0].text)
"
```

## Summary

### Key Steps

1. **Environment Setup**: Docker or local, verify NPU
2. **Install**: `pip install vllm-ascend`
3. **Start Service**: Python API or OpenAI API
4. **Test**: Offline inference or online service
5. **Monitor**: npu-smi info and logs

### Common Commands

```bash
# Verify environment
npu-smi info

# Install
pip install vllm-ascend

# Start service
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000

# Test
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model": "Qwen/Qwen2.5-7B-Instruct", "messages": [{"role": "user", "content": "Hello"}]}'

# Monitor
watch -n 1 npu-smi info
```
