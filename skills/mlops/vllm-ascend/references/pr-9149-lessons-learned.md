# PR #9149: BalanceScheduler + RecomputeScheduler Mutual Exclusion

**Issue**: #8975  
**PR**: https://github.com/vllm-project/vllm-ascend/pull/9149  
**Status**: Merged (after code review feedback and test addition)

## Problem

PD disaggregation deployment hangs silently - all 32 ranks stuck in MC2 AlltoAll.

**Root Cause**: `VLLM_ASCEND_BALANCE_SCHEDULING` (BalanceScheduler) and `recompute_scheduler_enable` (RecomputeScheduler) enabled simultaneously causes MoE communication type mismatch:
- Some DP ranks perform `All2AllV`
- Others perform `MC2`
- Result: AlltoAll deadlock where all ranks wait for each other

## Initial Fix (Incorrect)

Added mutual exclusion check at line 502 in `platform.py`:

```python
# After recompute_scheduler block (line 496-508)
if envs_ascend.VLLM_ASCEND_BALANCE_SCHEDULING and ascend_config.recompute_scheduler_enable:
    raise ValueError("...")
```

## Gemini Code Assist Feedback

**Issue**: The check is **redundant and unreachable** in its current position.

**Reasoning**:
- Line 474-482: `VLLM_ASCEND_BALANCE_SCHEDULING` requires `kv_role='kv_both'` or `None` (PD-mixed mode)
- Line 484-491: `recompute_scheduler_enable` requires `kv_role='kv_producer'/'kv_consumer'` (PD-disaggregated mode)
- These modes are logically opposite, so one of the preceding checks will always raise `ValueError` before the new check is reached

**Suggestion**: Move check to before line 474 (beginning of scheduler configuration section)

## Corrected Fix

```python
# At line 474 (BEFORE other scheduler checks)
# NOTE: BalanceScheduler and RecomputeScheduler must not be enabled simultaneously.
# In PD disaggregation mode with multi-DP MoE, enabling both schedulers can cause
# MoE communication type mismatch across DP ranks (some perform All2AllV, others MC2),
# leading to AlltoAll deadlock. See https://github.com/vllm-project/vllm-ascend/issues/8975
if envs_ascend.VLLM_ASCEND_BALANCE_SCHEDULING and ascend_config.recompute_scheduler_enable:
    raise ValueError(
        "VLLM_ASCEND_BALANCE_SCHEDULING (balance scheduling) and recompute_scheduler_enable "
        "cannot be enabled simultaneously. This combination causes MoE communication type "
        "mismatch across DP ranks in PD disaggregation mode, leading to AlltoAll deadlock. "
        "Please disable one of them."
    )

if envs_ascend.VLLM_ASCEND_BALANCE_SCHEDULING:  # Now this comes AFTER
    ...
```

## Key Learnings

### 1. Validation Check Placement Order

When adding new validation checks, analyze existing checks first:
- Do existing checks already enforce the constraint?
- If yes, is the new check reachable?
- If unreachable, either move it before existing checks or don't add it

### 2. Implicit Mutual Exclusion

Two features can be mutually exclusive without explicit checks if:
- Feature A requires condition X
- Feature B requires condition NOT X
- Existing validation enforces both conditions

### 3. Automated Code Review is Valuable

Gemini Code Assist correctly identified:
- The code was unreachable
- The reasoning why (existing checks enforce mutual exclusivity)
- The solution (move check to correct position)

Always read bot feedback carefully - it often catches subtle logic errors.

## PR Title Format

```
[Ops][BugFix] Add mutual exclusion check for BalanceScheduler and RecomputeScheduler
```

## PR Description Template

```markdown
### What this PR does / why we need it?

This PR adds a mutual exclusion check to prevent `VLLM_ASCEND_BALANCE_SCHEDULING` 
(BalanceScheduler) and `recompute_scheduler_enable` (RecomputeScheduler) from being 
enabled simultaneously. This combination causes MoE communication type mismatches 
across DP ranks in PD disaggregation mode, leading to AlltoAll deadlocks.

Fixes #8975

### Does this PR introduce _any_ user-facing change?

Yes. Users who attempt to enable both schedulers will now receive a clear `ValueError` 
at startup explaining the conflict and the risk of deadlock.

### How was this patch tested?

- Logic verification: Confirmed that the check prevents conflicting configurations.
- Linting: `ruff check vllm_ascend/platform.py` passed.
```

