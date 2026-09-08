# Complete llama.cmp-v patch series

**All eight patches live here, in application order. Release binaries compile the complete series together.** The source in this repository already contains every patch; do not apply them again to a clone of this fork.

| Order | Patch |
| --- | --- |
| 1 | [DP4A MMQ routing](0001-dp4a-mmq-routing.patch) |
| 2 | [Volta Q4_K / Q5_K DP4A routing](0002-volta-q4k-q5k-dp4a.patch) |
| 3 | [Parallel model loading](0003-parallel-model-load.patch) |
| 4 | [Mapped host bridge](0004-mapped-host-bridge.patch) |
| 5 | [Research selector registry](0005-research-selectors.patch) |
| 6 | [Prompt graph capture seed](0006-prompt-graph-capture-seed.patch) |
| 7 | [Device-side mask expansion](0007-device-side-mask-expansion.patch) |
| 8 | [SM70 D256 shared Q and unit rescaling](0008-sm70-d256-shared-q.patch) |

## Reconstructing from upstream

The [manifest](manifest.json) pins upstream commit `4d9176092d00586775af140581bb0b558ddc4389` and the reconstructed source tree. Start with a clean checkout of that upstream commit, then apply all numbered patch files in lexical order with `git apply`. The first seven preserve the earlier mechanisms; patch 8 adds the accepted shared-Q and unit-rescale specialization.

Patch application and source equivalence are checked before binary compilation. These checks establish which source is built; they do not certify performance or GPU correctness. Read the [measurements and limitations](../docs/results/2026-09-07-sm70-d256-shared-q.md) before interpreting speed changes. Private runtime telemetry instrumentation is not included in this series.
