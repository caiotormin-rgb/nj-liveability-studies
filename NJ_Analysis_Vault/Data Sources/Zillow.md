---
tags: [data-source]
source: Zillow Research
status: not-pulled
api-key-required: false
geography: ZIP code
time-series: Monthly 2000–present
duckdb-tables: [zillow_home_values, zillow_rent, zillow_market, zillow_latest]
---

# Zillow Research Data

**No API key needed.** Downloads directly from Zillow's public CSV files.

## Run pipeline
```bash
python -m pipeline.run_all --only zillow
```

## Datasets included
| Series | Description | DuckDB table |
|---|---|---|
| ZHVI all homes | Smoothed, seasonally adjusted home value index | `zillow_home_values` (series='zhvi_all_homes') |
| ZHVI SFR | Single-family homes only | `zillow_home_values` (series='zhvi_sfr') |
| ZHVI bottom tier | Affordable segment (0–33rd percentile) | `zillow_home_values` (series='zhvi_bottom_tier') |
| ZHVI top tier | Luxury segment (67–100th percentile) | `zillow_home_values` (series='zhvi_top_tier') |
| ZORI | Observed rent index, all homes | `zillow_rent` |
| Days to pending | Market velocity | `zillow_market` |
| Sale-to-list ratio | Seller market strength | `zillow_market` |

## Key derived view: `zillow_latest`
Contains most recent ZHVI, ZORI, price-to-rent ratio, YoY appreciation, 5yr appreciation per ZIP.

## URL note
If downloads break, check: https://www.zillow.com/research/data/ for updated CSV links, then update `config.py → ZILLOW_URLS`.

## Notes / Issues
>
