# PD Disaggregation Debugging Guide

## Overview

PD (Prefill-Decode) disaggregation separates Prefill and Decode nodes for independent scaling. This architecture introduces specific failure modes.

## Common Issues

### 1. MC2 AlltoAll Deadlock

**Symptoms**:
- All ranks simultaneously stuck
- HCCL heartbeat detects STUCK state
- Deadlock in `group_name_*` MC2 AlltoAll
- No ERROR/OOM logs - silent hang
- AICore utilization drops to 0%

**Root Causes**:
1. **Scheduler Conflict**: BalanceScheduler + RecomputeScheduler enabled simultaneously
   - Fix: Add mutual exclusion check in `platform.py`
   
2. **MoE Communication Type Mismatch**: Different DP ranks use different communication methods
   - Some use `All2AllV`, others use `MC2`
   - Check `_EXTRA_CTX.moe_comm_type` consistency across ranks

**Debugging Steps**:
1. Check HCCL plog for stuck communication group
2. Identify communication type: `RunAlltoAllDirectFullmesh_device` = MC2 AlltoAll
3. Check environment variables: `VLLM_ASCEND_BALANCE_SCHEDULING`, `recompute_scheduler_enable`
4. Verify all DP ranks have same MoE communication configuration

### 2. KV Transfer Timeout

**Symptoms**:
- P node blocks waiting for KV cache transfer
- D node not receiving KV blocks

**Debugging**:
1. Check Mooncake connector logs
2. Verify network connectivity between P and D nodes
3. Check `kv_transfer_config` settings

### 3. TP/EP Mismatch

**Symptoms**:
- Dimension mismatch errors in MoE operations
- Different tensor shapes across ranks

**Debugging**:
1. Verify `pd_tp_ratio` and `pd_head_ratio` settings
2. Check expert parallel configuration
3. Ensure consistent TP/EP across P and D nodes

## Configuration Validation

Key checks in `platform.py`:

```python
# BalanceScheduler only for PD-mixed mode
if VLLM_ASCEND_BALANCE_SCHEDULING and kv_role != "kv_both":
    raise ValueError(...)

# RecomputeScheduler only for PD-disaggregated mode  
if recompute_scheduler_enable and (kv_transfer_config is None or kv_role == "kv_both"):
    raise ValueError(...)

# Mutual exclusion
if VLLM_ASCEND_BALANCE_SCHEDULING and recompute_scheduler_enable:
    raise ValueError(...)
```

## Useful Commands

```bash
# Check HCCL status
grep -r "STUCK" /var/log/hccl/

# Check MoE communication type
grep "moe_comm_type" vllm_logs.txt

# Monitor AICore utilization
npu-smi info -t board
```

## Related Issues

- #8975: PD disaggregation deadlock (BalanceScheduler + RecomputeScheduler conflict)
- #8808: KV pool blocking in P node
