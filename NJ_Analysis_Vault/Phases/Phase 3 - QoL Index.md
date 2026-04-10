---
tags: [phase, qol-index]
phase: 3
status: completed
started: 2026-03-06
completed: 2026-03-06
---

# Phase 3 — Composite Quality-of-Life Index

**Goal:** Build a scored, ranked QoL index for all NJ ZIP codes using two parallel methods (weighted Z-score and PCA), then validate against known benchmarks.

→ Previous: [[Phase 2 - Feature Engineering]]
→ Next: [[Phase 4 - Modeling]]

---

## ✅ Checklist

### Method A — Weighted Z-Score Index
- [x] Standardize all domain variables (Z-scores)
- [x] Invert variables where lower = better
- [x] Apply domain weights (see table below)
- [x] Compute composite score, normalize to 0–100
- [x] Rank all ZIP codes

### Method B — PCA Index
- [x] Standardize feature matrix
- [x] Fit PCA, determine # of components (explain ≥ 70% variance) → 4 components
- [x] Inspect loadings — PC1 = economic prosperity confirmed
- [x] Generate PCA-based scores
- [x] Compare PCA ranking vs. Z-score ranking

### Validation
- [x] Cross-check top/bottom 10 against known NJ towns ✓ (see Results)
- [x] Sensitivity test: ±10% weight variation — median rank std = 2.6 positions (stable)
- [ ] Compare with Niche / WalletHub NJ rankings as external benchmark
- [x] Document any surprises or anomalies

### Output
- [x] Save `qol_scores.parquet` (ZIP, QoL score, domain subscores, rank) → `data/processed/qol_scores.parquet`
- [ ] Load into DuckDB as `qol_scores` table (blocked: Jupyter kernel holds DB lock)
- [x] Summary stats by county (Somerset & Morris counties highest)

---

## 📊 Domain Weights (Weighted Z-Score Method)

| Domain | Variables | Weight | Notes |
|---|---|---|---|
| Economic Security | Income, poverty rate, unemployment | 30% | +5% from Safety (no data) |
| Housing Affordability | Price/income ratio, rent burden | 20% | Tax rate excluded (no ZIP-level data) |
| Education | % bachelor's+ | 15% | |
| Health & Environment | Obesity, smoking, inactivity, uninsured | 20% | +5% from Safety (no data) |
| Safety | — | 0% | FBI crime data not yet loaded |
| Flood & Climate Risk | % high-risk flood zone | 10% | |
| Mobility | Commute time, WFH rate, transit share | 5% | |

---

## 🎯 Validation Benchmarks

**Expected high scorers:** Princeton, Rumson, Westfield, Summit, Montclair, Ridgewood
**Expected low scorers:** Camden, Trenton, Paterson, Atlantic City, Newark
**Middle ground:** Parsippany, Cherry Hill, Toms River

---

## 📝 Results

### Top 20 ZIP Codes (Z-Score Method)
| Rank | ZIP | City | County | Score |
|---|---|---|---|---|
| 1 | 08550 | Princeton Junction | Mercer | 100.0 |
| 2 | 07078 | Short Hills | Essex | 99.7 |
| 3 | 07423 | Ho Ho Kus | Bergen | 98.3 |
| 4 | 07046 | Mountain Lakes | Morris | 97.7 |
| 5 | 07945 | Mendham | Morris | 97.7 |
| 6 | 07021 | Essex Fells | Essex | 97.5 |
| 7 | 07739 | Little Silver | Monmouth | 96.5 |
| 8 | 08502 | Belle Mead | Somerset | 95.3 |
| 9 | 07090 | Westfield | Union | 94.1 |
| 10 | 07704 | Fair Haven | Monmouth | 93.7 |

**Bottom 5:** 07114 Newark (0.0), 08102 Camden (6.6), 08103 Camden (8.0), 08104 Camden (8.2), 07522 Paterson (9.7)

### Top 20 ZIP Codes (PCA Method)
Same top 2 (08550, 07078). Notable difference: 07310 Jersey City ranks #16 on PCA (high education/income in waterfront), but #87 on Z-score (penalized by transit/commute weights).

### Notable Differences Between Methods
- **Method correlation: ρ = 0.956** — very high agreement overall
- **Coastal/beach ZIPs diverge most**: Long Beach Township, Lavallette, Deal — rank ~200 places higher on PCA vs Z-score. PCA captures their high income/education but Z-score penalizes high flood risk and price/income ratio.
- **Trenton-area ZIPs**: consistent at bottom of both methods ✓

### Sensitivity Analysis Outcome
- **Median rank std dev: 2.6 positions** across 200 trials with ±10% weight perturbation
- **90th percentile: 5.5 positions** — rankings are highly stable
- Most unstable: Ledgewood, Stone Harbor, Allenhurst — borderline ZIPs near domain boundaries

---

## 🐛 Issues

- `property_tax_rate` and `avg_annual_tax_bill` are entirely null in `v_zipcode_scorecard` (ZIP↔municipality join not implemented) — excluded from Housing Affordability domain. When fixed, re-add `property_tax_rate` to improve that domain.
- `qol_scores` DuckDB table not loaded due to Jupyter kernel lock. Run `pipeline/qol_analysis.py` after shutting down Jupyter kernel (see MEMORY.md).
- FBI crime data not yet loaded — Safety domain (10%) redistributed to Economic Security (+5%) and Health (+5%).
