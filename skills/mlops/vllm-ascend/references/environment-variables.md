# vLLM-Ascend Environment Variables

Complete reference for all environment variables used by vLLM-Ascend.

## Build-Time Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_JOBS` | CPU cores | Max compile threads for package build |
| `CMAKE_BUILD_TYPE` | Release | Build type: Release, Debug, RelWithDebugInfo |
| `COMPILE_CUSTOM_KERNELS` | 1 | Whether to compile custom kernels |
| `CXX_COMPILER` | system default | C++ compiler path |
| `C_COMPILER` | system default | C compiler path |
| `SOC_VERSION` | auto-detect | Ascend chip version |
| `VERBOSE` | 0 | Verbose compilation logs |
| `ASCEND_HOME_PATH` | /usr/local/Ascend/ascend-toolkit/latest | CANN toolkit path |
| `HCCL_SO_PATH` | libhccl.so | HCCL library path |
| `VLLM_VERSION` | installed version | Override vLLM version for dev |

## Runtime Variables

### Performance Optimization

| Variable | Default | Description |
|----------|---------|-------------|
| `VLLM_ASCEND_ENABLE_NZ` | 1 | NZ format optimization: 0=off, 1=quant only, 2=always |
| `VLLM_ASCEND_ENABLE_MATMUL_ALLREDUCE` | 0 | Enable Matmul-AllReduce fusion for TP |
| `VLLM_ASCEND_ENABLE_FLASHCOMM1` | 0 | FlashComm1 optimization for large concurrency |
| `VLLM_ASCEND_FLASHCOMM2_PARALLEL_SIZE` | 0 | FlashComm2 O-matrix TP group size |
| `VLLM_ASCEND_ENABLE_MLAPO` | 1 | MLAPO optimization for DeepSeek W8A8 |
| `VLLM_ASCEND_ENABLE_FUSED_MC2` | 0 | Fused MC2: 1=dispatch_ffn_combine, 2=dispatch_gmm_combine_decode |
| `VLLM_ASCEND_FUSION_OP_TRANSPOSE_KV_CACHE_BY_BLOCK` | 1 | Use fused transpose_kv_cache_by_block |

### Scheduling

| Variable | Default | Description |
|----------|---------|-------------|
| `VLLM_ASCEND_BALANCE_SCHEDULING` | 0 | Enable balanced prefill/decode scheduling (PD-mixed only) |

### Parallelism

| Variable | Default | Description |
|----------|---------|-------------|
| `VLLM_ASCEND_ENABLE_CONTEXT_PARALLEL` | 0 | Enable context parallelism |
| `DYNAMIC_EPLB` | false | Enable dynamic expert parallel load balancing |

### Memory

| Variable | Default | Description |
|----------|---------|-------------|
| `VLLM_ASCEND_ENABLE_BATCH_MEMCPY` | auto | Batch memcpy for KV offload: 1=force, 0=disable, None=auto-detect |

### Monitoring

| Variable | Default | Description |
|----------|---------|-------------|
| `MSMONITOR_USE_DAEMON` | 0 | Enable msMonitor performance monitoring |

## SOC Version Values

### Auto-Detection

The system auto-detects chip type via `npu-smi info`:

```bash
npu-smi info -l              # Get NPU ID
npu-smi info -t board -i 0   # Get chip info
```

### Manual Values

| Hardware | SOC_VERSION |
|----------|-------------|
| Atlas A2 (910B1) | ascend910b1 |
| Atlas A2 (910B2) | ascend910b2 |
| Atlas A2 (910B2C) | ascend910b2c |
| Atlas A2 (910B3) | ascend910b3 |
| Atlas A2 (910B4) | ascend910b4 |
| Atlas A3 (9391) | ascend910_9391 |
| Atlas A3 (9381) | ascend910_9381 |
| Atlas A3 (9372) | ascend910_9372 |
| Atlas A5 | ascend950_* (auto-detected) |
| Atlas 310P1 | ascend310p1 |
| Atlas 310P3 | ascend310p3 |
| Atlas 310P5 | ascend310p5 |

## Usage Examples

### Development Build

```bash
export SOC_VERSION=ascend910b1
export CMAKE_BUILD_TYPE=Debug
export VERBOSE=1
pip install -e .
```

### Production Deployment

```bash
export VLLM_ASCEND_ENABLE_NZ=2
export VLLM_ASCEND_ENABLE_MATMUL_ALLREDUCE=1
export VLLM_ASCEND_ENABLE_FLASHCOMM1=1
export VLLM_ASCEND_BALANCE_SCHEDULING=1
```

### Large-Scale EP

```bash
export VLLM_ASCEND_ENABLE_FUSED_MC2=1
export DYNAMIC_EPLB=true
```

### Debugging

```bash
export CMAKE_BUILD_TYPE=Debug
export VERBOSE=1
# Note: ASCEND_LAUNCH_BLOCKING=1 is incompatible with ACL Graph!
```

## Incompatibilities

1. **ACL Graph + ASCEND_LAUNCH_BLOCKING=1**: Must unset `ASCEND_LAUNCH_BLOCKING` for graph capture.

2. **BALANCE_SCHEDULING + PD-disaggregated**: Balance scheduling only works in PD-mixed mode (`kv_role='kv_both'`).

3. **FUSED_MC2 constraints**:
   - `dispatch_ffn_combine`: Only for W8A8, EP<=32, non-MTP, non-dynamic-EPLB
   - `dispatch_gmm_combine_decode`: Only for decode node W8A8 MoE

## CANN Environment

CANN paths are typically set by sourcing the environment script:

```bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
```

Or manually:

```bash
export ASCEND_HOME_PATH=/usr/local/Ascend/ascend-toolkit/latest
export ASCEND_TOOLKIT_HOME=$ASCEND_HOME_PATH
export LD_LIBRARY_PATH=$ASCEND_HOME_PATH/lib64:$LD_LIBRARY_PATH
export PATH=$ASCEND_HOME_PATH/bin:$PATH
```
