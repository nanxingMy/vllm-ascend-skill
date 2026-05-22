# PR Learning Workflow for vLLM-Ascend

> Systematic approach to learn from all historical merged PRs and continuously learn from new PRs

## Overview

This workflow enables the digital employee to:
1. Learn from all historical merged PRs in batches
2. Extract solutions, patterns, and best practices
3. Set up continuous learning for new PRs
4. Accumulate knowledge to vllm-ascend-skill repository

## Workflow Steps

### 1. Initial Setup

**Create learning script**:
```python
# scripts/learn_all_prs.py
# - Fetches merged PRs from GitHub API
# - Analyzes each PR's solution
# - Categorizes by type (Feature, Bug Fix, Documentation, etc.)
# - Saves to JSON and Markdown
```

**Create daily learning script**:
```python
# scripts/learn_daily_prs.py
# - Fetches today's merged PRs
# - Analyzes and extracts lessons
# - Appends to existing knowledge base
```

### 2. Batch Learning Process

**Strategy**: Learn PRs in batches of 50

**Why batch learning**:
- Avoids timeout issues
- Allows incremental progress
- Can resume if interrupted
- Network failures don't lose progress

**Execution**:
```bash
cd /c/Users/HuaWei/vllm-ascend-skill
python scripts/learn_all_prs.py  # Learns 50 PRs per run
```

**Progress tracking**:
- Script tracks already-learned PRs by reading existing JSON
- Skips duplicates on re-run (checks PR number)
- Saves progress after each batch
- Appends to existing data file

**Resuming after failure**:
```bash
# Just re-run - it automatically skips learned PRs
python scripts/learn_all_prs.py
```

### 3. PR Analysis

For each PR, extract:
- **Issue information**: Problem description (if linked)
- **Solution approach**: How the problem was solved
- **Modified files**: What code changed (+lines, -lines)
- **Code patterns**: Key implementation patterns
- **Categories**: Feature, Bug Fix, Documentation, Refactor, Test, Performance, Other

**Categorization logic**:
```python
def categorize_pr(title, files):
    categories = []
    title_lower = title.lower()
    
    # By title keywords
    if 'bugfix' in title_lower or 'fix' in title_lower:
        categories.append('Bug Fix')
    if 'feature' in title_lower or 'feat' in title_lower:
        categories.append('Feature')
    if 'doc' in title_lower:
        categories.append('Documentation')
    if 'refactor' in title_lower:
        categories.append('Refactor')
    if 'test' in title_lower or 'ut' in title_lower:
        categories.append('Test')
    if 'perf' in title_lower or 'performance' in title_lower:
        categories.append('Performance')
    
    return categories if categories else ['Other']
```

### 4. Knowledge Accumulation

**Output files**:
```
skill/references/learned-from-prs/
├── summary-{date}.md          # Human-readable summary
└── prs-data-{date}.json       # Machine-readable data
```

**JSON structure**:
```json
{
  "pr_number": 9149,
  "title": "[BugFix] Add mutual exclusion check",
  "author": "nanxingMy",
  "merged_at": "2026-05-22T10:00:00Z",
  "issue_number": 8975,
  "files_changed": 3,
  "additions": 42,
  "deletions": 8,
  "categories": ["Bug Fix"],
  "key_patterns": ["mutual exclusion", "scheduler check"]
}
```

**Commit and push**:
```bash
git add skill/references/learned-from-prs/
git commit -m "[Learn] Learn from all merged PRs - {date}"
git push origin main
```

### 5. Continuous Learning Setup

**Create cron job** for daily learning:
```yaml
name: learn-daily-merged-prs
schedule: "0 0 * * *"  # Daily at midnight
script: scripts/learn_daily_prs.py
```

**What it does**:
- Runs every day at midnight
- Fetches PRs merged in the last 24 hours
- Analyzes and extracts lessons
- Appends to knowledge base
- Commits and pushes automatically

