# PR Creation Best Practices for vLLM-Ascend

## Minimal Changes Principle

**CRITICAL**: Always keep PR changes minimal. Only modify what's necessary for the fix.

### Common Pitfalls

1. **Working on wrong branch**: If you work on a branch that contains previous PR commits, your new PR will include all those changes.
   - ❌ Bad: Creating PR from `bugfix/previous-issue` branch
   - ✅ Good: Creating clean branch from `main`

2. **Format changes**: Line ending changes (CRLF ↔ LF), whitespace, or formatting changes can inflate diff size.
   - ❌ Bad: 400+ insertions, 400- deletions for a 40-line fix
   - ✅ Good: 43 insertions, 0 deletions

3. **Using write_file on existing files**: This can change line endings and formatting.
   - ❌ Bad: `write_file` to overwrite entire file
   - ✅ Good: Use `patch` or `terminal` with `cat >>` to append

### Verification Steps

Before committing, ALWAYS verify:

```bash
git diff --stat
```

Expected output for a minimal fix:
```
 tests/ut/test_utils.py | 38 +++++++++++++++++++++++++
 vllm_ascend/utils.py   |  5 +++++
 2 files changed, 43 insertions(+)
```

If you see large numbers like:
```
 tests/ut/test_utils.py | 802 ++++++++++++++++++++++++-------------------------
 1 file changed, 401 insertions(+), 401 deletions(-)
```

**STOP!** This indicates format changes. Reset and redo.

### Correct Workflow

1. **Create clean branch**:
   ```bash
   git checkout -b bugfix/new-issue main
   # or
   git checkout -b bugfix/new-issue fork/main
   ```

2. **Apply only your fix**:
   - Use `patch` for targeted changes
   - Use `cat >>` to append to files (preserves formatting)
   - Avoid `write_file` on existing files

3. **Verify changes**:
   ```bash
   git diff --stat
   ```

4. **Commit with proper message**:
   ```bash
   git commit -s -m "[BugFix] Brief description
   
   What this PR does / why we need it:
   ...
   
   Fixes #XXXX
   "
   ```

5. **Push to new branch**:
   ```bash
   git push fork HEAD:bugfix/new-issue
   ```

### Examples

**Good PR #9199**:
- Files: 2
- Additions: 43
- Deletions: 0
- Clean, focused fix

**Bad PR (avoid)**:
- Files: 36
- Additions: 1800+
- Deletions: 0
- Mixed multiple PRs or format changes

## Handling Line Endings

Windows uses CRLF, Linux uses LF. Git can auto-convert.

To preserve original line endings:
- Use `cat >> file` to append (preserves existing format)
- Use `patch` (preserves existing format)
- Avoid `write_file` on existing files

To fix line ending issues:
```bash
# Reset the file
git checkout HEAD -- path/to/file

# Re-apply changes correctly
cat >> path/to/file << 'EOF'
your content
EOF
```

## Test Requirement

**CRITICAL USER PREFERENCE**: Always add unit tests for new features or bug fixes. This is not optional.

