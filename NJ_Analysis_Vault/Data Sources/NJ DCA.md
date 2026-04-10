---
tags: [data-source]
source: NJ Department of Community Affairs
status: not-pulled
api-key-required: false
geography: municipality
time-series: 2015–2023
duckdb-tables: [nj_property_tax, nj_equalization, nj_dca_budgets]
---

# NJ Department of Community Affairs (DCA)

**No API key needed.** Uses NJ Open Data Socrata API + Excel downloads.

## Run pipeline
```bash
python -m pipeline.run_all --only nj_dca
```

## Datasets included
| Dataset | Source | DuckDB table |
|---|---|---|
| Property tax rates & bills | NJ Open Data (Socrata) | `nj_property_tax` |
| Equalization valuations | NJ Open Data (Socrata) | `nj_equalization` |
| Municipal budget summaries | DCA Excel files (2015–2023) | `nj_dca_budgets` |

## Key variables
- `general_tax_rate` — municipal property tax rate (%)
- `effective_tax_rate` — effective rate after equalization
- `avg_tax_bill_residential` — average annual tax bill ($)
- `avg_assessed_value_residential` — average assessed value ($)

## Web resources
- Statistical tables: https://www.nj.gov/dca/divisions/dlgs/resources/statistical_tables.html
- NJ Open Data: https://data.nj.gov/

## Notes / Issues
>
