# vLLM-Ascend C++ Custom Operator Development

## Operator Implementation Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│  Python Layer (vllm_ascend/ops/*.py)                    │
│  - Calls torch.ops.vllm_ascend.xxx()                    │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│  Torch Binding (csrc/torch_binding.cpp)                 │
│  - ops.def("op_name", signature)                        │
│  - ops.impl("op_name", torch::kPrivateUse1, &func)      │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│  Torch Adapter (*_torch_adpt.h)                         │
│  - Parameter conversion, type dispatch                  │
│  - EXEC_NPU_CMD(aclnnOpName, args...)                   │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│  ACL NN Operator (op_host/ + op_kernel/)                │
│  - op_host/xxx_def.cpp    # Operator definition         │
│  - op_host/xxx_proto.cpp  # Prototype definition        │
│  - op_host/xxx_tiling.cpp # Tiling strategy             │
│  - op_kernel/xxx.cpp      # Kernel entry point          │
│  - op_kernel/xxx.h        # Kernel class definition     │
│  - op_kernel/xxx_kernel.hpp # Compute logic             │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
csrc/
├── torch_binding.cpp          # Python binding entry point
├── torch_binding_meta.cpp     # Metadata bindings
├── ops.h                      # Operator declarations
├── build.sh                   # Build script
├── build_aclnn.sh             # ACL NN build script
├── attention/                 # Attention operators
│   ├── lightning_indexer_vllm/
│   ├── recurrent_gated_delta_rule/
│   ├── reshape_and_cache_bnsd/
│   └── sparse_flash_attention/
├── moe/                       # MoE operators
│   ├── add_rms_norm_bias/
│   ├── apply_top_k_top_p_custom/
│   ├── moe_gating_top_k/
│   └── moe_init_routing_custom/
├── mc2/                       # MC2 communication fusion
│   ├── dispatch_ffn_combine/  # dispatch+FFN+combine fusion
│   ├── dispatch_gmm_combine_decode/
│   ├── matmul_allreduce_add_rmsnorm/
│   └── moe_combine_normal/
├── gmm/                       # Grouped matrix multiplication
├── mla_preprocess/            # MLA preprocessing
└── kernels/                   # Generic kernels
```

## Operator Definition Pattern (op_host/xxx_def.cpp)

```cpp
#include "register/op_def_registry.h"

