# Issue #4112: Adding Worker Shutdown Interface - Complete Workflow

## Issue Overview

**Issue**: #4112 - Some worker interfaces are missing
**Type**: Feature
**Difficulty**: ⭐⭐ (Medium)
**PR**: #9216

## Problem

vLLM calls certain worker interface methods that don't exist in vLLM-Ascend. One of them is `shutdown()`.

**Missing interfaces** (from issue):
- [x] check_health (already exists)
- [x] sample_tokens (completed)
- [ ] reinitialize_distributed
- [ ] reset_mm_cache
- [x] **shutdown** ← This PR
- [ ] save_sharded_state
- [x] get_kv_connector_handshake_metadata (completed)
- [ ] update_config
- [ ] reload_weights (in progress)

## Complete Workflow with User Corrections

### Step 1: Check vLLM Implementation

```bash
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/v1/worker/gpu_worker.py" | grep -A 20 "def shutdown"
```

vLLM's implementations show the pattern we need to follow.

### Step 2: Check if Dependencies Exist

**CRITICAL**: Before adding `worker.shutdown()` that calls `model_runner.shutdown()`, verify model_runner has the method!

```bash
# Check if model_runner has shutdown
grep -n "def shutdown" vllm_ascend/worker/model_runner_v1.py
# Output: (empty) - NO, it doesn't exist!
```

**User correction**: When I initially added worker.shutdown() without checking, user asked "这么修改正确吗？" (Is this modification correct?), revealing the issue.

**Conclusion**: Must add shutdown() to NPUModelRunner FIRST, then to NPUWorker.

### Step 3: Add shutdown() to NPUModelRunner

File: `vllm_ascend/worker/model_runner_v1.py`

Location: After `_prepare_multimodal_fields()` method (line ~4022)

```python
def shutdown(self) -> None:
    """Release NPU tensors (model weights, KV caches, workspace) so that
    memory is reclaimable when running in the same process."""
    from vllm.model_executor.layers.rotary_embedding import _ROPE_DICT
    from vllm.v1.worker.workspace import reset_workspace_manager

    # Synchronize all pending NPU operations before cleanup
    torch.npu.synchronize()
    
    if hasattr(self, "kv_caches") and self.kv_caches:
        for i in range(len(self.kv_caches)):
            self.kv_caches[i] = None  # type: ignore
        self.kv_caches.clear()

    if hasattr(self, "cross_layers_kv_cache") and self.cross_layers_kv_cache:
        for i in range(len(self.cross_layers_kv_cache)):
            self.cross_layers_kv_cache[i] = None  # type: ignore
        self.cross_layers_kv_cache.clear()

    if hasattr(self, "compilation_config") and self.compilation_config:
        self.compilation_config.static_forward_context.clear()
    
    self.model = None  # type: ignore[assignment]
    _ROPE_DICT.clear()

    reset_workspace_manager()
```

### Step 4: Add shutdown() to NPUWorker

File: `vllm_ascend/worker/worker.py`

Location: After `check_health()` method (line ~781)

```python
def shutdown(self) -> None:
    """Shutdown the worker and release NPU resources."""
    if self.profiler is not None:
        self.profiler.shutdown()

    # Release NPU resources held by the model runner so that memory
    # can be reclaimed when running in-process
    if model_runner := getattr(self, "model_runner", None):
        model_runner.shutdown()
```

### Step 5: Add Tests

**User correction**: Initially forgot tests. User asked "测试用例有没有增加" (Did you add test cases?)

File: `tests/ut/worker/test_worker_v1.py`

