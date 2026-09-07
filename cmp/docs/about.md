---
title: About
description: Who builds llama-cmpv, what it is for, and how it relates to upstream llama.cpp.
---

# About

## Who

**llama-cmpv** is built and maintained by **Joseph Stackhouse** at
[**Stack-Tech**](https://stack-tech.com).

<div class="grid cards" markdown>

-   :material-web:{ .lg .middle } **Stack-Tech**

    ---

    [stack-tech.com](https://stack-tech.com)

-   :material-github:{ .lg .middle } **Source**

    ---

    [github.com/Josephur](https://github.com/Josephur) — the fork, the patch
    series, and this site all live in one repository.

</div>

## What this is

A research fork of [llama.cpp](https://github.com/ggml-org/llama.cpp) carrying a
small series of patches that make NVIDIA CMP 100-210 mining cards usable for LLM
inference, plus the full record of the experiments behind them.

It is not a distribution and not a product. It is a patch series meant to be
rebased onto upstream repeatedly, kept small enough that rebasing stays
possible, and default-off so that carrying it changes nothing until a selector
is set.

## What it is not

!!! info "Not a fork of upstream's direction"

    Every patch here is additive and default-off. The repository root belongs to
    upstream llama.cpp — its build, its documentation, its contributor guidance.
    Everything this project adds lives under `cmp/`, including this site.

!!! info "Not benchmarks of llama.cpp"

    Nothing on this site is a claim about llama.cpp's performance in general.
    Every number is measured on one unusual machine — Volta silicon behind a
    Gen1 x1 link with no peer path — and several of the mechanisms here would be
    worthless or negative on ordinary hardware. That is stated on the pages, not
    buried in a footnote.

## Licence and attribution

The patches are offered against upstream llama.cpp under its **MIT** licence.
Upstream's copyright and licensing are unchanged by anything in this repository.

This documentation is authored by Joseph Stackhouse, Stack-Tech. If you use the
published findings and their documented limitations, an attribution link is appreciated.

## Contributing

The rules for anyone working on this fork, human or agent, live in a single
rules file in the working repository, kept in one file so they cannot drift
between copies. Patches here are offered upstream where they are general
enough; where they are specific to these cards they stay here.

## Contact

Issues and pull requests on the repository are the best route.
[github.com/Josephur](https://github.com/Josephur)
