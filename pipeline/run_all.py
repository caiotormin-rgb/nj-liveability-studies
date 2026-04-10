"""
run_all.py – Pipeline orchestrator for the NJ Municipality Data Pipeline.

Usage (from project root):
  python -m pipeline.run_all               # run all pipelines
  python -m pipeline.run_all --only census_acs zillow   # run specific pipelines
  python -m pipeline.run_all --skip fbi_crime           # skip specific pipelines
  python -m pipeline.run_all --force                    # force refresh (ignore cache)

Each pipeline is independent; failures are logged but don't abort others.
"""

import argparse
import logging
import sys
import time
from pathlib import Path

# Add project root to sys.path when run directly
sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Environment guard ──────────────────────────────────────────────────────
try:
    import duckdb as _duckdb  # noqa: F401
except ModuleNotFoundError:
    print(
        "\nERROR: 'duckdb' is not installed in the current Python environment.\n"
        "Activate the project environment first:\n\n"
        "    conda activate nj-pipeline\n\n"
        "Then retry:\n"
        "    python pipeline/run_all.py\n",
        file=sys.stderr,
    )
    sys.exit(1)

from config import DB_PATH, LOG_FORMAT, LOG_LEVEL

# ── Set up logging ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(DB_PATH).parent / "pipeline.log"),
    ],
)
logger = logging.getLogger("run_all")


# ── Pipeline registry ──────────────────────────────────────────────────────
# Ordered by priority and data dependency
PIPELINE_REGISTRY = {
    "zillow": {
        "module": "pipeline.zillow",
        "class":  "ZillowPipeline",
        "description": "Zillow ZHVI home values + ZORI rent (no API key needed)",
        "requires_key": False,
    },
    "census_acs": {
        "module": "pipeline.census_acs",
        "class":  "CensusACSPipeline",
        "description": "US Census ACS demographics, housing, income, education (CENSUS_API_KEY)",
        "requires_key": True,
        "key_env": "CENSUS_API_KEY",
    },
    "nj_dca": {
        "module": "pipeline.nj_dca",
        "class":  "NJDCAPipeline",
        "description": "NJ DCA municipal budgets, property tax, equalization",
        "requires_key": False,
    },
    "cdc_places": {
        "module": "pipeline.cdc_places",
        "class":  "CDCPlacesPipeline",
        "description": "CDC PLACES health metrics by ZCTA (no API key needed)",
        "requires_key": False,
    },
}


def run_pipeline(name: str, config: dict, force: bool = False) -> dict:
    """
    Dynamically import and run a single pipeline.

    Returns a result dict: {name, status, rows, elapsed_s, error}
    """
    import importlib

    t0 = time.time()
    try:
        mod = importlib.import_module(config["module"])
        cls = getattr(mod, config["class"])
        pipeline = cls()
        result_df = pipeline.run(force_refresh=force)
        rows = len(result_df) if result_df is not None else 0
        return {
            "pipeline": name,
            "status":   "✓ success",
            "rows":     rows,
            "elapsed_s": round(time.time() - t0, 1),
            "error":    None,
        }
    except Exception as e:
        logger.error(f"  ✗ Pipeline '{name}' failed: {e}", exc_info=True)
        return {
            "pipeline": name,
            "status":   "✗ failed",
            "rows":     0,
            "elapsed_s": round(time.time() - t0, 1),
            "error":    str(e),
        }


def print_summary(results: list[dict]):
    """Pretty-print a run summary table."""
    print("\n" + "=" * 65)
    print("  PIPELINE RUN SUMMARY")
    print("=" * 65)
    print(f"  {'Pipeline':<20}  {'Status':<12}  {'Rows':>10}  {'Time':>8}")
    print("  " + "-" * 58)
    for r in results:
        print(
            f"  {r['pipeline']:<20}  {r['status']:<12}  "
            f"{r['rows']:>10,}  {r['elapsed_s']:>6.1f}s"
        )
        if r["error"]:
            print(f"  {'':20}  └─ {r['error'][:50]}")
    print("=" * 65)
    success = sum(1 for r in results if "success" in r["status"])
    print(f"  {success}/{len(results)} pipelines succeeded.")
    print(f"  Database: {DB_PATH}\n")


