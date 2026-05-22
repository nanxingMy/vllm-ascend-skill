# vLLM-Ascend Contribution Patterns

Session-specific patterns and techniques learned while contributing to vLLM-Ascend project.

## PR Workflow Patterns

### Creating Clean Branches

**Problem**: Creating a branch from another feature branch instead of main pollutes the PR with unrelated commits.

**Solution**:
```bash
# Always start from main
git checkout main && git pull origin main
git checkout -b feature/my-feature

# If you already made the mistake, recover with:
git diff main > /tmp/feature.patch
git checkout main && git pull origin main
git checkout -b feature/my-feature-clean
git apply /tmp/feature.patch
git add . && git commit -m "..."
git push origin feature/my-feature --force
```

### Handling Version Comparison

**Issue**: Version strings with build metadata (e.g., `"0.20.1+cpu"`) fail strict comparison.

**Wrong**:
```python
from packaging.version import Version
Version("0.20.1") == Version("0.20.1+cpu")  # False!
```

**Correct**:
```python
from packaging.version import Version
Version("0.20.1+cpu").public == Version("0.20.1").public  # True
```

The `.public` attribute strips local version identifiers (the `+cpu` part) while preserving pre-release segments.

### Adding Platform Interfaces

When adding new methods to platform classes (e.g., `NPUPlatform`):

1. **Check vLLM base class first**:
   ```bash
   curl -s "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/platforms/interface.py" | grep -A 20 "def method_name"
   ```

2. **Match existing style**:
   - Read surrounding methods in the file
   - Copy the style exactly (type hints, docstrings, imports)
   - Don't introduce inconsistencies

3. **Add comprehensive tests**:
   - Test default behavior
   - Test valid inputs
   - Test invalid inputs (expect ValueError, not AssertionError)
   - Test edge cases

### Common Gemini Code Assist Feedback

1. **Use ValueError, not assert**:
   ```python
   # ❌ Bad
   assert condition, "message"
   
   # ✅ Good
   if not condition:
       raise ValueError("message")
   ```

2. **Cache repeated calls**:
   ```python
   # ❌ Bad
   if x in get_list():
       use(get_list())
   
   # ✅ Good
   items = get_list()
   if x in items:
       use(items)
   ```

3. **PR title format**: `[Module][Type] Description`
   - Module: `Ops`, `Attention`, `CI`, `Doc`, etc.
   - Type: `Feature`, `BugFix`, `Refactor`, etc.

4. **Avoid redundant synchronization calls**:
   ```python
   # ❌ Bad - calls synchronize multiple times
   if hasattr(self, "kv_caches") and self.kv_caches:
       torch.npu.synchronize()
       # ... cleanup kv_caches
   
   if hasattr(self, "cross_layers_kv_cache"):
       torch.npu.synchronize()  # Redundant!
       # ... cleanup cross_layers_kv_cache
   
   # ✅ Good - synchronize once at start
   torch.npu.synchronize()
   
   if hasattr(self, "kv_caches") and self.kv_caches:
       # ... cleanup kv_caches
   
   if hasattr(self, "cross_layers_kv_cache") and self.cross_layers_kv_cache:
       # ... cleanup cross_layers_kv_cache
   ```

5. **Check attributes are truthy, not just hasattr**:
   ```python
   # ❌ Bad - may iterate over None
   if hasattr(self, "cross_layers_kv_cache"):
       for item in self.cross_layers_kv_cache:  # TypeError if None!
           ...
   
   # ✅ Good - check truthiness
   if hasattr(self, "cross_layers_kv_cache") and self.cross_layers_kv_cache:
       for item in self.cross_layers_kv_cache:
           ...
   ```

6. **Guard against AttributeError for optional attributes**:
   ```python
   # ❌ Bad - may raise AttributeError
   self.compilation_config.static_forward_context.clear()
   
   # ✅ Good - check existence first
   if hasattr(self, "compilation_config") and self.compilation_config:
       self.compilation_config.static_forward_context.clear()
   ```

### Fixing Pre-commit Failures