```python
@patch("vllm_ascend.utils.adapt_patch")
@patch("vllm_ascend.ops")
def test_shutdown_with_profiler(self, mock_ops, mock_adapt_patch):
    """Test shutdown method - with profiler"""
    from vllm_ascend.worker.worker import NPUWorker

    with patch.object(NPUWorker, "__init__", lambda x, **kwargs: None):
        worker = NPUWorker()
        worker.profiler = MagicMock()
        worker.model_runner = MagicMock()

        worker.shutdown()

        worker.profiler.shutdown.assert_called_once()
        worker.model_runner.shutdown.assert_called_once()

@patch("vllm_ascend.utils.adapt_patch")
@patch("vllm_ascend.ops")
def test_shutdown_without_profiler(self, mock_ops, mock_adapt_patch):
    """Test shutdown method - without profiler"""
    from vllm_ascend.worker.worker import NPUWorker

    with patch.object(NPUWorker, "__init__", lambda x, **kwargs: None):
        worker = NPUWorker()
        worker.profiler = None
        worker.model_runner = MagicMock()

        worker.shutdown()

        worker.model_runner.shutdown.assert_called_once()

@patch("vllm_ascend.utils.adapt_patch")
@patch("vllm_ascend.ops")
def test_shutdown_without_model_runner(self, mock_ops, mock_adapt_patch):
    """Test shutdown method - without model_runner"""
    from vllm_ascend.worker.worker import NPUWorker

    with patch.object(NPUWorker, "__init__", lambda x, **kwargs: None):
        worker = NPUWorker()
        worker.profiler = MagicMock()
        # No model_runner attribute

        worker.shutdown()  # Should not raise error

        worker.profiler.shutdown.assert_called_once()
```

### Step 6: Create Clean Branch from Main

**User correction**: Initially created branch from wrong branch (included previous PR commits). User asked "为什么把上一个PR 的信息也提上来了" (Why did you include information from the previous PR?)

```bash
# WRONG: Creating from current branch
git checkout -b feature/add-worker-shutdown-4112  # Includes all previous commits!

# CORRECT: Creating from main
git checkout main
git pull origin main
git checkout -b feature/add-worker-shutdown-4112-clean
```

### Step 7: Commit and Push

```bash
git add vllm_ascend/worker/model_runner_v1.py vllm_ascend/worker/worker.py tests/ut/worker/test_worker_v1.py
git commit -s -m "[Worker][Feature] Add shutdown method to NPUWorker and NPUModelRunner

What this PR does / why we need it:
This PR adds the shutdown method to NPUWorker and NPUModelRunner 
to properly release NPU resources when the worker is shutdown.

Changes:
- Add shutdown() method to NPUModelRunner
- Add shutdown() method to NPUWorker
- Add comprehensive unit tests

Reference:
- Related to #4112
- Follows vLLM gpu_worker and gpu_model_runner implementation

Does this PR introduce any user-facing change:
Yes. Users can now properly shutdown the worker to release NPU resources.

How was this patch tested:
- Code follows vLLM interface definition
- Syntax check passed
- 3 unit tests added

Signed-off-by: nanxing <1014662416@qq.com>"

git push fork HEAD:feature/add-worker-shutdown-4112
```

### Step 8: Handle Gemini Code Assist Feedback

After creating PR #9216, Gemini Code Assist provided feedback:

**Feedback 1**: torch.npu.synchronize() called twice (redundant)
- **Solution**: Call once at the start, remove duplicate calls

**Feedback 2**: Accessing compilation_config.static_forward_context may raise AttributeError
- **Solution**: Check `hasattr(self, "compilation_config") and self.compilation_config` before accessing

**Apply feedback**:
```bash
git add vllm_ascend/worker/model_runner_v1.py
git commit -s -m "[Refactor] Improve shutdown method based on Gemini feedback

Address Gemini Code Assist feedback:
- Call torch.npu.synchronize() only once at the start
- Check cross_layers_kv_cache is truthy before iterating
- Check compilation_config exists before accessing

Signed-off-by: nanxing <1014662416@qq.com>"

git push fork HEAD:feature/add-worker-shutdown-4112
```

### Step 9: Monitor CI Status

```bash
# Check CI status
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/commits/{sha}/check-runs?per_page=50"

# If CI fails, check logs and fix
```

## Key Learnings

### 1. Check Dependencies First

**Mistake**: Added worker.shutdown() calling model_runner.shutdown() without checking if model_runner has the method.

