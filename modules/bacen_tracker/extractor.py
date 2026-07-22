"""
Funções de extração das séries temporais do Banco Central (SGS).

Endpoint: /dados/serie/bcdata.sgs.{codigo}/dados/ultimos/{n}?formato=json
"""

from typing import Optional

import requests

from .config import BASE_URL, HEADERS, REQUEST_TIMEOUT, SERIES, ULTIMOS_N


def _get_json(url: str) -> Optional[list]:
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na requisição a {url}: {e}")
        return None


def get_serie(codigo: int, nome: str, ultimos: int = ULTIMOS_N) -> list[dict]:
    """Retorna os últimos N pontos de uma série SGS, já rotulados."""
    url = f"{BASE_URL.format(codigo=codigo)}/ultimos/{ultimos}?formato=json"
    dados = _get_json(url)
    if not dados:
        return []

    for ponto in dados:
        ponto["serie"] = nome
        ponto["codigoSgs"] = codigo

    return dados


def get_todas_series() -> list[dict]:
    """Coleta todas as séries configuradas em SERIES e retorna uma lista plana."""
    todos_pontos: list[dict] = []
    for codigo, nome in SERIES.items():
        print(f"[bacen_tracker] Buscando série {nome} (SGS {codigo})...")
        pontos = get_serie(codigo, nome)
        print(f"[bacen_tracker] {nome}: {len(pontos)} pontos")
        todos_pontos.extend(pontos)
    return todos_pontos
