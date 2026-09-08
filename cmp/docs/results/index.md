---
title: Promoted patches
description: Verified measurements for permanently adopted patches.
---

# Promoted patches

Only permanently adopted patches appear here. Each entry links its source patch and measured data, including regressions and validation limits. Human acceptance does not imply statistical significance.

The [benchmark guide](benchmarks.md) explains the linked measurements. The [machine-readable index](index.json) contains the same promoted entries.

Inherited entries retain the date recorded in their original patch headers. Entries that share that date follow their preserved application order in the public patch series.

<!-- BEGIN GENERATED TIMELINE -->
<ol class="cmp-timeline">
<li class="cmp-entry cmp-verdict-kept">
  <div class="cmp-entry-when"><time datetime="2026-09-07">2026-09-07</time></div>
  <div class="cmp-entry-card">
    <p class="cmp-entry-head"><a href="2026-09-07-sm70-d256-shared-q/">SM70 D256 shared Q and unit rescaling preserve output through 250K</a><span class="cmp-pill cmp-pill-kept">kept</span></p>

    <p class="cmp-entry-summary">The combined shared-Q and unit-rescale patch was accepted after review of its gains, regressions and measurement limits. All four primary contexts preserved exact 256-token output. At 250K, observed request wall time was 2.677% lower than the original saved reference. These single samples do not establish statistical repeatability or native kernel attribution.</p>
    <dl class="cmp-entry-meta">
      <dt>headline</dt><dd>-2.676602% request wall time at 250K</dd>
      <dt>selectors</dt><dd>none</dd>
      <dt>contexts</dt><dd>8K, 64K, 128K, 250K</dd>
      <dt>output</dt><dd>byte-exact</dd>
      <dt>commit</dt><dd><code>4fe5ecd7536bad00fa4f589a293e9284d2086302</code></dd>
    </dl>
  </div>
</li>
<li class="cmp-entry cmp-verdict-kept">
  <div class="cmp-entry-when"><time datetime="2026-09-05">2026-09-05</time></div>
  <div class="cmp-entry-card">
    <p class="cmp-entry-head"><a href="../patches/mmq-dp4a-routing/">DP4A MMQ routing</a><span class="cmp-pill cmp-pill-kept">kept</span></p>

    <p class="cmp-entry-summary">Adds a selectable DP4A MMQ route for tested quantized SM70 prefill, where the automatic policy chose the generic FP16 tensor-core path. One matched six-card configuration measured 2.36x prefill throughput at 128K; this is not a decode claim.</p>
    <dl class="cmp-entry-meta">
      <dt>headline</dt><dd>2.36x matched prefill throughput at 128K</dd>
      <dt>selectors</dt><dd><code>--cuda-mmq force</code></dd>
      <dt>contexts</dt><dd>128K</dd>
      <dt>output</dt><dd>byte-exact</dd>
      <dt>commit</dt><dd><code>4e66a8481b33f41e8f25b64d083059c529a168a3</code></dd>
    </dl>
  </div>
</li>
<li class="cmp-entry cmp-verdict-kept">
  <div class="cmp-entry-when"><time datetime="2026-09-05">2026-09-05</time></div>
  <div class="cmp-entry-card">
    <p class="cmp-entry-head"><a href="../patches/mmq-dp4a-q4k-q5k/">Volta Q4_K and Q5_K DP4A</a><span class="cmp-pill cmp-pill-kept">kept</span></p>

    <p class="cmp-entry-summary">Extends the forced DP4A MMQ configuration to the Q4_K and Q5_K quantizations that SM70 previously left on the fallback path. The recorded effect was context-dependent: about 33.7% at a 4K prompt and 0.09% at an exact 100K prompt.</p>
    <dl class="cmp-entry-meta">
      <dt>headline</dt><dd>+33.7% at 4K; +0.09% at exact 100K</dd>
      <dt>selectors</dt><dd><code>--cuda-mmq force</code></dd>
      <dt>contexts</dt><dd>4K, 100K</dd>
      <dt>output</dt><dd>byte-exact</dd>
      <dt>commit</dt><dd><code>703d046c78b3ba7565f2605d54e7ba7f701afce6</code></dd>
    </dl>
  </div>
</li>
<li class="cmp-entry cmp-verdict-kept">
  <div class="cmp-entry-when"><time datetime="2026-09-05">2026-09-05</time></div>
  <div class="cmp-entry-card">
    <p class="cmp-entry-head"><a href="../patches/parallel-model-load/">Parallel model load</a><span class="cmp-pill cmp-pill-kept">kept</span></p>

    <p class="cmp-entry-summary">Overlaps independent per-GPU model uploads using positional reads instead of serially sharing one file offset. Matched cold-start controls were 51-59% faster; it is a readiness improvement, not token-generation throughput.</p>
    <dl class="cmp-entry-meta">
      <dt>headline</dt><dd>51-59% faster matched cold start</dd>
      <dt>selectors</dt><dd><code>LLAMA_MODEL_LOAD_PARALLEL=1</code></dd>
      <dt>contexts</dt><dd>cold start; no mmap, direct I/O, or tensor checking</dd>
      <dt>output</dt><dd>byte-exact</dd>
      <dt>commit</dt><dd><code>bc5cf34c680c898d2c7d9a974c848086df762024</code></dd>
    </dl>
  </div>
