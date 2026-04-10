import duckdb
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import urllib.request
import zipfile
import os

DB_PATH = '../data/db/nj_pipeline.duckdb'
con = duckdb.connect(DB_PATH, read_only=True)
print('Connected to DuckDB')

qol_scores = con.execute("SELECT zip_code, qol_score, qol_rank, city, zillow_county FROM qol_scores").df()
print(f"Loaded {len(qol_scores)} QoL scores")

shapefile_dir = '../data/raw/shapefiles'
os.makedirs(shapefile_dir, exist_ok=True)
zip_path = os.path.join(shapefile_dir, 'cb_2020_us_zcta520_500k.zip')

if not os.path.exists(zip_path):
    print("Downloading ZCTA shapefile...")
    url = "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
            out_file.write(response.read())
        print("Download complete.")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(shapefile_dir)
    except Exception as e:
        print(f"Error downloading: {e}")

print("Loading ZCTA shapefile...")
gdf = gpd.read_file(os.path.join(shapefile_dir, 'cb_2020_us_zcta520_500k.shp'))
gdf = gdf.rename(columns={'ZCTA5CE20': 'zip_code'})

nj_gdf = gdf.merge(qol_scores, on='zip_code', how='inner')
print(f"Merged GeoDataFrame has {len(nj_gdf)} rows")

fig, ax = plt.subplots(1, 1, figsize=(12, 16))
nj_gdf.plot(column='qol_score', 
            cmap='RdYlGn', 
            linewidth=0.5, 
            ax=ax, 
            edgecolor='0.5', 
            legend=True, 
            legend_kwds={'label': "Quality of Life Score (0-100)", 'orientation': "vertical", 'shrink': 0.6})

ax.set_title("New Jersey Quality of Life Index by ZIP Code", fontsize=16)
ax.axis('off')

top_zips = nj_gdf.nlargest(10, 'qol_score')
for idx, row in top_zips.iterrows():
    x = row.geometry.centroid.x
    y = row.geometry.centroid.y
    plt.annotate(text=row['city'], xy=(x, y), 
                 xytext=(3, 3), textcoords="offset points", fontsize=8, color='black', weight='bold',
                 path_effects=[pe.withStroke(linewidth=2, foreground="white")])

plt.tight_layout()
os.makedirs('../NJ_Analysis_Vault/EDA Findings', exist_ok=True)
plt.savefig('../NJ_Analysis_Vault/EDA Findings/qol_map.png', dpi=300, bbox_inches='tight')
print("Map saved to ../NJ_Analysis_Vault/EDA Findings/qol_map.png")
