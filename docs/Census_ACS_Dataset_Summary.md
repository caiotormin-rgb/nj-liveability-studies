# Census ACS Dataset Summary

## Overview
The Census ACS (American Community Survey) dataset is the **foundation** of your NJ community analysis, providing comprehensive demographics, economics, housing, and social metrics for New Jersey communities.

---

## Coverage

### Geographic Areas
- **600 unique ZIP Code Tabulation Areas (ZCTAs)**
- **705 unique places** (municipalities/cities/towns)
- **1,305 total unique geographic units**

### Time Series
- **12 years of data**: 2012–2023
- **14,311 total records** (geography × year combinations)
- Average: ~11 years per geography

### Latest Year (2023) Data Quality
- **1,298 total records** in 2023
- **95%+ coverage** for most key metrics:
  - Income: 1,230 records (94.8%)
  - Home values: 1,240 records (95.5%)
  - Poverty: 1,284 records (98.9%)
  - Education: 1,290 records (99.4%)
  - Unemployment: 1,285 records (99.0%)
  - Diversity: 1,298 records (100%)

---

## Data Categories & Variables (63 total columns)

### 1. **Geography & Identifiers** (6 columns)
- `geoid` – Unique geographic identifier
- `NAME` – Human-readable place name
- `geo_type` – "zcta" or "place"
- `state_fips` – State FIPS code (34 for NJ)
- `place_fips` – Place FIPS code (for municipalities)
- `zcta` – ZIP Code Tabulation Area code

### 2. **Demographics** (7 columns)
- `pop_total` – Total population
- `age_median` – Median age
- `race_white` – White population count
- `race_black` – Black/African American population count
- `race_asian` – Asian population count
- `race_hispanic` – Hispanic/Latino population count
- `diversity_index` – **Calculated metric**: Probability two random people are different races (0-1)

### 3. **Income & Poverty** (7 columns)
**Raw counts:**
- `income_median_hh` – Median household income ($)
- `income_per_capita` – Per capita income ($)
- `poverty_count` – Number of people below poverty line
- `poverty_universe` – Total population for poverty calculation
- `gini_index` – Income inequality measure (0-1, higher = more unequal)

**Calculated rates:**
- `poverty_rate` – % of population below poverty line

### 4. **Housing** (16 columns)
**Units & tenure:**
- `housing_units_total` – Total housing units
- `housing_occupied` – Occupied units
- `housing_vacant` – Vacant units
- `housing_owner_occ` – Owner-occupied units
- `housing_renter_occ` – Renter-occupied units
- `households` – Total households
- `avg_household_size` – Average people per household

**Values & costs:**
- `home_value_median` – Median home value ($)
- `gross_rent_median` – Median gross rent ($)

**Rent burden (raw counts):**
- `rent_burden_30_34pct` – Renters paying 30-34% of income
- `rent_burden_35_39pct` – Renters paying 35-39% of income
- `rent_burden_40_49pct` – Renters paying 40-49% of income
- `rent_burden_50plus_pct` – Renters paying 50%+ of income (severely burdened)
- `rent_burden_universe` – Total renters for calculation
- `gross_rent_pct_income` – Average gross rent as % of income

**Calculated rates:**
- `homeownership_rate` – % of occupied units that are owner-occupied
- `vacancy_rate` – % of housing units that are vacant
- `rent_burden_30plus_pct` – % of renters paying 30%+ of income on rent (burdened)
- `rent_burden_severe_pct` – % of renters paying 50%+ of income on rent (severely burdened)

### 5. **Education** (9 columns)
**Raw counts (population 25+):**
- `edu_total_25plus` – Total population age 25+
- `edu_hs_grad` – High school graduates
- `edu_some_college` – Some college, no degree
- `edu_associates` – Associate's degree
- `edu_bachelors` – Bachelor's degree
- `edu_masters` – Master's degree
- `edu_professional` – Professional degree (JD, MD, etc.)
- `edu_doctorate` – Doctoral degree

