# AGENTS.md

## Local rendering

Use the existing `cef_cheatsheet` Conda environment for local Quarto previews and renders.
Open `cef_cheatsheet.code-workspace` on WSL; new integrated terminals activate this environment and apply its Quarto tool paths.
For agent shells and launcher path failures, follow [.agents/runbooks/quarto-conda.md](.agents/runbooks/quarto-conda.md).

## Command reference entries

Use the `add-command-block` skill when adding verified commands to the cheat sheet.
Follow the skill's requirements for local version checks, concise descriptions, and minimal focused edits.

## WSL access from Windows Codex

If sandboxed PowerShell calls to `wsl.exe` return `Wsl/E_ACCESSDENIED`, use an approved escalated WSL call with the repository path passed via `--cd`.
