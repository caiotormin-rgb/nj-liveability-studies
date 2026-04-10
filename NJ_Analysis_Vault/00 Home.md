---
tags: [home, dashboard]
---

# 🏠 NJ Municipality Analysis — Home

> Understanding drivers of quality of life, income, and home values across all 565 NJ municipalities and ~300 ZIP codes.

---

## 📍 Project Status

| | |
|---|---|
| **Started** | 2026-03-03 |
| **Current Phase** | [[Phases/Phase 1 - EDA\|Phase 1 — EDA]] |
| **Pipeline status** | ✅ Run — DuckDB populated |
| **Model status** | ⬜ Not started |

---

## 🗺️ Phases

| Phase | Note | Status |
|---|---|---|
| 1 | [[Phases/Phase 1 - EDA]] | 🔵 In progress |
| 2 | [[Phases/Phase 2 - Feature Engineering]] | ⬜ Not started |
| 3 | [[Phases/Phase 3 - QoL Index]] | ⬜ Not started |
| 4 | [[Phases/Phase 4 - Modeling]] | ⬜ Not started |
| 5 | [[Phases/Phase 5 - Reporting]] | ⬜ Not started |

---

## 📦 Data Sources

| Source                       | Status       | Table in DuckDB                     |
| ---------------------------- | ------------ | ----------------------------------- |
| [[Data Sources/Census ACS]]  | ✅ Pulled | `acs_places`, `acs_zctas`           |
| [[Data Sources/Zillow]]      | ✅ Pulled | `zillow_home_values`, `zillow_rent` |
| [[Data Sources/NJ DCA]]      | ✅ Pulled | `nj_property_tax`, `nj_dca_budgets` |
| [[Data Sources/CDC PLACES]]  | ✅ Pulled | `cdc_places_wide`                   |
| [[Data Sources/FEMA NFIP]]   | ✅ Pulled | `fema_flood_summary`                |
| [[Data Sources/BLS LAUS]]    | ⬜ Not pulled | `bls_county_unemployment`           |
| [[Data Sources/FBI Crime]]   | ⬜ Not pulled | `fbi_crime_rates`                   |
| [[Data Sources/HUD CHAS]]    | ✅ Pulled | `hud_chas_places`                   |
| [[Data Sources/Tree Equity]] | ✅ Pulled + processed | `tree_equity_nj`                    |

---

## 🧠 Key Reference Notes

- [[Reference/Variable Dictionary]] — all 38 candidate features with source and expected sign
- [[Reference/SQL Queries]] — useful DuckDB queries to copy-paste
- [[Reference/Model Comparison]] — tracking model runs and metrics

---

## 📋 Open Tasks

```tasks
not done
```

---

## 🗒️ Recent Log

- 2026-03-03 — Project initialized. Pipeline code complete.
- 2026-03-05 — 7 of 9 data sources pulled. DuckDB populated. Tree equity processed. Affordability study completed (see `analysis/affordability_study/`).
- 2026-03-06 — Vault reorganized. Loose files consolidated into `analysis/` and `notebooks/`. Technical dataset summaries moved to `docs/`.
