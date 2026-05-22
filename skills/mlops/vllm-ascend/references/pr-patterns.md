# vLLM-Ascend PR Patterns and Examples

Analysis of 3168+ commits from vllm-ascend repository.

## PR Type Distribution

| Type | Count | Typical Scenarios |
|------|-------|-------------------|
| `[CI]` | 67+ | CI config, test workflows, image builds |
| `[BugFix]` | 50+ | Functional fixes, accuracy, compatibility |
| `[Doc]` | 39+ | Documentation, tutorials |
| `[Feature]` | 34+ | New features, models, operators |
| `[Misc]` | 20+ | Cleanup, dependency updates |
| `[Test]` | 12+ | Unit tests, E2E tests |
| `[Performance]` | 7+ | Optimizations |
| `[Refactor]` | 6+ | Architecture improvements |

## Example PRs

### BugFix: mooncake_connector multi-layer draft model (#8928)

**Problem**: Connector assumed only one additional layer for MTP.

**Solution**:
```python
# Before
end_layer_index = end_layer_index + 1

# After
self.num_draft_layers = 0
if self.vllm_config.speculative_config is not None:
    if self.vllm_config.speculative_config.method == "mtp":
        self.num_draft_layers = 1
    elif hasattr(...):
        self.num_draft_layers = num_hidden_layers
end_layer_index = end_layer_index + self.num_draft_layers
```

**Files changed**: 1 file, +16/-3 lines

### Performance: Remove sync for PIECEWISE (#9025)

**Problem**: Hard barrier before replay caused performance regression in PIECEWISE mode.

**Solution**:
```python
# Before
if not self.enable_enpu and not is_draft_eagle:
    torch.npu.current_stream().synchronize()

# After
need_sync = self.runtime_mode == CUDAGraphMode.FULL and not is_draft_eagle
if not self.enable_enpu and need_sync:
    torch.npu.current_stream().synchronize()
```

**Files changed**: 1 file, +3/-2 lines

### Refactor: Replace monkey-patch with PluggableLayer (#8702)

**Goal**: Replace runtime monkey-patching with explicit OOT replacement.

**Changes**:
1. Add `vllm_ascend/ops/bailing_moe_linear_attn.py` (169 lines)
2. Delete `vllm_ascend/patch/worker/patch_bailing_moe_linear.py`
3. Register in `utils.py`

**Pattern**:
```python
class AscendBailingMoELinearAttention(BailingMoELinearAttention):
    """NPU-friendly drop-in replacement."""
    
    def _prefill_and_mix_infer(self, q, k, v, ...):
        # NPU-specific implementation
        ...
    
    def _decode_infer(self, q, k, v, ...):
        # NPU-specific implementation
        ...
```

### Feature: LoRA with Qwen3.5 dense model (#9023)

**Changes**:
1. Modify `vllm_ascend/ops/gdn.py` - support projection layout
2. Modify `vllm_ascend/lora/utils.py` - handle merged linear layers
3. Add test `tests/e2e/singlecard/test_qwen35_densemodel_lora.py`
4. Update CI config `.github/workflows/scripts/config.yaml`

**Files changed**: 5 files, +126/-144 lines

### Test: MLA attention unit tests (#9043)

**Added**:
- `tests/ut/attention/test_mla_precision.py` (684 lines)
- `tests/ut/attention/utils.py` (268 lines)

**Pattern**: Compare MLA backend output against reference PyTorch SDPA.

## Key Lessons

1. **Minimal changes**: BugFix PRs often touch 1-2 files with small diffs
2. **Always add tests**: New features require corresponding tests
3. **Document performance**: Performance PRs should explain the gain
4. **Reference issues**: Use "Fixes #xxx" to link to issues
5. **Sign-off required**: All commits must be signed off
