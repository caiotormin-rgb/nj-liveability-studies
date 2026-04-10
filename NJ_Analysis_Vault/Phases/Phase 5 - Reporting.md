---
tags: [phase, reporting]
phase: 5
status: not-started
started:
completed:
---

# Phase 5 — Reporting & Deliverables

**Goal:** Turn model outputs into practical guides for homebuyers and investors, plus a technical report.

→ Previous: [[Phase 4 - Modeling]]
→ Next: —

---

## ✅ Checklist

### Homebuyer Guide
- [ ] Best overall QoL — top 25 ZIP codes by QoL score
- [ ] Best affordability — lowest price/income ratio + low tax burden
- [ ] Best for families — education + safety + health + parks subscores
- [ ] Best for remote workers — WFH share + nature access + tree canopy
- [ ] Best appreciation potential — high 5yr CAGR, below-median current price
- [ ] Lowest risk — flood zone, crime, employment stability combined
- [ ] Format as Word doc or clean notebook

### Investor Guide
- [ ] Undervalued markets — positive model residuals (actual < predicted value)
- [ ] Appreciation momentum — high CAGR + low current inventory signal
- [ ] Price-to-rent ratio map — where does buying pencil vs. renting?
- [ ] Risk-adjusted return table — CAGR adjusted for flood + tax burden

### Technical Report
- [ ] Full model specification tables (coefficients, SEs, p-values)
- [ ] Model comparison table (R², RMSE, Moran's I)
- [ ] SHAP summary plots
- [ ] GWR coefficient maps
- [ ] Data dictionary and methodology notes

### Interactive Notebook / Dashboard
- [ ] Any ZIP/municipality scorecard lookup
- [ ] Model-predicted vs. actual home value (over/undervaluation flag)
- [ ] What-if slider: change crime rate → see predicted value change
- [ ] Side-by-side comparison of 2 towns

---

## 📝 Decisions to Make

- [ ] Format for homebuyer guide — Word doc, HTML, or Notion page?
- [ ] Audience for investor guide — internal only or shareable?
- [ ] Dashboard — Jupyter widgets or Plotly Dash?

---

## 🐛 Issues

