# PR Complete Workflow: Lessons Learned from Multiple PRs

This document consolidates the complete PR workflow with all user corrections and lessons learned from PRs #9149, #9199, #9205, and Issue #4112 work.

## Critical User Corrections

### 1. ALWAYS Create PR Branches from Main (NOT Other PR Branches)

**User feedback**: "为什么把上一个PR 的信息也提上来了" and "进行提交的时候记得不要把上个Issue的信息提交上去"

**Wrong workflow**:
```bash
# Currently on feature/previous-pr branch
git checkout -b feature/new-pr  # WRONG - includes all previous commits!
```

**Correct workflow**:
```bash
# Always start from main
git checkout main
git pull origin main
git checkout -b feature/new-pr  # CORRECT - clean branch

# Or in one command
git checkout -b feature/new-pr origin/main
```

**If you already made the mistake**:
```bash
# Option 1: Create clean branch and cherry-pick
git checkout -b feature/new-pr-clean origin/main
git cherry-pick <commit-hash>

# Option 2: Create clean branch and re-apply changes
git checkout -b feature/new-pr-clean origin/main
# Manually re-apply your changes

# Verify clean
git log --oneline origin/main..HEAD  # Should only show your commits
git diff --stat origin/main...HEAD   # Should match expected changes
```

**Verification before pushing**:
```bash
# Check commit history
git log --oneline -5

# Check diff size
git diff --stat origin/main...HEAD

# Expected: 2 files, +43 lines
# Bad: 36 files, +1800 lines
```

**Real example**: PR #9205 initially included commits from PR #9199 because branch was created from `bugfix/version-suffix-clean-9167` instead of `main`.

---

### 2. ALWAYS Add Tests for New Features

**User feedback**: "为什么没有增加用例" and "测试用例有没有增加"

**Requirement**:
- Every new feature should have at least one test
- Every bug fix should have a regression test
- Tests go in `tests/ut/` for unit tests, `tests/e2e/` for integration

**Test patterns by feature type**:

**Platform interface methods** (`tests/ut/test_platform.py`):
```python
def test_get_supported_vit_attn_backends(self):
    backends = NPUPlatform.get_supported_vit_attn_backends()
    self.assertIsInstance(backends, list)
    self.assertIn(AttentionBackendEnum.TORCH_SDPA, backends)

def test_get_vit_attn_backend_default(self):
    backend = NPUPlatform.get_vit_attn_backend(head_size=64, dtype=torch.float16)
    self.assertEqual(backend, AttentionBackendEnum.TORCH_SDPA)

def test_get_vit_attn_backend_with_invalid_backend(self):
    with self.assertRaises(ValueError) as context:
        NPUPlatform.get_vit_attn_backend(
            head_size=64,
            dtype=torch.float16,
            backend=AttentionBackendEnum.FLASH_ATTN,
        )
    self.assertIn("not supported", str(context.exception))
```

**Worker methods** (`tests/ut/worker/test_worker_v1.py`):
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

        # Test shutdown
        worker.shutdown()

        # Verify profiler and model_runner shutdown were called
        worker.profiler.shutdown.assert_called_once()
        worker.model_runner.shutdown.assert_called_once()
```

**Workflow**:
1. Implement feature
2. Write tests covering: happy path, edge cases, error cases
3. Run tests: `pytest tests/ut/test_xxx.py -v`
4. Add to commit

---

### 3. Check Method Dependencies Before Calling Them

**User feedback**: "这么修改正确吗？"

**Wrong approach**:
```python
# worker.py - adding shutdown that calls model_runner.shutdown()
def shutdown(self):
    if model_runner := getattr(self, "model_runner", None):
        model_runner.shutdown()  # ERROR: model_runner doesn't have shutdown()!
```

**Correct approach**:
```python
# Step 1: First add the method to model_runner
# model_runner_v1.py
def shutdown(self):
    """Release NPU resources."""
    # ... implementation ...

# Step 2: Then add the caller in worker
# worker.py
def shutdown(self):
    if model_runner := getattr(self, "model_runner", None):
        model_runner.shutdown()  # Now this works!
```

**Verification**:
```bash
# Check if method exists before adding caller
grep -n "def shutdown" vllm_ascend/worker/model_runner_v1.py

# If no output, you need to add it first!
```

**Pattern**: When implementing interface methods that delegate to other objects, check vLLM's implementation to see what methods need to exist on the delegate.

**Real example**: Issue #4112 (shutdown interface) - needed to add shutdown() to both NPUModelRunner and NPUWorker, in that order.

---

### 4. Match Existing Code Style

**User feedback**: "你先看看platform.py 接口的定义风格，最好和他们写的风格相似"

**Check existing patterns**:
```bash
# View existing method styles
grep -A 5 "def get_." vllm_ascend/platform.py | head -20
```

**Style elements to match**:
- Type annotations: Some methods have `-> str`, `-> bool`, others don't
- Docstrings: Some have short docstrings, others detailed
- Import style: Import inside method vs at top
- Naming: Follow existing naming conventions

**Example: platform.py style**:
```python
# Some methods have return type
@classmethod
def get_punica_wrapper(cls) -> str:
    return "vllm_ascend.lora.punica_npu.PunicaWrapperNPU"

