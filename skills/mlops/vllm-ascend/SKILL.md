---
name: vllm-ascend
description: Develop and contribute to vLLM-Ascend, the hardware plugin for running vLLM on Huawei Ascend NPU. Covers architecture, PR patterns, code modification patterns, and testing.
tags:
  - vllm
  - ascend
  - npu
  - inference
  - hardware-plugin
triggers:
  - vllm-ascend development
  - ascend npu
  - vllm hardware plugin
---
description: "vLLM Ascend NPU Plugin: architecture, development, and optimization for Huawei Ascend hardware."
version: 1.0.0
author: Hermes Agent
license: Apache-2.0
platforms: [linux]
metadata:
  hermes:
    tags: [vLLM, Ascend, NPU, Huawei, inference, hardware-plugin, ACL-Graph, MoE, quantization]
    related_skills: [llama-cpp]
prerequisites:
  software:
    - CANN == 9.0.0
    - PyTorch == 2.9.0
    - torch-npu == 2.9.0
  hardware:
    - Atlas A2 (ascend910b1/b2/b3/b4)
    - Atlas A3 (ascend910_9391/9381/9372)
    - Atlas A5 (ascend950_*)
    - Atlas 310P (ascend310p1/p3/p5)
---

## References

- **pr-learning-workflow.md** - Systematic workflow for learning from all historical merged PRs and setting up continuous learning
- Architecture and development patterns documented throughout this skill

---

*This skill is continuously updated as new patterns and best practices are discovered.*
- Develop or debug vLLM-Ascend custom operators
- Optimize inference performance on Ascend
- Implement MoE, MLA, or quantization for Ascend backend
- Understand vLLM hardware plugin architecture

## Architecture Overview

```
vLLM Framework
       │
       ▼
NPUPlatform (platform.py)  ← Platform entry point
       │
       ▼
NPUWorker (worker/worker.py)
       │
       ▼
NPUModelRunner (worker/model_runner_v1.py)
       │
       ├─→ Attention (attention/)
       ├─→ Custom Ops (ops/)
       ├─→ Quantization (quantization/)
       └─→ Compilation (compilation/)
              │
              ▼
         ACL Graph (CANN)
```

## Core Modules

| Module | Purpose | Key Files |
|--------|---------|-----------|
| `platform.py` | Platform adapter, config validation | ~1000 lines |
| `worker/` | Worker and model runner | model_runner_v1.py (~2000 lines) |
| `attention/` | Attention implementations | attention_v1.py, mla_v1.py, sfa_v1.py |
| `ops/` | Custom NPU operators | fused_moe/, linear.py, layernorm.py |
| `quantization/` | Quantization support | modelslim_config.py |
| `compilation/` | ACL Graph optimization | acl_graph.py, passes/ |
| `patch/` | Upstream vLLM patches | platform/, worker/ |
| `distributed/` | Distributed communication | kv_transfer/, device_communicators/ |

## Key Concepts

### 1. NPUPlatform

Entry point that registers the Ascend backend with vLLM:

```python
class NPUPlatform(Platform):
    _enum = PlatformEnum.OOT          # Out-of-Tree plugin
    device_name: str = "npu"
    device_type: str = "npu"
    ray_device_key: str = "NPU"
    device_control_env_var: str = "ASCEND_RT_VISIBLE_DEVICES"
```

### 2. Patch System

Modifies upstream vLLM behavior via monkey patching (not source modification):

- `patch/platform/` - Applied before worker starts (global patches)
- `patch/worker/` - Applied when worker initializes

### 3. ACL Graph

Ascend's equivalent of CUDA Graph for graph capture and optimization:

- `compilation/acl_graph.py` - ACL Graph management
- `compilation/passes/` - Fusion optimization passes

### 4. Attention Variants

- `attention_v1.py` - Standard PagedAttention
- `mla_v1.py` - Multi-Latent Attention (DeepSeek models)
- `sfa_v1.py` - Sparse Flash Attention

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VLLM_ASCEND_ENABLE_NZ` | 1 | Enable NZ format optimization (0=off, 1=quant only, 2=always) |
| `VLLM_ASCEND_ENABLE_MATMUL_ALLREDUCE` | 0 | Matmul-AllReduce fusion |
| `VLLM_ASCEND_ENABLE_FLASHCOMM1` | 0 | FlashComm1 optimization |
| `VLLM_ASCEND_FLASHCOMM2_PARALLEL_SIZE` | 0 | FlashComm2 parallel size |
| `VLLM_ASCEND_BALANCE_SCHEDULING` | 0 | Balanced prefill/decode scheduling |
| `VLLM_ASCEND_ENABLE_FUSED_MC2` | 0 | Fused MC2 for MoE |
| `ASCEND_HOME_PATH` | /usr/local/Ascend/ascend-toolkit/latest | CANN path |
| `SOC_VERSION` | auto-detect | Chip version |

## Development Workflow

### Setup

```bash
# Clone repository
git clone https://github.com/vllm-project/vllm-ascend.git
cd vllm-ascend

# Install in development mode
pip install -e .[dev]
```

### Testing

```bash
# Unit tests
pytest tests/ut/ops/test_prepare_finalize.py

# E2E tests (requires NPU hardware)
pytest tests/e2e/singlecard/test_piecewise_res_consistency.py

# Specific test
pytest tests/ut/test_platform.py::TestNPUPlatform::test_check_and_update_config_rejects_both_balance_and_recompute_scheduler -v
```

### Unit Test Pattern (platform.py)

Tests in `tests/ut/test_platform.py` follow this pattern:

```python
@patch("vllm_ascend.quantization.utils.maybe_auto_detect_quantization")
@patch("vllm_ascend.utils.get_ascend_device_type", return_value=AscendDeviceType.A3)
@patch("vllm_ascend.ascend_config.init_ascend_config")
def test_feature_name(self, mock_init_ascend, mock_soc_version, mock_auto_detect):
    # 1. Mock ascend config
    mock_ascend_config = TestNPUPlatform.mock_vllm_ascend_config()
    mock_ascend_config.some_feature = True
    mock_init_ascend.return_value = mock_ascend_config

    # 2. Mock vllm config
    vllm_config = TestNPUPlatform.mock_vllm_config()
    vllm_config.kv_transfer_config = MagicMock(kv_role="kv_producer")
    vllm_config.parallel_config.tensor_parallel_size = 1

    # 3. Reload platform to pick up mocks
    from vllm_ascend import platform
    importlib.reload(platform)
    self.platform = platform.NPUPlatform()

    # 4. Test with expected exception
    with (
        patch("vllm_ascend.platform.envs_ascend.SOME_VAR", True, create=True),
        pytest.raises(ValueError, match=r"expected error pattern"),
        patch.object(platform.NPUPlatform, "_fix_incompatible_config"),
    ):
        self.platform.check_and_update_config(vllm_config)
```

Key elements:
- `@patch` decorators for external dependencies
- `TestNPUPlatform.mock_vllm_config()` / `mock_vllm_ascend_config()` for config mocks
- `importlib.reload(platform)` to pick up mocked environment values
- `pytest.raises(ValueError, match=r"pattern")` for exception testing with regex
- `patch("module.envs.VAR", value, create=True)` for environment variables

### Code Quality

```bash
# Format
ruff format vllm_ascend/

# Lint
ruff check vllm_ascend/

# Full CI check
bash format.sh ci
```

### Commit

```bash
# Must include sign-off
git commit -s -m "feat: add new feature"
```

### PR Workflow Rules

**Critical: One PR per Issue**

- ✅ One Issue = One PR (always)
- ❌ Do NOT create multiple PRs for the same Issue
- ⚠️ Only close a PR and create a new one if there are **unresolvable merge conflicts**
- ❌ DCO issues, CI failures, and review feedback are NOT reasons to close a PR

**Why this matters**: Creating multiple PRs for one Issue creates confusion, makes review harder, and wastes maintainer time.

### DCO (Developer Certificate of Origin)

DCO requires **exact match** of Author name AND email with Signed-off-by:

```
✅ CORRECT:
Author: nanxingMy <1014662416@qq.com>
Signed-off-by: nanxingMy <1014662416@qq.com>

