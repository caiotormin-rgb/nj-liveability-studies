"""
config.py – Central configuration for the NJ Municipality Data Pipeline.

All paths, API settings, and geographic constants live here.
"""
from pathlib import Path
from dotenv import load_dotenv
import os

# ── Load .env ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# ── Paths ──────────────────────────────────────────────────────────────────
DATA_DIR       = BASE_DIR / "data"
RAW_DIR        = DATA_DIR / "raw"
PROCESSED_DIR  = DATA_DIR / "processed"
DB_PATH        = str(DATA_DIR / "db" / "nj_pipeline.duckdb")

# Ensure directories exist
for d in [RAW_DIR, PROCESSED_DIR, DATA_DIR / "db"]:
    d.mkdir(parents=True, exist_ok=True)

# ── API Keys ───────────────────────────────────────────────────────────────
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY", "")
BLS_API_KEY    = os.getenv("BLS_API_KEY", "")
FBI_API_KEY    = os.getenv("FBI_API_KEY", "")
HUD_API_KEY    = os.getenv("HUD_API_KEY", "")
NOAA_API_KEY   = os.getenv("NOAA_API_KEY", "")

# ── Geographic Constants ───────────────────────────────────────────────────
NJ_FIPS           = "34"           # New Jersey state FIPS code
NJ_STATE_NAME     = "New Jersey"

# BLS prefix for NJ county LAUS series
NJ_BLS_COUNTY_PREFIX = f"LAUCN{NJ_FIPS}"

# ── Census ACS Configuration ───────────────────────────────────────────────
# Years for which to pull 5-year ACS estimates (2012 = 2008-2012 window, etc.)
ACS_YEARS = list(range(2012, 2024))   # 2012 – 2023 (2024 data not yet released)

# Key ACS variable groups to fetch
# Format: { short_name: (census_variable_id, label) }
ACS_VARIABLES = {
    # ── Population & Demographics ──────────────────────────────────────────
    "pop_total":          ("B01003_001E", "Total Population"),
    "age_median":         ("B01002_001E", "Median Age"),
    "race_white":         ("B02001_002E", "Population White Alone"),
    "race_black":         ("B02001_003E", "Population Black Alone"),
    "race_asian":         ("B02001_005E", "Population Asian Alone"),
    "race_hispanic":      ("B03003_003E", "Population Hispanic/Latino"),
    "households":         ("B11001_001E", "Total Households"),
    "avg_household_size": ("B25010_001E", "Average Household Size"),

    # ── Economics ──────────────────────────────────────────────────────────
    "income_median_hh":   ("B19013_001E", "Median Household Income ($)"),
    "income_per_capita":  ("B19301_001E", "Per Capita Income ($)"),
    "poverty_count":      ("B17001_002E", "Population Below Poverty Level"),
    "poverty_universe":   ("B17001_001E", "Poverty Universe (total)"),
    "gini_index":         ("B19083_001E", "Gini Index of Income Inequality"),

    # ── Housing ────────────────────────────────────────────────────────────
    "housing_units_total":    ("B25001_001E", "Total Housing Units"),
    "housing_occupied":       ("B25002_002E", "Occupied Housing Units"),
    "housing_vacant":         ("B25002_003E", "Vacant Housing Units"),
    "housing_owner_occ":      ("B25003_002E", "Owner-Occupied Units"),
    "housing_renter_occ":     ("B25003_003E", "Renter-Occupied Units"),
    "home_value_median":      ("B25077_001E", "Median Owner-Occupied Home Value ($)"),
    "gross_rent_median":      ("B25064_001E", "Median Gross Rent ($/mo)"),
    "rent_burden_30_34pct":   ("B25070_007E", "Renters Paying 30-34.9% Income on Rent"),
    "rent_burden_35_39pct":   ("B25070_008E", "Renters Paying 35-39.9% Income on Rent"),
    "rent_burden_40_49pct":   ("B25070_009E", "Renters Paying 40-49.9% Income on Rent"),
    "rent_burden_50plus_pct": ("B25070_010E", "Renters Paying 50%+ Income on Rent"),
    "rent_burden_universe":   ("B25070_001E", "Rent Burden Universe"),
    "gross_rent_pct_income":  ("B25071_001E", "Median Gross Rent as % of Household Income"),

    # ── Education ──────────────────────────────────────────────────────────
    "edu_total_25plus":   ("B15003_001E", "Population 25+"),
    "edu_hs_grad":        ("B15003_017E", "HS Diploma"),
    "edu_some_college":   ("B15003_019E", "Some College, No Degree"),
    "edu_associates":     ("B15003_021E", "Associate's Degree"),
    "edu_bachelors":      ("B15003_022E", "Bachelor's Degree"),
    "edu_masters":        ("B15003_023E", "Master's Degree"),
    "edu_professional":   ("B15003_024E", "Professional Degree"),
    "edu_doctorate":      ("B15003_025E", "Doctorate Degree"),

    # ── Employment & Commuting ─────────────────────────────────────────────
    "labor_force":           ("B23025_002E", "In Labor Force"),
    "employed":              ("B23025_004E", "Employed"),
    "unemployed":            ("B23025_005E", "Unemployed"),
    "labor_force_universe":  ("B23025_001E", "Population 16+ (Labor Force Universe)"),
    "commute_total":         ("B08301_001E", "Workers 16+ (Commute Universe)"),
    "commute_car_alone":     ("B08301_003E", "Commute: Drive Alone"),
    "commute_carpool":       ("B08301_004E", "Commute: Carpool"),
    "commute_transit":       ("B08301_010E", "Commute: Public Transit"),
    "commute_wfh":           ("B08301_021E", "Work From Home"),
    "travel_time_aggregate": ("B08013_001E", "Aggregate Travel Time to Work (minutes)"),
    "travel_time_universe":  ("B08303_001E", "Travel Time Universe (workers)"),
}

