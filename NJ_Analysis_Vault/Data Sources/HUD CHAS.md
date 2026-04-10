---
tags: [data-source]
source: HUD CHAS + Fair Market Rents
status: not-pulled
api-key-required: true
key-env-var: HUD_API_KEY
geography: municipality, ZCTA
time-series: 2015–2022
duckdb-tables: [hud_chas_places, hud_fair_mkt_rent, hud_safmr]
---

# HUD CHAS & Fair Market Rents

**Free key required:** https://www.huduser.gov/hudapi/public/register

## Run pipeline
```bash
python -m pipeline.run_all --only hud_chas
```

## Datasets
| Dataset | Description | Table |
|---|---|---|
| CHAS | Households by affordability/cost-burden tier | `hud_chas_places` |
| Fair Market Rents | FMR for 0–4BR units by metro/county | `hud_fair_mkt_rent` |
| Small Area FMR | FMR by ZIP code | `hud_safmr` |

## Why useful
CHAS provides more detailed housing affordability breakdowns than ACS alone — specifically, households broken out by income tier (extremely low, very low, low, moderate) and cost burden status.

SAFMR (Small Area FMR) is useful as a market rent benchmark at the ZIP level, especially for investor analysis.

## Notes / Issues
>
