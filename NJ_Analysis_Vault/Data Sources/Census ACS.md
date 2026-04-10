---
tags: [data-source]
source: Census ACS
status: not-pulled
api-key-required: true
key-env-var: CENSUS_API_KEY
geography: municipality, ZCTA
time-series: 2012–2023
duckdb-tables: [acs_places, acs_zctas]
---

# US Census ACS 5-Year Estimates

**Register for a free key:** https://api.census.gov/data/key_signup.html

## Run pipeline
```bash
python -m pipeline.run_all --only census_acs
```

## Key variables pulled
| Variable | Census ID | Description |
|---|---|---|
| `pop_total` | B01003_001E | Total population |
| `age_median` | B01002_001E | Median age |
| `income_median_hh` | B19013_001E | Median household income |
| `income_per_capita` | B19301_001E | Per capita income |
| `poverty_rate` | derived | % below poverty line |
| `gini_index` | B19083_001E | Income inequality |
| `home_value_median` | B25077_001E | Median owner-occ. home value |
| `gross_rent_median` | B25064_001E | Median gross rent |
| `homeownership_rate` | derived | % owner-occupied |
| `rent_burden_30plus_pct` | derived | % renters paying >30% on rent |
| `pct_bachelors_plus` | derived | % with BA or higher |
| `unemployment_rate_acs` | derived | Unemployment rate |
| `avg_commute_minutes` | derived | Average commute time |
| `pct_transit_commute` | derived | % using transit |
| `pct_wfh` | derived | % working from home |

## Notes / Issues
>