## Progress Estimation

**vLLM-Ascend statistics**:
- Total merged PRs: ~3000+
- Learning rate: 50 PRs per batch
- Estimated batches: ~60
- Time per batch: ~5-10 minutes

**Current progress** (as of 2026-05-22):
- Learned: **1370 PRs (46%)**
- Remaining: ~1630 PRs (54%)
- Batches completed: 28

## Learning Categories

| Category | Description | Learned Count |
|----------|-------------|---------------|
| Feature | New functionality | ~370 |
| Bug Fix | Issue resolution | ~410 |
| Documentation | Docs improvement | ~150 |
| Refactor | Code cleanup | ~100 |
| Test | Testing improvements | ~90 |
| Performance | Optimization | ~65 |
| Other | Miscellaneous | ~50 |

## Benefits

1. **Pattern Recognition**: Learn common solution patterns
2. **Best Practices**: Understand coding standards
3. **Problem Solving**: See how others solve similar issues
4. **Architecture Understanding**: Deep project knowledge
5. **Efficiency**: Faster issue resolution over time
6. **Skill Precipitation**: Knowledge becomes reusable skills

## Cron Jobs Created

| Job Name | Schedule | Purpose |
|----------|----------|---------|
| update-memory-to-vllm-ascend-skill | Daily 00:00 | Update memory to repo |
| deep-learn-vllm-ascend | Daily 00:00 | Deep project learning |
| module-learn-vllm-ascend | Daily 00:00 | Module-based learning |
| learn-daily-merged-prs | Daily 00:00 | Learn new merged PRs |

## Troubleshooting

### Network Failures

**Problem**: Git push fails with network error (Connection reset, SSL EOF)

**Solution**:
1. Learning continues locally - commits are saved
2. Script exits with error but progress is preserved
3. Retry push later:
   ```bash
   cd /c/Users/HuaWei/vllm-ascend-skill
   git push origin main
   ```
4. Or wait for next batch - it will commit again

### Script Timeout

**Problem**: Script times out during learning

**Solution**:
1. Script saves progress after each PR
2. Re-run script - it skips already-learned PRs
3. Continue until all PRs learned:
   ```bash
   python scripts/learn_all_prs.py  # Resume from where it stopped
   ```

### GitHub API Rate Limit

**Problem**: API returns 403 rate limit error

**Solution**:
1. Wait 1 hour for limit reset
2. Or use authenticated requests with token in headers

### SSL Errors

**Problem**: `SSLError: EOF occurred in violation of protocol`

**Solution**:
1. Transient network issue - retry
2. Script handles gracefully, continues with next PR
3. Failed PRs can be learned in next run

## Key Techniques Discovered

### 1. Skip Already-Learned PRs

```python
# Read existing data to get learned PR numbers
existing_prs = []
if data_file.exists():
    with open(data_file, 'r') as f:
        data = json.load(f)
        existing_prs = [pr['number'] for pr in data]

# Skip if already learned
if pr_number in existing_prs:
    print(f"已学习 {pr_number} 个 PR，将跳过")
    continue
```

### 2. Append to Existing Data

```python
# Read existing data
existing_prs = []
if data_file.exists():
    with open(data_file, 'r') as f:
        existing_prs = json.load(f)

# Append new PRs
existing_prs.extend(new_prs)

# Write back
with open(data_file, 'w') as f:
    json.dump(existing_prs, f, indent=2)
```

### 3. Continue Despite Failures

```python
for pr in prs:
    try:
        learn_pr(pr)
    except Exception as e:
        print(f"❌ 学习失败: {e}")
        continue  # Keep learning other PRs
```

## Related Files

- `scripts/learn_all_prs.py` - Batch learning script
- `scripts/learn_daily_prs.py` - Daily learning script
- `skill/references/learned-from-prs/` - Knowledge output directory
- `skill/references/LEARNING.md` - Module learning overview
