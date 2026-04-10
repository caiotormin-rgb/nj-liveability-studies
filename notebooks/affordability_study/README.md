# New Jersey Home Affordability Analysis

**Comprehensive time series analysis of housing affordability, demographic patterns, gentrification, and community change across New Jersey (2000-2026)**

## 📁 Project Structure

```
analysis/affordability_study/
├── README.md                              # This file
├── nj_affordability_analysis.ipynb        # Main analysis notebook
├── nj_affordability_report.md             # Comprehensive written report
├── visualizations/                        # Generated charts and figures
│   ├── nj_home_values_by_county.png
│   ├── nj_affordability_analysis.png
│   ├── nj_gentrification_patterns.png
│   ├── nj_community_degradation.png
│   ├── nj_regional_contrasts.png
│   └── nj_period_changes_heatmap.png
└── data_exports/                          # Analysis results (CSV)
    ├── communities_degrading_affordability.csv
    └── communities_positive_affordability.csv
```

## 🎯 Analysis Overview

This study examines how home affordability has evolved across New Jersey's 21 counties and 600+ ZIP codes over the past 26 years, revealing:

- **Time series trends** in home values (2000-2026)
- **Demographic patterns** and correlations with housing costs
- **Gentrification indicators** in rapidly appreciating communities
- **Community degradation** in economically distressed areas
- **Regional contrasts** between winners and losers
- **Outlier analysis** of exceptional communities

## 📊 Key Findings

### Overall Trends
- **Median home value**: $661,000 (2026)
- **Median price appreciation**: 223% since 2000
- **Price-to-income ratio**: 6.8x (median, indicating unaffordability)
- **Geographic spread**: 182 percentage points between highest and lowest county appreciation

### Community Classifications
- **High Gentrification**: 3,652 ZIP codes (55% of total)
  - Average 263% price appreciation
  - 50.5% with Bachelor's degrees
  - 4.9% poverty rate

- **Economic Distress**: 343 ZIP codes (5% of total)
  - Average 330% price appreciation but high poverty (29%)
  - 34% severe rent burden
  - 26% homeownership rate

- **Positive Growth**: 42 communities identified
  - Strong appreciation (>75%)
  - Maintained affordability (<6x income)
  - Low poverty (<10%)

## 📈 Visualizations

### 1. Home Values by County (2000-2026)
Time series showing divergent trends across NJ counties with recession markers.

### 2. Affordability Analysis
- Box plots of price-to-income ratios by county
- Scatter plot correlating income with home values

### 3. Gentrification Patterns
- County-level gentrification scores
- Education vs price appreciation
- Distribution of gentrification status
- Price change histogram

### 4. Community Degradation
- County degradation scores
- Poverty vs price growth scatter
- Degradation status distribution
- Rent burden analysis

### 5. Regional Contrasts
- Community type distribution (pie chart)
- Income comparison by type
- Price appreciation by type
- Poverty rates by type

### 6. Period Changes Heatmap
County-by-county performance across four economic periods:
- Pre-Recession (2000-2006)
- Recession/Recovery (2007-2011)
- Growth Period (2012-2019)
- Pandemic Era (2020+)

## 📄 Data Sources

- **Zillow Home Value Index (ZHVI)**: Monthly home values, 2000-2026
- **U.S. Census ACS**: Demographics, income, education, housing (2016-2020)
- **CDC PLACES**: Health indicators
- **Coverage**: 551 ZIP codes, 21 counties, 663K+ records

## 🚀 Running the Analysis

### Prerequisites
```bash
# Ensure you have the required environment
conda activate nj-pipeline
```

### Execute the Notebook
```bash
cd /Users/caiotormin/torm/nj_pipeline/analysis/affordability_study
jupyter notebook nj_affordability_analysis.ipynb
```

Or run all cells:
```bash
jupyter nbconvert --to notebook --execute nj_affordability_analysis.ipynb
```

### Expected Runtime
- Full analysis: ~2-3 minutes
- Database queries: ~30 seconds
- Visualizations: ~1 minute
- Exports: ~10 seconds

## 📑 Outputs

### Visualizations (PNG, 300 DPI)
All saved to `visualizations/` directory:
- 6 multi-panel figures
- Print-ready quality
- Annotated with insights

### Data Exports (CSV)
Saved to `data_exports/` directory:

**communities_degrading_affordability.csv** (56,520 records)
- ZIP codes with economic distress or declining affordability
- Columns: zip_code, county, home_value, price_change_pct, price_to_income_ratio, poverty_rate, income, community_type

**communities_positive_affordability.csv** (264,672 records)
- ZIP codes with strong growth and maintained affordability
- Columns: zip_code, county, home_value, price_change_pct, price_to_income_ratio, poverty_rate, income, education

## 🔍 Methodology

### Gentrification Score (0-5)
- +2 points: >100% price appreciation
- +1 point: 75-100% price appreciation
- +1 point: >50% Bachelor's degree holders
- +1 point: <10% poverty rate
- +1 point: >6x price-to-income ratio

Classification:
- **4-5**: High Gentrification
- **2-3**: Moderate Gentrification
- **0-1**: Stable

### Degradation Score (0-6)
- +2 points: <25% price appreciation
- +1 point: 25-50% price appreciation
- +2 points: >20% poverty rate
- +1 point: 15-20% poverty rate
- +1 point: >25% severe rent burden
- +1 point: <40% homeownership rate

Classification:
- **4-6**: High Degradation
- **2-3**: Moderate Degradation
- **0-1**: Stable/Growing

### Affordability Benchmarks
- **<3x income**: Affordable
- **3-5x income**: Moderately Affordable
- **5-7x income**: Unaffordable
- **>7x income**: Severely Unaffordable

## 📖 Report Sections

The comprehensive markdown report (`nj_affordability_report.md`) includes:

1. Executive Summary
2. Historical Home Value Trends (by phase)
3. Affordability Analysis (price-to-income ratios)
4. Gentrification Effects (case studies)
5. Community Degradation (distressed areas)
6. Regional Contrasts (winners vs losers)
7. Demographic Patterns & Correlations
8. Outlier Analysis (statistical extremes)
9. Time Series by Period (4 economic eras)
10. Communities with Degrading Affordability (63 ZIP codes detailed)
11. Communities with Positive Effects (42 ZIP codes detailed)
12. Conclusions & Policy Implications

## 🎓 Key Insights for Policy

### For Gentrifying Communities
- Implement inclusionary zoning
- Establish community land trusts
- Protect legacy residents from displacement
- Preserve affordable commercial spaces

### For Distressed Communities
- Target economic development incentives
- Invest in transit infrastructure
- Remediate brownfields
- Consider regional tax-base sharing

### Statewide Recommendations
- Reform affordable housing obligations (COAH)
- Create first-time homebuyer programs
- Address property tax burden (highest in nation)
- Enforce fair share housing requirements
- Expand transit to increase opportunity geography

## 📧 Contact & Attribution

**Analysis Date**: March 2026
**Data Pipeline**: NJ Pipeline Database
**Geographic Scope**: All 21 New Jersey Counties

For questions about methodology or data access, refer to the main project documentation.

---

*This analysis uses publicly available data from Zillow, U.S. Census Bureau, and CDC. While every effort has been made to ensure accuracy, users should verify findings with primary sources for critical decisions.*
