---
title: Benchmarks
description: Verified measurements accompanying permanently promoted patches.
publication: accepted
data:
  - current-stock.json
  - baseline-baseline-20260905.csv
  - single-card-mmq-current-20260723.csv
---

# Benchmarks

The [current complete-series chart](index.md#complete-fork-versus-stock) is generated from the latest direct stock comparison and includes copyable commands. The measurements below are the **historical seven-patch baseline**, retained as evidence of the earlier configurations. They are separate experiments with different models and harnesses: the one-card result does not predict six-card scaling, and the six-card result does not describe a small model on one card.

## Historical seven-patch comparison

<div class="cmp-benchmark-chart" role="figure" aria-labelledby="cmp-benchmark-chart-title" aria-describedby="cmp-benchmark-chart-note">
  <div class="cmp-benchmark-chart__heading">
    <p id="cmp-benchmark-chart-title" class="cmp-benchmark-chart__title">Prompt processing throughput vs stock</p>
    <p class="cmp-benchmark-chart__subtitle">Matched A/B within each row; stock = 1.00x. Bar scale ends at 3.20x.</p>
  </div>
  <div class="cmp-benchmark-chart__group">
    <div class="cmp-benchmark-chart__context">
      <strong>1 card / 8K</strong>
      <span>Qwen3.5 9B Q4_K_XL</span>
    </div>
    <div class="cmp-benchmark-chart__bars">
      <div class="cmp-benchmark-bar cmp-benchmark-bar--stock" style="--cmp-bar-size: 31.25%"><span>Stock</span><b>1.000x</b><small>352.61 tok/s</small></div>
      <div class="cmp-benchmark-bar cmp-benchmark-bar--fork" style="--cmp-bar-size: 96.38%"><span>llama-cmpv</span><b>3.084x</b><small>1,087.33 tok/s</small></div>
    </div>
  </div>
  <div class="cmp-benchmark-chart__group cmp-benchmark-chart__group--six">
    <div class="cmp-benchmark-chart__context">
      <strong>6 cards / 8K</strong>
      <span>Qwen3.8 Flash Next UD-IQ4_XS</span>
    </div>
    <div class="cmp-benchmark-chart__bars">
      <div class="cmp-benchmark-bar cmp-benchmark-bar--stock" style="--cmp-bar-size: 31.25%"><span>Stock</span><b>1.000x</b><small>108.98 tok/s</small></div>
      <div class="cmp-benchmark-bar cmp-benchmark-bar--fork" style="--cmp-bar-size: 64.19%"><span>llama-cmpv</span><b>2.054x</b><small>223.80 tok/s</small></div>
    </div>
  </div>
  <div class="cmp-benchmark-chart__group cmp-benchmark-chart__group--six">
    <div class="cmp-benchmark-chart__context">
      <strong>6 cards / 32K</strong>
      <span>Qwen3.8 Flash Next UD-IQ4_XS</span>
    </div>
    <div class="cmp-benchmark-chart__bars">
      <div class="cmp-benchmark-bar cmp-benchmark-bar--stock" style="--cmp-bar-size: 31.25%"><span>Stock</span><b>1.000x</b><small>92.37 tok/s</small></div>
      <div class="cmp-benchmark-bar cmp-benchmark-bar--fork" style="--cmp-bar-size: 68.00%"><span>llama-cmpv</span><b>2.176x</b><small>200.96 tok/s</small></div>
    </div>
  </div>
  <div class="cmp-benchmark-chart__group cmp-benchmark-chart__group--six">
    <div class="cmp-benchmark-chart__context">
      <strong>6 cards / 65K</strong>
      <span>Qwen3.8 Flash Next UD-IQ4_XS</span>
    </div>
    <div class="cmp-benchmark-chart__bars">
      <div class="cmp-benchmark-bar cmp-benchmark-bar--stock" style="--cmp-bar-size: 31.25%"><span>Stock</span><b>1.000x</b><small>74.79 tok/s</small></div>
      <div class="cmp-benchmark-bar cmp-benchmark-bar--fork" style="--cmp-bar-size: 69.44%"><span>llama-cmpv</span><b>2.222x</b><small>166.15 tok/s</small></div>
    </div>
  </div>
  <div class="cmp-benchmark-chart__group cmp-benchmark-chart__group--six">
    <div class="cmp-benchmark-chart__context">
      <strong>6 cards / 131K</strong>
      <span>Qwen3.8 Flash Next UD-IQ4_XS</span>
    </div>
    <div class="cmp-benchmark-chart__bars">
      <div class="cmp-benchmark-bar cmp-benchmark-bar--stock" style="--cmp-bar-size: 31.25%"><span>Stock</span><b>1.000x</b><small>54.09 tok/s</small></div>
      <div class="cmp-benchmark-bar cmp-benchmark-bar--fork" style="--cmp-bar-size: 70.69%"><span>llama-cmpv</span><b>2.262x</b><small>122.33 tok/s</small></div>
    </div>
  </div>
  <div class="cmp-benchmark-chart__group cmp-benchmark-chart__group--six">
    <div class="cmp-benchmark-chart__context">
      <strong>6 cards / 250K</strong>
      <span>Qwen3.8 Flash Next UD-IQ4_XS</span>
    </div>
    <div class="cmp-benchmark-chart__bars">
      <div class="cmp-benchmark-bar cmp-benchmark-bar--stock" style="--cmp-bar-size: 31.25%"><span>Stock</span><b>1.000x</b><small>35.65 tok/s</small></div>
      <div class="cmp-benchmark-bar cmp-benchmark-bar--fork" style="--cmp-bar-size: 71.28%"><span>llama-cmpv</span><b>2.281x</b><small>81.30 tok/s</small></div>
    </div>
  </div>
  <p id="cmp-benchmark-chart-note" class="cmp-benchmark-chart__note">Prompt processing only. The one-card and six-card tests used different models and harnesses; compare fork with stock within a row, not one row with another. Decode results are reported in the exact tables below.</p>
</div>

## One CMP 100-210

**Qwen3.5 9B Q4_K_XL, 8,192 prompt tokens, current-upstream same-binary policy A/B**

| Metric | Stock `auto` policy | llama-cmpv `force` policy | Change |
| --- | ---: | ---: | ---: |
| Prompt processing | 352.61 tok/s | 1,087.33 tok/s | **+208.37% (3.084x)** |
| Token generation | 61.70 tok/s | 61.64 tok/s | **-0.107%** |

The prefill gain comes from forcing the DP4A MMQ route at a shape where stock llama.cpp selected cuBLAS. It is not a 3.084x generation claim. Three repetitions covered each cell in the full prompt and micro-batch matrix; the maximum control coefficient of variation was 2.132%.

??? note "Model, build and complete benchmark flags"

    **Model:** Qwen3.5 9B Q4_K_XL

    **Hardware:** one native CMP 100-210, selected as `CUDA0`; maximum observed temperature 70 C

    **Build:** current-upstream artifact `c588c4f47683e73ad2d69f50480bec6cc85fd0f7`, native SM70

    **Prefill command flags:**

    ```text
    --model <Qwen3.5-9B-Q4_K_XL.gguf>
    --output json
    --progress
    --n-gpu-layers 999
    --split-mode layer
    --device CUDA0
    --flash-attn on
    --cuda-mmq auto|force
    --repetitions 3
    --n-prompt 8192
    --n-gen 0
    --batch-size 2048
    --ubatch-size 1024
    ```

    **Decode control flags:** the same common flags, with `--n-prompt 0 --n-gen 128 --batch-size 2048 --ubatch-size 512`.

    `CUDA_VISIBLE_DEVICES=0` restricted both arms to the same card. Only `--cuda-mmq auto` versus `--cuda-mmq force` changed within the current build. Model paths, device UUIDs and machine identities are intentionally excluded from the public record.

| model | devices | prompt tokens | batch size | ubatch size | metric | stock auto | fork force | change pct | repetitions | unit |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3.5 9B Q4_K_XL | 1 | 8192 | 2048 | 1024 | prompt throughput | 352.61 | 1087.33 | 208.37 | 3 | tokens/second |
| Qwen3.5 9B Q4_K_XL | 1 | 0 | 2048 | 512 | generation throughput | 61.70 | 61.64 | -0.107 | 3 | tokens/second |

[Download `single-card-mmq-current-20260723.csv`](data/single-card-mmq-current-20260723.csv){ .cmp-data-link download }

## Six CMP 100-210 cards

**Qwen3.8 Flash Next UD-IQ4_XS, layer split across six cards, 256 generated tokens**

| Prompt context | Prefill throughput | Prefill gain | TTFT | TTFT reduction | Decode throughput |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 8K | 108.98 -> 223.80 tok/s | **+105.4%** | 75.17 -> 36.60 s | **-51.3%** | 26.424 -> 26.295 tok/s |
| 32K | 92.37 -> 200.96 tok/s | **+117.6%** | 354.75 -> 163.05 s | **-54.0%** | 21.550 -> 21.634 tok/s |
| 65K | 74.79 -> 166.15 tok/s | **+122.2%** | 876.27 -> 394.43 s | **-55.0%** | 17.756 -> 17.922 tok/s |
| 131K | 54.09 -> 122.33 tok/s | **+126.2%** | 2,423.25 -> 1,071.47 s | **-55.8%** | 12.273 -> 13.044 tok/s |
| 250K | 35.65 -> 81.30 tok/s | **+128.1%** | 7,012.72 -> 3,075.13 s | **-56.1%** | 4.677 -> 5.041 tok/s |

The arrows show stock llama.cpp first and the seven-patch fork second. The main gain is prompt processing and time to first token. Decode ranges from -0.5% at 8K to +7.8% at 250K; the prefill percentage must not be quoted as generation speed.

??? note "Model, six-card layout and complete server flags"

    **Model:** Qwen3.8 Flash Next UD-IQ4_XS

    **Hardware:** six native CMP 100-210 cards in equal layer split, no usable P2P path

    **Requests:** 8,192 / 32,768 / 65,536 / 131,072 / 250,000 prompt tokens followed by exactly 256 generated tokens. Server contexts were pinned to 8,449 / 33,025 / 65,793 / 131,328 / 250,368 respectively.

    **Common server flags:**

    ```text
    --jinja
    --no-host
    --no-repack
    --load-mode mmap
    --lazy-mode auto
    --gpu-layers all
    --split-mode layer
    --batch-size 24576
    --ubatch-size 512
    --flash-attn on
    --cache-type-k f16
    --cache-type-v f16
    --no-context-shift
    --cuda-mmq force
    --backend-sampling
    --spec-type none
    --metrics
    --parallel 1
    ```

    **Fork selectors:** `GGML_CUDA_MAPPED_HOST_BRIDGE=1`, `GGML_CUDA_PROMPT_GRAPH_CAPTURE_SEED=1`, `GGML_SCHED_DEVICE_MASK=1`, and `LLAMA_MODEL_LOAD_PARALLEL=1`.

    The retained public table records the measured server contexts exactly; minor one-token context differences reflect the historical harness. Paths, ports, service names, GPU UUIDs and host identity are intentionally omitted.

??? info "Download the complete six-card measurements"

    | context | build | server ctx | prompt tok s | ttft s | decode tok s | tokens | markers ok |
    |---|---|---|---|---|---|---|---|
    | 8192 | stock | 8449 | 108.98 | 75.17 | 26.424 | 256 | yes |
    | 8192 | fork | 8449 | 223.80 | 36.60 | 26.295 | 256 | yes |
    | 32768 | stock | 33025 | 92.37 | 354.75 | 21.550 | 256 | yes |
    | 32768 | fork | 33025 | 200.96 | 163.05 | 21.634 | 256 | yes |
    | 65536 | stock | 65793 | 74.79 | 876.27 | 17.756 | 256 | yes |
    | 65536 | fork | 65793 | 166.15 | 394.43 | 17.922 | 256 | yes |
    | 131072 | stock | 131328 | 54.09 | 2423.25 | 12.273 | 256 | yes |
    | 131072 | fork | 131328 | 122.33 | 1071.47 | 13.044 | 256 | yes |
    | 250000 | stock | 250368 | 35.65 | 7012.72 | 4.677 | 256 | yes |
    | 250000 | fork | 250368 | 81.30 | 3075.13 | 5.041 | 256 | yes |

    [Download `baseline-baseline-20260905.csv`](data/baseline-baseline-20260905.csv){ .cmp-data-link download }

## Latest incremental patch

The later SM70 D256 shared-Q and unit-rescaling patch was measured against the already optimized six-card fork, not directly against stock. It reduced complete request time by 0.32% at 8K, 1.39% at 65K, 2.16% at 131K and 2.68% at 250K. Those byte-exact results were single saved-reference comparisons with uncontrolled drift; read the [full result and limitations](2026-09-07-sm70-d256-shared-q.md).

## Publication policy

The public portal publishes measurements only when a patch is permanently adopted. Ongoing, undecided and declined experiments stay in the private research record. A running test never appends to a published measurement file.

Each entry in the [promoted patch timeline](index.md) links its verified CSV and source patch. CSVs record the model label, device count, prompt and server contexts, exact output count, absolute reference and candidate measurements, and signed percentage changes. Negative duration changes mean faster execution; positive throughput changes mean faster execution.

Read the full result before treating a number as an improvement. Entries retain regressions, output checks, sampling limits and whether runtime activation was established. A human can accept a small or uncertain gain without claiming statistical significance. Saved-reference comparisons do not eliminate thermal or runtime drift.

The [method](../method.md) describes the evidence requirements. Only derived, reviewed measurements are public. Prompts, model responses, target identities, machine paths and raw per-card records remain private.
