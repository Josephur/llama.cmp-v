---
title: Benchmarks
description: Verified measurements accompanying permanently promoted patches.
---

# Benchmarks

The public portal publishes measurements only when a patch is permanently adopted. Ongoing, undecided and declined experiments stay in the private research record. A running test never appends to a published measurement file.

Each entry in the [promoted patch timeline](index.md) links its verified CSV and source patch. CSVs record the model label, device count, prompt and server contexts, exact output count, absolute reference and candidate measurements, and signed percentage changes. Negative duration changes mean faster execution; positive throughput changes mean faster execution.

Read the full result before treating a number as an improvement. Entries retain regressions, output checks, sampling limits and whether runtime activation was established. A human can accept a small or uncertain gain without claiming statistical significance. Saved-reference comparisons do not eliminate thermal or runtime drift.

The [method](../method.md) describes the evidence requirements. Only derived, reviewed measurements are public. Prompts, model responses, target identities, machine paths and raw per-card records remain private.
