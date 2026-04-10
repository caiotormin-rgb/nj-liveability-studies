---
tags: [phase, eda]
phase: 1
status: in-progress
started:
completed:
---

# Phase 1 — Exploratory Data Analysis

**Goal:** Understand distributions, identify outliers, quantify missing data, and surface the strongest bivariate relationships before modeling.

→ Previous: —
→ Next: [[Phase 2 - Feature Engineering]]

---

## ✅ Checklist

### Data Loading
- [ ] Load `acs_places` and `acs_zctas` from DuckDB
- [ ] Load `zillow_latest` and `zillow_home_values`
- [ ] Load `nj_property_tax`, `cdc_places_wide`, `fema_flood_summary`, `fbi_crime_rates`
- [ ] Build master flat file (ZIP-level join across all sources)
- [ ] Document row counts and join success rate per source

### Coverage Audit
- [ ] How many ZIPs have Zillow data?
- [ ] How many municipalities have FBI crime data?
- [ ] Which sources have the most missingness?
- [ ] Flag geographies with <3 sources available

### Univariate Analysis
- [ ] Histograms for all key variables (income, home value, rent, poverty rate, etc.)
- [ ] Box plots to identify outliers
- [ ] Log-transform skewed variables and re-check distributions
- [ ] Document which variables need transformation

### Bivariate Analysis
- [ ] Scatter matrix — top 15 variables
- [ ] Pearson correlation heatmap
- [ ] Spearman correlation heatmap (for non-normal variables)
- [ ] Flag pairs with |r| > 0.8 (multicollinearity risk)

### Geographic Checks
- [ ] Choropleth: home values by ZIP
- [ ] Choropleth: median income by municipality
- [ ] Choropleth: poverty rate
- [ ] Choropleth: flood risk (% high-risk zone)
- [ ] Confirm spatial patterns match known NJ geography

### Outlier Investigation
- [ ] List top 10 outliers per key variable
- [ ] Distinguish true outliers (Princeton, Rumson) vs. data errors
- [ ] Document decisions: keep, remove, or flag

### Missing Data
- [ ] `missingno` matrix visualization
- [ ] Per-variable missingness rate table
- [ ] Decide: imputation vs. listwise deletion per variable
- [ ] Document imputation strategy

---

## 🔍 Key Questions to Answer

- [ ] Are home values log-normally distributed?
- [ ] How correlated are income and education? (VIF implications)
- [ ] Is flood risk negatively correlated with home values in coastal ZIPs?
- [ ] Is there a clear urban/suburban/rural gradient?
- [ ] Which sources have the most coverage gaps?

---

## 📝 Findings

*(Add findings below as you work through the checklist)*

### Distributions
>

### Strongest Correlations Found
>

### Multicollinearity Concerns
>

### Outliers to Investigate
>

### Missing Data Summary
>

---

## 🐛 Issues / Blockers

*(Log any data problems here)*

---

## 🔗 Related Notes

- [[EDA Findings/]] — individual finding notes
- [[Reference/Variable Dictionary]]
- [[Reference/SQL Queries]]
