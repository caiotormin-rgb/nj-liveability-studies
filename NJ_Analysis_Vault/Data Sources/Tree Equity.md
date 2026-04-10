---
tags: [data-source]
source: Tree Equity Score (American Forests)
status: loaded
api-key-required: false
geography: census-block-group
time-series: snapshot (Tree Equity 2.0, 2023)
duckdb-tables: [tree_equity_blockgroups]
updated: 2026-03-05
---

# Tree Equity Score

**No API key needed.** Data downloaded from [Tree Equity Score website](https://www.treeequityscore.org).

## Database Table

### `tree_equity_blockgroups`
**6,363 block groups** across **21 NJ counties**

## Run pipeline
```bash
python scripts/ingest_tree_equity.py
```

## Schema (48 columns total)

### Most Commonly Used Columns
| Column | Type | Description | Range/Scale |
|--------|------|-------------|-------------|
| `block_group_id` | VARCHAR | 12-digit Census Block Group ID | Primary key |
| `county` | VARCHAR | County name | e.g., "Bergen County" |
| `treecanopy` | DOUBLE | Current tree canopy coverage | 0-1 scale (multiply by 100 for %) |
| `tc_gap` | DOUBLE | Gap between current and goal | 0-1 scale |
| `priority_i` | DOUBLE | Priority index for tree planting | 0-1 scale (higher = more need) |
| `tree_equity_score` | DOUBLE | Tree Equity Score | 0-100 scale |
| `cbg_pop` | DOUBLE | Block group population | Census estimate |
| `land_area` | DOUBLE | Land area | Square miles |
| `pctpoc` | DOUBLE | Percent people of color | 0-1 scale |
| `pctpov` | DOUBLE | Percent in poverty | 0-1 scale |
| `temp_diff` | DOUBLE | Temperature difference from average | Urban heat island (°F) |

### All 48 Columns
<details>
<summary>Click to expand full schema</summary>

**Geographic Identifiers (7)**
- `block_group_id` - 12-digit Census Block Group ID
- `place` - Place name
- `state` - State name
- `state_abbr` - State abbreviation (NJ)
- `county` - County name
- `ua_name` - Urban area name
- `congressio` - Congressional district

**Population & Demographics (11)**
- `cbg_pop` - Block group population
- `acs_pop` - ACS population estimate
- `ua_pop` - Urban area population
- `pctpoc` - Percent people of color (0-1)
- `pctpocnorm` - Normalized % people of color
- `pctpov` - Percent in poverty (0-1)
- `pctpovnorm` - Normalized poverty rate
- `child_perc` - Percent children (0-1)
- `seniorperc` - Percent seniors (0-1)
- `dep_ratio` - Dependency ratio
- `depratnorm` - Normalized dependency ratio

**Economic Indicators (4)**
- `unemplrate` - Unemployment rate (0-1)
- `unemplnorm` - Normalized unemployment
- `linguistic` - Linguistic isolation (0-1)
- `lingnorm` - Normalized linguistic isolation

**Tree Canopy Metrics (5)**
- `treecanopy` - Current tree canopy coverage (0-1)
- `tc_goal` - Tree canopy goal (0-1)
- `tc_gap` - Gap between current and goal (0-1)
- `cnpysource` - Canopy data source
- `biome` - Biome classification

**Environmental & Health (4)**
- `land_area` - Land area (sq mi)
- `temp_diff` - Temperature difference (°F)
- `temp_norm` - Normalized temperature
- `health_nor` - Normalized health index

**Tree Equity Scores & Rankings (5)**
- `tree_equity_score` - Tree Equity Score (0-100)
- `tesctyscor` - City-level Tree Equity Score (0-100)
- `priority_i` - Priority index (0-1, higher = more need)
- `rank` - Rank within group
- `rankgrpsz` - Rank group size

**Historical & Justice (2)**
- `holc_grade` - Historical HOLC redlining grade (A/B/C/D)
- `ej_disadva` - Environmental justice disadvantage

**Building & Vegetation Density by radius (9)**
- `_bld1200`, `_veg1200`, `_tot1200` - Building/vegetation at 1200m
- `_bld1500`, `_veg1500`, `_tot1500` - Building/vegetation at 1500m
- `_bld1800`, `_veg1800`, `_tot1800` - Building/vegetation at 1800m
- `dep_perc` - Dependency percentage

</details>

## Key Statistics
- **Tree canopy range**: 14.1% (Hudson County) to 60.4% (Sussex County)
- **Mean tree coverage**: 35.6%
- **Priority index**: Higher values (>0.4) indicate greater need for tree planting

## Geographic join note
Tree Equity data is at **Census Block Group** level. The current pipeline aggregates to **county level** for joining with ZCTA-level datasets (CDC PLACES, Zillow):

```sql
-- County-level aggregation for joining
WITH tree_county AS (
    SELECT
        county,
        AVG(treecanopy) * 100 as avg_tree_canopy_pct,
        AVG(priority_i) as avg_priority_index,
        AVG(tree_equity_score) as avg_tree_equity_score
    FROM tree_equity_blockgroups
    GROUP BY county
)
SELECT
    c.zcta,
    z.county,
    t.avg_tree_canopy_pct,
    t.avg_tree_equity_score,
    c.obesity,
    c.diabetes
FROM cdc_places_wide c
INNER JOIN zillow_latest z ON c.zcta = z.zip_code
INNER JOIN tree_county t ON z.county = t.county
WHERE c.year = 2023;
```

**Note**: All ZCTAs within the same county receive the same aggregated tree metrics. For more granular analysis, consider spatial joins or Census crosswalk files (Block Group → ZCTA).

## Why it matters
Studies show 10–15% home value premium near mature tree cover. Also linked to lower crime, better mental health, lower urban heat island effect, and stormwater management.

