"""
Funções genéricas para carregar o snapshot mais recente de cada recurso
em `data/raw/<fonte>/<recurso>/` para um DataFrame pandas.

Suporta os dois formatos usados pelos trackers do projeto:
- JSON versionado: {"_meta": {...}, "dados": [...]}  → <YYYYMMDD>.json
- Parquet (datasets grandes, ex: TSE): <YYYYMMDD>.parquet + <YYYYMMDD>_meta.json
"""

import json
from pathlib import Path
from typing import Optional

import pandas as pd

from .config import RAW_DATA_ROOT


def _ultimo_arquivo(diretorio: Path, extensao: str) -> Optional[Path]:
    """Retorna o arquivo mais recente (por nome, formato YYYYMMDD) de uma extensão."""
    if not diretorio.exists():
        return None
    arquivos = sorted(diretorio.glob(f"*.{extensao}"))
    return arquivos[-1] if arquivos else None


def carregar_recurso_json(fonte: str, recurso: str) -> pd.DataFrame:
    """Carrega o snapshot JSON mais recente de uma fonte/recurso como DataFrame."""
    diretorio = RAW_DATA_ROOT / fonte / recurso
    arquivo = _ultimo_arquivo(diretorio, "json")
    if not arquivo:
        print(f"[etl] Nenhum snapshot encontrado para {fonte}/{recurso}")
        return pd.DataFrame()

    with open(arquivo, "r", encoding="utf-8") as f:
        payload = json.load(f)

    dados = payload.get("dados", [])
    df = pd.DataFrame(dados)
    df.attrs["snapshot_arquivo"] = str(arquivo)
    df.attrs["coletado_em"] = payload.get("_meta", {}).get("coletado_em")
    return df


def carregar_recurso_parquet(fonte: str, recurso: str) -> pd.DataFrame:
    """Carrega o snapshot Parquet mais recente de uma fonte/recurso como DataFrame."""
    diretorio = RAW_DATA_ROOT / fonte / recurso
    arquivo = _ultimo_arquivo(diretorio, "parquet")
    if not arquivo:
        print(f"[etl] Nenhum snapshot encontrado para {fonte}/{recurso}")
        return pd.DataFrame()

    df = pd.read_parquet(arquivo)
    df.attrs["snapshot_arquivo"] = str(arquivo)
    return df