**Calculated rates:**
- `pct_bachelors_plus` – % with bachelor's degree or higher

### 6. **Employment** (5 columns)
**Raw counts:**
- `labor_force` – People in labor force
- `employed` – Employed people
- `unemployed` – Unemployed people
- `labor_force_universe` – Total population for labor force calculation

**Calculated rates:**
- `unemployment_rate_acs` – % of labor force unemployed

### 7. **Commuting** (10 columns)
**Mode of transportation:**
- `commute_total` – Total commuters
- `commute_car_alone` – Drive alone
- `commute_carpool` – Carpool
- `commute_transit` – Public transit
- `commute_wfh` – Work from home

**Travel time:**
- `travel_time_aggregate` – Total minutes traveled (all commuters)
- `travel_time_universe` – Total commuters for time calculation

**Calculated metrics:**
- `avg_commute_minutes` – Average commute time in minutes
- `pct_transit_commute` – % of commuters using public transit
- `pct_wfh` – % of workers who work from home

### 8. **Year** (1 column)
- `acs_year` – Year of ACS survey (2012-2023)

---

## Key Metrics for Your Analysis

### **Economic Opportunity**
- `income_median_hh` – Primary income indicator
- `income_per_capita` – Individual prosperity
- `poverty_rate` – Economic vulnerability
- `unemployment_rate_acs` – Job market health
- `gini_index` – Income inequality

### **Affordability**
- `home_value_median` – Housing cost baseline
- `gross_rent_median` – Rental cost baseline
- `rent_burden_30plus_pct` – % of renters who are cost-burdened
- `rent_burden_severe_pct` – % of renters severely cost-burdened
- `homeownership_rate` – Homeownership accessibility

### **Quality of Life**
- `pct_bachelors_plus` – Education level (proxy for opportunity)
- `avg_commute_minutes` – Transportation burden
- `pct_wfh` – Work flexibility
- `diversity_index` – Community diversity
- `age_median` – Age profile

### **Real Estate Drivers**
- `income_median_hh` + `pct_bachelors_plus` → Purchasing power
- `pop_total` → Market size
- `pct_transit_commute` → Accessibility
- `homeownership_rate` → Housing demand

---

## Calculated vs. Raw Metrics

**Calculated metrics** (derived from raw counts):
- `poverty_rate` = `poverty_count` / `poverty_universe` × 100
- `unemployment_rate_acs` = `unemployed` / `labor_force` × 100
- `pct_bachelors_plus` = (`edu_bachelors` + `edu_masters` + `edu_professional` + `edu_doctorate`) / `edu_total_25plus` × 100
- `homeownership_rate` = `housing_owner_occ` / `housing_occupied` × 100
- `vacancy_rate` = `housing_vacant` / `housing_units_total` × 100
- `rent_burden_30plus_pct` = (sum of rent_burden categories 30%+) / `rent_burden_universe` × 100
- `avg_commute_minutes` = `travel_time_aggregate` / `travel_time_universe`
- `pct_transit_commute` = `commute_transit` / `commute_total` × 100
- `pct_wfh` = `commute_wfh` / `commute_total` × 100
- `diversity_index` = 1 - Σ(race_proportion²) for all race categories

---

## Sample Use Cases

### 1. **Affordability Analysis**
```sql
SELECT
    NAME,
    income_median_hh,
    home_value_median,
    ROUND(home_value_median / income_median_hh, 2) AS affordability_ratio,
    rent_burden_30plus_pct
FROM census_acs
WHERE acs_year = 2023
  AND geo_type = 'zcta'
  AND income_median_hh IS NOT NULL
ORDER BY affordability_ratio DESC
```

### 2. **Income Drivers Analysis**
```sql
SELECT
    pct_bachelors_plus,
    income_median_hh,
    unemployment_rate_acs,
    poverty_rate
FROM census_acs
WHERE acs_year = 2023
  AND geo_type = 'zcta'
  AND pop_total > 1000  -- Filter small populations
```

