# Ascend Hardware Configuration Reference

## Hardware Series

| Series | SOC_VERSION | NPU Count | Use Case |
|--------|-------------|-----------|----------|
| Atlas A2 | ascend910b1/b2/b3/b4 | 8 | Mainstream inference |
| Atlas A3 | ascend910_9391/9381/9372 | 16 | High performance |
| Atlas A5 | ascend950_* | - | Latest generation |
| Atlas 310P | ascend310p1/p3/p5 | - | Inference dedicated |

## Hardware-Specific Environment Variables

### A3 Series (Recommended)

```bash
# Unified memory address direct transmission (REQUIRED for A3)
export ASCEND_ENABLE_USE_FABRIC_MEM=1

# For HDK 25.5.0 <= version < 26.0.0
export ASCEND_BUFFER_POOL=4:8  # 4 buffers of 8MB each
```

### A2 Series

```bash
# RoCE direct transmission (REQUIRED for A2)
export HCCL_INTRA_ROCE_ENABLE=1
```

### Common Variables

```bash
# RDMA timeout: 4.096 μs * 2^timeout
export HCCL_RDMA_TIMEOUT=17

# Connection timeout (ms) - formula: ~500ms × total_decode_cards
export ASCEND_CONNECT_TIMEOUT=10000

# Transfer timeout (ms)
export ASCEND_TRANSFER_TIMEOUT=10000

# Hash synchronization for KV Pool
export PYTHONHASHSEED=0
```

## Hardware Verification

### Check NPU Status

```bash
npu-smi info
```

### Check Network Connectivity (A2)

```bash
for i in {0..7}; do hccn_tool -i $i -link -g; done
for i in {0..7}; do hccn_tool -i $i -net_health -g; done
```

### Check Network Connectivity (A3)

```bash
for i in {0..15}; do hccn_tool -i $i -link -g; done
for i in {0..15}; do hccn_tool -i $i -net_health -g; done
```

### Get NPU IP Addresses

```bash
# A2
for i in {0..7}; do hccn_tool -i $i -ip -g | grep ipaddr; done

# A3
for i in {0..15}; do hccn_tool -i $i -ip -g | grep ipaddr; done
```

## Docker Device Mapping

### A2 (8 NPUs)

```bash
docker run --device /dev/davinci0 \
           --device /dev/davinci1 \
           ... \
           --device /dev/davinci7 \
           --device /dev/davinci_manager \
           --device /dev/devmm_svm \
           --device /dev/hisi_hdc \
           ...
```

### A3 (16 NPUs)

```bash
docker run --device /dev/davinci0 \
           ... \
           --device /dev/davinci15 \
           --device /dev/davinci_manager \
           --device /dev/devmm_svm \
           --device /dev/hisi_hdc \
           ...
```

## SOC_VERSION for CPU-Only Build

When building without NPU access, set SOC_VERSION:

```bash
# Atlas A2
export SOC_VERSION=ascend910b1

# Atlas A3
export SOC_VERSION=ascend910_9391

# Atlas 300I
export SOC_VERSION=ascend310p1

# Atlas A5
export SOC_VERSION=ascend950_*
```

## Performance Tuning by Hardware

### A3 Specific

- More streams available → larger ACL graph batch size range
- Enable `HCCL_OP_EXPANSION_MODE=AIV` for better communication performance

### A2 Specific

- Limited streams → may need to reduce ACL graph capture sizes
- Use `HCCL_INTRA_ROCE_ENABLE=1` for RoCE optimization

### Memory Management

```bash
# Prevent memory fragmentation
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True

# Max split size (reduces fragmentation)
export VLLM_ASCEND_MAX_SPLIT_SIZE_MB=512
```
