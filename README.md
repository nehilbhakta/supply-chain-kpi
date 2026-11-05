# Supply Chain KPI Dashboard — Simulated Procurement Data

A complete supply chain analytics project: a reproducible simulated
procurement dataset, KPI analysis in Python/pandas, a supplier scorecard with
a root-cause miss report, and a build spec for a Tableau Public dashboard.

> **All data in this project is SIMULATED.** It was generated with a fixed
> random seed to stand in for procurement data from source systems such as
> Coupa and Delphi. No real Amazon, supplier, or pricing data is used.
> The word "simulated" appears in the data files, the analysis output, and
> the dashboard spec so the dataset is never mistaken for real data.

## What is in here

| File | What it is |
|---|---|
| `generate_data.py` | Deterministic generator (seed 42): 10 suppliers, 3 sites, 40 SKUs, May–Oct 2026 |
| `data/purchase_orders.csv` | 732 PO lines: order date, promised ETA, actual delivery, qty, price, defects |
| `data/inventory.csv` | 720 monthly snapshots: on-hand, safety stock, reorder point per site × SKU |
| `data/price_changes.csv` | 84 supplier price changes with reasons |
| `data/data_dictionary.md` | Every column and every KPI, with formulas and refresh cadence |
| `analysis.py` | pandas KPI computation; prints a summary and writes `kpi_summary.csv`, `kpi_by_site.csv`, `stockout_risk_skus.csv` |
| `supplier_scorecard.md` | Supplier ranking + miss-report deep dive on the worst performer |
| `tableau_dashboard_spec.md` | How to build the dashboard in Tableau Public (no workbook is included) |
| `tests/verify.py` | Sanity checks on the data and KPI outputs |

## Headline findings (simulated data, May–Oct 2026)

- **732 purchase orders, $13.77M spend, 90.2% on-time delivery** network-wide
- **Worst supplier: Desert Freight Logistics (SUP-07)** — 69.1% on-time,
  +1.68 days average lateness, 4.00% defect rate, +9.68% average price
  increases — the subject of the miss report in `supplier_scorecard.md`
- **9 stockout-risk SKUs** in the October snapshot (7 of them at PHX-02),
  including nitrile gloves at 22 on hand vs 132 safety stock
- **$586,612 of excess inventory** above reorder points, largest at TEM-01

## How to run it

```bash
python generate_data.py   # regenerate the dataset (deterministic, seed 42)
python analysis.py        # print KPIs, write kpi_summary.csv etc.
python tests/verify.py    # sanity-check the data and outputs
```

Requires Python 3.10+ with pandas and numpy (`pip install pandas numpy`).

## How this maps to a Supply Chain Analyst role

- **KPI dashboards as a single source of truth** — on-time delivery, lead-time
  variance, stockout risk, excess inventory, price variance, each with a
  written definition, formula, and refresh cadence (`data/data_dictionary.md`).
- **Supplier and inventory visibility** — per-supplier and per-site views,
  with the Tableau spec covering supplier ETA, inventory by site/vendor,
  stockout risk, excess inventory, and forecast vs orders.
- **Deep dives and miss reports** — the scorecard's root-cause analysis on
  SUP-07 follows the miss-report format: what happened, the trend, the
  scope, the operational impact, a hypothesis clearly labelled as one, and
  prevention recommendations.
- **Data accuracy and governance** — `tests/verify.py` checks the data
  against its own rules (dates in range, on-time flag consistent with the
  dates, no missing deliveries), the same audit habit the role asks for.

## Limitations (honest ones)

- The data is simulated, so the findings describe the generator's assumptions,
  not a real operation — most visibly, one supplier was deliberately made
  unreliable, so the "worst performer" is by design, not discovery.
- Spend is illustrative: order quantities and unit prices were drawn from
  broad ranges, so the $13.77M total is large for consumables and should not
  be quoted as a real-world figure.
- Forecast vs orders is defined from average daily usage (the planning
  assumption in the data), not from a real forecast feed — a real deployment
  would measure forecast accuracy (MAPE) against the planning system's feed.
- The Tableau dashboard is a spec, not a workbook — building it in Tableau
  Public is the natural next step (2–3 hours from these CSVs).
