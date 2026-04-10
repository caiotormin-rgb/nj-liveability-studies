"""
nj_dca.py – NJ Department of Community Affairs (DCA) Municipal Finance Pipeline

Sources:
  1. NJ Open Data Portal (data.nj.gov / Socrata) – municipal property tax data
  2. NJ DCA Statistical Tables – budget summaries (scraped Excel downloads)
  3. NJ Division of Taxation – equalization / property values

Key datasets:
  - Municipal budget summaries (appropriations, revenues, surplus)
  - Property tax rates, ratios, and levy data
  - Equalized property values (EQV) – critical for real estate analysis
  - Staffing / personnel costs

NJ Open Data datasets (Socrata):
  - Property Tax: https://data.nj.gov/resource/9f3a-pkqs.json  (annual)
  - Municipal Budgets: available via DCA Statistical Tables Excel downloads
  - Senior Freeze: https://data.nj.gov/resource/3qem-6v3v.json

Output tables in DuckDB:
  nj_property_tax    – annual property tax rates and values by municipality
  nj_equalization    – equalized valuations by municipality
  nj_dca_budgets     – budget summaries where Excel files are available
"""

import io
from typing import Optional

import pandas as pd
import requests

from config import NJ_FIPS, NJ_COUNTY_FIPS
from .base import BasePipeline


# NJ Division of Taxation – General Tax Rate history (all municipalities, 1997-present)
_NJ_GTR_URL = "https://www.nj.gov/treasury/taxation/lpt/GTRhistory.xlsx"

# NJ Division of Taxation – Director's Ratio (equalization ratios, all municipalities)
_NJ_DIR_RATIOS_URL = "https://www.nj.gov/treasury/taxation/lpt/tev/DirRatios.xlsx"


