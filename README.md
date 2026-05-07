# NJ Liveability Studies

**Data pipeline + analysis studies exploring quality of life, affordability, and community change across New Jersey's 537 ZIP codes.**

---

## 🗺️ Interactive Explorer

**[→ Open the NJ Homebuyer Explorer](notebooks/nj_homebuyer_explorer.html)**

A single-file web app — no server required, just open in a browser. Covers all 537 NJ ZIP codes with live filtering and personalized ranking.

**What it does:**

- Reweight 6 QoL domains (schools, economic security, housing affordability, health, flood safety, commute) — the ranking updates instantly
- Filter by budget (max home price + price-to-income ratio), county, population size, and price pressure tier
- Grid or table view; click any town for a full profile with domain breakdown and 10-year price history
- Highlights hidden gems (high QoL, still attainable) and fast-appreciating markets

Credit: Caio Tormin, assisted by Claude Code

---

## Studies

### 1. Quality of Life Index

**[`notebooks/qol_analysis.ipynb`](notebooks/qol_analysis.ipynb)**

Composite QoL score for every NJ ZIP code built from six independent data domains.

| Domain | Sources |
| --- | --- |
| Economic Security | Census ACS — income, poverty, unemployment |
| Housing Affordability | Zillow ZHVI + ACS — price/income ratio, rent burden |
| Education | ACS — bachelor's degree attainment |
| Health & Environment | CDC PLACES — obesity, smoking, health access |
| Flood & Climate Risk | FEMA NFIP — share of housing in high-risk flood zones |
| Commute & Mobility | ACS — commute time, transit use, remote work % |

