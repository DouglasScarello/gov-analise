"""
Funções de extração de dados do Portal da Transparência (CGU).

Endpoints usados:
- /ceis                    → empresas/pessoas impedidas de contratar com o poder público
- /cnep                    → empresas punidas por corrupção (Lei Anticorrupção)
- /contratos               → contratos públicos federais, por órgão
- /orgaos-siafi            → catálogo de órgãos públicos federais
"""

import time
from typing import Optional

import requests

from .config import (
    BASE_URL,
    HEADERS,
    REQUEST_TIMEOUT,
    REQUEST_DELAY,
    MAX_PAGINAS_SANCOES,
    ORGAOS_CONTRATOS,
    MAX_PAGINAS_CONTRATOS_POR_ORGAO,
    MAX_PAGINAS_ORGAOS,
)


def _get_json(endpoint: str, params: dict) -> Optional[list]:
    try:
        response = requests.get(
            f"{BASE_URL}/{endpoint}", headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na requisição a {endpoint} ({params}): {e}")
        return None


def _paginar(endpoint: str, params_base: dict, max_paginas: int, label: str) -> list[dict]:
    registros: list[dict] = []
    pagina = 1

    while pagina <= max_paginas:
        params = {**params_base, "pagina": pagina}
        dados = _get_json(endpoint, params)
        if not dados:
            break

        registros.extend(dados)
        print(f"[transparencia_tracker] {label}: página {pagina} ({len(dados)} itens)")

        if len(dados) < 15:  # última página (tamanho padrão de página = 15)
            break

        pagina += 1
        time.sleep(REQUEST_DELAY)

    return registros


def get_ceis() -> list[dict]:
    """Empresas/pessoas impedidas de contratar com o poder público."""
    print("[transparencia_tracker] Buscando CEIS (impedidos de contratar)...")
    return _paginar("ceis", {}, MAX_PAGINAS_SANCOES, "CEIS")


def get_cnep() -> list[dict]:
    """Empresas punidas por corrupção (Cadastro Nacional de Empresas Punidas)."""
    print("[transparencia_tracker] Buscando CNEP (empresas punidas)...")
    return _paginar("cnep", {}, MAX_PAGINAS_SANCOES, "CNEP")


def get_contratos_todos_orgaos() -> list[dict]:
    """Contratos federais de uma amostra de órgãos superiores."""
    todos: list[dict] = []
    for codigo, nome in ORGAOS_CONTRATOS.items():
        print(f"[transparencia_tracker] Buscando contratos de {nome} ({codigo})...")
        registros = _paginar(
            "contratos",
            {"codigoOrgao": codigo},
            MAX_PAGINAS_CONTRATOS_POR_ORGAO,
            f"Contratos {nome}",
        )
        for r in registros:
            r["_orgaoNome"] = nome
        todos.extend(registros)
    return todos


def get_orgaos_siafi() -> list[dict]:
    """Catálogo de órgãos públicos federais (código SIAFI)."""
    print("[transparencia_tracker] Buscando catálogo de órgãos SIAFI...")
    return _paginar("orgaos-siafi", {}, MAX_PAGINAS_ORGAOS, "Órgãos SIAFI")
