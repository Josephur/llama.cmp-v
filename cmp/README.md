# CMP research for llama.cpp

This tree carries experimental changes for NVIDIA CMP 100-210 cards. The source builds with upstream CMake; runtime tuning is described in the documentation portal.

## Current release status

The inherited mechanisms have source and explanatory pages, and the inherited machine-applicable source series lives in `cmp/releases/inherited/`. Its application and source equivalence are verified. The results timeline records later optimization attempts, measurements and human acceptance decisions. The historical benchmark CSV lacks model and package provenance. It is historical evidence, not a reproducible release comparison.

No binary release is produced by the documentation export. Binary packages must be reviewed separately for dependencies, licenses, private paths and a public source revision before release.

## Building the source

Follow the upstream [build documentation](../docs/build.md). A CUDA build for these cards requires a toolchain that supports SM70 and a CPU baseline compatible with the target machine. Set `CMAKE_CUDA_ARCHITECTURES=70-real` and `GGML_CUDA=ON`; select the CPU features explicitly rather than inheriting those of the build machine.

## Documentation and patches

The portal lives under `cmp/docs/`. The intended correctness bar is identical generated output between matched control and candidate runs, followed by measured performance and evidence that the mechanism executed. A selector read alone does not establish execution.

`cmp/patches/` is reserved for reviewed, applicable release patches. The inherited source can be reconstructed using the separately labelled series in `cmp/releases/inherited/`. This does not certify a performance gain.
