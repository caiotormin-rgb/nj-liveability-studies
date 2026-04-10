# CDC PLACES Dataset Summary

**Last Updated**: 2026-03-05
**Data Source**: CDC PLACES (Population Level Analysis and Community Estimates)
**API**: Socrata Open Data - No key required
**Geographic Level**: ZCTA (ZIP Code Tabulation Area)

---

## Overview

The CDC PLACES dataset provides small-area estimates for chronic disease risk factors, health outcomes, and clinical preventive service use for all ZIP codes in the United States. This pipeline extracts data specifically for New Jersey ZCTAs.

---

## Database Tables

### Two Storage Formats

| Table | Format | Rows | Use Case |
|-------|--------|------|----------|
| **`cdc_places_zcta`** | Long | ~26,000+ | Filtering by measure, time-series analysis, metadata |
| **`cdc_places_wide`** | Wide | 1,174 | Cross-measure correlation, mapping, quick analysis |

### Table: `cdc_places_zcta` (Long Format)

**Structure**: One row per ZCTA × Year × Measure combination

**Columns**:
- `zcta` (VARCHAR) - 5-digit ZIP Code Tabulation Area
- `location_name` (VARCHAR) - ZCTA name (usually same as ZCTA)
- `state_abbr` (VARCHAR) - State abbreviation (NJ)
- `year` (BIGINT) - Data year (2022, 2023)
- `category` (VARCHAR) - Health measure category
- `measure_id` (VARCHAR) - Measure code (e.g., DIABETES, OBESITY)
- `measure_label` (VARCHAR) - Human-readable measure name
- `value` (DOUBLE) - Prevalence percentage
- `value_type` (VARCHAR) - "Age-adjusted prevalence" or "Crude prevalence"
- `ci_low` (DOUBLE) - Lower 95% confidence interval
- `ci_high` (DOUBLE) - Upper 95% confidence interval
- `total_pop` (DOUBLE) - Total population for the ZCTA

**Example Query**:
```sql
SELECT zcta, year, measure_id, value, ci_low, ci_high
FROM cdc_places_zcta
WHERE measure_id = 'DIABETES'
  AND year = 2023
ORDER BY value DESC
LIMIT 10;
```

---

### Table: `cdc_places_wide` (Wide Format)

**Structure**: One row per ZCTA × Year, with each health measure as a column

**Columns**:
- `zcta` (VARCHAR) - 5-digit ZIP Code Tabulation Area
- `location_name` (VARCHAR) - ZCTA name
- `year` (BIGINT) - Data year (2022, 2023)
- Plus **22 health measure columns** (all DOUBLE type):
  - `access2`, `arthritis`, `bphigh`, `cancer`, `casthma`, `chd`, `checkup`, `cholscreen`, `copd`, `csmoking`, `dental`, `depression`, `diabetes`, `ghlth`, `highchol`, `lpa`, `mhlth`, `obesity`, `phlth`, `sleep`, `stroke`, `teethlost`

**Data Processing**:
- Contains **age-adjusted prevalence only** (standardized for population comparison)
- Values aggregated using `mean()` if multiple value types exist
- All measure columns are lowercase

**Example Query**:
```sql
SELECT zcta, obesity, diabetes, bphigh, csmoking
FROM cdc_places_wide
WHERE year = 2023
  AND obesity > 35.0
ORDER BY obesity DESC;
```

---

## Data Coverage

| Metric | Value |
|--------|-------|
| **Total Records** | 1,174 rows (wide format) |
| **Unique ZCTAs** | 587 (all NJ ZCTAs with available data) |
| **Years Available** | 2022, 2023 |
| **Complete Data Year** | 2023 only (2022 is ~50% null) |
| **Health Measures** | 22 measures across 4 categories |
| **Geographic Scope** | New Jersey only (ZCTAs starting with 07 or 08) |

---

## Health Measures (22 Total)

Configured in `config.py:167-191`. All measures represent **prevalence percentages** unless otherwise noted.

### Chronic Diseases (11 measures)

| Measure ID | Column Name | Description | Median % (2023) |
|------------|-------------|-------------|-----------------|
| `ARTHRITIS` | `arthritis` | Arthritis among adults ≥18 | 19.5% |
| `BPHIGH` | `bphigh` | High blood pressure among adults ≥18 | **32.3%** |
| `CANCER` | `cancer` | Cancer (excluding skin) among adults ≥18 | 6.0% |
| `CASTHMA` | `casthma` | Current asthma among adults ≥18 | 9.1% |
| `CHD` | `chd` | Coronary heart disease among adults ≥18 | 5.5% |
| `COPD` | `copd` | COPD among adults ≥18 | 5.6% |
| `DIABETES` | `diabetes` | Diabetes among adults ≥18 | 9.8% |
| `HIGHCHOL` | `highchol` | High cholesterol among adults ≥18 | 36.5% |
| `KIDNEY` | `kidney` | Chronic kidney disease among adults ≥18 | *(Not in wide table - check config)* |
| `OBESITY` | `obesity` | Obesity among adults ≥18 (BMI ≥30) | **28.2%** |
| `STROKE` | `stroke` | Stroke among adults ≥18 | 2.6% |

