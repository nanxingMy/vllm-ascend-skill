# How vLLM-Ascend Works

## Core Concept

vLLM-Ascend is the **bridge** between vLLM and Huawei Ascend NPU:
- **Upward**: Implements vLLM's Platform interface
- **Downward**: Calls Ascend NPU operators and runtime
- **Middle**: Provides high-performance adaptation and optimization

## Software Stack

```
User Application (LLM.generate())
         ↓
vLLM Core Engine (Scheduler, Model Executor, KV Cache)
         ↓
vLLM-Ascend Plugin (NPUPlatform, NPUWorker, NPUModelRunner, Custom Ops)
         ↓
Ascend Software Stack (torch-npu, CANN, ATB/ACL)
         ↓
Ascend NPU Hardware (Atlas A2/A3/A5/310P)
```

## Core Components

### 1. NPUPlatform (vllm_ascend/platform.py)

**Purpose**: Platform abstraction layer - tells vLLM this is an NPU platform

**Key methods**:
- `get_attn_backend()` - Returns NPU-supported attention backend
- `get_device_name()` - Returns "npu"
- `is_cuda()` - Returns False (not CUDA)
- `check_device_capability()` - Checks device capabilities

**Inheritance**: `NPUPlatform(Platform)` - inherits from vLLM Platform base class

**Critical**: Before adding any method to NPUPlatform, CHECK if Platform base class already has it!

### 2. NPUWorker (vllm_ascend/worker/worker.py)

**Purpose**: Worker process - manages NPU device and executes model inference

**Key methods**:
- `init_device()` - Initialize NPU device
- `execute_model()` - Execute model inference
- `check_health()` - Check NPU health status
- `shutdown()` - Close and release resources

**Workflow**:
1. init_device() - Initialize NPU
2. Load model to NPU
3. execute_model() - Execute inference
4. Return results
5. shutdown() - Clean up resources

### 3. NPUModelRunner (vllm_ascend/worker/model_runner_v1.py)

**Purpose**: Model executor - manages model weights and KV Cache, executes forward pass

**Key methods**:
- `run()` - Execute one forward pass
- `update_config()` - Update model config
- `shutdown()` - Clean up KV Cache and weights

**Key data**:
- `model` - Model weights
- `kv_caches` - KV Cache storage
- `graph_runner` - Graph capture executor
- `attn_backend` - Attention backend

### 4. Custom Operators (vllm_ascend/ops/)

**Purpose**: NPU-specific operator implementations - replace vLLM's CUDA operators

**Key operators**:
- `attention/` - Attention operators (Flash Attention, Paged Attention)
- `quantization/` - Quantization operators (W8A8, FP8)
- `activation/` - Activation functions (SiLU, GELU)
- `normalization/` - Normalization (RMS Norm)

**Implementation**:
- Python implementation (simple operators)
- C++ implementation (performance-critical operators)
- Call CANN operator library

## Complete Workflow

### User Code
```python
from vllm import LLM
llm = LLM(model="Qwen/Qwen-7B")
output = llm.generate("Hello, world!")
```

### Execution Flow

**1. Initialization Phase**
```
LLM.__init__()
  → Create Engine
    → Select Platform (NPUPlatform)
      → Create Worker (NPUWorker)
        → init_device() - Initialize NPU
          → Create ModelRunner (NPUModelRunner)
            → Load model weights to NPU
```

**2. Inference Phase**
```
llm.generate("Hello, world!")
  → Engine.generate()
    → Scheduler.schedule()
      → Allocate KV Cache space
        → Worker.execute_model()
          → ModelRunner.run()
            → Prepare input tensors
            → Execute model forward pass
              → Embedding layer
              → Transformer layers (use NPU operators)
                → Self-Attention (Flash Attention)
                → MLP (quantization operators)
                → LayerNorm (RMS Norm)
              → LM Head
            → Sample output token
            → Update KV Cache
```

**3. Cleanup Phase**
```
Worker.shutdown()
  → ModelRunner.shutdown()
    → Clean up KV Cache
    → Clean up model weights
    → Release NPU resources
```

## Key Technologies

### 1. Paged Attention
- Efficient KV Cache management
- Reduce memory fragmentation
- Support variable-length sequences
- Memory utilization improved 2-4x

### 2. Flash Attention
- Accelerate attention computation
- Reduce memory access
- Support long sequences
- Attention computation accelerated 2-3x

### 3. Quantization
- Reduce model size
- Accelerate inference
- Lower memory usage
- Support: W8A8, W4A16, FP8, AWQ, GPTQ

### 4. Graph Capture
- Reduce operator scheduling overhead
- Optimize computation graph
- Accelerate inference
- Use torch.compile() and NPU graph capture

### 5. Distributed Inference
- Support multi-NPU inference
- Support large models
- Improve throughput
- Implement: Tensor Parallelism, Pipeline Parallelism, Expert Parallelism

## Relationship with vLLM

### Plugin Architecture

vLLM design:
- Core engine (platform-agnostic)
- Platform abstraction layer (Platform)
- Plugin mechanism

vLLM-Ascend as plugin:
- Implements Platform interface
- Provides platform-specific implementation
- Registers to vLLM

### Key Adaptation Points

**1. Platform Identification**
```python
# vLLM
if is_cuda():
    use CUDA
elif is_rocm():
    use ROCM

# vLLM-Ascend
NPUPlatform.is_cuda() → False
NPUPlatform.get_device_name() → "npu"
```

**2. Operator Replacement**
```python
# vLLM
import flash_attn  # CUDA operator

# vLLM-Ascend
from vllm_ascend.ops import flash_attn  # NPU operator
```

**3. Memory Management**
```python
# vLLM
torch.cuda.memory_allocated()

# vLLM-Ascend
torch.npu.memory_allocated()
```

**4. Device Operations**
```python
# vLLM
tensor.to("cuda")

# vLLM-Ascend
tensor.to("npu")
```

## Patch Mechanism

vLLM-Ascend uses patch mechanism to adapt vLLM:

**Patch files** (vllm_ascend/patch/):
- `patch_vllm.py` - Main patch entry
- `patch_model.py` - Model patch
- `patch_attention.py` - Attention patch
- `patch_quantization.py` - Quantization patch

**How it works**:
1. Import vLLM modules
2. Replace key functions/classes
3. Inject NPU implementations

**Example**:
```python
# Original vLLM code
def forward(x):
    return flash_attn_cuda(x)

# After vLLM-Ascend patch
def forward(x):
    return flash_attn_npu(x)
```

**Patch timing**: Happens at import time
```python
import vllm_ascend  # Automatically patches vLLM
```

## Summary

### Three Keys

1. **Adaptation** - Implement vLLM Platform interface
2. **Optimization** - High-performance NPU operators
3. **Compatibility** - Keep vLLM API unchanged

### Two Layers

1. **Platform Layer** - NPUPlatform, NPUWorker, NPUModelRunner
2. **Operator Layer** - Custom operators (ops/)

### One Mechanism

**Patch Mechanism** - Runtime replacement of vLLM implementations

### User Perspective

```python
from vllm import LLM  # Same as using CUDA
llm = LLM(model="Qwen/Qwen-7B")
# Automatically uses NPU (if vllm-ascend installed)
```

User doesn't need to care whether backend is CUDA or NPU!