## Files Modified

- `vllm_ascend/platform.py`: Added mutual exclusion check at line 474 (+12 lines)
- `tests/ut/test_platform.py`: Added unit test (+37 lines)

## Unit Test Added

Test follows existing pattern in `tests/ut/test_platform.py`:

```python
@patch("vllm_ascend.quantization.utils.maybe_auto_detect_quantization")
@patch("vllm_ascend.utils.get_ascend_device_type", return_value=AscendDeviceType.A3)
@patch("vllm_ascend.ascend_config.init_ascend_config")
@patch("vllm_ascend.core.recompute_scheduler.RecomputeSchedulerConfig.initialize_from_config")
def test_check_and_update_config_rejects_both_balance_and_recompute_scheduler(
    self, mock_init_recompute, mock_init_ascend, mock_soc_version, mock_auto_detect
):
    """Test that enabling both BalanceScheduler and RecomputeScheduler raises ValueError.
    
    This test verifies the mutual exclusion check added to prevent deadlock in
    PD disaggregation mode with multi-DP MoE. See Issue #8975.
    """
    mock_ascend_config = TestNPUPlatform.mock_vllm_ascend_config()
    mock_ascend_config.recompute_scheduler_enable = True
    mock_init_ascend.return_value = mock_ascend_config

    vllm_config = TestNPUPlatform.mock_vllm_config()
    vllm_config.kv_transfer_config = MagicMock(kv_role="kv_producer", engine_id="engine0")
    vllm_config.parallel_config.decode_context_parallel_size = 1
    vllm_config.parallel_config.prefill_context_parallel_size = 1
    vllm_config.parallel_config.tensor_parallel_size = 1
    vllm_config.scheduler_config = MagicMock()
    mock_init_recompute.return_value = MagicMock()

    from vllm_ascend import platform
    importlib.reload(platform)
    self.platform = platform.NPUPlatform()

    with (
        patch("vllm_ascend.platform.envs_ascend.VLLM_ASCEND_BALANCE_SCHEDULING", True, create=True),
        pytest.raises(ValueError, match=r"VLLM_ASCEND_BALANCE_SCHEDULING.*recompute_scheduler_enable.*cannot be enabled simultaneously"),
        patch.object(platform.NPUPlatform, "_fix_incompatible_config"),
        patch.object(platform, "check_kv_extra_config"),
    ):
        self.platform.check_and_update_config(vllm_config)
```

### Test Pattern Notes

1. **Mock decorators**: Use `@patch` for external dependencies
2. **Mock configs**: Use `TestNPUPlatform.mock_vllm_config()` and `mock_vllm_ascend_config()`
3. **Reload platform**: `importlib.reload(platform)` to pick up mocked values
4. **Exception matching**: Use `pytest.raises(ValueError, match=r"pattern")` with regex
5. **Environment variables**: Mock with `patch("module.envs.VAR", value, create=True)`

## Final Commits

1. `c2b41357` - [Ops][BugFix] Add mutual exclusion check for BalanceScheduler and RecomputeScheduler
2. `f12863ec` - [Test] Add unit test for BalanceScheduler and RecomputeScheduler mutual exclusion

---

## PR Monitoring & Automation

### Cron Job for PR Monitoring

Created `vllm-ascend-pr-monitor` cron job to automatically check PR status every 10 minutes:

```yaml
name: vllm-ascend-pr-monitor
schedule: every 10m
```

The cron job:
1. Fetches PR status via GitHub API
2. Checks for new reviews/comments
3. Analyzes feedback and determines if action needed
4. Reports status summary

### Skill for PR Feedback Handling

Created `pr-feedback-handler` skill for on-demand PR analysis:

```bash
# Use the skill
skill_view(name='pr-feedback-handler')
```

### Git Credential Management (Windows)

When switching GitHub users:

```bash
# List stored credentials
git credential-manager github list

# Get current credential
echo "protocol=https
host=github.com" | git credential-manager get

# Store new credential
echo "protocol=https
host=github.com
username=nanxingMy
password=<TOKEN>" | git credential-manager store

# Erase old credential
echo "protocol=https
host=github.com
username=fouronessu" | git credential-manager erase
```

