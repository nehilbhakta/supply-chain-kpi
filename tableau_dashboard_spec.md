# Tableau Dashboard Spec — Supply Chain KPI Dashboard

**No Tableau workbook exists in this repo.** This spec describes the dashboard
to build in Tableau Public from the CSVs in `data/`. It is written so the
build is mechanical: data sources, views, filters, and calculations are all
specified here.

## Data sources

Connect Tableau to the three CSVs and join/blend on the shared keys:

| Source | Grain | Join keys |
|---|---|---|
| `purchase_orders.csv` | PO line | `supplier_code`, `site`, `sku` |
| `inventory.csv` | site × SKU × month | `site`, `sku`, `snapshot_date` |
| `price_changes.csv` | price change | `supplier_code`, `sku` |

Calculated fields (names as written here):
- `On-Time` = `IF [Actual Delivery Date] <= [Promised ETA] THEN 1 ELSE 0 END`
- `OTD %` = `SUM([On-Time]) / COUNT([Po Id])`
- `Lead-Time Variance (days)` = `DATEDIFF('day', [Promised ETA], [Actual Delivery Date])`
- `Line Value` = `[Quantity] * [Unit Price Usd]`
- `Stockout Risk` = `IF [On Hand Qty] < [Safety Stock Qty] THEN 1 ELSE 0 END`
- `Excess Value` = `MAX([On Hand Qty] - [Reorder Point Qty], 0) * [Unit Price Usd]`
- `Price Change %` = `([New Unit Price Usd] - [Old Unit Price Usd]) / [Old Unit Price Usd]`

## Dashboard layout (one dashboard, 6 views)

1. **KPI header band** — big-number tiles: network OTD %, total POs, total
   spend, stockout-risk SKUs, excess inventory value, average price change.
2. **Supplier ETA** — bar chart of OTD % by supplier, coloured red below 85%,
   amber 85–92%, green above 92%; tooltip shows POs, avg lead-time variance,
   defect rate. Sorted worst-first so the problem supplier is visible.
3. **Inventory by site / vendor** — heatmap: sites × categories, cell colour =
   stockout-risk SKU count; side table of on-hand vs safety stock by site.
4. **Stockout risk** — table of the 9 at-risk SKUs (latest snapshot): site,
   SKU, on-hand, safety stock, days of cover (`on_hand / avg_daily_usage`).
5. **Excess inventory** — bar chart of excess inventory value by site and by
   category; reference line at the network median.
6. **Forecast vs orders** — line chart by month: forecasted demand
   (`avg_daily_usage × days in month`) vs actual ordered quantity, per
   category; gap highlighted where orders ran ahead of forecast.

## Filters (apply to all views)

- Site (PHX-01 / PHX-02 / TEM-01)
- Supplier (multi-select)
- Date range (order date, May–Oct 2026)
- Category

## Publishing

Publish to Tableau Public with the title "Supply Chain KPI Dashboard —
Simulated Procurement Data (May–Oct 2026)" and a caption on the dashboard
stating the data is simulated. Expected build time: 2–3 hours from these CSVs.
