# Deploying the Supply Chain KPI dashboard (static site)

Repo: **nehilbhakta/supply-chain-kpi**, branch `main`. The dashboard is a
single self-contained file, `site/index.html` — no framework, no build step,
no backend, no env vars. All numbers come from the repo's own verified files
(`kpi_summary.csv`, `kpi_by_site.csv`, `stockout_risk_skus.csv`,
`supplier_scorecard.md`) and the page is labelled SIMULATED DATA throughout.

## Vercel (static)

Vercel Dashboard → Add New → Project → Import `nehilbhakta/supply-chain-kpi`.

| Setting | Value |
|---|---|
| Framework Preset | Other (no framework — **not** Next.js) |
| Root Directory | `site/` |
| Build Command | (empty — no build step) |
| Output Directory | (leave default — the root of `site/`, i.e. `.` — do not set it to anything else) |
| Install Command | (empty — no dependencies) |
| Environment Variables | none |

The live URL serves `site/index.html` at `/`. Verify the amber
“SIMULATED DATA” banner is visible at the top and the headline tiles read
732 POs, $13,770,255 spend, 90.2% on-time delivery, Desert Freight Logistics
69.1% OTD, 9 stockout-risk SKUs, $586,612 excess inventory.

## Alternative — GitHub Pages (no Vercel account needed)

Repo Settings → Pages → Source: Deploy from a branch → Branch `main`,
folder `/site`. The same `index.html` is served at
`https://nehilbhakta.github.io/supply-chain-kpi/`.

## Updating the numbers

Edit the CSVs / re-run `python analysis.py`, then update `site/index.html`
to match — the page is hand-written from the CSVs, not generated, so the two
can drift if only one is updated.
