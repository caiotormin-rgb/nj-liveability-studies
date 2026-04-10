"""
Tree Equity Score Data Ingestion Script

This script downloads and processes Tree Equity Score data from American Forests.
Data source: https://www.treeequityscore.org/

Tree Equity Score is calculated at the Census block group level and includes:
- Tree canopy coverage percentage
- Priority index (equity score 0-100)
- Demographics and socioeconomic factors
- Urban heat metrics

Data Download:
Direct URL: https://tes-app-data-share.s3.amazonaws.com/nj/nj_csv.zip
"""

import duckdb
import pandas as pd
from pathlib import Path
import sys
import urllib.request
import zipfile

# Configuration
DB_PATH = Path("data/db/nj_pipeline.duckdb")
RAW_DATA_PATH = Path("data/raw/tree_equity")
PROCESSED_DATA_PATH = Path("data/processed/tree_equity")
DOWNLOAD_URL = "https://tes-app-data-share.s3.amazonaws.com/nj/nj_csv.zip"
ZIP_FILE = RAW_DATA_PATH / "nj_csv.zip"


def download_tree_equity_data():
    """Download Tree Equity Score data from S3."""
    print(f"\nDownloading Tree Equity Score data from:")
    print(f"{DOWNLOAD_URL}")

    # Ensure directory exists
    RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)

    try:
        # Download the file
        print("Downloading... (this may take a moment)")
        urllib.request.urlretrieve(DOWNLOAD_URL, ZIP_FILE)
        print(f"Downloaded to: {ZIP_FILE}")

        # Extract the ZIP file
        print("\nExtracting files...")
        with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
            zip_ref.extractall(RAW_DATA_PATH)

        # List extracted files
        extracted = list(RAW_DATA_PATH.glob("*.csv"))
        print(f"Extracted {len(extracted)} CSV file(s):")
        for f in extracted:
            print(f"  - {f.name}")

        return True

    except Exception as e:
        print(f"ERROR downloading data: {e}")
        return False


def find_tree_equity_file():
    """Find the tree equity data file in the raw data directory."""
    # Look for CSV files (excluding the zip file itself)
    csv_files = [f for f in RAW_DATA_PATH.glob("*.csv")]
    geojson_files = list(RAW_DATA_PATH.glob("*.geojson"))
    shp_files = list(RAW_DATA_PATH.glob("*.shp"))

    if csv_files:
        return csv_files[0], 'csv'
    elif geojson_files:
        return geojson_files[0], 'geojson'
    elif shp_files:
        return shp_files[0], 'shapefile'
    else:
        return None, None


def load_tree_equity_csv(file_path):
    """Load tree equity data from CSV."""
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df):,} records")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head())
    return df


def load_tree_equity_geojson(file_path):
    """Load tree equity data from GeoJSON."""
    try:
        import geopandas as gpd
        print(f"Loading data from {file_path}...")
        gdf = gpd.read_file(file_path)
        # Convert to regular dataframe for DuckDB
        df = pd.DataFrame(gdf.drop(columns='geometry'))
        print(f"Loaded {len(df):,} records")
        print(f"\nColumns: {list(df.columns)}")
        return df
    except ImportError:
        print("ERROR: geopandas not installed. Install with: conda install geopandas")
        sys.exit(1)


def clean_tree_equity_data(df):
    """Clean and standardize tree equity data."""
    print("\nCleaning data...")

    # Common column name variations - update based on actual data
    column_mapping = {
        'GEOID': 'block_group_id',
        'geoid': 'block_group_id',
        'BlockGroup': 'block_group_id',
        'block_group': 'block_group_id',
        'GEOID10': 'block_group_id',
        'TreeEquityScore': 'tree_equity_score',
        'tree_equity_score': 'tree_equity_score',
        'TES': 'tree_equity_score',
        'tes': 'tree_equity_score',
        'TreeCanopyPct': 'tree_canopy_pct',
        'tree_canopy_pct': 'tree_canopy_pct',
        'canopy_pct': 'tree_canopy_pct',
        'tree_canopy_percent': 'tree_canopy_pct',
        'PriorityIndex': 'priority_index',
        'priority': 'priority_index',
    }

    # Rename columns if they exist
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

    # Filter for New Jersey block groups (GEOID starts with 34)
    if 'block_group_id' in df.columns:
        df['block_group_id'] = df['block_group_id'].astype(str)
        df = df[df['block_group_id'].str.startswith('34')]
        print(f"Filtered to {len(df):,} NJ block groups")

    # Remove any duplicate records
    initial_count = len(df)
    if 'block_group_id' in df.columns:
        df = df.drop_duplicates(subset=['block_group_id'])
        if len(df) < initial_count:
            print(f"Removed {initial_count - len(df):,} duplicate records")

    return df


