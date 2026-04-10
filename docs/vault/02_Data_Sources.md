# Data Sources Reference

This document provides detailed information about each data source in the NJ Pipeline.

---

## 1. Zillow Home Value Index (ZHVI) & Zillow Observed Rent Index (ZORI)

### Overview
Zillow Research publishes monthly housing market data including home values and rental prices. This is one of the most comprehensive public datasets on U.S. housing markets.

### Data Source Details
- **Provider**: Zillow Group, Inc.
- **Website**: https://www.zillow.com/research/data/
- **License**: Free for research and analysis
- **Update Frequency**: Monthly
- **Download Date**: Current (automated monthly updates available)

### Metrics

#### ZHVI (Home Value Index)
- **Definition**: Smoothed, seasonally adjusted measure of the typical home value in a given region
- **Methodology**: Zillow's proprietary Zestimate algorithm
- **Time Range**: 2000-01-31 to 2026-01-31 (313 months)
- **Coverage**: 552 New Jersey ZIP codes

#### ZORI (Observed Rent Index)
- **Definition**: Measure of typical observed market rent across regions
- **Methodology**: Based on rental listings on Zillow
- **Time Range**: 2015-01-31 to 2026-01-31 (133 months)
- **Coverage**: 230 New Jersey ZIP codes (subset with sufficient rental data)

### Database Tables

#### `zillow_home_values`
```sql
CREATE TABLE zillow_home_values (
    zip_code VARCHAR,
    date DATE,
    zhvi DOUBLE,              -- Home value in dollars
    region_name VARCHAR,
    state VARCHAR,
    city VARCHAR,
    metro VARCHAR,
    county VARCHAR
);
```
- **Records**: ~683,000
- **Key**: (zip_code, date)
- **Time Series**: Monthly

#### `zillow_rent_index`
```sql
CREATE TABLE zillow_rent_index (
    zip_code VARCHAR,
    date DATE,
    zori DOUBLE,              -- Monthly rent in dollars
    region_name VARCHAR,
    state VARCHAR,
    city VARCHAR,
    metro VARCHAR,
    county VARCHAR
);
```
- **Records**: ~152,000
- **Key**: (zip_code, date)
- **Time Series**: Monthly

#### `zillow_zipcode_latest`
```sql
CREATE TABLE zillow_zipcode_latest (
    zip_code VARCHAR PRIMARY KEY,
    city VARCHAR,
    county VARCHAR,
    zhvi_latest DOUBLE,       -- Latest home value
    zori_latest DOUBLE,       -- Latest rent
    price_to_rent_ratio DOUBLE, -- ZHVI / (ZORI * 12)
    zhvi_date DATE,
    zori_date DATE
);
```
- **Records**: 552
- **Purpose**: Quick access to current market conditions

### Data Quality

#### Completeness
- **ZHVI**: 99.8% complete (very few missing months)
- **ZORI**: Started in 2015, so no data before that
- **Geographic**: Not all ZIP codes have rental data

#### Known Issues
1. **ZORI Availability**: Only 230 of 552 ZIP codes have rent data
2. **Small ZIP Codes**: Some very small ZIP codes may have spotty data
3. **Seasonal Adjustment**: Values are smoothed, may not reflect exact transaction prices

### Use Cases
- Housing affordability analysis
- Market trend identification
- Gentrification tracking
- Price-to-rent ratio analysis
- Geographic price comparison

### Example Queries

```sql
-- Latest home values by county
SELECT
    county,
    COUNT(*) as num_zips,
    AVG(zhvi_latest) as avg_home_value,
    MEDIAN(zhvi_latest) as median_home_value
FROM zillow_zipcode_latest
WHERE zhvi_latest IS NOT NULL
GROUP BY county
ORDER BY median_home_value DESC;

-- Home value growth since 2020
SELECT
    z1.zip_code,
    z1.zhvi as value_2020,
    z2.zhvi as value_latest,
    ((z2.zhvi - z1.zhvi) / z1.zhvi * 100) as pct_growth
FROM zillow_home_values z1
JOIN zillow_home_values z2 ON z1.zip_code = z2.zip_code
WHERE z1.date = '2020-01-31'
  AND z2.date = (SELECT MAX(date) FROM zillow_home_values)
ORDER BY pct_growth DESC;
```

