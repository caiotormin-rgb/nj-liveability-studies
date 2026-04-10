"""
cdc_places.py – CDC PLACES Local Health Data Pipeline

Fetches ZCTA-level health metrics from CDC PLACES via the Socrata API.
No API key required (but optional for higher rate limits).

Metrics include: diabetes, heart disease, obesity, smoking, mental health,
physical activity, insurance coverage, depression, and more.

See config.CDC_HEALTH_MEASURES for the full list of measures pulled.

Output tables in DuckDB:
  cdc_places_zcta   – health metrics by ZCTA + year (long format)
  cdc_places_wide   – pivoted wide format (one row per ZCTA+year, one col per measure)
"""

import time
from typing import Optional

import pandas as pd
import requests

from config import CDC_PLACES_ZCTA_ENDPOINT, CDC_HEALTH_MEASURES
from .base import BasePipeline

_NJ_ZIP_PREFIXES = ("07", "08")
_BATCH = 50000  # Socrata row limit per request


class CDCPlacesPipeline(BasePipeline):
    """
    Pulls CDC PLACES health metrics at the ZCTA level for New Jersey.
    """

    source_name = "cdc_places"

    def extract(self, force_refresh: bool = False, **kwargs) -> pd.DataFrame:
        """
        Download all CDC PLACES ZCTA records for NJ from Socrata.
        Uses pagination to handle the full dataset.
        """
        cache_file = "cdc_places_nj_raw.parquet"
        cached = self.load_raw(cache_file)
        if cached is not None and not force_refresh:
            self.logger.info("  Using cached CDC PLACES data")
            return cached

        self.logger.info("  Fetching CDC PLACES ZCTA data for NJ…")
        frames = []
        offset = 0

        measure_list = "','".join(CDC_HEALTH_MEASURES)
        while True:
            # Filter to NJ ZCTAs (locationid starts with 07/08) and target measures.
            # Note: the dataset no longer has a statedesc column.
            params = {
                "$limit":  _BATCH,
                "$offset": offset,
                "$where":  (
                    f"(locationid LIKE '07%' OR locationid LIKE '08%') "
                    f"AND measureid IN ('{measure_list}')"
                ),
                "$order":  "locationid,measureid,year",
            }
            try:
                resp = requests.get(
                    CDC_PLACES_ZCTA_ENDPOINT, params=params, timeout=90
                )
                resp.raise_for_status()
                batch = resp.json()
                if not batch:
                    break
                frames.append(pd.DataFrame(batch))
                self.logger.debug(
                    f"    Fetched {offset + len(batch)} rows so far…"
                )
                if len(batch) < _BATCH:
                    break
                offset += _BATCH
                time.sleep(0.3)
            except Exception as e:
                self.logger.error(f"  ✗ CDC PLACES fetch error: {e}")
                break

        if not frames:
            self.logger.warning("  No CDC PLACES data retrieved.")
            return pd.DataFrame()

        df = pd.concat(frames, ignore_index=True)
        self.save_raw(df, cache_file)
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean CDC PLACES data and produce:
          1. Long table (cdc_places_zcta)
          2. Wide table (cdc_places_wide) – pivoted by measureid
        """
        if df.empty:
            return df

        # ── Rename & select columns ────────────────────────────────────────
        rename = {
            "locationid":          "zcta",
            "locationname":        "location_name",
            "statedesc":           "state",
            "stateabbr":           "state_abbr",
            "year":                "year",
            "category":            "category",
            "measure":             "measure_label",
            "measureid":           "measure_id",
            "data_value":          "value",
            "data_value_type":     "value_type",      # Age-adjusted vs. crude prevalence
            "data_value_unit":     "value_unit",
            "low_confidence_limit":  "ci_low",
            "high_confidence_limit": "ci_high",
            "totalpopulation":     "total_pop",
            "geolocation":         "geolocation",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

        # ── Filter to NJ ZCTAs ─────────────────────────────────────────────
        df["zcta"] = df["zcta"].astype(str).str.zfill(5)
        df = df[df["zcta"].str.startswith(_NJ_ZIP_PREFIXES)].copy()

        # ── Cast types ────────────────────────────────────────────────────
        for col in ["value", "ci_low", "ci_high", "total_pop"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "year" in df.columns:
            df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

        # ── Long-format table ──────────────────────────────────────────────
        keep_cols = [
            "zcta", "location_name", "state_abbr", "year",
            "category", "measure_id", "measure_label",
            "value", "value_type", "ci_low", "ci_high", "total_pop",
        ]
        long_df = df[[c for c in keep_cols if c in df.columns]].copy()
        long_df = long_df.drop_duplicates(
            subset=["zcta", "year", "measure_id", "value_type"]
        )
        self.load(long_df, "cdc_places_zcta")

        # ── Wide-format table (age-adjusted prevalence only) ───────────────
        # Pivot so each measure becomes a column
        age_adj = long_df[
            long_df.get("value_type", pd.Series(dtype=str)).str.contains(
                "age.adjust", case=False, na=False
            )
            | long_df.get("value_type", pd.Series(dtype=str)).str.contains(
                "Age-adjusted", case=False, na=False
            )
        ] if "value_type" in long_df.columns else long_df

        if age_adj.empty:
            age_adj = long_df  # fall back to all value types

        try:
            wide_df = age_adj.pivot_table(
                index=["zcta", "location_name", "year"],
                columns="measure_id",
                values="value",
                aggfunc="mean",
            ).reset_index()
            wide_df.columns.name = None
            # Lowercase column names
            wide_df.columns = wide_df.columns.str.lower()
            self.load(wide_df, "cdc_places_wide")
        except Exception as e:
            self.logger.warning(f"  Could not create wide CDC table: {e}")

        return long_df