class NJDCAPipeline(BasePipeline):
    """
    Pulls NJ DCA municipal finance data:
      - Property tax rates + levies (via NJ Open Data Socrata API)
      - Equalized property valuations
      - Municipal budget summaries (via DCA Excel downloads)
    """

    source_name = "nj_dca"

    # ── Property Tax (NJ Treasury GTR history) ────────────────────────────

    def _fetch_gtr_excel(self) -> pd.DataFrame:
        """
        Download NJ Division of Taxation General Tax Rate history Excel.
        Columns: county, cd_code, district, then one column per year (wide).
        Returns long-format DataFrame: (county, cd_code, district, year, general_tax_rate).
        """
        cache_file = "gtr_history.parquet"
        cached = self.load_raw(cache_file)
        if cached is not None:
            return cached

        self.logger.info("  Downloading NJ General Tax Rate history…")
        try:
            resp = requests.get(_NJ_GTR_URL, timeout=60)
            resp.raise_for_status()
            raw = pd.read_excel(io.BytesIO(resp.content), header=None, engine="openpyxl")

            # Row 0 = year values starting at col 3; rows 1-3 = label rows; data from row 4
            years = [int(v) for v in raw.iloc[0, 3:].dropna() if str(v).isdigit()]
            data = raw.iloc[4:].copy().reset_index(drop=True)
            data.columns = ["county", "cd_code", "district"] + years + (
                ["_extra"] * (len(data.columns) - 3 - len(years))
            )
            data = data[["county", "cd_code", "district"] + years].copy()
            data = data.dropna(subset=["county"])

            long = data.melt(
                id_vars=["county", "cd_code", "district"],
                var_name="year",
                value_name="general_tax_rate",
            )
            long["year"] = pd.to_numeric(long["year"], errors="coerce").astype("Int64")
            long["general_tax_rate"] = pd.to_numeric(long["general_tax_rate"], errors="coerce")
            long = long.dropna(subset=["general_tax_rate"])
            self.save_raw(long, cache_file)
            return long
        except Exception as e:
            self.logger.error(f"  ✗ GTR history download failed: {e}")
            return pd.DataFrame()

    # ── Equalization / Director's Ratios ──────────────────────────────────

    def _fetch_dir_ratios_excel(self) -> pd.DataFrame:
        """
        Download NJ Division of Taxation Director's Ratio Excel.
        Returns long-format DataFrame: (county, cd_code, district, year, directors_ratio).
        """
        cache_file = "dir_ratios.parquet"
        cached = self.load_raw(cache_file)
        if cached is not None:
            return cached

        self.logger.info("  Downloading NJ Director's Ratios…")
        try:
            resp = requests.get(_NJ_DIR_RATIOS_URL, timeout=60)
            resp.raise_for_status()
            raw = pd.read_excel(io.BytesIO(resp.content), header=None, engine="openpyxl")

            # Row 0 = title; row 1 = headers (County, CD Code, District, years...); data from row 2
            years = [int(v) for v in raw.iloc[1, 3:].dropna() if str(v).replace('.0','').isdigit()]
            data = raw.iloc[2:].copy().reset_index(drop=True)
            data.columns = ["county", "cd_code", "district"] + years + (
                ["_extra"] * (len(data.columns) - 3 - len(years))
            )
            data = data[["county", "cd_code", "district"] + years].copy()
            data = data.dropna(subset=["county"])

            long = data.melt(
                id_vars=["county", "cd_code", "district"],
                var_name="year",
                value_name="directors_ratio",
            )
            long["year"] = pd.to_numeric(long["year"], errors="coerce").astype("Int64")
            long["directors_ratio"] = pd.to_numeric(long["directors_ratio"], errors="coerce")
            long = long.dropna(subset=["directors_ratio"])
            self.save_raw(long, cache_file)
            return long
        except Exception as e:
            self.logger.error(f"  ✗ Director's Ratios download failed: {e}")
            return pd.DataFrame()

    # ── ETL steps ──────────────────────────────────────────────────────────

    def extract(self, force_refresh: bool = False, **kwargs) -> pd.DataFrame:
        """Extract all DCA data sources."""
        self._prop_tax_raw     = self._fetch_gtr_excel()
        self._equalization_raw = self._fetch_dir_ratios_excel()
        self._budgets_raw      = pd.DataFrame()  # DCA budget Excel URLs no longer available
        return pd.DataFrame({"fetched": [True]})

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform and load all DCA sub-datasets."""
        results = {}

        # ── Property Tax ───────────────────────────────────────────────────
        pt = self._transform_property_tax(self._prop_tax_raw)
        if not pt.empty:
            self.load(pt, "nj_property_tax")
            results["nj_property_tax"] = len(pt)

        # ── Equalization ───────────────────────────────────────────────────
        eq = self._transform_equalization(self._equalization_raw)
        if not eq.empty:
            self.load(eq, "nj_equalization")
            results["nj_equalization"] = len(eq)

        return pd.DataFrame([
            {"table": k, "rows": v} for k, v in results.items()
        ])

    def _transform_property_tax(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the GTR history long-format table (already tidy from extract)."""
        if df.empty:
            return df
        df.columns = df.columns.str.lower().str.replace(r"[^a-z0-9_]", "_", regex=True).str.strip("_")
        df["general_tax_rate"] = pd.to_numeric(df.get("general_tax_rate"), errors="coerce")
        return df.dropna(subset=["general_tax_rate"]).reset_index(drop=True)

    def _transform_equalization(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the Director's Ratios long-format table (already tidy from extract)."""
        if df.empty:
            return df
        df.columns = df.columns.str.lower().str.replace(r"[^a-z0-9_]", "_", regex=True).str.strip("_")
        df["directors_ratio"] = pd.to_numeric(df.get("directors_ratio"), errors="coerce")
        return df.dropna(subset=["directors_ratio"]).reset_index(drop=True)

    def run(self, force_refresh: bool = False, **kwargs) -> pd.DataFrame:
        """Override run() since transform() handles all loading internally."""
        self.logger.info(f"▶ Starting pipeline: {self.source_name}")
        self.extract(force_refresh=force_refresh)
        summary = self.transform(pd.DataFrame())
        self.logger.info(f"✔ NJ DCA pipeline complete")
        return summary