### 3. **Trend Analysis (Income Growth)**
```sql
SELECT
    geoid,
    NAME,
    acs_year,
    income_median_hh,
    LAG(income_median_hh) OVER (PARTITION BY geoid ORDER BY acs_year) AS prev_year_income,
    ROUND((income_median_hh - LAG(income_median_hh) OVER (PARTITION BY geoid ORDER BY acs_year))
          / LAG(income_median_hh) OVER (PARTITION BY geoid ORDER BY acs_year) * 100, 2) AS yoy_growth_pct
FROM census_acs
WHERE geo_type = 'zcta'
ORDER BY geoid, acs_year
```

### 4. **Vulnerability Score**
```sql
SELECT
    NAME,
    poverty_rate,
    unemployment_rate_acs,
    rent_burden_severe_pct,
    ROUND((poverty_rate + unemployment_rate_acs + rent_burden_severe_pct) / 3, 2) AS vulnerability_score
FROM census_acs
WHERE acs_year = 2023
  AND geo_type = 'zcta'
ORDER BY vulnerability_score DESC
LIMIT 20
```

---

## Data Limitations & Considerations

### Missing Data
- **~5% missing** for income and home value metrics (small populations, insufficient sample)
- **~1% missing** for poverty, education, unemployment
- Missing values are typically in **very small ZCTAs** (population < 500)

### Small Population Issues
- ZCTAs with `pop_total < 500` may have:
  - High margins of error
  - More NULL values
  - Less reliable year-over-year comparisons
- **Recommendation**: Filter to `pop_total > 1000` for most analyses

### Temporal Considerations
- **ACS is a 5-year survey** (e.g., 2023 = 2019-2023 data)
- Data is **less current** than Zillow real estate prices
- **Inflation adjustment needed** for income/value comparisons across years

### Geographic Mismatches
- **ZCTAs ≠ ZIP Codes** (ZCTAs are Census approximations)
- **Places ≠ Municipalities** perfectly (some overlap/nesting)
- **No direct ZCTA → Municipality crosswalk** in current data

---

## Integration with Other Datasets

### Census ACS + Zillow
- **Join key**: `acs_zctas.zcta = zillow.zip_code`
- **Use case**: Compare ACS income vs. Zillow home values for affordability analysis

### Census ACS + CDC PLACES
- **Join key**: `acs_zctas.zcta = cdc_places.zcta`
- **Use case**: Correlate economic factors with health outcomes

### Census ACS + NJ DCA
- **Join challenge**: DCA is by municipality name, ACS places by GEOID
- **Workaround**: Fuzzy match on municipality name (already in v_municipality_scorecard view)
- **Use case**: Add property tax burden to affordability analysis

---

## Next Steps for Your Analysis

### Immediate Actions
1. **Create derived metrics table**:
   - Affordability ratio (home value / income)
   - Economic opportunity index
   - Quality of life composite score

2. **Build time series views**:
   - Income growth rates (5-year, 10-year)
   - Home value appreciation
   - Poverty rate trends

3. **Calculate percentile rankings**:
   - Rank all ZCTAs on each key metric
   - Identify top/bottom performers

### Analysis Priorities
1. **Correlation analysis**: Which factors predict high income? Low poverty?
2. **Cluster analysis**: Identify community "types" (affluent suburban, working-class urban, etc.)
3. **Trend identification**: Which communities are improving/declining?
4. **Affordability crisis mapping**: Where is housing unaffordable?

---

## Summary Statistics (2023 Data)

**Population:**
- Total: ~9M (summed across all geographies)
- Median ZCTA population: ~7,500

**Income:**
- Statewide median household income: ~$90k
- Range: $13k–$250k+

**Housing:**
- Median home value: ~$340k
- Median rent: ~$1,460/month
- Homeownership rate: ~72%

**Education:**
- Average % with bachelor's+: ~40%

**Economic Health:**
- Average poverty rate: ~8.5%
- Average unemployment: ~7.2%

---

*This dataset is your analytical foundation for understanding NJ communities.*
