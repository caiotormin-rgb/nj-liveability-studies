# Tree Canopy Coverage, Quality of Life, and Home Values (NJ Places, 2023)

**Scope:** NJ places (municipalities/CDPs) with population ≥ 1,500 and matched Tree Equity + ACS data.
**Sample size:** 339 places.
**Tree equity aggregation:** population-weighted averages of block-group Tree Equity data.
**Home values:** ACS median home value (2023).
**QoL index:** composite of income, poverty, unemployment, education, homeownership, rent burden, commute time.

## Key Correlations
| Outcome | Pearson r | Spearman ρ |
|---|---:|---:|
| Home Value Median | 0.129 | 0.113 |
| Qol Index | 0.259 | 0.266 |

## Regression Results (Standardized Betas)
**Home Value (log) ~ Tree Canopy + Income**
| Model | Variable | Beta | p-value |
|---|---|---:|---:|
| Base | treecanopy_pct | -0.099 | 0.0236 |
| Base | log_income | 0.788 | 1.18e-66 |

**Home Value (log) ~ Tree Canopy + Income + Controls**
| Model | Variable | Beta | p-value |
|---|---|---:|---:|
| Full | treecanopy_pct | -0.078 | 0.0369 |
| Full | log_income | 0.317 | 0.000528 |
| Full | poverty_rate | -0.012 | 0.843 |
| Full | pct_bachelors_plus | 0.600 | 3.37e-17 |
| Full | homeownership_rate | -0.097 | 0.0356 |
| Full | avg_commute_minutes | 0.034 | 0.299 |

**QoL Index ~ Tree Canopy + Income**
| Model | Variable | Beta | p-value |
|---|---|---:|---:|
| Base | treecanopy_pct | 0.035 | 0.338 |
| Base | log_income | 0.819 | 4.35e-99 |

**QoL Index ~ Tree Canopy + Income + Controls**
| Model | Variable | Beta | p-value |
|---|---|---:|---:|
| Full | treecanopy_pct | 0.012 | 0.000263 |
| Full | log_income | 0.245 | 7.15e-155 |
| Full | poverty_rate | -0.209 | 0 |
| Full | pct_bachelors_plus | 0.274 | 0 |
| Full | homeownership_rate | 0.266 | 0 |
| Full | avg_commute_minutes | -0.246 | 0 |
| Full | rent_burden_30plus_pct | -0.255 | 0 |
| Full | unemployment_rate_acs | -0.237 | 0 |

## Figures
- `NJ_Analysis_Vault/EDA Findings/tree_canopy_vs_home_value.png`
- `NJ_Analysis_Vault/EDA Findings/tree_canopy_vs_qol.png`

## Notes & Limitations
- Place names are matched by normalization and suffix stripping; some municipalities may be unmatched or mis-matched.
- Tree canopy is aggregated from block groups to places using population weights, not spatial area.
- ACS home values are self-reported medians; they are not Zillow ZHVI.
- Cross-sectional analysis (2023) shows association, not causation.
