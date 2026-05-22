# Documentation Parameter Mismatch Audit

## Issue

When serving models with `--served-model-name`, the value MUST match the `"model"` parameter in client curl requests. Mismatches cause "model not found" errors.

## Detection Method

```bash
# Find all documentation files with served-model-name
for file in $(grep -r "served-model-name" docs/ --include="*.md" -l); do
    echo "【文件】: $file"
    
    # Extract served-model-name values
    served_names=$(grep -oP "served-model-name\s+\K\w+" "$file" | sort -u)
    echo "  served-model-name 值: $served_names"
    
    # Extract model parameter values
    model_values=$(grep -oP '"model":\s*"\K[^"]+' "$file" | sort -u)
    echo "  model 值: $model_values"
    
    # Check for mismatches
    for sn in $served_names; do
        for mv in $model_values; do
            if [ "$sn" != "$mv" ]; then
                echo "  ⚠️  不匹配: served-model-name='$sn' vs model='$mv'"
            fi
        done
    done
done
```

## Audit Results (May 2026)

### ✅ Correctly Matched

| Document | served-model-name | model | Status |
|----------|------------------|-------|--------|
| DeepSeek-R1.md | `deepseek_r1` | `deepseek_r1` | ✅ Match |
| DeepSeek-V3.1.md | `deepseek_v3` | `deepseek_v3` | ✅ Match |
| DeepSeekOCR2.md | `deepseekocr2` | `deepseekocr2` | ✅ Match |
| Hunyuan-A13B-Instruct.md | `Hunyuan` | `Hunyuan` | ✅ Match |
| Qwen3-235B-A22B.md | `qwen3` | `qwen3` | ✅ Match |
| Qwen3-Dense.md | `qwen3` | `qwen3` | ✅ Match |
| Qwen3-VL-235B-A22B-Instruct.md | `qwen3` | `qwen3` | ✅ Match |
| pd_disaggregation_mooncake_multi_node.md | `ds_r1` | `ds_r1` | ✅ Match |
| pd_disaggregation_mooncake_single_node.md | `qwen25vl` | `qwen25vl` | ✅ Match |
| ray.md | `qwen` | `qwen` | ✅ Match |

### ❌ Mismatched (Need Fix)

| Document | served-model-name | model | Issue |
|----------|------------------|-------|-------|
| **DeepSeek-V3.2.md** | `dsv3` | `deepseek_v3.2` | ❌ **FIXED in PR** |
| GLM4.x.md | `glm47` | `glm` | ⚠️ Multiple values |
| GLM5.md | `glm` | `glm-5` | ❌ Mismatch |
| Kimi-K2.5.md | `kimi_k25` | `lightseekorg/kimi-k2.5-eagle3` | ⚠️ Different contexts |
| LLaVA-OneVision-Qwen2-0.5B-OV.md | `LLaVA` | `LLaVA-OneVision-0.5B` | ❌ Mismatch |
| Minitron-8B-Base.md | `minitron` | `minitron-8b-base` | ❌ Mismatch |
| Qwen2.5-Math-RM-72B.md | `qwen2` | `qwen2.5-math-rm-72b` | ❌ Mismatch |
| Qwen3-Coder-30B-A3B.md | `qwen3` | `qwen3-coder` | ❌ Mismatch |
| Qwen3.5-27B.md | `qwen3` | `qwen3.5` | ❌ Mismatch |
| Qwen3.5-397B-A17B.md | `qwen3` | `qwen3.5` | ❌ Mismatch |

## Fix Pattern

### Step 1: Identify the correct value

**Options**:
1. Use full model name (recommended): `deepseek_v3.2`, `qwen3.5`, `glm-5`
2. Use short alias: `dsv3`, `qwen3`, `glm`
3. Use model ID: `deepseek-ai/DeepSeek-V3.2`

**Recommendation**: Use the full model name for clarity and consistency.

### Step 2: Update documentation

```bash
# Find all instances
grep -n "served-model-name OLD_VALUE" docs/path/to/file.md

# Replace with correct value
sed -i 's/served-model-name OLD_VALUE/served-model-name NEW_VALUE/g' docs/path/to/file.md
```

### Step 3: Add parameter explanation

Add note explaining placeholder parameters:

```markdown
## Functional Verification

Once your server is started, you can query the model with input prompts:

**Note**: 
- `<node0_ip>`: The IP address of the node where the server is running. Use `localhost` if running locally.
- `<port>`: The port number specified in the server startup command (e.g., `7000`).

```shell
curl http://localhost:7000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "deepseek_v3.2",
        "prompt": "The future of AI is",
        "max_completion_tokens": 50
    }'
```
```

### Step 4: Verify fix

```bash
# Check served-model-name values
grep "served-model-name" docs/path/to/file.md

# Check model parameter values
grep '"model"' docs/path/to/file.md

# Should match!
```

## Example Fix: DeepSeek-V3.2.md (Issue #9358)

### Before

```shell
# Server startup
vllm serve /path/to/model \
    --served-model-name dsv3 \    # ← Short alias
    ...

# Client request
curl http://<node0_ip>:<port>/v1/completions \
    -d '{
        "model": "deepseek_v3.2",  # ← Full name (MISMATCH!)
        ...
    }'
```

**Problem**: `dsv3` != `deepseek_v3.2` → "model not found" error

### After

```shell
# Server startup
vllm serve /path/to/model \
    --served-model-name deepseek_v3.2 \  # ← Full name
    ...

# Client request  
curl http://localhost:7000/v1/completions \  # ← Concrete example
    -d '{
        "model": "deepseek_v3.2",  # ← Full name (MATCH!)
        ...
    }'
```

**Result**: Parameters match, request succeeds

### Changes Made

1. Replaced all `--served-model-name dsv3` with `--served-model-name deepseek_v3.2` (4 occurrences)
2. Added parameter explanation for `<node0_ip>` and `<port>`
3. Changed `<node0_ip>:<port>` to concrete `localhost:7000` example

## Related Issues

- Issue #9358: DeepSeek-V3.2.md parameter mismatch
- Similar issues likely exist in other model documentation

## Prevention

### For documentation authors

1. **Always test the example**: Run the exact commands in documentation
2. **Use consistent naming**: Pick one naming scheme and stick to it
3. **Explain placeholders**: Document what `<node0_ip>` and `<port>` mean
4. **Provide concrete examples**: Show actual values like `localhost:7000`

### For reviewers

1. **Check parameter consistency**: Verify served-model-name matches model parameter
2. **Test the documentation**: Follow the steps exactly as written
3. **Look for placeholders**: Ensure all placeholders are explained

## Automation Opportunity

Create a CI check that validates documentation parameter consistency:

```yaml
# .github/workflows/doc-check.yaml
name: Documentation Parameter Check

on: [pull_request]

jobs:
  check-params:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check served-model-name consistency
        run: |
          for file in $(grep -r "served-model-name" docs/ --include="*.md" -l); do
            served=$(grep -oP "served-model-name\s+\K\w+" "$file" | sort -u)
            model=$(grep -oP '"model":\s*"\K[^"]+' "$file" | sort -u)
            if [ "$served" != "$model" ]; then
              echo "::error file=$file::served-model-name ($served) != model parameter ($model)"
              exit 1
            fi
          done
```

This would catch mismatches before they're merged.

## Reference

- Issue: #9358
- PR: Fix DeepSeek-V3.2.md parameter mismatch
- Date: May 2026
- Files affected: `docs/source/tutorials/models/DeepSeek-V3.2.md`
