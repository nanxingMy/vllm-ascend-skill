---
name: continuous-learning
description: Continuous learning mechanism for digital employees - automatically update memory and skills daily based on accumulated experience from fixing issues and implementing features.
version: 1.0.0
author: nanxing
tags:
  - learning
  - automation
  - memory
  - skills
  - cron
triggers:
  - "学习机制"
  - "持续学习"
  - "自动更新"
  - "每天更新"
  - "memory 更新"
---

# Continuous Learning Mechanism

Automatically update memory and skills daily based on accumulated experience.

## Overview

Through continuously fixing issues and implementing features, the digital employee learns and accumulates experience. Every day at midnight, memory is automatically updated to the vllm-ascend-skill repository, forming a learning loop.

## Learning Loop

```
Fix Issues/Features → Accumulate Experience → Update Memory → Daily Sync → Knowledge Retention → Smarter
```

## Automation Configuration

### Cron Job

**Name**: `update-memory-to-vllm-ascend-skill`

**Schedule**: Every day at 00:00 (midnight)

**Script**: `scripts/update_memory.py`

**Target Repository**: `nanxingMy/vllm-ascend-skill`

### Setup

The cron job is automatically created and scheduled:

```bash
# Check cron job status
hermes cronjob list

# The job runs automatically at midnight
# Next run: 2026-05-22 00:00:00
```

## What Gets Updated

### 1. Technical Knowledge

- Project architecture understanding
- Code structure mastery
- Tool chain usage
- Best practices

### 2. Process Experience

- Issue analysis methods
- PR creation workflow
- DCO fix techniques
- CI problem handling

### 3. Domain Knowledge

- vLLM framework
- NPU platform
- Model support
- Performance optimization

## Learning Effects

As time progresses, the digital employee will:

- ✅ Become more familiar with vllm-ascend project
- ✅ Solve problems faster
- ✅ Produce higher quality code
- ✅ Better understand best practices
- ✅ Deeper architecture understanding

## Current Achievements

### Completed PRs: 5

- #9199: Version suffix fix
- #9383: MiniMax-M2.7 documentation
- #9381: DeepSeek-V3.2 parameters
- #9416: BalanceScheduler deadlock check
- #9216: NPUWorker shutdown method

### PRs Learned: 1170 (39% of ~3000 total)

Learning from historical merged PRs to extract patterns and best practices:
- Feature: ~370 PRs
- Bug Fix: ~410 PRs
- Documentation: ~150 PRs
- Refactor: ~100 PRs
- Test: ~90 PRs
- Performance: ~65 PRs
- Other: ~50 PRs

**Learning Strategy**: Batch learning (50 PRs per batch), skip already-learned, resume on failure

### Created Skills: 6

- Issue handling workflow (5 stages)
- PR feedback handling
- DCO fix process
- Lint fix techniques
- CI monitoring
- Automatic update

### Accumulated Knowledge: 13 entries

- DCO requirements and fixes
- Git configuration and push
- Lint check and fix
- Review feedback handling
- Project path and structure
- Code style conventions

## PR Learning System

### Overview

Systematically learn from all historical merged PRs to extract solution patterns, best practices, and code modification techniques. This knowledge becomes reusable skills for future issue resolution.

### Learning Strategy

**Batch Learning**: 50 PRs per batch to avoid timeout and allow resumption

**Progress Tracking**: Skip already-learned PRs by checking existing data

**Failure Handling**: Continue despite network/SSL errors, resume from last position

### Cron Job

**Name**: `learn-daily-merged-prs`

**Schedule**: Every day at 00:00 (midnight)

**Script**: `scripts/learn_daily_prs.py`

**Output**: `skill/references/learned-from-prs/prs-data-{date}.json`

### What Gets Learned

For each PR:
- Issue information and problem description
- Solution approach and implementation
- Modified files and code changes
- Key patterns and techniques
- Category (Feature, Bug Fix, Documentation, etc.)

### Learning Effects

- **Pattern Recognition**: Identify common solution patterns
- **Best Practices**: Learn coding standards from examples
- **Problem Solving**: See how others solve similar issues
- **Architecture Understanding**: Deep project knowledge
- **Skill Precipitation**: Knowledge becomes reusable skills

### Related

- See `vllm-ascend` skill → `references/pr-learning-workflow.md` for detailed workflow

## Module-Based Learning System

### Overview

A structured learning system that breaks down vLLM-Ascend into 7 modules, learning one module per day. This makes the knowledge accessible to everyone, not just the digital employee.

### Learning Modules

