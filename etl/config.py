"""
Configurações centrais da camada de ETL.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_ROOT = PROJECT_ROOT / "data" / "raw"
WAREHOUSE_DIR = PROJECT_ROOT / "data" / "warehouse"
WAREHOUSE_PATH = WAREHOUSE_DIR / "camara_analytics.duckdb"
