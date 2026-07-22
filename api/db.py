"""
Acesso ao warehouse DuckDB. Cada requisição abre sua própria conexão
somente-leitura (barato no DuckDB — apenas mapeia o arquivo) para não
compartilhar estado entre requisições concorrentes.
"""

import math
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

WAREHOUSE_PATH = Path(__file__).parent.parent / "data" / "warehouse" / "camara_analytics.duckdb"


def get_connection() -> duckdb.DuckDBPyConnection:
    if not WAREHOUSE_PATH.exists():
        raise FileNotFoundError(
            f"Warehouse não encontrado em {WAREHOUSE_PATH}. "
            "Rode: poetry run python -m etl.build_warehouse"
        )
    return duckdb.connect(str(WAREHOUSE_PATH), read_only=True)


def _limpar_valor(v: Any) -> Any:
    if isinstance(v, float) and math.isnan(v):
        return None
    if pd.isna(v):
        return None
    if isinstance(v, pd.Timestamp):
        return v.isoformat() if not pd.isna(v) else None
    return v


def query(sql: str, params: list | None = None) -> list[dict]:
    """Executa uma query e retorna uma lista de dicts, JSON-safe."""
    con = get_connection()
    try:
        df = con.execute(sql, params or []).fetchdf()
    finally:
        con.close()

    registros = df.to_dict(orient="records")
    return [{k: _limpar_valor(v) for k, v in reg.items()} for reg in registros]


def query_one(sql: str, params: list | None = None) -> dict | None:
    registros = query(sql, params)
    return registros[0] if registros else None