### Token Scope Requirements

| Action | Required Scope |
|--------|---------------|
| Push to fork | `repo` (for user's repos) |
| Update PR title/body | `public_repo` or `repo` |
| Read PR info | No auth required (public repos) |

**Note**: Token with only fork access cannot update PR on main repo. Use Issues API:

```bash
curl -X PATCH \
  -H "Authorization: token $TOKEN" \
  -d '{"title": "...", "body": "..."}' \
  "https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}"
```

### PR Review Status Analysis

```bash
# Get requested reviewers
curl -s "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/requested_reviewers"

# Analyze review states
curl -s "https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews" | python3 -c "
import sys, json
reviews = json.load(sys.stdin)
states = {}
for r in reviews:
    state = r.get('state', 'UNKNOWN')
    states[state] = states.get(state, 0) + 1
print(f'状态统计: {states}')
# APPROVED: 可合并
# CHANGES_REQUESTED: 需要修改
# COMMENTED: 仅评论
"
```

### mergeable_state Meanings

| State | Meaning |
|-------|---------|
| clean | Ready to merge |
| unstable | CI failing or pending |
| dirty | Merge conflicts |
| blocked | Branch protection rules |
| behind | Behind base branch |
| draft | Draft PR |

### Fork PR CI Limitations

Fork PRs have CI checks **skipped** by default due to security:
- Prevents malicious code execution in CI
- Maintainers can manually trigger CI
- Alternative: Use `[ci]` in commit message (if allowed)

---

## DCO (Developer Certificate of Origin) Fix

### Problem

DCO check failed with `action_required` status because commits lacked `Signed-off-by` line.

**Symptoms**:
- Check run shows `conclusion: action_required`
- PR `mergeable_state` remains `unstable`
- Commit message missing `Signed-off-by: Name <email>`

### Root Cause

vLLM-Ascend uses DCO GitHub App which requires every commit to have:
```
Signed-off-by: Your Name <your@email.com>
```

This certifies the developer has the right to submit the patch (similar to Linux kernel).

### Fix Workflow

**Option 1: Interactive rebase with exec (recommended for multiple commits)**

```bash
# Rebase from base commit, auto-signing each
git rebase -i <base-commit>^ --exec "git commit --amend --signoff --no-edit"

# Example: fix commits from c2b41357 onwards
git rebase -i c2b41357^ --exec "git commit --amend --signoff --no-edit"
```

**Option 2: filter-branch for range**

```bash
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --msg-filter \
  'cat && if ! grep -q "Signed-off-by:"; then echo ""; echo "Signed-off-by: nanxing <1014662416@qq.com>"; fi' \
  c2b41357..HEAD
```

**Option 3: Amend single commit**

```bash
git commit --amend --signoff --no-edit
```

### After Fixing

```bash
# Force push to update PR
git push fork HEAD:<branch> --force
```

### Common Mistakes

1. **Merge commits need Signed-off-by too**: `git merge main` creates merge commit without sign-off
   - Use `git merge --signoff main` instead
   - Or rebase instead of merge

2. **Duplicate Signed-off-by**: If commit already has sign-off, don't add another
   - Check with `git log -1 --format='%B' | grep Signed-off-by`

3. **Wrong email**: Must match git config `user.email`
   - Check: `git config user.email`

### Verification

```bash
# Check all commits have Signed-off-by
git log --format='%h %s%n%b' <base>..HEAD | grep -B1 "Signed-off-by"

# Or check specific commits
for sha in $(git log --format='%h' <base>..HEAD); do
  if ! git log -1 --format='%B' $sha | grep -q "Signed-off-by"; then
    echo "Missing: $sha"
  fi
done
```

### ruff Format Fix

pre-commit CI also failed due to formatting issues:

```bash
# Check what needs formatting
ruff format --check tests/ut/test_platform.py

# Fix formatting
ruff format tests/ut/test_platform.py

# Commit with sign-off
git add tests/ut/test_platform.py
git commit --signoff -m "[BugFix] Fix ruff format issues in test_platform.py"
```

Common ruff format issues:
- Trailing whitespace in docstrings
- Function call argument formatting (long lines)
- E501 line too long - split strings or use parentheses

