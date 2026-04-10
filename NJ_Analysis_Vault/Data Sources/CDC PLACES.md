---
tags: [data-source]
source: CDC PLACES
status: not-pulled
api-key-required: false
geography: ZCTA
time-series: 2020–2024
duckdb-tables: [cdc_places_zcta, cdc_places_wide]
---

# CDC PLACES Local Health Data

**No API key needed.** Uses Socrata API.

## Run pipeline
```bash
python -m pipeline.run_all --only cdc_places
```

## Key health measures (measure IDs)
| ID | Measure |
|---|---|
| DIABETES | Diabetes prevalence (%) |
| OBESITY | Obesity prevalence (%) |
| CSMOKING | Current smoking rate (%) |
| DEPRESSION | Depression prevalence (%) |
| LPA | Physical inactivity (%) |
| ACCESS2 | Uninsured (%) |
| MHLTH | Poor mental health ≥14 days/mo (%) |
| SLEEP | Insufficient sleep <7hrs (%) |
| CHD | Coronary heart disease (%) |
| BPHIGH | High blood pressure (%) |
| STROKE | Stroke (%) |

## Tables
- `cdc_places_zcta` — long format (ZCTA × year × measure)
- `cdc_places_wide` — pivoted (one column per measure)

## Notes / Issues
>
