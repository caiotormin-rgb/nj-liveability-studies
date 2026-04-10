# NJ Pipeline - Project Overview

## Purpose
The NJ Pipeline is a comprehensive data analytics pipeline that integrates multiple public datasets to analyze the relationships between environmental factors, public health outcomes, and socioeconomic indicators across New Jersey ZIP Code Tabulation Areas (ZCTAs).

## Key Objectives
1. **Environmental Health Analysis**: Understand how tree canopy coverage correlates with public health outcomes
2. **Socioeconomic Insights**: Explore relationships between housing values, environmental quality, and health
3. **Geographic Equity**: Identify areas with environmental and health disparities
4. **Data-Driven Decision Making**: Provide insights for urban planning, public health interventions, and community development

## Data Sources

### 1. Zillow Home Value Index (ZHVI) & Rent Index (ZORI)
- **Source**: Zillow Research Data
- **Coverage**: All NJ ZIP codes
- **Metrics**:
  - ZHVI: Median home values (monthly time series, 2000-2026)
  - ZORI: Median rental prices (monthly time series, 2015-2026)
- **Geographic Level**: ZIP code
- **Update Frequency**: Monthly
- **Status**: ✅ Integrated

### 2. CDC PLACES - Health Data
- **Source**: Centers for Disease Control and Prevention
- **Coverage**: 587 NJ ZCTAs
- **Metrics**: 22 health measures including:
  - Chronic conditions (obesity, diabetes, heart disease)
  - Behavioral risk factors (smoking, physical inactivity)
  - Preventive services (checkups, dental visits)
  - Mental health indicators
- **Geographic Level**: ZCTA (ZIP Code Tabulation Area)
- **Years Available**: 2022-2023
- **Status**: ✅ Integrated

### 3. Tree Equity Score
- **Source**: American Forests
- **Coverage**: Census block groups (aggregated to ZCTA)
- **Metrics**:
  - Tree canopy coverage percentage
  - Tree equity score (0-100)
  - Priority index for tree planting
  - Urban heat metrics
  - Demographics and socioeconomic factors
- **Geographic Level**: Block group → ZCTA
- **Status**: 🔄 Integration scripts ready, awaiting data download

## Technical Architecture

### Database
- **Engine**: DuckDB
- **Location**: `data/db/nj_pipeline.duckdb`
- **Advantages**:
  - Embedded (no server required)
  - OLAP optimized for analytics
  - SQL interface
  - Fast aggregations and joins

### Data Tables

#### Core Tables
1. **zillow_home_values**
   - Time series of home values by ZIP code
   - ~683K records (552 ZIPs × ~313 months)

2. **zillow_rent_index**
   - Time series of rental prices by ZIP code
   - ~152K records (230 ZIPs × ~133 months)

3. **zillow_zipcode_latest**
   - Latest snapshot of home values and rents
   - 552 ZIP codes

4. **cdc_places_wide**
   - Health measures by ZCTA and year
   - 1,174 records (587 ZCTAs × 2 years)

5. **tree_equity_blockgroups** (pending)
   - Block group level tree equity data
   - Detailed geographic granularity

6. **tree_equity_zcta** (pending)
   - ZCTA-level aggregated tree equity metrics
   - For easy joining with health and housing data

## Directory Structure

```
nj_pipeline/
├── data/
│   ├── raw/                    # Original downloaded data
│   │   ├── zillow/            # Zillow CSV files
│   │   ├── cdc_places/        # CDC PLACES CSVs
│   │   └── tree_equity/       # Tree Equity Score data
│   ├── processed/             # Cleaned/transformed data
│   │   ├── zillow/
│   │   ├── cdc_places/
│   │   └── tree_equity/
│   └── db/                    # DuckDB database
│       └── nj_pipeline.duckdb
│
├── scripts/                   # Data ingestion scripts
│   ├── ingest_zillow.py
│   ├── ingest_cdc_places.py
│   └── ingest_tree_equity.py
│
├── notebooks/                 # Analysis notebooks
│   ├── eda_zillow.ipynb
│   ├── eda_cdc_places.ipynb
│   └── eda_tree_equity.ipynb
│
└── docs/
    └── vault/                # Documentation (you are here)
```

