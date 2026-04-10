"""
Tree canopy coverage vs. quality of life and home values (NJ places).
Outputs a markdown report and a couple of charts.
"""
from __future__ import annotations

import os
import re
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm


ROOT = os.path.dirname(os.path.dirname(__file__))
TREE_PATH = os.path.join(ROOT, "data/processed/tree_equity/tree_equity_nj_processed.csv")
ACS_PLACES_PATH = os.path.join(ROOT, "data/census_acs_places_2023.csv")
OUT_DIR = os.path.join(ROOT, "NJ_Analysis_Vault/EDA Findings")
os.makedirs(OUT_DIR, exist_ok=True)

REPORT_PATH = os.path.join(OUT_DIR, "tree_canopy_qol_home_values_report.md")
PLOT_CANOPY_HOME = os.path.join(OUT_DIR, "tree_canopy_vs_home_value.png")
PLOT_CANOPY_QOL = os.path.join(OUT_DIR, "tree_canopy_vs_qol.png")


def normalize_place_name(s: str) -> str:
    s = s.lower().strip()
    s = s.replace(", new jersey", "")
    s = re.sub(r"\s+", " ", s)
    return s


def strip_place_suffix(s: str) -> str:
    s = normalize_place_name(s)
    s = re.sub(r"\s+(city|borough|township|town|village|cdp)$", "", s).strip()
    return s


def pop_weighted_mean(df: pd.DataFrame, value_col: str, weight_col: str) -> float:
    vals = df[value_col].astype(float)
    w = df[weight_col].astype(float)
    wsum = w.sum()
    if wsum <= 0 or vals.isnull().all():
        return float("nan")
    return (vals * w).sum() / wsum


def zscore(series: pd.Series) -> pd.Series:
    return (series - series.mean()) / series.std(ddof=0)


def compute_qol_index(df: pd.DataFrame) -> pd.Series:
    # Lightweight QoL index using ACS variables, similar to pipeline approach.
    components = {
        "income_median_hh": +1,
        "poverty_rate": -1,
        "unemployment_rate_acs": -1,
        "pct_bachelors_plus": +1,
        "homeownership_rate": +1,
        "rent_burden_30plus_pct": -1,
        "avg_commute_minutes": -1,
    }
    zs = []
    for col, sign in components.items():
        zs.append(sign * zscore(df[col]))
    composite = np.mean(zs, axis=0)
    scaled = 100 * (composite - np.nanmin(composite)) / (np.nanmax(composite) - np.nanmin(composite))
    return pd.Series(scaled, index=df.index)


def build_tree_equity_place() -> pd.DataFrame:
    te = pd.read_csv(TREE_PATH)
    te["place_norm"] = te["place"].astype(str).map(normalize_place_name)

    grouped = []
    for place, g in te.groupby("place_norm"):
        grouped.append(
            {
                "place_norm": place,
                "place_raw": g["place"].iloc[0],
                "cbg_pop": g["cbg_pop"].sum(),
                "treecanopy": pop_weighted_mean(g, "treecanopy", "cbg_pop"),
                "priority_i": pop_weighted_mean(g, "priority_i", "cbg_pop"),
                "tree_equity_score": pop_weighted_mean(g, "tree_equity_score", "cbg_pop"),
                "temp_diff": pop_weighted_mean(g, "temp_diff", "cbg_pop"),
                "pctpov": pop_weighted_mean(g, "pctpov", "cbg_pop"),
                "pctpoc": pop_weighted_mean(g, "pctpoc", "cbg_pop"),
            }
        )
    return pd.DataFrame(grouped)


def build_acs_places() -> pd.DataFrame:
    acs = pd.read_csv(ACS_PLACES_PATH)
    acs = acs[acs["acs_year"] == 2023].copy()
    acs["place_norm"] = acs["NAME"].astype(str).map(normalize_place_name)
    acs["place_norm_stripped"] = acs["NAME"].astype(str).map(strip_place_suffix)
    return acs


def join_places(tree_places: pd.DataFrame, acs_places: pd.DataFrame) -> pd.DataFrame:
    # Exact match first.
    exact = acs_places.merge(tree_places, on="place_norm", how="left", suffixes=("", "_tree"))

    # Fallback using suffix-stripped keys for still-unmatched rows.
    if exact["treecanopy"].isna().any():
        tree_places = tree_places.copy()
        tree_places["place_norm_stripped"] = tree_places["place_norm"].map(strip_place_suffix)
        acs_places = acs_places.copy()
        acs_places["place_norm_stripped"] = acs_places["place_norm"].map(strip_place_suffix)

        fallback = acs_places.merge(tree_places, on="place_norm_stripped", how="left", suffixes=("", "_tree"))

        # Prefer exact matches; fill only where missing.
        for col in ["place_raw", "cbg_pop", "treecanopy", "priority_i", "tree_equity_score", "temp_diff", "pctpov", "pctpoc"]:
            exact[col] = exact[col].fillna(fallback[col])
    return exact


def run_regression(df: pd.DataFrame, y: str, x_cols: list[str]) -> sm.regression.linear_model.RegressionResultsWrapper:
    X = df[x_cols].copy()
    X = sm.add_constant(X, has_constant="add")
    model = sm.OLS(df[y], X, missing="drop").fit(cov_type="HC3")
    return model


def standardize(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c] = zscore(out[c])
    return out


