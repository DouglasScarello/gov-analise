"""
Coleta contratações públicas federais (Compras.gov.br / PNCP) e persiste em
disco local, em snapshots JSON versionados por data — mesmo padrão usado
pelo civic_framework.collector e demais trackers do projeto.

Formato: data/raw/compras/<recurso>/<YYYYMMDD>.json
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .extractor import get_todas_contratacoes

log = logging.getLogger(__name__)

RAW_DATA_ROOT = Path(__file__).parent.parent.parent / "data" / "raw"
BASE_PATH = RAW_DATA_ROOT / "compras"


def _today() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%d")


def _salvar_snapshot(recurso: str, dados: list[dict], inicio: datetime) -> Path:
    duracao_ms = int((datetime.now(tz=timezone.utc) - inicio).total_seconds() * 1000)
    payload = {
        "_meta": {
            "recurso": recurso,
            "fonte": "compras",
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

    log.info(f"[compras] {recurso}: {len(dados)} registros → {arquivo}")
    return arquivo


def collect_contratacoes() -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    registros = get_todas_contratacoes()
    if registros:
        _salvar_snapshot("contratacoes", registros, inicio)
    return registros


def collect_all() -> dict:
    """Coleta contratações públicas federais. Retorna {recurso: total}."""
    registros = collect_contratacoes()
    return {"contratacoes": len(registros)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    print("\n🏢 Compras Tracker — Coleta de Contratações Públicas Federais")
    print("─" * 45)

    resultado = collect_all()

    print("\n── Resultado da Coleta ──")
    for recurso, total in resultado.items():
        print(f"  {'✅' if total > 0 else '⚠️ '} {recurso}: {total} registros")
    print(f"\nSalvo em: {BASE_PATH}")
