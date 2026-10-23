# CEF Cheat Sheet

Quarto source for a compact, GitHub Pages-hosted cheat sheet.

[CEF Cheat Sheet](https://cefect.github.io/cef_cheatsheet/)

## Development environment

Conda env with Quarto (bundles Pandoc and Typst) from [environment.yml](environment.yml).

```bash
# create once (or update after editing environment.yml)
conda env create -f environment.yml
conda env update -f environment.yml --prune

# activate and confirm
conda activate cef_cheatsheet
quarto --version
```

## Local preview

From the activated env:

```bash
quarto preview
```

The preview server opens the rendered site and refreshes when source files change.

## Reference sheets

- Non-command sheets live in [ref/](ref/).
- Each renders to HTML plus a one-page US Letter PDF (Typst), linked from the page.
- Shared print settings: [ref/_metadata.yml](ref/_metadata.yml) and [ref/sheet.typ](ref/sheet.typ).
- Landscape sheets add `include-in-header: landscape.typ` under `format: typst:`.
- Tables are pandoc grid tables; end a cell line with `\` for a hard line break.
- After edits, render one sheet's PDF to `_site/ref/` and confirm it is still one page:

```bash
quarto render ref/dtypes.qmd --to typst
```

## Publishing

The GitHub Actions workflow publishes changes pushed to `main`.

See [setup.md](setup.md) for the one-time GitHub Pages setup and manual publishing commands.

