# Analysis Guides

This guide provides step-by-step instructions for common analyses using the NJ Pipeline.

---

## Getting Started

### Prerequisites
1. Data loaded into DuckDB (`data/db/nj_pipeline.duckdb`)
2. Python environment with required packages
3. Jupyter notebook access (optional but recommended)

### Connecting to the Database

#### Python
```python
import duckdb
from pathlib import Path

db_path = Path('data/db/nj_pipeline.duckdb')
conn = duckdb.connect(str(db_path), read_only=True)

# Run a query
result = conn.execute("SELECT COUNT(*) FROM zillow_zipcode_latest").fetchone()
print(f"Number of ZIP codes: {result[0]}")

# Get DataFrame
df = conn.execute("SELECT * FROM cdc_places_wide WHERE year = 2023").df()
```

#### SQL Client
```bash
# Using DuckDB CLI
duckdb data/db/nj_pipeline.duckdb

# Or use any SQL client that supports DuckDB
```

---

## Analysis 1: Housing Market Analysis

### Objective
Understand New Jersey housing market trends, identify expensive vs. affordable areas, and analyze price-to-rent ratios.

### Step 1: Load Data

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Latest market snapshot
latest = conn.execute("""
    SELECT *
    FROM zillow_zipcode_latest
    WHERE zhvi_latest IS NOT NULL
    ORDER BY zhvi_latest DESC
""").df()
```

### Step 2: Summary Statistics

```python
print("Home Value Statistics:")
print(latest['zhvi_latest'].describe())

print("\nRent Statistics:")
print(latest['zori_latest'].describe())

print(f"\nMedian Price-to-Rent Ratio: {latest['price_to_rent_ratio'].median():.1f}")
```

### Step 3: Visualize Geographic Patterns

```python
# Home values by county
county_summary = latest.groupby('county').agg({
    'zhvi_latest': ['count', 'mean', 'median'],
    'zori_latest': 'median'
}).round(0)

# Plot
fig, ax = plt.subplots(figsize=(12, 8))
county_summary['zhvi_latest']['median'].sort_values().plot(kind='barh', ax=ax)
ax.set_xlabel('Median Home Value ($)')
ax.set_title('Median Home Values by County')
plt.tight_layout()
plt.show()
```

### Step 4: Time Series Analysis

```python
# Get time series for a specific ZIP code
zip_code = '07920'  # Example: Short Hills

time_series = conn.execute(f"""
    SELECT date, zhvi
    FROM zillow_home_values
    WHERE zip_code = '{zip_code}'
    ORDER BY date
""").df()

# Plot
plt.figure(figsize=(14, 6))
plt.plot(time_series['date'], time_series['zhvi'], linewidth=2)
plt.xlabel('Date')
plt.ylabel('Home Value ($)')
plt.title(f'Home Value Trend - ZIP {zip_code}')
plt.grid(True, alpha=0.3)
plt.show()
```

### Step 5: Comparative Analysis

```python
# Compare multiple ZIP codes
zip_codes = ['07920', '08540', '07302']  # Short Hills, Princeton, Jersey City

comparison = conn.execute(f"""
    SELECT
        zip_code,
        date,
        zhvi
    FROM zillow_home_values
    WHERE zip_code IN ('{"','".join(zip_codes)}')
    ORDER BY zip_code, date
""").df()

# Plot
fig, ax = plt.subplots(figsize=(14, 6))
for zip_code in zip_codes:
    data = comparison[comparison['zip_code'] == zip_code]
    ax.plot(data['date'], data['zhvi'], label=f'ZIP {zip_code}', linewidth=2)

ax.set_xlabel('Date')
ax.set_ylabel('Home Value ($)')
ax.set_title('Home Value Comparison')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

---

## Analysis 2: Public Health Disparities

### Objective
Identify ZCTAs with the highest health burdens and understand correlations between different health measures.

