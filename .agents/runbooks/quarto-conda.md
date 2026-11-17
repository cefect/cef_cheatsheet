# 1. Scope

Run the existing Conda Quarto launcher when its default share and Deno paths do not match the installed layout.

| Item | Applicability |
| --- | --- |
| Environment | CEFTOP WSL, existing `cef_cheatsheet` Conda environment |
| Last verified | 2026-11-17; Quarto 1.9.38, Pandoc 3.8.3, Typst 0.14.2 |
| Evidence | [ENV-001](../../issues.md#env-001-conda-quarto-launcher-paths) |
| Authorization | Read-only environment inspection authorized by implementation of plan section 3.1 |
| Limits | Process-local supported overrides; no installation, package edits, symlinks, or sandbox bypass |

# 2. Procedure

Use the existing environment and inspect its paths before applying the overrides.

1. Locate `cef_cheatsheet` using `conda env list`.
2. Confirm that its `bin/quarto`, `bin/deno`, `bin/sass`, `bin/pandoc`, `bin/typst`, and `share/quarto/version` exist.
3. Activate that environment and set only the process-local overrides below.

```bash
conda activate cef_cheatsheet
export QUARTO_SHARE_PATH="$CONDA_PREFIX/share/quarto"
export QUARTO_DENO="$CONDA_PREFIX/bin/deno"
export QUARTO_DART_SASS="$CONDA_PREFIX/bin/sass"
export QUARTO_PANDOC="$CONDA_PREFIX/bin/pandoc"
export QUARTO_TYPST="$CONDA_PREFIX/bin/typst"
quarto --version
quarto --help
```

Notes:
- Quarto explicitly supports these variables; the original environment remains unchanged on disk.
- Verification returned version `1.9.38` and successful command help.
- `cef_cheatsheet.code-workspace` activates this environment in new WSL terminals and supplies the same overrides.
- Last render check passed tool discovery but stopped at Deno `openKv` with `unable to open database file` in the Sass cache; see ENV-001 before further troubleshooting.
- **2026-11-17:** Typst rendering also requires the supported `QUARTO_PANDOC` and `QUARTO_TYPST` overrides above; the launcher otherwise requests missing `bin/tools/x86_64/pandoc`.
- **Verification:** `quarto render ref/agents.qmd --to typst` produced a single-page `_site/ref/agents.pdf` with all five overrides; HTML cache access remains unverified.

# 3. Retirement

Stop using these overrides when a repaired or replaced launcher resolves its tools correctly without them.

- Recheck normal startup after a Quarto package update.
- This record grants no installation or environment-repair permission.
