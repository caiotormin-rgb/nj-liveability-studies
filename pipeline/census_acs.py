"""
census_acs.py – US Census Bureau ACS 5-year Estimates Pipeline

Fetches ACS 5-year estimates for:
  1. NJ Places (municipalities / boroughs / cities / townships) – ~565 geographies
  2. ZCTAs (ZIP Code Tabulation Areas) for NJ

Variables pulled: demographics, income, poverty, housing values, rent,
rent burden, education, employment status, commuting mode.

Time series: ACS_YEARS defined in config.py (default 2012 – 2023).
Get a free Census API key at: https://api.census.gov/data/key_signup.html

Output tables in DuckDB:
  acs_places  – municipality-level, wide format, one row per (geoid, year)
  acs_zctas   – ZCTA-level, wide format, one row per (zcta, year)
"""

import math
import time
from typing import Optional
import os
import pandas as pd
import requests

from config import (
    ACS_VARIABLES,
    ACS_YEARS,
    CENSUS_API_KEY,
    NJ_FIPS,
)
from .base import BasePipeline


# Max variables per Census API request (URL length limit is ~2000 chars)
_BATCH_SIZE = 48

class CensusACSPipeline(BasePipeline):
    """
    Pulls ACS 5-year estimates from the Census Bureau API for all NJ
    municipalities (places) and ZCTAs across multiple survey years.
    """

    source_name = "census_acs"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or CENSUS_API_KEY
        if not self.api_key:
            self.logger.warning(
                "No CENSUS_API_KEY set. Requests will be rate-limited (500/day). "
                "Get a free key at https://api.census.gov/data/key_signup.html"
            )

    # ── Internal helpers ───────────────────────────────────────────────────

    def _fetch_acs(
        self,
        year: int,
        variables: list[str],
        geo_for: str,
        geo_in: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Query the Census ACS 5-year API for a single year and geography.

        Parameters
        ----------
        year      : survey year (e.g. 2022 → 2018-2022 window)
        variables : list of Census variable IDs (e.g. ['B01003_001E'])
        geo_for   : 'place:*' or 'zip code tabulation area:*'
        geo_in    : 'state:34' (optional, not all geographies support it)
        """
        base_url = f"https://api.census.gov/data/{year}/acs/acs5"

        # Always include NAME and GEO_ID
        get_cols = ["NAME", "GEO_ID"] + variables

        params: dict = {"get": ",".join(get_cols), "for": geo_for}
        if geo_in:
            params["in"] = geo_in
        if self.api_key:
            params["key"] = self.api_key

        resp = requests.get(base_url, params=params, timeout=60)
        if resp.status_code == 204:
            self.logger.warning(f"No data returned for year={year}, geo={geo_for}")
            return pd.DataFrame()
        resp.raise_for_status()

        data = resp.json()
        if not data or len(data) < 2:
            return pd.DataFrame()

        df = pd.DataFrame(data[1:], columns=data[0])
        df["acs_year"] = year
        return df

    def _fetch_acs_batched(
        self,
        year: int,
        geo_for: str,
        geo_in: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch all ACS_VARIABLES for a given year+geography in batches,
        then merge on NAME + GEO_ID.
        """
        var_ids = [v for v, _ in ACS_VARIABLES.values()]
        batches = [
            var_ids[i : i + _BATCH_SIZE]
            for i in range(0, len(var_ids), _BATCH_SIZE)
        ]

        frames = []
        for batch in batches:
            df_batch = self._fetch_acs(year, batch, geo_for, geo_in)
            if df_batch.empty:
                continue
            frames.append(df_batch)
            time.sleep(0.15)  # be polite to the API

        if not frames:
            return pd.DataFrame()

        # Merge all batches on NAME + GEO_ID + acs_year
        merged = frames[0]
        for frame in frames[1:]:
            # drop duplicate columns except merge keys
            drop_cols = [
                c for c in frame.columns
                if c in merged.columns and c not in ("NAME", "GEO_ID", "acs_year")
            ]
            frame = frame.drop(columns=drop_cols)
            merged = merged.merge(frame, on=["NAME", "GEO_ID", "acs_year"], how="left")

        return merged

    # ── ETL steps ──────────────────────────────────────────────────────────

    def extract(
        self,
        years: Optional[list[int]] = None,
        force_refresh: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Download ACS data for NJ places and ZCTAs across all specified years.
        Uses cached Parquet files when available.
        """
        years = years or ACS_YEARS
        all_frames: list[pd.DataFrame] = []

        for year in years:
            # ── Places (municipalities) ────────────────────────────────────
            cache_key_places = f"places_{year}.parquet"
            df_places = self.load_raw(cache_key_places) if not force_refresh else None

            if df_places is None:
                self.logger.info(f"  Fetching ACS places: year={year}")
                try:
                    df_places = self._fetch_acs_batched(
                        year, geo_for="place:*", geo_in=f"state:{NJ_FIPS}"
                    )
                    df_places["geo_type"] = "place"
                    if not df_places.empty:
                        self.save_raw(df_places, cache_key_places)
                except Exception as e:
                    self.logger.error(f"  ✗ Failed places {year}: {e}")
                    df_places = pd.DataFrame()

            if not df_places.empty:
                all_frames.append(df_places)

            # ── ZCTAs ──────────────────────────────────────────────────────
            # Note: ZCTAs don't fully nest within states in the Census API.
            # We pull NJ-adjacent ZCTAs using a cross-reference approach:
            # fetch by state=34 which returns ZCTAs with centroid in NJ.
            cache_key_zctas = f"zctas_{year}.parquet"
            df_zctas = self.load_raw(cache_key_zctas) if not force_refresh else None

            if df_zctas is None:
                self.logger.info(f"  Fetching ACS ZCTAs: year={year}")
                try:
                    # Some years support in=state:34 for ZCTAs; try both ways
                    try:
                        df_zctas = self._fetch_acs_batched(
                            year,
                            geo_for="zip code tabulation area:*",
                            geo_in=f"state:{NJ_FIPS}",
                        )
                    except Exception:
                        # Fallback: pull all ZCTAs (large!) – you can also
                        # pre-filter by providing a known NJ ZCTA list
                        self.logger.warning(
                            f"  ZCTA state filter failed for {year}, "
                            "using national pull (will filter in transform)"
                        )
                        df_zctas = self._fetch_acs_batched(
                            year,
                            geo_for="zip code tabulation area:*",
                            geo_in=None,
                        )

                    df_zctas["geo_type"] = "zcta"
                    if not df_zctas.empty:
                        self.save_raw(df_zctas, cache_key_zctas)

                except Exception as e:
                    self.logger.error(f"  ✗ Failed ZCTAs {year}: {e}")
                    df_zctas = pd.DataFrame()

            if not df_zctas.empty:
                all_frames.append(df_zctas)

            time.sleep(0.5)  # ~2 req/s well within the Census rate limit

        if not all_frames:
            self.logger.error("No data retrieved – check your Census API key.")
            return pd.DataFrame()

        return pd.concat(all_frames, ignore_index=True)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and type-cast the raw ACS DataFrame.

        Steps:
          1. Rename Census variable IDs to human-readable column names
          2. Parse GEO_ID into state/county/place components
          3. Cast numeric columns; replace Census sentinel values (-666666666)
             and negative values with NaN
          4. Derive computed columns (poverty rate, unemployment rate, etc.)
          5. Filter ZCTAs to NJ-based only (when national pull was used)
        """
        if df.empty:
            return df

        # ── 1. Rename variables ────────────────────────────────────────────
        # Build reverse map: census_var_id → short_name
        rename_map = {v_id: name for name, (v_id, _) in ACS_VARIABLES.items()}
        df = df.rename(columns=rename_map)

        # ── 2. Parse geography identifiers ────────────────────────────────
        # GEO_ID formats:
        #   Places:  "1600000US3400000" → state=34, place=00000
        #   ZCTAs:   "8600000US07001"   → zcta=07001
        df["geoid"] = df["GEO_ID"].str.replace(r".*US", "", regex=True)

        places_mask = df["geo_type"] == "place"
        if places_mask.any():
            df.loc[places_mask, "state_fips"]   = df.loc[places_mask, "geoid"].str[:2]
            df.loc[places_mask, "place_fips"]   = df.loc[places_mask, "geoid"].str[2:]
            # Extract county from 'state' column if present
            if "state" in df.columns:
                df.loc[places_mask, "state_fips"] = df.loc[places_mask, "state"]
            if "place" in df.columns:
                df.loc[places_mask, "place_fips"] = df.loc[places_mask, "place"]

        zcta_mask = df["geo_type"] == "zcta"
        if zcta_mask.any():
            df.loc[zcta_mask, "zcta"] = df.loc[zcta_mask, "geoid"].str[-5:]
            # Filter to NJ ZCTAs (07001-08999 range) when doing national pulls
            if "zip code tabulation area" in df.columns:
                df.loc[zcta_mask, "zcta"] = df.loc[
                    zcta_mask, "zip code tabulation area"
                ]
            nj_zcta_mask = zcta_mask & df["zcta"].str.startswith(("07", "08"))
            df = df[~zcta_mask | nj_zcta_mask]

        # ── 3. Cast numerics ───────────────────────────────────────────────
        numeric_cols = list(ACS_VARIABLES.keys())
        sentinel_values = {-666666666, -999999999, -888888888, -333333333}

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                # Replace Census sentinel values with NaN
                df[col] = df[col].where(~df[col].isin(sentinel_values), other=pd.NA)
                # Negative values (besides valid negatives) → NaN
                # Income, population, etc. cannot be negative
                if col not in ["gini_index"]:
                    df[col] = df[col].where(df[col] >= 0, other=pd.NA)

        # ── 4. Derived / computed columns ─────────────────────────────────
        # Poverty rate (%)
        df["poverty_rate"] = (
            df["poverty_count"] / df["poverty_universe"] * 100
        ).round(2)

        # Unemployment rate (%)
        df["unemployment_rate_acs"] = (
            df["unemployed"] / df["labor_force"] * 100
        ).round(2)

        # Bachelor's degree attainment rate (%) – BA or higher
        df["pct_bachelors_plus"] = (
            (
                df["edu_bachelors"]
                + df["edu_masters"]
                + df["edu_professional"]
                + df["edu_doctorate"]
            )
            / df["edu_total_25plus"]
            * 100
        ).round(2)

        # Homeownership rate (%)
        df["homeownership_rate"] = (
            df["housing_owner_occ"] / df["housing_occupied"] * 100
        ).round(2)

        # Vacancy rate (%)
        df["vacancy_rate"] = (
            df["housing_vacant"] / df["housing_units_total"] * 100
        ).round(2)

        # Renter cost burden rate (% severely cost-burdened, paying >30% income)
        df["rent_burden_30plus_pct"] = (
            (
                df["rent_burden_30_34pct"]
                + df["rent_burden_35_39pct"]
                + df["rent_burden_40_49pct"]
                + df["rent_burden_50plus_pct"]
            )
            / df["rent_burden_universe"]
            * 100
        ).round(2)

        # Severe rent burden (>50% income on rent)
        df["rent_burden_severe_pct"] = (
            df["rent_burden_50plus_pct"] / df["rent_burden_universe"] * 100
        ).round(2)

        # Average commute time (minutes)
        df["avg_commute_minutes"] = (
            df["travel_time_aggregate"] / df["travel_time_universe"]
        ).round(1)

        # Transit commute share (%)
        df["pct_transit_commute"] = (
            df["commute_transit"] / df["commute_total"] * 100
        ).round(2)

        # Work-from-home share (%)
        df["pct_wfh"] = (
            df["commute_wfh"] / df["commute_total"] * 100
        ).round(2)

        # Diversity index: 1 − Σ(pᵢ²)  (Herfindahl-style)
        # (higher = more diverse)
        race_cols = ["race_white", "race_black", "race_asian", "race_hispanic"]
        present_race_cols = [c for c in race_cols if c in df.columns]
        if present_race_cols and "pop_total" in df.columns:
            shares = df[present_race_cols].div(df["pop_total"], axis=0)
            df["diversity_index"] = (1 - (shares**2).sum(axis=1)).round(4)

        # ── 5. Clean up raw Census geography columns ───────────────────────
        drop_cols = [
            c for c in df.columns
            if c in ("state", "place", "zip code tabulation area", "GEO_ID")
        ]
        df = df.drop(columns=drop_cols, errors="ignore")

        # ── 6. Final type fixes ────────────────────────────────────────────
        df["acs_year"] = df["acs_year"].astype(int)
        df["NAME"] = df["NAME"].str.strip()

        # Reorder: identifiers first
        id_cols = [
            "geoid", "NAME", "geo_type", "state_fips", "place_fips", "zcta",
            "acs_year",
        ]
        present_id_cols = [c for c in id_cols if c in df.columns]
        other_cols = [c for c in df.columns if c not in present_id_cols]
        df = df[present_id_cols + other_cols]

        df = df.reset_index(drop=True)
        return df

    def run_places_only(self, years: Optional[list[int]] = None, **kwargs):
        """Convenience: run only the Places (municipality) portion."""
        years = years or ACS_YEARS
        all_frames = []
        for year in years:
            cache_key = f"places_{year}.parquet"
            df = self.load_raw(cache_key)
            if df is None:
                self.logger.info(f"  Fetching ACS places: year={year}")
                df = self._fetch_acs_batched(
                    year, geo_for="place:*", geo_in=f"state:{NJ_FIPS}"
                )
                df["geo_type"] = "place"
                if not df.empty:
                    self.save_raw(df, cache_key)
            all_frames.append(df)
            time.sleep(0.5)

        raw = pd.concat(all_frames, ignore_index=True)
        processed = self.transform(raw)
        self.load(processed[processed["geo_type"] == "place"], "acs_places")
        return processed
