"""
Coleta dados socioeconômicos do IBGE e persiste em disco local, em
snapshots JSON versionados por data — mesmo padrão usado pelo
civic_framework.collector, senado_tracker, bacen_tracker e siconfi_tracker.

Formato: data/raw/ibge/<recurso>/<YYYYMMDD>.json
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .extractor import get_todas_tabelas, get_estados

log = logging.getLogger(__name__)

RAW_DATA_ROOT = Path(__file__).parent.parent.parent / "data" / "raw"
BASE_PATH = RAW_DATA_ROOT / "ibge"


def _today() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%d")


def _salvar_snapshot(recurso: str, dados: list[dict], inicio: datetime) -> Path:
    duracao_ms = int((datetime.now(tz=timezone.utc) - inicio).total_seconds() * 1000)
    payload = {
        "_meta": {
            "recurso": recurso,
            "fonte": "ibge",
            "coletado_em": inicio.isoformat(),
            "duracao_ms": duracao_ms,
            "total_registros": len(dados),
            "versao_schema": "1.0",
        },
        "dados": dados,
    }

    destino = BASE_PATH / recurso
    destino.mkdir(parents=True, exist_ok=True)
    arquivo = destino / f"{_today()}.json"

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    log.info(f"[ibge] {recurso}: {len(dados)} registros → {arquivo}")
    return arquivo


def collect_indicadores_uf() -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    registros = get_todas_tabelas()
    if registros:
        _salvar_snapshot("indicadores_uf", registros, inicio)
    return registros


def collect_estados() -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    estados = get_estados()
    if estados:
        _salvar_snapshot("estados", estados, inicio)
    return estados


def collect_all() -> dict:
    """Coleta indicadores socioeconômicos por UF + catálogo de estados."""
    resultado = {}

    indicadores = collect_indicadores_uf()
    resultado["indicadores_uf"] = len(indicadores)

    estados = collect_estados()
    resultado["estados"] = len(estados)

    return resultado


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    print("\n📊 IBGE Tracker — Coleta de Dados Socioeconômicos")
    print("─" * 45)

    resultado = collect_all()

    print("\n── Resultado da Coleta ──")
    for recurso, total in resultado.items():
        print(f"  {'✅' if total > 0 else '⚠️ '} {recurso}: {total} registros")
    print(f"\nSalvo em: {BASE_PATH}")
