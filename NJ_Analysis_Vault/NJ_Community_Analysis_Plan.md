# New Jersey Community Data Analysis Plan

## Overview
This document outlines a comprehensive analysis framework for understanding New Jersey communities through census and economic data. The goal is to create artifacts that help citizens compare their towns and understand key drivers of income, quality of life, affordability, and real estate dynamics.

---

## 1. Data Assets Available

### Current Database Coverage
- **599 ZIP Code Tabulation Areas (ZCTAs)**
- **Total Population**: ~108M records across years
- **Time Series Data**: Multiple years of ACS data per ZCTA
- **63 Variables** covering demographics, economics, housing, and social factors

### Key Metrics Available
- Demographics: Population, age, race/ethnicity
- Economics: Income, poverty, unemployment, education
- Housing: Home values, rent, ownership rates, rent burden
- Geographic: Places (705) and ZCTAs (600)

---

## 2. Proposed Artifacts for Citizens

### 2.1 Interactive Dashboards

#### A. **Community Scorecard**
**Purpose**: Single-page overview of any ZCTA's vital statistics

**Metrics to Include**:
- Population size and trend (over time)
- Median household income vs. state average
- Poverty rate
- Median home value
- Homeownership rate
- Rent burden (% paying >30% of income)
- Educational attainment (% bachelor's+)
- Unemployment rate
- Diversity index

**Format**: PDF report or web dashboard with percentile rankings

---

#### B. **Comparative Rankings Tool**
**Purpose**: See where your community ranks on key metrics

**Categories**:
1. **Affordability Rankings**
   - Most/least affordable ZCTAs (income-to-housing ratio)
   - Lowest/highest rent burden
   - Property tax burden (if data available)

2. **Economic Opportunity Rankings**
   - Highest/lowest median incomes
   - Lowest unemployment rates
   - Highest education attainment

3. **Quality of Life Rankings**
   - Lowest poverty rates
   - Highest homeownership rates
   - Best economic mobility (income growth over time)

**Format**: Sortable table with filters

---

#### C. **Housing Affordability Calculator**
**Purpose**: Understand if housing is affordable in your area

**Calculations**:
- Income needed to afford median home (assuming 28% DTI)
- Income needed to afford median rent (30% rule)
- Affordability gap: median income vs. required income
- Rent vs. buy comparison
- Historical trends: How has affordability changed?

**Format**: Interactive calculator with ZCTA-specific results

---

### 2.2 Analytical Reports

#### D. **Key Drivers Analysis**
**Purpose**: Statistical analysis of what predicts high/low outcomes

**Analyses to Conduct**:

1. **Income Drivers**
   - Correlation analysis: What predicts higher median income?
     - Education levels
     - Industry composition (if available)
     - Proximity to urban centers
     - Demographics
   - Regression model: Quantify impact of each factor

2. **Quality of Life Drivers**
   - What factors correlate with low poverty rates?
   - What predicts high homeownership?
   - Education → Income → Quality of Life pathway analysis

3. **Unaffordability Drivers**
   - What makes housing unaffordable?
     - Home value vs. income mismatch
     - Rent burden analysis
     - Supply constraints (vacancy rates)
   - Gentrification indicators: Rapid income/value changes

4. **Real Estate Value Drivers**
   - What predicts high home values?
     - Income levels
     - School quality (if available)
     - Demographics
     - Location factors

**Format**: Written report with visualizations (scatter plots, regression tables)

---

#### E. **Vulnerability Index**
**Purpose**: Identify communities most at risk

**Components**:
- High poverty rate (>20%)
- Low median income (<$40k)
- High unemployment (>10%)
- Severe rent burden (>50% paying >30%)
- Low educational attainment

**Output**:
- Map of vulnerable ZCTAs
- List of communities needing support
- Trend analysis: Are they improving or declining?

**Format**: Heat map + detailed profiles

---

#### F. **Trend Analysis Report**
**Purpose**: How are communities changing over time?

**Metrics to Track**:
1. **Income trends** (2012-2022)
   - Which ZCTAs saw biggest income gains/losses?
   - Inflation-adjusted changes

2. **Housing market trends**
   - Home value appreciation rates
   - Rent growth rates
   - Affordability deterioration

3. **Demographic shifts**
   - Population growth/decline
   - Aging trends
   - Diversity changes

4. **Economic health trends**
   - Poverty rate changes
   - Unemployment trends
   - Educational attainment improvements

**Format**: Time series visualizations + top/bottom performers lists

---

### 2.3 Interactive Tools

#### G. **ZCTA Comparison Tool**
**Purpose**: Compare up to 5 ZCTAs side-by-side

**Features**:
- Select ZCTAs by code or map
- View key metrics in table format
- Visualize differences (radar charts, bar charts)
- Include state average for context
- Show percentile rankings

**Format**: Web-based interactive tool

---

#### H. **Migration Decision Tool**
**Purpose**: Help people decide where to live based on priorities

**User Inputs**:
- Budget (income level)
- Priorities (affordability, schools, diversity, etc.)
- Current location (for comparison)

**Output**:
- Top 10 recommended ZCTAs
- Pros/cons of each
- Cost-of-living comparison
- Commute considerations (if data available)

**Format**: Web-based recommendation engine

---

## 3. Statistical Analyses to Conduct

### 3.1 Correlation Studies
```sql
-- Income vs. Housing Value
-- Income vs. Education
-- Rent Burden vs. Poverty
-- Diversity vs. Economic Outcomes
```

### 3.2 Regression Models
**Target Variables**:
- Median household income
- Home values
- Poverty rates
- Quality of life composite score

**Predictors**:
- Education levels
- Age distribution
- Racial composition
- Homeownership rate
- Employment rate

### 3.3 Clustering Analysis
- Identify community "types" (affluent suburban, working-class urban, etc.)
- K-means or hierarchical clustering
- Profile each cluster

### 3.4 Time Series Analysis
- ARIMA forecasting for income/housing trends
- Identify inflection points
- Calculate growth rates and momentum

---

## 4. Key Questions to Answer

### For Individual Citizens:
1. How does my ZCTA compare to others in NJ?
2. Is housing affordable here relative to incomes?
3. Is my community improving or declining economically?
4. What are the best communities for my budget?
5. Where can I get the most value (income, housing, quality)?

### For Policymakers:
1. Which communities need the most support?
2. What interventions would have the biggest impact?
3. Are there warning signs of economic decline?
4. How does affordability vary across the state?
5. What policies correlate with better outcomes?

### For Researchers:
1. What drives income inequality across communities?
2. How does education impact economic mobility?
3. What predicts real estate appreciation?
4. Are there spatial patterns (clusters of poverty/wealth)?
5. How have communities changed over the past decade?

---

## 5. Visualization Recommendations

### Static Visualizations
1. **Choropleth maps**: Poverty, income, home values by ZCTA
2. **Scatter plots**: Income vs. education, income vs. home value
3. **Bar charts**: Top/bottom 20 ZCTAs for each metric
4. **Box plots**: Distribution of key metrics
5. **Heatmaps**: Correlation matrices
6. **Time series**: Trends over years

### Interactive Visualizations
1. **Filterable maps**: Click ZCTA to see details
2. **Slider controls**: Adjust income/budget to see recommendations
3. **Linked charts**: Click bar chart → highlight on map
4. **Animated time series**: Watch changes over time

---

## 6. Implementation Roadmap

### Phase 1: Data Preparation (Week 1-2)
- [ ] Clean and validate all data
- [ ] Calculate derived metrics (affordability ratios, etc.)
- [ ] Handle missing values appropriately
- [ ] Create time series datasets
- [ ] Build lookup tables for ZCTA names/locations

### Phase 2: Core Analytics (Week 3-4)
- [ ] Run correlation analyses
- [ ] Build regression models
- [ ] Conduct clustering analysis
- [ ] Calculate rankings and percentiles
- [ ] Create vulnerability index

### Phase 3: Artifact Development (Week 5-8)
- [ ] Build Community Scorecard template
- [ ] Create Rankings Dashboard
- [ ] Develop Affordability Calculator
- [ ] Write Key Drivers Report
- [ ] Build Comparison Tool
- [ ] Design Trend Analysis Report

### Phase 4: Visualization & Polish (Week 9-10)
- [ ] Create all static visualizations
- [ ] Build interactive web tools
- [ ] Design user-friendly interfaces
- [ ] Write documentation/help text
- [ ] User testing and refinement

### Phase 5: Deployment & Outreach (Week 11-12)
- [ ] Deploy web tools
- [ ] Publish reports
- [ ] Create executive summaries
- [ ] Prepare presentations
- [ ] Gather feedback and iterate

---

## 7. Technical Stack Recommendations

### Data Analysis
- **Python**: pandas, numpy, scipy, sklearn
- **DuckDB**: Fast SQL queries on local data
- **Jupyter**: Exploratory analysis and reporting

### Visualization
- **Static**: matplotlib, seaborn, plotly
- **Interactive**: Plotly Dash, Streamlit, or Tableau
- **Maps**: Folium, Plotly, or Mapbox

### Web Deployment
- **Backend**: Flask or FastAPI
- **Frontend**: React or Vue.js (for advanced tools)
- **Hosting**: GitHub Pages (static) or Heroku/AWS (dynamic)

---

## 8. Data Caveats & Limitations

1. **ZCTA boundaries** don't perfectly match municipalities
2. **Missing data** for some small-population ZCTAs
3. **ACS estimates** have margins of error
4. **Temporal mismatch**: Different years may not be directly comparable
5. **Causation**: Correlations don't prove causation
6. **Outliers**: Very small ZCTAs (pop < 500) may skew results

**Mitigation Strategies**:
- Filter out ZCTAs with pop < 500 for most analyses
- Report margins of error where relevant
- Use multi-year averages to reduce noise
- Clearly label correlations vs. causal claims

---

## 9. Next Steps

### Immediate Actions:
1. **Reconnect to database** (fix connection error)
2. **Create master analysis script** that:
   - Calculates all derived metrics
   - Exports clean datasets for visualization
   - Generates summary statistics
3. **Prioritize artifacts** based on impact and effort
4. **Start with Community Scorecard** (highest value, moderate effort)

### Quick Wins (This Week):
- Generate Top 20 / Bottom 20 lists for all key metrics
- Create affordability ratio metric (home value / income)
- Build simple HTML report with embedded charts
- Export CSV datasets for community consumption

---

## 10. Sample Analyses to Start With

### Analysis 1: Affordability Crisis Map
```python
# Calculate affordability ratio
nj_zctas['affordability_ratio'] = nj_zctas['home_value_median'] / nj_zctas['income_median_hh']

# Flag unaffordable areas (ratio > 5, which means 5x income)
nj_zctas['unaffordable'] = nj_zctas['affordability_ratio'] > 5

# Map and count
```

### Analysis 2: Economic Opportunity Index
```python
# Composite score (normalize and weight factors)
opportunity_score = (
    0.4 * normalized_income +
    0.3 * normalized_education +
    0.2 * (1 - normalized_poverty) +
    0.1 * (1 - normalized_unemployment)
)
```

### Analysis 3: Gentrification Detector
```python
# Find ZCTAs with:
# - Rapid income growth (>20% in 5 years)
# - Rapid home value growth (>30% in 5 years)
# - But still below median income (potential gentrifying areas)
```

---

## Appendix: Metric Definitions

**Rent Burden**: % of income spent on rent (>30% = burdened, >50% = severely burdened)

**Diversity Index**: Probability two random people are different races (0=homogeneous, 1=diverse)

**Affordability Ratio**: Median home value / Median household income (>5 = unaffordable)

**Vulnerability Score**: Composite of poverty, unemployment, rent burden, low income

**Quality of Life Index**: Composite of income, education, low poverty, homeownership

---

*Document Version: 1.0*
*Last Updated: 2026-03-03*
*Dataset: NJ ACS/Census Data (599 ZCTAs)*
