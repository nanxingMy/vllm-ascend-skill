# PR #9205: Adding get_vit_attn_backend Interface

**Issue**: #3489  
**PR**: #9205  
**Date**: 2026-05-15  
**Status**: Merged

## Summary

Added `get_vit_attn_backend` and `get_supported_vit_attn_backends` interfaces to NPUPlatform to support Vision Transformer (ViT) attention backends on NPU, following vLLM commit d3a6f212.

## Changes

### 1. Platform Interface Methods (vllm_ascend/platform.py)

```python
@classmethod
def get_supported_vit_attn_backends(cls) -> list:
    """Get supported ViT attention backends for NPU platform."""
    from vllm.v1.attention.backends.registry import AttentionBackendEnum
    return [
        AttentionBackendEnum.TORCH_SDPA,
    ]

@classmethod
def get_vit_attn_backend(
    cls,
    head_size: int,
    dtype: torch.dtype,
    backend = None,
):
    """
    Get the vision attention backend class of a device.
    
    NOTE: ViT Attention should be checked and override in the platform-specific
    implementation. we should not override this in any other places, like
    the model_executor/models/<model_name>.py.
    
    We check if the backend is None or not:
        1. If not, check if the backend is supported by the platform.
        2. If None, continue to the default selection logic.
    """
    from vllm.v1.attention.backends.registry import AttentionBackendEnum
    
    if backend is not None:
        supported_backends = cls.get_supported_vit_attn_backends()
        if backend not in supported_backends:
            raise ValueError(
                f"Backend {backend} is not supported for vit attention. "
                f"Supported backends are: {supported_backends}"
            )
        logger.info_once(f"Using backend {backend} for vit attention")
        return backend
    
    logger.info_once(
        f"Using default backend {AttentionBackendEnum.TORCH_SDPA} for vit attention"
    )
    return AttentionBackendEnum.TORCH_SDPA
```

### 2. Unit Tests (tests/ut/test_platform.py)

```python
def test_get_supported_vit_attn_backends(self):
    """Test get_supported_vit_attn_backends returns correct backends."""
    from vllm.v1.attention.backends.registry import AttentionBackendEnum
    
    backends = NPUPlatform.get_supported_vit_attn_backends()
    self.assertIsInstance(backends, list)
    self.assertIn(AttentionBackendEnum.TORCH_SDPA, backends)

def test_get_vit_attn_backend_default(self):
    """Test get_vit_attn_backend returns default backend when backend is None."""
    from vllm.v1.attention.backends.registry import AttentionBackendEnum
    
    backend = NPUPlatform.get_vit_attn_backend(
        head_size=64,
        dtype=torch.float16,
        backend=None,
    )
    self.assertEqual(backend, AttentionBackendEnum.TORCH_SDPA)

def test_get_vit_attn_backend_with_valid_backend(self):
    """Test get_vit_attn_backend returns the specified backend when valid."""
    from vllm.v1.attention.backends.registry import AttentionBackendEnum
    
    backend = NPUPlatform.get_vit_attn_backend(
        head_size=64,
        dtype=torch.float16,
        backend=AttentionBackendEnum.TORCH_SDPA,
    )
    self.assertEqual(backend, AttentionBackendEnum.TORCH_SDPA)

def test_get_vit_attn_backend_with_invalid_backend(self):
    """Test get_vit_attn_backend raises error for invalid backend."""
    from vllm.v1.attention.backends.registry import AttentionBackendEnum
    
    with self.assertRaises(ValueError) as context:
        NPUPlatform.get_vit_attn_backend(
            head_size=64,
            dtype=torch.float16,
            backend=AttentionBackendEnum.FLASH_ATTN,
        )
    self.assertIn("not supported for vit attention", str(context.exception))
```

## Iteration History

### Iteration 1: Initial Implementation
- Added interface methods
- Used `assert` for validation
- Committed and pushed

### Iteration 2: Gemini Feedback
**Feedback from Gemini Code Assist**:
1. Use `ValueError` instead of `assert` (assertions can be disabled)
2. Cache `supported_backends` to avoid redundant list creation
3. PR title format: Add `[Attention]` tag

**Applied**:
- Changed `assert` to `ValueError`
- Cached `supported_backends` variable
- Updated PR title to `[Attention][Feature] Add get_vit_attn_backend interface for NPU platform`

### Iteration 3: CI Failure - ruff format
**CI failed**: `lint / pre-commit` failed

**Diagnosis**:
```bash
ruff format --check vllm_ascend/platform.py tests/ut/test_platform.py
# Output: Would reformat: tests\ut\test_platform.py
#         Would reformat: vllm_ascend\platform.py
```

**Fix**:
```bash
ruff format vllm_ascend/platform.py tests/ut/test_platform.py
git add vllm_ascend/platform.py tests/ut/test_platform.py
git commit -s -m "[Style] Fix ruff formatting issues"
git push
```

### Iteration 4: CI Passed
All checks passed after formatting fix.

## Key Learnings

### 1. Always Add Tests
When adding new interface methods, always add corresponding unit tests:
- Test default behavior
- Test valid inputs
- Test invalid inputs (error cases)

### 2. Use ValueError Not Assert
Production code should use `ValueError` for input validation, not `assert`:
- `assert` can be disabled with Python `-O` flag
- `ValueError` is always enforced
- Better error messages for users

### 3. Cache Repeated Computations
When calling the same method multiple times, cache the result:
```python
# Bad
if backend not in cls.get_supported_vit_attn_backends():
    raise ValueError(f"... {cls.get_supported_vit_attn_backends()}")

# Good
supported_backends = cls.get_supported_vit_attn_backends()
if backend not in supported_backends:
    raise ValueError(f"... {supported_backends}")
```

### 4. Match Existing Code Style
Before adding code, read surrounding code to match style:
- Type annotations (present or absent)
- Docstring style (short vs detailed)
- Import style (inside method vs top)

### 5. Fix CI Issues Promptly
When CI fails on formatting:
```bash
ruff format <files>
git add <files>
git commit -s -m "[Style] Fix ruff formatting"
git push
```

### 6. Complete PR Workflow
1. Create clean branch from main
2. Implement + add tests
3. Commit and push
4. Create PR
5. Wait for Gemini feedback (2-3 minutes)
6. Apply feedback
7. Fix CI issues
8. Iterate until all checks pass

## References

- vLLM commit: d3a6f2120bb6b67fc58a3f1000d624cfb351eb05
- Issue: https://github.com/vllm-project/vllm-ascend/issues/3489
- PR: https://github.com/vllm-project/vllm-ascend/pull/9205
- Files: `vllm_ascend/platform.py`, `tests/ut/test_platform.py`

## Related Models

This interface enables ViT attention for vision models:
- Qwen2-VL
- Qwen2.5-VL
- Other vision-language models with ViT components
