---
title: Hardware and limitations
description: NVIDIA CMP 100-210 / CMP 100HX-210 compute units, tensor and FP64 throughput, PCIe restrictions, and measured comparison with a V100-reporting configuration.
---

# Hardware and limitations

The **NVIDIA CMP 100-210**, also known as **CMP 100HX-210**, uses GV100 silicon and reports CUDA compute capability **7.0 (SM70)**. Its HBM2 capacity and bandwidth make it useful for inference, but the GV100 name does not imply V100-level compute throughput or connectivity.

## What was taken away

The following resource and performance differences were observed in a September 7, 2026 hardware comparison. They describe tested configurations; they do not identify the hardware or firmware mechanism responsible for each restriction.

<div class="grid cards" markdown>

-   :material-chip:{ .lg .middle } **Fewer usable compute units**

    ---

    All nine native CMP cards enumerated reported **4,352 CUDA cores**, compared with **5,120** in the V100-reporting configuration. Kernels executed on **68 distinct SMs** in the tested native CMP and **80 SMs** in the comparison configuration. That is 12 fewer executing SMs, not merely a different product name. Exact physical tensor-core counts were not measured.

-   :material-calculator:{ .lg .middle } **Severely reduced tensor throughput**

    ---

    Direct FP16 tensor operations with FP32 accumulation reached **4.99 TFLOPS** on native CMP versus **98.71 TFLOPS** in the V100-reporting configuration, a **19.8x** difference in this probe. Both produced correct output. Tensor operations execute on CMP, but their usable throughput is far below what the silicon's ancestry might suggest. This is a throughput measurement, not a universal instruction-latency ratio.

-   :material-calculator-variant:{ .lg .middle } **Severely reduced FP64 throughput**

    ---

    FP64 matrix multiplication reached **0.354 TFLOPS** versus **5.68 TFLOPS**, about a **16x** difference. A separate direct double-precision FMA probe showed the same large deficit. FP32 was much closer, so treating all arithmetic as equally restricted would be misleading.

-   :material-transit-connection-variant:{ .lg .middle } **PCIe Gen1, one lane**

    ---

    Native cards negotiated **Gen1 x1**, with roughly 250 MB/s per direction before transaction overhead. Measured pinned-memory transfers reached about **200 MB/s to the GPU** and **209 MB/s back**, compared with **13.17 GB/s** and **12.50 GB/s** over Gen3 x16 in the comparison configuration. Model loading, offloading and host-staged card boundaries pay this cost.

-   :material-memory:{ .lg .middle } **Lower memory clock**

    ---

    Native cards reported **810 MHz** memory clocks versus **877 MHz** in the comparison configuration. Both exposed approximately **16 GB** and a **4,096-bit** memory bus. High on-card bandwidth remains a strength, but memory specifications alone do not describe compute performance.

