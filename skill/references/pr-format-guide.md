# vLLM-Ascend PR 格式指南

## 📋 从 Gemini Code Assist 学到的格式要求

---

## 1. PR 标题格式

### ✅ 正确格式

```
[Doc][BugFix] Fix parameter mismatch in DeepSeek-V3.2.md
```

### 格式要求

- **必须使用 `[]` 标签**
- **标签顺序**: `[类型][子类型]`
- **标题**: 简洁描述修改内容

### 常见标签

| 标签 | 说明 |
|------|------|
| `[Doc]` | 文档修改 |
| `[BugFix]` | Bug 修复 |
| `[Feature]` | 新功能 |
| `[CI]` | CI 相关 |
| `[Misc]` | 其他 |
| `[Model]` | 模型相关 |
| `[Ops]` | 算子相关 |
| `[Scheduler]` | 调度器相关 |

### 组合示例

```
[Doc][BugFix] Fix parameter mismatch in DeepSeek-V3.2.md
[Feature][Model] Add DeepSeek V4 support
[BugFix][Scheduler] Fix deadlock in BalanceScheduler
[CI][Misc] Bump actions version
```

---

## 2. PR 描述格式

### ✅ 正确格式

```markdown
### What this PR does / why we need it?

This PR corrects the `served-model-name` in the DeepSeek-V3.2 tutorial to ensure consistency with the model parameter used in the example query.

Fixes #9358

### Does this PR introduce _any_ user-facing change?

No.

### How was this patch tested?

Documentation update, verified by inspection.
```

### 必需部分

1. **What this PR does / why we need it?**
   - 描述 PR 做了什么
   - 为什么需要这个修改

2. **Does this PR introduce _any_ user-facing change?**
   - Yes 或 No
   - 如果 Yes，详细描述变化

3. **How was this patch tested?**
   - 测试方法
   - 例如：单元测试、手动测试、文档检查

4. **Fixes #XXX**
   - 关联的 Issue 编号

---

## 3. DCO 要求

### ✅ 每个 commit 必须有 Signed-off-by

```
Signed-off-by: Your Name <your.email@example.com>
```

### 提交时使用 `-s` 参数

```bash
git commit -s -m "[Doc][BugFix] Fix parameter mismatch"
```

### DCO 检查失败的原因

1. ❌ commit 缺少 `Signed-off-by`
2. ❌ merge commit 缺少 `Signed-off-by`
3. ⚠️ 需要在 PR 上确认 DCO

---

## 4. 分支命名规范

### ✅ 好的分支名

```
doc/fix-deepseek-v3.2-parameter-9358
bugfix/scheduler-mutex-check-8975
feature/add-vit-attn-backend-3489
```

### 格式

```
[类型]/[描述]-[issue编号]
```

### 类型

- `doc/` - 文档修改
- `bugfix/` - Bug 修复
- `feature/` - 新功能
- `ci/` - CI 相关

---

## 5. markdownlint 格式要求

### ❌ 错误格式

```markdown
**Note**: 
- item 1
- item 2
```

### ✅ 正确格式

```markdown
**Note**:

- item 1
- item 2
```

### 要求

1. **列表前要有空行**
2. **`**Note**:` 后不要有空格**
3. **列表项 `-` 后要有空格**

---

## 6. 完整工作流程

### 创建 PR 的正确流程

```bash
# 1. 从 main 创建分支
git checkout main
git pull origin main
git checkout -b doc/fix-issue-9358

# 2. 修改代码
# ...

# 3. 提交（使用 -s 添加 Signed-off-by）
git add .
git commit -s -m "[Doc][BugFix] Fix parameter mismatch

- Fix served-model-name
- Add parameter explanation

Fixes #9358

Signed-off-by: nanxing <1014662416@qq.com>"

# 4. 推送到 fork
git push fork HEAD:doc/fix-issue-9358

# 5. 手动创建 PR（Web UI）
# 访问: https://github.com/vllm-project/vllm-ascend/compare/main...nanxingMy:doc/fix-issue-9358?expand=1

# 6. 填写 PR 标题和描述（按格式）
```

---

## 7. 常见错误

### ❌ 错误的 PR 标题

```
Doc/fix deepseek v3.2 parameter 9358 v2
Fix bug
Update doc
```

### ✅ 正确的 PR 标题

```
[Doc][BugFix] Fix parameter mismatch in DeepSeek-V3.2.md
[BugFix][Scheduler] Fix deadlock in BalanceScheduler
[Feature][Model] Add DeepSeek V4 support
```

---

## 8. Gemini Code Assist 反馈处理

### 常见反馈

1. **PR 标题格式不符合规范**
   - 修改为 `[类型][子类型] 描述` 格式

2. **PR 描述格式不符合规范**
   - 添加必需的三个部分

3. **markdownlint 格式错误**
   - 修复列表格式
   - 添加空行

4. **模型名称不一致**
   - 检查是否应该修改
   - 有些名称不能改（如 `deepseek_v3.2`）

---

## 📚 参考

- [vLLM-Ascend Contributing Guide](https://github.com/vllm-project/vllm-ascend/blob/main/CONTRIBUTING.md)
- [Gemini Style Guide](https://github.com/vllm-project/vllm-ascend/blob/main/.gemini/styleguide.md)
- [DCO](https://developercertificate.org/)

---

**记住这些格式，下次创建 PR 时自动使用！** 🎊
