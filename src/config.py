from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"
PROCESSED_DIR = DATA_DIR / "processed"
MASTER_DATA_DIR = DATA_DIR / "master_data"
OUTPUT_DIR = BASE_DIR / "output"

for path in [RAW_DIR, STAGING_DIR, PROCESSED_DIR, MASTER_DATA_DIR, OUTPUT_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Time settings
START_DATE = "2023-01-01"
PERIODS = 36
FREQ = "MS"  # Month Start

# Business structure
ENTITIES = ["Canada", "USA", "UK"]
REGIONS = ["West", "Central", "East", "International"]
DEPARTMENTS = ["Sales", "Marketing", "Operations", "G&A", "Technology"]
PRODUCTS = ["Core", "Plus", "Enterprise"]
CUSTOMER_SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]

# Revenue base assumptions by entity
ENTITY_REVENUE_MULTIPLIER = {
    "Canada": 1.00,
    "USA": 1.35,
    "UK": 0.85,
}

# Regional mix
REGION_REVENUE_MULTIPLIER = {
    "West": 1.15,
    "Central": 1.00,
    "East": 0.95,
    "International": 0.80,
}

# Product mix
PRODUCT_PRICE = {
    "Core": 120,
    "Plus": 220,
    "Enterprise": 420,
}

PRODUCT_COST_RATIO = {
    "Core": 0.42,
    "Plus": 0.38,
    "Enterprise": 0.34,
}

SEGMENT_VOLUME_MULTIPLIER = {
    "SMB": 1.30,
    "Mid-Market": 1.00,
    "Enterprise": 0.70,
}

DEPARTMENT_OPEX_BASE = {
    "Sales": 90000,
    "Marketing": 65000,
    "Operations": 120000,
    "G&A": 50000,
    "Technology": 110000,
}

DEPARTMENT_HEADCOUNT_BASE = {
    "Sales": 12,
    "Marketing": 7,
    "Operations": 16,
    "G&A": 5,
    "Technology": 10,
}

# DuckDB file path
DUCKDB_PATH = BASE_DIR / "enterprise_fpna.duckdb"

# SQL directories
SQL_SCHEMA_DIR = BASE_DIR / "sql" / "schema"
SQL_VIEWS_DIR = BASE_DIR / "sql" / "views"
SQL_QA_DIR = BASE_DIR / "sql" / "qa"