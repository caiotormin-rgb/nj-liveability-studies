---
tags: [data-source]
source: FBI Crime Data Explorer
status: not-pulled
api-key-required: true
key-env-var: FBI_API_KEY
geography: agency (municipal police department)
time-series: 2010–2022
duckdb-tables: [fbi_agencies, fbi_crime_stats, fbi_crime_rates]
---

# FBI Crime Data Explorer

**Free key required:** https://api.data.gov/signup/

## Run pipeline
```bash
python -m pipeline.run_all --only fbi_crime
```

## Key variables (in `fbi_crime_rates`)
- `crime_rate_violent_per_100k` — violent crimes per 100k population
- `crime_rate_property_per_100k` — property crimes per 100k population
- Breakdown available: homicide, rape, robbery, aggravated assault, burglary, larceny, motor vehicle theft

## Geographic join note
FBI data is at the **agency (police department) level** — not ZIP code or municipality FIPS. Join via the `fbi_agencies` table which maps ORI codes to place names.

For municipalities with multiple agencies (e.g., county + municipal police), aggregate by taking sum of crime counts before computing rates.

## Notes / Issues
>
