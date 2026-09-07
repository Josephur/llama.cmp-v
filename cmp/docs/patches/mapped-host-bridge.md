---
title: Mapped pinned host bridge
description: Making the no-P2P cross-card handoff explicit — scheduler-visible CUDA ownership and a fixed four-slot mapped pinned bridge with event-ordered reuse.
---

# Mapped pinned host bridge

!!! abstract "At a glance"

    | | |
    | --- | --- |
    | **Commit** | `80b289d94` |
    | **Selector** | `GGML_CUDA_MAPPED_HOST_BRIDGE=1` |
    | **Aimed at** | cross-card tensor boundaries with no peer-to-peer path |
    | **Slots** | four, fixed, for boundaries up to 64 MiB |
    | **Output** | byte-for-byte unchanged, lossless by construction |

## The problem

These cards expose no peer-to-peer path. `cudaDeviceCanAccessPeer` is false for
every pair, there is no NVLink, and the link is PCIe Gen1 x1. So every
cross-card tensor boundary — every point where a layer-split model hands
activations from one card to the next — is a host round trip: down the link,
into host memory, back up the link.

That cost is unavoidable. What *was* avoidable is paying it through an implicit,
per-boundary path the scheduler cannot see, with a fresh staging allocation each
time and no ordering guarantee beyond whatever the surrounding synchronisation
happened to provide.

```mermaid
flowchart LR
    C3["Card 3<br/>layers 20&ndash;29"]
    C4["Card 4<br/>layers 30&ndash;39"]

    C3 -- "device to host<br/>PCIe Gen1 x1" --> HM[("host memory")]
    HM -- "host to device<br/>PCIe Gen1 x1" --> C4
    C3 -. "the path that does not exist" .-x C4

    classDef gone stroke-dasharray: 6 4,color:#b91c1c,stroke:#b91c1c
    class C3,C4 default
```

## The mechanism

Two parts.

**Scheduler-visible CUDA ownership.** The boundary becomes something the graph
scheduler knows about rather than an implicit copy hidden inside a backend
call. What is staged, when, and who is waiting on it are all explicit.

**A fixed four-slot mapped pinned bridge.** Staging buffers are mapped pinned
host memory, allocated once, reused, and sized for boundaries up to 64 MiB.
Reuse is ordered by CUDA events, so a slot is never rewritten while a consumer
is still reading it.

```mermaid
flowchart TB
    subgraph BRIDGE["four-slot mapped pinned bridge"]
        S0["slot 0"]
        S1["slot 1"]
        S2["slot 2"]
        S3["slot 3"]
    end

    P["producer card"] -->|"write, records event E"| S0
    S0 -->|"consumer waits on E"| Q["consumer card"]
    Q -->|"records completion event"| REUSE{"slot free?"}
    REUSE -- "event complete" --> S0
    REUSE -- "not yet" --> WAIT["producer waits;<br/>no slot is ever<br/>rewritten under a reader"]

    classDef safe fill:#0f766e,stroke:#134e4a,color:#fff
    class REUSE safe
```

Four slots, not a queue that grows: a fixed pool bounds pinned host memory, and
pinned memory on a host feeding six cards is a resource worth bounding. When all
four are in flight the producer waits, which is the correct behaviour on a link
that is already the bottleneck.

## The safety argument

!!! success "Lossless by construction"

    This patch changes **where bytes are staged, not what they contain**. No
    transformation, no compression, no precision change. The only correctness
    question is ordering, and ordering is enforced by CUDA events rather than by
    assumption: a slot is reusable only after the event marking its consumer's
    completion has fired.

That is a much stronger position than "we measured the same output". Byte-exact
verification across the ladder confirms it, but the argument does not depend on
the measurement.

## What it is not

This does not remove the host round trip. It cannot — there is no peer path to
route around it. It makes the round trip explicit, bounded and reusable. On a
single-card configuration there are no cross-card boundaries and the mechanism
has nothing to do.

## Enabling it

```bash
GGML_CUDA_MAPPED_HOST_BRIDGE=1 llama-server ...
```

Confirm the bridge's own log line reports the slot count. A selector read
through the [research registry](research-selectors.md) proves only that the
value was seen.
