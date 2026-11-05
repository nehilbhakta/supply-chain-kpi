"""Compute supply chain KPIs from the simulated dataset.

Reads data/purchase_orders.csv, data/inventory.csv, data/price_changes.csv,
prints a summary, and writes kpi_summary.csv (one row per supplier, plus
per-site rows in kpi_by_site.csv).

Metric definitions live in data/data_dictionary.md.

Usage:  python analysis.py
"""
import pandas as pd

po = pd.read_csv("data/purchase_orders.csv", parse_dates=["order_date", "promised_eta", "actual_delivery_date"])
inv = pd.read_csv("data/inventory.csv", parse_dates=["snapshot_date"])
pc = pd.read_csv("data/price_changes.csv", parse_dates=["change_date"])

po["lead_time_variance_days"] = (po["actual_delivery_date"] - po["promised_eta"]).dt.days
po["line_value_usd"] = po["quantity"] * po["unit_price_usd"]
po["defect_rate"] = po["defective_qty"] / po["quantity"]

# ---------------------------------------------------------------- per supplier
sup = po.groupby(["supplier_code", "supplier_name"]).agg(
    total_pos=("po_id", "count"),
    total_spend_usd=("line_value_usd", "sum"),
    on_time_delivery_pct=("on_time", lambda s: round(s.mean() * 100, 1)),
    avg_lead_time_variance_days=("lead_time_variance_days", lambda s: round(s.mean(), 2)),
    avg_lead_time_days=("lead_time_days", lambda s: round(s.mean(), 1)),
    defect_rate_pct=("defect_rate", lambda s: round(s.mean() * 100, 2)),
).reset_index()

price = pc.groupby(["supplier_code", "supplier_name"]).agg(
    price_changes=("change_id", "count"),
    avg_price_change_pct=("change_pct", lambda s: round(s.mean(), 2)),
    max_price_change_pct=("change_pct", "max"),
).reset_index()
sup = sup.merge(price, on=["supplier_code", "supplier_name"], how="left").fillna({"price_changes": 0})

# stockout-risk and excess inventory are site/SKU level; attribute to the
# supplier of the most recent PO for that SKU at that site (latest snapshot).
latest_inv = inv.sort_values("snapshot_date").groupby(["site", "sku"]).tail(1).copy()
latest_inv["stockout_risk"] = latest_inv["on_hand_qty"] < latest_inv["safety_stock_qty"]
latest_inv["excess_qty"] = (latest_inv["on_hand_qty"] - latest_inv["reorder_point_qty"]).clip(lower=0)
latest_inv["excess_value_usd"] = latest_inv["excess_qty"] * latest_inv["unit_price_usd"]

# ---------------------------------------------------------------- per site
site = po.groupby("site").agg(
    total_pos=("po_id", "count"),
    total_spend_usd=("line_value_usd", "sum"),
    on_time_delivery_pct=("on_time", lambda s: round(s.mean() * 100, 1)),
    avg_lead_time_variance_days=("lead_time_variance_days", lambda s: round(s.mean(), 2)),
).reset_index()
site_inv = latest_inv.groupby("site").agg(
    stockout_risk_skus=("stockout_risk", "sum"),
    total_skus=("sku", "count"),
    excess_inventory_value_usd=("excess_value_usd", lambda s: round(s.sum(), 2)),
).reset_index()
site = site.merge(site_inv, on="site")

# ---------------------------------------------------------------- headline numbers
total_pos = len(po)
otd = round(po["on_time"].mean() * 100, 1)
total_spend = round(po["line_value_usd"].sum(), 2)
stockout_n = int(latest_inv["stockout_risk"].sum())
excess_total = round(latest_inv["excess_value_usd"].sum(), 2)
avg_price_chg = round(pc["change_pct"].mean(), 2)
worst = sup.sort_values("on_time_delivery_pct").iloc[0]

print("=" * 72)
print("SUPPLY CHAIN KPI SUMMARY  (SIMULATED DATA, May-Oct 2026)")
print("=" * 72)
print(f"Purchase orders analysed : {total_pos}")
print(f"Total spend (PO lines)   : ${total_spend:,.2f}")
print(f"On-time delivery (all)   : {otd}%")
print(f"Stockout-risk SKUs       : {stockout_n} of {len(latest_inv)} site-SKUs (latest snapshot)")
print(f"Excess inventory value   : ${excess_total:,.2f}")
print(f"Average price change     : {avg_price_chg}% across {len(pc)} changes")
print(f"Worst supplier (OTD)     : {worst['supplier_name']} ({worst['supplier_code']}) — "
      f"{worst['on_time_delivery_pct']}% on-time, "
      f"+{worst['avg_lead_time_variance_days']} days avg late")
print()
print("--- Per supplier ---")
print(sup.sort_values("on_time_delivery_pct").to_string(index=False))
print()
print("--- Per site ---")
print(site.to_string(index=False))

sup.sort_values("on_time_delivery_pct").to_csv("kpi_summary.csv", index=False)
site.to_csv("kpi_by_site.csv", index=False)
latest_inv[latest_inv["stockout_risk"]].to_csv("stockout_risk_skus.csv", index=False)
print()
print("Wrote kpi_summary.csv, kpi_by_site.csv, stockout_risk_skus.csv")