### Step 1: Load 2023 Health Data

```python
health_data = conn.execute("""
    SELECT *
    FROM cdc_places_wide
    WHERE year = 2023
      AND obesity IS NOT NULL
""").df()
```

### Step 2: Calculate Health Burden Index

```python
# Composite index of key health measures
health_measures = ['obesity', 'diabetes', 'bphigh', 'csmoking', 'depression']
health_data['health_burden_index'] = health_data[health_measures].mean(axis=1)

# Sort by burden
worst_health = health_data.nsmallest(10, 'health_burden_index')
print("ZCTAs with Lowest Health Outcomes:")
print(worst_health[['zcta', 'health_burden_index'] + health_measures])
```

### Step 3: Correlation Analysis

```python
# Correlation matrix
corr_matrix = health_data[health_measures].corr()

# Heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0)
plt.title('Health Measure Correlations')
plt.tight_layout()
plt.show()
```

### Step 4: Geographic Clustering

```python
# Group by first 3 digits of ZCTA (rough county grouping)
health_data['region'] = health_data['zcta'].str[:3]

regional_health = health_data.groupby('region').agg({
    'health_burden_index': 'mean',
    'zcta': 'count'
}).rename(columns={'zcta': 'num_zctas'})

print("\nRegional Health Burden:")
print(regional_health.sort_values('health_burden_index', ascending=False))
```

---

## Analysis 3: Environmental Health Integration

### Objective
Analyze relationships between tree coverage, home values, and health outcomes.

### Prerequisites
- Tree Equity Score data must be loaded

### Step 1: Join All Three Datasets

```python
combined = conn.execute("""
    SELECT
        z.zip_code,
        z.county,
        z.zhvi_latest,
        z.zori_latest,
        c.obesity,
        c.diabetes,
        c.bphigh,
        c.csmoking,
        c.depression,
        t.avg_tree_canopy_pct,
        t.avg_tree_equity_score
    FROM zillow_zipcode_latest z
    LEFT JOIN cdc_places_wide c ON z.zip_code = c.zcta AND c.year = 2023
    LEFT JOIN tree_equity_zcta t ON z.zip_code = t.zcta
    WHERE z.zhvi_latest IS NOT NULL
""").df()

print(f"Combined dataset: {len(combined)} ZIP codes")
print(f"With tree data: {combined['avg_tree_canopy_pct'].notna().sum()}")
print(f"With health data: {combined['obesity'].notna().sum()}")
```

### Step 2: Tree Coverage vs. Home Values

```python
# Remove missing values
plot_data = combined[['avg_tree_canopy_pct', 'zhvi_latest']].dropna()

# Scatter plot
plt.figure(figsize=(12, 8))
plt.scatter(plot_data['avg_tree_canopy_pct'], plot_data['zhvi_latest'], alpha=0.5)

# Add trend line
z = np.polyfit(plot_data['avg_tree_canopy_pct'], plot_data['zhvi_latest'], 1)
p = np.poly1d(z)
plt.plot(plot_data['avg_tree_canopy_pct'],
         p(plot_data['avg_tree_canopy_pct']),
         "r--", linewidth=2, label='Trend')

# Correlation
corr = plot_data['avg_tree_canopy_pct'].corr(plot_data['zhvi_latest'])

plt.xlabel('Tree Canopy Coverage (%)')
plt.ylabel('Median Home Value ($)')
plt.title(f'Tree Coverage vs. Home Values (Correlation: {corr:.3f})')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### Step 3: Tree Coverage vs. Health Outcomes

```python
# Correlations with tree coverage
health_measures = ['obesity', 'diabetes', 'bphigh', 'csmoking', 'depression']

print("Correlations: Tree Coverage vs. Health Outcomes")
print("=" * 60)
for measure in health_measures:
    subset = combined[['avg_tree_canopy_pct', measure]].dropna()
    if len(subset) > 0:
        corr = subset['avg_tree_canopy_pct'].corr(subset[measure])
        print(f"{measure.capitalize():20s}: {corr:7.3f}")