def main() -> None:
    tree_places = build_tree_equity_place()
    acs_places = build_acs_places()
    merged = join_places(tree_places, acs_places)

    # Keep relevant columns and basic filters.
    use = merged.copy()
    use = use[use["treecanopy"].notnull()].copy()
    use = use[use["pop_total"] >= 1500].copy()
    use = use[(use["home_value_median"] > 0) & (use["income_median_hh"] > 0)].copy()
    use["treecanopy_pct"] = use["treecanopy"] * 100
    use["qol_index"] = compute_qol_index(use)
    use["log_home_value"] = np.log(use["home_value_median"])
    use["log_income"] = np.log(use["income_median_hh"])

    # Correlations
    corr_rows = []
    for metric in ["home_value_median", "qol_index"]:
        pearson = use["treecanopy_pct"].corr(use[metric], method="pearson")
        spearman = use["treecanopy_pct"].corr(use[metric], method="spearman")
        corr_rows.append((metric, pearson, spearman))

    # Regressions (standardized betas for interpretability)
    base_cols = ["treecanopy_pct", "log_income"]
    extra_cols = ["poverty_rate", "pct_bachelors_plus", "homeownership_rate", "avg_commute_minutes"]

    df_std_home = standardize(use, base_cols + extra_cols + ["log_home_value"])
    model_home_base = run_regression(df_std_home, "log_home_value", base_cols)
    model_home_full = run_regression(df_std_home, "log_home_value", base_cols + extra_cols)

    df_std_qol = standardize(use, base_cols + extra_cols + ["qol_index", "rent_burden_30plus_pct", "unemployment_rate_acs"])
    model_qol_base = run_regression(df_std_qol, "qol_index", base_cols)
    model_qol_full = run_regression(
        df_std_qol,
        "qol_index",
        base_cols + extra_cols + ["rent_burden_30plus_pct", "unemployment_rate_acs"],
    )

    # Plots
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(data=use, x="treecanopy_pct", y="home_value_median", ax=ax, scatter_kws={"alpha": 0.45, "s": 20})
    ax.set_xlabel("Tree canopy (%)")
    ax.set_ylabel("Median home value (ACS)")
    ax.set_title("Tree Canopy vs. Median Home Value (NJ Places, 2023)")
    fig.tight_layout()
    fig.savefig(PLOT_CANOPY_HOME, dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(data=use, x="treecanopy_pct", y="qol_index", ax=ax, scatter_kws={"alpha": 0.45, "s": 20}, color="teal")
    ax.set_xlabel("Tree canopy (%)")
    ax.set_ylabel("QoL index (0-100)")
    ax.set_title("Tree Canopy vs. QoL Index (NJ Places, 2023)")
    fig.tight_layout()
    fig.savefig(PLOT_CANOPY_QOL, dpi=150)
    plt.close(fig)

    # Report
    n_places = len(use)
    corr_md = "\n".join(
        [f"| {m.replace('_',' ').title()} | {p:.3f} | {s:.3f} |" for m, p, s in corr_rows]
    )

    def coef_table(model: sm.regression.linear_model.RegressionResultsWrapper, label: str) -> str:
        rows = []
        for var in model.params.index:
            if var == "const":
                continue
            rows.append(
                f"| {label} | {var} | {model.params[var]:.3f} | {model.pvalues[var]:.3g} |"
            )
        return "\n".join(rows)

    report = f"""# Tree Canopy Coverage, Quality of Life, and Home Values (NJ Places, 2023)\n\n"""
    report += f"**Scope:** NJ places (municipalities/CDPs) with population ≥ 1,500 and matched Tree Equity + ACS data.\n"
    report += f"**Sample size:** {n_places} places.\n"
    report += f"**Tree equity aggregation:** population-weighted averages of block-group Tree Equity data.\n"
    report += f"**Home values:** ACS median home value (2023).\n"
    report += f"**QoL index:** composite of income, poverty, unemployment, education, homeownership, rent burden, commute time.\n\n"

    report += "## Key Correlations\n"
    report += "| Outcome | Pearson r | Spearman ρ |\n"
    report += "|---|---:|---:|\n"
    report += corr_md + "\n\n"

    report += "## Regression Results (Standardized Betas)\n"
    report += "**Home Value (log) ~ Tree Canopy + Income**\n"
    report += "| Model | Variable | Beta | p-value |\n"
    report += "|---|---|---:|---:|\n"
    report += coef_table(model_home_base, "Base") + "\n\n"

    report += "**Home Value (log) ~ Tree Canopy + Income + Controls**\n"
    report += "| Model | Variable | Beta | p-value |\n"
    report += "|---|---|---:|---:|\n"
    report += coef_table(model_home_full, "Full") + "\n\n"

    report += "**QoL Index ~ Tree Canopy + Income**\n"
    report += "| Model | Variable | Beta | p-value |\n"
    report += "|---|---|---:|---:|\n"
    report += coef_table(model_qol_base, "Base") + "\n\n"

    report += "**QoL Index ~ Tree Canopy + Income + Controls**\n"
    report += "| Model | Variable | Beta | p-value |\n"
    report += "|---|---|---:|---:|\n"
    report += coef_table(model_qol_full, "Full") + "\n\n"

    report += "## Figures\n"
    report += f"- `NJ_Analysis_Vault/EDA Findings/{os.path.basename(PLOT_CANOPY_HOME)}`\n"
    report += f"- `NJ_Analysis_Vault/EDA Findings/{os.path.basename(PLOT_CANOPY_QOL)}`\n\n"

    report += "## Notes & Limitations\n"
    report += "- Place names are matched by normalization and suffix stripping; some municipalities may be unmatched or mis-matched.\n"
    report += "- Tree canopy is aggregated from block groups to places using population weights, not spatial area.\n"
    report += "- ACS home values are self-reported medians; they are not Zillow ZHVI.\n"
    report += "- Cross-sectional analysis (2023) shows association, not causation.\n"

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Wrote report: {REPORT_PATH}")
    print(f"Wrote plots: {PLOT_CANOPY_HOME}, {PLOT_CANOPY_QOL}")


if __name__ == "__main__":
    main()
