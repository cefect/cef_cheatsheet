# ADR 0001: Reference sheet print format

- Status: accepted
- Date: 2026-10-23
- Scope: printable reference sheets in `ref/` (Typst PDF output only; HTML is unconstrained)

## Context

Reference sheets are printed on US Letter and read at arm's length.
Earlier sheets used 8–11pt text to fit dense tables, which is hard to read on paper.

## Decision

Each reference sheet PDF must:

- fit on a single US Letter page (portrait or landscape);
- use a minimum font size of 12pt for all content, including inline code and table cells;
- use a minimum of 6pt for footnotes only;
- use minimal margins (0.25in);
- be greyscale (black text, grey fills/rules; no colored code, links, or highlights);
- shade alternating table rows for readability.

The web (HTML) version may use color and is not size-constrained.

When content does not fit, drop detail or move it to footnotes rather than shrinking the font or adding pages.

### Exception: agent model comparison

- **Approved 2026-11-24:** [Agents](../../ref/agents.qmd) uses two landscape US Letter pages: Codex on page 1 and Claude Code on page 2.
- Keep pricing and model details in separate tables, with release dates and official descriptions in the model table.
- Place each table's footnotes immediately beneath that table; these notes may use the existing footnote font size.
- Retain the 12pt minimum for table content and greyscale PDF output; the red–green cost scale appears only in HTML.

## Implementation

- [ref/_metadata.yml](../../ref/_metadata.yml): page size, margins, base font size, template partial.
- [ref/typst-template.typ](../../ref/typst-template.typ): compact title, greyscale, code sizing, footnote size, zebra rows.
- [ref/landscape.typ](../../ref/landscape.typ): opt-in landscape header for wide sheets.

## Consequences

- Sheets carry less detail than the original sources; footnotes hold secondary notes.
- New or edited sheets must be re-rendered and checked for page count before committing.
