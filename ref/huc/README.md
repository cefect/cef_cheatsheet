# 1. Status

Scaffold for the [Upper Colorado nested HUC reference sheets](plan.md).

| Stage | Status |
| --- | --- |
| 3.1 Environment and scaffold | Complete; dependency inventory and configuration recorded |
| 3.2 Data acquisition | In progress; WBD downloaded and inspected |
| 3.3–3.4 Maps and rendering | Build running; outputs unverified |
| 3.5 Acceptance | Pending |
| Data downloads / map products | WBD archive present; OSM, terrain, and map products pending |

# 2. Configuration

Use [config.yml](config.yml) as the shared input for future fetching and rendering scripts.

- **Region:** string code `14`, levels 2/4/6/8/10/12.
- **Frame:** EPSG:5070 with 5% padding on each side; numeric bounds remain null until stage 3.3 derives and persists them.
- **Layout:** 8.5 × 11 inches, 0.25-inch margins, identical 8 × 8.75-inch map slots.
- **Print:** greyscale, 12pt body/map labels, 8pt footnotes, 300 dpi terrain.
- **Paths:** repository-relative; downloads and map intermediates use the ignored build root.
- **Output indexes:** future producers must create README indexes for their managed directories.

# 3. Environment inventory

Verified on CEFTOP WSL on 2026-11-13; no software installed or environments changed.

| Capability | Available version / location | Finding |
| --- | --- | --- |
| Python | System Python 3.12.3 | Use explicit `python3`; `python` is absent |
| YAML | System PyYAML 6.0.1 | Configuration reader available |
| Vector/raster processing | System GDAL/OGR 3.8.4 | Python bindings, OSM reader, and PDF driver available |
| Projection | System pyproj 3.6.1 | Available |
| Plotting | System Matplotlib 3.6.3; Pillow 10.2.0 | Available |
| Quarto | `cef_cheatsheet` Conda environment, 1.9.38 | Version/help work with supported path overrides; see runbook |
| Typst | `cef_cheatsheet` Conda environment, 0.14.2 | Direct executable version and compile help verified |
| PDF assembly/inspection | `pypdf`, `pdfinfo`, `qpdf`, and Ghostscript absent | Recommend `pypdf` before stages 3.4–3.5 |

Notes:
- The existing Conda environment contains publishing tools and no Python interpreter; geospatial checks used `/usr/bin/python3`.
- GeoPandas, Shapely, Rasterio, Pyogrio, and Pyosmium are absent from system Python; the initial implementation can use installed GDAL/OGR rather than requiring these wrappers.
- Proposed dependency addition: a project-local `.venv` with system-site-packages for existing GDAL and plotting support, plus `pypdf` for PDF concatenation and inspection.
- Installation requires explicit user approval; it is not needed to validate this configuration.
- Quarto version/help checks do not establish that a full PDF render works; verify rendering in stage 3.3.
- Startup procedure and limits: [Quarto Conda runbook](../../.agents/runbooks/quarto-conda.md).

# 4. Development records

Track progress in [the plan](plan.md) and evidence in [HUC-001 / ENV-001](../../issues.md).

- The WBD inspection script reads the downloaded archive and writes `wbd_inspection.json` in the ignored build root.
- No build commands are documented as working before a real build exists.

# 5. Active build

- Attach: `tmux attach -t huc-build`, window `retry`.
- Follow: `tail -f _outputs/experiments/huc/reference_sheets/build-retry.log`.
- Build entry point: `python3 ref/huc/scripts/build_huc.py`.
- Downloads are cached; network is needed for uncached sources.
- Six PDFs and collection are expected under `_site/ref/huc/`; successful completion and visual review remain pending.
- Matplotlib assembles the collection directly, removing the need for a PDF-merging dependency.

- Elevation acquisition initially returned HTTP 504; bounded retry running in `huc-build:retry`, with topology results cached.
