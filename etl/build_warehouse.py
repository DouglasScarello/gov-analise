"""
Orquestra a camada de ETL: carrega os snapshots brutos de cada fonte,
limpa/normaliza, cruza o que é possível entre fontes, e grava tudo em
um único banco DuckDB.

Uso: poetry run python -m etl.build_warehouse
"""

import logging
import time

import duckdb
import pandas as pd

from . import clean
from .config import WAREHOUSE_DIR, WAREHOUSE_PATH
from .loaders import carregar_recurso_json, carregar_recurso_parquet
from .unify import (
    unificar_contratos_publicos,
    unificar_entidades_sancionadas,
    unificar_pessoas_politicas,
    unificar_tse_candidatos_geral,
)

# Anos de eleição geral (presidente/governador/senador/deputado) já coletados.
ANOS_ELEICAO_GERAL = [1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022]

# Anos de eleição municipal (prefeito/vice-prefeito/vereador) já coletados.
# 2024 é o recurso "candidatos" (default, sem sufixo de ano).
ANOS_ELEICAO_MUNICIPAL = [1996, 2000, 2004, 2008, 2012, 2016, 2020]

log = logging.getLogger(__name__)

# (fonte, recurso, tipo_arquivo, função_de_limpeza) -> nome da tabela staging
FONTES_JSON = [
    ("camara", "deputados", clean.limpar_camara_deputados),
    ("camara", "legislaturas", clean.limpar_camara_legislaturas),
    ("senado", "senadores", clean.limpar_senado_senadores),
    ("senado", "legislaturas", clean.limpar_senado_legislaturas),
    ("senado", "processos", clean.limpar_senado_processos),
    ("senado", "votacoes", clean.limpar_senado_votacoes),
    ("bacen", "series", clean.limpar_bacen_series),
    ("siconfi", "entes", clean.limpar_siconfi_entes),
    ("siconfi", "dca", clean.limpar_siconfi_dca),
    ("ibge", "indicadores_uf", clean.limpar_ibge_indicadores),
    ("compras", "contratacoes", clean.limpar_compras_contratacoes),
    ("datajud", "processos", clean.limpar_datajud_processos),
    ("transparencia", "ceis", clean.limpar_transparencia_sancoes),
    ("transparencia", "cnep", clean.limpar_transparencia_sancoes),
    ("transparencia", "contratos", clean.limpar_transparencia_contratos),
    ("transparencia", "orgaos_siafi", clean.limpar_transparencia_orgaos),
]

FONTES_PARQUET = [
    ("tse", "candidatos", clean.limpar_tse_candidatos),
] + [
    ("tse", f"candidatos_{ano}", clean.limpar_tse_candidatos) for ano in ANOS_ELEICAO_GERAL
] + [
    ("tse", f"candidatos_{ano}", clean.limpar_tse_candidatos) for ano in ANOS_ELEICAO_MUNICIPAL
]


def _gravar_tabela(con: duckdb.DuckDBPyConnection, nome: str, df: pd.DataFrame) -> int:
    if df.empty:
        log.warning(f"[etl] {nome}: sem dados, tabela não criada")
        return 0
    con.register("tmp_df", df)
    con.execute(f"CREATE OR REPLACE TABLE {nome} AS SELECT * FROM tmp_df")
    con.unregister("tmp_df")
    return len(df)


def build() -> dict:
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(WAREHOUSE_PATH))
    resultado: dict[str, int] = {}
    staging: dict[str, pd.DataFrame] = {}

    for fonte, recurso, limpar in FONTES_JSON:
        bruto = carregar_recurso_json(fonte, recurso)
        limpo = limpar(bruto)
        nome_tabela = f"stg_{fonte}_{recurso}"
        resultado[nome_tabela] = _gravar_tabela(con, nome_tabela, limpo)
        staging[f"{fonte}_{recurso}"] = limpo

    for fonte, recurso, limpar in FONTES_PARQUET:
        bruto = carregar_recurso_parquet(fonte, recurso)
        limpo = limpar(bruto)
        nome_tabela = f"stg_{fonte}_{recurso}"
        resultado[nome_tabela] = _gravar_tabela(con, nome_tabela, limpo)
        staging[f"{fonte}_{recurso}"] = limpo

    # ── Tabelas unificadas ──────────────────────────────────────
    geral = unificar_tse_candidatos_geral(
        [staging.get(f"tse_candidatos_{ano}", pd.DataFrame()) for ano in ANOS_ELEICAO_GERAL]
    )
    resultado["stg_tse_candidatos_geral"] = _gravar_tabela(con, "stg_tse_candidatos_geral", geral)

    municipal_geral = unificar_tse_candidatos_geral(
        [staging.get("tse_candidatos", pd.DataFrame())]
        + [staging.get(f"tse_candidatos_{ano}", pd.DataFrame()) for ano in ANOS_ELEICAO_MUNICIPAL]
    )
    resultado["stg_tse_candidatos_municipal_geral"] = _gravar_tabela(
        con, "stg_tse_candidatos_municipal_geral", municipal_geral
    )

    pessoas = unificar_pessoas_politicas(
        staging.get("camara_deputados", pd.DataFrame()),
        staging.get("senado_senadores", pd.DataFrame()),
    )
    resultado["pessoas_politicas"] = _gravar_tabela(con, "pessoas_politicas", pessoas)

    sancoes = unificar_entidades_sancionadas(
        staging.get("transparencia_ceis", pd.DataFrame()),
        staging.get("transparencia_cnep", pd.DataFrame()),
    )
    resultado["entidades_sancionadas"] = _gravar_tabela(con, "entidades_sancionadas", sancoes)

    contratos = unificar_contratos_publicos(
        staging.get("compras_contratacoes", pd.DataFrame()),
        staging.get("transparencia_contratos", pd.DataFrame()),
    )
    resultado["contratos_publicos"] = _gravar_tabela(con, "contratos_publicos", contratos)

    con.close()
    return resultado


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    print("\n🗄️  ETL — Construindo o warehouse unificado")
    print("─" * 50)

    inicio = time.time()
    resultado = build()
    duracao = time.time() - inicio

    print("\n── Tabelas gravadas ──")
    for tabela, total in resultado.items():
        print(f"  {'✅' if total > 0 else '⚠️ '} {tabela}: {total} registros")

    print(f"\nConcluído em {duracao:.1f}s → {WAREHOUSE_PATH}")