---

## 2. CDC PLACES - Local Data for Better Health

### Overview
The PLACES program provides health data at the local level. It's the expansion of the 500 Cities project and provides model-based estimates for chronic disease measures.

### Data Source Details
- **Provider**: Centers for Disease Control and Prevention (CDC)
- **Website**: https://www.cdc.gov/places
- **License**: Public domain (U.S. Government data)
- **Update Frequency**: Annual
- **Geographic Level**: ZIP Code Tabulation Area (ZCTA)

### Metrics Available (22 Total)

#### Chronic Health Outcomes (13 measures)
1. **arthritis**: Arthritis
2. **bphigh**: High Blood Pressure
3. **cancer**: Cancer (excluding skin cancer)
4. **casthma**: Current Asthma
5. **chd**: Coronary Heart Disease
6. **copd**: Chronic Obstructive Pulmonary Disease
7. **diabetes**: Diabetes
8. **ghlth**: General Health (Fair or Poor)
9. **highchol**: High Cholesterol
10. **obesity**: Obesity (BMI ≥ 30)
11. **phlth**: Physical Health Not Good
12. **stroke**: Stroke
13. **teethlost**: All Teeth Lost

#### Behavioral Risk Factors (5 measures)
14. **csmoking**: Current Smoking
15. **lpa**: No Leisure-Time Physical Activity
16. **mhlth**: Mental Health Not Good
17. **sleep**: Sleep Less Than 7 Hours

#### Preventive Services (4 measures)
18. **access2**: Lack of Health Insurance
19. **checkup**: Annual Checkup
20. **cholscreen**: Cholesterol Screening
21. **dental**: Dental Visit

### Database Table

#### `cdc_places_wide`
```sql
CREATE TABLE cdc_places_wide (
    zcta VARCHAR,
    location_name VARCHAR,
    year BIGINT,
    access2 DOUBLE,        -- All measures are percentages
    arthritis DOUBLE,
    bphigh DOUBLE,
    -- ... (22 health measures total)
    teethlost DOUBLE
);
```
- **Records**: 1,174 (587 ZCTAs × 2 years)
- **Key**: (zcta, year)
- **Years**: 2022, 2023

### Data Quality

#### Completeness
- **2023 Data**: 100% complete (587 ZCTAs with all measures)
- **2022 Data**: Many null values (incomplete year)
- **Recommended**: Use 2023 data for analysis

#### Methodology
- **Model-Based Estimates**: Not direct measurements
- **BRFSS Data**: Based on Behavioral Risk Factor Surveillance System
- **Small Area Estimation**: Statistical models for local estimates

#### Known Limitations
1. **New Jersey 2022 Issue**: Missing data for 4 measures (blood pressure, cholesterol) due to insufficient BRFSS sample
2. **Time Lag**: 2023 data released in 2024
3. **Estimates vs. Actual**: These are modeled estimates, not direct surveys

### Health Burden Index
The pipeline includes a composite "Health Burden Index" calculated as:
```python
health_burden_index = mean(obesity, diabetes, bphigh, csmoking, depression)
```

Higher values indicate worse health outcomes.

### Use Cases
- Health disparities analysis
- Public health planning
- Social determinants of health research
- Community health assessment
- Grant applications for health programs

### Example Queries

```sql
-- ZCTAs with highest diabetes prevalence
SELECT
    zcta,
    location_name,
    diabetes,
    obesity,
    bphigh
FROM cdc_places_wide
WHERE year = 2023
  AND diabetes IS NOT NULL
ORDER BY diabetes DESC
LIMIT 10;

-- Correlation between obesity and other conditions
SELECT
    CORR(obesity, diabetes) as obesity_diabetes_corr,
    CORR(obesity, bphigh) as obesity_bphigh_corr,
    CORR(obesity, chd) as obesity_chd_corr
FROM cdc_places_wide
WHERE year = 2023;
```

---

## 3. Tree Equity Score

### Overview
Tree Equity Score, developed by American Forests, measures how well the benefits of urban tree canopy are reaching those who need them most.

