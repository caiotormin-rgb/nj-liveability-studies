---
tags: [data-source]
source: FEMA OpenFEMA
status: not-pulled
api-key-required: false
geography: ZIP code
time-series: Policies 2009–present, Claims 1978–present
duckdb-tables: [fema_nfip_policies_nj, fema_nfip_claims_nj, fema_flood_summary]
---

# FEMA National Flood Insurance Program (NFIP)

**No API key needed.** OpenFEMA is fully public.

## Run pipeline
```bash
python -m pipeline.run_all --only fema_flood
```

## Key variables (in `fema_flood_summary`)
- `policy_count` — active NFIP policies in ZIP
- `pct_high_risk_flood_zone` — % policies in SFHA (A/V zones = mandatory purchase zones)
- `total_claims_all_time_usd` — cumulative historical claim payouts
- `total_claim_count` — number of claims ever filed

## Why this matters
NJ has significant flood exposure from Hurricane Sandy (2012) and ongoing coastal/tidal risk. ZIPs with high SFHA exposure tend to see insurance cost pressure on home values.

## Data caveats
- Locations anonymized to ZIP/tract level (privacy rules)
- Policy count ≠ total at-risk properties (uninsured properties not counted)
- Claims data goes back to 1978 but completeness varies

## API endpoint
`https://www.fema.gov/api/open/v2/FimaNfipPolicies`

## Notes / Issues
>