```

### Step 4: Create Environmental Health Index

```python
# Normalize tree coverage (0-100, higher is better)
tree_norm = (combined['avg_tree_canopy_pct'] - combined['avg_tree_canopy_pct'].min()) / \\
            (combined['avg_tree_canopy_pct'].max() - combined['avg_tree_canopy_pct'].min()) * 100

# Normalize health burden (0-100, higher is worse)
combined['health_burden'] = combined[health_measures].mean(axis=1)
health_norm = (combined['health_burden'] - combined['health_burden'].min()) / \\
              (combined['health_burden'].max() - combined['health_burden'].min()) * 100

# Environmental Health Index: more trees = positive, more health problems = negative
combined['env_health_index'] = tree_norm - health_norm

# Find best and worst areas
best = combined.nlargest(10, 'env_health_index')[
    ['zip_code', 'county', 'avg_tree_canopy_pct', 'health_burden', 'env_health_index']
]

worst = combined.nsmallest(10, 'env_health_index')[
    ['zip_code', 'county', 'avg_tree_canopy_pct', 'health_burden', 'env_health_index']
]

print("Best Environmental Health:")
print(best)
print("\nWorst Environmental Health:")
print(worst)
```

---

## Analysis 4: Temporal Trends

### Objective
Analyze how housing markets have changed over time, identify inflection points, and project future trends.

### Step 1: Overall Market Trends

```python
# Aggregate all ZIP codes
monthly_trends = conn.execute("""
    SELECT
        date,
        AVG(zhvi) as avg_home_value,
        MEDIAN(zhvi) as median_home_value,
        COUNT(*) as num_zips
    FROM zillow_home_values
    GROUP BY date
    ORDER BY date
""").df()

# Plot
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(monthly_trends['date'], monthly_trends['median_home_value'],
        linewidth=2, label='Median')
ax.plot(monthly_trends['date'], monthly_trends['avg_home_value'],
        linewidth=2, alpha=0.7, label='Mean')

# Mark significant events
ax.axvline(pd.Timestamp('2008-09-15'), color='red', linestyle='--',
           alpha=0.5, label='2008 Financial Crisis')
ax.axvline(pd.Timestamp('2020-03-01'), color='orange', linestyle='--',
           alpha=0.5, label='COVID-19 Pandemic')

ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Home Value ($)', fontsize=12)
ax.set_title('NJ Housing Market Trends (2000-2026)', fontsize=14)
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### Step 2: Calculate Growth Rates

```python
# Year-over-year growth
growth = conn.execute("""
    WITH yearly AS (
        SELECT
            YEAR(date) as year,
            AVG(zhvi) as avg_value
        FROM zillow_home_values
        WHERE MONTH(date) = 1  -- January of each year
        GROUP BY YEAR(date)
    )
    SELECT
        year,
        avg_value,
        LAG(avg_value) OVER (ORDER BY year) as prev_year_value,
        ((avg_value - LAG(avg_value) OVER (ORDER BY year)) /
         LAG(avg_value) OVER (ORDER BY year) * 100) as yoy_growth_pct
    FROM yearly
    ORDER BY year
""").df()

print("Year-over-Year Growth Rates:")
print(growth)
```

### Step 3: County Comparison Over Time

