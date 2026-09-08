---
title: Promoted patches
description: Verified measurements for permanently adopted patches.
---

# Promoted patches

Only permanently adopted patches appear here. Each entry links its source patch and measured data, including regressions and validation limits. Human acceptance does not imply statistical significance.

The [benchmark guide](benchmarks.md) explains the linked measurements. The [machine-readable index](index.json) contains the same promoted entries.

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
</ol>
<!-- END GENERATED TIMELINE -->