</li>
<li class="cmp-entry cmp-verdict-kept">
  <div class="cmp-entry-when"><time datetime="2026-09-05">2026-09-05</time></div>
  <div class="cmp-entry-card">
    <p class="cmp-entry-head"><a href="../patches/mapped-host-bridge/">Mapped pinned host bridge</a><span class="cmp-pill cmp-pill-kept">kept</span></p>

    <p class="cmp-entry-summary">Makes no-P2P CUDA handoffs explicit through scheduler-visible ownership and a fixed four-slot mapped-pinned staging bridge. Event-ordered reuse preserves lossless cross-card transfers for boundaries up to 64 MiB.</p>
    <dl class="cmp-entry-meta">
      <dt>headline</dt><dd>four lossless mapped-pinned staging slots</dd>
      <dt>selectors</dt><dd><code>GGML_CUDA_MAPPED_HOST_BRIDGE=1</code></dd>
      <dt>contexts</dt><dd>cross-card boundaries up to 64 MiB</dd>
      <dt>output</dt><dd>byte-exact</dd>
      <dt>commit</dt><dd><code>f9859b80a39c5a133612363538f8a343d7f4a447</code></dd>
    </dl>
  </div>
</li>
<li class="cmp-entry cmp-verdict-kept">
  <div class="cmp-entry-when"><time datetime="2026-09-05">2026-09-05</time></div>
  <div class="cmp-entry-card">
    <p class="cmp-entry-head"><a href="../patches/research-selectors/">Research selector registry</a><span class="cmp-pill cmp-pill-kept">kept</span></p>

    <p class="cmp-entry-summary">Adds runtime-switchable research selectors and activation reporting, so a configured selector whose implementation was dropped cannot silently appear enabled. The registry is infrastructure: it changes no behavior by itself.</p>
    <dl class="cmp-entry-meta">
      <dt>headline</dt><dd>selector reads are observable at runtime</dd>
      <dt>selectors</dt><dd>none; provides the selector mechanism</dd>
      <dt>contexts</dt><dd>runtime activation reporting</dd>
      <dt>output</dt><dd>unchanged by construction</dd>
      <dt>commit</dt><dd><code>e5e027c3fcf638749a39438e4d4e7c9e93a994ee</code></dd>
    </dl>
  </div>
</li>
<li class="cmp-entry cmp-verdict-kept">
  <div class="cmp-entry-when"><time datetime="2026-09-05">2026-09-05</time></div>
  <div class="cmp-entry-card">
    <p class="cmp-entry-head"><a href="../patches/prompt-graph-capture-seed/">Prompt graph capture seed</a><span class="cmp-pill cmp-pill-kept">kept</span></p>

    <p class="cmp-entry-summary">Captures and instantiates a prompt graph executable on first observation without launching it; only later matching observations replay it. This avoids replaying a mutable first observation from an unproven executable. Recorded throughput effects varied by model family, with a small batch-one decode cost.</p>
    <dl class="cmp-entry-meta">
      <dt>headline</dt><dd>model-dependent prompt-throughput gain</dd>
      <dt>selectors</dt><dd><code>GGML_CUDA_PROMPT_GRAPH_CAPTURE_SEED=1</code></dd>
      <dt>contexts</dt><dd>compatible prompt graphs; batch-one decode release</dd>
      <dt>output</dt><dd>byte-exact</dd>
      <dt>commit</dt><dd><code>3f6f7ee022644bf913987f37ca683edbdb6c464e</code></dd>
    </dl>
  </div>
</li>
<li class="cmp-entry cmp-verdict-kept">
  <div class="cmp-entry-when"><time datetime="2026-09-05">2026-09-05</time></div>
  <div class="cmp-entry-card">
    <p class="cmp-entry-head"><a href="../patches/device-side-mask-expansion/">Device-side mask expansion</a><span class="cmp-pill cmp-pill-kept">kept</span></p>

    <p class="cmp-entry-summary">Publishes a compact row-visibility hint and rebuilds the expanded attention mask on the destination GPU, removing repeated host uploads rather than compressing them. It covers both the causal mask and sparse-attention block bias.</p>
    <dl class="cmp-entry-meta">
      <dt>headline</dt><dd>removes repeated expanded-mask uploads</dd>
      <dt>selectors</dt><dd>none; part of the attention path when built</dd>
      <dt>contexts</dt><dd>causal mask and sparse-attention block bias</dd>
      <dt>output</dt><dd>byte-exact</dd>
      <dt>commit</dt><dd><code>636415e0f216110dfab887bc81cfa9e324177c70</code></dd>
    </dl>
  </div>
</li>
</ol>
<!-- END GENERATED TIMELINE -->
