# Lint Fix Patterns

## Common Lint Failures

### 1. Yaml Sync Lint Error

**Problem**: New documentation file causes yaml sync lint error:
```
Check docs/yaml sync blocks...Failed
- hook id: check-docs-yaml-sync
- exit code: 1

MiniMax-M2.7.md:1: yaml sync lint error
  yaml: -
  target: -
```

**Root Cause**: New documentation file not in exclude list.

**Solution**: Add file to `pyproject.toml` exclude list:
```toml
[tool.check_docs_yaml_sync]
exclude = [
    "docs/source/tutorials/models/DeepSeek-R1.md",
    "docs/source/tutorials/models/DeepSeek-V3.1.md",
    ...,
    "docs/source/tutorials/models/MiniMax-M2.7.md",  # Add this line
]
```

**Steps**:
1. Read `pyproject.toml`
2. Find `[tool.check_docs_yaml_sync]` section
3. Add new file path to `exclude` list
4. Commit and push

**Example Fix**:
```bash
# 1. Edit pyproject.toml
# Add: "docs/source/tutorials/models/MiniMax-M2.7.md"

# 2. Commit
git add pyproject.toml
git commit -s -m "[Doc] Add MiniMax-M2.7.md to yaml sync exclude list

- Add MiniMax-M2.7.md to check_docs_yaml_sync exclude list
- Fix 'yaml sync lint error' in pre-commit
- Same as MiniMax-M2.5.md, no test cases needed"

# 3. Push
git push fork HEAD:<branch-name>
```

### 2. Ruff Format Error

**Problem**: Code not formatted correctly.

**Solution**:
```bash
ruff format <files>
git add <files>
git commit -s -m "[Style] Fix ruff formatting issues"
```

### 3. Ruff Check Error

**Problem**: Code style violations.

**Common issues**:
- F401: Unused imports
- SIM117: Nested with statements should be combined

**Solution**:
```bash
# Auto-fix
ruff check --fix <files>

# Manual fix if needed
# Then commit
git add <files>
git commit -s -m "[Style] Fix ruff check issues"
```

## Verification

Before pushing, always run:
```bash
# Format check
ruff format --check <files>

# Style check
ruff check <files>

# Pre-commit (runs all checks)
pre-commit run --all-files
```

## Important Notes

1. **Always run lint before committing** - Saves CI time
2. **Add new doc files to exclude list** - If they don't need yaml sync
3. **Match existing exclude patterns** - Look at similar files in the list
4. **Document why** - In commit message, explain why file is excluded

## Example: Fix PR #9383 Lint

PR #9383 had yaml sync lint error for MiniMax-M2.7.md.

Fix:
```bash
# 1. Add to pyproject.toml
# In [tool.check_docs_yaml_sync] exclude list:
# "docs/source/tutorials/models/MiniMax-M2.7.md"

# 2. Commit
git commit -s -m "[Doc] Add MiniMax-M2.7.md to yaml sync exclude list"

# 3. Push
git push fork HEAD:doc/add-minimax-m2.7-support-9291
```

Result: Lint check passed.