| Day | Module | Content |
|-----|--------|---------|
| Monday | Architecture Overview | Project intro, directory structure, core modules, data flow |
| Tuesday | Core Components | NPUWorker, NPUModelRunner, Platform, config management |
| Wednesday | Platform Adaptation | Platform detection, device features, performance tuning |
| Thursday | Operators | Attention ops, MoE ops, quantization ops |
| Friday | Distributed System | Parallel strategies, communication, KV transfer |
| Saturday | Testing | Unit tests, e2e tests, performance tests |
| Sunday | Best Practices | Code style, error handling, performance optimization |

### Cron Job

**Name**: `module-learn-vllm-ascend`

**Schedule**: Every day at 00:00 (midnight)

**Script**: `scripts/module_learn.py`

**Output**: `skill/references/learned/<module>.md`

### Learning Effects

- **Newcomers**: 30 minutes to understand the project
- **Developers**: 1 week to master core concepts
- **Contributors**: 1 month to become proficient
- **Experts**: 3 months to become an expert

### Documentation Structure

```
skill/references/learned/
├── 01-architecture.md        # Architecture overview
├── 02-core-components.md     # Core components
├── 03-platform-adaptation.md # Platform adaptation
├── 04-operators.md           # Operators
├── 05-distributed.md         # Distributed system
├── 06-testing.md             # Testing
└── 07-best-practices.md      # Best practices
```

### Goal

Make vLLM-Ascend accessible to everyone through structured, easy-to-understand documentation. Each module includes:
- Clear explanations
- Code examples
- Diagrams
- Best practices

## Learn from Other Users

### Overview

Automatically learn from other users' solutions when they solve the same issues. This helps avoid repeating mistakes and improves problem-solving approaches.

### Learning Process

```
1. Check my PR status
   ├─ Merged → No learning needed
   └─ Not merged → Continue analysis

2. Find other solutions
   ├─ Check Issue comments
   ├─ Search related PRs
   └─ Filter merged PRs

3. Analyze solutions
   ├─ Modified files
   ├─ Modification approach
   ├─ Key code changes
   └─ Commit messages

4. Extract lessons
   ├─ Solution approach
   ├─ Code patterns
   ├─ Best practices
   └─ Things to avoid
```

### Cron Job

**Name**: `learn-from-other-users`

**Schedule**: Every day at 06:00

**Script**: `scripts/learn_from_others.py`

**Output**: `skill/references/learned-from-others/lessons-{date}.md`

### My PRs to Monitor

- PR #9199 (Issue #9167): vllm_version_is version suffix
- PR #9383 (Issue #9291): MiniMax-M2.7 documentation
- PR #9381 (Issue #9358): DeepSeek-V3.2 parameters
- PR #9416 (Issue #8975): BalanceScheduler deadlock
- PR #9216 (Issue #4112): NPUWorker shutdown

### Learning Effects

- **Week 1**: Understand different solution approaches
- **Month 1**: Accumulate common problem solutions
- **Month 3**: Master best practices
- **Month 6**: Become a problem-solving expert

## Manual Trigger

To manually trigger the update:

```bash
cd C:/Users/HuaWei/vllm-ascend-skill
python scripts/update_memory.py
```

To manually trigger module learning:

```bash
cd C:/Users/HuaWei/vllm-ascend-skill
python scripts/module_learn.py
```

To manually trigger learning from others:

```bash
cd C:/Users/HuaWei/vllm-ascend-skill
python scripts/learn_from_others.py
```

## Configuration

### Memory Location

- System Memory: `C:/Users/HuaWei/AppData/Local/hermes/memory/memory.md`
- User Profile: `C:/Users/HuaWei/AppData/Local/hermes/memory/user.md`

### Skill Repository

- Local: `C:/Users/HuaWei/vllm-ascend-skill`
- Remote: `https://github.com/nanxingMy/vllm-ascend-skill`

### Git Configuration

```bash
git config user.name "nanxingMy"
git config user.email "1014662416@qq.com"
```

## Best Practices

### DO

- ✅ Let the automation run daily
- ✅ Continue fixing issues and features
- ✅ Trust the learning process
- ✅ Review updates in vllm-ascend-skill

### DON'T

- ❌ Don't manually edit the cron job
- ❌ Don't skip the daily updates
- ❌ Don't ignore accumulated knowledge

## Related Skills

- `vllm-ascend-issue-workflow` - Issue handling workflow
- `hermes-agent` - Hermes configuration

## References

- [Update Script](scripts/update_memory.py) - The script that performs the daily update
- [Module Learning System](references/module-learning-system.md) - Detailed documentation of the module-based learning system
