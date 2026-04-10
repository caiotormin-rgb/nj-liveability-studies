---
tags: [phase, features]
phase: 2
status: not-started
started:
completed:
---

# Phase 2 — Feature Engineering

**Goal:** Build the master feature matrix with derived variables, spatial lags, and time-series lags ready for modeling.

→ Previous: [[Phase 1 - EDA]]
→ Next: [[Phase 3 - QoL Index]]

---

## ✅ Checklist

### Derived Variables
- [ ] `home_price_to_income` = ZHVI / Median HH Income
- [ ] `rent_to_income_pct` = (ZORI × 12) / Median HH Income × 100
- [ ] `log_home_value` = ln(ZHVI)
- [ ] `log_income` = ln(Median HH Income)
- [ ] `pct_college_plus` = (BA + MA + Prof + PhD) / Pop 25+
- [ ] `effective_tax_burden` = Avg Tax Bill / ZHVI × 100
- [ ] `est_annual_own_cost` = mortgage P+I (20% down, 7%, 30yr) + tax bill
- [ ] `rent_vs_own_gap` = ZORI × 12 vs. est_annual_own_cost
- [ ] `diversity_index` = 1 − Σ(race share)²
- [ ] `crime_rate_violent` = FBI violent crimes / population × 100k
- [ ] `health_composite` = average of CDC diabetes, obesity, smoking, inactivity (inverted)
- [ ] `pct_flood_risk` = % NFIP policies in SFHA
- [ ] `zhvi_5yr_cagr` = 5-year CAGR of ZHVI
- [ ] `zhvi_volatility` = std dev of monthly ZHVI returns (5yr)

### Spatial Features
- [ ] Spatial lag of home values (queen contiguity, neighboring ZIPs)
- [ ] Distance to Manhattan (minutes by NJ Transit rail)
- [ ] Distance to nearest train station
- [ ] County fixed effects (21 dummies)
- [ ] Urban/suburban/rural classification (Census urban area designation)

### Time Series Features
- [ ] Year fixed effects (2012–2023)
- [ ] 1-year lag of ZHVI
- [ ] 1-year lag of income
- [ ] 5-year rolling average of unemployment rate

### Final Feature Matrix
- [ ] Assemble master `features.parquet` — one row per ZIP/municipality
- [ ] Confirm row count matches coverage expectations
- [ ] Write feature documentation (update [[Reference/Variable Dictionary]])
- [ ] Check VIF on all features — flag anything > 10

---

## 📝 Notes

### Geographic Join Decisions
>

### Variables Dropped / Modified from Plan
>

### VIF Results (after construction)
>

---

## 🐛 Issues

