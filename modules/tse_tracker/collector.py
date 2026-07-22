"""
Coleta dados eleitorais do TSE e persiste em disco local.

Diferente das demais fontes (JSON pequeno), o dataset de candidatos é grande
(~460 mil registros nacionais) — por isso é salvo em Parquet, seguindo o
padrão já usado pelo modules.tracker_gastos, ao invés do snapshot JSON.

Formato: data/raw/tse/<recurso>/<YYYYMMDD>.parquet + _meta.json
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .config import ANO_ELEICAO
from .extractor import get_candidatos

log = logging.getLogger(__name__)

RAW_DATA_ROOT = Path(__file__).parent.parent.parent / "data" / "raw"
BASE_PATH = RAW_DATA_ROOT / "tse"


def _today() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%d")


def _salvar_snapshot_parquet(recurso: str, registros: list[dict], inicio: datetime) -> Path:
    duracao_ms = int((datetime.now(tz=timezone.utc) - inicio).total_seconds() * 1000)
    destino = BASE_PATH / recurso
    destino.mkdir(parents=True, exist_ok=True)

    arquivo = destino / f"{_today()}.parquet"
    pd.DataFrame(registros).to_parquet(arquivo, index=False)

    meta = {
        "recurso": recurso,
        "fonte": "tse",
        "coletado_em": inicio.isoformat(),
        "duracao_ms": duracao_ms,
        "total_registros": len(registros),
        "versao_schema": "1.0",
        "arquivo": arquivo.name,
    }
    with open(destino / f"{_today()}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    log.info(f"[tse] {recurso}: {len(registros)} registros → {arquivo}")
    return arquivo


def collect_candidatos(ano: int = ANO_ELEICAO) -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    candidatos = get_candidatos(ano)
    if candidatos:
        _salvar_snapshot_parquet("candidatos", candidatos, inicio)
    return candidatos


def collect_all(ano: int = ANO_ELEICAO) -> dict:
    """Coleta candidatos do ano de eleição configurado. Retorna {recurso: total}."""
    candidatos = collect_candidatos(ano)
    return {"candidatos": len(candidatos)}


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Coleta dados eleitorais do TSE")
    parser.add_argument("--ano", type=int, default=ANO_ELEICAO, help="Ano da eleição")
    args = parser.parse_args()

    print("\n🗳️  TSE Tracker — Coleta de Dados Eleitorais")
    print("─" * 45)

    resultado = collect_all(ano=args.ano)

    print("\n── Resultado da Coleta ──")
    for recurso, total in resultado.items():
        print(f"  {'✅' if total > 0 else '⚠️ '} {recurso}: {total} registros")
    print(f"\nSalvo em: {BASE_PATH}")
