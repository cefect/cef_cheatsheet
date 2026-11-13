# 1. Summary

Develop six nested hydrologic unit code (HUC) reference sheets for the Upper Colorado region, with one US Letter page per HUC level and identical map extents throughout.

| Item | Status / scope |
| --- | --- |
| Plan | Section 3.1 complete; sections 3.2–3.4 in progress; section 3.5 pending |
| Geography | Upper Colorado, two-digit region code `14` |
| Levels | HUC2, HUC4, HUC6, HUC8, HUC10, HUC12 |
| Page format | 8.5 × 11 inches, portrait |
| Basemap | OSM context with shaded terrain; shared across all pages |
| Deliverables | Six one-page PDFs, one assembled six-page PDF, HTML index |

- Issue: [HUC-001](../../issues.md#huc-001-nested-huc-reference-sheets).
- Branch / PR: no dedicated branch or PR created.
- Print constraints: [ADR 0001](../../docs/adr/0001-reference-sheet-print-format.md).
- Existing rendering: [reference metadata](../_metadata.yml), [Typst template](../typst-template.typ), and [project README](../../README.md).

**Interpretation:** `HUC 02` means the two-digit level; `14` is the selected region code.
The first page title is **HUC 02: 14 — Upper Colorado**, with only the region boundary and its label over the terrain basemap.
Each subsequent page subdivides that same region at the next HUC level, without zooming into individual children.

# 2. Proposed Architecture

Add a small, reproducible map-generation workflow alongside the existing Quarto reference sheets.

| Component | Current | Proposed |
| --- | --- | --- |
| Sources | No HUC assets | USGS WBD boundaries, OSM context, elevation for hillshade |
| Configuration | Shared reference formatting | One HUC configuration defining region, levels, extent, projection, layout, and style |
| Processing | No geospatial workflow | Fetch, validate, select descendants, prepare one basemap, render six overlays |
| Page sources | Individual reference `.qmd` files | Six level-specific `.qmd` files using shared map assets |
| PDF output | One page per reference sheet | Preserve individual one-page sheets; concatenate copies into a separate collection PDF |
| Web entry | Existing reference menu | HUC HTML index linking individual sheets and the collection |

## 2.1. Page sequence and map design

Keep map position, dimensions, bounds, projection, and basemap identical across pages.

| Page | Heading | HUC overlay |
| --- | --- | --- |
| 1 | HUC 02: 14 — Upper Colorado | Region `14` only |
| 2 | HUC 04: Upper Colorado | All four-digit descendants of `14` |
| 3 | HUC 06: Upper Colorado | All six-digit descendants of `14` |
| 4 | HUC 08: Upper Colorado | All eight-digit descendants of `14` |
| 5 | HUC 10: Upper Colorado | All ten-digit descendants of `14` |
| 6 | HUC 12: Upper Colorado | All twelve-digit descendants of `14` |

- **Fixed framing:** derive bounds once from the HUC2 geometry in EPSG:5070, add approximately 5% padding, expand to the map-frame aspect ratio, and save the final numeric bounds.
- **Page geometry:** use 0.25-inch margins and fixed title, map, legend, and footer slots so longer headings never resize the map.
- **Basemap:** soft hillshade, pale land cover, restrained rivers and major roads, and a few useful place labels; keep the terrain visible beneath unfilled HUC polygons.
- **Hierarchy:** draw the current level clearly, retain the outer HUC2 outline, and optionally show the immediate parent level with a heavier line.
- **Labels:** use full HUC codes where they fit, with names on the coarser pages and white halos for contrast.
- **Dense levels:** show every boundary, apply collision avoidance, and disclose omitted labels with a count; provide a complete code/name/parent table as an HTML or CSV companion.
- **Print rules:** greyscale PDFs, minimum 12pt main text and map labels, and minimum 6pt footnotes, following ADR 0001.
- **Cartographic furniture:** one consistent legend, north arrow, projection note, and scale bar calculated for the projected map.
- **Raster quality:** render hillshade at 300 dpi at its final physical size; keep HUC lines and labels as vectors.

Notes:
- HUC10 and HUC12 labels will not all fit at basin-wide extent and 12pt; do not shrink labels or change the extent to compensate.
- Each individual sheet remains one page; the combined PDF is a separate collection of those sheets.
- Render the OSM context locally so embedded tile labels do not undermine the print font-size requirement.

## 2.2. Data acquisition and provenance

Fetch and cache source data once, then render every page from the same pinned inputs.

| Input | Authoritative source / access | Planned acquisition |
| --- | --- | --- |
| HUC polygons and names | [USGS hydrography downloads](https://www.usgs.gov/national-hydrography/access-national-hydrography-products) | Locate the region `14` WBD archive through the official download listing; retain the archive and its metadata |
| Boundary-service fallback | [USGS WBD MapServer](https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer) | Discover layers and fields, fetch region `14` and its descendants, and save complete query results locally |
| OSM context | [Geofabrik US extracts](https://download.geofabrik.de/north-america/us.html) | Fetch extracts covering the padded map extent; select major rivers, water bodies, roads, and settlements |
| Terrain | [USGS 3DEP products](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services) | Obtain a suitable regional DEM, initially the approximately 30 m product, for the full padded extent |
| Style reference | [OpenTopoMap project](https://github.com/der-stefan/OpenTopoMap) | Use its OSM-plus-relief appearance as inspiration; build a restrained local style rather than depending on public raster tiles |

- Confirm the WBD archive contains the six required levels before processing; use one release for the entire collection.
- Preserve HUC fields as strings, select `14` at HUC2 and the `14` prefix at finer levels, and verify the official region name from source attributes.
- If the service fallback is needed, inspect current layer metadata and record limits, paginate using object IDs or supported offsets, and compare downloaded counts with service counts.
- Record source URLs, retrieval dates, release identifiers where available, checksums, coordinate systems, licenses, feature counts, and spatial coverage in a manifest.
- Choose OSM extracts from the actual padded extent; merge and deduplicate overlapping extracts before clipping.
- Fetch elevation only at the resolution needed for a regional Letter map, then mosaic, reproject, and resample once to a shared grid.
- Prepare a single cached greyscale terrain/context basemap and reuse that exact asset on every page.
- Include USGS source credit and [OpenStreetMap attribution](https://www.openstreetmap.org/copyright) on every page, with readable source URLs in print footnotes.

Notes:
- The [USGS WBD FAQ](https://www.usgs.gov/faqs/how-can-i-find-huc-hydrologic-unit-code-stream-how-can-i-find-namelocation-stream-using-huc) identifies six required levels from two to twelve digits; optional HUC14/HUC16 are outside this collection.
- The WBD archive has been downloaded and inspected; OSM and elevation inputs remain pending.

## 2.3. Planned file layout

Keep source/configuration under `ref/huc/` and generated products under the existing site or an ignored build namespace.

| Path | Purpose |
| --- | --- |
| `ref/huc/plan.md` | Development plan and progress |
| `ref/huc/config.yml` | Region, levels, shared bounds, CRS, page geometry, and style |
| `ref/huc/scripts/` | Fetching, preparation, rendering, and validation entrypoints |
| `ref/huc/index.qmd` | HTML overview, downloads, source notes, and label-coverage explanation |
| `ref/huc/huc02.qmd` … `huc12.qmd` | Six individual sheet sources |
| `_outputs/experiments/huc/reference_sheets/` | Ignored downloads, manifest, prepared data, basemap, and map assets |
| `_site/ref/huc/` | Rendered HTML, individual PDFs, collection PDF, and code/name lookup |

- Keep large downloads and generated build assets out of Git.
- Have each producer maintain a short `README.md` in its managed output directories, indexing file groups and child directories.
- A Snakemake DAG is not applicable to this initial small workflow.
- No unresolved architecture decision is needed for the first implementation; use the defaults above and review the printed prototype before expanding the style.

# 3. Implementation Plan

Implement in stages, with a shared-extent print prototype before rendering the full collection.

## 3.1. Environment and scaffold — **complete**

- Re-read this plan and ADR 0001 before implementation.
- Inspect installed Quarto, Typst, geospatial tools, and PDF utilities; inspect local versions and help before selecting APIs or commands.
- Identify any missing dependencies and request explicit installation authorization if needed.
- Add shared configuration and output exclusions without changing other reference sheets.

Completed 2026-11-13; see the [configuration](config.yml), [environment inventory](README.md#3-environment-inventory), and [Quarto startup runbook](../../.agents/runbooks/quarto-conda.md).

- **Available:** system Python/GDAL/OGR, YAML, projection, plotting, and existing Conda Quarto/Typst tools.
- **Gap:** PDF assembly/inspection dependency `pypdf`; proposed installation requires explicit approval before proceeding.
- **Verification:** parsed configuration, checked print geometry and HUC scope, checked ignore rules and local links; no data or rendered maps produced.

## 3.2. Fetch and validate inputs — **in progress**

- Download the region `14` WBD archive, inspect its schema, and verify coverage through HUC12.
- Fetch OSM and terrain coverage for the padded region extent and write the provenance manifest.
- Check nonempty layers, unique codes, expected code lengths, parent-prefix relationships, valid geometries, and child coverage against parents within documented geometric tolerance.
- Record gaps, overlaps, source-date differences, and any geometry repairs in the issue log rather than silently changing boundaries.

2026-11-13: downloaded the USGS region 14 WBD archive and inspected codes and geometries with [inspect_wbd.py](scripts/inspect_wbd.py).

- **Counts:** HUC2 1, HUC4 8, HUC6 10, HUC8 60, HUC10 524, HUC12 3,179.
- **Checks passed:** nonempty levels, unique codes, code lengths, region and parent prefixes, and individual geometry validity.
- **Remaining:** fetch OSM and terrain coverage; check spatial gaps and overlaps against parents; complete provenance manifest and coverage verification.

## 3.3. Build the shared map and prototype — **in progress**

- Calculate and persist one projected map extent and one raster grid.
- Generate shaded relief and simplified OSM context, with locally controlled label sizes.
- Render HUC2 and HUC12 prototypes to test both the sparse and dense cases.
- Inspect both at actual printed size for terrain contrast, line clarity, label collisions, and footer space.

## 3.4. Render and integrate the collection — **in progress**

- Render all six one-page sheets from the same extent, basemap, and layout configuration.
- Assemble the PDFs in increasing HUC order without changing page size or scale.
- Add the HTML overview, complete HUC lookup, and a reference-menu link.
- Record verified build commands and dependency versions in a short HUC README during implementation.

## 3.5. Acceptance checks and handoff — pending

- Confirm six individual PDFs with exactly one 612 × 792 pt page each, and one collection PDF with exactly six pages in the specified order.
- Compare saved bounds, projection, map-frame dimensions, and basemap checksum across all six pages.
- Verify page 1 contains only the `14` HUC region overlay, and each later page contains all and only its selected-level descendants.
- Check full-region coverage, legibility at 100% print size, greyscale rendering, font sizes, attribution, and label-omission disclosure.
- Verify the companion lookup covers all selected units and the HTML download links resolve.
- Rebuild from cached inputs without network access and confirm the same map framing and feature counts.
- Update this plan's progress states and the issue log with source versions, output paths, verification results, and remaining limitations.

# 4. Active build — 2026-11-13

- Entry point: `ref/huc/scripts/build_huc.py`; runs coverage checks, bounded USGS elevation and OSM Overpass acquisition, then shared-frame PDF rendering.
- Session: `tmux attach -t huc-build`, window `retry`.
- Log: `_outputs/experiments/huc/reference_sheets/build-retry.log`.
- Current verification: frame persisted; 3,782 units and 603 parent groups processed; source acquisition running at handoff.
- Expected outputs: `_site/ref/huc/huc02.pdf` through `huc12.pdf`, `upper-colorado-nested-hucs.pdf`, and `upper-colorado-huc-lookup.csv`.
- Expected prototypes: `_outputs/experiments/huc/reference_sheets/maps/huc02-preview.png` and `huc12-preview.png`.
- Expected evidence: build-root `topology.json`, `manifest.json`, and prepared `basemap.tif`; not yet verified.
- Acquisition refinement: use a bounded Overpass context extract and a 3DEP service raster sampled to print resolution, avoiding full-state downloads.
- Remaining after worker success: inspect prototypes and topology report, verify PDFs, render the Quarto HTML index, and update completed states.

- Elevation acquisition initially returned HTTP 504; bounded retry running in `huc-build:retry`, with topology results cached.

# 5. Map revision — 2026-11-13

- User direction: remove HUC labels from HUC6/HUC8/HUC10/HUC12; retain HUC2/HUC4 labels.
- Add dashed state borders from the Census 2024 1:500,000 cartographic boundary archive.
- Remove page titles, north arrows, and bottom notes; preserve common map frame and scale bar.
- Required map-data attribution moves to a compact vertical line along the page edge.
- Rebuild log: `_outputs/experiments/huc/reference_sheets/build-revision.log`.

- Revision rebuild completed successfully; HUC12 preview checked for absent labels and removed page furniture.

- Latest revision: lower-left identification added to each page: HUC level and total selected-unit count (1, 8, 10, 60, 524, 3,179).

# 6. Outlet annotation

- USGS generic term: [outlet point](https://water.usgs.gov/themes/hydrologic-units/).
- [USGS regional description](https://water.usgs.gov/GIS/huc_name.html) locates the regional division at the Lee Ferry compact point.
- Map marker: Colorado River intersection with the downloaded WBD HUC2 boundary, derived from cached OSM river geometry at longitude -111.588412863279, latitude 36.864589616780.
- Label: “Outlet — Lee Ferry area”; this mapped dataset intersection is not asserted to be the surveyed legal Compact point or a USGS gage location.
- The region also includes the internally draining Great Divide Basin; not every part drains through this outlet.

# 7. Nested outlet markers

- Collection limited to HU2/HU4/HU6/HU8 by user request.
- Open circle diameters: 22/15/10/6 pt, respectively; ancestor rings retained.
- Primary outlets inferred using upstream-area accumulation over WBD HU12 `tohuc` routing, then river crossings of the current unit boundary.
- Shared terminal HU12 outlets reuse coordinates for concentric rings.
- Closed basins and unresolved river crossings recorded in build-root `outlets.json`; no invented outlet markers.
- HU2 crossing retains the previously verified Lee Ferry area location.

- Rebuild complete: four sheets and collection; HU4 preview inspected.
- Coverage: 1/8/9/54 primary markers at HU2/4/6/8; one closed basin at HU6/8 and five unresolved HU8 crossings.

- Lower-left outlet legend added beneath the unit count, using matching open-circle sizes and only the HU levels shown on each page.

# 8. Full collection and page headings

- Restore all six pages: HUC2/4/6/8/10/12.
- Place the primary HUC level in a bold upper-right title; retain unit count at lower left.
- Show outlet markers and legends only on HUC2–HUC8 pages.
- Rebuild target: `_site/ref/huc/upper-colorado-nested-hucs.pdf`.
