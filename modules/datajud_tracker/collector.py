"""
Coleta processos judiciais do CNJ DataJud e persiste em disco local, em
snapshots JSON versionados por data — mesmo padrão usado pelo
civic_framework.collector e demais trackers do projeto.

Formato: data/raw/datajud/<recurso>/<YYYYMMDD>.json
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .config import DATAJUD_API_KEY
from .extractor import get_todos_tribunais

log = logging.getLogger(__name__)

RAW_DATA_ROOT = Path(__file__).parent.parent.parent / "data" / "raw"
BASE_PATH = RAW_DATA_ROOT / "datajud"


def _today() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%d")


def _salvar_snapshot(recurso: str, dados: list[dict], inicio: datetime) -> Path:
    duracao_ms = int((datetime.now(tz=timezone.utc) - inicio).total_seconds() * 1000)
    payload = {
        "_meta": {
            "recurso": recurso,
            "fonte": "datajud",
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

    log.info(f"[datajud] {recurso}: {len(dados)} registros → {arquivo}")
    return arquivo


def collect_processos() -> list[dict]:
    if not DATAJUD_API_KEY:
        print("[ERRO] DATAJUD_API_KEY não configurada no .env — abortando coleta.")
        return []

    inicio = datetime.now(tz=timezone.utc)
    processos = get_todos_tribunais()
    if processos:
        _salvar_snapshot("processos", processos, inicio)
    return processos


def collect_all() -> dict:
    """Coleta amostra recente de processos dos tribunais configurados."""
    processos = collect_processos()
    return {"processos": len(processos)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    print("\n⚖️  DataJud Tracker — Coleta de Processos Judiciais")
    print("─" * 45)

    resultado = collect_all()

    print("\n── Resultado da Coleta ──")
    for recurso, total in resultado.items():
        print(f"  {'✅' if total > 0 else '⚠️ '} {recurso}: {total} registros")
    print(f"\nSalvo em: {BASE_PATH}")
