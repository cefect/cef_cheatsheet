---
name: update-agent-models
description: Refresh ref/agents.qmd with current official Codex and Claude Code models, pricing, release dates, descriptions, and source links.
---

# 1. Scope

Maintain the agent model reference sheet in this repository.

- Read `ref/agents.qmd`, `docs/adr/0001-reference-sheet-print-format.md`, and relevant entries in `issues.md` before editing.
- Preserve the comparison of Codex credits and Claude API USD rates; these are different billing units.
- Keep existing model rows unless officially retired from the documented surface; add newly released general-purpose models supported by Codex or Claude Code.
- Exclude specialized or restricted-access research models unless requested.

# 2. Verify current sources

Browse official sources on every invocation; do not reuse remembered prices or dates.

| Information | Starting sources |
| --- | --- |
| Codex rates and speed multipliers | https://learn.chatgpt.com/docs/pricing |
| Codex model availability and descriptions | https://learn.chatgpt.com/docs/models |
| Codex release dates | https://learn.chatgpt.com/docs/changelog and linked OpenAI announcements |
| Claude standard and fast rates | https://platform.claude.com/docs/en/about-claude/pricing |
| Claude descriptions and release dates | Individual model overview pages linked from pricing; use the `Released` field |
| Claude Code aliases and minimum versions | https://code.claude.com/docs/en/model-config and https://code.claude.com/docs/en/fast-mode |

- Follow current official links when a starting URL moves.
- Distinguish a model release from a later speed-mode release, training cutoff, or client release.
- Quote concise official description excerpts with attribution and direct links, respecting source quotation limits; label summaries if paraphrasing.
- For fast variants, reuse the base model description and release date and explicitly explain that convention.
- Mark unavailable or conflicting facts as unverified rather than inventing values; keep previous values visibly dated if sources cannot be checked.
- Check installed CLI versions and local help when documenting CLI behavior; distinguish local support from current documented aliases without installing updates.

# 3. Update and verify

- Update source links and verification dates only for facts actually rechecked, using the user's local date.
- Define Input, Cached / Cache hit, Output, all three Burn columns, and per-million-token units.
- Recompute each Burn value as that row's rate divided by the matching column of its provider's stated baseline; never compare credits directly with USD.
- Preserve material billing caveats: cache writes, prompt-length thresholds, speed multipliers, subscription versus API billing, alias targets, and minimum versions.
- Keep grid tables and the one-page landscape PDF; put secondary details in footnotes, following ADR 0001.
- Render `ref/agents.qmd` to Typst in the existing `cef_cheatsheet` Conda environment, following `.agents/runbooks/quarto-conda.md` when relevant.
- Verify one US Letter landscape page, readable tables, complete footnotes, source targets, and calculated ratios.
- Validate HTML too when feasible; report any remaining render limitation accurately.
- Record meaningful source discrepancies or render failures in the existing owning issue, or create a concise issue when new.
- Report changed facts, verification date, checks, and unresolved facts; do not commit or push unless explicitly requested.
