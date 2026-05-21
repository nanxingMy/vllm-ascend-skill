# 阶段 4: 检视意见处理

## 🎯 目标

检测、处理并关闭检视意见。

---

## 📋 步骤

### 4.1 检测检视意见

#### 获取 Review Comments
```bash
# 使用 GitHub CLI
gh api repos/vllm-project/vllm-ascend/pulls/<pr-number>/comments

# 使用 curl
curl -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/vllm-project/vllm-ascend/pulls/<pr-number>/comments"
```

#### 获取 Reviews
```bash
# 使用 GitHub CLI
gh api repos/vllm-project/vllm-ascend/pulls/<pr-number>/reviews

# 使用 curl
curl -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/vllm-project/vllm-ascend/pulls/<pr-number>/reviews"
```

#### 检视意见类型
| 类型 | 来源 | 处理方式 |
|------|------|---------|
| Review Comment | 代码行评论 | 修改代码 |
| Review | 整体评论 | 更新 PR |
| Issue Comment | 一般评论 | 回复说明 |

---

### 4.2 分析检视意见

#### 常见检视意见类型

##### 1. 代码修改建议
```
文件: vllm_ascend/platform.py
行: 499
内容: 建议修改代码逻辑
```

**处理**: 修改代码 → 提交 → 推送

##### 2. PR 格式建议
```
内容: 建议更新 PR title 和 summary
```

**处理**: 更新 PR 描述

##### 3. 测试建议
```
内容: 建议添加测试用例
```

**处理**: 添加测试 → 提交 → 推送

##### 4. 文档建议
```
内容: 建议更新文档
```

**处理**: 更新文档 → 提交 → 推送

---

### 4.3 自动处理检视意见

#### 工作流程
```
检测 → 分析 → 修改 → 提交 → 回复 → 关闭
```

#### 处理代码修改建议
```bash
# 1. 修改代码
# 编辑文件

# 2. 提交修改
git add <files>
git commit -s -m "Address review feedback: <description>"
git push origin <branch-name>

# 3. 回复检视意见
gh api repos/vllm-project/vllm-ascend/pulls/<pr-number>/comments \
  -f body="✅ Thank you for the feedback! I have updated the code."
```

#### 处理 PR 格式建议
```bash
# 1. 更新 PR 描述
gh pr edit <pr-number> \
  --repo vllm-project/vllm-ascend \
  --title "New Title" \
  --body "New Body"

# 2. 回复检视意见
gh api repos/vllm-project/vllm-ascend/pulls/<pr-number>/comments \
  -f body="✅ Updated PR title and summary as suggested."
```

#### 处理测试建议
```bash
# 1. 添加测试
# 编辑测试文件

# 2. 运行测试验证
pytest tests/ut/test_platform.py -v

# 3. 提交修改
git add tests/
git commit -s -m "Add tests as suggested in review"
git push origin <branch-name>

# 4. 回复检视意见
gh api repos/vllm-project/vllm-ascend/pulls/<pr-number>/comments \
  -f body="✅ Added tests as suggested."
```

---

### 4.4 回复并关闭检视意见

#### 回复方式

##### 方式 1: 回复特定评论
```python
import requests

response = requests.post(
    'https://api.github.com/repos/vllm-project/vllm-ascend/pulls/<pr-number>/comments',
    headers={'Authorization': f'token {token}'},
    json={
        'body': '✅ Thank you for the feedback! I have addressed this comment.',
        'in_reply_to': comment_id
    }
)
```

##### 方式 2: 创建总结评论
```python
response = requests.post(
    'https://api.github.com/repos/vllm-project/vllm-ascend/issues/<pr-number>/comments',
    headers={'Authorization': f'token {token}'},
    json={
        'body': '''## ✅ Review Feedback Addressed

All review comments have been addressed:

1. **Comment 1**: Updated code logic
2. **Comment 2**: Added test cases
3. **Comment 3**: Updated documentation

Thank you for the feedback! 🎉'''
    }
)
```

#### 标记为已解决
```markdown
## ✅ Review Feedback Addressed

All review comments have been addressed:
- [x] Comment 1: ...
- [x] Comment 2: ...
- [x] Comment 3: ...

Thank you for the feedback! 🎉
```

