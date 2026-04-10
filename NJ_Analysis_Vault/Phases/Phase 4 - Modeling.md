---
tags: [phase, modeling]
phase: 4
status: not-started
started:
completed:
---

# Phase 4 — Regression & Machine Learning Modeling

**Goal:** Fit and compare 6 model types across 4 targets. Extract feature importance and SHAP values. Map residuals to find undervalued markets.

→ Previous: [[Phase 3 - QoL Index]]
→ Next: [[Phase 5 - Reporting]]

---

## ✅ Checklist

### Setup
- [ ] Train/test split (80/20 — consider spatial split if Moran's I is significant)
- [ ] Final feature matrix loaded and checked
- [ ] Target variables confirmed: `log_home_value`, `zhvi_5yr_cagr`, `log_income`, `qol_score`
- [ ] Missing data strategy applied

### Spatial Diagnostics (before modeling)
- [ ] Compute Moran's I on raw home values
- [ ] If significant: compute spatial weight matrix (queen contiguity)
- [ ] Decide: spatial error model needed? GWR needed?

### Model 1 — OLS Regression
- [ ] Fit on all 4 targets
- [ ] Check VIF — remove features > 10
- [ ] Residual plots (normality, homoscedasticity)
- [ ] Moran's I on residuals
- [ ] Log run → [[Reference/Model Comparison]]

### Model 2 — Ridge / Lasso
- [ ] 5-fold cross-validated GridSearchCV for alpha
- [ ] Lasso: identify which features are zeroed out
- [ ] Compare coefficient magnitudes vs. OLS
- [ ] Log run → [[Reference/Model Comparison]]

### Model 3 — Random Forest
- [ ] Tune: `max_depth`, `n_estimators`, `min_samples_leaf`
- [ ] Permutation feature importance plot
- [ ] Partial dependence plots for top 5 features
- [ ] Log run → [[Reference/Model Comparison]]

### Model 4 — XGBoost / LightGBM
- [ ] Tune: `max_depth`, `learning_rate`, `n_estimators` (early stopping)
- [ ] SHAP summary plot (global feature importance)
- [ ] SHAP beeswarm plot
- [ ] SHAP dependence plots for top 5 features
- [ ] Log run → [[Reference/Model Comparison]]

### Model 5 — Panel OLS (Fixed Effects)
- [ ] Build panel dataset (municipality × year, 2012–2023)
- [ ] Within-municipality variation only (entity FE)
- [ ] Time FE also? Test both.
- [ ] Cluster standard errors by county
- [ ] Log run → [[Reference/Model Comparison]]

### Model 6 — Geographically Weighted Regression
- [ ] Build spatial weights and geometry
- [ ] Select bandwidth (AIC-based)
- [ ] Map key coefficients (e.g., crime effect varies by location?)
- [ ] Log run → [[Reference/Model Comparison]]

### Interpretation
- [ ] Consolidated feature importance table (all models)
- [ ] Map of residuals — where is model wrong? (undervalued markets signal)
- [ ] Write up top 10 positive and negative drivers of home values
- [ ] What-if analysis: crime −20%, commute −5min — modeled effect on values?

---

## 📊 Model Comparison Summary

*(Fill in as models are run — or use [[Reference/Model Comparison]])*

| Model | Target | R² | RMSE | Moran's I (resid) | Notes |
|---|---|---|---|---|---|
| | | | | | |

---

## 🔍 Key Findings

### Top Drivers of Home Values
>

### Top Drivers of Income
>

### Spatial Patterns in Residuals
>

### Interesting Non-linearities
>

---

## 🐛 Issues

