"""Generate the simulated procurement dataset for the Supply Chain KPI project.

SIMULATED DATA — no real Amazon, supplier, or pricing data is used anywhere
in this project. The generator is deterministic: fixed seed (42), so anyone
re-running it gets byte-identical CSVs.

Entities
--------
- 10 suppliers, each with a reliability profile (on-time probability, lead-time
  mean/spread, defect rate). One supplier (SUP-07, "Desert Freight Logistics")
  is deliberately unreliable — it becomes the worst performer in the scorecard.
- 3 sites: PHX-01 (Phoenix), PHX-02 (Phoenix), TEM-01 (Tempe).
- 40 SKUs across 5 categories: Packaging, Cleaning, Safety, Office, MRO.
- ~6 months: 2026-05-01 to 2026-10-31.

Outputs (data/)
----------
- purchase_orders.csv : one row per PO line (~600 rows)
- inventory.csv       : monthly snapshots, one row per site x SKU x month
- price_changes.csv   : supplier price changes over the period

Usage:  python generate_data.py
"""
import random
from datetime import date, timedelta

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)
random.seed(SEED)

START = date(2026, 5, 1)
END = date(2026, 10, 31)
MONTHS = pd.period_range(START, END, freq="M")

SUPPLIERS = [
    # code, name, on-time prob, lead-time mean days, lead-time sd, defect rate
    ("SUP-01", "Sonoran Packaging Co",      0.97, 5, 1.0, 0.004),
    ("SUP-02", "Valley Industrial Supply",  0.94, 7, 1.5, 0.008),
    ("SUP-03", "Copper State Safety Gear",  0.95, 6, 1.2, 0.006),
    ("SUP-04", "Desert Office Products",    0.93, 4, 1.0, 0.010),
    ("SUP-05", "Arizona MRO Services",      0.90, 8, 2.0, 0.012),
    ("SUP-06", "Grand Canyon Chemicals",    0.92, 9, 2.2, 0.009),
    ("SUP-07", "Desert Freight Logistics",  0.68, 12, 4.5, 0.041),
    ("SUP-08", "Phoenix Pallet & Crate",    0.96, 5, 1.1, 0.005),
    ("SUP-09", "Southwest Janitorial Co",   0.91, 6, 1.8, 0.011),
    ("SUP-10", "Mesa Fasteners & Tools",    0.95, 4, 0.9, 0.007),
]
SITES = ["PHX-01", "PHX-02", "TEM-01"]

CATEGORIES = {
    "Packaging": ["Cardboard boxes (24x18x12)", "Stretch wrap rolls", "Shipping tape",
                  "Pallets (48x40)", "Bubble wrap", "Mailers (padded)",
                  "Labels (4x6)", "Strapping bands"],
    "Cleaning": ["Floor cleaner (5 gal)", "Disinfectant spray", "Paper towels (case)",
                 "Trash bags (55 gal)", "Mop heads", "Degreaser",
                 "Hand soap (1 gal)", "Broom & dustpan sets"],
    "Safety": ["Nitrile gloves (box)", "Safety glasses", "Hi-vis vests",
               "Ear plugs (box)", "First-aid kits", "Hard hats",
               "Safety cones", "Spill kits"],
    "Office": ["Printer paper (ream)", "Ink cartridges", "Pens (box)",
               "Folders", "Sticky notes", "Binders",
               "Envelopes", "Desk organizers"],
    "MRO": ["LED bulbs (pack)", "Batteries (AA, pack)", "Duct tape",
            "Cable ties (pack)", "Lubricant spray", "Air filters",
            "Light switches", "Extension cords"],
}

# ---------------------------------------------------------------- SKUs
skus = []
for cat, items in CATEGORIES.items():
    for i, item in enumerate(items, 1):
        code = f"SKU-{cat[:3].upper()}-{i:02d}"
        unit_price = round(float(rng.uniform(4, 180)), 2)
        daily_use = int(rng.integers(2, 25))
        skus.append({
            "sku": code, "description": item, "category": cat,
            "unit_price_usd": unit_price, "avg_daily_usage": daily_use,
            "lead_time_days": int(rng.integers(3, 12)),
        })
SKU_DF = pd.DataFrame(skus)
SKU_BY_CODE = SKU_DF.set_index("sku")