**User caught it**: "这么修改正确吗？" (Is this modification correct?)

**Fix**: Check with `grep -n "def shutdown" <file>` before adding caller.

### 2. Order Matters

**Correct order**:
1. Add method to dependency (NPUModelRunner)
2. Add caller to dependent (NPUWorker)
3. Add tests

**Why**: If you add caller first, it will fail at runtime with AttributeError.

### 3. Always Add Tests

**Mistake**: Initially forgot to add tests.

**User caught it**: "测试用例有没有增加" (Did you add test cases?)

**Fix**: Add comprehensive tests covering all scenarios (with/without profiler, with/without model_runner).

### 4. Create Clean Branch from Main

**Mistake**: Created branch from another PR branch, including all previous commits.

**User caught it**: "为什么把上一个PR 的信息也提上来了" (Why did you include information from the previous PR?)

**Fix**: Always `git checkout -b new-branch origin/main` to create clean branch.

### 5. Address Gemini Feedback Promptly

Gemini Code Assist provides valuable suggestions that should be incorporated:
- Code improvements (better patterns, error handling)
- Performance optimizations (avoid redundant calls)
- Safety checks (prevent AttributeError)

### 6. Follow vLLM Pattern

vLLM's implementation is the reference:
- Same method signature
- Same cleanup steps (adapted for NPU)
- Same error handling

**NPU-specific adaptations**:
- `torch.accelerator.synchronize()` → `torch.npu.synchronize()`
- GPU tensors → NPU tensors
- GPU resources → NPU resources

## Complete Workflow Summary

```
1. Identify missing interface from Issue #4112
2. Check vLLM implementation for reference
3. Check if dependencies exist (model_runner.shutdown?)
4. Add to dependency first (NPUModelRunner.shutdown)
5. Add to dependent second (NPUWorker.shutdown)
6. Add comprehensive tests
7. Verify diff size matches expected
8. Create clean branch from main (NOT from other PR branches)
9. Commit with sign-off
10. Push and create PR
11. Wait for Gemini Code Assist feedback
12. Apply feedback in new commit
13. Push and monitor CI
14. Iterate until all checks pass
```

## Files Modified

```
vllm_ascend/worker/model_runner_v1.py | 25 +++++++++++++++++++++++++
vllm_ascend/worker/worker.py          | 10 ++++++++++
tests/ut/worker/test_worker_v1.py     | 55 ++++++++++++++++++++++++++++++++++++++++
3 files changed, 90 insertions(+)
```

## Gemini Code Assist Feedback Applied

### Feedback 1: Redundant torch.npu.synchronize()

**Before**:
```python
if hasattr(self, "kv_caches") and self.kv_caches:
    torch.npu.synchronize()  # First call
    ...

if hasattr(self, "cross_layers_kv_cache"):
    torch.npu.synchronize()  # Second call (redundant)
    ...
```

**After**:
```python
# Synchronize all pending NPU operations before cleanup
torch.npu.synchronize()  # Single call at start

if hasattr(self, "kv_caches") and self.kv_caches:
    ...

if hasattr(self, "cross_layers_kv_cache") and self.cross_layers_kv_cache:
    ...
```

### Feedback 2: AttributeError Risk

**Before**:
```python
self.compilation_config.static_forward_context.clear()  # May raise AttributeError
```

**After**:
```python
if hasattr(self, "compilation_config") and self.compilation_config:
    self.compilation_config.static_forward_context.clear()
```

## Related

- Issue: https://github.com/vllm-project/vllm-ascend/issues/4112
- PR: https://github.com/vllm-project/vllm-ascend/pull/9216
- vLLM gpu_worker.py: https://github.com/vllm-project/vllm/blob/main/vllm/v1/worker/gpu_worker.py
- vLLM gpu_model_runner.py: https://github.com/vllm-project/vllm/blob/main/vllm/v1/worker/gpu_model_runner.py
- Skill pitfall #27: Always create PR branches from main
- Skill pitfall #30: Check method dependencies before calling them
- Skill pitfall #31: Always add tests for new features
