# CI Failure Diagnosis Guide

## Distinguishing Code Problems from Infrastructure Problems

When CI fails, it's critical to quickly determine whether the failure is due to:
1. **Code problem** - Your changes introduced a bug
2. **Infrastructure problem** - CI environment issue (network, dependencies, resources)

## Common Infrastructure Failures

### 1. Network Connection Errors

**Symptoms:**
```
pip._vendor.urllib3.exceptions.ProtocolError: ('Connection broken: IncompleteRead(X bytes read, Y more expected)')
```

**Diagnosis:**
- Check if error occurs during package download (pip, npm, etc.)
- Look for "Connection broken", "IncompleteRead", "timeout"
- Check if multiple jobs fail at the same step

**Solution:**
- This is NOT a code problem
- Retry CI: Click "Re-run all jobs" on GitHub
- Or create empty commit: `git commit --allow-empty -m "[CI] Retry"`

### 2. Dependency Installation Failures

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement X
ModuleNotFoundError: No module named 'X'
```

**Diagnosis:**
- Check if error is in "Install dependencies" step
- Check if package exists in PyPI
- Check version constraints

**Solution:**
- If package missing: Add to requirements.txt
- If version conflict: Pin specific version
- If transient: Retry CI

### 3. Resource Exhaustion

**Symptoms:**
```
OOMKilled
Cannot allocate memory
No space left on device
```

**Diagnosis:**
- Check if error is "Out of memory" or "disk full"
- Check if running on resource-limited runner

**Solution:**
- Reduce test parallelism
- Clean up temporary files
- Request larger runner

## Code Problem Indicators

### 1. Test Failures

**Symptoms:**
```
AssertionError
pytest failed
Test case X failed
```

**Diagnosis:**
- Error is in your test code or production code
- Stack trace points to your files

**Solution:**
- Fix the code
- Add missing test cases

### 2. Compilation Errors

**Symptoms:**
```
SyntaxError
ImportError
TypeError
```

**Diagnosis:**
- Error is in Python/C++ code
- Clear indication of what's wrong

**Solution:**
- Fix syntax error
- Fix import path
- Fix type mismatch

### 3. Lint Failures

**Symptoms:**
```
ruff check failed
E501 line too long
F401 unused import
```

**Diagnosis:**
- Code style issue

**Solution:**
```bash
ruff format .
ruff check --fix .
```

## Decision Tree

```
CI Failed
    │
    ├─ Error during "Install" step?
    │   └─ YES → Likely infrastructure issue → Retry CI
    │
    ├─ Error message contains "Connection", "timeout", "network"?
    │   └─ YES → Network issue → Retry CI
    │
    ├─ Error message contains "OOM", "memory", "disk"?
    │   └─ YES → Resource issue → Reduce load or request larger runner
    │
    ├─ Error in your test files?
    │   └─ YES → Code problem → Fix tests
    │
    └─ Error in production code?
        └─ YES → Code problem → Fix code
```

## Example: PR #9149 Network Failure

**Error:**
```
pip._vendor.urllib3.exceptions.ProtocolError: ('Connection broken: IncompleteRead(35766015 bytes read, 152685937 more expected)')
```

**Analysis:**
- Occurred during "Install vllm-project/vllm-ascend" step
- Downloading mypy package
- Connection interrupted after 35.7 MB of 152.7 MB
- Multiple jobs failed at same step

**Conclusion:** Network infrastructure issue, NOT code problem

**Action:** Retry CI (network issue resolved on retry)

## Monitoring CI Status

### Automated Monitoring

Set up cron job to check PR status every 5 minutes:

```bash
# Create cron job
hermes cron create \
  --name "pr-monitor" \
  --schedule "every 5m" \
  --deliver origin \
  --prompt "Check PR #XXX status and report"
```

### Manual Check

```bash
# Get PR head SHA
curl -s "https://api.github.com/repos/OWNER/REPO/pulls/PR_NUMBER" | \
  python -c "import sys, json; print(json.load(sys.stdin)['head']['sha'])"

# Check CI status
curl -s "https://api.github.com/repos/OWNER/REPO/commits/SHA/check-runs" | \
  python -c "
import sys, json
d = json.load(sys.stdin)
runs = d.get('check_runs', [])
for r in runs:
    name = r.get('name')
    status = r.get('status')
    conclusion = r.get('conclusion')
    print(f'{name}: {status} / {conclusion}')
"
```

## Best Practices

1. **Always check the error message first** - Most errors clearly indicate whether they're code or infrastructure
2. **Look at the step name** - "Install", "Setup", "Checkout" steps are infrastructure
3. **Check multiple jobs** - If all jobs fail at same step, likely infrastructure
4. **Don't assume code is wrong** - Many CI failures are transient
5. **Retry before debugging** - If unsure, retry once before deep investigation
