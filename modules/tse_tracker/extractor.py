"""
Funções de extração de dados eleitorais do TSE via catálogo CKAN.

Fluxo para "candidatos":
1. package_show(candidatos-<ano>) → lista de recursos (URLs de ZIPs por UF + Brasil)
2. baixa o ZIP do recurso consolidado nacional
3. extrai o CSV "_BRASIL" e carrega como DataFrame
"""

import io
import zipfile
from typing import Optional

import pandas as pd
import requests

from .config import (
    CKAN_BASE_URL,
    HEADERS,
    REQUEST_TIMEOUT,
    DOWNLOAD_TIMEOUT,
    PACOTE_CANDIDATOS,
    NOME_ARQUIVO_BRASIL,
    CSV_ENCODING,
    CSV_SEP,
)


def _get_json(url: str, params: Optional[dict] = None) -> Optional[dict]:
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na requisição a {url}: {e}")
        return None


def get_pacote(nome_pacote: str) -> Optional[dict]:
    """Retorna os metadados (incluindo lista de recursos) de um pacote CKAN."""
    data = _get_json(f"{CKAN_BASE_URL}/package_show", params={"id": nome_pacote})
    if not data or not data.get("success"):
        return None
    return data["result"]


def _url_recurso_brasil(pacote: dict) -> Optional[str]:
    """Encontra, entre os recursos do pacote, o ZIP de candidatos consolidado (Brasil)."""
    for recurso in pacote.get("resources", []):
        url = recurso.get("url", "")
        if url.endswith(".zip") and "consulta_cand_" in url and "fotos" not in url:
            return url
    return None


def get_candidatos(ano: int = None) -> list[dict]:
    """Baixa e extrai o CSV nacional de candidatos, retornando registros como dicts."""
    nome_pacote = PACOTE_CANDIDATOS if ano is None else f"candidatos-{ano}"
    nome_arquivo = NOME_ARQUIVO_BRASIL if ano is None else f"consulta_cand_{ano}_BRASIL.csv"

    print(f"[tse_tracker] Buscando pacote '{nome_pacote}' no catálogo CKAN...")
    pacote = get_pacote(nome_pacote)
    if not pacote and ano is not None:
        # Alguns anos (ex: 2020) foram publicados no catálogo com sufixo "-subtemas".
        nome_pacote_alt = f"candidatos-{ano}-subtemas"
        print(f"[tse_tracker] Pacote '{nome_pacote}' não encontrado, tentando '{nome_pacote_alt}'...")
        pacote = get_pacote(nome_pacote_alt)
    if not pacote:
        print(f"[tse_tracker] Pacote '{nome_pacote}' não encontrado.")
        return []

    url_zip = _url_recurso_brasil(pacote)
    if not url_zip:
        print("[tse_tracker] Recurso ZIP de candidatos (Brasil) não encontrado no pacote.")
        return []

    print(f"[tse_tracker] Baixando {url_zip} ...")
    try:
        resp = requests.get(url_zip, headers=HEADERS, timeout=DOWNLOAD_TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha ao baixar {url_zip}: {e}")
        return []

    print("[tse_tracker] Extraindo CSV consolidado...")
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        with zf.open(nome_arquivo) as f:
            df = pd.read_csv(f, sep=CSV_SEP, encoding=CSV_ENCODING, dtype=str)

    print(f"[tse_tracker] {len(df)} candidatos carregados.")
    return df.to_dict(orient="records")
