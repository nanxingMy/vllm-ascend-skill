# Hermes Skill Structure for Shareable Projects

## Overview

When creating a Hermes skill that others can clone and use as a "digital employee" or automation tool, follow this structure to ensure one-click setup and usage.

## Directory Layout

```
project-name/
├── README.md              # Usage guide (how to clone, setup, use)
├── setup.sh               # One-click setup script (CRITICAL)
├── USAGE_GUIDE.md         # Detailed usage instructions
├── install.sh             # Optional: dependency installation
├── push.sh                # Optional: push to GitHub helper
│
└── skill/                 # Hermes skill structure
    ├── SKILL.md           # Skill definition (Hermes reads this)
    │
    └── references/        # Knowledge documents
        ├── architecture.md      # How the system works
        ├── inheritance.md       # Key relationships (most important!)
        ├── development-guide.md # How to develop/debug
        ├── lessons-learned.md   # Mistakes to avoid
        ├── pr-examples.md       # Real PR examples
        ├── quick-start.md       # Quick start guide
        └── examples.md          # Usage examples
```

## SKILL.md Structure

```markdown
---
name: skill-name
description: What this skill does
version: 1.0.0
author: your-name
tags:
  - tag1
  - tag2
---

# Skill Name

## Overview
Brief description of what this skill does.

## Triggers
When this skill should be activated.

## Core Knowledge
Key concepts and patterns.

## Workflow
Step-by-step process.

## Best Practices
DO and DON'T lists.

## Pitfalls
Common mistakes and how to avoid them.

## Examples
Real usage examples.

## References
- [Topic](references/topic.md)
```

## setup.sh Template

```bash
#!/bin/bash
# Hermes configuration script

set -e

echo "========================================="
echo "Skill Name - Hermes Configuration"
echo "========================================="
echo ""

# 1. Check Hermes is installed
echo "【1/5】检查 Hermes..."
if ! command -v hermes &> /dev/null; then
    echo "❌ Hermes 未安装"
    echo "请先安装: pip install hermes-agent"
    exit 1
fi
echo "✅ Hermes 已安装"

# 2. Create Hermes directories
HERMES_DIR="${HERMES_DIR:-$HOME/.hermes}"
SKILLS_DIR="$HERMES_DIR/skills"
mkdir -p "$SKILLS_DIR"
mkdir -p "$HERMES_DIR/memory"

# 3. Install skill
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SOURCE="$SCRIPT_DIR/skill"
SKILL_TARGET="$SKILLS_DIR/skill-name"

if [ -d "$SKILL_TARGET" ]; then
    echo "⚠️  Skill 已存在，更新中..."
    rm -rf "$SKILL_TARGET"
fi

cp -r "$SKILL_SOURCE" "$SKILL_TARGET"
echo "✅ Skill 已安装到: $SKILL_TARGET"

# 4. Import knowledge to Hermes memory
MEMORY_FILE="$HERMES_DIR/memory/skill_knowledge.md"
cat > "$MEMORY_FILE" << 'EOF'
# Core Knowledge Summary

## Key Concept 1
Brief explanation.

## Key Concept 2
Brief explanation.
EOF
echo "✅ 知识库已导入"

# 5. Create config if needed
CONFIG_FILE="$HERMES_DIR/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
model: anthropic/claude-sonnet-4

memory:
  enabled: true
  files:
    - skill_knowledge.md

skills:
  enabled: true
  directories:
    - ~/.hermes/skills
EOF
fi

echo ""
echo "========================================="
echo "✅ 配置完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. 启动 Hermes: hermes"
echo "2. 加载 skill: /load-skill skill-name"
echo "3. 开始工作: 帮我分析 Issue #XXX"
```

## README.md Template

```markdown
# Project Name - Digital Employee

## One-Click Setup

```bash
git clone https://github.com/user/project-name.git
cd project-name
bash setup.sh
hermes
/load-skill skill-name
```

## What This Does

Brief description of capabilities.

## Prerequisites

- Python 3.10-3.11
- Git
- Hermes Agent (`pip install hermes-agent`)

## Usage

### Basic Usage

```
用户: 帮我分析 Issue #XXX

数字员工: 我来分析...
【分析】问题类型
【检查】关键点
【修复】方案
【提交】PR
```

## Knowledge Base

- [Architecture](skill/references/architecture.md) - How it works
- [Inheritance](skill/references/inheritance.md) - Key relationships
- [Examples](skill/references/examples.md) - Usage examples
```

## Key Principles

### 1. Knowledge vs Tool Separation

- **Knowledge**: Markdown documents (human-readable, reference material)
- **Tool**: Hermes Agent (execution engine)
- **Skill**: Bridge between knowledge and tool

### 2. One-Click Philosophy

Users should be able to:
1. Clone the project
2. Run ONE command (`bash setup.sh`)
3. Start using immediately

No manual configuration, no editing files, no setup steps.

### 3. Self-Contained

The project should include:
- All knowledge needed
- All setup scripts
- All usage examples
- All troubleshooting guides

Users shouldn't need to look up external documentation.

## Common Mistakes

### ❌ Mistake 1: Only Markdown, No Skill Structure

```
project/
├── README.md
├── docs/
│   ├── architecture.md
│   └── guide.md
```

**Problem**: Others can read the docs but can't use them as a working tool.

**Fix**: Add `skill/SKILL.md` and `setup.sh`.

### ❌ Mistake 2: No setup.sh

**Problem**: Users have to manually:
- Create `~/.hermes/skills/` directory
- Copy skill files
- Configure Hermes
- Import knowledge

**Fix**: Automate everything in `setup.sh`.

### ❌ Mistake 3: SKILL.md Missing Frontmatter

```markdown
# My Skill

Some content...
```

**Problem**: Hermes can't recognize the skill.

**Fix**: Add YAML frontmatter:
```markdown
---
name: my-skill
description: What it does
version: 1.0.0
---

# My Skill
...
```

## Verification Checklist

After creating the project, verify:

- [ ] `skill/SKILL.md` exists with proper frontmatter
- [ ] `setup.sh` is executable (`chmod +x setup.sh`)
- [ ] `setup.sh` creates `~/.hermes/skills/<name>/`
- [ ] `setup.sh` imports knowledge to `~/.hermes/memory/`
- [ ] README.md has one-click instructions
- [ ] Clone → setup.sh → hermes works end-to-end

## Example: vllm-ascend-skill

Created May 2026 as a shareable digital employee for vLLM-Ascend development.

**Structure**:
- 16 files total
- `skill/SKILL.md` with complete knowledge
- `setup.sh` for one-click configuration
- `skill/references/` with 7 knowledge documents

**User workflow**:
```bash
git clone https://github.com/nanxingMy/vllm-ascend-skill.git
cd vllm-ascend-skill
bash setup.sh
hermes
/load-skill vllm-ascend-digital-employee
帮我分析 Issue #8975
```

**Result**: Anyone can have a 24/7 digital employee for vLLM-Ascend work.
