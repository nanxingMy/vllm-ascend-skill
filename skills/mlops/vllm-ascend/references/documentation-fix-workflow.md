# Documentation Fix Workflow

## Overview

Fixing documentation issues in vLLM-Ascend follows a specific workflow, especially for parameter mismatch issues.

## Parameter Mismatch Detection

### Problem Pattern

When serving models with custom `--served-model-name`, the value MUST match the `"model"` parameter in client requests.

**Symptoms**:
- Client request fails with "model not found" error
- User follows documentation exactly but gets error
- Issue reports about parameter inconsistency

### Detection Script

```bash
# Find all docs with served-model-name
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

## Fix Pattern

### Steps

1. **Identify the correct model name**
   - Check if the model parameter is the actual API name (don't change it!)
   - Update served-model-name to match the model parameter

2. **Update all instances**
   - Use `patch` with `replace_all=true` to update all occurrences
   - Verify with `git diff` that changes are minimal

3. **Add parameter explanation**
   - Explain what `<node0_ip>` means (e.g., localhost)
   - Explain what `<port>` means (e.g., 8000)
   - Use concrete examples

4. **Keep placeholders for clarity**
   - Don't hardcode values like `localhost:7000`
   - Keep `<node0_ip>:<port>` for generality
   - Add explanation in notes

### Example: Issue #9358

**File**: `docs/source/tutorials/models/DeepSeek-V3.2.md`

**Problem**:
- served-model-name: `dsv3`
- model parameter: `deepseek_v3.2`
- Mismatch causes "model not found" error

**Fix**:
```bash
# Update served-model-name to match model parameter
patch --replace-all \
  --old "served-model-name dsv3" \
  --new "served-model-name deepseek_v3.2"
```

**Add explanation**:
```markdown
**Note**: 
- `<node0_ip>`: The IP address of the node where the server is running (e.g., localhost).
- `<port>`: The port number specified in the server startup command (e.g., 8000).

```shell
curl http://<node0_ip>:<port>/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "deepseek_v3.2",
        ...
    }'
```
```

## Gemini Code Assist Feedback

### Common Feedback for Doc PRs

1. **PR title format**: Add `[BugFix]` tag
   ```
   Wrong: [Doc] Fix parameter mismatch
   Right: [Doc][BugFix] Fix parameter mismatch
   ```

2. **Parameter naming consistency**: Use consistent naming throughout
   - If Gemini says "don't change model parameter", it's usually correct
   - The model parameter might be the actual API name

3. **Port number consistency**: Match port numbers with rest of document
   - Check other examples in the document
   - Use the same port (usually 8000, not 7000)

4. **Placeholder vs hardcoded**: Keep placeholders for clarity
   - Don't hardcode `localhost:7000`
   - Keep `<node0_ip>:<port>` with explanation

### Workflow

1. Create PR and wait 2-3 minutes for Gemini feedback
2. Fetch feedback via GitHub API:
   ```bash
   curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/pulls/{PR_NUM}/comments"
   ```
3. Review each feedback carefully
4. Apply corrections in new commit
5. Push → CI re-runs automatically

## Common Mismatches Found (May 2026 Audit)

| Document | served-model-name | model | Status |
|----------|------------------|-------|--------|
| DeepSeek-V3.2.md | `dsv3` | `deepseek_v3.2` | ✅ Fixed (PR #9369) |
| GLM4.x.md | `glm47` | `glm` | ⚠️ Pending |
| GLM5.md | `glm` | `glm-5` | ⚠️ Pending |
| Qwen3.5-27B.md | `qwen3` | `qwen3.5` | ⚠️ Pending |
| Qwen3.5-397B-A17B.md | `qwen3` | `qwen3.5` | ⚠️ Pending |

## Prevention Tips

1. **When adding new model documentation**:
   - Use full model name for both served-model-name and model parameter
   - Example: `deepseek_v3.2` for both, not `dsv3`

2. **When updating existing documentation**:
   - Run the detection script first
   - Fix all mismatches in one PR
   - Add explanation for placeholders

3. **When reviewing PRs**:
   - Check for parameter consistency
   - Verify port numbers match document style
   - Ensure placeholders have explanations

## Reference

- Issue #9358: DeepSeek-V3.2.md parameter mismatch
- PR #9369: Fix with Gemini Code Assist feedback
- Date: May 2026
