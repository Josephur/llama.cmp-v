# Instructions for llama.cmp-v

This is the independently maintained llama.cmp-v fork. These instructions govern this fork, its private toolkit and publication to Josephur/llama.cmp-v.

## Scope and authorization

Upstream llama.cpp contribution restrictions apply only to contributions addressed to ggml-org/llama.cpp. They do not prohibit agent-assisted development, documentation, MkDocs maintenance, commit messages or publication in this fork. A public fork is still this fork; public visibility does not make an operation an upstream submission.

Carry out user-authorized fork work, including documentation and site updates. Obtain explicit user authorization before committing, pushing or publishing when it has not already been provided. Verify the destination remote before any publication. Do not submit upstream contributions without consulting the upstream project's current contribution and agent guidance and the user.

## Working conventions

Preserve existing edits and active services. Read relevant code before changing it, reuse existing infrastructure and keep changes focused. Use concise ASCII code comments. Run checks appropriate to the changed code or documentation and report which checks actually ran.

Report user-facing dates and times in America/Indiana/Indianapolis. Preserve original timestamps in raw evidence when needed.

## Private toolkit and public output

If cmp/AGENTS.md exists, read it before toolkit or CMP research work. The private toolkit is the source of maintained fork changes. Public output is generated through its reviewed export process; never export private configuration, tooling or raw evidence. For documentation or MkDocs work initiated in the public checkout, update the maintained source and regenerate through that process when available. Do not mistake upstream submission restrictions for a ban on updating this fork's site.

## Policy maintenance

In the private toolkit, cmp/config/fork-AGENTS.md is the authoritative copy of this file. After importing upstream, run python3 -B cmp/scripts/fork-policy.py apply, then cmp/scripts/audit-workspace.sh. Setup and public export install this policy; the workspace and export audits reject a missing or changed policy. Do not resolve an upstream merge conflict by discarding the fork policy. A fresh upstream-only clone has no fork tooling: restore the fork branch or toolkit before using this workflow.
