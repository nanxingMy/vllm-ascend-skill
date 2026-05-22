# Issue 分析工作流

本文档记录分析 vLLM-Ascend GitHub Issue 并编写修复的完整流程。

## 一、获取 Issue 信息

### 1.1 列出 Open Issues

```bash
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/issues?state=open&per_page=20&sort=updated" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for issue in data:
    labels = ', '.join([l['name'] for l in issue.get('labels', [])])
    print(f\"#{issue['number']} | {labels} | {issue['title'][:60]}\")
"
```

### 1.2 获取 Issue 详情

```bash
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/issues/{ISSUE_NUMBER}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Title:', data['title'])
print('Labels:', ', '.join([l['name'] for l in data.get('labels', [])]))
print('Body:', data.get('body', 'No body'))
"
```

### 1.3 获取 Issue 评论

```bash
curl -s "https://api.github.com/repos/vllm-project/vllm-ascend/issues/{ISSUE_NUMBER}/comments" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for i, comment in enumerate(data):
    print(f\"Comment {i+1} by {comment['user']['login']}:\")
    print(comment['body'][:2000])
"
```

## 二、分析 Issue 类型

### 2.1 按标签分类

| 标签 | 类型 | 分析重点 |
|------|------|----------|
| `bug` | BugFix | 错误信息、复现步骤、影响范围 |
| `performance` | Performance | 性能退化点、基准数据 |
| `feature` | Feature | 需求描述、实现方案 |
| `documentation` | Doc | 文档缺失点 |

### 2.2 按模块分类

从 Issue 标题和标签识别涉及模块：
- `[Platform]` → `platform.py`
- `[Worker]` → `worker/`
- `[Attention]` → `attention/`
- `[MoE]` → `ops/fused_moe/`
- `[Quantization]` → `quantization/`
- `[Distributed]` → `distributed/`

## 三、定位问题代码

### 3.1 搜索相关代码

```bash
# 搜索关键词
grep -r "关键词" vllm_ascend/ --include="*.py"

# 或使用 search_files 工具
```

### 3.2 分析调用链

1. 从错误信息定位入口函数
2. 追踪调用链向上到触发点
3. 识别关键变量和状态

### 3.3 检查已有修复模式

参考 `references/debugging-patterns.md` 中的常见 BugFix 模式。

## 四、编写修复

### 4.1 修复原则

1. **最小侵入**: 只修改必要的代码
2. **清晰注释**: 解释为什么这样修复
3. **引用 Issue**: 注释中引用 Issue 编号
4. **保持风格**: 遵循项目代码风格

### 4.2 修复模板

```python
# NOTE: [简短描述问题]
# [详细解释根因和影响]
# See https://github.com/vllm-project/vllm-ascend/issues/{ISSUE_NUMBER}
if [冲突条件]:
    raise ValueError(
        "[配置项A] and [配置项B] cannot be enabled simultaneously. "
        "[解释后果]. Please disable one of them."
    )
```

### 4.3 验证修复

```bash
# 代码检查
ruff check vllm_ascend/[修改文件].py

# 单元测试 (如有)
pytest tests/ut/[相关测试].py
```

## 五、提交 PR

### 5.1 Git 工作流

```bash
# 创建分支
git checkout -b bugfix/[简短描述]-[ISSUE_NUMBER]

# 提交修改 (必须 -s 签名)
git add [修改文件]
git commit -s -m "[BugFix][Module] 简短描述

详细解释问题和解决方案。

Fixes #{ISSUE_NUMBER}"

# 推送到 fork
git push fork bugfix/[简短描述]-[ISSUE_NUMBER]
```

### 5.2 PR 标题格式

```
[Type][Module] Description
```

类型: BugFix, Feature, Performance, Refactor, Misc, Doc, CI, Test

### 5.3 PR 描述模板

```markdown
### What this PR does / why we need it?

[问题描述]
[根因分析]
[解决方案]

### Does this PR introduce _any_ user-facing change?

[Yes/No + 详细说明]

### How was this patch tested?

- [测试方法]

Fixes #{ISSUE_NUMBER}

---------
Signed-off-by: Name <email>
```

## 六、案例：Issue #8975 分析

### 6.1 Issue 概要

- **标题**: PD分离部署，推理服务偶发性卡死
- **标签**: bug, triaged, pd-disaggreagtion, core-features
- **现象**: D0/D1 的 32 rank 同时卡死，HCCL heartbeat 检测到 STUCK

### 6.2 根因分析

从评论中提取关键信息：
1. 死锁发生在 `group_name_233` (MC2 AlltoAll)
2. 用户设置了 `VLLM_ASCEND_BALANCE_SCHEDULING=1`
3. BalanceScheduler + RecomputeScheduler 同时启用
4. 导致不同 DP rank 使用不同 MoE 通信类型

### 6.3 定位代码

```
platform.py:474-496
├── BalanceScheduler 检查 (L474-482)
├── RecomputeScheduler 检查 (L484-496)
└── 缺少: 两者互斥检查
```

### 6.4 修复代码

```python
# NOTE: BalanceScheduler and RecomputeScheduler must not be enabled simultaneously.
# In PD disaggregation mode with multi-DP MoE, enabling both schedulers can cause
# MoE communication type mismatch across DP ranks (some perform All2AllV, others MC2),
# leading to AlltoAll deadlock. See https://github.com/vllm-project/vllm-ascend/issues/8975
if envs_ascend.VLLM_ASCEND_BALANCE_SCHEDULING and ascend_config.recompute_scheduler_enable:
    raise ValueError(
        "VLLM_ASCEND_BALANCE_SCHEDULING (balance scheduling) and recompute_scheduler_enable "
        "cannot be enabled simultaneously. This combination causes MoE communication type "
        "mismatch across DP ranks in PD disaggregation mode, leading to AlltoAll deadlock. "
        "Please disable one of them."
    )
```

### 6.5 提交信息

```
[BugFix][Platform] Add mutual exclusion check for BalanceScheduler and RecomputeScheduler

This PR adds a mutual exclusion check to prevent VLLM_ASCEND_BALANCE_SCHEDULING
(BalanceScheduler) and recompute_scheduler_enable (RecomputeScheduler) from
being enabled simultaneously.

Fixes #8975

Signed-off-by: nanxing <1014662416@qq.com>
```

## 七、常见 Issue 类型速查

| Issue 类型 | 典型特征 | 定位模块 | 修复模式 |
|-----------|---------|---------|---------|
| 配置冲突 | 多个配置同时启用导致异常 | platform.py | 添加互斥检查 |
| 维度不匹配 | shape mismatch 错误 | ops/, quantization/ | 检查权重处理逻辑 |
| 通信死锁 | HCCL STUCK, AlltoAll hang | distributed/, ops/fused_moe/ | 检查通信组一致性 |
| 内存 OOM | out of memory | platform.py, worker/ | 内存规划、释放时机 |
| 精度问题 | 输出错误、accuracy drop | quantization/, ops/ | scale/offset 传递 |