def create_analytical_views():
    """
    Create cross-source analytical views in DuckDB after all pipelines run.
    These views join multiple tables for analysis-ready queries.
    """
    import duckdb

    logger.info("Creating analytical views…")
    views = {
        # ── Alias views so analytical views can reference familiar names ────
        "acs_zctas": """
        CREATE OR REPLACE VIEW acs_zctas AS
        SELECT * FROM census_acs WHERE geo_type = 'zcta'
        """,

        "acs_places": """
        CREATE OR REPLACE VIEW acs_places AS
        SELECT * FROM census_acs WHERE geo_type = 'place'
        """,

        # ── ZIP-level quality-of-life scorecard ───────────────────────────
        "v_zipcode_scorecard": """
        CREATE OR REPLACE VIEW v_zipcode_scorecard AS
        SELECT
            -- Geography
            z.zip_code,
            z.city,
            z.metro,
            z.county              AS zillow_county,

            -- Real estate (Zillow)
            z.zhvi_current        AS home_value_zillow,
            z.zori_current        AS rent_zillow,
            z.price_to_rent_ratio,
            z.zhvi_yoy_pct        AS home_value_yoy_pct,
            z.zhvi_5yr_pct        AS home_value_5yr_pct,

            -- Demographics (ACS – most recent year)
            acs.pop_total,
            acs.age_median,
            acs.income_median_hh,
            acs.poverty_rate,
            acs.pct_bachelors_plus,
            acs.unemployment_rate_acs,
            acs.homeownership_rate,
            acs.home_value_median  AS home_value_acs,
            acs.gross_rent_median  AS rent_acs,
            acs.rent_burden_30plus_pct,
            acs.pct_transit_commute,
            acs.avg_commute_minutes,
            acs.pct_wfh,
            acs.diversity_index,

            -- Health (CDC PLACES – most recent)
            h.diabetes            AS diabetes_pct,
            h.obesity             AS obesity_pct,
            h.csmoking            AS smoking_pct,
            h.depression          AS depression_pct,
            h.lpa                 AS physical_inactivity_pct,
            h.access2             AS uninsured_pct,
            h.mhlth               AS poor_mental_health_pct,
            h.sleep               AS insufficient_sleep_pct,
            h.chd                 AS heart_disease_pct,

            -- Property tax (NJ Treasury – general tax rate at municipality level)
            -- nj_property_tax is keyed by district name, not zip code;
            -- these columns are NULL until a zip↔municipality crosswalk is added.
            NULL::DOUBLE           AS property_tax_rate,
            NULL::DOUBLE           AS avg_annual_tax_bill,
            NULL::DOUBLE           AS avg_assessed_value_residential

        FROM zillow_latest z

        LEFT JOIN (
            SELECT *
            FROM acs_zctas
            WHERE acs_year = (SELECT MAX(acs_year) FROM acs_zctas)
        ) acs ON acs.zcta = z.zip_code

        LEFT JOIN (
            SELECT zcta,
                   MAX(year) AS max_year
            FROM cdc_places_wide
            GROUP BY zcta
        ) h_yr ON h_yr.zcta = z.zip_code
        LEFT JOIN cdc_places_wide h
            ON h.zcta = z.zip_code AND h.year = h_yr.max_year

        ORDER BY z.zip_code
        """,

        # ── Municipality-level scorecard ───────────────────────────────────
        "v_municipality_scorecard": """
        CREATE OR REPLACE VIEW v_municipality_scorecard AS
        SELECT
            acs.geoid,
            acs.NAME             AS municipality,
            acs.acs_year,
            acs.pop_total,
            acs.age_median,
            acs.income_median_hh,
            acs.poverty_rate,
            acs.pct_bachelors_plus,
            acs.unemployment_rate_acs,
            acs.homeownership_rate,
            acs.home_value_median,
            acs.gross_rent_median,
            acs.rent_burden_30plus_pct,
            acs.avg_commute_minutes,
            acs.pct_transit_commute,
            acs.pct_wfh,
            acs.diversity_index,
            acs.gini_index,
            -- Property tax (joined by municipality name)
            pt.general_tax_rate
        FROM acs_places acs
        LEFT JOIN (
            SELECT district, general_tax_rate,
                   ROW_NUMBER() OVER (PARTITION BY district ORDER BY year DESC) AS rn
            FROM nj_property_tax
        ) pt ON LOWER(pt.district) LIKE '%' || LOWER(SPLIT_PART(acs.NAME, ',', 1)) || '%'
            AND pt.rn = 1
        ORDER BY acs.NAME, acs.acs_year
        """,

        # ── Home affordability index ───────────────────────────────────────
        "v_affordability_index": """
        CREATE OR REPLACE VIEW v_affordability_index AS
        SELECT
            zip_code,
            city,
            home_value_zillow,
            income_median_hh,
            rent_zillow,
            -- How many years of income to buy (lower = more affordable)
            ROUND(home_value_zillow / NULLIF(income_median_hh, 0), 2)
                AS home_price_to_income_ratio,
            -- % of gross income needed to rent (lower = more affordable)
            ROUND(rent_zillow * 12 / NULLIF(income_median_hh, 0) * 100, 1)
                AS rent_to_income_pct,
            price_to_rent_ratio,
            home_value_yoy_pct,
            home_value_5yr_pct,
            property_tax_rate,
            avg_annual_tax_bill,
            -- All-in annual ownership cost estimate: mortgage + tax
            -- (assumes 20% down, 7% rate, 30yr fixed)
            ROUND(
                (home_value_zillow * 0.80 * 0.07 / 12
                 * POWER(1 + 0.07/12, 360)
                 / (POWER(1 + 0.07/12, 360) - 1)
                ) * 12
                + COALESCE(avg_annual_tax_bill, home_value_zillow * property_tax_rate / 100, 0),
                0
            ) AS est_annual_ownership_cost_usd
        FROM v_zipcode_scorecard
        WHERE home_value_zillow IS NOT NULL
          AND income_median_hh  IS NOT NULL
        ORDER BY home_price_to_income_ratio
        """,
    }

    import duckdb
    with duckdb.connect(DB_PATH) as conn:
        for view_name, sql in views.items():
            try:
                conn.execute(sql)
                logger.info(f"  ✓ View created: {view_name}")
            except Exception as e:
                logger.warning(f"  ⚠ View {view_name} failed (some tables may not exist yet): {e}")


