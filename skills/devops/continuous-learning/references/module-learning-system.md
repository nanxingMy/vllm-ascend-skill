# Module-Based Learning System

A structured approach to learning vLLM-Ascend that makes knowledge accessible to everyone.

## Overview

Instead of learning everything at once, the system breaks down vLLM-Ascend into 7 modules, learning one module per day. This prevents information overload and ensures comprehensive coverage.

## Learning Schedule

| Day | Module | Topics | Output File |
|-----|--------|--------|-------------|
| Monday | Architecture Overview | Project intro, directory structure, core modules, data flow | `01-architecture.md` |
| Tuesday | Core Components | NPUWorker, NPUModelRunner, Platform, config management | `02-core-components.md` |
| Wednesday | Platform Adaptation | Platform detection, device features, performance tuning | `03-platform-adaptation.md` |
| Thursday | Operators | Attention ops, MoE ops, quantization ops | `04-operators.md` |
| Friday | Distributed System | Parallel strategies, communication, KV transfer | `05-distributed.md` |
| Saturday | Testing | Unit tests, e2e tests, performance tests | `06-testing.md` |
| Sunday | Best Practices | Code style, error handling, performance optimization | `07-best-practices.md` |

## Module Content Structure

Each module document includes:

### 1. Overview
- Module purpose and scope
- Key concepts
- Prerequisites

### 2. Detailed Explanation
- Architecture diagrams
- Code flow
- Component relationships

### 3. Code Examples
- Real code snippets from vllm-ascend
- Annotated with explanations
- Common patterns

### 4. Best Practices
- Recommended approaches
- Common pitfalls
- Performance tips

### 5. References
- Related files
- Further reading
- Related modules

## Automation

### Cron Job: `module-learn-vllm-ascend`

**Schedule**: Every day at 00:00

**Script**: `scripts/module_learn.py`

**Process**:
1. Determine current day of week
2. Select appropriate module
3. Analyze vllm-ascend codebase
4. Generate structured documentation
5. Commit and push to vllm-ascend-skill

### Manual Execution

```bash
cd C:/Users/HuaWei/vllm-ascend-skill
python scripts/module_learn.py
```

## Learning Outcomes

### For Newcomers (30 minutes)
- Understand what vLLM-Ascend is
- Know the basic architecture
- Understand the directory structure
- Know where to find key files

### For Developers (1 week)
- Master all core components
- Understand platform adaptation
- Know operator implementations
- Understand distributed system

### For Contributors (1 month)
- Familiar with entire codebase
- Can implement new features
- Know testing patterns
- Follow best practices

### For Experts (3 months)
- Deep understanding of all modules
- Can optimize performance
- Can debug complex issues
- Can mentor others

## Document Quality Standards

Each generated document must:

1. **Be Self-Contained**: Understandable without reading other modules
2. **Have Clear Structure**: Use consistent headings and formatting
3. **Include Examples**: Real code from the project
4. **Be Actionable**: Readers can apply the knowledge
5. **Stay Current**: Updated automatically every week

## Integration with Continuous Learning

The module-based learning system complements the continuous learning mechanism:

- **Continuous Learning**: Accumulates experience from fixing issues
- **Module Learning**: Systematically covers all aspects of the project

Together, they ensure:
- Experience is captured (continuous learning)
- Knowledge is structured (module learning)
- Documentation is always up-to-date (both)

## Success Metrics

- ✅ All 7 modules generated
- ✅ Each module < 2000 lines (readable in one session)
- ✅ Code examples from actual project
- ✅ Clear explanations for all skill levels
- ✅ Automatic weekly updates

## User Feedback

**User requirement**: "This task needs to learn vllm-ascend architecture, design, and code aspects, various kinds, so that everyone can understand vllm-ascend when they see it. If too long, can split into multiple modules and learn in batches."

**Implementation**: 7 modules, one per day, each focused on a specific aspect, with automatic daily learning and documentation generation.
