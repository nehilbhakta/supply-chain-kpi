"""Verify the supply chain KPI project outputs.

Checks: CSVs exist and load, row counts are sane, dates are in range, KPI
outputs exist and are non-empty, and headline numbers are internally
consistent (OTD in [0,100], worst supplier below network average).

Usage:  python tests/verify.py   (run from the project root)
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
failures = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")
    if not ok:
        failures.append(name)


po = pd.read_csv(ROOT / "data/purchase_orders.csv", parse_dates=["order_date", "promised_eta", "actual_delivery_date"])
inv = pd.read_csv(ROOT / "data/inventory.csv", parse_dates=["snapshot_date"])
pc = pd.read_csv(ROOT / "data/price_changes.csv", parse_dates=["change_date"])

check("purchase_orders loads", len(po) > 500, f"{len(po)} rows")
check("inventory loads", len(inv) > 500, f"{len(inv)} rows")
check("price_changes loads", len(pc) > 20, f"{len(pc)} rows")
check("PO dates in May-Oct 2026",
      po["order_date"].min() >= pd.Timestamp("2026-05-01") and po["order_date"].max() <= pd.Timestamp("2026-10-31"),
      f"{po['order_date'].min().date()} to {po['order_date'].max().date()}")
check("10 suppliers", po["supplier_code"].nunique() == 10)
check("3 sites", po["site"].nunique() == 3)
check("40 SKUs", po["sku"].nunique() == 40)
check("no missing actual delivery dates", po["actual_delivery_date"].notna().all())
check("on_time flag consistent",
      ((po["actual_delivery_date"] <= po["promised_eta"]) == po["on_time"]).all())
check("inventory snapshot months = 6", inv["snapshot_date"].dt.to_period("M").nunique() == 6)
check("no negative quantities", (po["quantity"] > 0).all() and (inv["on_hand_qty"] >= 0).all())

for f in ["kpi_summary.csv", "kpi_by_site.csv", "stockout_risk_skus.csv"]:
    p = ROOT / f
    check(f"{f} exists and non-empty", p.exists() and p.stat().st_size > 0)

kpi = pd.read_csv(ROOT / "kpi_summary.csv")
check("kpi_summary has 10 suppliers", len(kpi) == 10)
check("OTD in [0,100]", kpi["on_time_delivery_pct"].between(0, 100).all())
network_otd = round(po["on_time"].mean() * 100, 1)
check("worst supplier below network OTD",
      kpi["on_time_delivery_pct"].min() < network_otd,
      f"worst {kpi['on_time_delivery_pct'].min()}% vs network {network_otd}%")
check("stockout-risk file non-empty", len(pd.read_csv(ROOT / "stockout_risk_skus.csv")) > 0)

print()
if failures:
    print(f"{len(failures)} check(s) FAILED: {failures}")
    sys.exit(1)
print("All checks passed.")
