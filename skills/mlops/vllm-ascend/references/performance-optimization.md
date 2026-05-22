# vLLM-Ascend Performance Optimization Patterns

## Optimization Categories

| Category | Method | Typical Gain |
|----------|--------|--------------|
| **Operator Replacement** | Use more efficient operator | 3-10% |
| **Async Execution** | Independent stream overlap | 2-5% |
| **Sync Removal** | Remove unnecessary syncs | 5-20% |
| **Memory Optimization** | Weak ref, memory pool | Avoid OOM |
| **Communication Fusion** | Fuse communication ops | 10-30% |
| **Tiling Optimization** | Optimize block strategy | 5-15% |

## Pattern 1: Operator Replacement

**Example**: Replace `npu_fusion_attention` with `_npu_flash_attention_unpad`

**Before**:
```python
context_layer = torch_npu.npu_fusion_attention(
    query=query, key=key, value=value,
    actual_seq_qlen=seq_lens_cpu,
    actual_seq_kvlen=seq_lens_cpu,
    head_num=head_num,
    scale=scale_value,
    input_layout="TND",
)[0]
```

**After**:
```python
context_layer = torch.empty_like(query)
torch_npu._npu_flash_attention_unpad(
    query=query, key=key, value=value,
    seq_len=seq_lens_cpu,
    scale_value=scale_value,
    num_heads=head_num,
    num_kv_heads=num_kv_heads,
    out=context_layer,
)
```

**Result**: 290 tps → 300 tps (+3.4%)

**PR**: `c9aff2b0` - Replace npu_fusion_attention with _npu_flash_attention_unpad

## Pattern 2: Async Stream Execution

**Problem**: Synchronous copy blocks computation

**Solution**: Use independent stream for async copy

```python
def _copy_valid_sampled_token_count(self, next_token_ids, valid_sampled_tokens_count):
    if self.valid_sampled_token_count_event is None:
        return

    # Create independent stream to overlap copy with draft model prepare_input
    with torch.npu.stream(self.valid_sampled_token_count_copy_stream):
        # Wait for current stream to finish
        self.valid_sampled_token_count_copy_stream.wait_stream(torch.npu.current_stream())
        
        # Async copy
        counts = valid_sampled_tokens_count
        counts_cpu = self.valid_sampled_token_count_cpu
        assert counts_cpu is not None
        counts_cpu[:counts.shape[0]].copy_(counts, non_blocking=True)
        
        # Record event for synchronization
        self.valid_sampled_token_count_event.record()

    # Stash for GPU-side correction if needed
    if self.use_async_spec_decode:
        self.valid_sampled_token_count_gpu = valid_sampled_tokens_count
    self.input_batch.prev_sampled_token_ids = next_token_ids.unsqueeze(1)
```

**Result**: 878 tps → 899 tps (+2.4%)

**PR**: `3e1b977b` - Asynchronous Scheduling Issuance Bubble Optimization

## Pattern 3: Conditional Synchronization

**Problem**: Synchronization added for one mode affects all modes

**Before**:
```python
if not self.enable_enpu and not is_draft_eagle:
    torch.npu.current_stream().synchronize()
entry.aclgraph.replay()
```

**After**:
```python
# Only sync when actually needed (FULL mode only)
is_draft_eagle = _EXTRA_CTX.is_draft_model and self.use_eagle
need_sync = self.runtime_mode == CUDAGraphMode.FULL and not is_draft_eagle

if not self.enable_enpu and need_sync:
    torch.npu.current_stream().synchronize()
entry.aclgraph.replay()
```

**PR**: `894798ba` - Remove sync for PIECEWISE

## Pattern 4: Workspace Memory Release

**Problem**: Graph capture workspace persists, causing OOM

**Solution**: Use weak references to release immediately

```python
from vllm_ascend.utils import weak_ref_tensors

def weak_ref_workspaces(params):
    if params is None:
        return
    for num_tokens in params.workspaces:
        if params.workspaces[num_tokens] is not None:
            params.workspaces[num_tokens] = weak_ref_tensors(params.workspaces[num_tokens])

# In graph capture
with torch.npu.graph(aclgraph, pool=self.graph_pool):
    output = self.runnable(*args, **kwargs)
    
    # Release output immediately if safe
    if self.aclgraph_options.weak_ref_output:
        output = weak_ref_tensors(output)

# Always release workspaces
weak_ref_workspaces(_graph_params)
weak_ref_workspaces(_draft_graph_params)
weak_ref_workspaces(_draft_graph_prefill_params)
```

**PR**: `d89046d8` - Fix the graph capturing OOM

## Pattern 5: Memory Budget Planning

**Problem**: Graph capture and KV cache compete for same memory budget

**Solution**: Track separately, provide user guidance

