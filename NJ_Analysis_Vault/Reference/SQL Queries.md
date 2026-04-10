---
tags: [reference, sql]
---

# SQL Query Reference

Useful DuckDB queries to copy-paste into a Python session or DataSpell SQL console.

```python
import duckdb
from config import DB_PATH
conn = duckdb.connect(DB_PATH)
```

---

## 📋 Inventory

### List all tables and row counts
```sql
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'main'
ORDER BY table_type, table_name;
```

---

## 🏠 Zillow

### Most recent home value + rent per ZIP
```sql
SELECT * FROM zillow_latest ORDER BY zhvi_current DESC;
```

### Home value time series for specific ZIPs
```sql
SELECT zip_code, date, zhvi_usd
FROM zillow_home_values
WHERE series = 'zhvi_all_homes'
  AND zip_code IN ('07030', '07102', '07043')
ORDER BY zip_code, date;
```

### Price-to-rent ratio distribution
```sql
SELECT
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY price_to_rent_ratio) AS p25,
    MEDIAN(price_to_rent_ratio) AS p50,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY price_to_rent_ratio) AS p75
FROM zillow_latest
WHERE price_to_rent_ratio BETWEEN 5 AND 60;
```

### County-level median home value
```sql
SELECT county,
       MEDIAN(zhvi_current)  AS median_home_value,
       MEDIAN(zori_current)  AS median_rent,
       MEDIAN(price_to_rent_ratio) AS median_ptr,
       COUNT(*) AS zip_count
FROM zillow_latest
WHERE county IS NOT NULL
GROUP BY county
ORDER BY median_home_value DESC;
```

---

## 👥 Census ACS

### Latest year municipalities, sorted by income
```sql
SELECT NAME, pop_total, income_median_hh, poverty_rate,
       pct_bachelors_plus, homeownership_rate, home_value_median
FROM acs_places
WHERE acs_year = (SELECT MAX(acs_year) FROM acs_places)
  AND pop_total > 1000
ORDER BY income_median_hh DESC;
```

### Income time series for a specific municipality
```sql
SELECT acs_year, income_median_hh, home_value_median, poverty_rate
FROM acs_places
WHERE NAME LIKE '%Princeton%'
ORDER BY acs_year;
```

### Rent burden hot spots
```sql
SELECT NAME, gross_rent_median, rent_burden_30plus_pct, rent_burden_severe_pct
FROM acs_places
WHERE acs_year = (SELECT MAX(acs_year) FROM acs_places)
ORDER BY rent_burden_severe_pct DESC
LIMIT 20;
```

---

## 💸 Affordability

### Full affordability index
```sql
SELECT * FROM v_affordability_index
ORDER BY home_price_to_income_ratio;
```

### Most affordable ZIPs with strong appreciation
```sql
SELECT zip_code, city, home_value_zillow, income_median_hh,
       home_price_to_income_ratio, home_value_yoy_pct, home_value_5yr_pct
FROM v_affordability_index
WHERE home_price_to_income_ratio < 5     -- affordable
  AND home_value_yoy_pct > 5             -- appreciating
ORDER BY home_value_yoy_pct DESC;
```

---

## 🌊 Flood Risk

### Top flood-risk ZIPs
```sql
SELECT * FROM fema_flood_summary
ORDER BY pct_high_risk_flood_zone DESC NULLS LAST
LIMIT 20;
```

### Join flood risk to home values
```sql
SELECT z.zip_code, z.city, z.zhvi_current, f.pct_high_risk_flood_zone,
       f.total_claims_all_time_usd
FROM zillow_latest z
JOIN fema_flood_summary f USING (zip_code)
ORDER BY f.pct_high_risk_flood_zone DESC;
```

---

## 🏥 Health

### Worst health outcomes by ZCTA
```sql
SELECT zcta, location_name, diabetes, obesity, csmoking, lpa, depression
FROM cdc_places_wide
WHERE year = (SELECT MAX(year) FROM cdc_places_wide)
ORDER BY diabetes DESC
LIMIT 20;
```

---

## 🏛️ Property Tax

### Highest and lowest tax rate municipalities
```sql
SELECT municipality, county, general_tax_rate, avg_tax_bill_residential,
       avg_assessed_value_residential, year
FROM nj_property_tax
WHERE year = (SELECT MAX(year) FROM nj_property_tax)
ORDER BY general_tax_rate DESC;
```

---

## 🔗 Cross-Source Scorecard

### Full ZIP-level scorecard
```sql
SELECT * FROM v_zipcode_scorecard;
```

### Build your own composite (example)
```sql
SELECT zip_code, city,
       income_median_hh,
       home_price_to_income_ratio,
       poverty_rate,
       avg_tree_canopy_pct,
       pct_high_risk_flood_zone,
       diabetes_pct,
       property_tax_rate
FROM v_zipcode_scorecard
WHERE pop_total > 5000
ORDER BY income_median_hh DESC;
```
