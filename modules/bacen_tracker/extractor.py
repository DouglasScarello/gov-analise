"""
Funções de extração das séries temporais do Banco Central (SGS).

Dois endpoints:
- /dados/serie/bcdata.sgs.{codigo}/dados/ultimos/{n}?formato=json — só os
  últimos N pontos (máx. 20), usado como fallback rápido.
- /dados/serie/bcdata.sgs.{codigo}/dados?dataInicial=...&dataFinal=... —
  histórico por intervalo de datas, sem esse limite; é o usado por padrão.
"""

from datetime import datetime
from typing import Optional

import requests

from .config import ANOS_HISTORICO, BASE_URL, HEADERS, REQUEST_TIMEOUT, SERIES, ULTIMOS_N


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


def get_serie_historica(codigo: int, nome: str, anos: int = ANOS_HISTORICO) -> list[dict]:
    """Retorna o histórico de uma série SGS nos últimos `anos` anos, já rotulado."""
    hoje = datetime.now()
    data_final = hoje.strftime("%d/%m/%Y")
    data_inicial = hoje.replace(year=hoje.year - anos).strftime("%d/%m/%Y")

    url = f"{BASE_URL.format(codigo=codigo)}?formato=json&dataInicial={data_inicial}&dataFinal={data_final}"
    dados = _get_json(url)
    if not dados:
        return []

    for ponto in dados:
        ponto["serie"] = nome
        ponto["codigoSgs"] = codigo

    return dados


def get_todas_series(anos: int = ANOS_HISTORICO) -> list[dict]:
    """Coleta o histórico de todas as séries configuradas em SERIES e retorna uma lista plana."""
    todos_pontos: list[dict] = []
    for codigo, nome in SERIES.items():
        print(f"[bacen_tracker] Buscando {anos} anos de histórico de {nome} (SGS {codigo})...")
        pontos = get_serie_historica(codigo, nome, anos)
        print(f"[bacen_tracker] {nome}: {len(pontos)} pontos")
        todos_pontos.extend(pontos)
    return todos_pontos
