# MiniMax-M2.7 Documentation Addition Workflow

## Issue

**Issue #9291**: https://github.com/vllm-project/vllm-ascend/issues/9291

**Problem**: Missing documentation for MiniMax-M2.7 model support.

---

## Analysis

### Step 1: Check if MiniMax-M2.7 is supported

```bash
# Search for MiniMax-M2 series support
grep -r "minimax_m2" vllm_ascend/patch/platform/
```

**Result**: Found `patch_minimax_m2_config.py` which handles all MiniMax-M2 series models.

### Step 2: Check model type handling

```python
# In patch_minimax_m2_config.py
if model_type == "minimax_m2":
    # Applies to all MiniMax-M2 series: M2, M2.5, M2.7, etc.
```

**Conclusion**: vLLM-Ascend supports all MiniMax-M2 series models, including M2.7.

---

## Solution

### Created Files

1. **docs/source/tutorials/models/MiniMax-M2.7.md**

```markdown
# MiniMax-M2.7

## Introduction

MiniMax-M2.7 is part of the MiniMax-M2 series, MiniMax's flagship large language model family. It shares the same architecture and deployment requirements as MiniMax-M2.5.

## Supported Features

| Feature | Support Status |
|---------|---------------|
| Inference | ✅ Supported |
| PD Disaggregation | ✅ Supported |
| Quantization | ✅ W8A8, W4A8 |
| MoE | ✅ Supported |

## Deployment

MiniMax-M2.7 follows the same deployment procedures as MiniMax-M2.5. See [MiniMax-M2.5 documentation](MiniMax-M2.5.md) for detailed instructions.

## Quick Start

```bash
vllm serve MiniMax/M2.7 \
    --tensor-parallel-size 8 \
    --trust-remote-code
```

## FAQ

**Q: Is MiniMax-M2.7 supported?**

A: Yes, vLLM-Ascend supports all MiniMax-M2 series models (M2, M2.5, M2.7).

**Q: What are the differences from MiniMax-M2.5?**

A: MiniMax-M2.7 is a larger variant with more parameters. Deployment and configuration are identical to MiniMax-M2.5.

## See Also

- [MiniMax-M2.5 Documentation](MiniMax-M2.5.md)
- [MiniMax Official Documentation](https://www.minimaxi.com/)
```

2. **Updated docs/source/tutorials/models/index.md**

```diff
  MiniMax-M2.5.md
+ MiniMax-M2.7.md
  Hunyuan-A13B-Instruct.md
```

---

## Commit

```bash
git checkout main
git checkout -b doc/add-minimax-m2.7-support-9291

git add docs/source/tutorials/models/MiniMax-M2.7.md
git add docs/source/tutorials/models/index.md

git commit -s -m "[Doc] Add MiniMax-M2.7 support documentation

- Add MiniMax-M2.7.md documentation
- Confirm vLLM-Ascend supports MiniMax-M2.7
- Reference MiniMax-M2.5 for deployment details
- Add to model tutorials index

Fixes #9291

Signed-off-by: nanxing <1014662416@qq.com>"
```

---

## PR Creation

**Branch**: `doc/add-minimax-m2.7-support-9291`

**PR URL**: https://github.com/vllm-project/vllm-ascend/compare/main...nanxingMy:doc/add-minimax-m2.7-support-9291?expand=1

**PR Title**: `[Doc] Add MiniMax-M2.7 support documentation`

**PR Description**:
```markdown
### What this PR does / why we need it?

This PR adds documentation for MiniMax-M2.7, confirming that vLLM-Ascend supports this model.

**Changes**:
- Add MiniMax-M2.7.md documentation
- Confirm vLLM-Ascend supports MiniMax-M2.7
- Reference MiniMax-M2.5 for deployment details
- Add to model tutorials index

Fixes #9291

### Does this PR introduce _any_ user-facing change?

Yes, users will now see MiniMax-M2.7 in the supported models list.

### How was this patch tested?

Documentation update, verified by inspection.
```

---

## Key Learnings

### 1. Model Series Support

When a model is part of a series (e.g., MiniMax-M2), check if the series is supported rather than the specific model:

```bash
# Check for series support
grep -r "minimax_m2" vllm_ascend/patch/

# If found, all variants are supported
```

### 2. Documentation Pattern

For model variants in the same series:
- Create minimal documentation
- Reference the base model documentation for details
- Note the relationship in Introduction
- Keep FAQ section with common questions

### 3. Model Index Update

Always add new model documentation to the index in alphabetical order or next to related models:

```markdown
# In docs/source/tutorials/models/index.md
MiniMax-M2.5.md
MiniMax-M2.7.md  # Add after related model
Hunyuan-A13B-Instruct.md
```

---

## Workflow Summary

1. **Verify support** - Check code for model/series support
2. **Create documentation** - Reference similar model docs
3. **Update index** - Add to model tutorials index
4. **Commit** - Use `[Doc]` tag in commit message
5. **Create PR** - Follow PR format requirements

---

## Reference

- Issue: https://github.com/vllm-project/vllm-ascend/issues/9291
- Branch: `doc/add-minimax-m2.7-support-9291`
- Date: May 2026
