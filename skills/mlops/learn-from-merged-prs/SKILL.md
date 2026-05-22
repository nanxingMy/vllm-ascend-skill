---
name: learn-from-merged-prs
description: Learn from merged PRs in a repository to accumulate patterns, best practices, and problem-solving techniques. Extracts Bug Fix, Feature, Performance, Refactor, and other patterns from PR history.
triggers:
  - Learn from all merged PRs
  - Accumulate knowledge from PR history
  - Extract patterns from PRs
  - Set up continuous PR learning
---

# Learn from Merged PRs

Learn from merged PRs in a repository to accumulate patterns, best practices, and problem-solving techniques.

## When to Use

- Learning from historical PRs in a repository
- Setting up continuous PR learning system
- Extracting patterns from PR history
- Building knowledge base from PR contributions

## Workflow

### 1. Setup Learning System

```bash
# Create learning directory
mkdir -p skill/references/learned-from-prs

# Create learning script
# See scripts/learn_all_prs.py
```

### 2. Learn from Merged PRs

**Strategy**: Learn PR by PR (not Issue by Issue)

**Reasoning**:
- PRs have explicit modifications
- Each PR represents a concrete solution
- Can directly extract patterns from code changes
- Simpler workflow

**Process**:
1. Get merged PRs from GitHub API
2. For each PR:
   - Extract title, author, merged date
   - Find corresponding Issue (if exists)
   - Analyze modified files
   - Categorize PR (Bug Fix, Feature, Performance, Refactor, Documentation, Test, Other)
   - Extract patterns and techniques
3. Save to knowledge base

### 3. PR Categorization

**Categories**:
- **Bug Fix**: Fixes errors, corrects behavior
- **Feature**: Adds new functionality
- **Performance**: Improves speed, memory, efficiency
- **Refactor**: Code restructuring without behavior change
- **Documentation**: Docs, comments, README
- **Test**: Adds or modifies tests
- **Other**: CI/CD, dependencies, misc

**Detection** (by title keywords):
```
Bug Fix: fix, bugfix, bug, error, issue, resolve, patch
Feature: feat, feature, add, support, implement, enable
Performance: perf, performance, optimize, speed, memory
Refactor: refactor, restructure, clean, simplify
Documentation: doc, docs, document, readme, comment
Test: test, tests, ut, e2e, nightly
```

### 4. Knowledge Extraction

For each PR, extract:
- **Problem**: What issue was being solved?
- **Solution**: What approach was taken?
- **Files Modified**: Which files were changed?
- **Code Patterns**: What coding patterns were used?
- **Best Practices**: What best practices can be learned?

### 5. Batch Learning

**Recommended**: Learn in batches of 50 PRs

**Reasoning**:
- Avoids API rate limits
- Allows incremental progress
- Can resume if interrupted
- Network issues don't lose progress

**Command**:
```python
python scripts/learn_all_prs.py  # Learns 50 PRs per run
```

### 6. Continuous Learning

**Setup Cron Job**:
```bash
# Create cron job for daily learning
hermes cronjob create \
  --name "learn-daily-merged-prs" \
  --schedule "0 0 * * *" \
  --script scripts/learn_daily_prs.py
```

**Daily Learning**:
- Runs at midnight
- Learns PRs merged that day
- Appends to existing knowledge base
- Commits and pushes automatically

### 7. Output Format

**Summary Document** (`summary-{date}.md`):
```markdown
# PR Learning Summary - {date}

## Statistics
- Total PRs learned: X
- Bug Fix: Y
- Feature: Z
- Performance: W
...

## Key Patterns
1. Pattern 1
2. Pattern 2
...
```

**Raw Data** (`prs-data-{date}.json`):
```json
{
  "date": "2026-05-22",
  "total_prs": 1919,
  "prs": [
    {
      "pr_number": 9381,
      "title": "...",
      "author": "...",
      "merged_at": "...",
      "issue_number": 9358,
      "files_modified": 1,
      "lines_added": 9,
      "lines_deleted": 4,
      "categories": ["Bug Fix", "Documentation"],
      "patterns": [...]
    }
  ]
}
```

## Pitfalls

### 1. API Rate Limits
- **Problem**: GitHub API has rate limits
- **Solution**: Learn in batches of 50, add delays between requests

### 2. Network Failures
- **Problem**: Network can fail during learning
- **Solution**: Save locally first, push when network available

### 3. Large PRs
- **Problem**: Some PRs modify many files
- **Solution**: Still learn from them, but note complexity

### 4. Skip Already Learned
- **Problem**: Don't re-learn same PRs
- **Solution**: Track learned PR numbers, skip if already in knowledge base

### 5. Category Ambiguity
- **Problem**: Some PRs fit multiple categories
- **Solution**: Allow multiple categories per PR

## User Preferences

- **Don't Stop**: Keep learning until all PRs are learned
- **Batch Size**: 50 PRs per batch
- **Push Frequency**: After each batch (when network available)
- **Resume**: Skip already-learned PRs

## Tools Used

- `requests`: GitHub API calls
- `json`: Data storage
- `subprocess`: Git operations
- `cronjob`: Scheduled learning

## Related Skills

- `github-pr-workflow`: PR lifecycle management
- `github-issues`: Issue management
- `hermes-agent`: Cron job setup

## References

- `scripts/learn_all_prs.py`: Main learning script
- `scripts/learn_daily_prs.py`: Daily learning script
- `references/learned-from-prs/`: Output directory
