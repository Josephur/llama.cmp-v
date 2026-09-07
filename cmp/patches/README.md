# Release patches

This directory is reserved for machine-applicable patches, in application order, named `NNNN-<mechanism>.patch`. Explanatory pages under `cmp/docs/patches/` are not patch files.

The inherited source series lives under `cmp/releases/inherited/`; its manifest records verified reconstruction from the upstream base. This directory contains subsequently accepted optimizations. The generated source already includes those changes, so do not apply them twice.

Every patch excludes private tooling and must reproduce the reviewed source change when applied to its preceding fork base. Each accepted optimization has a result entry with verified output comparisons, measurements, regressions and the acceptance decision. Human acceptance of marginal gains does not establish statistical significance or runtime selector attribution. Unaccepted experiments retain their write-ups and evidence without becoming release patches.

- `0001-sm70-d256-shared-q.patch`: human-approved sm70-d256-shared-q; source already applied in the generated tree.