### Data Source Details
- **Provider**: American Forests
- **Website**: https://www.treeequityscore.org
- **License**: Available for download (check terms on website)
- **Update**: Tree Equity Score 2.0 (2023)
- **Geographic Level**: Census Block Group

### Metrics

#### Primary Metrics
1. **Tree Canopy Coverage (%)**: Percentage of area covered by tree canopy
2. **Tree Equity Score (0-100)**: Composite score indicating tree equity
   - 0-49: Low tree equity (priority areas)
   - 50-74: Moderate tree equity
   - 75-100: High tree equity

3. **Priority Index**: Areas identified for tree planting investment

#### Additional Metrics (varies by data version)
- Population density
- Income levels
- Race/ethnicity demographics
- Urban heat island effects
- Health factors (asthma, heart disease)
- Employment rates

### Database Tables

#### `tree_equity_blockgroups`
```sql
CREATE TABLE tree_equity_blockgroups (
    geoid VARCHAR,              -- 12-digit Census Block Group ID
    county VARCHAR,             -- County name (e.g., "Bergen County")
    treecanopy DOUBLE,          -- Tree canopy coverage (0-1 scale, multiply by 100 for %)
    tc_gap DOUBLE,              -- Tree canopy gap (0-1 scale)
    priority_i DOUBLE,          -- Priority index for tree planting (0-1 scale, higher = more need)
    tes DOUBLE,                 -- Tree Equity Score (0-100)
    cbg_pop DOUBLE,             -- Block group population
    land_area DOUBLE,           -- Land area in square miles
    pctpoc DOUBLE,              -- Percent people of color (0-1 scale)
    pctpov DOUBLE,              -- Percent poverty (0-1 scale)
    temp_diff DOUBLE,           -- Temperature difference from average
    -- Note: Additional demographic/environmental fields may exist
);
```
- **Records**: 6,363 block groups across New Jersey
- **Geographic Level**: Census Block Group
- **Counties**: 21 New Jersey counties
- **Key Metrics**:
  - **treecanopy**: 0.141 to 0.984 (14.1% to 98.4%), mean: 35.6%
  - **priority_i**: 0 to 1, higher values indicate greater need for tree planting
  - **tes**: Tree Equity Score (0-100), lower scores indicate areas needing intervention

#### County-Level Aggregations
For analysis joining with ZCTA-level data (CDC PLACES, Zillow), tree equity data is aggregated at the county level:

```sql
-- Example aggregation query
SELECT
    county,
    COUNT(*) as num_block_groups,
    AVG(treecanopy) * 100 as avg_tree_canopy_pct,
    AVG(tc_gap) as avg_tc_gap,
    AVG(priority_i) as avg_priority_index,
    SUM(cbg_pop) as total_population,
    SUM(land_area) as total_land_area
FROM tree_equity_blockgroups
GROUP BY county;
```

**County-Level Statistics:**
- 21 counties with tree equity data
- Sussex County: Highest tree coverage (60.4%)
- Hudson County: Lowest tree coverage (14.1%)
- Priority Index: Counties with high values (>0.4) need more tree planting investment

### Aggregation Methodology

**Current Implementation:**
Block groups are aggregated to **county level** for joining with ZCTA-level datasets (CDC PLACES, Zillow):

```sql
-- County-level aggregation used in analysis
WITH tree_county AS (
    SELECT
        county,
        AVG(treecanopy) * 100 as avg_tree_canopy_pct,
        AVG(priority_i) as avg_priority_index
    FROM tree_equity_blockgroups
    GROUP BY county
)
SELECT
    c.zcta,
    z.county,
    t.avg_tree_canopy_pct,
    t.avg_priority_index
FROM cdc_places_wide c
INNER JOIN zillow_latest z ON c.zcta = z.zip_code
INNER JOIN tree_county t ON z.county = t.county;
```

**Note:** This approach uses county as the linking field between tree equity data (block group level) and ZCTA-level datasets. All ZCTAs within the same county receive the same aggregated tree equity metrics.

**Future Improvement:**
For more granular analysis, consider:
1. Spatial join using block group centroids and ZCTA boundaries
2. Population-weighted aggregation
3. Using a Census geographic crosswalk file (Block Group → ZCTA)

### Data Quality