```python
# During profiling, track separately
peak_activation_memory = ...
non_torch_memory = ...

# Graph capture returns actual consumption
graph_pool_bytes = capture_model(...)

# Calculate available KV cache
total_budget = total_memory * gpu_memory_utilization
available_kv = total_budget - weights - peak_activation - non_torch - graph_pool_bytes

# Log suggestion for users
logger.info(
    f"Free memory on device ({free:.2f}/{total:.2f} GiB). "
    f"Actual usage: {weights:.2f} GiB for weights, "
    f"{peak_activation:.2f} GiB for peak activation, "
    f"{non_torch:.2f} GiB for non-torch memory, "
    f"{graph_pool:.2f} GiB for NPU graph memory. "
    f"Replace gpu_memory_utilization with --kv-cache-memory={available_kv} "
    f"to skip profiling on future runs."
)
```

**PR**: `65289ca8` - Account for Graph Capture Memory in KV Cache Planning

## Pattern 6: Communication Optimization (HCCL)

**Environment Variables**:
```bash
# Use AIV mode for better performance
export HCCL_OP_EXPANSION_MODE=AIV

# Increase buffer size
export HCCL_BUFFSIZE=1024

# Set network interface
export HCCL_IF_IP=10.0.0.102
export HCCL_SOCKET_IFNAME=eth0
```

**Code Pattern**:
```python
# Enable AIV mode at runtime
os.environ["HCCL_OP_EXPANSION_MODE"] = "AIV"
```

## Pattern 7: Avoid CPU-NPU Sync

**Problem**: `.item()` triggers synchronous transfer

**Bad**:
```python
for i in range(num_tokens):
    value = tensor[i].item()  # Sync each iteration!
```

**Good**:
```python
# Batch transfer
values = tensor[:num_tokens].cpu().numpy()  # Single transfer
for i in range(num_tokens):
    value = values[i]
```

## Pattern 8: In-Place Operations

**Bad**:
```python
x = x + y      # Creates new tensor
x = x * scale  # Creates another new tensor
```

**Good**:
```python
x.add_(y)           # In-place
x.mul_(scale)       # In-place
```

## Pattern 9: Batch Operations

**Bad**:
```python
for block in blocks:
    process_block(block)  # N separate kernel launches
```

**Good**:
```python
process_blocks(blocks)  # Single batched kernel
```

## Pattern 10: Graph Mode Selection

| Mode | Use Case | Performance |
|------|----------|-------------|
| FULL | Simple models, fixed batch | Best |
| PIECEWISE | Complex models, variable batch | Good |
| FULL_DECODE_ONLY | Decode-only workloads | Best for decode |
| FULL_AND_PIECEWISE | Hybrid attention | Balanced |

```python
# Select mode
--compilation-config '{"cudagraph_mode": "piecewise"}'

# Or capture specific sizes
--compilation-config '{"cudagraph_capture_sizes": [1, 2, 4, 8, 16, 32]}'
```

## Performance Profiling Workflow

### 1. Identify Bottleneck

```bash
# Enable profiler
--profiler-config '{"profiler": "torch", "torch_profiler_dir": "./profile"}'

# At runtime
curl -X POST http://localhost:8080/start_profile
# ... run workload ...
curl -X POST http://localhost:8080/stop_profile
```

### 2. Analyze Results

```python
from torch_npu.profiler.profiler import analyse
analyse("./profile/*_ascend_pt/")

# Check files:
# - trace_view.json (Chrome Tracing)
# - operator_details.csv
# - kernel_details.csv
# - op_statistic.csv
```

### 3. Apply Optimization

Based on analysis:
- High operator time → Consider operator replacement
- High communication time → Enable HCCL optimizations
- High memory usage → Apply memory optimization patterns

### 4. Verify Improvement

```bash
# Benchmark before/after
python benchmarks/benchmark_serving.py \
    --model Qwen/Qwen3-30B-A3B \
    --dataset sharegpt \
    --num-prompts 1000
```

## Common Performance Issues

### Issue: Low GPU Utilization

**Causes**:
- Too many small kernels
- Excessive synchronization
- CPU-bound operations

**Solutions**:
- Batch operations
- Remove unnecessary syncs
- Use async execution

### Issue: High TTFT

**Causes**:
- Large prefill without chunking
- Communication overhead

**Solutions**:
- Enable chunked prefill
- Use PD disaggregation
- Optimize HCCL settings

### Issue: High TPOT

**Causes**:
- Small batch size
- Preemption
- Decode bottleneck

**Solutions**:
- Increase concurrency
- Increase KV cache
- Use FULL_DECODE_ONLY mode

### Issue: Memory Fragmentation

**Causes**:
- Dynamic allocation/deallocation
- Long running process

**Solutions**:
```bash
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
```

## Benchmark Commands

```bash
# Throughput benchmark
python benchmarks/benchmark_serving.py \
    --model Qwen/Qwen3-30B-A3B \
    --tensor-parallel-size 2 \
    --dataset sharegpt

# Latency benchmark
python benchmarks/benchmark_latency.py \
    --model Qwen/Qwen3-30B-A3B \
    --batch-size 1

# Multi-node benchmark
python benchmarks/benchmark_serving.py \
    --model deepseek-ai/DeepSeek-V3 \
    --tensor-parallel-size 8 \
    --pipeline-parallel-size 2
```
