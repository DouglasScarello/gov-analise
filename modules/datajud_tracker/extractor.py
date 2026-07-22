"""
Funções de extração de processos judiciais via CNJ DataJud.

A API é um proxy Elasticsearch público por tribunal:
POST /api_publica_{tribunal}/_search  (Authorization: APIKey <chave>)

Cada tribunal é um índice isolado — não existe endpoint único "todos os
tribunais". Este extractor busca, por tribunal, os processos com
movimentação mais recente (ordenados por dataHoraUltimaAtualizacao desc).
"""

from typing import Optional

import requests

from .config import BASE_URL, HEADERS, REQUEST_TIMEOUT, TRIBUNAIS, TAMANHO_AMOSTRA


def _post_json(url: str, body: dict) -> Optional[dict]:
    try:
        response = requests.post(url, headers=HEADERS, json=body, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na requisição a {url}: {e}")
        return None


def get_processos_recentes_tribunal(sigla: str, nome: str, tamanho: int = TAMANHO_AMOSTRA) -> list[dict]:
    """Retorna os processos mais recentemente atualizados de um tribunal."""
    url = f"{BASE_URL}/api_publica_{sigla}/_search"
    body = {
        "size": tamanho,
        "sort": [{"dataHoraUltimaAtualizacao": {"order": "desc"}}],
        "query": {"match_all": {}},
    }

    data = _post_json(url, body)
    if not data:
        return []

    hits = data.get("hits", {}).get("hits", [])
    processos = []
    for hit in hits:
        fonte = hit.get("_source", {})
        fonte["_tribunalSigla"] = sigla.upper()
        fonte["_tribunalNome"] = nome
        processos.append(fonte)

    return processos


def get_todos_tribunais() -> list[dict]:
    """Coleta a amostra recente de todos os tribunais configurados em TRIBUNAIS."""
    todos: list[dict] = []
    for sigla, nome in TRIBUNAIS.items():
        print(f"[datajud_tracker] Buscando processos recentes de {nome} ({sigla.upper()})...")
        processos = get_processos_recentes_tribunal(sigla, nome)
        print(f"[datajud_tracker] {sigla.upper()}: {len(processos)} processos")
        todos.extend(processos)
    return todos