### Health Behaviors (4 measures)

| Measure ID | Column Name | Description | Median % (2023) |
|------------|-------------|-------------|-----------------|
| `CSMOKING` | `csmoking` | Current smoking among adults ≥18 | 10.3% |
| `LPA` | `lpa` | No leisure-time physical activity | 23.0% |
| `SLEEP` | `sleep` | Sleeping <7 hours among adults ≥18 | 38.5% |
| `TEETHLOST` | `teethlost` | All teeth lost among adults ≥65 | 9.0% |

### Mental Health (4 measures)

| Measure ID | Column Name | Description | Median % (2023) |
|------------|-------------|-------------|-----------------|
| `DEPRESSION` | `depression` | Depression among adults ≥18 | 15.8% |
| `GHLTH` | `ghlth` | Fair or poor self-rated health | 18.0% |
| `MHLTH` | `mhlth` | Mental health not good ≥14 days/month | 14.5% |
| `PHLTH` | `phlth` | Physical health not good ≥14 days/month | 11.8% |

### Healthcare Access (3 measures)

| Measure ID | Column Name | Description | Median % (2023) |
|------------|-------------|-------------|-----------------|
| `ACCESS2` | `access2` | No health insurance among adults 18-64 | 13.2% |
| `CHECKUP` | `checkup` | Annual checkup in past year | 77.2% |
| `CHOLSCREEN` | `cholscreen` | Cholesterol screening in past 5 years | 83.5% |
| `DENTAL` | `dental` | Dental visit in past year | 69.0% |

---

## Key Differences: Long vs. Wide Format

| Aspect | Long (`cdc_places_zcta`) | Wide (`cdc_places_wide`) |
|--------|---------------------------|--------------------------|
| **Rows** | ~26,000+ (587 ZCTAs × 2 years × 22 measures) | 1,174 (587 ZCTAs × 2 years) |
| **Measure Storage** | Single `measure_id` column with `value` | Each measure is its own column |
| **Metadata** | Includes CI, value_type, category, population | Only prevalence values |
| **Value Types** | Both age-adjusted & crude prevalence | Age-adjusted prevalence only |
| **Analysis Use** | Time-series, filtering by measure | Correlation analysis, geographic mapping |
| **Query Complexity** | Requires filtering on `measure_id` | Direct column access |

**When to use Long format**:
- Filtering/analyzing specific measures
- Time-series analysis over multiple years
- Need confidence intervals or metadata
- Joining with other long-format datasets

**When to use Wide format**:
- Cross-measure correlation analysis
- Geographic heat mapping
- Quick EDA and summary statistics
- Calculating composite health indices

---

## Data Quality Notes

### Year Coverage
- **2022 Data**: ~50% null values across all measures (appears incomplete/placeholder)
- **2023 Data**: Complete coverage for all 587 ZCTAs
- **Recommendation**: Use 2023 data only for analysis

### Age Adjustment
- Wide table uses **age-adjusted prevalence** only
- Age adjustment standardizes rates to a common population structure
- Allows fair comparison between ZCTAs with different age distributions
- Critical for chronic disease measures that increase with age

### Missing Measures
- `KIDNEY` is configured in `config.py` but not present in the wide table (check if API removed it)
- Some 2022 measures have partial data (e.g., `sleep`, `teethlost`)

### Geographic Limitations
- **Only ZCTA-level data** - no county, city, or census tract breakdowns
- Must manually aggregate to county level using ZCTA-to-county crosswalks
- Some small ZCTAs may have suppressed data due to small sample sizes

---

## Geographic Insights (2023 Data)

### Healthiest ZCTAs (Lowest Composite Health Burden)

| Rank | ZCTA | Location Area | Health Burden Index |
|------|------|---------------|---------------------|
| 1 | 08544 | Princeton area | 8.2 |
| 2 | 08240 | Avalon/Stone Harbor | 9.5 |
| 3 | 07311 | Jersey City | 10.1 |
| 4 | 08641 | Pennington | 10.8 |
| 5 | 07310 | Jersey City | 11.2 |

### Highest Health Burden ZCTAs

| Rank | ZCTA | Location Area | Health Burden Index |
|------|------|---------------|---------------------|
| 1 | 07114 | Newark | 30.0 |
| 2 | 08320 | Atlantic City area | 28.9 |
| 3 | 08103 | Camden | 28.5 |
| 4 | 08302 | Bridgeton | 27.8 |
| 5 | 08327 | Millville area | 27.2 |

