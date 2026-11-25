# 1. Status

Project issue index and concise development history.

| Issue | Status | Scope |
| --- | --- | --- |
| [HUC-001](#huc-001-nested-huc-reference-sheets) | Data acquisition in progress | Upper Colorado HUC2–HUC12 reference collection |
| [ENV-001](#env-001-conda-quarto-launcher-paths) | Startup workaround verified | Conda Quarto 1.9.38 on CEFTOP WSL |
| [AGENT-001](#agent-001-official-model-reference-and-refresh-skill) | Reference refreshed | Agent model sources, descriptions, release dates, and pricing definitions |

# 2. Issues

## AGENT-001: Official model reference and refresh skill

- **2026-11-24 — refreshed:** [agent sheet](ref/agents.qmd) checked against linked official OpenAI and Anthropic pricing, model guides, release records, and CLI documentation.
- **Finding:** existing token rates remain current; added linked base-model release dates, official description excerpts, pricing-column definitions, and explicit provider-specific Burn calculations.
- **Client scope:** local Codex CLI 0.167.1 and Claude Code 2.1.269 inspected with local help; current Claude aliases require newer versions as documented in the sheet.
- **Maintenance:** created and applied [project-local update skill](.agents/skills/update-agent-models/SKILL.md); no packages installed or clients updated.
- **Verification:** skill validator, all 42 Burn ratios, reference-link definitions, and single-use footnotes checked; Quarto 1.9.38 rendered one landscape US Letter page with 12pt table text and 8pt footnotes, visually inspected.
- **HTML:** complete render verified using the ENV-001 temporary-cache procedure; outputs `_site/ref/agents.html` and `_site/ref/agents.pdf`.
- **2026-11-24 — readability revision:** user approved the [two-page Agents exception](docs/adr/0001-reference-sheet-print-format.md#exception-agent-model-comparison), with Codex and Claude on separate landscape pages and greyscale printing retained.
- **Layout:** separate price and release/description tables; footnotes immediately beneath their table; HTML-only green–yellow–red shading compares each numeric column within its provider on a logarithmic scale.
- **Implementation:** [page filter](ref/agents-layout.lua) formats local notes and computes static HTML cell colors; [scoped CSS](ref/agents.css) adds numeric alignment, a legend, and horizontal scrolling for narrow screens.
- **Verification:** both formats render; two-page PDF visually checked for provider split, greyscale tables, and complete local notes; HTML structure checked for four tables, adjacent notes, 84 shaded numeric cells, matching colors for equal values, and green/red endpoints.
- **Maintenance:** refresh skill updated for the approved layout and validated; all prices and 42 Burn ratios preserved.

## HUC-001: Nested HUC reference sheets

- **2026-11-13 — planned:** [Development plan](ref/huc/plan.md) for six US Letter sheets with identical extents, OSM terrain context, and USGS WBD data acquisition.
- **Constraint:** basin-wide HUC10/HUC12 maps cannot label every unit at the existing 12pt print minimum; retain all boundaries and provide a complete companion lookup.
- **2026-11-13 — section 3.1 complete:** added [shared configuration](ref/huc/config.yml), scoped build exclusions, and [environment inventory](ref/huc/README.md#3-environment-inventory).
- **Dependencies:** installed system GDAL/OGR can support geospatial processing; `pypdf` is absent and its proposed installation requires user approval before PDF assembly/inspection.
- **Verification:** configuration parsing, Letter layout arithmetic, region/level scope, output exclusions, and local links checked; data acquisition, rendering, and print checks remain pending.
- **2026-11-13 — WBD fetched:** USGS region 14 shapefile archive dated 2025-01-08, SHA-256 `673df784ad15e4bd006e6a5ed3d869294f07abbbedec105c6e3cf9bb66498935`.
- **WBD inspection:** HUC2/4/6/8/10/12 counts 1/8/10/60/524/3,179; no invalid individual geometries, duplicate codes, or missing parent codes.
- **Outstanding:** parent/child spatial gaps and overlaps, OSM and terrain downloads, and complete provenance and coverage verification.

- **2026-11-13 — active build:** `ref/huc/scripts/build_huc.py` running in tmux `huc-build:build`; frame saved and topology computed; USGS elevation returned HTTP 504; bounded retry running in `huc-build:retry`.
- **Outputs pending:** bounded terrain/OSM downloads, PDF collection and six sheets, prototypes, and manifest.

- **2026-11-13 — map revision:** HUC labels restricted to levels 2/4; dashed Census state borders added; titles, north arrows, and bottom notes removed; attribution moved to the page edge.

- **2026-11-13 — counts revision:** lower-left HUC level and total unit counts added to all six pages.

- **Outlet annotation:** Colorado River/WBD boundary intersection in the Lee Ferry area added to every map; coordinates and derivation recorded in the plan.

- **Nested outlet rebuild:** collection now HU2–HU8; outlet counts 1/8/9/54, with one closed unit at HU6/HU8 and five unresolved HU8 crossings; detail in ignored `outlets.json`.
- **Verification:** four-page rendering completed; HU4 preview checked for open circles and concentric parent rings.

- **Legend revision:** lower-left outlet marker legend added; symbols match the plotted HU2/4/6/8 circle sizes and expand with page level.

- **Full collection revision:** restored six pages through HUC12, moved HUC-level title to upper right, restricted outlet markers and legends to HUC2–HUC8.

## ENV-001: Conda Quarto launcher paths

- **2026-11-13 — startup workaround verified:** Quarto 1.9.38 in the existing `cef_cheatsheet` Conda environment looks for missing `share/version` and `bin/tools/x86_64/deno` paths.
- **Finding:** `share/quarto/version` and `bin/deno` exist; the launcher supports process-local `QUARTO_SHARE_PATH` and `QUARTO_DENO` overrides.
- **Solution:** [bounded startup runbook](.agents/runbooks/quarto-conda.md); no installation or environment edits performed.
- **Verification:** version and help succeed with overrides; direct Typst 0.14.2 version/compile help also succeed; full rendering remains unverified.
- **2026-11-14 — HTML render blocked:** `quarto render --to html` starts with the documented overrides but fails because `bin/tools/x86_64/dart-sass/sass` is missing in the `cef_cheatsheet` environment.
- **Scope:** encountered while validating the move of tool pages into `pages/`; no environment changes made.
- **2026-11-14 — workspace configured:** WSL workspace terminals activate `cef_cheatsheet`; added supported `QUARTO_DART_SASS` pointing to its existing `bin/sass`, resolving the missing Sass executable.
- **Verification:** Quarto 1.9.38 starts in the activated environment; HTML rendering now fails in Deno `openKv` with `unable to open database file` while opening the Sass cache.
- **Outstanding:** cache access and complete rendering remain unverified; no cache permissions or environment installation changed.
- **2026-11-17 — Typst render verified:** rendering `ref/agents.qmd` initially failed with missing `bin/tools/x86_64/pandoc`; existing Pandoc 3.8.3 and Typst 0.14.2 work through supported process-local `QUARTO_PANDOC` and `QUARTO_TYPST` overrides.
- **Solution:** extended the [startup runbook](.agents/runbooks/quarto-conda.md); no installation or environment changes.
- **Verification:** Quarto 1.9.38 produced a one-page `_site/ref/agents.pdf`; HTML Sass cache access remains unverified.
- **2026-11-24 — HTML cache workaround verified:** default-cache rendering reproduced Deno `openKv` / `unable to open database file`; Quarto's installed `xdgUserCacheDir` honors `XDG_CACHE_HOME`.
- **Solution:** a process-local fresh `/tmp` cache allowed complete HTML rendering, followed by a successful one-page Typst render; recorded in the [runbook](.agents/runbooks/quarto-conda.md#21-html-sass-cache-access).
- **Scope:** no persistent environment, default-cache, package, or permission changes; original cache access remains unresolved.