Each domain is normalized 0–100 and combined into a final QoL score. Rankings range from Princeton Junction (#1, score 100) to Newark (#537, score 0). Full scored dataset exported to [`notebooks/Cell output 12 [DW].csv`](notebooks/Cell%20output%2012%20%5BDW%5D.csv).

**Key EDA charts** (`NJ_Analysis_Vault/EDA Findings/`):

- [`qol_top20.png`](NJ_Analysis_Vault/EDA%20Findings/qol_top20.png) — top 20 towns by composite score
- [`qol_by_county.png`](NJ_Analysis_Vault/EDA%20Findings/qol_by_county.png) — county-level score distributions
- [`qol_domain_correlations.png`](NJ_Analysis_Vault/EDA%20Findings/qol_domain_correlations.png) — cross-domain correlation matrix
- [`qol_distribution.png`](NJ_Analysis_Vault/EDA%20Findings/qol_distribution.png) — statewide score distribution
- [`qol_pca_scree.png`](NJ_Analysis_Vault/EDA%20Findings/qol_pca_scree.png) — PCA scree plot across domains

---

### 2. Affordability & Gentrification Study

**[`notebooks/affordability_study/nj_affordability_analysis_fixed.ipynb`](notebooks/affordability_study/nj_affordability_analysis_fixed.ipynb)**

26-year time series (2000–2026) on home values, affordability ratios, and community-level classification across all 551 NJ ZIP codes.

**What's classified:**

| Tier | Criteria | Count |
| --- | --- | --- |
| High Gentrification | >100% appreciation, low poverty, high education | 12 ZIPs |
| Moderate Pressure | Below Average / Moderate price growth | 412 ZIPs |
| Low Pressure | Stable or declining prices | 109 ZIPs |

**Key findings:**

- Median statewide price-to-income ratio: **5.2×** (unaffordable threshold is 5×)
- Spread between top and bottom county appreciation over 26 years: **182 percentage points**
- Hudson County led all appreciation (+210%) driven by Jersey City/Hoboken
- 63 ZIP codes classified as having degrading affordability; 42 with positive balanced growth

Full written report: [`notebooks/affordability_study/nj_affordability_report.md`](notebooks/affordability_study/nj_affordability_report.md)

Scored dataset exported to [`notebooks/affordability_study/Cell output 8 [DW].csv`](notebooks/affordability_study/Cell%20output%208%20%5BDW%5D.csv)

**Visualizations** (`notebooks/affordability_study/visualizations/`):

- [`nj_geographic_analysis_2015_2025.png`](notebooks/affordability_study/visualizations/nj_geographic_analysis_2015_2025.png) — geographic price change map
- [`nj_gentrification_patterns.png`](notebooks/affordability_study/visualizations/nj_gentrification_patterns.png) — gentrification score by county
- [`nj_home_values_by_county.png`](notebooks/affordability_study/visualizations/nj_home_values_by_county.png) — 26-year county-level time series
- [`nj_affordability_analysis.png`](notebooks/affordability_study/visualizations/nj_affordability_analysis.png) — price/income ratio distributions
- [`nj_community_degradation.png`](notebooks/affordability_study/visualizations/nj_community_degradation.png) — poverty vs. price growth scatter
- [`stat_viz4_income_vs_home_value.png`](notebooks/affordability_study/visualizations/stat_viz4_income_vs_home_value.png) — income vs. home value by county

---

### 3. Source EDA Notebooks

Exploratory analysis notebooks for each raw data source, used to validate ingestion and understand distributions before building the QoL index.

| Notebook | Data Source |
| --- | --- |
| [`notebooks/eda_zillow.ipynb`](notebooks/eda_zillow.ipynb) | Zillow ZHVI/ZORI — 683K home value records, 2000–2026 |
| [`notebooks/eda_cdc_places.ipynb`](notebooks/eda_cdc_places.ipynb) | CDC PLACES — 22 health measures across 587 NJ ZCTAs |
| [`notebooks/eda_census.ipynb`](notebooks/eda_census.ipynb) | Census ACS — income, education, housing by ZIP |
| [`notebooks/eda_fema_flood.ipynb`](notebooks/eda_fema_flood.ipynb) | FEMA NFIP — flood zone coverage by ZIP |
| [`notebooks/eda_hud_housing.ipynb`](notebooks/eda_hud_housing.ipynb) | HUD CHAS — housing cost burden and affordability |
| [`notebooks/eda_tree_equity.ipynb`](notebooks/eda_tree_equity.ipynb) | American Forests Tree Equity Score — canopy coverage |

---

## Pipeline

The data pipeline ingests, cleans, and loads all sources into a local DuckDB database (`data/db/nj_pipeline.duckdb`).

```text
pipeline/
├── run_all.py          # Orchestrator — runs all pipelines in sequence
├── base.py             # Abstract base class with DuckDB connection management
├── zillow.py           # Zillow ZHVI + ZORI
├── census_acs.py       # Census ACS (5-year estimates, 2012–2023)
├── cdc_places.py       # CDC PLACES health measures
├── nj_dca.py           # NJ Dept. of Community Affairs
└── qol_analysis.py     # QoL index computation
```

**Run the pipeline:**

```bash
conda activate nj-pipeline
python pipeline/run_all.py
```

> Note: DuckDB only allows one writer at a time. Shut down any active Jupyter kernels before running.

**Setup:**

```bash
conda create -n nj-pipeline python=3.11
conda activate nj-pipeline
pip install duckdb pandas numpy matplotlib seaborn jupyter pgeocode
cp .env.example .env  # add API keys: CENSUS_API_KEY, BLS_API_KEY, HUD_API_KEY
```

---

## Data Sources

| Source | Records | Coverage |
| --- | --- | --- |
| Zillow ZHVI | 683K | 552 NJ ZIPs, 2000–2026 |
| Census ACS | — | 587 ZCTAs, 2012–2023 |
| CDC PLACES | 1,174 | 587 NJ ZCTAs, 2022–2023 |
| FEMA NFIP | — | All NJ ZIPs |
| BLS LAUS | — | County-level unemployment |
| HUD CHAS | — | Housing cost burden by ZIP |

---

## Project Layout

```text
nj_pipeline/
├── notebooks/
│   ├── nj_homebuyer_explorer.html        ← interactive widget
│   ├── qol_analysis.ipynb                ← QoL index study
│   ├── viz_qol_map.ipynb                 ← QoL map visualizations
│   ├── affordability_study/
│   │   ├── nj_affordability_analysis_fixed.ipynb
│   │   ├── nj_affordability_report.md
│   │   └── visualizations/
│   └── eda_*.ipynb                       ← per-source EDA
├── pipeline/                             ← ingestion + QoL computation
├── data/
│   ├── raw/                              ← parquet files per source
│   ├── processed/                        ← qol_scores.parquet
│   └── db/nj_pipeline.duckdb
├── NJ_Analysis_Vault/                    ← Obsidian research notes + EDA charts
├── config.py                             ← URLs, API keys, paths
└── environment.yml
```

---

Caio Tormin · 2026 · Assisted by Claude Code
