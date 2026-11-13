# 1. Scope

Run the existing Conda Quarto launcher when its default share and Deno paths do not match the installed layout.

| Item | Applicability |
| --- | --- |
| Environment | CEFTOP WSL, existing `cef_cheatsheet` Conda environment |
| Last verified | 2026-11-13; Quarto 1.9.38, Typst 0.14.2 |
| Evidence | [ENV-001](../../issues.md#env-001-conda-quarto-launcher-paths) |
| Authorization | Read-only environment inspection authorized by implementation of plan section 3.1 |
| Limits | Process-local supported overrides; no installation, package edits, symlinks, or sandbox bypass |

# 2. Procedure

Use the existing environment and inspect its paths before applying the overrides.

1. Locate `cef_cheatsheet` using `conda env list`.
2. Confirm that its `bin/quarto`, `bin/deno`, and `share/quarto/version` exist.
3. Activate that environment and set only the process-local overrides below.

```bash
export QUARTO_SHARE_PATH="$CONDA_PREFIX/share/quarto"
export QUARTO_DENO="$CONDA_PREFIX/bin/deno"
quarto --version
quarto --help
```

Notes:
- The launcher explicitly supports both variables; the original environment remains unchanged on disk.
- Verification returned version `1.9.38` and successful command help.
- This verifies startup only; other bundled tool paths and full rendering still require verification before use.

# 3. Retirement

Stop using these overrides when a repaired or replaced launcher resolves its tools correctly without them.

- Recheck normal startup after a Quarto package update.
- This record grants no installation or environment-repair permission.
