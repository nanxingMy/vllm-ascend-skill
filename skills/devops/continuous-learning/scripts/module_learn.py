#!/usr/bin/env python3
"""
vLLM-Ascend 分模块学习系统

学习模块：
1. 架构概览 (Monday)
2. 核心组件 (Tuesday)
3. 平台适配 (Wednesday)
4. 算子实现 (Thursday)
5. 分布式系统 (Friday)
6. 测试体系 (Saturday)
7. 最佳实践 (Sunday)
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 配置
VLLM_ASCEND_DIR = Path("C:/Users/HuaWei/vllm-ascend")
SKILL_DIR = Path("C:/Users/HuaWei/vllm-ascend-skill/skill/references")
LEARN_DIR = SKILL_DIR / "learned"
GIT_USER = "nanxingMy"
GIT_EMAIL = "1014662416@qq.com"

# 确保学习目录存在
LEARN_DIR.mkdir(parents=True, exist_ok=True)

class ModuleLearner:
    """模块学习器"""
    
    def __init__(self, module_name):
        self.module_name = module_name
        self.content = []
        
    def add_section(self, title, content):
        """添加章节"""
        self.content.append(f"\n## {title}\n\n{content}\n")
    
    def add_code_example(self, title, code, explanation):
        """添加代码示例"""
        self.content.append(f"\n### {title}\n\n```python\n{code}\n```\n\n**说明**: {explanation}\n")
    
    def generate_doc(self):
        """生成文档"""
        return f"""# {self.module_name}

> 学习时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{''.join(self.content)}
"""

def learn_architecture():
    """学习架构概览"""
    print("学习模块 1: 架构概览")
    
    learner = ModuleLearner("vLLM-Ascend 架构概览")
    
    # 1. 项目简介
    learner.add_section("项目简介", """
vLLM-Ascend 是 vLLM 在华为 NPU 平台上的适配实现。

**核心目标**:
- 在华为 NPU 上高效运行大语言模型
- 提供与 vLLM 一致的 API 接口
- 优化 NPU 特有的性能

**主要特性**:
- 支持多种模型架构
- 自动平台检测和适配
- 高效的内存管理
- 分布式推理支持
""")
    
    # 2. 目录结构
    learner.add_section("目录结构", """
```
vllm-ascend/
├── vllm_ascend/          # 核心代码
│   ├── worker/           # 工作进程
│   ├── platform/         # 平台适配
│   ├── attention/        # 注意力机制
│   ├── ops/              # 算子实现
│   ├── distributed/      # 分布式
│   ├── patch/            # 补丁
│   └── quantization/     # 量化
├── tests/                # 测试
│   ├── ut/               # 单元测试
│   └── e2e/              # 端到端测试
├── docs/                 # 文档
└── csrc/                 # C++ 源码
```
""")
    
    # 3. 核心模块
    learner.add_section("核心模块", """
| 模块 | 功能 | 关键文件 |
|------|------|---------|
| worker | 工作进程管理 | worker.py |
| platform | 平台适配 | platform.py |
| attention | 注意力机制 | sfa_v1.py |
| ops | 算子实现 | fused_moe.py |
| distributed | 分布式系统 | parallel_state.py |
""")
    
    # 4. 数据流
    learner.add_section("数据流", """
```
用户请求
    ↓
NPUWorker (工作进程)
    ↓
NPUModelRunner (模型运行器)
    ↓
Platform (平台适配)
    ↓
Attention/Ops (算子执行)
    ↓
NPU (硬件执行)
```
""")
    
    return learner.generate_doc()

def learn_core_components():
    """学习核心组件"""
    print("学习模块 2: 核心组件")
    
    learner = ModuleLearner("vLLM-Ascend 核心组件")
    
    # 1. NPUWorker
    learner.add_section("NPUWorker", """
**职责**: 管理单个 NPU 设备上的模型执行

**关键方法**:
- `init_model()`: 初始化模型
- `execute_model()`: 执行模型推理
- `shutdown()`: 关闭工作进程

**代码示例**:
```python
class NPUWorker:
    def init_model(self):
        # 初始化模型运行器
        self.model_runner = NPUModelRunner(...)
        
    def execute_model(self, execute_model_req):
        # 执行模型
        output = self.model_runner.execute_model(...)
        return output
```
""")
    
    # 2. NPUModelRunner
    learner.add_section("NPUModelRunner", """
**职责**: 执行模型的前向传播

**关键组件**:
- 模型加载和初始化
- 输入数据处理
- 输出结果处理
- 内存管理

**执行流程**:
```
1. 接收请求
2. 准备输入
3. 执行前向传播
4. 处理输出
5. 返回结果
```
""")
    
    # 3. Platform
    learner.add_section("Platform", """
**职责**: 平台检测和适配

**平台类型**:
- NPUPlatform: NPU 平台
- NPUPlatform310P: 310P 设备
- NPUPlatform910B: 910B 设备

