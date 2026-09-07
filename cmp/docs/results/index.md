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

    <p class="cmp-entry-summary">The user approved the combined shared-Q and unit-rescale candidate as a modestly helpful patch. All four primary contexts preserved exact 256-token output. At 250K, request wall time was 2.677% lower than the original saved reference, saving 86.499 seconds; 2.304 seconds of that saving was incremental to the first shared-Q candidate. Generation regressed at 8K and 65K against the original reference and at every context against the first candidate. Native repeatability and selector attribution remain unproven. The indexed headline now describes the combined candidate; the original measurements below remain unchanged historical evidence.</p>
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