# ── Zillow URLs ────────────────────────────────────────────────────────────
# These are the stable Zillow research CSV download paths (as of 2025).
# If they break, check https://www.zillow.com/research/data/
ZILLOW_URLS = {
    # ZHVI: All homes (SFR + condo), smoothed, seasonally adjusted, monthly
    "zhvi_all_homes": (
        "https://files.zillowstatic.com/research/public_csvs/zhvi/"
        "Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
    ),
    # ZHVI: Single-family only
    "zhvi_sfr": (
        "https://files.zillowstatic.com/research/public_csvs/zhvi/"
        "Zip_zhvi_uc_sfr_tier_0.33_0.67_sm_sa_month.csv"
    ),
    # ZORI: Observed rent index, all homes, smoothed, monthly
    "zori_all_homes": (
        "https://files.zillowstatic.com/research/public_csvs/zori/"
        "Zip_zori_uc_sfrcondomfr_sm_month.csv"
    ),
    # ZHVI: Bottom tier (affordable segment)
    "zhvi_bottom_tier": (
        "https://files.zillowstatic.com/research/public_csvs/zhvi/"
        "Zip_zhvi_uc_sfrcondo_tier_0.0_0.33_sm_sa_month.csv"
    ),
    # ZHVI: Top tier (luxury segment)
    "zhvi_top_tier": (
        "https://files.zillowstatic.com/research/public_csvs/zhvi/"
        "Zip_zhvi_uc_sfrcondo_tier_0.67_1.0_sm_sa_month.csv"
    ),
    # NOTE: days_to_pending and sale_to_list URLs were removed — both return
    # HTTP 404 as of 2026-03. Check https://www.zillow.com/research/data/
    # for updated file paths, then add them back here with keys
    # "days_to_pending" and "sale_to_list".
}

# ── NJ FIPS → County Name mapping ─────────────────────────────────────────
NJ_COUNTY_FIPS = {
    "001": "Atlantic",
    "003": "Bergen",
    "005": "Burlington",
    "007": "Camden",
    "009": "Cape May",
    "011": "Cumberland",
    "013": "Essex",
    "015": "Gloucester",
    "017": "Hudson",
    "019": "Hunterdon",
    "021": "Mercer",
    "023": "Middlesex",
    "025": "Monmouth",
    "027": "Morris",
    "029": "Ocean",
    "031": "Passaic",
    "033": "Salem",
    "035": "Somerset",
    "037": "Sussex",
    "039": "Union",
    "041": "Warren",
}

# ── CDC PLACES Socrata endpoint ────────────────────────────────────────────
# ZCTA-level health metrics (2024 release covers 2021 BRFSS data)
CDC_PLACES_ZCTA_ENDPOINT = "https://data.cdc.gov/resource/qnzd-25i4.json"
CDC_PLACES_PLACE_ENDPOINT = "https://data.cdc.gov/resource/eav7-hnsx.json"

# Which health measures to pull (measureid values)
CDC_HEALTH_MEASURES = [
    "ACCESS2",   # Lack of health insurance
    "ARTHRITIS", # Arthritis
    "BPHIGH",    # High blood pressure
    "CANCER",    # Cancer (excluding skin)
    "CASTHMA",   # Current asthma
    "CHD",       # Coronary heart disease
    "CHECKUP",   # Annual checkup (preventive care)
    "CHOLSCREEN",# Cholesterol screening
    "COPD",      # COPD
    "CSMOKING",  # Current smoking
    "DENTAL",    # Dental visit
    "DEPRESSION",# Depression
    "DIABETES",  # Diabetes
    "GHLTH",     # General health (fair/poor)
    "HIGHCHOL",  # High cholesterol
    "KIDNEY",    # Chronic kidney disease
    "LPA",       # Physical inactivity
    "MHLTH",     # Mental health (poor ≥14 days)
    "OBESITY",   # Obesity
    "PHLTH",     # Physical health (poor ≥14 days)
    "SLEEP",     # Sleep <7 hours
    "STROKE",    # Stroke
    "TEETHLOST", # All teeth lost
]

# ── BLS LAUS Series configuration ─────────────────────────────────────────
# Series codes for NJ counties (34 = NJ FIPS)
# Format: LAUCN{state2}{county3}{measure2}
# Measures: 03=unemployment rate, 04=unemployment, 05=employment, 06=labor force
BLS_LAUS_MEASURES = {
    "03": "unemployment_rate",
    "04": "unemployment_count",
    "05": "employment_count",
    "06": "labor_force",
}

# ── FBI CDE API ────────────────────────────────────────────────────────────
FBI_API_BASE = "https://api.usa.gov/crime/fbi/sapi"
FBI_CRIME_YEARS = list(range(2010, 2023))  # Available years

# ── FEMA OpenFEMA ──────────────────────────────────────────────────────────
FEMA_API_BASE = "https://www.fema.gov/api/open/v2"

# ── HUD CHAS ───────────────────────────────────────────────────────────────
HUD_API_BASE = "https://www.huduser.gov/hudapi/public"
# Available CHAS years (5-year ACS windows)
HUD_CHAS_YEARS = ["2015-2019", "2016-2020", "2017-2021", "2018-2022"]

# ── Logging ────────────────────────────────────────────────────────────────
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
