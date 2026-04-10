
------
---
title: "Zillow Data Analysis"
output: html_notebook
runtime: shiny


## Tables

### 1. **zillow_home_values** (Time Series)
- **Records**: 683,279 rows
- **Time Range**: 2000-01-31 to 2026-01-31 (313 months, ~26 years)
- **Geographic Coverage**: 551 unique NJ ZIP codes
- **Granularity**: Monthly time series data

**Columns**:
- `zip_code` (VARCHAR) - NJ ZIP code identifier
- `city` (VARCHAR) - City name
- `county` (VARCHAR) - County name (21 NJ counties)
- `date` (DATE) - Month-end date
- `zhvi_usd` (DOUBLE) - Zillow Home Value Index in USD
- `State` (VARCHAR) - State identifier
- `StateName` (VARCHAR) - State name

**Statistics**:
- Median home value (Jan 2026): $657,744
- Range: $164,962 (Camden) to $8,169,608 (Deal)
- Growth: 223.2% from 2000 to 2026
- Median YoY growth: 9.4%
- Median 5-year growth: 58.0%

---

### 2. **zillow_rent** (Time Series)
- **Records**: 30,590 rows
- **Time Range**: 2015-01-31 to 2026-01-31 (133 months, ~11 years)
- **Geographic Coverage**: 230 unique NJ ZIP codes
- **Granularity**: Monthly time series data

**Columns**:
- `zip_code` (VARCHAR) - NJ ZIP code identifier
- `city` (VARCHAR) - City name
- `county` (VARCHAR) - County name
- `date` (DATE) - Month-end date
- `zori_usd` (DOUBLE) - Zillow Observed Rent Index in USD

**Statistics**:
- Median monthly rent (Jan 2026): $2,496
- Range: ~$1,500 to $26,250
- Growth: 57.2% from 2015 to 2026
- Overlap: 229 ZIP codes have both ZHVI and ZORI data

---

## Key Metrics

**Price-to-Rent Ratios**:
- Median ratio: 22.5 (favors renting)
- 19 ZIPs favor buying (ratio < 15)
- 142 ZIPs favor renting (ratio > 21)

**County Rankings** (by median home value):
1. Monmouth County: $1,179,303
2. Cape May County: $1,134,554
3. Bergen County: $977,946
...
21. Cumberland County: $332,133

**Data Quality**: Complete time series with no gaps, consistent monthly observations across all ZIP codes in scope.