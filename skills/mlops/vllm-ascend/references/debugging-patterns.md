# vLLM-Ascend Debugging and Issue Resolution Patterns

## PR Type Distribution (3168+ commits)

| Type | Count | Description |
|------|-------|-------------|
| CI | 67+ | CI/CD improvements |
| BugFix | 50+ | Bug fixes |
| Doc | 39+ | Documentation |
| Feature | 34+ | New features |
| Misc | 20+ | Miscellaneous |
| Test | 12+ | Test improvements |
| Performance | 7+ | Performance optimizations |
| Refactor | 6+ | Code refactoring |

## Common BugFix Patterns

### 1. None Guard Pattern

**Problem**: Optional config objects accessed without None check
**Symptom**: `TypeError: 'NoneType' object is not iterable` or `AttributeError`

**Solution**:
```python
# Before (buggy)
for layer in self.all_moe_layers:
    ...

# After (fixed)
if self.all_moe_layers is not None:
    for layer in self.all_moe_layers:
        ...
```

**Example PR**: `7d90f709` in `vllm_ascend/ops/fused_moe/fused_moe.py`

### 2. Locale/Subprocess Parsing Pattern

**Problem**: Subprocess output parsing fails in non-English environments
**Symptom**: Parsing errors, unexpected output format

**Solution**:
```python
import os
import subprocess

# Force C locale for consistent output
env = os.environ.copy()
env['LC_ALL'] = 'C'
env['LANG'] = 'C'
env['LC_MESSAGES'] = 'C'

result = subprocess.run(cmd, env=env, capture_output=True, text=True)
```

**Example PR**: `0cef5b09` in `vllm_ascend/cpu_binding.py`

### 3. NZ Format Compatibility Pattern

**Problem**: Fused MC2 operators require NZ format but receive ND format
**Symptom**: Shape mismatch, operator failures

**Solution**:
```python
from vllm_ascend.utils import ACL_FORMAT_FRACTAL_NZ

if envs_ascend.VLLM_ASCEND_ENABLE_FUSED_MC2:
    weight = torch_npu.npu_format_cast(weight, ACL_FORMAT_FRACTAL_NZ)
else:
    weight = maybe_trans_nz(weight)
```

### 4. Stream Synchronization Pattern

**Problem**: Async operations complete out of order
**Symptom**: Incorrect results, race conditions

**Solution**:
```python
# Before graph replay, synchronize
if need_sync:
    torch.npu.current_stream().synchronize()
entry.aclgraph.replay()
```

## Debugging Workflow

### Step 1: Reproduce the Issue

```bash
# Enable debug logging
export VLLM_LOGGING_LEVEL=DEBUG

# Run with minimal config
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen3-0.6B \
    --enforce-eager \
    --tensor-parallel-size 1
```

### Step 2: Collect Environment Info

```bash
# Use project's collect_env.py
python collect_env.py

# Check NPU status
npu-smi info
```

### Step 3: Profile if Performance Issue

```bash
# Enable profiler
--profiler-config '{"profiler": "torch", "torch_profiler_dir": "./profile"}'

# Analyze
python -c "from torch_npu.profiler.profiler import analyse; analyse('./profile/*_ascend_pt/')"
```

### Step 4: Isolate the Problem

- Try `--enforce-eager` to disable ACL Graph
- Reduce `--tensor-parallel-size` to 1
- Try different model sizes
- Check if issue is model-specific or general

## Common Error Messages and Solutions

### "libatb.so not found"

**Cause**: NNAL not installed
**Solution**:
```bash
wget https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/CANN/CANN%209.0.0/Ascend-cann-nnal_9.0.0_linux-$(uname -i).run
chmod +x Ascend-cann-nnal_9.0.0_linux-$(uname -i).run
./Ascend-cann-nnal_9.0.0_linux-$(uname -i).run --install
source /usr/local/Ascend/nnal/atb/set_env.sh
```

### "ASCEND_LAUNCH_BLOCKING is incompatible with ACL Graph"

**Cause**: Debug mode conflicts with graph capture
**Solution**:
```bash
unset ASCEND_LAUNCH_BLOCKING
```

### "Out of memory" during graph capture

**Cause**: Too many graph sizes or large batch sizes
**Solution**:
```bash
# Reduce batch sizes
--max-num-seqs 64  # instead of 128

# Or use piecewise mode (default)
--compilation-config '{"cudagraph_mode": "piecewise"}'
```

### "HCCL communication timeout"