**Ruff format failure**:
```bash
python -m ruff format <files>
git add . && git commit -m "style: fix ruff formatting" && git push
```

**Ruff check failure**:
```bash
python -m ruff check <files> --fix
git add . && git commit -m "style: fix lint issues" && git push
```

## Monitoring Multiple PRs

When monitoring multiple PRs simultaneously:

```bash
for pr_num in 9149 9199 9205; do
  # Get PR info
  curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/pulls/$pr_num" | python -c "
import sys, json
pr = json.load(sys.stdin)
print(f'PR #{pr[\"number\"]}: {pr[\"title\"][:50]}')
print(f'  State: {pr[\"state\"]}, Mergeable: {pr[\"mergeable_state\"]}')
"
  
  # Get CI status
  sha=$(curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/pulls/$pr_num" | python -c "import sys, json; print(json.load(sys.stdin)['head']['sha'])")
  
  curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/commits/$sha/check-runs" | python -c "
import sys, json
runs = json.load(sys.stdin).get('check_runs', [])
failed = [r for r in runs if r.get('conclusion') == 'failure']
print(f'  CI: {len(runs)} checks, {len(failed)} failed')
"
done
```

## Key Learnings

1. **Always branch from main** - prevents PR pollution (see detailed recovery steps above)
2. **Always add tests** - PRs without tests will be rejected. User signal: "为什么没有增加用例"
3. **Match existing style** - consistency over perfection. User signal: "你先看看platform.py 接口的定义风格"
4. **Use ValueError not assert** - production-safe validation (assertions can be disabled with `-O`)
5. **Run ruff format before committing** - prevents CI failures
6. **Monitor and iterate** - fix CI issues immediately
7. **Verify diff stats** - Use `git diff --stat` to ensure changes match expectations. Example: 38-line addition should show +38, not +400 -400
8. **Check dependent classes have required methods** - Before calling `model_runner.shutdown()`, verify `model_runner` actually has a `shutdown()` method. If not, implement it first.

## Implementing Worker/ModelRunner Methods

When adding new methods to worker or model runner classes:

### Pattern: Adding shutdown() method

1. **Implement in ModelRunner first** (worker depends on it):
   ```python
   def shutdown(self) -> None:
       """Release NPU resources."""
       # Synchronize once at start
       torch.npu.synchronize()
       
       # Clear caches (check truthiness)
       if hasattr(self, "kv_caches") and self.kv_caches:
           for i in range(len(self.kv_caches)):
               self.kv_caches[i] = None
           self.kv_caches.clear()
       
       # Clear optional attributes (check existence AND truthiness)
       if hasattr(self, "compilation_config") and self.compilation_config:
           self.compilation_config.static_forward_context.clear()
       
       # Reset model reference
       self.model = None
       
       # Reset workspace
       reset_workspace_manager()
   ```

2. **Then implement in Worker**:
   ```python
   def shutdown(self) -> None:
       """Shutdown worker and release resources."""
       if self.profiler is not None:
           self.profiler.shutdown()
       
       if model_runner := getattr(self, "model_runner", None):
           model_runner.shutdown()
   ```

3. **Add tests for all scenarios**:
   ```python
   def test_shutdown_with_profiler(self):
       """Test shutdown with profiler."""
       worker.profiler = MagicMock()
       worker.model_runner = MagicMock()
       worker.shutdown()
       worker.profiler.shutdown.assert_called_once()
       worker.model_runner.shutdown.assert_called_once()
   
   def test_shutdown_without_profiler(self):
       """Test shutdown without profiler."""
       worker.profiler = None
       worker.model_runner = MagicMock()
       worker.shutdown()
       worker.model_runner.shutdown.assert_called_once()
   
   def test_shutdown_without_model_runner(self):
       """Test shutdown when model_runner doesn't exist."""
       worker.profiler = MagicMock()
       # Don't set model_runner attribute
       worker.shutdown()  # Should not raise
       worker.profiler.shutdown.assert_called_once()
   ```

## Automated PR Monitoring Pattern

**User preference**: Automate PR monitoring, CI checking, and feedback handling.

### Complete PR Monitoring Script