#### Accuracy
- **Tree Canopy**: Derived from high-resolution imagery
- **Google Earth Engine**: Processing platform
- **Validation**: Ground-truthed in select areas

#### Limitations
1. **Single Time Point**: No historical trend data
2. **Block Group Aggregation**: Loss of granularity when aggregating to ZCTA
3. **Urban Focus**: Optimized for urban/suburban areas
4. **Data Age**: Check version date (Tree Equity Score 2.0 is from 2023)

### Use Cases
- Environmental justice analysis
- Urban forestry planning
- Grant applications for tree planting
- Climate resilience planning
- Public health interventions (urban heat, air quality)
- Community engagement and advocacy

### Example Queries

```sql
-- Counties with highest and lowest tree canopy coverage
SELECT
    county,
    COUNT(*) as num_block_groups,
    AVG(treecanopy) * 100 as avg_tree_canopy_pct,
    AVG(priority_i) as avg_priority_index,
    SUM(cbg_pop) as total_population
FROM tree_equity_blockgroups
GROUP BY county
ORDER BY avg_tree_canopy_pct DESC;

-- Join tree coverage with health data (county-level aggregation)
WITH tree_county AS (
    SELECT
        county,
        AVG(treecanopy) * 100 as avg_tree_canopy_pct,
        AVG(priority_i) as avg_priority_index
    FROM tree_equity_blockgroups
    GROUP BY county
)
SELECT
    c.zcta,
    z.county,
    t.avg_tree_canopy_pct,
    t.avg_priority_index,
    c.obesity,
    c.diabetes,
    c.bphigh
FROM cdc_places_wide c
INNER JOIN zillow_latest z ON c.zcta = z.zip_code
INNER JOIN tree_county t ON z.county = t.county
WHERE c.year = 2023
ORDER BY t.avg_tree_canopy_pct DESC;

-- Find priority counties (high priority index + high health burden)
WITH tree_county AS (
    SELECT
        county,
        AVG(treecanopy) * 100 as avg_tree_canopy_pct,
        AVG(priority_i) as avg_priority_index
    FROM tree_equity_blockgroups
    GROUP BY county
),
health_by_county AS (
    SELECT
        z.county,
        AVG(c.obesity) as avg_obesity,
        AVG(c.diabetes) as avg_diabetes,
        AVG(c.bphigh) as avg_bphigh,
        AVG(c.csmoking) as avg_smoking
    FROM cdc_places_wide c
    INNER JOIN zillow_latest z ON c.zcta = z.zip_code
    WHERE c.year = 2023
    GROUP BY z.county
)
SELECT
    t.county,
    t.avg_tree_canopy_pct,
    t.avg_priority_index,
    (h.avg_obesity + h.avg_diabetes + h.avg_bphigh + h.avg_smoking) / 4 as health_burden
FROM tree_county t
JOIN health_by_county h ON t.county = h.county
WHERE t.avg_priority_index > 0.35
ORDER BY health_burden DESC;

-- Block group level analysis: Find specific high-priority block groups
SELECT
    geoid,
    county,
    treecanopy * 100 as tree_canopy_pct,
    priority_i,
    tes as tree_equity_score,
    cbg_pop as population
FROM tree_equity_blockgroups
WHERE priority_i > 0.5  -- High priority areas
  AND cbg_pop > 500     -- Sufficient population
ORDER BY priority_i DESC
LIMIT 20;
```

---

## Data Integration Notes

### Geographic Keys
- **Zillow**: Uses ZIP codes (table: `zillow_latest`)
- **CDC PLACES**: Uses ZCTAs (ZIP Code Tabulation Areas)
- **Tree Equity**: Uses Census Block Groups → aggregated to **County** for joining

### Joining Strategy
```sql
-- Three-way join example using county as the linking field
WITH tree_county AS (
    SELECT
        county,
        AVG(treecanopy) * 100 as avg_tree_canopy_pct,
        AVG(priority_i) as avg_priority_index,
        AVG(tes) as avg_tree_equity_score
    FROM tree_equity_blockgroups
    GROUP BY county
)
SELECT
    z.zip_code,
    z.county,
    z.zhvi_latest,
    z.zori_latest,
    c.obesity,
    c.diabetes,
    t.avg_tree_canopy_pct,
    t.avg_priority_index
FROM zillow_latest z
LEFT JOIN cdc_places_wide c ON z.zip_code = c.zcta AND c.year = 2023
LEFT JOIN tree_county t ON z.county = t.county;
```