## Key Analyses

### 1. Environmental Health Correlations
- **Question**: Does tree canopy coverage correlate with better health outcomes?
- **Approach**: Join tree equity data with CDC PLACES health metrics
- **Expected Findings**: Areas with higher tree coverage may show:
  - Lower obesity rates
  - Reduced chronic disease prevalence
  - Better mental health indicators

### 2. Socioeconomic Patterns
- **Question**: How do housing values relate to environmental quality and health?
- **Approach**: Three-way analysis of home values, tree coverage, and health outcomes
- **Expected Findings**:
  - Wealthier areas (higher home values) likely have more tree coverage
  - Environmental inequality patterns
  - Health disparities by ZIP code wealth

### 3. Priority Area Identification
- **Question**: Which communities need the most intervention?
- **Approach**: Create composite indices combining:
  - Low tree equity scores
  - High health burden
  - Lower socioeconomic indicators
- **Output**: Ranked list of ZCTAs for targeted interventions

### 4. Temporal Trends
- **Question**: How have housing markets changed over time?
- **Approach**: Time series analysis of ZHVI and ZORI (2000-2026)
- **Insights**:
  - Gentrification patterns
  - Market recovery after 2008 financial crisis
  - COVID-19 housing market impacts
  - Rent vs. home price growth rates

## Data Quality Notes

### Coverage
- **Zillow**: 552 ZIP codes with home values, 230 with rent data
- **CDC PLACES**: 587 ZCTAs (note: only 2023 data is complete)
- **Tree Equity**: TBD after download

### Limitations
1. **Geographic Mismatch**:
   - Zillow uses ZIP codes
   - CDC uses ZCTAs (similar but not identical)
   - Tree Equity uses block groups
   - Join strategy: Direct match on ZIP/ZCTA codes

2. **Temporal Gaps**:
   - CDC data: Only 2022-2023 available
   - Tree Equity: Single time point (no historical)
   - Zillow: Full time series back to 2000

3. **Missing Data**:
   - 2022 CDC data: Many null values
   - Not all ZIP codes have rent data
   - Tree coverage: Awaiting download

## Use Cases

### Public Health Planning
- Identify areas with combined environmental and health deficits
- Target tree planting programs in high-need communities
- Design health interventions based on environmental factors

### Urban Planning
- Inform green space development priorities
- Support zoning decisions
- Guide infrastructure investment

### Community Advocacy
- Demonstrate environmental inequality
- Support grant applications for tree planting
- Provide data for environmental justice initiatives

### Academic Research
- Multi-factor health determinants
- Environmental sociology
- Urban ecology
- Health geography

## Next Steps

1. **Download Tree Equity Score Data**
   - Visit: https://www.treeequityscore.org/methodology
   - Download NJ data
   - Run `scripts/ingest_tree_equity.py`

2. **Run Complete Analysis**
   - Execute all three EDA notebooks
   - Generate correlation matrices
   - Create visualizations

3. **Advanced Analytics**
   - Machine learning models for health prediction
   - Clustering analysis to identify community types
   - Geospatial visualizations with mapping

4. **Expand Data Sources**
   - Air quality data (EPA)
   - Crime statistics
   - School performance metrics
   - Transportation access

## Related Documentation
- [[02_Data_Sources]] - Detailed information on each dataset
- [[03_Analysis_Guides]] - How to run specific analyses
- [[04_API_Reference]] - Database schema and query examples
- [[05_Troubleshooting]] - Common issues and solutions

## Contact & Contribution
This is a living project. Data sources, analyses, and documentation will be updated as the project evolves.

**Last Updated**: 2026-03-05
**Version**: 1.0
**Status**: Active Development
