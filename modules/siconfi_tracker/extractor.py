"""
Funções de extração de dados fiscais do SICONFI (Tesouro Nacional).

Endpoints usados:
- /entes                → catálogo de entes federativos (municípios/estados/União)
- /dca?an_exercicio=&id_ente=  → Declaração de Contas Anuais (balanço patrimonial consolidado)
"""

import time
from typing import Optional

import requests

from .config import BASE_URL, HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY, ANO_EXERCICIO, ENTES


def _get_json(url: str, params: Optional[dict] = None) -> Optional[dict]:
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na requisição a {url}: {e}")
        return None


def get_entes(an_exercicio: int = ANO_EXERCICIO) -> list[dict]:
    """Retorna o catálogo de entes federativos (municípios, estados, União)."""
    print(f"[siconfi_tracker] Buscando catálogo de entes ({an_exercicio})...")
    data = _get_json(f"{BASE_URL}/entes", params={"an_exercicio": an_exercicio})
    if not data:
        return []
    itens = data.get("items", [])
    print(f"[siconfi_tracker] {len(itens)} entes encontrados.")
    return itens


def get_dca_ente(id_ente: int, sigla: str, an_exercicio: int = ANO_EXERCICIO) -> list[dict]:
    """Retorna a Declaração de Contas Anuais (balanço) de um ente específico."""
    data = _get_json(
        f"{BASE_URL}/dca",
        params={"an_exercicio": an_exercicio, "id_ente": id_ente},
    )
    if not data:
        return []
    itens = data.get("items", [])
    for item in itens:
        item["_siglaEnte"] = sigla
    return itens


def get_dca_todos_entes(entes: dict = ENTES, an_exercicio: int = ANO_EXERCICIO) -> list[dict]:
    """Coleta o DCA (balanço patrimonial) da União + todos os estados configurados."""
    todos: list[dict] = []
    total = len(entes)

    for i, (id_ente, sigla) in enumerate(entes.items(), start=1):
        print(f"[siconfi_tracker] DCA {i}/{total} ({sigla})...")
        itens = get_dca_ente(id_ente, sigla, an_exercicio)
        todos.extend(itens)
        time.sleep(REQUEST_DELAY)

    print(f"[siconfi_tracker] Total de linhas de balanço coletadas: {len(todos)}")
    return todos