def aggregate_to_zcta(conn):
    """
    Aggregate block group level tree equity data to ZCTA level.

    This uses a simplified approach based on GEOID structure.
    Block group GEOID: 12 digits (state+county+tract+block group)
    ZCTA can be approximated from the ZIP code portion.

    Note: A proper geographic crosswalk would be more accurate.
    """
    print("\nAggregating to ZCTA level...")

    # This aggregation strategy depends on the actual data structure
    # We'll try multiple approaches

    try:
        # Check if we have a ZIP code column
        schema_check = conn.execute("""
            SELECT column_name
            FROM (DESCRIBE tree_equity_blockgroups)
            WHERE column_name LIKE '%zip%' OR column_name LIKE '%zcta%'
        """).df()

        if len(schema_check) > 0:
            # If there's a direct ZCTA/ZIP column, use it
            zip_col = schema_check['column_name'].iloc[0]
            agg_query = f"""
            CREATE OR REPLACE TABLE tree_equity_zcta AS
            SELECT
                {zip_col} as zcta,
                COUNT(*) as num_block_groups,
                AVG(tree_equity_score) as avg_tree_equity_score,
                MIN(tree_equity_score) as min_tree_equity_score,
                MAX(tree_equity_score) as max_tree_equity_score,
                AVG(tree_canopy_pct) as avg_tree_canopy_pct,
                MIN(tree_canopy_pct) as min_tree_canopy_pct,
                MAX(tree_canopy_pct) as max_tree_canopy_pct
            FROM tree_equity_blockgroups
            WHERE {zip_col} IS NOT NULL
            GROUP BY {zip_col}
            ORDER BY zcta
            """
        else:
            # Fallback: Try to extract from block group ID
            # Note: This is approximate and may not work perfectly
            print("Note: No direct ZCTA column found. Using approximation from GEOID.")
            print("Results may need manual verification.")

            agg_query = """
            CREATE OR REPLACE TABLE tree_equity_zcta AS
            SELECT
                SUBSTRING(block_group_id, 1, 5) as zcta_approx,
                COUNT(*) as num_block_groups,
                AVG(tree_equity_score) as avg_tree_equity_score,
                MIN(tree_equity_score) as min_tree_equity_score,
                MAX(tree_equity_score) as max_tree_equity_score,
                AVG(tree_canopy_pct) as avg_tree_canopy_pct,
                MIN(tree_canopy_pct) as min_tree_canopy_pct,
                MAX(tree_canopy_pct) as max_tree_canopy_pct
            FROM tree_equity_blockgroups
            WHERE block_group_id IS NOT NULL
            GROUP BY SUBSTRING(block_group_id, 1, 5)
            ORDER BY zcta_approx
            """

        conn.execute(agg_query)
        result = conn.execute("SELECT COUNT(*) as count FROM tree_equity_zcta").fetchone()
        print(f"Created ZCTA-level aggregation with {result[0]:,} ZCTAs")

        # Show sample
        sample = conn.execute("SELECT * FROM tree_equity_zcta LIMIT 5").df()
        print("\nSample aggregated data:")
        print(sample)

    except Exception as e:
        print(f"Note: ZCTA aggregation encountered an issue: {e}")
        print("You may need to adjust the aggregation logic based on actual data structure")


def load_to_duckdb(df):
    """Load tree equity data into DuckDB."""
    print(f"\nLoading data into DuckDB at {DB_PATH}...")

    conn = duckdb.connect(str(DB_PATH))

    # Create block group level table
    conn.execute("DROP TABLE IF EXISTS tree_equity_blockgroups")
    conn.execute("CREATE TABLE tree_equity_blockgroups AS SELECT * FROM df")

    # Get record count
    count = conn.execute("SELECT COUNT(*) FROM tree_equity_blockgroups").fetchone()[0]
    print(f"Loaded {count:,} records into tree_equity_blockgroups table")

    # Show schema
    schema = conn.execute("DESCRIBE tree_equity_blockgroups").df()
    print("\nTable schema:")
    print(schema)

    # Try to aggregate to ZCTA level
    aggregate_to_zcta(conn)

    conn.close()
    print("\nData loading complete!")


def main():
    """Main execution function."""
    print("=" * 70)
    print("TREE EQUITY SCORE DATA INGESTION")
    print("=" * 70)

    # Check if data file exists
    file_path, file_type = find_tree_equity_file()

    if file_path is None:
        print("\nNo data file found. Attempting to download...")
        success = download_tree_equity_data()

        if not success:
            print("\nFailed to download data automatically.")
            print("\nManual download instructions:")
            print(f"1. Visit: {DOWNLOAD_URL}")
            print(f"2. Save to: {RAW_DATA_PATH.absolute()}/")
            print("3. Run this script again")
            return

        # Try to find the file again after download
        file_path, file_type = find_tree_equity_file()
        if file_path is None:
            print("ERROR: Could not find CSV file after extraction")
            return

    print(f"\nFound data file: {file_path.name} ({file_type})")

    # Load data based on file type
    if file_type == 'csv':
        df = load_tree_equity_csv(file_path)
    elif file_type == 'geojson':
        df = load_tree_equity_geojson(file_path)
    else:
        print(f"Shapefile format requires geopandas. Converting to CSV first...")
        return

    # Clean and process
    df = clean_tree_equity_data(df)

    # Save processed data
    PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)
    processed_file = PROCESSED_DATA_PATH / "tree_equity_nj_processed.csv"
    df.to_csv(processed_file, index=False)
    print(f"\nSaved processed data to: {processed_file}")

    # Load into DuckDB
    load_to_duckdb(df)

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Open: notebooks/eda_tree_equity.ipynb")
    print("2. Join with CDC PLACES and Zillow data for analysis")
    print("3. Create environmental health visualizations")


if __name__ == "__main__":
    main()
