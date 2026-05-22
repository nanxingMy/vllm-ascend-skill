# PR Monitoring Workflow

Automated PR monitoring and feedback handling for vLLM-Ascend.

## Overview

This workflow monitors PR CI status, detects failures, and automatically handles feedback from automated code review bots (e.g., Gemini Code Assist).

## Components

1. **Cron Job**: `vllm-ascend-pr-monitor` (every 5 minutes)
2. **Skill**: `pr-feedback-handler` (on-demand)
3. **Output**: Results delivered to current conversation

## Setup

### Create Cron Job

```bash
# Create cron job for PR monitoring
hermes cron create \
  --name "vllm-ascend-pr-monitor" \
  --schedule "every 5m" \
  --deliver "origin" \
  --prompt "Check PR #XXXX status and report CI results"
```

### Manual Trigger

```bash
# Run monitoring immediately
hermes cron run vllm-ascend-pr-monitor
```

## Monitoring Checklist

### 1. Check PR Status

```bash
# Get PR head SHA
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/pulls/XXXX" | \
  python -c "import sys, json; print(json.load(sys.stdin)['head']['sha'])"

# Check CI status
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/commits/<SHA>/check-runs" | \
  python -c "
import sys, json
d = json.load(sys.stdin)
runs = d.get('check_runs', [])
completed = [r for r in runs if r.get('status') == 'completed']
in_progress = [r for r in runs if r.get('status') == 'in_progress']
success = [r for r in completed if r.get('conclusion') == 'success']
failure = [r for r in completed if r.get('conclusion') == 'failure']

print(f'运行中: {len(in_progress)} | 成功: {len(success)} | 失败: {len(failure)}')

if failure:
    print('\n失败的任务:')
    for r in failure:
        print(f'  - {r.get(\"name\")}')
        print(f'    URL: {r.get(\"html_url\")}')
"
```

### 2. Analyze Failures

#### Network Failures

**Symptoms**:
- `pip._vendor.urllib3.exceptions.ProtocolError: ('Connection broken: IncompleteRead(...)'`
- `failed to run script step: command terminated with non-zero exit code`

**Cause**: CI environment network instability, not code issue

**Solution**: Re-run CI or create empty commit to trigger new run

#### Code Failures

**Symptoms**:
- Syntax errors
- Import errors
- Test failures

**Action**: Analyze error, fix code, push new commit

### 3. Handle Bot Feedback

#### Gemini Code Assist

**Workflow**:
1. PR created → Gemini posts feedback within minutes
2. Fetch feedback via GitHub API
3. Review suggestions carefully (usually correct)
4. Apply improvements in new commit
5. Push → CI re-runs automatically

**Fetching Feedback**:

```bash
# Get PR comments
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/issues/XXXX/comments" | \
  python -c "
import sys, json
comments = json.load(sys.stdin)
for c in comments:
    if 'gemini' in c.get('user', {}).get('login', '').lower():
        print(c.get('body'))
"

# Get review comments (inline)
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/pulls/XXXX/comments" | \
  python -c "
import sys, json
comments = json.load(sys.stdin)
for c in comments:
    if 'gemini' in c.get('user', {}).get('login', '').lower():
        print(f'File: {c.get(\"path\")}, Line: {c.get(\"line\")}')
        print(c.get('body'))
"
```

Common feedback patterns:

1. **Redundant/unreachable code**
   - Move code to correct position
   - Or remove if truly redundant
   - Example: PR #9149 - check was unreachable, moved before existing checks

2. **PR title/summary format**
   - Title: `[Type][Module] Description`
   - Summary must include: What/Why, User-facing change, How tested

3. **Suggested code changes**
   - Review carefully - bot suggestions are usually correct
   - Example: PR #9199 - suggested using `Version.public` property

4. **Better patterns/APIs**
   - Bot may suggest more robust or idiomatic approaches
   - Example: Use `.public` property instead of manual string manipulation

**Important**: Don't ignore Gemini feedback - it catches issues humans miss.

## Workflow

```
1. Cron job triggers every 5 minutes
   ↓
2. Check PR CI status
   ↓
3. If failures detected:
   ├─ Network failure → Re-run CI
   └─ Code failure → Analyze & fix
   ↓
4. Check for bot comments
   ↓
5. If bot feedback:
   └─ Apply fixes & push
   ↓
6. Report status to conversation
```

## Example Output

```
======================================================================
PR #9149 CI 监控报告 - 2026-05-15 10:43:28
======================================================================
总计: 30 个任务
运行中: 2 | 排队: 0 | 成功: 7 | 失败: 0 | 跳过: 21
======================================================================

⏳ 运行中的任务:
  - smart test (v0.20.2) / smart-ut (cpu x0)
  - smart test (ce29c26b...) / smart-ut (cpu x0)

⏳ 等待 2 个任务完成...
```

## Tips

1. **Distinguish network vs code failures**: Network failures are transient, code failures need fixes
2. **Check all failed jobs**: Sometimes multiple jobs fail for the same root cause
3. **Read bot feedback carefully**: Automated reviewers often identify root cause
4. **Keep monitoring**: Don't stop after first fix, continue until all checks pass

## Related

- [pr-9149-lessons-learned.md](pr-9149-lessons-learned.md) - PR #9149 experience: code review feedback handling
- [pr-9149-network-failure.md](pr-9149-network-failure.md) - PR #9149 CI network failure case study