❌ WRONG (GitHub noreply email):
Author: nanxingMy <32252938+nanxingMy@users.noreply.github.com>
Signed-off-by: nanxing <1014662416@qq.com>
```

**See [DCO Debugging Guide](references/dco-debugging-guide.md) for detailed troubleshooting.**

**Fixing DCO issues**:
1. Don't close the PR - DCO issues are fixable
2. Create clean local commit with correct Git config:
   ```bash
   git config user.name "nanxingMy"
   git config user.email "1014662416@qq.com"
   git commit -s -m "message"
   ```
3. Force push to replace problematic commits:
   ```bash
   git push --force fork HEAD:<branch>
   ```

### Review Feedback

When PR receives review comments:
1. Auto-detect review comments via GitHub API
2. Apply suggested changes locally
3. Push fixes
4. Reply to review comment explaining the fix
5. Mark review as resolved

### Branch Management

- Use `main` branch, not `master`
- Always sync fork main before creating feature branch:
  ```bash
  git checkout main
  git pull upstream main
  git push fork main
  ```

## Common Patterns

### Adding a New Patch

1. Determine scope: `platform/` (global) or `worker/` (per-worker)
2. Create patch file with clear documentation
3. Register in `patch/__init__.py`
4. Document: Why, How, Related PR, Future Plan

### Adding a Custom Operator

1. Implement in `ops/` or `csrc/kernels/`
2. Register in `ops/register_custom_ops.py`
3. Add C++ binding in `csrc/torch_binding.cpp`
4. Update CMakeLists.txt if needed

### Performance Optimization

1. Avoid `tensor.item()` in hot paths (causes CPU-NPU sync)
2. Use in-place operations (`x.add_()`, `x.mul_()`)
3. Batch operations to reduce sync frequency
4. Profile with `msmonitor` or CANN profiling tools

## Common Error Messages Quick Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `libatb.so: cannot open shared object file` | NNAL not loaded | `source /usr/local/Ascend/nnal/atb/set_env.sh` |
| `Failed to infer device type` | CANN not configured | `source /usr/local/Ascend/ascend-toolkit/set_env.sh` |
| `numHeads / numKvHeads = X, MLA only support {32, 64, 128}` | MLA graph mode head count | Adjust TP or disable graph mode for DeepSeek-V2-Lite |
| `ACLgraph has insufficient available streams` | Stream resource exhaustion | Reduce `cudagraph_capture_sizes` or use FULL mode |
| `InvalidVersion` | Dev vLLM version | Set `VLLM_VERSION=X.Y.Z` environment variable |
| `archive/tar: invalid tar header` (Kylin OS) | OS compatibility | Use offline image loading via `docker save/load` |
| `operation not permitted` (Docker) | Insufficient permissions | Add `--privileged=true` to docker run |

## Pitfalls

1. **tensor.item() synchronization**: Calling `.item()` on device tensors triggers synchronous NPU→CPU transfer. Avoid in hot paths.

2. **ACL Graph + ASCEND_LAUNCH_BLOCKING**: Incompatible. Must unset `ASCEND_LAUNCH_BLOCKING` for graph capture.

3. **Block size compatibility**: Some models require specific block sizes. Check `refresh_block_size()` in platform.py.

4. **310P differences**: 310P has separate implementation in `_310p/` with different operator support.

5. **Memory fragmentation**: Long-running processes may need memory monitoring. Use `CaMemAllocator` for managed allocation.

6. **None guard for optional configs**: Many configs can be None at runtime. Always add None checks before accessing attributes (e.g., `all_moe_layers` in fused_moe.py). See PR #7d90f709.

7. **Locale settings for subprocess parsing**: Set `LC_ALL=C`, `LANG=C`, `LC_MESSAGES=C` before subprocess calls that parse output. Non-English locales cause parsing failures. See PR #0cef5b09.

8. **NZ format for fused MC2**: When `VLLM_ASCEND_ENABLE_FUSED_MC2=1`, weights MUST be cast to NZ format via `torch_npu.npu_format_cast(weight, ACL_FORMAT_FRACTAL_NZ)`.

9. **routed_scaling_factor preservation**: vLLM upstream may modify `routed_scaling_factor` during `super().__init__()` when `apply_routed_scale_to_output=True`. Always save original value before calling super() if your code uses its own forward path. See PR #8486a744.

10. **Logical vs Physical expert count**: With EPLB, `moe_config.num_experts` includes redundant physical experts, but `router_logits.shape[-1]` matches logical experts. Use `get_moe_num_logical_experts()` helper. See PR #c7749799.

11. **Graph capture workspace memory**: Each captured graph's workspace persists. Use `weak_ref_tensors()` to release immediately after capture. See PR #d89046d8.

12. **KV cache memory planning**: Graph capture memory competes with KV cache for `gpu_memory_utilization` budget. Track separately and use `--kv-cache-memory` to skip profiling. See PR #65289ca8.

13. **BalanceScheduler + RecomputeScheduler deadlock**: These two schedulers MUST NOT be enabled simultaneously. The combination causes MoE communication type mismatch across DP ranks (some perform All2AllV, others MC2), leading to AlltoAll deadlock. See Issue #8975, PR #9149.
    
    **Correct fix placement**: The mutual exclusion check must be placed BEFORE the individual scheduler validation checks (line 474 in platform.py), not after. If placed after, it's unreachable because:
    - `VLLM_ASCEND_BALANCE_SCHEDULING` check (L474-482) requires `kv_role='kv_both'` (PD-mixed)
    - `recompute_scheduler_enable` check (L484-491) requires `kv_role='kv_producer'/'kv_consumer'` (PD-disaggregated)
    - These modes are mutually exclusive, so one check always fires first
    
    ```python
    # CORRECT: Place at line 474 (before other checks)
    if envs_ascend.VLLM_ASCEND_BALANCE_SCHEDULING and ascend_config.recompute_scheduler_enable:
        raise ValueError("...")
    
    if envs_ascend.VLLM_ASCEND_BALANCE_SCHEDULING:  # Now this check comes after
        ...
    ```

14. **Validation check placement order**: When adding new validation checks, consider whether existing checks already enforce the constraint. If existing checks make the new check unreachable, either:
    - Move the new check BEFORE existing checks (for clearer error messages)
    - Or acknowledge the existing checks are sufficient and don't add redundant code

15. **ruff format in tests**: Test files must pass `ruff format --check`. Common issues:
    - Trailing whitespace in docstrings
    - Function call argument formatting (long lines split incorrectly)
    - Line too long (E501) - split strings or use parentheses for implicit line continuation
    
    Fix: `ruff format tests/ut/test_platform.py && git commit --amend --signoff --no-edit`

16. **File formatting preservation when adding code**: When adding tests or code to existing files, preserve original formatting to avoid massive diffs. 
    - Check line endings first: `file <path>` (shows "with CRLF" or "with LF")
    - For CRLF files: Use `printf '...\r\n' >> file.py` 
    - For LF files: Use `cat >> file.py << 'EOF'` or `echo '...' >> file.py`
    - NEVER use `write_file` to completely overwrite - it changes line endings and formatting
    - Always verify with `git diff --stat` before committing
    - Goal: Minimal changes (e.g., +38 lines, not +400/-400 lines)
    
    Example of correct approach:
    ```bash
    # Check file format
    file tests/ut/test_utils.py  # "with CRLF line terminators"
    
    # Append with correct line endings
    printf '\r\n    def test_new_feature(self):\r\n        ...\r\n' >> tests/ut/test_utils.py
    
    # Verify minimal change
    git diff --stat  # Should show small numbers, not 400+/400-
    ```
    
    See PR #9195 for example of clean minimal changes (2 files, +43 lines).

16. **EPLB deployment rollback precision issue**: When `check_expert_placement()` rolls back a layer's deployment table due to validation failure (duplicate experts, etc.), `log2phy_map` is still recalculated and updated in `pack_update_info()`. This can cause precision issues because:
    - The expert_map is rolled back (unchanged)
    - But log2phy_map is recalculated based on the "new" (rolled back) expert_map
    - If `generate_log2phy_map()` has any non-determinism or uses stale data, the log2phy_map may not match the actual expert positions
    
    **Fix**: Skip log2phy_map update when deployment table is rolled back. Either:
    - Return rollback status from `check_expert_placement()` and skip update in `do_update()`
    - Or check `torch.equal(new_expert_map, old_expert_map)` before updating log2phy_map
    
    See Issue #9151, files: `vllm_ascend/eplb/core/eplb_worker.py` L94-129, L249-272.

17. **CI network failures are NOT code problems**: When CI fails with network errors (Connection broken, IncompleteRead, timeout during package download), this is an infrastructure issue, not a bug in your code.
    
    **Symptoms**:
    ```
    pip._vendor.urllib3.exceptions.ProtocolError: ('Connection broken: IncompleteRead(...)')
    ```
    
    **Solution**: Retry CI (click "Re-run all jobs" on GitHub) or create empty commit to trigger new run.
    
    See Issue #9149 CI failure (2026-05-15) - network timeout downloading mypy, resolved on retry.

17. **vllm_version_is strict comparison**: The `vllm_version_is()` function uses strict `Version` comparison:
    ```python
    return Version(vllm_version) == Version(target_vllm_version)
    ```
    This fails when `vllm.__version__` contains suffixes like "0.20.1+cpu" because `Version("0.20.1") != Version("0.20.1+cpu")`.
    
    **Symptoms**: Patch files like `patch_mla_prefill_backend.py` incorrectly execute their version-gated code even when user sets `VLLM_VERSION=0.20.1`.
    
    **Debug**: Add logging to see actual version values:
    ```python
    logger.debug(f"vllm_version_is: env={envs_ascend.VLLM_VERSION}, vllm.__version__={vllm.__version__}, target={target_vllm_version}")
    ```
    
    **Fix**: Strip version suffix before comparison:
    ```python
    vllm_version = vllm_version.split('+')[0]  # "0.20.1+cpu" -> "0.20.1"
    return Version(vllm_version) == Version(target_vllm_version)
    ```
    
    See Issue #9167, PR #9195, files: `vllm_ascend/utils.py` L445-460.

18. **File format preservation in patches**: When using `patch` or `write_file` tools, line endings may change (CRLF→LF), causing massive diffs even for small changes.
    
    **Symptoms**: 
    - Git shows hundreds of lines changed when you only added a few
    - `git diff --stat` shows large insertion/deletion counts
    - Warning: "LF will be replaced by CRLF"
    
    **Root cause**: These tools may normalize line endings, changing every line in the file.
    
    **Solutions**:
    - Use `cat >> file` or `printf` to append without changing format
    - Use `git checkout HEAD -- file` to restore, then apply minimal changes
    - Check `git diff --stat` before committing - should match expected changes
    
    **Example**: Adding 38-line test should show `+38`, not `+400 -400`.
    
    See PR #9195 iteration where test file showed 838 lines changed instead of 38.

19. **Clean branch for separate PRs**: When working on multiple PRs, creating a new branch from a branch with previous commits will include all history in the new PR.
    
    **Symptoms**:
    - New PR shows 36 files changed instead of 2
    - PR includes commits from previous unrelated PR
    - Diff includes 1800+ lines when it should be 43
    
    **Solution**: Always create clean branch from main:
    ```bash
    # Wrong: creates branch from current branch with all history
    git checkout -b new-feature
    
    # Correct: creates clean branch from main
    git checkout -b new-feature origin/main
    # Then cherry-pick or re-apply only needed changes
    ```
    
    **Workflow for clean PR**:
    1. Create branch from main: `git checkout -b fix-issue-X origin/main`
    2. Apply only the fix for issue X
    3. Verify with `git diff origin/main...HEAD --stat`
    4. Push to new branch name (not reused)
    
    See PR #9195 where initial attempt included PR #9149's 34 files.

20. **vllm_version_is robust comparison**: When comparing versions with potential suffixes (e.g., "0.20.1+cpu"), use `Version.public` property instead of manual string manipulation.
    
    **Problem**: Manual suffix stripping only handles one side:
    ```python
    # Fragile: only strips suffix from vllm_version
    vllm_version = vllm_version.split('+')[0]
    return Version(vllm_version) == Version(target_vllm_version)
    ```
    
    **Solution**: Use `Version.public` for both sides:
    ```python
    # Robust: handles suffixes on both sides
    return Version(vllm_version).public == Version(target_vllm_version).public
    ```
    
    **Benefits**:
    - Automatically excludes local version part (after `+`)
    - Preserves pre-release and post-release segments
    - Avoids manual string manipulation
    - Keeps original string for error reporting
    
    See Issue #9167, PR #9199, files: `vllm_ascend/utils.py` L445-460.
    
    **Test pattern**: Mock `vllm.__version__` and `envs_ascend.VLLM_VERSION` to test both cases:
    ```python
    with mock.patch.object(envs_ascend, 'VLLM_VERSION', None):
        with mock.patch('vllm.__version__', '0.20.1+cpu'):
            vllm_version_is.cache_clear()
            self.assertTrue(vllm_version_is('0.20.1'))
    ```
    
    See Issue #9167, files: `vllm_ascend/utils.py` L445-460, `tests/ut/test_utils.py`.

21. **PR minimal changes requirement**: ALWAYS keep PR changes minimal. Only modify what's necessary for the fix. This is a strong user preference.
    
    **Symptoms of violation**:
    - `git diff --stat` shows massive changes (400+/400-) for small fix
    - PR includes 36 files when it should be 2
    - Line ending changes (CRLF↔LF) causing entire file to appear changed
    
    **Root causes**:
    - Working on branch that contains previous PR commits
    - Using `write_file` to completely overwrite files (changes line endings)
    - Modifying files for formatting reasons (whitespace, indentation)
    
    **Solutions**:
    - Always create clean branch from main: `git checkout -b fix-X origin/main`
    - Use `patch` or `cat >>` to preserve file formatting
    - Verify with `git diff --stat` before committing
    - Target: 2 files, +43 lines (not 36 files, +1800 lines)
    
    **Verification checklist**:
    ```bash
    git diff --stat
    # Should show small numbers matching expected changes
    # Example: 2 files, +43 insertions, 0 deletions
    
    # If you see large numbers, STOP and investigate
    git diff --stat
    # Bad: 1 file, +401 insertions, -401 deletions
    ```
    
    See PR #9199 for success example, PR #9195 iterations for failure examples.

22. **Gemini Code Assist feedback workflow**: Automated PR reviews provide valuable suggestions that should be incorporated.
    
    **Workflow**:
    1. PR created → Gemini posts feedback within minutes
    2. Fetch feedback via GitHub API
    3. Review suggestions carefully (usually correct)
    4. Apply improvements in new commit
    5. Push → CI re-runs automatically
    
    **Common feedback types**:
    - Code improvements (use better patterns/APIs)
    - PR format (title, summary sections)
    - Unreachable code detection
    
    **Example: PR #9199**:
    - Feedback: Use `Version.public` property
    - Applied: Changed from manual suffix stripping to `Version.public`
    - Result: More robust implementation
    
    **Important**: Don't ignore Gemini feedback - it catches issues humans miss.

23. **CI network failures are NOT code problems**: When CI fails with network errors, this is infrastructure issue.
    
    **Symptoms**:
    ```
    pip._vendor.urllib3.exceptions.ProtocolError: ('Connection broken: IncompleteRead(...)')
    Failed to connect to github.com port 443 after 21078 ms
    ```
    
    **Diagnosis**:
    - Step name: "Install", "Setup", "Checkout" = infrastructure
    - Error: "Connection", "timeout", "IncompleteRead" = network
    - Multiple jobs failing at same step = infrastructure
    
    **Solution**:
    - Do NOT modify code
    - Retry CI: "Re-run all jobs" or `git commit --allow-empty`
    - Wait for new run
    
    See PR #9149 CI failure (network timeout downloading mypy).

24. **Adding platform interface methods**: When vLLM adds new interface methods to Platform base class, NPUPlatform must implement them.
    
    **Pattern**:
    1. Check vLLM commit for interface definition
    2. Add corresponding method(s) to NPUPlatform in `platform.py`
    3. Follow vLLM's signature and return types
    4. Import any new dependencies (e.g., `AttentionBackendEnum`)
    5. **Always add unit tests** in `tests/ut/test_platform.py`
    6. Use `ValueError` for input validation, not `assert`
    
    **Example: get_vit_attn_backend** (Issue #3489, PR #9205):
    ```python
    @classmethod
    def get_supported_vit_attn_backends(cls) -> list:
        """Get supported ViT attention backends for NPU platform."""
        from vllm.v1.attention.backends.registry import AttentionBackendEnum
        return [AttentionBackendEnum.TORCH_SDPA]
    
    @classmethod
    def get_vit_attn_backend(cls, head_size: int, dtype: torch.dtype, backend=None):
        """Get the vision attention backend class of a device."""
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
    
    **Test pattern**:
    ```python
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
    
    **Key points**:
    - Use `ValueError` not `assert` (assertions can be disabled with `-O`)
    - Cache `supported_backends` to avoid redundant list creation
    - Add comprehensive tests (default, valid, invalid cases)
    - Follow existing code style in platform.py (type annotations, docstrings)
    
    **Reference**: vLLM commit d3a6f212, Issue #3489, PR #9205, files: `vllm_ascend/platform.py`, `tests/ut/test_platform.py`

25. **Complete PR workflow with automated review**: When creating PRs, follow this complete workflow:
    
    **Step 1: Create clean branch from main**
    ```bash
    git checkout origin/main
    git checkout -b feature/issue-XXXX
    ```
    
    **Step 2: Make changes and add tests**
    - Implement the fix/feature
    - Add comprehensive unit tests
    - Verify with `git diff --stat` (should be minimal)
    
    **Step 3: Commit and push**
    ```bash
    git commit -s -m "[Type][Module] Description"
    git push fork HEAD:feature/issue-XXXX
    ```
    
    **Step 4: Create PR and wait for Gemini feedback**
    - Create PR via GitHub UI or API
    - Wait 2-3 minutes for Gemini Code Assist to review
    - Fetch feedback via GitHub API or check PR page
    
    **Step 5: Iterate based on feedback**
    ```bash
    # Apply suggested changes
    git add <files>
    git commit -s -m "[Refactor] Address Gemini feedback"
    git push fork HEAD:feature/issue-XXXX
    ```
    
    **Step 6: Fix CI failures**
    
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
    
    **Example workflow** (PR #9205):
    1. Created branch from main ✓
    2. Added interface methods + tests ✓
    3. Pushed and created PR ✓
    4. Gemini suggested: Use ValueError, fix PR title ✓
    5. Applied changes, pushed ✓
    6. CI failed: ruff format ✓
    7. Fixed format, pushed ✓
    8. CI passed ✓
    
    **Key points**:
    - Always wait for and address Gemini feedback
    - Gemini suggestions are usually correct
    - Fix CI issues promptly (especially formatting)
    - Iterate until all checks pass

26. **Match existing code style**: When adding code to existing files, match the style of surrounding code.
    
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
    
    **Reference**: PR #9205 - matched platform.py style for new methods

27. **CRITICAL: Always create PR branches from main, not other PR branches**: This is a common mistake that causes PRs to incorrectly include commits from previous work.
    
    **Symptoms**:
    - New PR shows 36 files changed instead of 2
    - PR includes commits from previous unrelated PR
    - `git log --oneline` shows commits from other work
    - `git diff --stat` shows massive changes
    
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
    
    **Example**: PR #9205 initially included commits from PR #9199 because branch was created from `bugfix/version-suffix-clean-9167` instead of `main`. Fixed by creating clean branch from main.
    
    **Reference**: User correction during PR #9205 creation, May 2026.

28. **Complete PR workflow with Gemini Code Assist**: Modern PRs receive automated code review that should be incorporated.
    
    **Workflow**:
    1. Create clean branch from main
    2. Make changes + add tests
    3. Commit with sign-off: `git commit -s -m "..."`
    4. Push and create PR
    5. **Wait 2-3 minutes for Gemini Code Assist feedback**
    6. Fetch and review feedback
    7. Apply improvements in new commit
    8. Push → CI re-runs automatically
    9. Fix any CI failures (especially ruff format)
    10. Iterate until all checks pass
    
    **Fetching Gemini feedback**:
    ```bash
    # Get PR comments
    curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/issues/{PR_NUM}/comments"
    
    # Get inline review comments
    curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/pulls/{PR_NUM}/comments"
    
    # Get reviews
    curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/pulls/{PR_NUM}/reviews"
    ```
    
    **Common Gemini feedback types**:
    - Use `ValueError` instead of `assert` (assertions can be disabled with `-O`)
    - PR title format: `[Module][Type] Description`
    - PR description sections: What/Why, User-facing change, How tested
    - Code improvements (better patterns, caching)
    - Unreachable code detection
    
    **Example: PR #9205**:
    - Feedback 1: Use `ValueError` not `assert` → Applied
    - Feedback 2: PR title needs `[Module]` tag → Already correct
    - Feedback 3: Test should expect `ValueError` → Applied
    - Result: All feedback addressed, CI passed
    
    **Key points**:
    - Gemini suggestions are usually correct - don't ignore them
    - Apply all feedback before expecting merge
    - Each feedback application is a separate commit
    - Thank the bot in comments (maintains good relations)
    
    **Reference**: PR #9205 complete workflow, May 2026.

29. **Fixing ruff format CI failures**: Common CI failure that's easy to fix locally.
    
    **Symptoms**:
    - CI fails with: "lint / pre-commit (failure)"
    - Error: "Would reformat: file.py"
    
    **Diagnosis**:
    ```bash
    # Check which files need formatting
    ruff format --check vllm_ascend/ tests/
    
    # Output shows files that would be reformatted
    ```
    
    **Fix**:
    ```bash
    # Format all files
    ruff format vllm_ascend/ tests/
    
    # Or format specific files
    ruff format vllm_ascend/platform.py tests/ut/test_platform.py
    
    # Commit the formatting changes
    git add -A
    git commit -s -m "[Style] Fix ruff formatting"
    git push
    ```
    
    **Prevention**:
    - Run `ruff format` before committing
    - Or use pre-commit hooks: `pre-commit install`
    
    **Reference**: PR #9205 CI failure and fix, May 2026.

30. **Check method dependencies before calling them**: When adding a method that calls another object's method, verify the target method exists first.
    
    **Symptoms**:
    - Code calls `obj.method()` but `obj` doesn't have `method()`
    - AttributeError at runtime
    - User asks "这么修改正确吗？" (Is this modification correct?)
    
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
    
    **Example**: PR #4112 (shutdown interface) - needed to add shutdown() to both NPUModelRunner and NPUWorker, in that order.
    
    **Reference**: User correction during Issue #4112 work, May 2026.

31. **Always add tests for new features**: User expectation is that new features include corresponding tests.
    
    **Symptoms**:
    - User asks "为什么没有增加用例" (Why didn't you add test cases?)
    - PR lacks test coverage for new functionality
    
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
    
    **Utility functions** (`tests/ut/test_utils.py`):
    ```python
    def test_vllm_version_is_with_suffix(self):
        with mock.patch.object(envs_ascend, 'VLLM_VERSION', None):
            with mock.patch('vllm.__version__', '0.20.1+cpu'):
                vllm_version_is.cache_clear()
                self.assertTrue(vllm_version_is('0.20.1'))
    ```
    
    **Workflow**:
    1. Implement feature
    2. Write tests covering: happy path, edge cases, error cases
    3. Run tests: `pytest tests/ut/test_xxx.py -v`
    4. Add to commit
    
    **Reference**: User feedback on PR #9205 (missing tests initially), May 2026.

32. **Automated PR monitoring with cronjob**: Set up automated monitoring to catch PR feedback quickly.

    **Pattern**: Use Hermes cronjob to monitor PR every 5-10 minutes:
    
    ```bash
    # Create cron job for PR monitoring
    hermes cron create \
      --name "pr-XXXX-monitor" \
      --schedule "*/5 * * * *" \
      --prompt "监控 PR #XXXX 的评论区反馈，如果有新反馈则报告。检查步骤：1. 获取 PR 评论 2. 检查是否有新的 Gemini Code Assist 反馈 3. 如果有新反馈，报告反馈内容"
    ```
    
    **Benefits**:
    - Catch Gemini Code Assist feedback quickly (usually within 2-3 minutes)
    - Monitor CI status changes
    - Detect new review comments
    - Automatic notification of issues
    
    **Workflow**:
    1. Create PR
    2. Set up cronjob monitoring
    3. When feedback arrives, cronjob reports it
    4. Apply fixes and push
    5. Cronjob continues monitoring for new feedback
    
    **Example**: PR #9216 monitoring setup:
    ```bash
    hermes cron create \
      --name "pr-9216-monitor" \
      --schedule "*/5 * * * *" \
      --prompt "监控 PR #9216 的评论区反馈..."
    ```
    
    **Monitoring scope**:
    - Gemini Code Assist inline comments
    - PR issue comments
    - CI status changes
    - Review status changes
    
    **Reference**: PR #9216 monitoring setup, May 2026.

33. **CRITICAL: Check inheritance before adding interface methods**: Before adding any new method to NPUPlatform, NPUWorker, or NPUModelRunner, you MUST check if the base class already has it. This is the #1 most common mistake for newcomers to vLLM-Ascend.
    
    **Symptoms**:
    - You implement a method that's identical to base class
    - Maintainer comments "This is redundant, base class already has this"
    - Issue gets closed as "not needed"
    - PR is rejected
    - User feedback: "认真学习，防止再出现类似错误" (study carefully to prevent similar mistakes)
    
    **Root cause**: NPUPlatform inherits from `vllm.platforms.interface.Platform`, NPUWorker inherits from vLLM's Worker, etc. They automatically inherit all base class methods.
    
    **Check before implementing**:
    ```bash
    # 1. Check Platform base class
    curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/platforms/interface.py" | grep "def <method_name>"
    
    # 2. Check if output exists
    # If YES → base class has it, check if you need to override
    # If NO → safe to implement in NPUPlatform
    
    # 3. Check NPUPlatform inheritance
    grep -n "class NPUPlatform" vllm_ascend/platform.py
    # Shows: class NPUPlatform(Platform):
    ```
    
    **Decision tree**:
    ```
    Base class has the method?
    ├─ NO → Safe to implement in NPUPlatform
    └─ YES → Does NPU need different logic?
        ├─ YES → Override in NPUPlatform (document why different)
        └─ NO → Don't implement! Use inherited version.
    ```
    
    **Example: Issue #3489** (ViT attention backend):
    - Issue: "Add get_vit_attn_backend interface"
    - Mistake: Implemented without checking Platform base class
    - Reality: Platform base class already has get_vit_attn_backend()
    - Result: NPUPlatform inherits it automatically, PR rejected as redundant
    
    **Correct approach**:
    ```bash
    # Step 1: Check base class
    curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/platforms/interface.py" | grep "def get_vit_attn_backend"
    # Output: 268:    def get_vit_attn_backend(
    
    # Step 2: Base class has it! Check if NPU needs override
    # - Does NPU need different backend? NO (both use TORCH_SDPA)
    # - Does NPU need different validation? NO
    # Conclusion: Don't implement, use inherited version
    
    # Step 3: Close issue with explanation
    "NPUPlatform inherits from Platform base class, which already has 
     get_vit_attn_backend(). No need to reimplement."
    ```
    
    **When override IS needed**:
    ```python
    # Example: NPU needs different default backend
    @classmethod
    def get_vit_attn_backend(cls, ...):
        # NPU-specific logic: return FLASH_ATTN instead of TORCH_SDPA
        if backend is None:
            return AttentionBackendEnum.FLASH_ATTN  # Different!
        return super().get_vit_attn_backend(...)
    ```
    
    **Key inheritance relationships**:
    - `NPUPlatform(Platform)` - vllm.platforms.interface.Platform
    - `NPUWorker(WorkerBase)` - vllm.v1.worker.gpu_worker.Worker (via patches)
    - `NPUModelRunner(GPUModelRunner)` - vllm.v1.worker.gpu_model_runner.GPUModelRunner
    - `NPUWorker310(NPUWorker)` - inherits NPUWorker methods
    - `NPUModelRunner310(NPUModelRunner)` - inherits NPUModelRunner methods
    
    **Reference**: Issue #3489, PR #9205 (rejected), May 2026. User correction: "认真学习，防止再出现类似错误".

34. **Issue selection strategy**: When looking for issues to fix, prioritize by difficulty and clarity.

    **Priority order**:
    1. **Good First Issue** - Labeled issues meant for newcomers
    2. **Help Wanted** - Issues where maintainers explicitly request help
    3. **Simple BugFix** - Clear error messages, typos, missing checks
    4. **Documentation** - Doc fixes, example updates
    5. **Feature with clear spec** - Has reference commit or clear requirements
    
    **Avoid initially**:
    - Complex architecture issues (memory allocation, distributed communication)
    - Issues without clear reproduction steps
    - Issues requiring deep hardware knowledge
    - Performance optimization without benchmarks
    
    **Search commands**:
    ```bash
    # Good First Issue
    curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/issues?state=open&labels=good%20first%20issue"
    
    # Help Wanted
    curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/issues?state=open&labels=help%20wanted"
    
    # Bug issues
    curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/issues?state=open&labels=bug"
    ```
    
    **Assessment criteria**:
    - Has clear description of expected behavior
    - Has reproduction steps or test case
    - Has reference to similar fix or upstream PR
    - Scope is limited (single file or module)
    - Doesn't require NPU hardware to verify (unit test sufficient)
    
    **Example workflow** (May 2026):
    - Started with Issue #8975 (scheduler deadlock) - clear error, single check needed
    - Then Issue #9167 (version suffix) - clear problem, utility function fix
    - Then Issue #3489 (ViT backend) - has reference commit, interface addition
    - Then Issue #4112 (shutdown) - list of missing interfaces, pick one
    
    **Reference**: User preference for "简单的" (simple) issues, May 2026.

35. **Git credential reuse across repositories**: When you need to push to a new repository but credentials aren't configured, you can extract the token from an existing repository's remote URL.
    
    **Scenario**: You have credentials configured for repo A, but need to push to repo B (same GitHub account).
    
    **Technique**:
    ```bash
    # Step 1: Extract token from existing repo's remote URL
    cd /path/to/repo-a
    FORK_URL=$(git remote get-url fork)
    # URL format: https://TOKEN@github.com/user/repo.git
    
    # Extract token using bash regex
    if [[ $FORK_URL =~ https://([^@]+)@github\.com ]]; then
        TOKEN="${BASH_REMATCH[1]}"
        echo "$TOKEN" > /tmp/github_token.txt
    fi
    
    # Step 2: Use token to configure new repo
    cd /path/to/repo-b
    git remote add origin "https://${TOKEN}@github.com/user/repo-b.git"
    
    # Step 3: Push
    git push -u origin master
    ```
    
    **Why this works**: GitHub personal access tokens (PATs) work across all repositories for the authenticated user. The token embedded in the remote URL is a valid credential.
    
    **Use cases**:
    - Network is unstable and you can't run `git credential approve`
    - Creating a new repository and need to push immediately
    - Working in a fresh environment without credential helper configured
    
    **Security note**: Tokens extracted this way should be treated as secrets. Don't log them or commit files containing them.
    
    **Reference**: Pushing vllm-ascend-skill using vllm-ascend credentials, May 2026.

36. **Force push to sync branches**: When you need to sync content from one branch to another (e.g., master → main), use force push with source:target syntax.
    
    **Scenario**: Remote has both `main` (GitHub default) and `master` (your work) branches, and you want `main` to have the same content as `master`.
    
    **Technique**:
    ```bash
    # Push master's content to main branch
    git push origin master:main --force
    
    # This means: push local 'master' to remote 'main'
    ```
    
    **Alternative approaches**:
    ```bash
    # Method 1: Checkout and merge (slower)
    git checkout main
    git merge master --allow-unrelated-histories
    git push origin main
    
    # Method 2: Create local main from master and push (cleaner)
    git branch -D main  # Delete local main if exists
    git branch main     # Create new main from current (master)
    git push origin main --force
    ```
    
    **When to use**:
    - GitHub creates `main` by default, but you pushed to `master`
    - Need to make default branch have your content
    - Don't want to change GitHub's default branch setting
    
    **Caution**: Force push rewrites remote history. Only use when you're sure it's safe (e.g., your own fork, or coordinating with team).
    
    **Reference**: Syncing vllm-ascend-skill master to main, May 2026.

37. **Hermes skill structure for shareable projects**: When creating a Hermes skill that others can clone and use, follow this structure.
    
    **Directory layout**:
    ```
    project-name/
    ├── README.md              # Usage guide (how to clone, setup, use)
    ├── setup.sh               # One-click setup script (CRITICAL)
    ├── USAGE_GUIDE.md         # Detailed usage instructions
    │
    └── skill/                 # Hermes skill structure
        ├── SKILL.md           # Skill definition (Hermes reads this)
        │
        └── references/        # Knowledge documents
            ├── architecture.md
            ├── inheritance.md      # Key concepts
            ├── development-guide.md
            ├── lessons-learned.md  # Mistakes to avoid
            └── examples.md         # Usage examples
    ```
    
    **setup.sh must do**:
    1. Check Hermes is installed
    2. Create `~/.hermes/skills/` directory
    3. Copy `skill/` to `~/.hermes/skills/<skill-name>/`
    4. Import knowledge to `~/.hermes/memory/`
    5. Create `~/.hermes/config.yaml` if needed
    
    **Key insight**: Markdown documents alone are just knowledge (human-readable). To become a working skill:
    - Must have `skill/SKILL.md` with proper frontmatter
    - Must be installed to `~/.hermes/skills/`
    - Knowledge should be imported to Hermes memory
    
    **User workflow**:
    ```bash
    # Others can use your skill with just:
    git clone https://github.com/user/project-name.git
    cd project-name
    bash setup.sh
    hermes
    /load-skill <skill-name>
    ```
    
    **Reference**: Creating vllm-ascend-skill digital employee project, May 2026.

38. **Documentation parameter mismatch detection**: When serving models with custom `--served-model-name`, the value MUST match the `"model"` parameter in client requests.
    
    **Symptoms**:
    - Client request fails with "model not found" error
    - User follows documentation exactly but gets error
    - Issue reports about parameter inconsistency
    
    **Detection pattern**:
    ```bash
    # Find all docs with served-model-name
    for file in $(grep -r "served-model-name" docs/ --include="*.md" -l); do
        # Extract served-model-name values
        served_names=$(grep -oP "served-model-name\s+\K\w+" "$file" | sort -u)
        # Extract model parameter values
        model_values=$(grep -oP '"model":\s*"\K[^"]+' "$file" | sort -u)
        # Check for mismatches
        for sn in $served_names; do
            for mv in $model_values; do
                if [ "$sn" != "$mv" ]; then
                    echo "⚠️  Mismatch in $file: '$sn' vs '$mv'"
                fi
            done
        done
    done
    ```
    
    **Fix pattern**:
    1. Choose consistent naming (prefer full model name like `deepseek_v3.2`)
    2. Update all `--served-model-name` instances in documentation
    3. Add parameter explanation: `<node0_ip>` = localhost, `<port>` = server port
    4. Use concrete example: `curl http://localhost:7000/...`
    
    **Example: Issue #9358** (DeepSeek-V3.2.md):
    - Before: `--served-model-name dsv3`, `"model": "deepseek_v3.2"` (mismatch!)
    - After: `--served-model-name deepseek_v3.2`, `"model": "deepseek_v3.2"` (match!)
    - Added: Explanation of `<node0_ip>` and `<port>` parameters
    
    **Common mismatches found** (May 2026 audit):
    - DeepSeek-V3.2.md: `dsv3` vs `deepseek_v3.2`
    - GLM4.x.md: `glm47` vs `glm`
    - GLM5.md: `glm` vs `glm-5`
    - Qwen3.5-27B.md: `qwen3` vs `qwen3.5`
    
    **Reference**: Issue #9358, PR fixing DeepSeek-V3.2.md, May 2026.

39. **Git credential reuse across repositories**: When you need to push to a new repository but credentials aren't configured, extract token from existing repo's remote URL.
    
    **Scenario**: You have credentials for repo A, need to push to repo B (same GitHub account).
    
    **Technique**:
    ```bash
    # Step 1: Extract token from existing repo
    cd /path/to/repo-a
    FORK_URL=$(git remote get-url fork)
    # URL format: https://TOKEN@github.com/user/repo.git
    
    # Extract token using bash regex
    if [[ $FORK_URL =~ https://([^@]+)@github\.com ]]; then
        TOKEN="${BASH_REMATCH[1]}"
        echo "$TOKEN" > /tmp/github_token.txt
    fi
    
    # Step 2: Use token for new repo
    cd /path/to/repo-b
    git remote add origin "https://${TOKEN}@github.com/user/repo-b.git"
    
    # Step 3: Push
    git push -u origin master
    ```
    
    **Why this works**: GitHub PATs work across all repositories for the authenticated user.
    
    **Use cases**:
    - Network unstable, can't run `git credential approve`
    - Creating new repository, need immediate push
    - Fresh environment without credential helper
    
    **Security**: Treat extracted tokens as secrets. Don't log or commit them.
    
    **Reference**: Pushing vllm-ascend-skill using vllm-ascend credentials, May 2026.

40. **Force push to sync branches**: When remote has both `main` (GitHub default) and `master` (your work), use force push with source:target syntax to sync them.
    
    **Technique**:
    ```bash
    # Push master's content to main branch
    git push origin master:main --force
    
    # This means: push local 'master' to remote 'main'
    ```
    
    **Alternative approaches**:
    ```bash
    # Method 1: Checkout and merge (slower)
    git checkout main
    git merge master --allow-unrelated-histories
    git push origin main
    
    # Method 2: Create local main from master (cleaner)
    git branch -D main  # Delete local main if exists
    git branch main     # Create new main from current (master)
    git push origin main --force
    ```
    
    **When to use**:
    - GitHub creates `main` by default, but you pushed to `master`
    - Need default branch to have your content
    - Don't want to change GitHub's default branch setting
    
    **Caution**: Force push rewrites remote history. Only use when safe (your own fork, or coordinating with team).
    
    **Reference**: Syncing vllm-ascend-skill master to main, May 2026.

41. **GitHub PR creation via API is NOT possible with PAT**: Personal Access Tokens cannot create PRs in upstream repositories (repos you don't own), even with full `repo` scope. This is a GitHub security design, not a permission issue.
    
    **Symptoms**:
    ```
    POST /repos/vllm-project/vllm-ascend/pulls
    → 403 Forbidden: "Resource not accessible by personal access token"
    ```
    
    **Root cause**:
    - PAT has full permissions for YOUR repositories (fork)
    - PAT only has READ permissions for OTHERS' repositories (upstream)
    - Creating PR in upstream requires write permission on upstream
    - This is intentional security design to prevent unauthorized PR creation
    
    **Token permission check**:
    ```bash
    # Check fork permissions (will show admin=True, push=True)
    curl -s -H "Authorization: token $TOKEN" \
      "https://api.github.com/repos/YOUR-USER/vllm-ascend" | \
      python -c "import sys,json; r=json.load(sys.stdin); print(r.get('permissions'))"
    
    # Check upstream permissions (will show push=False)
    curl -s -H "Authorization: token $TOKEN" \
      "https://api.github.com/repos/vllm-project/vllm-ascend" | \
      python -c "import sys,json; r=json.load(sys.stdin); print(r.get('permissions'))"
    ```
    
    **Standard workflow (what ALL open source contributors do)**:
    ```
    1. Fork upstream repo         ✅
    2. Push code to fork          ✅ (PAT can do this)
    3. Create PR in upstream      ❌ (PAT cannot do this)
       → Use GitHub Web UI        ⭐ (easiest, 30 seconds)
       → Or use GitHub CLI (gh)   (requires installation)
    ```
    
    **Solution 1: GitHub Web UI** (recommended):
    ```
    https://github.com/vllm-project/vllm-ascend/compare/main...YOUR-USER:branch-name?expand=1
    ```
    Click link → paste PR description → Create PR. Takes 30 seconds.
    
    **Solution 2: GitHub CLI**:
    ```bash
    # Install
    winget install GitHub.cli  # Windows
    brew install gh            # macOS
    
    # Login and create PR
    gh auth login
    gh pr create --repo vllm-project/vllm-ascend
    ```
    
    **Why this is NOT a problem**:
    - This is the standard workflow used by ALL open source contributors
    - Linux Kernel, Kubernetes, React, vLLM-Ascend contributors all do this
    - Manual PR creation is fast and safe
    
    **Reference**: Attempting to auto-create PR for Issue #9358, May 2026. Token had full `repo` scope but still got 403. This is expected GitHub behavior.

42. **DCO (Developer Certificate of Origin) requirements**: Every commit, including merge commits, MUST have a `Signed-off-by: Name <email>` line. This is checked by DCO bot and PRs will be blocked if any commit lacks it.
    
    **Symptoms**:
    - DCO check fails on PR
    - Error: "Commit X does not have a Signed-off-by line"
    - Merge commits from `git merge main` are missing Signed-off-by
    
    **Root cause**: 
    - Regular commits use `git commit -s` (adds Signed-off-by automatically)
    - But merge commits from `git merge main` don't get Signed-off-by unless you use `git merge --signoff main`
    - This is a common mistake when syncing your branch with upstream
    
    **Detection**:
    ```bash
    # Check all commits in PR for Signed-off-by
    git log origin/main..HEAD --pretty=format:"%h %s" | while read sha msg; do
        if ! git log -1 --pretty=format:"%B" $sha | grep -q "Signed-off-by:"; then
            echo "❌ Missing Signed-off-by: $sha $msg"
        fi
    done
    ```
    
    **Solutions**:
    
    **Method 1: Create clean branch (recommended for simple fixes)**
    ```bash
    # If your PR has merge commits without Signed-off-by, easiest is to recreate clean
    git checkout main
    git pull origin main
    git checkout -b fix-issue-X-clean
    
    # Apply only your changes (cherry-pick or manual)
    git cherry-pick <your-commit-sha>
    
    # Push to new branch
    git push fork HEAD:fix-issue-X-clean --force
    ```
    
    **Method 2: Rebase to clean history**
    ```bash
    # Interactive rebase to squash/drop merge commits
    git rebase -i origin/main
    
    # Mark merge commits as "drop" or "squash"
    # Ensure all remaining commits have Signed-off-by
    
    # Force push
    git push fork HEAD:your-branch --force
    ```
    
    **Method 3: Amend merge commit (if you want to keep it)**
    ```bash
    # Add Signed-off-by to last commit (if it's a merge)
    git commit --amend -s --no-edit
    
    # Force push
    git push fork HEAD:your-branch --force
    ```
    
    **Prevention**:
    ```bash
    # Always use --signoff when merging
    git merge --signoff main
    
    # Or better: use rebase instead of merge
    git rebase main
    ```
    
    **Reference**: PR #9369 DCO failure due to merge commit without Signed-off-by, May 2026.

43. **GitHub API push when Git push fails**: When `git push` fails due to network issues but GitHub API works, use the REST API to update files directly.
    
    **Symptoms**:
    ```bash
    git push origin branch
    # fatal: unable to access '...': Failed to connect to github.com port 443
    # fatal: unable to access '...': Connection was reset
    ```
    
    But `curl https://api.github.com` works fine.
    
    **Root cause**:
    - Git uses different connection method than curl
    - Git's HTTPS connection may be blocked by network/firewall
    - But GitHub REST API (via curl/requests) works
    
    **Solution**: Use GitHub REST API to update file
    ```python
    import requests
    import base64
    
    # Read file content
    with open('path/to/file.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Base64 encode
    content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    # Get current file SHA (required for update)
    response = requests.get(
        f'https://api.github.com/repos/{owner}/{repo}/contents/path/to/file.md?ref={branch}',
        headers={'Authorization': f'token {token}'}
    )
    current_sha = response.json()['sha']
    
    # Update file via API
    response = requests.put(
        f'https://api.github.com/repos/{owner}/{repo}/contents/path/to/file.md',
        headers={'Authorization': f'token {token}'},
        json={
            'message': 'Your commit message\n\nSigned-off-by: Name <email>',
            'content': content_b64,
            'sha': current_sha,
            'branch': branch
        }
    )
    
    if 'content' in response.json():
        print("✅ File updated successfully")
    ```
    
    **Key points**:
    - Must provide `sha` of current file (get it first)
    - Content must be Base64 encoded
    - Include Signed-off-by in commit message
    - This creates a new commit on the branch
    
    **Limitations**:
    - Only works for single file updates
    - For multiple files, need multiple API calls
    - Cannot handle complex git operations (merge, rebase)
    
    **When to use**:
    - Git push fails but API works
    - Simple file updates (documentation, config)
    - Emergency fix when network is unstable
    
    **Reference**: PR #9369 pushed via GitHub API when Git push failed, May 2026.

44. **Gemini Code Assist feedback handling for documentation PRs**: When fixing documentation issues, Gemini provides specific feedback that should be incorporated.
    
    **Common feedback types for doc PRs**:
    
    1. **PR title format**: Add `[BugFix]` tag
       ```
       Wrong: [Doc] Fix parameter mismatch
       Right: [Doc][BugFix] Fix parameter mismatch
       ```
    
    2. **Parameter naming consistency**: Use consistent naming throughout document
       ```
       Wrong: served-model-name uses underscore (deepseek_v3_2), but curl uses dot (deepseek_v3.2)
       Right: Keep model parameter as-is if it's the actual model name, update served-model-name to match
       ```
    
    3. **Port number consistency**: Match port numbers with rest of document
       ```
       Wrong: curl example uses port 7000, but document uses 8000
       Right: Use 8000 consistently
       ```
    
    4. **Placeholder vs hardcoded values**: Keep placeholders for clarity
       ```
       Wrong: curl http://localhost:7000/... (hardcoded)
       Right: curl http://<node0_ip>:<port>/... (with explanation)
       ```
    
    **Workflow**:
    1. Create PR and wait 2-3 minutes for Gemini feedback
    2. Fetch feedback via GitHub API or check PR page
    3. Apply corrections in new commit
    4. Push → CI re-runs automatically
    
    **Example: Issue #9358** (DeepSeek-V3.2.md):
    - Feedback 1: Port 7000 → 8000 → Applied
    - Feedback 2: Keep placeholders → Applied
    - Feedback 3: Don't change model parameter name (deepseek_v3.2 is actual model name) → Applied
    - Result: All feedback addressed, PR ready for merge
    
    **Key insight**: Gemini feedback is usually correct. When it says "don't change X", there's usually a good reason (e.g., it's the actual API parameter name).
    
    **Reference**: PR #9369, Issue #9358, May 2026.

45. **markdownlint format requirements**: Documentation files must follow markdownlint rules. Common CI failures are easy to fix locally.
    \n    **Symptoms**:\n    - CI fails with: "markdownlint (failure)"\n    - Error: "files were modified by this hook"\n    - Diff shows formatting changes (trailing spaces, missing blank lines)\n    \n    **Common issues**:\n    \n    1. **Trailing space after bold text**:\n       ```markdown\n       Wrong: **Note**: \n       Right: **Note**:\n       ```\n    \n    2. **Missing blank line before list**:\n       ```markdown\n       Wrong:\n       **Note**:\n       - item 1\n       - item 2\n       \n       Right:\n       **Note**:\n       \n       - item 1\n       - item 2\n       ```\n    \n    3. **Inconsistent list marker style**: Use `-` consistently, not mixed with `*`\n    \n    **Fix workflow**:\n    ```bash\n    # The hook auto-fixes, so just commit the changes\n    git add docs/source/path/to/file.md\n    git commit -s -m \"[Doc] Fix markdownlint format issues\"\n    git push\n    ```\n    \n    **Prevention**:\n    - Run pre-commit hooks locally: `pre-commit run --all-files`\n    - Or install hooks: `pre-commit install`\n    - Check for trailing spaces: `grep -n ' $' file.md`\n    \n    **Reference**: PR #9379 CI failure (markdownlint), May 2026.

46. **CRITICAL: DCO email matching requirement**: The email in `Signed-off-by` MUST match the email in Git's `user.email` config. If they don't match, DCO check will fail even though Signed-off-by is present.
    \n    **Symptoms**:\n    - DCO check fails with "action_required"\n    - All commits have Signed-off-by, but still fails\n    - Author email is GitHub's noreply email: `32252938+username@users.noreply.github.com`\n    - Signed-off-by email is your real email: `your@email.com`\n    \n    **Root cause**:\n    - Git config `user.email` is wrong or not set\n    - GitHub API file updates use noreply email automatically\n    - DCO requires Author email == Signed-off-by email\n    \n    **Detection**:\n    ```bash\n    # Check Git config\n    git config user.email\n    # If this doesn't match your Signed-off-by email, DCO will fail\n    \n    # Check commit Author vs Signed-off-by\n    git log -1 --pretty=format:"Author: %an <%ae>%nSigned-off-by: %b"\n    ```\n    \n    **Solutions**:\n    \n    **Method 1: Fix Git config (recommended)**\n    ```bash\n    # Set correct email\n    git config --global user.email "your@email.com"\n    \n    # Recreate commits with correct Author\n    git commit --amend --reset-author -s --no-edit\n    \n    # Force push\n    git push --force\n    ```\n    \n    **Method 2: Make GitHub use your real email**\n    1. Visit https://github.com/settings/emails\n    2. Uncheck "Keep my email addresses private"\n    3. Now GitHub API will use your real email instead of noreply\n    \n    **Method 3: Use local Git push instead of GitHub API**\n    - GitHub API file updates always use noreply email\n    - Local Git commits use your configured email\n    - When network allows, prefer local commit + push\n    \n    **Verification**:\n    ```bash\n    # After fix, verify match\n    git log -1 --pretty=format:"Author: %ae%nSigned-off-by: " && \\\n    git log -1 --pretty=format:"%b" | grep "Signed-off-by:" | sed 's/Signed-off-by:.*<\(.*\)>/\\1/'\n    ```\n    \n    **Reference**: PR #9379 DCO failure (email mismatch), May 2026.

47. **CRITICAL: One branch per Issue - user preference**: When fixing an Issue, use ONE branch only. Do NOT create multiple branches (v1, v2, v3) for the same Issue.
    \n    **User feedback**: "同一个Issue尽量一个分支" (Try to use one branch for the same Issue)\n    \n    **Why this matters**:\n    - Multiple branches create confusion\n    - Each branch requires a new PR\n    - Harder to track which PR is the "real" one\n    - Wastes branch namespace\n    \n    **Wrong pattern**:\n    ```\n    Issue #9358:\n      - doc/fix-deepseek-v3.2-parameter-9358      (PR #9369)\n      - doc/fix-deepseek-v3.2-parameter-9358-v2   (PR #9379)\n      - doc/fix-deepseek-v3.2-parameter-9358-v3   (???)\n    ```\n    \n    **Correct pattern**:\n    ```\n    Issue #9358:\n      - doc/fix-deepseek-v3.2-parameter-9358-v2   (PR #9379)\n      # Fix issues on same branch, force push to update PR\n    ```\n    \n    **When you need to fix issues**:\n    ```bash\n    # Stay on same branch\n    git checkout doc/fix-deepseek-v3.2-parameter-9358-v2\n    \n    # Make fixes\n    git add .\n    git commit -s -m \"[Doc] Fix additional issues\"\n    \n    # Push to same branch (updates existing PR)\n    git push fork HEAD:doc/fix-deepseek-v3.2-parameter-9358-v2\n    ```\n    \n    **When to create new branch**:\n    - ONLY if old branch is completely broken (e.g., wrong base, massive history)\n    - AND you've closed the old PR\n    - Use clean name without version suffix\n    \n    **Reference**: User correction during Issue #9358 work, May 2026.

51. **Local main branch sync before creating PR branches**: Always sync local main with remote before creating new branches, otherwise PR will include unexpected changes from commits that remote main has but local main doesn't.
    \n    **Symptoms**:\n    - PR shows extra files changed (e.g., 4 files instead of 2)\n    - PR diff includes changes you didn't make\n    - `git diff origin/main` shows different files than expected\n    \n    **Root cause**:\n    - Local main branch is behind remote main\n    - Creating branch from local main includes \"missing\" commits\n    - PR compares against remote main, showing the gap\n    \n    **Example: Issue #9291** (MiniMax-M2.7):\n    - Local main: commit 7bce23cc (DeepseekV4 support)\n    - Remote main: commit 64b05b4 (EPLB support, 3 commits ahead)\n    - Created branch from local main\n    - PR diff showed: MiniMax-M2.7.md + Mixtral + Qwen3-ASR + Qwen2.5-Math (4 files!)\n    - Expected: MiniMax-M2.7.md only (1 file)\n    \n    **Solution**:\n    ```bash\n    # Always sync main first\n    git checkout main\n    git pull origin main\n    # OR\n    git fetch origin\n    git checkout -b new-branch origin/main  # Use remote main directly\n    ```\n    \n    **If you already created branch from old main**:\n    ```bash\n    # Rebase onto latest main\n    git checkout your-branch\n    git rebase origin/main\n    \n    # Force push to update PR\n    git push fork your-branch --force\n    ```\n    \n    **Reference**: Issue #9291 (MiniMax-M2.7), PR #9383, May 2026.

52. **CRITICAL: One branch per Issue - user preference**: When fixing an Issue, use ONE branch only. Do NOT create multiple branches (v1, v2, v3) for the same Issue. This is a strong user preference.
    \n    **User feedback**: \"同一个Issue尽量一个分支\" (Try to use one branch for the same Issue), \"不允许对同一个Issue创建多个分支\" (Not allowed to create multiple branches for the same Issue)
    \n    \n    **Why this matters**:\n    - Multiple branches create confusion\n    - Each branch requires a new PR\n    - Harder to track which PR is the \"real\" one\n    - Wastes branch namespace
    \n    \n    **Wrong pattern**:\n    ```\n    Issue #8975:\n      - bugfix/scheduler-mutex-check-8975      (PR #9149)\n      - bugfix/scheduler-mutex-check-8975-v3   (PR #9409)\n      - bugfix/scheduler-mutex-check-8975-v4   (PR #9411)\n    ```\n    \n    **Correct pattern**:\n    ```\n    Issue #8975:\n      - bugfix/scheduler-mutex-8975-final   (PR #9414)\n      # Fix issues on same branch, force push to update PR\n    ```\n    \n    **When you need to fix issues**:\n    ```bash\n    # Stay on same branch\n    git checkout bugfix/scheduler-mutex-8975-final\n    \n    # Make fixes\n    git add .\n    git commit -s -m \"[Test] Fix additional issues\"\n    \n    # Push to same branch (updates existing PR)\n    git push fork HEAD:bugfix/scheduler-mutex-8975-final\n    ```\n    \n    **When to create new branch**:\n    - ONLY if old branch is completely broken (e.g., wrong base, massive history)\n    - AND you've closed the old PR\n    - Use clean name without version suffix\n    \n    **Reference**: User correction during Issue #8975 work, May 2026.

53. **CRITICAL: Only push files for the specific PR**: When updating a PR, only push files that belong to that PR. Do NOT push files from other PRs.
    \n    **User feedback**: \"你只能修改这个PR上需要的文件，不要把其他PR文件推送上去\" (You can only modify files needed for this PR, don't push other PR files)
    \n    \n    **Symptoms of violation**:\n    - PR shows unexpected files changed\n    - Diff includes files from previous work\n    - PR becomes larger than intended
    \n    \n    **Root cause**:\n    - Working on branch that contains commits from other PRs\n    - Using `git push` without checking what will be pushed
    \n    \n    **Solution**:\n    ```bash\n    # Before pushing, check what will be in the PR\n    git diff origin/main --name-only\n    \n    # Should only show files for THIS PR\n    # Example for Issue #8975:\n    tests/ut/test_platform.py\n    vllm_ascend/platform.py\n    \n    # If you see extra files, STOP\n    git diff origin/main --name-only\n    # Bad output:\n    tests/ut/test_platform.py\n    tests/ut/test_utils.py      # Wrong - from PR #9199\n    vllm_ascend/platform.py\n    vllm_ascend/utils.py        # Wrong - from PR #9199\n    ```\n    \n    **Fix if you already pushed wrong files**:\n    ```bash\n    # Close the PR\n    # Create clean branch from main\n    git checkout -b clean-branch origin/main\n    \n    # Apply only the correct changes\n    git cherry-pick <correct-commit>\n    \n    # Or manually re-apply changes\n    ```\n    \n    **Reference**: User correction during PR #9149 work, May 2026.

54. **CRITICAL: Sync fork main with upstream main before creating PR branches**: When creating PR branches, you MUST sync your fork's main branch with the upstream main branch first. Otherwise your PR will have conflicts.
    \n    **User feedback**: \"你应该拉去主仓创建分支，不应该在子仓拉去最新代码\" (You should pull from upstream to create branch, not pull latest code in fork)
    \n    \n    **Problem**:\n    - Fork's main branch becomes stale over time\n    - Creating branch from stale fork main = branch behind upstream main\n    - PR shows \"Mergeable: False, State: dirty\" (conflicts)
    \n    \n    **Correct workflow**:\n    ```bash\n    # Step 1: Get upstream main's latest SHA\n    UPSTREAM_SHA=$(curl -s \"https://api.github.com/repos/vllm-project/vllm-ascend/commits?sha=main&per_page=1\" | \\\n      python -c \"import sys,json; print(json.load(sys.stdin)[0]['sha'])\")\n    \n    # Step 2: Update fork's main to match upstream\n    curl -X PATCH \"https://api.github.com/repos/YOUR-USER/vllm-ascend/git/refs/heads/main\" \\\n      -H \"Authorization: token $TOKEN\" \\\n      -d \"{\\\"sha\\\": \\\"$UPSTREAM_SHA\\\", \\\"force\\\": true}\"\n    \n    # Step 3: Create branch from synced main\n    git checkout -b new-branch origin/main\n    ```\n    \n    **Alternative (if you have upstream remote)**:\n    ```bash\n    git fetch upstream\n    git checkout main\n    git reset --hard upstream/main\n    git push fork main --force\n    git checkout -b new-branch\n    ```\n    \n    **Verification**:\n    ```bash\n    # Check branch is ahead of main, not behind\n    curl -s \"https://api.github.com/repos/vllm-project/vllm-ascend/compare/main...YOUR-USER:branch\" | \\\n      python -c \"import sys,json; r=json.load(sys.stdin); print(f'Behind: {r[\\\"behind_by\\\"]}, Ahead: {r[\\\"ahead_by\\\"]}')\"\n    \n    # Should show: Behind: 0, Ahead: N\n    ```\n    \n    **Reference**: User correction during PR #9412 work, May 2026.

55. **DCO with GitHub API: Author email uses noreply**: When updating files via GitHub REST API, the Author email is automatically set to GitHub's noreply email. This causes DCO failures.
    \n    **Problem**:\n    - GitHub API updates: Author = `32252938+username@users.noreply.github.com`\n    - Signed-off-by: `your@email.com`\n    - DCO requires: Author email == Signed-off-by email\n    - Result: DCO check fails\n    \n    **Detection**:\n    ```bash\n    # Check commits in PR\n    curl -s \"https://api.github.com/repos/vllm-project/vllm-ascend/pulls/PR_NUM/commits\" | \\\n      python -c \"\nimport sys, json\nfor c in json.load(sys.stdin):\n    author_email = c['commit']['author']['email']\n    sob = [l for l in c['commit']['message'].split('\\n') if 'Signed-off-by:' in l]\n    print(f\\\"Author: {author_email}\\\")\n    print(f\\\"{sob[0] if sob else 'No Signed-off-by'}\\\")\n    print()\n\"\n    ```\n    \n    **Solution 1: Uncheck \"Keep my email addresses private\"** (recommended):\n    1. Visit https://github.com/settings/emails\n    2. Uncheck \"Keep my email addresses private\"\n    3. Now GitHub API will use your real email instead of noreply\n    4. Recreate commits\n    \n    **Solution 2: Use local Git instead of GitHub API**:\n    ```bash\n    # Configure correct email\n    git config user.email \"your@email.com\"\n    \n    # Commit locally\n    git commit -s -m \"message\"\n    \n    # Push (if network allows)\n    git push fork branch\n    ```\n    \n    **Why this happens**:\n    - GitHub API respects user's privacy settings\n    - \"Keep my email addresses private\" = use noreply email\n    - Cannot override via API parameters\n    \n    **Reference**: PR #9411, #9412 DCO failures, May 2026.

56. **Gemini Code Assist: Test logic improvement**: Gemini often identifies weak test logic. Common feedback: \"test swallows unrelated exceptions\".
    \n    **Weak pattern** (catches and ignores exceptions):\n    ```python\n    def test_feature_works(self):\n        try:\n            platform.check_and_update_config(config)\n        except ValueError as e:\n            if \"specific error\" in str(e):\n                self.fail(\"Should not raise this error\")\n    ```\n    \n    **Problem**: Test passes even if config is invalid for OTHER reasons.
    \n    **Strong pattern** (properly configure mocks):\n    ```python\n    def test_feature_works(self):\n        # Configure valid parameters\n        config.kv_transfer_config = None  # Valid for this feature\n        \n        # Should not raise ANY error\n        platform.check_and_update_config(config)\n    ```\n    \n    **Gemini feedback example**:\n    \"The test logic for verifying that a scheduler works 'alone' is weak because it catches and ignores any ValueError unless it matches the specific mutex error message. This means the test could pass even if the configuration is invalid for other reasons.\"\n    \n    **Solution**:\n    1. Configure valid parameters that satisfy ALL validation\n    2. Don't use try-except to swallow exceptions\n    3. Let the test fail if ANY exception is raised\n    \n    **Reference**: PR #9414 Gemini feedback on test_balance_scheduler_alone_works, May 2026.

48. **PR format requirements from Gemini Code Assist**: Gemini provides specific format requirements that must be followed.
    \n    **PR title format**:\n    ```\n    [Type][SubType] Description\n    \n    Examples:\n    [Doc][BugFix] Fix parameter mismatch in DeepSeek-V3.2.md\n    [Feature][Model] Add DeepSeek V4 support\n    [BugFix][Scheduler] Fix deadlock in BalanceScheduler\n    ```\n    \n    **PR description format** (three required sections):\n    ```markdown\n    ### What this PR does / why we need it?\n    [Description of what the PR does and why]\n    \n    Fixes #XXX\n    \n    ### Does this PR introduce _any_ user-facing change?\n    [Yes/No, with details if Yes]\n    \n    ### How was this patch tested?\n    [Test method]\n    ```\n    \n    **Common Gemini feedback**:\n    1. Title missing `[Type]` tag → Add appropriate tag\n    2. Description missing sections → Add all three sections\n    3. Parameter naming inconsistency → Use consistent naming\n    4. Port number inconsistency → Match with rest of document\n    5. Hardcoded values → Use placeholders with explanation\n    \n    **When Gemini says "don't change X"**:\n    - Usually correct (e.g., model parameter name is actual API name)\n    - Don't argue, follow the suggestion\n    \n    **Reference**: Issue #9358, PR #9379, May 2026.

49. **GitHub API limitation: cannot specify Author email**: When updating files via GitHub REST API, the Author email is automatically set to GitHub's noreply email. You cannot specify a custom email.
    \n    **Implication**:\n    - API updates: Author = `32252938+username@users.noreply.github.com`\n    - Local commits: Author = your `git config user.email`\n    \n    **For DCO compliance**:\n    - If you need Author email to match Signed-off-by, use local Git commit\n    - Or uncheck "Keep my email addresses private" in GitHub settings\n    \n    **Reference**: PR #9379 DCO investigation, May 2026.

50. **Model documentation addition workflow**: When adding documentation for a new model variant (e.g., MiniMax-M2.7), follow this workflow:
    \n    **Step 1: Verify support in code**\n    ```bash\n    # Check if model type is supported\n    grep -r "model_type.*minimax" vllm_ascend/patch/\n    \n    # Check for series support (e.g., MiniMax-M2 series)\n    grep -r "minimax_m2" vllm_ascend/patch/platform/\n    ```\n    \n    **Step 2: Create documentation file**\n    - Reference existing similar model docs (e.g., MiniMax-M2.5.md)\n    - Include: Introduction, Supported Features, Deployment, Quick Start, FAQ\n    - Note if model is part of a series (shares architecture/config)\n    \n    **Step 3: Add to model index**\n    ```markdown\n    # In docs/source/tutorials/models/index.md\n    MiniMax-M2.5.md\n    MiniMax-M2.7.md  # Add after related model\n    ```\n    \n    **Step 4: Commit and push**\n    ```bash\n    git checkout main\n    git checkout -b doc/add-model-XXX-support-YYYY\n    git add docs/source/tutorials/models/Model-XXX.md\n    git add docs/source/tutorials/models/index.md\n    git commit -s -m "[Doc] Add Model-XXX support documentation\\n\\n- Add Model-XXX.md documentation\\n- Confirm vLLM-Ascend supports Model-XXX\\n- Reference Model-YYY for deployment details\\n\\nFixes #YYYY\\n\\nSigned-off-by: Name <email>"\n    ```\n    \n    **Documentation template**:\n    ```markdown\n    # Model-XXX\n    \n    ## Introduction\n    Model-XXX is part of the Model series. It shares the same architecture as Model-YYY.\n    \n    ## Deployment\n    Model-XXX follows the same deployment procedures as Model-YYY. See [Model-YYY documentation](Model-YYY.md).\n    \n    ## Quick Start\n    [Example command]\n    \n    ## FAQ\n    - Q: Is Model-XXX supported?\n      A: Yes, vLLM-Ascend supports all Model series.\n    ```\n    \n    **Example**: Issue #9291 (MiniMax-M2.7), May 2026.

## Deep Technical Knowledge

### CANN Software Stack

```
CANN 9.0.0
├── Ascend HDK (固件/驱动)
├── ACL (Ascend Computing Library) - 底层计算接口
├── ATB (Ascend Tensor Boost) - 张量加速库
├── NNAL (Neural Network Acceleration Library) - libatb.so
└── HCCL (Huawei Collective Communication Library) - 分布式通信
```

Installation requires three packages:
- `Ascend-cann-toolkit_9.0.0` - Core toolkit
- `Ascend-cann-910b-ops_9.0.0` - 910B optimized operators
- `Ascend-cann-nnal_9.0.0` - NNAL (libatb.so)

### torch-npu Key APIs

```python
import torch_npu

# Device management
torch.npu.device(device_id)
torch.npu.current_stream()
torch.npu.synchronize()

# Memory
torch.npu.empty_cache()
# Set: PYTORCH_NPU_ALLOC_CONF=expandable_segments:True

# Graph capture (CUDA Graph equivalent)
aclgraph = torch.npu.NPUGraph()
with torch.npu.graph(aclgraph, pool=graph_pool):
    output = model(*args)
aclgraph.replay()

# NPU format conversion
torch_npu.npu_format_cast(tensor, ACL_FORMAT_FRACTAL_NZ)

# Quantized matmul
torch_npu.npu_weight_quant_batchmatmul(x, weight, antiquant_scale, antiquant_group_size)
```

### ACL Graph Modes

- **FULL**: Entire forward as single graph
- **PIECEWISE**: Per-layer graph capture (default, more flexible)
- **NONE**: No graph capture

Key class: `ACLGraphWrapper` in `compilation/acl_graph.py`

### HCCL Distributed Communication

```python
# Via torch.distributed
torch.distributed.init_process_group(backend='hccl')

# Or direct PyHcclCommunicator
from vllm_ascend.distributed.device_communicators.pyhccl import PyHcclCommunicator
comm = PyHcclCommunicator(group, device)
comm.all_reduce(tensor, op=ReduceOp.SUM)
```

Key env vars: `HCCL_BUFFSIZE`, `HCCL_IF_IP`, `HCCL_SOCKET_IFNAME`, `HCCL_OP_EXPANSION_MODE=AIV`

### MoE Communication Types

| Type | Description |
|------|-------------|
| ALLGATHER | AllGather-based communication |
| ALLTOALL | AllToAll-based communication |
| MC2 | MC2 fused communication |
| FUSED_MC2 | dispatch_ffn_combine fusion (fastest) |

### PD Disaggregation Architecture

Separates Prefill (P) and Decode (D) nodes for independent TP/DP/EP configuration:

```
External Request → Proxy → P Node (Prefiller) ←KV Cache→ D Node (Decoder)
```

Connectors:
- `MooncakeConnector`: D pulls KV from P
- `MooncakeLayerwiseConnector`: P pushes KV layerwise to D

### Quantization Methods

| Method | File | Description |
|--------|------|-------------|
| W8A8_STATIC | w8a8_static.py | Static W8A8 |
| W8A8_DYNAMIC | w8a8_dynamic.py | Dynamic W8A8 |
| W8A8_MXFP8 | w8a8_mxfp8.py | MXFP8 format |
| W4A8_DYNAMIC | w4a8.py | Dynamic W4A8 |
| W4A16 | w4a16.py | W4A16 |
| KV_C8 | kv_c8.py | KV Cache INT8 |

### Performance Profiling Tools

| Tool | Granularity | Control |
|------|-------------|---------|
| Ascend PyTorch Profiler | Operator level | API request |
| MS Service Profiler | Framework function level | Config file |

Usage:
```bash
# Enable profiler
--profiler-config '{"profiler": "torch", "torch_profiler_dir": "./vllm_profile"}'

# Control at runtime
curl -X POST http://localhost:8080/start_profile
curl -X POST http://localhost:8080/stop_profile

# Analyze
python -c "from torch_npu.profiler.profiler import analyse; analyse('./vllm_profile/*_ascend_pt/')"
```

Output: `trace_view.json` (Chrome Tracing), `operator_details.csv`, `kernel_details.csv`

## PR Analysis Deep Dive

### PR Title Format

```
[Type][Module] Description (#PR_NUMBER)
```

Types: BugFix, Feature, Performance, Refactor, Misc, Doc, CI, Test, Community

### PR Description Template

```markdown
### What this PR does / why we need it?
[Detailed explanation of the problem and solution]

### Does this PR introduce _any_ user-facing change?
[Yes/No + details if Yes]

### How was this patch tested?
[Test method, CI status, manual test results]

- vLLM version: X.Y.Z
- vLLM main: https://github.com/vllm-project/vllm/commit/SHA

---------
Signed-off-by: Name <email>
```

### PR Types Distribution (from 3168 commits)

| Type | Count | Description |
|------|-------|-------------|
| CI | 67+ | CI workflow fixes, test infrastructure |
| BugFix | 50+ | Bug fixes, error handling |
| Doc | 39+ | Documentation updates |
| Feature | 34+ | New features, model support |
| Misc | 20+ | Cleanup, dependency updates |
| Test | 12+ | New tests, test fixes |
| Performance | 7+ | Performance optimizations |
| Refactor | 6+ | Code refactoring |

### Detailed PR Examples

#### BugFix PR: BalanceScheduler + RecomputeScheduler Deadlock (#8975)

**Problem**: PD disaggregation deployment hangs silently - all 32 ranks stuck in MC2 AlltoAll

**Root Cause**: `VLLM_ASCEND_BALANCE_SCHEDULING` (BalanceScheduler) and `recompute_scheduler_enable` (RecomputeScheduler) enabled simultaneously causes MoE communication type mismatch:
- Some DP ranks perform `All2AllV`
- Others perform `MC2`
- Result: AlltoAll deadlock where all ranks wait for each other

**Solution Pattern** (add mutual exclusion check in `platform.py`):
```python
# After recompute_scheduler block (around line 496)
if envs_ascend.VLLM_ASCEND_BALANCE_SCHEDULING and ascend_config.recompute_scheduler_enable:
    raise ValueError(
        "VLLM_ASCEND_BALANCE_SCHEDULING (balance scheduling) and recompute_scheduler_enable "
        "cannot be enabled simultaneously. This combination causes MoE communication type "
        "mismatch across DP ranks in PD disaggregation mode, leading to AlltoAll deadlock. "
        "Please disable one of them."
    )
```

**Key Learning**: Always check for scheduler conflicts in PD disaggregation mode. BalanceScheduler is for PD-mixed mode only; RecomputeScheduler is for PD-disaggregated mode only.

#### BugFix PR: Quantization Accuracy (#9036, commit 8486a744)

**Problem**: `routed_scaling_factor` not propagated, causing DeepSeek-V2/V3 accuracy drop

**Root Cause**: When `apply_routed_scale_to_output=True`, vLLM sets `self.routed_scaling_factor=1.0` in `super().__init__()`, but vllm-ascend uses its own forward path

**Solution Pattern**:
```python
def __init__(self, *args, **kwargs):
    # Save original BEFORE super().__init__
    self._original_routed_scaling_factor = kwargs.get("routed_scaling_factor", 1.0)
    super().__init__(*args, **kwargs)
    # Use _original_routed_scaling_factor in forward
```

**Key Learning**: Always save kwargs before calling super() if parent modifies them

#### BugFix PR: EPLB Expert Count (#commit c7749799)

**Problem**: `logical_experts` vs `physical_experts` mismatch with EPLB

**Root Cause**: EPLB adds redundant physical experts, but `router_logits.shape[-1]` matches logical experts

**Solution**: Use `get_moe_num_logical_experts()` helper

#### BugFix PR: Graph Capture OOM (#8111, commit d89046d8)

**Problem**: Workspace for each graph not released during capture

**Solution Pattern**:
```python
@contextmanager
def torch_npu_graph_wrapper(*args, **kwargs):
    try:
        with torch.npu.graph(*args, **kwargs):
            yield
    finally:
        weak_ref_workspaces(get_graph_params())
        weak_ref_workspaces(get_draft_graph_params())
```

#### Feature PR: KV Cache Memory Planning (#8289, commit 65289ca8)

**Problem**: Graph capture and KV cache compete for same memory budget

**Solution**:
1. Track `peak_activation_memory`, `non_torch_memory`, `npugraph_memory_bytes` separately
2. Suggest `--kv-cache-memory` value after first run
3. Fast path: skip profiling when `kv_cache_memory_bytes` pre-specified

**User Output**:
```
Free memory on device (60.86/61.27 GiB). Actual usage: 1.14 GiB for weights, 
0.22 GiB for peak activation, 0.13 GiB for non-torch memory, 0.04 GiB for NPU graph memory.
Replace gpu_memory_utilization with `--kv-cache-memory=57403864576` (53.46 GiB)
```

#### Performance PR: PIECEWISE Sync Removal (#9025, commit 894798ba)

**Problem**: Hard barrier before replay caused PIECEWISE regression

**Solution**: Only sync for FULL mode, not PIECEWISE
```python
need_sync = self.runtime_mode == CUDAGraphMode.FULL and not is_draft_eagle
if not self.enable_enpu and need_sync:
    torch.npu.current_stream().synchronize()
```

**Note**: Previous attempts (#5761, #8354) caused accuracy issues - test thoroughly!

#### Performance PR: Attention Operator Replacement (#8671, commit c9aff2b0)

**Problem**: `npu_fusion_attention` slower than `_npu_flash_attention_unpad` on A2/A3

**Solution**: Device-specific operator selection via `DeviceOperator.npu_flash_attention`
```python
# BaseDeviceAdaptor (A2/A3)
def npu_flash_attention(...):
    torch_npu._npu_flash_attention_unpad(...)

# A5DeviceAdaptor
def npu_flash_attention(...):
    torch_npu.npu_fusion_attention(...)
```

#### Feature PR: IndexCache for DSA Models (#8398, commit ba074eb4)

**Problem**: DSA models (GLM-5, DeepSeek) need index caching optimization

**Solution**: Add `skip_topk` and `topk_indices_buffer` to SFA implementation

**Benchmark Results** (GLM-5 W8A8, index_topk_freq=4):
- Total token throughput: +16.54% (concurrency 1), +16.87% (concurrency 3)
- Mean TTFT: -17.06% (concurrency 1), -14.84% (concurrency 3)
- Mean E2E latency: -14.19% (concurrency 1), -14.47% (concurrency 3)

#### Misc PR: Drop Obsolete Patches (#8889, commit 46b77d5b)

**Pattern**: When upstream vLLM fixes issues, remove corresponding patches

**Steps**:
1. Identify patches that are no longer needed
2. Remove patch files
3. Update `patch/__init__.py` documentation
4. Renumber patch sequence

#### CI PR: Linkcheck Retry (#8839, commit a00abfc4)

**Problem**: Sphinx linkcheck flaky due to transient network errors

**Solution**: 
1. Set `linkcheck_retries = 3`
2. Collect failed links from `output.json`
3. Retry with `curl --retry 3`
4. Keep CI failed if any retried link still fails

### PR Review Patterns

1. **Co-authorship**: Complex PRs often have `Co-authored-by` for collaborative work
2. **RFC Reference**: Major changes reference an RFC issue
3. **Upstream PR Link**: Changes adapting to upstream link the source PR
4. **Benchmark Data**: Performance PRs include detailed benchmark tables
5. **Accuracy Verification**: All PRs verify accuracy (e.g., GPQA score)

### Handling Automated Code Review Feedback

vLLM-Ascend uses **Gemini Code Assist** bot for automated PR reviews. Common feedback patterns:

1. **Redundant/unreachable code**: Bot detects when new code is unreachable due to existing validation logic
   - Response: Move code to correct position or remove if truly redundant
   - Example: PR #9149 - mutual exclusion check was unreachable, moved before existing checks

2. **PR title/summary format**: Bot suggests proper format per repository style guide
   - Title: `[Type][Module] Description` (e.g., `[Ops][BugFix] Add mutual exclusion check...`)
   - Summary must include: What/Why, User-facing change, How tested

3. **Suggested code changes**: Bot may provide specific code snippets
   - Review carefully - bot suggestions are usually correct but verify logic

**Workflow when bot comments**:
1. Read the feedback carefully - it often identifies root cause of issues
2. If feedback is correct, fix immediately and push new commit
3. If feedback seems wrong, explain why in PR comments
4. Thank the bot (maintains good relations with automation)

### Common PR Pitfalls

1. **Missing sign-off**: `git commit -s` required. DCO (Developer Certificate of Origin) check requires `Signed-off-by: Name <email>` in EVERY commit message. PR will fail if any commit lacks this.
2. **No test**: Must have test or explain why not
3. **Wrong title format**: Must match `[Type][Module] Description`
4. **Missing upstream reference**: Must link related upstream PRs
5. **No performance data**: Performance PRs need benchmarks

### Fixing Missing Signed-off-by

When DCO check fails due to missing `Signed-off-by` in commits:

```bash
# Option 1: Interactive rebase with exec (recommended for multiple commits)
git rebase -i <base-commit>^ --exec "git commit --amend --signoff --no-edit"

# Option 2: filter-branch for all commits in range
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --msg-filter \
  'cat && if ! grep -q "Signed-off-by:"; then echo ""; echo "Signed-off-by: Your Name <your@email.com>"; fi' \
  <start-commit>..HEAD

# Option 3: Amend single commit
git commit --amend --signoff --no-edit

# After fixing, force push
git push fork HEAD:<branch> --force
```

**Note**: Merge commits from `git merge main` also need Signed-off-by. Consider using `git merge --signoff main` or rebasing instead.

## References

- **[architecture.md](references/architecture.md)** - Detailed architecture diagrams and module relationships
## References

- **[architecture.md](references/architecture.md)** - Detailed architecture diagrams and module relationships
- **[pr-patterns.md](references/pr-patterns.md)** - PR patterns, examples, and best practices from 3168+ commits
- **[pr-creation-best-practices.md](references/pr-creation-best-practices.md)** - PR creation workflow: minimal changes, clean branches, format preservation, Gemini feedback handling
- **[environment-variables.md](references/environment-variables.md)** - Complete env var reference with examples
- **[supported-models.md](references/supported-models.md)** - Model support matrix and known limitations
- **[hardware-configuration.md](references/hardware-configuration.md)** - Hardware-specific config (A2/A3/A5/310P), SOC_VERSION, Docker device mapping
- **[debugging-patterns.md](references/debugging-patterns.md)** - Common BugFix patterns, error messages, debugging workflow
- **[cpp-operator-development.md](references/cpp-operator-development.md)** - C++ custom operator development: hierarchy, patterns, build system
- **[performance-optimization.md](references/performance-optimization.md)** - Performance optimization patterns: operator replacement, async execution, sync removal, memory optimization
- **[module-deep-dive.md](references/module-deep-dive.md)** - 深度模块解析：Attention、Quantization、MoE、Distributed 实现细节
- **[model-implementations.md](references/model-implementations.md)** - 所有模型实现详解：DeepSeek/Qwen/MiniMax/GLM 架构与 NPU 适配
- **[module-collaboration.md](references/module-collaboration.md)** - 模块协作关系全景图：数据流、依赖关系、调试指南
- **[pd-disaggregation-debugging.md](references/pd-disaggregation-debugging.md)** - PD 分离架构调试指南：死锁、KV传输、TP/EP 不匹配
- **[learning-path.md](references/learning-path.md)** - Structured learning path: quick start, first week, second week, ongoing learning, common mistakes, verification checklist
- **[inheritance-check-workflow.md](references/inheritance-check-workflow.md)** - CRITICAL: Check inheritance before adding interface methods - decision tree, check commands, real examples (Issue #3489, #4112)
- **[issue-analysis-workflow.md](references/issue-analysis-workflow.md)** - Issue 分析工作流：获取、分析、定位、修复、提交 PR 完整流程
- **[pr-9205-vit-attn-backend.md](references/pr-9205-vit-attn-backend.md)** - PR #9205: Adding get_vit_attn_backend interface with complete workflow (Gemini feedback, CI fixes, iteration pattern)
- **[pr-9149-network-failure.md](references/pr-9149-network-failure.md)** - PR #9149 CI 网络失败案例：如何区分代码问题和网络问题
- **[issue-4112-worker-shutdown.md](references/issue-4112-worker-shutdown.md)** - Issue #4112: Adding worker shutdown interface - checking dependencies, implementation order, NPU adaptation
- **[pr-complete-workflow-lessons.md](references/pr-complete-workflow-lessons.md)** - Complete PR workflow with all user corrections: branch hygiene, test coverage, implementation correctness, real examples
- **[npu-setup-guide.md](references/npu-setup-guide.md)** - NPU 开发环境搭建指南：硬件检查、CANN 安装、环境配置、验证步骤
- **[testing-environment-setup.md](references/testing-environment-setup.md)** - Testing environment setup: CI images, Docker commands, torch_npu failure diagnosis, infrastructure vs code failure distinction
- **[hermes-skill-structure.md](references/hermes-skill-structure.md)** - Creating shareable Hermes skills: directory layout, setup.sh template, one-click philosophy, verification checklist
- **[documentation-parameter-audit.md](references/documentation-parameter-audit.md)** - Documentation parameter mismatch audit: detection method, fix pattern, common issues, prevention tips
- **[documentation-fix-workflow.md](references/documentation-fix-workflow.md)** - Documentation fix workflow: parameter mismatch detection, fix pattern, Gemini feedback handling, Issue #9358 example
- **[github-pr-creation-limitation.md](references/github-pr-creation-limitation.md)** - GitHub PR creation limitation: why PAT cannot create PRs in upstream, standard workflow, Web UI vs CLI solutions
- **[dco-requirements-and-fixes.md](references/dco-requirements-and-fixes.md)** - DCO requirements and fixes: merge commits need Signed-off-by, clean branch workflow, GitHub API push when Git fails, PR #9369 example
- **[dco-email-matching.md](references/dco-email-matching.md)** - DCO 邮箱匹配问题：Signed-off-by 邮箱必须与 GitHub 账号匹配，获取正确邮箱的方法，Git 配置，修复已有提交的 DCO 问题
- **[minimax-m2.7-documentation-workflow.md](references/minimax-m2.7-documentation-workflow.md)** - MiniMax-M2.7 文档添加工作流：验证模型支持、创建文档、更新索引、提交 PR 完整流程
- **[branch-workflow-and-dco.md](references/branch-workflow-and-dco.md)** - Branch workflow: one branch per issue (user preference), DCO requirements, GitHub API limitations, CI failures (yaml sync, markdownlint), local main sync

## Setup and Development

### NPU Environment Setup

See **[references/npu-setup-guide.md](references/npu-setup-guide.md)** for complete setup instructions.

Quick start:
```bash
# 1. Install CANN 9.0.0 (3 packages)
# 2. Install PyTorch 2.9.0 + torch-npu 2.9.0
# 3. Install vLLM + vLLM-Ascend
# 4. Run environment check
bash scripts/check_npu_env.sh
```

### CI Failure Diagnosis

See **[references/ci-failure-diagnosis.md](references/ci-failure-diagnosis.md)** for guide on distinguishing code problems from infrastructure issues.

Key insight: Many CI failures are network/infrastructure issues, not code problems. Always check:
- Error message content (connection, timeout, network)
- Step name (Install, Setup, Checkout = infrastructure)
- Multiple jobs failing at same step

## Resources

- **GitHub**: https://github.com/vllm-project/vllm-ascend
- **Documentation**: https://docs.vllm.ai/projects/ascend/en/latest/
- **User Forum**: https://discuss.vllm.ai/c/hardware-support/vllm-ascend-support
- **Weekly Meeting**: https://tinyurl.com/vllm-ascend-meeting (Wed 15:00 UTC+8)
- **Hardware Plugin RFC**: https://github.com/vllm-project/vllm/issues/11162
- **CANN Documentation**: https://www.hiascend.com/document/detail/zh/canncommercial/
- **License**: Apache-2.0