**关键方法**:
```python
class NPUPlatform:
    @staticmethod
    def get_device_name() -> str:
        # 获取设备名称
        
    @staticmethod
    def is_device_available() -> bool:
        # 检查设备是否可用
```
""")
    
    return learner.generate_doc()

def learn_platform_adaptation():
    """学习平台适配"""
    print("学习模块 3: 平台适配")
    
    learner = ModuleLearner("vLLM-Ascend 平台适配")
    
    # 1. 平台检测
    learner.add_section("平台检测", """
**自动检测流程**:
```python
def detect_platform():
    if is_npu_available():
        device_name = get_npu_device_name()
        if device_name == "Ascend910B":
            return NPUPlatform910B()
        elif device_name == "Ascend310P":
            return NPUPlatform310P()
        else:
            return NPUPlatform()
    else:
        raise RuntimeError("NPU not available")
```
""")
    
    # 2. 设备特性
    learner.add_section("设备特性", """
| 设备 | 特性 | 内存 | 算力 |
|------|------|------|------|
| 910B | 高性能训练推理 | 32GB | 256 TOPS |
| 310P | 推理优化 | 8GB | 88 TOPS |

**关键差异**:
- 内存容量
- 算力大小
- 支持的算子
- 优化策略
""")
    
    # 3. 平台配置
    learner.add_section("平台配置", """
**配置项**:
```python
# ascend_config.py
class AscendConfig:
    # 设备配置
    device_type: str = "npu"
    device_name: str = "Ascend910B"
    
    # 内存配置
    memory_utilization: float = 0.9
    
    # 性能配置
    enable_expert_parallel: bool = False
```
""")
    
    return learner.generate_doc()

def learn_operators():
    """学习算子实现"""
    print("学习模块 4: 算子实现")
    
    learner = ModuleLearner("vLLM-Ascend 算子实现")
    
    # 1. 注意力算子
    learner.add_section("注意力算子", """
**类型**:
- SFA (Scaled Flash Attention)
- Paged Attention
- Multi-Query Attention

**实现**:
```python
# sfa_v1.py
class SFAV1:
    def forward(self, query, key, value):
        # 实现 Flash Attention
        output = flash_attention(query, key, value)
        return output
```
""")
    
    # 2. MoE 算子
    learner.add_section("MoE 算子", """
**MoE (Mixture of Experts)**:
```python
# fused_moe.py
def fused_moe(
    hidden_states,
    gate_logits,
    experts,
    ...
):
    # 1. 路由计算
    topk_weights, topk_ids = torch.topk(gate_logits, k)
    
    # 2. 专家计算
    expert_outputs = []
    for expert_id in topk_ids:
        output = experts[expert_id](hidden_states)
        expert_outputs.append(output)
    
    # 3. 结果聚合
    output = sum(w * o for w, o in zip(topk_weights, expert_outputs))
    return output
```
""")
    
    # 3. 量化算子
    learner.add_section("量化算子", """
**支持的量化方法**:
- W8A8: 8-bit 权重和激活
- W4A8: 4-bit 权重，8-bit 激活
- INT8: 整数量化

**实现**:
```python
# w8a8_dynamic.py
class W8A8DynamicLinear:
    def forward(self, x):
        # 动态量化
        x_quant = self.quantize(x)
        # 量化矩阵乘法
        output = self.quant_matmul(x_quant, self.weight)
        # 反量化
        output = self.dequantize(output)
        return output
```
""")
    
    return learner.generate_doc()

def learn_distributed():
    """学习分布式系统"""
    print("学习模块 5: 分布式系统")
    
    learner = ModuleLearner("vLLM-Ascend 分布式系统")
    
    # 1. 并行策略
    learner.add_section("并行策略", """
**支持的并行方式**:
- 数据并行 (DP)
- 张量并行 (TP)
- 流水线并行 (PP)
- 专家并行 (EP)

**配置**:
```python
# 并行配置
parallel_config = ParallelConfig(
    tensor_parallel_size=2,
    pipeline_parallel_size=1,
    expert_parallel_size=1,
)
```
""")
    
    # 2. 通信
    learner.add_section("通信机制", """
**通信原语**:
- AllReduce: 梯度聚合
- AllGather: 数据收集
- ReduceScatter: 数据分发

**实现**:
```python
# parallel_state.py
def tensor_parallel_all_reduce(input):
    # 张量并行的 AllReduce
    output = torch.distributed.all_reduce(input)
    return output
```
""")
    
    # 3. KV 传输
    learner.add_section("KV 传输", """
**KV Cache 传输**:
```python
# kv_transfer.py
class KVTransfer:
    def send_kv_cache(self, kv_cache):
        # 发送 KV Cache 到其他节点
        
    def recv_kv_cache(self):
        # 接收 KV Cache 从其他节点
```
""")
    
    return learner.generate_doc()

def learn_testing():
    """学习测试体系"""
    print("学习模块 6: 测试体系")
    
    learner = ModuleLearner("vLLM-Ascend 测试体系")
    
    # 1. 单元测试
    learner.add_section("单元测试", """