# ---------------------------------------------------------------- purchase orders
po_rows = []
po_id = 1000
d = START
while d <= END:
    # 3-5 PO lines per day
    for _ in range(int(rng.integers(3, 6))):
        sup = SUPPLIERS[int(rng.integers(0, len(SUPPLIERS)))]
        code, name, otp, lt_mean, lt_sd, defect = sup
        sku = SKU_DF.iloc[int(rng.integers(0, len(SKU_DF)))]
        site = SITES[int(rng.integers(0, len(SITES)))]
        qty = int(rng.integers(10, 400))
        promised_lead = max(1, int(round(rng.normal(lt_mean, lt_sd))))
        promised_eta = d + timedelta(days=promised_lead)
        on_time = rng.random() < otp
        if on_time:
            # on-time means delivered on or before the promised ETA
            actual_lead = promised_lead - int(rng.integers(0, 2))
        else:
            actual_lead = promised_lead + int(rng.integers(2, 12))
        actual_delivery = d + timedelta(days=actual_lead)
        defective_qty = int(rng.binomial(qty, defect))
        po_rows.append({
            "po_id": f"PO-{po_id}", "order_date": d.isoformat(),
            "site": site, "supplier_code": code, "supplier_name": name,
            "sku": sku["sku"], "description": sku["description"],
            "category": sku["category"], "quantity": qty,
            "unit_price_usd": round(float(sku["unit_price_usd"] *
                                          rng.normal(1.0, 0.03)), 2),
            "promised_eta": promised_eta.isoformat(),
            "actual_delivery_date": actual_delivery.isoformat(),
            "lead_time_days": actual_lead,
            "promised_lead_time_days": promised_lead,
            "on_time": bool(on_time),
            "defective_qty": defective_qty,
        })
        po_id += 1
    d += timedelta(days=1)

po_df = pd.DataFrame(po_rows)

# ---------------------------------------------------------------- inventory snapshots
inv_rows = []
for month in MONTHS:
    month_end = month.end_time.date()
    for site in SITES:
        for _, sku in SKU_DF.iterrows():
            safety = sku["avg_daily_usage"] * sku["lead_time_days"]
            reorder = safety + sku["avg_daily_usage"] * 3
            # on-hand: mostly healthy, sometimes below safety stock
            roll = rng.random()
            if roll < 0.12:
                on_hand = int(rng.integers(0, max(1, safety)))
            elif roll < 0.30:
                on_hand = int(safety * rng.uniform(1.0, 1.8))
            else:
                on_hand = int(reorder * rng.uniform(1.0, 2.2))
            inv_rows.append({
                "snapshot_date": month_end.isoformat(), "site": site,
                "sku": sku["sku"], "description": sku["description"],
                "category": sku["category"], "on_hand_qty": on_hand,
                "safety_stock_qty": int(safety),
                "reorder_point_qty": int(reorder),
                "unit_price_usd": sku["unit_price_usd"],
                "avg_daily_usage": int(sku["avg_daily_usage"]),
            })
inv_df = pd.DataFrame(inv_rows)

# ---------------------------------------------------------------- price changes
pc_rows = []
pc_id = 1
for _ in range(84):
    sup = SUPPLIERS[int(rng.integers(0, len(SUPPLIERS)))]
    sku = SKU_DF.iloc[int(rng.integers(0, len(SKU_DF)))]
    change_date = START + timedelta(days=int(rng.integers(0, 183)))
    old = round(float(sku["unit_price_usd"] * rng.normal(1.0, 0.05)), 2)
    # SUP-07 raises prices more often / more steeply
    pct = float(rng.normal(0.09 if sup[0] == "SUP-07" else 0.03, 0.04))
    new = round(old * (1 + pct), 2)
    pc_rows.append({
        "change_id": f"PC-{pc_id:03d}", "change_date": change_date.isoformat(),
        "supplier_code": sup[0], "supplier_name": sup[1],
        "sku": sku["sku"], "description": sku["description"],
        "old_unit_price_usd": old, "new_unit_price_usd": new,
        "change_pct": round((new - old) / old * 100, 2),
        "reason": random.choice(["Raw material cost increase", "Fuel surcharge",
                                 "Contract renegotiation", "Supplier list-price update",
                                 "Volume discount ended"]),
    })
    pc_id += 1
pc_df = pd.DataFrame(pc_rows).sort_values("change_date").reset_index(drop=True)

# ---------------------------------------------------------------- write
po_df.to_csv("data/purchase_orders.csv", index=False)
inv_df.to_csv("data/inventory.csv", index=False)
pc_df.to_csv("data/price_changes.csv", index=False)
print(f"purchase_orders.csv: {len(po_df)} rows")
print(f"inventory.csv:       {len(inv_df)} rows")
print(f"price_changes.csv:   {len(pc_df)} rows")
print(f"suppliers: {len(SUPPLIERS)}, sites: {len(SITES)}, SKUs: {len(SKU_DF)}")
print(f"period: {START} to {END}")
