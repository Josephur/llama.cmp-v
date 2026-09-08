# llama.cmp-v: llama.cpp for NVIDIA CMP 100-210 (CMP 100HX-210)

**This fork targets NVIDIA CMP 100-210 / CMP 100HX-210 cryptocurrency mining cards for local LLM inference.** These NVIDIA Volta / GV100 cards use CUDA compute capability 7.0 (SM70), but their mining configuration has restrictions that ordinary GPU inference builds do not account for.

The tested CMP configuration has PCIe Gen1 x1 links, no usable CUDA peer-to-peer path between cards, and rejected Nsight CUDA profiling. These restrictions make model uploads, host-staged multi-GPU transfers and kernel submission expensive. The patches address those costs and add SM70-specific execution paths. They do not unlock hardware, change firmware or turn a CMP into a fully enabled Tesla V100. Modified boards can behave differently; the exact enforcement mechanism is not established by these measurements.

The source includes seven inherited patches plus the accepted SM70 D256 shared-Q and unit-rescaling patch. Public measurements retain regressions and validation limits. Gains depend on the model, request and hardware configuration.

- [Hardware and limitations](https://josephur.github.io/llama.cmp-v/hardware/)
- [Patch descriptions](https://josephur.github.io/llama.cmp-v/patches/)
- [Accepted measurements](https://josephur.github.io/llama.cmp-v/results/)
- [Binary releases](https://github.com/Josephur/llama.cmp-v/releases)

SM70 binary builds use **CUDA 12.9.2** and **`CMAKE_CUDA_ARCHITECTURES=70-real`**. CUDA 13 removed offline compilation support for Volta. A successful build establishes the compiled target, not correctness or performance on every CMP configuration. The NVIDIA driver must support the card and CUDA runtime.

## Complete patch series

All eight patches are in [one directory](https://github.com/Josephur/llama.cmp-v/tree/main/cmp/patches), with a manifest specifying their application order and upstream base. The public source already contains the complete series. Both Linux and Windows SM70 binaries compile that complete source; they are not separate per-patch builds.

## Building the source

Follow the upstream [build documentation](../docs/build.md). Use CUDA 12.9.2, `CMAKE_CUDA_ARCHITECTURES=70-real` and `GGML_CUDA=ON`. Select a compatible host CPU baseline explicitly. Build and publishing automation stays private; downloadable binaries will appear on the public Releases page after their builds and checks pass.

## Documentation and evidence

Public documentation and derived measurements are under `cmp/docs/`. The correctness target is identical generated output in matched comparisons. Recorded evidence distinguishes exact-output checks, runtime activation and performance uncertainty. Source reconstruction alone does not establish a speedup.
