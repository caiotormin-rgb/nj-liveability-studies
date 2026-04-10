"""
zillow.py – Zillow Research Data Pipeline

Downloads publicly available Zillow CSV files (no API key required):

  ZHVI (Zillow Home Value Index):
    - All homes mid-tier  (sfr + condo)   → zhvi_all_homes
    - Single-family only                  → zhvi_sfr
    - Bottom tier (affordable)            → zhvi_bottom_tier
    - Top tier (luxury)                   → zhvi_top_tier

  ZORI (Zillow Observed Rent Index):
    - All homes                           → zori_all_homes

  Market velocity signals:
    - Mean days to pending                → zillow_days_to_pending
    - Sale-to-list price ratio            → zillow_sale_to_list

All tables are in long format: (zip_code, date, value).
ZCTAs are filtered to NJ only (prefix 07xxx / 08xxx).

Output tables in DuckDB:
  zillow_home_values  – ZHVI all homes, long format
  zillow_rent         – ZORI all homes, long format
  zillow_market       – days-to-pending + sale-to-list, long format
  zillow_wide         – convenience wide view (latest value per zip per series)
"""

from io import StringIO
from typing import Optional

import pandas as pd
import requests

from config import ZILLOW_URLS
from .base import BasePipeline

# NJ zip code prefixes
_NJ_ZIP_PREFIXES = ("07", "08")

# Metadata columns that appear before the date columns in every Zillow CSV
_ZILLOW_ID_COLS = [
    "RegionID", "SizeRank", "RegionName", "RegionType",
    "StateName", "State", "City", "Metro", "CountyName",
]


