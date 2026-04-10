"""
Census ACS Data Exploration with Data Wrangler
===============================================

This script loads Census ACS data for visual exploration in VS Code's Data Wrangler.

Usage:
1. Open this file in VS Code
2. Click on the "df" variable in the Variables pane
3. Click "Open in Data Wrangler" to explore visually

Available datasets:
- zcta_2023: Latest year ZCTA data (598 records)
- zcta_all: All years ZCTA data (7,149 records)
- places_2023: Latest year Places/municipalities data (700 records)
"""

import pandas as pd
import duckdb

# Connect to database
conn = duckdb.connect('../data/db/nj_pipeline.duckdb', read_only=True)

# Load latest year ZCTA data
zcta_2023 = conn.execute("""
    SELECT
        geoid,
        NAME,
        zcta,
        pop_total,
        age_median,
        income_median_hh,
        income_per_capita,
        poverty_rate,
        unemployment_rate_acs,
        pct_bachelors_plus,
        home_value_median,
        gross_rent_median,
        homeownership_rate,
        vacancy_rate,
        rent_burden_30plus_pct,
        rent_burden_severe_pct,
        avg_commute_minutes,
        pct_transit_commute,
        pct_wfh,
        diversity_index,
        gini_index,
        -- Racial composition
        race_white,
        race_black,
        race_asian,
        race_hispanic
    FROM acs_zctas
    WHERE acs_year = (SELECT MAX(acs_year) FROM acs_zctas)
    ORDER BY geoid
""").df()

# Calculate derived metrics for analysis
zcta_2023['affordability_ratio'] = zcta_2023['home_value_median'] / zcta_2023['income_median_hh']
zcta_2023['rent_to_income_annual_pct'] = (zcta_2023['gross_rent_median'] * 12) / zcta_2023['income_median_hh'] * 100

# Classify ZCTAs by size
def classify_population(pop):
    if pd.isna(pop):
        return 'Unknown'
    elif pop < 1000:
        return 'Very Small (<1k)'
    elif pop < 5000:
        return 'Small (1k-5k)'
    elif pop < 20000:
        return 'Medium (5k-20k)'
    elif pop < 50000:
        return 'Large (20k-50k)'
    else:
        return 'Very Large (50k+)'

zcta_2023['population_category'] = zcta_2023['pop_total'].apply(classify_population)

# Classify by income
def classify_income(income):
    if pd.isna(income):
        return 'Unknown'
    elif income < 40000:
        return 'Low (<$40k)'
    elif income < 75000:
        return 'Lower-Middle ($40k-$75k)'
    elif income < 100000:
        return 'Middle ($75k-$100k)'
    elif income < 150000:
        return 'Upper-Middle ($100k-$150k)'
    else:
        return 'High ($150k+)'

zcta_2023['income_category'] = zcta_2023['income_median_hh'].apply(classify_income)

# Affordability classification
def classify_affordability(ratio):
    if pd.isna(ratio):
        return 'Unknown'
    elif ratio < 3:
        return 'Very Affordable (<3x)'
    elif ratio < 4:
        return 'Affordable (3-4x)'
    elif ratio < 5:
        return 'Moderately Unaffordable (4-5x)'
    elif ratio < 7:
        return 'Unaffordable (5-7x)'
    else:
        return 'Very Unaffordable (7x+)'

zcta_2023['affordability_category'] = zcta_2023['affordability_ratio'].apply(classify_affordability)

print(f"Loaded {len(zcta_2023)} ZCTA records for 2023")
print(f"\nColumns: {list(zcta_2023.columns)}")
print(f"\nSample data:")
print(zcta_2023.head())

# For Data Wrangler - rename for easy access
df = zcta_2023

print("\n" + "="*60)
print("READY FOR DATA WRANGLER!")
print("="*60)
print("\nIn VS Code:")
print("1. Run this cell to load 'df'")
print("2. Look at the Variables pane (bottom of the window)")
print("3. Click on 'df' variable")
print("4. Click 'Open in Data Wrangler' button")
print("\nData Wrangler will let you:")
print("- Sort and filter data visually")
print("- Create charts and visualizations")
print("- Perform aggregations and groupings")
print("- Export cleaned/transformed data")

# Also available: time series data
zcta_all_years = conn.execute("""
    SELECT
        geoid,
        zcta,
        acs_year,
        pop_total,
        income_median_hh,
        poverty_rate,
        unemployment_rate_acs,
        home_value_median,
        gross_rent_median,
        pct_bachelors_plus
    FROM acs_zctas
    ORDER BY geoid, acs_year
""").df()

print(f"\n\nAlso loaded: zcta_all_years ({len(zcta_all_years)} records)")
print("Use this for trend analysis across 2012-2023")

conn.close()
