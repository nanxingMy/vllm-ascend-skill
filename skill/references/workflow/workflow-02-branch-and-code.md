# 阶段 2: 分支创建与代码修改

## 🎯 目标

创建分支并修改代码，完成本地测试。

---

## 📋 步骤

### 2.1 同步 Fork Main

#### 为什么需要同步？
- 确保 fork 的 main 与主仓库同步
- 避免创建分支时出现冲突
- 使用最新的代码基础

#### 同步方法

##### 方法 1: 使用 GitHub API（推荐）
```python
import requests

# 获取主仓库 main 的最新 SHA
response = requests.get(
    'https://api.github.com/repos/vllm-project/vllm-ascend/git/refs/heads/main',
    headers={'Authorization': f'token {token}'}
)
main_sha = response.json()['object']['sha']

# 更新 fork main
response = requests.patch(
    'https://api.github.com/repos/nanxingMy/vllm-ascend/git/refs/heads/main',
    headers={'Authorization': f'token {token}'},
    json={'sha': main_sha, 'force': True}
)
```

##### 方法 2: 使用 Git 命令
```bash
# 添加主仓库为 remote（如果还没有）
git remote add upstream https://github.com/vllm-project/vllm-ascend.git

# 获取主仓库最新代码
git fetch upstream main

# 更新本地 main
git checkout main
git reset --hard upstream/main

# 推送到 fork
git push origin main --force
```

---

### 2.2 创建新分支

#### 分支命名规范
```
<type>/<description>-<issue-number>

type:
  - feature: 新功能
  - bugfix: Bug 修复
  - doc: 文档更新
  - refactor: 重构
  - test: 测试

示例:
  - bugfix/scheduler-mutex-8975
  - feature/add-new-api-1234
  - doc/update-readme-5678
```

#### 创建分支
```bash
# 切换到 main
git checkout main

# 确保是最新的
git pull origin main

# 创建新分支
git checkout -b <branch-name>

# 示例
git checkout -b bugfix/scheduler-mutex-8975
```

---

### 2.3 修改代码

#### 修改步骤
1. **定位代码位置**
   ```bash
   # 搜索相关代码
   grep -r "search_term" vllm_ascend/
   
   # 查看文件
   cat vllm_ascend/platform.py
   ```

2. **修改代码**
   - 使用编辑器修改文件
   - 或使用 `patch` 工具
   - 或使用 `sed` 命令

3. **验证修改**
   ```bash
   # 查看修改
   git diff
   
   # 查看修改的文件
   git status
   ```

#### 修改原则
- **最小修改原则**: 只修改必要的代码
- **保持风格一致**: 匹配现有代码风格
- **添加注释**: 解释修改原因
- **关联 Issue**: 在注释中引用 Issue 编号

---

### 2.4 本地测试

#### 运行测试
```bash
# 运行单元测试
pytest tests/ut/test_platform.py -v

# 运行特定测试
pytest tests/ut/test_platform.py::TestNPUPlatform::test_method -v

# 运行所有测试
pytest tests/ut/ -v
```

#### 代码检查
```bash
# 格式检查
ruff check vllm_ascend/

# 格式化
ruff format vllm_ascend/

# 类型检查
mypy vllm_ascend/
```

#### 验证修改
- [ ] 代码编译通过
- [ ] 单元测试通过
- [ ] 代码格式检查通过
- [ ] 功能验证通过

---

## 🔧 工具使用

### 使用 patch 工具
```python
from hermes_tools import patch

# 替换代码
patch(
    path='vllm_ascend/platform.py',
    old_string='old code',
    new_string='new code'
)
```

### 使用 read_file 工具
```python
from hermes_tools import read_file

# 读取文件
result = read_file(
    path='vllm_ascend/platform.py',
    offset=100,
    limit=50
)
```

### 使用 search_files 工具
```python
from hermes_tools import search_files

# 搜索代码
result = search_files(
    pattern='enable_balance_scheduling',
    path='vllm_ascend/',
    target='content'
)
```

---

## 📝 案例: Issue #8975

### 创建分支
```bash
# 同步 fork main
# (使用 GitHub API)

# 创建分支
git checkout main
git checkout -b bugfix/scheduler-mutex-8975
```

### 修改代码

#### 文件 1: vllm_ascend/platform.py
```python
# 添加互斥检查
# NOTE: BalanceScheduler and RecomputeScheduler must not be enabled simultaneously.
# In PD disaggregation mode with multi-DP MoE, enabling both schedulers can cause
# MoE communication type mismatch across DP ranks (some perform All2AllV, others MC2),
# leading to AlltoAll deadlock. See https://github.com/vllm-project/vllm-ascend/issues/8975
if ascend_config.enable_balance_scheduling and ascend_config.recompute_scheduler_enable:
    raise ValueError(
        "VLLM_ASCEND_BALANCE_SCHEDULING (balance scheduling) and recompute_scheduler_enable "
        "cannot be enabled simultaneously. This combination causes MoE communication type "
        "mismatch across DP ranks in PD disaggregation mode, leading to AlltoAll deadlock. "
        "Please disable one of them."
    )
```

#### 文件 2: tests/ut/test_platform.py
```python
# 添加单元测试
def test_balance_scheduler_and_recompute_scheduler_mutex_check(self):
    """Test that BalanceScheduler and RecomputeScheduler cannot be enabled simultaneously."""
    # ... test code ...

def test_balance_scheduler_alone_works(self):
    """Test that BalanceScheduler alone works fine."""
    # ... test code ...

def test_recompute_scheduler_alone_works(self):
    """Test that RecomputeScheduler alone works fine."""
    # ... test code ...
```

### 本地测试
```bash
# 运行测试
pytest tests/ut/test_platform.py::TestNPUPlatform::test_balance_scheduler_and_recompute_scheduler_mutex_check -v

# 格式化
ruff format vllm_ascend/platform.py tests/ut/test_platform.py
```

---

## ✅ 检查清单

### 代码修改完成检查
- [ ] Fork main 已同步
- [ ] 新分支已创建
- [ ] 代码已修改
- [ ] 测试已添加
- [ ] 本地测试通过
- [ ] 代码格式检查通过

### 准备进入下一阶段
- [ ] 所有修改已完成
- [ ] 本地测试通过
- [ ] 准备提交代码

---

## 📝 输出

完成本阶段后，应该有：

1. **分支名称**: `<branch-name>`
2. **修改的文件**: 文件列表
3. **测试结果**: 通过/失败
4. **准备提交**: 是/否

---

## 🔄 下一阶段

准备完成后，进入 [阶段 3: PR 创建与 DCO 处理](./workflow-03-pr-and-dco.md)

---

**阶段**: 2/5  
**文档版本**: v1.0