```bash
# Monitor multiple PRs until all CI passes
monitor_prs() {
  local pr_numbers=("$@")
  local all_passed=false
  
  while [ "$all_passed" = false ]; do
    all_passed=true
    echo "=== Checking PR Status: $(date '+%H:%M:%S') ==="
    
    for pr_num in "${pr_numbers[@]}"; do
      # Get PR info
      pr_info=$(curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/pulls/$pr_num")
      sha=$(echo "$pr_info" | python -c "import sys, json; print(json.load(sys.stdin)['head']['sha'])")
      title=$(echo "$pr_info" | python -c "import sys, json; print(json.load(sys.stdin)['title'][:50])")
      
      # Check CI status
      ci_status=$(curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/commits/$sha/check-runs" | python -c "
import sys, json
runs = json.load(sys.stdin).get('check_runs', [])
total = len(runs)
success = sum(1 for r in runs if r.get('conclusion') == 'success')
failed = sum(1 for r in runs if r.get('conclusion') == 'failure')
running = sum(1 for r in runs if r.get('status') == 'in_progress')
print(f'{total}|{success}|{failed}|{running}')
")
      
      IFS='|' read -r total success failed running <<< "$ci_status"
      
      if [ "$failed" -gt 0 ]; then
        echo "❌ PR #$pr_num: $title"
        echo "   CI: $success/$total passed, $failed failed"
        all_passed=false
        # Auto-fix logic here
      elif [ "$running" -gt 0 ]; then
        echo "🔄 PR #$pr_num: $title"
        echo "   CI: $running checks running..."
        all_passed=false
      else
        echo "✅ PR #$pr_num: $title"
        echo "   CI: All $total checks passed"
      fi
    done
    
    if [ "$all_passed" = false ]; then
      sleep 30
    fi
  done
  
  echo "✅ All PRs CI passed!"
}

# Usage
monitor_prs 9149 9199 9205
```

### Using Cronjob Tool for Automated Monitoring

**User preference**: Automate PR monitoring with Hermes cronjob tool for hands-off feedback handling.

```bash
# Create a cron job to monitor PR every 5 minutes
cronjob \
  --action create \
  --name "pr-9216-monitor" \
  --prompt "监控 PR #9216 的评论区反馈，如果有新反馈则报告。

检查步骤：
1. 获取 PR #9216 的评论
2. 检查是否有新的 Gemini Code Assist 反馈
3. 如果有新反馈，报告反馈内容
4. 如果没有新反馈，报告'无新反馈'

PR URL: https://github.com/vllm-project/vllm-ascend/pull/9216" \
  --schedule "*/5 * * * *"
```

**Benefits**:
- Automatically checks PR every 5 minutes
- Reports new Gemini Code Assist feedback
- Can trigger automatic fixes based on feedback patterns
- Hands-off monitoring while you work on other tasks

**Workflow**:
1. Create PR and push code
2. Set up cronjob monitoring
3. When feedback arrives, apply fixes
4. Commit and push fixes
5. Cronjob continues monitoring until PR is merged

### Handling Gemini Code Assist Feedback Automatically

```bash
# Get latest Gemini feedback for a PR
get_gemini_feedback() {
  local pr_num=$1
  
  # Check for review comments
  curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/pulls/$pr_num/comments" | python -c "
import sys, json
comments = json.load(sys.stdin)

for c in comments:
    user = c.get('user', {}).get('login')
    if 'gemini' in user.lower():
        path = c.get('path')
        line = c.get('line')
        body = c.get('body', '')
        
        # Check for high priority
        if 'high' in body.lower() or '⚠️' in body or '❌' in body:
            print(f'HIGH PRIORITY: {path}:{line}')
            print(body[:300])
            print('---')
"
}

# Apply common fixes based on feedback patterns
apply_gemini_fixes() {
  # 1. Replace assert with ValueError
  # 2. Cache repeated function calls
  # 3. Fix PR title format
  # 4. Add missing tests
  # 5. Fix ruff formatting
  
  python -m ruff format .
  git add . && git commit -m "refactor: address Gemini Code Assist feedback" && git push
}
```