**Health Burden Index**: Average of obesity, diabetes, high blood pressure, smoking, and depression prevalence.

---

## Measure Prevalence Statistics (2023)

| Measure | Mean % | Median % | Min % | Max % | Range |
|---------|--------|----------|-------|-------|-------|
| High Blood Pressure | 32.6 | 32.3 | 6.4 | 49.4 | 43.0 |
| Obesity | 28.5 | 28.2 | 12.1 | 45.4 | 33.3 |
| Physical Inactivity | 23.0 | 22.0 | 11.5 | 47.4 | 35.9 |
| Depression | 15.9 | 15.8 | 9.1 | 24.0 | 14.9 |
| Mental Health Issues | 14.8 | 14.5 | 8.0 | 25.3 | 17.3 |
| Diabetes | 10.2 | 9.8 | 0.9 | 20.0 | 19.1 |
| Current Smoking | 10.8 | 10.3 | 3.3 | 29.8 | 26.5 |
| Coronary Heart Disease | 5.6 | 5.5 | 0.5 | 12.1 | 11.6 |
| Stroke | 3.0 | 2.6 | 0.6 | 9.3 | 8.7 |

**Key Findings**:
- **High variability** in diabetes (19.1% range) and smoking (26.5% range)
- **Highest median prevalence**: High blood pressure (32.3%), obesity (28.2%)
- **Lowest median prevalence**: Stroke (2.6%), CHD (5.5%)

---

## Correlation Analysis

### Strongest Positive Correlations (r > 0.85)

| Measure 1 | Measure 2 | Correlation | Interpretation |
|-----------|-----------|-------------|----------------|
| Diabetes | Physical Inactivity | 0.89 | Strong behavioral link |
| High BP | Coronary Heart Disease | 0.89 | Direct cardiovascular pathway |
| Obesity | Current Smoking | 0.87 | Overlapping risk factors |
| Smoking | Physical Inactivity | 0.86 | Clustered unhealthy behaviors |
| Smoking | Mental Health Issues | 0.86 | Stress/coping mechanism |

### Key Insights
- **Chronic diseases cluster together** (metabolic syndrome pattern)
- **Behavioral measures are highly correlated** (smoking + inactivity)
- **Mental health linked to physical health** behaviors
- **Opportunity for multi-factor interventions** targeting correlated conditions

---

## Use Cases & Analysis Examples

### 1. Identify High-Risk Communities
```sql
-- ZCTAs with obesity >35% AND diabetes >15%
SELECT zcta, location_name, obesity, diabetes, bphigh
FROM cdc_places_wide
WHERE year = 2023
  AND obesity > 35.0
  AND diabetes > 15.0
ORDER BY obesity DESC;
```

### 2. Healthcare Access Gaps
```sql
-- Areas with low insurance and poor preventive care
SELECT zcta, access2, checkup, dental
FROM cdc_places_wide
WHERE year = 2023
  AND access2 > 20.0  -- >20% uninsured
  AND checkup < 70.0  -- <70% annual checkup
ORDER BY access2 DESC;
```

### 3. Mental Health Hot Spots
```sql
-- ZCTAs with high depression and mental health burden
SELECT zcta, depression, mhlth, ghlth
FROM cdc_places_wide
WHERE year = 2023
  AND depression > 18.0
  AND mhlth > 17.0
ORDER BY depression DESC;
```

### 4. Create Composite Health Index
```python
# In pandas after loading wide format
df['metabolic_index'] = df[['obesity', 'diabetes', 'bphigh']].mean(axis=1)
df['behavioral_index'] = df[['csmoking', 'lpa', 'sleep']].mean(axis=1)
df['overall_burden'] = df[['obesity', 'diabetes', 'bphigh',
                            'csmoking', 'depression']].mean(axis=1)
```

### 5. Year-over-Year Trends (when more years available)
```sql
-- Compare 2022 vs 2023 diabetes prevalence
SELECT
    a.zcta,
    a.value as diabetes_2022,
    b.value as diabetes_2023,
    (b.value - a.value) as change
FROM cdc_places_zcta a
JOIN cdc_places_zcta b
  ON a.zcta = b.zcta
  AND a.measure_id = b.measure_id
WHERE a.measure_id = 'DIABETES'
  AND a.year = 2022
  AND b.year = 2023
ORDER BY change DESC;
```

---

## Pipeline Implementation Details

### Source File
- **Pipeline Class**: `CDCPlacesPipeline` in `pipeline/cdc_places.py:30`
- **Base Endpoint**: `https://data.cdc.gov/resource/qnzd-25i4.json`
- **API Method**: Socrata REST API with pagination
- **Batch Size**: 50,000 rows per request
- **Rate Limiting**: 0.3s sleep between requests