# ── CLI entry point ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Run NJ Municipality Data Pipeline(s)"
    )
    parser.add_argument(
        "--only",
        nargs="*",
        metavar="PIPELINE",
        help=f"Run only these pipelines. Choices: {list(PIPELINE_REGISTRY.keys())}",
    )
    parser.add_argument(
        "--skip",
        nargs="*",
        metavar="PIPELINE",
        default=[],
        help="Skip these pipelines.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if raw cache exists.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available pipelines and exit.",
    )
    args = parser.parse_args()

    if args.list:
        print("\nAvailable pipelines:\n")
        for name, cfg in PIPELINE_REGISTRY.items():
            key_note = f"  [API key: {cfg.get('key_env', '')}]" if cfg["requires_key"] else ""
            print(f"  {name:<20}  {cfg['description']}{key_note}")
        print()
        return

    # Determine which pipelines to run
    to_run = list(PIPELINE_REGISTRY.keys())
    if args.only:
        to_run = [p for p in args.only if p in PIPELINE_REGISTRY]
        unknown = [p for p in args.only if p not in PIPELINE_REGISTRY]
        if unknown:
            logger.warning(f"Unknown pipelines: {unknown}")
    if args.skip:
        to_run = [p for p in to_run if p not in args.skip]

    logger.info(f"Running {len(to_run)} pipeline(s): {to_run}")
    logger.info(f"Force refresh: {args.force}")
    logger.info(f"Database: {DB_PATH}")

    # ── Pre-flight: verify the database is not locked ──────────────────────
    import duckdb
    try:
        with duckdb.connect(DB_PATH):
            pass
    except duckdb.IOException as e:
        if "lock" in str(e).lower():
            logger.error(
                "Cannot open the database – another process holds the lock.\n"
                "  If you have a Jupyter notebook open, shut down its kernel:\n"
                "    Kernel → Shut Down Kernel  (or restart the kernel)\n"
                "  Then retry:\n"
                "    conda activate nj-pipeline && python pipeline/run_all.py"
            )
        else:
            logger.error(f"Cannot open database: {e}")
        sys.exit(1)

    # ── Run each pipeline ──────────────────────────────────────────────────
    results = []
    for name in to_run:
        cfg = PIPELINE_REGISTRY[name]
        logger.info(f"\n{'─'*60}\n  Pipeline: {name}\n{'─'*60}")
        result = run_pipeline(name, cfg, force=args.force)
        results.append(result)

    # ── Create analytical views ────────────────────────────────────────────
    try:
        create_analytical_views()
    except Exception as e:
        logger.warning(f"Could not create analytical views: {e}")

    print_summary(results)


if __name__ == "__main__":
    main()
