# vLLM-Ascend 架构详解

## 🏗️ 整体架构

### 软件栈层次

```
┌─────────────────────────────────────┐
│   用户应用 (User Application)        │
│   - 使用 vLLM API                    │
│   - 例如：LLM.generate()             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   vLLM 核心引擎                      │
│   - 调度器 (Scheduler)               │
│   - 模型执行器 (Model Executor)      │
│   - KV Cache 管理                    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   vLLM-Ascend 插件                   │
│   - NPUPlatform (平台抽象)           │
│   - NPUWorker (工作进程)             │
│   - NPUModelRunner (模型执行)        │
│   - 自定义算子 (ops/)                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   昇腾软件栈                         │
│   - torch-npu (PyTorch NPU 后端)     │
│   - CANN (Compute Architecture)     │
│   - ATB/ACL (算子库)                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   昇腾 NPU 硬件                      │
│   - Atlas A2/A3/A5/310P              │
└─────────────────────────────────────┘
```

## 🎯 vLLM-Ascend 的定位

### 是什么？

vLLM-Ascend 是 vLLM 的昇腾 NPU 插件，让 vLLM 能在华为昇腾 NPU 上运行。

### 为什么需要？

- vLLM 原生支持 NVIDIA GPU (CUDA)
- 华为昇腾 NPU 使用不同的硬件架构
- 需要适配层来连接 vLLM 和昇腾 NPU
- vLLM-Ascend 就是这个适配层

### 核心思想

vLLM-Ascend 是 vLLM 和昇腾 NPU 之间的桥梁：
- **向上**：实现 vLLM 的 Platform 接口
- **向下**：调用昇腾 NPU 的算子和运行时
- **中间**：提供高性能的适配和优化

## 🔧 核心组件

### 1. NPUPlatform

**文件**: `vllm_ascend/platform.py`

**作用**:
- 平台抽象层
- 告诉 vLLM 这是一个 NPU 平台
- 提供 NPU 特定的配置和方法

**关键方法**:
```python
class NPUPlatform(Platform):
    def get_attn_backend(self, ...):
        # 返回 NPU 支持的注意力后端
        
    def get_device_name(self):
        return "npu"
        
    def is_cuda(self):
        return False  # 不是 CUDA
        
    def check_device_capability(self):
        # 检查 NPU 能力
```

**继承关系**:
```
Platform (vLLM 基类)
  ↓ 继承
NPUPlatform (vLLM-Ascend)
```

### 2. NPUWorker

**文件**: `vllm_ascend/worker/worker.py`

**作用**:
- 工作进程，负责模型推理
- 管理 NPU 设备
- 执行模型前向计算

**关键方法**:
```python
class NPUWorker(GPUWorker):
    def init_device(self):
        # 初始化 NPU 设备
        
    def execute_model(self, ...):
        # 执行模型推理
        
    def check_health(self):
        # 检查 NPU 健康状态
        
    def shutdown(self):
        # 关闭并释放资源
```

**工作流程**:
1. `init_device()` - 初始化 NPU
2. 加载模型到 NPU
3. `execute_model()` - 执行推理
4. 返回结果
5. `shutdown()` - 清理资源

### 3. NPUModelRunner

**文件**: `vllm_ascend/worker/model_runner_v1.py`

**作用**:
- 模型执行器
- 管理模型权重和 KV Cache
- 执行模型的前向传播

**关键方法**:
```python
class NPUModelRunner(GPUModelRunner):
    def run(self, ...):
        # 执行一次前向传播
        
    def update_config(self, ...):
        # 更新模型配置
        
    def shutdown(self):
        # 清理 KV Cache 和权重
```

**关键数据**:
- `model` - 模型权重
- `kv_caches` - KV Cache 存储
- `graph_runner` - 图捕获执行器
- `attn_backend` - 注意力后端

### 4. 自定义算子

**目录**: `vllm_ascend/ops/`

**作用**:
- 为 NPU 实现特定的算子
- 替换 vLLM 的 CUDA 算子
- 提供高性能实现

**关键算子**:

#### Attention 算子
```
ops/attention/
├─ flash_attention    # Flash Attention
└─ paged_attention    # Paged Attention
```

#### 量化算子
```
ops/quantization/
├─ w8a8              # INT8 量化
└─ fp8               # FP8 量化
```

