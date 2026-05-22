# vLLM-Ascend Architecture Details

## Project Statistics

- Total Python code: ~82,000 lines
- Total commits: 3,168+
- Core modules: 15+

## Directory Structure

```
vllm-ascend/
├── vllm_ascend/           # Python package (~82K LOC)
│   ├── __init__.py        # Plugin registration
│   ├── platform.py        # NPUPlatform (991 lines)
│   ├── ascend_config.py   # Configuration (636 lines)
│   ├── envs.py            # Environment variables
│   ├── worker/            # Worker layer
│   │   ├── worker.py      # NPUWorker (823 lines)
│   │   ├── model_runner_v1.py  # v1 runner (~2000 lines)
│   │   └── v2/            # v2 model runner
│   ├── attention/         # Attention mechanisms
│   │   ├── attention_v1.py    # Standard (~1000 lines)
│   │   ├── mla_v1.py      # MLA (788 lines)
│   │   ├── sfa_v1.py      # SFA (577 lines)
│   │   └── context_parallel/
│   ├── ops/               # Custom operators
│   │   ├── fused_moe/     # MoE operators
│   │   ├── linear.py      # Linear layers
│   │   ├── layernorm.py   # Normalization
│   │   └── triton/        # Triton kernels
│   ├── quantization/      # Quantization
│   ├── compilation/       # Graph compilation
│   │   ├── acl_graph.py   # ACL Graph
│   │   └── passes/        # Fusion passes
│   ├── distributed/       # Distributed
│   │   ├── device_communicators/
│   │   └── kv_transfer/   # KV transfer (PD)
│   └── patch/             # Upstream patches
│       ├── platform/      # Global patches
│       └── worker/        # Worker patches
├── csrc/                  # C++ source
│   ├── kernels/           # AscendC kernels
│   ├── attention/
│   ├── moe/
│   └── torch_binding.cpp
├── tests/
│   ├── ut/                # Unit tests
│   └── e2e/               # E2E tests
└── docs/
```

## Core Classes

### NPUPlatform (platform.py)

Entry point for Ascend platform:

```python
class NPUPlatform(Platform):
    _enum = PlatformEnum.OOT
    device_name: str = "npu"
    device_type: str = "npu"
    simple_compile_backend: str = "eager"
    ray_device_key: str = "NPU"
    device_control_env_var: str = "ASCEND_RT_VISIBLE_DEVICES"
    dispatch_key: str = "PrivateUse1"
```

Key methods:
- `check_and_update_config()` - Validate and update config
- `get_compile_backend()` - Return custom compiler
- `get_pass_manager_cls()` - Graph fusion passes

### NPUWorker (worker/worker.py)

Main worker process:

```python
class NPUWorker(WorkerBase):
    def __init__(self, vllm_config, local_rank, rank, ...):
        # Register patches
        adapt_patch()
        # Register custom ops
        register_ascend_customop(vllm_config)
        ...
```

### NPUModelRunner (worker/model_runner_v1.py)

Model execution on NPU (~2000 lines).

## Supported Hardware

| Chip | SOC_VERSION | Type |
|------|-------------|------|
| Atlas A2 | ascend910b1/b2/b3/b4 | Inference/Training |
| Atlas A3 | ascend910_9391/9381/9372 | Inference/Training |
| Atlas A5 | ascend950_* | New generation |
| Atlas 310P | ascend310p1/p3/p5/p7 | Edge inference |

## Key Technologies

1. **ACL Graph**: Ascend's graph capture (like CUDA Graph)
2. **PD Disaggregation**: Prefill-Decode separation
3. **Expert Parallelism (EP)**: Large-scale MoE deployment
4. **Sequence Parallelism (SP)**: Long sequence optimization
5. **MLA**: Multi-Latent Attention (DeepSeek)
6. **SFA**: Sparse Flash Attention

## Build System

- CMake + pybind11 for C++ extensions
- AscendC for custom kernels
- setup.py for Python packaging

```bash
# Build
pip install -e .

# With custom options
MAX_JOBS=8 CMAKE_BUILD_TYPE=Release pip install -e .
```