```python
# Top 5 counties by median value
top_counties = latest.groupby('county')['zhvi_latest'].median().nlargest(5).index.tolist()

# Get time series for these counties
county_trends = conn.execute(f"""
    SELECT
        h.county,
        h.date,
        AVG(h.zhvi) as avg_value
    FROM zillow_home_values h
    WHERE h.county IN ('{"','".join(top_counties)}')
    GROUP BY h.county, h.date
    ORDER BY h.county, h.date
""").df()

# Plot
fig, ax = plt.subplots(figsize=(16, 8))
for county in top_counties:
    data = county_trends[county_trends['county'] == county]
    ax.plot(data['date'], data['avg_value'], label=county, linewidth=2)

ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Average Home Value ($)', fontsize=12)
ax.set_title('Home Value Trends - Top 5 Counties', fontsize=14)
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

---

## Analysis 5: Affordability Analysis

### Objective
Identify affordable vs. expensive areas and calculate price-to-income ratios.

### Step 1: Price-to-Rent Ratio

```python
# Analyze areas by price-to-rent ratio
affordability = latest[['zip_code', 'county', 'zhvi_latest', 'zori_latest',
                        'price_to_rent_ratio']].dropna()

# Categorize
affordability['category'] = pd.cut(affordability['price_to_rent_ratio'],
                                   bins=[0, 15, 20, 100],
                                   labels=['Rent Favorable', 'Balanced', 'Buy Favorable'])

print("Affordability Distribution:")
print(affordability['category'].value_counts())

# Visualization
fig, ax = plt.subplots(figsize=(12, 6))
affordability.boxplot(column='price_to_rent_ratio', by='category', ax=ax)
plt.suptitle('')
ax.set_title('Price-to-Rent Ratio by Category')
ax.set_xlabel('Category')
ax.set_ylabel('Price-to-Rent Ratio')
plt.tight_layout()
plt.show()
```

### Step 2: Identify Investment Opportunities

```python
# Low price, high appreciation potential
# Get recent growth rate
recent_growth = conn.execute("""
    SELECT
        zip_code,
        zhvi as value_2020,
        (SELECT zhvi FROM zillow_home_values h2
         WHERE h2.zip_code = h1.zip_code
         ORDER BY date DESC LIMIT 1) as value_latest
    FROM zillow_home_values h1
    WHERE date = '2020-01-31'
""").df()

recent_growth['growth_pct'] = (
    (recent_growth['value_latest'] - recent_growth['value_2020']) /
    recent_growth['value_2020'] * 100
)

# Merge with latest data
opportunities = latest.merge(recent_growth[['zip_code', 'growth_pct']], on='zip_code')

# Find: below median price, above median growth
median_price = opportunities['zhvi_latest'].median()
median_growth = opportunities['growth_pct'].median()

opportunities['is_opportunity'] = (
    (opportunities['zhvi_latest'] < median_price) &
    (opportunities['growth_pct'] > median_growth)
)

print(f"Investment Opportunities: {opportunities['is_opportunity'].sum()} ZIP codes")
print("\nTop 10 Opportunities:")
print(opportunities[opportunities['is_opportunity']].nlargest(10, 'growth_pct')[
    ['zip_code', 'county', 'zhvi_latest', 'growth_pct']
])
```

---

## Tips and Best Practices

### Performance Optimization
```sql
-- Use WHERE clause to filter before joins
-- Bad:
SELECT * FROM large_table
JOIN another_table USING (key)
WHERE large_table.year = 2023;

-- Good:
SELECT * FROM (
    SELECT * FROM large_table WHERE year = 2023
) lt
JOIN another_table USING (key);
```

### Handling Missing Data
```python
# Check completeness before analysis
print("Data completeness:")
print(df.notna().sum() / len(df) * 100)

# Drop rows with missing key variables
df_clean = df.dropna(subset=['key_variable1', 'key_variable2'])

# Or fill with appropriate values
df['tree_canopy'] = df['tree_canopy'].fillna(df['tree_canopy'].median())
```

### Visualization Tips
```python
# Set a consistent style
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Save figures
fig.savefig('output/figure_name.png', dpi=300, bbox_inches='tight')
```

---

## Related Documentation
- [[01_Pipeline_Overview]] - Project overview
- [[02_Data_Sources]] - Data source details
- [[04_API_Reference]] - Database schema reference

**Last Updated**: 2026-03-05