-   :material-chart-timeline-variant-shimmer:{ .lg .middle } **No supported CUPTI profiling**

    ---

    NVIDIA explicitly excludes CMP from CUPTI support. Nsight CUDA profiling was rejected on the native CMP configuration. CUDA events and other instrumentation can still provide measurements; unavailable CUPTI support does not mean all observation is impossible. See [NVIDIA's CUPTI result codes](https://docs.nvidia.com/cupti/api/group__CUPTI__RESULT__API.html).

-   :material-monitor-off:{ .lg .middle } **No display outputs**

    ---

    The cards are headless. NVIDIA describes removal of display outputs as a CMP design choice. This does not by itself establish that every graphics or video-processing engine is absent. See [NVIDIA's CMP announcement](https://blogs.nvidia.cn/blog/geforce-cmp/).

</div>

## Measured compute and transfer comparison

**V100 below means the tested V100-reporting configuration. These are configuration measurements, not factory V100 specifications or a same-board before/after experiment.** Compute measurements used one native CMP and one comparison device. Only the reported CUDA-core inventory covered all nine native CMP cards.

| Measurement | Native CMP 100-210 | V100 (reported identity) |
| --- | ---: | ---: |
| CUDA cores reported | 4,352 | 5,120 |
| Distinct SMs observed executing kernels | 68 | 80 |
| Direct WMMA, FP16 inputs / FP32 accumulation | 4.985 TFLOPS | 98.710 TFLOPS |
| FP16 matrix multiplication, FP32 output | 5.610 TFLOPS | 64.460 TFLOPS |
| FP32 matrix multiplication | 10.890 TFLOPS | 12.094 TFLOPS |
| FP64 matrix multiplication | 0.3543 TFLOPS | 5.680 TFLOPS |
| Direct FP32 FMA | 11.785 TFLOPS | 12.551 TFLOPS |
| Direct FP64 FMA | 0.3761 TFLOPS | 6.303 TFLOPS |
| Pinned host memory to GPU | 0.19974 GB/s | 13.172 GB/s |
| GPU to pinned host memory | 0.20890 GB/s | 12.502 GB/s |
| Device-to-device copy, payload bytes | 366.123 GB/s | 403.713 GB/s |
| Memory clock | 810 MHz | 877 MHz |
| Negotiated PCIe link | Gen1 x1 | Gen3 x16 |

### Method and limits

Timings are medians of three repetitions using the same compiled SM70 probe on both configurations, CUDA 12.9.2, cuBLAS 12.9.2 and driver 575.57.08. Clocks were not changed; short tests include boost transitions, so these are not clock-normalized peak ratings. One-second telemetry cannot establish identical clocks for every kernel.

The table's matrix tests used 2,048 x 2,048 matrices; 1,024 x 1,024 cases were also checked. Each timed repetition contained five matrix multiplications after warmup. Constant inputs had exactly representable expected outputs, and every output element matched. FP32 used pedantic compute mode. Direct WMMA used four accumulators per warp, 2,000 iterations, four warps per block and four blocks per SM; all outputs matched, and disassembly confirmed HMMA instructions. These checks demonstrate the tested operations, not general model correctness.

Direct scalar probes used eight FMA chains and 20,000 iterations. Disassembly confirmed FFMA and DFMA, but scalar output validation was limited to finite, positive values. Transfers used 64 MiB buffers and verified all copied bytes. Device-copy bandwidth counts payload once; reading and writing that payload creates roughly twice as much HBM traffic. Do not compare that column directly with a memory-bandwidth specification.

Both configurations report the same 6 MiB L2 cache, 96 KiB shared memory and 65,536 registers per SM, and a maximum SM clock of 1,380 MHz. Both advertise an FP32-to-FP64 performance ratio of 2 despite the measured native FP64 deficit. Capability fields are not throughput measurements. Conflicting ECC reports prevent a claim about functional ECC differences.

## Other limits of the tested system

**No usable peer route or NVLink connection was observed.** The P2P read matrix reports **chipset not supported** between every pair, including pairs involving the V100-reporting device. This establishes a limitation of the tested host, not a proven CMP-only restriction. Cross-card transfers in this configuration stage through host memory.

## What this means for llama.cpp

Both compute and transport matter. Reduced tensor throughput makes kernel selection important during prompt processing; the narrow PCIe link affects startup, offloading and multi-card boundaries. The dominant cost depends on model, quantization, context length, batch size and device split. A faster isolated kernel does not automatically produce a faster request.

| Cost to investigate | Relevant patch |
| --- | --- |
| Unsuitable quantized matrix routing on SM70 | [DP4A MMQ routing](patches/mmq-dp4a-routing.md) and [Q4_K / Q5_K coverage](patches/mmq-dp4a-q4k-q5k.md) |
| Serial per-GPU model upload | [Parallel model load](patches/parallel-model-load.md) |
| Host-staged card boundaries | [Mapped pinned host bridge](patches/mapped-host-bridge.md) |
| Prompt graph submission | [Prompt graph capture seed](patches/prompt-graph-capture-seed.md) |
| Repeated mask uploads | [Device-side mask expansion](patches/device-side-mask-expansion.md) |
| D256 attention work | [Accepted shared-query investigation](results/2026-09-07-sm70-d256-shared-q.md) |

Use an SM70-capable toolchain. The project's binary configuration targets native `70-real` cubins without PTX fallback. That is a build choice, not an additional hardware feature removed from CMP.

Hardware comparison numbers are diagnostic evidence, not patch speedups or promises for other cards. See the [accepted results](results/index.md) for measured application behavior and tradeoffs.
