"""
Funções de extração do registro de deputados da Câmara.

Endpoint: /deputados (lista paginada via HATEOAS)
"""

from typing import Optional

import requests

from .config import BASE_URL, HEADERS, REQUEST_TIMEOUT


def _get_json(url: str, params: Optional[dict] = None) -> Optional[dict]:
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na requisição a {url}: {e}")
        return None


def get_deputados_atuais() -> list[dict]:
    """Retorna o registro completo de deputados em exercício, paginando via HATEOAS."""
    print("[camara_tracker] Buscando deputados em exercício...")
    todos: list[dict] = []
    params = {"itens": 100, "ordem": "ASC", "ordenarPor": "nome", "pagina": 1}
    url = f"{BASE_URL}/deputados"

    while True:
        data = _get_json(url, params)
        if not data:
            break
        registros = data.get("dados", [])
        if not registros:
            break
        todos.extend(registros)

        links = data.get("links", [])
        if not any(link.get("rel") == "next" for link in links):
            break
        params["pagina"] += 1

    print(f"[camara_tracker] {len(todos)} deputados encontrados.")
    return todos
