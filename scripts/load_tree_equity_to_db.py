"""
Load processed Tree Equity data into DuckDB.

This script loads the already-downloaded and processed Tree Equity Score data
into the DuckDB database. Run this if the main ingestion script failed due to
database locks.
"""

import duckdb
import pandas as pd
from pathlib import Path

# Configuration
DB_PATH = Path("data/db/nj_pipeline.duckdb")
PROCESSED_FILE = Path("data/processed/tree_equity/tree_equity_nj_processed.csv")

print("=" * 70)
print("TREE EQUITY DATA - DATABASE LOADING")
print("=" * 70)

# Check if processed file exists
if not PROCESSED_FILE.exists():
    print(f"\nERROR: Processed file not found at: {PROCESSED_FILE}")
    print("Please run: python scripts/ingest_tree_equity.py first")
    exit(1)

# Load the processed data
print(f"\nLoading processed data from: {PROCESSED_FILE}")
df = pd.read_csv(PROCESSED_FILE)
print(f"Loaded {len(df):,} records")

# Connect to database
print(f"\nConnecting to database: {DB_PATH}")
conn = duckdb.connect(str(DB_PATH))

# Create block group level table
print("\nCreating tree_equity_blockgroups table...")
conn.execute("DROP TABLE IF EXISTS tree_equity_blockgroups")
conn.execute("CREATE TABLE tree_equity_blockgroups AS SELECT * FROM df")

count = conn.execute("SELECT COUNT(*) FROM tree_equity_blockgroups").fetchone()[0]
print(f"✓ Loaded {count:,} records into tree_equity_blockgroups")

# Show schema
schema = conn.execute("DESCRIBE tree_equity_blockgroups").df()
print(f"\nTable has {len(schema)} columns")

# Check for ZCTA/ZIP columns
print("\nChecking for geographic identifiers...")
key_cols = conn.execute("""
    SELECT column_name
    FROM (DESCRIBE tree_equity_blockgroups)
    WHERE column_name IN ('GEOID', 'place', 'county', 'state')
""").df()
print(f"Key columns: {list(key_cols['column_name'])}")

# Create ZCTA aggregation
print("\n" + "=" * 70)
print("AGGREGATING TO ZCTA LEVEL")
print("=" * 70)

# The Tree Equity data uses block group GEOIDs
# We need to map these to ZCTAs for joining with other data

# First, let's check if we can use county as a proxy
print("\nChecking data structure...")
sample = conn.execute("SELECT GEOID, place, county, treecanopy, tes FROM tree_equity_blockgroups LIMIT 5").df()
print(sample)

# Strategy: Create a lookup from block group to approximate ZCTA
# For NJ, we can try to match by place name or county
# This is approximate - ideally we'd use Census ZCTA-to-Block Group crosswalk

print("\nCreating ZCTA aggregation using place names as proxy...")

# Aggregate by place (which often corresponds to cities/towns with ZCTAs)
agg_query = """
CREATE OR REPLACE TABLE tree_equity_by_place AS
SELECT
    place,
    county,
    COUNT(*) as num_block_groups,
    AVG(treecanopy) as avg_tree_canopy_pct,
    MIN(treecanopy) as min_tree_canopy_pct,
    MAX(treecanopy) as max_tree_canopy_pct,
    AVG(tes) as avg_tree_equity_score,
    MIN(tes) as min_tree_equity_score,
    MAX(tes) as max_tree_equity_score,
    AVG(priority_i) as avg_priority_index,
    AVG(pctpoc) as avg_pct_poc,
    AVG(pctpov) as avg_pct_poverty,
    AVG(temp_diff) as avg_temp_difference
FROM tree_equity_blockgroups
WHERE place IS NOT NULL
GROUP BY place, county
ORDER BY place
"""

conn.execute(agg_query)
place_count = conn.execute("SELECT COUNT(*) FROM tree_equity_by_place").fetchone()[0]
print(f"✓ Created aggregation by place: {place_count} places")

# Also create county-level aggregation
print("\nCreating county-level aggregation...")
county_query = """
CREATE OR REPLACE TABLE tree_equity_by_county AS
SELECT
    county,
    COUNT(*) as num_block_groups,
    AVG(treecanopy) as avg_tree_canopy_pct,
    MIN(treecanopy) as min_tree_canopy_pct,
    MAX(treecanopy) as max_tree_canopy_pct,
    AVG(tes) as avg_tree_equity_score,
    MIN(tes) as min_tree_equity_score,
    MAX(tes) as max_tree_equity_score,
    AVG(priority_i) as avg_priority_index,
    AVG(pctpoc) as avg_pct_poc,
    AVG(pctpov) as avg_pct_poverty,
    AVG(temp_diff) as avg_temp_difference
FROM tree_equity_blockgroups
GROUP BY county
ORDER BY county
"""

conn.execute(county_query)
county_count = conn.execute("SELECT COUNT(*) FROM tree_equity_by_county").fetchone()[0]
print(f"✓ Created aggregation by county: {county_count} counties")

# Show sample of aggregated data
print("\nSample aggregated data by place:")
sample_agg = conn.execute("""
    SELECT place, county, num_block_groups, avg_tree_canopy_pct, avg_tree_equity_score
    FROM tree_equity_by_place
    ORDER BY avg_tree_equity_score DESC
    LIMIT 5
""").df()
print(sample_agg)

print("\nSample aggregated data by county:")
sample_county = conn.execute("""
    SELECT county, num_block_groups, avg_tree_canopy_pct, avg_tree_equity_score
    FROM tree_equity_by_county
    ORDER BY avg_tree_equity_score DESC
""").df()
print(sample_county)

# Note about ZCTA matching
print("\n" + "=" * 70)
print("NOTE: ZCTA MATCHING")
print("=" * 70)
print("""
The Tree Equity data is at the Census block group level.
For precise ZCTA-level analysis, we would need a geographic crosswalk.

For now, we've created aggregations by:
1. Place (city/town) - use tree_equity_by_place
2. County - use tree_equity_by_county

To join with your ZCTA-level data (CDC PLACES, Zillow):
- You can match by county
- Or manually map major cities to their primary ZCTAs

Example join by county:
SELECT
    c.zcta,
    c.obesity,
    z.zhvi_latest,
    t.avg_tree_canopy_pct
FROM cdc_places_wide c
JOIN zillow_zipcode_latest z ON c.zcta = z.zip_code
JOIN tree_equity_by_county t ON z.county = t.county
WHERE c.year = 2023
""")

# List all created tables
print("\n" + "=" * 70)
print("TABLES CREATED")
print("=" * 70)
tables = conn.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'main'
    AND table_name LIKE '%tree%'
    ORDER BY table_name
""").df()
print(tables)

conn.close()
print("\n✓ Database loading complete!")
