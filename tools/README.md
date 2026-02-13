# Tools Integration Layer

This directory contains wrappers and scripts that let LLM-driven workflows call:

- locally installed bioinformatics programs
- external bioinformatics APIs

It is intentionally parallel to `src/` so workflows can import or shell-call these utilities.

## Layout

- `tools/local/`: adapters for local executables (for example `mmseqs`, `blastp`, `mafft`).
- `tools/api/`: adapters for remote APIs (for example UniProt, RCSB, NCBI, AlphaFold DB).
- `tools/scripts/`: small CLI entrypoints that workflows/notebooks can call.
- `tools/config/`: registry/config placeholders for tool discovery and defaults.

## Usage Pattern

1. LLM workflow decides which tool to run.
2. Workflow calls a function from `tools/local` or `tools/api`, or executes a script in `tools/scripts`.
3. Wrapper returns a normalized dictionary payload (status + outputs + logs).

## Notes

- Keep wrappers deterministic and thin.
- Parse external outputs into structured records before handing to LLM prompts.
- Put binary-specific assumptions (flags, versions) inside wrappers, not notebooks.