#### 激活函数
```
ops/activation/
├─ silu              # SiLU 激活
└─ gelu              # GELU 激活
```

#### 归一化
```
ops/normalization/
└─ rms_norm          # RMS Norm
```

**实现方式**:
- Python 实现（简单算子）
- C++ 实现（性能关键算子）
- 调用 CANN 算子库

## 🔄 工作流程

### 推理请求流程

```python
# 用户代码
from vllm import LLM
llm = LLM(model="Qwen/Qwen-7B")
output = llm.generate("Hello, world!")
```

### 执行流程

#### 1. 初始化阶段

```
LLM.__init__()
  └─ 创建 Engine
     └─ 选择 Platform (NPUPlatform)
        └─ 创建 Worker (NPUWorker)
           └─ init_device() - 初始化 NPU
              └─ 创建 ModelRunner (NPUModelRunner)
                 └─ 加载模型权重到 NPU
```

#### 2. 推理阶段

```
llm.generate("Hello, world!")
  └─ Engine.generate()
     └─ Scheduler.schedule()
        └─ 分配 KV Cache 空间
           └─ Worker.execute_model()
              └─ ModelRunner.run()
                 ├─ 准备输入张量
                 ├─ 执行模型前向传播
                 │  ├─ Embedding 层
                 │  ├─ Transformer 层
                 │  │  ├─ Self-Attention
                 │  │  ├─ MLP
                 │  │  └─ LayerNorm
                 │  └─ LM Head
                 ├─ 采样输出 token
                 └─ 更新 KV Cache
```

#### 3. 清理阶段

```
Worker.shutdown()
  └─ ModelRunner.shutdown()
     ├─ 清理 KV Cache
     ├─ 清理模型权重
     └─ 释放 NPU 资源
```

## 🔌 与 vLLM 的关系

### 插件架构

vLLM 设计:
- 核心引擎（平台无关）
- 平台抽象层 (Platform)
- 插件机制

vLLM-Ascend 作为插件:
- 实现 Platform 接口
- 提供平台特定实现
- 注册到 vLLM

### 关键适配点

#### 1. 平台识别

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

#### 2. 算子替换

```python
# vLLM
import flash_attn  # CUDA 算子

# vLLM-Ascend
from vllm_ascend.ops import flash_attn  # NPU 算子
```

#### 3. 内存管理

```python
# vLLM
torch.cuda.memory_allocated()

# vLLM-Ascend
torch.npu.memory_allocated()
```

#### 4. 设备操作

```python
# vLLM
tensor.to("cuda")

# vLLM-Ascend
tensor.to("npu")
```

### Patch 机制

vLLM-Ascend 使用 patch 机制适配 vLLM:

**目录**: `vllm_ascend/patch/`

```
patch/
├─ patch_vllm.py        # 主 patch 入口
├─ patch_model.py       # 模型 patch
├─ patch_attention.py   # 注意力 patch
└─ patch_quantization.py # 量化 patch
```

**工作原理**:
1. 导入 vLLM 模块
2. 替换关键函数/类
3. 注入 NPU 实现

**示例**:
```python
# 原始 vLLM 代码
def forward(x):
    return flash_attn_cuda(x)

# vLLM-Ascend patch 后
def forward(x):
    return flash_attn_npu(x)
```

Patch 发生在导入时:
```python
import vllm_ascend  # 自动 patch vLLM
```

## 🎯 总结

### 三个关键

1. **适配 (Adaptation)**
   - 实现 vLLM 的 Platform 接口
   - 告诉 vLLM 这是 NPU 平台
   - 提供 NPU 特定的实现

2. **优化 (Optimization)**
   - 高性能的 NPU 算子
   - Paged Attention, Flash Attention
   - 量化、图捕获等优化

3. **兼容 (Compatibility)**
   - 保持 vLLM API 不变
   - 用户代码无需修改
   - 自动选择 NPU 后端

### 两个层次

1. **平台层 (Platform Layer)**
   - NPUPlatform, NPUWorker, NPUModelRunner
   - 管理设备、执行模型

2. **算子层 (Operator Layer)**
   - 自定义算子 (ops/)
   - 替换 CUDA 算子为 NPU 算子

### 一个机制

**Patch 机制**:
- 运行时替换 vLLM 的实现
- 注入 NPU 特定的代码
- 对用户透明