**Cause**: Network misconfiguration or timeout too short
**Solution**:
```bash
export HCCL_RDMA_TIMEOUT=17
export ASCEND_CONNECT_TIMEOUT=10000
export ASCEND_TRANSFER_TIMEOUT=10000
```

## Testing Your Fix

### Unit Tests

```bash
# Run specific test
pytest tests/ut/ops/test_fused_moe.py -v

# Run all unit tests
pytest tests/ut/ -v
```

### E2E Tests

```bash
# Single card
pytest tests/e2e/nightly/single_node/singlecard/ -v

# Multi card (requires hardware)
pytest tests/e2e/nightly/single_node/multicard_ops_a2/ -v
```

### Format and Lint

```bash
# Must pass before PR
bash format.sh ci
```

## Advanced BugFix Patterns (From PR Analysis)

### 5. Quantization Accuracy Pattern

**Problem**: `routed_scaling_factor` not propagated to expert selection
**Symptom**: Accuracy degradation in DeepSeek-V2/V3 models
**Root Cause**: vLLM upstream sets `routed_scaling_factor=1.0` when `apply_routed_scale_to_output=True`, but vLLM-Ascend uses its own forward path

**Solution**:
```python
# Save original value before super().__init__ modifies it
self._original_routed_scaling_factor = kwargs.get("routed_scaling_factor", 1.0)
super().__init__(*args, **kwargs)

# Use original value in expert selection
topk_weights, topk_ids = select_experts(
    ...,
    routed_scaling_factor=self._original_routed_scaling_factor,
)

# Apply scaling if needed
if routed_scaling_factor != 1.0:
    topk_weights = topk_weights * routed_scaling_factor
```

**Example PR**: `8486a744` - Fix quantization accuracy bug

### 6. EPLB Expert Count Mismatch Pattern

**Problem**: Confusion between logical and physical expert counts
**Symptom**: `AssertionError: Number of global experts mismatch (excluding redundancy)`
**Root Cause**: vLLM upstream distinguishes logical experts (router_logits) from physical experts (logical + EPLB replicas). Ascend code used `moe_config.num_experts` (physical) where logical count was needed.

**Solution**:
```python
from vllm_ascend.quantization.methods.base import get_moe_num_logical_experts

# Get correct logical expert count
num_logical_experts = get_moe_num_logical_experts(
    layer, num_experts,
    global_redundant_expert_num=global_redundant_expert_num,
    num_shared_experts=num_shared_experts,
)

# Use for: router validation, expert selection, zero expert handling
# Physical count for: dispatch, redundant expert handling
```

**Example PR**: `c7749799` - Fix Ascend MoE routing expert count with EPLB

### 7. KV Transfer Failure Pattern (PD Disaggregation)

**Problem**: KV cache transmission failures not handled properly
**Symptom**: Requests hang, resources leak, inconsistent state
**Root Cause**: No error tracking for failed blocks, no cleanup signal

**Solution**:
```python
# 1. Mark failed blocks as invalid
# 2. Add FAILED_SENDING_MSG signal between producer/consumer
# 3. Track invalid block IDs for retry

class MooncakeLayerwiseConnector:
    FAILED_SENDING_MSG = "FAILED_SENDING_MSG"
    
    def handle_transfer_failure(self, block_ids):
        # Mark blocks invalid
        for block_id in block_ids:
            self.invalid_blocks.add(block_id)
        # Signal consumer
        self._send_signal(self.FAILED_SENDING_MSG)
        # End request gracefully
        self.scheduler.end_request(request_id)
```

**Example PR**: `4b3a2af7` - Fix for transmit kv cache failure
**Fixes**: #7871, #8427

### 8. Graph Capture OOM Pattern

**Problem**: Workspace memory not released during graph capture
**Symptom**: OOM as number of captured graphs increases
**Root Cause**: Each graph's workspace persists after capture

**Solution**:
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
    output = weak_ref_tensors(output)  # Release immediately

# Always release workspaces
weak_ref_workspaces(_graph_params)
```

**Example PR**: `d89046d8` - Fix the graph capturing OOM in model_runner_v2

### 9. KV Cache Memory Planning Pattern

**Problem**: Graph capture memory not accounted in KV cache planning
**Symptom**: Unexpected OOM or smaller-than-expected KV cache
**Root Cause**: `gpu_memory_utilization` budget shared between graph capture and KV cache

**Solution**:
```python
# Track separately during profiling
peak_activation_memory = ...
non_torch_memory = ...
graph_pool_bytes = capture_model(...)  # Returns actual consumption

