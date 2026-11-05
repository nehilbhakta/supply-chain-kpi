# Supplier Scorecard — May–Oct 2026

**SIMULATED DATA.** Rankings computed by `analysis.py` from
`data/purchase_orders.csv`, `data/inventory.csv`, `data/price_changes.csv`.
Full table: `kpi_summary.csv`. Network on-time delivery: **90.2%** (732 POs).

| Rank | Supplier | POs | Spend | OTD % | Avg late (days) | Defect % | Avg price change % |
|---|---|---|---|---|---|---|---|
| 1 | Phoenix Pallet & Crate (SUP-08) | 80 | $1,351,059 | 97.5 | -0.22 | 0.44 | +3.48 |
| 2 | Mesa Fasteners & Tools (SUP-10) | 64 | $1,355,104 | 96.9 | -0.31 | 0.89 | +5.04 |
| 3 | Sonoran Packaging Co (SUP-01) | 71 | $1,480,204 | 95.8 | -0.41 | 0.47 | -0.03 |
| 4 | Valley Industrial Supply (SUP-02) | 72 | $1,332,198 | 95.8 | -0.22 | 0.86 | +4.70 |
| 5 | Copper State Safety Gear (SUP-03) | 73 | $1,191,663 | 94.5 | -0.08 | 0.67 | +2.59 |
| 6 | Grand Canyon Chemicals (SUP-06) | 67 | $1,229,881 | 94.0 | -0.24 | 0.94 | +3.88 |
| 7 | Desert Office Products (SUP-04) | 64 | $1,226,690 | 90.6 | +0.03 | 0.83 | +5.39 |
| 8 | Southwest Janitorial Co (SUP-09) | 73 | $1,327,057 | 86.3 | +0.48 | 1.09 | +2.71 |
| 9 | Arizona MRO Services (SUP-05) | 87 | $1,730,386 | 85.1 | +0.33 | 1.18 | +2.20 |
| 10 | **Desert Freight Logistics (SUP-07)** | 81 | $1,546,014 | **69.1** | **+1.68** | 4.00 | +9.68 |

## Miss report — deep dive: Desert Freight Logistics (SUP-07)

**What happened.** SUP-07 delivered on time on only 69.1% of its 81 POs,
21 points below the network average (90.2%) and 16 points below the next-worst
supplier (SUP-05, 85.1%). 25 of 81 deliveries were late; 15 were more than
5 days late, with a maximum of 11 days late. Average lateness was +1.68 days,
more than triple the next-worst supplier (+0.48). The problem is network-wide,
not site-specific: OTD was 70.8% at PHX-01, 66.7% at PHX-02 and 70.0% at TEM-01.

**It is getting worse, not better.** Monthly OTD: May 78.9% → Jun 37.5% →
Jul 82.4% → Aug 61.5% → Sep 60.0% → Oct 71.4%. The June collapse (37.5%)
and the sub-72% readings in four of six months rule out a single bad week.

**It is not one category.** Packaging is worst (52.9% OTD, 17 POs), but
MRO (68.8%), Cleaning (73.3%), Safety (75.0%) and Office (76.5%) are all
below the network average — the failure is systemic across the supplier's
operation, not a single product line.

**Quality and price are failing too.** Defect rate is 4.00% (652 defective
units of 15,682) — about 4× the next-worst supplier and 9× the best.
Average price increase is +9.68% across 7 changes, the highest in the
network, with individual increases up to +13.59% (Oct 25, strapping bands,
"contract renegotiation"). The supplier is simultaneously the least reliable,
the lowest quality, and the most expensive on price movement.

**Operational impact.** SUP-07 is the 3rd-largest spend in the network
($1.55M). Its late deliveries are a plausible contributor to the 7
stockout-risk SKUs at PHX-02 in the October snapshot — including nitrile
gloves (22 on hand vs 132 safety stock) — though the inventory file does not
attribute stockouts to a supplier, so that link is a hypothesis to verify,
not a finding.

**Root-cause hypothesis (to confirm with the supplier, not assumed).**
The pattern — lateness across all sites and categories, a June cliff, high
defects, and repeated price increases citing fuel and contract costs —
points to a capacity or subcontracting problem rather than a routing issue:
the supplier appears to be accepting more volume than it can fulfil and
passing cost pressure through as price increases. This needs a supplier
business review to confirm; the data alone cannot prove the cause.

## Prevention recommendations

1. **Immediate (this week):** put SUP-07 on a weekly performance watch —
   OTD, late-days and defect rate reported every Monday until OTD recovers
   above 85% for four consecutive weeks.
2. **Short term (30 days):** dual-source the Packaging SKUs (worst category,
   52.9% OTD) — shift at least 50% of Packaging volume to SUP-01 or SUP-08
   while SUP-07 is on watch; require SUP-07 to submit a corrective action
   plan with a named owner and dates.
3. **Medium term (quarter):** renegotiate or re-bid the SUP-07 contract —
   price increases averaging +9.68% cannot stand alongside 69% OTD; tie any
   renewal to an OTD service-level agreement (≥90%) with a rebate for misses.
4. **Process:** add an automated alert when any supplier's rolling 4-week
   OTD drops below 85% or a single delivery is >5 days late, so the next
   SUP-07 is caught in week one, not month six.
