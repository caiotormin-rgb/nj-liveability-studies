"""
base.py – Abstract base class for all NJ pipeline ETL modules.

Every pipeline inherits from BasePipeline and implements:
  - extract()   → returns a raw pd.DataFrame
  - transform() → cleans / reshapes the raw DataFrame
  - run()       → orchestrates extract → transform → load → save_raw
"""

import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path

import duckdb
import pandas as pd

from config import DB_PATH, RAW_DIR, LOG_LEVEL, LOG_FORMAT

# ── Module-level logging setup ─────────────────────────────────────────────
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)


class BasePipeline(ABC):
    """
    Abstract base class for all data pipelines.

    Provides:
      - DuckDB connection management
      - Raw-data caching to Parquet
      - Standard load / upsert patterns
      - Retry-aware HTTP helpers
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._db_path = DB_PATH
        self._raw_dir = Path(RAW_DIR) / self.source_name
        self._raw_dir.mkdir(parents=True, exist_ok=True)

    # ── Identity ───────────────────────────────────────────────────────────

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Short identifier used for table names and raw-data sub-directories."""

    # ── Abstract ETL steps ─────────────────────────────────────────────────

    @abstractmethod
    def extract(self, **kwargs) -> pd.DataFrame:
        """Download / query the source data and return a raw DataFrame."""

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean, reshape, and type-cast the raw DataFrame."""

    # ── DuckDB helpers ─────────────────────────────────────────────────────

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Return an open DuckDB connection. Caller is responsible for closing."""
        return duckdb.connect(self._db_path)

    def load(
        self,
        df: pd.DataFrame,
        table_name: str,
        if_exists: str = "replace",
        schema: str = "main",
    ) -> None:
        """
        Load *df* into DuckDB table *schema.table_name*.

        Parameters
        ----------
        df          : DataFrame to load
        table_name  : destination table (created if absent)
        if_exists   : 'replace' (drop + recreate) | 'append' | 'skip'
        schema      : DuckDB schema (default 'main')
        """
        if df.empty:
            self.logger.warning(f"Empty DataFrame – skipping load to {table_name}.")
            return

        full_name = f"{schema}.{table_name}" if schema != "main" else table_name

        with self.get_connection() as conn:
            if if_exists == "replace":
                conn.execute(
                    f"CREATE OR REPLACE TABLE {full_name} AS SELECT * FROM df"
                )
            elif if_exists == "append":
                # Create table if it doesn't exist, then INSERT
                conn.execute(
                    f"CREATE TABLE IF NOT EXISTS {full_name} AS "
                    f"SELECT * FROM df WHERE 1=0"
                )
                conn.execute(f"INSERT INTO {full_name} SELECT * FROM df")
            elif if_exists == "skip":
                exists = conn.execute(
                    f"SELECT count(*) FROM information_schema.tables "
                    f"WHERE table_name = '{table_name}'"
                ).fetchone()[0]
                if exists:
                    self.logger.info(f"Table {table_name} already exists – skipping.")
                    return
                conn.execute(
                    f"CREATE TABLE {full_name} AS SELECT * FROM df"
                )

        self.logger.info(f"  ✓ Loaded {len(df):,} rows → {full_name}")

    def query(self, sql: str) -> pd.DataFrame:
        """Run *sql* against the DuckDB database and return a DataFrame."""
        with self.get_connection() as conn:
            return conn.execute(sql).df()

    def table_exists(self, table_name: str) -> bool:
        with self.get_connection() as conn:
            count = conn.execute(
                "SELECT count(*) FROM information_schema.tables "
                f"WHERE table_name = '{table_name}'"
            ).fetchone()[0]
        return count > 0

    # ── Raw-data caching ───────────────────────────────────────────────────

    def save_raw(self, df: pd.DataFrame, filename: str) -> Path:
        """Save *df* as a Parquet file in the raw data directory."""
        path = self._raw_dir / filename
        df.to_parquet(path, index=False)
        self.logger.debug(f"  Raw data saved → {path}")
        return path

    def load_raw(self, filename: str) -> pd.DataFrame | None:
        """Load a previously saved raw Parquet file, or return None."""
        path = self._raw_dir / filename
        if path.exists():
            self.logger.debug(f"  Loading cached raw data ← {path}")
            return pd.read_parquet(path)
        return None

    # ── HTTP helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _get_with_retry(
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        max_retries: int = 3,
        backoff: float = 2.0,
        timeout: int = 60,
    ) -> dict | list:
        """
        Perform a GET request with exponential back-off on 429/5xx responses.

        Returns parsed JSON or raises on persistent failure.
        """
        import requests

        for attempt in range(1, max_retries + 1):
            resp = requests.get(
                url, params=params, headers=headers, timeout=timeout
            )
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_retries:
                wait = backoff ** attempt
                logging.getLogger("BasePipeline").warning(
                    f"HTTP {resp.status_code} on attempt {attempt}/{max_retries}. "
                    f"Retrying in {wait:.0f}s…"
                )
                time.sleep(wait)
            else:
                resp.raise_for_status()

    # ── Orchestrator ───────────────────────────────────────────────────────

    def run(self, force_refresh: bool = False, **kwargs) -> pd.DataFrame:
        """
        Full ETL run: extract → transform → load.

        Parameters
        ----------
        force_refresh : if True, re-download even if raw cache exists
        **kwargs      : forwarded to extract()
        """
        self.logger.info(f"▶ Starting pipeline: {self.source_name}")
        t0 = time.time()

        raw_df = self.extract(force_refresh=force_refresh, **kwargs)
        processed_df = self.transform(raw_df)
        self.load(processed_df, self.source_name.replace("-", "_"))

        elapsed = time.time() - t0
        self.logger.info(
            f"✔ Completed {self.source_name} in {elapsed:.1f}s "
            f"| {len(processed_df):,} rows"
        )
        return processed_df
