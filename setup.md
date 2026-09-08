# Setup and hosting

This repository uses Quarto to render the site and GitHub Actions to publish it to GitHub Pages.

## Prerequisites

Install Quarto and authenticate the GitHub CLI:

```bash
quarto --version
gh auth login
```

## Work locally

Start a live preview from the repository root:

```bash
quarto preview
```

Render a static site without starting a server:

```bash
quarto render
```

The generated files are written to `_site/` and are intentionally not committed.

## One-time GitHub Pages setup

After the repository exists on GitHub, configure Pages to use GitHub Actions:

1. Open the repository on GitHub.
2. Go to **Settings** → **Pages**.
3. Under **Build and deployment**, choose **GitHub Actions** as the source.
4. Push to `main`; the **Deploy Quarto site to Pages** workflow will build and deploy the site.

If Pages is already enabled, the source can also be configured from the command line:

```bash
gh api --method POST "repos/OWNER/REPOSITORY/pages" --raw-field build_type=workflow
```

Replace `OWNER/REPOSITORY` with the GitHub repository slug.

## Publish updates

Edit a `.qmd` file, preview locally, then commit and push:

```bash
git add .
git commit -m "Update cheat sheet"
git push
```

The published URL appears in the GitHub Actions deployment summary and in **Settings** → **Pages**.

