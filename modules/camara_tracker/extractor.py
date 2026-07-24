"""
Funções de extração do registro de deputados da Câmara.

Endpoint: /deputados (lista paginada via HATEOAS)
"""

import time
from typing import Optional

import requests

from .config import BASE_URL, HEADERS, LEGISLATURAS, REQUEST_DELAY, REQUEST_TIMEOUT


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


def get_deputados_por_legislaturas(legislaturas: list[int] = LEGISLATURAS) -> list[dict]:
    """Retorna o registro de deputados (id, nome, partido, UF) de cada legislatura
    informada — permite montar o histórico de mandatos por pessoa.

    Busca uma legislatura por vez (uma consulta combinando todas sobrecarrega a
    API da Câmara e retorna 504)."""
    print(f"[camara_tracker] Buscando deputados das legislaturas {legislaturas}...")
    todos: list[dict] = []
    url = f"{BASE_URL}/deputados"

    for legislatura in legislaturas:
        params = {"idLegislatura": legislatura, "itens": 100, "ordem": "ASC", "ordenarPor": "nome", "pagina": 1}
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
        print(f"[camara_tracker] legislatura {legislatura}: {len(todos)} registros acumulados.")

    print(f"[camara_tracker] {len(todos)} registros de mandatos por legislatura encontrados.")
    return todos


def get_proposicoes_por_deputado(id_deputado: int) -> list[dict]:
    """Retorna as proposições (PL, PEC, PLP etc.) de autoria de um deputado,
    paginando via HATEOAS. Cobre toda a carreira do parlamentar, não só a
    legislatura atual."""
    todas: list[dict] = []
    params = {
        "idDeputadoAutor": id_deputado,
        "itens": 100,
        "ordem": "DESC",
        "ordenarPor": "id",
        "pagina": 1,
    }
    url = f"{BASE_URL}/proposicoes"

    while True:
        data = _get_json(url, params)
        if not data:
            break
        registros = data.get("dados", [])
        if not registros:
            break
        for r in registros:
            r["_idDeputadoAutor"] = id_deputado
        todas.extend(registros)

        links = data.get("links", [])
        if not any(link.get("rel") == "next" for link in links):
            break
        params["pagina"] += 1

    return todas


def get_proposicoes_todos_deputados(ids: list[int]) -> list[dict]:
    """Coleta proposições de autoria de uma lista de deputados, com pausa
    entre requisições. Pode levar alguns minutos para os ~513 deputados atuais."""
    todas: list[dict] = []
    total = len(ids)

    for i, id_deputado in enumerate(ids, start=1):
        proposicoes = get_proposicoes_por_deputado(id_deputado)
        todas.extend(proposicoes)
        if i % 50 == 0 or i == total:
            print(f"[camara_tracker] proposições {i}/{total} deputados ({len(todas)} acumuladas)...")
        time.sleep(REQUEST_DELAY)

    print(f"[camara_tracker] Total de proposições coletadas: {len(todas)}")
    return todas