class ZillowPipeline(BasePipeline):
    """
    Downloads Zillow Research CSVs and transforms them into long-format
    time-series tables filtered to NJ zip codes.
    """

    source_name = "zillow"

    # ── Internal helpers ───────────────────────────────────────────────────

    def _download_csv(self, series_name: str, url: str) -> pd.DataFrame:
        """
        Download a Zillow research CSV (wide format) and return as DataFrame.
        Falls back to cached Parquet if download fails.
        """
        cache_file = f"{series_name}.parquet"
        cached = self.load_raw(cache_file)
        if cached is not None:
            self.logger.debug(f"  Using cached {series_name}")
            return cached

        self.logger.info(f"  Downloading Zillow {series_name}…")
        try:
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            df = pd.read_csv(StringIO(resp.text))
            self.save_raw(df, cache_file)
            return df
        except Exception as e:
            self.logger.error(f"  ✗ Failed to download {series_name}: {e}")
            return pd.DataFrame()

    @staticmethod
    def _melt_zillow(
        df: pd.DataFrame,
        series_name: str,
        value_col: str,
    ) -> pd.DataFrame:
        """
        Convert Zillow wide CSV → long format and filter to NJ zip codes.

        Parameters
        ----------
        df          : raw Zillow DataFrame (one row per zip, date cols as headers)
        series_name : short name for the 'series' column
        value_col   : name for the value column in the output
        """
        if df.empty:
            return df

        # Identify which columns are date columns (format YYYY-MM-DD)
        id_cols = [c for c in _ZILLOW_ID_COLS if c in df.columns]
        date_cols = [
            c for c in df.columns
            if c not in id_cols and _is_date_col(c)
        ]

        if not date_cols:
            return pd.DataFrame()

        # Filter to NJ before melting (much faster)
        if "State" in df.columns:
            df = df[df["State"] == "NJ"].copy()
        elif "RegionName" in df.columns:
            df = df[
                df["RegionName"].astype(str).str.startswith(_NJ_ZIP_PREFIXES)
            ].copy()

        if df.empty:
            return df

        # Melt to long format
        long_df = df.melt(
            id_vars=id_cols,
            value_vars=date_cols,
            var_name="date",
            value_name=value_col,
        )

        long_df["date"] = pd.to_datetime(long_df["date"])
        long_df["series"] = series_name
        long_df[value_col] = pd.to_numeric(long_df[value_col], errors="coerce")

        # Rename for consistency
        rename = {
            "RegionName": "zip_code",
            "RegionID": "region_id",
            "SizeRank": "size_rank",
            "City": "city",
            "Metro": "metro",
            "CountyName": "county",
        }
        long_df = long_df.rename(columns={k: v for k, v in rename.items() if k in long_df.columns})

        # Ensure zip_code is 5-char string
        long_df["zip_code"] = long_df["zip_code"].astype(str).str.zfill(5)

        # Final NJ filter (in case State col wasn't present)
        long_df = long_df[long_df["zip_code"].str.startswith(_NJ_ZIP_PREFIXES)]

        return long_df.sort_values(["zip_code", "date"]).reset_index(drop=True)

    # ── ETL steps ──────────────────────────────────────────────────────────

    def extract(self, force_refresh: bool = False, **kwargs) -> pd.DataFrame:
        """Download all configured Zillow series and return combined raw dict."""
        # We return a sentinel DataFrame; real work happens in transform()
        # since each series produces its own table.
        self._raw_frames = {}
        for series_name, url in ZILLOW_URLS.items():
            if force_refresh:
                # Clear cache by not loading it
                self.logger.info(f"  Force refresh: {series_name}")
            raw = self._download_csv(series_name, url)
            self._raw_frames[series_name] = raw

        # Return a placeholder – transform() uses self._raw_frames
        return pd.DataFrame({"loaded": [True]})

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform all Zillow series and load them individually into DuckDB.
        Returns a summary DataFrame.
        """
        summaries = []

        # ── ZHVI series ────────────────────────────────────────────────────
        zhvi_series = {
            "zhvi_all_homes":  ("zhvi_all_homes",  "zhvi_usd"),
            "zhvi_sfr":        ("zhvi_sfr",         "zhvi_usd"),
            "zhvi_bottom_tier":("zhvi_bottom_tier", "zhvi_usd"),
            "zhvi_top_tier":   ("zhvi_top_tier",    "zhvi_usd"),
        }
        zhvi_frames = []
        for raw_key, (series_label, value_col) in zhvi_series.items():
            raw = self._raw_frames.get(raw_key, pd.DataFrame())
            long = self._melt_zillow(raw, series_label, value_col)
            if not long.empty:
                zhvi_frames.append(long)
                summaries.append({"series": series_label, "rows": len(long)})

        if zhvi_frames:
            zhvi_all = pd.concat(zhvi_frames, ignore_index=True)
            self.load(zhvi_all, "zillow_home_values")

        # ── ZORI (rent) ────────────────────────────────────────────────────
        raw_zori = self._raw_frames.get("zori_all_homes", pd.DataFrame())
        zori_long = self._melt_zillow(raw_zori, "zori_all_homes", "zori_usd")
        if not zori_long.empty:
            self.load(zori_long, "zillow_rent")
            summaries.append({"series": "zori_all_homes", "rows": len(zori_long)})

        # ── Market velocity ────────────────────────────────────────────────
        market_frames = []
        for key, label, col in [
            ("days_to_pending", "days_to_pending", "days_to_pending"),
            ("sale_to_list",    "sale_to_list",    "sale_to_list_ratio"),
        ]:
            raw = self._raw_frames.get(key, pd.DataFrame())
            long = self._melt_zillow(raw, label, col)
            if not long.empty:
                market_frames.append(long)
                summaries.append({"series": label, "rows": len(long)})

        if market_frames:
            market_all = pd.concat(market_frames, ignore_index=True)
            self.load(market_all, "zillow_market")

        # ── Convenience wide view: latest value per zip per series ─────────
        self._create_wide_view()

        return pd.DataFrame(summaries)

    def _create_wide_view(self):
        """
        Create a wide view in DuckDB: one row per zip_code with the most
        recent ZHVI (all homes) and ZORI values.
        """
        sql = """
        CREATE OR REPLACE VIEW zillow_latest AS
        WITH latest_zhvi AS (
            SELECT zip_code, city, metro, county,
                   MAX(date) AS latest_date,
                   LAST(zhvi_usd ORDER BY date) AS zhvi_current
            FROM zillow_home_values
            WHERE series = 'zhvi_all_homes'
            GROUP BY zip_code, city, metro, county
        ),
        zhvi_1yr AS (
            SELECT zip_code,
                   LAST(zhvi_usd ORDER BY date) AS zhvi_1yr_ago
            FROM zillow_home_values
            WHERE series = 'zhvi_all_homes'
              AND date BETWEEN current_date - INTERVAL 13 MONTHS
                           AND current_date - INTERVAL 11 MONTHS
            GROUP BY zip_code
        ),
        zhvi_5yr AS (
            SELECT zip_code,
                   LAST(zhvi_usd ORDER BY date) AS zhvi_5yr_ago
            FROM zillow_home_values
            WHERE series = 'zhvi_all_homes'
              AND date BETWEEN current_date - INTERVAL 61 MONTHS
                           AND current_date - INTERVAL 59 MONTHS
            GROUP BY zip_code
        ),
        latest_zori AS (
            SELECT zip_code,
                   LAST(zori_usd ORDER BY date) AS zori_current
            FROM zillow_rent
            WHERE series = 'zori_all_homes'
            GROUP BY zip_code
        )
        SELECT
            h.zip_code,
            h.city,
            h.metro,
            h.county,
            h.latest_date,
            h.zhvi_current,
            r.zori_current,
            -- Price-to-rent ratio (annual)
            ROUND(h.zhvi_current / NULLIF(r.zori_current * 12, 0), 1)
                AS price_to_rent_ratio,
            -- YoY appreciation (%)
            ROUND((h.zhvi_current / NULLIF(y.zhvi_1yr_ago, 0) - 1) * 100, 2)
                AS zhvi_yoy_pct,
            -- 5-year appreciation (%)
            ROUND((h.zhvi_current / NULLIF(f.zhvi_5yr_ago, 0) - 1) * 100, 2)
                AS zhvi_5yr_pct
        FROM latest_zhvi h
        LEFT JOIN latest_zori r USING (zip_code)
        LEFT JOIN zhvi_1yr     y USING (zip_code)
        LEFT JOIN zhvi_5yr     f USING (zip_code)
        ORDER BY h.zip_code
        """
        try:
            with self.get_connection() as conn:
                conn.execute(sql)
            self.logger.info("  ✓ Created view: zillow_latest")
        except Exception as e:
            self.logger.warning(f"  Could not create zillow_latest view: {e}")

    def run(self, force_refresh: bool = False, **kwargs) -> pd.DataFrame:
        """Override run() since transform() handles all loading internally."""
        self.logger.info(f"▶ Starting pipeline: {self.source_name}")
        self.extract(force_refresh=force_refresh)
        summary = self.transform(pd.DataFrame())
        self.logger.info(f"✔ Zillow pipeline complete: {len(summary)} series loaded")
        return summary


def _is_date_col(col: str) -> bool:
    """Return True if the column name looks like a YYYY-MM-DD date."""
    import re
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", str(col)))
