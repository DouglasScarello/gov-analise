"""
Coleta os dados abertos do Senado Federal e persiste em disco local,
em snapshots JSON versionados por data — mesmo padrão usado pelo
civic_framework.collector para os dados municipais.

Formato: data/raw/senado/<recurso>/<YYYYMMDD>.json
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .extractor import (
    get_autorias_todos_senadores,
    get_senadores_atuais,
    get_senadores_legislaturas,
    get_votacoes_todos_senadores,
    get_processos,
)

log = logging.getLogger(__name__)

RAW_DATA_ROOT = Path(__file__).parent.parent.parent / "data" / "raw"
BASE_PATH = RAW_DATA_ROOT / "senado"


def _today() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%d")


def _salvar_snapshot(recurso: str, dados: list[dict], inicio: datetime) -> Path:
    duracao_ms = int((datetime.now(tz=timezone.utc) - inicio).total_seconds() * 1000)
    payload = {
        "_meta": {
            "recurso": recurso,
            "fonte": "senado",
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

    log.info(f"[senado] {recurso}: {len(dados)} registros → {arquivo}")
    return arquivo


def collect_senadores() -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    senadores = get_senadores_atuais()
    if senadores:
        _salvar_snapshot("senadores", senadores, inicio)
    return senadores


def collect_processos(ano: int = None) -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    processos = get_processos(ano=ano)
    if processos:
        _salvar_snapshot("processos", processos, inicio)
    return processos


def collect_votacoes(senadores: list[dict]) -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    codigos = [s["id"] for s in senadores if s.get("id")]
    votacoes = get_votacoes_todos_senadores(codigos)
    if votacoes:
        _salvar_snapshot("votacoes", votacoes, inicio)
    return votacoes


def collect_autorias(senadores: list[dict]) -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    codigos = [s["id"] for s in senadores if s.get("id")]
    autorias = get_autorias_todos_senadores(codigos)
    if autorias:
        _salvar_snapshot("autorias", autorias, inicio)
    return autorias


def collect_legislaturas() -> list[dict]:
    inicio = datetime.now(tz=timezone.utc)
    registros = get_senadores_legislaturas()
    if registros:
        _salvar_snapshot("legislaturas", registros, inicio)
    return registros


def collect_all(incluir_votacoes: bool = True, ano: int = None) -> dict:
    """Coleta senadores, processos e (opcionalmente) votações. Retorna {recurso: total}."""
    resultado = {}

    senadores = collect_senadores()
    resultado["senadores"] = len(senadores)

    processos = collect_processos(ano=ano)
    resultado["processos"] = len(processos)

    if incluir_votacoes and senadores:
        votacoes = collect_votacoes(senadores)
        resultado["votacoes"] = len(votacoes)

    return resultado


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Coleta dados abertos do Senado Federal")
    parser.add_argument("--ano", type=int, default=None, help="Filtrar processos por ano")
    parser.add_argument(
        "--skip-votacoes",
        action="store_true",
        help="Pula a coleta de votações (mais lenta, ~81 requisições)",
    )
    args = parser.parse_args()

    print("\n🏛️  Senado Tracker — Coleta de Dados Abertos")
    print("─" * 45)

    resultado = collect_all(incluir_votacoes=not args.skip_votacoes, ano=args.ano)

    print("\n── Resultado da Coleta ──")
    for recurso, total in resultado.items():
        print(f"  {'✅' if total > 0 else '⚠️ '} {recurso}: {total} registros")
    print(f"\nSalvo em: {BASE_PATH}")
