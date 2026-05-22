# Testing Environment Setup for vLLM-Ascend

## Recommended Testing Images

### Main Branch Environment (CANN 9.0.0)

For testing issues and PRs against the main branch:

```
Python: >= 3.10, < 3.12
CANN: 9.0.0
PyTorch: 2.10.0
torch-npu: 2.10.0
```

### CI-Used Docker Images

**Primary image (910B chip)**:
```bash
swr.cn-southwest-2.myhuaweicloud.com/base_image/ascend-ci/cann:9.0.0-910b-ubuntu22.04-py3.11
```

**A3 chip**:
```bash
swr.cn-southwest-2.myhuaweicloud.com/base_image/ascend-ci/cann:9.0.0-a3-ubuntu22.04-py3.11
```

**A2 chip**:
```bash
swr.cn-southwest-2.myhuaweicloud.com/base_image/ascend-ci/cann:9.0.0-a2-ubuntu22.04-py3.11
```

## Using CI Images for Local Testing

### Pull and Run

```bash
# Pull the image
docker pull swr.cn-southwest-2.myhuaweicloud.com/base_image/ascend-ci/cann:9.0.0-910b-ubuntu22.04-py3.11

# Run with NPU devices
docker run -it \
  --device=/dev/davinci0 \
  --device=/dev/davinci_manager \
  --device=/dev/devmm_svm \
  --device=/dev/hisi_hdev \
  -v /usr/local/Ascend:/usr/local/Ascend \
  -v $(pwd):/workspace \
  swr.cn-southwest-2.myhuaweicloud.com/base_image/ascend-ci/cann:9.0.0-910b-ubuntu22.04-py3.11 \
  /bin/bash
```

### Inside Container

```bash
cd /workspace
git clone https://github.com/vllm-project/vllm-ascend.git
cd vllm-ascend
pip install -e .

# Run specific tests
pytest tests/ut/worker/test_worker_v1.py::TestNPUWorker::test_shutdown_with_profiler -v
```

## Why Use CI Images?

1. **Consistency**: Same environment as CI, results are reliable
2. **Pre-configured**: All dependencies installed, ready to use
3. **Avoid issues**: No environment configuration problems

## Hardware Requirements

Supported hardware (from README.md):
- ✅ Atlas 800I A2 Inference series
- ✅ Atlas A2 Training series
- ✅ Atlas 800I A3 Inference series
- ✅ Atlas A3 Training series
- ⚠️ Atlas 300I Duo (Experimental)
- ✅ Atlas 310P (requires special handling, see `_310p/` directory)

## Alternative: Ascend Official Images

```bash
# From Ascend official repository
docker pull ascendhub.huawei.com/public-ascendhub/ascend-pytorch:24.0.rc1-910b-openeuler22.03-py3.11

# Then install vLLM-Ascend
pip install vllm-ascend
```

## Common CI Infrastructure Failures

### torch_npu Loading Failure

**Symptoms**:
```
RuntimeError: Failed to load the backend extension: torch_npu
```

**Diagnosis**: This is an infrastructure/environment issue, NOT a code problem.

**Occurs**: During test import phase (`conftest.py:43 import torch`), before any tests run.

**Solution**: This is a CI environment configuration issue. Report to maintainers or wait for CI fix.

**Reference**: PR #9216 e2e-light 310p test failures (May 2026).

### Distinguishing Code vs Infrastructure Failures

| Failure Type | Indicators | Action |
|--------------|-----------|--------|
| **Infrastructure** | Connection timeout, IncompleteRead, torch_npu load failure, import errors | Do NOT modify code, retry CI or wait |
| **Code** | Test assertion failures, logic errors, ruff format errors | Fix code and push |

**Key insight**: If failure happens during import/setup phase (before tests run), it's infrastructure. If failure is in test execution, check if it's your code.

## Testing Strategy

### For Issue Fixing

1. Use CI image matching target hardware (910B, A3, etc.)
2. Run relevant unit tests first: `pytest tests/ut/...`
3. If available, run e2e tests: `pytest tests/e2e/...`
4. Verify fix doesn't break other tests

### For PR Validation

1. CI will run automatically
2. Monitor CI results
3. Distinguish infrastructure failures from code failures
4. Fix only code failures

## Reference

- User question about testing environment (May 2026)
- PR #9216 CI failures (310p torch_npu loading)
- CI workflow files: `.github/workflows/pr_test_light.yaml`