namespace ops {
class DispatchFFNCombine : public OpDef {
 public:
  explicit DispatchFFNCombine(const char *name) : OpDef(name) {
    // Input definition
    this->Input("a")
        .ParamType(REQUIRED)
        .DataType({ge::DT_FLOAT16, ge::DT_BF16, ge::DT_BF16})
        .Format({ge::FORMAT_ND, ge::FORMAT_ND, ge::FORMAT_ND})
        .UnknownShapeFormat({ge::FORMAT_ND, ge::FORMAT_ND, ge::FORMAT_ND});
    
    // Dynamic input (list/tensor array)
    this->Input("w1")
        .ParamType(DYNAMIC)
        .DataType({ge::DT_INT8, ge::DT_INT8, ge::DT_INT8})
        .Format({ge::FORMAT_ND, ge::FORMAT_ND, ge::FORMAT_FRACTAL_NZ})
        .UnknownShapeFormat({ge::FORMAT_ND, ge::FORMAT_ND, ge::FORMAT_FRACTAL_NZ})
        .IgnoreContiguous();
    
    // Output definition
    this->Output("out")
        .ParamType(REQUIRED)
        .DataType({ge::DT_FLOAT16, ge::DT_BF16, ge::DT_BF16})
        .Format({ge::FORMAT_ND, ge::FORMAT_ND, ge::FORMAT_ND});
    
    // Attributes
    this->Attr("group").AttrType(REQUIRED).String();
    this->Attr("M").AttrType(OPTIONAL).Int();
    this->Attr("transB").AttrType(OPTIONAL).Bool(false);
    
    // AICore configuration
    OpAICoreConfig aicore_config;
    aicore_config.DynamicCompileStaticFlag(true)
        .DynamicFormatFlag(true)
        .DynamicRankSupportFlag(true)
        .DynamicShapeSupportFlag(true)
        .NeedCheckSupportFlag(false)
        .PrecisionReduceFlag(true)
        .ExtendCfgInfo("aclnnSupport.value", "support_aclnn")
        .ExtendCfgInfo("jitCompile.flag", "static_false")
        .ExtendCfgInfo("multiKernelSupportDynamicGraph.value", "multi_kernel");
    
    // Hardware support
    this->AICore().AddConfig("ascend910_93", aicore_config);  // A3
    this->AICore().AddConfig("ascend910b", aicore_config);    // A2
    
    // MC2 communication (if needed)
    this->MC2().HcclGroup("group");
  }
};

OP_ADD(DispatchFFNCombine);
}  // namespace ops
```

## Torch Adapter Pattern (*_torch_adpt.h)

```cpp
namespace vllm_ascend {
std::tuple<at::Tensor&, at::Tensor&> dispatch_ffn_combine(
    const at::Tensor& x,
    const at::TensorList& weight1,
    const at::TensorList& weight2,
    const at::Tensor& expert_idx,
    const at::TensorList& scale1,
    const at::TensorList& scale2,
    const c10::optional<at::TensorList>& bias1,
    const c10::optional<at::TensorList>& bias2,
    const at::Tensor& probs,
    c10::string_view group,
    int64_t max_output_size,
    at::Tensor& out,
    at::Tensor& expert_token_nums,
    const c10::optional<at::Tensor>& x_active_mask
) {
    char *group_ep_ptr = const_cast<char *>(group.data());
    
    // Type dispatch
    bool is_int8 = weight1[0].dtype() == at::kChar;
    bool is_int4 = weight1[0].dtype() == at::kInt;
    
    if (is_int8) {
        EXEC_NPU_CMD(aclnnDispatchFFNCombine,
                 x, weight1, weight2, expert_idx,
                 scale1, scale2, probs,
                 x_active_mask.has_value() ? x_active_mask.value() : at::Tensor(),
                 group_ep_ptr, max_output_size, out, expert_token_nums);
    } else if (is_int4) {
        EXEC_NPU_CMD(aclnnDispatchFFNCombineW4A8,
                 x, weight1, weight2, expert_idx,
                 scale1, scale2, bias1, bias2, probs,
                 group_ep_ptr, max_output_size, out, expert_token_nums);
    } else {
        EXEC_NPU_CMD(aclnnDispatchFFNCombineBF16,
                 x, weight1, weight2, expert_idx,
                 scale1, scale2, probs,
                 group_ep_ptr, max_output_size, out, expert_token_nums);
    }
    return {out, expert_token_nums};
}
}
```

## Kernel Class Pattern (op_kernel/xxx.h)

```cpp
using namespace AscendC;
#include "kernel_operator.h"

template <typename AType_, typename BType_, typename CType_, bool TB_, bool Nz_>
class DispatchFFNCombine {
public:
    __aicore__ inline DispatchFFNCombine() {};
    
    __aicore__ inline void Init(
        GM_ADDR xGM, GM_ADDR weight1GM, GM_ADDR weight2GM,
        GM_ADDR expertIdGM, GM_ADDR scale1GM, GM_ADDR scale2GM,
        GM_ADDR probs, GM_ADDR xActiveMaskGM,
        GM_ADDR outGM, GM_ADDR expertTokenNums,
        GM_ADDR workspaceGM, GM_ADDR tilingGM
    );
    
    __aicore__ inline void Process();

private:
    // GM addresses
    GM_ADDR xGM_;
    GM_ADDR weight1GM_;
    GM_ADDR weight2GM_;
    GM_ADDR expertIdGM_;
    GM_ADDR outGM_;
    
    // Tiling parameters
    int32_t m, k, n;           // Matrix dimensions
    int32_t topK;              // Top-K value
    int32_t EP;                // Expert parallelism
    int32_t expertPerRank;     // Experts per rank
    int32_t maxOutputSize;
    
    // Block tiling
    int32_t m0, k0, n0;
    int32_t aivNum;
};
```

## Tiling Pattern (op_host/xxx_tiling.cpp)

Tiling determines how work is partitioned across AI cores:

```cpp
// Key tiling parameters:
// - m0, k0, n0: Block sizes for matrix multiplication
// - aivNum: Number of AI vector cores
// - Split strategy for multi-core execution
```

## Python Binding Registration (torch_binding.cpp)

```cpp
// In library initialization
TORCH_LIBRARY_FRAGMENT(vllm_ascend, ops) {
    // Define operator signature
    ops.def(
        "dispatch_ffn_combine(Tensor x, Tensor[] weight1, Tensor[] weight2, "
        "Tensor expert_idx, Tensor[] scale1, Tensor[] scale2, "
        "Tensor[]? bias1, Tensor[]? bias2, Tensor probs, str group, "
        "int max_output_size, Tensor! out, Tensor! expert_token_nums, "
        "Tensor? x_active_mask=None) -> (Tensor out, Tensor expert_token_nums)"
    );
    
    // Register implementation for NPU device
    ops.impl("dispatch_ffn_combine", torch::kPrivateUse1, 
             &vllm_ascend::dispatch_ffn_combine);
}
```

## Python Wrapper (vllm_ascend/ops/*.py)

```python
import torch

