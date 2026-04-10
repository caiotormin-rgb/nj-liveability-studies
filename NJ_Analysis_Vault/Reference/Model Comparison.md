---
tags: [reference, modeling]
---

# Model Comparison Log

Track every model run here. For detailed experiment tracking, use MLflow alongside this note.

```bash
# Start MLflow UI
mlflow ui --port 5000
# Open: http://localhost:5000
```

---

## Target: `log_home_value` (log of Zillow ZHVI)

| Model | R² (test) | RMSE (test) | Moran's I (resid) | Key notes | Date |
|---|---|---|---|---|---|
| OLS baseline | | | | | |
| OLS + county FE | | | | | |
| Ridge (α=?) | | | | | |
| Lasso (α=?) | | | | | |
| Random Forest | | | | | |
| XGBoost | | | | | |
| GWR | | | | | |

---

## Target: `zhvi_5yr_cagr` (5-year appreciation)

| Model | R² (test) | RMSE | Notes | Date |
|---|---|---|---|---|
| | | | | |

---

## Target: `log_income` (log of Median HH Income)

| Model | R² (test) | RMSE | Notes | Date |
|---|---|---|---|---|
| | | | | |

---

## Target: `qol_score`

| Model | R² (test) | RMSE | Notes | Date |
|---|---|---|---|---|
| | | | | |

---

## Feature Importance Summary

*(Fill in after fitting tree models)*

### Home Value — Top 10 Drivers
| Rank | Feature | SHAP / Importance | Direction |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

### Income — Top 10 Drivers
| Rank | Feature | SHAP / Importance | Direction |
|---|---|---|---|
| | | | |

---

## Hyperparameter Log

| Model | Target | Parameters | CV Score | Notes |
|---|---|---|---|---|
| Ridge | log_home_value | alpha= | | |
| XGBoost | log_home_value | max_depth= , lr= , n_est= | | |

---

## Spatial Diagnostics

| Variable | Moran's I | p-value | Interpretation |
|---|---|---|---|
| ZHVI raw | | | |
| OLS residuals | | | |
| XGBoost residuals | | | |
