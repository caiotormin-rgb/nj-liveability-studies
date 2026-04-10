"""
NJ Municipality Data Pipeline
──────────────────────────────
A collection of ETL pipelines that pull public data about New Jersey
municipalities and ZIP codes (ZCTAs) and load it into a local DuckDB
analytical database.

Sources:
  census_acs  – US Census Bureau ACS 5-year estimates
  zillow       – Zillow ZHVI (home values) and ZORI (rent index)
  nj_dca       – NJ Dept of Community Affairs municipal finance
  cdc_places   – CDC PLACES local health data
  bls_laus     – BLS Local Area Unemployment Statistics
  fbi_crime    – FBI Crime Data Explorer agency-level crime stats
  hud_chas     – HUD CHAS housing affordability
  fema_flood   – FEMA NFIP flood insurance policies & claims
"""

from .base import BasePipeline

__all__ = ["BasePipeline"]