**Important:** The `zillow_latest` table includes a `county` field that serves as the bridge between ZIP codes and tree equity data.

### Coverage Comparison
| Dataset | NJ Records | Geographic Unit | Notes |
|---------|-----------|-----------------|-------|
| Zillow ZHVI | 552 | ZIP Code | Has county field for joining |
| Zillow ZORI | 230 | ZIP Code (subset) | Not all ZIPs have rent data |
| CDC PLACES | 587 | ZCTA | Links to Zillow via zip_code |
| Tree Equity | 6,363 | Census Block Group | Aggregate to county for joining |
| Tree Equity | 21 | County (aggregated) | Current join level |

### Missing Data Strategy
- Use `LEFT JOIN` to preserve all records
- Check for `NULL` values after joining
- Document which ZCTAs/ZIPs lack specific data
- Consider imputation or exclusion based on analysis needs

---

## 4. Census ACS — Demographics, Economics & Housing

### Overview
The U.S. Census American Community Survey (5-year estimates) is the analytical foundation of the NJ community analysis, providing demographics, income, housing, education, and commuting data for all NJ municipalities and ZCTAs.

### Data Source Details
- **Provider**: U.S. Census Bureau
- **Geographic Level**: ZCTA + Place (municipality)
- **Time Range**: 2012–2023 (12 years)
- **Coverage**: 600 ZCTAs, 705 places
- **Status**: ✅ Integrated

### Key Tables
- `acs_places` — 705 NJ municipalities
- `acs_zctas` — 600 NJ ZCTAs

### Key Variables
63 variables across demographics, income/poverty, housing, education, employment, commuting. Full variable list and SQL examples: see `docs/Census_ACS_Dataset_Summary.md`.

### Join Keys
- `acs_zctas.zcta = cdc_places.zcta`
- `acs_zctas.zcta = zillow.zip_code` (approx)
- Municipality match to NJ DCA via fuzzy name join

---

## 5. Additional Integrated Sources

| Source | Status | Tables | Details |
|--------|--------|--------|---------|
| NJ DCA | ✅ Pulled | `nj_property_tax`, `nj_dca_budgets` | Property tax rates + municipal budgets |
| FEMA NFIP | ✅ Pulled | `fema_flood_summary` | Flood insurance claims + policies |
| HUD CHAS | ✅ Pulled | `hud_chas_places` | Housing affordability by income tier |
| BLS LAUS | ⬜ Not pulled | `bls_county_unemployment` | County-level unemployment time series |
| FBI Crime | ⬜ Not pulled | `fbi_crime_rates` | Violent + property crime by agency |

---

## Future Data Source Candidates

### Environmental Data
- **EPA Air Quality**: AQI by county/monitor
- **USGS Water Quality**: Stream and groundwater data
- **NOAA Climate**: Temperature, precipitation trends

### Other
- **IRS**: Income statistics by ZIP code
- **Transit Access**: Distance to public transportation
- **Food Access**: USDA Food Desert data
- **DOT**: Traffic accident data

---

## Data Update Procedures

### Zillow
1. Check for new monthly releases
2. Download updated ZIP code files
3. Run `scripts/ingest_zillow.py`
4. Verify record counts

### CDC PLACES
1. Annual release (typically fall)
2. Download from CDC data portal
3. Run `scripts/ingest_cdc_places.py`
4. Check for new measures or methodology changes

### Tree Equity Score
1. Monitor American Forests for updates
2. Download when new version is released
3. Run `scripts/ingest_tree_equity.py`
4. Compare with previous version if applicable

---

## Related Documentation
- [[01_Pipeline_Overview]] - Project overview and architecture
- [[03_Analysis_Guides]] - How to perform specific analyses
- [[04_API_Reference]] - Database schema and query examples

**Last Updated**: 2026-03-05
**Tree Equity Schema Updated**: 2026-03-05 (corrected column names and aggregation methodology)
