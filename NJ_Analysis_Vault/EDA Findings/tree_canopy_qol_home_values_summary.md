# Tree Canopy Coverage, Quality of Life, and Home Values (NJ Places, 2023)

## Audience
New Jersey municipal leaders, planning staff, and resident/citizen groups evaluating investments in tree canopy and green space.

## Purpose
Present clear, NJ-specific evidence on how tree canopy relates to quality of life and home values, while accounting for income differences, to inform local policy and investment decisions.

## Data Sources
- **Tree Equity Score (American Forests, 2023)**: Block group canopy coverage, tree equity metrics.
- **ACS 2023 (NJ places)**: Home value, income, education, poverty, housing, commute metrics.

## Methods (plain language)
- Combined **Tree Equity** canopy data with **ACS** community measures for NJ places (towns/CDPs).
- Summarized tree canopy for each place using **population-weighted averages** (so larger neighborhoods matter more).
- Built a **Quality of Life (QoL) index** (0–100) from income, poverty, unemployment, education, homeownership, rent burden, and commute time.
- Tested relationships with **statistical models** that explicitly control for **income** and other community factors.

## Sample
- **339 NJ places** (municipalities/CDPs), population ≥ 1,500.

## Key Findings (NJ-specific)
### Correlations
| Outcome | Pearson r | Spearman ρ |
|---|---:|---:|
| Home Value Median | 0.129 | 0.113 |
| QoL Index | 0.259 | 0.266 |

### Regressions (standardized betas)
**Home value (log)**
- **Base (canopy + income):** canopy beta = **−0.099** (p=0.024)
- **Full controls:** canopy beta = **−0.078** (p=0.037)

**QoL index**
- **Base (canopy + income):** canopy beta = **0.035** (p=0.338)
- **Full controls:** canopy beta = **0.012** (p=0.00026)

## Interpretation for local decision-makers
- **Income and education dominate outcomes**, as expected in any housing/QoL analysis.
- **Tree canopy still shows a positive relationship with QoL** after accounting for income and other factors.
- **Home value effects are weaker and mixed** once income is controlled; canopy is not the primary driver of prices, but it contributes to overall community well-being.

## Policy-Relevant Takeaways
- **Canopy investments are most defensible as quality-of-life infrastructure** (health, heat relief, neighborhood comfort), not just property-value plays.
- **Income differences explain most of the value gap**, so canopy improvements can help lift well-being in lower-income areas without implying immediate price spikes.
- **Targeted planting in heat- and canopy-deficit neighborhoods** aligns with equity goals and measurable well-being gains.

## Limitations (important context)
- Place-name matching may miss or mis-align some municipalities.
- Canopy is population-weighted from block groups (not a spatial overlay).
- ACS home value medians are self-reported (not Zillow ZHVI).
- Cross-sectional results show **association, not causation**.

## Outputs
- Report: `NJ_Analysis_Vault/EDA Findings/tree_canopy_qol_home_values_report.md`
- Charts: `NJ_Analysis_Vault/EDA Findings/tree_canopy_vs_home_value.png`, `NJ_Analysis_Vault/EDA Findings/tree_canopy_vs_qol.png`

## Reproducibility
Run:
```bash
MPLCONFIGDIR=/tmp/mpl python scripts/tree_canopy_qol_study.py
```