def dispatch_ffn_combine(
    x: torch.Tensor,
    weight1: list[torch.Tensor],
    weight2: list[torch.Tensor],
    expert_idx: torch.Tensor,
    ...
) -> tuple[torch.Tensor, torch.Tensor]:
    return torch.ops.vllm_ascend.dispatch_ffn_combine(
        x, weight1, weight2, expert_idx, ...
    )
```

## Build System (CMakeLists.txt)

```cmake
# Add operator library
add_library(dispatch_ffn_combine SHARED
    op_kernel/dispatch_ffn_combine.cpp
    op_host/dispatch_ffn_combine_def.cpp
    op_host/dispatch_ffn_combine_proto.cpp
    op_host/dispatch_ffn_combine_tiling.cpp
)

# Link dependencies
target_link_libraries(dispatch_ffn_combine
    ascendcl
    acl_op_api
    ${TORCH_LIBRARIES}
)
```

## Development Workflow

### 1. Create Operator Structure

```bash
mkdir -p csrc/my_op/op_host csrc/my_op/op_kernel
```

### 2. Implement Components

1. `op_host/my_op_def.cpp` - Operator definition
2. `op_host/my_op_proto.cpp` - Prototype
3. `op_host/my_op_tiling.cpp` - Tiling strategy
4. `op_kernel/my_op.cpp` - Kernel entry
5. `op_kernel/my_op.h` - Kernel class
6. `op_kernel/my_op_kernel.hpp` - Compute logic

### 3. Add Torch Adapter

```cpp
// csrc/my_op/my_op_torch_adpt.h
namespace vllm_ascend {
at::Tensor my_op(const at::Tensor& input, ...) {
    EXEC_NPU_CMD(aclnnMyOp, input, ...);
    return output;
}
}
```

### 4. Register in torch_binding.cpp

```cpp
ops.def("my_op(Tensor input, ...) -> Tensor");
ops.impl("my_op", torch::kPrivateUse1, &vllm_ascend::my_op);
```

### 5. Build

```bash
cd csrc
bash build.sh
```

### 6. Test

```python
# tests/ut/ops/test_my_op.py
import torch
import torch_npu

def test_my_op():
    x = torch.randn(10, 64, device="npu")
    out = torch.ops.vllm_ascend.my_op(x)
    assert out.shape == expected_shape
```

## Common Patterns

### NZ Format Handling

```cpp
// Weights often need NZ format for optimal performance
this->Input("weight")
    .Format({ge::FORMAT_FRACTAL_NZ});
```

### Optional Input Handling

```cpp
// In adapter
const at::Tensor& mask_value = mask.has_value() ? mask.value() : at::Tensor();

// In definition
this->Input("maskOptional")
    .ParamType(OPTIONAL);
```

### Dynamic Input (Tensor List)

```cpp
// In definition
this->Input("weights")
    .ParamType(DYNAMIC)
    .IgnoreContiguous();

// In adapter signature
const at::TensorList& weights
```

### MC2 Communication

```cpp
// For distributed operators
this->MC2().HcclGroup("group");

// In adapter
char *group_ptr = const_cast<char *>(group.data());
```

## Hardware-Specific Configuration

```cpp
// Different configs for different hardware
OpAICoreConfig a3_config;
a3_config.DynamicCompileStaticFlag(true);

OpAICoreConfig a2_config;
a2_config.DynamicCompileStaticFlag(false);

this->AICore().AddConfig("ascend910_93", a3_config);  // A3
this->AICore().AddConfig("ascend910b", a2_config);    // A2
```

## Debugging

### Enable Operator Logging

```bash
export ASCEND_GLOBAL_LOG_LEVEL=INFO
export ASCEND_SLOG_PRINT_TO_STDOUT=1
```

### Check Operator Support

```python
# Check if operator is registered
import torch
print(torch.ops.vllm_ascend.__dict__)
```

### Profile Operator

```python
import torch_npu
with torch_npu.profiler.profile():
    output = torch.ops.vllm_ascend.my_op(input)
```
