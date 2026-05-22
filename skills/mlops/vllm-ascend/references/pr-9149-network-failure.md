# CI 网络问题诊断案例

## PR #9149 网络失败

### 时间线

1. **第一次 CI 运行** (SHA: 569c770)
   - 3 个任务失败
   - 所有失败都在 "Install vllm-project/vllm-ascend" 步骤

2. **错误分析**
   - 错误类型：`pip._vendor.urllib3.exceptions.ProtocolError`
   - 具体错误：`IncompleteRead(35766015 bytes read, 152685937 more expected)`
   - 发生位置：下载 `mypy==1.11.1` 时

3. **本地验证**
   ```bash
   python -m py_compile vllm_ascend/platform.py  # 通过
   python -m py_compile tests/ut/test_platform.py  # 通过
   ```
   结论：代码没有问题

4. **处理**
   - 创建空提交触发新 CI
   - 新 CI 运行 (SHA: baed493)
   - 全部通过

### 关键学习

**网络问题特征：**
- 错误包含 `IncompleteRead`, `Connection broken`, `ProtocolError`
- 失败发生在 pip/wget 下载阶段
- 多个任务在同一安装步骤失败

**处理原则：**
- 不要修改代码（问题不在代码）
- 重新触发 CI 即可
- 可以创建空提交或点击 "Re-run all jobs"

### 诊断流程

```
CI 失败
    ↓
检查失败步骤
    ↓
是否都在 "Install" 步骤？
    ├─ 是 → 检查日志关键词
    │        ├─ 网络关键词 → 网络问题，重试 CI
    │        └─ 无网络关键词 → 可能是代码问题，本地验证
    └─ 否 → 测试失败，分析测试日志
```

### 相关文件

- 详细诊断指南：`pr-feedback-handler` skill → `references/ci-network-issues.md`
