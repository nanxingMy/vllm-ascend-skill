# Inheritance Check Workflow

## Why This Matters

vLLM-Ascend classes inherit from vLLM base classes. Before adding any new method, you MUST check if the base class already has it. Implementing a method that's identical to the base class is redundant and will be rejected by maintainers.

## Inheritance Hierarchy

```
vLLM (upstream)
└─ vllm/platforms/interface.py
   └─ class Platform (base)
      ├─ get_attn_backend()
      ├─ get_vit_attn_backend()
      ├─ get_supported_vit_attn_backends()
      └─ ...

vLLM-Ascend (plugin)
└─ vllm_ascend/platform.py
   └─ class NPUPlatform(Platform)  ← Inherits Platform
      ├─ Automatically inherits all Platform methods
      ├─ Can override if NPU needs different logic
      └─ ...
```

Similar for:
- `NPUWorker` inherits from vLLM's `Worker`
- `NPUModelRunner` inherits from vLLM's `GPUModelRunner`
- `NPUWorker310` inherits from `NPUWorker`
- `NPUModelRunner310` inherits from `NPUModelRunner`

## Decision Tree

```
Need to add method X to NPUPlatform?
│
├─ Step 1: Check if Platform base class has X
│   │
│   ├─ NO → Safe to implement in NPUPlatform
│   │
│   └─ YES → Step 2: Does NPU need different logic?
│       │
│       ├─ YES → Override in NPUPlatform
│       │         - Document WHY different
│       │         - Add tests for NPU-specific behavior
│       │
│       └─ NO → Don't implement!
│                 - Use inherited version
│                 - Close issue with explanation
```

## Check Commands

### Check Platform Base Class

```bash
# Check if Platform has a method
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/platforms/interface.py" | grep "def <method_name>"

# Example: Check get_vit_attn_backend
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/platforms/interface.py" | grep "def get_vit_attn_backend"
# Output: 268:    def get_vit_attn_backend(
# → Base class HAS this method!
```

### Check Worker Base Class

```bash
# Check if Worker has a method
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/v1/worker/gpu_worker.py" | grep "def <method_name>"

# Example: Check shutdown
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/v1/worker/gpu_worker.py" | grep "def shutdown"
# Output: (none)
# → Base class does NOT have this method, safe to implement
```

### Check ModelRunner Base Class

```bash
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/v1/worker/gpu_model_runner.py" | grep "def <method_name>"
```

### Check NPUPlatform Inheritance

```bash
grep -n "class NPUPlatform" vllm_ascend/platform.py
# Output: 95:class NPUPlatform(Platform):
# → NPUPlatform inherits from Platform
```

## Real Examples

### Example 1: Issue #3489 - ViT Attention Backend (WRONG)

**Issue**: "Add get_vit_attn_backend interface"

**Mistake**: Implemented without checking base class

```python
# I added this to NPUPlatform (REDUNDANT!)
@classmethod
def get_supported_vit_attn_backends(cls) -> list:
    return [AttentionBackendEnum.TORCH_SDPA]

@classmethod
def get_vit_attn_backend(cls, ...):
    if backend is not None:
        # validation logic
        ...
    return AttentionBackendEnum.TORCH_SDPA
```

**Reality**: Platform base class already has this!

```python
# vllm/platforms/interface.py (already exists!)
@classmethod
def get_vit_attn_backend(cls, ...):
    if backend is not None:
        assert backend in cls.get_supported_vit_attn_backends()
        return backend
    return AttentionBackendEnum.TORCH_SDPA
```

**Result**: 
- PR rejected by maintainer @shen-shanshan
- Comment: "This is redundant, base class already has this"
- Issue closed as "not needed"

**Correct approach**:
```bash
# Step 1: Check base class
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/platforms/interface.py" | grep "def get_vit_attn_backend"
# Output: 268:    def get_vit_attn_backend(

# Step 2: Base class has it! Check if NPU needs override
# - Does NPU need different backend? NO
# - Does NPU need different validation? NO

# Step 3: Don't implement, use inherited version
# Close issue: "NPUPlatform inherits get_vit_attn_backend from Platform base class"
```