### Extract Process
1. Filters to NJ ZCTAs (locationid LIKE '07%' OR '08%')
2. Filters to configured measures only (22 measures)
3. Paginates through full dataset
4. Caches raw data as `cdc_places_nj_raw.parquet`

### Transform Process
1. **Rename columns** to snake_case
2. **Filter to NJ** ZCTAs (07xxx, 08xxx)
3. **Cast types** (numeric values, year as Int64)
4. **Create long table** (`cdc_places_zcta`)
   - Keep all value types (age-adjusted, crude)
   - Include confidence intervals
   - Deduplicate on (zcta, year, measure_id, value_type)
5. **Create wide table** (`cdc_places_wide`)
   - Filter to age-adjusted prevalence only
   - Pivot on measure_id
   - Aggregate using mean() if duplicates
   - Lowercase all column names

### Load Process
- Direct insertion into DuckDB tables
- Tables auto-created if not exist
- Overwrites existing data (no incremental append)

---

## Integration with Other Datasets

### Join with Census ACS Data
```sql
-- Correlate health outcomes with socioeconomic factors
SELECT
    c.zcta,
    c.obesity,
    c.diabetes,
    a.income_median_hh,
    a.poverty_rate,
    a.edu_bachelors_pct
FROM cdc_places_wide c
JOIN census_acs a
  ON c.zcta = a.zcta
  AND c.year = a.year
WHERE c.year = 2023;
```

### Join with Zillow Housing Data
```sql
-- Health outcomes vs. housing affordability
SELECT
    h.zcta,
    h.obesity,
    h.depression,
    z.zhvi_median,
    z.zori_median
FROM cdc_places_wide h
JOIN zillow_wide z
  ON h.zcta = z.zcta
WHERE h.year = 2023;
```

### Join with HUD CHAS Data
```sql
-- Health burden vs. housing cost burden
SELECT
    c.zcta,
    c.obesity,
    c.diabetes,
    u.cost_burden_30_50_pct,
    u.cost_burden_50plus_pct
FROM cdc_places_wide c
JOIN hud_chas u
  ON c.zcta = u.zcta
WHERE c.year = 2023;
```

---

## Limitations & Considerations

### Methodological
- **Model-based estimates**: PLACES uses small area estimation, not direct surveys
- **Based on BRFSS**: Behavioral Risk Factor Surveillance System (phone survey)
- **Age-adjustment**: Standardizes to 2000 US population - may not reflect actual counts
- **Self-reported data**: Subject to recall bias and social desirability bias

### Geographic
- **ZCTA boundaries** don't align perfectly with ZIP codes
- **No sub-ZCTA granularity** (can't drill down to neighborhoods)
- **Rural areas** may have wider confidence intervals due to smaller samples
- **Must aggregate manually** for county-level analysis

### Temporal
- **Limited years**: Only 2022-2023 available currently
- **Lag time**: 2023 data likely reflects 2021-2022 survey period
- **No monthly/quarterly** breakdowns - annual only

### Analysis
- **No individual-level data** - cannot analyze intersectionality
- **Prevalence only** - no incidence or survival data
- **Cross-sectional** - cannot establish causality from correlations
- **No adjustment for multiple comparisons** when doing exploratory analysis

---

## Recommendations for Analysis

### For Public Health Analysis
1. **Focus on 2023 data only** (2022 is incomplete)
2. **Use age-adjusted prevalence** from wide table for fair comparison
3. **Create composite indices** rather than focusing on single measures
4. **Map geographic disparities** to identify intervention areas
5. **Cross-reference with social determinants** (Census, HUD data)

### For Predictive Modeling
1. **Join with socioeconomic factors** (income, education, housing)
2. **Include spatial features** (distance to healthcare, transit access)
3. **Consider clustering algorithms** to identify health profiles
4. **Use confidence intervals** to weight model inputs appropriately

### For Monitoring & Reporting
1. **Track "hot spot" ZCTAs** with high burden over time
2. **Monitor healthcare access gaps** (insurance, checkups, dental)
3. **Calculate equity metrics** (e.g., ratio of highest/lowest burden areas)
4. **Create dashboards** showing top/bottom performing ZCTAs

---

## References & Resources

- **CDC PLACES Homepage**: https://www.cdc.gov/places/
- **Socrata API Documentation**: https://dev.socrata.com/
- **BRFSS Methodology**: https://www.cdc.gov/brfss/
- **ZCTA Documentation**: https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html

---

## Change Log

| Date | Change | Notes |
|------|--------|-------|
| 2026-03-05 | Initial documentation | Based on EDA of 2022-2023 data |

---

**Maintained by**: NJ Pipeline Project
**Contact**: See project README for maintainer information