# Calculate available KV cache
available = total_memory * gpu_memory_utilization - weights - peak_activation - non_torch - graph_pool

# Output suggestion for future runs
logger.info(f"Replace gpu_memory_utilization with --kv-cache-memory={available}")
```

**Example PR**: `65289ca8` - Account for Graph Capture Memory in KV Cache Planning

### 10. PIECEWISE Performance Regression Pattern

**Problem**: Unnecessary synchronization in PIECEWISE mode
**Symptom**: Severe TPOT regression in PIECEWISE mode
**Root Cause**: Hard barrier added for FULL mode was applied to PIECEWISE too

**Solution**:
```python
# Only sync when actually needed
is_draft_eagle = _EXTRA_CTX.is_draft_model and self.use_eagle
need_sync = self.runtime_mode == CUDAGraphMode.FULL and not is_draft_eagle

if not self.enable_enpu and need_sync:
    torch.npu.current_stream().synchronize()
entry.aclgraph.replay()
```

**Example PR**: `894798ba` - Remove sync for PIECEWISE
**Related Issues**: #4233, #8877, #8854

## PR Templates

### BugFix PR Template

```markdown
[BugFix] Brief description (#PR_number)

### What this PR does / why we need it?
- Problem description
- Root cause analysis
- Solution approach

fixes: #issue_number

### Does this PR introduce _any_ user-facing change?
Yes/No (if Yes, describe)

### How was this patch tested?
```bash
pytest tests/path/to/test.py -v
```
Test result: PASSED

- vLLM version: X.Y.Z
- vLLM main: https://github.com/vllm-project/vllm/commit/SHA
```

### Feature PR Template

```markdown
[Feature] Brief description (#PR_number)

### What this PR does / why we need it?
- Feature description
- Use case
- Implementation approach

### Does this PR introduce _any_ user-facing change?
Yes, new parameter/feature: --new-param

### How was this patch tested?
Test coverage description

- vLLM version: X.Y.Z
```

### Performance PR Template

```markdown
[Performance] Brief description (#PR_number)

### What this PR does / why we need it?
- Performance issue description
- Benchmark before/after
- Optimization approach

### Does this PR introduce _any_ user-facing change?
No

### How was this patch tested?
Performance benchmark results
```

## CI Failure Patterns

### CI Installation Failure Pattern

**Problem**: All CI tasks fail at "Install vllm-ascend" step
**Symptom**: Multiple jobs fail, all at installation step (not test step)

**Diagnosis**:
1. Check if failures are consistent across all jobs → environment/dependency issue
2. Check if failures are in specific Python version → version compatibility issue
3. Check if failures are in specific vLLM version → upstream compatibility issue
4. Check recent main branch merges → possible breaking change from recent PR

**Investigation Steps**:
```bash
# 1. Check CI run details
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/commits/{sha}/check-runs"

# 2. Get job details to find exact failed step
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/actions/jobs/{job_id}"

# 3. Open browser to view logs (if API access denied)
start "https://github.com/vllm-project/vllm-ascend/actions/runs/{run_id}"
```

**Common Causes**:
- Recent main branch PR introduced breaking change (check PR #9155 "Main2main" syncs)
- Dependency version mismatch (torch-npu, CANN)
- Syntax error in recently modified files
- Import error due to missing module

**Resolution**:
1. View logs in browser (API often returns 403 for logs)
2. Check if issue is in your PR code or environment
3. If environment issue, wait for CI fix or report in PR comments
4. If code issue, fix and push new commit

### CI Test Failure Pattern

**Problem**: Installation succeeds but tests fail
**Symptom**: Jobs pass install step, fail at test step

**This indicates code logic issue, not environment issue.**

Focus on:
1. Test error messages
2. Stack traces
3. Test configuration differences

## PR Checklist

- [ ] Title format: `[Type][Module] Description` (Type: BugFix/Feature/Performance/Doc/CI/Test/Misc/Refactor)
- [ ] Signed-off-by in commit (`git commit -s`)
- [ ] What/Why section in description
- [ ] User-facing change documented (Yes/No)
- [ ] How tested section with actual commands
- [ ] vLLM version specified
- [ ] Unit tests pass (`pytest tests/ut/`)
- [ ] Format check passes (`bash format.sh ci`)
- [ ] Related issues linked (`fixes: #xxx`)
