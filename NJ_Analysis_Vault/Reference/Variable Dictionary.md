---
tags: [reference, features]
---

# Variable Dictionary

All 38 candidate predictor variables. Update the Status column as you work through the feature engineering phase.

| Variable | Description | Source | Geography | Expected Sign | Status |
|---|---|---|---|---|---|
| **Economics** | | | | | |
| `income_median_hh` | Median household income | ACS | Municipality | + | ⬜ |
| `income_per_capita` | Per capita income | ACS | Municipality | + | ⬜ |
| `poverty_rate` | % population below poverty line | ACS | Municipality | − | ⬜ |
| `gini_index` | Income inequality (0–1) | ACS | Municipality | varies | ⬜ |
| `unemployment_rate_acs` | ACS unemployment rate (%) | ACS | Municipality | − | ⬜ |
| `unemployment_rate_bls` | BLS county unemployment (%) | BLS | County | − | ⬜ |
| **Housing** | | | | | |
| `home_value_median` | Median owner-occ. home value (ACS) | ACS | Municipality | + | ⬜ |
| `zhvi_current` | Zillow Home Value Index | Zillow | ZIP | + | ⬜ |
| `gross_rent_median` | Median gross rent | ACS | Municipality | + | ⬜ |
| `zori_current` | Zillow Observed Rent Index | Zillow | ZIP | + | ⬜ |
| `homeownership_rate` | % owner-occupied units | ACS | Municipality | + | ⬜ |
| `vacancy_rate` | % vacant housing units | ACS | Municipality | − | ⬜ |
| `rent_burden_30plus_pct` | % renters paying >30% income on rent | ACS | Municipality | − | ⬜ |
| `general_tax_rate` | Municipal property tax rate (%) | NJ DCA | Municipality | − | ⬜ |
| `avg_tax_bill_residential` | Average annual residential tax bill ($) | NJ DCA | Municipality | − | ⬜ |
| **Education** | | | | | |
| `pct_bachelors_plus` | % adults with BA or higher | ACS | Municipality | + | ⬜ |
| **Demographics** | | | | | |
| `pop_total` | Total population | ACS | Municipality | varies | ⬜ |
| `age_median` | Median age | ACS | Municipality | varies | ⬜ |
| `diversity_index` | Racial diversity (Herfindahl-style) | ACS | Municipality | varies | ⬜ |
| **Commuting** | | | | | |
| `avg_commute_minutes` | Average commute time (minutes) | ACS | Municipality | − | ⬜ |
| `pct_transit_commute` | % workers using public transit | ACS | Municipality | + | ⬜ |
| `pct_wfh` | % workers working from home | ACS | Municipality | + | ⬜ |
| **Health** | | | | | |
| `diabetes` | Diabetes prevalence (%) | CDC PLACES | ZCTA | − | ⬜ |
| `obesity` | Obesity prevalence (%) | CDC PLACES | ZCTA | − | ⬜ |
| `csmoking` | Current smoking rate (%) | CDC PLACES | ZCTA | − | ⬜ |
| `lpa` | Physical inactivity rate (%) | CDC PLACES | ZCTA | − | ⬜ |
| `access2` | % uninsured | CDC PLACES | ZCTA | − | ⬜ |
| `depression` | Depression prevalence (%) | CDC PLACES | ZCTA | − | ⬜ |
| **Environment** | | | | | |
| `canopy_pct` | Average tree canopy cover (%) | Tree Equity | Tract/ZCTA | + | ⬜ |
| `tree_equity_score` | Tree Equity Score (0–100) | Tree Equity | Tract | + | ⬜ |
| `pct_high_risk_flood_zone` | % NFIP policies in SFHA | FEMA | ZIP | − | ⬜ |
| `flood_claims_historical` | Total historical NFIP claims ($) | FEMA | ZIP | − | ⬜ |
| **Crime** | | | | | |
| `crime_rate_violent` | Violent crimes per 100k pop | FBI CDE | Agency | − | ⬜ |
| `crime_rate_property` | Property crimes per 100k pop | FBI CDE | Agency | − | ⬜ |
| **Derived** | | | | | |
| `price_to_rent_ratio` | ZHVI / (ZORI × 12) | Derived | ZIP | varies | ⬜ |
| `home_price_to_income` | ZHVI / Median HH Income | Derived | ZIP | − | ⬜ |
| `zhvi_5yr_cagr` | 5-year compound annual growth rate | Derived | ZIP | + | ⬜ |
| `zhvi_volatility` | Std dev of monthly ZHVI returns (5yr) | Derived | ZIP | − | ⬜ |
| `effective_tax_burden` | Tax bill / ZHVI × 100 | Derived | ZIP | − | ⬜ |

---

## Variables Removed / Modified

*(Document any changes from the original plan here)*

| Variable | Reason | Decision | Date |
|---|---|---|---|
| | | | |