When user asks "为什么没有增加用例" (why didn't you add test cases), this means you forgot tests. Always include:
- Unit tests for new functions/methods
- Regression tests for bug fixes
- Integration tests for new APIs

**Test file locations**:
- Unit tests: `tests/ut/` or `tests/unit/`
- Integration tests: `tests/it/` or `tests/integration/`
- E2E tests: `tests/e2e/`

## Code Style Matching

**USER PREFERENCE**: Before adding new code, always match the existing style in the file.

When user says "你先看看platform.py 接口的定义风格，最好和他们写的风格相似" (look at the style first, match it), this means:
1. Read existing code to understand patterns
2. Match type annotations (if file uses them, add them; if not, don't)
3. Match docstring format (Google-style, NumPy-style, or none)
4. Match import style (top-level vs inside functions)
5. Don't introduce style inconsistencies

**Example workflow**:
```bash
# 1. Read similar methods in the file
# 2. Note: Do they have type hints? Docstrings?
# 3. Match exactly - consistency over perfection
```

## Gemini Code Assist Feedback Handling

vLLM-Ascend uses Gemini Code Assist for automated PR reviews. Here's how to handle feedback:

### Fetching Feedback

```bash
# Get PR comments
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/issues/PR_NUMBER/comments"

# Get review comments
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/pulls/PR_NUMBER/reviews"

# Get inline comments
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/pulls/PR_NUMBER/comments"
```

### Common Feedback Patterns

1. **Code suggestions**: Gemini provides specific code snippets
   - Review carefully
   - Apply if correct
   - Example: PR #9199 - suggested using `Version.public` property

2. **PR title format**: Suggests proper format
   - Title: `[Type][Module] Description`
   - Example: `[Ops][BugFix] Strip version suffix...`

3. **Unreachable code**: Detects when code can't be reached
   - Move to correct position
   - Example: PR #9149 - check moved before existing validation

### Workflow

1. Fetch feedback using GitHub API
2. Parse Gemini's suggestions
3. Apply improvements if valid
4. Push new commit
5. Monitor CI for new run

### Example: PR #9199

**Feedback**: Use `Version.public` property instead of manual suffix stripping

**Before**:
```python
vllm_version = vllm_version.split('+')[0]
return Version(vllm_version) == Version(target_vllm_version)
```

**After**:
```python
return Version(vllm_version).public == Version(target_vllm_version).public
```

**Result**: More robust, handles suffixes on both sides

### Example: PR #9205

**Feedback**: Use `ValueError` instead of `assert` for input validation

**Gemini's reasoning**: 
- `assert` statements can be disabled with Python's `-O` optimization flag
- Production code should use explicit exceptions
- Cache `get_supported_vit_attn_backends()` result to avoid redundant list creation

**Before**:
```python
if backend is not None:
    assert backend in cls.get_supported_vit_attn_backends(), (
        f"Backend {backend} is not supported for vit attention. "
        f"Supported backends are: {cls.get_supported_vit_attn_backends()}"
    )
```

**After**:
```python
if backend is not None:
    supported_backends = cls.get_supported_vit_attn_backends()
    if backend not in supported_backends:
        raise ValueError(
            f"Backend {backend} is not supported for vit attention. "
            f"Supported backends are: {supported_backends}"
        )
```

**Test update**:
```python
# Changed from AssertionError to ValueError
with self.assertRaises(ValueError) as context:
    NPUPlatform.get_vit_attn_backend(
        head_size=64,
        dtype=torch.float16,
        backend=AttentionBackendEnum.FLASH_ATTN,
    )
```

**Workflow**:
1. Fetched Gemini feedback via GitHub API
2. Identified 3 issues: PR title format, assert→ValueError, test update
3. Applied all fixes in new commit
4. Pushed → CI re-ran automatically
5. All checks passed

**Key learning**: Gemini catches issues humans miss - always review and apply valid suggestions

## CI Monitoring

### Polling Pattern

```bash
for i in {1..30}; do
  result=$(curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/commits/SHA/check-runs" | python -c "
import sys, json
d = json.load(sys.stdin)
runs = d.get('check_runs', [])

completed = [r for r in runs if r.get('status') == 'completed']
in_progress = [r for r in runs if r.get('status') == 'in_progress']
queued = [r for r in runs if r.get('status') == 'queued']

success = [r for r in completed if r.get('conclusion') == 'success']
failure = [r for r in completed if r.get('conclusion') == 'failure']

if failure:
    print('❌ Failed')
    sys.exit(1)
elif len(in_progress) == 0 and len(queued) == 0 and len(success) > 0:
    print('✅ All checks passed')
    sys.exit(0)
else:
    print(f'⏳ {len(in_progress)} running, {len(queued)} queued')
    sys.exit(2)
")
  
  if [ $? -eq 0 ]; then
    echo "CI passed!"
    exit 0
  elif [ $? -eq 1 ]; then
    echo "CI failed!"
    exit 1
  fi
  
  sleep 60
done
```

### Status Interpretation

- `status: queued` - Waiting to run
- `status: in_progress` - Currently running
- `status: completed` + `conclusion: success` - Passed
- `status: completed` + `conclusion: failure` - Failed
- `status: completed` + `conclusion: skipped` - Skipped (not counted)

## Network Failure Handling

**CRITICAL**: Many CI failures are network/infrastructure issues, NOT code problems.

### Symptoms of Network Failure

```
pip._vendor.urllib3.exceptions.ProtocolError: ('Connection broken: IncompleteRead(...)')
Failed to connect to github.com port 443 after 21078 ms: Could not connect to server
Connection was reset
```

### Diagnosis

1. **Check step name**: "Install", "Setup", "Checkout" = infrastructure
2. **Check error content**: "Connection", "timeout", "IncompleteRead", "ProtocolError" = network
3. **Check multiple jobs**: All failing at same step = infrastructure issue

### Solution

1. This is NOT a code problem - do NOT modify code
2. Retry CI:
   - Click "Re-run all jobs" on GitHub PR page
   - Or create empty commit: `git commit --allow-empty -m "Retry CI"`
3. Wait for new CI run

### Example: PR #9149

First CI run failed with:
```
pip._vendor.urllib3.exceptions.ProtocolError: ('Connection broken: IncompleteRead(35766015 bytes read, 152685937 more expected)')
```

**Diagnosis**: Network timeout downloading mypy package (downloaded 35.7MB of 152.7MB)

**Solution**: Retried CI - second run passed

**Key learning**: Don't waste time debugging code when CI fails during package installation

## Complete PR Workflow

### Step-by-Step

1. **Analyze Issue**
   ```bash
   curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/issues/NUMBER"
   ```

2. **Create Clean Branch**
   ```bash
   git fetch origin
   git checkout -b fix-issue-NUMBER origin/main
   ```

3. **Implement Fix**
   - Modify only necessary files
   - Preserve file formatting (use `patch` or `cat >>`)
   - Add unit tests

4. **Verify Minimal Changes**
   ```bash
   git diff --stat
   # Should match expected: e.g., 2 files, +43 lines
   ```

5. **Commit**
   ```bash
   git add specific_files_only
   git commit -s -m "[BugFix] Description
   
   What this PR does / why we need it:
   [Explain problem and solution]
   
   Fixes #NUMBER
   
   Signed-off-by: Name <email>"
   ```

6. **Push**
   ```bash
   git push fork HEAD:fix-issue-NUMBER
   ```

7. **Create PR** (via GitHub web UI or API)

8. **Monitor CI**
   - Poll every 60-90 seconds
   - Detect network failures (retry, don't fix code)
   - Wait for all checks to pass

9. **Handle Gemini Feedback**
   - Fetch bot comments via API
   - Review suggestions
   - Apply if valid
   - Push new commit
   - CI re-runs automatically

10. **Wait for Merge**
    - All CI checks passed
    - DCO check passed
    - Ready for maintainer review

## Common Mistakes to Avoid

1. ❌ Modifying files for formatting reasons
2. ❌ Creating branch from another branch (includes all history)
3. ❌ Using `write_file` to completely overwrite (changes line endings)
4. ❌ Ignoring Gemini Code Assist feedback
5. ❌ Treating network failures as code problems
6. ❌ Not verifying `git diff --stat` before committing
7. ❌ Reusing branch names for different PRs
8. ❌ Including unrelated changes in PR

## Success Checklist

### Before Pushing
- [ ] Changes are minimal (only what's necessary)
- [ ] `git diff --stat` shows expected numbers
- [ ] File formatting preserved (no massive line changes)
- [ ] Unit tests added
- [ ] Commit message has Signed-off-by
- [ ] Branch created from main (not another branch)

### After Pushing
- [ ] PR created with correct title format `[Type][Module] Description`
- [ ] PR description follows template
- [ ] CI monitoring started
- [ ] Gemini feedback reviewed and incorporated
- [ ] All CI checks passed

## Summary

1. **Always create clean branch from main** - avoid mixing PRs
2. **Verify diff size** - should match expected changes
3. **Preserve file formatting** - use `patch` or `cat >>`
4. **Handle Gemini feedback** - apply valid suggestions
5. **Monitor CI** - poll until all checks complete
6. **Network failures are NOT code problems** - retry CI, don't modify code
