# Tree Equity Score Data Download Instructions

## Data Source
**Tree Equity Score** by American Forests
Website: https://www.treeequityscore.org

## What is Tree Equity Score?
Tree Equity Score measures how well the benefits of urban tree canopy are reaching communities that need them most. The score ranges from 0-100 and is calculated at the Census block group level.

### Metrics Included:
- **Tree Canopy Coverage (%)**: Percent of area covered by tree canopy
- **Tree Equity Score (0-100)**: Composite score indicating tree equity
- **Priority Index**: Areas prioritized for tree planting
- **Demographics**: Population, income, race/ethnicity data
- **Urban Heat**: Heat island effects and surface temperature
- **Health Factors**: Asthma, heart disease prevalence

## How to Download Data

### Step 1: Visit the Website
Go to: **https://www.treeequityscore.org/methodology**

### Step 2: Navigate to Data Download
- Click on the **"Data Download"** tab at the top of the page
- Or look for "Methods & Data" in the main navigation menu

### Step 3: Select New Jersey
- Find New Jersey in the list of available states
- The data should be available for all 38 states covered by Tree Equity Score

### Step 4: Choose Format
Download in one of these formats:
- **CSV** (Recommended - easiest to work with)
- **GeoJSON** (If you need geographic boundaries)
- **Shapefile** (For GIS analysis)

### Step 5: Save the File
Place the downloaded file in this directory:
```
nj_pipeline/data/raw/tree_equity/
```

## Expected File Names
The file might be named something like:
- `TreeEquityScore_NewJersey.csv`
- `NJ_tree_equity_score.csv`
- `tree_equity_blockgroups_nj.csv`
- Or similar variation

## After Download

### Run the Ingestion Script
```bash
cd /Users/caiotormin/torm/nj_pipeline
python scripts/ingest_tree_equity.py
```

This script will:
1. Load the Tree Equity Score data
2. Clean and filter for New Jersey
3. Aggregate from block groups to ZCTA level
4. Load into the DuckDB database
5. Create analysis-ready tables

## Data Structure

### Block Group Level (tree_equity_blockgroups)
- **block_group_id**: Census block group GEOID (12-digit)
- **tree_equity_score**: Score from 0-100
- **tree_canopy_pct**: Percent tree canopy coverage
- **priority_index**: Priority for tree planting
- Additional demographic and environmental variables

### ZCTA Level (tree_equity_zcta)
Aggregated statistics for ZIP Code Tabulation Areas:
- **zcta**: 5-digit ZIP code
- **num_block_groups**: Number of block groups in this ZCTA
- **avg_tree_canopy_pct**: Average tree canopy coverage
- **avg_tree_equity_score**: Average equity score
- Min/max values for key metrics

## Integration with Existing Data

Once loaded, you can join tree equity data with:

### CDC PLACES Health Data
```sql
SELECT
    c.zcta,
    c.obesity,
    c.diabetes,
    t.avg_tree_canopy_pct,
    t.avg_tree_equity_score
FROM cdc_places_wide c
LEFT JOIN tree_equity_zcta t ON c.zcta = t.zcta
WHERE c.year = 2023
```

### Zillow Home Values
```sql
SELECT
    z.zip_code,
    z.zhvi_latest,
    t.avg_tree_canopy_pct,
    t.avg_tree_equity_score
FROM zillow_zipcode_latest z
LEFT JOIN tree_equity_zcta t ON z.zip_code = t.zcta
```

## Troubleshooting

### Data Not Available for Download
- Check if New Jersey is among the 38 states with available data
- Contact American Forests: https://www.treeequityscore.org/contact
- Check for updates to Tree Equity Score 2.0

### Different Column Names
The ingestion script handles common column name variations. If your data has different columns, update the `column_mapping` dictionary in `scripts/ingest_tree_equity.py`.

### Need Block Group to ZCTA Crosswalk
For more accurate ZCTA aggregation, you may need:
- Census Bureau's block group to ZCTA relationship file
- Spatial join using actual geographic boundaries
- Contact me if you need help with this

## Additional Resources

- **Tree Equity Score Map**: https://www.treeequityscore.org/map
- **Methodology**: https://www.treeequityscore.org/methodology
- **American Forests**: https://www.americanforests.org/
- **Tree Equity Score 2.0 Update**: https://www.americanforests.org/article/ushering-in-the-next-generation-tree-equity-score-2-0/

## Questions?
- Review the FAQ: https://www.treeequityscore.org/methodology?tab=faqs
- Contact American Forests for data-specific questions
- Check the ingestion script for processing details
