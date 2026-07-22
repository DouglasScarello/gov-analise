"""
Coleta dados do Portal da Transparência e persiste em disco local, em
snapshots JSON versionados por data — mesmo padrão usado pelo
civic_framework.collector e demais trackers do projeto.

Formato: data/raw/transparencia/<recurso>/<YYYYMMDD>.json
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .config import PORTAL_TRANSPARENCIA_API_KEY
from .extractor import get_ceis, get_cnep, get_contratos_todos_orgaos, get_orgaos_siafi

log = logging.getLogger(__name__)

RAW_DATA_ROOT = Path(__file__).parent.parent.parent / "data" / "raw"
BASE_PATH = RAW_DATA_ROOT / "transparencia"


def _today() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%d")


def _salvar_snapshot(recurso: str, dados: list[dict], inicio: datetime) -> Path:
    duracao_ms = int((datetime.now(tz=timezone.utc) - inicio).total_seconds() * 1000)
    payload = {
        "_meta": {
            "recurso": recurso,
            "fonte": "transparencia",
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

    log.info(f"[transparencia] {recurso}: {len(dados)} registros → {arquivo}")
    return arquivo


def collect_ceis() -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    dados = get_ceis()
    if dados:
        _salvar_snapshot("ceis", dados, inicio)
    return dados


def collect_cnep() -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    dados = get_cnep()
    if dados:
        _salvar_snapshot("cnep", dados, inicio)
    return dados


def collect_contratos() -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    dados = get_contratos_todos_orgaos()
    if dados:
        _salvar_snapshot("contratos", dados, inicio)
    return dados


def collect_orgaos() -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    dados = get_orgaos_siafi()
    if dados:
        _salvar_snapshot("orgaos_siafi", dados, inicio)
    return dados


def collect_all() -> dict:
    """Coleta CEIS, CNEP, contratos (amostra de órgãos) e catálogo de órgãos."""
    if not PORTAL_TRANSPARENCIA_API_KEY:
        print("[ERRO] PORTAL_TRANSPARENCIA_API_KEY não configurada no .env — abortando coleta.")
        return {}

    resultado = {}
    resultado["ceis"] = len(collect_ceis())
    resultado["cnep"] = len(collect_cnep())
    resultado["contratos"] = len(collect_contratos())
    resultado["orgaos_siafi"] = len(collect_orgaos())
    return resultado


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    print("\n🔎 Transparência Tracker — Coleta do Portal da Transparência")
    print("─" * 45)

    resultado = collect_all()

    print("\n── Resultado da Coleta ──")
    for recurso, total in resultado.items():
        print(f"  {'✅' if total > 0 else '⚠️ '} {recurso}: {total} registros")
    print(f"\nSalvo em: {BASE_PATH}")