# Some have parameter types
@classmethod
def get_device_name(cls, device_id: int = 0) -> str:
    ...

# Some have partial type annotations
@classmethod
def get_attn_backend_cls(cls, selected_backend, attn_selector_config, num_heads: int | None = None):
    ...
```

**How to match style**:
1. Read surrounding code (20-50 lines before/after)
2. Note which elements have type annotations
3. Note docstring style (short vs detailed)
4. Copy the pattern that matches majority

---

## Complete PR Workflow

### Step 1: Create Clean Branch from Main
```bash
git checkout main
git pull origin main
git checkout -b feature/issue-XXXX
```

### Step 2: Make Changes and Add Tests
- Implement the fix/feature
- Add comprehensive unit tests
- Verify with `git diff --stat` (should be minimal)

### Step 3: Commit and Push
```bash
git commit -s -m "[Type][Module] Description"
git push fork HEAD:feature/issue-XXXX
```

### Step 4: Create PR and Wait for Gemini Feedback
- Create PR via GitHub UI or API
- Wait 2-3 minutes for Gemini Code Assist to review
- Fetch feedback via GitHub API or check PR page

### Step 5: Iterate Based on Feedback
```bash
# Apply suggested changes
git add <files>
git commit -s -m "[Refactor] Address Gemini feedback"
git push fork HEAD:feature/issue-XXXX
```

### Step 6: Fix CI Failures

**Common CI issue: ruff format**
```bash
# Check format
ruff format --check vllm_ascend/ tests/

# Fix format
ruff format vllm_ascend/ tests/

# Commit
git add -A
git commit -s -m "[Style] Fix ruff formatting"
git push
```

**Common Gemini feedback types**:
- Use `ValueError` instead of `assert` for validation
- PR title format: `[Module][Type] Description`
- PR description must have: What/Why, User-facing change, How tested
- Code improvements (better patterns, caching)
- Unreachable code detection

---

## Real Examples from This Session

### PR #9205: ViT Attention Backend Interface

**Workflow**:
1. Created branch from main ✓
2. Added interface methods + tests ✓
3. Pushed and created PR ✓
4. Gemini suggested: Use ValueError, fix PR title ✓
5. Applied changes, pushed ✓
6. CI failed: ruff format ✓
7. Fixed format, pushed ✓
8. CI passed ✓

**Key learnings**:
- Always wait for and address Gemini feedback
- Gemini suggestions are usually correct
- Fix CI issues promptly (especially formatting)
- Iterate until all checks pass

### Issue #4112: Worker Shutdown Interface (PR #9216)

**Workflow**:
1. Initially created branch from wrong branch (included previous PR commits) ✗
2. User corrected: "为什么把上一个PR 的信息也提上来了"
3. Recreated clean branch from main ✓
4. Initially forgot to add NPUModelRunner.shutdown() ✗
5. User asked: "这么修改正确吗？"
6. Added shutdown() to NPUModelRunner first, then NPUWorker ✓
7. Initially forgot tests ✗
8. User asked: "测试用例有没有增加"
9. Added comprehensive tests (3 test cases) ✓
10. Created PR #9216 ✓
11. Gemini Code Assist provided feedback ✓
12. Applied feedback: optimize synchronize calls, add safety checks ✓
13. Total: 3 files, 90 lines (35 functional + 55 tests)

**Gemini Code Assist feedback applied**:
- Call torch.npu.synchronize() only once at start (not twice)
- Check cross_layers_kv_cache is truthy before iterating
- Check compilation_config exists before accessing (prevent AttributeError)

**Key learnings**:
- ALWAYS create branch from main, not other branches
- Check dependencies before calling methods
- ALWAYS add tests for new features
- Verify implementation correctness before pushing
- Address Gemini Code Assist feedback promptly
- Gemini suggestions are usually correct

---

## Verification Checklist

Before pushing any PR:

```bash
# 1. Check branch is from main
git log --oneline origin/main..HEAD
# Should only show your commits, not previous PR commits

# 2. Check diff size
git diff --stat origin/main...HEAD
# Should match expected changes (e.g., 2 files, +90 lines)

# 3. Check tests exist
ls tests/ut/test_*.py
# Should have corresponding test file

# 4. Run tests locally
pytest tests/ut/test_xxx.py -v
# Should pass

# 5. Check format
ruff format --check vllm_ascend/ tests/
# Should pass

# 6. Check lint
ruff check vllm_ascend/ tests/
# Should pass
```

---

## Summary

The three most critical lessons from this session:

1. **Branch hygiene**: ALWAYS create PR branches from main, never from other PR branches
2. **Test coverage**: ALWAYS add tests for new features, no exceptions
3. **Implementation correctness**: Check dependencies exist before calling them

These seem obvious in hindsight, but are easy to violate when working on multiple PRs in parallel or under time pressure. The user corrections were invaluable for catching these issues early.
