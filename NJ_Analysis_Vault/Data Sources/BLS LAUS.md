---
tags: [data-source]
source: Bureau of Labor Statistics
status: not-pulled
api-key-required: false
geography: county
time-series: Monthly 2010–2024
duckdb-tables: [bls_county_unemployment, bls_county_unemployment_wide]
---

# BLS Local Area Unemployment Statistics (LAUS)

**API key optional.** v1 API works without a key (limited to 10 years). Register for v2 at https://data.bls.gov/registrationEngine/ for 20 years.

## Run pipeline
```bash
python -m pipeline.run_all --only bls_laus
```

## Series pulled (per county)
| Code | Measure |
|---|---|
| 03 | Unemployment rate (%) |
| 04 | Unemployment count |
| 05 | Employment count |
| 06 | Labor force total |

## Coverage note
BLS LAUS is **county-level**. Municipality-level unemployment is not available from BLS. For the model, county unemployment will be assigned to all municipalities/ZIPs within each county.

## Notes / Issues
>
