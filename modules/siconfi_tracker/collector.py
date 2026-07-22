"""
Coleta dados fiscais do SICONFI e persiste em disco local, em snapshots
JSON versionados por data — mesmo padrão usado pelo civic_framework.collector,
senado_tracker e bacen_tracker.

Formato: data/raw/siconfi/<recurso>/<YYYYMMDD>.json
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .config import ANO_EXERCICIO, ENTES
from .extractor import get_entes, get_dca_todos_entes

log = logging.getLogger(__name__)

RAW_DATA_ROOT = Path(__file__).parent.parent.parent / "data" / "raw"
BASE_PATH = RAW_DATA_ROOT / "siconfi"


def _today() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%d")


def _salvar_snapshot(recurso: str, dados: list[dict], inicio: datetime) -> Path:
    duracao_ms = int((datetime.now(tz=timezone.utc) - inicio).total_seconds() * 1000)
    payload = {
        "_meta": {
            "recurso": recurso,
            "fonte": "siconfi",
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

    log.info(f"[siconfi] {recurso}: {len(dados)} registros → {arquivo}")
    return arquivo


def collect_entes(an_exercicio: int = ANO_EXERCICIO) -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    entes = get_entes(an_exercicio)
    if entes:
        _salvar_snapshot("entes", entes, inicio)
    return entes


def collect_dca(an_exercicio: int = ANO_EXERCICIO) -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    dca = get_dca_todos_entes(ENTES, an_exercicio)
    if dca:
        _salvar_snapshot("dca", dca, inicio)
    return dca


def collect_all(an_exercicio: int = ANO_EXERCICIO) -> dict:
    """Coleta catálogo de entes + balanço (DCA) da União e estados. Retorna {recurso: total}."""
    resultado = {}

    entes = collect_entes(an_exercicio)
    resultado["entes"] = len(entes)

    dca = collect_dca(an_exercicio)
    resultado["dca"] = len(dca)

    return resultado


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Coleta dados fiscais do SICONFI")
    parser.add_argument("--ano", type=int, default=ANO_EXERCICIO, help="Ano de exercício do balanço")
    args = parser.parse_args()

    print("\n💵 SICONFI Tracker — Coleta de Finanças Públicas")
    print("─" * 45)

    resultado = collect_all(an_exercicio=args.ano)

    print("\n── Resultado da Coleta ──")
    for recurso, total in resultado.items():
        print(f"  {'✅' if total > 0 else '⚠️ '} {recurso}: {total} registros")
    print(f"\nSalvo em: {BASE_PATH}")
