# vLLM-Ascend 单元测试模式

## 测试文件位置

- 单元测试: `tests/ut/`
- 端到端测试: `tests/e2e/`

## Platform 测试模式

测试文件: `tests/ut/test_platform.py`

### 基本结构

```python
import importlib
from unittest.mock import MagicMock, patch
import pytest
import torch
from vllm.config.compilation import CompilationMode, CUDAGraphMode
from vllm.platforms import PlatformEnum

from tests.ut.base import TestBase
from vllm_ascend.platform import NPUPlatform
from vllm_ascend.utils import AscendDeviceType

class TestNPUPlatform(TestBase):
    @staticmethod
    def mock_vllm_config():
        mock_vllm_config = MagicMock()
        mock_vllm_config.compilation_config = MagicMock()
        mock_vllm_config.model_config = MagicMock()
        mock_vllm_config.parallel_config = MagicMock()
        mock_vllm_config.cache_config = MagicMock()
        mock_vllm_config.scheduler_config = MagicMock()
        mock_vllm_config.scheduler_config.max_num_seqs = None
        mock_vllm_config.speculative_config = None
        mock_vllm_config.additional_config = {}
        return mock_vllm_config

    @staticmethod
    def mock_vllm_ascend_config():
        mock_ascend_config = MagicMock()
        mock_ascend_config.recompute_scheduler_enable = False
        mock_ascend_config.SLO_limits_for_dynamic_batch = -1
        return mock_ascend_config

    def setUp(self):
        self.platform = NPUPlatform()
```

### ValueError 测试模式

```python
@patch("vllm_ascend.quantization.utils.maybe_auto_detect_quantization")
@patch("vllm_ascend.utils.get_ascend_device_type", return_value=AscendDeviceType.A3)
@patch("vllm_ascend.ascend_config.init_ascend_config")
@patch("vllm_ascend.core.recompute_scheduler.RecomputeSchedulerConfig.initialize_from_config")
def test_check_and_update_config_rejects_invalid_config(
    self, mock_init_recompute, mock_init_ascend, mock_soc_version, mock_auto_detect
):
    """Test docstring explaining what is being tested."""
    # Setup mock config
    mock_ascend_config = TestNPUPlatform.mock_vllm_ascend_config()
    mock_ascend_config.recompute_scheduler_enable = True
    mock_init_ascend.return_value = mock_ascend_config

    # Setup vllm_config
    vllm_config = TestNPUPlatform.mock_vllm_config()
    vllm_config.kv_transfer_config = MagicMock(kv_role="kv_producer", engine_id="engine0")
    vllm_config.parallel_config.decode_context_parallel_size = 1
    vllm_config.parallel_config.prefill_context_parallel_size = 1
    vllm_config.parallel_config.tensor_parallel_size = 1
    vllm_config.scheduler_config = MagicMock()
    mock_init_recompute.return_value = MagicMock()

    # Reload platform module
    from vllm_ascend import platform
    importlib.reload(platform)
    self.platform = platform.NPUPlatform()

    # Test that ValueError is raised
    with (
        patch("vllm_ascend.platform.envs_ascend.SOME_ENV_VAR", True, create=True),
        pytest.raises(ValueError, match=r"expected error message pattern"),
        patch.object(platform.NPUPlatform, "_fix_incompatible_config"),
        patch.object(platform, "check_kv_extra_config"),
    ):
        self.platform.check_and_update_config(vllm_config)
```

### 常用 Patch 装饰器

```python
# 基础装饰器（每个测试都需要）
@patch("vllm_ascend.quantization.utils.maybe_auto_detect_quantization")
@patch("vllm_ascend.utils.get_ascend_device_type", return_value=AscendDeviceType.A3)
@patch("vllm_ascend.ascend_config.init_ascend_config")
@patch("vllm_ascend.core.recompute_scheduler.RecomputeSchedulerConfig.initialize_from_config")

# 环境变量 patch
patch("vllm_ascend.platform.envs_ascend.VLLM_ASCEND_BALANCE_SCHEDULING", True, create=True)

# 跳过不必要的检查
patch.object(platform.NPUPlatform, "_fix_incompatible_config")
patch.object(platform, "check_kv_extra_config")
```

### 运行测试

```bash
# 运行单个测试
python -m pytest tests/ut/test_platform.py::TestNPUPlatform::test_name -v

# 运行所有 platform 测试
python -m pytest tests/ut/test_platform.py -v
```

## 注意事项

1. **依赖问题**: 本地可能缺少 `torch-npu` 等 NPU 依赖，无法运行测试
2. **语法验证**: 使用 `python -m py_compile tests/ut/test_platform.py` 验证语法
3. **CI 测试**: 依赖 CI 进行实际测试（fork PR 可能被 skipped）
4. **Mock 顺序**: 装饰器从下往上应用，注意参数顺序
