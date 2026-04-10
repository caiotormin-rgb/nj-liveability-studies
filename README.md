# NJ Pipeline - Environmental Health & Housing Analytics

A comprehensive data analytics pipeline integrating environmental, public health, and housing data across New Jersey ZIP codes.

## 🎯 Project Overview

This pipeline combines three major data sources to enable multi-dimensional analysis of community health and environmental quality:

- **🏠 Zillow Housing Data**: Home values and rents (2000-2026)
- **🏥 CDC PLACES Health Data**: 22 health measures across 587 ZCTAs
- **🌳 Tree Equity Score**: Urban tree canopy and environmental justice metrics

### Key Questions Answered
- How does tree canopy coverage correlate with public health outcomes?
- What are the relationships between housing values, environmental quality, and community health?
- Which communities face the greatest environmental and health challenges?
- How have housing markets evolved over time?

## 📊 Data Sources

| Dataset | Records | Time Period | Coverage |
|---------|---------|-------------|----------|
| Zillow ZHVI | 683K | 2000-2026 | 552 NJ ZIP codes |
| Zillow ZORI | 152K | 2015-2026 | 230 NJ ZIP codes |
| CDC PLACES | 1,174 | 2022-2023 | 587 NJ ZCTAs |
| Tree Equity | TBD | 2023 | ~587 ZCTAs |

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.11+
conda create -n nj-pipeline python=3.11
conda activate nj-pipeline

# Install dependencies
pip install duckdb pandas numpy matplotlib seaborn jupyter
```

### Setup Database
```bash
# 1. Download data (see docs/vault for instructions)
# 2. Run ingestion scripts
python scripts/ingest_zillow.py
python scripts/ingest_cdc_places.py
python scripts/ingest_tree_equity.py  # After downloading Tree Equity data

# 3. Verify database
python -c "import duckdb; conn = duckdb.connect('data/db/nj_pipeline.duckdb'); print(conn.execute('SHOW TABLES').df())"
```

### Run Analysis
```bash
# Start Jupyter
jupyter notebook

# Open notebooks:
# - notebooks/eda_zillow.ipynb
# - notebooks/eda_cdc_places.ipynb
# - notebooks/eda_tree_equity.ipynb
```

## 📁 Project Structure

```
nj_pipeline/
├── data/
│   ├── raw/              # Original data files
│   │   ├── zillow/
│   │   ├── cdc_places/
│   │   └── tree_equity/
│   ├── processed/        # Cleaned data
│   └── db/              # DuckDB database
│       └── nj_pipeline.duckdb
│
├── scripts/             # Data ingestion scripts
│   ├── ingest_zillow.py
│   ├── ingest_cdc_places.py
│   └── ingest_tree_equity.py
│
├── notebooks/           # Analysis notebooks
│   ├── eda_zillow.ipynb
│   ├── eda_cdc_places.ipynb
│   └── eda_tree_equity.ipynb
│
└── docs/
    └── vault/          # Comprehensive documentation
        ├── 01_Pipeline_Overview.md
        ├── 02_Data_Sources.md
        └── 03_Analysis_Guides.md
```

## 💡 Example Analyses

### 1. Tree Coverage vs. Health Outcomes
```python
import duckdb

conn = duckdb.connect('data/db/nj_pipeline.duckdb')

# Find correlation between tree coverage and obesity
result = conn.execute("""
    SELECT
        CORR(t.avg_tree_canopy_pct, c.obesity) as correlation
    FROM tree_equity_zcta t
    JOIN cdc_places_wide c ON t.zcta = c.zcta
    WHERE c.year = 2023
""").fetchone()

print(f"Correlation: {result[0]:.3f}")
```

### 2. Housing Market Trends
```python
# Get median home values over time
trends = conn.execute("""
    SELECT
        date,
        MEDIAN(zhvi) as median_home_value
    FROM zillow_home_values
    GROUP BY date
    ORDER BY date
""").df()

import matplotlib.pyplot as plt
plt.figure(figsize=(14, 6))
plt.plot(trends['date'], trends['median_home_value'])
plt.title('NJ Median Home Values (2000-2026)')
plt.show()
```

### 3. Environmental Health Index
```python
# Identify priority areas (low trees + poor health)
priority_areas = conn.execute("""
    SELECT
        t.zcta,
        t.avg_tree_canopy_pct,
        (c.obesity + c.diabetes + c.bphigh) / 3 as health_burden
    FROM tree_equity_zcta t
    JOIN cdc_places_wide c ON t.zcta = c.zcta
    WHERE c.year = 2023
      AND t.avg_tree_canopy_pct < 20
    ORDER BY health_burden DESC
    LIMIT 10
""").df()
```

## 📈 Key Findings

### Health Patterns (2023 CDC Data)
- **Median Obesity Rate**: 28.2% (range: 12.1% - 45.4%)
- **Median Diabetes Rate**: 9.8% (range: 0.9% - 20.0%)
- **Strongest Correlation**: Diabetes ↔ Physical Inactivity (r=0.89)

### Housing Market
- **Median Home Value**: Varies widely by county
- **Price Growth 2020-2026**: Significant appreciation post-COVID
- **Price-to-Rent Ratio**: Tool for buy vs. rent decisions

### Environmental Equity
- Tree canopy coverage varies dramatically across ZCTAs
- Lower-income areas typically have less tree coverage
- Correlation with health outcomes under investigation

## 🔧 Technologies

- **Database**: DuckDB (embedded OLAP database)
- **Data Processing**: Python, Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn
- **Analysis**: Jupyter Notebooks
- **Data Sources**: Public datasets (Zillow, CDC, American Forests)

## 📚 Documentation

Comprehensive documentation available in `docs/vault/`:

- **[Pipeline Overview](docs/vault/01_Pipeline_Overview.md)**: Architecture and objectives
- **[Data Sources](docs/vault/02_Data_Sources.md)**: Detailed data documentation
- **[Analysis Guides](docs/vault/03_Analysis_Guides.md)**: Step-by-step analysis tutorials

## 🌱 Next Steps

### Immediate
1. ✅ Complete Zillow data ingestion
2. ✅ Complete CDC PLACES data ingestion
3. 🔄 Download and ingest Tree Equity Score data
4. 📊 Run comprehensive cross-dataset analysis

### Future Enhancements
- **Add Census Data**: Demographics, income, education
- **EPA Air Quality**: Add pollution metrics
- **Crime Statistics**: Safety indicators
- **School Data**: Education quality metrics
- **Transit Access**: Public transportation proximity
- **Interactive Dashboards**: Streamlit or Plotly Dash
- **Geospatial Visualizations**: Choropleth maps
- **Predictive Models**: ML for health outcome prediction

## 🤝 Contributing

This is a personal research project, but suggestions and feedback are welcome!

### To Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request with clear description

## 📄 Data Licenses

- **Zillow**: Available for research use
- **CDC PLACES**: Public domain (U.S. Government data)
- **Tree Equity Score**: Check American Forests terms

All analyses are for research and educational purposes.

## ⚠️ Disclaimer

This project uses public data sources for research purposes. Findings should not be used as the sole basis for public health or investment decisions. Consult with domain experts for policy or financial decisions.

## 📧 Contact

Questions or suggestions? Feel free to reach out or open an issue.

## 🙏 Acknowledgments

- **Zillow Research**: For comprehensive housing market data
- **CDC**: For public health data through the PLACES program
- **American Forests**: For Tree Equity Score methodology and data
- **U.S. Census Bureau**: For geographic boundaries and demographic data

---

**Last Updated**: March 2026
**Status**: Active Development
**Version**: 1.0