**测试框架**: pytest

**测试类型**:
- 算子测试
- 模型测试
- 平台测试
- 配置测试

**示例**:
```python
# test_platform.py
def test_platform_detection():
    platform = detect_platform()
    assert platform is not None
    assert platform.is_device_available()
```
""")
    
    # 2. 端到端测试
    learner.add_section("端到端测试", """
**测试流程**:
```
1. 启动服务
2. 发送请求
3. 验证响应
4. 清理资源
```

**示例**:
```python
# test_model_inference.py
def test_llama_inference():
    # 启动服务
    server = start_server()
    
    # 发送请求
    response = server.generate("Hello, world!")
    
    # 验证
    assert len(response) > 0
    
    # 清理
    server.shutdown()
```
""")
    
    # 3. 性能测试
    learner.add_section("性能测试", """
**测试指标**:
- 吞吐量 (tokens/s)
- 延迟 (ms)
- 内存使用 (GB)
- GPU 利用率 (%)

**基准测试**:
```python
def benchmark_throughput():
    # 测试吞吐量
    start_time = time.time()
    for _ in range(1000):
        model.generate(prompt)
    end_time = time.time()
    
    throughput = 1000 / (end_time - start_time)
    return throughput
```
""")
    
    return learner.generate_doc()

def learn_best_practices():
    """学习最佳实践"""
    print("学习模块 7: 最佳实践")
    
    learner = ModuleLearner("vLLM-Ascend 最佳实践")
    
    # 1. 代码风格
    learner.add_section("代码风格", """
**Python 风格**:
- 遵循 PEP 8
- 使用类型注解
- 编写文档字符串

**示例**:
```python
def execute_model(
    self,
    request: ExecuteModelRequest,
) -> List[SamplerOutput]:
    \"\"\"执行模型推理。
    
    Args:
        request: 执行请求
        
    Returns:
        采样输出列表
    \"\"\"
    ...
```
""")
    
    # 2. 错误处理
    learner.add_section("错误处理", """
**使用 ValueError 而非 assert**:
```python
# ❌ 错误
assert condition, "error message"

# ✅ 正确
if not condition:
    raise ValueError("error message")
```

**日志记录**:
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Starting model execution")
logger.error(f"Failed to load model: {e}")
```
""")
    
    # 3. 性能优化
    learner.add_section("性能优化", """
**内存优化**:
- 使用 KV Cache
- 实现增量计算
- 优化内存布局

**计算优化**:
- 算子融合
- 使用 NPU 特有指令
- 减少数据传输

**示例**:
```python
# 算子融合
@torch.jit.script
def fused_attention(q, k, v):
    # 单个算子完成多个操作
    return flash_attention(q, k, v)
```
""")
    
    return learner.generate_doc()

def get_current_module():
    """获取当前应该学习的模块"""
    # 根据星期几决定学习哪个模块
    weekday = datetime.now().weekday()  # 0=Monday, 6=Sunday
    
    modules = [
        ("01-architecture", learn_architecture),
        ("02-core-components", learn_core_components),
        ("03-platform-adaptation", learn_platform_adaptation),
        ("04-operators", learn_operators),
        ("05-distributed", learn_distributed),
        ("06-testing", learn_testing),
        ("07-best-practices", learn_best_practices),
    ]
    
    return modules[weekday]

def save_module_doc(module_name, doc):
    """保存模块文档"""
    doc_file = LEARN_DIR / f"{module_name}.md"
    doc_file.write_text(doc, encoding='utf-8')
    print(f"  已保存: {doc_file}")

def git_commit_and_push():
    """提交并推送"""
    import subprocess
    
    os.chdir(SKILL_DIR.parent.parent)
    
    subprocess.run(['git', 'config', 'user.name', GIT_USER], check=True)
    subprocess.run(['git', 'config', 'user.email', GIT_EMAIL], check=True)
    subprocess.run(['git', 'add', 'skill/references/learned/'], check=True)
    
    commit_msg = f"[Learn] {datetime.now().strftime('%Y-%m-%d')} - Module learning"
    subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
    subprocess.run(['git', 'push', 'origin', 'main'], check=True)

def main():
    """主函数"""
    print(f"\n{'='*70}")
    print(f"vLLM-Ascend 分模块学习 - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*70}\n")
    
    # 获取当前模块
    module_name, learn_func = get_current_module()
    
    print(f"今日学习模块: {module_name}\n")
    
    # 学习模块
    doc = learn_func()
    
    # 保存文档
    save_module_doc(module_name, doc)
    
    # 提交推送
    print("\n提交并推送...")
    git_commit_and_push()
    
    print(f"\n{'='*70}")
    print("学习完成！")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
