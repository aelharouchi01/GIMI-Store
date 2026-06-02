# GIMI Store Code

All source files for the GIMI online store landing page.

## What to deploy

The site is a single self-contained page plus its assets, both at the repo root:
- `index.html` — the store page (all CSS + JS + product data inline)
- `gimi-store-assets/` — only the images the page actually uses

To publish: drag `index.html` and `gimi-store-assets/` (or the whole repo) onto Netlify
or any static host. No build step.

## Folder structure

| Path | Contents |
|---|---|
| `index.html` | The store page (single self-contained HTML file with all CSS + JS + product data inline) |
| `gimi-store-assets/` | Only the images used by the page: 2 root files (`gimi-logo-white.png`, `2x.jpeg`) + `v2/` (63 product badges & book covers). Pruned to used-only on 2026-06-02. |
| `scripts/` | Python + Node scripts used to build, patch, and audit the store and the catalogue deck |
| `data/` | Extracted source-of-truth data (deck prices, descriptions, storylines, taxonomy) in JSON |
| `blueprints/` | Word-doc structure blueprints (v10 is latest) |

Note: assets are kept used-only — re-run `scripts/clean_assets.py` (dry-run by default,
`RUN` to apply) after adding/removing products to prune anything `index.html` no longer references.

## Source-of-truth rules (as of V64 audit)

- **Pricing** — Training Prices sheet / V64 deck (cert + training price per course)
- **Descriptions** — CRM sheet for courses; V64 deck for the two masterclasses
- **Durations** — CRM "Hours" column for courses; V64 deck for masterclasses
- **Process & Examination cards, storylines, includes** — V64 deck

## Product structure (65 products, 8 groups)

Innovation Core (10) · Innovation Elective (10) · Future Foresight (5) · Leadership Core (2) ·
Consulting Core (4) · Books & Guides (13) · Programs & Tools (13) · Memberships (8)

## How the page works

`index.html` is one file. Near the bottom, the `PRODUCTS = [ ... ]` array holds every
product's data (title, code, prices, duration, description, includes, eligibility, badge path).
The rendering functions build the grid cards and the detail modal from that array. To change a
product, edit its `mk({ ... })` entry. No build step is required to view the page.

## Key scripts (in `scripts/`)

- `audit_v64.py` — full QA: compares the store against the deck (prices, descriptions, durations, cards)
- `extract_v64*.py` — pull structured data out of the catalogue PPTX
- `apply_v64_batch.py`, `rebuild_cards.py`, `patch_taxonomy.py` — apply deck data into the store HTML
- `build_blueprint.js` — regenerate the Word blueprint (needs `npm install docx`)
- `build_deck_v3.py` — generate the product-catalogue PowerPoint (needs `python-pptx`)

Note: `node_modules/` is intentionally not included. Run `npm install` inside `scripts/` if you
need the Node tooling (`docx`, etc.).