### Example 2: Issue #4112 - Worker Shutdown (CORRECT)

**Issue**: "Add shutdown method to worker"

**Check**:
```bash
# Check if Worker base class has shutdown
curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/v1/worker/gpu_worker.py" | grep "def shutdown"
# Output: (none)
```

**Result**: Base class does NOT have shutdown

**Implementation**: Safe to add to NPUWorker

```python
# vllm_ascend/worker/worker.py
def shutdown(self) -> None:
    """Shutdown the worker and release NPU resources."""
    if self.profiler is not None:
        self.profiler.shutdown()
    
    if model_runner := getattr(self, "model_runner", None):
        model_runner.shutdown()
```

**Key**: This is NPU-specific cleanup logic, not in base class.

### Example 3: When Override IS Needed

**Scenario**: NPU needs different default backend

```python
# Check base class - has get_vit_attn_backend
# But NPU needs FLASH_ATTN instead of TORCH_SDPA

@classmethod
def get_vit_attn_backend(cls, ...):
    """Override: NPU uses FLASH_ATTN by default."""
    if backend is None:
        # NPU-specific: different default
        return AttentionBackendEnum.FLASH_ATTN
    
    # Delegate to base class for validation
    return super().get_vit_attn_backend(...)
```

**This is valid** because:
1. Base class has the method (checked)
2. NPU needs different logic (documented)
3. Override provides NPU-specific behavior

## Checklist Before Adding Any Method

- [ ] 1. Identify which base class NPUPlatform/NPUWorker/NPUModelRunner inherits from
- [ ] 2. Check if base class has the method (use curl commands)
- [ ] 3. If base class has it:
  - [ ] Check if NPU needs different logic
  - [ ] If NO → Don't implement, close issue
  - [ ] If YES → Override with documentation
- [ ] 4. If base class doesn't have it:
  - [ ] Safe to implement
  - [ ] Check dependencies (does it call other methods that exist?)
  - [ ] Add tests
- [ ] 5. Verify with maintainer if unsure

## Common Mistakes

### Mistake 1: Blindly Implementing

```python
# WRONG: Implementing without checking
def some_method(self):
    # implementation
```

**Fix**: Always check base class first!

### Mistake 2: Copy-Paste from Base Class

```python
# WRONG: Exact copy of base class method
def get_vit_attn_backend(self, ...):
    # Same logic as Platform.get_vit_attn_backend
    ...
```

**Fix**: If logic is identical, don't implement!

### Mistake 3: Not Understanding Inheritance

```python
# WRONG: Thinking you MUST implement every interface
# Reality: Inheritance gives you base implementation automatically
```

**Fix**: Understand that `class NPUPlatform(Platform)` means NPUPlatform has ALL Platform methods.

## Testing Inheritance

```python
# Test that inherited method works
def test_inherited_method(self):
    """Test that NPUPlatform inherits method from Platform."""
    from vllm_ascend.platform import NPUPlatform
    from vllm.v1.attention.backends.registry import AttentionBackendEnum
    
    # Call inherited method
    backend = NPUPlatform.get_vit_attn_backend(
        head_size=64,
        dtype=torch.float16
    )
    
    # Should work without any implementation in NPUPlatform
    self.assertEqual(backend, AttentionBackendEnum.TORCH_SDPA)
```

## Quick Reference

| Class | Inherits From | Check Command |
|-------|---------------|---------------|
| NPUPlatform | Platform | `curl .../interface.py \| grep "def X"` |
| NPUWorker | Worker | `curl .../gpu_worker.py \| grep "def X"` |
| NPUModelRunner | GPUModelRunner | `curl .../gpu_model_runner.py \| grep "def X"` |
| NPUWorker310 | NPUWorker | `grep "def X" vllm_ascend/worker/worker.py` |
| NPUModelRunner310 | NPUModelRunner | `grep "def X" vllm_ascend/worker/model_runner_v1.py` |

## References

- Issue #3489 - ViT backend (rejected as redundant)
- Issue #4112 - shutdown method (correct, base class doesn't have it)
- PR #9205 - Rejected PR
- User correction: "认真学习，防止再出现类似错误"