---

## 🔧 自动化脚本

### 自动处理检视意见
```python
import requests

def process_review_comments(pr_number, token):
    # 1. 获取检视意见
    response = requests.get(
        f'https://api.github.com/repos/vllm-project/vllm-ascend/pulls/{pr_number}/comments',
        headers={'Authorization': f'token {token}'}
    )
    comments = response.json()
    
    # 2. 处理每个检视意见
    for comment in comments:
        # 分析检视意见
        feedback_type = analyze_feedback(comment['body'])
        
        # 根据类型处理
        if feedback_type == 'code':
            modify_code(comment)
            commit_and_push()
            reply_to_comment(comment['id'], '✅ Code updated')
        elif feedback_type == 'format':
            update_pr_description()
            reply_to_comment(comment['id'], '✅ PR updated')
        elif feedback_type == 'test':
            add_tests()
            commit_and_push()
            reply_to_comment(comment['id'], '✅ Tests added')
    
    # 3. 创建总结评论
    create_summary_comment(pr_number)
```

---

## 📝 案例: PR #9416

### 检视意见
```
来源: Gemini Code Assist
文件: vllm_ascend/platform.py
行: 499
优先级: High

内容: To adhere to the repository's pull request summary style guide, 
please update the PR title and summary as follows:

**Suggested PR Title:**
[Ops][BugFix] Add mutual exclusion check for BalanceScheduler and RecomputeScheduler

**Suggested PR Summary:**
### What this PR does / why we need it?
...
```

### 处理步骤

#### 1. 分析检视意见
- 类型: PR 格式建议
- 需要更新 PR title 和 summary

#### 2. 更新 PR
```bash
gh pr edit 9416 \
  --repo vllm-project/vllm-ascend \
  --title "[Ops][BugFix] Add mutual exclusion check for BalanceScheduler and RecomputeScheduler" \
  --body "### What this PR does / why we need it?

This PR introduces a mutual exclusion check between BalanceScheduler and RecomputeScheduler.

Fixes #8975

### Does this PR introduce _any_ user-facing change?

Yes. The system will now raise a ValueError if both schedulers are enabled.

### How was this patch tested?

- Added unit tests in tests/ut/test_platform.py
- Verified that each scheduler can be enabled individually"
```

#### 3. 回复检视意见
```python
requests.post(
    'https://api.github.com/repos/vllm-project/vllm-ascend/pulls/9416/comments',
    headers={'Authorization': f'token {token}'},
    json={
        'body': '✅ Thank you for the feedback! I have updated the PR title and summary according to the repository style guide.',
        'in_reply_to': 3279410804
    }
)
```

#### 4. 创建总结评论
```python
requests.post(
    'https://api.github.com/repos/vllm-project/vllm-ascend/issues/9416/comments',
    headers={'Authorization': f'token {token}'},
    json={
        'body': '''## ✅ Review Feedback Addressed

All review comments from Gemini Code Assist have been addressed:

1. **PR Title**: Updated to follow the repository style guide
2. **PR Summary**: Updated with proper sections

Thank you for the feedback! 🎉'''
    }
)
```

---

## ✅ 检查清单

### 检视意见处理检查
- [ ] 已获取所有检视意见
- [ ] 已分析每个检视意见
- [ ] 已修改代码/PR 描述
- [ ] 已提交并推送修改
- [ ] 已回复每个检视意见
- [ ] 已创建总结评论
- [ ] 所有检视意见已关闭

### 准备进入下一阶段
- [ ] 无未处理的检视意见
- [ ] 所有修改已提交
- [ ] 准备监控 CI

---

## 📝 输出

完成本阶段后，应该有：

1. **检视意见数量**: 已处理 `<n>` 条
2. **修改内容**: 修改描述
3. **回复状态**: ✅ 已回复
4. **总结评论**: ✅ 已创建

---

## 🔄 下一阶段

准备完成后，进入 [阶段 5: CI 监控与合并](./workflow-05-ci-and-merge.md)

---

**阶段**: 4/5  
**文档版本**: v1.0
